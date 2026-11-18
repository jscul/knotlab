# Referee report CUBE-DOUBLING-R1 (fresh code, no Codex)

**Verdict: Confirmed. No Block.**
- **What holds.** The proof is correct. The referee checked L1 to L5 and the induction line by line, and its own code (which shares
  nothing with `check.py` or `rules.py`) agrees one size past every frozen check:
  - **L4.** Every admitted extension of Q₅ with up to three knots: 112 at the least cost, 80 subdivisions and 32 pendants. Each one
    equals the single knot the proof names.
  - **L5, found by search.** After either step from Q_s, s = 1 to 5, the zero-cost steps are exactly the fills of the 2^s − 1
    unoccupied orientations. The search does not use the certificates, and no zero-cost step goes against the constants.
  - **The certificates themselves** work to s = 8: 255 distinct fills in each class.
  - **"Every tie rule."** From one knot, every class of base reachable by cheapest steps was enumerated to n = 33. The cube comes at
    4, 8, 16 and 32, each the only class. At every reachable base before a cube, the free steps are exactly the fills of every
    unoccupied orientation.
- **What changes.**
  - **The theorem is stronger than stated.** It holds for any cap of three or more knots per step, because L1 and L4 do not depend
    on the number of knots.
  - **A99 is missing** from four of the places that quote the result.
  - **The peek** shows P3's two cube clauses before the freeze, not one.
  - **The unpredicted finding has exact bounds:**
    - under every tie rule the new order arrives between n = 2^d + 2 and n = 2^d + 2^(d−1) + 1;
    - the referee gives a short proof;
    - the bound is computed for d = 2, 3, 4.
- **What is known.**
  - The ingredients are classical: hypercube cut systems, lattice dimension, and expansions (Mulder, Chepoi).
  - No source in the search describes this growth or its theorem.
  - **Why the expansion theorems do not cover it.** The rule fills orientations outside the median hull of what is present, which
    Mulder's median expansion would not. So the cube growth is not median closure.

## What holds

- **L1 (zero-cost steps are fills).**
  - **Why.** Under A99, N′ = N means p is forced on every state, so it has a value on each state pair. On the constants only a
    middle knot forces p, and it forces p to their value (L2). So p has an orientation, and no split is added.
  - **Checked** (`referee_cube.py` items 2 and 3):
    - every complement-respecting assignment of p was tested, including those against the constants;
    - after either step, to s = 5, and at every reachable base to n = 33, no zero-cost step goes against the constants.
- **L2 (forcing).** Correct, and rederived from the bit rule B(x, y, z) ⇔ not (x = z ≠ y).
  - **The middle knot** forces p to u's value where u and v agree. That is consistent with o iff A(u) ∩ A(v) = ∅.
  - **The end knot B(u, v, p)** forces p to v's value where u ≠ v. That is consistent iff A(v) ⊆ A(u), and it covers
    A(u) \ A(v).
  - **The constants.** Only middle knots cover the constants.
- **L3 (certificates survive fills; the owner's monotonicity question).**
  - **The proof.** A fill keeps N and keeps every split (each split's states gain p on one side). It changes no distinction's
    orientation.
  - Forcing (L2) depends only on the orientations of the knots' distinctions and on the state pairs. So a certificate stays a
    certificate.
  - **Checked directly** (item 3). At every one of the reachable classes before each cube (for instance 276 classes at n = 24), the
    free steps are exactly the fills of every unoccupied orientation. That is L3 and L5 together, on every base the rule can reach.
- **L4 (the cheapest steps from Q_s).** By the intersection closure of all knots' allowed masks (item 1):

  | s | Admitted extensions | At least cost (N + 2) | Subdivisions | Pendants |
  | --- | --- | --- | --- | --- |
  | 2 | 13 | 8 | 4 | 4 |
  | 3 | 45 | 20 | 12 | 8 |
  | 4 | 145 | 48 | 32 | 16 |
  | 5 | 453 | 112 | 80 | 32 |

  No extension is free. Each least-cost extension is classified by the pair of old states that doubles, and each equals the state
  set of the single knot B(u, p, v) or B(v̄, v, p) that the proof names.
- **L5 ("every unoccupied orientation"; the owner's first point).**
  - **By hand.** Every A set and every consistency condition in both classes holds. The orientations listed are exactly the
    unoccupied ones:
    - for a subdivision, (1, 0, w) with w ≠ w₀, and (0, 1, w) for every w;
    - for a pendant, (x, 1) with x ≠ c.
  - **By search, without the certificates** (item 2). After a subdivision and after a pendant from Q_s, s = 1 to 5, the zero-cost
    admitted extensions with up to three knots are exactly the 1, 3, 7, 15 and 31 fills. For s ≤ 3 the full closure agrees.
  - **The study's certificates, in the referee's semantics.** They work for s = 1 to 8 in both classes, giving 1, 3, 7, …, 255
    distinct fills.
- **The theorem, under every tie rule** (the owner's second point; item 3).
  - **What the proof uses.** Only the existence of a zero-cost step, and that every zero-cost step is a fill (L1). So any choice
    among the cheapest steps works.
  - **What the referee enumerated.** Every class of base reachable from one knot, the line of three, by any sequence of cheapest
    steps, up to renaming. Every tie rule, including one that reads the history, stays inside this set.

  | n | 4 | 8 | 16 | 17 | 20 | 24 | 28 | 32 | 33 |
  | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
  | Classes | 1 (Q₂) | 1 (Q₃) | 1 (Q₄) | 2 | 62 | 276 | 44 | 1 (Q₅) | 2 |
  | States | 6 | 8 | 10 | 12 | 12 | 12 | 12 | 12 | 14 |

  The states equal 2⌈log₂ n⌉ + 2 at every n from 4 to 33.
- **The exact distribution.** Under the study's weighting (uniform over distinct cheapest extensions), the referee's numbers of
  orders equal the study's to the last digit: 0.4 at n = 10, 0.37778 at 18 and 0.85055 at 20.

## 1. The theorem holds for any cap of at least three knots (Not a block; a strengthening)

- **What the note says.** Its Limitations read: "With fewer knots per step the free fills do not exist (S2); with more, other free
  steps may."
- **Why other free steps cannot exist.**
  - L1 does not use the number of knots: every zero-cost step is a fill, whatever the cap.
  - L4 characterises the least-cost extensions of Q_s by their state sets. Those extensions are the same under any cap, since the
    one-knot steps already reach them.
  - L5 needs three knots, and a larger cap keeps the certificates.
  - So the theorem holds for every cap K ≥ 3, and for an unbounded number of knots per step.
- **Checked with up to four knots** (item 4, s = 2, 3):
  - from Q_s, the least cost is still N + 2, with 8 and 20 extensions;
  - after either step the zero-cost extensions are still exactly the 3 and 7 fills.
- **Fix.** Write "for any cap of three or more knots per step" in the theorem, and drop "with more, other free steps may".

## 2. Where the dependence on A99 is stated (the coordinator's question; Not a block)

- **Why A99 matters.** L4 uses A99: N′ − N counts the old state pairs that allow both values of p. Without A99, a step that drops
  old states could be cheaper. So the theorem is a theorem about A99's move set.
- **Stated.**
  - The note's Limitations and its goals section ("A99 stays assumed; this theorem holds under it").
  - The proof's Words ("As in A99").
  - The objects row.
- **Missing.**
  - The intuition entry ("can be reached by three knots touching what is already there, without adding a state"). It names neither
    betweenness knots nor that old states are kept.
  - The G1 and G16 checkpoint rows. G1 names "up to three betweenness knots per step" but not A99.
  - The A97 line ("proved the cheapest law's cube growth for every size").
- **A99's own entry.** It is not updated. Its "Rests on it" still cites the computed cube growth, and it has no history line for
  the theorem.
- **Fix.**
  - Add "(A99: betweenness knots, every old state kept)" in those three places.
  - In A99, change "Rests on it" to "the cheapest rule grows cubes (proved, CUBE-DOUBLING)", and add a history line.

## 3. The disclosed peek and P3 (Not a block)

- **What was seen.** The pre-registration says P3's "last clause" was seen. The class counts printed to n = 16 also show one class
  at n = 8, so both cube clauses were in view.
- **What was already known.** STATE-RULES's runs had already shown Q₃ and Q₄ in 40 of 40 runs and Q₅ in 5 of 5.
- **So P3 tests little.** Only the state counts and the new range n = 17 to 20 are a test. P3 carries little predictive weight.
- **Nothing rests on it.** The result is a proof. The referee's enumeration was made without the peek, and covers every tie rule to
  n = 33, including Q₅ at 32.
- **Fix.** Write "both cube clauses (Q₃ at 8 and Q₄ at 16) were visible" in the disclosure.

## 4. When the new order arrives (the unpredicted finding, sharpened)

- **The study's finding.** It reports four orders at n = 10 with probability 0.4 and at n = 13 with probability 1. The referee's
  enumeration gives the same, and the same shape at each doubling:

  | d | First n with d + 1 orders in some run | First n with d + 1 orders in every run |
  | --- | --- | --- |
  | 2 | 6 | 7 |
  | 3 | 10 | 13 |
  | 4 | 18 | 25 |

  That is, between n = 2^d + 2 and n = 2^d + 2^(d−1) + 1.
- **A short proof (the referee's).**
  - **Subdivision class.** The two halves a and b of the doubled split are nested (no point lies at (0, 1, ·)). So they fit in one
    chain, and the number of orders λ is d.
    - The first fill at some (0, 1, w) makes a and b cross. Then all d + 1 splits cross pairwise, and λ = d + 1.
    - Before that, the rule can fill at most the 2^(d−1) − 1 points (1, 0, w), w ≠ w₀.
  - **Pendant class.** The new split t = {p₀, fills…} is compatible with every old split on which all its points agree, so λ = d.
    - λ becomes d + 1 when t's points differ from c on every split.
    - Before that, the rule can fill at most the 2^(d−1) − 1 points that agree with c on one fixed split.
  - **Both bounds are reached.** The earliest is the first fill (0, 1, w), or x = c̄. The latest comes after the 2^(d−1) − 1 points
    that avoid it.
- **The reading.** In the subdivision class the new order arrives exactly when the rule first fills an orientation outside the
  median hull (§5).
- **Fix.** The note's "the new order arrives with the first fills after the split is added" can give these bounds.

## 5. What is known, and what this adds (the novelty question)

John's direction applies here: folklore is publishable, so this section reports what is known and what the program's perspective
adds. A correction would be due only where a novelty claim fails, and none does. The note's own wording is suitably hedged: "new as
far as I know", "may be folklore … cited, not held back".

- **Known, with sources.**
  - **The cube's cut system and its lattice dimension.** λ(Q_d) = d: d pairwise crossing splits need d chains (Eppstein, "The
    lattice dimension of a graph", European J. Combin. 26, 2005).
  - **Mulder's convex expansion theorem.** A graph is a median graph iff it is obtained from K₁ by a sequence of convex expansions
    (Mulder, 1978).
  - **Chepoi's theorem.** A graph is a partial cube iff it is obtained from K₁ by expansions (Chepoi, 1988).
  - **The hierarchy.** Convex expansions give median graphs, isometric ones almost-median graphs, connected ones semi-median graphs.
  - Both theorems are as cited in Ovchinnikov's survey [Partial cubes: structures, characterizations, and
    constructions](https://arxiv.org/pdf/0704.0010) and Klavžar's preprints on expansion procedures
    ([one](https://users.fmf.uni-lj.si/klavzar/preprints/convex-lemma-scan.pdf),
    [two](https://users.fmf.uni-lj.si/klavzar/preprints/38320p.pdf)).
  - **Median betweenness.** Sholander characterised median betweenness by ternary axioms. Medians in the hypercube are
    coordinatewise majorities ([a survey of betweenness axiomatics](https://home.iitm.ac.in/naru/mypapers/axiom-blk.pdf); Bowditch's
    [notes on median algebras](https://warwick.ac.uk/fac/sci/maths/people/staff/brian_bowditch/median-algebras.pdf)).
  - **The knot on states.** On states, B(x, y, z) holds at every state iff y lies between x and z coordinatewise. That is the
    hypercube's geodesic betweenness. As a constraint it is NAE(x, ¬y, z), the program's own earlier reading.
- **Not found.**
  - **What the search covered.** Expansions of partial cubes and median graphs; betweenness axiomatics; hypercube intervals and
    medians. The referee searched rather than relying on the advisor's memory.
  - **What it did not find.** A cheapest growth under three-place betweenness constraints, or a theorem that it reaches the cube at
    every doubling.
  - **Where the step analysis stands.** L1, L2 and L4 are elementary coordinatewise reasoning. A specialist would likely regard them
    as routine.
- **Why the expansion theorems are not this result** (item 4). The rule does not grow by median closure.
  - **After a subdivision from Q_s.** The median hull of the occupied orientations is Q_{s−1} × (a path of three points), with
    3·2^(s−1) points (6, 12, 24, 48 for s = 2 to 5). The rule fills all 2^(s+1). The reason is that a coordinatewise majority keeps
    a ≥ b, so the points (0, 1, w) never enter the hull.
  - **After a pendant.** The median hull adds no point at all: 5, 9, 17 and 33 occupied stay 5, 9, 17 and 33. Yet the rule fills
    every (x, 1).
  - **What does reach them.** The end knots, which force p beyond a point (a "ray"), not between two. Median closure has no
    counterpart for them. So the cheapest rule's free room is the whole cube of its splits, not a median graph's hull.
  - That is a substantive difference from Mulder's picture, not only a change of words.
- **What the perspective adds.**
  - **The reading.** Built from knots alone, the cheapest continuation is forced to fill the cube of its own splits. It gains one
    order at each doubling.
  - **The certificates in knot terms.** One interval and two rays.
  - **The bound of §4** on when the new order arrives.
  - **The contrast with median closure.** The cheapest continuation crosses splits that median growth would keep nested.

## 6. Smaller points (Not a block)

- **L1's order of argument.** L1 says "p has an orientation" before L2 shows that only a middle knot forces p on the constants, and
  forces it to their value. A one-line forward reference would close the gap; the referee's search confirms the fact.
- **Scope.** "The cheapest law never keeps two orders" (G1) is said of A99's move set, from one knot. Keep it so.
- **The Q₁ base case.** The line of three is Q₁ after either kind of step (both give a line), so L5 with s = 1 applies.

## Fixes for the thread (listed for the owner, not folded in)

1. **The strengthening.** "Any cap of three or more knots per step" in the theorem and its quotes; drop "with more, other free steps
   may". **Not a block.**
2. **A99.**
   - Name it in the intuition entry, the G1 and G16 rows and the A97 line.
   - Update A99's "Rests on it" and add a history line.

   **Not a block.**
3. **The disclosure.** Both cube clauses were visible. **Not a block.**
4. **Optional.**
   - Give the arrival bounds of §4 and the median-hull contrast of §5 in the note.
   - Replace "Mulder and Chepoi (related, from the advisor's memory and not checked)" with the checked citations.
   - Add L1's forward reference.

## How the work was split

- **The referee:**
  - read the note, the pre-registration, the proof, `check.py` and the results;
  - checked every lemma by hand;
  - wrote its own semantics, closure, forcing search, class enumeration (sets of orientations up to the cube's symmetries), the
    lattice dimension, the median hull and the four-knot check (`referee_cube.py`);
  - searched the literature.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_cube.py`:**
  - 1, L4 to s = 5;
  - 2, L5 by search to s = 5, and the certificates to s = 8;
  - 3, every tie rule from one knot to n = 33;
  - 4, the median hull and four knots.
- **Outputs:** `referee_cube_1.json` to `referee_cube_4.json`.

Reproduce, from `research/CUBE-DOUBLING-20261118-001/referee-R1/`:

```sh
../../../.venv/bin/python -B referee_cube.py 1 > referee_cube_1.json
../../../.venv/bin/python -B referee_cube.py 2 > referee_cube_2.json
../../../.venv/bin/python -B referee_cube.py 3 33 > referee_cube_3.json
../../../.venv/bin/python -B referee_cube.py 4 > referee_cube_4.json
```
