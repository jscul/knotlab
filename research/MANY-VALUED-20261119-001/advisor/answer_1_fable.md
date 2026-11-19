['claude-fable-5-2']
**Short answer:** the rule as written is not states-only, because a junction's support can be non-minimal. M2 is forced by a symmetry in the K4 case and I expect it to fail elsewhere. M3 is mostly a restatement of uniqueness, so the headline should be about uniqueness.

I reasoned from your text only and assumed the growth acts on the presentation (which distinctions sit in one member and which in two); I do not have the growth rule in front of me.

## 1. Well defined, but not states-only as written

**A junction's support can be non-minimal.** Take seven distinctions a, b, c, d, p, q, r and the stage

- NAE(a, b, p), NAE(c, d, q), NAE(p, q, r), NAE(a, b, c, d, r).

It is admissible (every distinction is in exactly two members) and irredundant (I checked each member against the other three by hand). But NAE(a, b, c, d) is implied: if a = b = c = d = 0 then p = q = 1, so r = 0, and the five-place member is all 0. So the five-place junction is not in M(S); M(S) holds (a, b, c, d) instead, which is minimal.

This has three consequences:

- **The pool depends on the stage.** "M(S) ∪ {the stage's junctions}" is read from the presentation, so two stages with the same states get different pools. That is the choice you had not noticed.
- **This start has at least two presentations.** They are the stage (A), and the stage with the five-place member replaced by NAE(a, b, c, d) (B). B is admissible, irredundant and allows the same states.
- **A and B differ in what is open.** In A every distinction is in two members; in B, r is in one. If growth happens at distinctions held once, they grow differently.

The start has a double touch (the junction meets (a, b, p) at both a and b), so it is in the class where your undefined points live. Check whether the census contains it or whether it can arise mid-trajectory.

**Pools that are states-only.** There are two, and they answer different questions:

| Pool | States-only | Stage always a presentation | Effect on the example |
|---|---|---|---|
| M(S) only | yes | no | B is a presentation, A is not, so the rule may grow something the stage is not |
| Every implied NAE set (all supersets of members of M(S)) | yes | yes, if admissible and irredundant | A and B both count, so "several" |

I recommend the full implied pool as the definition, with the M-only count reported beside it. Your current pool is the full pool cut down by knowledge of the stage.

**Other choices to state in the freeze:**

- **Unique as a set, or up to symmetry.** Two presentations exchanged by a permutation of distinctions that preserves S are different sets but the same structure (see question 2).
- **No auxiliary distinctions.** Presentations are over the stage's distinctions only.
- **The admissible class is an input.** The rule reads the states plus the declared class (at least three places, at most two members per distinction); say so.
- **Irredundancy at later rounds.** "No redundant knot" is stated for starts. If a grown stage has a redundant member, the stage is not among its own presentations.

## 2. M2 is forced for K4 and unsupported elsewhere

**K4 is a symmetry.** Read the six distinctions as the pairs of four knots. The map sending each pair to the complementary pair turns each knot's three places into the three pairs among the other three knots. So it swaps your two presentations. Since both allow the same states, the map preserves S. Any label-free growth therefore grows them isomorphically at every round, not just three. The K4 agreement is not evidence for M2.

**No general reason.** Two presentations not exchanged by a symmetry of S can differ in total size, and so in how many distinctions are held once. I know of no invariant forcing equal counts. The A/B pair above is the natural counterexample candidate.

**Suggested split:**

- **M2a (a theorem, not a prediction).** Presentations in one orbit of the symmetries of S grow isomorphically. Fold this into the rule: defined when the presentation is unique up to symmetries of S. K4 then becomes defined.
- **M2b (the risky one).** Presentations in different orbits grow the same counts. I would predict this fails, and test it on A/B first.

## 3. The headline overstates; uniqueness is the finding

**M3 is nearly M1 again.** If the refined rule means "apply the growth to the unique presentation", and that presentation is the stage, then it equals the cheapest growth by construction. M3's content is then only that uniqueness holds at every trajectory point, plus that the stage is in the pool, which your pool guarantees by including it. Freeze it as that uniqueness claim.

**A more accurate headline:** "Within the range checked, the allowed states fix their admissible irredundant presentation, up to symmetry, so any rule that reads the presentation reads only the states." This is stronger than a statement about the cheapest growth, and it is what the data would show.

**Qualifiers it needs:**

- The range: starts of up to four knots, at most 18 distinctions, 6 rounds.
- The exception rate, by start as well as by point.
- The pool used.
- "Under not-all-equal, in the admissible class."

**On M1.** The 146 points come from few starts, so points on one trajectory are correlated. Having seen 40, freeze the 95% on the remaining 106 and report it by start. Under the full implied pool the pilot's 39 of 40 may drop, so rerun the pilot on that pool before freezing the number.
