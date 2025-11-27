import numpy as np
import matplotlib.pyplot as plt
from cable import Cable

# 引入 main.py 中的核心类
try:
    from main import Host, Packet, Utils, Modem, AppLayer
except ImportError:
    print("❌ 错误：找不到 main.py。请确保 main.py 存在且名字正确。")
    exit()

def sniff_packet(signal):
    """
    [仿真核心] 像 Wireshark 一样嗅探线缆上的信号
    直接解码模拟信号来获取真实数据，绝不使用预定义值。
    """
    if signal is None or len(signal) == 0:
        return None
    
    # 使用一个临时的 Modem 进行解码（相当于抓包工具）
    sniffer = Modem() 
    bits = sniffer.demodulate(signal)
    packet = Packet.from_bits(bits)
    return packet

def visualize_protocol_timeline():
    """
    可视化 2: 协议时序图 (真实仿真版)
    数据来源：严格基于 Host 类返回的 Signal 进行解码分析。
    """
    print("📈 正在运行真实仿真并生成时序图...")
    
    # --- 1. 初始化仿真环境 ---
    cable = Cable(length=10, attenuation=0, noise_level=0)
    client = Host(1, cable)
    server = Host(2, cable)
    
    events = [] # 记录所有真实发生的事件
    sim_time = 0.0
    
    # 定义丢包区间 (模拟干扰)
    DROP_START = 4.0
    DROP_END = 6.0
    
    def log_event(time, host_addr, action, packet, status="Success"):
        """记录事件用于绘图"""
        seq_info = f"{packet.seq}" if packet else "?"
        p_type = packet.type if packet else "Unknown"
        events.append({
            "time": time,
            "host": host_addr,
            "action": action,     # Send, Receive, Timeout
            "type": p_type,       # DATA, ACK
            "seq": seq_info,
            "status": status
        })

    def propagate_signal(sender, signal, current_time):
        """
        递归信号传播函数
        返回：是否传输成功 (bool)
        """
        if signal is None: return False
        
        # [验证点 1] 嗅探发送的信号，确保是真实数据
        real_packet = sniff_packet(signal)
        if real_packet is None: return False # 信号无效
        
        # 记录“发送”事件
        # 检查是否是在丢包区间
        is_dropped = (DROP_START < current_time < DROP_END)
        status = "Lost" if is_dropped else "Success"
        
        log_event(current_time, sender.address, "Send", real_packet, status)
        
        if is_dropped:
            return False # 模拟物理层丢包，不调用 receive

        # 物理传输
        rx_signal = cable.transmit(signal)
        receiver = server if sender == client else client
        
        # 接收处理
        response_signal, _ = receiver.receive(rx_signal)
        
        # 记录“接收”事件 (接收方视角)
        log_event(current_time + 0.5, receiver.address, "Receive", real_packet, "Success")
        
        # 如果有回应 (ACK)，递归调用
        if response_signal is not None:
            # 嗅探 ACK 信号
            ack_packet = sniff_packet(response_signal)
            # 记录 ACK 发送
            log_event(current_time + 0.6, receiver.address, "Send", ack_packet, "Success")
            
            # ACK 传回给原发送者
            # 这里简化 ACK 不会丢失
            client_rx = cable.transmit(response_signal)
            sender.receive(client_rx)
            log_event(current_time + 1.0, sender.address, "Receive", ack_packet, "Success")
            
        return True

    # --- 2. 执行仿真剧本 ---
    
    # [Step 1] 正常发送
    # Client 真实调用 send，产生真实信号
    print(f"[{sim_time}s] Client sending packet...")
    signal = client.send(2, "Hello", sim_time)
    propagate_signal(client, signal, sim_time)
    
    # [Step 2] 模拟时间流逝到丢包区间
    sim_time = 5.0
    print(f"[{sim_time}s] Client sending packet (will be lost)...")
    # Client 再次发送 (Seq 应该自动增加了)
    signal = client.send(2, "LostData", sim_time)
    propagate_signal(client, signal, sim_time) 
    # 注意：propagate_signal 内部会根据 sim_time 判断丢包，并在 events 中标记为 Lost
    
    # [Step 3] 模拟超时
    # 我们知道 client 的 timeout 是 3.0s
    # 跳到 Time = 9.0 (5.0 + 4.0)
    sim_time += 4.0
    print(f"[{sim_time}s] Checking timeouts...")
    
    # 真实调用 check_timeouts
    # 如果 main.py 逻辑有 bug，这里 retry_signals 将为空，图上就不会画重传
    retry_signals = client.check_timeouts(sim_time)
    
    if len(retry_signals) > 0:
        for sig in retry_signals:
            # 嗅探一下，确认是重传包
            pkt = sniff_packet(sig)
            print(f"   >>> Detected retransmission of SEQ={pkt.seq}")
            # 记录超时事件标记
            events.append({"time": sim_time, "host": 1, "action": "Timeout", "seq": pkt.seq, "type": "EVENT", "status": "Timeout"})
            # 执行重传传播
            propagate_signal(client, sig, sim_time)
    else:
        print("   >>> No retransmission detected! (Logic Error in main.py?)")

    # --- 3. 绘图 (基于 events 数据) ---
    print("🎨 正在绘制图形...")
    fig, ax = plt.subplots(figsize=(12, 6))
    
    y_client = 3
    y_server = 1
    
    # 设置画布
    ax.set_ylim(0, 4)
    ax.set_xlim(0, 12)
    ax.set_yticks([])
    ax.set_title("Protocol Sequence - Generated from Real Signal Analysis")
    
    # 画主机线
    ax.axhline(y_client, color='blue', linestyle='-', alpha=0.3)
    ax.text(0, y_client + 0.2, 'Host 1 (Client)', fontweight='bold', color='blue')
    ax.axhline(y_server, color='green', linestyle='-', alpha=0.3)
    ax.text(0, y_server + 0.2, 'Host 2 (Server)', fontweight='bold', color='green')
    
    # 遍历真实记录的事件进行绘制
    for e in events:
        t = e['time']
        h = e['host']
        action = e['action']
        status = e['status']
        ptype = e['type']
        seq = e['seq']
        
        y = y_client if h == 1 else y_server
        
        if action == "Send":
            # 区分 DATA 和 ACK 颜色
            color = 'blue' if ptype == 'DATA' else 'green'
            if status == 'Lost': color = 'red'
            
            # 画点
            marker = 'x' if status == 'Lost' else 'o'
            ax.plot(t, y, marker=marker, color=color, markersize=10)
            
            # 标注
            label = f"{ptype}\nSeq={seq}"
            ax.text(t, y + 0.3, label, ha='center', fontsize=8, color=color)
            
            # 画箭头
            if status == 'Lost':
                ax.arrow(t, y, 0.5, -0.8, head_width=0.15, color='red', alpha=0.5)
                ax.text(t + 0.5, y - 1, "Dropped", color='red', fontsize=9)
            else:
                dy = -1.8 if h == 1 else 1.8 # 这里的方向取决于谁发给谁
                # 如果是 ACK (Host 2 -> 1)，向上画
                # 如果是 DATA (Host 1 -> 2)，向下画
                # 根据本次仿真，Host 1 总是发 DATA，Host 2 总是发 ACK
                final_dy = -1.8 if ptype == 'DATA' else 1.8
                ax.arrow(t, y, 0.5, final_dy, head_width=0.15, color=color, alpha=0.3)

        elif action == "Timeout":
            ax.plot(t, y, marker='D', color='orange', markersize=12, zorder=10)
            ax.text(t, y + 0.5, "Timeout!", ha='center', color='orange', fontweight='bold')

    ax.set_xlabel("Simulation Time (s)")
    ax.grid(True, axis='x', linestyle='--', alpha=0.3)
    
    print("✅ 绘图完成。")
    plt.savefig('retransmission.png',dpi=320)
    plt.show()

def visualize_physical_layer():
    """保留之前的物理层波形图，因为那已经是真实仿真的了"""
    print("📊 正在生成物理层波形图...")
    packet = Packet(src=1, dst=2, payload_str="Hi", type='DATA', seq=1)
    bits = packet.to_bits()
    display_bits = bits[:50] 
    modem = Modem(samples_per_bit=10)
    tx_signal = modem.modulate(display_bits)
    cable = Cable(length=100, attenuation=0.1, noise_level=0.4) 
    rx_signal = cable.transmit(tx_signal)
    
    plt.figure(figsize=(14, 10))
    plt.subplots_adjust(hspace=0.5)
    
    ax1 = plt.subplot(3, 1, 1)
    ax1.set_title("1. Digital Bit Stream")
    ax1.step(np.arange(len(display_bits)), display_bits, where='mid', color='black', linewidth=2)
    ax1.set_ylim(-0.5, 1.5)
    ax1.grid(True, alpha=0.3)
    for i, b in enumerate(display_bits):
        ax1.text(i, b + 0.1, str(b), ha='center', fontsize=8, color='blue')

    ax2 = plt.subplot(3, 1, 2)
    ax2.set_title("2. Analog Signals: Transmitted vs. Received (Noisy)")
    t = np.arange(len(tx_signal))
    ax2.plot(t, tx_signal, 'g--', alpha=0.6, label='Tx')
    ax2.plot(t, rx_signal[:len(t)], 'r-', alpha=0.7, label='Rx')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    ax3 = plt.subplot(3, 1, 3)
    ax3.set_title("3. Demodulation Sampling")
    ax3.plot(t, rx_signal[:len(t)], 'lightgray')
    
    samples_per_bit = modem.samples_per_bit
    full_tx_bits = modem.preamble + display_bits
    for i in range(len(full_tx_bits)):
        if i * samples_per_bit >= len(t): break
        start = i * samples_per_bit
        end = start + samples_per_bit
        center = start + samples_per_bit / 2
        segment = rx_signal[start:end]
        avg_val = np.mean(segment)
        threshold = 0
        decided = 1 if avg_val > threshold else 0
        original = full_tx_bits[i]
        color = 'green' if decided == original else 'red'
        ax3.scatter(center, avg_val, color=color, s=40, zorder=5)
    
    plt.show()

if __name__ == "__main__":
    visualize_physical_layer()
    visualize_protocol_timeline()