Advisor consultation for `BUILT-BINDING-20261126-001` (study directory research/BUILT-BINDING-20261126-001), before its
test is frozen. Read docs/ADVISOR_HIVEMIND.md first, then the files named. Answer with counterexamples and checks, mark
each claim's status, add one dated entry to the hivemind, and touch nothing else.

Context. The binding study's referee (research/BINDING-20261126-001/referee-R1/report.md) refuted "growth leaves
whole-held facts unbound": a built 30-knot start (three rings of five, each ring knot two loose, connecting knots none)
binds at round 2 three disjoint cycles of round-1 fresh distinctions (tuples 000, 011, 101, 110), and the sampled
ten-knot start binds three path parities at round 3. The coordinator asks whether such a binding is MADE BY GROWTH or
is the sum of the knot laws read off the start.

What I computed (all in this directory):
- repro.py (my builder of the referee's starts, canonical engine forbid.grown, my readings), repro_explore.jsonl: the
  three preparations reproduce; and `analyse` adds an ORIGIN test: a carrier f on stage t is a function of the start's
  values on the allowed states iff f + (sum of stage laws) is supported on start distinctions (`old_representative`);
  then, by the refereed projection lemma (ordinary growth keeps the start's allowed states on its own distinctions),
  the carriers' joint values equal their representatives' joint values on the start's allowed states. Result on all
  three preparations and at rounds 2 and 3: every carrier has a representative (each ring's ten loose distinctions),
  the relation holds at the start, its sum is a sum of start laws; at the start the representatives are not class
  labels under the shortest changes in the 30-knot (detour) preparation, but are in the two 21-knot ones.
- repro_paths.py / repro_paths.json: the ten-knot path witness reproduces at round 3 (stage equals the referee's);
  origin the same (relation at the start; 9 of 10 start laws in it); under changes of at most five distinctions two of
  its three carriers are NOT class labels (the referee read only the shortest changes there).
- repro_cuts.py / repro_cuts.jsonl: the referee's cut construction; under both cuts one three-parent birth with no fresh
  distinction makes the relation at round 1 (8 tuples at the start, 4 after); ordinary growth leaves it free.
- origin_scan.py with origin_census.jsonl, origin_heldout.jsonl: on 11,802 census and 1,196 held-out stages (rounds 1
  to 3, ordinary parity), every allowed change that keeps all start values lies in the span H of the small changes,
  under both readings (so every class fact is a function of the start's values). built.py / built_explore.jsonl: the
  advisor's 14-knot start binds from round 0 by the start's laws (your earlier proposal); closing.py: implied iff a
  birth takes every loose distinction of its structure, exact on the census (this is the theorem of
  research/ERASURE-AND-CLOSING-SIGNS-20261121-001B/closing_law.md lines 9-25).

Questions.
1. Is the origin test right? Is "every carrier has a start representative and the relation holds on the start's
   allowed states" the correct reading of "the relation was in the start", independent of the representative chosen?
2. Prove or break: under ordinary parity growth, every allowed change that keeps all start distinctions fixed (Z_new)
   is a sum of shortest changes through each distinction (Z_new in H), at every round. If true, ordinary growth never
   makes a relation among class facts: every binding's relation is the start's, and growth only decides which start
   functions are class facts and gives them new carriers. Where might it fail (rounds past 3, implied births, double
   meetings, the second reading)? Give the smallest candidate counterexample you can.
3. The frozen predictions I intend (attack each): P1 on built ring families (R = 3, 4 rings; n = 4 to 7 knots; two
   attachment styles; direct or detour links; connecting knots with no loose) the per-ring carriers born in round t - 1
   bind at every round t >= 2 by one parity rule, each a class label read by no single knot under the shortest changes;
   P2 every binding found under ordinary growth has the start's relation (origin test); P3 controls: one loose
   distinction at one connecting knot removes the relation at every round; cutting the links leaves no binding; P4 the
   cuts make a relation the start did not have on the modified start; P5 under not-all-equal growth the same carriers
   take every tuple; P6 on fresh sampled starts of 9 to 12 knots, Z_new in H on every stage.
4. On the owner's rungs (repetition; a tower: facts of one layer, bound by a rule, make a next layer with the same
   property; recursion), which does this reach, and is the answer different for the cut law?
5. What would a relation made by ordinary growth itself look like, and what cheapest search would find one if any
   exists?
