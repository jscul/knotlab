[claude-code:unrecognized_model] {"model":"claude-fable-5-2","query_source":"sdk"}
I did this by reasoning only; nothing was run or checked against the repo.

**Verdict.** The lemma is right once three things in its statement are fixed. The static test as designed is not yet a fair test of S1: most of its P1 population satisfies P1 vacuously, the size bound sits below where a non-vacuous collision can first appear, and the same-states check may be incomplete.

## 1. The lemma

The proof goes through, with these repairs:

- **"Third" must exclude the junction itself.** For a loose-holding v meeting a and b, the common junction w must differ from v, or P1 is trivially true. Your proof gives this (w existed before v), but the definition and the checker must say w ∉ {v, a, b}.
- **Oversubscription is unspecified.** A live junction with k loose distinctions can sit in more than k candidate pairs or sets. The lemma needs "every loose distinction of a live junction is consumed and every new junction meets only its parents", so state what the law does when demand exceeds supply.
- **Closing with o a cut vertex.** If G − o is disconnected, a 0-fresh junction's parity is implied as soon as it holds all loose distinctions of one component, not of the stage. Either assume the start is connected in G − o or restate the closing clause per component. P1 and P2 survive either way.
- **Round 1, offshoots, closing.** These are fine. Parents may meet each other at round 1 and the proof never uses that they don't. Offshoots meet one junction, so P1 is vacuous for them. A closed stage has no loose junctions, so both properties are vacuous.

The same argument proves more, and I would record it now:

- **P1⁺:** w holds no loose distinction, since it belongs to stage r−1 and those hold none after round r.
- **P4 (round ≥ 2):** the junctions a loose junction meets do not meet each other, because they were the previous round's loose junctions and P2 held then.
- **Peeling:** returning the loose junctions' taken distinctions gives a stage that again satisfies all of these, down to a start.

Reached stages are far thinner than P1 ∧ P2, which matters for question 2.

## 2. Fairness of the static test

- **Vacuous strata dominate.** P1 says nothing about closed arrangements or about arrangements whose loose junctions each meet at most one junction. The second class is essentially "any simple core plus an apex". In both, S1 becomes "the table carries the states of simple graphs", a much stronger claim that growth does not need. Reached stages almost never fall in these strata. Report S1 separately for three strata: closed, pendant-only, and at least one loose junction meeting two or more.
- **The bound is too low for the non-vacuous stratum.** Over dense cores (four junctions pairwise meeting, wheels, the literature's octahedron), every pair has a common junction, so P1 permits any attachment. Two attachments are only likely to collide if they give the same counts of distinctions per junction. On a 4-junction core, two or three pair-junctions always differ in those counts. So the first plausible collisions need 8–10 junctions.
- **Enumerate the P1 side by construction.** S1 only involves P1 arrangements, so you need not enumerate everything. Build core plus loose junctions attached to pairwise-backed sets, and push that side to 9–10 junctions. Keep the full ≤ 7 census only as the S2 control.
- **The same-states check may be incomplete.** With o allowed as a cut vertex and 2-separations {o, j} present, Whitney twists give same-states pairs that are neither junction-graph isomorphisms nor obviously twin renamings. If your "renaming checked by rank" is not a full search, same-states pairs get counted as other-states, which inflates S2 and can falsely fail S1.
- **A complete decision procedure exists.** Every matroid isomorphism is a table isomorphism. So enumerate table isomorphisms modulo twin classes and rank-check each. Certify "other states" by an invariant that differs, such as the bond-size spectrum or spanning-tree count. Report anything undecided as undecided.
- **Add a power baseline.** Report the number of P1 arrangements, the number of P1 tables, and for each other-states group how many members are P1. Compare the P1–P1 count with what a matched-prevalence control property gives, for example P1 imposed on non-loose junctions. "Zero of an expected 0.3" is not evidence.
- **Contamination.** The six truths and their rivals at 7 junctions are the cases you already looked at. Exclude them from the count of fresh evidence.
- **S3 is not a prediction.** It is implied by S1. Replace it with a ladder frozen in advance: S1 (P1), S1′ (P1⁺ ∧ P2 ∧ P4), S1″ (peelable down to a legal start). If S1 fails in a vacuous stratum but S1″ holds, the route to the target survives. Freezing the ladder first keeps this from being a post-hoc rescue.

## 3. My bet

- S1 as written, vacuous strata included, at ≤ 7 junctions: about 55% that it holds.
- S1 in the non-vacuous stratum at ≤ 7: about 85%, but mostly for lack of room.
- S1 in the non-vacuous stratum at 9–10 junctions: about 60%.
- S1″: about 85%.

The most likely places for a P1–P1 other-states collision:

- **Closed or pendant-only arrangements**, on graphs with small bonds that are not junction stars. There the table stops reading "which distinctions share a junction".
- **Regular dense cores with two kinds of pair**, carrying three or more 2-parent loose junctions. On the octahedron the kinds are meeting pairs and non-meeting pairs, both backed. Look for two attachment patterns with equal counts per junction.

## 4. A proof route if S1 holds

1. **Extract the exchange move from the 11 rivals.** For each violating triple, write the truth-to-rival change as a local move. The conjecture to prove is then that every other-states table isomorphism factors through such moves, and each move needs an unbacked pair.
2. **Test a stronger statement first.** Check whether, among P1 meet-once arrangements, every table isomorphism (modulo twins) is a matroid isomorphism. This is cheap in the census. If it holds, it is the cleaner theorem. If it fails, the proof must construct a different renaming, and you learn that before investing.
3. **Recover the stars.** Show a table isomorphism sends each loose junction's star to a bond of the same size, and that P1⁺ forces that bond to be a star up to a twist at {o, j}. The backed pair gives the closed walk v–a–w–b, and with meet-once that should pin the two shared distinctions of v as lying in exactly one small bond together. Stars span the equation space, so the loose layer is done.
4. **Induct by peeling.** This is the hard step. Stage r−1 is stage r with the loose junctions contracted into o, so its bonds are the bonds of stage r that avoid the current loose distinctions. The table records only the smallest bond through a pair, which may use loose distinctions. You need a lemma that for pairs of older distinctions some smallest bond avoids the loose layer, or that the loose layer adds a computable amount. Check this numerically on the 2,698 stages before attempting it.

Because of step 4, I would aim the proof at S1″ for reached stages, not at static P1.

## 5. Names

- **P1.** "Parent rule" misleads. Statically there are no parents, the content is about a further common junction, and "share a parent" already names candidacy. I suggest **backed pairs**: "any two junctions a live junction meets are backed by another junction that meets both". I avoided "witness" because the program already uses it.
- **P2.** "Apart" leans spatial. I suggest **live junctions never meet**. "Live" already means "holds loose distinctions", and by the lemma the static and grown senses agree.
