# 快速入门指南

## 5分钟上手可视化功能

### 第一步：进入mingled文件夹

```bash
cd /Users/gansz/Projects/EE315_project/mingled
```

### 第二步：选择运行方式

#### 方式A：交互式菜单（推荐新手）

```bash
python visualizaiton.py
```

然后按提示选择：
- 输入 `1` 查看物理层分析
- 输入 `2` 查看调制方式对比
- 输入 `3` 查看协议时序图
- 输入 `4` 一次运行所有可视化
- 输入 `0` 退出

#### 方式B：示例脚本（带详细说明）

```bash
python example_visualization.py
```

#### 方式C：Python代码直接调用

```python
# 在Python交互式环境或脚本中
from visualizaiton import visualize_physical_layer_accurate

# 运行物理层分析
visualize_physical_layer_accurate()
```

### 第三步：查看结果

可视化完成后，会：
1. 在屏幕上显示图表（关闭窗口继续）
2. 在当前目录生成PNG图片文件

生成的文件：
- `physical_layer_analysis.png` - 物理层精确分析
- `modulation_comparison.png` - 调制方式对比
- `protocol_timeline.png` - 协议时序图

## 常见场景

### 场景1：我想看看ASK、FSK、BPSK有什么区别

```bash
python visualizaiton.py
# 选择 2
```

或

```python
from visualizaiton import visualize_modulation_schemes
visualize_modulation_schemes()
```

### 场景2：我想分析误码率

```bash
python visualizaiton.py
# 选择 1
```

查看图表底部会显示BER（误码率）信息。

### 场景3：我想看完整的通信过程

```bash
python visualizaiton.py
# 选择 3
```

这会展示包括超时重传、丢包等完整的网络通信过程。

### 场景4：生成所有图表用于报告

```bash
python visualizaiton.py
# 选择 4
```

所有图表会自动保存为高清PNG文件（320 DPI），可直接用于报告和演示。

## 调整参数

如需调整参数（如噪声水平、显示的比特数等），编辑`visualizaiton.py`文件中的对应函数。

例如，调整物理层分析的噪声水平：

```python
def visualize_physical_layer_accurate():
    # 找到这一行
    NOISE_LEVEL = 1.2  # 改成你想要的值，如 0.5, 1.0, 2.0
    # ...
```

## 故障排除

### Q: 运行时提示找不到模块
A: 确保你在mingled文件夹中运行，或者将mingled添加到Python路径

### Q: matplotlib警告
A: 这些是环境配置警告，不影响功能，可以安全忽略

### Q: 图表不显示
A: 检查你的环境是否支持GUI。如果是服务器环境，图片仍会保存到文件。

## 更多信息

- 详细文档：`README_VISUALIZATION.md`
- 集成说明：`INTEGRATION_SUMMARY.md`
- 示例代码：`example_visualization.py`

## 一行命令演示

```bash
# 快速运行所有可视化（非交互模式）
cd mingled && python -c "from visualizaiton import *; visualize_physical_layer_accurate(); visualize_modulation_schemes(); visualize_protocol_timeline()"
```

注意：每个可视化完成后需要关闭窗口才能继续下一个。

---

**开始探索吧！** 🚀
