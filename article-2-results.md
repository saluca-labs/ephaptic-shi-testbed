# The Ripple Travels: Two-Channel Interference in a Substrate With No Neurons

*Part 2 of the ephaptic / substrate-independence pair. Reports the testbed proposed in Part 1. Draft v0.1 — 2026-07-15.*

> Editorial rule honored here: every number below is a direct output of the simulator in `ephaptic_sim.py` / `run.py`, reproducible with one command. Figures are in `figs/`. Where a result is weak or a metric is noisy, it is said so. Nothing is inscribed — the wavelength is measured, never a parameter (see Part 1 and the `testbed-spec.md` anti-circularity contract).

---

## The claim under test

Part 1 argued that Rebbin et al.'s two-speed ephaptic-axonal interference motif is **substrate-independent**: build it out of a fast directed channel and a slow shared-field channel — with no neurons, no ions, no ephaptic physics — and its measurable signature should survive. The signature has a decisive fingerprint: the synchrony-vs-distance ripple should have a wavelength that scales as `λ ∝ 1/f`, with the constant of proportionality fixed by the two conduction speeds,

```
λ = 1 / [ f (1/v_ep − 1/v_ax) ]
```

We built the motif (fast channel = directed messages arriving at delay `d/v_ax`; slow channel = a sub-threshold phase bias arriving at `d/v_slow` that shifts *when* a unit fires, never *whether*), ran bursts from sources scattered across the array, and measured the baseline-corrected conditional firing probability against pairwise distance — exactly Rebbin's estimator. Speeds used throughout: `v_ax = 0.62`, `v_ep = 0.08` mm/ms, from the paper.

## M1 — the ripple is there

At 40 Hz on a faithful 4×2 mm array, synchrony does **not** decay smoothly with distance. It rings: a fast near-field falloff, a dip, and a rebound. Fitting an exponential-plus-cosine gives a **measured wavelength of 2.48 mm**, against a predicted **2.30 mm** — a 8% miss, on a quantity that appears nowhere in the code. *(Fig. M1)*

## M3 — the decisive fingerprint: λ ∝ 1/f

Sweeping the oscillation frequency from 20 to 55 Hz (on a 6×4 mm array — enlarged beyond the dish, an in-silico affordance, to resolve the longer wavelengths) and extracting the emergent wavelength at each:

| f (Hz) | 1/f (ms) | λ measured (mm) | λ predicted (mm) |
|---|---|---|---|
| 30 | 33.3 | 3.18 | 3.06 |
| 40 | 25.0 | 2.41 | 2.30 |
| 45 | 22.2 | 2.21 | 2.04 |
| 50 | 20.0 | 1.88 | 1.84 |
| 55 | 18.2 | 1.68 | 1.67 |

Regressing the resolved wavelengths against `1/f`: **measured slope 0.0975 vs. predicted 0.0919** (6% high), **intercept −0.04 mm** (theory demands zero), **R² = 0.991**. *(Fig. M3)* The 20 and 25 Hz points have predicted wavelengths that exceed the array and are correctly flagged **unresolved** rather than forced — the same ceiling Rebbin's dish hit for beta. The fingerprint holds, and it holds *quantitatively*, in a system with no biology in it.

## M4 — ablation: the ripple is field-driven

Turn the slow channel off (its gain to zero) and rerun at 40 Hz. The non-monotonic rebound — the ripple's signature — **collapses from 0.18 to 0.01**, leaving a clean monotonic decay. *(Fig. M4)* Whatever is making the ripple is the slow shared-field channel, not array geometry, wiring, or the measurement. This is the manipulation Rebbin's group can only aspire to in tissue (patterned stimulation over critical days); here it is a flag.

## M5 — identifiability: the wavelength is set by the speed *difference*

The sharpest objection from the paper's own Q&A was that the ripple resembles a "Mexican hat," which many *static*, frequency-free mechanisms (e.g. two cell types with short-range excitation and long-range inhibition) can also produce. So we tested whether the wavelength carries a signature no static kernel could: dependence on the conduction speeds. Fixing `f = 40 Hz` and sweeping `v_ep` toward `v_ax`, the resolved wavelengths sit on the prediction's identity line:

| v_ep (mm/ms) | λ measured (mm) | λ predicted (mm) |
|---|---|---|
| 0.06 | 1.68 | 1.66 |
| 0.07 | 2.14 | 1.97 |
| 0.09 | 2.79 | 2.63 |
| 0.10 | 3.12 | 2.98 |
| 0.11 | 3.40 | 3.34 |

As the two speeds converge, the **predicted wavelength diverges and the ripple vanishes** — six of the eleven `v_ep` values become unresolvable as `v_ep → v_ax`, exactly the limit where `1/v_ep − 1/v_ax → 0`. *(Fig. M5)*

Together, M3 and M5 pin it: the ripple's wavelength depends on **both** the oscillation frequency **and** the two conduction speeds, exactly as `λ = 1/[f(1/v_ep − 1/v_ax)]` demands. A static, fixed-length kernel has neither dependence by construction. In silico, the frequency-and-speed scaling *is* a fingerprint of two-speed interference specifically.

*(Honest caveat: the `resolved` gate is noisy near threshold — it drops the occasional accurate point, e.g. `v_ep = 0.08`, whose measured λ = 2.45 mm is fine. The trend and the vanishing are robust; the per-point flagging is not surgical.)*

## M6 — the developmental half: edge banding needs the field

Rebbin's second claim is generative: activity-dependent apoptosis, biased by the field, produces spatial structure. We scored each unit by its coherence with the rest, pruned the lowest half, and looked at the survivors. With the slow channel **on**, survivors form **two bands hugging the short edges with a depleted middle** — an edge-minus-center contrast of **+0.96** — the same "two vertical bands" the paper reports. With the field **off**, the survivors collapse to a single central blob (contrast **−0.62**). *(Fig. M6)* The anisotropy is a product of the field, not of pruning alone.

## What this does and does not establish

**Does:** the two-channel-at-two-speeds motif reproduces Rebbin's full observational signature — the ripple (M1), its `1/f` scaling (M3), its dependence on the speed difference (M5), and the field-dependent developmental banding (M6) — in a substrate with no neurons. The motif is therefore **substrate-independent**: the signature is a property of the abstract computation, realizable in message-passing and shared memory.

**The double edge, restated with the result in hand.** This is good news for neuromorphic and multi-agent design — the interference motif is a general primitive, and its two knobs (the speed ratio, the oscillation frequency) set the structure it produces. It is *cautionary* news for the biology's causal claim: because a neuron-free substrate reproduces the signature **and its frequency/speed scaling**, observing that signature in cortex — even with the scaling — does not by itself identify ephaptic coupling as the cause. It is consistent with ephaptic coupling; it is equally consistent with anything else that instantiates two channels at two speeds. The observational fingerprint and the causal mechanism have to be argued separately, because the fingerprint travels.

**Does not:** say anything about ion channels, astrocytes, or real cortex. This is a model organism for a *mechanism*, one abstraction beyond a cell culture. Its worth is that it is fully observable and fully perturbable — the two things a developing brain is not. Analogy, not homology.

## Limitations (stated, not buried)

- The generative model (M6) is phenomenological — pruning by a coherence score, not biophysical apoptosis. It reproduces the *geometry*, not the cell biology.
- The `resolved` wavelength gate is noisy near threshold (M3, M5); reported trends are robust, per-point flags are not.
- Wavelengths longer than the array are unmeasurable — the same limit the real dish has; we sidestep it in silico by enlarging the array, which biology cannot.
- The slow channel is posited, not derived. We test whether *positing* two channels at two speeds reproduces the signature — the claim of Part 1 — not whether such channels arise from something deeper.

## The experiment silicon can't do

Every affordance we used to sharpen the test — toggling the field, enlarging the array, tuning conduction speeds — is one biology lacks. The converse also holds: the experiment that would actually pin ephaptic *causation* in tissue is the one Rebbin's group named as future work — drive cultures with patterned stimulation during the critical days and watch the bands move ("shrink the Mexican hat by half"). In silicon that was a config change; in the incubator it is the real frontier. The two substrates are complementary: the toggleable model sharpens the questions; only the tissue answers them about brains.

---

*Reproduce: `python run.py` (≈80 s) regenerates every figure and `results.json`. Code and spec: `ephaptic_sim.py`, `run.py`, `testbed-spec.md`.*
