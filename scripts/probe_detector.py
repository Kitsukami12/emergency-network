import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold, StratifiedKFold
from torchvision import models, transforms as T

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "data/videos/data")
EXT = {".jpg", ".jpeg", ".png"}
CACHE = Path("results/features.npz")
Path("results").mkdir(exist_ok=True)


def video_id(p):
    m = re.match(r"(?:test)?(\d+)_\d+", p.stem)
    if m:
        return f"v{m.group(1)}"
    m = re.match(r"acc(\d+)", p.stem)
    return f"acc{m.group(1)}" if m else "unknown:" + p.stem


items = [(f, lab, video_id(f))
         for s in ["train", "val", "test"]
         for cls, lab in [("Accident", 1), ("Non Accident", 0)]
         for f in sorted((ROOT / s / cls).glob("*")) if f.suffix.lower() in EXT]
paths = [i[0] for i in items]
y = np.array([i[1] for i in items])
groups = np.array([i[2] for i in items])

# how are the classes spread across videos?
by = defaultdict(set)
for _, lab, g in items:
    if not g.startswith("unknown"):
        by[g].add(lab)
both = sum(len(v) == 2 for v in by.values())
print(f"{len(by)} placed videos: {both} contain BOTH classes, "
      f"{sum(v == {1} for v in by.values())} accident-only, "
      f"{sum(v == {0} for v in by.values())} normal-only")

# frozen ResNet18 features, computed once
if CACHE.exists():
    X = np.load(CACHE)["X"]
else:
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    net = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    net.fc = nn.Identity()
    net.eval().to(device)
    tf = T.Compose([T.Resize((288, 352)), T.Resize((224, 224)), T.ToTensor(),
                    T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
    feats = []
    with torch.no_grad():
        for i in range(0, len(paths), 32):
            batch = torch.stack([tf(Image.open(p).convert("RGB")) for p in paths[i:i + 32]])
            feats.append(net(batch.to(device)).cpu().numpy())
    X = np.concatenate(feats)
    np.savez(CACHE, X=X)
print("features:", X.shape)


def cv_auc(splits):
    aucs = []
    for tr, te in splits:
        if len(set(y[te])) < 2:
            continue
        clf = LogisticRegression(max_iter=3000, C=0.1, class_weight="balanced")
        clf.fit(X[tr], y[tr])
        aucs.append(roc_auc_score(y[te], clf.predict_proba(X[te])[:, 1]))
    return np.array(aucs)


random_auc = cv_auc(StratifiedKFold(5, shuffle=True, random_state=0).split(X, y))
group_auc = cv_auc(GroupKFold(5).split(X, y, groups))
print(f"\nRANDOM frame split : AUC {random_auc.mean():.3f} +/- {random_auc.std():.3f}")
print(f"BY-VIDEO split     : AUC {group_auc.mean():.3f} +/- {group_auc.std():.3f}  folds={np.round(group_auc, 2)}")