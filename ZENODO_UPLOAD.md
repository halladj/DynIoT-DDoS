# Zenodo manual upload — copy-paste sheet

The GitHub→Zenodo webhook kept returning HTTP 409, so upload manually instead.
Go to **https://zenodo.org/uploads/new** and fill in the fields below.

---

## Files to upload
- `data/dyniot_ddos_timeseries.csv.gz`  (11,084 rows — in this repo)
- `combined_flow_features.csv`  (795,683 rows — copy from the sim box:
  `/home/halladj_hamza/projects/misc/workspace/batch_validate/combined_flow_features.csv`)
  Upload it **uncompressed**; Zenodo allows up to 50 GB per record.

## Resource type
`Dataset`

## Title
```
DynIoT-DDoS: a mobility-aware, multi-attack DDoS detection dataset for Smart City IoT
```

## Authors (Creators)
| Name | Affiliation |
|---|---|
| Halladj, Hamza | MISC Laboratory, University Constantine 2 - Abdelhamid Mehri, Constantine, Algeria |
| Saïdouni, Djamel Eddine | University Constantine 2 - Abdelhamid Mehri, Constantine, Algeria |
| Maati, Bouchera | Faculty of Sciences, Ferhat Abbas University Setif 1, Setif, Algeria |
| Díaz, Gregorio | School of Computer Science, University of Castilla-La Mancha, Albacete, Spain |

Add ORCIDs if the co-authors have them — it improves indexing.

## Description
```
DynIoT-DDoS is a mobility-aware benchmark dataset for DDoS detection in Smart City IoT,
generated with the NS-3 network simulator (v3.43).

Unlike existing IoT intrusion-detection benchmarks, which record traffic from stationary
topologies, DynIoT-DDoS captures a mobile IoT agent traversing a spatially heterogeneous
field of 61 fixed nodes. As the agent moves, its neighbour count, and therefore its
legitimate traffic, rises and falls continuously. Attacks are context-triggered: each
malicious node transmits only while the mobile agent is inside its 20 m radio range, so
adversarial traffic co-occurs with the legitimate, mobility-induced surge. This
operationalises the "flash-crowd ambiguity" for a node in motion.

CONTENTS
- Time-series view: 11,084 labelled samples x 18 columns, sampled at 1 Hz.
- Flow-level view: 795,683 records x 14 columns (CICFlowMeter-style per-flow features).
Both are derived from the same 184 simulation runs, balanced across four context-triggered
attack types (UDP, TCP and ICMP floods, and MAC-layer channel jamming; 46 scenarios each).

SCENARIO GRID
Start offset d in {0, 20, 40} m; movement angle alpha in 15-degree steps (0 to 75.3 deg);
attacker count n in {1, 3, 5}; along-path spacing s in {8, 24} m. All malicious nodes are
placed on the agent's traversal path, guaranteeing exposure.

FEATURES
Four spatial-context attributes (Mobile_X_Pos, Movement_Angle, Start_Offset, Node_Density)
and four network-activity counters measured on the mobile agent's own interface
(Node_Sending_Rate_Pkts/Bytes, Rx_Bytes_Per_Sec, Rx_Pkts_Per_Sec). Labels are
Is_Under_Attack (binary) and Attack_Type (4 classes). Two oracle columns
(Malicious_Neighbors, Dist_To_Attacker) document label derivation and MUST be excluded
from training: using them is direct label leakage.

EVALUATION NOTE
Rows within a scenario are temporally autocorrelated. Always group by Scenario_ID (e.g.
scikit-learn GroupKFold). A random row-wise split leaks near-duplicate rows into the test
set and substantially inflates scores.

CAVEATS
Simulation-based; not validated against physical-testbed captures. The 72% attack
prevalence follows from deliberate on-path attacker placement and is a worst-case
adversarial workload, not a deployment-typical base rate. A single density-gradient
topology and straight-line, constant-speed trajectories are used. Physical layer is
IEEE 802.11n ad hoc (IBSS) only.

A reproduction script accompanying the dataset regenerates the reference detection and
ablation results under leakage-free, scenario-grouped 5-fold cross-validation.
```

## License
`Creative Commons Attribution 4.0 International (CC BY 4.0)`

## Keywords
```
Internet of Mobile Things; IoMT; DDoS detection; intrusion detection dataset; Smart City;
NS-3; network simulation; mobility; machine learning benchmark; network security
```

## Related identifiers
| Relation | Identifier |
|---|---|
| `is supplemented by` (or `is derived from`) | https://github.com/halladj/DynIoT-DDoS |

Once the paper is accepted, add its DOI with relation `is supplement to`.

## Version
`1.0.0`

---

## After publishing

1. Zenodo gives you **two DOIs**:
   - a **version DOI** (this exact upload)
   - a **concept DOI** (always resolves to the newest version)
   Use the **concept DOI** in the paper's Data Availability statement.

2. Update the paper — replace the placeholder in `main.tex`:
   ```
   The simulation framework, generated dataset, configurations, and analysis notebooks
   are openly available at https://doi.org/<CONCEPT-DOI> and
   https://github.com/halladj/DynIoT-DDoS.
   ```
   (and delete the `% TODO` line beneath it)

3. Add the DOI badge to this repo's README:
   ```markdown
   [![DOI](https://zenodo.org/badge/DOI/<DOI>.svg)](https://doi.org/<DOI>)
   ```
