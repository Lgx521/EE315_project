import numpy as np
import matplotlib.pyplot as plt
from cable import Cable

# 尝试导入 main.py 中的核心类
try:
    from main import Packet, Modem, Utils
except ImportError:
    print("❌ 错误：找不到 main.py。请确保 main.py 存在且名字正确。")
    exit()

def visualize_physical_layer_accurate():
    """
    准确的物理层可视化：对比发送比特、接收信号与实际解调比特
    """
    print("📊 正在生成精确物理层分析图...")
    print("此视图对比原始发送比特与 Modem 实际解调后的比特，以准确反映物理层性能。")

    # ==============================
    # 1. 配置与数据生成
    # ==============================
    # 噪声水平：设置一个中等噪声，既能看到波形畸变，又不会导致解调完全失败
    NOISE_LEVEL = 1.2
    # 为了绘图清晰，我们截取展示的比特数
    DISPLAY_BITS = 60

    # 初始化 Modem 和 Cable
    # 注意：这里使用默认的 ASK 调制，如果你在 main.py 里改成了 BPSK，这里也会体现
    modem = Modem() 
    cable = Cable(length=50, attenuation=0.1, noise_level=NOISE_LEVEL)

    # 创建要发送的数据包 (稍微长一点以便观察)
    packet_str = "PhysLayerTestString"
    packet = Packet(src=10, dst=20, payload_str=packet_str, type='DATA', seq=1)
    
    # 获取原始发送比特 (这是不含前导码的 Payload 部分)
    tx_payload_bits = packet.to_bits()

    # ==============================
    # 2. 执行传输仿真
    # ==============================
    print(f"Is Modulating {len(tx_payload_bits)} bits...")
    # 调制：Modem 会自动在前面添加前导码
    tx_signal = modem.modulate(tx_payload_bits)
    
    print(f"Is Transmitting signal through cable (Noise={NOISE_LEVEL})...")
    # 传输：添加噪声和衰减
    rx_signal = cable.transmit(tx_signal)
    
    print("Is Demodulating received signal...")
    # 解调：获取 Modem 实际解出的比特 (Modem 会尝试剥离前导码)
    rx_payload_bits = modem.demodulate(rx_signal)

    # ==============================
    # 3. 数据对齐与准备绘图
    # ==============================
    # 为了绘图对比，我们需要截取相同长度的数据
    # 取实际解出长度、原始长度和最大显示长度中的最小值
    plot_len = min(len(tx_payload_bits), len(rx_payload_bits), DISPLAY_BITS)
    
    tx_plot = tx_payload_bits[:plot_len]
    rx_plot = rx_payload_bits[:plot_len]
    
    # 计算波形图的显示范围
    # 假设 Modem 内部 samples_per_bit 是常量
    samples_per_bit = modem.samples_per_bit
    # 我们需要加上前导码的长度来定位信号波形中的 payload 部分
    preamble_offset = len(modem.preamble) * samples_per_bit
    signal_plot_len = plot_len * samples_per_bit
    # 截取对应的接收信号片段用于展示
    rx_signal_plot = rx_signal[preamble_offset : preamble_offset + signal_plot_len]
    # 如果信号太短(可能因同步失败被截断), 则有多少画多少
    if len(rx_signal_plot) == 0:
         rx_signal_plot = rx_signal[:signal_plot_len] # Fallback

    # ==============================
    # 4. 绘制图表
    # ==============================
    fig, axes = plt.subplots(3, 1, figsize=(12, 8.5), sharex=False)
    plt.subplots_adjust(hspace=0.4)

    # --- 子图 1: 原始发送比特 (Ground Truth) ---
    ax1 = axes[0]
    ax1.set_title(f"1. Original Tx Bits (Payload, First {plot_len} bits) - Ground Truth")
    # 使用阶梯图展示数字信号
    ax1.step(np.arange(plot_len), tx_plot, where='mid', color='blue', linewidth=2, label='Tx Bits')
    ax1.set_ylim(-0.2, 1.2)
    ax1.set_yticks([0, 1])
    ax1.grid(True, alpha=0.3)
    # 在上方标注数值
    for i, bit in enumerate(tx_plot):
        ax1.text(i, bit + 0.05, str(bit), ha='center', fontsize=9, color='blue')
    ax1.legend(loc='upper right')

    # --- 子图 2: 接收到的模拟信号 (Analog Signal) ---
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
    # 调整 X 轴刻度以匹配比特索引 (辅助查看)
    ax2_top = ax2.secondary_xaxis('top')
    ax2_top.set_ticks(np.arange(0, len(rx_signal_plot) + 1, samples_per_bit))
    ax2_top.set_xticklabels(np.arange(0, plot_len + 1))
    ax2_top.set_xlabel("Bit Index Approximation")


    # --- 子图 3: 实际解调比特 (Actual Demodulated Result) ---
    ax3 = axes[2]
    ax3.set_title("3. Actual Demodulated Rx Bits (Compare with Fig 1)")
    
    # 绘制基准线
    ax3.step(np.arange(plot_len), rx_plot, where='mid', color='green', linewidth=2, alpha=0.6, label='Rx Bits (Demodulated)')
    
    # 对比并高亮错误
    error_count = 0
    for i in range(plot_len):
        tx_bit = tx_plot[i]
        rx_bit = rx_plot[i]
        
        if tx_bit != rx_bit:
            error_count += 1
            # 绘制红色的错误标记
            ax3.plot(i, rx_bit, 'rx', markersize=12, markeredgewidth=2, label='Bit Error' if error_count == 1 else "")
            ax3.text(i, rx_bit + 0.15, f"Bit Error", ha='center', color='red', fontsize=9, fontweight='bold')
        else:
            # 标注正确的数值
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
    plt.subplots_adjust(bottom=0.1) # 留出底部空间给文字
    plt.savefig('Recover_bits_msgs_e.png',dpi=320)
    plt.show()

if __name__ == "__main__":
    visualize_physical_layer_accurate()