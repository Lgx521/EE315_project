#!/usr/bin/env python3
"""
集成测试脚本
验证所有可视化功能是否正常工作
"""

import sys

def test_imports():
    """测试所有必要的模块导入"""
    print("=" * 60)
    print("测试 1: 模块导入")
    print("=" * 60)
    
    try:
        print("导入 cable...")
        from cable import Cable
        print("✅ cable.Cable 导入成功")
        
        print("导入 wireless_channel...")
        from wireless_channel import WirelessChannel
        print("✅ wireless_channel.WirelessChannel 导入成功")
        
        print("导入 simulation_core...")
        from simulation_core import Packet, Modem, Host, Utils, AppLayer, run_simulation, SIM_EVENTS
        print("✅ simulation_core.Packet 导入成功")
        print("✅ simulation_core.Modem 导入成功")
        print("✅ simulation_core.Host 导入成功")
        print("✅ simulation_core.Utils 导入成功")
        print("✅ simulation_core.AppLayer 导入成功")
        print("✅ simulation_core.run_simulation 导入成功")
        print("✅ simulation_core.SIM_EVENTS 导入成功")
        
        print("导入 visualizaiton...")
        import visualizaiton
        print("✅ visualizaiton 模块导入成功")
        
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_class_instantiation():
    """测试核心类的实例化"""
    print("\n" + "=" * 60)
    print("测试 2: 类实例化")
    print("=" * 60)
    
    try:
        from simulation_core import Packet, Modem, Host
        from wireless_channel import WirelessChannel
        from cable import Cable
        
        print("创建 Cable 实例...")
        cable = Cable(length=50, attenuation=0.1, noise_level=0.1)
        print("✅ Cable 实例创建成功")
        
        print("创建 WirelessChannel 实例...")
        channel = WirelessChannel(length=50, attenuation=0.1, noise_level=0.1)
        print("✅ WirelessChannel 实例创建成功")
        
        print("创建 Modem 实例...")
        modem = Modem()
        print("✅ Modem 实例创建成功")
        
        print("创建 Packet 实例...")
        packet = Packet(src=1, dst=2, payload_str="Test", type='DATA', seq=0)
        print("✅ Packet 实例创建成功")
        
        print("创建 Host 实例...")
        host = Host(address=1, cable=cable, mod_scheme='ASK')
        print("✅ Host 实例创建成功")
        
        return True
    except Exception as e:
        print(f"❌ 实例化失败: {e}")
        return False

def test_basic_functionality():
    """测试基本功能"""
    print("\n" + "=" * 60)
    print("测试 3: 基本功能")
    print("=" * 60)
    
    try:
        from simulation_core import Packet, Modem, Utils
        from cable import Cable
        
        print("测试 Utils.str_to_bits...")
        bits = Utils.str_to_bits("Hi")
        print(f"  'Hi' -> {len(bits)} bits")
        print("✅ Utils.str_to_bits 工作正常")
        
        print("测试 Utils.bits_to_str...")
        text = Utils.bits_to_str(bits)
        assert text == "Hi", "比特转字符串失败"
        print(f"  {len(bits)} bits -> '{text}'")
        print("✅ Utils.bits_to_str 工作正常")
        
        print("测试 Packet.to_bits...")
        packet = Packet(src=1, dst=2, payload_str="Test", type='DATA', seq=0)
        packet_bits = packet.to_bits()
        print(f"  数据包 -> {len(packet_bits)} bits")
        print("✅ Packet.to_bits 工作正常")
        
        print("测试 Modem.modulate (ASK)...")
        modem = Modem()
        signal = modem.modulate([1, 0, 1, 0], scheme='ASK')
        print(f"  4 bits -> {len(signal)} samples")
        print("✅ Modem.modulate(ASK) 工作正常")
        
        print("测试 Modem.modulate (FSK)...")
        signal = modem.modulate([1, 0, 1, 0], scheme='FSK')
        print(f"  4 bits -> {len(signal)} samples")
        print("✅ Modem.modulate(FSK) 工作正常")
        
        print("测试 Modem.modulate (BPSK)...")
        signal = modem.modulate([1, 0, 1, 0], scheme='BPSK')
        print(f"  4 bits -> {len(signal)} samples")
        print("✅ Modem.modulate(BPSK) 工作正常")
        
        print("测试 Cable.transmit...")
        cable = Cable(length=50, attenuation=0.1, noise_level=0.1)
        rx_signal = cable.transmit(signal)
        print(f"  {len(signal)} samples -> {len(rx_signal)} samples (含延迟)")
        print("✅ Cable.transmit 工作正常")
        
        print("测试 Modem.demodulate...")
        rx_bits = modem.demodulate(rx_signal, scheme='BPSK')
        print(f"  {len(rx_signal)} samples -> {len(rx_bits)} bits")
        print("✅ Modem.demodulate 工作正常")
        
        return True
    except Exception as e:
        print(f"❌ 功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_visualization_functions():
    """测试可视化函数是否可调用（不实际运行）"""
    print("\n" + "=" * 60)
    print("测试 4: 可视化函数可用性")
    print("=" * 60)
    
    try:
        from visualizaiton import (
            visualize_physical_layer_accurate,
            visualize_modulation_schemes,
            visualize_protocol_timeline
        )
        
        print("✅ visualize_physical_layer_accurate 函数可用")
        print("✅ visualize_modulation_schemes 函数可用")
        print("✅ visualize_protocol_timeline 函数可用")
        
        return True
    except Exception as e:
        print(f"❌ 可视化函数导入失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("集成测试开始")
    print("=" * 60 + "\n")
    
    results = []
    
    # 运行测试
    results.append(("模块导入", test_imports()))
    results.append(("类实例化", test_class_instantiation()))
    results.append(("基本功能", test_basic_functionality()))
    results.append(("可视化函数", test_visualization_functions()))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！可视化功能集成成功！")
        print("=" * 60)
        print("\n现在可以运行可视化功能：")
        print("  python visualizaiton.py")
        print("  或")
        print("  python example_visualization.py")
        return 0
    else:
        print("⚠️  部分测试失败，请检查错误信息")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
