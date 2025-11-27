import numpy as np
import time
import copy
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
        """简单CRC-8校验"""
        checksum = sum(bits) % 256
        return [int(b) for b in bin(checksum)[2:].zfill(8)]

# ============================================================================
# 2. 物理层 (Modem)
# ============================================================================

class Modem:
    def __init__(self, sample_rate=100, samples_per_bit=10):
        self.sample_rate = sample_rate
        self.samples_per_bit = samples_per_bit
        self.high_level = 1.0
        self.low_level = -1.0
        self.preamble = [1, 0, 1, 0, 1, 0, 1, 0] 

    def modulate(self, bits):
        tx_bits = self.preamble + bits
        signal = []
        for b in tx_bits:
            val = self.high_level if b == 1 else self.low_level
            signal.extend([val] * self.samples_per_bit)
        return np.array(signal)

    def demodulate(self, signal):
        threshold = (self.high_level + self.low_level) / 2
        
        # 简单同步：寻找信号能量起始点（简化处理）
        # 实际应使用相关性计算
        start_index = 0
        for i, val in enumerate(signal):
            if abs(val) > 0.5: # 简单的噪声门限
                start_index = i
                break
        
        # 稍微向后偏移一点以跳过不稳定区域
        signal = signal[start_index:]
        
        num_bits = len(signal) // self.samples_per_bit
        decoded_bits = []
        
        for i in range(num_bits):
            start = i * self.samples_per_bit
            end = start + self.samples_per_bit
            segment = signal[start:end]
            if len(segment) == 0: break
            avg = np.mean(segment)
            decoded_bits.append(1 if avg > threshold else 0)
            
        # 移除前导码 (Preamble)
        # 这里进行简单的模式匹配
        preamble_len = len(self.preamble)
        if len(decoded_bits) > preamble_len:
            # 检查前几个比特是否大概符合前导码（简化：直接切除）
            return decoded_bits[preamble_len:]
        else:
            return []

# ============================================================================
# 3. 网络层 (Packet & Host)
# ============================================================================

class Packet:
    """
    更新后的数据包结构：
    [SRC(8)] [DST(8)] [TYPE(8)] [SEQ(8)] [LEN(8)] [PAYLOAD...] [CRC(8)]
    增加了 SEQ 字段
    """
    def __init__(self, src, dst, payload_str, type='DATA', seq=0):
        self.src = src
        self.dst = dst
        self.type = type      # 'DATA' or 'ACK'
        self.seq = seq        # 序列号
        self.payload = payload_str

    def to_bits(self):
        src_bits = [int(b) for b in bin(self.src)[2:].zfill(8)]
        dst_bits = [int(b) for b in bin(self.dst)[2:].zfill(8)]
        
        type_map = {'DATA': 1, 'ACK': 2}
        type_bits = [int(b) for b in bin(type_map.get(self.type, 0))[2:].zfill(8)]
        
        # 序列号 (8 bits)
        seq_bits = [int(b) for b in bin(self.seq % 256)[2:].zfill(8)]
        
        payload_bits = Utils.str_to_bits(self.payload)
        len_bits = [int(b) for b in bin(len(payload_bits) // 8)[2:].zfill(8)]
        
        header = src_bits + dst_bits + type_bits + seq_bits + len_bits
        data = header + payload_bits
        crc_bits = Utils.calculate_crc(data)
        
        return data + crc_bits

    @staticmethod
    def from_bits(bits):
        # 头部现在是 5 bytes (40 bits) + CRC 1 byte
        if len(bits) < 48: 
            return None
        
        def bits_to_int(b): return int("".join(map(str, b)), 2)
        
        src = bits_to_int(bits[0:8])
        dst = bits_to_int(bits[8:16])
        msg_type_int = bits_to_int(bits[16:24])
        seq = bits_to_int(bits[24:32]) # 读取序列号
        length = bits_to_int(bits[32:40])
        
        msg_type = 'DATA' if msg_type_int == 1 else 'ACK'
        
        payload_start = 40
        payload_end = payload_start + length * 8
        
        if payload_end + 8 > len(bits): # 长度检查
            return None

        payload_bits = bits[payload_start:payload_end]
        received_crc = bits[payload_end:payload_end+8]
        
        # CRC 校验
        calculated_crc = Utils.calculate_crc(bits[0:payload_end])
        if received_crc != calculated_crc:
            return None # 校验失败
            
        payload_str = Utils.bits_to_str(payload_bits)
        return Packet(src, dst, payload_str, msg_type, seq)


class Host:
    def __init__(self, address, cable):
        self.address = address
        self.cable = cable
        self.modem = Modem()
        
        # --- 可靠传输状态 ---
        self.next_seq = 0            # 下一个发送的序列号
        self.received_seqs = set()   # 已处理的序列号（用于去重）
        
        # 待确认列表: { seq_num: {'packet': PacketObj, 'sent_time': timestamp} }
        self.pending_acks = {}       
        self.timeout_interval = 3.0  # 超时时间 (模拟时间单位)

    def send(self, target_address, message, current_time, reliable=True):
        """发送消息，如果 reliable=True，则加入重传队列"""
        print(f"[Host {self.address}] Sending SEQ={self.next_seq} to {target_address}: '{message}'")
        
        packet = Packet(self.address, target_address, message, 'DATA', seq=self.next_seq)
        
        # 1. 记录到待确认列表 (Level 3: Retransmission)
        if reliable:
            self.pending_acks[self.next_seq] = {
                'packet': packet,
                'sent_time': current_time
            }
            self.next_seq += 1 # 准备下一个序列号
            
        # 2. 物理发送
        return self._transmit_packet(packet)

    def _transmit_packet(self, packet):
        """辅助函数：将包转为信号并返回"""
        bits = packet.to_bits()
        return self.modem.modulate(bits)

    def receive(self, analog_signal):
        """接收处理，返回可能需要立即发送的信号（如ACK）"""
        bits = self.modem.demodulate(analog_signal)
        if not bits: return None
            
        packet = Packet.from_bits(bits)
        if packet is None: return None # CRC 失败

        if packet.dst == self.address:
            # --- 处理 ACK 包 ---
            if packet.type == 'ACK':
                print(f"[Host {self.address}] 🆗 Received ACK for SEQ={packet.seq}")
                if packet.seq in self.pending_acks:
                    del self.pending_acks[packet.seq] # 移除待确认项，停止计时
                return None

            # --- 处理 DATA 包 ---
            elif packet.type == 'DATA':
                # Level 3: 避免重复处理
                packet_id = (packet.src, packet.seq)
                if packet_id in self.received_seqs:
                    print(f"[Host {self.address}] ⚠️ Duplicate SEQ={packet.seq} received, resending ACK.")
                else:
                    print(f"[Host {self.address}] ✅ RECEIVED SEQ={packet.seq}: '{packet.payload}'")
                    self.received_seqs.add(packet_id)

                # Level 3: 发送 ACK
                # ACK 的序列号应与收到的 DATA 序列号一致
                ack_packet = Packet(self.address, packet.src, "ACK", 'ACK', seq=packet.seq)
                return self._transmit_packet(ack_packet)
                
        return None

    def check_timeouts(self, current_time):
        """
        [Level 3] 检查超时并重传
        返回：需要重传的信号列表
        """
        retransmit_signals = []
        for seq, info in self.pending_acks.items():
            if current_time - info['sent_time'] > self.timeout_interval:
                print(f"[Host {self.address}] ⏳ Timeout for SEQ={seq}. Retransmitting...")
                # 重传逻辑
                info['sent_time'] = current_time # 重置计时器
                signal = self._transmit_packet(info['packet'])
                retransmit_signals.append(signal)
        return retransmit_signals

# ============================================================================
# 4. 模拟主循环 (Simulation Loop)
# ============================================================================

def run_simulation():
    print("="*60)
    print("Network Simulation: Reliability, Sequence Numbers & Retransmission")
    print("="*60)

    # 创建带噪声的信道 (Level 1)
    cable = Cable(length=50, attenuation=0.0, noise_level=0.1)
    
    host_A = Host(address=10, cable=cable)
    host_B = Host(address=20, cable=cable)
    
    # 模拟时间
    sim_time = 0.0
    
    # 辅助函数：模拟总线上的信号传播
    def propagate_signal(sender, signal):
        if signal is None: return
        # 1. 信号通过 Cable
        rx_signal = cable.transmit(signal)
        
        # 2. 模拟丢包 (为了测试重传，我们随机丢弃一些信号)
        # 这里我们硬编码：如果是特定的时间点，强制“信号丢失”（不传给接收方）
        # 假设我们在 Time=5.0 时的信号被丢弃了
        if 4.0 < sim_time < 6.0:
            print(f"   >>> [CHANNEL FAILURE] Signal lost in transmission! (Time={sim_time})")
            return 

        # 3. 接收方处理
        receiver = host_B if sender == host_A else host_A
        response_signal = receiver.receive(rx_signal)
        
        # 4. 如果接收方回发了信号 (ACK)，递归传播
        if response_signal is not None:
            propagate_signal(receiver, response_signal)

    # --- 场景 1: 正常传输 ---
    print(f"\n[Time={sim_time}] Scenario 1: Normal Transmission")
    signal = host_A.send(20, "Hello B", current_time=sim_time)
    propagate_signal(host_A, signal)
    
    # 推进时间
    sim_time += 2.0 
    
    # --- 场景 2: 模拟丢包与超时重传 ---
    print(f"\n[Time={sim_time}] Scenario 2: Packet Loss & Retransmission")
    # 这次发送的数据将在 propagate_signal 中被“丢弃” (因为 sim_time=5.0 在 4.0-6.0 区间)
    signal = host_A.send(20, "This will be lost", current_time=sim_time) # SEQ应该增加了
    propagate_signal(host_A, signal) # 这里会触发 CHANNEL FAILURE
    
    # 此时 Host A 的 pending_acks 里仍然有这个包
    print(f"   Host A pending ACKs: {list(host_A.pending_acks.keys())}")
    
    # 推进时间 (模拟等待)
    print("\n... Ticking time forward ...")
    sim_time += 4.0 # 现在 Time = 9.0，超过了 timeout (3.0)
    
    # 检查超时
    print(f"[Time={sim_time}] Checking timeouts...")
    # Host A 检查超时，应该返回重传信号
    retry_signals = host_A.check_timeouts(sim_time)
    
    for sig in retry_signals:
        # 重传的信号应该能成功 (因为现在时间不在丢包区间)
        propagate_signal(host_A, sig)

    # --- 场景 3: 模拟 ACK 丢失 (导致重复包) ---
    print(f"\n[Time={sim_time}] Scenario 3: ACK Loss (Duplicate Handling)")
    # 我们这里手动模拟：B 收到了，但 B 发回的 ACK 在路上丢了
    # 为了演示，我们手动操作 Host B 接收，并拦截其 ACK
    
    msg = "ACK will be lost"
    packet = Packet(10, 20, msg, 'DATA', seq=host_A.next_seq)
    # Host A 记录发送
    host_A.pending_acks[host_A.next_seq] = {'packet': packet, 'sent_time': sim_time}
    host_A.next_seq += 1
    
    # 手动让 B 接收 (不经过 propagate_signal，确保 B 收到)
    print(f"[Host 10] Sending SEQ={packet.seq} (Simulating ACK loss)")
    tx_signal = host_A._transmit_packet(packet)
    rx_signal = cable.transmit(tx_signal) # 物理传输
    ack_signal = host_B.receive(rx_signal) # B 收到并产生 ACK
    
    print("   >>> [CHANNEL FAILURE] ACK lost on the way back to A!")
    # 我们故意不把 ack_signal 传回给 A
    
    # 时间流逝，A 超时重传
    sim_time += 4.0
    print(f"\n[Time={sim_time}] A timeouts and retransmits SEQ={packet.seq}")
    retry_signals = host_A.check_timeouts(sim_time)
    
    for sig in retry_signals:
        # A 重传相同的数据包
        # B 应该检测到重复，不向上层递交，但重发 ACK
        propagate_signal(host_A, sig)

if __name__ == "__main__":
    run_simulation()