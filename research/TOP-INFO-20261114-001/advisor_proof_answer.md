<!-- claude -p --model claude-fable-5-2 --tools "" (modelUsage: claude-fable-5-2), 2026-11-14 -->

**Verdict:** I find no fatal error in any of the three proofs, but the localisation statement is wrong in one clause and has two unstated conditions. I checked only the text you pasted, not the READ-RULE proof or Lemma W.

**Theorem P′.** Correct. The remark's relation checks out: any three ports with x are full (the fourth port can always be chosen to avoid the two removed states), and the four ports alone are already NAE4, so no bond holds x. "Covered" is never used.

**Two-block window.** Correct, provided all copies at the end of an S-word have the same block type. Otherwise the state must include c's type.

**Localisation.**
1. **The side-subtree clause is false as stated.** The proof bounds each run *between occupied levels* by m. A side subtree holding j members in a chain can put the last one about j·(m + 1) levels below the branch point. The bound should be "within m levels of the previous occupied level", so up to roughly C·(m + 1) in total.
2. **The cut needs the copy type in the state.** If callee kinds differ, equal product and carry map at l and l′ do not make the cut word a legal word. Inside side subtrees, m must also bound the states of products started from any copy, not only along the target's word.
3. **"Large s" depends on C.** The longest stretch exceeds m levels only when s is beyond about (C + 1)·m·(Π + 1) + C, which the statement should say.

The arithmetic for B is fine: at most C stretches of at most m(Π + 1) − 1 levels plus C occupied levels gives at most C·m·(Π + 1).

**Decidability.** It does not follow from these three proofs; your stated gap is accurate. I doubt it is genuinely open, though. Here is an unverified sketch of a bound on C:

- **Reformulate.** L(s) ≤ C exactly when some W of size at most C is non-full while W∖V and W∖X_c are full (the P′ argument).
- **Finite type.** At each level, record for W and for W∖V the family {S_α} of port-state sets compatible with each assignment α to the members above. There are at most 2^(2^(2^k)) such families per component for k ports.
- **Pump occupied levels.** The three conditions depend only on these types and their mirror from below. Cutting between two levels of equal type, Π apart modulo Π, keeps them and removes members.

A least W then has occupied levels bounded in terms of m, k and block size, with the same argument inside subtrees.