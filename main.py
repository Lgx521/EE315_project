import numpy as np
import time
import copy
from cable import Cable

# ============================================================================
# 全局事件记录器 (SIM_EVENTS)
# 供 visualization.py 读取，用于绘制时序图
# ============================================================================
SIM_EVENTS = []

def record_event(time_point, host_id, action, seq, ptype, status="Success"):
    """
    统一记录仿真事件
    :param action: "Send", "Receive", "Timeout"
    :param status: "Success", "Lost"
    """
    SIM_EVENTS.append({
        "time": time_point,
        "host": host_id,
        "action": action,
        "seq": seq,
        "type": ptype,
        "status": status
    })

# ============================================================================
# 1. 工具类 (Utils)
# ============================================================================
class Utils:
    @staticmethod
    def str_to_bits(s):
        """字符串 -> 比特流"""
        result = []
        for char in s:
            bin_val = bin(ord(char))[2:].zfill(8)
            result.extend([int(b) for b in bin_val])
        return result

    @staticmethod
    def bits_to_str(bits):
        """比特流 -> 字符串"""
        chars = []
        for i in range(0, len(bits), 8):
            byte = bits[i:i+8]
            if len(byte) < 8: break
            str_val = "".join(str(b) for b in byte)
            chars.append(chr(int(str_val, 2)))
        return "".join(chars)

    @staticmethod
    def calculate_crc(bits):
        """CRC-8 校验和计算"""
        checksum = sum(bits) % 256
        return [int(b) for b in bin(checksum)[2:].zfill(8)]

# ============================================================================
# 2. 应用层协议 (Application Layer)
# ============================================================================
class AppLayer:
    """简单的应用层协议模拟"""
    @staticmethod
    def create_request(method, content):
        return f"{method} {content}"
    
    @staticmethod
    def create_response(code, content):
        return f"{code} {content}"

    @staticmethod
    def parse(message):
        parts = message.split(' ', 1)
        if len(parts) < 2: return {'type': 'RAW', 'content': message}
        return {'type': parts[0], 'content': parts[1]}

# ============================================================================
# 3. 物理层 (Modem) - 支持多种调制方式
# ============================================================================
class Modem:
    """
    支持调制方式: ASK, FSK, BPSK
    """
    def __init__(self, sample_rate=1000, samples_per_bit=20):
        self.sample_rate = sample_rate
        self.samples_per_bit = samples_per_bit
        # 同步前导码
        self.preamble = [1, 0, 1, 0, 1, 0, 1, 0]
        
        # 预生成载波 (用于 BPSK 和 FSK)
        self.t = np.linspace(0, 1, self.samples_per_bit, endpoint=False)
        
        # BPSK 载波: 2 cycles per bit
        self.carrier_bpsk = np.sin(2 * np.pi * 2 * self.t)
        
        # FSK 载波: f1 (Mark/1) = 2 cycles, f2 (Space/0) = 1 cycle
        self.carrier_f1 = np.sin(2 * np.pi * 2 * self.t)
        self.carrier_f2 = np.sin(2 * np.pi * 1 * self.t)

    def modulate(self, bits, scheme='ASK'):
        """调制入口: Bits -> Signal"""
        tx_bits = self.preamble + bits
        signal = []
        
        if scheme == 'ASK':
            for b in tx_bits:
                val = 1.0 if b == 1 else -1.0 # 双极性 ASK
                signal.extend([val] * self.samples_per_bit)
                
        elif scheme == 'BPSK':
            for b in tx_bits:
                wave = self.carrier_bpsk if b == 1 else -self.carrier_bpsk
                signal.extend(wave)
                
        elif scheme == 'FSK':
            for b in tx_bits:
                wave = self.carrier_f1 if b == 1 else self.carrier_f2
                signal.extend(wave)
                
        return np.array(signal)

    def demodulate(self, signal, scheme='ASK'):
        """解调入口: Signal -> Bits"""
        if signal is None or len(signal) == 0: return []
        
        # 1. 简单的能量检测同步
        threshold = 0.3
        start_index = 0
        for i, val in enumerate(signal):
            if abs(val) > threshold:
                start_index = i
                break
        
        # 截取有效信号
        signal = signal[start_index:]
        num_bits = len(signal) // self.samples_per_bit
        decoded_bits = []

        # 2. 逐比特解调
        for i in range(num_bits):
            segment = signal[i*self.samples_per_bit : (i+1)*self.samples_per_bit]
            if len(segment) < self.samples_per_bit: break
            
            bit = 0
            if scheme == 'ASK':
                bit = 1 if np.mean(segment) > 0 else 0
                
            elif scheme == 'BPSK':
                # 相干解调
                score = np.sum(segment * self.carrier_bpsk)
                bit = 1 if score > 0 else 0
                
            elif scheme == 'FSK':
                # 相关解调
                s1 = np.sum(segment * self.carrier_f1)
                s0 = np.sum(segment * self.carrier_f2)
                bit = 1 if s1 > s0 else 0
                
            decoded_bits.append(bit)
            
        # 3. 移除前导码
        if len(decoded_bits) > len(self.preamble):
            return decoded_bits[len(self.preamble):]
        return []

# ============================================================================
# 4. 无线信道 (WirelessChannel) [Bonus]
# ============================================================================
class WirelessChannel(Cable):
    """
    模拟无线信道，增加瑞利衰落 (Rayleigh Fading)
    """
    def transmit(self, signal):
        # 1. 父类基础传输 (衰减 + 加性高斯白噪声)
        base_signal = super().transmit(signal)
        
        # 2. 模拟多径效应导致的瑞利衰落
        fading_factor = np.random.rayleigh(scale=0.9)
        fading_factor = np.clip(fading_factor, 0.2, 1.5)
        
        return base_signal * fading_factor

# ============================================================================
# 5. 网络层 (Packet & Host)
# ============================================================================
class Packet:
    def __init__(self, src, dst, payload_str, type='DATA', seq=0):
        self.src = src
        self.dst = dst
        self.type = type
        self.seq = seq
        self.payload = payload_str

    def to_bits(self):
        # 简化的头部封装
        header_vals = [self.src, self.dst, 1 if self.type=='DATA' else 2, self.seq, len(self.payload)]
        bits = []
        for val in header_vals:
            bits.extend([int(b) for b in bin(val)[2:].zfill(8)]) # 8-bit fields
        
        # 载荷
        payload_bits = Utils.str_to_bits(self.payload)
        # 长度字段修正 (字节长度)
        len_bits = [int(b) for b in bin(len(payload_bits)//8)[2:].zfill(8)]
        # 替换上面的 header 里的长度占位 (简单起见重新组装)
        
        # 正确组装顺序: SRC, DST, TYPE, SEQ, LEN
        data = []
        data.extend([int(b) for b in bin(self.src)[2:].zfill(8)])
        data.extend([int(b) for b in bin(self.dst)[2:].zfill(8)])
        data.extend([int(b) for b in bin(1 if self.type=='DATA' else 2)[2:].zfill(8)])
        data.extend([int(b) for b in bin(self.seq % 256)[2:].zfill(8)])
        data.extend([int(b) for b in bin(len(payload_bits) // 8)[2:].zfill(8)])
        data.extend(payload_bits)
        
        # CRC
        crc_bits = Utils.calculate_crc(data)
        return data + crc_bits

    @staticmethod
    def from_bits(bits):
        if len(bits) < 48: return None
        
        def bits_to_int(b): return int("".join(map(str, b)), 2)
        
        src = bits_to_int(bits[0:8])
        dst = bits_to_int(bits[8:16])
        type_int = bits_to_int(bits[16:24])
        seq = bits_to_int(bits[24:32])
        length = bits_to_int(bits[32:40])
        
        payload_start = 40
        payload_end = payload_start + length * 8
        if payload_end + 8 > len(bits): return None
        
        payload_bits = bits[payload_start:payload_end]
        received_crc = bits[payload_end:payload_end+8]
        calculated_crc = Utils.calculate_crc(bits[0:payload_end])
        
        if received_crc != calculated_crc: return None
        
        msg_type = 'DATA' if type_int == 1 else 'ACK'
        return Packet(src, dst, Utils.bits_to_str(payload_bits), msg_type, seq)

class Host:
    def __init__(self, address, cable, mod_scheme='ASK'):
        self.address = address
        self.cable = cable
        self.mod_scheme = mod_scheme # 当前使用的调制方式
        self.modem = Modem()
        
        self.next_seq = 0
        self.received_seqs = set()
        self.pending_acks = {} 
        self.timeout_interval = 3.0
        self.server_files = {'/index.html': '<html>Hello World</html>'}

    def send(self, target_address, message, current_time, reliable=True):
        """发送数据: 返回 (signal, packet_object)"""
        print(f"[Host {self.address}] Sending SEQ={self.next_seq} to {target_address}: '{message}' ({self.mod_scheme})")
        packet = Packet(self.address, target_address, message, 'DATA', seq=self.next_seq)
        
        if reliable:
            self.pending_acks[self.next_seq] = {'packet': packet, 'sent_time': current_time}
            self.next_seq += 1
            
        signal = self._transmit_packet(packet)
        return signal, packet

    def _transmit_packet(self, packet):
        bits = packet.to_bits()
        return self.modem.modulate(bits, scheme=self.mod_scheme)

    def receive(self, analog_signal, current_time):
        """
        接收数据: 返回 (response_signal, app_data, response_packet)
        """
        bits = self.modem.demodulate(analog_signal, scheme=self.mod_scheme)
        if not bits: return None, None, None
        
        packet = Packet.from_bits(bits)
        if packet is None: return None, None, None # CRC Error

        response_signal = None
        response_packet = None
        app_data = None

        if packet.dst == self.address:
            # 记录接收事件 (Receive)
            record_event(current_time, self.address, "Receive", packet.seq, packet.type)

            if packet.type == 'ACK':
                print(f"[Host {self.address}] 🆗 Received ACK for SEQ={packet.seq}")
                if packet.seq in self.pending_acks:
                    del self.pending_acks[packet.seq]
            
            elif packet.type == 'DATA':
                packet_id = (packet.src, packet.seq)
                if packet_id in self.received_seqs:
                    print(f"[Host {self.address}] ⚠️ Duplicate SEQ={packet.seq}, resending ACK.")
                else:
                    print(f"[Host {self.address}] ✅ RECEIVED SEQ={packet.seq}: '{packet.payload}'")
                    self.received_seqs.add(packet_id)
                    app_data = packet.payload
                    # 简单触发一下应用层
                    self._handle_app_layer(packet.payload)

                # 生成 ACK
                response_packet = Packet(self.address, packet.src, "ACK", 'ACK', seq=packet.seq)
                response_signal = self._transmit_packet(response_packet)

        return response_signal, app_data, response_packet

    def _handle_app_layer(self, payload):
        parsed = AppLayer.parse(payload)
        return parsed['type'] == 'GET'

    def check_timeouts(self, current_time):
        """检查超时: 返回 [(signal, packet), ...]"""
        retransmit_data = []
        for seq, info in self.pending_acks.items():
            if current_time - info['sent_time'] > self.timeout_interval:
                print(f"[Host {self.address}] ⏳ Timeout for SEQ={seq}. Retransmitting...")
                record_event(current_time, self.address, "Timeout", seq, "EVENT")
                
                info['sent_time'] = current_time
                packet = info['packet']
                signal = self._transmit_packet(packet)
                retransmit_data.append((signal, packet))
        return retransmit_data

# ============================================================================
# 6. 主程序 (参数化入口)
# ============================================================================

def run_simulation(target_scheme='ASK'):
    """
    运行单次完整的仿真流程 (用于 visualization.py 调用)
    :param target_scheme: 指定调制方式 (ASK, FSK, BPSK)
    """
    global SIM_EVENTS
    # 如果作为独立脚本运行，清空事件；被调用时由调用者控制
    if __name__ == "__main__":
        SIM_EVENTS.clear()

    print(f"\n--- Starting Simulation (Scheme={target_scheme}) ---")
    
    channel = WirelessChannel(length=50, attenuation=0.0, noise_level=0.1)
    client = Host(address=1, cable=channel, mod_scheme=target_scheme)
    server = Host(address=2, cable=channel, mod_scheme=target_scheme)
    
    sim_state = {'time': 0.0}
    
    def propagate(sender, signal, packet_obj):
        """递归传播信号"""
        # [Fix] 使用 is not None 检查，避免 numpy 数组真值歧义
        if signal is None or packet_obj is None: return
        t = sim_state['time']
        
        # 模拟物理传输
        rx_signal = channel.transmit(signal)
        
        # 丢包区间 (4.0s - 6.0s)
        is_loss_period = (4.0 < t < 6.0)
        
        if is_loss_period:
            print(f"   >>> [CHANNEL FAILURE] Signal lost! (Time={t})")
            record_event(t, sender.address, "Send", packet_obj.seq, packet_obj.type, "Lost")
            return 

        # 记录成功发送
        record_event(t, sender.address, "Send", packet_obj.seq, packet_obj.type, "Success")

        receiver = server if sender == client else client
        
        # 接收 (0.5s 延迟)
        resp_signal, _, resp_packet = receiver.receive(rx_signal, t + 0.5)
        
        # ACK 回传
        # [Fix] 使用 is not None 检查
        if resp_signal is not None and resp_packet is not None:
            propagate(receiver, resp_signal, resp_packet)

    # 1. 正常请求
    print(f"[Time={sim_state['time']}] Scenario 1: Normal Request")
    sig, pkt = client.send(2, "GET /index.html", sim_state['time'])
    propagate(client, sig, pkt)
    
    sim_state['time'] += 2.0 
    
    # 2. 第二个正常请求
    print(f"[Time={sim_state['time']}] Scenario 2: Second Request")
    sig, pkt = client.send(2, "DATA 2", sim_state['time'])
    propagate(client, sig, pkt)

    sim_state['time'] += 3.0

    # 3. 丢包与重传
    print(f"[Time={sim_state['time']}] Scenario 3: Loss & Retransmission")
    # Time=5.0 -> Lost
    sig, pkt = client.send(2, "CRITICAL", sim_state['time']) 
    propagate(client, sig, pkt) 
    
    print("... Waiting for timeout ...")
    sim_state['time'] += 4.0 # Time=9.0 -> Timeout
    
    # 检查超时
    retries = client.check_timeouts(sim_state['time'])
    for sig, pkt in retries:
        propagate(client, sig, pkt)

if __name__ == "__main__":
    # 默认作为独立脚本运行时，跑一遍 ASK
    run_simulation('ASK')
    print(f"\nSimulation finished with {len(SIM_EVENTS)} events recorded.")