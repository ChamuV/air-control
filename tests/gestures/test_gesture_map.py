# tests/gestures/test_middle_pinch.py

from types import SimpleNamespace

from aircontrol.plugins.detectors.middle_pinch import MiddlePinchDetector


def make_landmarks(
    thumb=(0.50, 0.50),
    index=(0.80, 0.50),
    middle=(0.53, 0.50),
    ring=(0.80, 0.70),
    pinky=(0.80, 0.90),
):
    lms = [SimpleNamespace(x=0.0, y=0.0) for _ in range(21)]

    # Landmark indices used by the detector
    THUMB_TIP = 4
    INDEX_TIP = 8
    MIDDLE_TIP = 12
    RING_TIP = 16
    PINKY_TIP = 20

    lms[THUMB_TIP] = SimpleNamespace(x=thumb[0], y=thumb[1])
    lms[INDEX_TIP] = SimpleNamespace(x=index[0], y=index[1])
    lms[MIDDLE_TIP] = SimpleNamespace(x=middle[0], y=middle[1])
    lms[RING_TIP] = SimpleNamespace(x=ring[0], y=ring[1])
    lms[PINKY_TIP] = SimpleNamespace(x=pinky[0], y=pinky[1])

    return SimpleNamespace(landmark=lms)


def test_middle_pinch_emits_gesture_when_thumb_and_middle_are_close():
    detector = MiddlePinchDetector(
        pinch_threshold=0.05,
        other_finger_min_dist=0.06,
        cooldown_frames=8,
    )

    hand_landmarks = make_landmarks(
        thumb=(0.50, 0.50),
        middle=(0.53, 0.50),  # close to thumb
        index=(0.80, 0.50),
        ring=(0.80, 0.70),
        pinky=(0.80, 0.90),
    )

    events = detector.update(hand_landmarks)

    assert len(events) == 1
    assert events[0].name == "gesture.middle_pinch"
    assert "d_tm" in events[0].payload


def test_middle_pinch_does_not_emit_when_index_is_also_close():
    detector = MiddlePinchDetector(
        pinch_threshold=0.05,
        other_finger_min_dist=0.06,
        cooldown_frames=8,
    )

    hand_landmarks = make_landmarks(
        thumb=(0.50, 0.50),
        middle=(0.53, 0.50),  # close to thumb
        index=(0.54, 0.50),   # also close, should block gesture
        ring=(0.80, 0.70),
        pinky=(0.80, 0.90),
    )

    events = detector.update(hand_landmarks)

    assert events == []


def test_middle_pinch_respects_cooldown():
    detector = MiddlePinchDetector(
        pinch_threshold=0.05,
        other_finger_min_dist=0.06,
        cooldown_frames=2,
    )

    hand_landmarks = make_landmarks(
        thumb=(0.50, 0.50),
        middle=(0.53, 0.50),
        index=(0.80, 0.50),
        ring=(0.80, 0.70),
        pinky=(0.80, 0.90),
    )

    first = detector.update(hand_landmarks)
    second = detector.update(hand_landmarks)
    third = detector.update(hand_landmarks)
    fourth = detector.update(hand_landmarks)

    assert len(first) == 1
    assert second == []
    assert third == []
    assert len(fourth) == 1


def test_middle_pinch_returns_empty_for_missing_hand():
    detector = MiddlePinchDetector()

    events = detector.update(None)

    assert events == []