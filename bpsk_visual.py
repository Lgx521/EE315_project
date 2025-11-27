import numpy as np
import matplotlib.pyplot as plt
from cable import Cable

# 引入 main.py 中的类
try:
    from main import Packet, Modem, WirelessChannel
except ImportError:
    print("❌ 错误：找不到 main.py。")
    exit()

def visualize_all_schemes():
    print("📊 正在生成三种调制方式的对比图 (ASK vs FSK vs BPSK)...")
    
    # 1. 准备测试数据
    # 我们使用一个简单的比特序列: 1, 0, 1, 1, 0 (方便观察连1和0的变化)
    # 注意: Modem 会自动在前面加上 Preamble [1, 0, 1, 0, 1, 0, 1, 0]
    raw_bits = [1, 0, 1, 1, 0] 
    
    # 初始化 Modem (高采样率以显示圆滑的正弦波)
    modem = Modem(sample_rate=1000, samples_per_bit=40)
    
    # 初始化信道 (加一点点噪声，体现真实感，但不要太多以免掩盖波形特征)
    channel = WirelessChannel(length=50, attenuation=0.1, noise_level=0.3)

    # 2. 绘图配置
    fig, axes = plt.subplots(3, 1, figsize=(14, 8.5),layout="constrained")
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
        # 加上一点瑞利衰落和噪声
        rx_signal = channel.transmit(tx_signal)
        
        t = np.arange(len(tx_signal))
        
        # --- 绘图 ---
        ax.set_title(f"Scheme: {scheme} (Modulation)", fontsize=12, fontweight='bold', color=color)
        
        # 画发送信号 (半透明填充，表示理想波形)
        ax.plot(t, tx_signal, color=color, alpha=0.4, linewidth=1, label='Tx (Clean)')
        ax.fill_between(t, tx_signal, alpha=0.1, color=color)
        
        # 画接收信号 (实线，表示实际波形)
        # ax.plot(t, rx_signal[:len(t)], color='black', alpha=0.6, linewidth=0.8, linestyle='--', label='Rx (Noisy)')
        
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

    plt.savefig('modulation_visualization.png',dpi=320)

    print("✅ 对比绘图完成。")
    plt.show()

if __name__ == "__main__":
    visualize_all_schemes()