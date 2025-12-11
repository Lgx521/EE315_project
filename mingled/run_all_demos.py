#!/usr/bin/env python3
"""
Data Communication Project - Complete Demo Runner
Run all Level demos with one click, or selectively run specific Level
"""

import sys
import os

print("=" * 80)
print("Data Communication Project - Complete Demo System")
print("=" * 80)

def print_menu():
    """Display menu"""
    print("\nPlease select demo to run:")
    print("=" * 80)
    print("  1. Level 1: Point-to-Point Communication (Point-to-Point Communication)")
    print("     - Complete bit stream transmission process")
    print("     - Message fragmentation functionality")
    print("     - System performance under different noise")
    print("     - Transmission rate vs Shannon formula comparison")
    print()
    print("  2. Level 2: Multi-Host Communication (Multi-Host Communication)")
    print("     - Addressing mechanism and packet header design")
    print("     - simple topologyMulti-Host Communication")
    print("     - Complex topology and multi-hop routing")
    print("     - Network topology visualization")
    print()
    print("  3. Level 3: Extension Features (Extension Features)")
    print("     - Reliable transport layer (ARQ)")
    print("     - Channel coding (Hamming)")
    print("     - Application layer protocol (HTTP-like)")
    print("     - Performance optimization (Multiple modulation schemes)")
    print("     - Wireless communication (Rayleigh fading)")
    print()
    print("  4. Run all demos (Complete flow)")
    print("  5. Quick test (Verify functionality)")
    print()
    print("  0. exit")
    print("=" * 80)

def run_level1():
    """Run Level 1 demo"""
    print("\n" + "=" * 80)
    print("Starting Level 1 Demo...")
    print("=" * 80)
    import demo_level1
    demo_level1.main()

def run_level2():
    """Run Level 2 demo"""
    print("\n" + "=" * 80)
    print("Starting Level 2 Demo...")
    print("=" * 80)
    import demo_level2
    demo_level2.main()

def run_level3():
    """Run Level 3 demo"""
    print("\n" + "=" * 80)
    print("Starting Level 3 Demo...")
    print("=" * 80)
    import demo_level3
    demo_level3.main()

def run_all():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("Starting complete demo flow")
    print("=" * 80)
    print("\nNote:")
    print("  - Will pause after each Level, press Enter to continue")
    print("  - Visualization charts will be displayed sequentially")
    print("  - Total time needed15-20minutes")
    print()
    
    confirm = input("Confirm to start?(y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled。")
        return
    
    try:
        # Level 1
        print("\n" + "▶" * 40)
        print("Part 1/3 : Level 1")
        print("▶" * 40)
        run_level1()
        input("\n✅ Level 1 Complete! Press Enter to continue Level 2...")
        
        # Level 2
        print("\n" + "▶" * 40)
        print("Part 2/3 : Level 2")
        print("▶" * 40)
        run_level2()
        input("\n✅ Level 2 Complete! Press Enter to continue Level 3...")
        
        # Level 3
        print("\n" + "▶" * 40)
        print("Part 3/3 : Level 3")
        print("▶" * 40)
        run_level3()
        
        # Summary
        print("\n" + "=" * 80)
        print("🎉 Complete demo flow finished!")
        print("=" * 80)
        print("\nGenerated files:")
        print("  Level 1:")
        print("    - level1_noise_impact.png")
        print("    - level1_shannon_comparison.png")
        print("  Level 2:")
        print("    - level2_topology.png")
        print("  Level 3:")
        print("    - level3_channel_coding.png")
        print("    - level3_wireless.png")
        print("    - ber.png (if ranPerformance optimization)")
        print()
        print("All demo scripts:")
        print("  - demo_level1.py")
        print("  - demo_level2.py")
        print("  - demo_level3.py")
        print()
        print("Detailed documentation:")
        print("  - DEMO_GUIDE.md (Demo Guide)")
        print("  - README_VISUALIZATION.md (Visualization Guide)")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  User interrupted demo。")
    except Exception as e:
        print(f"\n\n❌ during demoError occurred: {e}")
        import traceback
        traceback.print_exc()

def run_quick_test():
    """Quick test verification"""
    print("\n" + "=" * 80)
    print("Running quick test...")
    print("=" * 80)
    
    try:
        import test_integration
        exit_code = test_integration.main()
        
        if exit_code == 0:
            print("\n✅ All tests passed! System running normally。")
            print("\nYou can now safely run complete demos。")
        else:
            print("\n⚠️  Test failed，Please check error messages。")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    while True:
        try:
            print_menu()
            choice = input("Please enter option (0-5): ").strip()
            
            if choice == '0':
                print("\nThank you! Goodbye!")
                break
            elif choice == '1':
                run_level1()
            elif choice == '2':
                run_level2()
            elif choice == '3':
                run_level3()
            elif choice == '4':
                run_all()
            elif choice == '5':
                run_quick_test()
            else:
                print("\n❌ Invalid option, please select again。")
                continue
            
            # Ask whether to continue
            print()
            cont = input("Return to main menu?(y/n): ").strip().lower()
            if cont != 'y':
                print("\nThank you! Goodbye!")
                break
                
        except KeyboardInterrupt:
            print("\n\nUser interrupted program。goodbye！")
            break
        except Exception as e:
            print(f"\n❌ Error occurred: {e}")
            import traceback
            traceback.print_exc()
            
            cont = input("\nContinue?(y/n): ").strip().lower()
            if cont != 'y':
                break

if __name__ == "__main__":
    main()

