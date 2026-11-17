Before freezing a design and predictions I would like a colleague's check (gaps, a simpler exact test, which outcome you expect and
why). Please be concrete and brief (under 600 words).

Setting (as in the last two questions). Addressed not-all-equal patterns, a tree of blocks with finitely many orbit types. For the 13
patterns at issue (mutants of one census pattern), F[r] = all assignments for every 4-address type (so r0 = 0, no bottom-band effect,
and truncating the pattern anywhere is exact for projections above the cut), and L_N(3, s) is non-increasing in N. Types and children:
0->[1], 1->[2], 2->[3,4], 3->[2,5], 4->[6,7], 5->[8,7], 6->[4,4], 7->[7,7], 8->[5,5]; orbits of type >= 2 have 4 addresses. Level-3
orbits have types 3 and 4. Type 7 is self-similar. The saturated composite automaton has 88 states (threshold 5, period 2); on its
periodic part exactly two composites are not products, both type 7 -> type 7 (one per parity):
  x = 0000 -> z = 0000 only (even length; 1111 at odd), x = 1111 -> 1111 (0000 at odd);
  x in P = {0011, 1100} -> any z;  every other x -> any z except P.
So across a long stretch the only information carried is a class of a type-7 orbit, kappa in {Z0, Z1, P, Other}, with z in P => x in P,
and x constant => z constant. Readings: L = 3, 4, 5, 5, 6, 6 for s = 1..6 (exact), and for one of them exactly 7 at s = 7 and 8 (depth 12,
certified), by bonds spread along a 4-6-4-6 line (never type 7). Stems (top orbit + the lower orbit's 0-2 ancestors below the top + the
lower orbit) hold no bond of any size at s = 7, 8.

Argument I have: by the dichotomy (on each residue, eventually constant or linear), the reach is bounded iff some "mode bond" exists: a
bond whose part below a long member-free window is near v and whose window crossing is a type-7 line. Such a bond reads the class:
type I, the part above forces X = 0000 (X the type-7 orbit at the window's top) and one address of v is set to 1; type II, the part
above forces X notin P (e.g. two addresses of X unequal) and v's four addresses are set to 0011. The top member must be needed: without
it the part above must not force the condition.

Planned exact test: for X a type-7 orbit at level a = 4, 5, 6, build the real pattern truncated at level a + 1 outside X's subtree,
with X's subtree cut to one type-7 path of length L0 = 5 and 6 to a type-7 orbit V (side children kept as leaves, deeper parts dropped,
exact since F = all), and run the certified least-bond search for a bond with a member at level 3 and one in V, members restricted to
the region outside the path plus V. Any bond found has the same projection at every larger s of the same parity (same composite), so
it bounds L at every depth from s = a - 3 + L0 on: the 13 would be bounded. If no bond is found for any a <= 6 and truncation, that is
not a proof of growth; for that I would need a product test allowing the mode: show that no set above can force X's class with the top
member needed, for X at any level.

Questions: (a) Is the planned test exact and is the "bounded iff a mode bond exists" step right (it uses the dichotomy, which is not yet
refereed)? (b) Which outcome do you expect, given that stems found nothing and the least bonds at s = 7, 8 are chains of 7 along a
4-6 line, and why? (c) For the growth side, is there a finite argument: e.g. since the composite from a type-4 or type-5 parent into a
long type-7 line is a product (the mode at X is independent of everything above X's parent block), the top can affect X's class only
through X's parent's block, so "can the top force X's class" reduces to a finite question about one block and the top's reach to that
block, which itself grows? Is that sound, or does the bond's freedom to hold X's own addresses break it? (d) Anything you would predict
differently.
