import matplotlib.pyplot as plt
import copy
import main

def visualize_separate_schemes():
    print("🚀 启动对比可视化引擎 (Fixed Causality)...")
    
    schemes = ['ASK', 'FSK', 'BPSK']
    colors = {'ASK': 'blue', 'FSK': 'green', 'BPSK': 'purple'}
    
    fig, axes = plt.subplots(3, 1, figsize=(12, 18))
    plt.subplots_adjust(hspace=0.4)
    Y_CLIENT, Y_SERVER = 3, 1
    
    for i, scheme in enumerate(schemes):
        ax = axes[i]
        color = colors[scheme]
        
        main.run_simulation(target_scheme=scheme)
        events = copy.deepcopy(main.SIM_EVENTS)
        
        ax.set_title(f"Protocol Sequence - Modulation: {scheme}", fontsize=14, fontweight='bold', color=color)
        ax.set_ylim(0, 4)
        ax.set_xlim(0, 12)
        ax.set_yticks([Y_SERVER, Y_CLIENT])
        ax.set_yticklabels(['Host 2 (Server)', 'Host 1 (Client)'], fontweight='bold')
        
        # 轨道
        ax.axhline(Y_CLIENT, color=color, alpha=0.1, linewidth=2)
        ax.axhline(Y_SERVER, color=color, alpha=0.1, linewidth=2)
        ax.axvspan(4.0, 6.0, facecolor='red', alpha=0.05)
        ax.text(5.0, 3.8, "Loss Zone", ha='center', color='red', fontsize=8)

        for e in events:
            t = e['time']
            host = e['host']
            action = e['action']
            status = e['status']
            ptype = e['type']
            seq = e['seq']
            
            y_pos = Y_CLIENT if host == 1 else Y_SERVER
            
            # 绘制 Timeout
            if action == 'Timeout':
                ax.plot(t, y_pos, marker='D', color='orange', markersize=10, zorder=10)
                ax.text(t, y_pos + 0.4, "Timeout", ha='center', color='orange', fontsize=8, fontweight='bold')
                continue

            # 绘制节点
            node_color = color if ptype == 'DATA' else 'gray'
            if status == 'Lost': node_color = 'red'
            marker = 'X' if status == 'Lost' else 'o'
            
            ax.plot(t, y_pos, marker=marker, color=node_color, markersize=8)
            
            lbl = f"{action} {ptype}\nSeq={seq}"
            offset = 0.3 if host == 1 else -0.4
            ax.text(t, y_pos + offset, lbl, ha='center', fontsize=8, color=node_color)
            
            # 绘制箭头
            if action == "Send":
                target_y = Y_SERVER if host == 1 else Y_CLIENT
                # 传播时间设为 0.5 (匹配 main.py 中的设定)
                arrow_dx = 0.5 
                
                if status == 'Success':
                    ax.annotate("", 
                                xy=(t + arrow_dx, target_y), xytext=(t, y_pos),
                                arrowprops=dict(arrowstyle="->", color=node_color, lw=1.5, alpha=0.6))
                elif status == 'Lost':
                    mid_y = (y_pos + target_y) / 2
                    ax.annotate("", 
                                xy=(t + 0.3, mid_y), xytext=(t, y_pos),
                                arrowprops=dict(arrowstyle="-[", color='red', lw=1.5))
                    ax.text(t + 0.3, mid_y, " X", color='red', fontweight='bold')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    visualize_separate_schemes()