import serial
import numpy as np
import matplotlib.pyplot as plt

#Config
serialPortName = 'COM4'
baudRate = 1000000
samplingRate = 24000
bytesPerSample = 4

serialPort = serial.Serial(serialPortName, baudRate, timeout=0)

plt.ion()
figure, axis = plt.subplots()

plotLength = 2048
audioBuffer = np.zeros(plotLength, dtype=np.float32)

waveformLine, = axis.plot(audioBuffer)
axis.set_ylim(-0.025, 0.025)
axis.set_xlim(0, plotLength)
axis.set_title("Live Waveform")
axis.set_xlabel("Sample")
axis.set_ylabel("Amplitude")

rawDataBuffer = bytearray()

while True:
    incomingBytes = serialPort.read(4096)
    if incomingBytes:
        rawDataBuffer.extend(incomingBytes)

    availableSamples = len(rawDataBuffer) // bytesPerSample
    if availableSamples == 0:
        plt.pause(0.001)
        continue

    bytesToProcess = availableSamples * bytesPerSample
    rawChunk = rawDataBuffer[:bytesToProcess]
    rawDataBuffer = rawDataBuffer[bytesToProcess:]

    array32Bit = np.frombuffer(rawChunk, dtype='<i4')
    array24Bit = (array32Bit >> 8).astype(np.int32)
    scaledAudio = array24Bit / float(2**23)

    if len(scaledAudio) >= plotLength:
        audioBuffer = scaledAudio[-plotLength:]
    else:
        audioBuffer = np.roll(audioBuffer, -len(scaledAudio))
        audioBuffer[-len(scaledAudio):] = scaledAudio

    waveformLine.set_ydata(audioBuffer)
    figure.canvas.draw()
    figure.canvas.flush_events()
