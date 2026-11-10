import cv2
import numpy as np
import pytest

from wmr.baseline import BaselineConfig, build_templates, cell_bounds, read_meter
from wmr.metrics import position_accuracy, reading_accuracy

FIT_READINGS = ["01234", "56789", "13579", "24680", "98765", "43210"]


def draw_meter(reading: str, offset: int = 0) -> np.ndarray:
    image = np.full((60, 200), 40, dtype=np.uint8)
    for position, digit in enumerate(reading):
        origin = (position * 40 + 8 + offset, 45)
        cv2.putText(image, digit, origin, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 220, 3)
    return image


def fit_templates(config: BaselineConfig) -> np.ndarray:
    return build_templates([draw_meter(r) for r in FIT_READINGS], FIT_READINGS, config)


def test_cell_bounds_split_width_evenly():
    assert [cell_bounds(200, 5, p) for p in range(5)] == [
        (0, 40),
        (40, 80),
        (80, 120),
        (120, 160),
        (160, 200),
    ]


def test_build_templates_requires_every_digit():
    with pytest.raises(ValueError):
        build_templates([draw_meter("00000")], ["00000"], BaselineConfig())


def test_read_meter_recovers_aligned_reading():
    config = BaselineConfig()
    templates = fit_templates(config)
    assert templates.shape == (10, 60, 40)
    assert read_meter(draw_meter("30718"), templates, config) == "30718"


def test_read_meter_tolerates_shift_within_search_range():
    config = BaselineConfig()
    templates = fit_templates(config)
    assert read_meter(draw_meter("52964", offset=4), templates, config) == "52964"


def test_position_and_reading_accuracy():
    truths = ["00123", "00456"]
    predictions = ["00123", "00459"]
    assert position_accuracy(truths, predictions) == [1.0, 1.0, 1.0, 1.0, 0.5]
    assert reading_accuracy(truths, predictions) == 0.5


def test_metrics_reject_mismatched_lengths():
    with pytest.raises(ValueError):
        reading_accuracy(["00123"], [])
