# The Brain's Second Wire, and Why You Can Build It Without a Brain

*On ephaptic-axonal interference, and what a memory-mesh of software agents can and cannot tell us about it.*

*Draft v0.1 — 2026-07-15. Public thought-piece. Companion experimental spec: `testbed-spec.md`.*

---

## The wire we agreed to ignore

For sixty years the working picture of a brain has been a graph: neurons are nodes, synapses are edges, and computation is what happens when weighted signals travel the edges. Connectionism, spike-timing-dependent plasticity, the whole apparatus of modern computational neuroscience, rests on the idea that **the wire is the synapse** and everything else is noise.

It is a productive picture. It is also incomplete in a specific, physical way: neurons are not only wired to each other, they are *immersed* in each other. Every spike perturbs the extracellular electric field, and that field, however faintly, biases the neurons around it. This is **ephaptic coupling** — influence with no synapse, no axon, no directed connection at all. It is usually dismissed, and for a defensible reason: at the level of one neuron nudging its neighbor, the effect is tiny and short-range. The field decays fast. One-to-one, it rounds to zero.

A recent talk from Daniel Rebbin (working with Wesley Clawson, Michael Levin, Casper Hesp, and Dimitris Pinotsis, at Tufts' Allen Discovery Center) makes the case that rounding it to zero is a mistake — and does so with an unusually crisp, falsifiable argument. This piece is about that argument, and about a second claim I want to layer on top of it: that its most important feature is **substrate-independent**, and that this is simultaneously good news for anyone building computers and slightly awkward news for the biology.

## Two wires, two speeds

Rebbin's move is to stop treating the field as background and start treating it as a *second channel* that runs in parallel with the synaptic one — crucially, **at a different speed.**

- The synaptic-axonal channel is fast: super-threshold spikes cross a culture at roughly **0.62 mm/ms**, the familiar axonal conduction speed. It decides *whether* a downstream neuron fires.
- The ephaptic channel is slow: a sub-threshold phase advance creeps along at about **0.08 mm/ms** — nearly an order of magnitude slower. It doesn't decide whether a neuron fires; it nudges *when.*

Two signals leave the same source. One sprints, one strolls. At any given distance they arrive carrying different phases of the ongoing oscillation, and — like any two waves at different speeds — they *interfere.* Where they arrive in phase, downstream neurons synchronize; where they arrive out of phase, they don't. The consequence is a prediction with teeth: **synchrony should not fall off smoothly with distance. It should ripple.**

And it does. On dense multi-electrode arrays of developing rat cortex, Rebbin finds exactly that non-monotonic, cosine-like variation of synchrony with distance — a bump of extra correlation at a characteristic 2–3 mm, right where the two-speed arithmetic says it should be. The single most convincing detail is that the ripple's wavelength *tracks frequency the right way*: slower oscillations (beta) produce longer wavelengths than faster ones (gamma). That is not the kind of thing you get from a fudge factor. It is the fingerprint of genuine interference.

There is a second half, about development rather than function: if you let the neurons that fail to synchronize die off — activity-dependent apoptosis, which really happens — the survivors settle into a banded spatial pattern that the standard "just synapses" models, even generous two-exponential ones, cannot reproduce. The field doesn't just modulate activity; it helps decide *who gets wired at all.*

It is a good argument. It is also, as the best arguments are, honestly incomplete — and the room said so.

## The question from the back of the room

In the Q&A, someone named the weakness precisely. The combined influence — short-range excitation, long-range suppression, a bump in the middle — has a shape neuroscientists know well: a **Mexican hat.** And Mexican hats are cheap. Pattern-formation theory has produced them for decades from ingredients that have nothing to do with ephaptic fields — for instance, two populations of neurons with different connection ranges. So: is the two-speed interference model the *only* thing that makes this ripple, or merely *one* thing?

Rebbin conceded the point. His defense is parsimony — he'd rather not assume two cell types with two hand-tuned decay lengths, and the specific two-exponential model he tested failed to reproduce the structure. That is a reasonable defense. It is not a proof. The signature, on its own, does not uniquely identify its cause. Hold onto that, because it is where the software comes in — from an unexpected side.

## Now take the neurons away

Here is the observation this piece exists to make. **Nothing in the two-speed argument is about neurons.** Strip it to its logic and you have:

1. a population of units at positions in space,
2. a fast, *directed* channel that carries decisions between specific units, and
3. a slow, *undirected* channel — a shared field every unit is immersed in — that carries timing bias to everyone nearby.

That is not a description of cortex. It is, almost line for line, a description of a certain kind of distributed software system: a mesh of autonomous agents that (a) send each other explicit messages through a broker — fast, point-to-point, the "axonal" channel — and (b) all read and write a common memory substrate that subtly biases what each does next — slow, ambient, the "ephaptic" channel. I've spent a while building exactly that kind of system for entirely unrelated reasons (agent coordination, persistent memory), and I did not set out to model a brain. But the motif is the same motif, and that is the point.

So the question becomes empirical and, pleasingly, *cheap to ask*: if you build the two-channel, two-speed motif in a substrate with **no neurons, no ions, no ephaptic physics whatsoever** — just messages and shared memory — do you get the ripple? Do you get the frequency scaling? The companion spec (`testbed-spec.md`) lays out the experiment in pre-registered detail; the short version is that the fast channel becomes directed broker messages delivered with a distance-proportional delay, the slow channel becomes a bias that diffuses through shared memory at a much lower speed and can only shift a unit's timing (never trigger it), and we measure synchrony against distance exactly as Rebbin does — then sweep the oscillation frequency and check whether the emergent wavelength obeys `λ ∝ 1/f`.

Two guardrails make this an experiment rather than a metaphor. First, **the wavelength is never a parameter** — each agent follows purely local rules, and the synchrony-vs-distance curve is a *measured output* no line of code contains. Second, **the frequency-scaling law is the pass/fail criterion**, not the ripple itself; a lone ripple proves little, but `λ ∝ 1/f` holding across a swept range without re-tuning is hard to counterfeit.

## Why the answer matters either way — and cuts both ways

Suppose it works: the silicon mesh ripples, and the wavelength scales with frequency just as the arithmetic predicts. What have we learned?

**Good news, for builders.** The two-channel interference motif is not a biological quirk. It is a *substrate-independent computational primitive* — a way that any system combining fast directed signaling with slow ambient coupling will spontaneously organize itself into distance-structured synchrony. Neuromorphic engineers have only just begun to exploit the analog "backplane" of a computing medium as anything other than a nuisance; this says the backplane can do structured work, and tells you the knob — the speed ratio and the oscillation frequency — that sets the structure. That is a design principle you can build on.

**Awkward news, for the biology — and this is the part I think is worth the article.** If a system with no ephaptic physics reproduces the signature *and its frequency scaling*, then the signature is even less diagnostic than the Q&A feared. The room worried that a static two-cell-type kernel could fake the ripple. Substrate-independence says something stronger: the ripple and its scaling are properties of the *abstract motif*, realizable in media that share none of cortex's mechanisms. Which means observing the ripple in tissue — even with the frequency scaling — **does not, by itself, license the conclusion that ephaptic coupling caused it.** It is consistent with ephaptic coupling. It is also consistent with anything else that instantiates two-channels-at-two-speeds.

This is not a debunking. Rebbin's model may well be the right account of what happens in that dish; the developmental, apoptotic half of his story is mechanistically specific in a way that the software analog deliberately does not touch. The point is narrower and, I think, useful: **the observational signature and the causal mechanism have to be argued for separately, because the signature travels.** The experiment that would actually pin it in tissue is the one Rebbin's own group named as future work — not observing the field, but *perturbing* it, driving cultures with patterned stimulation during the critical days and watching the bands move. In silicon, that perturbation is a config flag; in the incubator it is a year of hard work. That asymmetry is exactly why the two substrates are worth studying together: the model organism you can toggle sharpens the questions you take back to the one you can't.

## What I am and am not claiming

I am not claiming a mesh of software agents is a brain, or a model of one. It shares no biology with cortex, and a positive result would say nothing about ion channels or astrocytes or dendrites. It is a **model organism for a mechanism** — one abstraction further out than a cell culture is from a living brain — and its entire value is that it is fully observable and fully perturbable, the two things a developing brain is not.

What I *am* claiming is that Rebbin et al. have found something whose most interesting property is that it isn't only theirs. The second wire in the brain — the field, the thing we agreed to ignore — turns out to be an instance of a pattern general enough to build out of message queues and shared memory. That generality is a gift to the people building the next generation of computers, and a caution to the people trying to prove what the brain is doing. Both halves are worth saying out loud.

The experiment is specified. The result — whichever way it falls — is the sequel.

## Postscript: the result is in

Between drafting this and posting it, the testbed was built and run. The short version: the neuron-free mesh **does** ripple; its wavelength scales as `λ ∝ 1/f` with a fitted slope of 0.098 against a predicted 0.092 (R² = 0.99); ablating the slow channel collapses the ripple; and the wavelength tracks the two conduction speeds exactly as the interference formula demands. The signature is substrate-independent — and the double edge above is therefore not hypothetical but confirmed: a system with no ephaptic physics reproduces the fingerprint, scaling and all. Part 2 reports the numbers, the figures, and the limitations in full.

---

*Part 2 reports the testbed results. If you work on ephaptic coupling, neuromorphic architectures, or multi-agent systems and want to poke holes in the design, that is exactly the feedback this is looking for.*
