import sys
import numpy as np
from scipy.io.wavfile import read as wavread
from pysoundcard import Stream

"""Play an audio file."""

fs, wave = wavread(sys.argv[1])
print(fs)
wave = np.array(wave, dtype=np.int16)

blocksize = 256
s = Stream(samplerate=fs, blocksize=blocksize, dtype='int16')
s.start()
while True:
    s.write(wave[0:(1024*100)])
s.stop()
