# Data Communication and Networks - Course Project

## Project Overview

This project requires you to build a complete network communication system from the ground up. You need to simulate the communication process from the physical layer to the application layer.

## Project Requirements

### Level 1: Point-to-Point Communication (30 points)

**Scenario**: Two hosts connected directly via cable

**Requirements**:

1. Implement digital signal generation (convert data to bit stream)
2. Implement modulator (convert digital signal to analog signal)
3. Use the provided `Cable` class to transmit signals
4. Implement demodulator (recover digital signal from analog signal)
5. Implement data recovery (convert bit stream back to original data)

**Flow**:

```
Host A: Data → Bit Stream → Modulation → Analog Signal → Cable → Analog Signal → Demodulation → Bit Stream → Data :Host B
```

**Grading Criteria**:

- Successfully transmit simple strings (15 points)
- Handle longer messages (5 points)
- Basic error detection mechanism (10 points)

---

### Level 2: Multi-Host Communication (30 points)

**Scenario**: N hosts connected to the same channel

**Requirements**:

1. Based on Level 1, design a mechanism to distinguish different hosts
2. Implement addressing mechanism (how to specify target host)
3. Implement routing/forwarding mechanism (how messages reach their destination)
4. Handle simultaneous transmissions from multiple hosts

**Grading Criteria**:

- Distinguish different hosts (15 points)
- Correctly route to target host (15 points)

---

### Level 3: Extension Features (at most 40 points)

Choose from the following features to implement (can select multiple):

#### Transport Layer (15 points)

- Implement reliable transport (ACK/NACK)
- Implement sequence numbers
- Implement timeout retransmission
- Implement flow control

#### Channel Coding (15 points)

- Implement Hamming code or other error correction codes
- Implement CRC checksum
- Correct transmission errors
- Performance testing (error rate vs correction rate)

#### Application Layer Protocol (10 points)

- Design application layer protocol (e.g., HTTP, FTP, etc.)
- Implement request-response pattern
- Implement protocol parsing

#### Performance Optimization (10 points)

- Implement multiple modulation schemes (ASK, FSK, PSK, etc.)
- Compare performance of different modulation schemes

#### Wireless Communication (10 points)

- Use wireless channel (instead of cable).
- MIMO.
- Precoding & combining (beamforming).

## Provided Tools

### Cable Class (cable.py)

This is the only infrastructure provided by the course, simulating the physical transmission medium. See, **cables are everywhere. So implement it (call it) everywhere.**

**Main Methods**:

```python
cable = Cable(length=100, attenuation=0.1, noise_level=0.05, debug_mode=True)

# Transmit signal
received_signal = cable.transmit(signal)

# Get propagation delay
delay = cable.get_propagation_delay()

# Plot waveforms (debug mode)
cable.plot_signals()

# Get statistics
stats = cable.get_signal_stats()
```

**Parameter Descriptions**:

- `length`: Cable length (meters)
- `attenuation`: Attenuation coefficient
- `noise_level`: Noise level (higher means more noise)
- `debug_mode`: Whether to enable debug mode (display waveforms)

---

## Getting Started

### 1. Understand the Cable Class

Run the provided example:

```bash
python cable.py
```

### 2. Implement Level 1

Start with the simplest approach:

**Step 1**: Implement a simple modulator

```python
def modulate(bits):
    # Convert bits to analog signal
    # Hint: Use high level for 1, low level for 0
    pass
```

**Step 2**: Implement demodulator

```python
def demodulate(signal):
    # Recover bits from analog signal
    pass
```

**Step 3**: Test

```python
# Sender
message = "Hello"
bits = string_to_bits(message)
signal = modulate(bits)

# Transmission
cable = Cable()
received_signal = cable.transmit(signal)

# Receiver
received_bits = demodulate(received_signal)
received_message = bits_to_string(received_bits)

print(f"Sent: {message}")
print(f"Received: {received_message}")
```

## Grading Criteria

- **Level 1 (30 points)**: Basic communication functionality
- **Level 2 (30 points)**: Multi-host addressing and routing
- **Level 3 (40 points)**: Extension features (multiple options available)

**Total Score**: 100 points (60 points base + 40 points extensions)

---

## FAQ

**Q1: How to generate analog signals?**
A: The simplest way is using numpy arrays. Use high level (e.g., 1.0) for 1 and low level (e.g., 0.0) for 0. Each bit can be represented by multiple sample points.

For example, to generate a sine wave (analog signal):

```python
import numpy as np

# Parameters
duration = 1.0  # seconds
sample_rate = 1000  # Hz
frequency = 5  # Hz (5 cycles per second)

# Time array
t = np.linspace(0, duration, int(duration * sample_rate), endpoint=False)

# Generate sine wave
analog_signal = np.sin(2 * np.pi * frequency * t)
```

**Q2: Will noise affect communication?**
A: Yes! That's why you need to design good modulation schemes and error detection mechanisms. Start with low noise for testing, then gradually increase it.

**Q3: Must I implement all levels?**
A: No. Levels 1 and 2 are foundational (60 points), Level 3 is for extensions (40 points). Choose based on your time and capability.

**Q4: Can I use third-party libraries?**
A: You can use common libraries like numpy and matplotlib, but core modulation/demodulation and protocol design must be implemented by yourself.

**Q5: How to debug?**
A: Use Cable's debug_mode to view signal waveforms. You can also use print statements for intermediate results.

Happy coding! If you have questions, please contact the TA (yaolj2024@mail.sustech.edu.cn). We prioritize these who draw their issues in GitHub.
