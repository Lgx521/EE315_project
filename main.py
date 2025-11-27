import numpy as np
import time
import copy
from cable import Cable


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
# 3. 物理层 (Physical Layer - Modem)
# ============================================================================

class Modem:
    """
    调制解调器
    负责数字比特流与模拟信号之间的转换 (ASK 调制)
    """
    def __init__(self, sample_rate=100, samples_per_bit=10):
        self.sample_rate = sample_rate
        self.samples_per_bit = samples_per_bit
        self.high_level = 1.0
        self.low_level = -1.0
        # 同步前导码 (Preamble)，用于辅助解调器定位信号开始
        self.preamble = [1, 0, 1, 0, 1, 0, 1, 0] 

    def modulate(self, bits):
        """[Level 1] 调制: Bits -> Analog Signal"""
        # 添加前导码
        tx_bits = self.preamble + bits
        signal = []
        for b in tx_bits:
            val = self.high_level if b == 1 else self.low_level
            # 过采样 (Oversampling)
            signal.extend([val] * self.samples_per_bit)
        return np.array(signal)

    def demodulate(self, signal):
        """[Level 1] 解调: Analog Signal -> Bits"""
        if signal is None or len(signal) == 0:
            return []

        threshold = (self.high_level + self.low_level) / 2
        
        # 1. 简单同步: 寻找信号能量起始点
        start_index = 0
        for i, val in enumerate(signal):
            if abs(val) > 0.5: # 简单的能量检测门限
                start_index = i
                break
        
        # 截取有效信号部分
        signal = signal[start_index:]
        num_bits = len(signal) // self.samples_per_bit
        decoded_bits = []
        
        # 2. 积分判决 (Integrate and Dump)
        for i in range(num_bits):
            start = i * self.samples_per_bit
            end = start + self.samples_per_bit
            segment = signal[start:end]
            if len(segment) == 0: break
            # 取平均值抗噪
            avg = np.mean(segment)
            decoded_bits.append(1 if avg > threshold else 0)
        
        # 3. 移除前导码
        preamble_len = len(self.preamble)
        if len(decoded_bits) > preamble_len:
            return decoded_bits[preamble_len:]
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
        return self.modem.modulate(bits)

    def receive(self, analog_signal, current_time):
        """
        接收信号处理
        Returns: (response_signal, app_data)
        增加了 current_time 参数用于记录事件日志
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
    print("Full Stack Network Simulation (Instrumented for Visualization)")
    print("Levels 1, 2, 3 + Visualization Support")
    print("="*60)
    
    # 每次运行前清空全局事件记录
    global SIM_EVENTS
    SIM_EVENTS.clear()

    # 初始化信道
    cable = Cable(length=50, attenuation=0.0, noise_level=0.1)
    
    # 初始化主机
    client = Host(address=1, cable=cable)
    server = Host(address=2, cable=cable)
    
    # 仿真状态容器 (使用字典以允许在闭包中修改)
    sim_state = {'time': 0.0}
    
    def propagate_signal(sender, signal, packet_info=None):
        """
        递归传播信号，处理丢失、接收和 ACK
        :param sender: 发送方 Host 对象
        :param signal: 模拟信号数组
        :param packet_info: 发送的 Packet 对象 (用于日志记录优化)
        """
        if signal is None: 
            return
        
        current_t = sim_state['time']
        
        # 尝试推断 packet 信息用于日志 (如果没传)
        seq_num = "?"
        p_type = "DATA"
        
        if packet_info:
            seq_num = packet_info.seq
            p_type = packet_info.type
        elif sender == client:
             # 如果没有显式传入 packet_info (首次发送), 
             # 此时 next_seq 已经+1了，所以当前发的 seq 是 next_seq - 1
             seq_num = sender.next_seq - 1
        
        # 模拟物理传输
        rx_signal = cable.transmit(signal)
        
        # --- [丢包逻辑控制中心] ---
        # 如果你想取消丢包，将下方条件改为 False
        # is_loss_period = False 
        is_loss_period = (4.0 < current_t < 6.0)
        
        if is_loss_period:
            print(f"   >>> [CHANNEL FAILURE] Signal lost! (Time={current_t})")
            # 记录丢包事件 [Visual Log]
            record_event(current_t, sender.address, "Send", seq_num, p_type, status="Lost")
            return 

        # 记录成功发送事件 [Visual Log]
        record_event(current_t, sender.address, "Send", seq_num, p_type, status="Success")

        # 确定接收方
        receiver = server if sender == client else client
        
        # 接收并处理
        # 加上 0.5s 的传播延迟
        response_signal, app_data = receiver.receive(rx_signal, current_t + 0.5)
        
        # 如果有回应 (ACK)，递归传播
        if response_signal is not None:
            # ACK 包不需要外部传入 packet_info，因为在 receive 内部已经记录了 Send ACK 事件
            # 这里主要是为了让 ACK 回传给原发送方
            propagate_signal(receiver, response_signal, packet_info=None)

    # --- 场景 1: 正常应用层请求 (HTTP GET) ---
    print(f"\n[Time={sim_state['time']}] Scenario 1: Normal Request")
    req_msg = AppLayer.create_request("GET", "/index.html")
    signal = client.send(2, req_msg, sim_state['time'])
    propagate_signal(client, signal)
    
    sim_state['time'] += 2.0 
    
    # --- 场景 2: 另一个请求 (404 Not Found) ---
    print(f"\n[Time={sim_state['time']}] Scenario 2: Request Missing File")
    req_msg = AppLayer.create_request("GET", "/secret.txt")
    signal = client.send(2, req_msg, sim_state['time'])
    propagate_signal(client, signal)

    sim_state['time'] += 3.0

    # --- 场景 3: 模拟丢包与重传 ---
    print(f"\n[Time={sim_state['time']}] Scenario 3: Packet Loss & Retransmission")
    # 此时 time=5.0，处于丢包区间 (4.0 - 6.0)
    signal = client.send(2, "Critical Data", sim_state['time']) 
    propagate_signal(client, signal) 
    
    print("\n... Simulating wait time for timeout ...")
    sim_state['time'] += 4.0 # Time = 9.0 (超过超时阈值)
    
    # 检查超时并获取重传信号
    retry_data = client.check_timeouts(sim_state['time']) # 返回 [(signal, packet), ...]
    
    for sig, pkt in retry_data:
        # 重传，传入 packet info 以便记录准确日志
        propagate_signal(client, sig, packet_info=pkt)

if __name__ == "__main__":
    run_simulation()