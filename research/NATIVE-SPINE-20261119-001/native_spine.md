# Can the growth pick its own spine?

Epic `NATIVE-SPINE-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for `JUNCTION-KINDS-20261119-001#1`,
bounded to three rules. Goal G17. **Referee pending.**

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `79f09ca40` at 13:18 UTC after a pilot (disclosed).
- The run went through the shared runner (`NATIVE-SPINE-B1`, `runs/native-spine`, 10 cases), all ok by 13:19 UTC.
- Code: [rulelib.py, job.py, merge.py](../../experiments/NATIVE-SPINE-20261119-001B/NATIVE-SPINE-20261119-001B-E001_rules/),
  reusing `JUNCTION-KINDS-20261119-001`'s spinelib.
- Results: [results.json](../../artifacts/NATIVE-SPINE-20261119-001B/NATIVE-SPINE-20261119-001B-E001_rules/results.json).

**Words.** As in the pre-registration.
- The **spine relation** joins each junction of round t to its ancestors exactly two and three rounds back.
- A rule **picks the spine** when what it keeps pairs every junction of round t with exactly one of those ancestors, using each
  junction of rounds t − 2 and t − 3 once.
- The **forced share** of a round is the share of its junctions whose partner is the same in every such pairing.

## The answer

**In the owner's terms.**
- **No rule tried picks the spine, and nothing in the ancestry forces it.** 204 recurrent rounds of the ten plastic-number eddies
  were scored.
  - **"Newest ancestor"** keeps only the junctions two rounds back. It can never reach those three rounds back, so it fails by count.
  - **"Most chains"** fails the same way. The ancestor with the most parent chains is three rounds back every time (100% of what
    it keeps), so it can never reach two rounds back. Its few single picks collide, and late in the window almost every junction
    has a tie (98 to 99%).
  - **"Fewest chains"** leans to two rounds back (63 to 69%) but leaves most junctions tied (91 to 96% in the last round).
  - **The forced reading of "newest"** takes a partner only where every pairing agrees, and here nothing is forced: the forced share
    is 0 at every one of the 204 rounds. Every junction can swap its partner within some other pairing.
- **The pairing is not evidence of a substitution.** A degree-preserving shuffle of the relation, keeping how many candidates each
  junction has and how many junctions each ancestor serves, still has a perfect pairing at rounds 10, 15 and 20 in all ten (30 of
  30). So the pairing that `JUNCTION-KINDS-20261119-001` read as "ancestry carries the count" follows from the counts and the
  density of ancestry. That reading is corrected (a Narrowing; see Corrections).
- **So the spine is not in the growth.** The counts obey c(t) = c(t − 2) + c(t − 3), but no rule tried, and no forced structure,
  turns that into one partner per junction. Combined with JUNCTION-KINDS and JUNCTION-MAP, this is the fourth finite object that the
  break-shape eddies do not carry: clusters on the candidate map, the junction map, kinds of junction, and now a native spine.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| S1 | (a check, by count) N never picks the spine | **held** | 0 of 204 rounds |
| S2 | M never picks the spine | **held** | 0 of 204; M keeps only depth-3 ancestors |
| S3 | F never picks the spine | **held** | 0 of 204 |
| S4 | the forced share is below 1 from round 6 | **held** | it is 0 at every round |
| S5 | (risky, the advisor's) M's single picks collide by round 13 in at least 8 of the ten | **held** | 10 of 10 |

5 of 5 held. Null: 30 of 30 shuffled relations keep a perfect pairing.

## Why it holds

- **"Most chains" sees only depth 3.** Going three steps up multiplies the chains, so a depth-3 ancestor almost always has more
  chains than any depth-2 one. The advisor predicted this depth bias.
- **Nothing is forced.** A pair lies in every perfect pairing exactly when it is on no alternating cycle. The relation is dense
  (each junction has many ancestors at each depth), so every pair lies on one.
- **The null.** Hall's condition depends only on how candidates are shared. A relation this dense with these degrees meets it at
  random, so the pairing's existence carries little information.

## Known results, and what this adds

- **Known, cited once.** Hopcroft–Karp; forced pairs as the pairs on no alternating cycle (the strongly connected components of the
  alternating digraph); degree-preserving switchings.
- **What this adds.** For the break-shape eddies, the recurrence c(t) = c(t − 2) + c(t − 3) is not read off the ancestry by any of
  three natural rules, nothing in the ancestry forces a pairing, and the pairing itself is what a random relation with the same
  degrees has.

## Limitations

- Three rules, as bounded, and the forced reading. Rules that read the future of a junction, or symmetry-based arguments, were not
  tried. Only the latter could prove that no native rule exists.
- The shuffle null is tested at three rounds per start.
- 24 rounds; the ten plastic-number starts only.

## Corrections

- **`JUNCTION-KINDS-20261119-001`, Narrowing (overreading).** "Ancestry carries the count … the substitution a → b, b → c, c → ab
  made of real parent chains" read the existence of a perfect pairing as structure. A degree-preserving shuffle has one too (30 of
  30 here), so it shows only that the counts are compatible with the ancestry. Logged in `docs/CORRECTIONS.md`, and corrected in
  that note, the working doc, its object row and its goals row.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze. Its answer stayed within its text.
- **Held.** N is refuted by count, not by evidence. The forced reading of "newest" has the forced pairs as its ceiling. M has a
  depth bias, and it was total: M keeps depth 3 only. The risky S5, at 10 of 10. The null, which turned out to be decisive.
- **Taken as a direction.** The automorphism test: a rule read from the ancestry must commute with its symmetries, so a symmetry of
  the start that moves every perfect pairing would prove that no native rule exists, at every horizon.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: three spine rules | **Status:** Successful (5 of 5 held) | No rule picks the spine, nothing is forced, and the pairing exists in a degree-preserving null |
| Local direction: a finite object behind the break-shape eddies | Practically exhausted | Four objects tried (cluster map, junction map, kinds of junction, native spine); none carries the count |
| Broader exploration: what the cheapest growth builds | Known alternatives | The steady eddies' rates are the catalogue's family; how the growth produces them in the break shapes is unexplained |
| Long-term goal: G17 | Obstruction learned | The rare eddies' recurrence is not a local or ancestral structure of the growth that was found |

**Next step:** Research directions — none selected yet (awaiting the coordinator)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The automorphism test: symmetries of the ten starts, and whether any perfect pairing is invariant under them | 2/3 — the only route found to prove that no native spine exists | 2/3 — the starts are small; symmetries of their growth need care | compute the starts' automorphisms → stop at an invariant pairing, or a junction fixed by a symmetry with no fixed candidate | Alternative · proposed |
| 2 | The explosive kind (`BREAK-EDDIES-20261119-001#2`), with part U's 624 still-rising starts | 2/3 | 2/3 | as there | Alternative · deferred |
| 3 | The y⁴(1 + y)² starts' spine (`JUNCTION-KINDS-20261119-001#2`), now with the shuffle null first | 1/3 — the null makes a pairing weak evidence | 3/3 | as there, null first | Alternative · deferred |

## Final report as sent (2026-11-19 13:24 UTC)

**Outcome:** The growth doesn't pick its own spine. None of the three rules gives the one-to-one pairing of each round with the two rounds its recurrence names: the newest ancestor, the one with the most parent chains, or the one with the fewest. Nothing in the ancestry forces any pair either. 5 of 5 frozen predictions held, on 204 rounds of the ten plastic-number eddies. Closed, referee pending.

- **Why the rules fail.** "Newest" can only reach two rounds back, so it fails by count. "Most chains" always lands three rounds back (100% of its picks), so it fails the same way, with collisions. "Fewest chains" leaves 91–96% of junctions tied by the end.
- **Nothing is forced.** In every pairing, every junction could swap its partner within another pairing. The forced share is 0 at all 204 rounds.
- **The null settles it.** A shuffled relation, keeping how many candidates each junction has and how many junctions each ancestor serves, still pairs off perfectly (30 of 30). So the pairing JUNCTION-KINDS reported only shows that the counts fit how dense the ancestry is. I corrected that reading (Narrowing, below).
- **Where the line stands.** This is the fourth finite object tried for the break-shape eddies: the cluster map, the junction map, kinds of junction, and now a native spine. None carries their count. Their rates are the catalogue's family, but how the growth produces them in these shapes is unexplained.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: three spine rules | **Status:** Successful (5 of 5 held) | No rule picks the spine, nothing is forced, and the pairing exists in a shuffled null |
| Local direction: a finite object behind the break-shape eddies | Practically exhausted | Four objects tried; none carries the count |
| Broader exploration: what the cheapest growth builds | Known alternatives | Steady eddies have family rates; the mechanism in the break shapes is unexplained |
| Long-term goal: G17 | Obstruction learned | The rare eddies' recurrence isn't a local or ancestral structure we can find |

**Next step:** Research directions — none selected yet (awaiting the coordinator)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The automorphism test: does a symmetry of the starts move every perfect pairing? That would prove no native spine exists | 2/3 | 2/3 | compute the ten starts' symmetries → stop at an invariant pairing, or a fixed junction with no fixed partner | Alternative |
| 2 | The explosive kind, with part U's 624 still-rising starts | 2/3 | 2/3 | as in BREAK-EDDIES | Alternative · deferred |
| 3 | The y⁴(1 + y)² spine, null first | 1/3 | 3/3 | as in JUNCTION-KINDS | Alternative · deferred |

**Corrections:** one, a **Narrowing** of JUNCTION-KINDS (just published). "Ancestry carries the count … the substitution made of real parent chains" read a perfect pairing's existence as structure. A shuffled relation has one too. The counts and verdicts stand. It's logged in docs/CORRECTIONS.md and knotlab's HISTORY.md (323c2ccdf). **Goals:** G17 checkpoint (obstruction learned). **Assumptions:** none changed. **Basket:** `JUNCTION-KINDS-20261119-001#1` taken. The basket's next open items are `B196` (a decision procedure for bounded reach on small orbits, 3/3, 2/3) and `RING-PAIR-20261119-001#2` (prove the identification, 3/3, 2/3). **Advisor:** Fable 5.2, before the freeze, staying within its text. It said "newest" fails by count, proposed the forced reading, predicted the depth bias (it was total) and the risky collisions (10 of 10), and suggested the null, which turned out to be decisive.

**Referee hand-off.** The decision note is `research/NATIVE-SPINE-20261119-001/native_spine.md`; the prior-work line is in the pre-registration (objects-gate passes). Please check:
- `rulelib.forced_fraction` (the alternating digraph and its components);
- `shuffled_has_perfect`;
- the most-chains depth split on one round by hand.
