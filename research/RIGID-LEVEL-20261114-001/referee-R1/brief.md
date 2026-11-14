# Referee brief RIGID-LEVEL-R1 (from the coordinator, 2026-11-14; light check, no Codex)

**The epic.** `RIGID-LEVEL-20261114-001`, commit a9a2993db, closed Inconclusive.

**The claim.** Rigidity of #2 at every level is not proved; it is certified to 14 and conjectured beyond. The obstacles:
1. **Not affine.** With g = f XOR parity, the knot constraint is not affine.
2. **One-sided closure.** It stays at 3 to 5 addresses, and the pair graph is not bipartite at levels 5 to 12.
3. **Propagation.** Unit propagation and depth-1 probing fail at levels 6, 8 and 10. Depth 2 refutes 3 of 6 at level 6 and 0 of 3
   at level 8.
4. **Proof sizes.** CaDiCaL's proofs grow 8 to 40 times per two levels, against the pattern's 4 times.
5. **Induction.** Solutions do not project down levels.

**What to check (short).** That the note claims no more than "not proved, these routes fail", and that the "not affine" and "pair
graph non-bipartite at levels 5 to 12" statements recompute. Do not spend Codex time trying to prove rigidity.
