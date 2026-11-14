# Design: reach across levels in addressed patterns (stage 1; predictions frozen after the pilot)

Epic `LEVEL-REACH-20261114-001` (`ADDR-KNOTS-20261113-001#3`; G17, with G1), approved by John 2026-11-14 02:38 UTC ("Yes, let's investigate"); at the coordinator's 02:44 UTC note it runs beside LEVEL-RETURN's background runs. Advisor consulted on the design (`advisor_design_*.md`); the finite-inflation lemma for bounded patterns is backlog B175. Codex builds from `codex_spec.md`.

## Object (after the advisor, 2026-11-14)
- Distinctions: addresses of every length 0..N. Description: automaton (s ≤ 5) + placements of three terms; a term (g, a): g a word
  of length ≤ 2 in the state maps, a ∈ {none, 0, 1}; t(w) = g(w)·a. Knot at every w where the three results have length ≤ N and are
  distinct. Knots lie within a level or join level n to n + 1.
- Weighting: the census's code plus log2 3 bits per term's letter. Settled by construction and reported apart: no placement joining
  two levels (levels never meet); tree-only placements (ruler, L = s + 2); dead union pattern (death level recorded).
- Top: every address of level k0 = 3 (the root is isolated in most descriptions); target: level k0 + s, s = 1..S.

## Observable
- L_N(s) = the least bond (minimal non-shattered set) holding an address of level k0 and one of level k0 + s, members anywhere in
  levels 0..N; N = k0 + S + 2, gate N + 1 (L is non-increasing in N: growth verdicts are "to depth N").
- Also: the maximum over target addresses of the least bond, the share of target addresses bound at each size, and the overshoot
  (deepest member's level minus the target's).
- Exact method: implicit hitting set over implicates (bonds = inclusion-minimal supports of implied clauses), smallest first, with
  certificates both ways (a refutation for the forbidden assignment, states for every proper subset).
- Outcomes per pattern and class: dead, no bond, rigid-like (L = 2 at every s read), bounded (3..k_max), growing to depth N;
  bounded and polynomial activity reported apart from exponential.

## Settled / known
- The gap argument holds (knots span one level step) but forgetting across whole levels is far stronger than across 3 ports, and the
  plain tree is not forgetful though it is a ruler: the finite-semigroup test does not transfer (exponential, polynomial classes);
  for bounded automata a finite inflation might give ports (a lemma to prove, not assumed).
- Joint rigidity on levels 0..N gives L = 2 everywhere; per-level rigidity does not.

## Predictions (directional now; numbers frozen after a pilot on a held-out seed split)
- Rigid-like and dead shares rise from bounded to exponential; growth concentrates in the bounded class; overshoot mostly
  exponential.

## Prior work to check
Tree reconstruction (Mossel; Evans, Kenyon, Peres and Schulman), point-to-set correlations (Montanari and Semerjian), freezing in
random CSPs (Achlioptas and Ricci-Tersenghi; Zdeborová and Krzakala), prime implicates and backbones, Schreier graphs (D'Angeli,
Donno, Matter and Nagnibeda; Bondarenko).
