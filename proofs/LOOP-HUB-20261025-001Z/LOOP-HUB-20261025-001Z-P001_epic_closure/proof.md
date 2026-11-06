# Closure of the hubs-with-loops epic

Status: Proved

Epic `LOOP-HUB-20261025-001` closed on 2026-10-25. This is a ledger: one line per conclusion, with its novelty label and evidence. It
makes no new claim. The decision note is `research/LOOP-HUB-20261025-001/hubs_with_loops.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | No gadget of an open knot violated the arm inequality under adversarial annealing at 4 to 40 knots (384 runs), in chains of double edges (lengths 1 to 12) or in fully paired cores (3 to 15 knots); equality was reached in every run up to 16 knots, so the inequality is sharp. | A recorded computation | `LOOP-HUB-20261025-001A-E001`, supported; controls passed, independent re-check reproduced the verdict |
| 2 | On 2,000 small gadgets (371,328 linked pairs), linked pairs split by the empty side at the first branching knot never exceeded F(u + eᵢ)F(ū) or F(u)F(ū + eᵢ). | A recorded computation | `…001A-E001`, P3 |
| 3 | For each linked difference pattern, rerouting terminal i's arm maps its compatible configurations injectively into those of the image pattern; patterns map injectively on trees, which gives a second proof of the tree theorem. | Elementary; new to the program | `LOOP-HUB-20261025-001B-P001`, Lemma 1 |
| 4 | For the axes u and u + eᵢ together, the arm inequality is equivalent to \|minor\| ≤ agree + cross in the table of terminal i against terminals j and k, and to 2F(u)F(ū) ≤ G(A)G(Ā) + split_j + split_k; G is positive on every pattern, so two terminals can never be locked to an antipodal pair. | Elementary | `…001B-P001`, Proposition 2 |
| 5 | Gadgets of two or three knots satisfy the arm inequality but break the bound per partner solution, per image pattern, for one-sided path-flip matchings and without the agreeing terms; any proof for gadgets with loops must therefore be global. | Exact computation; new to the program | `…001B-P001`, Proposition 3 and Corollary 4 |

## Challenged assumptions

The decision note records three workspace assumptions this epic challenges:
- that a smarter routing rule would extend the tree proof to loops (false for every local rule);
- that collisions of the reroute signal violations (false: they occur only with slack);
- that the agreeing terms are slack (false, even on a two-knot tree).

## Recommendation

**Full pivot to the space intuition: twists in three dimensions.**
- **The question.** Can a native law built from the twisted Fibonacci knots give a Pachner-invariant count on triangulated 3-manifolds
  that sees more than H¹(M; Z₂)?
- **Why now.**
  - The hub question is settled for exact hubs and for trees, and is well supported in general. A full proof needs a global method,
    with modest conceptual payoff.
  - The twist is where the complexity and space lines meet: it is a signed reflection in the Fibonacci basis, and the Fibonacci rule
    needed a negative weight in three dimensions.
- **The first discriminator.** An exhaustive test of 2–3 and 1–4 invariance for laws placing the six open knots on tetrahedra.
- **Interest:** 2/3.
- **Alternatives:** a computer search for a closed family of inequalities proving the arm bound (1/3); Markov-chain experiments for the
  six (1/3); a note on native complexity (1/3).
- **Stop if** every surviving twisted law reduces to the trivial or parity class.
- **Execution:** deferred to the owner.
