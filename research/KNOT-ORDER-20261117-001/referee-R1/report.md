# Referee report KNOT-ORDER-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **What holds.**
  - K1 to K7 are correct as proofs, with one gap in K4's proof, which closes in two lines.
  - B passes the canonical knot test.
  - Every frozen number recomputes with the referee's own code.
  - **K4's "exactly m + 1" is stronger than claimed.** It is proved below for all 34 knots at every m, not only up to m = 8. The
    enumeration extends it to every three-place constraint, knot or not, up to m = 14.
  - The states-only rule really reads only the states. Run blind, with the distinctions renamed at random before every read, it
    still grows exact lines.
- **What changes.**
  - *The positive case of A97 rests on a different ruler from the weave's.* Under `WEAVE-LAWS-20261117-001`'s rule the line is
    frozen: it has 2n states, and its correlation falls linearly through zero. It is a ruler only in the disagreement count itself
    (A98's reading). So "the weave does not do both; a line of knots does" compares two readings.
  - *The line is a classical object.* It is the cut system of a path. In the gauge of any one distinction, it is exactly the
    up-sets of a chain: `DISTANCE-DIM-20261117-001`'s implication chain, made symmetric under flipping every value. Its order is
    the one put in by where the knots go, read back. What is new is the growth analysis.
  - *K7's two orders are the drawn grid's.*
  - *"The pattern continues itself" overstates.* An outside rule reads all the states and chooses; the states carry the
    information.

## What holds

- **Order.** The freeze, `11978fa6f`, is at 20:14:09 UTC; the run went from 20:14:16 to 20:14:39.
- **B is a knot** (the coordinator's item 3). `knotlab check --cnf "a ~b c; ~a b ~c" --loops a c --contact b` gives
  `is_knot: true`, with binding, invisible in parts and loss on erasure all true. It also reports `pairwise_definable: false`;
  see 6.
- **K1 (proved).** The proof is right for any arity:
  - with no place in [1, p], the threshold 1 up to q agrees with the (p, q) state on [p + 1, n];
  - with no place in [q + 1, n], the threshold 1 after p agrees on [1, q];
  - with no place in the middle block, the constant agrees outside it.

  The referee's exhaustive check covers every constraint on 2, 3 or 4 places that keeps every threshold, at n = 5, 6 and 7
  (1,305, 3,885 and 9,030 constraints). No exception was found. The study's `check.py` samples 300.
- **K2 (proved).** It is right, for windows of the line's own order. The strongest window-r base keeps the (1, r) state at
  n = r + 1 to r + 3 for r = 3, 4 and 5. That base restricts every window to its thresholds. At r = 3 it has 10, 16 and 26 states,
  the neighbour rule's counts, so the neighbour rule is already the strongest base of width 3.
- **K3 (proved; the coordinator's item 1, "forced").**
  - **The places are forced.** By K1, the new (1, m) state needs a constraint on {1}, [2, m] and {m + 1}. The new (m − 1, m)
    state needs one on [1, m − 1], {m} and {m + 1}. One three-place knot meets both only on {1, m, m + 1}.
  - **The excluded set is forced.** The knot must exclude 010 on (1, m, m + 1), and, by the flipped state, 101. It must keep the
    six monotone patterns. So it is B(1, m, m + 1).

  This is correct for m ≥ 2. The random-earlier rule confirms it: over 40 seeds to n = 12, the base is a line exactly while every
  chosen x was the start. The study's own seed reproduces its counts, 6, 8, 12, …, 298, 456.
- **K5 and K6 (proved).**
  - K5 follows from d = 2|i − j|.
  - K6's citation is right. `DISTANCE-ORDER-20261117-001A` statement 3(a) already covers "exclude 010 and 101", through its
    statement 1.
- **K7 (proved).**
  - B forbids a = c ≠ b inside the box, so the 1-set and the 0-set of an allowed state are each box-closed: convex in the grid
    graph.
  - In a median graph, the convex sets with convex complements are exactly the halfspaces (Mulder; Bandelt).
  - The referee recomputed 3 × 3, 3 × 4 and, one size past, 4 × 4, 3 × 5 and 4 × 5. These have 10, 12, 14, 14 and 16 states,
    each exactly the row cuts and column cuts, with d = 2·L1 and betweenness equal to the boxes.
- **The computations recompute.**
  - **R1.** 10 and 8 states at n = 4, the extras 0110 and 1001; 16 and 10 at n = 5; 8.
  - **Growth to n = 16,** one size past.
    - The start, states and inward ("spiral") rules give lines at every n, 32 states at 16.
    - The neighbour rule gives exactly 2·F(n + 1) at every n (1,220 at 14, 3,194 at 16).
    - The random rule fails as K3 says.

## 1. K4's "exactly m + 1": true for every knot at every m, but the proof has a gap (the coordinator's item 1; Not a block)

**The gap.** The proof says the single knot's places are "forced" to be the new distinction and its two neighbours "(K1, as in
K3)". But inserting between k and k + 1 creates only one new two-change state pair: every old distinction equal and the new one
different. K1 then forces only a place on each side of the new distinction, B(a, new, b) with a ≤ k < b. Adjacency needs one
more line:
- B(a, new, b) leaves the new value free exactly on the 2(b − a) old thresholds that cut between a and b, so the base has
  2m + 2(b − a) states;
- a line on m + 1 has 2m + 2, so b = a + 1.

**The referee's proof, for any three-place knot C on (new, a, b) with a < b and any m ≥ 3.** Steps 1 to 3 hold for any
constraint. Step 4 uses that a knot's excluded states are never one change apart.
1. **Every old threshold must survive.** Erasing the new distinction from a line on m + 1 leaves a line on m with 2m states. That
   must be the whole old line, and in the old order.
2. **How many old thresholds show each pattern.** Old thresholds show (x_a, x_b) = 00 and 11 on m − b + a each, and 01 and 10 on
   b − a each.
3. **C may remove at most one new value per pattern.** Removing both would kill a threshold. Each pattern left untouched doubles
   its thresholds. So the untouched patterns must cover exactly 2 thresholds. For m ≥ 3 the only ways are:
   - (A) 01 and 10 untouched, with b = a + 1;
   - (B) 00 and 11 untouched, with a and b the two ends;
   - (C) only 00, or only 11, untouched, with m − b + a = 2;
   - (D) only 01, or only 10, untouched, with b − a = 2.
4. **What each family gives.** The constraint must also keep its excluded states apart (no two at one change), and each family
   gives:
   - **(A)** B(a, new, b): the line, the m − 1 neighbour placements. The alternatives fail. NAE puts the new distinction at
     disagreement count 2m from both a and b, and a line has one pair at its largest count. "Exclude (v,0,0), (v,1,1)" puts it at
     count m + 1 from everything.
   - **(B)** B(new, a, b) or B(new, b, a): the two end placements. The alternative, "exclude (v,0,1), (v,1,0)", again puts the new
     distinction at count m + 1 from everything.
   - **(C) and (D)** force C to be three states of one parity, a not-exactly-two-class knot. The new distinction then sits at
     equal or nearly equal counts from a and b, which no position in a line on m + 1 allows: the two would have to be m or more
     places apart.

So, at every m, exactly m + 1 single three-place knots keep a line, all of them betweenness knots. X1 is now a theorem, not a
computation to m = 8.

The referee's enumeration goes further: over all 255 excluded sets, knots or not, it finds exactly m + 1 at every m from 3 to 14
(4, 5, …, 15, all of them among the 34, in three kinds: `referee_order.json`, item 3). For the constraints that are not knots,
families (C) and (D) also contain non-parity triples. These are excluded only by the enumeration to m = 14, not by the proof.

**Two slips.**
- The proof says non-betweenness knots are excluded "by `check.py`'s exhaustive search". That search is `growth.py`'s R3, and
  `check.py` checks only betweenness insertions.
- "Growing inward … every distinction is in at most three knots" is right. Each new distinction goes between the last two placed,
  which stay neighbours.

## 2. The post hoc kinds (the coordinator's item 2; Not a block)

The frozen flags were worse than "unusable": they were inverted. Each distinct constraint was stored with the first place order
the loop met, for example places (0, 1, 3) excluding {001, 110}. That is B(0, 3, 1), the new distinction between neighbours 0 and
1.
- So `betweenness` read False for every line-keeping knot at every m.
- `new_in_middle` read True only for the two end placements.

The study disclosed that the flags failed and read the kinds from the stored excluded sets. That reading is right; the referee
checked it independently. The kinds are now proved for every m (section 1). The verdict line should say what happened: "X1: the
count held as frozen; the kinds on a post hoc reading, since proved".

## 3. "Knots alone" (the coordinator's item 3; Narrowing, wording)

- **The base is knots alone.** It is a conjunction of canonical knots with no hidden distinctions, and no executor supplies an
  input to the relation.
- **The states-only rule uses only the states.** In `growth.py` it finds the ends with `ends_from_states` from the allowed states
  and picks a side with a coin. The rule's tracked order is used only to check the result.
  - The referee's blind rerun renames every distinction by a fresh random permutation before each read. It finds the ends as the
    unique pair at count 2(n − 1), and grows exact lines to n = 16 on 20 of 20 seeds.
  - It does use a supplied first knot B(0, 1, 2), a supplied fresh distinction at each step, and the names of places to write the
    new knot. Any growth rule needs these.
- **But the grower is outside the pattern.** At each step an outside rule enumerates all 2n states, computes every pair's count
  and chooses.
  - "The pattern can continue itself", "the states tell the pattern where those places are" and "Capability gained: knots alone
    build an order … and read its next placements from their states" give the pattern an agency it does not have.
  - A fair wording: "the states carry where the next knot may go. A rule that reads only the states, with no names or history,
    can continue the line. The choice among placements is the rule's."

## 4. K7's two orders (the coordinator's item 4; Narrowing, wording)

- **Which triples carry knots is the drawn grid's.** "b coordinatewise between a and c" uses the grid's coordinates: 68 box
  triples on 3 × 3 and 780 on 4 × 5.
- **The states then read that grid back.** They are the halfspaces of the drawn grid (the literature's cut system of a product of
  two paths, a median graph). The two orders are its two coordinates.
- **This is the same round trip** as `DISTANCE-DIM-20261117-001`'s implication half, which its referee named a drawn order read
  back.
- **The study does say** "this meeting pattern is given here; no growth rule for it is claimed".
- **But two summaries drop "drawn":** "Two independent orders, statically" and A97's "betweenness on every box of a grid holds two
  independent orders". The coordinator's summary does too ("two independent orders from knots alone").
- **A fair wording:** "on a drawn grid, box betweenness reads back the grid's two orders".

## 5. How far the headline reaches for A97, and what is classical (the coordinator's items 5 and 6; Narrowing)

- **One dimension, with a ruler different from the weave's.**
  - The headline and the note scope the result to one dimension; that is fair.
  - But the A97 paragraph says "The weave, the critical two-way pattern, does not do both (`WEAVE-LAWS-20261117-001`). A line of
    knots does." The two studies' rulers differ:
    - *the weave study* read a ruler as the log of the pair-count deviation growing linearly, which needs a disordered base;
    - *here* the ruler is the disagreement count itself, d = 2|i − j|, with exact additive betweenness (A98's reading).
  - *By the weave study's own rule, the line is frozen.* Its states per distinction are (2n)^(1/n) → 1 (1.349 at n = 10). Its
    correlation from an end is 1 − 2r/n, falling linearly through zero at the middle, so −log|C| is not a ruler.
  - Under this study's ruler, the weave has none: no distinction lies between two others in its disagreement count
    (`DISTANCE-ORDER-20261117-001`).
  - So "a line does both" holds under the disagreement-count reading, at the price of a nearly frozen base. The note says the
    price ("2n states"). It should also name the reading, and drop the comparison with the weave or make it within one reading.
- **The line is classical, and it is DISTANCE-DIM's chain.**
  - It is the cut system of a path, with d the path's cut metric; the note names this.
  - The note does not say what K3's gauge remark already shows for every state. In the gauge y = x ⊕ x_start, the line's 2n
    states are exactly the n up-sets of the chain start < 2 < … < n, each from two states (a state and its flip). The referee
    checked this at n = 4, 6, 8 and 10.
  - So the line is the implication chain of `DISTANCE-DIM-20261117-001` made symmetric under flipping every value. Its order,
    read back, is that chain's specialization order (Alexandrov; Birkhoff). That is a drawn order read back, as its referee noted.
    Here the order is drawn by where the knots go.
- **What is the study's own.**
  - The growth analysis:
    - the straddle lemma (elementary);
    - which single knots extend a line (now proved for every knot at every m);
    - the hub for one-sided outward growth, and no hub inward;
    - the failure of local growth;
    - the reading of placements from the states.
- **What is classical and should be named as such.**
  - *Named already:*
    - the betweenness of a linear order and its axioms (Huntington and Kline 1917; Huntington 1924);
    - the order up to reversal (Fishburn);
    - cut systems of paths and grids (Buneman; Deza and Laurent);
    - Opatrný's NP-completeness.
  - *To add:*
    - the line as the flip-symmetric up-sets of a chain;
    - median-graph halfspaces (Mulder; Bandelt) for K7;
    - the neighbour rule's 2·F(n + 1), the folklore count of strings in which no interior value stands alone. The advisor gave it,
      and it is not the study's.

## 6. Smaller points (Not a block)

- **"Pairwise" has two meanings in the program.**
  - In the glossary of the Intuitions guide, a relation is pairwise when its two-place projections define it, and no knot is
    pairwise ("no 2-CNF defines a knot"); `knotlab` reports `pairwise_definable: false` for B.
  - This study (K6, "It is a not-all-equal knot with b read flipped, so it is pairwise") uses it for "its pair counts carry the
    base". So does `WEAVE-LAWS-20261117-001` ("only the not-all-equal class is pairwise"), as does A97's newest text.
  - A glossary reader reads "B is pairwise" as "B is not a knot". One word should keep one meaning. A phrase such as "read from
    pair counts" serves the second; the advisor should be consulted on any new word.
- **"Spiral"** is a word from two dimensions for the program's own rule, and the rule nests inward along one gap. "The inward
  rule" says what it does.
- **`check.py`'s K1 check** samples 300 random constraints, although its docstring and the proof read as exhaustive. The referee's
  check is exhaustive to four places.

## Fixes for the thread (listed for the owner, not folded in)

1. **A97 and the headline.**
   - Name the ruler: the disagreement count with exact additive betweenness (A98's reading).
   - Say that, by `WEAVE-LAWS-20261117-001`'s rule, the line is frozen.
   - Make the weave comparison within one reading, or drop it.
   - Name the line as the flip-symmetric implication chain (the up-sets of a chain in the gauge of one distinction), the order put
     in by where the knots go and read back.

   **Narrowing.**
2. **K7.** Say "on a drawn grid … reads back the grid's two orders" in the note, A97 and any summary. **Narrowing.**
3. **"Knots alone".** Keep it for the base. Replace "the pattern can continue itself" and "read its next placements from their
   states" (the G1 and G16 checkpoint) with wording that puts the reading and the choice in an outside rule that uses only the
   states. **Narrowing, wording.**
4. **K4's proof.**
   - Add the count, 2m + 2(b − a), that forces neighbours.
   - Optionally replace "excluded by `check.py`'s exhaustive search for m ≤ 8" with the referee's proof for every knot at every
     m, and its enumeration of every three-place constraint to m = 14 (section 1).
   - X1's line: "count as frozen; kinds post hoc, since proved".

   **Not a block.**
5. **Classical names, and words.**
   - Add the classical names in 5.
   - Settle "pairwise", here and in `WEAVE-LAWS-20261117-001` and A97.
   - "Spiral" → "inward".
   - Describe `check.py`'s K1 check as sampled.

   **Not a block.**

## How the work was split

- **The referee:**
  - read the pre-registration, the proof, `check.py`, `growth.py`, the results, the post hoc kinds and the note;
  - checked K1 to K7 by hand, and proved K4's count for every knot at every m;
  - wrote its own state enumeration, growth rules (with a blind states rule), single-constraint classification over all 255
    excluded sets, exhaustive K1 and K2 checks, grid cuts and the gauge identity;
  - ran the canonical knot test on B.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_order.py` and `.json`.** The items are numbered 0 to 7:
  - 0, the knot test of B;
  - 1, R1;
  - 2, growth to n = 16, the blind states rule over 20 seeds, the random rule with the study's seed and over 40 seeds;
  - 3, every single three-place constraint at m = 3 to 14;
  - 4, K1 to four places at n = 5 to 7;
  - 5, K2;
  - 6, K7 to 4 × 5;
  - 7, the gauge identity and the line's correlation profile.

Reproduce, from `research/KNOT-ORDER-20261117-001/referee-R1/`:

```sh
../../../.venv/bin/python -B referee_order.py > referee_order.json
```
