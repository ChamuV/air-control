# src/aircontrol/cursor/mapping.py

def map_norm_to_screen(x_pt, y_pt, w, h):
    # defensive clamp
    x_pt = min(max(x_pt, 0.0), 1.0)
    y_pt = min(max(y_pt, 0.0), 1.0)

    px = int(x_pt * (w - 1))
    py = int(y_pt * (h - 1))

    return px, py