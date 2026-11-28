# Commutation fixed at birth: can growth's own closures still close odd?

Epic `LOCAL-COMMUTE-20261127-001`, under G18 Comparing growth laws, at the owner's go-ahead ("Yes, let's continue") on
direction 1 of the toy-theory placement (`TOY-PHASE-20261127-001#1`): add a phase to the model, with a rule that places
signs at birth, and test which grown structures keep a state. Design, arguments and predictions frozen before the code
was run, after a review (section "Review before the freeze"; the advisor was unavailable). Results follow in sections of
their own; nothing above them changes except by a dated notice. The canonical K1–K3 test and the growth law are unchanged.

## The question

The quantum account named the smallest change to the law that could supply an odd closing law: "a rule for which values
commute, fixed at each birth, that keeps a state on every grown structure". Two earlier studies settled the reading off
the finished structure. Rule R (two values commute exactly when some knot holds both) keeps a state on few structures
(`EVENTUAL-R-20261126-001`: 290 of 300 sampled starts lose it for good). With any choice of which unheld pairs fail to
commute, read off the finished closed pattern (the whole choices, the record's R3), an odd close is attainable exactly
where the pattern is not outerplanar, which is every census type (`NO-WHOLE-STATE-20261126-001`, part E). This study asks
what is lost when each pair must be decided **at birth**:

1. **Which birth rules keep a state?** Decide each pair of distinctions at the end of the round in which the later one is
   born, from the holding pattern then, and never revise it.
2. **Can birth choices close odd?** At each closure ordinary growth makes from a census start, is an odd closing sign
   attainable by birth choices that keep a state at every round, wherever the whole choices attain it?
3. **The natural birth rule.** Let every pair a birth rule may decide fail to commute (rule R restricted to what is
   decided at birth). Where does it lose its state?
4. **Choosing round by round.** Does a birth rule that chooses at each round, among the choices consistent so far, ever
   reach a round with no consistent choice?

What "at birth" removes is narrow, and the study says so: ordinary growth is deterministic, so every choice is in the end
a function of the start, and the one thing the birth rule forbids that the whole choices allow is a failing pair of two
distinctions born in the same round, both loose then, that the next round's births do not take together. Looking one
round ahead settles every such pair (`EVENTUAL-R-20261126-001`, part B); the birth rule looks no round ahead.

## In standard terms

Each distinction carries a binary observable (a Hermitian involution); two observables either commute or anticommute. A
knot's check is the product of its distinctions' observables, which must commute among themselves. A structure keeps a
state when all checks commute, so that one state is an eigenstate of every check (the literature's stabilizer state,
with a check's sign as its law). Where the knots' indicator vectors are dependent, the product of the checks is ±1 and
the signs must match it: that product's sign is the cost of reordering it (the account's identity), and an odd one is a
state-dependent parity proof of contextuality, the literature's GHZ type. The population is the census of 7,075 starts of
three to five knots (`research/FORBID-EDITS-20261126-001/forbid.py`, `starts()`), grown by ordinary parity growth on the
archived engine for up to four rounds, one vote per census start.

## Definitions

- **Birth round.** A start's distinctions are born at round 0; a birth's fresh distinctions at the round of the birth. A
  round's births are planned together and are simultaneous. Under ordinary growth a birth takes only loose distinctions,
  one from each parent, and a funded round takes every loose distinction, so a distinction is held at most twice and is
  loose only until the next funded round (`EVENTUAL-R-20261126-001`, part B, from the engine).
- **Held together.** Two distinctions are held together when some knot holds both.
- **The birth rule** decides each pair (a, b) at the end of the round in which the later of the two is born, using the
  holding pattern then, and never revises it. It may make the pair fail to commute only if no knot holds both and at least
  one of the two is already held twice then (so no later knot can hold both). Pairs of distinctions born in the same round
  and both loose at birth always commute. The **birth choices** are all choices on such pairs under which every two knots'
  checks commute; the **whole choices** (the record's R3) are the same with every pair that no knot of the finished
  structure holds.
- **The natural birth rule** Γ_R: every pair the birth rule may decide fails to commute.
- **Signs.** A birth with a fresh distinction keeps its classical law. An implied birth takes the classical law times the
  cost of reordering the product of its relation's checks. The closing sign is odd when that cost is −1.

## Arguments (proved here, checked by the code)

- **A1. Under a birth rule no knot ever holds two values that fail to commute.** A failing pair always contains a
  distinction held twice when the pair was decided, and ordinary growth never takes such a distinction again (births are
  built only from loose distinctions; the engine asserts at most two holders).
- **A2. Every birth choice keeps a state at every round.** A pair is decided by the time both of its distinctions exist
  and never changes, and a knot's distinctions are fixed at its birth, so the condition that two knots' checks commute is
  fixed once the later knot is born, and the conditions present at any round are a subset of all of them. The classical
  choice (all commute) is a birth choice, so a state always exists. Whether a choice consistent at one round can always be
  continued at the next is not proved: a pair decided at round t also enters the conditions between its loose member's
  second holder, born at round t + 1, and the other member's holders. Question 4 tests it.
- **A3. An implied birth closes the whole structure, and it is its round's only birth.** Hypotheses, read in the engine:
  the implied flag is a test against the old knots' laws only; every census start is connected and births keep it
  connected; every knot with a loose distinction is live. In a connected structure where each distinction is held at most
  twice, an implied birth's relation and the new knot hold every one of their distinctions twice, so no other knot shares a
  distinction with them. Every other birth gets at least one fresh distinction, so a closure is exactly an implied birth.
  The closing knot can have two places (the start (x1, x2, l0), (x1, x2, y1, y2), (y1, y2, l2) closes at round 1 on
  (l0, l2)). A start with no loose distinction is closed at round 0 and has no closure; such starts are counted apart.
- **A4. The closing sign is well defined on both sets of choices.** Listing the knots in any order, the cost is the parity
  of failing pairs whose two occurrences interleave. Exchanging two consecutive knots changes it by exactly the condition
  that those two checks commute, so on birth and whole choices it does not depend on the order (the record's R3 argument).
- **A5. At a closure in round 1, birth choices and whole choices coincide on the closed pattern.** The only pairs the
  birth rule cannot decide are pairs of start distinctions both loose at the start, and the closing birth takes every one
  of them, so they are held together anyway.
- **A6 (the reviewer's lemma, argued by hand).** At a closure in round t ≥ 2, suppose three of the closing knot's parents
  a, b, c lie in one block of the structure before the closing round (the literature's biconnected component). Then that
  structure has three paths meeting only at their ends, a to b, b to c and c to a, or three paths from a, b and c to one
  common knot (the literature's K4 and K2,3 subdivisions). Let the closing knot's distinction with a fail to commute with
  every distinction of the path opposite a (in the first case, the b–c path; in the second, the paths from b and c), and
  likewise for b and c. Every two knots' checks then commute, the cost is 1, and every failing pair is a distinction of the
  closing knot (born at round t − 1) against an older one, so the birth rule decides it at round t − 1.

## Prior work in the program

Searched before freezing, each with `--until` this date and `--exclude` this epic:

`python3 -B scripts/track.py objects "which values commute fixed at birth keeps a state" --until 2026-11-27 --exclude LOCAL-COMMUTE-20261127-001`
`python3 -B scripts/track.py objects "odd closing sign attainable outerplanar commutation choice" --until 2026-11-27 --exclude LOCAL-COMMUTE-20261127-001`
`python3 -B scripts/track.py objects "stabilizer state-dependent parity proof two contexts per observable" --until 2026-11-27 --exclude LOCAL-COMMUTE-20261127-001`
`python3 -B scripts/track.py objects "census starts grown ordinary parity growth closed patterns" --until 2026-11-27 --exclude LOCAL-COMMUTE-20261127-001`

A full-text search of the records (`rg -i "outerplanar|state-dependent|fixed at birth|Arkhipov"`) was run as well, after the
toy-theory referee's lesson.

- `NO-WHOLE-STATE-20261126-001` — same object: part E's R3 is the whole choices here, with its conditions and interleaving
  cost (`rule_census.py`, `analyse`); its result (odd attainable exactly where not outerplanar, all 173 census types) is
  the comparison, and its outerplanar controls are reused. Its advisor had named Arkhipov's theorem and the state-dependent
  version (`EVENTUAL-R-20261126-001/advisor_answer.md`, section 7).
- `EVENTUAL-R-20261126-001` — same population and a relative: rule R read off the whole, pairs settling as soon as either
  distinction is held twice, and the engine facts A1 rests on; this study replaces the whole by the moment of birth.
- `TOY-PHASE-20261127-001` — the placement this direction comes from; its rows 2 and 3 matched the first and third
  searches.
- `BIRTH-SIGN-WEIGHT-20261127-001`, `VALUE-CHANGE-20261126-001` — relatives: a supplied sign at the ring's close; reading a
  change and rule R's checks.
- `ERASURE-AND-CLOSING-SIGNS-20261121-001` — a relative: signed operator readings of drawn wholes (the literature's
  state-independent parity games) and simultaneous odd requirements; not the birth rule.
- `CREATED-PAIR-20261119-001`, `BUILT-BINDING-20261126-001`, `FIVE-PRODUCT-GUARDED-REUSE-20261115-001`,
  `RELATIONAL-NATIVE-CONTROL-20261010-001`, `CLOSED-BY-CUTS-20261127-001`, `RING-BOND-20261127-001`,
  `UPPER-GROWN-20261127-001`, `BOTH-LONG-20261126-001` — unrelated objects matched on shared words (grown census starts,
  binding, collisions).

## Prior work outside the program

- A. Arkhipov, "Extending and characterizing quantum magic games" ([arXiv:1209.3819](https://arxiv.org/abs/1209.3819)):
  a state-independent parity game with each observable in two contexts has a quantum solution exactly when its
  intersection graph is nonplanar.
- C. Okay, S. Roberts, S. D. Bartlett and R. Raussendorf, "Topological proofs of contextuality in quantum mechanics"
  ([arXiv:1701.01888](https://arxiv.org/abs/1701.01888)): state-independent and state-dependent parity proofs as
  cohomology.
- The literature's outerplanar graphs (graphs with a circular drawing in which no two edges cross; equivalently, adding
  one vertex joined to every vertex leaves the graph planar), named here once; in the program's words, the knots admit a
  circular order in which no two distinctions held by four different knots interleave.

Known: the whole-choice criterion (the record's R3) and its literature. Not found: a restriction to choices made at birth.

## Settled by construction (stated, not tested)

- A1–A5 and the lemma A6, which the code checks rather than discovers.
- Whole choices attain odd exactly on closed patterns that are not outerplanar (the record's R3; checked again here).
- At round-1 closures birth choices and whole choices coincide (A5).
- The natural birth rule at a round-1 closure is rule R on the closed pattern, so it keeps a state there exactly where the
  record's R1 holds.

## Predictions (frozen)

All counts are under one vote per census start; a closure type that recurs counts once per start.

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gates: the ring of three grows its four-knot closure; there birth choices attain odd, and Γ_R is the readers' matching, keeps a state and closes odd; with this study's own code, whole choices attain odd on all 173 census types and on none of the record's four outerplanar controls; on 100 seeded random birth and whole choices at seeded closures the closing sign is the same under 5 seeded orders of the knots; a mutant without the commuting conditions, listing the ring of four with doubled meetings in the order 0, 2, 1, 3, attains odd there (where the true answer is even). | any gate fails |
| P1 | A1, A3 and A5 hold on every structure of the run: no knot ever holds a pair the birth rule may decide; every closure is a single implied birth that closes the whole structure; at every round-1 closure birth and whole choices coincide. | any violation |
| P2 | At every closure of the run, whole choices attain odd exactly where the closed pattern is not outerplanar. | any disagreement |
| P3 | At every closure in rounds 2 to 4 where three of the closing knot's parents lie in one block of the structure before the closing round, birth choices attain odd (A6). | any such closure where they do not |
| P3′ | At the other closures in rounds 2 to 4 that are not outerplanar (a closing knot with two parents, or parents in different blocks), birth choices attain odd at every one: fixing commutation at birth loses no odd close. This is the study's open test; the count of such closures is reported whatever it is, with the three-label closure (a knot meeting three others once each, grown two rounds) named. | any such closure where whole choices attain odd and birth choices do not |
| P4 | The natural birth rule Γ_R loses its state (two checks fail to commute) by the end of the run on more than half of the census starts that make at least one funded round. | at half or fewer |
| P5 | Choosing round by round (at each round a uniformly random choice among those consistent with the earlier rounds), no run ever reaches a round with no consistent choice, on 500 seeded starts with 5 seeded runs each. | any run reaches one |

P3 follows from A6, and the reviewer settled the three-label closure by hand (birth choices attain odd there). P3′ is a
judgment: A6 needs three parents in one block, and its witness uses only the closing knot's distinctions against older
ones; elsewhere a witness might need a pair the birth rule forbids. P4 has a partial lower bound only: Γ_R agrees with rule
R wherever one member of a pair is held twice, and rule R already failed at round 0 on 112 of the rule-R study's 300
sampled starts. P5 is argued only in part: a birth with a fresh distinction has free pairs to meet its conditions, and an
implied birth's conditions follow from the older ones.

## Runs and stop rule

One script, `local_commute.py`: growth on the archived engine (`forbid.grown`), exact GF(2) elimination with integer bit
masks for every rank test, and planarity and blocks with networkx, as in the record. Every census start, up to four rounds
or until it closes or stalls; a structure above 40 knots is cut and counted as not run. The number of free directions of
birth and whole choices is reported at each closure. One size past: round 5 on a seeded sample of 200 starts still growing
at round 4 (seed 20261127), reported separately. A prefix is timed first; the whole run is expected to take minutes, under
a 4 GiB cap with one thread. The study stops when every prediction is scored; it changes no growth law and searches for no
native source.

## Review before the freeze

Fable 5.2 returned a usage limit (logged in `docs/ADVISOR_HIVEMIND.md`). An independent reviewer (a separate session,
read-only, reasoning by hand with no computation) checked the first draft. It found A1, A4 and A5 right and A3 right with
three hypotheses to state, and settled the three-label closure by hand. Changed before the freeze in response:

1. The framing of "at birth": growth is deterministic, so the only thing the birth rule forbids that whole choices allow is
   a failing pair of two same-round distinctions, loose at birth, taken apart by the next round; one round of lookahead
   gives the whole choices. Stated in the question.
2. A2: "decided once" was wrong for a single pair, whose loose member's second holder brings new conditions a round later.
   A2 now claims only that every birth choice keeps a state at every round; the round-by-round question became P5.
3. A3: its three hypotheses, the two-place closing knot and the starts closed at round 0 are stated.
4. P3: the reviewer's lemma (A6) makes the first draft's "a majority" nearly certain, so P3 now predicts every closure
   the lemma covers, and P3′ carries the open test on the closures it does not.
5. P4: the partial lower bound from rule R is stated; the prediction is unchanged.
6. The mutant gate: dropping the conditions does not change the verdict on the controls in their own order (one has no
   unheld pair at all), so the gate now lists the ring of four with doubled meetings in an order with an interleaving pair.
7. Words: "local" and "space" are no longer used for the two sets of choices ("birth choices", "whole choices"); A4's
   "consecutive knots"; the weighting is named for every count.

The reviewer's other suggestions, not adopted here: a less conservative birth rule using which live knots can be
co-parents (the engine's candidate pairs), choices unchanged by the structure's relabellings, and a round-by-round
comparison of the consistent choices with the final birth choices. They stay as directions.
