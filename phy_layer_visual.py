import numpy as np
import matplotlib.pyplot as plt
from cable import Cable

# 导入 main.py 中的类
try:
    from main import Packet, Modem
except ImportError:
    print("cannot import main.py")
    exit()

def visualize_physics():
    """
    可视化物理层: 比特流 -> 调制 -> 噪声传输 -> 解调采样
    """
    print("📊 正在生成物理层波形图 (Physical Layer Analysis)...")
    
    # 1. 准备数据
    # 创建一个简单的数据包
    packet = Packet(src=1, dst=2, payload_str="Hi", type='DATA', seq=1)
    payload_bits = packet.to_bits()
    
    # 初始化 Modem 和 Cable
    modem = Modem(samples_per_bit=10)
    # 为了演示效果，我们手动把前导码拿出来，这样绘图时能看到完整的比特流
    full_bits = modem.preamble + payload_bits
    
    # 为了绘图清晰，我们只截取前 60 个比特 (前导码 + 头部 + 部分载荷)
    display_len = 60
    display_bits = full_bits[:display_len]
    
    # 2. 调制 (Modulate)
    # 注意：我们这里手动调用底层逻辑以匹配 display_bits
    tx_signal = []
    for b in display_bits:
        val = modem.high_level if b == 1 else modem.low_level
        tx_signal.extend([val] * modem.samples_per_bit)
    tx_signal = np.array(tx_signal)
    
    # 3. 传输 (通过高噪声信道)
    # 设置较高的噪声 (0.4) 以便观察抗噪能力
    cable = Cable(length=100, attenuation=0.1, noise_level=0.4) 
    rx_signal = cable.transmit(tx_signal)
    
    # 4. 绘图配置
    plt.figure(figsize=(14, 10))
    plt.subplots_adjust(hspace=0.5)
    
    # --- 子图 1: 数字比特流 (Digital Bit Stream) ---
    ax1 = plt.subplot(3, 1, 1)
    ax1.set_title(f"1. Digital Bit Stream (Preamble + Header... First {display_len} bits)")
    # 绘制阶梯图
    ax1.step(np.arange(len(display_bits)), display_bits, where='mid', color='black', linewidth=2)
    ax1.set_ylim(-0.5, 1.5)
    ax1.set_yticks([0, 1])
    ax1.set_yticklabels(['0', '1'])
    ax1.grid(True, alpha=0.3)
    
    # 在线上标注数值 (区分前导码和数据)
    preamble_len = len(modem.preamble)
    for i, b in enumerate(display_bits):
        color = 'red' if i < preamble_len else 'blue'
        weight = 'bold' if i < preamble_len else 'normal'
        ax1.text(i, b + 0.1, str(b), ha='center', fontsize=8, color=color, fontweight=weight)
    
    # 添加文字说明
    ax1.text(0, 1.2, "Preamble (Sync)", color='red', fontsize=10, fontweight='bold')
    ax1.text(preamble_len, 1.2, "Packet Data", color='blue', fontsize=10)

    # --- 子图 2: 模拟信号 (Analog Signals) ---
    ax2 = plt.subplot(3, 1, 2)
    ax2.set_title("2. Analog Signals: Transmitted (Clean) vs. Received (Noisy)")
    t = np.arange(len(tx_signal))
    
    # 绘制发送信号 (绿色虚线)
    ax2.plot(t, tx_signal, 'g--', linewidth=1.5, alpha=0.6, label='Tx Signal (Clean)')
    # 绘制接收信号 (红色实线)
    ax2.plot(t, rx_signal[:len(t)], 'r-', linewidth=1, alpha=0.7, label='Rx Signal (Noisy)')
    
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylabel("Amplitude (V)")

    # --- 子图 3: 解调判决视角 (Demodulation Sampling) ---
    ax3 = plt.subplot(3, 1, 3)
    ax3.set_title("3. Demodulation Logic: Integration & Sampling")
    ax3.plot(t, rx_signal[:len(t)], 'lightgray', label='Raw Rx Signal')
    
    # 模拟 Modem 的采样逻辑进行绘图
    samples_per_bit = modem.samples_per_bit
    
    for i in range(len(display_bits)):
        start = i * samples_per_bit
        end = start + samples_per_bit
        center = start + samples_per_bit / 2
        
        # 提取当前比特周期的信号片段
        segment = rx_signal[start:end]
        # 计算积分均值 (Integrate and Dump)
        avg_val = np.mean(segment)
        
        # 判决 (Threshold = 0)
        threshold = 0
        decided_bit = 1 if avg_val > threshold else 0
        original_bit = display_bits[i]
        
        # 绘图: 绿色点表示正确，红色叉表示错误
        color = 'green' if decided_bit == original_bit else 'red'
        marker = 'o' if decided_bit == 1 else 'x' # 如果判决为1画圈，判决为0画叉
        
        # 画出采样点
        ax3.scatter(center, avg_val, color=color, s=50, zorder=5)
        
        # 可选: 画出该比特周期的平均线
        ax3.hlines(avg_val, start, end, colors=color, linestyles='-', linewidth=2, alpha=0.5)

    # 伪造图例
    ax3.scatter([], [], color='green', label='Correct Decode')
    ax3.scatter([], [], color='red', label='Bit Error')
    ax3.legend(loc='upper right')
    ax3.grid(True, alpha=0.3)
    ax3.set_xlabel("Sample Index")
    ax3.set_ylabel("Integrated Value")

    print("✅ 绘图完成。")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    visualize_physics()