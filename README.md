# DynIoT-DDoS

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21627584.svg)](https://doi.org/10.5281/zenodo.21627584)
[![Data licence: CC BY 4.0](https://img.shields.io/badge/data-CC%20BY%204.0-blue.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Code licence: MIT](https://img.shields.io/badge/code-MIT-green.svg)](LICENSE-CODE)

A **mobility-aware, multi-attack DDoS detection dataset** for Smart City IoT, generated with NS-3.

Unlike existing IoT intrusion-detection benchmarks, which record traffic from **stationary**
topologies, DynIoT-DDoS captures a mobile IoT agent traversing a spatially heterogeneous field of
fixed nodes. As the agent moves, its neighbour count, and therefore its legitimate traffic, rises
and falls continuously. Attacks are **context-triggered**: each malicious node fires only while the
mobile agent is inside its radio range, so adversarial traffic co-occurs with the legitimate,
mobility-induced surge. This operationalises the *flash-crowd ambiguity* for a node in motion.

## Contents

| Path | Description |
|---|---|
| `data/dyniot_ddos_timeseries.csv.gz` | Per-second time-series view — **11,084 rows × 18 columns** |
| `scripts/reproduce_paper_results.py` | Reproduces the paper's detection + ablation results |

> **Flow-level view** (795,683 records × 14 columns, CICFlowMeter-style per-flow features) is
> published alongside the archived release — see *Releases*.

## Dataset at a glance

- **184 scenarios** (46 per attack type), **11,084** labelled samples, sampled at 1 Hz
- **Attack prevalence: 72.03 %** — a deliberate worst-case adversarial workload (see *Caveats*)
- **4 context-triggered attack types**, perfectly balanced (2,771 rows each):
  `udp_flood`, `tcp_flood`, `icmp_flood`, `jamming` (MAC-layer channel jamming)

### Simulated environment
61 fixed nodes on a rhombus arena (W = 100 m, H = 76 m), 13 columns spaced 8 m apart with a peaked
per-column distribution `{1,1,3,5,7,7,9,9,7,5,3,3,1}`. One mobile agent at 1 m/s, 20 m radio range,
IEEE 802.11n **ad hoc (IBSS)**, hard-cutoff range propagation. Two-phase traffic: UDP-broadcast
neighbour discovery, then continuous TCP collaboration.

### Scenario grid
| Parameter | Values |
|---|---|
| Start offset `d` | 0, 20, 40 m |
| Movement angle `α` | 0° → `α_max(d)` in 15° steps (8 distinct angles, 0–75.3°) |
| Attackers `n_mal` | 1, 3, 5 |
| Along-path spacing `s` | 8, 24 m (0 when `n_mal` = 1) |

All malicious nodes are placed **on** the agent's traversal path, guaranteeing exposure.

## Schema (time-series view)

**Spatial context** (4) — the novel part
| Column | Description |
|---|---|
| `Mobile_X_Pos` | Agent x-coordinate (m) |
| `Movement_Angle` | Traversal angle α (degrees) |
| `Start_Offset` | Start x-position d (m) |
| `Node_Density` | ρ(t): fixed nodes within 20 m of the agent |

**Network activity** (4)
| Column | Description |
|---|---|
| `Node_Sending_Rate_Pkts` / `Node_Sending_Rate_Bytes` | Agent TX rate per 1 s window |
| `Rx_Bytes_Per_Sec` / `Rx_Pkts_Per_Sec` | Agent RX rate per 1 s window |

> Counters measure **the mobile agent's own NIC**, not network-wide aggregates.

**Labels** (2) — `Is_Under_Attack` (binary target), `Attack_Type` (4 classes)

**Oracle — excluded from training** (2) — `Malicious_Neighbors`, `Dist_To_Attacker`.
These document how the label was derived (`Is_Under_Attack := Malicious_Neighbors > 0`).
**Using them as inputs is label leakage** — a real node cannot know which neighbours are malicious.

**Metadata** (6) — `SimulationTime`, `Mobile_Y_Pos`, `Scenario_ID`, `Mobile_Speed`,
`N_Malicious`, `Mal_Spacing`

## Usage

```python
import pandas as pd
df = pd.read_csv("data/dyniot_ddos_timeseries.csv.gz")   # gzip read natively

SPATIAL = ["Mobile_X_Pos", "Movement_Angle", "Start_Offset", "Node_Density"]
NETWORK = ["Node_Sending_Rate_Pkts", "Node_Sending_Rate_Bytes",
           "Rx_Bytes_Per_Sec", "Rx_Pkts_Per_Sec"]
X, y    = df[NETWORK + SPATIAL], df["Is_Under_Attack"]
```

### Evaluate correctly — group by scenario

Rows within a scenario are temporally autocorrelated. A random row-wise split leaks near-duplicate
rows into the test set and **massively inflates scores**. Always group by `Scenario_ID`:

```python
from sklearn.model_selection import GroupKFold
cv = GroupKFold(5).split(X, y, groups=df["Scenario_ID"])
```

Reproduce the published numbers:
```bash
pip install pandas scikit-learn scipy
python scripts/reproduce_paper_results.py
```

## Reference results

Scenario-grouped 5-fold CV, leakage-free. Spatial context improves detection for every classifier
(mobility-aware wins in 5/5 folds in each case):

| Model | Mobility-aware (8 feat) | Network-only (4 feat) | Δ F1 |
|---|---|---|---|
| Random Forest (150 trees) | **0.926** ± 0.008 | 0.913 ± 0.010 | +1.3 pp |
| Gradient Boosting (150 est.) | **0.927** ± 0.008 | 0.909 ± 0.012 | +1.8 pp |
| Logistic Regression (scaled) | **0.925** ± 0.008 | 0.903 ± 0.015 | +2.2 pp |

Removing `Mobile_X_Pos` still beats network-only (+0.7 / +1.0 / +1.3 pp), so the gain reflects
**general spatial context** (density, angle, offset) rather than memorised attacker locations.

## Caveats and intended use

- **Simulation-based.** Not validated against physical-testbed captures; propagation uses a
  hard-cutoff range model, so real-world thresholds may differ.
- **72 % attack prevalence is by design**, a consequence of on-path attacker placement. It is a
  worst-case adversarial workload, **not** a deployment-typical base rate. Re-weight or resample
  if you need realistic prevalence.
- **Single topology and mobility model.** One density-gradient arena; straight-line, constant-speed
  trajectories. Robustness to other layouts (uniform, clustered, multi-hub) is untested.
- **Attack coverage** is four volumetric/MAC-layer classes. Low-and-slow, application-layer, and
  half-open (SYN) variants are absent.
- **802.11n only** — no LoRa, NB-IoT, or BLE.

## Generation code

Produced with an NS-3 3.43 framework (Python bindings). The generator is released separately;
see the *Releases* page for the version pinned to this dataset.

## Citation

Cite the dataset via its **concept DOI**, which always resolves to the newest version:

> Halladj, H., Saïdouni, D. E., Maati, B., & Díaz, G. (2026). *DynIoT-DDoS: a mobility-aware,
> multi-attack DDoS detection dataset for Smart City IoT* [Data set]. Zenodo.
> https://doi.org/10.5281/zenodo.21627584

```bibtex
@dataset{halladj2026dyniotddos,
  author    = {Halladj, Hamza and Sa\"{i}douni, Djamel Eddine and Maati, Bouchera and D\'{i}az, Gregorio},
  title     = {{DynIoT-DDoS}: a mobility-aware, multi-attack {DDoS} detection dataset for {Smart City IoT}},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.21627584},
  url       = {https://doi.org/10.5281/zenodo.21627584}
}
```

Please also cite the accompanying paper (see `CITATION.cff`):

> H. Halladj, D. E. Saïdouni, B. Maati, and G. Díaz, "DynIoT-DDoS: A Framework for Constructing
> Benchmark Datasets for DDoS Attack Detection in Dynamic Environments." *(under review)*

## Licence

- **Data** (`data/`) — [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (see `LICENSE`)
- **Code** (`scripts/`) — MIT (see `LICENSE-CODE`)
