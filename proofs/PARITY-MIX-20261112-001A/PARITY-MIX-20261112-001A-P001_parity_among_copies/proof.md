# Parity knots among stitched copies

Status: Proved where stated (the definitional facts, by hand, with the advisor model) with an exact census and uniform samples;
**referee pending** (the background referee thread). Ticket A of `research/PARITY-MIX-20261112-001/preregistration.md`, frozen with the
code in commit `a29eb99c8`.

Words as in the pre-registration: flip-blind parity knot (placewise sum all 0s or all 1s, one hidden reference per knot; read under
A78 as built from not-all-equal knots), flip-blind triple, count r, up to flips (each copy flipped on its own), flip-frozen, fixed by
count 0, reached by propagation, fixed but unreached, full fixing.

## 1. Settled by definition (proved; stated before the run)

- A parity knot forbids its three copies from being all equal, since a harmony's state is never constant.
- A harmony with no flip-blind triple has no state once one parity knot is placed.
- With parity at every cell, the placewise differences of any two places obey Ledrappier's law, so states exist only at Ledrappier's
  sizes (none on 4 × 4 or 8 × 8), and on 3 × 3 they are X(i, j) = U_{(i − j) mod 3} with (U₀, U₁, U₂) a flip-blind triple.
- Propagation is the definitional part: a parity knot with two known copies makes the third known up to a flip.

The two harnesses held on all 45 harmonies: on 3 × 3, one parity knot leaves a state only where a flip-blind triple exists, and parity
everywhere leaves one exactly where it does.

## 2. Which harmonies can hold a parity knot (exact; `result_census.json`)

**8 of the 45 harmonies have a flip-blind triple** (48 to 1,152 ordered triples each); the other 37 end at their first parity knot.
All 8 contain the orbit of 0011 or of 00101101 with another orbit (0011 + 01, 00001111 + 0011, 000111 + 0011 + 01, 00101101 + 0011,
000000111111 + 0011 + 01, 00001111 + 00101101 + 01, and the five- and seven-orbit harmonies), and in every one the largest subspace of
classes has dimension 2. In 6 harmonies the not-all-equal stitch forces one class in its first slot; none of them holds a flip-blind
triple.

## 3. Parity among not-all-equal stitches (exact on 3 × 3 and 4 × 4; sampled on 6 × 6 and 8 × 8)

For the 8 harmonies, with 1 ≤ k < nm parity knots (weighted over placements):

| Repeat | Placements | With a state | Full fixing | A count fixed but unreached |
| --- | --- | --- | --- | --- |
| 3 × 3, every placement | 4,080 | 114 (2.8%) | 24 | 69 |
| 4 × 4, every placement | 524,272 | 850 (0.16%) | 646 | 806 |
| 6 × 6, 20 per k (k = 3, ..., 33) | 1,760 | 6 (0.34%) | 0 | 0 |
| 8 × 8, 10 per k (k = 4, ..., 60) | 1,200 | 0 | 0 | 0 |

- **Survival is rare.** A state survives only at a few k: on 3 × 3 at k = 3 and 6 (and at 0 and 9); on 4 × 4 at most 0.5% of the
  placements at any k; on 6 × 6 only at k = 6, once in 20 for each of 6 harmonies; on 8 × 8 never. Parity everywhere
  keeps its states at 3 × 3 and 6 × 6 and has none at 4 × 4 and 8 × 8, as Ledrappier's law says.
- **Something beyond definition, where it survives (the frozen failure criterion is not met).** In 69 of the 114 surviving placements
  on 3 × 3 and 806 of the 850 on 4 × 4, count 0 fixes a count up to flips that propagation from count 0 does not reach; in 24 and 646,
  count 0 fixes every count (full fixing). So in the placements that survive, the harmony's states and the knots together pass
  influence through whole counts further than any single knot passes it. With no parity knot (k = 0), counts fixed but unreached also
  occur, through the not-all-equal locks of `SHIFT-LOCK-20261112-001`: they are not counted above.
- **Full fixing is not typical at any mixed density.** It never exceeds 3.6% of the placements at any k with 0 < k < nm (3 × 3, k = 6),
  is under 0.4% on 4 × 4, and is absent on the samples of 6 × 6 and 8 × 8. Only parity at every cell gives it typically, and there it
  is definitional.

## 4. After the run (descriptive; labelled)

- **Why one parity knot empties 3 × 3** (`after_run_one_knot.py`). No flip-blind triple of any of the 8 harmonies is a triple of its
  not-all-equal stitch (0 of 48 to 1,152). In 3 of them the other eight stitches on 3 × 3 already force the ninth cell's triple into the
  stitch, so one parity knot is a contradiction; in the other 5 they do not, and the emptiness is computed, not explained. The
  referee's product lemma (`LINE-LOCK-R1`: a permutive set of triples in a not-all-equal stitch puts a whole product of state sets inside
  it) does not by itself give this, since one triple is not a permutive set.
- **What survives** (`after_run_survivors.py`). On 3 × 3 the surviving placements with three parity knots are exactly the stars of a
  copy (the three knots that hold it), one per copy; over 3 × 3 and 4 × 4, 606 of the 964 survivors are unions of stars, the parity
  knots surrounding whole copies, and three of the harmonies survive in other shapes.

## What this establishes

- Proved: the definitional facts above; for the 37 harmonies without a flip-blind triple, one parity knot ends every arrangement.
- Exact on the range: parity knots and not-all-equal stitches almost never coexist (2.8% of placements on 3 × 3, 0.16% on 4 × 4, none
  in the 8 × 8 samples); where they do, count 0 usually fixes counts no propagation reaches, so something beyond definition happens, but
  only in rare structured placements on small repeats.
- So the smallest change that lets influence pass through whole counts is not typical: a scattering of parity knots ends the
  arrangement, and only parity everywhere, at Ledrappier's sizes, carries it as a rule.
- Not established: why flip-blind triples and stitch triples never meet (computed on 8 harmonies), placewise parity shifted like the
  harmony's own knot, larger structured placements (a region of parity knots inside the not-all-equal arrangement).
