# Is the bond bounded where the calls remember: pre-registration

Epic `CARRY-BOUND-20261114-001` (`CENSUS-FORGET-20261114-001#2`, backlog B174, with `TIE-CYCLE-20261114-001#2`; G17, with G1),
2026-11-14, at the coordinator's go-ahead. Frozen before any window, path or direct result is computed for any family of the
population. Code by Codex from this text in one hand-off, run by the thread on the shared runner. The advisor model was consulted
twice before the freeze (`advisor_review_answer.md`, `advisor_review2_answer.md`). The canonical K1–K3 test is unchanged.

## The question

`CENSUS-FORGET-20261114-001` certified growth with nothing chosen in 53.2% of the census's first-ray growth weight. The rest is
almost all **non-forgetting**: some long product of per-call port relations is never rectangular, so the gap argument says nothing.
`TIE-CYCLE-20261114-001` found what these families keep: almost always a value carried down by identity, rarely a tie through knots,
and otherwise a one-way order. For these families, per depth, with members anywhere, any covered target and paths that may change
with the depth: is the least bond bounded, or does it grow by some other argument?

## The question in standard terms

In iterated hyperedge-replacement NAE instances whose port-relation semigroup has a non-rectangular idempotent, whether the least
minimal non-shattered set containing a root port and a vertex at derivation depth s stays bounded in s. Upper bounds come from
exact projections onto a finite window, eventually periodic in s; lower bounds from rectangular powers on a quotient.

## Prior work in the program

`python3 -B scripts/track.py objects "carried top port local knot bounded bond at every depth" --until 2026-11-14 --exclude CARRY-BOUND-20261114-001`
`python3 -B scripts/track.py objects "non-forgetting nested families free bond bounded per depth" --until 2026-11-14 --exclude CARRY-BOUND-20261114-001`
`python3 -B scripts/track.py objects "order-type idempotent no conserved quantity bond" --until 2026-11-14 --exclude CARRY-BOUND-20261114-001`

- `TRUE-RATE-20261113-001`: carried top ports among bounded rules, and a post-hoc carried-port certificate of at most 3 on one ray;
  the closest relative. This study makes it per depth, over every word, with members anywhere.
- `REACH-CENSUS-20261113-001`: first-ray bounds, 82% of them a carried top port; the population's source.
- `FREE-TARGET-20261114-001`, `CENSUS-FORGET-20261114-001`: the free bond, forgetting and its covered targets; the population is
  CENSUS-FORGET's undecided half.
- `TIE-CYCLE-20261114-001`: the strata (identity, tie, order); `FORGET-RULE-20261114-001`: rule N.
- `EVERY-RAY-20261113-001`: the min-over-paths DP reused here.
- `LOOP-LOCK-20261112-001`, `SHIFT-LOCK-20261112-001`: lexical hits, unrelated.

## Words

- **Covered target**: an own distinction of a copy of S at depth s reached from main through S calls only, with S the ray
  definition, as in `CENSUS-FORGET-20261114-001` after its referee. Depth is counted as in FREE-TARGET's code.
- **L(s)**: the least bond (minimal non-shattered set) containing a port of main and a covered target at depth s, with members
  anywhere in the infinite usual-limit pattern.
- **Bounded**: some C with L(s) ≤ C at every large s. **Bounded on progressions**: ≤ C on some residues of s modulo a period and
  not on others. **Grows**: L(s) → ∞.
- **Carried position**: a port position k of S that holds a port of main at depth s by identity (edges j → k when the k-th argument
  of a SELF call of S is the copy's port j; for a wrapper main, the start is the set of S positions that receive main's ports).
  R_s is the set of carried positions at depth s; it is eventually periodic.
- **Pendant**: an own distinction of S that occurs in exactly one constraint of S's flattened block and in no call's arguments, of
  any definition.

## Population and strata

The census first-ray growers that `CENSUS-FORGET-20261114-001` left undecided: non-chains whose verdict is non-forgetting or
capped, 5,964 families (6,028 draws). **In scope**: no other self-holding definition with own distinctions reachable from main or
S, and no delayed S (the criteria of CENSUS-FORGET's referee, `target_inventory.py`). Out-of-scope families are a labelled row only:
there, an upper bound to covered targets still bounds the bond, but a lower bound does not. Strata, by TIE-CYCLE's classification:
- **I**: an identity cycle among S's SELF calls (about 5,622 in scope).
- **T**: a tie cycle and no identity cycle (5).
- **O**: no tie cycle, only order-type non-rectangular idempotents (91).
- **X**: the rest (1 with other labels; capped classifications).

## Proved here (before the run)

The usual-limit relations are the decreasing limits from "everything allowed", so by compactness they are the exact projections
of the infinite subtrees onto their ports. Every family below is living (it has an allowed state), checked per family.

**Lemma W (window).** Let w be an S-call word of length s from the top copy of S, c the copy at its end, and J_w the joint relation
of main's ports with c's ports in the pattern with c's subtree removed. J_w = Start · R_{w1} · … · R_{ws}, where R_i is the
projection of S's block, every other call replaced by its usual-limit relation, onto (parent ports, the i-th call's arguments), and
Start is main's block projected likewise (the diagonal when main = S). Then the projection of the whole pattern onto main's ports
together with every distinction of c's block is exactly {(t, b) : (t, b|ports) ∈ J_w, b satisfies c's knots and its children's
usual-limit relations}.
*Proof.* The pattern is a tree of copies, and c's subtree meets the rest only through c's ports. The usual-limit relations are the
exact projections of the infinite subtrees onto their ports. Composition is exact by the same separation at each copy on the way.
A distinction of c that is the same distinction as a port of main (identity along w), or two ports of c that are the same
distinction, is one variable: the window tracks this identity map with J_w and merges such variables. ∎

**Window bound.** Every bond of the window projection that contains a port of main and an own distinction of c is a bond of the
pattern (non-shattering and minimality are read off the exact projection). So L(s) ≤ U(s), the minimum over words of length s of the
least such window bond. The state of a word is its pair (J_w, identity partition of main's ports and c's ports). The set Q_s of
states at length s is a function of Q_{s−1}, so the first repeat proves periodicity, and U is computed exactly at every s, every
residue included. No repeat before the cap means undecided (a capped semigroup length set certifies nothing).

**Theorem B (carried pendant knot).** Suppose the family is living, K is the set of positions k of S whose block has a knot
{k, x, y} with x and y pendant, and every set in the repeating part of R_s meets K. Then L(s) ≤ 3 at every large s.
*Proof.* At depth s some copy has a port of main p at a position k ∈ K. Its pendant x and y occur in no other constraint, so every
allowed state extends to all six NAE triples on (p, x, y). p takes both values (living and complement-closed), so the projection on
{p, x, y} is NAE: constrained, every pair free. ∎ If only some residues meet K, the bound holds on those progressions only, and is
reported as its own cell.

**Widened B (the advisor's).** If at a carried position k the block has a knot {k, x, z} with x own and z anything, then
{p, x, z} is non-shattered, and the bond it contains holds both p and x unless z is tied opposite to p or to x while {p, x} is
free. Both are read exactly in the window.

**Lemma G (growth on the live quotient).** If a non-shattered set contains a distinction that lies in no constraint, it stays
non-shattered without it, so no bond contains such a distinction. A port position is **dead** when every occurrence of it, in every
definition, is as an argument at a dead position (a least fixed point across all definitions), and a distinction is free when every
position it occupies is dead. Delete the dead coordinates from every R_i. If every r-product of the reduced relations is
rectangular, the gap argument applies, so L(s) ≥ 2 + ⌊s/r⌋, shifted by one level for a wrapper main.

**Lemma G2 (trimmed gap, the advisor's suggestion, checked here).** Let a member-free stretch of a bond run from copy c_a to copy
c_b along the target's word v. The pattern's realisable pairs of port states across it are exactly
M' = {(α, β) ∈ M_v : α ∈ A, β ∈ G_S}, where A is the image of c_a's context (the second coordinate of J at c_a) and G_S is S's
usual-limit relation, because the outside, the stretch and c_b's subtree meet only through α and β. If M' is rectangular, the bond's
projection is a product of its two sides' projections, both shattered by minimality, so it is shattered: a contradiction. Hence if
for every reachable context state and every word v of length r the trimmed product is rectangular, L(s) ≥ 1 + ⌊s/r⌋ (it grows; the
constant is not the point). Lemma G2 applies to the live quotient too.

## Methods

1. **Window, census-wide** (every family of the population). U(s) per residue, exact; the window bonds' sizes; B, widened B and the
   tie variant as readings inside the window; Lemma G's and Lemma G2's certificates (r up to 8).
2. **Path DP, on a frozen sample.** EVERY-RAY's min-over-paths DP (members on the path; L ≤ L_path), with its exact per-depth
   residue test, on: all T, O and X families the window leaves undecided at some residue, and a sample of the I families it leaves
   so. The I sample is stratified by the period of R_s (1, or more) and by whether some carried position shares a knot with an own
   distinction (yes, no): up to 30 per cell, taken in order of sha256("CARRY:" + key).
3. **Direct search, finite readings.** On the families still undecided after step 2 (up to 60, the same order): the exact least
   bond to a covered target at s = 1 to 6, members anywhere within the unfolded pattern to depth s + 2 with usual-limit relations at
   the frontier (FREE-TARGET's referee's direct search, reused). These are upper bounds per depth. A family that "grows to depth 6"
   is **undecided**, never "grows".

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | **Gates.** (a) The window's per-call relations equal CENSUS-FORGET's R_i for every family, and every family is living. (b) Every B-covered family has U(s) ≤ 3 at every covered residue. (c) **Negative control:** on 300 certified-forgetting families (the first 300 in sha256("CARRY:" + key) order), U(s) ≥ 2 + ⌊s/r⌋ at every s up to the repeat (shifted for wrappers), as the gap argument proves; Lemma G2 certifies all 300. (d) **Brute force:** on 50 stratum I families (the same order), the window projection at every state reached by s ≤ 3 equals the projection of the explicitly unfolded pattern to depth s + 1 with usual-limit relations at the leaves, computed by separate code; and 200 window bonds, drawn with seed 20261114, are re-verified there. (e) No family is certified both bounded and growing. | any fails |
| P1 | **Carrying bounds the bond.** In stratum I, the window bounds L at every large depth in at least 80% of the in-scope weight. | below 80% |
| P2 | **An order bounds less often.** O's share bounded at every large depth by the window is at least 20 points below I's. O's share is reported alone, with its Wilson interval. | the gap is under 20 points |
| P3 | **The residue is identity that never meets an own distinction.** Among in-scope I families the window leaves unbounded at some residue, at least 80% by weight have, on that residue, no carried position that shares a knot with an own distinction (an identity cycle that holds no port of main, or one in port-only knots). Opposite ties are then rare. | below 80% |
| P4 | **Ties act like identity.** All 5 in-scope T families are window-bounded at every large depth. Reported family by family. | any is not |
| P5 | **Growth is rare here.** Lemmas G and G2 together certify growth in at most 5% of the in-scope population by weight. | above 5% |
| — | Reported: the window bound's sizes (that a carried bond through one knot has at most 3 members is settled by construction, so this is not a prediction); B's and widened B's shares of the window-bounded weight (readings, not tests); progressions-only cells; the window bond's size distribution; the out-of-scope row; the path DP's and the direct search's results on the sample, with the undecided cell. | — |

**Undecided** (any cap or timeout, a family with a capped length set, or a residue left without a window bound) counts as **not
bounded** in P1 to P4 and as **not growing** in P5. A sensitivity with undecided families left out is reported beside each share. P2 is underpowered (O's
Wilson half-width is about 10 points) and P4 is all or nothing at n = 5; both are read as such.

## Runs and stop rule

Codex builds `window.py`, the job for the shared runner, the sample selection, the path and direct runners and the gates in one
hand-off, writing only in `experiments/CARRY-BOUND-20261114-001A/CARRY-BOUND-20261114-001A-E001_window/codex/`, without commits.
The thread runs the census-wide window on the shared runner (3 workers, 3 GB per case, MemoryMax 12 GB, 600 s per case, one retry
for timeouts and memory), then the sample. Each run over about ten minutes is registered in `docs/LONG_RUNNING.md`. Stop after the
runs, their summary, a referee hand-off and the report.

## Clarification after TIE-CYCLE's referee (2026-11-14, before any result)

TIE-CYCLE-R1 found that the sort of idempotents into conserved labels and orders is a census label read on each idempotent's core,
not a dichotomy: one O family (4f5934b2e118) also conserves a parity, and core labels need not hold between a word's ends. So the
strata here are reporting labels, computed exactly as frozen (`classify_full`), and **O** means "no tie cycle, only one-way core
comparabilities", not "nothing carried". P2 compares the window's shares on these labels and claims nothing about what O families
conserve. Nothing else changes; no code or prediction is affected.
