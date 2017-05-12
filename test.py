#! /usr/bin/env python

from pysoundcard import Stream
from webrtcvad import Vad

SAMPLE_RATE = 32000
HOP_S = 320  # this is the number of frames in 10 ms

s = Stream(
    blocksize=HOP_S,  # TODO not sure what this does
    channels=1,
    dtype='int16',
    samplerate=SAMPLE_RATE
)

v = Vad(2)

s.start()


while True:
    vec = s.read(HOP_S)
    print(v.is_speech(vec.tostring(), SAMPLE_RATE))

    if len(vec) < HOP_S:
        break
