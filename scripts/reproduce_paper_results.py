#!/usr/bin/env python3
"""Two reviewer-requested experiments on the regenerated multi-attack dataset:
  1. Fold variability + significance of mobility-aware vs network-only.
  2. Mobile_X_Pos-excluded ablation (general spatial context vs location memorization).
Scenario-grouped 5-fold CV (leakage-free), RF/GB/LR.
"""
import numpy as np, pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GroupKFold
from sklearn.metrics import f1_score
from scipy import stats

CSV = "data/dyniot_ddos_timeseries.csv.gz"
SEED = 42
NET     = ["Node_Sending_Rate_Pkts", "Node_Sending_Rate_Bytes", "Rx_Bytes_Per_Sec", "Rx_Pkts_Per_Sec"]
SPATIAL = ["Mobile_X_Pos", "Movement_Angle", "Start_Offset", "Node_Density"]
MOB     = NET + SPATIAL                                   # 8
MOB_noX = NET + ["Movement_Angle", "Start_Offset", "Node_Density"]   # 7 (drop Mobile_X_Pos)
LABEL, GROUP = "Is_Under_Attack", "Scenario_ID"

df = pd.read_csv(CSV)
y = df[LABEL].to_numpy(); g = df[GROUP].to_numpy()

def models():
    return {
        "RandomForest":       RandomForestClassifier(n_estimators=150, random_state=SEED, n_jobs=-1),
        "GradientBoosting":   GradientBoostingClassifier(n_estimators=150, random_state=SEED),
        "LogisticRegression": make_pipeline(StandardScaler(),
                               LogisticRegression(max_iter=1000, random_state=SEED)),
    }

def per_fold_f1(feats):
    """Return list of per-fold F1 for a feature set (scenario-grouped 5-fold), per model."""
    X = df[feats].to_numpy()
    out = {name: [] for name in models()}
    gkf = GroupKFold(5)
    for name, proto in models().items():
        for tr, te in gkf.split(X, y, g):
            m = models()[name]  # fresh
            m.fit(X[tr], y[tr])
            out[name].append(f1_score(y[te], m.predict(X[te]), zero_division=0))
    return out

print("Computing per-fold F1 (this takes a minute)...")
f1_mob   = per_fold_f1(MOB)
f1_net   = per_fold_f1(NET)
f1_noX   = per_fold_f1(MOB_noX)

print("\n" + "="*74)
print("EXPERIMENT 1 — Fold variability + significance (mobility-aware vs network-only)")
print("="*74)
print(f"{'Model':<20}{'Mob F1 (mean±std)':<22}{'Net F1 (mean±std)':<22}{'Δpp':>6}")
sig = {}
for name in models():
    mob = np.array(f1_mob[name]); net = np.array(f1_net[name])
    diff = mob - net
    t_p = stats.ttest_rel(mob, net).pvalue
    try:
        w_p = stats.wilcoxon(mob, net).pvalue
    except ValueError:
        w_p = float("nan")
    sig[name] = (mob, net, diff, t_p, w_p)
    print(f"{name:<20}{mob.mean():.4f} ± {mob.std():.4f}   {net.mean():.4f} ± {net.std():.4f}   {100*diff.mean():+5.2f}")
print("\nPer-fold detail and paired tests (H0: mobility = network):")
for name in models():
    mob, net, diff, t_p, w_p = sig[name]
    wins = int((diff > 0).sum())
    print(f"\n  {name}")
    print(f"    mob folds: {[f'{v:.4f}' for v in mob]}")
    print(f"    net folds: {[f'{v:.4f}' for v in net]}")
    print(f"    per-fold Δ: {[f'{100*v:+.2f}pp' for v in diff]}")
    print(f"    mean Δ = {100*diff.mean():+.2f}pp | folds mob>net: {wins}/5 | "
          f"paired t p={t_p:.4f} | Wilcoxon p={w_p:.4f}")

print("\n" + "="*74)
print("EXPERIMENT 2 — Mobile_X_Pos-excluded (general spatial context vs location memorization)")
print("="*74)
print(f"{'Model':<20}{'Mob-8 F1':>10}{'Mob-noX-7 F1':>14}{'Net-4 F1':>10}"
      f"{'noX vs net':>12}{'full vs noX':>13}")
for name in models():
    m8  = np.array(f1_mob[name]).mean()
    m7  = np.array(f1_noX[name]).mean()
    n4  = np.array(f1_net[name]).mean()
    print(f"{name:<20}{m8:>10.4f}{m7:>14.4f}{n4:>10.4f}"
          f"{100*(m7-n4):>+11.2f}pp{100*(m8-m7):>+12.2f}pp")
print("\nReading: if 'noX vs net' stays clearly positive, the gain is GENERAL spatial context")
print("(density/angle/offset), not just memorizing attacker x-locations. 'full vs noX' is")
print("the extra value contributed specifically by the mobile's along-path position.")
