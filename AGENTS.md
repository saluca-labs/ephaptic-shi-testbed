# AGENTS.md

Instructions for AI coding agents working in this repository.

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
- No em-dashes in docs. Use a plain hyphen.

## Do not

- Edit `paper/` (the archived preprint), `testbed-spec.md` (the pre-registration) or the companion articles to match new results. A change in results is an erratum for the author to publish, not a silent edit.
- Commit a regenerated `results.json` or `figs/` unless the change in results is the point of the PR.
- Commit secrets, hostnames, internal paths or personal emails.

## Done means

`python run.py` completes, the results diff is explained in the PR, and README.md, llms.txt and CITATION.cff still describe the code accurately.
