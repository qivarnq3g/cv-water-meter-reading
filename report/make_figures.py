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
from wmr.roll import last_digit_roll, roll_tier

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


def frozen_reader(**changes):
    results = ROOT / "experiments" / "phuc" / "results"
    templates = np.load(results / "templates.npy")
    selected = json.loads((results / "selected.json").read_text(encoding="utf-8"))["config"]
    values = dict(pitch=selected["pitch"], threshold=selected["threshold"], max_shift=selected["max_shift"])
    values.update(changes)
    return WheelReader(templates, WheelConfig(**values))


def window_scores(reader, image):
    cell = extract_cell(preprocess(image), 5, 4).astype(np.float32)
    s = reader.config.max_shift
    padded = cv2.copyMakeBorder(cell, 0, 0, s, s, cv2.BORDER_REPLICATE)
    patches = np.stack([padded[:, x:x + cell.shape[1]].ravel() for x in range(2 * s + 1)])
    patches -= patches.mean(axis=1, keepdims=True)
    denom = reader.norms[:, None] * np.linalg.norm(patches, axis=1)[None, :]
    scores = np.divide(reader.bank @ patches.T, denom, out=np.full(denom.shape, -1, np.float32), where=denom > 1e-8)
    return cell, scores.max(axis=1)


def e2_example(data_root):
    readers = {s: frozen_reader(max_shift=s) for s in (2, 6)}
    for sample in read_split(ROOT / "experiments" / "splits" / "dev_val.csv"):
        if not sample.is_half_word:
            continue
        image = load_image(data_root, sample)
        roll = last_digit_roll(image)
        if roll_tier(roll) != "heavy":
            continue
        digit = sample.reading[-1]
        if readers[2].read(image)[-1] != digit and readers[6].read(image)[-1] == digit                 and abs(readers[6].phase(image)[0] % 1 - roll / 2) < 0.1:
            return sample, image
    raise RuntimeError("no dev_val example found")


def grid_accuracy(path):
    with open(path, encoding="utf-8", newline="") as handle:
        return {(int(r["pitch"]), int(r["max_shift"]), float(r["threshold"])): float(r["last_accuracy"])
                for r in csv.DictReader(handle)}


def figure_e2_params(data_root, grid_path, out):
    sample, image = e2_example(data_root)
    accuracy = grid_accuracy(grid_path)
    truth = sample.reading[-1]
    rows = [
        ("Bán kính trượt ngang $s_x$", "max_shift", (2, 6, 10), lambda v: f"$s_x$ = {v}"),
        ("Bước bánh xe $p$", "pitch", (54, 58, 62), lambda v: f"$p$ = {v}"),
        ("Ngưỡng giải mã $t$", "threshold", (0.4, 0.5, 0.6), lambda v: f"$t$ = {comma(v, 1)}"),
    ]
    fig, axes = plt.subplots(3, 3, figsize=(10, 9.6))
    for r, (name, key, values, label) in enumerate(rows):
        for c, v in enumerate(values):
            reader = frozen_reader(**{key: v})
            cell, scores = window_scores(reader, image)
            index = int(np.argmax(scores))
            phase = reader.indices[index] / reader.config.pitch
            digit = str(int(np.floor(phase + 1 - reader.config.threshold)) % 10)
            cfg = reader.config
            acc = accuracy[(cfg.pitch, cfg.max_shift, round(cfg.threshold, 1))]
            pair = np.hstack([cell, np.full((cell.shape[0], 6), 255, np.float32), reader.windows[index]])
            ax = axes[r, c]
            ax.imshow(pair, cmap="gray", vmin=0, vmax=255)
            verdict = "đúng" if digit == truth else "sai"
            ax.set_title(f"{label(v)}\nr = {comma(phase)}, đọc {digit} ({verdict}), NCC = {comma(float(scores[index]))}\n"
                         f"dev_val: {comma(acc * 100)}%", fontsize=10,
                         color="#0b6e63" if digit == truth else "#c0392b")
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)
        axes[r, 0].set_ylabel(name, fontsize=11)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    return {"name": sample.name, "reading": sample.reading}


def figure_pipeline(data_root, name, out):
    sample = next(s for s in read_split(ROOT / "experiments" / "splits" / "dev_val.csv") if s.name == name)
    image = load_image(data_root, sample)
    reader = frozen_reader()
    equalized = preprocess(image)
    cell, scores = window_scores(reader, image)
    index = int(np.argmax(scores))
    r = reader.indices / reader.config.pitch
    fig = plt.figure(figsize=(12, 6.2))
    grid = fig.add_gridspec(2, 4, height_ratios=[1, 1.25], width_ratios=[1.6, 1.6, 0.55, 0.55], hspace=0.45, wspace=0.3)
    a = fig.add_subplot(grid[0, 0])
    a.imshow(image, cmap="gray", vmin=0, vmax=255)
    a.set_title("(1) Ảnh vùng đọc, mức xám", fontsize=10)
    a.axis("off")
    b = fig.add_subplot(grid[0, 1])
    b.imshow(equalized, cmap="gray", vmin=0, vmax=255)
    b.set_title("(2) Cân bằng histogram, (3) chia năm ô", fontsize=10)
    b.axis("off")
    width = equalized.shape[1] // 5
    for k in range(5):
        b.add_patch(Rectangle((k * width - 0.5, -0.5), width, equalized.shape[0], fill=False,
                              ec="#c47f4a" if k < 4 else "#c0392b", lw=1.5))
    c = fig.add_subplot(grid[0, 2])
    c.imshow(cell, cmap="gray", vmin=0, vmax=255)
    c.set_title("Ô cuối", fontsize=10)
    c.axis("off")
    d = fig.add_subplot(grid[0, 3])
    d.imshow(reader.windows[index], cmap="gray", vmin=0, vmax=255)
    d.set_title("Cửa sổ khớp nhất", fontsize=10)
    d.axis("off")
    e = fig.add_subplot(grid[1, :])
    e.plot(r, scores, color=COLORS["proposed"], lw=1.2)
    e.axvline(r[index], color="#c0392b", ls=":", lw=1.2)
    truth = int(sample.reading[-1])
    e.axvspan(truth - 1 + reader.config.threshold, truth + reader.config.threshold, color="#0b6e63", alpha=0.1)
    e.set_xlim(0, 10)
    e.set_xticks(range(11))
    e.set_xlabel("Vị trí cửa sổ trên dải r (đơn vị chữ số)")
    e.set_ylabel("NCC lớn nhất theo trượt ngang")
    e.yaxis.set_major_formatter(FuncFormatter(lambda v, _: comma(v, 1)))
    e.set_title(f"(4) đến (6) NCC của ô cuối với {len(r)} cửa sổ trên dải; đỉnh tại r = {comma(r[index])}; "
                f"vùng xanh là các r giải mã ra chữ số đúng {truth}", fontsize=10)
    fig.savefig(out)
    plt.close(fig)
    return {"phase": float(r[index]), "score": float(scores[index])}


def figure_e4_pitch(path, out):
    with open(path, encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    mismatches = sorted({float(r["mismatch"]) for r in rows})
    phases = sorted({float(r["phi"]) for r in rows})
    value = {(float(r["mismatch"]), float(r["phi"])): r for r in rows}
    fig, (left, right) = plt.subplots(1, 2, figsize=(11.5, 4.2), gridspec_kw={"width_ratios": [1.15, 1]})
    shades = plt.cm.viridis(np.linspace(0.05, 0.85, len(phases)))
    x = [m * 100 for m in mismatches]
    for color, phi in zip(shades, phases):
        left.plot(x, [float(value[(m, phi)]["proposed_reads_lower_or_next"]) * 100 for m in mismatches], "-o",
                  color=color, ms=4, lw=1.6, label=f"φ = {comma(phi, 1)}")
    left.axhline(50, color="#c0392b", lw=1, ls=":")
    left.set_xlabel("Lệch bước thật so với p = 58 (%)")
    left.set_ylabel("Đọc ra d hoặc d + 1 (%)")
    left.set_ylim(30, 80)
    percent_axis(left.yaxis)
    left.legend(frameon=False, fontsize=9, ncol=3, loc="lower center")
    left.set_title("(a) Tỉ lệ đọc đúng một trong hai chữ số")
    grid = np.array([[float(value[(m, phi)]["proposed_phase_median"]) for m in mismatches] for phi in phases])
    image = right.imshow(grid, origin="lower", cmap="magma_r", vmin=0, vmax=1.2, aspect="auto")
    for i in range(len(phases)):
        for j in range(len(mismatches)):
            right.text(j, i, comma(grid[i, j]), ha="center", va="center", fontsize=7.5,
                       color="white" if grid[i, j] > 0.6 else "black")
    right.set_xticks(range(len(mismatches)), [f"{m * 100:+.0f}" for m in mismatches])
    right.set_yticks(range(len(phases)), [comma(p, 1) for p in phases])
    right.set_xlabel("Lệch bước thật so với p = 58 (%)")
    right.set_ylabel("Pha lăn φ")
    right.set_title("(b) Trung vị sai số pha (chữ số)")
    for spine in right.spines.values():
        spine.set_visible(False)
    bar = fig.colorbar(image, ax=right, shrink=0.85, pad=0.02)
    bar.ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: comma(v, 1)))
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


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
    example = figure_e2_params(data_root, ROOT / "experiments" / "phuc" / "results" / "e2_grid.csv", FIGURES / "fig-e2-params.png")
    stats["e2_example"] = example | figure_pipeline(data_root, example["name"], FIGURES / "fig-pipeline.png")
    figure_e4_pitch(ROOT / "experiments" / "quang" / "results" / "e4_pitch_curve.csv", FIGURES / "fig-e4-pitch.png")
    (ROOT / "report" / "stats.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({g: {m: round(v["accuracy"] * 100, 2) for m, v in e.items() if isinstance(v, dict) and "accuracy" in v} | {"paired": e["paired"]} for g, e in stats.items() if g not in ("strip_example", "e2_example")}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
