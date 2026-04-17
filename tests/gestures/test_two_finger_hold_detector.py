# tests/plugins/detectors/test_two_finger_hold_detector.py

from types import SimpleNamespace

from aircontrol.plugins.detectors.index_middle_scroll import IndexMiddleScrollDetector


def make_hand(index_tip_y: float, middle_tip_y: float, pinched: bool = True):
    lms = [SimpleNamespace(x=0.5, y=0.5) for _ in range(21)]

    # Index + middle pinch gesture:
    # keep tips close together when pinched
    if pinched:
        lms[8] = SimpleNamespace(x=0.500, y=index_tip_y)   # INDEX_TIP
        lms[12] = SimpleNamespace(x=0.515, y=middle_tip_y) # MIDDLE_TIP
    else:
        lms[8] = SimpleNamespace(x=0.45, y=index_tip_y)
        lms[12] = SimpleNamespace(x=0.60, y=middle_tip_y)

    return SimpleNamespace(landmark=lms)


def test_index_middle_scroll_does_not_repeat_without_new_motion():
    detector = IndexMiddleScrollDetector(
        pinch_threshold=0.05,
        hold_frames=2,
        move_deadzone=0.01,
        scroll_gain=100.0,
    )

    # Frame 1: pinch begins, no event yet.
    first = detector.update(make_hand(index_tip_y=0.30, middle_tip_y=0.30, pinched=True))
    assert first == []

    # Frame 2: hold long enough to enter scroll mode.
    second = detector.update(make_hand(index_tip_y=0.30, middle_tip_y=0.30, pinched=True))
    assert len(second) == 1
    assert second[0].name == "gesture.index_middle_scroll.start"

    # Move upward a bit: should emit one scroll move event.
    third = detector.update(make_hand(index_tip_y=0.20, middle_tip_y=0.20, pinched=True))
    assert len(third) == 1
    assert third[0].name == "gesture.index_middle_scroll.move"
    assert third[0].payload["direction"] == "up"
    assert third[0].payload["amount"] > 0

    # Holding at the same position should not emit again.
    fourth = detector.update(make_hand(index_tip_y=0.20, middle_tip_y=0.20, pinched=True))
    assert fourth == []


def test_index_middle_scroll_emits_end_on_release():
    detector = IndexMiddleScrollDetector(
        pinch_threshold=0.05,
        hold_frames=2,
        move_deadzone=0.01,
        scroll_gain=100.0,
    )

    detector.update(make_hand(index_tip_y=0.30, middle_tip_y=0.30, pinched=True))
    detector.update(make_hand(index_tip_y=0.30, middle_tip_y=0.30, pinched=True))

    end_events = detector.update(make_hand(index_tip_y=0.30, middle_tip_y=0.30, pinched=False))
    assert len(end_events) == 1
    assert end_events[0].name == "gesture.index_middle_scroll.end"