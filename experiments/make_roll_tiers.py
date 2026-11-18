import argparse
import csv
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from wmr.dataset import default_data_root, load_image, read_split
from wmr.roll import TIERS, RollConfig, last_digit_roll, roll_tier

TIER_TITLES = {"light": "Nhẹ", "medium": "Trung bình", "heavy": "Nặng"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Score last-digit roll and split a set into three tiers.")
    parser.add_argument("--data-root", type=Path, default=default_data_root())
    parser.add_argument("--split", type=Path, default=Path("experiments/splits/eval.csv"))
    parser.add_argument("--out", type=Path, default=Path("experiments/roll/eval_roll.csv"))
    parser.add_argument("--figure", type=Path, default=Path("report/figures/roll-tiers.png"))
    parser.add_argument("--examples", type=int, default=6)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    config = RollConfig()
    samples = read_split(args.split)
    images = [load_image(args.data_root, sample) for sample in samples]
    scores = [last_digit_roll(image, config) for image in images]
    tiers = [roll_tier(score, config.cuts) for score in scores]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["name", "roll", "tier"])
        for sample, score, tier in zip(samples, scores, tiers):
            writer.writerow([sample.name, f"{score:.4f}", tier])

    counts = Counter(tiers)
    for tier in TIERS:
        members = [s for s, t in zip(samples, tiers) if t == tier]
        half_word = sum(s.is_half_word for s in members)
        print(f"{tier}: {counts[tier]} images, {half_word} half-word")

    rng = np.random.default_rng(args.seed)
    fig, axes = plt.subplots(len(TIERS), args.examples, figsize=(2.2 * args.examples, 1.2 * len(TIERS) + 0.6))
    for row, tier in enumerate(TIERS):
        members = [i for i, t in enumerate(tiers) if t == tier]
        picks = sorted(rng.choice(members, size=min(args.examples, len(members)), replace=False), key=lambda i: scores[i])
        for col in range(args.examples):
            ax = axes[row, col]
            ax.axis("off")
            if col < len(picks):
                index = picks[col]
                ax.imshow(images[index], cmap="gray", vmin=0, vmax=255)
                ax.set_title(f"{TIER_TITLES[tier]}, độ lăn {scores[index]:.2f}", fontsize=8)
    fig.tight_layout()
    args.figure.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.figure, dpi=150)
    print(f"wrote {args.out} and {args.figure}")


if __name__ == "__main__":
    main()
