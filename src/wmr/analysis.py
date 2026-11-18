import cv2
import numpy as np
from .metrics import position_accuracy, reading_accuracy
from .roll import TIERS

def summarize(rows):
    result = []
    for method in sorted({r['method'] for r in rows}):
        for tier in ('all', *TIERS):
            group = [r for r in rows if r['method'] == method and (tier == 'all' or r['tier'] == tier)]
            if not group:
                result.append(dict(method=method, tier=tier, n=0)); continue
            t, p = [r['reading'] for r in group], [r['prediction'] for r in group]
            acc = position_accuracy(t, p)
            errors = [r for r in group if r['reading'][-1] != r['prediction'][-1]]
            adjacent = sum((int(r['reading'][-1])-int(r['prediction'][-1])) % 10 in (1,9) for r in errors)
            result.append(dict(method=method, tier=tier, n=len(group),
                               **{f'd{i+1}':a for i,a in enumerate(acc)},
                               first4=float(np.mean(acc[:4])), full=reading_accuracy(t,p),
                               last_errors=len(errors), adjacent_errors=adjacent,
                               adjacent_fraction=adjacent/len(errors) if errors else None))
    return result

def nuisance(image):
    return dict(brightness=float(image.mean()), contrast=float(image.std()),
                sharpness=float(cv2.Laplacian(image, cv2.CV_64F).var()))
