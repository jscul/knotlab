# Referee report NAE-METRIC-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **The proofs hold.** C1 (Lemmas 1 and 2, with the bond structure), C2 (the block reduction), C3 (rings, any mixture) and C4 were
  checked by hand.
- **The referee's own code agrees on everything proved,** and goes one size past.
  - **Glued bases:** additivity holds on every separated triple of every complement-closed or parity base.
  - **Rings:** every ring of 3 to 10 knots with any mixture of not-all-equal and betweenness laws has b = steps + 1.
  - **Cacti:** b − 1 = steps on 150 random ones, up to 18 distinctions.
- **One Narrowing: the series-parallel conjecture (P6) fails with a single betweenness knot.**
  - On two graph-like bases whose knot graph is series-parallel (11 and 13 distinctions), all knots are not-all-equal except one
    betweenness knot, and the triangle inequality fails. Two independent freedom tests confirm it.
  - That is inside P6's stated scope ("plain or twisted", twisted being one switched knot).
  - With every knot not-all-equal, the conjecture survives on 129 more bases.
- **The owner's flags.**
  - Lemma 1's case y ∉ T, and the complement step: right (§1).
  - The ring lower bound, with all own distinctions free for twisted and mixed rings: right (§2).
  - The gluing in C2 and the block definition: right (§3).
  - The late prior-work lines changed no frozen prediction (§4).
- **One scope note.** C1's working hypothesis is that every bond through y can force y both ways. Bases mixing parity with
  not-all-equal or betweenness knots can break it, and there additivity fails. The note never claims them, but should say they are
  excluded.

## What holds

- **F1 to F3.** F1 is the join over y. F2 needs y to take both values on each side, which complement-closure gives. F3 is right:
  the missing pattern π restricted to B − y occurs and forces y to ¬π_y, and π's complement, also missing, forces it the other way.
- **Lemma 2.**
  - **Upper bound.** T = (S₁ ∪ S₂) − y.
    - Every T − t is free: values on S₂ − y allow some y, and S₁ − t is free and holds y.
    - T is constrained: the forcing along S₁ − y fixes y to ρ's value, and S₂'s missing ρ then fixes z.
  - **Lower bound.**
    - y ∉ T, because otherwise T − x and T − z cover T_R ∪ {y} and T_L ∪ {y}, and their join over y is full.
    - With y ∉ T, Lemma 1's argument gives bonds B_L ∋ x, y and B_R ∋ y, z inside T_L ∪ {y} and T_R ∪ {y}.
  - **The bond structure follows:** 𝓛's bonds, 𝓡's bonds, and every (B_L ∪ B_R) − y.
- **C4.** On a complement-closed base with both constants, {x, y, z} is a bond exactly when its pairs are separated and one of the
  three is never alone. So b ≤ 2 exactly when every separated pair has a third between them. That is a diameter statement, as the
  note says.
- **The referee's computations** (`referee_nae.py`):

  | Check | Referee | Study |
  | --- | --- | --- |
  | Glued bases: not-all-equal; betweenness with not-all-equal; four-place with three-place not-all-equal; parity with y not fixed (1,021 bases) | Lemma 1 on all; b − 1 additive on all 8,564 separated triples; the bond count identity on all | 1,000 bases, 16,719 triples, count on 858 |
  | Control: the clause "not all ones" (not complement-closed), 150 bases | additivity fails on 114 of 1,183 triples; the count on 33 | — |
  | Mixed parity, not-all-equal and betweenness in one block, 237 bases | Lemma 1 fails on 5; 49 of 1,928 triples not additive; the count fails on 14 | not claimed |
  | Rings of 3 to 8 knots, every pair exactly; 9 and 10, the 12 farthest pairs and 8 more; any NAE/betweenness mixture, 30 rings | b = steps + 1 on all 1,580 pairs; largest b = ⌊m/2⌋ + 2 on all 30; no triangle failure | rings 3 to 9, plain and one twist |
  | Random cacti of knots and rings, mixed laws, up to 18 distinctions | 150 cacti, 13,401 pairs, b − 1 = steps on all | 200 cacti |
  | Graph-like, series-parallel, every knot not-all-equal (10 to 15 distinctions) | 0 of 129 fail; with a K4 minor, 5 of 31 | 0 of 354 (plain or one twist) |
  | Graph-like, series-parallel, laws drawn at random (10 to 15 distinctions) | **2 of 133 fail**; with a K4 minor, 1 of 27 | — |

- **The mixed failures.**
  - **An example.** The left block has a betweenness knot on 1, 0, 2 with 1 in the middle, NAE(1, 3, 0), odd parity on 2, 1, 0 and odd parity on 4, 3,
    0. In it every pair {0, w} is a bond of two that forces 0 only to 1, so F3 fails. Then b(1, 6) = 2 while b(1, 0) = b(0, 6) = 1.
  - **The cause** is one-way ties, as in BOND-METRIC's twisted R5.
  - **What to add.** C1's hypothesis section names complement-closed bases and parity bases where y is free. The answer's "this
    holds for every base of not-all-equal and betweenness knots … and for parity bases too" is right as worded. It should add that
    bases mixing parity with the others are not covered, and can fail.

## 1. Lemma 1, the case y ∉ T (the owner's flag; right)

- **The setup.** T is a bond holding x, w ∈ L with T_R ≠ ∅. Both parts are free, being proper subsets.
- **The projection.** By F1 and F2, the projection onto T is {(u, r) : Y_L(u) ∩ Y_R(r) ≠ ∅}. Since T is constrained, there are u₀
  and r₀ with Y_L(u₀) = {v} and Y_R(r₀) = {¬v}.
- **A bond B′ ∋ y.** So T_L ∪ {y} is constrained, and it holds a bond B′ of 𝓛. B′ contains y, since T_L is free.
- **x is in B′.** Suppose x ∉ B′.
  - **The complement step.** F3 gives values on B′ − y forcing y to v; this is where complement-closure is used.
  - Together with r₀ (which allows only ¬v), they make a pattern of T − x missing. So T − x is constrained, against T being a bond.
  - So x ∈ B′, and likewise w ∈ B′, with |B′| ≤ |T_L| + 1 ≤ |T|.
- **The case y ∈ T.** The projection is that onto T_L ∪ {y} times all values on T_R, so T_L ∪ {y} would be a constrained proper
  subset.
- **Why the hypothesis is needed.** Without complement-closure, B′ − y may force y only to ¬v, and the step fails. The referee's
  clause control and the mixed-parity bases show it does fail then.

## 2. The ring lower bound, (iii) for twisted and mixed rings (the owner's flag; right)

- **(i)** Forgetting p_j removes K_j, so bonds missing p_j are the chain's bonds.
- **(ii)** By C1 at each joint, the chain's bonds are its runs: the two end ring distinctions and the privates between. So such a
  bond holds a whole route between x and z, with at least s + 2 members.
- **(iii) All the privates are free together.**
  - Given its two ring distinctions, a knot of either law leaves its private free under one relation and forces it under the other.
    For not-all-equal the free relation is "different". For betweenness it is "different" when the private is the middle and
    "equal" when it is an end.
  - Choose the ring distinctions so that K₁ to K_(m−1) leave theirs free. Complementing every ring distinction keeps all the
    relations and flips the forced value of p_m, so every joint value of the privates occurs.
  - The argument uses nothing about which law each knot has, so it covers any mixture, not only one twist.
- **The count.** A bond holding all the privates has at least m + 1 ≥ s + 2 members, since s ≤ ⌊m/2⌋ + 1 ≤ m − 1.
- **The referee's mixed rings agree to ten knots.**

## 3. The gluing in C2, and the blocks (the owner's flag; right)

- **The blocks.**
  - A knot's distinctions form a clique in the primal graph, so each knot lies in one block, at any arity.
  - A cut vertex of the primal graph splits the knots into groups meeting only there: a separating distinction.
- **Inside a block.** Lemma 1, applied at each cut distinction, makes b inside a block the block's own.
- **Across blocks.** Lemma 2 along the block-cut tree makes d = b − 1 additive.
- **The triangle inequality reduces to the blocks.** It is d(x, z) ≤ d(x, y) + d(y, z) + 1.
  - **Routes meeting at a cut distinction c:** the slack is 2d(c, y) + 1.
  - **Routes meeting at a block:** it reduces to the block's own inequality between the gates, with slack 1 + 2d(y, y′), or to d ≥ 0
    when gates coincide.
  - **Infinite values:** they enter only through some block's gate pair, which carries the block's own inequality.
- **No violation spans two blocks.** The referee's glued bases had none.

## 4. The prior-work lines added after the freeze (the owner's question; nothing changed)

- **The diff** between the freeze (13d727a38) and the close (284fd9df2):
  - in the pre-registration, only the two labelled prior-work lines (DISTANCE-ORDER, CUMULANT-DIST), each marked "added after the
    freeze";
  - in the proof file, an appended "Computed in ticket B" section;
  - generated manifests.
- **No case, reading or prediction changed**, and the experiment code is unchanged.

## 5. The series-parallel conjecture (Narrowing)

- **The counterexamples** (`referee_nae_sp_failures.json`, `referee_nae_sp_single_twist.json`):
  - **The first, on 11 distinctions:** {1,7,0}, {8,1,9}, {4,3,2}, {5,0,4}, {5,3,6}, {10,6,2}. All are not-all-equal except {4,3,2},
    a betweenness knot with 3 in the middle; the same base with {5,3,6} as the betweenness knot also fails.
    - **Graph-like:** every distinction lies in at most two knots, and the knots meet at most once.
    - **Series-parallel:** the knot graph has edges 0–1, 0–3, 2–3, 2–4, 2–5, 3–4, 4–5, and no K4 minor.
    - **The failure:** b(0, 10) is infinite while b(0, 2) = 3 and b(2, 10) = 2.
  - **The second, on 13 distinctions**, is likewise.
  - **The checks.** Each was rechecked with a second, independent freedom test (np.unique against a bincount).
  - **The plain versions pass.** The same knot graphs with every knot not-all-equal do not fail.
- **These are inside P6's frozen scope.** Graph-like, series-parallel, and twisted in the study's sense: one knot switched at one
  place. So P6 ("metric, plain or twisted") is false as stated.
  - The study's 354 bases did not meet a failure: about half were plain, and only a few of each graph's single twists fail (2 of
    18 and 2 of 21 here).
- **What survives.** With every knot not-all-equal: 0 failures on 129 more series-parallel bases (10 to 15 distinctions), against 5
  of 31 with a K4 minor.
- **The fix.** Restrict the conjecture to plain not-all-equal, or state it as refuted for twisted bases, with the example. The table
  row "meeting once, each distinction in two knots, no K4: yes in all 354 checked" should say "plain only". Direction 1 (a proof by
  two-distinction separations) should aim at the plain case.

## Fixes for the thread (listed for the owner, not folded in)

1. **P6 and the series-parallel conjecture.** False with one betweenness knot (11 and 13 distinctions; example above). Keep it for
   plain not-all-equal only (0 of 129 more fail), and score P6 as failed for its twisted half. **Narrowing.**
2. **C1's scope.** Name the working hypothesis, that every bond through y forces y both ways. Say that bases mixing parity with
   not-all-equal or betweenness are excluded and can fail: 5 of 237 random glued bases break Lemma 1, through one-way ties of two.
   **Not a block.**

## How the work was split

- **The referee:**
  - read the note, the pre-registration, proofs C1 to C4, `naelib.py` and `job.py`, and the post-freeze diff;
  - checked the proofs by hand;
  - wrote `referee_nae.py`: its own states and bond search, glued bases with a clause control, mixed rings, cacti, and graph-like
    series-parallel bases with random and with plain laws.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_nae.py`.**
- **`referee_nae_glue.json`, `_rings.json`, `_cacti.json`, `_sp.json`, `_sp_plain.json`, `_sp_failures.json` and
  `_sp_single_twist.json`.**

Reproduce, from `research/NAE-METRIC-20261118-001/referee-R1/`:

```sh
for p in glue rings cacti sp sp_plain; do ../../../.venv/bin/python -B referee_nae.py $p > referee_nae_$p.json; done
```
