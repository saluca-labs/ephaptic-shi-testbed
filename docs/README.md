# Docs index

Every prose document in this repository, grouped by what you want to do. Paths are relative to the
repository root.

## Start here

- [`README.md`](../README.md): what the testbed is, the results table, how to run it, and two
  diagrams of the code path.
- [`AGENTS.md`](../AGENTS.md): orientation for AI agents working in the repo, the only numbers to
  trust, and what not to edit.

## The design, before the results

- [`testbed-spec.md`](../testbed-spec.md): the pre-registered design (v0.1, 2026-07-15). The
  signature to reproduce, the analytic prediction, the local rules, the measurements M1 to M6 and
  their pass and fail criteria, and what is out of scope.

## The results

- [`paper/ephaptic-shi-preprint.md`](../paper/ephaptic-shi-preprint.md) (also
  [PDF](../paper/ephaptic-shi-preprint.pdf)): the preprint this code reproduces. Methods, results for
  M1, M3, M4, M5 and M6, limitations. Archived under the concept DOI
  [10.5281/zenodo.21386649](https://doi.org/10.5281/zenodo.21386649).
- [`results.json`](../results.json) and [`figs/`](../figs/): the numbers and figures from the
  committed run of `python run.py`.

## The argument, for a general reader

- [`article-1-substrate-independence.md`](../article-1-substrate-independence.md): the thought-piece
  that proposes the test and says what a neuron-free result can and cannot show.
- [`article-2-results.md`](../article-2-results.md): the companion essay reporting M1 to M6 and the
  limitations.

The spec, the preprint and the two articles are archived as written. A change in results is an
erratum for the author to publish, not an edit to these files.
