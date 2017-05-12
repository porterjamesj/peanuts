#! /usr/bin/env python

from pysoundcard import Stream
from webrtcvad import Vad
from scipy.io.wavfile import read as wavread
import numpy as np

from itertools import cycle


SAMPLE_RATE = 32000
HOP_S = 320  # this is the number of frames in 10 ms

_sr, wave = wavread("teacher.wav")
wave = np.array(wave, dtype=np.int16)


def open_mic_stream():
    return Stream(
        blocksize=256,  # TODO not sure what this does
        channels=1,
        dtype='int16',
        samplerate=SAMPLE_RATE,
    )


def main():
    mic = open_mic_stream()
    vad = Vad(3)

    mic.start()

    i = 0
    while True:
        mic.write(wave[i:i+1024])
        i += 1024
        sample = mic.read(HOP_S).tostring()
        print(vad.is_speech(sample, SAMPLE_RATE))

        # TODO hmmmm, probably remove
        if len(sample) < HOP_S:
            break


if __name__ == "__main__":
    main()
