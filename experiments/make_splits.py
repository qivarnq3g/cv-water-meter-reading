import argparse
from pathlib import Path

from wmr.dataset import assign_dev_subset, default_data_root, load_labels, write_split


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Write the development (fit, val) and evaluation sample lists."
    )
    parser.add_argument("--data-root", type=Path, default=default_data_root())
    parser.add_argument("--output-dir", type=Path, default=Path("experiments/splits"))
    args = parser.parse_args()

    development = load_labels(args.data_root, "train")
    evaluation = load_labels(args.data_root, "test")
    subsets = {
        "dev_fit": [s for s in development if assign_dev_subset(s.name) == "fit"],
        "dev_val": [s for s in development if assign_dev_subset(s.name) == "val"],
        "eval": evaluation,
    }
    for name, samples in subsets.items():
        write_split(args.output_dir / f"{name}.csv", samples)
        half_word = sum(sample.is_half_word for sample in samples)
        print(f"{name}: {len(samples)} images, {half_word} half-word")


if __name__ == "__main__":
    main()
