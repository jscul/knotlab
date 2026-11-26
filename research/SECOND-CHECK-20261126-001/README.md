# The second kind of check: is it already in the structure?

Epic `SECOND-CHECK-20261126-001`, under G18, at the coordinator's pick after the two-class study (the rings' classes are
the sectors of a classical code; a quantum code has a second kind of check that puts a relative sign between sectors).
The coordinator's reading, to test: in the literature's toric code the second check lives on the dual, where the roles
are exchanged; here, read each move (a shortest allowed change through a distinction) as a knot holding the distinctions
it changes. Is that exchanged pattern lawful, does growth commute with the exchange, does its constraint act as the
ring's long change? Only if no native check exists, would a supplied rule acting by the long change let a local reader's
statistics show a relative sign, with free settings and no signalling? Computed and argued; advisor consulted read-only
in the repository ([question](advisor_question.md), [answer](advisor_answer.md)); referee pending.


> **Refereed (R1, [report](referee-R1/report.md)): confirmed with fixes, no Block.** All 26 pinned exchanged holders pass the
> record's knot test, and neither reading of the exchange selects a relative sign. **Narrowings:** the pinned exchange
> was confirmed to give back the bare ring at five, seven and eight knots (not six); at eight knots two least free reads
> use only loose distinctions and two least pinned changes avoid every old ring distinction; short moves keep either
> relative sign, which a supplied class-changing read can tell apart. **Not a block:** exchanging twice does not give
> back the grown ring, so the intuition that the two are each other's dual fails; the repetition-code comparison is a
> comparison, not an equivalence; the two-ring square would need readers holding parent-to-child distinctions.
> **And a later correction by the thread** (the both-distances study, `BOTH-LONG-20261126-001`): "one distance is always
> short" holds after one round only; grown further, a ring's class has both distances equal to n on odd rings (from
> about (n − 1)/2 rounds), and on even rings one distance equal to n with the other growing by two a round. Logged in
> `docs/CORRECTIONS.md`.
## What was found ([`dual.py`](dual.py), `rings_dual.jsonl`; [`commute.py`](commute.py), [output](commute_out.jsonl))

Rings of n knots with two loose distinctions each, parity, one round of ordinary growth.

| | Loose values free | Loose values pinned at zero |
|---|---|---|
| The exchanged pattern | not lawful: two-place pieces from loose pairs, a distinction held by up to five to eight moves | n = 5, 7, 8, 9, 10: a ring of n four-place knots, every distinction held by at most two (the local test only; the pinned preparation already fails the record's forgetting test at its new loose holders, motion study) |
| Least class label (to read the class) | n (a whole cycle) | 3 |
| Least class change (to change it) | 5 (four neighbouring knots) | n (the old ring) |

- **The exchange undoes growth.** With loose values pinned, the grown ring's exchanged pattern is the bare ring itself,
  up to renaming (n = 5, 7, 8, 9, 10; not n = 6). Growth does not commute with the exchange: the bare ring's exchanged
  pattern is one knot holding exactly the old ring (the long change itself, read as a check), and growing it gives n + 1
  knots of n places.
- **One distance is always short.** Free, the class is read only across a whole cycle but changed by five distinctions;
  pinned, read by three and changed only across the whole ring. The structure is the literature's repetition code in one
  reading or the other, not the toric code, where both distances grow. On even rings the pinned classes are made by the
  pinning (the free moves already span the old ring there).

## Is it a second check? (the argument, with the advisor's counterexamples)

- **Read as a parity law on values**, the exchanged knots are a further classical restriction (with the original knots
  they leave four states on the pinned rings of five and seven knots, checked), not a conjugate check.
- **Read as invariance of the weighting under the moves**, they are the motion study's own reading ("a weighting fixed by
  a group H of changes is exactly a constant on each set x + H"): already recorded, with both signs between the classes
  left free. The relative sign is a preparation, not a check.
- **Its lawfulness needs the pinning**, a choice, which also decides which distance is short and makes the even rings'
  classes.

**So there is no native second check.** A supplied one works in the narrow sense the record already shows: with loose
values free, the motion study's supplied change read of a five-distinction class change shows the relative sign to one
reader holding four neighbouring knots, +1 with certainty on one sign and −1 on the other. With two readers splitting the
pinned old ring, the product of their change reads shows the sign while each marginal stays fair, and nothing signals;
but a shared hidden value reproduces that table, so it is no excess. The advisor's remaining lead: two pinned rings, each
split between the same two readers, give each reader two anticommuting pairs of a read and a change, the setting of the
literature's Mermin–Peres square; under the motion study's supplied change read and probability rule that square would be
the supplied quantum rule again, as the four-settings study already showed for three readers.

## What this does not say

- That no growth rule could make a second check; the pinning and the move rule are scaffolds (A291).
- The Mermin–Peres square on two rings was not computed (it would test the supplied reading, not growth).
- Not-all-equal (no classes there in what was read).
