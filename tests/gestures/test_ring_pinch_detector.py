# tests/plugins/detectors/test_ring_pinch_detector.py

from types import SimpleNamespace

from aircontrol.plugins.detectors.ring_pinch import RingPinchDetector


def make_hand(thumb=(0.5, 0.5), ring=(0.8, 0.8)):
    lms = [SimpleNamespace(x=0.0, y=0.0) for _ in range(21)]
    lms[4] = SimpleNamespace(x=thumb[0], y=thumb[1])   # THUMB_TIP
    lms[16] = SimpleNamespace(x=ring[0], y=ring[1])    # RING_TIP
    return SimpleNamespace(landmark=lms)


def test_ring_pinch_emits_start_then_move_then_end():
    detector = RingPinchDetector(pinch_threshold=0.05)

    start_and_move = detector.update(make_hand(thumb=(0.5, 0.5), ring=(0.53, 0.5)))
    move_only = detector.update(make_hand(thumb=(0.5, 0.5), ring=(0.53, 0.5)))
    end_only = detector.update(make_hand(thumb=(0.5, 0.5), ring=(0.8, 0.8)))

    assert [e.name for e in start_and_move] == [
        "gesture.ring_pinch.start",
        "gesture.ring_pinch.move",
    ]
    assert [e.name for e in move_only] == ["gesture.ring_pinch.move"]
    assert [e.name for e in end_only] == ["gesture.ring_pinch.end"]


def test_ring_pinch_emits_end_when_hand_disappears_while_pinching():
    detector = RingPinchDetector(pinch_threshold=0.05)

    detector.update(make_hand(thumb=(0.5, 0.5), ring=(0.53, 0.5)))  # enter pinch
    events = detector.update(None)

    assert [e.name for e in events] == ["gesture.ring_pinch.end"]
