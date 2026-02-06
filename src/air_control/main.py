# src/air_control/main.py
from pynput.keyboard import Key, Controller, Listener

# Create keyboard controller
kb = Controller()

# --- DEMO OUTPUT (comment these while testing listener if needed) ---
kb.press('a')
kb.release('a')
kb.type('Hello World')

def on_press(key):
    try:
        print(f"Alphanumeric key {key.char} pressed")
    except AttributeError:
        print(f"Special key {key} pressed")

def on_release(key):
    print(f"Key {key} released")
    if key == Key.esc:
        print("ESC pressed, exiting listener")
        return False  # stop listener

# Start listening
with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()