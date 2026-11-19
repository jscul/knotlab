# Do loops keep branching under not-all-equal?

Epic `NAE-GROWTH-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead. Goals G17 and G1. **Referee pending.**

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `db07fd8f5` at 03:33 UTC after a pilot (disclosed).
- The run went from 03:34 UTC through the shared runner (`NAE-GROWTH-B1`, `runs/nae-growth`): 294 cases on 6 workers, all ok by
  03:39 UTC.
- Gates: G1–G6 pass (`checks.py`, [checks_output.json](../../experiments/NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae/checks_output.json)).
- Code: [naelib.py, bondlib.py, job.py, merge.py, checks.py](../../experiments/NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae/).
  The post hoc reading of part B is `posthoc_b.py`.
- Results: [results.json](../../artifacts/NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae/results.json) and
  [posthoc_b.json](../../artifacts/NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae/posthoc_b.json).

"Growth" is the cheapest growth of `FRESH-COUNT-20261118-001`: its complete-round joining policy and its fewest counts (A104).
"Not-all-equal" (NAE) reads every junction as the constraint that its distinctions are not all equal. Words as in
`CLUSTER-ALL-20261119-001`: an endless chain, a relay.

## The answer

**In the owner's terms.**
- **Yes. Loops keep branching under not-all-equal exactly as under parity.** Junction counts are the same at every round, so the
  ratios are the same roots:
  - the ring of five with one spare per knot grows by the golden ratio;
  - the spare-less ring makes 5 junctions every round;
  - a ring with one spare on one knot grows by 1.1347;
  - two joined rings grow at 2.6075.

  This held on every one of the 22,949 census starts that parity does not close, and on the go-ahead's chain and two-ring join
  (13,822 junctions at round 11 under both laws).
- **The one difference: not-all-equal never closes.**
  - Where parity closes (3,492 census starts), the not-all-equal top junction takes one fresh distinction where parity's takes
    none.
  - From there two endless chains grow, with 1, 2, 3, 4, … junctions a round. When the top had only one old distinction it takes
    two fresh ones, and the tail is 2, 3, 4, ….
  - So every closing start becomes a two-dimensional growth. This was proved, and seen on all 3,492.
  - The 234 starts with nothing loose close at once under both laws. The 11,010 that stall stall alike.
- **Why.** The cheapest growth reads the law in one place only: whether a new junction's constraint already holds, given the
  junctions before it.
  - Under parity it holds exactly at the closing top, the last junction, which takes every loose distinction there is.
  - Under not-all-equal it never holds. Each new junction takes one distinction from each parent, and every parent keeps at least
    two places for itself, so some allowed state makes the new junction's old distinctions all equal. The argument colours the
    junctions' shared distinctions in two colours, so that every junction sees both (proved; the advisor's lemma).
- **The cluster picture survives with one change.** The junctions of each round are still the unrolled map's clusters, and a
  finished piece still relays into two chains when other pieces are alive. Under not-all-equal, a finished piece relays even when
  it is the last one. Parity's "it closes" clause becomes the relay clause.
- **Is bond distance still enough to say who joins whom? Mostly under not-all-equal, much less under parity.** The test took the
  2,644 different small stages of these growths (up to 15 distinctions).
  - Under not-all-equal, 95% of them have a bond-distance table that no other stage shares. For those, the table says who joins
    whom next. Under parity only 40% do.
  - Wherever two stages share a table, they join differently in the next round (all 128 pairs under not-all-equal, all 2,902
    under parity).
  - **The main reason is the growth's, not the distance's.** The growth reads which junction holds which distinction, and the
    allowed states do not always fix that.
    - Under parity, adding junctions together gives a different presentation with the same allowed states, so 2,802 of its 2,902
      collisions are the same states.
    - Under not-all-equal, 115 of its 128 collisions are the same states, almost all through a redundant junction, one whose
      constraint is already implied by the others.
  - **The rest are the table's.** Bond distance misses some many-place not-all-equal junctions, which hide little (13
    collisions, such as two touching knots with or without a four-place junction across them). Under parity it misses 99.
- **Where a law has no cheapest growth.** For one-in-three and majority, no junction is a knot (the canonical checker), so the
  cheapest growth, which makes knots, has nothing to make. Under one-in-three, no fresh count even keeps the old states.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | gate checks | held | structural parity = GF(2) on 529 starts; SAT = brute force (300 random, 69 implied); bondlib = dual-code supports on 40 stages; knotlab: NAE 3–6 and parity 3–5 knots, one-in-k and majority 3–5 not; the lemma on 1,998 sets (and 41 of 1,520 sets leaving one place are not free); one-in-three removes a state at every count, majority at 1 and 2 |
| P1 | no parity-implied junction: identical | **held** | 22,949 of 22,949 (11,703 alive, 11,010 stall, 234 closed at once, 2 at the junction cap) |
| P2 | parity closures relay: k (or k + 1) at T + k | **held** | 3,492 of 3,492 (727 with a one-distinction top) |
| P3 | no NAE junction implied; the lemma's hypotheses | **held** | 0 implied; fewest places 3, each parent gives 1, fewest kept 2 |
| P4 | parity implies only the closing top | **held** | 3,492 implied junctions, every one the top of a closing growth, demand 0 |
| P5 | the go-ahead's starts identical | **held** | 9 of 9 (the lone knots by P2) |
| B1 | tree stages: equal tables | **held** | 97 of 97 |
| B2 | some stage with a cycle differs | **held** | 2,491 of 2,547 differ; NAE larger on 46,883 pairs, smaller on 12,304 |
| B3 | NAE collisions are state collisions | failed | 115 of 128 (13 with different states) |
| B3c | parity collisions are state collisions | failed | 2,802 of 2,902 (99 with different states, 1 undecided) |
| B4 | every NAE collision has a redundant junction | failed | 118 of 128 |
| B5 | NAE collisions without one join alike | failed | 0 of 10 join alike |
| B5c | some parity collision without one joins differently | **held** | 2,796 such pairs |

8 of 12 held. Two scoring notes, added after the run:
- **B5c is inverted in `merge.py`.** Its field reports "every such pair joins alike" (false). The frozen decision rule says B5c holds
  when a pair joins differently, as stated.
- **One go-ahead start was entered twice.** `P-ring5-spare1` was meant as "one spare per knot" but repeats the bare ring (four-place
  knots). The start with one spare per knot is `P-ring5-five-place`, five five-place knots, and it is the golden-ratio ring.

## Why it holds

- **T1, the keep clause is K2.** A junction with p old places and f ≥ 1 fresh ones keeps every old state, whatever the old states
  are, exactly when its relation is free on every set of all but one of its places, which is K2. The count max(d, 3 − p, 1) is at least 1 except at an implied
  junction. So for a knot law the law enters only through "implied" (G4 confirms that NAE on 3 to 6 places is a knot).
- **T2, NAE never implies here.** Suppose every distinction lies in at most two junctions, every junction has at least three
  places, and each parent keeps at least two places outside the new junction J.
  1. Remove J's old distinctions and draw the rest as a multigraph: junctions as points, shared distinctions as lines, loose ones as
     pendant lines.
  2. A connected multigraph that is not an odd cycle has a 2-colouring of its lines in which every point of degree at least two
     sees both colours (Bondy and Murty 1976, §6.1). Colour each component so.
  3. An odd-cycle component has only points of degree two. These are all parents of J, since other junctions keep at least three
     places. Colour it all 1.
  4. Give J's old distinctions 0. Every junction then sees both values, so all of them are satisfied while J's old distinctions
     are all equal, and J is not implied.

  The policy gives J one distinction from each parent, and every junction has at least three places (P3 logged both on every
  run), so the hypotheses always hold. The stronger form, that any set leaving every junction two places is free, held on 1,998
  random sets (G5). It is sharp: 41 sets leaving a junction one place are not free.
- **T3, parity implies only the closing top.** A sum of junction equations supported on loose distinctions alone has no
  distinction leaving the summed set, so the set is a union of components. In a connected growth the implied junction takes every
  loose distinction, is alone in its round, and leaves nothing loose (demand 0).
- **The tail.** The not-all-equal top gets max(0, 3 − p, 1) fresh distinctions. From one, an offshoot with two fresh distinctions
  starts two chains. From two, the two chains start at once. The policy then builds the down-closed sets of two chains, the pairs
  (i, j) of positions on them (the literature's ℕ²), with k + 1 of them at size k. Hence 1, 2, 3, … from T + 1, or 2, 3, 4, …,
  that is y^(T+1)/(1 − y)² or y^(T+1)(2 − y)/(1 − y)². This is the cluster rule's relay term.

## Known results, and what this adds

- **The colouring lemma** is classical (Bondy and Murty 1976, §6.1; it underlies proofs of König's edge-colouring theorem).
  **Parity's implications** are linear algebra over GF(2): a sum of equations whose support is only loose distinctions is a sum over
  whole components.
- **Same relation, different presentation.** Two presentations of one parity relation differ by adding equations together, so
  they have the same states; this is classical (equivalent generator sets of one code). That a growth reads the presentation was
  already found in the program: `FIRST-KNOT-20261118-001` ("the same relation grows differently by presentation") and
  `MIXED-NEXT-JOIN-20261117-001` (identical states, different next rounds).
- **Bond distance does not determine not-all-equal relations** from four distinctions (`DISTANCE-INFO-20261117-001`). The 13
  different-state collisions are instances.
- **What this adds.**
  - The cheapest growth does not depend on which knot law is used, except at implied junctions. Under not-all-equal it never
    closes (proved), checked on the whole census.
  - The cluster rule carries over, with the relay always on.
  - How often the table hides who joins whom is measured on one family under both laws: 60% of small stages under parity share
    their table with a stage that joins differently, 5% under not-all-equal, and almost all such pairs have the same allowed states.

## Limitations

- One policy (A104), the census's sizes and weighting (A106), and horizons of 14 rounds or 3,000 junctions. The tails are proved,
  and seen for at least three rounds.
- Part B covers stages of up to 15 distinctions from starts of up to four knots. "No other stage shares the table" is relative to
  that population; a larger one can only add collisions. The same-states test searches the tables' isomorphisms, with one parity
  pair undecided.
- Not-all-equal on many places hides little (log2(2^k / (2^k − 2)) bits at k places), so "every junction is a knot" holds, while
  the large junctions are knots that hide almost nothing (the advisor's point).
- BOND-NEXT-JOIN's reader was run only as a control outside its family. It is exact on 93 parity and 993 NAE stages of 2,644.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze.
- **What it gave.**
  - T2 and its proof, with a counterexample to my weaker argument.
  - The keep clause as K2 (T1) and the tail form (P2), whose one-distinction case I added.
  - The warning that one-in-three and majority are not knot laws.
- **What it advised against.** A second knot law as a confirmation, and computing bond tables unless the record claims something
  about them. Part B does claim something: it measures whether the table says who joins whom.
- **Where it was wrong.** It called "who joins whom" identical by construction. That is true for the joins, but the question is
  whether the distances reveal them, and the answer differs by law.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the cheapest growth under not-all-equal | **Status:** Successful (8 of 12 held; all five growth predictions) | Identical to parity except at closures, which relay into two chains (proved and checked on the census); bond distance reveals who joins whom on 95% of small stages |
| Local direction: growth under other laws | Practically exhausted | Every knot law enters only through implication (T1); not-all-equal never implies (T2); laws without knots have no cheapest growth; other knot laws are untested (direction 4) |
| Broader exploration: what the cheapest growth builds | Known alternatives | The same structures under both laws; the presentation, not the law, is what the growth reads |
| Long-term goal: G17 | Capability gained | Growth results stated for both knot laws, with the one place they differ |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A growth that reads only the allowed states (challenging A108): grow each stage's irredundant presentation, or one fixed by the states alone, and see whether the cheapest growth stays well defined | 3/3 — the canonical reading takes a system as the states it allows; the growth should too | 2/3 — under NAE the 115 same-state collisions say where to look | define the state-read growth on the part-B stages → stop at a law that is well defined on all of them, or a pair of same-state stages no state-read rule can grow alike | Selected · awaiting go-ahead |
| 2 | Disagreement counts instead of bond distance (`DISTANCE-ORDER-20261117-001`: they fix every NAE relation from four distinctions) | 2/3 — isolates the table's own loss from the presentation's | 3/3 — rerun part B's tables | swap the table → stop at the collision count | Alternative · deferred |
| 3 | Majority's growth with its own keep clause (f > p fresh distinctions) | 2/3 — the one law found here that changes the branching, outside knots | 3/3 | grow the census under majority with f = p + 1 → stop at whether it branches | Alternative · deferred |
| 4 | A second knot law ("ones not divisible by three") | 1/3 — confirms T1 | 3/3 | as part C | Alternative · deferred |

## Final report as sent (2026-11-19 03:51 UTC)

**Outcome:** Yes. Under not-all-equal, loops branch exactly as under parity, with the same counts at every round and therefore the same ratios: the golden ratio for the ring of five with one spare per knot, 5 a round for the spare-less ring, and 2.6075 for two joined rings. The one difference is that not-all-equal never closes. Where parity closes, the top junction relays into two endless chains. This is proved and was checked on the whole census. 8 of 12 frozen predictions held, and all five growth ones did. Closed, referee pending.

- **Why the law barely matters.** The cheapest growth reads its law in one place: whether a new junction's constraint already holds. Under parity that happens only at the closing top. Under not-all-equal it never happens, because every parent keeps two places of its own. The proof is a two-colouring argument from the advisor.
- **The census.** 22,949 of 26,441 starts grow identically. The other 3,492, which parity closes, relay with 1, 2, 3, … junctions a round (2, 3, 4, … when the top held one distinction).
- **The cluster picture survives.** A finished piece now always relays, even when it is the last one.
- **Bond distance, who joins whom.** It is mostly enough under not-all-equal and much less under parity. On 2,644 small stages, 95% have a table no other stage shares under not-all-equal; under parity, 40%. Where two stages share a table they always join differently.
  - The main cause is the growth, not the distance. The growth reads which junction holds which distinction, and the same allowed states can come from different presentations: 2,802 of parity's 2,902 colliding pairs, and 115 of not-all-equal's 128.
  - That is why four part-B predictions failed (B3, B3c, B4, B5). I've recorded the cause as assumption A108.
- **Where there is no cheapest growth.** Under one-in-three or majority, no junction is a knot.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the cheapest growth under not-all-equal | **Status:** Successful (8 of 12 held) | Identical to parity except at closures, which relay (proved, census-checked); bond distance shows who joins whom on 95% of small stages |
| Local direction: growth under other laws | Practically exhausted | A knot law enters only through implication; not-all-equal never implies; laws without knots have no cheapest growth |
| Broader exploration: what the cheapest growth builds | Known alternatives | The same structures under both laws; the presentation, not the law, is what the growth reads |
| Long-term goal: G17 | Capability gained | Growth results now hold for both knot laws, with the one place they differ |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A growth that reads only the allowed states (challenges A108) | 3/3 — the canonical reading takes a system as its allowed states; the growth should too | 2/3 — the 115 same-state collisions show where to look | define it on the part-B stages → stop at a law well defined on all of them, or a same-state pair no state-read rule can grow alike | Selected · awaiting go-ahead |
| 2 | Disagreement counts instead of bond distance (they fix every not-all-equal relation from four distinctions) | 2/3 — separates the table's own loss from the presentation's | 3/3 — rerun part B | swap the table → stop at the collision count | Alternative · deferred |
| 3 | Majority's growth with its own keep clause (more fresh than old distinctions) | 2/3 — the one law found that changes the branching, outside knots | 3/3 | grow the census → stop at whether it branches | Alternative · deferred |

**Corrections:** none for this study. Separately, I folded in the CLUSTER-ALL referee's two Not a block points (a scope cut drawn after the pilot's misses, now disclosed; "all 15,261" now names its two conventions), logged in docs/CORRECTIONS.md (8d06fa352). **Goals:** G17 and G1 checkpoint (capability gained). **Assumptions:** A108 added (the growth reads which junction holds which distinction, not only the allowed states); A104 history line (its results are not parity's alone). **Basket:** none taken; the earlier lines' items stay open. **Advisor:** Fable 5.2, before the freeze. It gave the no-implication lemma with its proof, the keep clause as K2, the tail form and the warning about non-knot laws. It wrongly called "who joins whom" identical by construction: the joins are, but whether distances reveal them differs by law.

**Referee hand-off.** The decision note is `research/NAE-GROWTH-20261119-001/nae_growth.md`, and the prior-work line is in the pre-registration (objects-gate passes, after `DISTANCE-ORDER-20261117-001` was added at the close and marked so). Please check:
- the two-colouring proof (T2) and its use of Bondy and Murty's lemma;
- the same-states test in part B, which searches only the tables' isomorphisms (one parity pair undecided);
- the two scoring notes: B5c is inverted in merge.py, and one pilot start repeats the bare ring.
