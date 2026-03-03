aircontrol/
  gestures/        # core framework: engine, dispatcher, events, plugin_base
  plugins/         # actual gesture implementations: pinch, cursor_move, volume_swipe
  actions/         # mouse, volume, window controllers
  cursor/          # cursor modes + smoothing + mapping
  tracking/        # mediapipe tracker

  aircontrol/
  cursor/            # capability: how cursor position is computed
    controller.py
    palm_mode.py
    index_mode.py
    mapping.py
    smoothing.py

  actions/           # capability: how actions are executed (mouse/volume/window)
    mouse_control.py
    volume_control.py
    window_control.py

  gestures/          # framework: how detectors+events+actions connect
    events.py
    dispatcher.py
    engine.py
    plugin_base.py
    loader.py

  plugins/           # features: detectors + action mappings
    cursor_move_plugin.py
    pinch_click_plugin.py
    volume_plugin.py
    window_swipe_plugin.py