# 数据通信项目 - 可视化模块使用指南

## 概述

本可视化模块整合了三个主要的画图功能，用于全面分析和展示数据通信系统的各个层面。

## 功能特性

### 1. 物理层精确分析 (Physical Layer Analysis)
- **功能**: 对比发送比特、接收信号和解调比特
- **展示内容**:
  - 原始发送比特序列（Ground Truth）
  - 经过信道传输后的模拟信号（含噪声和衰减）
  - 实际解调后的比特序列
  - 误码率（BER）分析
- **输出文件**: `physical_layer_analysis.png`

### 2. 三种调制方式对比 (Modulation Schemes Comparison)
- **功能**: 展示ASK、FSK、BPSK三种调制方式的波形特征
- **展示内容**:
  - ASK（幅移键控）- 振幅变化
  - FSK（频移键控）- 频率变化
  - BPSK（二进制相移键控）- 相位变化
  - 前导码和数据部分的标注
- **输出文件**: `modulation_comparison.png`

### 3. 全栈协议时序可视化 (Protocol Timeline)
- **功能**: 展示完整的网络通信过程时序图
- **展示内容**:
  - 三种调制方式下的通信过程对比
  - 数据包发送和接收事件
  - ACK确认过程
  - 丢包和超时重传机制
  - 干扰区域标注
- **输出文件**: `protocol_timeline.png`

## 使用方法

### 方式一：交互式菜单

```bash
cd mingled
python visualizaiton.py
```

然后根据提示选择：
- `1` - 运行物理层精确分析
- `2` - 运行调制方式对比
- `3` - 运行协议时序可视化
- `4` - 运行所有可视化
- `0` - 退出

### 方式二：直接调用函数

```python
from visualizaiton import (
    visualize_physical_layer_accurate,
    visualize_modulation_schemes,
    visualize_protocol_timeline
)

# 运行单个可视化
visualize_physical_layer_accurate()

# 或运行多个
visualize_modulation_schemes()
visualize_protocol_timeline()
```

### 方式三：作为模块导入

```python
import visualizaiton

# 运行特定可视化
visualizaiton.visualize_physical_layer_accurate()
```

## 依赖项

确保已安装以下Python包：
```bash
pip install numpy matplotlib
```

## 文件结构

```
mingled/
├── visualizaiton.py          # 主可视化模块
├── simulation_core.py         # 仿真核心模块（Packet, Modem, Host等类）
├── wireless_channel.py        # 无线信道模拟
├── cable.py                   # 有线信道模拟
├── common.py                  # 通用工具函数
└── README_VISUALIZATION.md    # 本文档
```

## 核心类说明

### simulation_core.py 中的类

1. **Packet** - 数据包封装
   - 包含源地址、目标地址、载荷、类型、序列号
   - 支持CRC校验

2. **Modem** - 调制解调器
   - 支持ASK、FSK、BPSK三种调制方式
   - 包含同步前导码机制
   - 实现互相关同步算法

3. **Host** - 网络主机
   - 实现可靠传输协议
   - 支持超时重传机制
   - 包含应用层协议处理

4. **Utils** - 工具类
   - 比特流与字符串转换
   - CRC校验计算

## 可视化参数调整

### 物理层分析参数

在 `visualize_physical_layer_accurate()` 函数中：
```python
NOISE_LEVEL = 1.2      # 噪声水平 (0.0-2.0)
DISPLAY_BITS = 60      # 显示的比特数
```

### 调制方式对比参数

在 `visualize_modulation_schemes()` 函数中：
```python
raw_bits = [1, 0, 1, 1, 0]                          # 测试比特序列
modem = Modem(sample_rate=1000, samples_per_bit=40) # 采样参数
noise_level = 0.3                                   # 信道噪声
```

### 协议时序参数

在 `simulation_core.py` 的 `run_simulation()` 函数中：
```python
noise_level = 0.1           # 信道噪声
loss_period = (4.0, 6.0)   # 丢包时间段
timeout_interval = 3.0      # 超时时间
```

## 输出示例

所有可视化图表会：
1. 显示在屏幕上（需要关闭窗口才能继续）
2. 自动保存为高分辨率PNG文件（320 DPI）

## 注意事项

1. **兼容性**: 本模块与mingled文件夹中的其他代码完全兼容，不会影响原有功能
2. **独立性**: 可视化模块可以独立运行，不依赖项目的其他部分
3. **性能**: 协议时序可视化会运行三次完整的网络仿真，可能需要几秒钟时间

## 故障排除

### 问题：导入错误
```python
ImportError: No module named 'cable'
```
**解决方案**: 确保在mingled文件夹中运行，或将mingled添加到Python路径

### 问题：matplotlib警告
```
/Users/xxx/.matplotlib is not a writable directory
```
**解决方案**: 这是环境配置警告，不影响功能，可以忽略

### 问题：图表不显示
**解决方案**: 
- 检查是否在GUI环境中运行
- 尝试使用 `plt.savefig()` 仅保存图片而不显示

## 扩展功能

你可以轻松添加新的可视化功能：

```python
def visualize_custom_analysis():
    """自定义可视化功能"""
    # 你的代码
    modem = Modem()
    # ... 进行分析和绘图
    plt.savefig('custom_analysis.png', dpi=320)
    plt.show()
```

然后在 `main()` 函数中添加菜单选项。

## 作者与许可

本可视化模块整合自原项目的多个可视化组件，保持了原有功能的完整性。

