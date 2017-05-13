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

_sr, wave = wavread("teacher.wav")
wave = np.array(wave, dtype=np.int16)
wave = wave[:, 0:1]  # turn to mono by just picking one channel lol

forever_wave = cycle(wave)


def open_mic_stream():
    return Stream(
        blocksize=256,  # TODO not sure what this does
        channels=1,
        dtype='int16',
        samplerate=SAMPLE_RATE,
    )


buf = np.empty((256, 1), dtype=np.int16)
vad = Vad(3)
vad_q = deque([False], 5)


def callback(in_data, out_data, time_info, status):
    global buf  # TODO yuk
    buf = np.concatenate((buf, in_data))
    if len(buf) > HOP_S:  # we can pass data to vad
        ten_ms, rest = buf[0:HOP_S], buf[HOP_S:]
        vad_q.append(vad.is_speech(ten_ms.tostring(), SAMPLE_RATE))
        buf = rest
    if sum(vad_q) > len(vad_q)*0.3:
        out_data[:] = list(islice(forever_wave, len(out_data)))
    else:
        out_data[:] = np.zeros(out_data.shape)
    return continue_flag


def main():
    s = Stream(
        blocksize=256,  # TODO not sure what this does
        channels=1,
        dtype='int16',
        samplerate=SAMPLE_RATE,
        callback=callback
    )
    s.start()
    time.sleep(10000)
    s.stop()


if __name__ == "__main__":
    main()
