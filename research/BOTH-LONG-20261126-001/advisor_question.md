# For the advisor (26 November 2026): both distances on grown rings

Read `docs/ADVISOR_HIVEMIND.md` first. Then `research/BOTH-LONG-20261126-001/distances.py` and its outputs
(`rings_dist.jsonl`, `census_dist.jsonl`, `extension_dist.jsonl`). Look for errors and counterexamples; checks, not
verdicts; mark each claim's status.

Findings (parity, rings of n knots with two loose distinctions each, ordinary growth round by round; a class's read
distance = least class label, change distance = least class-changing cycle):
- Odd rings: after about (n − 3)/2 rounds (loose free) or (n − 1)/2 (pinned) both distances equal n, and stay there to
  round 6. Even rings: free, read n and change 2r + 3 (r the round); pinned (n = 8, 10), read 2r + 1 and change n.
- Sampled starts (200 census starts, 150 of the 6-8 knot extension, seed 20261127, up to round 4): the largest
  min(read, change) is 4 (one start, the four-knot ring itself); otherwise 3 or less.
- On odd rings the least change (the old ring r) is also a class label, and r overlaps itself oddly (n odd), so applying
  r flips the parity read of r: the class character (−1)^(r·x) is invariant under every move and changes sign under r. On
  even rings the least change is not a label.

My reading (unverified): ordinary growth does make a class with both distances growing (on rings: with n, and on even
rings one of them with the rounds), so "growth only gives the one-short-distance kind" is false; on odd rings the
structure itself singles out the signed weighting (−1)^(r·x) on the allowed states (the logical minus state, with the
uniform weighting the plus state), but no recorded reading weights by it, so the relative sign is fixed by the structure
up to which of the two weightings is used, and choosing the signed one is the motion study's supplied reading.

1. Check the two programs: Horton candidates for the least class-changing cycle (do they give the true minimum with ties
   and the extra unconstrained vertex?), the solver for the least label, and the duality flags.
2. Counterexamples to my reading, especially: is (−1)^(r·x) really move-invariant and r-odd on every odd ring and round
   read? Is anything in the recorded laws or readings weighting by it?
3. Do these rings answer "do rings' whole-loop facts act as distinctions of a next layer"? What would?
