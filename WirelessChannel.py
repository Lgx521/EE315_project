from cable import Cable
import numpy as np
# ============================================================================
# [Bonus: Wireless Communication] 无线信道模拟
# ============================================================================
class WirelessChannel(Cable):
    """
    模拟无线信道，增加瑞利衰落 (Rayleigh Fading) 和 随机相位干扰
    """
    def transmit(self, signal):
        # 1. 调用父类基础传输 (衰减 + 白噪声)
        base_signal = super().transmit(signal)
        
        # 2. 模拟多径效应导致的随机衰落 (Fading)
        # 生成一个瑞利分布的随机系数，乘在信号上
        # scale 参数控制衰落的平均强度
        fading_factor = np.random.rayleigh(scale=0.9)
        
        # 避免衰落系数过大导致信号爆表，或过小导致完全丢失
        fading_factor = np.clip(fading_factor, 0.2, 1.5)
        
        # 应用衰落
        faded_signal = base_signal * fading_factor
        
        return faded_signal