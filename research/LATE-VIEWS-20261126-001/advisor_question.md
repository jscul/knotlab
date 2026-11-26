You are advising on how to predict, from a finite start alone, the late "view" of a deterministic growth. Be concrete;
at most 450 words; a numbered list. Do not praise.

Facts. The cheapest growth builds knots in rounds; inside a proved class the knots of round t are exactly the connected
clusters of t + 1 members of the universal cover (the "unrolled map") of a finite hypergraph-like "map of joins" (members:
the start's live knots, plus one leaf member per leftover loose distinction; groups: live knots that share a distinction
with one common knot). A birth's local type is (kind = join or offshoot, number of parents p, fresh distinctions f,
places = p + f); p is the number of members of the cluster whose removal leaves it connected, f is its demand (the
number of one-member extensions that will be clusters next round, at least 1 under the law used). Proved: dimension =
largest number of endless chains in one connected part (a relay counts two); counts on rings follow a lap-weight
generating function W(y), rate x with W(1/x) = 1.

Data. On every census start of up to five knots of dimension two, the late view (counts per round of each local type)
is: two-parent joins with f = 2 growing by a fixed slope, plus constants: one-parent offshoots (2, 3 or 4 a round),
sometimes a group of three and a (2, 3) join, or binomial-type joins from a block; slopes are 1, 2, 3, or 2^k for hub
families. These are not functions of simple round-1 statistics (e.g. the number of leftover distinctions after round
1 predicts neither the offshoot constant nor the slope).

Questions.
1. Is a typed transfer matrix (or typed lap-weight series) on the map of joins the right route to compute each type's
   count per round exactly from the start, i.e. typed cluster enumeration on a periodic tree-like cover? What is the
   simplest correct formulation, and where does it break (cycles, groups of three, blocks)?
2. A cheaper intermediate predictor to freeze first: e.g. "late offshoots per round = number of chain ends", "slope =
   number of endless chains in a part minus one" — what static quantities would you try, and how to define them on the
   map so that they are computable without growing?
3. What held-out test and stop rule would make a positive result meaningful rather than circular?
