import argparse
import csv
from pathlib import Path

from wmr.baseline import BaselineConfig, build_templates, read_meter
from wmr.dataset import default_data_root, load_image, read_split
from wmr.metrics import position_accuracy, reading_accuracy


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fit the template-matching baseline on dev_fit and score it on a split."
    )
    parser.add_argument("--data-root", type=Path, default=default_data_root())
    parser.add_argument("--splits-dir", type=Path, default=Path("experiments/splits"))
    parser.add_argument("--split", default="eval", choices=["dev_val", "eval"])
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    config = BaselineConfig()
    fit_samples = [s for s in read_split(args.splits_dir / "dev_fit.csv") if not s.is_half_word]
    templates = build_templates(
        [load_image(args.data_root, sample) for sample in fit_samples],
        [sample.reading for sample in fit_samples],
        config,
    )

    samples = read_split(args.splits_dir / f"{args.split}.csv")
    predictions = [
        read_meter(load_image(args.data_root, sample), templates, config) for sample in samples
    ]

    groups = {
        "all": [True] * len(samples),
        "not half-word": [not sample.is_half_word for sample in samples],
        "half-word": [sample.is_half_word for sample in samples],
    }
    columns = ["d1", "d2", "d3", "d4", "d5", "full"]
    print(f"templates from {len(fit_samples)} dev_fit images, scored on {args.split}")
    print(f"{'group':<14}{'n':>6}" + "".join(f"{column:>7}" for column in columns))
    for group, mask in groups.items():
        truths = [s.reading for s, keep in zip(samples, mask) if keep]
        chosen = [p for p, keep in zip(predictions, mask) if keep]
        values = position_accuracy(truths, chosen) + [reading_accuracy(truths, chosen)]
        print(f"{group:<14}{len(truths):>6}" + "".join(f"{value:>7.3f}" for value in values))

    output = args.output or Path("outputs") / f"baseline_{args.split}.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["name", "reading", "prediction", "is_reversed", "is_half_word"])
        for sample, prediction in zip(samples, predictions):
            writer.writerow(
                [
                    sample.name,
                    sample.reading,
                    prediction,
                    int(sample.is_reversed),
                    int(sample.is_half_word),
                ]
            )
    print(f"predictions written to {output}")


if __name__ == "__main__":
    main()
