import librosa
import librosa.display
import matplotlib.pylab as plt
import sys
import numpy
numpy.set_printoptions(threshold=sys.maxsize)
y, sr = librosa.load('C:\\lectureshort.wav', sr=1000)
# y is the signal data (amplitude), sr is the sample rate
#y, sr = librosa.load(librosa.ex('trumpet'), duration=10)
fig, ax = plt.subplots(nrows=1, sharex=True)
librosa.display.waveshow(y, sr=sr)
#print(y)
file = open("file1.txt", "w+")
file.write(str(y))
file.close()

"""
plt.figure()
plt.plot(y)
plt.xlabel('time')
plt.ylabel('amplitude')
plt.plot()
"""