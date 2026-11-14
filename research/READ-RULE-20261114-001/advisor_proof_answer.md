<!-- claude -p --model claude-fable-5-2 --tools "" (modelUsage: claude-fable-5-2), 2026-11-14 -->

**Verdict:** I found no error in the proofs of R, R1, Claim 1′ or Claim 2′ (first part), but two statements overreach, and the stated gap does not look like the real one. Nothing was run; this is a reading check, and I took L(s) to be the least size of a bond holding p and a covered target at depth s.

**Theorem R.** The case split is complete; the two mixed sub-cases (z = ¬p with z = x, and z = p with z = ¬x) fall under the "equal" bullets. The statement is mis-scoped, though:
- **Exception:** as written, "L(s) ≤ 3" reads as unconditional, but in the exception the proof gives no bound at all. It should read "L(s) ≤ 3 unless …".
- **Tie clause:** "L(s) ≤ 2 when {p, x} is tied" is true by definition, so it carries no content.
- **z = p bullet:** this contradicts "three distinct distinctions" in the Setting. Either the bullet is dead or the Setting needs to allow it.

**Theorem R1.** Correct. The six triples do shatter all three pairs.

**Claim 1′.** Correct, including the step from the product slice to U_t × D_t. One caveat on the hypothesis: if c_a passes c_b a port by identity that is not a main port, M_t can be a product only when that coordinate is constant on the slice.

**Claim 2′ (first part).** Correct.

**"What is proved" overreaches.**
- **Span:** Claim 1′ gives T plus members on one side of each stretch. "Local", meaning bounded span, is not proved.
- **Which T:** it needs T ⊆ W for each stretch's own T.
- **Side subtrees:** rectangularity is assumed only along v, so they are uncontrolled.

**The gap.** I think it is misidentified. Cluster count and cluster span look irrelevant:
- **Linear case:** a bond holding p and a target at depth s has a member at every copy not in a member-free stretch. If all stretches are shorter than N, then |W| ≥ s/N.
- **Bounded case:** otherwise some stretch is longer than N. The stretch relations M_n live in a finite set, so they are eventually periodic with some period q. Inserting q periods leaves M, the outside relation and c_b's inside relation unchanged, so the shifted set is a bond of the same size and L(s + kqπ) ≤ L(s).

So the dichotomy reduces to a pumping lemma for member-free stretches, which uses no rectangularity. What needs checking:
- the inserted copy is a covered target at depth s + qπ;
- the identity pattern repeats along with M;
- the residues are taken mod qπ, not mod π.