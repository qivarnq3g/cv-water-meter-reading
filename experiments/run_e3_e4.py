import argparse
import csv
import json
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np

from wmr.analysis import summarize
from wmr.baseline import BaselineConfig, extract_cell, match_scores, preprocess
from wmr.dataset import default_data_root, load_image, read_split
from wmr.proposed import WheelConfig, WheelReader
from wmr.roll import TIERS, ink_mask, last_digit_roll, roll_tier

SPLITS = Path('experiments/splits')
PHUC = Path('experiments/phuc/results')


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def frozen():
    selected = json.loads((PHUC / 'selected.json').read_text())
    if selected['selection_split'] != 'dev_val':
        raise ValueError('configuration must come from dev_val')
    return np.load(PHUC / 'templates.npy'), WheelConfig(**selected['config'])


def last_digit(image, templates, shift):
    scores = match_scores(preprocess(image), templates, 4, BaselineConfig(max_shift=shift))
    return int(np.argmax(scores))


def decode(phase, threshold):
    return int(np.floor(phase + 1 - threshold)) % 10


def digit_height(gray):
    mask = ink_mask(gray)
    width = mask.shape[1] // 5
    heights = []
    for position in range(4):
        cell = mask[:, position * width + width // 5:(position + 1) * width - width // 5]
        rows = np.flatnonzero(cell.mean(axis=1) > 0.25)
        if len(rows):
            heights.append(rows[-1] - rows[0] + 1)
    return float(np.median(heights)) if heights else float('nan')


def e3(args, templates, config):
    variants = {
        'baseline': WheelReader(templates, replace(config, enabled=False)),
        'proposed': WheelReader(templates, config),
        'discrete_phase': WheelReader(templates, replace(config, continuous=False)),
    }
    rows, heights = [], []
    for sample in read_split(SPLITS / 'eval.csv'):
        image = load_image(args.data_root, sample)
        roll = last_digit_roll(image)
        tier = roll_tier(roll)
        heights.append(dict(name=sample.name, tier=tier, digit_height=digit_height(image)))
        for method, reader in variants.items():
            rows.append(dict(name=sample.name, reading=sample.reading, prediction=reader.read(image),
                             method=method, tier=tier, roll=roll))
    write_csv(args.output_dir / 'e3_predictions.csv', rows)
    write_csv(args.output_dir / 'e3_summary.csv', summarize(rows))
    return rows, heights


def prediction4(rows, heights, args):
    height = {h['name']: h['digit_height'] for h in heights}
    median = float(np.nanmedian(list(height.values())))
    result = []
    for tier in TIERS:
        for group in ('near', 'far'):
            names = {h['name'] for h in heights if h['tier'] == tier
                     and (abs(h['digit_height'] / median - 1) > args.height_tolerance) == (group == 'far')}
            for method in ('baseline', 'proposed'):
                picked = [r for r in rows if r['method'] == method and r['name'] in names]
                accuracy = sum(r['reading'][-1] == r['prediction'][-1] for r in picked) / len(picked) if picked else None
                result.append(dict(tier=tier, height_group=group, method=method, n=len(picked),
                                   last_accuracy=accuracy))
    write_csv(args.output_dir / 'e4_height_split.csv', result)
    write_csv(args.output_dir / 'e4_digit_heights.csv', heights)
    return dict(median_digit_height=median, tolerance=args.height_tolerance)


def direction_check(args, templates, config):
    samples = [s for s in read_split(SPLITS / 'dev_val.csv') if s.is_half_word]
    forward = WheelReader(templates, config)
    backward = WheelReader(templates[::-1].copy(), config)
    scores = []
    for sample in samples:
        image = load_image(args.data_root, sample)
        scores.append((forward.phase(image)[1], backward.phase(image)[1]))
    scores = np.array(scores)
    return dict(n=len(samples), forward_mean_score=float(scores[:, 0].mean()),
                backward_mean_score=float(scores[:, 1].mean()),
                forward_wins=float((scores[:, 0] > scores[:, 1]).mean()))


def synthetic(args, templates, config):
    rng = np.random.default_rng(args.seed)
    pool = {d: [] for d in range(10)}
    for sample in read_split(SPLITS / 'dev_val.csv'):
        if sample.is_half_word:
            continue
        image = load_image(args.data_root, sample)
        if last_digit_roll(image) < args.still_roll:
            pool[int(sample.reading[-1])].append(image)
    anchors = [(d, im) for d in range(10) for im in pool[d] if pool[(d + 1) % 10]]
    picks = rng.choice(len(anchors), size=min(args.pairs, len(anchors)), replace=False)
    reader = WheelReader(templates, config)
    phases = np.round(np.arange(0, args.max_phase + 1e-9, args.step), 4)
    methods = ['proposed'] + [f'baseline_s{s}' for s in args.shifts]
    rows = []
    for pair, pick in enumerate(picks):
        digit, image = anchors[pick]
        partners = pool[(digit + 1) % 10]
        partner = partners[rng.integers(len(partners))]
        lower = extract_cell(image, 5, 4).astype(np.float32)
        upper = extract_cell(partner, 5, 4).astype(np.float32)
        upper = (upper - upper.mean()) / (upper.std() + 1e-6) * lower.std() + lower.mean()
        strip = np.vstack([lower, upper])
        height, start = lower.shape[0], image.shape[1] // 5 * 4
        for phi in phases:
            offset = int(round(phi * height))
            rolled = image.copy()
            rolled[:, start:start + lower.shape[1]] = np.clip(strip[offset:offset + height], 0, 255).astype(np.uint8)
            estimate, _ = reader.phase(rolled)
            row = dict(pair=pair, digit=digit, phi=float(phi), measured_roll=last_digit_roll(rolled),
                       proposed=decode(estimate, config.threshold),
                       phase_error=float((estimate - (digit + phi) + 5) % 10 - 5))
            for shift in args.shifts:
                row[f'baseline_s{shift}'] = last_digit(rolled, templates, shift)
            rows.append(row)
    write_csv(args.output_dir / 'e4_synthetic.csv', rows)
    curve = []
    for phi in phases:
        group = [r for r in rows if r['phi'] == phi]
        record = dict(phi=float(phi), n=len(group),
                      measured_roll=float(np.mean([r['measured_roll'] for r in group])),
                      proposed_phase_mae=float(np.mean([abs(r['phase_error']) for r in group])),
                      proposed_phase_median=float(np.median([abs(r['phase_error']) for r in group])),
                      proposed_phase_within_quarter=float(np.mean([abs(r['phase_error']) < 0.25 for r in group])))
        for method in methods:
            record[f'{method}_reads_lower'] = float(np.mean([r[method] == r['digit'] for r in group]))
            record[f'{method}_reads_lower_or_next'] = float(np.mean(
                [r[method] in (r['digit'], (r['digit'] + 1) % 10) for r in group]))
        curve.append(record)
    write_csv(args.output_dir / 'e4_curve.csv', curve)
    breaks = {}
    for method in methods:
        below = [c['phi'] for c in curve if c[f'{method}_reads_lower_or_next'] < args.break_level]
        breaks[method] = below[0] if below else None
    return dict(pairs=len(picks), still_pool={d: len(v) for d, v in pool.items()},
                break_level=args.break_level, first_phi_below_break_level=breaks), curve


def plot(curve, out, shifts):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    phi = [c['phi'] for c in curve]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].plot(phi, [c['proposed_reads_lower_or_next'] for c in curve], 'o-', label='Đề xuất')
    for shift in shifts:
        axes[0].plot(phi, [c[f'baseline_s{shift}_reads_lower_or_next'] for c in curve], 's--',
                     label=f'Baseline, trượt ±{shift}')
    axes[0].set_xlabel('Pha lăn tổng hợp φ')
    axes[0].set_ylabel('Tỉ lệ đọc ra d hoặc d + 1')
    axes[0].set_title('E4: độ chính xác theo pha lăn')
    axes[0].set_ylim(0, 1.02)
    axes[0].legend()
    axes[1].plot(phi, [c['proposed_phase_median'] for c in curve], 'o-', label='Trung vị sai số pha (chữ số)')
    axes[1].plot(phi, [c['proposed_phase_within_quarter'] for c in curve], 's--', label='Tỉ lệ sai số pha dưới 0,25')
    axes[1].set_xlabel('Pha lăn tổng hợp φ')
    axes[1].set_ylim(0, 1.02)
    axes[1].set_title('E4: ước lượng pha của phương pháp đề xuất')
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(out / 'e4_curve.png', dpi=160)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description='E3 ablation on eval and E4 breaking-point tests with the frozen dev_val configuration.')
    ap.add_argument('--data-root', type=Path, default=default_data_root())
    ap.add_argument('--output-dir', type=Path, default=Path('experiments/quang/results'))
    ap.add_argument('--pairs', type=int, default=400)
    ap.add_argument('--step', type=float, default=0.05)
    ap.add_argument('--max-phase', type=float, default=0.5)
    ap.add_argument('--still-roll', type=float, default=0.21)
    ap.add_argument('--shifts', type=int, nargs='+', default=[2, 6, 10])
    ap.add_argument('--break-level', type=float, default=0.5)
    ap.add_argument('--height-tolerance', type=float, default=0.09)
    ap.add_argument('--seed', type=int, default=0)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    templates, config = frozen()
    report = dict(config=asdict(config))
    rows, heights = e3(args, templates, config)
    report['prediction4'] = prediction4(rows, heights, args)
    report['direction'] = direction_check(args, templates, config)
    report['synthetic'], curve = synthetic(args, templates, config)
    plot(curve, args.output_dir, args.shifts)
    (args.output_dir / 'e3_e4_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
