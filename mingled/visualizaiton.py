"""
数据通信项目 - 集成可视化模块
包含三个主要可视化功能：
1. 物理层精确分析 (发送比特 vs 接收信号 vs 解调比特)
2. 三种调制方式对比 (ASK vs FSK vs BPSK)
3. 全栈协议时序可视化 (网络仿真事件时序图)
"""

import numpy as np
import matplotlib.pyplot as plt
import copy
from cable import Cable
from wireless_channel import WirelessChannel

# 导入simulation_core中的核心类
from simulation_core import Packet, Modem, Utils, Host, run_simulation, SIM_EVENTS


# ============================================================================
# 可视化功能 1: 物理层精确分析
# ============================================================================
def visualize_physical_layer_accurate():
    """
    准确的物理层可视化：对比发送比特、接收信号与实际解调比特
    展示物理层调制解调的完整过程和误码率分析
    """
    print("📊 正在生成精确物理层分析图...")
    print("此视图对比原始发送比特与 Modem 实际解调后的比特，以准确反映物理层性能。")

    # ==============================
    # 1. 配置与数据生成
    # ==============================
    NOISE_LEVEL = 1.2  # 中等噪声水平
    DISPLAY_BITS = 60  # 展示的比特数

    # 初始化 Modem 和 Cable
    modem = Modem() 
    cable = Cable(length=50, attenuation=0.1, noise_level=NOISE_LEVEL)

    # 创建要发送的数据包
    packet_str = "PhysLayerTestString"
    packet = Packet(src=10, dst=20, payload_str=packet_str, type='DATA', seq=1)
    
    # 获取原始发送比特
    tx_payload_bits = packet.to_bits()

    # ==============================
    # 2. 执行传输仿真
    # ==============================
    print(f"Modulating {len(tx_payload_bits)} bits...")
    tx_signal = modem.modulate(tx_payload_bits)
    
    print(f"Transmitting signal through cable (Noise={NOISE_LEVEL})...")
    rx_signal = cable.transmit(tx_signal)
    
    print("Demodulating received signal...")
    rx_payload_bits = modem.demodulate(rx_signal)

    # ==============================
    # 3. 数据对齐与准备绘图
    # ==============================
    plot_len = min(len(tx_payload_bits), len(rx_payload_bits), DISPLAY_BITS)
    
    tx_plot = tx_payload_bits[:plot_len]
    rx_plot = rx_payload_bits[:plot_len]
    
    # 计算波形图的显示范围
    samples_per_bit = modem.samples_per_bit
    preamble_offset = len(modem.preamble) * samples_per_bit
    signal_plot_len = plot_len * samples_per_bit
    rx_signal_plot = rx_signal[preamble_offset : preamble_offset + signal_plot_len]
    
    if len(rx_signal_plot) == 0:
         rx_signal_plot = rx_signal[:signal_plot_len]

    # ==============================
    # 4. 绘制图表
    # ==============================
    fig, axes = plt.subplots(3, 1, figsize=(12, 8.5), sharex=False)
    plt.subplots_adjust(hspace=0.4)

    # --- 子图 1: 原始发送比特 ---
    ax1 = axes[0]
    ax1.set_title(f"1. Original Tx Bits (Payload, First {plot_len} bits) - Ground Truth")
    ax1.step(np.arange(plot_len), tx_plot, where='mid', color='blue', linewidth=2, label='Tx Bits')
    ax1.set_ylim(-0.2, 1.2)
    ax1.set_yticks([0, 1])
    ax1.grid(True, alpha=0.3)
    for i, bit in enumerate(tx_plot):
        ax1.text(i, bit + 0.05, str(bit), ha='center', fontsize=9, color='blue')
    ax1.legend(loc='upper right')

    # --- 子图 2: 接收到的模拟信号 ---
    ax2 = axes[1]
    ax2.set_title("2. Received Analog Signal (Corresponding to Payload Area)")
    t = np.arange(len(rx_signal_plot))
    ax2.plot(t, rx_signal_plot, color='red', alpha=0.7, linewidth=1, label='Rx Signal (Noisy)')
    
    # 画出比特边界辅助线
    for i in range(plot_len + 1):
        ax2.axvline(x=i * samples_per_bit, color='gray', linestyle=':', alpha=0.5)
        
    ax2.grid(True, alpha=0.3)
    ax2.set_ylabel("Amplitude (V)")
    ax2.legend(loc='upper right')
    ax2_top = ax2.secondary_xaxis('top')
    ax2_top.set_ticks(np.arange(0, len(rx_signal_plot) + 1, samples_per_bit))
    ax2_top.set_xticklabels(np.arange(0, plot_len + 1))
    ax2_top.set_xlabel("Bit Index Approximation")

    # --- 子图 3: 实际解调比特 ---
    ax3 = axes[2]
    ax3.set_title("3. Actual Demodulated Rx Bits (Compare with Fig 1)")
    
    ax3.step(np.arange(plot_len), rx_plot, where='mid', color='green', linewidth=2, alpha=0.6, label='Rx Bits (Demodulated)')
    
    # 对比并高亮错误
    error_count = 0
    for i in range(plot_len):
        tx_bit = tx_plot[i]
        rx_bit = rx_plot[i]
        
        if tx_bit != rx_bit:
            error_count += 1
            ax3.plot(i, rx_bit, 'rx', markersize=12, markeredgewidth=2, label='Bit Error' if error_count == 1 else "")
            ax3.text(i, rx_bit + 0.15, f"Bit Error", ha='center', color='red', fontsize=9, fontweight='bold')
        else:
            ax3.text(i, rx_bit + 0.05, str(rx_bit), ha='center', fontsize=9, color='green')

    ax3.set_ylim(-0.2, 1.4)
    ax3.set_yticks([0, 1])
    ax3.grid(True, alpha=0.3)
    ax3.set_xlabel("Bit Index")
    ax3.legend(loc='upper right')
    
    # 计算并显示误码率
    ber = error_count / plot_len if plot_len > 0 else 0
    plt.figtext(0.5, 0.01, f"Displayed Region Analysis: {error_count} Errors in {plot_len} Bits (BER = {ber:.2%}) | Noise Level = {NOISE_LEVEL}", 
                ha='center', fontsize=12, bbox={"facecolor":"orange", "alpha":0.2, "pad":5})

    print("✅ 准确版物理层绘图完成。")
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.1)
    plt.savefig('physical_layer_analysis.png', dpi=320)
    plt.show()


# ============================================================================
# 可视化功能 2: 三种调制方式对比
# ============================================================================
def visualize_modulation_schemes():
    """
    生成三种调制方式的对比图 (ASK vs FSK vs BPSK)
    展示不同调制方式的波形特征和区别
    """
    print("📊 正在生成三种调制方式的对比图 (ASK vs FSK vs BPSK)...")
    
    # 1. 准备测试数据
    raw_bits = [1, 0, 1, 1, 0] 
    
    # 初始化 Modem (高采样率以显示圆滑的正弦波)
    modem = Modem(sample_rate=1000, samples_per_bit=40)
    
    # 初始化信道 (轻微噪声)
    channel = WirelessChannel(length=50, attenuation=0.1, noise_level=0.3)

    # 2. 绘图配置
    fig, axes = plt.subplots(3, 1, figsize=(14, 8.5), layout="constrained")
    plt.subplots_adjust(hspace=0.4)
    
    schemes = ['ASK', 'FSK', 'BPSK']
    colors = {'ASK': 'blue', 'FSK': 'green', 'BPSK': 'purple'}
    
    # 完整的比特流 (Preamble + Data)
    full_bits = modem.preamble + raw_bits
    
    for i, scheme in enumerate(schemes):
        ax = axes[i]
        color = colors[scheme]
        
        # --- 调制 (Tx) ---
        tx_signal = modem.modulate(raw_bits, scheme=scheme)
        
        # --- 传输 (Rx) ---
        rx_signal = channel.transmit(tx_signal)
        
        t = np.arange(len(tx_signal))
        
        # --- 绘图 ---
        ax.set_title(f"Scheme: {scheme} (Modulation)", fontsize=12, fontweight='bold', color=color)
        
        # 画发送信号 (半透明填充，表示理想波形)
        ax.plot(t, tx_signal, color=color, alpha=0.4, linewidth=1, label='Tx (Clean)')
        ax.fill_between(t, tx_signal, alpha=0.1, color=color)
        
        # 标注比特位
        samples = modem.samples_per_bit
        for bit_idx, bit in enumerate(full_bits):
            x_center = bit_idx * samples + samples / 2
            # 区分前导码和数据
            txt_color = 'gray' if bit_idx < 8 else 'red'
            weight = 'normal' if bit_idx < 8 else 'bold'
            lbl = "Pre" if bit_idx == 0 else ("Data" if bit_idx == 8 else str(bit))
            if bit_idx != 0 and bit_idx != 8: lbl = str(bit)
            
            ax.text(x_center, 1.5, lbl, ha='center', color=txt_color, fontweight=weight)
            
            # 画竖线分隔比特
            ax.axvline(x=bit_idx * samples, color='gray', linestyle=':', alpha=0.3)
        
        ax.set_ylim(-2, 2)
        ax.set_xlim(0, len(tx_signal))
        ax.grid(True, alpha=0.2)
        
        # 添加特征说明
        if scheme == 'ASK':
            desc = "Feature: Amplitude changes (1 -> High, 0 -> Low)"
        elif scheme == 'FSK':
            desc = "Feature: Frequency changes (1 -> Dense waves, 0 -> Loose waves)"
        elif scheme == 'BPSK':
            desc = "Feature: Phase flips 180° at bit boundaries (e.g., look at 1->0 transition)"
        
        ax.text(len(tx_signal)*0.01, -1.8, desc, fontsize=10, style='italic', backgroundcolor='white')

    plt.savefig('modulation_comparison.png', dpi=320)
    print("✅ 对比绘图完成。")
    plt.show()


# ============================================================================
# 可视化功能 3: 全栈协议时序可视化
# ============================================================================
def visualize_protocol_timeline():
    """
    生成全栈协议时序可视化图 (3 Schemes)
    展示完整的网络通信过程，包括正常传输、丢包和超时重传
    """
    print("🚀 启动全栈协议时序可视化 (3 Schemes)...")
    
    # 定义要对比的三种调制方式
    schemes = ['ASK', 'FSK', 'BPSK']
    colors = {'ASK': '#1f77b4', 'FSK': '#2ca02c', 'BPSK': '#9467bd'}
    
    # 创建 3 行 1 列的画布
    fig, axes = plt.subplots(3, 1, figsize=(14, 16), sharex=True)
    plt.subplots_adjust(hspace=0.3)
    
    # Y轴坐标定义
    Y_CLIENT = 3.0
    Y_SERVER = 1.0
    
    for i, scheme in enumerate(schemes):
        ax = axes[i]
        color = colors[scheme]
        
        # ==========================================
        # 核心: 每次运行前清空全局事件记录
        # ==========================================
        SIM_EVENTS.clear() 
        
        # 运行仿真
        print(f"Running simulation for {scheme}...")
        run_simulation(target_scheme=scheme)
        
        # 深拷贝数据，防止被下一次运行覆盖
        events = copy.deepcopy(SIM_EVENTS)
        
        # --- 绘图设置 ---
        ax.set_title(f"Scheme: {scheme} (Physical Layer)", fontsize=14, fontweight='bold', color=color, loc='left')
        ax.set_ylim(0, 4.5)
        ax.set_xlim(0, 13)
        
        # 绘制 Host 轨道线
        ax.axhline(Y_CLIENT, color='blue', alpha=0.1, linewidth=2, linestyle='-')
        ax.axhline(Y_SERVER, color='green', alpha=0.1, linewidth=2, linestyle='-')
        ax.text(0.2, Y_CLIENT + 0.2, "Host 1 (Client)", color='blue', fontweight='bold')
        ax.text(0.2, Y_SERVER + 0.2, "Host 2 (Server)", color='green', fontweight='bold')
        
        # 绘制丢包区域 (Loss Zone) - 对应 4.0s - 6.0s
        ax.axvspan(4.0, 6.0, facecolor='red', alpha=0.07)
        ax.text(5.0, 4.2, "Interference Zone\n(Packet Loss)", ha='center', va='center', color='red', fontsize=9, alpha=0.6)

        # --- 绘制事件 ---
        for e in events:
            t = e['time']
            host = e['host']
            action = e['action']
            status = e['status']
            ptype = e['type']
            seq = e['seq']
            
            # 确定 Y 坐标
            y_start = Y_CLIENT if host == 1 else Y_SERVER
            y_target = Y_SERVER if host == 1 else Y_CLIENT
            
            # 1. 绘制 Timeout 事件 (菱形)
            if action == 'Timeout':
                ax.plot(t, y_start, marker='D', color='orange', markersize=10, zorder=10, markeredgecolor='white')
                ax.text(t, y_start + 0.4, "Timeout!", ha='center', color='orange', fontsize=9, fontweight='bold')
                
                # 画一个回旋箭头表示重试
                ax.annotate("", xy=(t-0.2, y_start+0.2), xytext=(t+0.2, y_start+0.2),
                            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.5", color='orange', ls='--'))
                continue

            # 2. 绘制节点 (圆点)
            if status == 'Lost':
                ax.plot(t, y_start, marker='x', color='red', markersize=10, markeredgewidth=2)
            else:
                node_color = color if ptype == 'DATA' else 'gray'
                ax.plot(t, y_start, marker='o', color=node_color, markersize=8, zorder=5)
                
                # 标签: "DATA Seq=0"
                label_y_offset = 0.3 if host == 1 else -0.5
                ax.text(t, y_start + label_y_offset, f"{ptype}\nSeq={seq}", 
                        ha='center', fontsize=8, color=node_color)

            # 3. 绘制传输箭头 (核心时序逻辑)
            if action == "Send":
                delay = 0.5  # 传播延迟
                
                if status == 'Success':
                    # 成功的箭头：从源指到宿
                    arrow_color = color if ptype == 'DATA' else 'gray'
                    style = "->"
                    if ptype == 'ACK': style = "-|>"
                    
                    ax.annotate("", 
                                xy=(t + delay, y_target), 
                                xytext=(t, y_start),
                                arrowprops=dict(arrowstyle=style, color=arrow_color, lw=1.5, alpha=0.7))
                                
                elif status == 'Lost':
                    # 失败的箭头：断在半路，打个叉
                    mid_time = t + (delay * 0.6)
                    mid_y = (y_start + y_target) / 2
                    
                    ax.annotate("", 
                                xy=(mid_time, mid_y), 
                                xytext=(t, y_start),
                                arrowprops=dict(arrowstyle="-[", color='red', lw=1.5))
                    
                    ax.text(mid_time + 0.1, mid_y, "❌ Dropped", color='red', fontsize=8, fontweight='bold', ha='left')

    # 全局设置
    axes[-1].set_xlabel("Simulation Time (seconds)", fontsize=12)
    plt.suptitle("Full-Stack Network Simulation: Protocol Analysis across Modulation Schemes", fontsize=16, y=0.95)
    
    # 保存或显示
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig('protocol_timeline.png', dpi=320)
    print("✅ 可视化完成，正在显示图表...")
    plt.show()


# ============================================================================
# 主函数 - 提供菜单选择
# ============================================================================
def main():
    """
    主函数：提供菜单让用户选择要运行的可视化功能
    """
    print("=" * 60)
    print("数据通信项目 - 集成可视化系统")
    print("=" * 60)
    print("\n请选择要运行的可视化功能：")
    print("1. 物理层精确分析 (发送比特 vs 接收信号 vs 解调比特)")
    print("2. 三种调制方式对比 (ASK vs FSK vs BPSK)")
    print("3. 全栈协议时序可视化 (网络仿真事件时序图)")
    print("4. 运行所有可视化")
    print("0. 退出")
    print("=" * 60)
    
    choice = input("\n请输入选项 (0-4): ").strip()
    
    if choice == '1':
        visualize_physical_layer_accurate()
    elif choice == '2':
        visualize_modulation_schemes()
    elif choice == '3':
        visualize_protocol_timeline()
    elif choice == '4':
        print("\n正在运行所有可视化功能...\n")
        visualize_physical_layer_accurate()
        print("\n" + "=" * 60 + "\n")
        visualize_modulation_schemes()
        print("\n" + "=" * 60 + "\n")
        visualize_protocol_timeline()
    elif choice == '0':
        print("退出程序。")
        return
    else:
        print("无效选项，请重新运行程序。")
        return
    
    print("\n" + "=" * 60)
    print("可视化完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
