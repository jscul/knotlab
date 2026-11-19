# Advisor question 1 (MANY-VALUED-20261119-001, before the freeze)

Analysis please. You have no tools in this session, so reason only from what is written here and do not describe files or runs.

**Setting** (STATES-GROWTH-20261119-001, your rank-1 rule). The states-only growth grows on M(S), the minimal not-all-equal
constraints, when M(S) is admissible. It was undefined at 146 trajectory points from census starts of up to four knots, every one
from a start with a triangle of knots or a double touch.

**Pilot** (40 of the 146, disclosed). I listed every presentation of the same allowed states: subsets Q of M(S) ∪ {the stage's
junctions} that are admissible (members of at least three places, each distinction in at most two, all distinctions held),
irredundant, and allow exactly the stage's states.
- **39 of 40 have exactly one such presentation: the stage itself.** M(S) is inadmissible only because it carries extra derived
  constraints, for example NAE(0, 3, 4, 6) from the triangle of knots (0, 1, 3), (0, 2, 4), (1, 2, 5) with the junction
  (3, 4, 5, 6). No admissible irredundant presentation uses them.
- **One start has two:** four three-place knots pairwise touching once (your K4 example in knot form). Both presentations grow
  identically for three rounds; it stalls or closes at once.

**Proposed refined rule.** Grow the unique admissible irredundant presentation of the states when there is exactly one, and call it
undefined only when there are several.

**Planned frozen predictions.**
- **M1.** At least 95% of the 146 points have exactly one presentation.
- **M2** (risky). Where there are several, they grow the same counts for three rounds.
- **M3.** On every trajectory from census starts of up to four knots with no redundant knot, the refined states-only growth equals
  the cheapest growth at every round within reach (at most 18 distinctions, 6 rounds).

## Questions

1. Is the refined rule well defined and genuinely states-only? Does "the unique admissible irredundant presentation" need any choice
   I have not noticed, such as whether presentations may use constraints outside M(S) ∪ {the stage's junctions}? Can a junction's
   support be non-minimal (a proper subset also implied), so that it lies outside M?
2. Is M2 plausible in general? Is there a reason two admissible irredundant presentations of the same states must grow the same
   counts, for instance a symmetry such as K4's stars-and-triangles duality? Or is the K4 case special?
3. If M3 holds, under not-all-equal the cheapest growth would read only the states except at redundant knots and at points with
   several presentations. Is that the right headline, or does it overstate?
