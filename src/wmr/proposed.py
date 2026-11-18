"""Periodic wheel NCC; only the last digit differs from the baseline."""
from dataclasses import dataclass
import cv2
import numpy as np
from .baseline import BaselineConfig, extract_cell, preprocess, read_meter

@dataclass(frozen=True)
class WheelConfig:
    pitch: int = 58
    threshold: float = 0.5
    max_shift: int = 6
    enabled: bool = True
    continuous: bool = True
    def __post_init__(self):
        if self.pitch < 2 or self.max_shift < 0 or not 0 < self.threshold <= 1:
            raise ValueError("invalid wheel configuration")

def wheel_windows(templates, config=WheelConfig()):
    """Phase zero is the centered digit; next digit enters from below.

    Resize each full cell to the pitch, then sample periodic windows. The
    center offset aligns digit centers even when pitch differs from cell height.
    """
    height, width = templates.shape[1:]
    strip = np.concatenate([cv2.resize(t, (width, config.pitch)) for t in templates])
    offset = (config.pitch - height) // 2
    return np.stack([strip[(np.arange(height) + y + offset) % len(strip)]
                     for y in range(len(strip))]).astype(np.float32)

class WheelReader:
    def __init__(self, templates, config=WheelConfig()):
        self.templates, self.config = templates, config
        self.windows = wheel_windows(templates, config)
        self.indices = np.arange(len(self.windows))
        if not config.continuous:
            distance = np.abs((self.indices + config.pitch // 2) % config.pitch - config.pitch // 2)
            self.indices = self.indices[distance <= config.max_shift]
            self.windows = self.windows[self.indices]
        centered = self.windows - self.windows.mean(axis=(1, 2), keepdims=True)
        self.bank = centered.reshape(len(centered), -1)
        self.norms = np.linalg.norm(self.bank, axis=1)

    def phase(self, image):
        cell = extract_cell(preprocess(image), 5, 4).astype(np.float32)
        s = self.config.max_shift
        padded = cv2.copyMakeBorder(cell, 0, 0, s, s, cv2.BORDER_REPLICATE)
        patches = np.stack([padded[:, x:x+cell.shape[1]].ravel() for x in range(2*s+1)])
        patches -= patches.mean(axis=1, keepdims=True)
        denom = self.norms[:, None] * np.linalg.norm(patches, axis=1)[None, :]
        scores = np.divide(self.bank @ patches.T, denom,
                           out=np.full(denom.shape, -1, np.float32), where=denom > 1e-8)
        index, horizontal = np.unravel_index(np.argmax(scores), scores.shape)
        return float(self.indices[index] / self.config.pitch), float(scores[index, horizontal])

    def read(self, image):
        base = read_meter(image, self.templates, BaselineConfig(max_shift=self.config.max_shift))
        if not self.config.enabled:
            return base
        phase, _ = self.phase(image)
        digit = int(np.floor(phase + 1 - self.config.threshold)) % 10
        return base[:4] + str(digit)
