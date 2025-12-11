# 🚀 快速开始 - 数据通信项目演示

## ⚡ 一分钟快速启动

```bash
cd /Users/gansz/Projects/EE315_project/mingled
python run_all_demos.py
```

然后根据菜单选择要运行的Level（1-5）。

---

## 📚 文件说明

### 核心演示脚本

| 文件 | 说明 | 运行命令 |
|------|------|---------|
| `run_all_demos.py` | **统一启动入口** (推荐) | `python run_all_demos.py` |
| `demo_level1.py` | Level 1完整演示 | `python demo_level1.py` |
| `demo_level2.py` | Level 2完整演示 | `python demo_level2.py` |
| `demo_level3.py` | Level 3完整演示 | `python demo_level3.py` |

### 文档

| 文件 | 内容 |
|------|------|
| `START_HERE.md` | **本文档** - 最快上手 |
| `DEMO_GUIDE.md` | 详细演示指南（必读） |
| `DEMO_COMPLETION_REPORT.md` | 完成报告和检查清单 |

---

## 📊 三个Level对应关系

### Level 1: 点对点通信 (30分)
**文件**: `demo_level1.py`

✅ 演示1：完整的比特流传输过程  
✅ 演示2：消息分片传输功能  
✅ 演示3：不同噪声下的系统表现  
✅ 演示4：香农公式对比  

**生成文件**: 
- `level1_noise_impact.png`
- `level1_shannon_comparison.png`

---

### Level 2: 多主机通信 (30分)
**文件**: `demo_level2.py`

✅ 演示1：寻址机制和数据包头设计  
✅ 演示2：简单拓扑的多主机通信  
✅ 演示3：复杂拓扑和多跳路由  
✅ 演示4：网络拓扑可视化  

**生成文件**: 
- `level2_topology.png`

---

### Level 3: 扩展功能 (40分)
**文件**: `demo_level3.py`

✅ 扩展1：传输层可靠传输 (ARQ)  
✅ 扩展2：信道编码 (Hamming)  
✅ 扩展3：应用层协议 (HTTP-like)  
✅ 扩展4：性能优化 (多调制)  
✅ 扩展5：无线通信 (瑞利衰落)  

**生成文件**: 
- `level3_channel_coding.png`
- `level3_wireless.png`
- `ber.png`

---

## 🎬 录屏演示流程

### 推荐流程
1. **运行** `python run_all_demos.py`
2. **选择** 对应的Level（1、2或3）
3. **录制** 整个运行过程
4. **讲解** 关键输出和图表
5. **重复** 直到完成所有Level

### 时间分配
- Level 1: 5-8分钟
- Level 2: 5-8分钟
- Level 3: 10-15分钟（根据演示的扩展数量）

---

## ✅ 答辩前检查清单

### 环境检查
- [ ] 进入正确目录: `cd mingled`
- [ ] Python环境正常
- [ ] 依赖包已安装 (`numpy`, `matplotlib`)

### 运行测试
```bash
python test_integration.py
```
确保显示 "🎉 所有测试通过！"

### 准备工作
- [ ] 阅读 `DEMO_GUIDE.md` 了解所有功能
- [ ] 至少运行一遍每个Level的演示
- [ ] 保存好生成的PNG图片文件
- [ ] 准备好讲解每个功能的实现方法

---

## 💡 常见问题

### Q: 图表不显示？
A: 图片会自动保存为PNG文件，可以手动打开查看。

### Q: 演示运行很慢？
A: 香农公式对比需要测试25个点，每个点5000 bits，需要耐心等待。

### Q: 想单独测试某个演示？
A: 直接运行对应的Level脚本，每个演示都是独立的函数。

### Q: 如何调整参数？
A: 编辑对应的 `demo_level*.py` 文件，参数都有清晰的注释。

---

## 📖 详细文档

需要更多信息？查看：

1. **`DEMO_GUIDE.md`** - 完整的演示指南
   - 每个Level的详细说明
   - 实现方法解释
   - 评分要点对应
   - 录屏建议

2. **`DEMO_COMPLETION_REPORT.md`** - 完成报告
   - 交付内容总览
   - 技术亮点
   - 答辩准备检查清单
   - 代码统计

3. **`README_VISUALIZATION.md`** - 可视化模块说明
   - 之前集成的可视化功能
   - 使用方法

---

## 🎯 核心优势

✨ **完整性**: 所有要求的功能都已实现  
✨ **专业性**: 可视化图表采用IEEE标准  
✨ **易用性**: 一键运行，交互式菜单  
✨ **清晰性**: 详细的实现方法说明  
✨ **可靠性**: 所有代码经过测试验证  

---

## 📞 需要帮助？

1. 先查看 `DEMO_GUIDE.md`
2. 运行 `python test_integration.py` 验证环境
3. 检查终端输出的错误信息

---

**祝演示成功！** 🎉

---

**创建时间**: 2025年12月11日  
**版本**: v1.0  
**状态**: ✅ 准备就绪

