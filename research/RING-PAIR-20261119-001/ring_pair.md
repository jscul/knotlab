# What rule do two joined rings of knots grow by?

Epic `RING-PAIR-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for `JOIN-GROWTH-20261118-001#1`. Goal
G17. **Referee pending.** Its scope was narrowed on 19 November by `RING-IDENT-20261119-001`, which proved the rule with one added
condition: the knot graph must contain a cycle (see Correction).

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `3b2acc84f` at 01:26 UTC, after the model was found
  and checked on recorded growths (disclosed). The test ran from 01:27 UTC through the shared runner (`RING-PAIR-B1`,
  `runs/ring-pair`, 20 cases on 3 workers).
- Code: [covermodel.py, fresh.py, job.py, merge.py, checks.py](../../experiments/RING-PAIR-20261119-001B/RING-PAIR-20261119-001B-E001_cover/),
  with the growth of `JOIN-GROWTH-20261118-001B`; the exploration in `pilot/`.
- Results: [results.json](../../artifacts/RING-PAIR-20261119-001B/RING-PAIR-20261119-001B-E001_cover/results.json).

"Growth" counts junctions by round. Words: the **candidate map** of a start has a point for each knot, and joins at once all the
knots that share a distinction with one knot (they are pairwise candidates through it); the **unrolled map** is what that map
becomes when every cycle in it is opened out and continued instead of closed (the literature's universal cover); a **cluster** is
a finite set of its points that hangs together. "Fractal" stays in the owner's quotation marks.

## The answer

**In the owner's terms.**
- **Yes: there is an exact rule, and it is simple.** Draw the candidate map of the start and unroll it. The junctions the growth
  makes in round t are exactly the clusters of t + 1 points of the unrolled map, each counted once however often it repeats.
  - Set down before growing, it gave the count of every round of 17 fresh joins never grown before, exactly: joined rings, chains
    and bouquets of three rings, a ring with a second cycle through a path, and the advisor's two likeliest breakers.
  - It also reproduces every recorded growth inside its scope.
- **What "unrolled" means.** In the candidate map a ring of knots is a cycle. Unrolled, the cycle becomes an endless chain, and each
  lap of the growth is one more stretch of it. With two joined rings, a walk can turn into the other ring every time it passes the
  joint, so the unrolled map branches there, forever. The branching is what makes two rings lock into a new kind of growth.
- **What "a rule that refers to itself" means here.** Count the clusters that enter one block of the unrolled map from one side.
  Such a cluster is the point entered, plus, for each further block, "skip it, or enter it", and entering a further block is the
  same count again. So the count appears on both sides of its own equation, U = y Π(1 + U).
  - With one ring the unrolled map is a chain, the self-reference never branches, and the equation is linear: the rate is a root
    of a polynomial. This is `RING-FORMULA-20261118-001`'s formula, and `JOIN-GROWTH-20261118-001`'s menus are its factors.
  - With two or more independent cycles it branches, the equation is quadratic or higher, and the counts follow C λ^t t^(−5/2).
- **The "logic based fractal", precisely.** The unrolled map of two joined rings has finitely many kinds of branch, and each branch
  contains copies of every kind. That is exact self-similarity, and the self-referring equation is its count; with one ring the
  map is only periodic. It is not a dimension claim: a dimension would need a distance on the map's ends that the program has not
  built. And the count does not show emergence by itself.
- **Known mathematics, cited once.** These are the lattice animals of a tree-like map, whose exponent 5/2 is the Bethe lattice's
  (Fisher and Essam, 1961), counted by positive algebraic systems (Drmota, Lalley, Woods). What this adds is that the cheapest
  parity growth's rounds are exactly these clusters.
- **The scope.** The rule is claimed where every knot gets its places from its shares and its first-round joins, without the floor
  of three; where surplus distinctions sit on knots asked for two or more joins; where the first round has only pairs; and, added
  after the run, where the knot graph contains a cycle (corrected: see Correction). Outside
  it, the floor's distinctions renew and nest, as `JOIN-GROWTH-20261118-001` found, and three out-of-scope starts grown here behave
  differently: two grow by a fixed amount a round, one exponentially.

| Start (fresh, frozen) | Rounds grown, all equal to the rule | Rate (1/radius of its equation) |
| --- | --- | --- |
| two rings of five through a path of two knots | 17 rounds (0–16), 312,976 junctions | 2.2939 |
| rings of five and seven sharing a knot | 15 rounds (0–14), 300,733 junctions | 2.5654 |
| rings of five and seven through a path of one knot | 17 rounds (0–16), 285,810 junctions | 2.2470 |
| a chain of three rings of five (middle joints two apart) | 12 rounds (0–11), 254,363 junctions | 3.2460 |
| a chain of three rings of five (middle joints neighbours) | 12 rounds (0–11), 308,870 junctions | 3.3008 |
| three rings of five through one knot | 11 rounds (0–10), 750,141 junctions | 4.1138 |
| two rings of seven joined twice | 13 rounds (0–12), 637,700 junctions | 3.2691 |
| two rings of five, a surplus distinction far out on each | 14 rounds (0–13), 284,108 junctions | 2.7650 |
| rings of nine and five sharing a knot | 16 rounds (0–15), 364,226 junctions | 2.3829 |
| a ring of five with a second cycle through four knots | 15 rounds (0–14), 418,360 junctions | 2.7415 |
| a ring of five carrying a lone knot (two surplus), joined to a ring of seven | 15 rounds (0–14), 382,292 junctions | 2.5343 |
| two rings of seven through a path of one knot | 19 rounds (0–18), 457,067 junctions | 2.0851 |
| three rings of five joined to one central knot | 13 rounds (0–12), 607,468 junctions | 3.1558 |
| control: a ring of nine with two lone knots and a surplus (one cycle) | 26 rounds (0–25), 328,128 junctions | 1.4191 |
| two rings of five joined by two paths of one knot | 12 rounds (0–11), 383,328 junctions | 3.5491 |
| falsifier: a ring of eight with lone knots on alternate knots | 21 rounds (0–20), 300,172 junctions | 1.6174 |
| falsifier: two rings of five sharing a knot, plus a path of three knots | 12 rounds (0–11), 763,527 junctions | 3.7807 |


The rates of the one-cycle starts (the control and the ring of eight) are poles, computed as the same radius: 1.419 and 1.617 (the
grown ratios 1.403 and 1.618 at the last round). The three out-of-scope starts, all with a group of three in round 1: two rings of
five joined twice at knots two apart grow exponentially (ratio 2.43 at round 14); a ring of five with a second cycle through two
knots, and a ring of seven with one through two knots, grow by a fixed amount a round for 80 rounds.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | gate checks | held | the model equals all 36 in-scope census starts and the 5–5 pilot, differs on all 100 out of scope; brute force agrees to size 9 on three starts; a mutant without the blocks differs; the rooted identity holds to round 20 |
| P1 | every round of the 17 fresh in-scope starts equals the rule | **held** | 17 of 17, every round grown (11 to 26 rounds, 254,363 to 763,527 junctions), including both falsifiers |

## Why it holds (outline, not proved)

The advisor's route, which this study checks by computation only:
- **Counting.** Two blocks share at most one point (no two knots have two common neighbours), so the unrolled map is a tree of
  blocks and its deck group is free. Clusters are counted once per orbit by the block-tree recursion and the dissymmetry of block
  trees; equivalently, the clusters through a point number (t + 1) c(t) (gate G4).
- **Growth.**
  - Round = size − 1, by induction.
  - A cluster's parents are the cluster less one point whose removal keeps it together: for three or more points, two such
    parents share a connected grandparent.
  - The joining rule's groups are exactly the full parent sets of the clusters. This is the weakest step. In the unrolled map no
    false group arises; in the start, a false group would need a short cycle of candidates that does not unroll closed, and the
    scope's last two conditions exclude it. The advisor reads them as saying the knot–distinction graph has no cycle of three, four
    or six; that reading is recorded, not tested.

## Known results, and what this adds

Known, cited once:
- lattice animals on the Bethe lattice and their exponent θ = 5/2 (Fisher and Essam, J. Math. Phys. 2, 1961; Lubensky and
  Isaacson, Phys. Rev. A 20, 1979), and animals on non-amenable graphs (Madras and Wu, 2010);
- block trees and their dissymmetry (Otter 1948; Harary and Uhlenbeck 1953; Bergeron, Labelle and Leroux 1998);
- positive algebraic systems and their square-root singularity (Drmota 1997; Lalley 1993; Woods 1997; Flajolet and Sedgewick 2009,
  VII; Banderier and Drmota 2015);
- free groups acting freely on trees (Bass–Serre).

What this adds: the cheapest parity growth of every start in the scope is exactly the cluster count of its unrolled candidate map.
That one rule covers, in one picture:
- the ring formula: the unrolled ring is an endless chain with surplus points;
- `JOIN-GROWTH-20261118-001`'s menus: F_s = 1 + y(1 + y)^s is the cluster count of a point carrying s pendant points;
- its nested chains: candidates two apart are neighbouring blocks;
- the non-rational growth of joined rings, now exact.

## Limitations

- **Computed here, proved since.** The identification of the growth with the clusters is checked on every grown round of 17 fresh
  starts, 36 recorded census starts and 7 recorded two-ring joins (`JOIN-GROWTH-20261118-001`). `RING-IDENT-20261119-001` proved it
  for every round, with the scope's added condition that the knot graph has a cycle.
- **Scope.** Starts with a distinction from the floor, surplus at a knot of demand 1, a group of three in round 1, or two knots
  with two common neighbours are outside the scope. All 100 out-of-scope census starts differ from the rule from round 1.
- **The horizon** is 11 to 26 rounds per start. The rates and the exponent come from the rule's equations, not from the growth.
- **One policy** (A104) and the bare convention (A107). "Growth" counts junctions by round; bond balls are not measured.

## Correction (19 November 2026, a Narrowing)

The scope as first stated is too wide. When the knot graph is a tree, the candidate complex's components are finite. A component's
whole cluster then has nothing left to join while other loose distinctions remain elsewhere, so it is not implied, and the floor gives
it one fresh distinction: a relay, as `CLUSTER-ALL-20261119-001` names it.
- **The example.** Two stars joined at their centres (knot 0 joined to 1, 2 and 3; knot 3 joined to 4 and 5) meets every condition
  above, and `covermodel.in_scope` accepts it. It grows 6, 6, 2, 2, 4, 6, 8, …, against the rule's 6, 6, 2, 0.
- **How often.** Among RING-PAIR-scope starts on 3 to 7 knots, 21 of the 43 trees differ, and all 45 with a cycle agree.
- **What stands.** Every result above concerns starts with a cycle, and `RING-IDENT-20261119-001` proves the rule for all of them,
  every round (its Proposition 5 is this example). Logged in `docs/CORRECTIONS.md`.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze.
- It judged the counting half sound and gave the rooted identity, now gate G4, and the −5/2 from it.
- It outlined the growth half's proof and named the groups step as the weakest.
- It proposed the two falsifiers, F16 and F17; both hold.
- It gave the literature and the wording: "self-similar (finitely many branch types)" for two or more cycles, with "fractal" kept
  in quotation and no claim of emergence.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the rule two joined rings grow by | **Status:** Successful | An exact rule, clusters of the unrolled candidate map, predicted every round of 17 fresh starts; its equation refers to itself and is algebraic; c ≈ C λ^t t^(−5/2) |
| Local direction: an exact model of the cheapest parity growth | Continue | One rule now covers rings, joined parts, chains and joined rings in its scope; the floor's distinctions and groups of three are outside it |
| Broader exploration: what the cheapest growth builds | Known alternatives | Inside the scope, clusters of a cover: one cycle gives a rational rate, two or more an algebraic one; trees of knots give polynomial growth through renewing chains (outside the scope) |
| Long-term goal: G17 Typical and rare meeting patterns | Capability gained | The growth of every start in the scope is computed from its candidate map alone, to any round |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | One rule for every start: extend the clusters to the floor's distinctions (renewing points as endless pendant chains) and test it on the whole touch census | 3/3 — the census's typical two dimensions, its rare three and four, and its rings would all be one cluster count | 3/3 — the hanging pair already matched by hand, the model and the census exist | freeze the extended rule on the 26,441 census arrangements and the JOIN-GROWTH paths → stop at the rule predicting every growing arrangement, or the first that breaks it | Selected · awaiting go-ahead |
| 2 | Prove the identification (the groups step) | 3/3 — turns the cluster rule into a theorem about the growth | 2/3 — the advisor's outline, the scope's reading as no short cycles | write the lemma that a false group needs a non-unrolling cycle of length ≤ 3 → stop at a proof or a counterexample start | Alternative · deferred |
| 3 | The scope's edge: groups of three in round 1 | 2/3 — explains the slow and closing starts seen | 2/3 — three grown examples | fill the round-1 triples as blocks of a different kind and test on the chords → stop at a rule for them, or a proof none of this kind works | Alternative · deferred |

- **#1.** Payoff 3/3: the touch census's dimensions (two typical, three and four rare) were read off with a chain rule that missed
  some cases. A cluster rule would explain them, the rings and the joins together. Concreteness 3/3: renewing offshoots as endless
  pendant chains reproduced the bare hanging pair exactly, and the census runs exist. Bound: one epic.
- **#2** and **#3** are independent of #1. #2 ties with #1 on payoff and is less concrete.

**Corrections:** `JOIN-GROWTH-20261118-001` (Narrowing, published in commit `b2576533d` and reported on 19 November): two joined
rings grow as C λ^t t^(−5/2) with rates 2.19 to 2.87, not t^(−3/2) with 2.14 to 2.79. **Goals:** G17 checkpoint (capability
gained); no goal changed. **Assumptions:** none new; A104 and A107 bound the scope. **Basket:** B196, `FRESH-COUNT-20261118-001#1`,
B202, `PLUS-ONE-20261118-001#1`, `JOIN-GROWTH-20261118-001#2` and `#3`; none taken.

## Final report as sent (2026-11-19 02:01 UTC)

**Outcome:** Two joined rings grow by an exact, simple rule that refers to itself. I drew which knots can join which, and opened every cycle of that map out into an endless branching map. The junctions made in round t are then exactly its clusters of t + 1 points, each counted once. Set down before growing, the rule gave the count of every round of 17 fresh joins never grown before (17 of 17, including the advisor's two likeliest breakers). Closed, referee pending.

- **What "a rule that refers to itself" means here.** To count clusters, you count the ways of entering one part of the map: the knot itself, then, for each further part, skip it or enter it. Entering a further part is the same count again, so the count appears on both sides of its own equation, U = y Π(1 + U).
  - With one ring the map unrolls to an endless chain. The equation is linear and the rate is a root of a polynomial; this is the ring formula, and yesterday's menus are its factors.
  - With two rings the map branches every time a walk passes the joint. The equation becomes quadratic, and the counts follow C λ^t t^(−5/2).
- **The "logic based fractal", precisely.** The branching map has finitely many kinds of branch, and each branch contains copies of every kind. That is exact self-similarity, and the self-referring equation is its count. It is not a dimension claim, and the count does not show emergence by itself.
- **Known mathematics, cited once.** These are lattice animals on a tree-like map, with the Bethe lattice's exponent 5/2 (Fisher and Essam, 1961), counted by positive algebraic systems (Drmota, Lalley, Woods). What is new is that the cheapest parity growth's rounds are exactly these clusters. One rule now covers rings, joined parts, chains and joined rings.
- **Scope.** No knot may take a distinction from the three-place floor, and round 1 must have only pairs. All 100 census starts outside the scope differ from the rule. Three out-of-scope starts grown here: two grow by a fixed amount a round, one exponentially.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the rule two joined rings grow by | **Status:** Successful | An exact rule (clusters of the unrolled candidate map) predicted every round of 17 fresh starts; its equation refers to itself and is algebraic; c ≈ C λ^t t^(−5/2) |
| Local direction: an exact model of the cheapest parity growth | Continue | One rule covers rings, joined parts, chains and joined rings in its scope; the floor's distinctions and round-1 triples are outside it |
| Broader exploration: what the cheapest growth builds | Known alternatives | In the scope, clusters of a cover: one cycle gives a rational rate, two or more an algebraic one; trees of knots grow polynomially through renewing chains (outside the scope) |
| Long-term goal: G17 Typical and rare meeting patterns | Capability gained | The growth of every start in the scope follows from its candidate map alone, to any round |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | One rule for every start: add the floor's renewing distinctions as endless pendant chains and test the clusters on the whole touch census | 3/3 — the census's typical two dimensions, rare three and four, and rings as one count | 3/3 — the hanging pair already matched by hand; the census exists | freeze it on the 26,441 census arrangements and JOIN-GROWTH's paths → stop at every growing arrangement predicted, or the first that breaks it | Selected · awaiting go-ahead |
| 2 | Prove the identification (the groups step) | 3/3 — makes the rule a theorem | 2/3 — the advisor's outline | prove that a false group needs a short cycle that does not unroll → stop at a proof or a counterexample | Alternative · deferred |
| 3 | The scope's edge: groups of three in round 1 | 2/3 — explains the slow and closing starts | 2/3 — three grown examples | fill round-1 triples as a new kind of block, test on chords → stop at a rule or a proof none of this kind works | Alternative · deferred |

**Corrections:** `JOIN-GROWTH-20261118-001`, a Narrowing published and reported earlier tonight. Two joined rings grow as t^(−5/2) with rates 2.19 to 2.87, not t^(−3/2) with 2.14 to 2.79. **Goals:** G17 checkpoint (capability gained); no goal changed. **Assumptions:** none new; A104 and A107 bound the scope. **Basket:** B196, `FRESH-COUNT-20261118-001#1`, B202, `PLUS-ONE-20261118-001#1`, `JOIN-GROWTH-20261118-001#2` and `#3`; none taken. **Advisor:** Fable 5.2, before the freeze. It judged the counting half sound and gave the rooted identity, which became a gate check. It outlined the proof, naming the weakest step, proposed the two falsifiers (both held), and supplied the literature and the wording ("self-similar", with "fractal" kept in quotation).

**Referee hand-off.** The decision note is `research/RING-PAIR-20261119-001/ring_pair.md`, and the prior-work line is in the pre-registration (objects-gate passes). Please check:
- that `covermodel.py`'s block recursion and dissymmetry count are the orbit count (gate G4 is the independent check);
- the scope conditions;
- the two logged amendments: a scorer import fix, and a memory rerun with the same code and caps.

Publication is paused (out of GitHub Actions minutes); all of this is committed locally.
