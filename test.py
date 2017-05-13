#! /usr/bin/env python

from pysoundcard import Stream, continue_flag
from webrtcvad import Vad
from scipy.io.wavfile import read as wavread
import numpy as np

import time
from collections import deque
from itertools import cycle, islice


SAMPLE_RATE = 32000
HOP_SIZE = 3*(SAMPLE_RATE / 100)  # this is the number of frames in 10 ms
BLOCK_SIZE = 256  # TODO hmmmm

# onset params TODO tweak a lot
LAG_TIME = 7  # in ms
NECESSARY_FRACTION = 0.5


def open_wav(name="teacher.wav"):
    sr, wave = wavread(name)
    assert sr == SAMPLE_RATE
    wav = np.array(wave, dtype=np.int16)
    wav = (wav[:, 0:1] + wav[:, 1:2]) / 2  # stereo -> mono
    return wav


class VoiceOver(object):
    """
    Bag of state for tracking stuff in the stream callback.
    """

    def __init__(self):
        self.input_buf = np.empty((BLOCK_SIZE, 1), dtype=np.int16)
        self.vad = Vad(3)
        self.vad_q = deque([False], LAG_TIME)
        self.output = cycle(open_wav())

    def output_take(self, n_bytes):
        return list(islice(self.output, n_bytes))

    def input_is_talking(self):
        return sum(self.vad_q) > len(self.vad_q)*NECESSARY_FRACTION

    def callback(self, in_data, out_data, time_info, status):
        self.input_buf = np.concatenate((self.input_buf, in_data))
        if len(self.input_buf) > HOP_SIZE:  # we can pass data to vad
            ten_ms, rest = (self.input_buf[0:HOP_SIZE],
                            self.input_buf[HOP_SIZE:])
            self.vad_q.append(
                self.vad.is_speech(ten_ms.tostring(), SAMPLE_RATE)
            )
            self.input_buf = rest
        if self.input_is_talking():
            out_data[:] = self.output_take(len(out_data))
        else:
            out_data[:] = np.zeros(out_data.shape)
        return continue_flag


def main():
    vo = VoiceOver()
    soundcard = Stream(
        blocksize=BLOCK_SIZE,
        channels=1,
        dtype='int16',
        samplerate=SAMPLE_RATE,
        callback=vo.callback,
    )
    soundcard.start()
    while True:
        time.sleep(5)
    soundcard.stop()


if __name__ == "__main__":
    main()
