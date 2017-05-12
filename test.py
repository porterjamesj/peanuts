#! /usr/bin/env python

from pysoundcard import Stream
from soundfile import blocks
from webrtcvad import Vad

from itertools import cycle


SAMPLE_RATE = 32000
HOP_S = 320  # this is the number of frames in 10 ms


def open_mic_stream():
    return Stream(
        blocksize=HOP_S,  # TODO not sure what this does
        channels=1,
        dtype='int16',
        samplerate=SAMPLE_RATE
    )


def open_speaker_stream():
    return Stream(44100)


def infinite_teacher_noise():
    return cycle(blocks(
        "teacher.wav",
        1000000
    ))


def main():
    mic = open_mic_stream()
    speak = open_speaker_stream()
    vad = Vad(3)  # TODO maybe 3?

    speak.start()
    # soundcard.start()

    for noise in infinite_teacher_noise():
        # sample = soundcard.read(HOP_S).tostring()
        speak.write(noise)
        # print(vad.is_speech(sample, SAMPLE_RATE))

        # # TODO hmmmm, probably remove
        # if len(sample) < HOP_S:
        #     break


if __name__ == "__main__":
    main()
