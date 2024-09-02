import time

from config import *
from screens import *
from hardware.dwin import *
from hardware.rotary_encoder import *

class EvilDwin(object):
    def __init__(self):
        self.lcd = T5UIC1_LCD(LCD_COM_Port)
        self.screen = Screen_MainMenu(self.lcd)
        
        self.rotary = RotaryEncoder(ENCODER_PIN_A, ENCODER_PIN_B, LatchMode.TWO03)
        self.last_rotary_time = time.time()
    
    def handle_input(self):
        if time.time() - self.last_rotary_time < ROTARY_DELAY:
            return
        
        self.rotary.tick()
        direction = self.rotary.getDirection()
        if direction == Direction.NOROTATION:
            return
        elif direction == Direction.CLOCKWISE:
            event = EVENT_ROTARY_CW
        elif direction == Direction.COUNTERCLOCKWISE:
            event = EVENT_ROTARY_CCW
        
        self.screen.handle_input(event)
        self.last_rotary_time = time.time()

    def run(self):
        while True:
            self.handle_input()

if __name__ == "__main__":
    app = EvilDwin()
    app.run()