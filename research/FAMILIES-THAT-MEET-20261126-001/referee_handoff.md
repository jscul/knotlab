# Referee hand-off: families that meet

Epic `FAMILIES-THAT-MEET-20261126-001`, closed 26 November 2026, referee pending. Three checks by the thread, none
registered. [What stands](decision.md).

**What to recheck, in order of what rests on it.**

1. **The argument "apart for good"** ([third step](third_step/README.md), "Why", steps 1 to 5). It restates for
   two sides the statement that parts act alone past their start
   ([`RING-IN-BALANCE-20261123-001A`](../RING-IN-BALANCE-20261123-001A/preregistration.md), lines 95 to 99), which
   has not been refereed either. Check each step against the engine's round (`play_round`, `build_roster`), under
   waiting above all, and the claim that a fresh count reads nothing of the other side once no group joins them.
2. **The verdict "same for good"** for 118 pairs: that both starts were read to a round with no group joining the
   sides (kept or cancelled), and that everything outside the second side is the same by name and fresh count in
   every round read ([`tally_deep.py`](third_step/tally_deep.py), [`reach_deep.py`](third_step/reach_deep.py)).
   Is the name of a knot (kind, parents' names, index among equal births) the same for the same knot in two starts?
3. **The counts**: 31 of 81, 0 of 162, 106 of 106, 763 rounds, and the one-step cause named birth for birth
   ([`decide.py`](third_step/decide.py): 48 offshoots, 33 parents). Regrow with independent code.
4. **The retiring by hand** ([`ablate.py`](third_step/ablate.py)): that barring the second side's loose
   distinctions is a fair way to remove it, and the seven starts' agreement.
5. **The first two steps' counts** (the price formula on 4,662 and 8,918 knots; 30 of 30; 11 of 27), and the
   wording of the first step's conclusion, which was narrowed once already to this start.
6. **Wording.** Whether "nothing is felt under the ordinary count" stays inside "on this start, for these changes,
   in the rounds read"; the influence-cone study shows changes of what is witnessed together do travel under the
   ordinary count ([`INFLUENCE-CONE-20261120-001`](../INFLUENCE-CONE-20261120-001/decision.md)).

**Known limits, stated in the notes.** One built start; laws that take nothing; a cap is a scaffold (A274); caps of
10 and 12 undecided at two and three steps; the reason for round c − 1 not found (one candidate failed).
