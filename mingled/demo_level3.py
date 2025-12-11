#!/usr/bin/env python3
"""
Level 3: Extension Features Demo Script
Demonstrate various advanced features, including:
1. Transport layer reliable transmission (ACK/NACK, timeout retransmission)
2. Channel coding (Hamming codes, BER testing)
3. Application layer protocol (HTTP-like)
4. Performance optimization (Multiple modulation schemes comparison)
5. Wireless communication (Rayleigh fading)
"""

import numpy as np
import matplotlib.pyplot as plt
import time
from cable import Cable
from wireless_channel import WirelessChannel
from node import Node
from common import *

print("=" * 80)
print("Level 3: Extension Features - Complete Demonstration")
print("=" * 80)


# ============================================================================
# Extension 1: Reliable Transport Layer (Transport Layer)
# ============================================================================
def Extension_1_reliable_transport():
    """
    Extension 1:Reliable Transport Layer
    - Implementation of Stop-and-Wait ARQ protocol
    - ACK/NACK mechanism
    - Timeout retransmission
    - sequence number management
    """
    print("\n" + "=" * 80)
    print("[Extension 1] Reliable Transport Layer")
    print("=" * 80)
    
    print("\n>>> Implementation Method:")
    print("=" * 80)
    print("Protocol: Stop-and-Wait ARQ (Automatic Repeat Request)")
    print("  ")
    print("  Sender                           Receiver")
    print("    |                                |")
    print("    |----> DATA (Seq=0) ------------>|")
    print("    |                                | Receive Success")
    print("    |<---- ACK (Seq=0) <-------------|")
    print("    |                                |")
    print("    |----> DATA (Seq=1) ------------>|")
    print("    |          (packet loss)                |")
    print("    |                                |")
    print("   ... Timeout waiting ...                 |")
    print("    |                                |")
    print("    |----> DATA (Seq=1) Retransmit ------->|")
    print("    |                                | Receive Success")
    print("    |<---- ACK (Seq=1) <-------------|")
    print("    |                                |")
    print("  ")
    print("Key Features:")
    print("  1. Sequence Number: Alternating 0 and 1 (Stop-and-Wait)")
    print("  2. ACK Confirmation: Receiver sends acknowledgment message")
    print("  3. Timeout Retransmission: Sender sets timeout timer")
    print("  4. Deduplication: Receiver filters duplicate packets")
    print("=" * 80)
    
    print("\n>>> Scenario: Simulating packet loss and retransmission")
    print("-" * 80)
    
    # Create a channel that will drop packets
    from level3_final_arq import LossyCable, run_final_demo
    
    print("Note: Using specialLossyCable，will forcefully drop the first packet")
    print("      Observe how system detects loss and retransmits automatically")
    print()
    
    # Run ARQ demo
    run_final_demo()
    
    print("\n✅ Demo Complete!")
    print("\nKey Observations:")
    print("  1. First transmission dropped")
    print("  2. Sender detects timeout")
    print("  3. automatically retransmits packet")
    print("  4. Receiver successfully receives and sends ACK")


# ============================================================================
# Extension 2: Channel Coding (Channel Coding)
# ============================================================================
def Extension_2_channel_coding():
    """
    Extension 2: Channel Coding
    - Hamming(7,4)error-correcting code
    - Coding and decoding process
    - BER vs error correction performance test
    - rate comparison with/without coding
    """
    print("\n" + "=" * 80)
    print("[Extension 2] Channel Coding")
    print("=" * 80)
    
    print("\n>>> Implementation Method:")
    print("=" * 80)
    print("Hamming(7,4) error-correcting code")
    print("  - Input: 4 bits data")
    print("  - Output: 7 bits codeword (4 data bits + 3 parity bits)")
    print("  - Capability: Detect 2-bit errors, correct 1-bit errors")
    print("  ")
    print("  Coding Example:")
    print("    Input data: [d1, d2, d3, d4]")
    print("    Coding Output: [p1, p2, d1, p3, d2, d3, d4]")
    print("    where p1, p2, p3 are parity bits")
    print("  ")
    print("  Generator matrix G (4×7):")
    print("    Every 4 data bits generate 7-bit codeword via matrix multiplication")
    print("  ")
    print("  Parity check matrix H (3×7):")
    print("    Used for syndrome calculation and error correction during decoding")
    print("=" * 80)
    
    print("\n>>> Performance Test: BER vs error correction effect")
    print("-" * 80)
    
    # Test parameters
    noise_levels = np.linspace(0.1, 0.8, 8)
    test_bits_count = 2000
    
    ber_raw = []
    ber_hamming = []
    
    print(f"Test setup: {test_bits_count} bits, noise range {noise_levels[0]:.1f}-{noise_levels[-1]:.1f}")
    print("\nStarting test...")
    
    for idx, noise in enumerate(noise_levels, 1):
        # Generate random data
        tx_bits = np.random.randint(0, 2, test_bits_count).tolist()
        
        cable = Cable(length=10, attenuation=0.0, noise_level=noise, debug_mode=False)
        delay = cable.delay_points
        
        # Scheme A: No Coding
        tx_signal = modulate_bpsk(tx_bits)
        rx_signal = cable.transmit(tx_signal)
        rx_signal_sync = rx_signal[delay:]
        rx_bits_raw = demodulate_bpsk(rx_signal_sync)
        
        min_len = min(len(tx_bits), len(rx_bits_raw))
        errors_raw = sum(1 for i in range(min_len) if tx_bits[i] != rx_bits_raw[i])
        ber_raw.append(errors_raw / min_len if min_len > 0 else 1.0)
        
        # Scheme B: Hamming Coding
        enc_bits, padding = apply_hamming_encoding(tx_bits)
        tx_signal = modulate_bpsk(enc_bits)
        rx_signal = cable.transmit(tx_signal)
        rx_signal_sync = rx_signal[delay:]
        rx_enc_bits = demodulate_bpsk(rx_signal_sync)
        dec_bits = apply_hamming_decoding(rx_enc_bits, padding)
        
        min_len = min(len(tx_bits), len(dec_bits))
        errors_hamming = sum(1 for i in range(min_len) if tx_bits[i] != dec_bits[i])
        ber_hamming.append(errors_hamming / min_len if min_len > 0 else 1.0)
        
        print(f"  [{idx}/{len(noise_levels)}] noise={noise:.2f}: "
              f"Raw BER={ber_raw[-1]:.4f}, Hamming BER={ber_hamming[-1]:.4f}, "
              f"Gain={ber_raw[-1]/ber_hamming[-1] if ber_hamming[-1]>0 else float('inf'):.2f}x")
    
    print("-" * 80)
    
    # Plotcomparisonfigure
    print("\n>>> Generating performance comparison figure...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Subplot1: BERcomparison
    ax1.semilogy(noise_levels, ber_raw, 'ro-', linewidth=2, 
                markersize=8, label='No Coding (Raw)')
    ax1.semilogy(noise_levels, ber_hamming, 'gs-', linewidth=2, 
                markersize=8, label='Hamming(7,4) Coding')
    ax1.set_xlabel('Noise Level (σ)', fontsize=12)
    ax1.set_ylabel('Bit Error Rate (BER) (BER)', fontsize=12)
    ax1.set_title('Channel Coding Performance Comparison', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=11)
    
    # Subplot2: Coding Gain
    coding_gain = [raw/ham if ham > 0 else 0 for raw, ham in zip(ber_raw, ber_hamming)]
    ax2.plot(noise_levels, coding_gain, 'b^-', linewidth=2, markersize=8)
    ax2.axhline(y=1, color='r', linestyle='--', label='No Gain Line')
    ax2.set_xlabel('Noise Level (σ)', fontsize=12)
    ax2.set_ylabel('Coding Gain (Factor)', fontsize=12)
    ax2.set_title('Hamming Error Correction Gain', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=11)
    
    plt.suptitle('Level 3: Channel Coding Effect Analysis', fontsize=16, fontweight='bold', y=1.00)
    plt.tight_layout()
    
    plt.savefig('level3_channel_coding.png', dpi=300, bbox_inches='tight')
    print("    ✅ Figure saved: level3_channel_coding.png")
    plt.show()
    
    # Rate analysis
    print("\n>>> transmission rateanalysis:")
    print("-" * 80)
    print(f"No Coding:")
    print(f"  - Coding rate: 1.0 (no redundancy)")
    print(f"  - Effective rate = Modulation rate × (1 - BER) × 1.0")
    print(f"  ")
    print(f"Hamming(7,4)Coding:")
    print(f"  - Coding rate: 4/7 ≈ 0.571 (57.1%)")
    print(f"  - Effective rate = Modulation rate × (1 - BER) × 0.571")
    print(f"  ")
    print(f"Conclusion:")
    print(f"  - Low noise: CodingOverhead greater than gain, no coding is better")
    print(f"  - High noise: CodingSignificantly reduces BER, coding is better")
    print("-" * 80)
    
    print("\n✅ Demo Complete!")


# ============================================================================
# Extension 3: Application Layer Protocol (Application Layer)
# ============================================================================
def Extension_3_application_protocol():
    """
    Extension3：Application Layer Protocol
    - HTTP-likeProtocol design
    - GET request and response
    - 200 OK / 404 Not Found
    - complete request-response pattern
    """
    print("\n" + "=" * 80)
    print("[Extension 3] Application Layer Protocol")
    print("=" * 80)
    
    print("\n>>> Implementation Method:")
    print("=" * 80)
    print("HTTP-likeProtocol design")
    print("  ")
    print("  Request format:")
    print("    GET|/path/to/resource")
    print("  ")
    print("  Response format:")
    print("    200 OK|<content>")
    print("    404 Not Found|File /path/to/resource missing")
    print("  ")
    print("  Communication flow:")
    print("    ")
    print("    Client                       Server")
    print("      |                            |")
    print("      |---> GET|/index.html ------>|")
    print("      |                            | Find file")
    print("      |<--- 200 OK|<html>... <-----|")
    print("      |                            |")
    print("      |---> GET|/missing.txt ----->|")
    print("      |                            | File not found")
    print("      |<--- 404 Not Found|... <----|")
    print("      |                            |")
    print("  ")
    print("=" * 80)
    
    print("\n>>> Scenario demo:")
    print("-" * 80)
    
    # Create client and server
    cable = Cable(length=30, attenuation=0.05, noise_level=0.1, debug_mode=False)
    
    client = Node("Client", mac_address=10, debug=True)
    server = Node("Server", mac_address=20, debug=True)
    
    client.connect(cable, server)
    server.connect(cable, client)
    
    # Server provided resources
    print("\nServer resources:")
    for path, content in server.app_data.items():
        print(f"  {path}: '{content}'")
    
    print("\n>>> Scenario 1: Request existing resource")
    print("-" * 80)
    print("Client Request: GET /index.html")
    client.http_get(target_mac=20, uri="/index.html")
    print("-" * 80)
    
    time.sleep(0.5)
    
    print("\n>>> Scenario 2: Request non-existing resource")
    print("-" * 80)
    print("Client Request: GET /missing.txt")
    client.http_get(target_mac=20, uri="/missing.txt")
    print("-" * 80)
    
    print("\n✅ Demo Complete!")
    print("\nKey Observations:")
    print("  1. Application layer protocol implemented on top of transport layer")
    print("  2. Server returns appropriate status code based on request")
    print("  3. Implemented complete request-response pattern")


# ============================================================================
# Extension 4: Performance Optimization - multiple modulation schemescomparison
# ============================================================================
def Extension_4_modulation_comparison():
    """
    Extension4：Performance Optimization
    - ASK vs FSK vs BPSK comparison
    - of different modulation schemesnoise resistance performance
    - BER curve comparison
    """
    print("\n" + "=" * 80)
    print("[Extension 4] Performance Optimization - Modulation Schemes Comparison")
    print("=" * 80)
    
    print("\n>>> Implementation Method:")
    print("=" * 80)
    print("Three modulation schemes:")
    print("  ")
    print("  1. ASK (Amplitude Shift Keying) - Amplitude Shift Keying")
    print("     - Principle: Vary carrier amplitude")
    print("     - 1 → High amplitude, 0 → Low amplitude")
    print("     - Features: Simple implementation, poor noise resistance")
    print("  ")
    print("  2. FSK (Frequency Shift Keying) - Frequency Shift Keying")
    print("     - Principle: Vary carrier frequency")
    print("     - 1 → High frequency, 0 → Low frequency")
    print("     - Features: Good noise resistance, high bandwidth requirement")
    print("  ")
    print("  3. BPSK (Binary Phase Shift Keying) - Binary Phase Shift Keying")
    print("     - Principle: Vary carrier phase")
    print("     - 1 → 0°, 0 → 180°")
    print("     - Features: Best noise resistance, high spectral efficiency")
    print("=" * 80)
    
    print("\n>>> Performance Test: under different noiseBERcomparison")
    print("-" * 80)
    
    # Import existing performance test
    from performance_lab import run_experiment
    
    print("Running complete BER performance test...")
    print("Note: This will test BPSK, BPSK+Hamming, QPSK performance under different noise")
    print()
    
    # Run performance test (will generate charts)
    run_experiment()
    
    print("\n✅ Demo Complete!")
    print("\nKey Observations:")
    print("  1. BPSKBest performance under low noise")
    print("  2. Hamming CodingSignificantly improves performance under high noise")
    print("  3. QPSKtransmission rateHigher but BER slightly higher")


# ============================================================================
# Extension 5: Wireless Communication
# ============================================================================
def Extension_5_wireless_communication():
    """
    Extension5：Wireless Communication
    - Wireless Channel Simulation
    - Rayleigh Fading (Rayleigh Fading)
    - andWired Channelcomparison
    """
    print("\n" + "=" * 80)
    print("[Extension 5] Wireless Communication")
    print("=" * 80)
    
    print("\n>>> Implementation Method:")
    print("=" * 80)
    print("Wireless Channel Simulation")
    print("  ")
    print("  Physical phenomena:")
    print("    - Multipath propagation: Signal reaches receiver via different paths")
    print("    - Rayleigh fading: Multipath superposition causes random signal amplitude fluctuation")
    print("    - Random phase: phase shift due to different paths")
    print("  ")
    print("  Implementation:")
    print("    1. Inherit from wired Cable class")
    print("    2. Add Rayleigh distributed random fading coefficient")
    print("    3. Fading coefficient limited to0.2-1.5between")
    print("  ")
    print("  class WirelessChannel(Cable):")
    print("      def transmit(signal):")
    print("          base_signal = super().transmit(signal)")
    print("          fading_factor = np.random.rayleigh(scale=0.9)")
    print("          fading_factor = np.clip(fading_factor, 0.2, 1.5)")
    print("          return base_signal * fading_factor")
    print("=" * 80)
    
    print("\n>>> Comparison Test: Wired vs Wireless")
    print("-" * 80)
    
    # Test parameters
    test_message = "Wireless Test Message"
    tx_bits = string_to_bits(test_message)
    n_trials = 100
    noise_level = 0.3
    
    print(f"Test setup:")
    print(f"  - Message: '{test_message}'")
    print(f"  - Test trials: {n_trials}")
    print(f"  - Noise Level: {noise_level}")
    print()
    
    # Wired ChannelTest
    wired_bers = []
    cable_wired = Cable(length=50, attenuation=0.1, noise_level=noise_level, debug_mode=False)
    
    print("Testing wired channel...")
    for i in range(n_trials):
        tx_signal = modulate_bpsk(tx_bits)
        rx_signal = cable_wired.transmit(tx_signal)
        rx_signal_sync = rx_signal[cable_wired.delay_points:]
        rx_bits = demodulate_bpsk(rx_signal_sync)
        
        min_len = min(len(tx_bits), len(rx_bits))
        errors = sum(1 for j in range(min_len) if tx_bits[j] != rx_bits[j])
        ber = errors / min_len if min_len > 0 else 1.0
        wired_bers.append(ber)
    
    # Wireless ChannelTest
    wireless_bers = []
    cable_wireless = WirelessChannel(length=50, attenuation=0.1, noise_level=noise_level)
    
    print("Testing wireless channel...")
    for i in range(n_trials):
        tx_signal = modulate_bpsk(tx_bits)
        rx_signal = cable_wireless.transmit(tx_signal)
        rx_signal_sync = rx_signal[cable_wireless.delay_points:]
        rx_bits = demodulate_bpsk(rx_signal_sync)
        
        min_len = min(len(tx_bits), len(rx_bits))
        errors = sum(1 for j in range(min_len) if tx_bits[j] != rx_bits[j])
        ber = errors / min_len if min_len > 0 else 1.0
        wireless_bers.append(ber)
    
    print("-" * 80)
    
    # Statistical results
    print("\n>>> Statistical Results:")
    print(f"Wired Channel:")
    print(f"  - Average BER: {np.mean(wired_bers):.4f}")
    print(f"  - BER std dev: {np.std(wired_bers):.4f}")
    print(f"  - BER range: [{np.min(wired_bers):.4f}, {np.max(wired_bers):.4f}]")
    print()
    print(f"Wireless Channel:")
    print(f"  - Average BER: {np.mean(wireless_bers):.4f}")
    print(f"  - BER std dev: {np.std(wireless_bers):.4f}")
    print(f"  - BER range: [{np.min(wireless_bers):.4f}, {np.max(wireless_bers):.4f}]")
    
    # Plotcomparisonfigure
    print("\n>>> Generatingcomparisonfigure...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Subplot 1: BER histogram
    ax1.hist(wired_bers, bins=20, alpha=0.7, label='Wired Channel', color='blue', edgecolor='black')
    ax1.hist(wireless_bers, bins=20, alpha=0.7, label='Wireless Channel', color='red', edgecolor='black')
    ax1.axvline(np.mean(wired_bers), color='blue', linestyle='--', linewidth=2, label='Wired Mean')
    ax1.axvline(np.mean(wireless_bers), color='red', linestyle='--', linewidth=2, label='Wireless Mean')
    ax1.set_xlabel('Bit Error Rate (BER) (BER)', fontsize=12)
    ax1.set_ylabel('Frequency', fontsize=12)
    ax1.set_title('BER Distribution Comparison', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Subplot 2: BER time series
    ax2.plot(wired_bers, 'b-', alpha=0.6, label='Wired Channel')
    ax2.plot(wireless_bers, 'r-', alpha=0.6, label='Wireless Channel')
    ax2.axhline(np.mean(wired_bers), color='blue', linestyle='--', linewidth=1.5)
    ax2.axhline(np.mean(wireless_bers), color='red', linestyle='--', linewidth=1.5)
    ax2.set_xlabel('Trial Number', fontsize=12)
    ax2.set_ylabel('Bit Error Rate (BER) (BER)', fontsize=12)
    ax2.set_title('BER Fluctuation Comparison', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.suptitle('Level 3: Wired vs Wireless Channel Performance Comparison', fontsize=16, fontweight='bold', y=1.00)
    plt.tight_layout()
    
    plt.savefig('level3_wireless.png', dpi=300, bbox_inches='tight')
    print("    ✅ Figure saved: level3_wireless.png")
    plt.show()
    
    print("\n✅ Demo Complete!")
    print("\nKey Observations:")
    print("  1. Wireless Channel has larger BER fluctuation (Rayleigh fading effect)")
    print("  2. Wireless Channel typically has higher average BER thanWired Channel")
    print("  3. Requires stronger error correction codes and retransmission mechanisms to handle wireless fading")


# ============================================================================
# Main function
# ============================================================================
def main():
    """Main function: run all Extension feature demonstrations"""
    print("\nStarting Level 3 Extension feature demonstrations...")
    print("Note: You can choose to run specific Extensions or all of them。\n")
    
    Extensions = [
        ("Reliable Transport Layer", Extension_1_reliable_transport),
        ("Channel Coding", Extension_2_channel_coding),
        ("Application Layer Protocol", Extension_3_application_protocol),
        ("Performance Optimization", Extension_4_modulation_comparison),
        ("Wireless Communication", Extension_5_wireless_communication),
    ]
    
    print("Available Extension features:")
    for i, (name, _) in enumerate(Extensions, 1):
        print(f"  {i}. {name}")
    print("  6. Run all Extension features")
    print("  0. Exit")
    
    try:
        choice = input("\nPlease select (0-6): ").strip()
        
        if choice == '0':
            print("Exit demo。")
            return
        elif choice == '6':
            # Run all
            for name, func in Extensions:
                print(f"\nRunning Extension: {name}")
                func()
                if func != Extensions[-1][1]:  # not the last one
                    input("\nPress Enter to continue to next Extension...")
        elif choice in ['1', '2', '3', '4', '5']:
            idx = int(choice) - 1
            name, func = Extensions[idx]
            print(f"\nRunning Extension: {name}")
            func()
        else:
            print("Invalid option。")
            return
        
        print("\n" + "=" * 80)
        print("🎉 Level 3 Demo Complete！")
        print("=" * 80)
        print("\nGenerated files:")
        print("  - level3_channel_coding.png (Channel Codingperformance)")
        print("  - level3_wireless.png (Wireless channel comparison)")
        print("  - ber.png (BERperformance curve，if ranPerformance Optimization)")
        
    except KeyboardInterrupt:
        print("\n\nUser interrupted demo。")
    except Exception as e:
        print(f"\n\nError occurred during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

