# Air Control

Hand-gesture based laptop control using MediaPipe, OpenCV, and a plugin-driven event system.

## Features
- Real-time hand tracking from webcam.
- Gesture detectors emit `gesture.*` events.
- YAML maps gestures to actions.
- Command plugins execute mouse/media/window/app actions.
- Cursor controller supports mode toggling and smoothing.

## Requirements
- Python 3.10+
- Webcam
- macOS recommended for media/window/call actions in this repo

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Optional dev tools:
```bash
pip install -e ".[dev]"
```

## Run
```bash
aircontrol
```

Press:
- `q` to quit
- `t` to toggle cursor enable/disable

## Gesture Mapping
Mappings live in `src/aircontrol/config/gesture_map.yaml`.

Current defaults include:
- `gesture.pinch` -> `mouse.click`
- `gesture.middle_pinch` -> `mouse.right_click`
- `gesture.ring_pinch.start/move/end` -> `drag.start/move/end`
- `gesture.index_middle_pinch` -> `cursor.toggle_mode`
- `gesture.fist` -> `media.mute_toggle`
- `gesture.volume_up_hold` -> `media.volume_up`
- `gesture.volume_down_hold` -> `media.volume_down`
- `gesture.open_palm_hold` -> `media.play_pause`
- `gesture.horizontal_yo` -> `camera.screenshot`
- `gesture.two_finger_hold` -> `scroll.continuous`
- `gesture.flag_wave_right` -> `window.left`
- `gesture.flag_wave_left` -> `window.right`
- `gesture.vulcan_salute` -> `app.quit`

Priority resolution is configured in `src/aircontrol/config/gesture_priority.yaml`.

## Project Structure
```text
src/aircontrol/
  actions/      # action backends (mouse, media, window, screenshot, call)
  camera/       # webcam wrapper
  config/       # gesture map + priority config
  cursor/       # cursor modes, mapping, smoothing, controller
  gestures/     # engine, dispatcher, mapper, plugin interfaces
  plugins/
    detectors/  # gesture detectors
    commands/   # action command handlers
  tracking/     # MediaPipe hand tracking
  main.py       # app entrypoint
```

## Notes
- Some actions are OS-specific (currently macOS-oriented).
- If a plugin fails to load, startup logs will print the module and error.
