# The advisor's answer (26 November 2026), before the census was frozen

I answered from the pasted design alone and did not open the repo's growth code or the three scripts. The citations are from memory; check them before they go in.

## 1. Proof A2

The argument is right in substance, but three things need fixing before it is called proved.

- **It runs in the wrong direction.** Starting from a point of V_11 you produce one point of V_00 carrying the fourth relation. That does not rule out the reading being balanced on V_00, which would give three ±1 and one 0, so CHSH = 3. Start instead from an arbitrary (α′, β′) ∈ V_00, get (α′, β″) ∈ V_01 and (α‴, β′) ∈ V_10 from the record conditions, and sum to (α‴, β″) ∈ V_11. Then every point of V_00 has value c_01 + c_10 + c_11.
- **The spaces are affine, not linear.** Odd parity equations make them cosets. The step survives because you add three points, and an affine space over GF(2) is closed under odd sums. Say "sum of the three"; the text says "their sum" of two.
- **The middle is missing.** States are (α, γ, β), with γ the distinctions of knots neither reader holds. The proof goes through only if each reader's setting-dependent equations touch record coordinates alone. If Alice's birth has a middle knot as parent and its equation touches γ, the three-point sum no longer lands in S_0.

Growth can break exactly one hypothesis: that the equations split as W (no setting) + S_x + T_y. The three ways are:

- **A birth with parents from both sides,** or any equation whose presence or right-hand side depends on (x, y) jointly. Parity then reaches 4 linearly: a + b = x·y is the literature's PR box, with affine spaces and no signalling in the values.
- **A middle birth that changes with one edit.** T then depends on x.
- **A stall.** It is a whole-round event, so one reader's edit removes the other's births.

All three should show in the shapes of the complete record, so the census catches them as signalling. Flag every placement as "splits" or "does not split", and claim A2 only for the first kind.

A2 also needs the uniform weighting on the space. U and S agree for parity because fibres have equal size; say so.

## 2. A3 and the reading

"Measurement dependence" is fair. "Not conditioning on settings" is defensible only as a reading.

Mathematically, μ(λ) α_x(λ_A) β_y(λ_B) / Z(x, y) is exactly the detection-loophole form: local acceptance followed by renormalising per setting pair. A3 is the standard "guess your own setting" model, where p is Alice's guess of x and she survives when it is right.

The report should say plainly:

- Every table in this class has a local model with local rejection, so nothing here is nonlocal.
- Bell's theorem is not beaten; its hypothesis fails, so it does not apply.
- Normalising each setting pair separately is a choice of weighting (a scaffold), and no signalling is not automatic in this class; it holds in A3 by symmetry.
- Experiments that closed the detection loophole in 2015 rule this mechanism out as discarded runs. It survives only read as worlds that never exist, which puts it nearer the literature's retrocausal or all-at-once models than post-selection in a laboratory.

Sharper citations:

- **Branciard, *Phys. Rev. A* 83, 032123 (2011).** The post-selected local bound is CHSH ≤ 4/η − 2 for local survival fraction η. It reaches 4 at η = 2/3 and gives the Garg–Mermin 82.8% threshold at 2√2.
- **Garg and Mermin, *Phys. Rev. D* 35, 3831 (1987); Eberhard, *Phys. Rev. A* 47, R747 (1993).** The efficiency thresholds.
- **Hall, *PRL* 105, 250404 (2010); Barrett and Gisin, *PRL* 106, 100406 (2011).** How much measurement dependence is needed.

Branciard's bound gives an exact, checkable link. Record η for each reader's edit (the fraction of old weight that survives it) and test every excess against 4/η − 2. A3 has η = 1/2, which is more forbidding than 4 requires.

## 3. The census

My main worry is that the census comes out clean because the class is too small, not because the laws cannot do it.

- **Two-sided forbidding needs room.** Each reader needs a join of three parents of its own, and the two joins must not share a parent whose distinctions enter both. With five knots, two three-parent joins must overlap in at least one knot. With E2 (two holders each, none meeting) five knots leaves a single middle knot.
- **The Mermin census is tighter still.** Three pairwise non-meeting readers in five knots is close to one hub with three holders. Three separate forbidding joins look out of reach.

Before freezing I would change these:

1. **Run a structural pre-count first.** No tables: per law and edit, count placements where each reader's edit makes a no-fresh join of three parents, split by "splits" or "does not split". If the count is zero, report "class too small, not run as a test", not a clean census. Then either extend to six or seven knots along a registered order, or add one built start, recorded as a scaffold.
2. **Add a kind "shared birth"** for a birth in both readers' records, kept apart from the three existing kinds.
3. **Add a kind "no allowed state"** for Z(x, y) = 0. Dropping such a setting pair silently is itself post-selection.
4. **Name births from the reader's own side.** A global index shifts when the far edit adds births, which gives false signalling or false agreement.
5. **Record η and the splits flag** per placement.
6. **Add a three-reader A3:** the guess-your-setting model reaching Mermin win 1, so the "class reaches the maximum" statement covers both games.
7. **Use exact rationals,** and test the record's joint distribution, not each value's marginal.

On stalls: a stall in (x, 1) but not (x, 0) changes Alice's record, so it is correctly signalling. The trap is a stall that depends on (x, y) jointly while each reader's record keeps the same distribution, the PR pattern in shapes. Record such a case as its own row, not merged with ordinary excess.

## 4. Predictions

- **Parity:** I agree. Zero excess without signalling on placements that split; on the others, any excess comes with a change of shape. The three-reader best stays 3/4.
- **Not-all-equal, ordinary count:** I agree on both weightings.
- **Not-all-equal, A129/A130:** zero excesses without signalling in three to five knots, but mostly by vacuity. I expect the pre-count to find no placement that splits and has forbidding on both sides, or only a handful.

Where forbidding is one-sided, I expect excesses with every single value fair and the complete record changed, sitting between 2 and about 5/2.

If a larger class does give an excess without signalling, it must respect 4/η − 2. A three-parent not-all-equal join with nothing fresh removes only the all-equal combinations, about a quarter of the old weight if the three given values are near uniform under U. That gives η ≈ 3/4 and a ceiling near 10/3.

Finding no such excess would not surprise me. Unchanged records need a reader's survival to be independent of the whole far record while still correlated with the far reading. A3 gets that from a three-way relation, q + s = p·r. I do not see how one round of not-all-equal growth from a small start builds such a relation.
