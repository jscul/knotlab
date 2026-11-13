# Proved rates for the law's reach along a ray: pre-registration

Epic `PROVED-RATE-20261113-001` (`BOND-DEPTH-20261112-001` direction 1; G17, with G1), 2026-11-13, at the coordinator's go-ahead;
the first study computed by Codex from a frozen spec (`codex_spec.md`), as the owner agreed. Frozen before the run. The canonical
K1–K3 test is unchanged.

## The question

`BOND-DEPTH-20261112-001` found the least ray bond L_ray(s) exactly bounded in 204 one-definition limit-only families, rising
steadily within depth 30 in 240, flat within 30 without proof in 163. Can the long-run behaviour be proved: a growth rate when the
reach grows, boundedness at every depth when it does not?

## In standard terms

The minimum cycle mean of a finite weighted state graph of a min-plus recurrence, as the liminf rate of a fixed-length shortest
path, and a sufficient test for boundedness at every length.

## Method (frozen in `codex_spec.md`; computed by Codex)

The whole reachable graph of the ray DP (nodes (F, G), middle transitions with cost |W|), up to two million nodes; trimmed to nodes
reachable from a start and co-reachable to an accepting closing; λ = the minimum over its strongly connected components of the
minimum cycle mean (Karp 1978), exact; `bounded_all` when some trimmed node's empty-W cycle closes acceptingly at every node. Gate:
L_ray(s) recomputed from the graph equals BOND-DEPTH's records.

## Settled or known (stated, not tested)

- **What λ proves.** On a complete graph every walk is a simple path plus cycles, so L_ray(s) ≥ λ(s − |V|): λ > 0 proves linear
  growth of the ray bond at every depth. λ is the liminf of L_ray(s)/s, not always a limit: lengths in some residues may be forced
  through other components (the advisor's). A capped graph gives only λ_partial ≥ λ.
- **What bounded proves.** λ = 0 alone shows boundedness along an arithmetic progression of depths; `bounded_all` proves it at every
  depth from the empty-W cycle's start on. Zero-mean cycles are exactly cycles of the empty-W map.
- **What a ray rate says about the true bond.** Ray bonds are bonds, so L_ray ≥ the true least bond: boundedness transfers to the
  true bond; λ_ray > 0 shows only that no ray-shaped bond is shorter than λ s, and nothing about bonds through side branches.
- **Known.** Minimum cycle means (Karp 1978), min-plus eventual periodicity (Cohen, Dubois, Quadrat and Viot 1983; Heidergott,
  Olsder and van der Woude 2006). Ours: their use for least bonds in nested NAE patterns.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gate: L_ray(s) recomputed from the graph equals the records for every family whose graph was built. | any mismatch |
| P1 | **The graphs close.** At least 80% of the 653 read families have a complete graph (under two million nodes). | below 80% |
| P2 | **Depth 30 saw the real rate.** Of the "rising" families with complete graphs, at least 90% have λ > 0. | below 90% |
| P3 | **And the real flatness.** Of the "flat" families with complete graphs, at least 90% are `bounded_all`. | below 90% |
| — | Reported: λ's distribution, graph sizes, families bounded only along progressions, the "capped" families' outcomes. | — |

The advisor model reviewed the draft cold (`advisor_review_answer.md`): it showed λ is a liminf and a lower-bound rate, that λ = 0
alone shows boundedness only along a progression, that a capped graph's λ is one-sided, and what a ray rate shows about the true
bond. All adopted.

## Hand-off and stop rule

One spec out, one result back (`codex exec`, gpt-6.1-sol at maximum reasoning, fallback gpt-6-astra at xhigh; workspace-write
sandbox; one memory-capped unit; writes only in the study's `codex/` folder; never commits). The thread checks the output,
interprets, commits and reports; a hand-off to the referee thread. Registered in `docs/LONG_RUNNING.md`.
