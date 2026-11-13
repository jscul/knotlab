**Verdict:** the method is exact as stated, with one hole: the Karp step.

**Exactness**
- **G-combination: exact.** Non-fullness is upward-monotone, so minimality reduces to single deletions. Forgetting w replaces one child's mask by the union of its two w-masks, and R_P distributes over union in one child argument. Pooling G over which member was forgotten is fine because the root test is universal.
- **Sets suffice.** Children's assignments are independent, so sets of masks lose nothing, and cost is additive, so least cost per summary is enough.
- **One thing to check in code:** G_S must be built from paired masks (same rest-assignment), never from F_S alone.
- **Cost cap: sound.** A ray bond is a bond anywhere, so L ≤ L_ray, and the top port and v cost 2.
- **Karp: not sound as described.** The cap depends on s, so the ray-summary graph does too. For a rate you need the uncapped generic table (finite, possibly huge) or a proof that a per-level side cost bound suffices. Run Karp only on the part reachable from C_s states and co-reachable to accepting roots.

**Settled by construction (not tests)**
- L ≤ L_ray, and λ_true ≤ λ_ray.
- No level skipping.
- DP equals brute force at the same truncation: this is a code check, not a finding.
- P2 is mostly implied by P1 plus the proved theorem; it has content only where L < L_ray.

**Validation**
- Make the brute force test bonds by direct projection of the full relation, with no masks.
- Compare the full set of bonds by size, not just the minimum.
- h = 2 cannot test the fixed point, so add h = 3 on the smallest family.
- Include at least one family where L < L_ray, otherwise the G-branch is untested.
- Add a mutant: with F used in place of G, the comparison must fail.

**Cheaper exact pruning**
- Drop side summaries with ∅ ∈ F_S: they contain a bond that excludes the top port.
- Drop non-empty side summaries with F_S = {G}: their members are inessential, so W is not minimal.
- More generally, drop any summary whose G contains ∅.

**Predictions to make instead**
- **P1′:** the number of families with L(s) < L_ray(s) for some s ≤ 12 (give a number).
- **P2′:** in those families, the deficit L_ray − L is bounded in s (a boundary effect) rather than linear. This is the discriminating prediction.
- **P3:** λ_true > 0 in all 226 families, and equal to λ_ray in at least X%.
- State what falsifies each: any family with a zero-cost trim cycle kills P3.
