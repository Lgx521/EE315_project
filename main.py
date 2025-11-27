import numpy as np
import struct
import time
from cable import Cable

# ============================================================================
# 1. 工具类 (Utils)
# ============================================================================

class Utils:
    @staticmethod
    def str_to_bits(s):
        """将字符串转换为比特列表 [0, 1, ...]"""
        result = []
        for char in s:
            # 获取字符的ASCII值，转为8位二进制
            bin_val = bin(ord(char))[2:].zfill(8)
            result.extend([int(b) for b in bin_val])
        return result

    @staticmethod
    def bits_to_str(bits):
        """将比特列表转换回字符串"""
        chars = []
        for i in range(0, len(bits), 8):
            byte = bits[i:i+8]
            if len(byte) < 8: break
            str_val = "".join(str(b) for b in byte)
            chars.append(chr(int(str_val, 2)))
        return "".join(chars)

    @staticmethod
    def calculate_crc(bits):
        """简单的CRC-8校验模拟 (用于演示)"""
        # 这里使用简单的求和校验作为替代，演示原理
        # 实际工程应使用多项式除法
        checksum = sum(bits) % 256
        return [int(b) for b in bin(checksum)[2:].zfill(8)]

# ============================================================================
# 2. 物理层 (Physical Layer - Modem)
# ============================================================================

class Modem:
    """
    调制解调器
    负责：比特流 <---> 模拟信号
    """
    def __init__(self, sample_rate=100, samples_per_bit=10):
        self.sample_rate = sample_rate
        self.samples_per_bit = samples_per_bit
        # 简单幅移键控 (ASK): 1 -> 1.0V, 0 -> -1.0V (双极性更好抗噪)
        self.high_level = 1.0
        self.low_level = -1.0
        
        # 扩频/同步头：用于帮助解调器找到信号开始的位置
        # 发送 10101010 作为前导码
        self.preamble = [1, 0, 1, 0, 1, 0, 1, 0] 

    def modulate(self, bits):
        """[Level 1] 调制: 将比特流转换为模拟波形"""
        # 1. 添加前导码 (Preamble) 以便接收端同步
        tx_bits = self.preamble + bits
        
        signal = []
        for b in tx_bits:
            val = self.high_level if b == 1 else self.low_level
            # 每个比特重复 samples_per_bit 次 (矩形波)
            signal.extend([val] * self.samples_per_bit)
            
        return np.array(signal)

    def demodulate(self, signal):
        """[Level 1] 解调: 将模拟波形恢复为比特流"""
        # 1. 简单的能量检测或阈值判决
        # 由于 Cable 会引入延迟和噪声，我们需要先找到信号的"头"
        
        # 简单处理：我们假设信号足够强，直接按阈值归一化为 0/1
        # 在真实场景中需要做相关性分析(Correlation)来找前导码
        
        digital_signal = []
        threshold = (self.high_level + self.low_level) / 2
        
        # 逐点判决
        raw_bits = [1 if s > threshold else 0 for s in signal]
        
        # 2. 下采样 (Downsampling) - 取每个比特周期的中间点
        # 这里我们做一个简单的同步扫描：寻找前导码模式
        
        # 将原始比特流转为字符串以便查找
        raw_str = "".join(map(str, raw_bits))
        preamble_str = "".join(map(str, self.preamble))
        
        # 扩频后的前导码大概长度
        # 注意：这里为了简化，我们假设没有严重的频率偏移，直接按步长采样
        decoded_bits = []
        
        # 简单的积分判决：每 samples_per_bit 个点取平均
        num_bits = len(signal) // self.samples_per_bit
        
        for i in range(num_bits):
            start = i * self.samples_per_bit
            end = start + self.samples_per_bit
            segment = signal[start:end]
            avg = np.mean(segment)
            decoded_bits.append(1 if avg > threshold else 0)
            
        # 3. 移除前导码
        # 寻找前导码的结束位置。这里简化处理：直接切片
        # 在高噪声下，应该使用滑动窗口匹配前导码
        if len(decoded_bits) > len(self.preamble):
            return decoded_bits[len(self.preamble):]
        else:
            return []

# ============================================================================
# 3. 网络层与链路层 (Host)
# ============================================================================

class Packet:
    """定义数据包结构"""
    def __init__(self, src, dst, payload_str, type='DATA'):
        self.src = src # 源地址 (int)
        self.dst = dst # 目的地址 (int)
        self.type = type # DATA 或 ACK
        self.payload = payload_str

    def to_bits(self):
        """
        封包格式: [SRC(8bit)] [DST(8bit)] [TYPE(8bit)] [LEN(8bit)] [PAYLOAD] [CRC(8bit)]
        """
        src_bits = [int(b) for b in bin(self.src)[2:].zfill(8)]
        dst_bits = [int(b) for b in bin(self.dst)[2:].zfill(8)]
        
        type_map = {'DATA': 1, 'ACK': 2}
        type_bits = [int(b) for b in bin(type_map.get(self.type, 0))[2:].zfill(8)]
        
        payload_bits = Utils.str_to_bits(self.payload)
        len_bits = [int(b) for b in bin(len(payload_bits) // 8)[2:].zfill(8)] # 长度以字节为单位
        
        header = src_bits + dst_bits + type_bits + len_bits
        data = header + payload_bits
        
        # [Level 3] 添加CRC校验
        crc_bits = Utils.calculate_crc(data)
        
        return data + crc_bits

    @staticmethod
    def from_bits(bits):
        """解包"""
        if len(bits) < 40: # 最小头部长度 5 bytes * 8
            return None
        
        # 提取各个字段
        def bits_to_int(b): return int("".join(map(str, b)), 2)
        
        src = bits_to_int(bits[0:8])
        dst = bits_to_int(bits[8:16])
        msg_type_int = bits_to_int(bits[16:24])
        length = bits_to_int(bits[24:32])
        
        msg_type = 'DATA' if msg_type_int == 1 else 'ACK'
        
        payload_end = 32 + length * 8
        payload_bits = bits[32:payload_end]
        received_crc = bits[payload_end:payload_end+8]
        
        # [Level 3] 校验 CRC
        calculated_crc = Utils.calculate_crc(bits[0:payload_end])
        if received_crc != calculated_crc:
            print(f"[ERROR] CRC Check Failed! Data Corrupted.")
            return None
            
        payload_str = Utils.bits_to_str(payload_bits)
        return Packet(src, dst, payload_str, msg_type)


class Host:
    """
    网络主机
    实现 Level 2 (寻址) 和 Level 3 (可靠传输)
    """
    def __init__(self, address, cable):
        self.address = address
        self.cable = cable
        self.modem = Modem()
        self.received_buffer = []

    def send(self, target_address, message, reliable=False):
        """发送消息"""
        print(f"\n[Host {self.address}] Sending to {target_address}: '{message}'")
        
        # 1. 封装数据包
        packet = Packet(self.address, target_address, message, 'DATA')
        bits = packet.to_bits()
        
        # 2. 调制
        analog_signal = self.modem.modulate(bits)
        
        # 3. 物理传输 (通过 Cable)
        # 注意：在真实网络中，这里只是把信号放到介质上。
        # 为了模拟多主机环境，我们假设 Cable 是一个共享总线。
        # 这里我们模拟"广播"，所有连接到这个 Cable 的主机都会收到信号。
        # 实际上 Cable 类是点对点的，所以我们通过外部逻辑把信号传给所有其他主机。
        return analog_signal

    def receive(self, analog_signal):
        """接收并处理信号"""
        # 1. 解调
        bits = self.modem.demodulate(analog_signal)
        if not bits:
            return
            
        # 2. 解包
        packet = Packet.from_bits(bits)
        if packet is None:
            return # CRC失败或格式错误

        # 3. [Level 2] 地址过滤
        if packet.dst == self.address:
            if packet.type == 'DATA':
                print(f"[Host {self.address}] ✅ RECEIVED from {packet.src}: '{packet.payload}'")
                # [Level 3] 自动发送 ACK
                self.send_ack(packet.src)
            elif packet.type == 'ACK':
                print(f"[Host {self.address}] 🆗 ACK Received from {packet.src}")
        else:
            # 这里的 Debug 信息用于证明地址过滤在工作
            # print(f"[Host {self.address}] Ignored packet for {packet.dst}")
            pass

    def send_ack(self, target_address):
        """[Level 3] 发送 ACK"""
        packet = Packet(self.address, target_address, "ACK", 'ACK')
        bits = packet.to_bits()
        signal = self.modem.modulate(bits)
        # 在这里我们简化处理，假设ACK通过某种“魔法”回传，
        # 或者在主循环中显式调用 cable 传输。
        # 为了演示代码结构，我们仅仅打印构造好了ACK
        # 实际传输逻辑在 main 的总线模拟中处理
        return signal

# ============================================================================
# 4. 主程序与测试场景
# ============================================================================

def run_simulation():
    print("="*60)
    print("Data Communication Simulation (Level 1, 2, 3)")
    print("="*60)

    # 初始化物理介质
    # 增加一点噪声来测试鲁棒性
    shared_cable = Cable(length=50, attenuation=0.01, noise_level=0.1, debug_mode=False)
    
    # 初始化主机
    host_A = Host(address=1, cable=shared_cable)
    host_B = Host(address=2, cable=shared_cable)
    host_C = Host(address=3, cable=shared_cable) # 用于测试地址过滤
    
    hosts = [host_A, host_B, host_C]
    
    def simulate_bus_transmission(sender, signal):
        """模拟共享总线：一个发，大家收"""
        print(f"--- Transmission on Cable (Length: {len(signal)} samples) ---")
        # 信号通过线缆（增加噪声和衰减）
        transmitted_signal = shared_cable.transmit(signal)
        
        # 广播给除了发送者以外的所有人
        for h in hosts:
            if h.address != sender.address:
                # 尝试接收
                response = h.receive(transmitted_signal)
                # 如果接收者回发了 ACK (Level 3)，我们需要处理这个ACK
                # 这里为了简单，如果 receive 返回了信号(ACK)，我们可以递归调用传输
                # 但这会导致死循环如果逻辑不对，暂不递归处理 ACK 的传输
                
    
    # --- 测试场景 1: Level 1 (基本通信) & Level 2 (寻址) ---
    print("\n>>> Scenario 1: Host A sends to Host B")
    signal = host_A.send(target_address=2, message="Hello World!")
    simulate_bus_transmission(host_A, signal)

    # --- 测试场景 2: Level 2 (地址过滤) ---
    print("\n>>> Scenario 2: Host A sends to Host C (Host B should ignore)")
    signal = host_A.send(target_address=3, message="Secret for C")
    simulate_bus_transmission(host_A, signal)

    # --- 测试场景 3: Level 1 (长消息) & Level 3 (CRC校验) ---
    print("\n>>> Scenario 3: Host B sends long message to A")
    long_msg = "Data Comm is fun when you build it from scratch!"
    signal = host_B.send(target_address=1, message=long_msg)
    simulate_bus_transmission(host_B, signal)
    
    # --- 测试场景 4: 模拟高噪声导致 CRC 失败 ---
    print("\n>>> Scenario 4: High Noise Interference")
    bad_cable = Cable(length=100, attenuation=0.5, noise_level=0.8) # 高噪声
    
    # 手动制造一次传输
    print("[Host 1] Sending critical data...")
    packet = Packet(1, 2, "Critical Data", 'DATA')
    bits = packet.to_bits()
    modem = Modem()
    raw_signal = modem.modulate(bits)
    noisy_signal = bad_cable.transmit(raw_signal)
    
    print("[Host 2] Attempting to receive noisy signal...")
    host_B.receive(noisy_signal) # 应该打印错误或什么都不显示（因为CRC失败）

if __name__ == "__main__":
    run_simulation()