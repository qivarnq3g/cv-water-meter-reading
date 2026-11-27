import argparse
import csv
import json
import math
import os
from collections import defaultdict
from pathlib import Path

import cv2
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter
from scipy.stats import binomtest

from wmr.baseline import extract_cell, preprocess
from wmr.dataset import load_image, read_split
from wmr.proposed import WheelConfig, WheelReader, wheel_windows

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "report" / "figures"
TIERS = ["light", "medium", "heavy"]
TIER_NAMES = {"light": "Nhẹ", "medium": "Trung bình", "heavy": "Nặng", "all": "Toàn tập"}
METHOD_NAMES = {
    "baseline": "Baseline",
    "discrete_phase": "Bỏ pha giữa hai chữ số",
    "proposed": "Dải tuần hoàn",
}
COLORS = {"baseline": "#6b7b85", "discrete_phase": "#c47f4a", "proposed": "#0b6e63"}

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
    }
)


def comma(value, digits=2):
    return f"{value:.{digits}f}".replace(".", ",")


def percent_axis(axis):
    axis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}"))


def wilson(hits, n, z=1.96):
    p = hits / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centre - half, centre + half


def load_predictions(path):
    table = defaultdict(dict)
    with open(path, encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            table[row["method"]][row["name"]] = row
    return table


def last_correct(row):
    return row["reading"][-1] == row["prediction"][-1]


def adjacent(row):
    truth, guess = int(row["reading"][-1]), int(row["prediction"][-1])
    return (guess - truth) % 10 in (1, 9)


def tier_stats(predictions):
    names = list(predictions["baseline"])
    groups = {"all": names}
    for tier in TIERS:
        groups[tier] = [n for n in names if predictions["baseline"][n]["tier"] == tier]
    stats = {}
    for group, members in groups.items():
        entry = {"n": len(members)}
        for method, rows in predictions.items():
            hits = sum(last_correct(rows[n]) for n in members)
            errors = [rows[n] for n in members if not last_correct(rows[n])]
            low, high = wilson(hits, len(members))
            entry[method] = {
                "hits": hits,
                "accuracy": hits / len(members),
                "ci95": [low, high],
                "full": sum(rows[n]["reading"] == rows[n]["prediction"] for n in members) / len(members),
                "errors": len(errors),
                "adjacent_errors": sum(adjacent(r) for r in errors),
            }
        base, prop = predictions["baseline"], predictions["proposed"]
        wins = sum(last_correct(prop[n]) and not last_correct(base[n]) for n in members)
        losses = sum(last_correct(base[n]) and not last_correct(prop[n]) for n in members)
        n = len(members)
        diff = (wins - losses) / n
        se = math.sqrt(wins + losses - (wins - losses) ** 2 / n) / n
        entry["paired"] = {
            "wins": wins,
            "losses": losses,
            "difference": diff,
            "ci95": [diff - 1.96 * se, diff + 1.96 * se],
            "mcnemar_p": binomtest(wins, wins + losses, 0.5).pvalue,
        }
        stats[group] = entry
    return stats


def figure_tiers(data_root, out):
    rows = {}
    with open(ROOT / "experiments" / "roll" / "eval_roll.csv", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            rows[row["name"]] = row
    samples = {s.name: s for s in read_split(ROOT / "experiments" / "splits" / "eval.csv")}
    rng = np.random.default_rng(0)
    fig, axes = plt.subplots(3, 5, figsize=(12, 3.6))
    for r, tier in enumerate(TIERS):
        names = sorted(n for n, row in rows.items() if row["tier"] == tier)
        chosen = sorted(rng.choice(names, 5, replace=False), key=lambda n: float(rows[n]["roll"]))
        for c, name in enumerate(chosen):
            ax = axes[r, c]
            ax.imshow(load_image(data_root, samples[name]), cmap="gray", vmin=0, vmax=255)
            ax.set_title(f"{TIER_NAMES[tier]}, R = {comma(float(rows[name]['roll']))}", fontsize=10)
            ax.axis("off")
    fig.savefig(out)
    plt.close(fig)


def figure_e1_e3(stats, out):
    methods = ["baseline", "discrete_phase", "proposed"]
    groups = ["all"] + TIERS
    x = np.arange(len(groups))
    width = 0.26
    fig, ax = plt.subplots(figsize=(9, 4.2))
    for i, method in enumerate(methods):
        acc = np.array([stats[g][method]["accuracy"] * 100 for g in groups])
        low = np.array([stats[g][method]["ci95"][0] * 100 for g in groups])
        high = np.array([stats[g][method]["ci95"][1] * 100 for g in groups])
        pos = x + (i - 1) * width
        ax.bar(pos, acc, width, color=COLORS[method], label=METHOD_NAMES[method])
        ax.errorbar(pos, acc, yerr=[acc - low, high - acc], fmt="none", ecolor="#222", capsize=3, lw=1)
        for p, a, h in zip(pos, acc, high):
            ax.text(p, h + 1.2, comma(a), ha="center", va="bottom", fontsize=7.5)
    ax.set_xticks(x, [f"{TIER_NAMES[g]}\n(n = {stats[g]['n']:,})".replace(",", ".") for g in groups])
    ax.set_ylabel("Độ chính xác chữ số cuối (%)")
    ax.set_ylim(0, 80)
    percent_axis(ax.yaxis)
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.16))
    fig.savefig(out)
    plt.close(fig)


def figure_e2(path, out):
    grid = defaultdict(dict)
    with open(path, encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            grid[row["threshold"]][(int(row["pitch"]), int(row["max_shift"]))] = float(row["last_accuracy"]) * 100
    pitches, shifts = [54, 58, 62], [2, 6, 10]
    thresholds = sorted(grid)
    values = [np.array([[grid[t][(p, s)] for s in shifts] for p in pitches]) for t in thresholds]
    vmin, vmax = min(v.min() for v in values), max(v.max() for v in values)
    best = max(((t, p, s) for t in thresholds for p in pitches for s in shifts), key=lambda k: grid[k[0]][(k[1], k[2])])
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.4), sharey=True)
    for ax, t, v in zip(axes, thresholds, values):
        image = ax.imshow(v, cmap="Greens", vmin=vmin, vmax=vmax)
        for i, p in enumerate(pitches):
            for j, s in enumerate(shifts):
                dark = v[i, j] > (vmin + vmax) / 2
                ax.text(j, i, comma(v[i, j]), ha="center", va="center", fontsize=10, color="white" if dark else "#111")
                if (t, p, s) == best:
                    ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, ec="#c0392b", lw=2.5))
        ax.set_xticks(range(3), shifts)
        ax.set_yticks(range(3), pitches)
        ax.set_title(f"Ngưỡng t = {t.replace('.', ',')}")
    axes[0].set_ylabel("Bước bánh xe p (điểm ảnh)")
    axes[1].set_xlabel("Bán kính dịch ngang (điểm ảnh)")
    cbar = fig.colorbar(image, ax=axes, shrink=0.85, pad=0.02)
    cbar.set_label("Chữ số cuối đúng trên dev_val (%)")
    fig.savefig(out)
    plt.close(fig)


def figure_e4(path, out):
    with open(path, encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    phi = np.array([float(r["phi"]) for r in rows])
    series = [
        ("proposed_reads_lower_or_next", "Dải tuần hoàn", COLORS["proposed"], "o", "-"),
        ("baseline_s2_reads_lower_or_next", "Baseline, dịch ±2", "#9aa7b0", "s", "--"),
        ("baseline_s6_reads_lower_or_next", "Baseline, dịch ±6", COLORS["baseline"], "s", "--"),
        ("baseline_s10_reads_lower_or_next", "Baseline, dịch ±10", "#2f3b43", "s", "--"),
    ]
    fig, (left, right) = plt.subplots(1, 2, figsize=(11, 4.0))
    for key, label, color, marker, style in series:
        left.plot(phi, [float(r[key]) * 100 for r in rows], style, marker=marker, color=color, label=label, lw=2, ms=5)
    left.axhline(50, color="#c0392b", lw=1, ls=":")
    left.text(0.505, 51, "50%", color="#c0392b", fontsize=9, ha="right")
    left.set_xlabel("Pha lăn tổng hợp φ (phần chiều cao ô)")
    left.set_ylabel("Đọc ra d hoặc d + 1 (%)")
    left.set_ylim(0, 80)
    percent_axis(left.yaxis)
    left.xaxis.set_major_formatter(FuncFormatter(lambda v, _: comma(v, 1)))
    left.legend(frameon=False, fontsize=9.5, loc="lower left")
    left.set_title("(a) Tỉ lệ đọc đúng một trong hai chữ số")
    right.plot(phi, [float(r["proposed_phase_median"]) for r in rows], "-o", color=COLORS["proposed"], lw=2, ms=5)
    right.set_xlabel("Pha lăn tổng hợp φ (phần chiều cao ô)")
    right.set_ylabel("Trung vị sai số pha (chữ số)")
    right.xaxis.set_major_formatter(FuncFormatter(lambda v, _: comma(v, 1)))
    right.yaxis.set_major_formatter(FuncFormatter(lambda v, _: comma(v, 1)))
    right.set_title("(b) Sai số định vị pha của dải tuần hoàn")
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def figure_strip(data_root, out):
    results = ROOT / "experiments" / "phuc" / "results"
    templates = np.load(results / "templates.npy")
    selected = json.loads((results / "selected.json").read_text(encoding="utf-8"))["config"]
    config = WheelConfig(pitch=selected["pitch"], threshold=selected["threshold"], max_shift=selected["max_shift"])
    windows = wheel_windows(templates, config)
    p = config.pitch
    strip = np.concatenate([cv2.resize(t, (templates.shape[2], p)) for t in templates])
    sample = next(s for s in read_split(ROOT / "experiments" / "splits" / "eval.csv") if s.name == "test1656.jpg")
    image = load_image(data_root, sample)
    cell = extract_cell(preprocess(image), 5, 4)
    phase, score = WheelReader(templates, config).phase(image)
    best = windows[int(round(phase * p)) % len(windows)]
    fig = plt.figure(figsize=(12, 4.2))
    grid = fig.add_gridspec(1, 6, width_ratios=[1.0, 0.25, 1, 1, 1, 2.0], wspace=0.35)
    ax = fig.add_subplot(grid[0])
    lo, hi = 0, 3 * p
    ax.imshow(strip[lo:hi], cmap="gray", aspect="equal")
    for k, f in enumerate([0.0, 0.25, 0.5]):
        y = 1 * p + f * p - lo
        ax.add_patch(Rectangle((-0.5, y - 0.5), strip.shape[1], templates.shape[1], fill=False, ec=["#0b6e63", "#c47f4a", "#c0392b"][k], lw=2))
    ax.set_yticks([0, p, 2 * p], ["0", "p", "2p"])
    ax.set_xticks([])
    ax.set_title("(a) Đoạn dải 0, 1, 2", fontsize=10)
    for k, f in enumerate([0.0, 0.25, 0.5]):
        a = fig.add_subplot(grid[2 + k])
        a.imshow(windows[int(round((1 + f) * p))], cmap="gray")
        a.set_title(f"r = {comma(1 + f)}", fontsize=10, color=["#0b6e63", "#c47f4a", "#c0392b"][k])
        a.axis("off")
    pair = fig.add_subplot(grid[5])
    pair.imshow(np.hstack([cell.astype(np.float32), np.full((cell.shape[0], 6), 255, np.float32), best]), cmap="gray")
    pair.set_title(f"(b) Ô cuối test1656.jpg (trái)\nvà cửa sổ khớp nhất (phải)\nr = {comma(phase)}, NCC = {comma(score)}", fontsize=10)
    pair.axis("off")
    fig.savefig(out)
    plt.close(fig)
    return {"phase": phase, "score": score}


def main():
    parser = argparse.ArgumentParser(description="Build report figures and statistics from saved experiment results.")
    parser.add_argument("--data-root", default=os.environ.get("WMR_DATA_ROOT", "data"))
    args = parser.parse_args()
    data_root = Path(args.data_root)
    FIGURES.mkdir(parents=True, exist_ok=True)
    predictions = load_predictions(ROOT / "experiments" / "quang" / "results" / "e3_predictions.csv")
    stats = tier_stats(predictions)
    figure_tiers(data_root, FIGURES / "fig-tiers.png")
    figure_e1_e3(stats, FIGURES / "fig-e1-e3.png")
    figure_e2(ROOT / "experiments" / "phuc" / "results" / "e2_grid.csv", FIGURES / "fig-e2.png")
    figure_e4(ROOT / "experiments" / "quang" / "results" / "e4_curve.csv", FIGURES / "fig-e4.png")
    stats["strip_example"] = figure_strip(data_root, FIGURES / "fig-strip.png")
    (ROOT / "report" / "stats.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({g: {m: round(v["accuracy"] * 100, 2) for m, v in e.items() if isinstance(v, dict) and "accuracy" in v} | {"paired": e["paired"]} for g, e in stats.items() if g != "strip_example"}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
