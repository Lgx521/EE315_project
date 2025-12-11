#!/usr/bin/env python3
"""
Level 1: Point-to-Point Communication Demo Script
Complete demonstration of basic communication link implementation, including:
1. Complete bit stream transmission process
2. Message fragmentation functionality
3. System performance under noise conditions
4. Transmission rate comparison with Shannon formula
"""

import numpy as np
import matplotlib.pyplot as plt
import time
from cable import Cable
from common import *

print("=" * 80)
print("Level 1: Point-to-Point Communication - Complete Demonstration")
print("=" * 80)

# ============================================================================
# Demo 1: Complete bit stream transmission process
# ============================================================================
def demo_1_basic_transmission():
    """
    Demo 1: Complete bit stream transmission process
    - String to bit stream encoding
    - Physical layer modulation
    - Channel transmission (with noise and attenuation)
    - Demodulation and decoding
    """
    print("\n" + "=" * 80)
    print("[Demo 1] Complete Bit Stream Transmission Process")
    print("=" * 80)
    
    # Implementation method explanation
    print("\n>>> Implementation Method:")
    print("1. Encoding: Convert string to 8-bit ASCII bit stream")
    print("2. Frame Structure: [Preamble(8bit)] + [Length(8bit)] + [Payload]")
    print("3. Modulation: BPSK (1→+1V, 0→-1V), 20 samples per bit")
    print("4. Channel: Simulated attenuation and AWGN")
    print("5. Demodulation: Energy detection synchronization + threshold decision")
    print("6. Decoding: Extract payload using length field and convert to string")
    
    # Test message
    original_message = "Hello CN2024!"
    print(f"\n>>> Original Message: '{original_message}'")
    print(f">>> Message Length: {len(original_message)} characters")
    
    # Step 1: String to bit stream
    tx_bits = string_to_bits(original_message)
    print(f"\n[Step 1] Encoding: {len(original_message)} chars → {len(tx_bits)} bits")
    print(f"    First 16 bits: {tx_bits[:16]}")
    
    # Step 2: Modulation
    tx_signal = modulate_bpsk(tx_bits)
    print(f"[Step 2] Modulation: {len(tx_bits)} bits → {len(tx_signal)} samples")
    print(f"    Sampling rate: {SAMPLES_PER_SYMBOL} samples/bit")
    
    # Step 3: Channel transmission
    cable = Cable(length=50, attenuation=0.1, noise_level=0.15, debug_mode=False)
    print(f"[Step 3] Channel Transmission:")
    print(f"    - Cable length: {cable.length}m")
    print(f"    - Attenuation: {cable.attenuation}")
    print(f"    - Noise level: {cable.noise_level}")
    
    rx_signal = cable.transmit(tx_signal)
    print(f"    Transmission complete: {len(tx_signal)} → {len(rx_signal)} samples (with delay)")
    
    # Step 4: Demodulation
    print(f"[Step 4] Demodulation:")
    # Remove delay
    rx_signal_sync = rx_signal[cable.delay_points:]
    rx_bits = demodulate_bpsk(rx_signal_sync)
    print(f"    {len(rx_signal)} samples → {len(rx_bits)} bits")
    
    # Step 5: Decoding
    print(f"[Step 5] Decoding:")
    recovered_message = bits_to_string(rx_bits)
    print(f"    {len(rx_bits)} bits → {len(recovered_message)} characters")
    
    # Result comparison
    print(f"\n>>> Transmission Result:")
    print(f"    Original:  '{original_message}'")
    print(f"    Received:  '{recovered_message}'")
    
    if original_message == recovered_message:
        print("    ✅ SUCCESS! Data transmitted correctly!")
    else:
        print("    ❌ FAILURE! Data mismatch!")
        # Calculate BER
        errors = sum(1 for i in range(min(len(tx_bits), len(rx_bits))) 
                    if tx_bits[i] != rx_bits[i])
        ber = errors / min(len(tx_bits), len(rx_bits))
        print(f"    BER: {ber:.4f} ({errors}/{min(len(tx_bits), len(rx_bits))} bits)")


# ============================================================================
# Demo 2: Message fragmentation functionality
# ============================================================================
def demo_2_fragmentation():
    """
    Demo 2: Message fragmentation functionality
    - Split long message into small fragments
    - Transmit each fragment individually
    - Reassemble at receiver
    """
    print("\n" + "=" * 80)
    print("[Demo 2] Message Fragmentation Transmission")
    print("=" * 80)
    
    print("\n>>> Implementation Method:")
    print("1. Split long message into fragments of fixed size")
    print("2. Encode and transmit each fragment independently")
    print("3. Reassemble all fragments at receiver in order")
    print("4. Verify the reassembled complete message")
    
    # Long message
    long_message = "This is a long message that needs to be fragmented for transmission!"
    chunk_size = 10  # 10 characters per fragment
    
    print(f"\n>>> Original Message: '{long_message}'")
    print(f">>> Message Length: {len(long_message)} characters")
    print(f">>> Fragment Size: {chunk_size} chars/fragment")
    
    # Fragmentation
    fragments = [long_message[i:i+chunk_size] 
                for i in range(0, len(long_message), chunk_size)]
    print(f">>> Total Fragments: {len(fragments)}")
    
    # Create channel (light noise)
    cable = Cable(length=30, attenuation=0.05, noise_level=0.1, debug_mode=False)
    
    # Transmit each fragment
    print(f"\n>>> Starting Fragment Transmission:")
    print("-" * 80)
    received_fragments = []
    
    for idx, fragment in enumerate(fragments, 1):
        # Encode and modulate
        tx_bits = string_to_bits(fragment)
        tx_signal = modulate_bpsk(tx_bits)
        
        # Transmit
        rx_signal = cable.transmit(tx_signal)
        rx_signal_sync = rx_signal[cable.delay_points:]
        
        # Demodulate and decode
        rx_bits = demodulate_bpsk(rx_signal_sync)
        rx_fragment = bits_to_string(rx_bits)
        
        received_fragments.append(rx_fragment)
        
        # Display progress
        status = "✅" if fragment == rx_fragment else "❌"
        print(f"Fragment {idx}/{len(fragments)}: '{fragment[:15]}...' → '{rx_fragment[:15]}...' {status}")
        time.sleep(0.1)  # Simulate transmission delay
    
    print("-" * 80)
    
    # Reassemble
    reassembled_message = ''.join(received_fragments)
    print(f"\n>>> Reassembly Result:")
    print(f"    Original:    '{long_message}'")
    print(f"    Reassembled: '{reassembled_message}'")
    
    if long_message == reassembled_message:
        print("    ✅ Fragment transmission SUCCESS! Complete reassembly!")
    else:
        print("    ❌ Fragment transmission FAILED! Incomplete reassembly!")


# ============================================================================
# Demo 3: System performance under different noise levels
# ============================================================================
def demo_3_noise_impact():
    """
    Demo 3: System performance under different noise levels
    - Test multiple noise levels
    - Calculate bit error rate
    - Visualize noise impact on transmission quality
    """
    print("\n" + "=" * 80)
    print("[Demo 3] System Performance Under Different Noise Levels")
    print("=" * 80)
    
    print("\n>>> Experiment Setup:")
    print("1. Fixed test message")
    print("2. Variable noise level: 0.0 → 1.0")
    print("3. Calculate BER for each noise level")
    print("4. Plot BER vs Noise curve")
    
    # Test parameters
    test_message = "Test Message"
    noise_levels = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    
    print(f"\n>>> Test Message: '{test_message}'")
    print(f">>> Noise Range: {noise_levels[0]} - {noise_levels[-1]}")
    print(f"\n>>> Starting Test:")
    print("-" * 80)
    
    results = []
    tx_bits = string_to_bits(test_message)
    
    for noise in noise_levels:
        # Create channel
        cable = Cable(length=50, attenuation=0.1, noise_level=noise, debug_mode=False)
        
        # Transmission
        tx_signal = modulate_bpsk(tx_bits)
        rx_signal = cable.transmit(tx_signal)
        rx_signal_sync = rx_signal[cable.delay_points:]
        rx_bits = demodulate_bpsk(rx_signal_sync)
        
        # Calculate BER
        min_len = min(len(tx_bits), len(rx_bits))
        errors = sum(1 for i in range(min_len) if tx_bits[i] != rx_bits[i])
        ber = errors / min_len if min_len > 0 else 1.0
        
        # Try to decode
        rx_message = bits_to_string(rx_bits)
        success = (rx_message == test_message)
        
        results.append({
            'noise': noise,
            'ber': ber,
            'errors': errors,
            'success': success
        })
        
        status = "✅ Success" if success else "❌ Failure"
        print(f"Noise {noise:.1f}: BER={ber:.4f} ({errors}/{min_len} errors) - {status}")
    
    print("-" * 80)
    
    # Visualization
    print("\n>>> Generating visualization...")
    plt.figure(figsize=(10, 6))
    
    noise_vals = [r['noise'] for r in results]
    ber_vals = [r['ber'] for r in results]
    colors = ['green' if r['success'] else 'red' for r in results]
    
    plt.bar(noise_vals, ber_vals, color=colors, alpha=0.7, width=0.08)
    plt.axhline(y=0.5, color='orange', linestyle='--', label='Theoretical Failure Threshold (BER=0.5)')
    
    plt.xlabel('Noise Level (σ)', fontsize=12)
    plt.ylabel('Bit Error Rate (BER)', fontsize=12)
    plt.title('Level 1: Impact of Noise on Transmission Quality', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    
    plt.savefig('level1_noise_impact.png', dpi=300)
    print("    ✅ Figure saved: level1_noise_impact.png")
    plt.show()


# ============================================================================
# Demo 4: Shannon formula comparison
# ============================================================================
def demo_4_shannon_comparison():
    """
    Demo 4: Transmission rate comparison with Shannon formula
    - Shannon Formula: C = B * log2(1 + SNR)
    - Compare theoretical capacity with actual throughput
    """
    print("\n" + "=" * 80)
    print("[Demo 4] Transmission Rate vs Shannon Capacity Limit")
    print("=" * 80)
    
    print("\n>>> Theoretical Foundation:")
    print("Shannon-Hartley Theorem: C = B × log₂(1 + SNR)")
    print("  C: Channel capacity (bits/symbol)")
    print("  B: Bandwidth (normalized to 1 for discrete systems)")
    print("  SNR: Signal-to-Noise Ratio")
    
    print("\n>>> Experiment Setup:")
    print("1. Test actual system throughput at different SNR levels")
    print("2. Calculate Shannon theoretical capacity")
    print("3. Compare actual performance with theoretical limit")
    
    # SNR range: -10dB to 20dB
    snr_db_range = np.linspace(-10, 20, 25)
    
    print(f"\n>>> SNR Test Range: {snr_db_range[0]:.1f}dB to {snr_db_range[-1]:.1f}dB")
    print(f">>> Starting test ({len(snr_db_range)} points, please wait)...")
    print("-" * 80)
    
    shannon_capacity = []
    actual_throughput = []
    
    # Test data
    N_BITS = 5000
    tx_bits = np.random.randint(0, 2, N_BITS).tolist()
    
    for idx, snr_db in enumerate(snr_db_range, 1):
        # Calculate noise power
        snr_linear = 10 ** (snr_db / 10.0)
        signal_power = 1.0  # BPSKSignal power
        noise_power = signal_power / snr_linear
        noise_sigma = np.sqrt(noise_power)
        
        # Shannon Capacity
        capacity = np.log2(1 + snr_linear)
        shannon_capacity.append(capacity)
        
        # Actual test
        cable = Cable(length=10, attenuation=0.0, noise_level=noise_sigma, debug_mode=False)
        
        tx_signal = modulate_bpsk(tx_bits)
        rx_signal = cable.transmit(tx_signal)
        rx_signal_sync = rx_signal[cable.delay_points:]
        rx_bits = demodulate_bpsk(rx_signal_sync)
        
        # CalculateBERandMutual Information
        min_len = min(len(tx_bits), len(rx_bits))
        errors = sum(1 for i in range(min_len) if tx_bits[i] != rx_bits[i])
        ber = errors / min_len if min_len > 0 else 0.5
        
        # Mutual Information I = 1 - H(BER)
        if ber == 0 or ber == 1:
            h_ber = 0
        else:
            h_ber = -ber * np.log2(ber) - (1-ber) * np.log2(1-ber)
        
        throughput = 1.0 - h_ber
        throughput = max(0, throughput)  # Ensure non-negative
        actual_throughput.append(throughput)
        
        # Display progress
        if idx % 5 == 0:
            print(f"Progress: {idx}/{len(snr_db_range)} - SNR={snr_db:.1f}dB, "
                  f"Shannon={capacity:.3f}, Actual={throughput:.3f}")
    
    print("-" * 80)
    print(">>> Test complete! Generating comparison plot...")
    
    # Plot comparison
    plt.figure(figsize=(12, 7))
    
    # Shannon limit
    plt.plot(snr_db_range, shannon_capacity, 'k--', 
             linewidth=2.5, label='Shannon Capacity Limit (Theoretical)')
    
    # Actual BPSK performance
    plt.plot(snr_db_range, actual_throughput, 'b-o', 
             linewidth=2.0, markersize=5, label='BPSK Actual Throughput')
    
    # Fill gap
    plt.fill_between(snr_db_range, actual_throughput, shannon_capacity,
                     color='#E0E0E0', alpha=0.5, label='Unachieved Capacity Gap')
    
    # Annotate key points
    plt.annotate('Waterfall Region\n(High Noise)', xy=(-5, 0.2), xytext=(-8, 1.0),
                arrowprops=dict(facecolor='red', shrink=0.05, width=2),
                fontsize=11, bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))
    
    plt.annotate('BPSK Saturation\n(1 bit/symbol)', xy=(15, 1.0), xytext=(12, 2.0),
                arrowprops=dict(facecolor='blue', shrink=0.05, width=2),
                fontsize=11, bbox=dict(boxstyle='round', facecolor='cyan', alpha=0.3))
    
    plt.xlabel('Signal-to-Noise Ratio SNR (dB)', fontsize=14)
    plt.ylabel('Spectral Efficiency (bits/symbol)', fontsize=14)
    plt.title('Level 1: System Performance vs Shannon Capacity Limit', fontsize=16, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper left', fontsize=12)
    plt.xlim([-10, 20])
    plt.ylim([0, 7])
    
    plt.tight_layout()
    plt.savefig('level1_shannon_comparison.png', dpi=300)
    print("    ✅ Figure saved: level1_shannon_comparison.png")
    plt.show()
    
    # Analysis results
    print("\n>>> Analysis Results:")
    # Find SNR where BPSK reaches 0.9 bit/symbol
    idx_90 = None
    for i, thr in enumerate(actual_throughput):
        if thr >= 0.9:
            idx_90 = i
            break
    
    if idx_90 is not None:
        print(f"    - BPSK reaches 0.9 bit/symbol at SNR={snr_db_range[idx_90]:.1f}dB")
        print(f"    - Corresponding Shannon capacity: {shannon_capacity[idx_90]:.2f} bit/symbol")
        print(f"    - Capacity utilization: {actual_throughput[idx_90]/shannon_capacity[idx_90]*100:.1f}%")
    
    # Gap at high SNR
    high_snr_idx = -1
    print(f"    - At high SNR ({snr_db_range[high_snr_idx]:.1f}dB):")
    print(f"      Shannon capacity: {shannon_capacity[high_snr_idx]:.2f} bit/symbol")
    print(f"      BPSK actual:      {actual_throughput[high_snr_idx]:.2f} bit/symbol")
    print(f"      Efficiency:       {actual_throughput[high_snr_idx]/shannon_capacity[high_snr_idx]*100:.1f}%")
    print(f"\n    ✅ Conclusion: Due to fixed modulation order, BPSK cannot approach Shannon limit,")
    print(f"                  wasting significant channel capacity at high SNR!")


# ============================================================================
# Main function
# ============================================================================
def main():
    """Main function: run all demonstrations"""
    print("\nStarting Level 1 demonstrations...")
    print("Note: Some demos will generate visualization charts. Close the chart window to continue.\n")
    
    try:
        # Demo 1: Basic transmission
        demo_1_basic_transmission()
        input("\nPress Enter to continue to next demo...")
        
        # Demo 2: Fragmentation
        demo_2_fragmentation()
        input("\nPress Enter to continue to next demo...")
        
        # Demo 3: Noise impact
        demo_3_noise_impact()
        input("\nPress Enter to continue to next demo...")
        
        # Demo 4: Shannon comparison
        demo_4_shannon_comparison()
        
        print("\n" + "=" * 80)
        print("🎉 Level 1 All Demos Completed!")
        print("=" * 80)
        print("\nGenerated files:")
        print("  - level1_noise_impact.png (Noise impact analysis)")
        print("  - level1_shannon_comparison.png (Shannon formula comparison)")
        
    except KeyboardInterrupt:
        print("\n\nUser interrupted demo.")
    except Exception as e:
        print(f"\n\nError occurred during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

