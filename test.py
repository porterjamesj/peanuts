#! /usr/bin/env python

from pysoundcard import Stream, continue_flag
from webrtcvad import Vad
from scipy.io.wavfile import read as wavread
import numpy as np

import time
from collections import deque
from itertools import cycle, islice


SAMPLE_RATE = 32000
HOP_S = 320  # this is the number of frames in 10 ms


# onset params
LAG_TIME = 5  # in ms
NECESSARY_FRACTION = 0.3


def open_wav(name="teacher.wav"):
    sr, wave = wavread(name)
    assert sr == SAMPLE_RATE
    wav = np.array(wave, dtype=np.int16)
    wav = (wav[:, 0:1] + wav[:, 1:2]) / 2
    return wav


class VoiceOver(object):
    """
    Bag of state for tracking stuff in the stream callback.
    """

    def __init__(self):
        self.input_buf = np.empty((256, 1), dtype=np.int16)
        self.vad = Vad(3)
        self.vad_q = deque([False], LAG_TIME)
        self.output = cycle(open_wav())

    def callback(self, in_data, out_data, time_info, status):
        self.input_buf = np.concatenate((self.input_buf, in_data))
        if len(self.input_buf) > HOP_S:  # we can pass data to vad
            ten_ms, rest = self.input_buf[0:HOP_S], self.input_buf[HOP_S:]
            self.vad_q.append(
                self.vad.is_speech(ten_ms.tostring(), SAMPLE_RATE)
            )
            self.input_buf = rest
        if sum(self.vad_q) > len(self.vad_q)*NECESSARY_FRACTION:
            out_data[:] = list(islice(self.output, len(out_data)))
        else:
            out_data[:] = np.zeros(out_data.shape)
        return continue_flag


def open_mic_stream():
    return Stream(
        blocksize=256,  # TODO not sure what this does
        channels=1,
        dtype='int16',
        samplerate=SAMPLE_RATE,
    )


def main():
    vo = VoiceOver()
    s = Stream(
        blocksize=256,  # TODO not sure what this does
        channels=1,
        dtype='int16',
        samplerate=SAMPLE_RATE,
        callback=vo.callback,
    )
    s.start()
    while True:
        time.sleep(5)
    s.stop()


if __name__ == "__main__":
    main()
