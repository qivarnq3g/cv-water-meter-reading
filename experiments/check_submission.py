"""Validate a submission checkout without the full dataset or a Git directory."""
import argparse
import csv
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def rows(path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def check(root):
    required = [
        'README.md', 'requirements.txt', 'requirements-dev.txt', 'pyproject.toml',
        'experiments/run_sample.py', 'experiments/run_phuc.py', 'experiments/run_e3_e4.py',
        'data/sample/recognition_labels.csv', 'notebooks/phuc_experiments.ipynb',
        'report/report.md', 'report/questions-answers.md', 'report/phuc-presentation.md',
        'report/Doc-chi-so-dong-ho-nuoc-Suon-thuyet-trinh.pptx',
        'experiments/phuc/results/templates.npy', 'experiments/phuc/results/selected.json',
        'experiments/quang/results/e4_pitch_curve.csv',
        'experiments/quang/results/e4_pitch_synthetic.csv',
    ]
    missing = [name for name in required if not (root/name).is_file()]
    if missing:
        raise ValueError('Missing required files: ' + ', '.join(missing))
    sample_labels = rows(root/'data/sample/recognition_labels.csv')
    for row in sample_labels:
        if not (root/'data/sample'/row['name']).is_file():
            raise ValueError('Missing sample image: ' + row['name'])
    e3 = rows(root/'experiments/quang/results/e3_predictions.csv')
    maps = {}
    for method in ('baseline', 'proposed'):
        chosen = [r for r in e3 if r['method'] == method]
        maps[method] = {r['name']: r for r in chosen}
        if len(maps[method]) != len(chosen) or len(chosen) != 2000:
            raise ValueError('Invalid prediction names for ' + method)
    if maps['baseline'].keys() != maps['proposed'].keys():
        raise ValueError('Unpaired evaluation predictions')
    for name, row in maps['baseline'].items():
        other = maps['proposed'][name]
        if row['reading'] != other['reading'] or row['tier'] != other['tier']:
            raise ValueError('Inconsistent labels or tiers: ' + name)
    grid = rows(root/'experiments/phuc/results/e2_grid.csv')
    if len({(r['pitch'], r['max_shift'], r['threshold']) for r in grid}) != 27:
        raise ValueError('E2 must contain 27 unique configurations')
    pitch = rows(root/'experiments/quang/results/e4_pitch_curve.csv')
    if len({(r['mismatch'], r['phi']) for r in pitch}) != 54 or any(int(r['n']) != 165 for r in pitch):
        raise ValueError('Invalid E4 pitch grid')
    report = (root/'report/report.md').read_text(encoding='utf-8')
    if re.findall(r'^# (\d+)\.', report, re.M) != list(map(str, range(1, 13))):
        raise ValueError('Report must contain 12 sections')
    for image in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', report):
        if not (root/'report'/image).is_file():
            raise ValueError('Missing report figure: ' + image)
    deck = root/'report/Doc-chi-so-dong-ho-nuoc-Suon-thuyet-trinh.pptx'
    with ZipFile(deck) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError('Corrupt slide asset: ' + bad)
        slides = [p for p in archive.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml', p)]
        if len(slides) != 14:
            raise ValueError('Expected the established 14-slide deck')
        for name in archive.namelist():
            if name.endswith('.xml'):
                ET.fromstring(archive.read(name))
        if 'Đúng một phần' not in archive.read('ppt/slides/slide9.xml').decode('utf-8-sig'):
            raise ValueError('Slide 9 has no updated partial-support conclusion')
    return {
        'source_checks': 'passed', 'samples': len(sample_labels), 'eval_images': 2000,
        'e2_configurations': 27, 'e4_pitch_cells': 54, 'slides': 14,
        'sha256': {name: hashlib.sha256((root/name).read_bytes()).hexdigest() for name in required},
        'limits': ['Does not verify slide or report rendering, cover information, rehearsal or Moodle submission.',
                   'Run pytest, run_sample and the notebook separately to verify execution.'],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path, default=Path('outputs/submission_check.json'))
    args = parser.parse_args()
    result = check(args.root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Submission source checks passed. Manifest:', args.output)
    print('Rendering, cover information, rehearsal and Moodle submission require separate verification.')


if __name__ == '__main__':
    main()
