[![CI](https://github.com/ChamuV/air-control/actions/workflows/ci.yml/badge.svg)](https://github.com/ChamuV/air-control/actions)

# AirControl

A modular, real-time gesture interface for controlling a computer using hand tracking.

AirControl uses real-time hand tracking to interpret gestures and map them to system actions such as mouse input, media control, scrolling, and window navigation.

---

## Overview

AirControl is built as a modular, real-time pipeline:

```
Webcam input
    ↓
MediaPipe landmark extraction
    ↓
Gesture detection
    ↓
Gesture events
    ↓
Priority resolution (conflict handling + locks)
    ↓
Gesture mapping (config-driven)
    ↓
Command execution (mouse / media / system)
```

Hand landmarks are extracted using Google’s MediaPipe framework and converted into higher-level gesture events. These events are then mapped to actions through a configurable system, allowing flexible control without modifying core logic.

---

## Key Features

- Real-time hand tracking using MediaPipe
- Event-based gesture detection (`gesture.*`)
- Configurable gesture → action mappings (YAML)
- Priority-based conflict resolution with gesture locks for drag and scroll
- Plugin-based architecture for detectors and commands
- Cursor control with smoothing and mode switching
- Continuous integration with GitHub Actions (linting + tests on push / PR)

---

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

For development work (tests + linting):

```bash
pip install -e "[dev]"
```

This project uses `pyproject.toml` for dependency management, so a separate `requirements.txt` file is not required for normal installation.

---

## Usage

Run the application:

```bash
aircontrol
```

Controls:
- `q` → quit
- `t` → toggle cursor control

### Development / checks

Run the test suite:

```bash
pytest
```

Run linting:

```bash
ruff check .
```

A GitHub Actions CI workflow is included so tests and lint checks run automatically on pushes and pull requests.

---

## Gesture System

Gesture behaviour is defined through configuration files:

- Mapping: `src/aircontrol/config/gesture_map.yaml`
- Priority: `src/aircontrol/config/gesture_priority.yaml`

The following gestures are currently supported and mapped to system actions in the default profile:

### Current Gesture Set

| Gesture | Action |
|--------|--------|
| Pinch | Left click |
| Middle pinch | Right click |
| Ring pinch (start/move/end) | Drag |
| Pinky pinch (thumb + pinky) | Toggle cursor mode |
| Index–middle pinch (hold + move) | Scroll mode (continuous up/down scrolling) |
| Middle pinch swipe (left/right) | Switch windows / spaces |
| Fist | Toggle mute |
| Volume up hold | Increase volume |
| Volume down hold | Decrease volume |
| Open palm hold | Play / pause media |
| Horizontal yo | Screenshot |
| Call sign (thumb + pinky extended) | Start call |
| Vulcan salute | Quit application |

---

## Architecture

AirControl is designed as a modular system with clear separation of responsibilities:

- **Tracking**: Extract hand landmarks (MediaPipe)
- **Detection**: Convert landmarks → gesture events
- **Mapping**: Map gestures → actions (configurable)
- **Priority**: Resolve conflicts between simultaneous gestures
- **Commands**: Execute system-level actions

This separation allows gestures, actions, mappings, and interaction policies (such as drag/scroll locking) to evolve independently.

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

- Some features are currently macOS-specific, especially media control, window switching, and calling.
- Dependencies are managed through `pyproject.toml` rather than a standalone requirements file.
- If a plugin fails to load, errors will be shown in the startup logs.

---

## Future Improvements

- Improve gesture robustness and reduce remaining false positives in overlapping poses
- Refine smoothing, scroll feel, and overall interaction responsiveness
- Expand cross-platform support beyond the current macOS-oriented actions
- Add calibration profiles for different users, cameras, and thresholds
- Improve observability and debugging for gesture tuning

## License

This project is licensed under the MIT License.