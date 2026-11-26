# The advisor's answer (26 November 2026), read-only in the repository

I read the three programs and their outputs but could not run anything (no shell here), so every prediction below is unrun. I found no bug that overturns a count, but one stated finding looks wrong and three are weaker than worded.

## 1. Counterexamples and code

**Likely counterexample to "even rings' classes are fixed by loose values".**
- `rings_canonical.jsonl` shows two grown forms. n = 3, 4, 6 grow to 6n distinctions; n = 5, 7, 8, 9 grow to 5n.
- The "even" finding rests on n = 4 and 6 only, the short rings that grow differently.
- n = 8 is of the 5n form, and its loose-free row is "not run" (dimension 24 > 22).
- Its pinned row has two classes, so some allowed change with no loose part lies outside the pinned H.
- By the generator argument in `motion.md` (rank 3n − 1 against 3n), I expect n = 8 loose-free to have two classes with a class change avoiding the loose distinctions, like the odd rings.
- The split is then short ring against long ring, not even against odd. Run n = 8 and n = 10 loose-free by rank instead of enumeration.

**The "avoids the loose distinctions" test (`classes.py` lines 85–88).**
- It is correct as an existence test.
- With `pin_loose` it is a tautology: every element of S has zero loose part, so the flag equals "classes > 1". Drop the pinned flags from any count.
- With 4 or 8 classes (19 starts in `weights_out.txt`), existence does not show that every pair of classes is exchanged by a loose-avoiding change. Report the dimension of (S0 + H)/H against that of S/H; step (3) covers only that part.

**The move definition** matches the archive (minimum size through each distinction, ties kept). The elimination routines are fully reduced and correct. `weights.py` line 70 (`reduced(proj) and [...]`) works but only by accident of style.

**Step (2) holds, but the `weights.py` check is weaker than "keeps every class" suggests.**
- A birth with a fresh distinction puts no condition on old states, so only zero-fresh births could remove a class.
- The run covers 594 of the 794 starts. The other 200 are "no round" under every law and should be reported as not run.
- It never tests whether the old class sign survives the new shortest changes, that is, whether P(H′) ⊆ H. The drop from 794 to 510 (749 on the other engine) suggests it often does not, and the count depends on the engine. So "preserved" holds for the round's weights, not for the next stage's moves.

**Step (3) covers only the 530.** For the 264 the class is a function of loose values, so a law acting through loose distinctions could tell them apart; only (2) protects those. Also unchecked: whether a class sign can be read inside one knot's holdings (least size of z modulo the knot rows). If so, one local reader reads the class directly, at equal weight.

**Step (4) is true by definition.** It restates the last line of `motion.md` ("contains no relative sign between distinct allowed assignments"). Present it as the framing, not a finding.

**Not-all-equal.**
- The move search can only miss moves: the pool reaches two steps from d, a size-4 move can reach three, and sizes stop at 4. So "one class" is safe.
- Single flips are usually allowed there, so one class is nearly automatic and is not the parity reading's counterpart.
- `nae_sample.jsonl` has 38 "not run" entries and `nae_rings.jsonl` has 5. "All 200 read" should say how many stages were not read.

## 2. Recorded operations that weight with a sign

None arises from growth; each is supplied.

- **The class sign itself:** `research/READS-HOLDERS-SOURCES-20261120-001A/motion.md`. The supplied read sign (−1)^(z·x) with z the old ring is exactly the opposite-weight weighting, and the change read in its last section tells the two apart (replay in that study's `motion.py`).
- **A sign with no schedule:** `research/KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001/phase_comparison.md`. At winding 2 a five-place not-all-equal knot leaves the sign (−1)^⌊2s/5⌋ on allowed words. The same file says parity contributes a positive factor, so the sign lives under the law with one class and the classes under the law with no sign.
- **Untested candidate:** the orientation signs of matching counts (the literature's Kasteleyn signs) named in `research/BEYOND-REJECTION-20261126-001/advisor_answer.md`. Nobody has checked whether they follow the class.
- **Closed:** the reordering sign, which belongs to the schedule.

## 3. The literature link

It is right in outline, with three qualifications.

- **The match:** S is a classical code's words, H the span of short words, and S/H the sectors. The outside change t is one logical operator, the read z the conjugate one, and the opposite-weight weighting is the −1 state of t.
- **The toric code has both kinds of check; this has one.** The conjugate sign is exactly what is missing and must be supplied. That is the study's result in the literature's terms.
- **These sectors are not protected by locality.** With inclusion-minimal changes there is one class (`motion.md`), and the pinned source ring's "shortest" change is the whole ring. The sectors belong to the choice "shortest through a distinction", which is a scaffold; record it and test another choice.
- **The 264 fit the literature's planar code better.** There the sector is fixed by values on the open boundary, here the loose values; the 530 are the closed case.
