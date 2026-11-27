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


def stacked_cells():
    rng = np.random.default_rng(5)
    return [rng.uniform(0, 255, (60, 40)).astype(np.float32) for _ in range(3)]


def test_rolled_window_at_native_period_matches_cells():
    from wmr.roll import rolled_window
    above, middle, below = stacked_cells()
    np.testing.assert_array_equal(rolled_window([above, middle, below], 60, 0.0), middle)
    half = rolled_window([above, middle, below], 60, 0.5)
    np.testing.assert_array_equal(half[:30], middle[30:])
    np.testing.assert_array_equal(half[30:], below[:30])


def test_rolled_window_centres_resized_digit():
    from wmr.roll import rolled_window
    cells = stacked_cells()
    stack = cv2.resize(np.vstack(cells), (40, 216), interpolation=cv2.INTER_LINEAR)
    np.testing.assert_array_equal(rolled_window(cells, 72, 0.0), stack[78:138])
    np.testing.assert_array_equal(rolled_window(cells, 72, 0.25), stack[96:156])


def test_rolled_window_rejects_window_outside_stack():
    from wmr.roll import rolled_window
    with pytest.raises(ValueError):
        rolled_window(stacked_cells(), 20, 0.5)
