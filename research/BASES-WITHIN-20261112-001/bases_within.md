# Bases within bases

Epic `BASES-WITHIN-20261112-001` (backlog B164, G17 with G8 and G6; program mathematics, group arithmetic), 2026-11-12, at the
coordinator's go-ahead with the owner's approval of the redirect. Pre-registered in [preregistration.md](preregistration.md), frozen
in commit `8e2e41275` before any census ran. Proof family: `proofs/BASES-WITHIN-20261112-001A/`. **Referee pending** (the
background referee thread).

## Words

As in the guide's glossary and the pre-registration: harmony (A70), inner harmony, outer base, stitch (now holding distinctions of
three harmonies), stitch at one place, level, tie class, bond distance, the farthest tie. The pre-registration's "stitch with
offsets" is called a **shifted stitch** here, with **shifts** (s, t, u) for its members, because the glossary's offset is the relative
phase of two orbits, and one word keeps one meaning.

## The question

The owner: "each boolean variable could be its own micro infinite series of logic, that's bound to others", and, on overlapping,
"like fractal, or meeting patterns that are more complex than just triangle edges meeting. Like they can fold in immensely complex
ways and can be kind of globally influential." Read with A75: each distinction of an outer base becomes an inner harmony, and each
outer knot a stitch of the inner harmonies at every place. What does the law read at the outer level? Does repeating the step change
anything (a fixed point would be one reading of his "fractal")? Which combinations end? And how far does fixing one distinction reach
as the nesting deepens?

## The answer

**Stitched at one place, nesting keeps the outer law exactly, never ends, and forces nothing new: the only thing it adds is room.**

- **The outer level reads its own law, exactly (proved).** Every outer state lifts, x_(j,i) = s_j ⊕ w(i) with any inner state w
  (the advisor's mirror lift), so the outer base with inner harmonies allows exactly the outer states at each place, lives exactly
  when the outer base lives, and keeps doing so at every level. What the outer knots read of the inner harmonies is how often their
  states disagree at each offset; that changes how many states there are, never which outer states are allowed.
- **One series is one distinction exactly: the alternation (proved).** 0101… is the only harmony whose states read as a single
  yes-or-no, and with it each level is a copy of the one below: the exact fixed point. Every other harmony carries more than one bit,
  its phase, and multiplies the states.
- **Forcing only multiplies (proved; checked to level 4).** Two distinctions of a level are tied exactly when they are tied
  coordinate by coordinate in the seed. Four of five seeds force nothing, so their levels force nothing at any depth. The Fano plane
  less one knot forces its removed knot's three distinctions equal, and at level k that tie reaches the whole level (farthest tie 2k,
  equal to the farthest distinction) while holding a share that falls as (3/7)^k.
- **A drawn fractal nesting forces nothing (exact, to level 7).** Three copies sharing corners, again and again (the literature's
  Sierpinski gasket), lives at every level, and fixing a corner forces no other distinction, though the farthest distinction doubles
  each level, to 128 bonds at level 7. Influence stays local, at zero, at every depth: the negative the coordinator asked to report.
- **Shifts are where the inner phases matter, and they mostly loosen (exact on 26,340 and on 60 sampled assignments per pair).** A
  shifted stitch ended a living outer base only on the tightest pattern, four distinctions with all four triples knotted, and for
  17 of 45 harmonies; it brought the contradictory Fano plane back to life in 16,320 of the alternation's 16,384 sign patterns and in
  every sampled assignment of every other harmony.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| The outer level reads disagreement counts; harmonies of harmonies are harmonies; only the alternation is one distinction exactly | proved by hand (L1 to L3) |
| Stitched at one place, every outer state lifts: the outer law kept exactly, nothing ends, at every level | proved by hand (L4, the advisor's; L5, L6); checked on 1,485 pairs |
| Ties of levels are products of the seed's | proved by hand (L7, in the advisor's form); checked on 100 origins at levels 1 to 4 |
| Shifts matter only around closed chains; for the alternation they are signs | proved by hand (L8, L9); checked |
| The drawn three-copy nesting forces nothing to level 7 | exact computation |
| Shifted stitches end a living base only at the four-distinction pattern, and revive the Fano plane almost always | exact on every assignment tried (all for the alternation, 60 sampled per other pair) |
| Counts of the levels of each harmony | E1 dropped at its cap; a reduced follow-up after the run, descriptive (below) |

## Against the pre-registration

| Item | Outcome |
| --- | --- |
| Checks of L4, L7 (seeds), L8, L9 and the control | all passed |
| E1 (levels 2 and 3 of 45 harmonies) | **dropped**: reached its 1-hour cap (level-3 enumerations on up to 4,096 distinctions) |
| P1, P2, P3 (the advisor's counts for 0011 and 000111; rigid only for the alternation) | not tested by the frozen run; all three hold in the follow-up after the run |
| P4 every harmony has an ending assignment of shifts (the advisor's) | **failed**: 17 of 45 in the sample, all on one pattern |
| P5 the seeds, by L7 | held |
| P6 the Fano seed's share falls as (3/7)^k | held (3/7, 9/49, 27/343, 81/2,401) |
| P7 the three-copy nesting forces nothing, at every level (this epic's) | held to level 7 |

## The follow-up after the run

E1 wrote nothing before its cap, so a reduced follow-up ran after the run (descriptive, not frozen; the frozen functions; level 2 of
all 45 harmonies capped at 20,000 states, and level 3 of 0011): 0011 has 4, 16 and 256 states at levels 1, 2 and 3; 000111 has 6 and
102; the one-orbit harmonies of periods 8, 10 and 12 have 528, 2,470 and 11,016 at level 2, the same for the two words of each period;
26 harmonies passed the cap. Only the alternation is rigid. So repeating the step keeps what is allowed and multiplies the room
fast: for 0011 the states square at each level. The tie class of the origin was the product of the line ties for all 45, as L7 says.
All parts that ran stayed inside their caps except E1; the earlier epic's route measurement (ODD-SEARCH-A2) also reached its cap the
same night and is recorded as dropped there.

**Review.** Referee pending: the background referee thread has the hand-off (arrangement of 2026-11-12).

## What it changes

- **For the owner's recursion.** Each distinction can be its own infinite series bound to others, and the law at the level above is
  then exactly the same law, at every level: a fixed point, as far as what is allowed goes. But a fixed point of what is allowed is
  not yet a fractal of structure: the inner series add hidden room, never a new constraint or a new forced value.
- **For "globally influential".** Influence does not come from nesting. It comes from a seed that already forces (then it reaches
  every depth, in a shrinking share) or from shifted stitches, which mostly undo contradictions rather than spread them. A design where
  influence grows with depth was not found.

## Assumptions

A70 used; A75 (bases within bases are stitched at one place) added and used; status unchanged.

## Corrections

None.

## In the owner's words

If every yes-or-no is itself an endless pattern tied to the others at every point, the logic one level up is exactly the logic
below: the same patterns are allowed, nothing new is ruled out, and it never runs out of room. That holds at every depth, so the rule
is its own fixed point. The one endless pattern that behaves exactly like a single yes-or-no is the plain alternation 0101…; every
other one carries extra hidden freedom. What nesting does not do is spread influence: fixing one point forces nothing new, even in a
fractal built from copies of copies. Influence only travels as far as the smallest piece already forces it.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — bases within bases | **Status:** Successful, referee pending | the owner's three questions answered for stitches at one place (proved), the nesting and shifted arms run; one arm dropped at its cap and followed up |
| Local direction — nesting | Continue | the reading under which nesting could create forcing (substitution, A75's challenge) is untested |
| Broader exploration — G17's census | Known alternatives | `RANDOM-FATES-20261112-001`'s outcomes and limits; harmonies along two shifts |
| Long-term goal — G17 Typical and rare meeting patterns | Obstruction learned | nesting at one place keeps the law exactly and spreads no influence; influence must come from the seed or from shifts |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Nesting by substitution | 2/3 — Substantial | 2/3 — Testable | replace each distinction by a finite block of an inner harmony and bind blocks at chosen distinctions, iterated on the five seeds and the three-copy nesting → forcing that grows with depth, or none | Selected · awaiting go-ahead |
| 2 | A seed whose influence does not shrink | 2/3 — Substantial | 2/3 — Testable | search small near-contradictory seeds for one whose tied share does not fall with level → one, or a proof that the share must fall | Alternative · deferred |
| 3 | Why shifts loosen | 1/3 — Incremental | 3/3 — Ready | which patterns of up to 5 knots end under shifted stitches, and why the Fano plane revives (switching classes of signs) → a lemma | Alternative · deferred |
| 4 | Counting the levels | 1/3 — Incremental | 3/3 — Ready | the level-2 counts 2, 16, 102, 528, 2,470, 11,016 of one-orbit harmonies → a formula, or the first word that breaks the same-period rule | Alternative · deferred |

- **#1** tests A75 directly: under substitution the mirror lift need not apply, so it is the one reading left where nesting itself
  could make influence travel.
- **#2** asks for the owner's "globally influential" in share, not only in reach: the Fano seed reaches everything but holds less and
  less of it.

**Corrections:** none. **Goals:** G17 checkpoint (obstruction learned, with G8 and G6; no goal change; its Open line's B164 part
answered for stitches at one place). **Assumptions:** A70 used; A75 added and used, unchanged. **Basket:** #1 to #4 recorded; in the
arithmetic line's basket ODD-FAMILY #1 and #2 rate higher on concreteness (3/3) but were set aside by the coordinator as of
diminishing return for the owner's goals, and HARMONY-ARITH #2 (harmonies along two shifts) now has these levels as instances. **Advisor:** consulted twice before the freeze: it supplied the mirror lift (L4), the product form
of L7, the shifted arm, the counts P1 and P2, the positive control and the drawn nesting arm, and judged native shift rules flat.

## Final report as sent

Sent to the owner in the project thread on 2026-11-12 at about 08:03 UTC, verbatim:

> Done. If every yes-or-no is its own endless pattern, bound to the others at every place, the logic one level up is exactly the logic below. That holds at every level, and nesting never ends. It also spreads no influence. The write-up is research/BASES-WITHIN-20261112-001/bases_within.md. The independent referee is pending with the background referee thread.
>
> • **The level above is the level below (proved).** Every outer state lifts, so the nested base allows exactly the outer base's states, at every depth. The rule is its own fixed point. The inner patterns add hidden room and never a new constraint: 0011 gives 4, 16 and 256 states at levels 1 to 3.
> • **One endless pattern is exactly one yes-or-no: 0101… (proved).** Every other pattern carries a hidden phase on top of its bit.
> • **No global influence from nesting (proved; exact to depth 7).** Forced values only multiply what the seed pattern already forces. A drawn fractal of three copies sharing corners forces nothing at all down to level 7, even though its far end doubles at every level. A seed that does force (the Fano plane less one knot) reaches every depth, but over a shrinking share: (3/7)^k.
> • **Shifts are where the hidden phase matters, and they mostly loosen.** Stitches with shifts ended a living pattern only in one case, where all four triples of four distinctions are knotted. They brought the contradictory Fano plane back to life almost every time.
>
> | Scope | Verdict | Why |
> | --- | --- | --- |
> | This attempt — bases within bases | **Status:** Successful, referee pending | your three questions answered for stitches at one place (proved); the levels run hit its cap and was followed up after the run |
> | Local direction — nesting | Continue | the one reading where nesting itself could spread influence (substitution) is untested |
> | Broader exploration — G17's census | Known alternatives | the random-patterns census; harmonies along two shifts |
> | Long-term goal — G17 Typical and rare meeting patterns | Obstruction learned | nesting keeps the law and spreads no influence; influence has to come from the seed or from shifts |
>
> **Next step:** Research directions — selected: #1
>
> | # | Direction | Payoff | Concreteness | First step → stop when | Status |
> | --- | --- | --- | --- | --- | --- |
> | 1 | Nesting by substitution | 2/3 — Substantial | 2/3 — Testable | each distinction becomes a finite block, blocks bound at chosen distinctions, iterated → forcing that grows with depth, or none | Selected · awaiting go-ahead |
> | 2 | A seed whose influence doesn't shrink | 2/3 — Substantial | 2/3 — Testable | search small near-contradictory seeds → one whose forced share holds at depth, or a proof it must fall | Alternative · deferred |
> | 3 | Why shifts loosen | 1/3 — Incremental | 3/3 — Ready | patterns of up to 5 knots under shifts; why the Fano plane revives → a lemma | Alternative · deferred |
> | 4 | Counting the levels | 1/3 — Incremental | 3/3 — Ready | level-2 counts 2, 16, 102, 528, 2,470, 11,016 → a formula | Alternative · deferred |
>
> **Corrections:** none. **Goals:** G17 checkpoint (obstruction learned), no goal change. **Assumptions:** A75 added (this reading of "bound to others"; substitution is its challenge, #1). **Basket:** #1 to #4 recorded. **Words:** "stitch" in the glossary now covers three harmonies, with "stitch at one place" and "shifted stitch". **Advisor:** consulted twice before the freeze. It supplied the lifting lemma and its main counts, and it judged that native shift rules reduce to stitches at one place. Also: the last epic's route measurement hit its cap and is recorded as dropped, with no claims affected.
