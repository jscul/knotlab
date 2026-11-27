# Does the binding step repeat? A third layer of whole-held facts

Epic `THIRD-LAYER-20261126-001`, at the coordinator's go-ahead after the built-binding referee. A check by the thread,
not a registered study; computed. The sections down to "Frozen" were committed before the frozen runs (`965e73547a`).
Refereed (R1: **refuted, two Blocks**; folded in below).

> **Referee R1: refuted** ([report](referee-R1/report.md), [proof](referee-R1/argument.md)). **Block:** "one
> second-layer knot per connected start, and no two can share a fact" is false. On the three-ring start of rings of
> four knots (split attachments, double links), the whole-ring facts R, S, T and the first ring's two alternating
> family facts P, Q have pairwise disjoint carriers and obey exactly two independent equations, R + S + T = 0 and
> P + Q + R = 0, each triple taking exactly 000, 011, 101 and 110; at round 5 all five are class facts at the scale of
> twelve and no single knot has a class fact of its own; removing one start law frees only the first triple, one birth
> law only the second ([certificate](referee-R1/ring_overlap_counts.json)). A 48-knot start gives another, and on
> thirteen five-knot rings a third-layer knot exists under a chosen reading (18 selected second-layer knots; two more
> eligible knots make its facts locally readable). Whether ordinary growth selects a further layer is open.
> **Block:** Conjecture B as stated (its hypothesis is impossible as worded, and a nine-knot ring grouping keeps a
> least flip of four for twelve rounds). **What holds, now proved by the referee:** no birth mixes families (0 of
> 23,149); the one relation among the named family facts; the least change flipping a nonzero sum of family facts grows
> by exactly two each funded round (all 14,876 comparisons); a start parity outside the family span is flipped by a
> change of at most the larger of four and the number of start knots. **Narrowings:** T4's membership test held for
> the nonconstant family facts (645 null rows were skipped by the scorer); at the larger scale the family facts are
> held by no part on 8 of 12 constructions (not 10), the whole-ring facts on 4 of 12; the scale description of
> Conjecture T; the solver's outputs (None for a fixed parity, a string above the cap).

## The question

The coordinator: take a start in which several second-layer knots exist (groups of rings, each group's facts bound by
a parity rule) and those second-layer knots share whole-held facts the way first-layer knots share distinctions; ask
whether, after ordinary growth, a fact exists that no single ring and no single second-layer knot reads, and whether
such facts are again bound. Stop at a third layer with a frozen test, or at the reason the step does not repeat.

## The advisor's answer, and what it predicts ([question](advisor/question.md), [answer](advisor/answer.md))

**Families.** Join two live knots of the start (knots holding a loose distinction) when some knot shares a distinction
with each (the engine's candidate rule); the classes are the start's **families**, and a family's fact l_A is the
parity of its knots' loose distinctions. **Claim T (two kinds of fact).** Under ordinary parity growth a family's fact
*lasts*: the least change flipping it grows by two distinctions a round. Every other class fact is *bounded*: the least
change flipping it is fixed by the start. **The one relation.** A sum of start laws supported on loose distinctions
takes the same coefficient across every shared distinction, so it is all the laws of a connected part or none (the
component lemma of the closing law); hence the facts l_A of a connected start obey exactly one relation, the sum of all
its laws. **So the step does not repeat by itself:** on a large enough scale the facts that growth keeps are the
families' facts, bound by one second-layer knot per connected start; two second-layer knots that share a fact would
need two relations; a further layer could only sit in changes the start already has, which growth leaves as they were.

## Seen before the freeze

- **The binding facts are sums of single-knot facts at small scale** ([`jointly.py`](jointly.py),
  [`jointly_examples.py`](jointly_examples.py)): on all 32 built ring families and all 19 sampled bindings, each bound
  fact is a sum of class facts that single connecting knots read; only the 14-knot start and the sampled ten-knot start
  (shortest changes) bind facts held by no part (logged as a narrowing of the built-binding study).
- **Lasting and bounded, on one start** ([`minflip.py`](minflip.py), [`explore_flip.py`](explore_flip.py)): on the
  three-ring start of five-knot rings with double links, the least change flipping a ring's fact is 5, 7, 9, 11 and 13
  at rounds 0 to 4; flipping a connecting knot's attachment parity takes 5, 7, 9, 11, then 12. At round 4, at the scale
  of twelve (a small change is any allowed change of at most twelve distinctions), no knot reads any class fact of its
  own and the three ring facts are class facts held by no part ([`scale.py`](scale.py),
  [`explore_scale.py`](explore_scale.py)). At the scale of five they are sums of single-knot facts.
- [`twokinds.py`](twokinds.py) on three built families: six families (rings of four split into two each), one rule over
  six facts, flips 3, 5, 7, 9 and 11, no birth across families.

## Frozen

**Sets.** A seeded sample of 1,000 census starts of three to five knots (`random.Random(20261215)`), the 900 fresh
starts of six to eight knots, the 400 sampled starts of nine to twelve knots (`forbid.sampled`, seed 20261212 + n, the
extension's weighting with at most 30 distinctions), the 32 built ring families and the 14-knot start, and the merge
control (each of the 16 three-ring families with one more knot, holding no loose distinction, that shares two
distinctions with a knot of the first ring and one with a knot of the second). Rounds 0 to 4 of ordinary parity growth,
until a round stalls, closes or passes 300 distinctions.

**Predictions** ([`twokinds.py`](twokinds.py)).
- **T1.** No birth has parents descended from two families.
- **T2.** On every connected start, the families' facts take the joint values of one parity rule with every proper
  subfamily free (m ≥ 3 families), are tied (m = 2) or fixed (m = 1). On the merge control m drops by one.
- **T3.** On every start and family whose fact is not fixed, the least change flipping it at round t is at least its
  round-0 value plus 2t.
- **T4.** Where rounds 3 and 4 are read, the number of class facts under changes of at most five distinctions is the
  same at both, and from round 3 every family's fact is one of them.

**Read, no prediction.** On the 16 three-ring families at round 4, at the scale one below the families' least flipping
change: which bound facts are held by no part.

**Stop.** T1 to T4 as predicted: the reason the step does not repeat under ordinary growth is the one relation per
connected start among the facts that last. A start breaking T1 or T2 (two relations among lasting facts in one connected
start) is the third-layer candidate, frozen and tested on its own.

**What it would not show.** The forbidding cuts (they can add relations among family facts: the built-binding referee
found seven constraints in one round on two of its cut starts); capped group rules; rounds past 4; a proof of claim T.

## What was found

All frozen runs finished ([`score.py`](score.py), [`score.json`](score.json)); no deviation.

**T1 to T3 and T4's dimension test held on every start read; T4's membership test held for the nonconstant family facts** [R1] (2,349 starts: 1,000 census, 900 held-out, 400 sampled, 33
built, 16 merge controls; 6,481 rounds read). No birth had parents descended from two families (T1). The families'
facts took the joint values of one parity rule with every proper subfamily free on every connected start with three or
more families, were tied on every start with two and fixed on every start with one; the merge control lowered the
number of families by one on all 16 (T2). The least change flipping each family's fact grew by at least two
distinctions a round on every start and round read (T3). Where rounds 3 and 4 were read (945 starts), the number of
class facts under changes of at most five was the same at both, and every family's fact was one of them (T4). Families
on the census sample: 715 starts have one (their fact is fixed), 245 two, 8 three, 32 none; on the held-out starts 142
have three or more; on the larger sample 54.

**The read at a larger scale** ([`scale_read.py`](scale_read.py), [`frozen_scale_read.jsonl`](frozen_scale_read.jsonl)):
on the three-ring built families at round 4, at the scale one below the families' least flipping change (10 for rings of
four, 12 for rings of five and seven), the families' facts are class facts on all 12 read, and held by no part on 10
of them [R1: 8 of 12 for the family facts, 4 of 12 for the whole-ring facts]. On the paired rings of five and seven each connecting
knot's own parity of its two attachment distinctions is still a class fact at that scale, and the families' facts are
sums of them; a later round or a larger scale was not run. The four families of rings of six passed the size cap.

**[Withdrawn: Block, referee R1.] So the step does not repeat under ordinary growth, and this is the reason.** It
does not follow: the one relation holds among the named family facts, but sums of family facts can have carriers of
their own, and any linear dependence among three or more separately carried facts is a second-layer knot. The referee
found two sharing a fact on a frozen start (below).

**Not run.** The forbidding cuts (which can add relations among families' facts), capped group rules, rounds past 4,
rings of six at round 4, and a built start whose closed changes carry a third layer (the advisor's 32-knot candidate,
which does not grow).
