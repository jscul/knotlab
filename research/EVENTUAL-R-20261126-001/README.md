# Rule R read off the whole structure: well defined, consistent with earlier readings, and bounded?

Epic `EVENTUAL-R-20261126-001`, under G18, at the coordinator's go-ahead after `NO-WHOLE-STATE-20261126-001`, whose
rule R (two values commute exactly when some knot holds both) forces an odd closing sign at 12 of the 121 closed
patterns growth reaches but changes at a birth when read stage by stage. Under the owner's reading of layers (nothing
changes over time; rounds are a reading outward of one fixed unlimited structure), a rule read off the whole is not
disqualified for being unreadable mid-growth. So R is tested here in that form: two distinctions have a joint value
exactly when some knot of the whole structure holds both. Computed; the advisor consulted read-only in the repository
([question](advisor_question.md), [answer](advisor_answer.md)); referee pending.

**Words.** A *read set* is a set of distinctions whose values commute under R (every two held by a common knot), so one
reader can read them together. Its *laws* are the products of knots whose distinctions left over after cancelling lie
inside it, each with the sign of that product. The *counting state* is the one the signed knots fix: every knot even
except, in each closed component, its last knot, which takes the sign the component's product forces; read by counting,
it is uniform on each read set's allowed words.

## A. Part counting against the state's counts ([`part_a.py`](part_a.py), [output](part_a_out.txt))

Run first, as the cheap direction the previous study named (its stop condition: all agree, or a counterexample; no
predictions were frozen for it). On the 21 census types where R makes every knot commute, every nonempty subset of
every maximal read set: 3,789 read sets. Four rules for the laws on a read set:

| Rule | Agrees with the state's counts |
|---|---|
| (iv) every element of the group the signed knots generate, enumerated | the reference |
| (iii) products of knots, signed by the operator product | 3,789 of 3,789 (a check of the code) |
| (i) the closed part rule: knots wholly inside, each with its own sign | 3,774; the 15 others all on the one type with a cut knot |
| (ii) products of knots, signed by the GF(2) sum of their signs | 3,685; the 104 others on every type where R forces an odd sign, and on the cut-knot type |

So **counting within a part reproduces the state's counts wherever no knot cuts the pattern**: under R, the counts
within each part are the literature's stabiliser statistics on these 21 types. And where the closing sign is odd,
products of knots read with GF(2) signs contradict themselves on every knot's own places (the product of the other
knots gives the same distinctions with the opposite parity): the reordering sign is what keeps them consistent.

## B. R read off the whole structure ([`part_b.py`](part_b.py), [preregistration](preregistration.md), [tally](tally_out.txt), [rows](part_b_census.jsonl.gz))

**Is it well defined?** Yes, pair by pair. A birth takes only loose distinctions, one from each parent, and a funded
round takes every loose distinction (the engine, `rival_growth.py` lines 71 and 81, read by the advisor). So two
distinctions settle as soon as either is held twice (no later knot can hold it) or one knot holds both; only pairs of
loose distinctions of two different newest knots stay open, and they settle in the next round. A closed or stalled
structure is the whole, and everything in it is settled. The commutation of two knots changes from one round to the
next only between two knots born in the earlier round, by the parity of their common children: **1,035 changes on the
300 sampled starts, every one predicted by that formula.**

**Sample.** 300 census starts (three to five knots, uniform over the census, seed 20261128, one vote per start),
ordinary parity growth on the canonical engine for up to four rounds: 96 closed, 70 stalled, 134 still growing.

**Is any earlier reading contradicted?** Not one that signs by the operator product: with the whole's R and signs, the
laws from the knots read so far are a part of the whole's laws with the same signs (entailed, as the advisor pointed
out), and on the closers whose knots commute no read set even gained a law from a later layer (0 of 10). The reader who
*is* contradicted is the one the engines describe, who signs a product of knots by the GF(2) sum of their signs: on all 4
closers whose sign R forces odd it meets a contradiction (on the knots' own place sets, as in part A), and on the 6 that
R forces even it never does.

**But the whole has no state on almost every start.** Under R read off the whole, some two knots' operators fail to
commute, for good, on **290 of the 300** sampled starts: on all 134 still growing (112 already at round 0, the rest by
round 2), on all 70 that stall, and on 86 of the 96 that close. Two knots whose operators fail to commute cannot both
read their own law with certainty in any state, so **what R contradicts is the knots' own laws**: no state makes every
knot hold. The 10 starts where every knot pair commutes are all closers (two of them closed at the start); R forces the
closing sign odd on 4 of them (six knots each) and even on 6.

**The demand for a state as a prediction.** At the 36 growing rounds before a start's first failing pair, some choice of
the open pairs would make every knot pair commute (unique at 13), and the next round realises one at 16. Once a pair
fails, no choice exists (589 rounds). So the demand that a state exist predicts the next round less than half the time
and is refuted, finally, on most starts at once.

Predictions (frozen): 1 held (every growing start has a settled failing pair by round 3); **2 failed** (only 10 of the
96 closers have commuting knots, not more than a third: the advisor's guess that small closures mostly commute was
wrong under this weighting); 3 held (no exception to the flip formula); 4 held (16 of 36); 5 held (4 of 4 odd, 0 of 6
even); 7 not tested (in the advisor's small case no birth had both knots as parents, and the pair settles commuting).

## C. The bound under R with one state ([`part_c.py`](part_c.py), [output](part_c_out.txt))

- **Where a state exists, the tables are the literature's quantum ones**, so nothing reaches the no-signalling maximum
  where the quantum limit is lower: Tsirelson's 2√2 for two readers (1980) holds for any state and commuting readers'
  values. With the counting state and values that are products of distinctions' values, CHSH is at most 2 (if three of
  the four pair products are laws the fourth is too; if one reader's two settings fail to commute at most two are laws):
  the advisor's argument, checked by hand. Computed only for single distinctions, where every pair correlation is 0
  (no product of knots leaves exactly two distinctions), so the computed check is weak. The previous study's referee
  showed that a counting state read with values that are *not* products of distinctions' values can reach 14/5.
- **Three readers reach 4, which is the quantum value:** on the four-knot closure, readers (0,5), (1,4) and (2,3), the
  four scored correlations are +1, +1, +1, −1 and the three-reader value is 4 against at most 2 for a list of values
  (Mermin, 1990); 4 is also the most any three-reader table can give, so it exceeds nothing quantum.
- **The two-reader 4 is excluded under R**: the pattern of part A of the previous study has no state with its odd sign
  under R or under any choice of which pairs of values fail to commute, among values that pairwise commute or
  anticommute (it is outerplanar; the previous study's R3).
- **But these are tables read inside knots.** Under R two values can be read together only if a common knot holds
  both, so every reader whose values are read jointly with another's shares knots with it: the tables show the
  literature's contextuality, not readers separated from each other. Readers whose knots never meet have no joint
  table under R at all.

## What this does not say

- That growth makes R or any state; every engine still signs by GF(2).
- Anything about other commutation rules, or about R on structures read past four rounds (pairs are settled or open,
  so nothing open was read as failing).
- That the counting state's CHSH bound of 2 was computed for products of values (argued only).

## Scaffolds

R itself (beside the current rule, all values commute, and the free choices of the previous study's R3); the round
limit, made harmless by classing pairs settled or open (the flip formula is the second choice: it predicts every change
one round on); the engine (canonical; not swapped); the weighting of starts (uniform over the census, seed 20261128; not
swapped); the realisation of values (no relations beyond R); the counting state. The 290-of-300 finding is about R; the
flip formula and settling are about the growth law.
