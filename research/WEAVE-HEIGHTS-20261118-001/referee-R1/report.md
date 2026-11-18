# Referee report WEAVE-HEIGHTS-R1 (fresh code, no Codex)

**Verdict: Confirmed. No Block.**
- **Every proof checks by hand.** That covers Lemma 0 to Theorem 7 and Lemma 8, with the three places the owner asked about read
  line by line: Proposition 3's parity bookkeeping, Lemma 0's topology, and Lemma 5's use of the cited theorems.
- **The referee's own code reproduces every check, two sizes past the study where it went to eight knots and one size past where it
  went to twelve.**
  - Proposition 3 holds set by set on every disc to ten knots: 24,146,944 sets (the study had 833,536, to eight). It also holds on 300
    random discs of twelve knots: 3,043,328 sets.
  - A control with the bound lowered to 3(m − 3) fails on 8.6 million of the sets to ten knots. So the check can tell the bound apart
    from its neighbour.
  - Flagness, convex balls, the triangle condition, no level knot, D + D = 3·steps and Lemma 8's identities hold on every disc to ten
    knots, on the 300 discs of twelve, and on 3,000 random discs each of thirteen and fourteen knots.
  - Theorem 7 one size past: no bonded pair below steps + 1 among 227,039 bonded pairs on 2,500 random discs of thirteen knots (the
    referee's DOUBLE-MEET-R1 census).
- **The citations are only partly checked.**
  - The statements Lemma 5 uses are the standard ones, and secondary sources confirm them: the characterisation of bridged graphs,
    convex balls, and bridged ⇒ weakly modular (so the triangle condition).
  - The theorem numbers could not be checked against the primary texts, which were not reachable. The note already says so.
  - The conclusions the citations supply are themselves checked mechanically to fourteen knots.
  - **Not a block.**
- **DOUBLE-MEET's fold-in (`b3afe07ca`) is faithful.** Two stale phrases remain (see Fixes).

## What holds

| Check | Referee | Study |
| --- | --- | --- |
| Lemma 1's count (states = 2 × consistent falling choices) | every disc to 8 knots (1,080), no exception | 1,080 |
| Proposition 3, set by set | every disc to 10 knots (7,917; 24,146,944 sets, 16,577,093 constrained) and 300 random discs of 12 knots (3,043,328 sets), no exception | discs to 8 knots, 833,536 sets |
| Control: the bound 3(m − 3) in place of 3(m − 2) | fails on 8,639,470 sets to 10 knots and 969,738 at 12 | not run |
| Flagness (Lemma 0) | to 10 knots and 6,000 random discs of 13 and 14, no exception | to 12 knots |
| Convex balls; the triangle condition (Lemma 5's ingredients) | 809,727 balls, 1,362,036 triangle cases, no exception | to 12 knots |
| No level knot (Lemma 5) | none | none |
| D(x, y) + D(y, x) = 3 s(x, y) (Lemma 6) | every pair, no exception | to 12 knots |
| Lemma 8's two identities | every lone distinction, no exception | to 12 knots |
| Theorem 7, b ≥ steps + 1 | none below on 2,500 random discs each of 12 and 13 knots (DOUBLE-MEET-R1: 199,346 and 227,039 bonded pairs) | 3,365,574 bonded pairs at 12 knots |

- D is the referee's own Dijkstra on the walk weights: 1 forward, 2 backward.
- The least cyclic D-sum of every subset comes from the referee's own Held–Karp.
- Constrained sets are read from the states. A set counts as constrained by the criterion when it contains a tight subset.

## 1. Proposition 3's parity bookkeeping (pressed hardest)

Every step holds.

- **The difference constraints.**
  - With h(s) = r_s + 6k_s, the constraint g(t) − g(s) ≤ D(s, t) is k_t − k_s ≤ (D − r_t + r_s)/6. For integer k this is the floor W.
  - Integer difference constraints with integer weights are feasible exactly when there is no negative cycle (Bellman–Ford gives an
    integer solution). A negative closed walk contains a negative simple cycle.
- **The residues.**
  - a_i ≡ 0 (mod 3) by Lemma 2(i) and r ≡ c.
  - ⌊a_i/6⌋ = (a_i − 3ε_i)/6, and this is right for negative a_i too.
  - The r's telescope, so Σ a_i = L and Σ ε_i ≡ L/3 (mod 2).
- **The flips.**
  - Changing σ(s_i) keeps r_i ≡ c (mod 3) and changes its parity, so r_i moves by ±3. That shifts a_i and a_{i−1} by 3 each and flips
    both ε's.
  - Flips of adjacent pairs around an m-cycle generate exactly the even-weight vectors. So the reachable ε are exactly those with
    Σ ε of the fixed parity, and the largest reachable sum is m or m − 1, as stated.
- **The direction "short cycle ⇒ constrained".**
  - L/3 ≤ m − 2 is enough in both parity cases.
  - The proof's "force L/3 ≤ m − 3" is true but stronger than needed.
- **The direction "constrained ⇒ short cycle".**
  - L < 3Σ ε with the same parity gives L/3 ≤ Σ ε − 2 ≤ m − 2.
  - m = 2 is excluded because D(s, t) + D(t, s) is a positive multiple of 3. (It is in fact 3 s(s, t) ≥ 3 by Lemma 6, but the proof
    does not need Lemma 6 here.)
- **Corollary 4's subset step** is right: a bond is a minimal constrained set, so a tight sub-collection of it must be all of it.
- **The mechanical check is sharp.** The bound 3(m − 2) agrees with the states on every set. Lowering it by one notch, to 3(m − 3),
  disagrees on 52% of the constrained sets.

## 2. Lemma 0's topology

Every step holds.

- **The union is a surface with boundary.** A lattice pair lies in two lattice knots, so the pairs of T lie in one or two knots of T.
  The no-pinch condition makes the knots at each distinction a fan or the full wheel of six, so each point has a half-disc or disc
  neighbourhood.
- **It is a disc.** A compact connected surface in the plane has genus 0, so χ = 2 − (boundary curves). Then V − |E| + |T| = 1 gives
  one boundary curve, and the surface is a disc.
- **The flagness argument.**
  - Suppose a lattice knot k ∉ T has all three of its pairs in E. Then each pair lies in exactly one knot of T, so all three are
    boundary pairs.
  - A simple closed curve that contains a closed 3-cycle is that 3-cycle, so the boundary is ∂k.
  - By Schoenflies the disc is then k or the closure of the unbounded side. Neither is possible: the first means T = {k} ∌ k, and the
    second is not compact.
- **The remark on fans of five** (in Lemma 5) is right. Flagness is exactly what stops the two end neighbours of a five-knot fan from
  being adjacent through the missing sixth knot.

## 3. Lemma 5 and its citations

- **The argument after the citations is correct.**
  - Suppose a knot {a, b, c} is level at t ≥ 1. The triangle condition gives a common neighbour of a and b at t − 1.
  - By flagness the common neighbours of a and b are the far distinctions of the two lattice knots on {a, b}. One of them is c, at
    distance t, so the other, c′, is in V at distance t − 1.
  - In the same way a′ = b + c − a and b′ = c + a − b are in V at distance t − 1. Since a′ − b′ = 2(b − a), they are not adjacent.
  - c is adjacent to both, so it lies on a geodesic of length 2 between two points of the ball of radius t − 1. Convexity puts c in
    that ball: a contradiction.
- **The hypotheses of the characterisation are verified correctly in the proof.**
  - With no 4-clique, the clique complex is the 2-complex, and it is simply connected by Lemma 0.
  - By flagness, each distinction's link is the path or the 6-cycle of its fan or wheel, so it has no induced C4 or C5.
- **The cited statements,** checked against secondary sources (the primary texts were not reachable):
  - **Characterisation.** Bridged graphs are exactly the graphs whose clique complexes are simply connected and whose vertex links
    have no induced 4- or 5-cycles. Chepoi, Adv. Appl. Math. 24 (2000), 125–179, DOI 10.1006/aama.1999.0677. These are also the
    1-skeleta of systolic complexes, Januszkiewicz–Świątkowski, Publ. Math. IHÉS 104 (2006).
    - Confirmed as the standard statement.
    - The theorem number is not checked.
    - Some secondary sources trace the local-to-global form to a 1999 preprint.
  - **Convex balls.** Bridged graphs are exactly the graphs in which the balls around convex sets are convex. Soltan–Chepoi 1983;
    Farber–Jamison, Discrete Math. 66 (1987), 231–247.
    - Confirmed.
    - Lemma 5 uses the special case of balls around a vertex.
  - **The triangle condition.** Bridged graphs are weakly modular, so they satisfy it. This is classical (Chepoi 1989). Chalopin,
    Chepoi, Hirai and Osajda, Mem. AMS 268, no. 1309 (2020), is a correct survey citation for it.
    - Confirmed.
    - The theorem number is not checked.
- **What this means.**
  - The proof of Lemma 5 is correct given standard, correctly stated theorems. Only their numbering is unverified, and the note's
    Limitations already says so.
  - Independently of the sources, the two ingredients themselves (convex balls, the triangle condition) and Lemma 5's conclusion
    hold on every disc the referee checked, to fourteen knots.
  - **Not a block.** The study's direction 3, a citation-free proof, would remove the dependence. A short route: the weave's discs
    are planar triangulations with interior degree 6 and links that are paths or 6-cycles (6-large), so a direct
    boundary-turning argument is plausible.

## 4. Lemmas 1, 2, 6, 8 and Theorem 7

All hold as written.

- **Lemma 1.**
  - Each knot has exactly one equal pair, so ω sums to 0 around each knot and integrates by simple connectivity.
  - h ≡ c (mod 3), because every increment is ≡ 1.
  - h is unique up to 6, because parity decides every increment.
  - The count Q1 checks the bijection directly.
- **Lemma 2(iii).** h(b) ≤ h(a) + 1 and h(a) ≤ h(b) + 2 put the increment in [−2, 1], and since it is ≡ 1 (mod 3), it lies in
  {−2, 1}.
- **Lemma 6.**
  - "≥": Lemma 5 makes the three changes of δ around each knot exactly −1, 0 and +1, so ω₁ and ω₂ each have one −2 per knot.
  - Then h₁ − h₂ = 3δ + const, and Lemma 2(ii) gives the bound.
- **Theorem 7.** It uses only the triangle inequality for D (a shortest-walk quasi-metric) and Corollary 4.
- **Lemma 8.**
  - u → v is forward, so D(s, v) ≤ D(s, u) + 1 and D(u, t) ≤ 1 + D(v, t).
  - So entering x from v, and leaving it to u, is never worse.
- **The folklore rule.**
  - The height function (Blöte–Hilhorst; Nienhuis–Hilhorst–Blöte), integer difference constraints (Thurston) and bridged graphs
    are cited once, with "what this adds". That is the right treatment.
  - The criterion for constrained sets and the round-trip identity are fairly claimed as the program's. The note says no literature
    search was run.
  - No novelty claim is false.

## 5. DOUBLE-MEET's fold-in (`b3afe07ca`)

- **Faithful to DOUBLE-MEET-R1.**
  - The Block on P5 is recorded, with the 12-knot disc and the two 13-knot discs.
  - The corrected statement is the one the referee gave: a patch fails only through lone pairs of opposite classes facing each other,
    unbonded or, from twelve knots, bonded too far.
  - "At least steps + 1" is marked sketched and computed (now proved here).
  - The CORRECTIONS entry, HISTORY, the intuition entry, A39 and the G1 row are updated, and the Referee section's numbers match the
    referee's JSON.
- **Two stale phrases remain.** Both are wording only (see Fixes 1 and 2).
  - The note's position table (`double_meet.md`, the "This attempt" row) still says "a patch is a true distance exactly when it has no
    unbonded such pair", without the qualifier.
  - A97's history line for `DOUBLE-MEET-20261118-001` still says "failures only through unbonded lone pairs". From twelve knots,
    bonded ones fail too.

## Fixes for the thread (listed for the owner, not folded in)

1. **DOUBLE-MEET's position table.** In the "This attempt" row, qualify "a patch is a true distance exactly when it has no unbonded
   such pair" with "on the census to eleven knots; beyond, bonded facing pairs can fail too". **Narrowing (wording)**, a residue of
   the Block already logged. It needs no new CORRECTIONS entry; it completes the existing one.
2. **A97's history line** for `DOUBLE-MEET-20261118-001`: change "unbonded lone pairs" to "lone pairs of opposite classes facing each
   other, unbonded or (from twelve knots) bonded too far". **Narrowing (wording)**, the same residue.
3. **Lemma 5's citations.** Keep the note's caveat that the theorem numbers are unchecked. Add that the statements are confirmed as
   standard, and that their conclusions on these graphs are checked to fourteen knots (this report). **Not a block.**
4. **Proposition 3, a cosmetic point.** "Force L/3 ≤ m − 3" can read "give L/3 ≤ m − 2 < m − 1", since that is all the step uses.
   **Not a block.**

## How the work was split

- **The referee:**
  - read the note, the proof, the pre-registration and `job.py`, and checked every proof by hand;
  - searched for the cited theorems: secondary sources were reachable, the primary texts were not;
  - wrote `referee_heights.py`. It uses the referee's own walk weights and Held–Karp, states and discs from its DOUBLE-MEET-R1
    `referee_double.py`, set-by-set freeness, the 3(m − 3) control, ball convexity, the triangle condition, Lemma 1's count, and
    Lemmas 6 and 8;
  - read the `b3afe07ca` fold-in against DOUBLE-MEET-R1.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_heights.py`.**
- **`referee_heights.json`.**

Reproduce, from `research/WEAVE-HEIGHTS-20261118-001/referee-R1/` (about two minutes on 16 workers):

```sh
../../../.venv/bin/python -B referee_heights.py > referee_heights.json
```
