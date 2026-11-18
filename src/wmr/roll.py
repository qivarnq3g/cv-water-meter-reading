from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np
from scipy.ndimage import gaussian_filter1d

TIERS = ("light", "medium", "heavy")


@dataclass(frozen=True)
class RollConfig:
    digit_count: int = 5
    column_span: tuple[float, float] = (0.1, 0.9)
    block_size: int = 15
    threshold_offset: int = 8
    sigma: float = 1.5
    margin: int = 5
    cuts: tuple[float, float] = (1 / 3, 2 / 3)


def ink_mask(gray: np.ndarray, config: RollConfig = RollConfig()) -> np.ndarray:
    equalized = cv2.equalizeHist(gray)
    return cv2.adaptiveThreshold(
        equalized,
        1,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV,
        config.block_size,
        config.threshold_offset,
    )


def ink_profile(gray: np.ndarray, config: RollConfig = RollConfig()) -> np.ndarray:
    mask = ink_mask(gray, config)
    cell_width = mask.shape[1] // config.digit_count
    start = (config.digit_count - 1) * cell_width
    lo, hi = config.column_span
    cell = mask[:, start + int(lo * cell_width) : start + int(hi * cell_width)]
    return gaussian_filter1d(cell.mean(axis=1).astype(np.float64), config.sigma)


def gap_row(profile: np.ndarray, margin: int) -> int:
    height = len(profile)
    if height <= 2 * margin:
        raise ValueError("image is too short for the margin")
    return margin + int(np.argmin(profile[margin : height - margin]))


def last_digit_roll(gray: np.ndarray, config: RollConfig = RollConfig()) -> float:
    profile = ink_profile(gray, config)
    row = gap_row(profile, config.margin)
    height = len(profile)
    return min(row, height - 1 - row) / ((height - 1) / 2)


def roll_tier(score: float, cuts: tuple[float, float] = RollConfig.cuts) -> str:
    if score < cuts[0]:
        return TIERS[0]
    if score < cuts[1]:
        return TIERS[1]
    return TIERS[2]
