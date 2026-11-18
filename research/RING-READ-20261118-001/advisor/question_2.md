Follow-up, same study (your first answer is folded in). Under 400 words: check the new reader and say which prediction you would
bet against.

Frozen results (rounds 10, 12, 14, 15, 16, 18, 20): tables at m = 6, 7, 8 agree; no one-parent junction after round 1; no triangle
in G; no two junctions share two distinctions; every layer cut >= 11; G (with o) is 3-connected at every round. The clique reader
run on (R1) gives 3 spurious junctions at 10-14 and the repair-plus-table-check (R2) then has exactly one survivor, the truth; the
round regrown from it equals the true next round; the least horizon is (largest size) - 1 = 6. Your linear prune (R1') changed
nothing (the spurious cliques are not parity consequences). From round 15, when stage 8 first runs, R1 misses one junction and
gives 104 spurious ones (148 at round 20, 17 missed), all within rounds 0-6 of the seed, and R2 finds no legal repair. Diagnosis
at round 15: the missed junction is the round-1 three-distinction one-parent junction, one of whose pairs the pairwise prune
removes at stage 8 (R1 recomputes every star from scratch each stage); the spurious cliques come from bonds of size <= 8 that are
sums of three or more small junctions (sizes 3-5) near the seed, which the pairwise prune does not remove.

New reader R3, to be frozen before it runs:
- keep every junction read at an earlier stage (no recomputation);
- at stage s remove a short pair (distance < s) when both its distinctions lie in the support of a sum of a connected set of at
  most g = 3 known junctions with support <= s, unless one known junction contains both;
- new junctions at stage s are the maximal cliques of what remains that are not known and not in the GF(2) span of the known ones;
- then R2's legality repair and table check.
Predictions: R3 alone exact at every round 10-20; with repair and check, one survivor, the truth; the regrown round equals the true
one; least horizon (largest size) - 1.

Questions: (1) Is g = 3 enough, given no triangles (your girth lemma), or should g grow with s? (2) Does keeping known junctions
risk a wrong early junction poisoning later stages? (3) Bet: which prediction fails, if any?
