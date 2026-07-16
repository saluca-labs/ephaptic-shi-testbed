# Ephaptic-Analog Testbed

A neuron-free testbed for **two-channel, two-speed interference** — the mechanism Rebbin et al. (bioRxiv 2025, [10.1101/2025.11.03.686361](https://doi.org/10.1101/2025.11.03.686361)) propose for ephaptic-axonal shaping of neural self-organization.

We build the motif in a substrate with **no neurons, no ions, and no ephaptic physics** — a mesh of software agents in which the fast channel is directed message passing and the slow channel is a sub-threshold bias diffusing through shared memory — and ask whether the observational signature survives. It does, quantitatively. This makes the point that the interference signature is **substrate-independent** — which is good news for neuromorphic/multi-agent design, and a constructive caution for causal inference in tissue.

**This is analogy, not homology** — a model organism for a mechanism, one abstraction beyond a cell culture. It makes no claim about ion channels, astrocytes, or real cortex.

## Results at a glance

| Test | Result |
|---|---|
| **M1** — ripple exists | synchrony rings with distance; λ = 2.48 mm measured vs. 2.30 predicted (40 Hz) |
| **M3** — `λ ∝ 1/f` (decisive) | fitted slope 0.098 vs. 0.092 predicted, intercept ≈ 0, R² = 0.99 |
| **M4** — ablation | slow channel off → ripple collapses (rebound 0.18 → 0.01) |
| **M5** — identifiability | wavelength set by the speed difference; vanishes as v_ep → v_ax |
| **M6** — generative | field on → two edge bands (contrast +0.96); field off → central blob (−0.62) |

The wavelength is **measured** from the simulated spike trains — no line of code computes `λ = 1/[f(1/v_ep − 1/v_ax)]`.

## Reproduce

```bash
pip install -r requirements.txt
python run.py
```

Regenerates every figure (`figs/`) and `results.json` in ~80 s. Deterministic — no wall-clock randomness.

## Layout

- `ephaptic_sim.py` — the two-channel simulator and analysis functions
- `run.py` — experiments M1–M6 → `figs/` + `results.json`
- `testbed-spec.md` — the pre-registered experimental design
- `results.json` — machine-readable results
- `figs/` — the five figures
- `paper/` — the preprint (`.md` and `.pdf`)
- `article-1-substrate-independence.md`, `article-2-results.md` — the companion essays

## Citation

Ruvalcaba, C., & Saluca Agentic AI Research Team (2026). *The Second Wire Is Substrate-Independent: A Neuron-Free Testbed for Ephaptic-Axonal Interference.* Zenodo. `[DOI pending publication]`

## License

[PolyForm Noncommercial License 1.0.0](LICENSE) — free to read, run, modify, and share for noncommercial purposes; commercial use requires a separate license from Saluca LLC.

## Disclosure

Produced by a human-directed agentic AI research system (the Saluca Agentic AI Research Team). The human author originated the question, made all decisions, and is solely accountable for every claim. Not peer-reviewed.
