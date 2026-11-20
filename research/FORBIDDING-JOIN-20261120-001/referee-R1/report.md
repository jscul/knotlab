# Referee report FORBIDDING-JOIN-001-R1 (lean)

**Verdict: stands. The Narrowing it logged against G18's explanation is graded correctly. No Block, no new correction.**

1. **The rivals forbid states yet always leave a complete state: correct.** The rivals grant f = min(q, max(h, q − 1)) or
   f = min(q, h), with h = max(0, 3 − p).
   - **Parity:** a homogeneous parity system always allows the all-zero state.
   - **Not-all-equal:** every distinction has at most two holders and every holder keeps at least three places (both rivals grant
     at least h, so p + f ≥ 3). A colouring giving every holder both values then always exists, by the classical edge-colouring
     fact for minimum degree three.
   - **Infinite histories:** compactness carries this to every infinite history.
   - **States can be removed.** A birth granted no fresh distinction constrains its old inputs.
2. **Free settings give CHSH ≤ 2: correct (Bell–CHSH and Fine).** One common weighting of complete surviving states gives a single
   joint distribution of all four readings. So preserving every old state was sufficient but not necessary.
   - **The logged Narrowing** of G18's explanation (an interpretation of a sufficient hypothesis) is the right grade. The
     conclusion stands; only the stated reason narrows.
3. **The seven-knot source stalls under both rivals: confirmed.** It was regrown with the referee's engine under both knot laws.
   - **The first births.** The ordinary first births get fresh counts 3 × 7 and 4 × 1. One-fewer gives 2 × 7 and 3 × 1. The arity
     floor gives 1 × 8.
   - **The stall.** Both rivals stall at the next round (attempted size 3) under parity and under not-all-equal. The ordinary law
     continues.
   - **Not regrown:** the six-knot start that continues forever.
4. **The 5/2 table needs a supplied dependence on both settings: correct.** With free settings and responses depending only on the
   local setting and the shared state, the bound is 2. Exceeding it requires Bob's response to depend on Alice's setting, as
   supplied.

**How the work was split.** The referee read `decision.md` and `setting_dependent_control.md`, and regrew the source with its own
engine (seconds, run directly). No study code was run. No Claude helper, Codex or advisor was used.
