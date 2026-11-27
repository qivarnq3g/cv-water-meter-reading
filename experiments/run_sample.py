import argparse
import csv
import json
from pathlib import Path

import numpy as np

from wmr.baseline import BaselineConfig, read_meter
from wmr.dataset import read_split, read_upright_gray
from wmr.proposed import WheelConfig, WheelReader
from wmr.roll import last_digit_roll, roll_tier


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Read the sample meters with the baseline and the proposed wheel reader using the saved templates and configuration."
    )
    parser.add_argument("--sample-dir", type=Path, default=Path("data/sample"))
    parser.add_argument("--results-dir", type=Path, default=Path("experiments/phuc/results"))
    parser.add_argument("--output", type=Path, default=Path("outputs/sample_predictions.csv"))
    args = parser.parse_args()

    templates = np.load(args.results_dir / "templates.npy")
    selected = json.loads((args.results_dir / "selected.json").read_text(encoding="utf-8"))
    reader = WheelReader(templates, WheelConfig(**selected["config"]))

    rows = []
    for sample in read_split(args.sample_dir / "recognition_labels.csv"):
        image = read_upright_gray(args.sample_dir / sample.name, sample.is_reversed)
        roll = last_digit_roll(image)
        rows.append(
            {
                "name": sample.name,
                "reading": sample.reading,
                "roll": round(roll, 3),
                "tier": roll_tier(roll),
                "baseline": read_meter(image, templates, BaselineConfig()),
                "proposed": reader.read(image),
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    print(f"{'name':<10} {'reading':<8} {'roll':>6} {'tier':<7} {'baseline':<9} {'proposed':<9}")
    for row in rows:
        print(
            f"{row['name']:<10} {row['reading']:<8} {row['roll']:>6.3f} {row['tier']:<7} "
            f"{row['baseline']:<9} {row['proposed']:<9}"
        )
    print(f"Saved {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
