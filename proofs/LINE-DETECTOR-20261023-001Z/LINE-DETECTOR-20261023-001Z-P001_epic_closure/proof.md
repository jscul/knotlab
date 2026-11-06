# Closure of the line-detector epic

Status: Proved

Epic `LINE-DETECTOR-20261023-001` closed on 2026-10-23. This is a ledger: one line per conclusion, with its novelty label and
evidence. It makes no new claim. The decision note is `research/LINE-DETECTOR-20261023-001/line_detector.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | In every two-literal tiling world on a triangular torus, shared coins included, a configuration contradicts along no class, along the multiples of one class, or along every odd class: the trichotomy. The doubly allowed tiling makes the parity of every closed implication walk the relative twist of its class. | New to the program; moderate folklore risk | `LINE-DETECTOR-20261023-001B-P001`, Lemmas 1 and 2, Theorem 3; exact in A (P2) on 3 × 3 and 3 × 4, sampled on 4 × 4 |
| 2 | Hence a lone line is a pure line and a line event in two-literal worlds. The dual-pair failures of shared-coin worlds are failures of the line event itself. | New to the program | `…001B-P001`, Corollary |
| 3 | Three-place worlds break the trichotomy. Certified configurations contradict along some odd classes and not others, and 12 of the 30 three-place placements (four orbits) do so on every torus computed. | Certified computation; direction-dependent periodicity of two-dimensional shift spaces is classical, the contrast is the program's | `…001B-P001`, Propositions 4 and 5; A (P3) |
| 4 | So at three places a lone line is not a line event. For the most lopsided dual pairs of `TRIPLE-SHIELD-20261023-001`, the lone lines nearly all contradict along classes the event never checks: all of them on 3 × 3, all but 6 and all but 1176 on 3 × 4. Lines pure among eight classes still differ across dual pairs (395160 against 547584 for placement 111 on 3 × 4). The scoping prediction that no lone line of those families is pure failed on 3 × 4. | A recorded computation | A (P4 refuted, P5) |
| 5 | Classifying contradictions by their minimal witnesses does not show their direction, even at two literals. | A recorded observation | Decision note |

## Challenged assumptions

The decision note records four workspace assumptions this epic challenges:
- that a three-cylinder lone line is the three-place analogue of a lone loop;
- that the lopsided three-place ratios show the line seeing the twist;
- that coin reach rather than clause width is the dividing line (it divides shielding; clause width divides the direction
  structure);
- that minimal witnesses show a contradiction's direction.

It also asks the owner whether to supersede `TRIPLE-SHIELD-20261023-001-D001` formally.

## Recommendation

**Continue with a fresh epic: directional rigidity.**
- **The question.** Which contacts are all or nothing in direction?
- **The first step.** Test the 18 rigid three-place placements with up to 16 classes and larger tori. Then compare the algebra of
  rigid and selective contacts.
- **Interest:** 2/3.
- **Alternatives:** a note (1/3) and the 3/4 constant (1/3).
- **Execution:** deferred to the owner.
