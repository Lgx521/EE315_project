import numpy as np
import time
import copy
from cable import Cable

# 1. 工具类 (Utils)

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
        """[Level 3] CRC 校验和计算"""
        checksum = sum(bits) % 256
        return [int(b) for b in bin(checksum)[2:].zfill(8)]

# ============================================================================
# 2. [Level 3 Extension] 应用层协议 (Application Layer)
# ============================================================================

class AppLayer:
    """
    [Level 3] 简单的应用层协议模拟 (类似 HTTP)
    格式: METHOD CONTENT
    """
    @staticmethod
    def create_request(method, content):
        """创建请求, e.g., 'GET /index.html'"""
        return f"{method} {content}"
    
    @staticmethod
    def create_response(code, content):
        """创建响应, e.g., '200 OK: Data'"""
        return f"{code} {content}"

    @staticmethod
    def parse(message):
        """解析应用层消息"""
        parts = message.split(' ', 1)
        if len(parts) < 2:
            return {'type': 'RAW', 'content': message}
        return {'type': parts[0], 'content': parts[1]}

# ============================================================================
# 3. 物理层 (Modem) - Level 1
# ============================================================================

class Modem:
    def __init__(self, sample_rate=100, samples_per_bit=10):
        self.sample_rate = sample_rate
        self.samples_per_bit = samples_per_bit
        # 调制参数 (ASK)
        self.high_level = 1.0
        self.low_level = -1.0
        # 同步前导码
        self.preamble = [1, 0, 1, 0, 1, 0, 1, 0] 

    def modulate(self, bits):
        """[Level 1] 调制: Bits -> Analog Signal"""
        tx_bits = self.preamble + bits
        signal = []
        for b in tx_bits:
            val = self.high_level if b == 1 else self.low_level
            signal.extend([val] * self.samples_per_bit)
        return np.array(signal)

    def demodulate(self, signal):
        """[Level 1] 解调: Analog Signal -> Bits"""
        if signal is None or len(signal) == 0:
            return []

        threshold = (self.high_level + self.low_level) / 2
        
        # 简单同步: 寻找信号能量起始点
        start_index = 0
        for i, val in enumerate(signal):
            if abs(val) > 0.5: # 简单的能量检测
                start_index = i
                break
        
        signal = signal[start_index:]
        num_bits = len(signal) // self.samples_per_bit
        decoded_bits = []
        
        # 积分判决 (Integrate and Dump)
        for i in range(num_bits):
            start = i * self.samples_per_bit
            end = start + self.samples_per_bit
            segment = signal[start:end]
            if len(segment) == 0: break
            avg = np.mean(segment)
            decoded_bits.append(1 if avg > threshold else 0)
        
        # 移除前导码
        preamble_len = len(self.preamble)
        if len(decoded_bits) > preamble_len:
            return decoded_bits[preamble_len:]
        else:
            return []

# ============================================================================
# 4. 网络层 (Packet & Host) - Level 2 & 3
# ============================================================================

class Packet:
    """
    数据包结构:
    [SRC] [DST] [TYPE] [SEQ] [LEN] [PAYLOAD] [CRC]
    """
    def __init__(self, src, dst, payload_str, type='DATA', seq=0):
        self.src = src
        self.dst = dst
        self.type = type # 'DATA' or 'ACK'
        self.seq = seq   # [Level 3] Sequence Number
        self.payload = payload_str

    def to_bits(self):
        # 头部封装
        src_bits = [int(b) for b in bin(self.src)[2:].zfill(8)]
        dst_bits = [int(b) for b in bin(self.dst)[2:].zfill(8)]
        
        type_map = {'DATA': 1, 'ACK': 2}
        type_bits = [int(b) for b in bin(type_map.get(self.type, 0))[2:].zfill(8)]
        
        seq_bits = [int(b) for b in bin(self.seq % 256)[2:].zfill(8)]
        
        payload_bits = Utils.str_to_bits(self.payload)
        len_bits = [int(b) for b in bin(len(payload_bits) // 8)[2:].zfill(8)]
        
        header = src_bits + dst_bits + type_bits + seq_bits + len_bits
        data = header + payload_bits
        
        # [Level 3] CRC 计算与附加
        crc_bits = Utils.calculate_crc(data)
        return data + crc_bits

    @staticmethod
    def from_bits(bits):
        # 最小长度检查 (Header 5 bytes + CRC 1 byte = 48 bits)
        if len(bits) < 48: 
            return None
        
        def bits_to_int(b): return int("".join(map(str, b)), 2)
        
        src = bits_to_int(bits[0:8])
        dst = bits_to_int(bits[8:16])
        msg_type_int = bits_to_int(bits[16:24])
        seq = bits_to_int(bits[24:32])
        length = bits_to_int(bits[32:40])
        
        msg_type = 'DATA' if msg_type_int == 1 else 'ACK'
        
        payload_start = 40
        payload_end = payload_start + length * 8
        
        if payload_end + 8 > len(bits): 
            return None # 长度不匹配

        payload_bits = bits[payload_start:payload_end]
        received_crc = bits[payload_end:payload_end+8]
        
        # [Level 3] CRC 校验
        calculated_crc = Utils.calculate_crc(bits[0:payload_end])
        if received_crc != calculated_crc:
            return None # 校验失败
            
        payload_str = Utils.bits_to_str(payload_bits)
        return Packet(src, dst, payload_str, msg_type, seq)

class Host:
    def __init__(self, address, cable):
        self.address = address # [Level 2] Addressing
        self.cable = cable
        self.modem = Modem()
        
        # [Level 3] Reliability State
        self.next_seq = 0
        self.received_seqs = set()
        self.pending_acks = {} # {seq: {packet, sent_time}}
        self.timeout_interval = 3.0
        
        # [Level 3] App Layer Server Data
        self.server_files = {
            '/index.html': '<html>Hello World</html>',
            '/api/status': '{"status": "ok"}'
        }

    def send(self, target_address, message, current_time, reliable=True):
        """发送消息接口"""
        print(f"[Host {self.address}] Sending SEQ={self.next_seq} to {target_address}: '{message}'")
        
        packet = Packet(self.address, target_address, message, 'DATA', seq=self.next_seq)
        
        # 加入重传队列
        if reliable:
            self.pending_acks[self.next_seq] = {
                'packet': packet, 
                'sent_time': current_time
            }
            self.next_seq += 1
            
        return self._transmit_packet(packet)

    def _transmit_packet(self, packet):
        bits = packet.to_bits()
        return self.modem.modulate(bits)

    def receive(self, analog_signal):
        """
        接收信号处理
        Returns: (response_signal, app_data)
        """
        # 1. 物理层解调
        bits = self.modem.demodulate(analog_signal)
        if not bits: 
            return None, None
            
        # 2. 链路层解包
        packet = Packet.from_bits(bits)
        if packet is None: 
            return None, None # CRC Error or Format Error

        response_signal = None
        app_data = None

        # [Level 2] 路由过滤 (只处理发给自己的)
        if packet.dst == self.address:
            
            # --- Case A: 收到 ACK ---
            if packet.type == 'ACK':
                print(f"[Host {self.address}] 🆗 Received ACK for SEQ={packet.seq}")
                if packet.seq in self.pending_acks:
                    del self.pending_acks[packet.seq] # 停止计时
            
            # --- Case B: 收到数据 ---
            elif packet.type == 'DATA':
                packet_id = (packet.src, packet.seq)
                
                # [Level 3] 重复包检测
                if packet_id in self.received_seqs:
                    print(f"[Host {self.address}] ⚠️ Duplicate SEQ={packet.seq}, resending ACK.")
                else:
                    print(f"[Host {self.address}] ✅ RECEIVED SEQ={packet.seq} Data: '{packet.payload}'")
                    self.received_seqs.add(packet_id)
                    app_data = packet.payload
                    
                    # [Level 3] 应用层逻辑触发
                    app_response = self._handle_app_layer(packet.payload)
                    if app_response:
                        print(f"[Host {self.address}] 🤖 App Layer Logic: Client asked for resource, Server prepares: '{app_response[:20]}...'")

                # [Level 3] 自动发送 ACK
                ack_packet = Packet(self.address, packet.src, "ACK", 'ACK', seq=packet.seq)
                response_signal = self._transmit_packet(ack_packet)

        return response_signal, app_data

    def _handle_app_layer(self, payload):
        """处理 HTTP 风格请求"""
        parsed = AppLayer.parse(payload)
        if parsed['type'] == 'GET':
            resource = parsed['content']
            if resource in self.server_files:
                return f"200 OK {self.server_files[resource]}"
            else:
                return "404 Not Found"
        return None

    def check_timeouts(self, current_time):
        """[Level 3] 超时重传检查"""
        retransmit_signals = []
        for seq, info in self.pending_acks.items():
            if current_time - info['sent_time'] > self.timeout_interval:
                print(f"[Host {self.address}] ⏳ Timeout for SEQ={seq}. Retransmitting...")
                info['sent_time'] = current_time # Reset timer
                signal = self._transmit_packet(info['packet'])
                retransmit_signals.append(signal)
        return retransmit_signals

# ============================================================================
# 5. 主程序 (Simulation Loop)
# ============================================================================

def run_simulation():
    print("="*60)
    print("Network Simulation")
    print("Included: Reliability, CRC, Application Layer Protocol")
    print("="*60)

    # 初始化信道 (Level 1 Requirement)
    cable = Cable(length=50, attenuation=0.0, noise_level=0.1)
    
    client = Host(address=1, cable=cable)
    server = Host(address=2, cable=cable)
    
    sim_time = 0.0
    
    def propagate_signal(sender, signal):
        """递归传播信号 (处理 ACK)"""
        # 是否测试丢包逻辑  
        is_retrans = False

        if signal is None: 
            return
            
        # 模拟物理传输
        rx_signal = cable.transmit(signal)
        
        # 模拟特定时间段的丢包 (测试重传机制)
        if 4.0 < sim_time < 6.0 and is_retrans:
            print(f"   >>> [CHANNEL FAILURE] Signal lost in transmission! (Time={sim_time})")
            return 

        receiver = server if sender == client else client
        
        # 接收并处理
        response_signal, app_data = receiver.receive(rx_signal)
        
        # [Fix] 显式检查 response_signal 是否存在
        if response_signal is not None:
            # 这里的 response_signal 通常是 ACK
            propagate_signal(receiver, response_signal)

    # --- 场景 1: 应用层请求 (HTTP GET) ---
    print(f"\n[Time={sim_time}] Scenario 1: App Layer - Client requests file")
    req_msg = AppLayer.create_request("GET", "/index.html")
    signal = client.send(2, req_msg, current_time=sim_time)
    propagate_signal(client, signal)
    
    sim_time += 2.0 
    
    # --- 场景 2: 应用层请求 (404 Not Found) ---
    print(f"\n[Time={sim_time}] Scenario 2: App Layer - Client requests missing file")
    req_msg = AppLayer.create_request("GET", "/secret.txt")
    signal = client.send(2, req_msg, current_time=sim_time)
    propagate_signal(client, signal)

    sim_time += 3.0

    # --- 场景 3: 丢包与重传机制 ---
    print(f"\n[Time={sim_time}] Scenario 3: Packet Loss & Retransmission")
    signal = client.send(2, "Critical Data", current_time=sim_time) 
    # 注意：此时 sim_time=5.0，处于丢包区间 (4.0 - 6.0)
    propagate_signal(client, signal) 
    
    print("\n... Simulating wait time for timeout ...")
    sim_time += 4.0 # 时间流逝，触发超时
    
    # 检查客户端的超时队列
    retry_signals = client.check_timeouts(sim_time)
    for sig in retry_signals:
        # 重传 (此时时间已过丢包区间，应该成功)
        propagate_signal(client, sig)

if __name__ == "__main__":
    run_simulation()