# Pre-registration: which parity placements survive

Epic `PARITY-SURVIVE-20261112-001` (`PARITY-MIX-20261112-001` direction 1, reshaped by the coordinator: characterise the survivors
first, then ask typical or rare under a stated weighting; G17 with G8; program mathematics, group arithmetic), written on 2026-11-12
before the census runs, at the coordinator's go-ahead under the owner's standing mandate. Code frozen with this file in
`proofs/PARITY-SURVIVE-20261112-001A/PARITY-SURVIVE-20261112-001A-P001_which_survive/` (`survive_lib.py`, `check.py`). The canonical
K1–K3 test is unchanged.

## The question

`PARITY-MIX-20261112-001` found that flip-blind parity knots and not-all-equal stitches almost never coexist among harmony copies,
and that where they do, count 0 fixes counts that local propagation does not reach. The coordinator asked two things of that: is
"fixed but unreached" nearly automatic when propagation can only use parity knots (the stitch forces no slot for these 8 harmonies),
and is the fixing only the parity knots' own arithmetic inside copies they surround? So: **which placements survive, how common is
survival as size grows, and how far does fixing pass through the not-all-equal stitches rather than staying inside parity?**

## Words

As in `PARITY-MIX-20261112-001` and the glossary (flip-blind parity knot, count r, up to flips, flip-frozen, fixed by count r₀,
reached by propagation, full fixing; classes, a state with its complement). New, plain (no new word: "star" is the literature's word for a vertex's neighbourhood, so a copy's knots
are called its three knots): a parity cell is **isolated** when no knot sharing a copy with it is parity; the **class-level system**, classes in place of states,
with flip-blind class triples at parity cells and the stitch's class triples elsewhere, which forgets which member of each class a
copy is (the advisor's "lifting"); the **tiers** of fixing count r from count r₀: **F**, the full system; **P**, parity knots and
every copy a state of the harmony, with no not-all-equal stitch; **L**, the parity equations alone, over F₂ on classes; **GAC**,
arc consistency on class domains with both relations, started from count r₀'s classes (a fair local baseline, in place of
PARITY-MIX's propagation through parity knots alone).

## Settled already, or by definition (the advisor model's, rechecked)

- With parity everywhere, a state is X with classes depending on c − r through a flip-blind triple; it exists iff 3 divides n.
- Every n × n survivor repeated is a kn × kn survivor, so "none in samples" is rarity, never absence.
- The 3 × 3 placement with parity off one diagonal class survives iff the stitch allows some class-monochromatic triple: settled by
  its class system (unique up to renaming classes), a check, not a finding.
- Lemma A (no flip-blind triple is a stitch triple) is a finite statement; its census is its proof on the 45 harmonies, and a
  conceptual proof is attempted only if it comes cheaply.
- Fixing must be measured from every base count: one placement per translation class misses the shifts along the first copy shift,
  which move counts (the referee's early note on PARITY-MIX, 39 against 24 full fixings on 3 × 3).

## The census (frozen)

- **lemma.** The 45 harmonies: flip-blind triples, those the stitch allows, classes.
- **small.** The 8 harmonies with a flip-blind triple; every placement on 3 × 3 and 4 × 4 (survival on one per translation class,
  weighted by class size; fixing from every base count, which covers every placement): survival, class-level survival, an isolated
  parity cell, and on survivors with 0 < k < nm the tiers F, P, L and GAC for every pair (base count, other count).
- **scale.** The stated weighting: each cell parity independently with probability ρ, ρ in {1/8, 1/4, 1/2, 3/4, 7/8}; n = 3 to 9;
  100 placements per (harmony, n, ρ), seeded: the same measures; and per harmony the first-moment rate λ(ρ) = ln|W| + ρ ln(|FB| / |W|³)
  + (1 − ρ) ln(|R| / |W|³) per cell (survival of n × n at most about e^{λ n²} where λ < 0).
- **Cap.** 1 hour and 16 GB per part; rows saved as they finish.

## What counts (frozen)

- **B1, lifting never binds:** class-level survival equals survival on every 3 × 3 and 4 × 4 placement. A placement that survives at
  class level only is an obstruction from the choice of state within classes; listed.
- **B2, isolated parity cells are fatal:** no survivor (0 < k < nm) has an isolated parity cell, on 3 × 3, 4 × 4 and the samples.
- **Typical or rare:** typical if, at some ρ and some n ≥ 6, at least 10% of the placements survive; rare if under 1% at every ρ for
  every n ≥ 6.
- **Where fixing comes from:** over survivors, the pairs (base count, count) fixed in F and not flip-frozen, split into those fixed in
  L (parity's own arithmetic), in P but not L (parity with the harmony's states), and in F but not P (**the stitches' share**: fixing
  that passes through not-all-equal stitches); and those not fixed by GAC (beyond the local baseline). The coordinator's worry holds if
  the stitches' share is empty and almost all fixing is in L.

## Predictions (frozen; the advisor's unless marked)

- Lemma A on all 8 harmonies (a check of the earlier census; 99%).
- B1: mine, 55% that lifting never binds.
- B2: isolated parity cells fatal (80%).
- Survival decays with n at fixed ρ; at high ρ the order is n ∈ {3, 6, 9} ≫ 7 > 5 ≫ {4, 8} (70%); rare by the criterion above
  (mine, 80%).
- Fixing beyond GAC on some survivor (85%); almost all fixing in L (75%); the stitches' share under a tenth of the fixed pairs (60%; the
  advisor predicted it empty or tiny, but one instance was seen before the freeze, below).

## Known mathematics, checked before the freeze

The triangular plaquette model (Newman and Moore, 1999; Garrahan and Newman), three-spin parity on the same knot shape, with ground
states fixed by the size's arithmetic and unique at 2^k; linear cellular automata on rings (Martin, Odlyzko and Wolfram, 1984);
fractal symmetries (Yoshida; Devakul and co-authors); mixed hypergraph colouring, at the class level with three classes (Voloshin's
C- and D-edges; Kündgen, Mendelsohn and Voloshin on planar mixed hypergraphs); uniquely extendible constraints (Connamacher and Molloy),
of which the parity knot on classes is one; mixtures of linear and non-linear clauses ((2 + p)-SAT, Monasson and co-authors), locked
constraint problems (Zdeborová and Mézard); Schaefer's dichotomy (the mixture is NP-complete in general). No paper on this exact
mixture is known to the advisor or me. What could be new: the survivors' rule on harmony copies, their rate by size under one weighting,
and the stitches' share of fixing.

## Seen before the freeze (disclosed)

All of `PARITY-MIX-20261112-001`'s results and its survivors' shapes; per harmony, the classes and class-level triples of the 8
harmonies (one has exactly 3 classes: 0011 + 01); a smoke test of the code on one known 3 × 3 survivor of 0011 + 01 (the three knots of
copy (1, 1)): it survives at class level too, and from base count 0 its count 1 is fixed in F but not in P, L or GAC.

**Referee.** The background referee thread (referee pending). Assumptions in force: A70, A75, A77, A78. Nothing here bears on P versus
NP.
