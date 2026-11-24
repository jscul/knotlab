# Does a birth that takes a shared distinction let growth finish a structure with a hidden excess?: pre-registration

Ticket `REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C` of epic `REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001` (the arm ticket B's pre-registration left for after ticket A; G18 with G17), 2026-11-23. Frozen before the study's code is written or run. Code by a Claude Opus sub-agent from this note; analysis and verdict by the thread. The canonical K1–K3 test is unchanged.

## The question

Ticket B found that ordinary growth changes how much each old word counts and never which old words are allowed, and that every start it lifted to a hidden excess already held a distinction with three holders. Ticket A stated the re-reading move as a growth law, rule R: a knot that owes more loose distinctions than it holds pays the rest with shared ones. Two questions. Under rule R, does any part of a structure with a hidden excess gain one, and is the gain owed to a birth that took a shared distinction? And which single added knots, each with a fresh distinction so that no old word is forbidden, lift a part with at most two holders per distinction to a hidden excess?

## In standard terms

A search of constraint networks, produced by a degree-relaxed synchronous rewriting rule from sub-networks of known examples, for projected relations on six designated variables that admit a CHSH value above 2 under exact no-signalling with a supplied post-selecting constraint; and an exhaustive census of single soft constraints (a not-all-equal constraint with one private variable, which multiplies the weight of an assignment by 2 or 1) added to such sub-networks.

## Prior work in the program

`python3 -B scripts/track.py objects "one added not-all-equal knot with a fresh distinction on shared distinctions lifting a hidden score from two" --until 2026-11-23 --exclude REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001`

`python3 -B scripts/track.py objects "growth under the re-reading law from founder starts of structures with a hidden excess" --until 2026-11-23 --exclude REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001`

`python3 -B scripts/track.py objects "which single births give a structure a hidden excess census of taken sets" --until 2026-11-23 --exclude REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001`

`REVIEW-LEADS-20261123-001` — a relative: its present-words ticket scored pairs of sides with two holders per distinction and found at most exactly 2 when hidden; its both-laws ticket imposed two laws on every knot, which is not what is done here.
`FOUR-READINGS-20261120-001` — a relative: settings inside the state with complete records under one common weighting; bound of 2.
`COPIES-AND-MEETINGS-20261120-001` — unrelated object.
`THIRD-HOLDER-20261123-001` — the source of the targets and of the move: a birth that takes a distinction already held twice, and the ceiling for a given weight ratio.
`OVERLAP-READ-20261111-001` — unrelated object.

Seen before this freeze: the results of ticket B and the preliminary tables of ticket A (rule R changes no recorded source; about 85% of the sparse draws that stall at once grow under it; payments happen at round 1 only; no old word fails to extend). By the thread's own check: ten of ticket B's starts with at most two holders, each of 7 knots, hidden, score exactly 2, lack one knot nae(y3,k1,k2,k3) whose three other distinctions already have two holders; given one fresh distinction, that knot lifts them to 271/135 (two starts) or 541/270 (eight), hidden. Nothing under rule R on these starts and no census of added knots has been run.

## Prior work outside the program

None found beyond what the third-holder epic cites (local models with selection: Pearle 1970; Garg and Mermin 1987).

## Settled by construction (stated, not tested)

Every birth in either arm has a fresh distinction, so no old word is forbidden and the set of allowed observer words never changes; the seven-knot structure stays out of reach under rule R as under ordinary growth. A parity birth gives every old word the same number of completions. A not-all-equal birth with f fresh distinctions gives 2^f completions when what it takes is not all equal and 2^f − 1 when it is; arm 2's knot therefore counts an old word twice when T is not all equal in it and once when it is. On the ten known starts no knot is short, so rule R is ordinary growth there and gains nothing (ticket B).

## What is supplied

The starts (parts of the census's structures); the observers and the setting births, which take distinctions that may already be shared; the equal weighting of finished words; rule R, its conventions and the choices drawn; the law given to each newborn; arm 2's knot, which is a supplied knot and not growth. Each is a scaffold and is recorded as one at close.

## Definitions (frozen)

- **Starts.** The 49,961 founder starts of ticket B with their targets and observer distinctions. Two-holder: every distinction of the start has at most two holders (12,147); three-holder: the rest (37,814). Stalled: the start stalls at round 1 under ordinary growth (6,312 two-holder and 21,575 three-holder).
- **Weighting, records, hidden, score, hidden excess.** As in ticket B. A gain is a hidden excess at a later stage of a start that has none at stage 0.
- **Arm 1, growth under rule R.** Rule R as frozen in ticket A, by its engine on full holdings, with a fresh distinction for every birth (every start holds a not-all-equal founder, as in ticket B), for 3 rounds or until a stage passes 20 distinctions. Every stalled start is grown under conventions O and N. Each two-holder stalled start is also grown under every allowed round-1 choice when there are at most 64, and otherwise under 62 more choices drawn by seed 2026112350. Each newborn is even parity, odd parity or not-all-equal: every assignment when there are at most 4,096, otherwise 4,096 drawn by seed 2026112351 with one generator per history. Histories enumerated in full and histories with drawn choices or assignments are counted apart.
- **Paying birth.** A birth that takes at least one distinction that already has two or more holders.
- **Gain through a payment.** A gain at some stage and assignment such that the same stage, with every paying birth of the history changed to even parity and the other laws kept, has no hidden excess.
- **Arm 2, one added knot.** For each two-holder start with no hidden excess at stage 0 (12,073): one not-all-equal knot that takes a set T of 2, 3 or 4 of the start's distinctions and one fresh distinction, for every T. No growth is run.
- **Classes of T.** By shared distinctions in T: none, one, two or more. By observers: T inside one observer's three distinctions (the form of a setting birth); T holds observer distinctions of one side only and others; T holds observer distinctions of both sides; T holds none. By origin: T is what some round-1 birth takes under ordinary growth from that start; T is what some round-1 birth takes under rule R for some allowed choice (every choice when there are at most 4,096, otherwise recorded as not decided); neither.
- **The known shape.** T is one loose observer distinction and three shared distinctions.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Checks of the code. On 500 drawn two-holder starts with no short knot in any round, arm 1's engine gives ticket B's knots per stage and its number of tables with a hidden excess per stage (three-law version); the same comparison on 500 drawn three-holder starts is reported, since ticket B read their meetings its own way. Tables agree with word-by-word enumeration on 100 drawn grown stages of arm 1 and 200 drawn pairs of start and T of arm 2. Allowed observer words never change in either arm. The ten known starts give 271/135 (two) and 541/270 (eight). | any fails on the two-holder starts |
| P1 | Under rule R no two-holder start without a hidden excess gains one, under any convention, choice or assignment tested. | one does: the smallest is reported in full, and whether it is through a payment |
| P2 | Under rule R some stalled three-holder start gains a hidden excess through a payment. | none does |
| P3 | In arm 2 no T made only of loose distinctions gives a hidden excess. | one does |
| P4 | In arm 2 some gain has a T that is not of the known shape. | every gain has the known shape |

P3 adds to ticket B only the sets that ordinary growth does not group and the starts that stall. Whatever P1's verdict, arm 2 reports for every gain whether rule R or ordinary growth makes that T at round 1 of its start.

## Runs and stop rule

One script per arm and one for the checks. The study stops when both arms are done. It reports: for arm 1, residual stalls at round 1 by class, histories and tables tested, gains by class, in full enumeration or drawn, through a payment or not, and the share of stalled three-holder starts that grow and gain beside ticket B's 34 of 7,957 under ordinary growth; for arm 2, the number of starts, sets and gains by each class of T, the least T that works, the largest score, and the smallest gain in full. Every run stays under ten minutes and under 12 GB; work is split into runs and nothing is stopped by the clock. Nothing is tuned after values are seen; a changed definition is reported with both versions. Deviations go in `deviations.md` in the experiment family. Results are referee pending.

**Advisor.** Claude Fable 5.2 reviewed the design cold before this freeze (`research/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001/advisor/question_c.md`, `answer_c.json`). Its strongest objections: a gain under rule R may come only from the round no longer stalling, with ticket B's birth on loose distinctions doing the work, so the prediction about three-holder starts was near-certain and said nothing about re-reading; a null on drawn assignments is a sample and not a census; arm 2 is a supplied knot and not growth, and a T inside one observer's distinctions repeats that observer's setting birth; the prediction that some start beyond the ten known gains was nearly foregone. Changes: gains are classed as through a payment or not and P2 asks for one through a payment; full enumerations are counted apart from draws; T is classed by its relation to the observers and by whether either rule makes it; P4 asks for a different shape of T. Its cheaper first test, rule R on the ten known starts, is settled above: no knot is short there.
