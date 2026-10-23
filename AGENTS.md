# AGENTS.md

Instructions for AI coding agents working in this repository.

## What this is

The reproduction harness for one preprint: a neuron-free simulation in which two channels at two
speeds produce a synchrony ripple whose wavelength scales as 1/f. It is not a library and not a
model of real tissue.

## Read in this order

1. `README.md`: results, the "How it works" diagram, and the Architecture sequence diagram.
2. `ephaptic_sim.py`: the simulator (`run_condition`, `simulate_burst`) and the measurement stage
   (`synchrony_vs_distance`, `analyze`, `fit_wavelength`).
3. `run.py`: experiments M1, M3, M4, M5 and M6, and where each figure and result is written.
4. `testbed-spec.md`: the pre-registered design the experiments answer to.
5. `docs/README.md`: the map of every other document.

## What you can and cannot see

- All the code and the committed results are here. There is no other repo and no network call.
- The archived preprint is on Zenodo (concept DOI 10.5281/zenodo.21386649); `paper/` holds the
  same text as Markdown and PDF.
- `simulate_burst_static` (the fixed-wavelength control generator) is in the code but no
  experiment in `run.py` calls it, so there is no committed result from it.

## The only numbers to trust

- Every result in the README table: `results.json`, under the keys `M1`, `M3`, `M4`, `M5`, `M6`
  (for example `M3.slope_meas`, `M3.r2`, `M4.on.rebound_frac`, `M6.contrast_on`).
- The channel speeds and the predicted slope: `results.json` `_meta` (`v_ax`, `v_slow`,
  `pred_slope`), set as `V_AX` and `V_SLOW` in `run.py`.
- Run time: `results.json` `_meta.elapsed_s` is the original run on its machine, not a benchmark.

## Quickstart

```bash
python run.py
```

## Setup

```bash
python -m venv .venv
. .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Python 3.10 or later; tested with 3.12. CPU only, no network access needed.

## Test

There is no unit test suite. The check is the full reproduction:

```bash
python run.py
git diff --stat
```

Passing looks like `DONE in <seconds>s -> figs/ and results.json` and a `results.json` diff limited to the last digits of floats and `elapsed_s`. Look at the five regenerated figures; they should be visually identical to the committed ones.

## Conventions

- Dependencies are numpy, scipy and matplotlib only. Do not add others.
- Determinism is part of the result: use `numpy.random.RandomState` with explicit seeds, never wall-clock or global random state.
- The simulator must not compute the predicted wavelength `1/[f(1/v_ep - 1/v_ax)]`; the wavelength is measured from spike trains. Only `run.py` may use the formula, for plotting the prediction.
- Units: frequency in kHz, distance in mm, time in ms, speed in mm/ms.
- If the call path between `run.py` and `ephaptic_sim.py` changes, update both README diagrams in the same change.
- No em-dashes in docs. Use a plain hyphen.

## Do not

- Edit `paper/` (the archived preprint), `testbed-spec.md` (the pre-registration) or the companion articles to match new results. A change in results is an erratum for the author to publish, not a silent edit.
- Commit a regenerated `results.json` or `figs/` unless the change in results is the point of the PR.
- Commit secrets, hostnames, internal paths or personal emails.

## Done means

`python run.py` completes, the results diff is explained in the PR, and README.md, llms.txt and CITATION.cff still describe the code accurately.
