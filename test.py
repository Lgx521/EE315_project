import unittest
import numpy as np
from cable import Cable
# 导入 main.py 中的核心类
from main import Host, Packet, AppLayer, Utils, Modem

class TestAppLayer(unittest.TestCase):
    """测试 Level 3 扩展: 应用层协议"""
    
    def test_protocol_formatting(self):
        """测试请求和响应的格式化"""
        # 测试请求生成
        req = AppLayer.create_request("GET", "/index.html")
        self.assertEqual(req, "GET /index.html")
        
        # 测试响应生成
        res = AppLayer.create_response("200", "OK")
        self.assertEqual(res, "200 OK")

    def test_parsing(self):
        """测试消息解析"""
        # 正常情况
        msg = "GET /data.txt"
        parsed = AppLayer.parse(msg)
        self.assertEqual(parsed['type'], "GET")
        self.assertEqual(parsed['content'], "/data.txt")
        
        # 异常情况 (只有指令没有内容)
        msg_raw = "PING"
        parsed_raw = AppLayer.parse(msg_raw)
        self.assertEqual(parsed_raw['type'], "RAW")
        self.assertEqual(parsed_raw['content'], "PING")

class TestReliability(unittest.TestCase):
    """测试 Level 3 扩展: 可靠传输 (序列号与重传)"""
    
    def setUp(self):
        # 使用理想信道进行逻辑测试 (不引入随机噪声干扰逻辑验证)
        self.cable = Cable(length=10, attenuation=0, noise_level=0, debug_mode=False)
        self.sender = Host(address=1, cable=self.cable)
        self.receiver = Host(address=2, cable=self.cable)

    def test_sequence_number_increment(self):
        """测试序列号是否自动递增"""
        current_time = 0.0
        
        # 发送第一个包 (SEQ 0)
        self.sender.send(target_address=2, message="First", current_time=current_time)
        self.assertEqual(self.sender.next_seq, 1)
        self.assertIn(0, self.sender.pending_acks)
        
        # 发送第二个包 (SEQ 1)
        self.sender.send(target_address=2, message="Second", current_time=current_time)
        self.assertEqual(self.sender.next_seq, 2)
        self.assertIn(1, self.sender.pending_acks)

    def test_retransmission_logic_dynamic(self):
        """
        核心测试：动态模拟超时重传
        (不使用预定义数据，完全跑真实逻辑)
        """
        sim_time = 0.0
        message = "Critical Data"
        
        # 1. Host A 发送数据
        # ------------------------------------------------
        print("\n[Test] Host A sending data...")
        self.sender.send(target_address=2, message=message, current_time=sim_time)
        
        # 验证: 已加入待确认列表
        self.assertIn(0, self.sender.pending_acks)
        # 获取刚存入的包对象以便后续比对
        original_packet_obj = self.sender.pending_acks[0]['packet']
        
        # 2. 模拟丢包 (Simulate Packet Loss)
        # ------------------------------------------------
        print("[Test] Simulating packet loss (Receiver gets nothing)")
        # 我们故意不调用 receiver.receive()，假装信号在 cable 中丢了
        
        # 3. 时间流逝，未达超时阈值
        # ------------------------------------------------
        sim_time += 1.0 # 过了 1秒 (阈值是 3.0秒)
        retry_signals = self.sender.check_timeouts(sim_time)
        
        # 验证: 不应产生重传信号
        self.assertEqual(len(retry_signals), 0, "Should not retransmit before timeout")
        
        # 4. 时间流逝，超过超时阈值 -> 触发重传
        # ------------------------------------------------
        sim_time += 3.0 # 总共过了 4秒 ( > 3.0)
        print(f"[Test] Time is now {sim_time}, checking timeouts...")
        retry_signals = self.sender.check_timeouts(sim_time)
        
        # 验证: 必须产生重传信号
        self.assertTrue(len(retry_signals) > 0, "Should generate retransmission signal after timeout")
        
        # 5. 验证重传内容的正确性
        # ------------------------------------------------
        print("[Test] Verifying retransmitted signal content...")
        retransmitted_signal = retry_signals[0]
        
        # 使用接收方的 Modem 解调这个重传信号
        rx_bits = self.receiver.modem.demodulate(retransmitted_signal)
        rx_packet = Packet.from_bits(rx_bits)
        
        self.assertIsNotNone(rx_packet)
        self.assertEqual(rx_packet.seq, 0, "Retransmitted packet must keep original SEQ")
        self.assertEqual(rx_packet.payload, message, "Payload must match original")
        self.assertEqual(rx_packet.src, 1)

    def test_ack_processing(self):
        """测试 ACK 接收后清除重传队列"""
        sim_time = 0.0
        self.sender.send(target_address=2, message="Ping", current_time=sim_time)
        
        # 确保在队列中
        self.assertIn(0, self.sender.pending_acks)
        
        # 模拟收到 ACK (构造一个 ACK 包并由 Sender 接收)
        # 注意：这里我们不需要真的经过 Modem，直接注入逻辑或模拟完美接收
        ack_packet = Packet(src=2, dst=1, payload_str="ACK", type='ACK', seq=0)
        ack_bits = ack_packet.to_bits()
        ack_signal = self.sender.modem.modulate(ack_bits)
        
        # Sender 接收 ACK
        self.sender.receive(ack_signal)
        
        # 验证: 应该从待确认列表中移除
        self.assertNotIn(0, self.sender.pending_acks, "ACK should remove item from pending list")

    def test_duplicate_detection(self):
        """测试接收端去重逻辑"""
        # 构造一个数据包
        packet = Packet(src=1, dst=2, payload_str="Dup Test", type='DATA', seq=5)
        bits = packet.to_bits()
        signal = self.sender.modem.modulate(bits)
        
        # 1. 第一次接收
        self.receiver.receive(signal)
        self.assertIn((1, 5), self.receiver.received_seqs, "First packet should be recorded")
        
        # 2. 第二次接收 (模拟重传到达)
        # 捕获标准输出或检查内部状态变更通常比较复杂，
        # 这里我们通过检查 received_seqs 集合的大小没变来验证没有重复处理
        initial_set_size = len(self.receiver.received_seqs)
        
        self.receiver.receive(signal) # 再次接收
        
        self.assertEqual(len(self.receiver.received_seqs), initial_set_size, "Duplicate packet should not increase received set")

class TestIntegration(unittest.TestCase):
    """集成测试: 应用层 + 传输层 + 物理层"""
    
    def test_http_get_scenario(self):
        """模拟完整的 HTTP GET 交互"""
        cable = Cable(length=10, attenuation=0, noise_level=0)
        client = Host(1, cable)
        server = Host(2, cable)
        
        # 1. Client 发送 GET 请求
        req_str = AppLayer.create_request("GET", "/index.html")
        tx_signal = client.send(2, req_str, current_time=0.0)
        
        # 2. 传输 (通过 Cable)
        rx_signal = cable.transmit(tx_signal)
        
        # 3. Server 接收并处理
        # Server.receive 会自动调用 _handle_app_layer 并打印日志
        # 为了测试，我们不仅依赖打印，还要检查返回值中的 ACK 信号，
        # 并且我们可以通过 "Hack" 检查 server 内部是否解析出了意图
        
        ack_signal, app_data = server.receive(rx_signal)
        
        # 验证 Server 收到了正确的数据
        self.assertEqual(app_data, "GET /index.html")
        
        # 验证 Server 识别了请求 (通过手动调用 handle 验证逻辑，因为 receive 内部调用无法直接断言)
        response = server._handle_app_layer(app_data)
        self.assertTrue("200 OK" in response)
        self.assertTrue("<html>" in response)

if __name__ == '__main__':
    unittest.main(verbosity=2)