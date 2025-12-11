#!/usr/bin/env python3
"""
可视化功能使用示例
演示如何使用visualizaiton模块的各项功能
"""

from visualizaiton import (
    visualize_physical_layer_accurate,
    visualize_modulation_schemes,
    visualize_protocol_timeline
)

def example_1_physical_layer():
    """
    示例1：运行物理层精确分析
    展示发送比特、接收信号和解调比特的对比
    """
    print("=" * 60)
    print("示例 1: 物理层精确分析")
    print("=" * 60)
    print("这个示例将展示：")
    print("- 原始发送的比特序列")
    print("- 经过信道传输后的模拟信号（含噪声）")
    print("- 解调后恢复的比特序列")
    print("- 误码率分析")
    print()
    
    input("按回车键继续...")
    visualize_physical_layer_accurate()


def example_2_modulation():
    """
    示例2：运行三种调制方式对比
    展示ASK、FSK、BPSK的波形特征
    """
    print("\n" + "=" * 60)
    print("示例 2: 三种调制方式对比")
    print("=" * 60)
    print("这个示例将展示：")
    print("- ASK (幅移键控) - 通过振幅变化传输信息")
    print("- FSK (频移键控) - 通过频率变化传输信息")
    print("- BPSK (二进制相移键控) - 通过相位变化传输信息")
    print()
    
    input("按回车键继续...")
    visualize_modulation_schemes()


def example_3_protocol():
    """
    示例3：运行全栈协议时序可视化
    展示完整的网络通信过程
    """
    print("\n" + "=" * 60)
    print("示例 3: 全栈协议时序可视化")
    print("=" * 60)
    print("这个示例将展示：")
    print("- 客户端和服务器之间的通信过程")
    print("- 数据包的发送和接收")
    print("- ACK确认机制")
    print("- 丢包和超时重传")
    print("注意：此过程会运行三次完整的网络仿真（对应三种调制方式）")
    print()
    
    input("按回车键继续...")
    visualize_protocol_timeline()


def example_all():
    """
    运行所有示例
    """
    print("=" * 60)
    print("运行所有可视化示例")
    print("=" * 60)
    print()
    
    example_1_physical_layer()
    example_2_modulation()
    example_3_protocol()
    
    print("\n" + "=" * 60)
    print("所有示例运行完成！")
    print("生成的图片文件：")
    print("- physical_layer_analysis.png")
    print("- modulation_comparison.png")
    print("- protocol_timeline.png")
    print("=" * 60)


if __name__ == "__main__":
    print("=" * 60)
    print("数据通信项目 - 可视化功能示例")
    print("=" * 60)
    print("\n选择要运行的示例：")
    print("1. 物理层精确分析")
    print("2. 三种调制方式对比")
    print("3. 全栈协议时序可视化")
    print("4. 运行所有示例")
    print("0. 退出")
    print("=" * 60)
    
    choice = input("\n请输入选项 (0-4): ").strip()
    
    if choice == '1':
        example_1_physical_layer()
    elif choice == '2':
        example_2_modulation()
    elif choice == '3':
        example_3_protocol()
    elif choice == '4':
        example_all()
    elif choice == '0':
        print("退出程序。")
    else:
        print("无效选项。")

