import matplotlib.pyplot as plt
import main  # 直接导入 main 模块

def visualize_real_logic():
    print("🚀 启动可视化：正在运行 main.py 的真实业务逻辑...")
    
    # 1. 运行仿真 (这一步会执行 main.py 中的 run_simulation)
    # 所有的 Print 输出都会显示在终端，同时数据会被记录到 main.SIM_EVENTS
    main.run_simulation()
    
    events = main.SIM_EVENTS
    
    if not events:
        print("❌ 警告：没有捕获到任何事件。请检查 main.py 是否正常运行。")
        return

    print(f"📊 捕获到 {len(events)} 个事件，正在绘图...")

    # 2. 绘图逻辑
    fig, ax = plt.subplots(figsize=(12, 6))
    
    y_client = 3
    y_server = 1
    
    ax.set_ylim(0, 4)
    ax.set_xlim(0, 12)
    ax.set_yticks([])
    ax.set_title("Real-Time Protocol Sequence (Visualizing main.py Execution)")
    
    # 画轨道
    ax.axhline(y_client, color='blue', linestyle='-', alpha=0.3)
    ax.text(0, y_client + 0.2, 'Host 1 (Client)', fontweight='bold', color='blue')
    ax.axhline(y_server, color='green', linestyle='-', alpha=0.3)
    ax.text(0, y_server + 0.2, 'Host 2 (Server)', fontweight='bold', color='green')
    
    # 画事件
    for e in events:
        t = e['time']
        h = e['host']
        action = e['action']
        status = e['status']
        ptype = e['type']
        seq = e['seq']
        
        y = y_client if h == 1 else y_server
        
        # 绘制 Timeout
        if action == "Timeout":
            ax.plot(t, y, marker='D', color='orange', markersize=12, zorder=10)
            ax.text(t, y + 0.5, f"Timeout\nSeq={seq}", ha='center', color='orange', fontsize=9, fontweight='bold')
            continue

        # 绘制 Send / Receive
        color = 'blue' if ptype == 'DATA' else 'green'
        if status == 'Lost': color = 'red'
        
        marker = 'o'
        if status == 'Lost': marker = 'x'
        
        # 如果是 Receive，稍微画晚一点/偏移一点，避免重叠
        # 但在时序图上，通常 Send 和 Receive 是有连线的
        # 这里简化处理：只画点
        
        ax.plot(t, y, marker=marker, color=color, markersize=10)
        
        label_y = y + 0.3 if h == 1 else y - 0.4
        label = f"{action} {ptype}\nSeq={seq}"
        if status == 'Lost': label += "\n(Dropped)"
        
        ax.text(t, label_y, label, ha='center', fontsize=8, color=color)
        
        # 绘制连线 (仅针对成功的 Send)
        if action == "Send" and status == "Success":
            # 查找匹配的 Receive 事件 (简单起见，画个指向对面的箭头)
            target_y = y_server if h == 1 else y_client
            ax.arrow(t, y, 0.5, target_y - y, head_width=0.1, length_includes_head=True, color=color, alpha=0.2)
        elif action == "Send" and status == "Lost":
             ax.arrow(t, y, 0.5, -0.5, head_width=0.1, color='red', alpha=0.5)

    ax.set_xlabel("Simulation Time (s)")
    ax.grid(True, axis='x', linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    visualize_real_logic()