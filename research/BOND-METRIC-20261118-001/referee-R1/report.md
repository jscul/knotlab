# Referee report BOND-METRIC-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **The theorem holds.** Among the 34 three-place laws passing K1 and K2, bond distance is a metric on every base of copies of one
  law exactly when the law is parity.
  - **The proofs.** T1 to T5 were checked by hand.
  - **The bases.** Every base the proofs name was rebuilt with the referee's own code and fails or passes as stated: T2, T3, both of
    T4's bases and its twist, T5 and its twist, and P6's pair.
  - **The census.** It agrees: each of the nine languages first fails where the study says, the parity bases never fail, and the
    not-all-equal meeting-once counts on eight distinctions match exactly.
- **One size past corrects a minimality claim.** "Not exactly two ones" (R5) does not need eight distinctions to fail.
  - On seven distinctions with six knots, 8,190 of 1,356,250 bases fail. An example is {0,1,2}, {0,1,3}, {0,1,4}, {0,2,3},
    {2,4,5}, {3,4,6}, where 5 and 6 are held by no bond while each is two from 0.
  - None fails on seven with five knots, or on six distinctions with up to eight knots.
  - So T5's base is a failing base, not the smallest. **Narrowing.**
- **One wording narrowing.** "Bond distance is a metric exactly where knots compose" holds law by law, not base by base.
  Not-all-equal trees and the tori checked are metric although not-all-equal knots do not compose.
- **The owner's flags all check out.**
  - **T5:** its closure argument is right (§1).
  - **The nine languages:** the right unit (§2).
  - **P3b and P6:** both rightly scored failed (§3).

## What holds

- **T1.**
  - **The matroid.** If the bonds satisfy elimination, they are the circuits of a matroid: they form an antichain, being minimal
    constrained sets. The free sets are its independent sets.
  - **The inequality for b.** Whitney's equivalence ("equal or on a common circuit") gives a circuit C₃ ⊆ C₁ ∪ C₂ through x and z,
    so b(x, z) ≤ |C₁| + |C₂| − 2.
  - **The inequality for b − 1.**
    - If C₁ ≠ C₂, then C₃ ≠ C₁ ∪ C₂, because C₁ ∪ C₂ properly contains the circuit C₁. That gains one more, so b − 1 satisfies the
      inequality.
    - If C₁ = C₂, the bound reads |C| − 2 ≤ 2|C| − 4, which holds.
  - **Infinite pairs.** b is infinite exactly between different connected parts, so no infinite left side meets a finite right
    side.
  - **The referee's random parity bases** (`referee_metric_parity.json`): 1,500 of them, with either constant, 4 to 11
    distinctions and 1 to 7 knots. 0 failures of b, and 0 of b − 1.
- **T2 to T5 and P6, rebuilt** (`referee_metric_bases.json`; b on the pairs named, then the number of failing triples):

  | Base | States | The two short sides | The long side | Failing triples |
  | --- | --- | --- | --- | --- |
  | T2: NAE {a,b,c}, {a,b,d} | 10 | b(c, a) = b(a, d) = 2 | b(c, d) = ∞ | 2 |
  | T3: two clauses sharing two; sharing one | 13; 25 | 2, 2 | ∞ | 2; 4 |
  | T4: R6(a; b, c), R6(d; b, c); R6(a; b, c), R6(a; d, e); the first with c switched | 10; 20; 10 | 2, 2 | ∞ | 2; 4; 2 |
  | T5: the R5 closure base; with a, c, d switched | 34; 34 | b(c, a) = b(a, d) = 2 | b(c, d) = ∞ | 6; 6 |
  | Two R5 knots sharing two | 7 | 2, 2 | b(c, d) = 2 | 0 |
  | P6: NAE {0,1,2}, {0,1,3}, {0,4,5}, {2,4,5} | 24 | b(3, 0) = b(0, 4) = 2 | b(3, 4) = ∞ | 6 |

  - **P6's pair 3, 4** takes its four joint values 6, 6, 6 and 6 times: fully independent, as the note says.
- **The smallest failures per language** (`referee_metric_smallest.json`; every placement of the language's law, every base of two
  and three knots on four and five distinctions):

  | Language | (4, 2) | (4, 3) | (5, 2) | (5, 3) |
  | --- | --- | --- | --- | --- |
  | parity | 0 of 6 | 0 of 4 | 0 of 15 | 0 of 100 |
  | not-all-equal | 6 of 6 | 0 of 4 | 0 of 15 | 10 of 100 |
  | betweenness | 30 of 54 | 0 of 216 | 0 of 135 | 1,710 of 2,970 |
  | clause | 6 of 6 | 0 of 4 | 15 of 15 | 100 of 100 |
  | clause, twisted | 30 of 54 | 24 of 216 | 75 of 135 | 2,130 of 2,970 |
  | R5 | 0 of 6 | 0 of 4 | 0 of 15 | 0 of 100 |
  | R5, twisted | 0 of 54 | **12 of 216** | 0 of 135 | 240 of 2,970 |
  | R6 | 6 of 54 | 0 of 216 | 15 of 135 | 820 of 2,970 |
  | R6, twisted | 6 of 54 | 48 of 216 | 15 of 135 | 550 of 2,970 |

  - **Six languages fail at (4, 2), as P3 said.** The twisted R5 first fails at (4, 3), 12 bases. The study's 108 counts knots on
    distinct triples only; the referee's 216 allows two knots on one triple. The 12 failures are the same.
- **Not-all-equal meeting at most once, on eight distinctions** (`referee_metric_nae8.json`; systems covering the eight that allow a
  state). These are exactly the study's counts: with four knots, 0 of 25,200 fail; with five, 10,080 of 75,600; with six, 0 of
  68,880.

## 1. T5, the R5 closure argument (the owner's flag; holds)

- **The free-set criterion.** R5 allows weights 0, 1 and 3, so the allowed states are the sets of ones closed under "two of a knot
  force the third". S is free exactly when cl(A) ∩ S = A for every A ⊆ S. By monotonicity of closure, that holds exactly when no
  member of S is in the closure of the others.
- **{a, f₁, c} is a bond.**
  - It is constrained: a and f₁ force b, and then g₁, f₂, g₂, c and d, so c ∈ cl({a, f₁}).
  - Its pairs are free, because single elements force nothing.
  - The same holds for {a, f₂, d}.
- **No bond holds c and d.**
  - **T holds a (or b) and something else.** Then T closes to everything, so d ∈ cl(T) and S − c is not free.
  - **T = {a}.** Then {a, c, d} is free, since a with c or with d forces nothing.
  - **T avoids a and b.** It can hold at most one of f₁ and g₁, and at most one of f₂ and g₂. Then any closure adds only the other
    member of each pair, outside S, so S is free.
- **The twist.** Each knot holds exactly one of a, c and d, so switching those three turns every knot into a twisted R5. R5 is
  symmetric in its places, so which place is switched does not matter.
- **The code agrees.** It confirms both bases: b(c, a) = b(a, d) = 2 and b(c, d) = ∞.
- **But T5's base is not the smallest R5 failure** (`referee_metric_r5.json`):
  - **No failures:** on six distinctions with 5, 6, 7 or 8 knots (13,992, 37,500, 76,800 and 125,700 bases), or on seven with
    five knots (221,396).
  - **Failures:** on seven distinctions with six knots, 8,190 of 1,356,250 bases.
  - **The example.** In {0,1,2}, {0,1,3}, {0,1,4}, {0,2,3}, {2,4,5}, {3,4,6}, each of 5 and 6 is two from every one of 0 to 4, but
    no bond holds 5 and 6.
  - **The fix.** "Its failure needs eight and six" should read "it first fails on seven distinctions with six knots". The census
    stopped at four knots, so it could not see this. **Narrowing.**

## 2. The nine languages (the owner's flag; the right unit)

- **The counts check.** The referee's own count (`referee_metric_laws.json`) gives 34 laws passing K1 and K2, in 9 classes under
  reordering places and switching every value at once, and in 5 classes under reordering and every switch. The nine named
  representatives cover the nine classes, with 2, 1, 3, 2, 6, 2, 6, 6 and 6 laws.
- **Why nine is the unit for "copies of one law".**
  - Reordering places is a symmetry of base-building, since a knot may place its law in any order. So is the global flip, which
    keeps every set's freedom.
  - A single-place switch is a symmetry of a given base's bonds. But switching one distinction changes its place in each knot that
    holds it, which may be different places in different knots, so it turns copies of one law into a mixture.
  - So five classes would wrongly merge, for instance, not-all-equal bases with betweenness bases.
- **The theorem needs a failing base per language, and has one.** Six come at (4, 2), the twisted R5 at (4, 3), and R5 at seven
  distinctions (above) or T5's eight.

## 3. The scoring of P3b and P6 (the owner's flag; both rightly failed)

- **P3b** said neither R5 language fails within six distinctions and four knots. The twisted R5 fails at (4, 3), so it failed.
  - The referee's search adds that R5 itself fails at (7, 6). So the advisor's "R5 passes" is right only within the census's
    bound.
- **P6** said every infinite failure under not-all-equal has a correlated pair. The pair 3, 4 above is fully independent, so it
  failed. Its exact arithmetic is confirmed: the joint counts 6, 6, 6, 6.

## 4. Smaller points (Not a block)

- **"Bond distance is a metric exactly where knots compose".** As a base-level statement this is more than is proved.
  - T1 gives one direction: elimination makes a metric. The converse holds law by law (the theorem), not base by base.
  - Not-all-equal trees and the tori checked are metric, although not-all-equal knots do not compose.
  - The "Why" paragraph's "the triangle inequality is composition" is an interpretation.
  - Write "a metric on every base of one law exactly when the law's knots compose".
- **Known results** are rightly cited once: Whitney's equivalence, minimal non-shattered sets, Horn closure, and the program's
  KNOT-CIRCUITS and BOND-CHAIN.

## Fixes for the thread (listed for the owner, not folded in)

1. **R5's smallest failure.** It first fails on seven distinctions with six knots (8,190 of 1,356,250 bases; example above), not
   eight. None fails on six distinctions with up to eight knots, or on seven with five. Replace "its failure needs eight and six",
   and note that T5's base is not the smallest. **Narrowing.**
2. **"Exactly where knots compose".** Scope it to laws: "a metric on every base of copies of one law exactly when the law is
   parity". Not-all-equal trees and tori are metric without composing. **Narrowing (wording).**
3. **The twisted R5 count.** 12 failing bases of 108 on distinct triples, or of 216 if two knots may share a triple. Say which.
   **Not a block.**

## How the work was split

- **The referee:**
  - read the note, the pre-registration, proofs T1 to T5, and `metriclib.py`;
  - checked the proofs by hand;
  - wrote `referee_metric.py`: its own laws and languages, states, bond matrix with infinity, the proofs' bases, the smallest
    failures per language, random parity bases, R5 one size past, and not-all-equal meeting once on eight distinctions.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_metric.py`.**
- **`referee_metric_laws.json`, `_bases.json`, `_smallest.json`, `_parity.json`, `_r5.json` and `_nae8.json`.**

Reproduce, from `research/BOND-METRIC-20261118-001/referee-R1/`:

```sh
for p in laws bases smallest parity r5 nae8; do ../../../.venv/bin/python -B referee_metric.py $p > referee_metric_$p.json; done
```
