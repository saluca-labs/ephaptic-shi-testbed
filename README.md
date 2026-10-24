![ephaptic-shi-testbed](docs/img/banner-2026-10-23.jpg)

# Ephaptic-Analog Testbed

A neuron-free testbed for **two-channel, two-speed interference**, the mechanism Rebbin et al. (bioRxiv 2025, [10.1101/2025.11.03.686361](https://doi.org/10.1101/2025.11.03.686361)) propose for ephaptic-axonal shaping of neural self-organization. It is the companion code, data and preprint for researchers who want to reproduce or extend the result.

We build the motif in a substrate with **no neurons, no ions, and no ephaptic physics** (a mesh of software agents in which the fast channel is directed message passing and the slow channel is a sub-threshold bias diffusing through shared memory) and ask whether the observational signature survives. It does, quantitatively. This makes the point that the interference signature is **substrate-independent**, which is good news for neuromorphic/multi-agent design, and a constructive caution for causal inference in tissue.

**This is analogy, not homology:** a model organism for a mechanism, one abstraction beyond a cell culture. It makes no claim about ion channels, astrocytes, or real cortex.

## How it works

One condition is many bursts. Each burst starts at a random source; every agent is armed by the
fast channel and fires at the next tick its slow-channel phase is receptive. Synchrony against
distance is then measured from the fire times, and the wavelength is read off that curve. Every
box names a function in `ephaptic_sim.py`.

```mermaid
flowchart TD
    IN["inputs: Array lattice, f_khz, v_ax, v_slow, n_bursts, seed"] --> RC["run_condition: RandomState(seed) samples n_bursts source points"]
    RC -->|"one call per burst"| SB["simulate_burst"]
    SB --> FA["fast channel: arm time d / v_ax"]
    SB --> SL["slow channel: phase offset d / v_slow, or zero when slow_on=False"]
    FA --> FI["step in dt ticks: fire when armed and cos(2 pi f (t - t0)) > recept, or when armed if slow_on=False; add jitter"]
    SL --> FI
    FI -->|"list of fire-time arrays, one per burst"| SV["synchrony_vs_distance: pairs firing within 2 ms, by distance bin, minus baseline"]
    SV --> AN["analyze: _fit_exp and fit_wavelength on the curve"]
    AN --> OUT["measured lam, resolved, rebound_frac, snr"]
```

The prediction `1/[f(1/v_ep - 1/v_ax)]` appears only in `run.py` (`pred_lambda`, `PRED_SLOPE`),
where it is plotted next to the measurement. M6 takes the fire times down a different branch; see
[Architecture](#architecture).

## Status

Research artifact. This code reproduces the preprint *The Second Wire Is Substrate-Independent* (Zenodo, published 2026-07-16; see [Citation](#citation)). The repository has one commit (`c98cc5c`) and is not under active development. Not peer-reviewed.

Re-checked 2026-10-22 from a fresh clone: `python run.py` completed and reproduced `results.json` (every value matched to 13 or more significant digits, apart from the run time `elapsed_s`) and all five figures, which were visually identical to the committed ones. The PNG bytes differ because of renderer and font versions.

## Results at a glance

| Test | Result |
|---|---|
| **M1** - ripple exists | synchrony rings with distance; λ = 2.48 mm measured vs. 2.30 predicted (40 Hz) |
| **M3** - `λ ∝ 1/f` (decisive) | fitted slope 0.098 vs. 0.092 predicted, intercept ≈ 0, R² = 0.99 (5 of 8 frequencies resolved inside the array) |
| **M4** - ablation | slow channel off → ripple collapses (rebound 0.18 → 0.01) |
| **M5** - identifiability | wavelength set by the speed difference; vanishes as v_ep → v_ax |
| **M6** - generative | field on → two edge bands (contrast +0.96); field off → central blob (−0.62) |

The wavelength is **measured** from the simulated spike trains; no line of code computes `λ = 1/[f(1/v_ep − 1/v_ax)]`.

Where each number comes from: every value in the table is a field of [`results.json`](results.json)
under its experiment's key (`M1`, `M3`, `M4`, `M5`, `M6`; for example `M3.slope_meas`, `M3.r2`,
`M4.on.rebound_frac`, `M6.contrast_on`), written by `python run.py`, which also draws the matching
figure in [`figs/`](figs/) (`M1_ripple.png`, `M3_scaling.png`, `M4_ablation.png`,
`M5_speeddiff.png`, `M6_anisotropy.png`). The preprint that reports them is archived under the
concept DOI [10.5281/zenodo.21386649](https://doi.org/10.5281/zenodo.21386649).

![M3: measured wavelength against 1/f. Five resolved points lie on a fitted line of slope 0.097, R squared 0.99, close to the dotted prediction of slope 0.092; three unresolved points are marked with crosses](figs/M3_scaling.png)

![M1: baseline-corrected synchrony against pairwise distance at 40 Hz, with an exponential plus cosine fit; measured wavelength 2.48 mm, predicted 2.30 mm](figs/M1_ripple.png)

## Install

```bash
git clone https://github.com/saluca-labs/ephaptic-shi-testbed
cd ephaptic-shi-testbed
python -m venv .venv && . .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Dependencies are `numpy`, `scipy` and `matplotlib` (floors in `requirements.txt`). Tested 2026-10-22 with Python 3.12.10, numpy 2.5.4, scipy 1.18.1 and matplotlib 3.11.2 on Windows 11. CPU only.

## Quickstart

```bash
python run.py
```

Regenerates every figure (`figs/`) and `results.json`. `results.json` records 87.3 s for the original run; the 2026-10-22 check run took 210 s on a different machine. Deterministic: fixed numpy seeds, no wall-clock randomness. The run prints one line per condition, ending (real output, 2026-10-22):

```text
[M3] SLOPE meas=0.0975  pred=0.0919  intercept=-0.041  R2=0.991  (n=5)
[M4] ON rebound=0.18 snr=1.08 resolved=True | OFF rebound=0.01 snr=2.01 resolved=False
[M5] wavelength tracks the speed difference; 6 high-v_slow pts show the ripple vanishing
[M6] edge-center contrast  ON=+0.963 (edge bands)  OFF=-0.625 (central blob)

DONE in 210.2s -> figs/ and results.json
```

Running it overwrites the committed `figs/*.png` and `results.json` in place; `git diff results.json` then shows only last-digit float differences and `elapsed_s`.

## Usage

Run one condition from Python instead of the full suite (the M1 setup, about 6 s):

```python
from ephaptic_sim import Array, run_condition, synchrony_vs_distance, analyze

arr = Array(width_mm=4.0, height_mm=2.0, nx=40, ny=20)
fires = run_condition(arr, 0.040, v_ax=0.62, v_slow=0.08, n_bursts=300, seed=1)
centers, p_corr, _ = synchrony_vs_distance(arr, fires, nbins=45)
a = analyze(centers, p_corr)
print(f"lambda={a['lam']:.3f} mm  resolved={a['resolved']}  rebound={a['rebound_frac']:.2f}")
```

Real output, 2026-10-22:

```text
lambda=2.484 mm  resolved=True  rebound=0.20
```

Frequencies are in kHz (0.040 = 40 Hz) and speeds in mm/ms. `run_condition` also takes `slow_on=False` (the M4 ablation) and `static=True` (the static fixed-wavelength control generator, a stand-in for "Mexican hat" models, defined in `simulate_burst_static` but not called by `run.py`). `analyze` returns the measured wavelength `lam`, `resolved`, `rebound_frac`, `snr` and fit statistics; see its docstring.

## Architecture

- `ephaptic_sim.py`: the two-channel simulator (`Array`, `simulate_burst`, `run_condition`) and the measurement stage (`synchrony_vs_distance`, `fit_wavelength`, `analyze`). Channel speeds are inputs; the wavelength is an output.
- `run.py`: experiments M1, M3, M4, M5 and M6 → `figs/` + `results.json`. M2 in the spec is the wavelength-extraction step used inside the others, so it has no figure of its own.
- `testbed-spec.md`: the pre-registered experimental design
- `results.json`: machine-readable results
- `figs/`: the five figures
- `paper/`: the preprint (`.md` and `.pdf`)
- `article-1-substrate-independence.md`, `article-2-results.md`: the companion essays

How `run.py` uses the simulator. Each experiment calls `run_condition` with its own array,
frequencies, speeds and seed. M1, M3, M4 and M5 measure through `analyze`; M6 instead ranks agents
by coherence and compares where the survivors sit. The `__main__` block runs M1, M3, M4, M5 and M6
in that order, then writes the collected `RESULTS` dict to `results.json`.

```mermaid
sequenceDiagram
    participant M as run.py M1, M3, M4, M5
    participant M6 as run.py M6
    participant RC as ephaptic_sim.run_condition
    participant SB as ephaptic_sim.simulate_burst
    participant SV as ephaptic_sim.synchrony_vs_distance
    participant AN as ephaptic_sim.analyze
    M->>RC: array, f, v_ax, v_slow, n_bursts, seed, slow_on
    loop each burst
        RC->>SB: source point, per-burst RandomState
        SB-->>RC: fire time per agent
    end
    RC-->>M: list of fire-time arrays
    M->>SV: fire times
    SV-->>M: distance bins, baseline-corrected synchrony
    M->>AN: synchrony curve
    AN-->>M: lam, resolved, rebound_frac, snr, model
    Note over M: plot against pred_lambda, write figs/*.png and RESULTS
    M6->>RC: slow_on True, then False
    RC-->>M6: fire times
    Note over M6: coherence_score, prune_and_map, banding_index, then figs/M6_anisotropy.png and RESULTS
```

| Experiment | Array | Frequency | Varied | Seed |
|---|---|---|---|---|
| M1 | 4x2 mm, 40x20 | 40 Hz | nothing | 1 |
| M3 | 6x4 mm, 48x32 | 20 to 55 Hz in 5 Hz steps | frequency; slope of lam on 1/f by least squares | 3 |
| M4 | 6x4 mm, 48x32 | 40 Hz | `slow_on` True vs False | 3 |
| M5 | 6x4 mm, 48x32 | 40 Hz | `v_slow` 0.06 to 0.62 mm/ms | 7 |
| M6 | 4x2 mm, 40x20 | 40 Hz | `slow_on` True vs False | 5 |

`simulate_burst_static` (the fixed-wavelength control, reached with `run_condition(..., static=True)`)
is defined but not called by `run.py`.

## Citation

Ruvalcaba, C., & Saluca Agentic AI Research Team (2026). *The Second Wire Is Substrate-Independent: A Neuron-Free Testbed for Ephaptic-Axonal Interference.* Zenodo. https://doi.org/10.5281/zenodo.21386649

That is the concept DOI, which always resolves to the latest version. Machine-readable metadata is in [CITATION.cff](CITATION.cff).

## License

Split by path, declared file by file in [`REUSE.toml`](REUSE.toml) ([REUSE](https://reuse.software)
layout; the licence texts are in [`LICENSES/`](LICENSES/)):

- **Code and repository docs** (`ephaptic_sim.py`, `run.py`, `requirements.txt`, README, AGENTS.md,
  llms.txt, `docs/`): **PolyForm-Noncommercial-1.0.0**, see [LICENSE](LICENSE): free to read, run,
  modify, and share for noncommercial purposes; commercial use requires a separate license from
  Saluca LLC. GitHub shows this licence as "Other" because it does not auto-detect PolyForm licences.
- **Paper, figures, data and research text** (`paper/`, `figs/`, `results.json`, the two
  `article-*.md` files, `testbed-spec.md`): **CC-BY-NC-4.0**, the licence of the Zenodo record.

## Links

- Preprint record: https://doi.org/10.5281/zenodo.21386649 (PDF also in [paper/](paper/))
- Source paper: Rebbin et al., bioRxiv 2025, https://doi.org/10.1101/2025.11.03.686361
- Pre-registered design: [testbed-spec.md](testbed-spec.md)
- Every document, grouped by intent: [docs/README.md](docs/README.md)

## Disclosure

Produced by a human-directed agentic AI research system (the Saluca Agentic AI Research Team). The human author originated the question, made all decisions, and is solely accountable for every claim. Not peer-reviewed.

_Last updated: 2026-10-22_
