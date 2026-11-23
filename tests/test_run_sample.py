import csv
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_run_sample_reads_every_sample_with_both_methods(tmp_path):
    output = tmp_path / "sample_predictions.csv"
    result = subprocess.run(
        [sys.executable, "experiments/run_sample.py", "--output", str(output)],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
        capture_output=True,
        text=True,
        check=True,
    )
    rows = list(csv.DictReader(output.open(encoding="utf-8")))
    labels = list(csv.DictReader((ROOT / "data/sample/recognition_labels.csv").open(encoding="utf-8")))
    assert [row["name"] for row in rows] == [label["name"] for label in labels]
    for row in rows:
        assert row["tier"] in {"light", "medium", "heavy"}
        assert len(row["baseline"]) == 5 and row["baseline"].isdigit()
        assert len(row["proposed"]) == 5 and row["proposed"].isdigit()
        assert row["proposed"][:4] == row["baseline"][:4]
    assert "test5.jpg" in result.stdout


def test_run_sample_matches_saved_eval_predictions(tmp_path):
    output = tmp_path / "sample_predictions.csv"
    subprocess.run(
        [sys.executable, "experiments/run_sample.py", "--output", str(output)],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
        check=True,
    )
    saved = {
        (row["name"], row["method"]): row["prediction"]
        for row in csv.DictReader((ROOT / "experiments/phuc/results/predictions.csv").open(encoding="utf-8"))
    }
    for row in csv.DictReader(output.open(encoding="utf-8")):
        assert row["baseline"] == saved[(row["name"], "baseline")]
        assert row["proposed"] == saved[(row["name"], "proposed")]
