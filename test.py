import numpy as np
import matplotlib.pyplot as plt
from cable import Cable
# 引入你保存的 main.py 中的类
try:
    from main import Host, Packet, Utils, Modem
except ImportError:
    print("错误：找不到 main.py。请确保你将之前的完整代码保存为 main.py")
    exit()

def plot_modulation_analysis():
    """
    可视化 1: 深入分析物理层
    展示：比特流 -> 调制信号 -> 噪声信号 -> 解调判决
    """
    print("正在生成物理层波形分析图...")
    
    # 1. 准备数据
    message = "Hi!" # 短消息方便绘图
    host = Host(1, None) # 只需要 Modem 功能，不需要真实的 Cable 连接
    
    # 手动构建数据包和比特流
    packet = Packet(1, 2, message, 'DATA', seq=0)
    bits = packet.to_bits()
    
    # 我们只截取前 40 个比特进行详细展示 (大约是头部的一部分)，避免图太长
    display_bits = bits[:40] 
    
    # 2. 调制 (Modulation)
    modem = Modem(samples_per_bit=10) # 假设 main.py 中 samples_per_bit=10
    clean_signal = modem.modulate(display_bits)
    
    # 3. 模拟信道 (Channel)
    # 创建一个噪声较大的环境来展示鲁棒性
    cable = Cable(length=100, attenuation=0.1, noise_level=0.3)
    noisy_signal = cable.transmit(clean_signal) # 注意：Cable 可能会加上延迟或衰减
    
    # 4. 绘图
    plt.figure(figsize=(15, 10))
    plt.subplots_adjust(hspace=0.4)
    
    # --- 子图 1: 原始数字比特流 ---
    plt.subplot(3, 1, 1)
    plt.title(f"1. Digital Bit Stream (First {len(display_bits)} bits of Packet Header)")
    # 画阶梯图表示 0 和 1
    x_bits = np.arange(len(display_bits))
    plt.step(x_bits, display_bits, where='mid', color='black', linewidth=2, label='Logic Bits')
    plt.ylim(-0.5, 1.5)
    plt.yticks([0, 1])
    plt.grid(True, alpha=0.3)
    for i, b in enumerate(display_bits):
        plt.text(i, b + 0.1, str(b), ha='center', fontsize=8, color='blue')
    plt.legend(loc='upper right')

    # --- 子图 2: 模拟信号对比 (发送 vs 接收) ---
    plt.subplot(3, 1, 2)
    plt.title("2. Physical Layer Signals: Clean Transmitted vs. Noisy Received")
    
    samples_per_bit = modem.samples_per_bit
    t = np.arange(len(clean_signal))
    
    # 画发送信号
    plt.plot(t, clean_signal, 'g--', linewidth=1.5, alpha=0.7, label='Tx Signal (Clean)')
    # 画接收信号
    plt.plot(t, noisy_signal[:len(t)], 'r-', linewidth=1, alpha=0.6, label='Rx Signal (Noisy + Attenuated)')
    
    # 画判决阈值线
    threshold = 0 # 假设双极性信号阈值为0
    plt.axhline(y=threshold, color='k', linestyle=':', label='Decision Threshold')
    
    plt.ylabel("Amplitude (Volts)")
    plt.legend(loc='upper right')
    plt.grid(True, alpha=0.3)
    
    # --- 子图 3: 解调判决逻辑 (采样点) ---
    plt.subplot(3, 1, 3)
    plt.title("3. Demodulation Logic: Sampling & Averaging")
    
    # 绘制接收信号
    plt.plot(t, noisy_signal[:len(t)], 'lightgray', label='Raw Signal')
    
    # 模拟解调器的采样过程
    # 我们计算每个比特周期的平均值，用点画出来
    decoded_values = []
    decoded_indices = []
    
    # 注意：这里我们假设已经完美同步（跳过前导码处理，直接按索引画图）
    # 这里的处理是为了可视化，简化了 Modem 类中的同步搜索过程
    preamble_len = 8 * samples_per_bit # 假设前导码长度
    
    for i in range(len(display_bits)):
        # 加上前导码偏移
        start = i * samples_per_bit + preamble_len
        end = start + samples_per_bit
        
        if end > len(noisy_signal): break
        
        # 计算该区间的平均值（积分）
        segment = noisy_signal[start:end]
        avg_val = np.mean(segment)
        
        # 记录中心点位置用于画图
        center_idx = start + samples_per_bit / 2
        decoded_values.append(avg_val)
        decoded_indices.append(center_idx)
        
        # 判定颜色
        color = 'green' if (avg_val > threshold and display_bits[i]==1) or (avg_val < threshold and display_bits[i]==0) else 'red'
        marker = 'o' if display_bits[i] == 1 else 'x'
        
        plt.scatter(center_idx, avg_val, color=color, s=50, zorder=5)
    
    # 伪造一个图例项
    plt.scatter([], [], color='green', label='Correctly Demodulated')
    plt.scatter([], [], color='red', label='Demodulation Error')
    
    plt.xlabel("Sample Index")
    plt.ylabel("Integrated Value")
    plt.legend()
    plt.grid(True)
    
    print("绘图完成。请查看弹出的窗口。")
    plt.show()

def plot_retransmission_timeline():
    """
    可视化 2: 序列号与重传的时序图 (简化版)
    这里我们不用真实的 simulation loop，而是手动生成数据来展示逻辑
    """
    
    events = [
        # (Time, Host, Event, Seq, Status)
        (0.5, 'A', 'Send', 0, 'Success'),
        (1.0, 'B', 'Receive', 0, 'Success'),
        (1.2, 'B', 'Ack', 0, 'Success'),
        (1.7, 'A', 'RxAck', 0, 'Success'),
        
        (2.5, 'A', 'Send', 1, 'Lost'), # 发送丢失
        (5.5, 'A', 'Timeout', 1, 'Retransmit'), # 超时重传
        (5.6, 'A', 'Send', 1, 'Success'), # 重传成功
        (6.1, 'B', 'Receive', 1, 'Success'),
        (6.3, 'B', 'Ack', 1, 'Lost'), # ACK 丢失
        
        (9.5, 'A', 'Timeout', 1, 'Retransmit'), # A 再次超时
        (9.6, 'A', 'Send', 1, 'Duplicate'),
        (10.1, 'B', 'Receive', 1, 'Duplicate'), # B 收到重复
        (10.3, 'B', 'Ack', 1, 'Success'), # B 重发 ACK
        (10.8, 'A', 'RxAck', 1, 'Success'),
    ]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 绘制 Host A 和 Host B 的轴线
    ax.axhline(y=2, color='blue', linestyle='-', alpha=0.3)
    ax.text(0, 2.1, 'Host A (Sender)', color='blue', fontweight='bold')
    
    ax.axhline(y=1, color='green', linestyle='-', alpha=0.3)
    ax.text(0, 1.1, 'Host B (Receiver)', color='green', fontweight='bold')
    
    # 绘制事件
    for time, host, event, seq, status in events:
        y_pos = 2 if host == 'A' else 1
        
        marker = 'o'
        color = 'gray'
        label_text = f"{event}({seq})"
        
        if status == 'Success': color = 'blue' if host=='A' else 'green'
        if status == 'Lost': color = 'red'; marker = 'x'
        if status == 'Retransmit' or status == 'Timeout': color = 'orange'; marker = 'D'
        if status == 'Duplicate': color = 'purple'
        
        ax.plot(time, y_pos, marker=marker, color=color, markersize=10)
        
        # 添加文字标注
        offset = 0.15 if host == 'A' else -0.15
        ax.text(time, y_pos + offset, label_text, ha='center', fontsize=9, color=color)
        
        # 画传输线 (箭头)
        if event == 'Send' and status != 'Lost':
            # 找到下一个 Receive
            ax.arrow(time, 2, 0.4, -0.9, head_width=0.1, head_length=0.1, fc='blue', ec='blue', alpha=0.3)
        if event == 'Ack' and status != 'Lost':
            ax.arrow(time, 1, 0.4, 0.9, head_width=0.1, head_length=0.1, fc='green', ec='green', alpha=0.3)

    plt.title("Sequence Number & Retransmission Timeline Visualization")
    plt.xlabel("Simulation Time (arbitrary units)")
    plt.yticks([]) 
    plt.xlim(0, 12)
    plt.ylim(0, 3)
    plt.grid(True, axis='x', linestyle='--')
    plt.show()

if __name__ == "__main__":
    # 运行两个可视化函数
    print("1. Physical Layer Analysis")
    plot_modulation_analysis()
    
    print("\n2. Retransmission Logic Demonstration")
    plot_retransmission_timeline()