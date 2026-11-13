## What I checked by hand (#2 only)

I assumed your conventions: successor chosen by the input letter, and (q,r) means r first.

- **q1 and q2 are affine.** q1: y₁ = x₁, yᵢ = xᵢ + xᵢ₋₁ + 1 (the Gray-code map plus a complement). q2 is the same with y₁ flipped.
- **q0 is not affine.** It flips every letter up to and including the first 1 (position k), then y_{k+1} = x_{k+1} + 1, then follows the q1 rule.
- **Parities** (n ≥ 2): par(q1x) = xₙ + n + 1 and par(q2x) = xₙ + n. par(q0x) = xₙ + n + 1, except for x = 0ⁿ and x = 0ⁿ⁻¹1.
- **[1,8,12]:** q1²x and q2²x always have opposite parity, so it is satisfied at every level.
- **[0,8,10]:** q1²x and q2q0x have opposite parity except at x = 0ⁿ⁻²1b. There they agree, and x itself differs from them exactly when n is odd.
- **[1,9,10]:** fine except at x = 0ⁿ⁻²1b, where all three parities agree. But there q0x = q1q2x = 1ⁿ⁻²0(b+1), so the knot is dropped.

So word parity is a state at every odd n ≥ 3. This is a case split, not a one-line proof, because the swap count depends on x and not just on n.

A consequence you can test: at even n, parity violates only two knots, x = 0ⁿ⁻²10 and 0ⁿ⁻²11 in [0,8,10]. If I am right, deleting those two makes every even level alive, and every dead core at even levels contains one of them. That also tests my conventions.

## 1. Alive half

The automatic-state product is sound. The transducers are synchronous and read left to right, so "three images distinct and the state agrees on all three, at length ≡ p" is a regular language. Emptiness proves it for all n. The size is tiny: at most 9³ run states × |M|³ × 5 equality partitions × 2.

- **Dropped knots.** Encode the "dropped when not distinct" rule exactly. The #2 proof depends on it.
- **Short words.** Let the product handle them. My formulas needed n ≥ 3.
- **Finding M for the other five.** Do not read it off solver models. Fix a feature automaton (first letter, last one or two letters, word parity, final states of the three generators' runs, level parity) and let SAT find the output table across several levels at once. Then prove it by the product.
- **Risk.** An automatic state may not exist for some patterns. Say so in advance.

An n → n+2 lift for alive needs a map from level n+2 to level n sending knots to knots. Dropping letters fails exactly at degenerate projections, and the parity state is not preserved by it. I would not pursue that for the alive half.

## 2. Dead half

Death at n+2 follows from death at n if there is a map from level n into level n+2 sending knots to knots. Three discriminators, cheapest first:

1. **Reduce death to a forced equality.** For #2 at even n, the system minus the two special knots is alive. So death means the rest forces x = q1²x = q2q0x at x = 0ⁿ⁻²1b. Compute forced equalities of the reduced system at levels 6, 8, 10 and see which chain of knots forces it and how the chain grows. Look for the analogous few bad knots in #3.
2. **Sections of the cover.** A section appends letters s(x) so that knots stay knots.
   - One letter: this is linear over GF(2), s(gᵢx) + s(gⱼx) = sw(stateᵢ(x)) + sw(stateⱼ(x)). It is a rank computation, feasible to level 16. I expect no section, given the alternation; confirm it.
   - Two letters: a 4-valued constraint problem per address, a small SAT instance at n = 4 → 6 and 6 → 8. If sections exist and look automatic, prove them by the same product construction.
3. **Resolution width.** Measure the width of the dead proofs at levels 6, 8, 10 with your knot-closure tool. Bounded width suggests an automatic derivation; growing width means a global obstruction.

Your "no fixed core" claim is not yet established. Core sizes 10, 30, 89, 602 come from non-minimum cores. Test directly whether the level-3 core embeds as a sub-pattern of level 5 (subgraph search by SAT), and run the small cores through your Fano-atom decomposition.

## 3. Design

- **R2 for #2 is a theorem,** if my hand check holds. Prove both linear states by the product first and relabel R2 as a replay check. The alive half of R1 for #2 and #3 is then also settled.
- **Forced verdicts.** If no knot at level n+1 projects to a degenerate triple, alive(n) forces alive(n+1). List those levels before freezing.
- **Unknowns.** Freeze the conflict budget and how an unknown counts in R1–R3. Level 16 has about 590k knots for nine placements.
- **Checker.** It must:
  - check the CNF against a second, independent pattern generator, since LRAT only certifies CNF ⇒ unsat;
  - check that each hint is used in order;
  - handle deletions;
  - reject mutated proofs as negative controls.

  Pure Python on proofs of 10⁸ steps may be too slow, so freeze a fallback.
- **R3.** The 48 were selected for a return, so expect regression. Calibrate the 80% on persistence from levels 7–9 to 10–12 in the same 41. Define the treatment of patterns mixed at 10–12. Add a period-3 or period-4 check.
- **Add R4:** the two-knot prediction for #2 above. It is cheap and sharply falsifiable.

## 4. Literature (from memory, unverified)

- **Classification.** Bondarenko, Grigorchuk, Kravchenko, Muntyan, Nekrashevych, Savchuk and Šunić classified 3-state automata over two letters (2008). Look up your seven by their numbers there; the list includes the Aleshin and Bellaterra automata.
- **Affine states.** Lamplighter-type automata (Grigorchuk–Żuk) have affine states like #2's. Their Schreier graphs are de Bruijn-like (Grigorchuk–Leemann–Nagnibeda).
- **Counting on Schreier graphs.** D'Angeli–Donno–Nagnibeda treat Ising and dimer models on self-similar Schreier graphs. Bondarenko's thesis covers Schreier graphs of bounded automata; yours have exponential activity, so it does not apply directly.
- **Covers.** Voltage graphs (Gross–Tucker) are the language for sections of two-fold covers.
- **Gray code.** "Parity of the Gray code is the last bit" is classical, and it is exactly the #2 computation.

I know of no result on two-colouring three-place patterns by level parity.
