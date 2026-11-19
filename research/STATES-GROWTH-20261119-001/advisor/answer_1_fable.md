['claude-fable-5-2']
# Advisor answer 1 (STATES-GROWTH-20261119-001)

**Short answer.** Under not-all-equal (NAE), a states-only cheapest growth exists on the stages where the minimal constraints are themselves an admissible presentation, and nowhere else without a new rule. Under parity, "loose" cannot be read from the states even in the best case. Everything below is reasoning from your text; the small examples are worked by hand and are meant to be replayed.

Notation: `M(S)` is the set of minimal sets of distinctions on which no state of `S` is constant. It depends only on the states.

## Three facts to replay first

**F1. `M(S)` always presents the same states.** Every junction is an implied constraint, so it contains a member of `M`, and every member of `M` holds on `S`. But `M` need not be admissible (at least three places, each distinction in at most two members).

**F2. The hint in question 2 is false: an irredundant NAE presentation is not unique.** Take six distinctions in three opposite pairs, with the eight 3-sets that pick one from each pair (in the literature's picture, the stars and triangles of K4).
- The four "stars" are an admissible, irredundant presentation. So are the four "triangles".
- They have the same states. If a triangle is constant, each of its three junctions needs its last distinction to disagree, and those three make the fourth star constant. The converse is symmetric.
- A set is implied exactly when it meets all three opposite pairs, so `M` is all eight 3-sets and each distinction lies in four of them.
- Frozen prediction: 18 allowed states, 8 minimal constraints, 2 irredundant admissible presentations.

The general mechanism is forcing: a 3-place junction whose neighbours are all 3-place with nothing loose yields an extra implied constraint on the neighbours' other distinctions. One loose distinction on a neighbour removes it.

**F3. Under parity, "loose" is a choice of dropped junction.** A parity presentation with each distinction in at most two junctions is a graph in the literature's sense (junctions as vertices, distinctions as edges). Add the implied junction that holds all loose distinctions, which is the sum of all junctions. In this completed system nothing is loose.
- The states fix only its cycle matroid.
- Any junction of the completed system can be the dropped one. Each choice gives a presentation with the same states and a different loose set.
- Your row operation (replace a junction by its sum with a neighbour) is this re-choice in the cases where it stays admissible.
- By Whitney's 2-isomorphism theorem, the only further freedom is twisting at 2-junction cuts. If the completed system is 3-connected, it is unique.

This would explain 60% against 5%: under NAE the sum of junctions is not implied, so looseness is real there.

## 1. Candidate definitions

| Rank | Definition | Well defined? | Needs |
|---|---|---|---|
| 1 | Cheapest growth run on `M(S)`. This merges your (a) and (b): loose = in exactly one member of `M`, candidates and groups read on `M`. | Only when `M(S)` is admissible. Fresh distinctions are compared up to renaming. | A per-round verdict: `M = P` (saturated), `M ≠ P` but admissible (sharpened), or `M` inadmissible (undefined). The output of a round need not be saturated, so recompute `M` every round. |
| 2 | (c) as a many-valued growth: the set of outcomes over all admissible presentations of `S`, up to renaming. | Yes. The set is finite, since degree at most two bounds the junction count. | Enumeration of presentations. It measures A108 rather than removing it. A union of junction sets breaks the degree bound, so only the intersection of events (loose in every presentation, candidate in every presentation) is a single rule, and under parity it is likely near empty by F3. |
| 3 | A direct rule in A99's style, from bonds or pair disagreement counts. | Yes. | It is a new growth, not a states-only cheapest growth, so there is no fair comparison with the catalogue. |

I recommend rank 1, with rank 2 used only to report what happens on the stages where rank 1 is undefined.

## 2. Reading loose and candidate from the states

**NAE.**
- On saturated stages, yes, trivially: `M` is the presentation.
- Two saturated stages with the same states are equal, so saturated stages never collide. The informative number is the saturated share, not the collision share.
- Elsewhere, no. A redundant junction uses up looseness without changing the states, and F2 shows two irredundant presentations.
- Do not define loose by forgetting ("forgetting x leaves an NAE system"). For {x,y,a} and {x,y,b}, forgetting x frees both junctions, yet `M` equals the presentation and x is held twice. Two junctions sharing two distinctions are a discrepancy family for that definition.
- Unchecked: whether a junction can fail to be in `M` because a proper subset of it is implied. Test it.

**Parity.**
- No, by F3.
- What the states do give, when the completed system is 3-connected, is all of its junctions including the implied one. They are exactly the bonds whose removal leaves the rest connected as a matroid (Tutte and Kelmans, non-separating cocircuits).
- The states do not say which junction is the dropped one. A states-only parity growth is therefore either many-valued, one outcome per dropped junction, or it needs a states-invariant choice of the dropped junction. I see no natural one.

## 3. Canonical presentation under NAE

- `M` is canonical as a constraint set, but not always admissible (F2).
- It equals the irredundant presentation only on saturated stages. An irredundant presentation need not be unique (F2).
- **Duplicate pair.** Its states are those of the lone knot and `M` is the single 3-set. Any states-only growth must treat the two alike, and rank 1 grows. "Closing by duplication" is not an event the states can see, and the same holds for any implied junction, including those the cheapest growth makes under its `d` exception. This is the main forced divergence from the cheapest growth.

## 4. What to test first

In order of cost:

1. **Replay F2 and the duplicate pair.** Predictions: 18 states, 8 minimal constraints, 2 presentations; the duplicate pair has one minimal constraint.
2. **Saturated share over the 2,644 stages under NAE.** Compute `M` as the minimal hitting sets of the states' one-sets.
   - Prediction: no saturated stage is in the 5%.
   - Prediction: every collision not explained by a redundant junction contains a forced configuration as in F2.
   - My guess is that 85–95% are saturated. This is the one number I cannot derive.
3. **Parity classes.** For each same-states class, build the completed system. Prediction: where it is 3-connected, the admissible presentations are exactly one per junction of the completed system whose removal leaves every remaining junction with at least three places, and all collisions are re-choices of the dropped junction. The remaining classes differ by twists at 2-junction cuts.
4. **Catalogue.** Run rank 1 along the rings with spares and record the three-way verdict each round.
   - Keeps eddies and rates: every stage on the trajectory is saturated. The two growths then agree round by round and W = y^L (1 + y) is unchanged. A spare on each ring junction blocks the forcing of F2, so I expect this for plain rings, but I have not seen the catalogue's stages.
   - Loses them: a round where the cheapest growth makes an implied junction, or closes on a duplicate. The states-only growth then leaves those distinctions loose and keeps growing, so rates shift from that round on. The first such round is the result to report.
