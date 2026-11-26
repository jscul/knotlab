# The advisor's cold review (Claude Fable 5.2, no tools), 26 November 2026

The question is [advisor_question.md](advisor_question.md). Its "118 of the 162 pairs at d = 2, 3" was my miscount (118 is the number over all three distances; at two and three steps it is 82), which finding 1 caught. What was done about each finding is in the [note](README.md), "After the advisor's review".

1. **The "118 of 162" count contradicts the results.** Retire/offshoots at caps 4–9 gives 72 pairs at d = 2, 3, and waiting at caps 4–5 gives 12, so the ceiling is 84, less any pair touching the 2 of 108 starts not read to round c − 1. The same count at d = 1 gives exactly your 36. Reaching 108 would need caps 10 and 12 read to rounds 9 and 11, which the headline's "8 rounds read" rules out. Recount, and say which starts are the two unread ones.

2. **C1–C2 hold only if the recorded count includes cancelled groups.** Under waiting, a group whose outside and second-side members are both short is cancelled, both wait, and it re-forms next round. If the count is of kept groups, zero does not imply zero later. State that it is counted before cancellation, or recount.

3. **Under waiting, zero is sufficient for parting but not necessary.** A set of waiting siblings in which nobody acts in a round is frozen forever, because nothing outside it can change their owe. "Not zero within the rounds read at caps 6 and up" may therefore be permanently joined but inert. Check whether the surviving cross groups are frozen, and if so use "no cross group with a member that can still act" as the criterion.

4. **C1 is sound as quoted, with three unstated premises.** Write them in:
   - Each given distinction goes to exactly one child, offshoots included, so siblings share nothing directly.
   - Retired and acted knots are not members.
   - No original is short in round 1. This holds here (owe = h, no triangles) but not for other starts.
   - D adds no gap: a new knot and a waiting member never share a parent.

5. **"Same for good" needs more than birth digests.** It also needs:
   - the digest to be a multiset;
   - the outside's member state entering the parting round to be equal (waiting members and their h; inferable under a fixed treatment, but say so);
   - a name index that is canonical and independent of second-side enumeration;
   - zero in both starts by a common round.

   It also rests on C2–C3, which are unrefereed, so write "same for good, given C1–C3".

6. **The detectors are mismatched.** "Differs" is read on the first side by a coarse sorted list, while the argument uses the outside by name. A change must pass through s and t, which are rest, before reaching b1's descendants. Report the outside-digest comparison for all 243 pairs: the d = 2, 3 zero is weaker than it looks, and the d = 1 count of 31 of 81 may undercount. The d = 2 by-name check ("no group holds one of them with a first-side member") should say outside member, for the same reason.

7. **"Does not arrive at any cap from 4 to 9" overstates.** It covers waiting at caps 6–9 (24 pairs at d = 2, 3), where the sides never parted in the rounds read; those are "not seen" only. Restrict the claim to retire/offshoots plus waiting at caps 4–5, conditional on C1–C3.

8. **The caps 10 and 12 null at d = 2, 3 is uninformative, not merely unseen.** At d = 1 the second side differs in round 4 and arrival is in round 6 (cap 10) or 7–8 (cap 12). At d = 2 the second side differs in round 6, so arrival would be expected around round 8 or later, at or past the read depth. Cap 10 parts in round 9 only if the c − 1 rule extrapolates. Say the 9/10 boundary may be an artifact of depth.

9. **"The same cap parts the families for good in round c − 1" is one step beyond the data.** Round c − 1 was observed at caps 4–9 only, in 106 of 108 starts, with d and m ≤ 3. "For good" is C2 plus 763 observed rounds. Write "at caps 4 to 9, in every start read that far".

10. **The headline omits or flattens several results.**
    - Waiting arrivals at caps 6 and 8 (d = 1) are missing.
    - Cap 12 is 8 of 9, not all.
    - "Nothing is felt" without a cap means 8–9 rounds on the first-side list, with the sides still joined, so C3 gives nothing there.
    - "Nothing is ever short" is provable and should be stated as such: with no cap, f ≥ D, which is next round's owe.

11. **The d = 1 mechanism is a count coincidence.** 28 groups and 28 extra offshoots match in number only. Verify by name that the extra offshoots' parents are the first-side members of those 28 groups.

12. **Cheapest check: an ablation run.** For one parted start per treatment, delete every second-side knot at the zero round and continue. The outside digests must match the full run in every later round. Add an assertion each round that every joinable pair shares a parent and a birth round. This tests C1–C3 and the implementation together.
