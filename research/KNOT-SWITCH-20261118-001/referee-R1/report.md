# Referee report KNOT-SWITCH-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **The proofs hold.** W1 to W4 were checked by hand.
- **W2, over all nine assignments.** The referee enumerated every way to give four distinctions four knots with each distinction a
  middle once.
  - The three fill-type assignments allow exactly the six patterns W2 lists and force a crossing.
  - The other six force two of the four distinctions to be copies, so they never occur in a copy-free base.
- **The runs reproduce.** The referee's own KF3 and SEEDK started from the study's 105 bracketings.
  - **The four readings agree at every step** of all 210 runs (5,840 steps). They are: nothing crosses, no filled knot, b₂ = 0,
    and no fill yet.
  - **SEEDK is strong in 105 of 105 runs.** It keeps two orders at every step after the first fill, passes three or more full
    grids, and makes every later subdivision at a full grid.
  - **W4 holds:** the saturated line has b₂ = C(n − 1, 3), no filled knot and no crossing, for n = 4 to 9.
- **A Narrowing of the headline's scope.** "SEED's 'nothing crosses yet' reads, in the knots, 'no filled knot yet'" holds along
  these growths, and there all four readings flip together at the first move.
  - In general a crossing needs no filled knot. On 3,000 random copy-free presentations, 2,772 of the 2,776 bases with a crossing
    have no filled knot among their knots, and 2,760 have none even among all the knots the base satisfies.
  - W2's direction (a filled knot forces a crossing) held on all of them.
  - So the knot reading is a sufficient sign of a crossing that, on these growths, happens to appear first. It is not the knots'
    general state for "nothing crosses".

## What holds

- **W1 (a move attaches a cone).**
  - **The cone.** Every old pair a knot-local move uses already lies in K, so K′ = K ∪ cone(L) with cone(L) ∩ K = L.
  - **What the sequence gives.** Mayer–Vietoris gives b₂(K′) = b₂(K) + dim ker(H₁(L) → H₁(K)). b₁ gains the cokernel and the
    components of L minus one, since K is connected.
- **W2 (a filled knot forces a crossing)** (`referee_switch_w2.json`).

  | Middles on the four triples | Assignments | Allowed patterns | Copies forced | Crossing |
  | --- | --- | --- | --- | --- |
  | Paired as a knot and its fill (a double transposition) | 3 | 0000, 1111, and two crossing two-and-two patterns with their complements | no | yes |
  | A four-cycle | 6 | 0000, 1111, and one two-and-two pattern with its complement | yes, two distinctions always equal | no |

  - The proof's pattern elimination is right. A and C differ only on ar | cb, and a and r only on ac | br, so distinct
    distinctions need both patterns, and the two cross.
  - **One wording fix.** The definition "each of the four the middle of exactly one" also admits the four-cycle assignments. The
    note's own gloss, "a knot together with the three knots of its fill", is the right definition. The four-cycle cases force a
    copy, so they cannot occur in a copy-free base, but the definition should exclude them or say so. The study's
    `filled_knots()` accepts both, which is harmless there for the same reason.
- **W3 (the switch along these rules).**
  - **The first move is a fill.** It is a fill of a presentation knot (MEET-ORDERS Lemma A), because fills are cheapest or keep the
    condition.
  - **That move flips all four readings.** It makes the knot's filled knot, b₂ = 1 (L is the triangle a-c-b, which bounds), and the
    first crossing (PICK-TWO S6).
  - **None of them flips back.** Knots stay, b₂ never falls (W1), and crossings never go away (PICK-TWO S1).
  - **Before it:** a bracketing is a divided polygon, with no K₄ in its pair graph, so there is no filled knot, b₂ = 0, and nothing
    crosses.
  - So W3 is a statement about the first move.
- **W4 (b₂ depends on the presentation)** (`referee_switch_w4.json`).
  - The line presented by every knot it satisfies has b₂ = 1, 4, 10, 20, 35, 56 = C(n − 1, 3) for n = 4 to 9, with no filled knot
    and no crossing.
  - The implied knots on four distinctions of a line have their middles at the inner two, so they are never a fill.
- **The runs** (`referee_switch_runs.json`; the referee's own KF3 options from MEET-ORDERS-R1, and SEED's condition from PICK-TWO-R1
  with knot-local moves).

  | Rule, from 105 bracketings (5, 6, 7 all; 8 every third) | Runs | Steps | Four readings agree at every step | Further |
  | --- | --- | --- | --- | --- |
  | KF3, to n = 30 | 105 | 2,395 | 105 | λ at the end 5 to 7 |
  | SEEDK, to n = 40 | 105 | 3,445 | 105 | two orders at every step after the first fill: 105; three or more full grids: 105; every later subdivision at a full grid: 105 |

  The study ran NN and NN2 too (420 runs, 11,050 steps). The referee ran KF3 and SEEDK, which carry the claims about SEED.

## 1. The scope of the knot reading (Narrowing)

- **What is proved.** One direction holds in every presentation: a filled knot forces a crossing (W2).
- **The other direction is a fact about these growths.** All four readings flip together at the first move, so along them "no
  filled knot yet" is equivalent to "no move yet" as well.
- **Outside these growths** (`referee_switch_converse.json`):
  - The referee drew 3,000 random copy-free presentations: 5 to 7 distinctions and 3 to 9 random betweenness knots, each middle at
    random.
  - **A crossing without a filled knot is the usual case.** 2,776 of the bases have a crossing. Of those, 2,772 have no filled knot
    among their knots, and 2,760 have none among all the knots the base satisfies. An example on six distinctions is the four
    knots (1,4,5), (0,3,4), (1,0,3) and (1,4,2): 22 states, a crossing, and no filled knot even when saturated.
  - **The forcing direction held throughout:** 0 bases with a filled knot and no crossing.
- **What this means for the answer.** The knots' "not yet closed" marks SEED's switch on these growths, because the first fill
  closes a knot and makes the first crossing in one step. As a reading of "nothing crosses" in general, it only signals a crossing,
  and does not track one.
  - The note's limitation says the converse is shown only along these growths. The answer and the position table should carry
    that: "along these growths, both ways".
  - The study's own direction 2 (when does a crossing imply a filled knot?) has a first answer: rarely, on random presentations.
- **For A101.** As the note says, SEEDK must still be told to stop being free once the knots close. The count handed over is
  PICK-TWO's "one free step", now read in the knots.

## 2. Smaller points (Not a block)

- **Q2's "all four triples knotted"** is a weaker test than the filled knot, and it agrees along these growths too. In a copy-free
  base, only the fill-type middles can carry four knots on four distinctions with each distinction a middle once (§ What holds,
  W2).
- **"The smallest even knot set there is"** is right: four triangles on four vertices, the literature's boundary of a tetrahedron,
  as the note labels it.
- **The post hoc readings** are labelled as such in the note: b₂ rising with each new filled knot, loops after the switch, and 240
  rises in orders under KF3 with no new filled knot.

## Fixes for the thread (listed for the owner, not folded in)

1. **Scope the answer.** "SEED's switch reads 'no filled knot yet'" holds along these growths, where all four readings flip at the
   first move. In general a filled knot forces a crossing, but a crossing almost never comes with one: 2,772 of 2,776 crossing
   random presentations have no filled knot. **Narrowing.**
2. **The definition of a filled knot.** Say "a knot and the three knots of its fill", or say that "each the middle of one" also
   admits four-cycle middles, which force a copy. **Not a block.**

## How the work was split

- **The referee:**
  - read the note, the pre-registration, proofs W1 to W4, and `knotlib.py`;
  - checked the proofs by hand;
  - wrote `referee_switch.py`: the nine middle assignments, the saturated lines, the random-presentation converse, and KF3 and
    SEEDK runs with its own b₂ and filled-knot test. It builds on its MEET-ORDERS-R1, KNOT-CAP-R1, COUNT-BALLS-R1 and CUBE-DOUBLING-R1
    code.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_switch.py`.**
- **`referee_switch_w2.json`, `_w4.json`, `_converse.json` and `_runs.json`.**

Reproduce, from `research/KNOT-SWITCH-20261118-001/referee-R1/`:

```sh
for p in w2 w4 converse runs; do ../../../.venv/bin/python -B referee_switch.py $p > referee_switch_$p.json; done
```
