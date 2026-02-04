# src/air_control/main.py
from pynput.keyboard import Key, Controller
from pynput import keyboard


# press and release the 'a' key
keyboard = Controller()
keyboard.press('a')
keyboard.release('a')

# type a full word
keyboard.type('Hello World')

# special keys
keyboard.press(Key.space)
keyboard.release(Key.space)
keyboard.press(Key.enter)
keyboard.release(Key.enter)

