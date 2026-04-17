# tests/plugins/detectors/test_two_finger_hold_detector.py

from types import SimpleNamespace

from aircontrol.plugins.detectors.index_middle_scroll import TwoFingerHoldDetector


def make_hand(index_tip_y: float, middle_tip_y: float):
    lms = [SimpleNamespace(x=0.5, y=0.5) for _ in range(21)]

    # Thumb sideways gate: |tip.x - ip.x| > 0.04
    lms[4] = SimpleNamespace(x=0.60, y=0.50)   # THUMB_TIP
    lms[3] = SimpleNamespace(x=0.50, y=0.50)   # THUMB_IP

    # Ring + pinky folded gate: tip.y >= mcp.y
    lms[16] = SimpleNamespace(x=0.55, y=0.70)  # RING_TIP
    lms[13] = SimpleNamespace(x=0.55, y=0.60)  # RING_MCP
    lms[20] = SimpleNamespace(x=0.58, y=0.70)  # PINKY_TIP
    lms[17] = SimpleNamespace(x=0.58, y=0.60)  # PINKY_MCP

    # Index finger (fully extended)
    lms[8] = SimpleNamespace(x=0.45, y=index_tip_y)   # INDEX_TIP
    lms[6] = SimpleNamespace(x=0.45, y=0.50)          # INDEX_PIP
    lms[5] = SimpleNamespace(x=0.45, y=0.80)          # INDEX_MCP

    # Middle finger (fully extended)
    lms[12] = SimpleNamespace(x=0.50, y=middle_tip_y)  # MIDDLE_TIP
    lms[10] = SimpleNamespace(x=0.50, y=0.50)          # MIDDLE_PIP
    lms[9] = SimpleNamespace(x=0.50, y=0.80)           # MIDDLE_MCP

    return SimpleNamespace(landmark=lms)


def test_two_finger_hold_does_not_repeat_without_new_motion():
    detector = TwoFingerHoldDetector(
        pose_confirm_frames=1,
        mode_confirm_frames=1,
        move_deadzone=0.01,
        scroll_gain=100.0,
        full_ext_thresh=0.6,
    )

    # Warm-up: establish mode + baseline.
    detector.update(make_hand(index_tip_y=0.20, middle_tip_y=0.20))
    detector.update(make_hand(index_tip_y=0.20, middle_tip_y=0.20))

    # First movement should emit one scroll step.
    first = detector.update(make_hand(index_tip_y=0.35, middle_tip_y=0.35))
    assert len(first) == 1
    assert first[0].name == "gesture.two_finger_hold"
    assert first[0].payload["direction"] == "up"
    assert first[0].payload["amount"] > 0

    # Holding at the same position should not emit again.
    second = detector.update(make_hand(index_tip_y=0.35, middle_tip_y=0.35))
    assert second == []
