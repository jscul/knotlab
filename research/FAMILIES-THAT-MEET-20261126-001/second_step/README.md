# The second step: under a cap of 6 to 8, more than the one count crosses

Epic `FAMILIES-THAT-MEET-20261126-001`, 26 November 2026 (UTC). **A check by the thread, not a registered study.**
Its expectation was written at the head of the program before it ran; part of it held and part failed. No referee
has read this. [The first step](../first_step/README.md) · [the program](which.py) ·
[its output](which_to_round_7.jsonl)

**The first step changed one number on the second family's side, and under a cap the first family's side made
something else. Here that number is held and what lies one step beyond it is changed. Under the ordinary count and
under caps of 2 to 5 the first family's side is then the same. Under caps of 6 to 8 it differs in 11 comparisons of
27: what the first side makes then depends on the second side beyond the original they share a neighbour with.**

## What was run

The generator study's start of 21 knots, with the second family's own original b2 given two more candidate pairs
in three ways. In each b2 has degree 4, so that the knots b2 shares with the first family's originals s and t are
asked for the same number of joins. They differ one step further out:

| Start | What is added at b2 | Degree of b2 | Degrees of b2's new partners |
| --- | --- | --- | --- |
| as given | nothing | 2 | none |
| `ring` | b2 on one ring of four with three new originals (the first step's change) | 4 | 2 and 2 |
| `two` | two new partners, each on a ring of four of its own | 4 | 3 and 3 |
| `four` | two new partners, each on two rings of four | 4 | 5 and 5 |

Laws: the ordinary count and caps of 2 to 8; short knots retire, make offshoots or wait; both knot laws; seven
rounds. The first family's side is read by descent, as in the first step: the knots that have b1 among their
original ancestors and neither b2 nor a new original.

## What was found

| Law | `ring`, `two` and `four` compared: comparisons in which the first side differs | Where |
| --- | --- | --- |
| The ordinary count | 0 of 9 | 997 births on the first side in every start |
| Caps of 2 and 3 | 0 of 18 | the first side makes 2 to 56 births |
| Caps of 4 and 5 | 0 of 18 | the three differ from the start as given, from round 2, and not from each other |
| Caps of 6, 7 and 8 | 11 of 27 | cap 6, waiting: `two` from each of the others, in round 7. Cap 7, waiting: `four` from each of the others, in round 7. Cap 8: `four` from each of the others in round 4 under each treatment; and `two` from `ring` in round 7 under waiting |

- Parity gives the same rounds and the same counts of births in all 24 studies.
- **The expectation.** That the ordinary count gives one side in all four starts: held. That under some cap the
  three starts with the same degree at b2 give different sides: held, at caps 6 to 8. That this comes a round or
  more after the round in which the start as given and `ring` part: held at caps 6 and 7 (round 7 against round
  3), failed at cap 8, where both come in round 4.
- **What the numbers suggest, not shown.** A knot is paid in full when it is asked for no more than the cap. The
  knot made from s, b2 and one of b2's new partners would receive 6 fresh distinctions under the ordinary count in
  `ring`, 7 in `two` and 9 in `four`. So a cap of 4 or 5 cuts all three alike, and a cap of 6 to 8 cuts some and
  not others. On that reading the
  larger the cap, the further out the second side is felt, and with no cap nothing is felt at all. One case does
  not fit it without more: at cap 6 with waiting `ring` and `four` give the same side and `two` differs from
  both. I have not read those births.

## What this shows and does not show

- **Shown, on this start through seven rounds.** Under a cap of 6 to 8 the first family's side can differ between
  second sides that ask the same of the shared originals' knots. So what crosses under a cap is not only the one
  count at the original nearest the first family.
- **Not shown: form in a fuller sense.** The three starts differ in another count, the degree of b2's new
  partners, and in how many rings hang there. Starts that agree in those too and differ further out were not
  built.
- **Not shown: lasting families under a cap.** This step was first planned as that question. The reading I wrote
  for it (knots that never come to share a descendant) is not what the generator study means by a family, which
  is a set closed under taking parents; under that study's own law my reading finds one family, the whole growth,
  at every round through 16. The question needs a definition that a finite growth can decide before it is run.
- **Seven rounds, one start, one program.** The first side by descent is a reading. Supplied: the start, the three
  changes, the cap.

## How to rerun

```bash
cd research/FAMILIES-THAT-MEET-20261126-001/first_step && python3 -B make_engine_cap.py
cd ../second_step && python3 -B which.py 7 60000 > which_to_round_7.jsonl      # under a minute; run it under a memory cap
```
