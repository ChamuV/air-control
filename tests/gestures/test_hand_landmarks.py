# tests/tracking/test_hand_landmarks.py

from types import SimpleNamespace

import pytest

from aircontrol.tracking.hand_landmarks import dist


def test_dist_between_two_landmark_indices():
    lms = [
        SimpleNamespace(x=0.0, y=0.0),
        SimpleNamespace(x=3.0, y=4.0),
    ]

    assert dist(lms, 0, 1) == 5.0


def test_dist_between_two_points():
    p = SimpleNamespace(x=1.0, y=1.0)
    q = SimpleNamespace(x=4.0, y=5.0)

    assert dist(p, q) == 5.0


def test_dist_invalid_arg_count_raises_type_error():
    with pytest.raises(TypeError):
        dist(1)

    with pytest.raises(TypeError):
        dist(1, 2, 3, 4)