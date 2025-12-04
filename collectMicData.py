import serial
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt

#Config
PORT = 'COM10'
BAUDRATE = 1000000
SAMPLINGRATE = 24000 #24kHz
DURATION = 5 #In seconds
BYTESPERSAMPLE = 4 #32-bit per sample
SAMPLESAMOUNT = SAMPLINGRATE * DURATION
BYTESNEEDED = SAMPLESAMOUNT * BYTESPERSAMPLE

#Open serial port
serialPort = serial.Serial(PORT, BAUDRATE, timeout=1)

print(f"Capturing {DURATION} sec of audio ({SAMPLESAMOUNT} samples)...")

#Read exact number of bytes
data = bytearray()
while len(data) < BYTESNEEDED:
    chunk = serialPort.read(BYTESNEEDED - len(data))
    if chunk:
        data.extend(chunk)

serialPort.close() #Now that we have the data, we can close the serialport again
print(f"Read {len(data)} bytes from serial")

#Convert raw audio data into data suitable for wav files
array32Bit = np.frombuffer(data, dtype='<i4') #Convert 32-bit little-endian words
array24Bit = (array32Bit >> 8).astype(np.int32) #Extract top 24 bits (MSB-aligned)
scaledAudio = array24Bit / float(2**23)

#Save as 24-bit .wav file
sf.write('audio/capture.wav', scaledAudio, SAMPLINGRATE, subtype='PCM_24')
print("Saved capture.wav")

plt.plot(scaledAudio[:1000])
plt.title("Waveform (first 1000 samples)")
plt.xlabel("Sample")
plt.ylabel("Amplitude")
plt.show()
