from cable import Cable
import numpy as np

cable = Cable(length=100, attenuation=0.1, noise_level=0.05, debug_mode=True)

# Transmit signal
duration = 1.0  # seconds
sample_rate = 1000  # Hz
frequency = 5  # Hz (5 cycles per second)

# Time array
t = np.linspace(0, duration, int(duration * sample_rate), endpoint=False)

# Generate sine wave
signal = np.sin(2 * np.pi * frequency * t)
received_signal = cable.transmit(signal)

# Get propagation delay
delay = cable.get_propagation_delay()

# Plot waveforms (debug mode)
cable.plot_signals()

# Get statistics
stats = cable.get_signal_stats()