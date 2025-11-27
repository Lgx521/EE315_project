import matplotlib.pyplot as plt
import copy
import main  # 导入你的 main.py

def visualize_three_schemes():
    print("🚀 启动全栈协议时序可视化 (3 Schemes)...")
    
    # 定义要对比的三种调制方式
    schemes = ['ASK', 'FSK', 'BPSK']
    colors = {'ASK': '#1f77b4', 'FSK': '#2ca02c', 'BPSK': '#9467bd'}
    
    # 创建 3 行 1 列的画布
    fig, axes = plt.subplots(3, 1, figsize=(14, 16), sharex=True)
    plt.subplots_adjust(hspace=0.3)
    
    # Y轴坐标定义
    Y_CLIENT = 3.0
    Y_SERVER = 1.0
    
    for i, scheme in enumerate(schemes):
        ax = axes[i]
        color = colors[scheme]
        
        # ==========================================
        # 核心修复: 每次运行前清空全局事件记录
        # ==========================================
        main.SIM_EVENTS.clear() 
        
        # 运行仿真
        print(f"Running simulation for {scheme}...")
        main.run_simulation(target_scheme=scheme)
        
        # 深拷贝数据，防止被下一次运行覆盖
        events = copy.deepcopy(main.SIM_EVENTS)
        
        # --- 绘图设置 ---
        ax.set_title(f"Scheme: {scheme} (Physical Layer)", fontsize=14, fontweight='bold', color=color, loc='left')
        ax.set_ylim(0, 4.5)
        ax.set_xlim(0, 13) # 稍微加长一点x轴以容纳最后的数据
        
        # 绘制 Host 轨道线
        ax.axhline(Y_CLIENT, color='blue', alpha=0.1, linewidth=2, linestyle='-')
        ax.axhline(Y_SERVER, color='green', alpha=0.1, linewidth=2, linestyle='-')
        ax.text(0.2, Y_CLIENT + 0.2, "Host 1 (Client)", color='blue', fontweight='bold')
        ax.text(0.2, Y_SERVER + 0.2, "Host 2 (Server)", color='green', fontweight='bold')
        
        # 绘制丢包区域 (Loss Zone) - 对应 main.py 里的 4.0s - 6.0s
        ax.axvspan(4.0, 6.0, facecolor='red', alpha=0.07)
        ax.text(5.0, 4.2, "Interference Zone\n(Packet Loss)", ha='center', va='center', color='red', fontsize=9, alpha=0.6)

        # --- 绘制事件 ---
        for e in events:
            t = e['time']
            host = e['host']
            action = e['action']
            status = e['status']
            ptype = e['type']
            seq = e['seq']
            
            # 确定 Y 坐标
            y_start = Y_CLIENT if host == 1 else Y_SERVER
            y_target = Y_SERVER if host == 1 else Y_CLIENT
            
            # 1. 绘制 Timeout 事件 (菱形)
            if action == 'Timeout':
                ax.plot(t, y_start, marker='D', color='orange', markersize=10, zorder=10, markeredgecolor='white')
                ax.text(t, y_start + 0.4, "Timeout!", ha='center', color='orange', fontsize=9, fontweight='bold')
                
                # 画一个回旋箭头表示重试
                ax.annotate("", xy=(t-0.2, y_start+0.2), xytext=(t+0.2, y_start+0.2),
                            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.5", color='orange', ls='--'))
                continue

            # 2. 绘制节点 (圆点)
            # 成功是实心点，失败是红叉
            if status == 'Lost':
                ax.plot(t, y_start, marker='x', color='red', markersize=10, markeredgewidth=2)
            else:
                node_color = color if ptype == 'DATA' else 'gray'
                ax.plot(t, y_start, marker='o', color=node_color, markersize=8, zorder=5)
                
                # 标签: "DATA Seq=0"
                label_y_offset = 0.3 if host == 1 else -0.5
                ax.text(t, y_start + label_y_offset, f"{ptype}\nSeq={seq}", 
                        ha='center', fontsize=8, color=node_color)

            # 3. 绘制传输箭头 (核心时序逻辑)
            if action == "Send":
                # 传播延迟 (main.py 中是 0.5s)
                delay = 0.5
                
                if status == 'Success':
                    # 成功的箭头：从源指到宿
                    arrow_color = color if ptype == 'DATA' else 'gray'
                    style = "->"
                    if ptype == 'ACK': style = "-|>" # ACK 用空心箭头区分一下
                    
                    ax.annotate("", 
                                xy=(t + delay, y_target), 
                                xytext=(t, y_start),
                                arrowprops=dict(arrowstyle=style, color=arrow_color, lw=1.5, alpha=0.7))
                                
                elif status == 'Lost':
                    # 失败的箭头：断在半路，打个叉
                    mid_time = t + (delay * 0.6)
                    mid_y = (y_start + y_target) / 2
                    
                    ax.annotate("", 
                                xy=(mid_time, mid_y), 
                                xytext=(t, y_start),
                                arrowprops=dict(arrowstyle="-[", color='red', lw=1.5))
                    
                    ax.text(mid_time + 0.1, mid_y, "❌ Dropped", color='red', fontsize=8, fontweight='bold', ha='left')

    # 全局设置
    axes[-1].set_xlabel("Simulation Time (seconds)", fontsize=12)
    plt.suptitle("Full-Stack Network Simulation: Protocol Analysis across Modulation Schemes", fontsize=16, y=0.95)
    
    # 保存或显示
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    print("✨ 可视化完成，正在显示图表...")
    plt.show()

if __name__ == "__main__":
    visualize_three_schemes()