# How the law's reach typically behaves across nested patterns: pre-registration

Epic `REACH-CENSUS-20261113-001` (`BOND-DEPTH-20261112-001` direction 2; G17, with G1), 2026-11-13, the coordinator's choice under
the owner's standing instruction; computed by Codex from a frozen spec (`codex_spec.md`). Frozen before any census result was seen.
The canonical K1–K3 test is unchanged. Law: not-all-equal (NAE) on three-place knots.

## The question

Two studies measured the least ray bond L_ray(s) (the least bond among the ray's own distinctions joining a top distinction to a
distinction of the copy s levels down) in the 664 one-definition families alive only in the limit: it provably grows in 226 and is
bounded in at least 361 (`PROVED-RATE-20261113-001`, refereed). That cell is 0.3% of the weight. Across all 223,261 nested draws of
the short-description code, which reach is typical: growing with depth, bounded, or absent? Does it differ between families that
live at every depth, die with a dead limit, and live only in the limit?

## In standard terms

For iterated hyperedge-replacement NAE instances sampled with probability 2^-length from a straight-line grammar: the share (by
sampling weight and among distinct sampled families) whose least root-to-depth-s minimal non-shattered set along one derivation ray
grows linearly in s, stays bounded, or does not exist; decided per family by the minimum cycle mean and an exact residue test on a
finite min-plus state graph.

## Population and weighting

The draws: `LIMIT-ONLY-20261112-001`'s sample W (eight seeded workers, 150,000 tries each, main variant), regenerated exactly from
its seeds (checked before freezing: 223,261 draws, 0 mismatches of stored bits or definitions; Codex re-checks, G0). A draw's
family is its description without the depth. **By weight** means the share of draws, a Monte Carlo estimate of the description
weighting restricted to nested families under the code's caps (A79, A71). **Among distinct sampled families** means exact counts over
the 124,572 distinct families drawn; it overrepresents heavy families and describes the sampled set, not a population.

Cells, by the stored fate and the usual limit: **lives at every depth** (220,880 draws), **dies with a dead limit** (1,487),
**alive only in the limit** (894, the genuine cell of `LIMIT-ONLY-20261112-001`).

## The ray for several definitions (new; frozen in the spec)

Definitions that do not hold themselves are inlined. The ray definition S is main if main holds itself, otherwise the definition of
main's first call to one that does; the ray follows main's first call to S and then S's first SELF call; every other call to a
self-holding definition is a side branch read by its limit relation. For one definition this is BOND-DEPTH's ray. Every claim is
"along the first ray"; the last-call ray is computed on a frozen sample of 3,000 families as a robustness check.

## Settled by construction (stated, not tested; measured before freezing)

Each has a one-line proof: a dead limit allows no state, so no set containing a top distinction is a bond (**S1**, 0.67% of weight);
if main reaches no copy there is no depth (**S2**, 5.83%); if S has no own distinctions after inlining, every copy lives on the
distinctions above it and no own distinction exists at depth s (**S3**, 52.6%); a distinction in no constraint of the ray's
projection is free and independent, so it is in no bond, and if every own distinction of S is such then no ray bond exists
(**S4**, 2.37%). So 58.4% of the weight has **no depth** (S2, S3) and 3.0% **no ray bond by construction** (S1, S4). These are
properties of the definition of L_ray and of the code, not findings. The other **38.6%** of the weight (60,081 distinct families)
is computed. The "dies with a dead limit" cell is all S1, so the fate comparison is between the other two cells.

Also known: L_ray(s) is a fixed-length shortest path in a finite weighted graph, so it is eventually linear plus periodic on each
residue of s; λ (Karp 1978) is its liminf rate, L_ray(s) ≥ λ(s − t) on a complete graph; the referee's residue test (lcm of the
zero-cycle lengths) decides eventual boundedness exactly (`PROVED-RATE-20261113-001`, referee R1). A bounded ray bond bounds the true
least bond to the ray's copies from above; growth and absence are ray-only.

## Classes of a computed family

grows (λ > 0, complete graph), bounded (exact test positive), mixed by residue (λ = 0, not eventually bounded), lost at large
depths (acyclic trimmed graph), none at any depth, unresolved (block over 12 distinctions, 300,000 nodes or 300 s without a positive
certificate).

## Reporting and words

A share's band [low, high] counts unresolved against the class (low) and for it (high), with a 95% bootstrap interval over draws
(low's 2.5% quantile, high's 97.5%). **Typical**: the interval's lower end above 1/2. **Common**: lower end at least 5%. **Rare**:
upper end below 1%. Otherwise undecided at that word. **Undecided rule**: if unresolved exceeds 5% of a cell's computed weight,
predictions on that cell are declared undecided, not failed.

## Predictions (frozen)

The advisor model reviewed the design cold (`advisor_review_answer.md`); its changes are adopted: the no-depth share is a
definitional row, not a finding; P3 is not blind on the limit-only side, so P2 and P3 state a bracket; P1's denominator and its
treatment of unresolved are fixed; "mixed by residue" is named and counts against P1; bounded is worded as an upper bound on the true
bond; the ray convention gets a robustness check; the gates go deeper (brute force past the transient, a metamorphic wrap of the
664, timing on several definitions in the smoke run).

| # | Prediction | Fails when |
| --- | --- | --- |
| P1 | **Bounded reach is typical where a ray bond persists.** Among computed draws that live at every depth, in grows, bounded, mixed by residue or unresolved, bounded's share has its interval's lower end above 1/2 (unresolved and mixed counted against). Prior: 361 of 652 (55%) in the limit-only cell, near a coin flip. | lower end ≤ 1/2 |
| P2 | **Growth is common at every depth but less so than in the limit-only cell.** Among computed draws that live at every depth, grows' share has lower end at least 5% and upper end at most 24%. | either end outside |
| P3 | **Families alive only in the limit grow more often.** Grows' share among computed limit-only draws minus that among computed forever draws is at least 10 points with unresolved assigned against it, and its bootstrap 2.5% quantile is above 0. Not blind: 226 of the 664 one-definition limit-only families (34%) are known to grow. | either part |
| — | Reported: every class by cell, by weight and among distinct sampled families, by number of definitions and by own distinctions of S; λ values; bounded values and onsets; unresolved by cell and number of definitions; the first-call against last-call agreement. | — |

## Gates

G0 the regenerated draws match the stored rows. G1 the new code reproduces PR's nodes, completeness, λ and `bounded_all`,
BOND-DEPTH's L_ray(s) and the referee's exact tests on the one-definition families (all 664 at the census caps in the full run).
G2 wrapping a one-definition family under a new main shifts L_ray by one depth and keeps λ and the class. G3 an independent brute
force over the ray's states agrees with L_ray(s) up to s = 10 on 150 small families, at least 10 per class and 40 with several
definitions. G4 no family that lives at every depth has a dead usual limit. Any G0–G3 failure invalidates the run.

## Stop rule

One Codex hand-off (code, gates, smoke), one full run launched by the thread (registered in `docs/LONG_RUNNING.md`), its frozen
summary, a referee hand-off, report.
