# A built binding of three whole-held facts: made by the law, and does growth make one?

Epic `BUILT-BINDING-20261126-001`, at the coordinator's go-ahead on the advisor's top direction and, after the binding
study's referee reported, on the coordinator's request for a careful test of its constructions. A check by the thread,
not a registered study; computed. The sections down to "Frozen" were committed before the frozen runs.

## The question

The binding study's referee (`BINDING-20261126-001`, R1: refuted, two Blocks) found starts where ordinary parity growth
binds three facts that no single knot reads: a built 30-knot start (three rings of five knots, each ring knot holding two
loose distinctions, connecting knots holding none), where three disjoint cycles of distinctions born in round 1 take
exactly 000, 011, 101 and 110 at round 2; and one of the study's sampled ten-knot starts, where three path parities bind
at round 3. The coordinator's question: is such a binding made by growth, or is it the sum of the knot laws read off the
start? And which of the owner's rungs does it reach?

## The origin test

A carrier is a set of distinctions read as the parity of its values. On a grown stage it is a function of the start's
values on the allowed states exactly when its parity plus some sum of the stage's laws is supported on the start's own
distinctions (`repro.old_representative`). Ordinary growth keeps the start's allowed states on the start's distinctions
(the projection lemma, refereed in `LAYERS-20261126-001` and `BINDING-20261126-001`). So when every carrier of a binding
has such a representative, the carriers' joint values are their representatives' joint values on the start's allowed
states: **the relation was in the start**, and what growth adds is the carriers and their being kept by every small
change (class facts). When a carrier has none, the relation can be new.

## Seen before the freeze

All with the thread's own code ([`repro.py`](repro.py), the canonical engine `forbid.grown`, linear algebra over two
values checked against a solver call per tuple).

- **The advisor's 14-knot start** ([`built.py`](built.py), [`built_explore.jsonl`](built_explore.jsonl),
  [`built_controls_explore.jsonl`](built_controls_explore.jsonl)): three rings of four joined through two knots that
  share one distinction (31 distinctions). At rounds 0 to 3, under both readings of a small change, the three ring
  parities are class facts no single knot reads and take exactly the four even triples; the forced sum is the sum of the
  laws of the eight knots holding no loose distinction. The canonical checker passes the relation for every choice of
  contact ([`checker.json`](checker.json)); with two loose distinctions at a joining knot it allows all eight and is no
  knot. Controls: with the shared distinction of the joining knots removed, the facts are not class facts under the
  shortest changes at rounds 0 and 1 and are again at rounds 2 and 3 (the relation is there throughout); with one loose
  distinction at a joining knot the relation is gone (eight triples, the start stalls at round 1). So this binding is
  the start's, from round 0.
- **The referee's three ring preparations reproduce** ([`repro_explore.jsonl`](repro_explore.jsonl)): the 30-knot start
  and the two 21-knot ones, at rounds 2 and 3, under both readings. Removing any one start law, or any one law of the
  births that made the carriers, frees all eight triples. **Origin:** every carrier is a function of the start's
  values (its representative is its ring's ten loose distinctions), and those already obey the relation on the start's
  allowed states. At the start the representatives are not class facts under the shortest changes in the 30-knot start;
  in the two 21-knot ones they already are.
- **The ten-knot path witness reproduces** at round 3, on the referee's own stage ([`repro_paths.py`](repro_paths.py),
  [`repro_paths.json`](repro_paths.json)): four of eight triples, each carrier a class fact under the shortest changes
  and read by no single knot. Under changes of at most five distinctions two of its three carriers are not class facts.
  Origin: the same; the relation holds on the start's allowed states (nine of its ten start laws enter it).
- **The cut construction reproduces** ([`repro_cuts.py`](repro_cuts.py), [`repro_cuts.jsonl`](repro_cuts.jsonl)): on
  the 30-knot start with the three middle knots of the links joined pairwise and holding one loose distinction each,
  the three rings' loose groups take all eight triples at the start and under ordinary growth; under either forbidding
  cut one birth of three parents gets no fresh distinction and its law leaves the four even triples at round 1 (then
  the round stalls). This relation is new: the cut law makes it.
- **Every class fact is a function of the start's values** on every stage read ([`origin_scan.py`](origin_scan.py)):
  11,802 census stages and 1,196 held-out stages, rounds 1 to 3 of ordinary parity growth, under both readings. So on
  these stages no relation among class facts is made by growth.
- **The closing test** ([`closing.py`](closing.py)): a birth's law is implied exactly when its inputs are every loose
  distinction of its parents' connected structure, on all 37,722 census and 6,032 held-out parity births; under
  not-all-equal none of the 2,944 births that take every loose distinction is implied. This is the proved closing law of
  `ERASURE-AND-CLOSING-SIGNS-20261121-001B` (closing_law.md), read as the advisor's next-layer law: the sum of all the
  knot laws of a structure, which the growth reads when it closes.

## The argument (the advisor's sketch, to be tested)

From the advisor's review in the repository ([question](advisor/question.md), [answer](advisor/answer.md)). Read the
stage with the start knots removed: the births of rounds 1 to t, each new distinction joining its two holders, each
loose one joining its holder to one outside point U. The allowed changes that leave every start value as it was (Z_new)
are the closed loops of this reading. Three premises, read in the engine and checked here on every birth record
([`premises.py`](premises.py)):

1. no birth takes two distinctions of one parent, and each round takes every loose distinction of every live knot;
2. any two live knots with a common neighbour are parents of one birth of the next round;
3. a birth with no fresh distinction is the only birth of its connected structure, and each of its parents holds one
   loose distinction.

A round-s birth meets only its parents (round s − 1), its children (round s + 1) and, if newest, U, so the reading has
no loop of three, and by premise 1 its only loops of two are pairs of loose distinctions at one newest birth. Adding an
older birth w with children v and v′: by premise 2 the two children have a common neighbour (a common child, or U), which
closes a loop of four, and every other loop through w differs from these by loops not through w; by premise 3 a child
with no fresh distinction is w's only child. So Z_new is spanned by the pairs and the loops of four, each of which is a
shortest change through its distinctions. Then every class fact (even on every small change, under either reading) is a
function of the start's values; with the projection lemma, **every relation among class facts of an ordinarily grown
stage already holds among their start representatives**, and it is a sum of the start's own laws.

## Frozen

Committed before the runs below. Code: [`families.py`](families.py) (parts built, controls, nae, cuts, sampled),
[`premises.py`](premises.py), [`origin_scan.py`](origin_scan.py), [`repro.py`](repro.py) (whose sum of the
representatives now covers any number of carriers; it tested only three before).

**Sets.**
- **Built ring families** (a hand-built start, scaffold): R = 3 or 4 rings of n = 4, 5, 6 or 7 knots, each ring knot
  holding two loose distinctions; for every pair of rings two connecting knots holding none, attached split (one
  distinction with ring knots p and p + 2) or paired (two with ring knot 2p), linked double (two shared distinctions)
  or by a detour (one, and a chain of three knots each meeting the next twice): 32 starts. Ordinary parity growth,
  rounds 1 to 3. Carriers: at each round t ≥ 2 the fresh distinctions of the round-(t − 1) births of each ring's
  lineage; at every round 0 to 3 each ring's own loose distinctions (the start groups).
- **Controls** on the same 32: one loose distinction at the middle knot of the first detour (detour members) or at the
  first connecting knot (double members); the links made loose (each connecting knot's link places become loose
  distinctions). The origin control: at round 1 of each built start, one birth's first fresh distinction, its other
  fresh distinctions, and its inputs.
- **Cuts**: the R = 3 detour members with the three middle knots of the detours joined pairwise and holding one loose
  distinction each (the referee's modification), under the ordinary count and both forbidding cuts.
- **Not-all-equal**: the 32 built starts grown under not-all-equal, the same carrier rule, joint values by a solver.
- **The argument's premises and span**: every census start of three to five knots, the 900 fresh starts of six to
  eight knots, the 32 built starts, and fresh sampled starts of 9 to 12 knots (`forbid.sampled`, 100 of each size, seed
  20261212 + n; the extension's weighting: each pair of knots meets with chance 1/3, once or twice equally, each knot
  holds 0, 1 or 2 loose distinctions equally, kept when connected, every knot has three places and there are at most 30
  distinctions), rounds 1 to 6 or until the round stalls, closes or passes 20,000 distinctions; the span check on stages
  of at most 400 distinctions. Starts that give no stage are counted. Also under both cuts, as a read.

**Predictions.**
- **P1 (built, ordinary).** (a) At every round read the start groups take exactly 2^(R − 1) tuples with every proper
  sub-family free, and from round 2 on so do the new carriers: one parity rule, the canonical checker passing it for R
  = 3. (b) For n = 5 and 7, every new carrier at rounds 2 and 3 is a class fact read by no single knot under both
  readings of a small change; for n = 4 and 6 read, with no prediction. (c) Origin: every carrier has a start
  representative, the relation holds on the start's allowed states, and its sum is a sum of start laws.
- **P2 (the argument).** Premises 1 to 3 hold on every birth record of every round read, and on every stage of at most
  400 distinctions the pairs and loops of four have rank dim Z_new and lie in it. The origin control fails the origin
  test (the first fresh distinction is not a function of the start's values) while its three carriers obey one parity
  rule: the test can say no.
- **P3 (controls).** With a loose distinction at the middle knot of a detour, the start groups take all 2^R tuples at
  every round read. With the links made loose, the start groups take all 2^R tuples at every round read, or the
  round stalls. With a loose distinction at a connecting knot of a double link: 2^R tuples, or a stall.
- **P4 (cuts).** On every cut member, under each cut, one birth whose parents are the three middle knots gets no fresh
  distinction at round 1, and the start groups go from 8 tuples at round 0 to 4 at round 1; under the ordinary count
  they take 8 at every round read.
- **P5 (not-all-equal).** Read only: parity carriers are not this law's facts (the advisor), so their tuples are
  reported with no claim.

**Stop.** All of P1 (a, c), P2, P3 and P4 as predicted: the bindings exist on these built starts, their relation is
the start's own sum of knot laws, and what ordinary growth adds is carriers and keeping (with the argument, on every
stage read, ordinary growth makes no relation among class facts); the cut law makes one. Any broken premise, span
rank short of dim Z_new, or carrier without a start representative: a candidate relation made by ordinary growth,
frozen and tested on its own.

**How the answer will be given** (the coordinator's parts): (a) whether, after ordinary growth, three or more facts no
single knot reads obey a relation passing the knot test, and on which starts; (b) where the relation comes from; (c)
what growth contributes: whether before growth the same quantities were read at single knots, were class facts, or
were only functions of the start's values, and after growth are class facts held only by whole carriers; (d) under the
cuts, the relation one knot law makes. Then what each of the owner's rungs requires in those terms, and which are met.

**What it would not show.** Capped group rules (the advisor expects the argument to fail there first); rounds past 6;
other laws than parity and the recorded cuts; that the built families are typical under any weighting (they are
hand-built); a next layer's own small changes and laws.

## What was found

All frozen runs finished ([`score.py`](score.py), [`score.json`](score.json)). Every prediction held as made; no
deviation. Two rounds were not read, both at round 3 of the four-ring families of six knots with detour links, past the
500-distinction cap.

**(a) After ordinary growth, three or more facts that no single knot reads obey a relation passing the knot test: yes,
on built starts.** On all 32 built ring families (three or four rings of four to seven knots, both attachments, both
links), on all 62 rows read at rounds 2 and 3, the new carriers of each ring take exactly 2^(R − 1) of the 2^R joint
values with every proper sub-family free (one parity rule; the canonical checker passes it on the three-ring start of
the advisor, for every choice of contact), and every carrier is a class fact read by no single knot under both readings
of a small change. Also on the advisor's 14-knot start from round 0, and on the binding referee's sampled ten-knot start
at round 3 under the shortest changes only. Not on any census or held-out start (the binding referee's recount), and
the 400 fresh sampled starts of nine to twelve knots were read here only for the argument.

**(b) Where the relation comes from: the start's own knot laws.** On every row, every carrier has a start
representative (each ring's own loose distinctions), the representatives take the same joint values on the start's
allowed states, and their sum is a sum of start laws: the laws of all the knots, since the connecting knots hold no loose
distinction. The controls agree: one loose distinction at a detour's middle knot, far from every ring, frees all 2^R
values at every round read (16 of 16 detour families; 14 grow to round 3 and 2 stall); the other controls free them or stall (all 64 as predicted). The
origin test can say no: a birth's own law binds its fresh distinctions and inputs, and the test finds the first fresh
distinction is not a function of the start's values (32 of 32). **And ordinary growth makes no relation among class
facts on any stage read:** premises 1 to 3 held on every birth record and the pairs and loops of four spanned the changes
that keep the start's values on every stage (21,678 census, 2,348 held-out, 192 built and 398 sampled rounds; rounds 1
to 6; 1,964 census, 483 held-out and 331 sampled starts gave no stage, because their first round stalls or closes).
With the argument above (a sketch, checked here, not yet refereed), every class fact of an ordinarily grown stage is a
function of the start's values, so every relation among class facts already held at the start.

**(c) What growth contributes: it turns the start's relation into a relation among class facts, with carriers of its
own.** Before growth the representatives were already read by no single knot (every row), but they were not class facts
under changes of at most five distinctions on any family (0 of 62 rows), and under the shortest changes only on the
double-link families (32 rows; not on the 30 detour rows). After growth they are class facts under both readings on
every row. The mechanism, read from the constructions: at the start a change of five distinctions runs from one ring's
loose distinction through a connecting knot to another ring's and flips both rings' parities; growth consumes every
loose distinction, so after it no small change leaves a ring, and the parities can no longer be flipped one at a time.
And at every round from 2 on, the relation appears again on carriers made only of distinctions born in the round
before, disjoint, each held by a whole cycle of births.

**(d) Under the forbidding cuts, one knot law makes a new relation.** On the 8 three-ring detour families with the
middle knots joined pairwise and holding one loose distinction each, under both cuts one birth whose parents are the
three middle knots gets no fresh distinction at round 1, and its law (the parity of the middles' three loose
distinctions), with the start's laws, leaves the rings' loose groups 4 of 8 joint values where the start allowed all
8. Ordinary growth leaves them free at every round. Both cut runs then stall at round 2. Under the cuts premise 3
fails (on 144 census rounds under one fewer, 192 under the arity floor), yet the span still held on every stage.

**Not-all-equal** (read only): the same carriers take every joint value on every family and round.

## The owner's rungs, in these terms

| Rung | What it requires | Met? |
| --- | --- | --- |
| Repetition | the same kind of fact, held by the whole and by no part, at two layers | yes: a knot; a class fact no knot reads (lesson 12.2); now a parity rule among such facts |
| Tower, first step | facts of one layer held by the whole, bound by a rule that passes the knot test and that nothing outside supplies, where before the step they were not such facts | on built starts, yes: the rule is the start's own sum of knot laws, and growth makes the bound quantities class facts (under changes of at most five distinctions on every family; under the shortest changes on the detour families). Under the cuts the rule itself is new, one knot's law |
| Tower, every step | the bound layer again keeps facts held by its whole, by its own small changes and its own rule, step after step | not shown: the bound triple has no small changes or laws of its own yet, and both cut runs stall |
| Recursion | a pattern that grows back into itself | not shown |

**Caveat a referee should press.** As functions on the allowed states the bound facts are linearly dependent, as the
three distinctions of a parity knot are; what makes this more than a rule we define as a sum is that each fact has its
own carrier, disjoint from the others and read by no single knot. And the starts are hand-built (register entry for
this study's scaffolds); under the sampled weightings read so far no binding was found.
