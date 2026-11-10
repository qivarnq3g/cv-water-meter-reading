import cv2
import numpy as np
import pytest

from wmr.dataset import (
    MeterSample,
    assign_dev_subset,
    image_path,
    parse_label_row,
    read_split,
    read_upright_gray,
    write_split,
)


def test_parse_label_row_keeps_leading_zeros_and_flags():
    sample = parse_label_row(["train7.jpg", "00412", "1", "0", "0"], "train")
    assert sample == MeterSample("train7.jpg", "train", "00412", True, False)


def test_parse_label_row_rejects_wrong_column_count():
    with pytest.raises(ValueError):
        parse_label_row(["train7.jpg", "00412", "1"], "train")


def test_parse_label_row_rejects_non_numeric_reading():
    with pytest.raises(ValueError):
        parse_label_row(["train7.jpg", "0041x", "0", "0", "0"], "train")


def test_assign_dev_subset_is_deterministic_and_roughly_proportional():
    names = [f"train{i}.jpg" for i in range(5000)]
    first = [assign_dev_subset(name) for name in names]
    second = [assign_dev_subset(name) for name in names]
    assert first == second
    assert 0.17 < first.count("val") / len(names) < 0.23


def test_split_round_trip(tmp_path):
    samples = [
        MeterSample("a.jpg", "train", "00010", False, True),
        MeterSample("b.jpg", "test", "99999", True, False),
    ]
    path = tmp_path / "splits" / "x.csv"
    write_split(path, samples)
    assert read_split(path) == samples


def test_image_path_follows_dataset_layout(tmp_path):
    sample = MeterSample("test3.jpg", "test", "00123", False, False)
    expected = (
        tmp_path
        / "Word-Wheel_Water_Meter_Dataset"
        / "recognition"
        / "recognition_5-digit"
        / "test"
        / "5-digit_test_img"
        / "test3.jpg"
    )
    assert image_path(tmp_path, sample) == expected


def test_read_upright_gray_rotates_reversed_images(tmp_path):
    image = np.zeros((6, 10), dtype=np.uint8)
    image[0, 0] = 255
    path = tmp_path / "meter.png"
    cv2.imwrite(str(path), image)
    assert read_upright_gray(path, False)[0, 0] == 255
    rotated = read_upright_gray(path, True)
    assert rotated[5, 9] == 255
    assert rotated[0, 0] == 0


def test_read_upright_gray_reports_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_upright_gray(tmp_path / "missing.jpg", False)
