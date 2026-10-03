import json
import random
import re
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from sklearn.metrics import (confusion_matrix, f1_score, precision_score,
                             recall_score, roc_auc_score)
from sklearn.model_selection import GroupShuffleSplit
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms as T

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "data/videos/data")
EXT = {".jpg", ".jpeg", ".png"}
SEED, EPOCHS, BATCH, LR = 0, 8, 32, 1e-4
OUT = Path("models")
OUT.mkdir(exist_ok=True)
Path("results").mkdir(exist_ok=True)

random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)
device = ("mps" if torch.backends.mps.is_available()
          else "cuda" if torch.cuda.is_available() else "cpu")
print("device:", device)


def video_id(p: Path) -> str:
    """Guess the source video from the file name (the dataset does not say)."""
    m = re.match(r"(?:test)?(\d+)_\d+", p.stem)
    if m:
        return f"v{m.group(1)}"
    m = re.match(r"acc(\d+)", p.stem)
    if m:
        return f"acc{m.group(1)}"
    return "unknown:" + p.stem          # unplaceable: its own group


# 1. pool every split, ignore the dataset's own (leaky) split
items = []
for split in ["train", "val", "test"]:
    for cls, label in [("Accident", 1), ("Non Accident", 0)]:
        for f in sorted((ROOT / split / cls).glob("*")):
            if f.suffix.lower() in EXT:
                items.append((f, label, video_id(f)))
paths = [i[0] for i in items]
labels = np.array([i[1] for i in items])
groups = np.array([i[2] for i in items])
print(f"{len(items)} images, {len(set(groups))} source groups, "
      f"{sum(g.startswith('unknown') for g in groups)} unplaceable files")

# 2. split by video: 70% train, 15% val, 15% test
gss = GroupShuffleSplit(n_splits=1, test_size=0.30, random_state=SEED)
train_idx, rest_idx = next(gss.split(paths, labels, groups))
gss2 = GroupShuffleSplit(n_splits=1, test_size=0.50, random_state=SEED)
v, t = next(gss2.split(rest_idx, labels[rest_idx], groups[rest_idx]))
val_idx, test_idx = rest_idx[v], rest_idx[t]

for name, idx in [("train", train_idx), ("val", val_idx), ("test", test_idx)]:
    print(f"{name:<6}{len(idx):>5} images, {len(set(groups[idx])):>3} videos, "
          f"{labels[idx].sum():>4} accident")
assert not (set(groups[train_idx]) & set(groups[test_idx])), "leak between train and test"
json.dump({n: [str(paths[i]) for i in idx] for n, idx in
           [("train", train_idx), ("val", val_idx), ("test", test_idx)]},
          open("results/split.json", "w"), indent=1)

# 3. images are shrunk to the camera's resolution first, then to the network size
CAM = T.Resize((288, 352))
NORM = T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
train_tf = T.Compose([CAM, T.RandomResizedCrop(224, scale=(0.7, 1.0)),
                      T.RandomHorizontalFlip(), T.ColorJitter(0.3, 0.3, 0.3),
                      T.ToTensor(), NORM])
eval_tf = T.Compose([CAM, T.Resize((224, 224)), T.ToTensor(), NORM])


class Frames(Dataset):
    def __init__(self, idx, tf):
        self.idx, self.tf = idx, tf

    def __len__(self):
        return len(self.idx)

    def __getitem__(self, k):
        i = self.idx[k]
        return self.tf(Image.open(paths[i]).convert("RGB")), int(labels[i])


def loader(idx, tf, shuffle):
    return DataLoader(Frames(idx, tf), batch_size=BATCH, shuffle=shuffle, num_workers=0)


# 4. pretrained ResNet18, new 2-class head, fine-tuned
model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
model.fc = nn.Linear(model.fc.in_features, 2)
model.to(device)
opt = torch.optim.Adam(model.parameters(), lr=LR)
loss_fn = nn.CrossEntropyLoss()


def predict(dl):
    model.eval()
    probs, ys = [], []
    with torch.no_grad():
        for x, y in dl:
            p = torch.softmax(model(x.to(device)), dim=1)[:, 1]
            probs += p.cpu().tolist(); ys += y.tolist()
    return np.array(probs), np.array(ys)


best_f1 = -1
for epoch in range(1, EPOCHS + 1):
    model.train()
    total = 0.0
    for x, y in loader(train_idx, train_tf, True):
        opt.zero_grad()
        loss = loss_fn(model(x.to(device)), y.to(device))
        loss.backward(); opt.step()
        total += loss.item() * len(y)
    p, y = predict(loader(val_idx, eval_tf, False))
    f1 = f1_score(y, p >= 0.5, zero_division=0)
    print(f"epoch {epoch}: train loss {total / len(train_idx):.3f}, val F1 {f1:.3f}")
    if f1 > best_f1:
        best_f1 = f1
        torch.save(model.state_dict(), OUT / "detector.pt")

# 5. final test on videos the model has never seen
model.load_state_dict(torch.load(OUT / "detector.pt", map_location=device))
p, y = predict(loader(test_idx, eval_tf, False))
pred = p >= 0.5
print("\nTEST (unseen videos), accident = positive class")
print("precision:", round(precision_score(y, pred, zero_division=0), 3))
print("recall   :", round(recall_score(y, pred, zero_division=0), 3))
print("F1       :", round(f1_score(y, pred, zero_division=0), 3))
print("AUC      :", round(roc_auc_score(y, p), 3))
print("confusion [[TN FP] [FN TP]]:\n", confusion_matrix(y, pred))