from __future__ import annotations

import csv
import hashlib
import os
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

DATASET_DIR = "Word-Wheel_Water_Meter_Dataset"
SPLIT_HEADER = ["name", "source_split", "reading", "is_reversed", "is_half_word"]


@dataclass(frozen=True)
class MeterSample:
    name: str
    source_split: str
    reading: str
    is_reversed: bool
    is_half_word: bool


def default_data_root() -> Path:
    return Path(os.environ.get("WMR_DATA_ROOT", "data"))


def recognition_dir(data_root: Path, source_split: str, digit_count: int = 5) -> Path:
    return (
        Path(data_root)
        / DATASET_DIR
        / "recognition"
        / f"recognition_{digit_count}-digit"
        / source_split
    )


def label_path(data_root: Path, source_split: str, digit_count: int = 5) -> Path:
    file_name = f"{digit_count}-digit_{source_split}_rec_label_CSV.csv"
    return recognition_dir(data_root, source_split, digit_count) / file_name


def image_path(data_root: Path, sample: MeterSample) -> Path:
    digit_count = len(sample.reading)
    folder = f"{digit_count}-digit_{sample.source_split}_img"
    return recognition_dir(data_root, sample.source_split, digit_count) / folder / sample.name


def parse_label_row(row: list[str], source_split: str) -> MeterSample:
    if len(row) != 5:
        raise ValueError(f"expected 5 columns, got {len(row)}: {row}")
    name, reading, reversed_flag, half_word_flag, _six_digit_flag = row
    if not reading.isdigit():
        raise ValueError(f"reading is not numeric: {reading!r}")
    return MeterSample(
        name=name,
        source_split=source_split,
        reading=reading,
        is_reversed=reversed_flag == "1",
        is_half_word=half_word_flag == "1",
    )


def load_labels(data_root: Path, source_split: str, digit_count: int = 5) -> list[MeterSample]:
    path = label_path(data_root, source_split, digit_count)
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return [parse_label_row(row, source_split) for row in csv.reader(handle) if row]


def assign_dev_subset(name: str, val_percent: int = 20) -> str:
    digest = hashlib.sha1(name.encode("utf-8")).hexdigest()
    bucket = int(digest, 16) % 100
    return "val" if bucket < val_percent else "fit"


def write_split(path: Path, samples: list[MeterSample]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(SPLIT_HEADER)
        for sample in samples:
            writer.writerow(
                [
                    sample.name,
                    sample.source_split,
                    sample.reading,
                    int(sample.is_reversed),
                    int(sample.is_half_word),
                ]
            )


def read_split(path: Path) -> list[MeterSample]:
    with open(path, encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [
            MeterSample(
                name=row["name"],
                source_split=row["source_split"],
                reading=row["reading"],
                is_reversed=row["is_reversed"] == "1",
                is_half_word=row["is_half_word"] == "1",
            )
            for row in reader
        ]


def read_upright_gray(path: Path, is_reversed: bool) -> np.ndarray:
    if not Path(path).is_file():
        raise FileNotFoundError(f"image not found: {path}")
    data = np.fromfile(str(path), dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"cannot decode image: {path}")
    if is_reversed:
        image = cv2.rotate(image, cv2.ROTATE_180)
    return image


def load_image(data_root: Path, sample: MeterSample) -> np.ndarray:
    return read_upright_gray(image_path(data_root, sample), sample.is_reversed)
