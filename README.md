# AirControl

A modular, real-time gesture interface for controlling a computer using hand tracking.

AirControl uses real-time hand tracking to interpret gestures and map them to system actions such as mouse input, media control, scrolling, and window navigation.

---

## Overview

AirControl is built as a modular, real-time pipeline:

```
Webcam → Hand tracking → Gesture detection → Gesture events → Priority resolution → Mapping → Command execution
```

Hand landmarks are extracted using Google’s MediaPipe framework and converted into higher-level gesture events. These events are then mapped to actions through a configurable system, allowing flexible control without modifying core logic.

---

## Key Features

- Real-time hand tracking using MediaPipe
- Event-based gesture detection (`gesture.*`)
- Configurable gesture → action mappings (YAML)
- Priority-based conflict resolution
- Plugin-based architecture for detectors and commands
- Cursor control with smoothing and mode switching

---

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Optional development tools:

```bash
pip install -e "[dev]"
```

---

## Usage

Run the application:

```bash
aircontrol
```

Controls:
- `q` → quit
- `t` → toggle cursor control

---

## Gesture System

Gesture behaviour is defined through configuration files:

- Mapping: `src/aircontrol/config/gesture_map.yaml`
- Priority: `src/aircontrol/config/gesture_priority.yaml`

The following gestures are currently supported and mapped to system actions:

### Current Gesture Set

| Gesture | Action |
|--------|--------|
| Pinch | Left click |
| Middle pinch | Right click |
| Ring pinch (start/move/end) | Drag |
| Index–middle pinch | Toggle cursor mode |
| Fist | Toggle mute |
| Volume up hold | Increase volume |
| Volume down hold | Decrease volume |
| Open palm hold | Play / pause media |
| Horizontal yo | Screenshot |
| Two-finger hold | Continuous scroll |
| Flag wave right | Move window left |
| Flag wave left | Move window right |
| Vulcan salute | Quit application |

---

## Architecture

AirControl is designed as a modular system with clear separation of responsibilities:

- **Tracking**: Extract hand landmarks (MediaPipe)
- **Detection**: Convert landmarks → gesture events
- **Mapping**: Map gestures → actions (configurable)
- **Priority**: Resolve conflicts between simultaneous gestures
- **Commands**: Execute system-level actions

This separation allows gestures, actions, and mappings to evolve independently.

---

## Project Structure

```
src/aircontrol/
  actions/      # system actions (mouse, media, window, etc.)
  camera/       # webcam interface
  config/       # gesture mapping + priority config
  cursor/       # cursor modes, smoothing, controller
  gestures/     # event system, dispatcher, mapper
  plugins/
    detectors/  # gesture detectors
    commands/   # action handlers
  tracking/     # MediaPipe integration
  main.py       # entrypoint
```

---

## Notes

- Some features are currently macOS-specific (media and window control).
- If a plugin fails to load, errors will be shown in the startup logs.

---

## Future Improvements

- Improve gesture robustness and stability
- Refine smoothing and interaction responsiveness
- Expand cross-platform support
- Add more gesture primitives and composite gestures

## License

This project is licensed under the MIT License.