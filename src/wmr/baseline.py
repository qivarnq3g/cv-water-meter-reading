from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class BaselineConfig:
    digit_count: int = 5
    max_shift: int = 6
    template_positions: tuple[int, ...] = (0, 1, 2, 3)


def preprocess(gray: np.ndarray) -> np.ndarray:
    return cv2.equalizeHist(gray)


def cell_bounds(width: int, digit_count: int, position: int) -> tuple[int, int]:
    cell_width = width // digit_count
    start = position * cell_width
    return start, start + cell_width


def extract_cell(image: np.ndarray, digit_count: int, position: int) -> np.ndarray:
    start, end = cell_bounds(image.shape[1], digit_count, position)
    return image[:, start:end]


def build_templates(
    images: list[np.ndarray], readings: list[str], config: BaselineConfig
) -> np.ndarray:
    sums = None
    counts = np.zeros(10, dtype=np.int64)
    for image, reading in zip(images, readings):
        prepared = preprocess(image).astype(np.float32)
        for position in config.template_positions:
            cell = extract_cell(prepared, config.digit_count, position)
            if sums is None:
                sums = np.zeros((10, *cell.shape), dtype=np.float64)
            digit = int(reading[position])
            sums[digit] += cell
            counts[digit] += 1
    if sums is None or np.any(counts == 0):
        missing = [digit for digit in range(10) if counts[digit] == 0]
        raise ValueError(f"no template samples for digits: {missing}")
    return (sums / counts[:, None, None]).astype(np.float32)


def match_scores(
    prepared: np.ndarray, templates: np.ndarray, position: int, config: BaselineConfig
) -> np.ndarray:
    shift = config.max_shift
    padded = cv2.copyMakeBorder(prepared, shift, shift, shift, shift, cv2.BORDER_REPLICATE)
    start, end = cell_bounds(prepared.shape[1], config.digit_count, position)
    region = padded[:, start : end + 2 * shift].astype(np.float32)
    scores = np.empty(len(templates), dtype=np.float32)
    for digit, template in enumerate(templates):
        response = cv2.matchTemplate(region, template, cv2.TM_CCOEFF_NORMED)
        scores[digit] = response.max()
    return scores


def read_meter(image: np.ndarray, templates: np.ndarray, config: BaselineConfig) -> str:
    prepared = preprocess(image)
    digits = []
    for position in range(config.digit_count):
        scores = match_scores(prepared, templates, position, config)
        digits.append(str(int(np.argmax(scores))))
    return "".join(digits)
