import cv2
import numpy as np
import pytest

from wmr.roll import RollConfig, gap_row, last_digit_roll, roll_tier

PITCH = 54


def draw_digit(cell: np.ndarray, digit: int, baseline: int) -> None:
    cv2.putText(cell, str(digit), (6, baseline), cv2.FONT_HERSHEY_SIMPLEX, 1.4, 20, 3)


def draw_meter(last_offset: int) -> np.ndarray:
    image = np.full((60, 200), 230, dtype=np.uint8)
    for position in range(4):
        cell = image[:, position * 40 : (position + 1) * 40]
        draw_digit(cell, position, 47)
    last = np.full((60 + 2 * PITCH, 40), 230, dtype=np.uint8)
    for k, digit in enumerate((3, 4, 5)):
        draw_digit(last, digit, 47 + k * PITCH)
    top = PITCH + last_offset
    image[:, 160:200] = last[top : top + 60]
    return image


def test_centered_digit_scores_light():
    assert last_digit_roll(draw_meter(0)) < 1 / 3


def test_half_rolled_digit_scores_heavy():
    assert last_digit_roll(draw_meter(PITCH // 2)) > 2 / 3


def test_roll_grows_from_centered_to_half_roll():
    scores = [last_digit_roll(draw_meter(offset)) for offset in (0, PITCH // 4, PITCH // 2)]
    assert scores[0] < scores[1] < scores[2]


def test_roll_is_symmetric_in_direction():
    up = last_digit_roll(draw_meter(-PITCH // 2 + 2))
    down = last_digit_roll(draw_meter(PITCH // 2 - 2))
    assert abs(up - down) < 0.15


def test_gap_row_ignores_margin_rows():
    profile = np.ones(20)
    profile[0] = profile[19] = 0
    profile[10] = 0.5
    assert gap_row(profile, margin=3) == 10


def test_gap_row_rejects_short_profile():
    with pytest.raises(ValueError):
        gap_row(np.ones(6), margin=3)


@pytest.mark.parametrize(
    "score,tier",
    [(0.0, "light"), (0.33, "light"), (1 / 3, "medium"), (0.66, "medium"), (2 / 3, "heavy"), (1.0, "heavy")],
)
def test_roll_tier_boundaries(score, tier):
    assert roll_tier(score) == tier


def test_score_is_in_unit_interval():
    rng = np.random.default_rng(0)
    image = rng.integers(0, 256, size=(60, 200), dtype=np.uint8)
    assert 0.0 <= last_digit_roll(image, RollConfig()) <= 1.0
