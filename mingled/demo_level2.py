#!/usr/bin/env python3
"""
Level 2: Multi-Host Communication Demo Script
Complete demonstration of network topology and routing logic, including:
1. Multi-host communication in simple topology
2. Addressing mechanism and packet header design
3. Routing and forwarding functionality
4. Network topology and data flow visualization
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from cable import Cable
from node import Node
from common import *

print("=" * 80)
print("Level 2: Multi-Host Communication - Complete Demonstration")
print("=" * 80)


# ============================================================================
# Demo 1: Addressing Mechanism and Packet Header Design
# ============================================================================
def demo_1_addressing_and_header():
    """
    Demo 1: Addressing mechanism and packet header design
    - How MAC addresses distinguish different hosts
    - Detailed packet header structure
    - Frame encapsulation and parsing process
    """
    print("\n" + "=" * 80)
    print("[Demo 1] Addressing Mechanism and Packet Header Design")
    print("=" * 80)
    
    print("\n>>> Implementation Method:")
    print("=" * 80)
    print("1. Addressing Mechanism - How to distinguish different hosts?")
    print("   - Use MAC Address (Media Access Control Address)")
    print("   - Each host assigned unique 8-bit MAC address (0-255)")
    print("   - Similar to Ethernet hardware address concept")
    
    print("\n2. Packet Header Design:")
    print("   Frame Structure: [Preamble][Dest MAC][Source MAC][Length][Payload][CRC]")
    print("   ")
    print("   +------------------+------------------+------------------+")
    print("   | Preamble (8 bit) | Dest MAC (8 bit) | Source MAC (8 bit)")
    print("   +------------------+------------------+------------------+")
    print("   | Length (8 bit)   | Payload (variable) | CRC (32 bit)   |")
    print("   +------------------+------------------+------------------+")
    print("   ")
    print("   Field Descriptions:")
    print("   - Preamble: Synchronization sequence [1,0,1,0,1,0,1,0]")
    print("   - Dest MAC: Receiver address")
    print("   - Source MAC: Sender address")
    print("   - Length: Payload byte count")
    print("   - Payload: Actual data")
    print("   - CRC: Cyclic Redundancy Check for error detection")
    
    print("\n>>> Example Demonstration:")
    print("=" * 80)
    
    # Create a simple point-to-point connection
    cable = Cable(length=20, attenuation=0.05, noise_level=0.1, debug_mode=False)
    
    host_a = Node("Alice", mac_address=10, debug=True)
    host_b = Node("Bob", mac_address=20, debug=True)
    
    host_a.connect(cable, host_b)
    host_b.connect(cable, host_a)
    
    print(f"\nCreate nodes:")
    print(f"  - Alice: MAC Address = 10")
    print(f"  - Bob:   MAC Address = 20")
    
    print(f"\nSend message: Alice (10) → Bob (20)")
    print(f"Message content: 'Hello Bob!'")
    print("\nObserve packet encapsulation process:")
    print("-" * 80)
    
    # Send message (debug=True shows detailed frame structure)
    host_a.send_packet(target_mac=20, message="Hello Bob!")
    
    print("-" * 80)
    print("\n✅ Demo Complete!")
    print("\nKey Observations:")
    print("  1. Packet header contains all necessary routing information")
    print("  2. CRC ensures data integrity")
    print("  3. Preamble used for receiver synchronization")


# ============================================================================
# Demo 2: Multi-Host Communication in Simple Topology
# ============================================================================
def demo_2_simple_topology():
    """
    Demo 2: Multi-host communication in simple (3-node star) topology
    - Topology: A ←→ Router ←→ B
    - Direct communication vs routed communication
    """
    print("\n" + "=" * 80)
    print("[Demo 2] Multi-Host Communication in Simple Topology")
    print("=" * 80)
    
    print("\n>>> Network Topology:")
    print("=" * 80)
    print("              [Cable 1]        [Cable 2]")
    print("   Host A ←――――――――――→ Router ←――――――――――→ Host B")
    print("   MAC:10                99                20")
    print("=" * 80)
    
    # Create physical links
    cable_1 = Cable(length=30, attenuation=0.05, noise_level=0.1, debug_mode=False)
    cable_2 = Cable(length=40, attenuation=0.05, noise_level=0.1, debug_mode=False)
    
    # Create nodes
    host_a = Node("HostA", mac_address=10, debug=True)
    router = Node("Router", mac_address=99, debug=True)
    host_b = Node("HostB", mac_address=20, debug=True)
    
    # Establish physical connections
    host_a.connect(cable_1, router)
    router.connect(cable_1, host_a)
    router.connect(cable_2, host_b)
    host_b.connect(cable_2, router)
    
    print("\n>>> Scenario 1: Direct Communication (Host A → Router)")
    print("-" * 80)
    print("Host A sends message directly to Router...")
    host_a.send_packet(target_mac=99, message="Ping Router!")
    print("-" * 80)
    
    print("\n>>> Scenario 2: Routed Communication (Host A → Host B)")
    print("-" * 80)
    print("Note: Host A and Host B not directly connected, requires Router forwarding")
    print("\nConfiguring routing tables...")
    host_a.add_route(target_mac=20, next_hop_name="Router")
    router.add_route(target_mac=20, next_hop_name="HostB")
    router.add_route(target_mac=10, next_hop_name="HostA")
    
    print("Routing table configuration:")
    print(f"  - Host A: To 20(Host B) → Next hop: Router")
    print(f"  - Router: To 20(Host B) → Next hop: HostB")
    print(f"  - Router: To 10(Host A) → Next hop: HostA")
    
    print("\nHost A sends message to Host B...")
    print("Observe routing forwarding process:")
    print("-" * 80)
    host_a.send_packet(target_mac=20, message="Hello from A to B!")
    print("-" * 80)
    
    print("\n✅ Demo Complete!")
    print("\nKey Observations:")
    print("  1. Router looks up routing table based on destination MAC")
    print("  2. Packet reaches destination through router forwarding")
    print("  3. Each node only processes packets addressed to itself")


# ============================================================================
# Demo 3: Complex Topology and Multi-Hop Routing
# ============================================================================
def demo_3_complex_topology():
    """
    Demo 3: Complex topology and multi-hop routing
    - Topology: A ←→ R1 ←→ R2 ←→ B (4-node linear)
    - Multi-hop routing
    """
    print("\n" + "=" * 80)
    print("[Demo 3] Complex Topology and Multi-Hop Routing")
    print("=" * 80)
    
    print("\n>>> Network Topology:")
    print("=" * 80)
    print("   Host A ←→ Router1 ←→ Router2 ←→ Host B")
    print("   MAC:10      88         99         20")
    print("   ")
    print("   Note: Host A to Host B requires forwarding through two routers")
    print("=" * 80)
    
    # Create physical links
    cable_a_r1 = Cable(length=30, debug_mode=False)
    cable_r1_r2 = Cable(length=50, debug_mode=False)
    cable_r2_b = Cable(length=30, debug_mode=False)
    
    # Create nodes
    host_a = Node("HostA", mac_address=10, debug=True)
    router1 = Node("Router1", mac_address=88, debug=True)
    router2 = Node("Router2", mac_address=99, debug=True)
    host_b = Node("HostB", mac_address=20, debug=True)
    
    # Establish physical connections
    host_a.connect(cable_a_r1, router1)
    router1.connect(cable_a_r1, host_a)
    
    router1.connect(cable_r1_r2, router2)
    router2.connect(cable_r1_r2, router1)
    
    router2.connect(cable_r2_b, host_b)
    host_b.connect(cable_r2_b, router2)
    
    # Configure routing tables
    print("\n>>> Configure Routing Tables:")
    print("-" * 80)
    
    # Host A routing: to 20 via 88
    host_a.add_route(target_mac=20, next_hop_name="Router1")
    print("Host A:   To 20(Host B) → Next hop: Router1(88)")
    
    # Router1 routing: to 20 via 99
    router1.add_route(target_mac=20, next_hop_name="Router2")
    router1.add_route(target_mac=10, next_hop_name="HostA")
    print("Router1:  To 20(Host B) → Next hop: Router2(99)")
    
    # Router2 routing: to 20 direct, to 10 back via 88
    router2.add_route(target_mac=20, next_hop_name="HostB")
    router2.add_route(target_mac=10, next_hop_name="Router1")
    print("Router2:  To 20(Host B) → Next hop: HostB")
    
    # Host B routing: to 10 via 99
    host_b.add_route(target_mac=10, next_hop_name="Router2")
    print("Host B:   To 10(Host A) → Next hop: Router2(99)")
    print("-" * 80)
    
    print("\n>>> Starting Communication: Host A → Host B (Multi-hop Routing)")
    print("-" * 80)
    print("Observe packet path: A → R1 → R2 → B")
    print()
    
    host_a.send_packet(target_mac=20, message="Multi-hop message!")
    
    print("-" * 80)
    print("\n✅ Demo Complete!")
    print("\nKey Observations:")
    print("  1. Packet reaches destination after multiple forwards")
    print("  2. Each router decides next hop based on routing table")
    print("  3. Destination MAC address remains unchanged throughout transmission")


# ============================================================================
# Demo 4: Network Topology Visualization
# ============================================================================
def demo_4_topology_visualization():
    """
    Demo 4: Generate network topology visualization
    - Draw nodes and links
    - Label MAC addresses
    - Show data flow direction
    """
    print("\n" + "=" * 80)
    print("[Demo 4] Network Topology Visualization")
    print("=" * 80)
    
    print("\n>>> Generating topology diagram...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # ---- Subplot 1: Simple Star Topology ----
    ax1.set_title('Simple Star Topology\n(A ←→ Router ←→ B)', 
                  fontsize=14, fontweight='bold')
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 6)
    ax1.axis('off')
    
    # Node positions
    pos_a = (2, 3)
    pos_router = (5, 3)
    pos_b = (8, 3)
    
    # Draw links
    ax1.plot([pos_a[0], pos_router[0]], [pos_a[1], pos_router[1]], 
             'k-', linewidth=3, alpha=0.5)
    ax1.plot([pos_router[0], pos_b[0]], [pos_router[1], pos_b[1]], 
             'k-', linewidth=3, alpha=0.5)
    
    # Draw nodes
    circle_a = mpatches.Circle(pos_a, 0.5, color='lightblue', ec='blue', linewidth=2)
    circle_router = mpatches.Circle(pos_router, 0.5, color='lightgreen', ec='green', linewidth=2)
    circle_b = mpatches.Circle(pos_b, 0.5, color='lightcoral', ec='red', linewidth=2)
    
    ax1.add_patch(circle_a)
    ax1.add_patch(circle_router)
    ax1.add_patch(circle_b)
    
    # Labels
    ax1.text(pos_a[0], pos_a[1], 'A', ha='center', va='center', 
             fontsize=16, fontweight='bold')
    ax1.text(pos_a[0], pos_a[1]-0.9, 'MAC: 10', ha='center', fontsize=10)
    
    ax1.text(pos_router[0], pos_router[1], 'R', ha='center', va='center', 
             fontsize=16, fontweight='bold')
    ax1.text(pos_router[0], pos_router[1]-0.9, 'MAC: 99', ha='center', fontsize=10)
    
    ax1.text(pos_b[0], pos_b[1], 'B', ha='center', va='center', 
             fontsize=16, fontweight='bold')
    ax1.text(pos_b[0], pos_b[1]-0.9, 'MAC: 20', ha='center', fontsize=10)
    
    # Data flow arrows
    ax1.annotate('', xy=(pos_router[0]-0.3, pos_router[1]+0.2), 
                xytext=(pos_a[0]+0.3, pos_a[1]+0.2),
                arrowprops=dict(arrowstyle='->', color='blue', lw=2))
    ax1.annotate('', xy=(pos_b[0]-0.3, pos_b[1]+0.2), 
                xytext=(pos_router[0]+0.3, pos_router[1]+0.2),
                arrowprops=dict(arrowstyle='->', color='blue', lw=2))
    ax1.text(5, 4.5, 'Data Flow: A → R → B', ha='center', 
             fontsize=11, color='blue', fontweight='bold')
    
    # ---- Subplot 2: Multi-Hop Linear Topology ----
    ax2.set_title('Multi-Hop Linear Topology\n(A ←→ R1 ←→ R2 ←→ B)', 
                  fontsize=14, fontweight='bold')
    ax2.set_xlim(0, 14)
    ax2.set_ylim(0, 6)
    ax2.axis('off')
    
    # Node positions
    pos_a2 = (2, 3)
    pos_r1 = (5, 3)
    pos_r2 = (8, 3)
    pos_b2 = (11, 3)
    
    # Draw links
    ax2.plot([pos_a2[0], pos_r1[0]], [pos_a2[1], pos_r1[1]], 
             'k-', linewidth=3, alpha=0.5)
    ax2.plot([pos_r1[0], pos_r2[0]], [pos_r1[1], pos_r2[1]], 
             'k-', linewidth=3, alpha=0.5)
    ax2.plot([pos_r2[0], pos_b2[0]], [pos_r2[1], pos_b2[1]], 
             'k-', linewidth=3, alpha=0.5)
    
    # Draw nodes
    circle_a2 = mpatches.Circle(pos_a2, 0.4, color='lightblue', ec='blue', linewidth=2)
    circle_r1 = mpatches.Circle(pos_r1, 0.4, color='lightgreen', ec='green', linewidth=2)
    circle_r2 = mpatches.Circle(pos_r2, 0.4, color='lightgreen', ec='green', linewidth=2)
    circle_b2 = mpatches.Circle(pos_b2, 0.4, color='lightcoral', ec='red', linewidth=2)
    
    ax2.add_patch(circle_a2)
    ax2.add_patch(circle_r1)
    ax2.add_patch(circle_r2)
    ax2.add_patch(circle_b2)
    
    # Labels
    ax2.text(pos_a2[0], pos_a2[1], 'A', ha='center', va='center', 
             fontsize=14, fontweight='bold')
    ax2.text(pos_a2[0], pos_a2[1]-0.8, 'MAC: 10', ha='center', fontsize=9)
    
    ax2.text(pos_r1[0], pos_r1[1], 'R1', ha='center', va='center', 
             fontsize=14, fontweight='bold')
    ax2.text(pos_r1[0], pos_r1[1]-0.8, 'MAC: 88', ha='center', fontsize=9)
    
    ax2.text(pos_r2[0], pos_r2[1], 'R2', ha='center', va='center', 
             fontsize=14, fontweight='bold')
    ax2.text(pos_r2[0], pos_r2[1]-0.8, 'MAC: 99', ha='center', fontsize=9)
    
    ax2.text(pos_b2[0], pos_b2[1], 'B', ha='center', va='center', 
             fontsize=14, fontweight='bold')
    ax2.text(pos_b2[0], pos_b2[1]-0.8, 'MAC: 20', ha='center', fontsize=9)
    
    # Data flow arrows
    for start, end in [(pos_a2, pos_r1), (pos_r1, pos_r2), (pos_r2, pos_b2)]:
        ax2.annotate('', xy=(end[0]-0.3, end[1]+0.15), 
                    xytext=(start[0]+0.3, start[1]+0.15),
                    arrowprops=dict(arrowstyle='->', color='red', lw=2))
    
    ax2.text(6.5, 4.5, 'Data Flow: A → R1 → R2 → B', ha='center', 
             fontsize=11, color='red', fontweight='bold')
    
    plt.suptitle('Level 2: Network Topology Structure', fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    plt.savefig('level2_topology.png', dpi=300, bbox_inches='tight')
    print("    ✅ Topology figure saved: level2_topology.png")
    plt.show()


# ============================================================================
# Main Function
# ============================================================================
def main():
    """Main function: run all demonstrations"""
    print("\nStarting Level 2 demonstrations...")
    print("Note: Some demos will generate visualization charts. Close the chart window to continue.\n")
    
    try:
        # Demo 1: Addressing and packet header
        demo_1_addressing_and_header()
        input("\nPress Enter to continue to next demo...")
        
        # Demo 2: Simple topology
        demo_2_simple_topology()
        input("\nPress Enter to continue to next demo...")
        
        # Demo 3: Complex topology
        demo_3_complex_topology()
        input("\nPress Enter to continue to next demo...")
        
        # Demo 4: Topology visualization
        demo_4_topology_visualization()
        
        print("\n" + "=" * 80)
        print("🎉 Level 2 All Demos Completed!")
        print("=" * 80)
        print("\nGenerated files:")
        print("  - level2_topology.png (Network topology structure)")
        
    except KeyboardInterrupt:
        print("\n\nUser interrupted demo.")
    except Exception as e:
        print(f"\n\nError occurred during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

