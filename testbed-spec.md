# Ephaptic-Analog Testbed — Design Specification

**Project:** two-channel interference in a memory-mesh multi-agent system
**Status:** design / pre-registration draft (v0.1, 2026-07-15)
**Purpose:** provide the falsifiable experimental core that Article 1 (thought-piece) proposes and Article 2 (results) reports.

---

## 0. One-paragraph statement

Rebbin et al. (bioRxiv 2025) argue that neural self-organization is shaped by *interference between two channels at two speeds*: fast axonal spikes (~0.62 mm/ms) and a slow, sub-threshold ephaptic phase advance (~0.08 mm/ms), producing a cosinusoidal, non-monotonic variation of synchrony with distance whose wavelength scales with oscillation frequency. This spec builds the **same two-channel motif in a system with no neurons and no ephaptic physics** — an agent mesh with (a) directed broker messaging as the fast channel and (b) diffusion of sub-threshold bias through a shared memory field as the slow channel — and asks whether the *signature* survives. A positive result claims **substrate-independence of the motif**, not homology with cortex. That distinction is load-bearing and is stated everywhere it matters.

---

## 1. The signature we are trying to reproduce (and what makes it non-trivial)

From the talk, the three observables that matter:

1. **Cosinusoidal synchrony-vs-distance.** Conditional firing probability (node *j* fires within ±2 ms of node *i*), corrected for baseline rate, is **non-monotonic** in distance — a decaying exponential plus a ripple. Gamma-band wavelength ≈ 2.8–2.9 mm on a 4×2 mm array.
2. **Frequency scaling.** Lower oscillation frequency → longer wavelength. Beta (15–25 Hz) ripples reach the array edge; gamma (30–50 Hz) ripples at ~2.9 mm. This is the decisive fingerprint.
3. **Generative anisotropy.** Synchrony-dependent pruning ("apoptosis" of low-coherence units) reproduces a two-band spatial structure that axonal-only single- and double-exponential kernels cannot.

**Why a positive result is not circular.** The obvious objection: "you coded a two-speed interference kernel, of course you get fringes." The design forecloses this three ways:

- **Emergence, not inscription.** Each agent acts on *local* rules only — its directed inbox and the field value in its immediate neighborhood. No agent, and no line of code, contains the global synchrony-vs-distance curve. The wavelength is a *measured* output, never a parameter.
- **The scaling law is the test, not the ripple.** A single ripple could be coincidence or an artifact. `λ ∝ 1/f` holding across a swept frequency range **without re-tuning any other parameter** is hard to fake with an alternative generator. That is the pre-registered pass/fail criterion.
- **The ablation is built in.** Setting slow-channel gain to zero must collapse the ripple to monotonic decay. If it doesn't, the ripple came from something else and the result is negative — reported as such.

---

## 2. Analytic backbone (so the prediction is stated before we simulate)

Treat a source unit firing at phase 0 of an oscillation at frequency `f`. Its influence reaches a unit at distance `d` by two channels with propagation speeds `v_ax` (fast) and `v_ep` (slow). The channels arrive with a relative delay, so the phase they carry at distance `d` differs by

```
Δφ(d) = 2π f d (1/v_ep − 1/v_ax)
```

Temporal correlation (synchrony) peaks where the two channels are in phase, `Δφ = 2πn`, giving a characteristic wavelength

```
λ = 1 / [ f (1/v_ep − 1/v_ax) ]
```

**Sanity check against the paper's parameters.** With `v_ep = 0.08`, `v_ax = 0.62` mm/ms, `1/v_ep − 1/v_ax ≈ 10.9 ms/mm`:
- gamma `f = 40 Hz = 0.040 /ms` → `λ ≈ 2.3 mm`
- beta `f = 20 Hz` → `λ ≈ 4.6 mm`

Same order as their observed 2.8–2.9 mm (gamma) and edge-reaching beta; the offset reflects kernel/reference-frame details we do **not** claim to reproduce exactly. **We test the scaling `λ ∝ 1/f`, not the absolute value.** The absolute number is substrate-specific; the scaling law is the substrate-independent claim.

This formula is the pre-registered prediction. Article 2 stands or falls on whether the *simulated, emergent* wavelengths obey it.

---

## 3. SHI mapping

| Rebbin's system | Testbed analog | Notes |
|---|---|---|
| Neuron | Agent / node | ~1000–4000 units on a 2-D lattice mirroring the 4×2 mm HDMEA aspect ratio |
| Position on array | Lattice coordinate `(x,y)` | Euclidean distance is the independent variable |
| Axonal spike (fast, directed, super-threshold) | **Broker directed message** | delivered with delay `d / v_ax_sim`; determines *whether* a downstream unit fires |
| Ephaptic phase advance (slow, undirected, sub-threshold) | **Bias diffusing through the shared memory field** | delivered with delay `d / v_ep_sim`, `v_ep_sim ≪ v_ax_sim`; shifts a unit's firing *phase*, never its firing decision |
| Gamma oscillation | Intrinsic per-agent activity clock at frequency `f` | swept across a beta/gamma analog range |
| Synchrony (conditional firing prob.) | Same estimator, ±window on the sim clock | baseline-corrected identically |
| Synchrony-dependent apoptosis | Coherence-scored pruning of agents | prune lowest-coherence units until count hits target |
| Field decay length (short) | Neighborhood radius / kernel decay of the field write | short-range, as in tissue |

**Distance metric — decision.** Use an explicit synthetic 2-D lattice coordinate, **not** TKHR topic-ring distance, for the primary experiment. Reason: we need a clean, controllable metric to test `λ ∝ 1/f`; topic-ring distance is semantically meaningful but not calibrated in units. (A secondary, exploratory run over topic-ring distance is noted in §7 as future work — that is where the "does this say anything about *real* agent coordination" question lives, and it must not contaminate the clean physics test.)

---

## 4. Mechanics (the local rules)

Each simulation tick, for every agent `i`:

1. **Intrinsic clock.** `i` has phase `θ_i(t)` advancing at `2πf`. It is *eligible* to fire near its phase peak.
2. **Slow-channel read (sub-threshold).** `i` reads the shared field in its neighborhood: a sum over recent firings `j`, each contributing `A · exp(−d_ij / ℓ) · cos(2πf (t − d_ij/v_ep_sim − t_j))`, weight `A`, decay length `ℓ`. This **nudges `θ_i`** (a Kuramoto-style phase pull), it does **not** add to a firing threshold.
3. **Fast-channel read (super-threshold).** Directed messages from wired predecessors `j`, arriving at `t_j + d_ij/v_ax_sim`, add to `i`'s activation. If activation crosses threshold near the eligible phase, `i` **fires**.
4. **On firing.** `i` (a) emits directed messages to its wired successors (fast channel) and (b) writes a decaying, phase-stamped perturbation into the shared field (slow channel). Records spike time `t_i`.

Key invariant enforced in code and asserted in tests: **the slow channel can only move phase, never cause or prevent a spike.** If that invariant leaks, the ablation test is meaningless. Automated assertion: with fast channel disabled, total spike count must be invariant to slow-channel gain.

---

## 5. Measurements

| # | Quantity | Method | Pass criterion |
|---|---|---|---|
| M1 | Synchrony(distance) | baseline-corrected conditional firing prob. vs. Euclidean `d`, binned | visible non-monotonic ripple over exponential decay |
| M2 | Emergent wavelength `λ(f)` | fit residual-from-exponential to a cosine; extract `λ` | — |
| M3 | **Scaling law** | regress `λ` against `1/f` across ≥6 swept frequencies | slope matches §2 within CI; `R²` high; **primary result** |
| M4 | Ablation | rerun with slow-channel gain = 0 | ripple vanishes → monotonic decay (validates M1–M3 are field-driven) |
| M5 | Alt-generator control | axonal-only with two "cell types" (short-range excite + long-range inhibit) tuned to match M1 at one `f` | must **fail** to reproduce M3 scaling across `f` — this is the Mexican-hat identifiability test |
| M6 | Generative anisotropy | coherence-scored pruning; 2-D KS vs. a banded target | banding emerges with field on, not off |

**M5 is the intellectually critical control.** If a static two-cell-type kernel, tuned to match the ripple at one frequency, *also* reproduces `λ ∝ 1/f`, then the two-speed mechanism is not uniquely identified even in silico — a strong, honest, publishable negative that directly informs the biology. If it fails to scale (expected), that is positive evidence that the *dynamic two-speed* mechanism is doing distinct work.

---

## 6. Pre-registered outcomes (fill in Article 2)

- **Confirm:** M3 holds, M4 collapses it, M5 control fails to scale → "the two-channel interference signature is substrate-independent; the frequency-scaling fingerprint distinguishes it from static short-range/long-range kernels *in silico*."
- **Partial:** ripple present but scaling weak/noisy → "necessary conditions unclear; motif reproduces the static signature but not the dynamic fingerprint."
- **Refute:** no ripple, or M5 control *also* scales → "the signature is not diagnostic of a two-speed mechanism; observing it in tissue does not identify ephaptic causation" — the sharpest possible contribution to the identifiability debate.

Every branch is a real result. There is no outcome that wastes the run. Register this table before running.

---

## 7. Explicitly out of scope (state in both articles)

- **No claim about cortex.** Reproducing the signature in silicon says the *motif's logic is sufficient* to generate it; it says nothing about whether ephaptic physics causes it in tissue. Analogy, not homology.
- **Topic-ring distance run** (agents positioned by semantic proximity rather than synthetic lattice) is deferred to future work; it is where the "can coordination emerge from shared-memory proximity instead of orchestration" question lives — a Nexus-relevant question, kept separate from the clean physics test.
- **Biophysical realism** (cell types, inhibition, glia/astrocyte amplification) is not modeled. This is a motif test, one abstraction further out than Rebbin's culture is from a brain — and that extra abstraction is the whole point, not a shortcoming, *provided we never oversell it.*

---

## 8. Minimal build

- Single-process discrete-event sim; agents as lightweight objects, not full SHI runtime (the SHI mapping is conceptual/architectural — we are testing the *motif*, and a faithful minimal sim is more rigorous and more reproducible than bolting onto production infra).
- Deterministic seeds; no wall-clock randomness.
- Outputs: per-run spike raster, synchrony-vs-distance curves, `λ(f)` table, ablation/control overlays, KS anisotropy maps — these ARE the Article 2 figures.
- Everything scripted end-to-end so a skeptic can reproduce the frequency-scaling plot from one command.
