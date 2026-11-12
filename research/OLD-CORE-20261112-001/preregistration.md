# The old core's own end: pre-registration

Epic `OLD-CORE-20261112-001` (sub-goal B170, from `LIFE-JUMPS-20261112-001` direction 1; G17, with G7), 2026-11-12, at the
coordinator's go-ahead. Frozen before the registered run. The canonical K1–K3 test is unchanged. Words as in the guide's glossary and
`RANDOM-FATES-20261112-001`; the **core** C_k is the knots whose three distinctions are all among the oldest k.

## The question

Growth that keeps adding distinctions ties a rising share of itself over its life, always in its oldest distinctions
(`LIFE-JUMPS-20261112-001`). Does it end when its oldest distinctions, read as a pattern by themselves, reach the end of uniform knots
(about 2.1 knots per distinction)? The weighting is each named process (A71); "typical" means typical under it.

## In standard terms

For grown random 3-uniform hypergraphs (each new edge either closes on uniform old vertices or brings one new vertex), is the first
non-2-colourable prefix of the vertex order a near-critical uniform random hypergraph, or does its degree structure, or its growth,
make it die below the uniform threshold?

## Prior work (bounded search, with the advisor model)

Known: the end of uniform random NAE-3-SAT and hypergraph 2-colouring near 2.1 (Achlioptas and Moore; Achlioptas, Chtcherba,
Istrate and Moore; Castellani, Napolano, Ricci-Tersenghi and Zecchina; Coja-Oghlan and Panagiotou; Ding, Sly and Sun for regular
patterns); degree heterogeneity lowers and regular degrees raise satisfiability thresholds (Cooper, Frieze and Sorkin for 2-SAT with
given degrees; Boufkhad, Dubois, Interian and Selman for regular k-SAT; Ansótegui, Bonet and Levy, and Friedrich et al. for
power-law SAT); grown random graphs differ from degree-matched static ones (Callaway, Hopcroft, Kleinberg, Newman and Strogatz 2001;
Bollobás, Janson and Riordan). Not found: the end of grown random NAE patterns, where in them it lives, and whether their dying part
is uniform-like, degree-explained or neither.

## What is settled by definition or by arithmetic (not tested)

- Satisfiability of C_k is monotone in k, and C_n allows no state for a growth that ends, so k* (the least dead core) exists.
- Only a closing knot can end a growth, and it lies in every contradiction, so k* is at least the floor, its largest index + 1.
- Old distinctions carry more knots: for X(q) the oldest k end with about (1 + q/2)/(1 − q) knots per distinction (1.64 at q = 0.3,
  1.81 at 0.35), and D* = m*/k* is confined between 1/(1 − q) and that value (the advisor's arithmetic). So D* itself tests nothing
  for X; it is reported, not predicted.

## Design (frozen; `census.py`)

X(0.25) and X(0.3) to 6,000 moves; X(0.35), O global (0.3) and O local (0.3) to 2,000; 100 growths each; fresh seeds ("OC:...").
For each ending: k*, m*, D*, the floor, the core peeled of distinctions in at most one knot (n2, m2), and three matched resamples of
the dying core, 20 each, the share that allow no state: **P_u**, uniform patterns with k* distinctions and m* knots; **P_u2**, uniform
with n2 and m2; **P_d**, patterns with the core's degree sequence. And k*_deg, the least dead prefix when distinctions are ordered by
final degree instead of age.

## Predictions (frozen)

The advisor model reviewed a draft cold: it showed that the draft's density predictions were settled by arithmetic, that a random
reordering control is settled by the contradiction's size, and that k* has a mechanical floor; it proposed the matched resamples and
the order by degree used here, and the separation they make: a uniform-end law says the dying core is near-critical among uniform
patterns of its size and knots (P_u about 1/2); a degree law says patterns with its degrees die as it does; age alone predicts
neither.

| # | Prediction (each process with at least 10 endings) | Fails when |
| --- | --- | --- |
| L1 | **Uniform-end law.** The median P_u is at least 0.3. | any process below |
| L1p | **Uniform-end law after peeling.** The median P_u2 is at least 0.3. | any process below |
| L2 | **Degree law.** The median P_d is at least 0.3. | any process below |
| L3 | **Age is a proxy for degree.** k*_deg ≤ k* in at least 70% of endings. | any process below |

The pilot (8 growths per process, seeds 888000 to 888007, and a smoke test of the frozen code on run 0 of three settings) gave dying
cores at 1.46 to 1.80 knots per distinction (peeled 1.63 to 1.83) and P_u = 0, P_d = 0 to 0.25: the author expects L1 and L1p to fail
and is unsure of L2 and L3.

## Stop rule and runtime

One run, its summary, a hand-off to the referee thread, report. About ten minutes on eight workers.
