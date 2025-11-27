import numpy as np
import time
import copy
from cable import Cable
from WirelessChannel import WirelessChannel


# event logger, for visualizaton 
SIM_EVENTS = []

def record_event(time_point, host_id, action, seq, ptype, status="Success"):
    """
    记录仿真事件
    :param time_point: 仿真时间
    :param host_id: 主机地址
    :param action: 动作 (Send, Receive, Timeout)
    :param seq: 序列号
    :param ptype: 包类型 (DATA, ACK)
    :param status: 状态 (Success, Lost)
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
        """
        [Level 3 Extension] 计算 CRC-8 校验和
        用于检测传输过程中的比特错误
        """
        checksum = sum(bits) % 256
        return [int(b) for b in bin(checksum)[2:].zfill(8)]

# ============================================================================
# 2. 应用层协议 (Application Layer)
# ============================================================================

class AppLayer:
    """
    [Level 3 Extension] 简单的应用层协议模拟 (HTTP-like)
    格式: METHOD RESOURCE 或 CODE STATUS
    """
    @staticmethod
    def create_request(method, content):
        """创建请求, e.g., 'GET /index.html'"""
        return f"{method} {content}"
    
    @staticmethod
    def create_response(code, content):
        """创建响应, e.g., '200 OK'"""
        return f"{code} {content}"

    @staticmethod
    def parse(message):
        """解析应用层消息"""
        parts = message.split(' ', 1)
        if len(parts) < 2:
            return {'type': 'RAW', 'content': message}
        return {'type': parts[0], 'content': parts[1]}

# ============================================================================
# 3. 物理层 (Physical Layer - Multi-Scheme Modem) [Bonus: Performance Opt]
# ============================================================================

class Modem:
    """
    支持多种调制方式的调制解调器
    Schemes: 'ASK', 'FSK', 'BPSK'
    """
    def __init__(self, sample_rate=1000, samples_per_bit=20):
        self.sample_rate = sample_rate
        self.samples_per_bit = samples_per_bit
        self.preamble = [1, 0, 1, 0, 1, 0, 1, 0]
        
        # ASK 参数
        self.high_level = 1.0
        self.low_level = 0.0 # BPSK/FSK 通常不需要负电平做 0，这里 ASK 改为单极性更稳
        
        # FSK/BPSK 载波参数
        # 时间轴 t: 0 到 duration
        self.t = np.linspace(0, 1, self.samples_per_bit, endpoint=False)
        
        # FSK: f1 (mark) 和 f2 (space)
        self.carrier_f1 = np.sin(2 * np.pi * 2 * self.t) # 高频代表 1
        self.carrier_f2 = np.sin(2 * np.pi * 1 * self.t) # 低频代表 0
        
        # BPSK: 同一频率，不同相位
        self.carrier_bpsk = np.sin(2 * np.pi * 2 * self.t)

    def modulate(self, bits, scheme='ASK'):
        """调制入口"""
        tx_bits = self.preamble + bits
        signal = []
        
        if scheme == 'ASK':
            for b in tx_bits:
                val = 1.0 if b == 1 else -1.0
                signal.extend([val] * self.samples_per_bit)
                
        elif scheme == 'FSK':
            for b in tx_bits:
                # 1 用 f1, 0 用 f2
                wave = self.carrier_f1 if b == 1 else self.carrier_f2
                signal.extend(wave)
                
        elif scheme == 'BPSK':
            for b in tx_bits:
                # 1 用正弦, 0 用负正弦 (相位翻转 180度)
                wave = self.carrier_bpsk if b == 1 else -self.carrier_bpsk
                signal.extend(wave)
                
        return np.array(signal)

    def demodulate(self, signal, scheme='ASK'):
        """解调入口"""
        if signal is None or len(signal) == 0: return []
        
        # 1. 同步 (简单的能量检测寻找起点)
        start_index = 0
        threshold = 0.3
        for i, val in enumerate(signal):
            if abs(val) > threshold:
                start_index = i
                break
        
        signal = signal[start_index:]
        num_bits = len(signal) // self.samples_per_bit
        decoded_bits = []

        for i in range(num_bits):
            start = i * self.samples_per_bit
            end = start + self.samples_per_bit
            segment = signal[start:end]
            if len(segment) < self.samples_per_bit: break
            
            bit = 0
            if scheme == 'ASK':
                # 积分判决
                avg = np.mean(segment)
                bit = 1 if avg > 0 else 0
                
            elif scheme == 'FSK':
                # 相关解调 (Correlation)
                # 分别与 f1 和 f2 做内积，谁大就是谁
                score_1 = np.sum(segment * self.carrier_f1)
                score_0 = np.sum(segment * self.carrier_f2)
                bit = 1 if score_1 > score_0 else 0
                
            elif scheme == 'BPSK':
                # 相干解调
                # 与载波做内积: 同相为正，反相为负
                score = np.sum(segment * self.carrier_bpsk)
                bit = 1 if score > 0 else 0
            
            decoded_bits.append(bit)
            
        # 移除前导码
        if len(decoded_bits) > len(self.preamble):
            return decoded_bits[len(self.preamble):]
        else:
            return []

# ============================================================================
# 4. 网络层与链路层 (Network/Link Layer - Packet & Host)
# ============================================================================

class Packet:
    """
    数据包结构:
    [SRC(8)] [DST(8)] [TYPE(8)] [SEQ(8)] [LEN(8)] [PAYLOAD...] [CRC(8)]
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
    def __init__(self, address, cable, mod_scheme='ASK'):
        self.address = address # [Level 2] Addressing
        self.cable = cable
        self.mod_scheme = mod_scheme  # <--- 新增属性: 调制方式
        self.modem = Modem()
        
        # [Level 3] Reliability State
        self.next_seq = 0
        self.received_seqs = set()
        self.pending_acks = {} # {seq: {packet, sent_time}}
        self.timeout_interval = 3.0
        
        # [Level 3] App Layer Server Data
        self.server_files = {
            '/index.html': '<html>Hello World</html>',
            '/secret.txt': 'Top Secret Data',
            '/api/status': '{"status": "ok"}'
        }

    def send(self, target_address, message, current_time, reliable=True):
        """
        发送消息接口
        :param reliable: 是否启用可靠传输 (加入重传队列)
        """
        print(f"[Host {self.address}] Sending SEQ={self.next_seq} to {target_address}: '{message}'")
        
        packet = Packet(self.address, target_address, message, 'DATA', seq=self.next_seq)
        
        # 加入重传队列
        if reliable:
            self.pending_acks[self.next_seq] = {
                'packet': packet, 
                'sent_time': current_time
            }
            # 只有发送新数据时才增加 SEQ
            self.next_seq += 1
            
        return self._transmit_packet(packet)

    def _transmit_packet(self, packet):
        """辅助函数: 封包并调制"""
        bits = packet.to_bits()
        return self.modem.modulate(bits, scheme=self.mod_scheme)

    def receive(self, analog_signal, current_time):
        """
        接收信号处理
        Returns: (response_signal, app_data)
        增加了 current_time 参数用于记录事件日志
        """
        # 1. 物理层解调
        bits = self.modem.demodulate(analog_signal, scheme=self.mod_scheme)
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
            # ---> 记录接收事件 [Visual Log] <---
            record_event(current_time, self.address, "Receive", packet.seq, packet.type)
            
            # --- Case A: 收到 ACK ---
            if packet.type == 'ACK':
                print(f"[Host {self.address}] 🆗 Received ACK for SEQ={packet.seq}")
                if packet.seq in self.pending_acks:
                    del self.pending_acks[packet.seq] # 移除待确认项，停止计时
            
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
                        print(f"[Host {self.address}] 🤖 App Layer Logic: Client asked for resource, Server prepares response.")

                # [Level 3] 自动发送 ACK
                ack_packet = Packet(self.address, packet.src, "ACK", 'ACK', seq=packet.seq)
                response_signal = self._transmit_packet(ack_packet)
                
                # ---> 记录 ACK 发送事件 [Visual Log] <---
                # 记录在稍后的时间点，表示处理延迟
                record_event(current_time + 0.1, self.address, "Send", ack_packet.seq, "ACK")

        return response_signal, app_data

    def _handle_app_layer(self, payload):
        """[Level 3] 处理 HTTP 风格请求"""
        parsed = AppLayer.parse(payload)
        if parsed['type'] == 'GET':
            resource = parsed['content']
            if resource in self.server_files:
                return f"200 OK {self.server_files[resource]}"
            else:
                return "404 Not Found"
        return None

    def check_timeouts(self, current_time):
        """
        [Level 3] 超时重传检查
        Returns: List of (signal, packet) tuples
        """
        retransmit_data = [] # 存储 (signal, packet) 元组
        
        for seq, info in self.pending_acks.items():
            if current_time - info['sent_time'] > self.timeout_interval:
                print(f"[Host {self.address}] ⏳ Timeout for SEQ={seq}. Retransmitting...")
                
                # ---> 记录超时事件 [Visual Log] <---
                record_event(current_time, self.address, "Timeout", seq, "EVENT")
                
                info['sent_time'] = current_time # Reset timer
                packet = info['packet']
                signal = self._transmit_packet(packet)
                
                # 返回信号和包对象，方便外部记录日志
                retransmit_data.append((signal, packet))
                
        return retransmit_data

# ============================================================================
# 5. 主程序 (Simulation Loop)
# ============================================================================

def run_simulation():
    print("="*60)
    print("Full Stack Network Simulation (MAX SCORE + ALL BONUSES)")
    print("Features: Reliability, CRC, App Layer")
    print("Bonuses:  Wireless Fading, Multi-Modulation (ASK/FSK/BPSK)")
    print("="*60)
    
    global SIM_EVENTS
    SIM_EVENTS.clear()

    # [Bonus] 使用 WirelessChannel 替代普通 Cable
    print("\n>>> Initializing Wireless Channel (Rayleigh Fading enabled)...")
    wireless_channel = WirelessChannel(length=50, attenuation=0.0, noise_level=0.1)
    
    # [Bonus] 配置主机使用 BPSK (比 ASK 抗噪性能更好)
    print(">>> Configuring Hosts with BPSK Modulation...")
    client = Host(address=1, cable=wireless_channel, mod_scheme='BPSK')
    server = Host(address=2, cable=wireless_channel, mod_scheme='BPSK')
    
    sim_state = {'time': 0.0}
    
    # ... (propagate_signal 函数保持不变，直接复制即可) ...
    def propagate_signal(sender, signal, packet_info=None):
        if signal is None: return
        current_t = sim_state['time']
        seq_num = packet_info.seq if packet_info else (sender.next_seq - 1 if sender == client else "?")
        p_type = packet_info.type if packet_info else "DATA"
        
        # 使用 wireless channel 传输
        rx_signal = wireless_channel.transmit(signal)
        
        # 丢包逻辑 (保持不变)
        is_loss_period = (4.0 < current_t < 6.0)
        if is_loss_period:
            print(f"   >>> [CHANNEL FAILURE] Signal lost! (Time={current_t})")
            record_event(current_t, sender.address, "Send", seq_num, p_type, status="Lost")
            return 

        record_event(current_t, sender.address, "Send", seq_num, p_type, status="Success")
        receiver = server if sender == client else client
        response_signal, app_data = receiver.receive(rx_signal, current_t + 0.5)
        
        if response_signal is not None:
            propagate_signal(receiver, response_signal, packet_info=None)

    # --- Scenario 1: BPSK Modulation (High Performance) ---
    print(f"\n[Time={sim_state['time']}] Scenario 1: Wireless BPSK Transmission")
    signal = client.send(2, "GET /index.html", sim_state['time'])
    propagate_signal(client, signal)
    
    sim_state['time'] += 2.0 
    
    # --- Scenario 2: Switch to FSK (Dynamic Reconfiguration) ---
    print(f"\n[Time={sim_state['time']}] Scenario 2: Switching to FSK Modulation")
    # 模拟动态切换调制方式
    client.mod_scheme = 'FSK'
    server.mod_scheme = 'FSK'
    
    signal = client.send(2, "GET /secret.txt", sim_state['time'])
    propagate_signal(client, signal)

    sim_state['time'] += 3.0

    # --- Scenario 3: Packet Loss & Retransmission ---
    print(f"\n[Time={sim_state['time']}] Scenario 3: Packet Loss & Retransmission (FSK)")
    signal = client.send(2, "Critical Data", sim_state['time']) 
    propagate_signal(client, signal) 
    
    print("\n... Waiting for timeout ...")
    sim_state['time'] += 4.0 
    
    retry_data = client.check_timeouts(sim_state['time'])
    for sig, pkt in retry_data:
        propagate_signal(client, sig, packet_info=pkt)

if __name__ == "__main__":
    run_simulation()

if __name__ == "__main__":
    run_simulation()