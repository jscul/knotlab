# The guard under the cap of three and under holding: definitions

Epic `GUARD-CAP-AND-HOLD-20261124-001` (direction 4 of `LOCAL-ROUND-20261123-001`; goals G5 with G18). Frozen on
2026-11-24 with the pre-registration of ticket A, after the advisor's cold review and before any of the study's code is
written. It extends [the definitions of the one-birth-at-a-time study](../LOCAL-ROUND-20261123-001/definitions.md) ("LR"
below, cited by section) and [the shared definitions](../RING-IN-BALANCE-20261123-001/definitions.md) ("the shared
definitions", cited by line), and changes nothing in either for the laws they already cover. Every word keeps its meaning
there: member, short, waits, retires, part, weaned, brood, all-weaned, all-short, status, acting roster, waiters' roster, a
barring, allows, cutoff, matches through round r, underbuilds, x-last order. "Holder" keeps the record's sense, a knot that
holds a distinction. Four words are new: **stayer**, **the waiters' and stayers' roster**, **idle** (section 3) and **has
given** (section 4). A **reading** below is one pass of LR section 2.1, steps 1 to 5, over one part.

## 1. The cap of three in a plan

LR section 2.1, step 4, gains one line:

- **CAP-3**: f = min(max(D, 3 − p, 1), 3), with D found exactly as LR finds it for ORD: the number of groups containing the
  birth in a roster whose members are the births planned in the same reading, each with holding 1, and whose met sets are,
  for each member of that reading's roster, the births it is a parent of, when there are at least two.
- **Why only the births of that reading** (an argument for the referee). The shared definitions' demand (lines 55–58) also
  keeps the old members that still hold something. Past the start, under RELEASE, the only such members are waiters. A
  common knot of a waiter and a new knot would have to be a parent of both, and a parent that gave earlier has spent
  everything, so no knot meets both and no group holds both.
  - **At the start** this is exact only under the start clause's own condition: no start knot that acts meets a start knot
    that waits (LR section 2.2). The engine asserts that condition for every start and law it runs, and stops if it fails.
  - **Under holding it does not hold in general**: a stayer's older child that is still a member shares a met set with
    its newer child, and the demand found here leaves that group out. No registered start has this under the cap (section
    5).
  - A fact used in the predictions: where the demand roster has no group of three or more, D is the sum over the birth's
    parents of that parent's holding less one. So f depends only on the parents' holdings there, and a brood that is not
    yet all-weaned cannot by itself give a wrong f.
- **The gate compares D itself**, not only f, with the reference, and the engine's own complete rounds are computed through
  the plan of this section (not through the shared definitions' step 6 directly).
- The laws: **the two added rules** are (CAP-3, CANCEL-WAIT, RELEASE), as recorded for the ring that returns (shared
  definitions lines 69–70).

## 2. The fillers

The extra FILLERS (shared definitions line 67): of a new knot's f fresh distinctions, min(f, D) are usable and the rest are
barred at birth. **The three added rules** are the two with FILLERS.

- **Holdings at birth under FILLERS.** h₀(x) is the number of places x received at birth that were usable then: its places,
  less its parents, less its places that were barred at birth. Under (CAP-3, CANCEL-WAIT, RELEASE, FILLERS) nothing but
  the fillers bars a distinction, and a barred distinction is never taken, so "barred at birth" is found from the structure
  as x's loose barred places. For a start knot h₀ is as in LR.
- **A birth under FILLERS** is allowed with its fresh count f and its number of usable fresh distinctions min(f, D), both
  from the plan. D counts planned brood-mates, from the brood's roster at birth: it looks ahead to knots not yet made, as f
  already does. A birth **matches** (LR section 4) when the reference has a knot, not yet an image, with the same images
  of parents, the same f and the same number of places barred at birth.
- No barring (LR section 2.4, step 4) is made under this law: nothing retires.

## 3. Holding

HOLD (shared definitions lines 51–54): a member that is not short, after paying its kept groups, keeps the distinctions its
cancelled groups would have taken and makes offshoots only from the rest. The plan of LR section 2.1 is used under HOLD as
follows; everything not mentioned is unchanged.

1. **Step 3 under HOLD.** A member that is not short has as many planned offshoots as its holding less all its groups,
   kept and cancelled. It keeps one usable distinction for each of its cancelled groups. If it keeps at least one it is a
   **stayer** in this reading: it has acted, and it is still a member.
2. **Step 5 under HOLD, for every cancelling treatment.** The **waiters' and stayers' roster** of a roster has as members
   its waiters, with holdings unchanged, and its stayers, each with what it kept. Its met sets are the roster's met sets
   intersected with those members, kept when they have at least two. It takes the place of the waiters' roster: each of
   its parts is read by steps 1 to 5 in a further reading, and so on.
   - A reading of a part that plans no birth and no retirement leaves the part as it was, so a further reading gives the
     same. Such a part is **idle**: its members make no births for ever, and the recursion stops there. An all-short part
     is the case in which every member is short; under holding a part can also be idle with some members waiting and the
     others staying. Every other reading lowers the total held or removes a member, so the recursion ends.
   - Under CANCEL-RETIRE and CANCEL-OFFSHOOT a short member retires or spends everything, so only stayers are carried on.
3. **Planned births of a member** are the births of every reading in which it acts that have it among their parents. A
   stayer can act in several readings.
4. **What this leaves out** (a scaffold, stated before the runs). Under the complete rounds a stayer is a member of the
   live roster beside the new knots. It meets its own children, so a child of one of its children is joinable with it
   through that child, and its children of two different rounds are members of one brood. The rule above reads a stayer
   again only against the waiters and stayers of its own brood, and uses a brood's roster at birth as if all its knots
   were made in one round. Both are wrong under the complete rounds; the runs show where it first matters.
5. **Weaned is unchanged**: a knot is weaned when none of its parents is a member of the present roster. Under HOLD a
   parent that has made a birth may still be a member, and may stay one for ever. The guards R1, R2 and R3 are run with
   this meaning, as frozen.
6. **The last round R** (LR section 4) is the least round such that every knot born by round r, in the reference's roster
   after round R, is no member, or is a member of a part that is all-short, or of a part in which the reference's round
   R + 1 makes no birth and bars nothing.
7. **The match under holding.** Children of one parent can now be born in different rounds with the same fresh count. A
   birth is matched to the reference knot, not yet an image, with the same images of parents and the same fresh count
   that was born in the earliest round, and among those to the least-numbered.

## 4. One repaired guard, registered as a second law

The guard R3 cannot let the child of a stayer act, because a stayer may never stop being a member. One repair is
registered beside it, with its own prediction.

- A parent **has given** when it is no member of the present roster; or when every parent of every knot of its own brood
  has given, every birth planned for it in every reading is made, and its part, in the readings of that brood, is idle.
  (A start knot's "brood" is the start roster, whose knots have no parents.)
- **R3′** allows a remaining birth, or a barring, when every parent of every knot of the brood of the birth's parents
  has given. Under RELEASE a parent that has made all its births is no member, so R3′ is R3 there.
- R3′ repairs only the guard. It does not repair what item 4 of section 3 leaves out.

## 5. What the registered starts can and cannot show

- **The cap with holding** is run because the owner named both, but it tests little: on the cycles, the ring and the cycle
  of eight with three extra dead knots the growth ends at round 2 with every join waiting and every offshoot staying, and
  on the two small starts no knot is ever short under the cap, so holding never acts.
- Holding does act under a fixed ration of three with waiting, and under "just enough for three places" with a short knot
  retiring or making offshoots. Those are the laws that test it.

## 6. What is supplied by hand (scaffolds)

Everything LR lists in its section 5 (the parent relation, A242; the start clause and the rule for a further reading,
A243; the guards; the comparison), and here: the demand found among one reading's births; holdings at birth under the
fillers; the rule that a stayer is read again with the waiters and stayers of its brood; a brood's roster at birth used as
one round's roster under holding; "weaned" left as it is under holding; the repaired guard R3′ and its "has given"; the
match by earliest round.
