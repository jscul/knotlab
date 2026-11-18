# Referee report TREE-STEPS-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block on the study's own claims, which are about trees and single-law bases.**
- **The proofs and the numbers hold.**
  - H1, H2 and K1 to K4 hold as stated.
  - With its own code, the referee reproduces both distances at steps apart on every six-knot tree under every law assignment:
    1,216 bases and 94,848 pairs.
  - The same holds on 200 random seven-knot trees of the referee's own: 21,000 pairs, 196 of them mixed.
- **One Narrowing of the headline.** "The repaired distance keeps everything the first one read, parity and not-all-equal alike" is
  false on bases with cycles.
  - Close a not-all-equal path of k knots from x to y with a parity knot (x, y, z).
  - The first distance reads x and y as one step apart: their parity knot binds them, κ = 1 − C².
  - δ_K reads them as k steps apart, because their weak pair correlation C = (−1/3)^k makes every larger set reducible.
  - For k ≥ 3, δ_K also fails the triangle inequality, through z.
  - On trees, and on each law's own bases, nothing changes.
- **The owner's three flags.**
  - **K2's step:** right (§2).
  - **K1:** a single rule whose effect is exactly the case split, and the case split has the cost above (§3).
  - **H2's "fifteen knots is safe":** covers single hubs only. Spread and nested hubs are open (§4).
- **A correction to the referee's own CUMULANT-DIST report.** It said "parity hubs do not help". That is true only with one child
  per hung knot. With both children, a parity knot gives an exact copy of the coin for two distinctions.
  - The referee checked it here (κ = 2/3 at two parity knots and one path knot).
  - The CUMULANT-DIST report is corrected in the same commit.

## What holds (recomputed; `referee_steps.py`)

The referee used its own states, partition-formula cumulants and tree shapes from CUMULANT-DIST-R1, and its own irreducibility
test.

| Part | Referee | Study |
| --- | --- | --- |
| Every six-knot tree (19 shapes) × every parity/not-all-equal assignment | 1,216 bases, 94,848 pairs: δ = δ_K = steps apart on all, never differing (1,178 mixed) | the same |
| Random seven-knot trees, at most three knots per distinction, random laws (the referee's own 200) | 21,000 pairs: δ = δ_K = steps apart on all (196 mixed) | 80 trees, 8,400 pairs |
| H1, a not-all-equal hub with both children taken, (N, k) = (1, 1), (2, 1), (2, 2), (3, 1) | κ = κ_(2N+2)(coin)(−1/3)^(2N+k) on all four | the same, gated |
| H1, a parity hub with both children on x and a not-all-equal path to y, N = 1 to 4 | κ = κ_(N+2)(coin)(−1/3)^k: 0, 2/3, −2/9, 0, −16/3 | the same rate in H2 |

- **H1's extension is right.** Given σ = s_x, a hung not-all-equal knot's two children have a constant conditional covariance,
  −4/9. So any partition block holding both drops out of the law of total cumulance once |S| ≥ 3, and they act as two independent
  copies of mean −1/3. A hung parity knot's children have E[s_b s_c | σ] = σ and mean 0 each: one exact copy for two distinctions.
- **H2's threshold is right.**
  - The price per copy is the same in both cases: one distinction plus log₃ 3 for a not-all-equal child, two distinctions for a
    parity pair.
  - So a single hub shortcuts at 32 copies: 16 not-all-equal knots with both children, or 32 parity knots on a mixed tree.
  - The condition is log₃|κ_(2j+2)| > 4j, which first holds at 2j = 32.
  - It also needs the path to be long enough: k > 2j.
- **K3 and K4 are right.**
  - Every hub set contains T₀ = {x, y} together with the path's parity third distinctions, and T₀ binds.
  - With no parity knot on the path, C = (−1/3)^k ≠ 0 and K1 applies.
  - The open case, a parity knot on the path, is computed on every six-knot tree and on the referee's seven-knot sample.

## 1. Bases with cycles: what δ_K gives up (Narrowing)

- **The base.** Close a not-all-equal path of k knots from x to y with one parity knot (x, y, z). Here z = x ⊕ y.
  - Results are in `referee_steps_cycle.json`.

  | k | C(x, y) | δ(x, y) | δ_K(x, y) | δ_K(x, z) = δ_K(z, y) | Triangle inequality for δ_K |
  | --- | --- | --- | --- | --- | --- |
  | 2 | 1/9 | 1.011 | 2 | 1.011 | holds |
  | 3 | −1/27 | 1.001 | 3 | 1.001 | **fails** (3 > 2.002) |
  | 4 | 1/81 | 1.0001 | 4 | 1.0001 | **fails** |
  | 5 | −1/243 | 1.00002 | 5 | 1.00002 | **fails** |

- **Why.** {x, y, z} is a knot under K1 to K3: forgetting any one of the three leaves the other two free. Bond distance therefore
  reads x and y as one knot apart, and δ reads them as about 1.
  - δ_K rejects {x, y, z}: its subset {x, y} has nonzero cumulant, the weak correlation the long path leaves.
  - So δ_K reads the pair as k steps apart while z sits about one step from each.
- **What this says about the repair.**
  - It is not "the cumulant form of K2". K2 asks that the rest be *free* (unconstrained). Irreducibility asks that it be
    *uncorrelated* (zero cumulant). A not-all-equal path makes x and y correlated but not constrained, and that is exactly where
    the two part.
  - The headline "keeps everything the first one read" fails here. "One step per knot" holds on trees, not on cyclic bases with
    mixed laws, and those are direction 2's mixed laws on the weave.
- **The fix.**
  - Scope the headline to trees and single-law bases.
  - Call the rule "irreducible in cumulants, a relative of K2", not K2's cumulant form.
  - Add to the limitations that δ_K is not a metric (this cycle) and is blind to a knot whenever its pair correlates elsewhere.

## 2. K2's step (the owner's flag; holds)

- **The step.**
  - On a parity base, κ_S ≠ 0 makes the restricted matroid connected (CUMULANT-DIST D1).
  - So x and y lie on a circuit C ⊆ S with κ_C = ±1, and a non-circuit S contains C strictly and is not irreducible.
  - A circuit is irreducible: a proper subset holding x and y carries no dual codeword, so its spins are independent and its
    cumulant vanishes.
- **Its dependence.** K2 rests on D1's connectivity lemma. The referee's CUMULANT-DIST report (§1) noted that D1's proof needs the
  hypothesis "no circuit inside S meets both parts". With that hypothesis the lemma, and so K2, are proved.

## 3. Is K1 a case split dressed as one rule? (the owner's flag)

- **Both.** The rule is one: count only sets with no smaller binding set holding the pair. But its whole effect is the case
  split.
  - When C(x, y) ≠ 0, δ_K = τ, the count's reading, and nothing larger is ever looked at.
  - When C = 0, it is the least irreducible binding set: on parity bases, the least circuit.
- **So the unification is:** "the pair's correlation if it has one, otherwise the least minimal binding set". That is fair to say
  plainly.
- **The cost of the split is §1.** A pair correlation, however weak, overrides a knot holding the pair. δ_K also jumps as C crosses
  zero. On trees and single-law bases the split is harmless:
  - not-all-equal trees have C ≠ 0;
  - parity bases have C = 0 off their ties.

## 4. H2's "a distinction in at most fifteen knots is safe" (the owner's flag)

- **H2 proves what its heading says, for one hub.** Its own text says "cannot shortcut this way" and excludes nested hubs. The
  answer's "a distinction in at most fifteen knots is safe" drops that qualifier.
- **Two hubs, one at each end of a long path.**
  - The exact cumulant is μ^(N₁+N₂) times the mixed cumulant of two coins with correlation ρ = (−1/3)^k.
  - Its leading term is ρ·κ_(N₁+2)(coin)·κ_(N₂+2)(coin), so the gains add per hub.
  - Since log₃|κ_(N+2)| − 2N ≤ 0 below 32 copies, two sub-threshold hubs gain nothing to leading order.
  - A shortcut needs k beyond the copies, and there ρ is tiny.
  - The exact values at short paths sit above the leading term. With two four-copy hubs and k = 1, the exact κ is −0.0419
    against a leading term of −0.0130 (`referee_steps_hubs.json`). So this is an argument, not a proof.
- **Nested hubs.** Copies feeding copies through shared knots are linked at −1/3, not at a tiny ρ, so the leading-order argument
  does not apply. They are open, as the note's limitations say.
- **Fix:** "no single hub on a distinction in at most fifteen knots can shortcut; spread and nested hubs are open".
- **δ_K is unaffected.** It ignores any set that contains a binding set holding the pair (K3).

## 5. Smaller points (Not a block)

- **"The program's bases have at most six knots per distinction"** is the note's statement. The referee did not check it.
- **Known results.** Tree cumulants (Zwiernik and Smith) and the law of total cumulance are rightly cited. So are the tangent
  numbers. What is the program's: the threshold for its knots, and the irreducible-set reading.
- **Thresholds in the two notes.** The CUMULANT-DIST correction speaks of 32 knots with one child each (65 knots in all). H2 here
  needs only 16 with both children (49 in all). The two notes should give the same smallest hub.

## Fixes for the thread (listed for the owner, not folded in)

1. **Cyclic bases.** Scope "keeps everything the first one read" and "one step per knot under either law" to trees and single-law
   bases. Add the closed-path example, where δ_K misreads a parity knot as k steps and fails the triangle inequality. **Narrowing.**
2. **The K2 wording.** Use "irreducible in cumulants, a relative of K2". K2 asks for freedom, irreducibility for zero correlation.
   **Narrowing (wording).**
3. **H2.** Write "no single hub on a distinction in at most fifteen knots can shortcut; spread and nested hubs are open". **Not a
   block.**
4. **K1.** Say plainly that δ_K is the pair's τ when C ≠ 0 and the least minimal binding set otherwise. **Not a block.**
5. **The smallest hub.** Align CUMULANT-DIST's correction (32 knots, 65 in all) with H2 (16 knots, 49 in all). **Not a block.**
6. **The referee's own CUMULANT-DIST report** said "parity hubs do not help". Corrected in this commit. Parity hubs count at the
   same rate when both children are taken; pure parity trees are unaffected.

## How the work was split

- **The referee:**
  - read the note, the pre-registration, proofs H1, H2 and K1 to K4, and `treelib.py` and `job.py`;
  - checked the proofs by hand;
  - wrote `referee_steps.py` (both distances, the six-knot census, its own seven-knot sample, the hub cases and the closed path) on
    its CUMULANT-DIST-R1 code.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_steps.py`.**
- **`referee_steps_six.json`, `_rand7.json`, `_hubs.json` and `_cycle.json`.**

Reproduce, from `research/TREE-STEPS-20261118-001/referee-R1/`:

```sh
for p in six rand7 hubs cycle; do ../../../.venv/bin/python -B referee_steps.py $p > referee_steps_$p.json; done
```
