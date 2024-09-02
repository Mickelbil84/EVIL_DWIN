#####################################################################################################
# Transcribed from C++ [https://github.com/mathertel/RotaryEncoder/blob/master/src/RotaryEncoder.h]
#####################################################################################################

import time
from enum import Enum

#import RPi.GPIO as GPIO
import LePotatoPi.GPIO.GPIO as GPIO

def millis():
    return round(time.time() * 1000)

class Direction(Enum):
    NOROTATION = 0
    CLOCKWISE = 1
    COUNTERCLOCKWISE = -1

class LatchMode(Enum):
    FOUR3 = 1 # 4 steps, Latch at position 3 only (compatible to older versions)
    FOUR0 = 2 # 4 steps, Latch at position 0 (reverse wirings)
    TWO03 = 3 # 2 steps, Latch at position 0 and 3 

LATCH0 = 0
LATCH3 = 3
KNOBDIR = [
    0, -1, 1, 0,
    1, 0, 0, -1,
    -1, 0, 0, 1,
    0, 1, -1, 0
]

class RotaryEncoder(object):
    def __init__(self, pin1: int, pin2: int, mode: LatchMode = LatchMode.FOUR0):
        self._pin1 = pin1
        self._pin2 = pin2
        self._mode = mode

        GPIO.setup(self._pin1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self._pin2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        sig1 = GPIO.input(self._pin1)
        sig2 = GPIO.input(self._pin2)
        self._oldState = sig1 | (sig2 << 1)

        self._position = 0
        self._positionExt = 0
        self._positionExtPrev = 0
        self._positionExtTime = 0
        self._positionExtTimePrev = 0
    
    def getPosition(self) -> int:
        return self._positionExt

    def getDirection(self) -> Direction:
        ret = Direction.NOROTATION

        if self._positionExtPrev > self._positionExt:
            ret = Direction.COUNTERCLOCKWISE
        elif self._positionExtPrev < self._positionExt:
            ret = Direction.CLOCKWISE
        else:
            ret = Direction.NOROTATION

        self._positionExtPrev = self._positionExt
        return ret

    def setPosition(self, newPosition: int):
        if self._mode == LatchMode.FOUR3 or self._mode == LatchMode.FOUR0:
            self._position = ((newPosition << 2) | (self._position & 0x03))
            self._positionExt = newPosition
            self._positionExtPrev = newPosition
        elif self._mode == LatchMode.TWO03:
            self._position = ((newPosition << 1) | (self._position & 0x01))
            self._positionExt = newPosition
            self._positionExtPrev = newPosition

    def tick(self):
        sig1 = GPIO.input(self._pin1)
        sig2 = GPIO.input(self._pin2)
        thisState = sig1 | (sig2 << 1)

        if self._oldState == thisState:
            return

        self._position += KNOBDIR[thisState | (self._oldState << 2)]
        self._oldState = thisState

        if self._mode == LatchMode.FOUR3 and thisState == LATCH3:
            self._positionExt = self._position >> 2
            self._positionExtTimePrev = self._positionExtTime
            self._positionExtTime = millis()
        elif self._mode == LatchMode.FOUR0 and thisState == LATCH0:
            self._positionExt = self._position >> 2
            self._positionExtTimePrev = self._positionExtTime
            self._positionExtTime = millis()
        elif self._mode == LatchMode.TWO03 and ((thisState == LATCH0) or (thisState == LATCH3)):
            self._positionExt = self._position >> 1
            self._positionExtTimePrev = self._positionExtTime
            self._positionExtTime = millis()

    def getMillisBetweenRotations(self) -> int:
        return self._positionExtTime - self._positionExtTimePrev

    def getRPM(self) -> int:
        timeBetweenLastPositions = self._positionExtTime - self._positionExtTimePrev
        timeToLastPosition = millis() - self._positionExtTime
        t = float(max(timeBetweenLastPositions, timeToLastPosition))
        return 60000.0 / (t * 20.0)


# Simple test
if __name__ == "__main__":
    encoder = RotaryEncoder(26, 19, LatchMode.TWO03)
    while True:
        encoder.tick()
        direction = encoder.getDirection()
        if direction != Direction.NOROTATION:
            print(direction)