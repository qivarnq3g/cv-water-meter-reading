import argparse
import csv
import hashlib
import itertools
import json
from dataclasses import asdict
from pathlib import Path
import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from wmr.baseline import BaselineConfig, build_templates, preprocess, read_meter
from wmr.dataset import default_data_root, load_image, read_split
from wmr.proposed import WheelConfig, WheelReader
from wmr.roll import last_digit_roll, roll_tier
from wmr.analysis import summarize, nuisance

def split_hash(path):
    return hashlib.sha256(path.read_bytes().replace(bytes([13, 10]), bytes([10]))).hexdigest()

def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

def main():
    ap=argparse.ArgumentParser(description='E1/E2 tuning on dev_val and frozen-config evaluation on eval.')
    ap.add_argument('--data-root', type=Path, default=default_data_root())
    ap.add_argument('--output-dir', type=Path, default=Path('experiments/phuc/results'))
    ap.add_argument('--stage', choices=['tune','evaluate'], required=True)
    args=ap.parse_args(); out=args.output_dir; out.mkdir(parents=True,exist_ok=True)
    fit=[s for s in read_split(Path('experiments/splits/dev_fit.csv')) if not s.is_half_word]
    templates=build_templates([load_image(args.data_root,s) for s in fit], [s.reading for s in fit], BaselineConfig())
    if args.stage == 'tune':
        samples=read_split(Path('experiments/splits/dev_val.csv'))
        images=[load_image(args.data_root,s) for s in samples]
        trials=[]
        tiers=np.array([roll_tier(last_digit_roll(im)) for im in images])
        for pitch,shift in itertools.product((54,58,62),(2,6,10)):
            reader=WheelReader(templates,WheelConfig(pitch=pitch,max_shift=shift))
            phases=np.array([reader.phase(im)[0] for im in images])
            for threshold in (0.4,0.5,0.6):
                pred=(np.floor(phases+1-threshold).astype(int)%10)
                correct=pred==np.array([int(s.reading[-1]) for s in samples])
                row=dict(pitch=pitch,max_shift=shift,threshold=threshold,n=len(samples),last_accuracy=float(correct.mean()))
                for tier in ('light','medium','heavy'):
                    mask=tiers==tier
                    row[tier]=float(correct[mask].mean()) if mask.any() else None
                trials.append(row)
        write_csv(out/'e2_grid.csv',trials)
        best=max(trials,key=lambda r:r['last_accuracy'])
        config=WheelConfig(**{k:best[k] for k in ('pitch','max_shift','threshold')})
        fingerprints={p.name:split_hash(p) for p in Path('experiments/splits').glob('*.csv')}
        (out/'selected.json').write_text(json.dumps(dict(config=asdict(config),selection_split='dev_val',criterion='last_accuracy',split_sha256=fingerprints),indent=2))
        np.save(out/'templates.npy',templates)
        fig,axes=plt.subplots(3,4,figsize=(12,6))
        for row,idx in enumerate((0,len(images)//2,len(images)-1)):
            im=images[idx]; reader=WheelReader(templates,config); phase,_=reader.phase(im)
            panels=[im,preprocess(im),preprocess(im)[:,160:200],reader.windows[round(phase*config.pitch)%len(reader.windows)]]
            for ax,panel,title in zip(axes[row],panels,('Ảnh gốc','Cân bằng histogram','Ô chữ số cuối','Cửa sổ dải khớp nhất')):
                ax.imshow(panel,cmap='gray'); ax.set_title(title); ax.axis('off')
        fig.tight_layout(); fig.savefig(out/'e2_intermediates.png',dpi=160); plt.close(fig)
        print(json.dumps(best)); return
    selected=json.loads((out/'selected.json').read_text())
    if selected['selection_split']!='dev_val': raise ValueError('configuration must come from dev_val')
    for p in Path('experiments/splits').glob('*.csv'):
        if split_hash(p)!=selected['split_sha256'][p.name]: raise ValueError('split changed since tuning')
    templates=np.load(out/'templates.npy'); reader=WheelReader(templates,WheelConfig(**selected['config']))
    rows=[]; controls=[]
    for s in read_split(Path('experiments/splits/eval.csv')):
        im=load_image(args.data_root,s); roll=last_digit_roll(im); tier=roll_tier(roll)
        controls.append(dict(name=s.name,tier=tier,last_digit=s.reading[-1],half_word=int(s.is_half_word),**nuisance(im)))
        for method,pred in [('baseline',read_meter(im,templates,BaselineConfig())),('proposed',reader.read(im))]:
            rows.append(dict(name=s.name,reading=s.reading,prediction=pred,method=method,tier=tier,roll=roll))
    write_csv(out/'predictions.csv',rows); write_csv(out/'summary.csv',summarize(rows)); write_csv(out/'e1_controls.csv',controls)
    control_summary=[]
    for tier in ('light','medium','heavy'):
        group=[r for r in controls if r['tier']==tier]
        record=dict(tier=tier,n=len(group))
        for key in ('brightness','contrast','sharpness','half_word'):
            values=[r[key] for r in group]
            record[key+'_mean']=float(np.mean(values)) if values else None
            record[key+'_std']=float(np.std(values)) if values else None
        control_summary.append(record)
    write_csv(out/'e1_control_summary.csv',control_summary)
    stratified=[]
    for tier in ('light','medium','heavy'):
        for digit in '0123456789':
            group=[r for r in rows if r['method']=='baseline' and r['tier']==tier and r['reading'][-1]==digit]
            stratified.append(dict(tier=tier,digit=digit,n=len(group),accuracy=sum(r['prediction'][-1]==digit for r in group)/len(group) if group else None))
    write_csv(out/'e1_by_digit.csv',stratified)
    print(json.dumps(summarize(rows),indent=2))

if __name__=='__main__': main()
