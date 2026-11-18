# Referee report MID-RULE-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.** Part F (MID-RULE-B1) is still running, so Q2, Q3 and Q5 are not judged here.

- **The proofs hold.** E1 to E5 were checked by hand.
  - **E1, a new crossing needs two different end knots:** right.
  - **E2's "any base":** holds on any base of betweenness knots. On 400 random bases that no growth made, 10,244 fills have a
    certificate with at most one end knot, and none changes a relation of two splits or λ. Every certificate of each of the 33,430
    crossing-making fills has at least two end knots.
- **Part K reproduces with the referee's own knot-local engine.**
  - Both rules made exactly one fill per run in all 105 runs to n = 60, and in 35 runs taken one size past, to n = 75.
  - Each kept two orders after it, and none reached a full grid.
- **E5 checks out independently of part F.** From the line of five, each of its ten possible first fills was played out to
  n = 14. The three spanning ones reach full grids, and the seven others never do.
- **The owner's question: is "keeps two orders, told no number" fair? Only with a scope.**
  - Knot-locally, the rule never accepts a second fill, so it keeps two orders by lengthening: subdivisions keep every relation
    (N1), and E2 is never exercised.
  - Free, it grows full grids only from the 2 × 2 pattern, or when the free first fill spans the line: 6 / (n (n − 1)) of lines,
    11% at eight.
  - And the one free fill is handed over, as in PICK-TWO.
  - **Narrowing (wording).**

## What holds

- **E1.**
  - **The copy principle.** Each knot makes r copy one old distinction on the states it pins.
  - **Why two different knots.** If t₁ and t₂ come to cross, r's values on their states T₁ and T₂ are a pair no old distinction
    takes. So no single knot pins both.
  - **Why neither is a middle knot.** A middle knot on (x, y) pinning T₁ puts x and y on r's side of t₁. The quadrant is empty, so
    x and y lie together on the far side of t₂ from r. The knot would then pin r on T₂ to the wrong value.
- **E2.**
  - **No new crossing means no relation changes.** Without a new crossing no empty quadrant is filled, so no relation changes.
  - **So k and λ are unchanged.**
  - **MID2's certificates qualify.** A certificate with two middle knots, among at most three, has at most one end knot.
- **E3.**
  - **The first fill** makes two orders (PICK-TWO S6).
  - **Afterwards,** fills are E2's and subdivisions keep every relation (N1).
  - **The switch** is the first filled knot along growth from a bracketing (KNOT-SWITCH W3).
- **E4.**
  - **At a full grid** every fill makes a new crossing (NEVER-NEST N3 (i)), so E2 rules it out.
  - **After a subdivision** the new row's cells are medians forced by three middle knots on any pairs.
- **E5.**
  - **Uncrossed splits stay uncrossed** (E2, N1).
  - **A spanning first fill crosses every split.** The empty cells are then medians of its corner and the line's cells.
  - **The count.** (n − 2) / C(n, 3) = 6 / (n (n − 1)).

### The referee's computations (`referee_mid.py`)

- **E1 and E2 on bases no growth made** (`referee_mid_e1.json`): 400 random bases of 3 to 7 betweenness knots on 5 to 8
  distinctions, copy-free.
  - Every fill was listed with every certificate of one to three knots on r and old pairs: 43,677 fills in all.
  - **The 10,244 fills with a certificate of at most one end knot:** none changes a relation of two splits (so none changes k), and
    none changes λ.
  - **The 33,430 fills that make a new crossing:** every certificate has at least two end knots.
- **Part K** (`referee_mid_k.json`):
  - **The engine.** The referee's own knot-local enumeration of irredundant fills on co-knotted pairs, in Python integers, so there
    is no state limit. Starts: every bracketing of 5, 6 and 7, and every third of 8.

  | Rule | Runs | Fills per run | Two orders at every step after the first fill | Runs with a full grid |
  | --- | --- | --- | --- | --- |
  | MID2K to n = 60 | 105 | 1 in all | 105 | 0 |
  | ONEK to n = 60 | 105 | 1 in all | 105 | 0 |
  | MID2K to n = 75 (one size past) | 35 | 1 in all | 35 | 0 |
  | ONEK to n = 75 | 35 | 1 in all | 35 | 0 |

  - The first fill is always a presentation knot's fill. A bracketing of six offers four, one per knot, as Lemma A says.
- **E5 from the line of five** (`referee_mid_e5.json`). MID2F (free) was played out from each of the line's ten first fills to
  n = 14.
  - **The three spanning first fills** ((0, 1, 4), (0, 2, 4), (0, 3, 4)) reach a full two-way grid twice each.
  - **The seven others** never reach one.
  - **λ** stays 2 throughout.
  - **The share.** 3 of 10 = 6 / (5 × 4), as E5 says.

## 1. Is "keeps two orders, told no number, reading only the fill's knots" fair? (the owner's question; Narrowing, wording)

- **What is proved is right.** No fill certified with at most one end knot ever changes the number of orders, on any base of
  betweenness knots. So a rule taking only such fills after its first can never raise.
- **What the rules actually do:**
  - **Knot-local.** After the free first fill, no fill ever passes the test. The referee's runs found none in 210 runs to n = 60,
    or in 70 runs to n = 75. The rule lengthens forever, and two orders are kept by subdivisions alone (N1). E2 is never exercised.
    In effect the knot-local form is "one free fill, then lengthen". The note says it starves, which is honest, but the headline
    leads with keeping.
  - **Free.** It keeps two orders and refills full grids, but only from the 2 × 2 pattern or when the free first fill spans the
    line. That happens with chance 6 / (n (n − 1)): 30% at five, 11% at eight, 4.5% at twelve. Otherwise an uncrossed split stays
    forever and no full grid occurs.
- **The one free fill is a given.** As in PICK-TWO, the rule allows exactly one order-making step: the switch, at the first
  crossing or the first filled knot along growth. Its test then refuses every further one. So "told no number" holds for the number
  of orders, while the number of order-making steps, one, is built into the rule.
- **A fair headline.** "A fill can make a new crossing only through two different end knots (proved, on any base of betweenness
  knots). So after one free fill, a rule that reads only a fill's knots and takes those with at most one end knot never makes a third
  order. Free, it grows full grids only from a spanning first fill or the 2 × 2 pattern. Knot-local, it never fills again."

## 2. What waits on part F

- **Q2** (free forms strong from 2 × 2), **Q3** (strong exactly when the first fill spans) and **Q5** (ANY raises λ in every run)
  are the frozen checks of E4 and E5 and of the control.
- **What the referee checked meanwhile:** E5's mechanism on the line of five, all ten first fills.
- **Not checked here:** the 2 × 2 runs and the ANY control.
- The proofs E4 and E5 do not depend on part F, but the note's verdicts for Q2, Q3 and Q5 do. They should be read when MID-RULE-B1
  is folded in.

## Fixes for the thread (listed for the owner, not folded in)

1. **The headline.** Use §1's wording. Say that knot-locally the rule never accepts a second fill, so it keeps two orders by
   lengthening. Say that free, it grows only from a spanning first fill (6 / (n (n − 1)) of lines) or the 2 × 2 pattern. **Narrowing
   (wording).**
2. **"Any base".** Write "any base of betweenness knots", where splits and λ are defined. **Not a block.**
3. **The free first fill.** Name it as the given: one order-making step, as in PICK-TWO. **Not a block.**

## How the work was split

- **The referee:**
  - read the note, the pre-registration, proofs E1 to E5, and `midlib.py`;
  - checked the proofs by hand;
  - wrote `referee_mid.py`: certificate enumeration on random bases, its own knot-local MID2K and ONEK, and MID2F from every first
    fill of the line of five. It builds on its MEET-ORDERS-R1, KNOT-CAP-R1, KNOT-SWITCH-R1 and COUNT-BALLS-R1 code.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_mid.py`.**
- **`referee_mid_e1.json`, `referee_mid_k.json` and `referee_mid_e5.json`.**

Reproduce, from `research/MID-RULE-20261118-001/referee-R1/`:

```sh
for p in e1 k e5; do ../../../.venv/bin/python -B referee_mid.py $p > referee_mid_$p.json; done
```
