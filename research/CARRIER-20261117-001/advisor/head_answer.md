[claude-code:unrecognized_model] {"model":"claude-fable-5-2","query_source":"sdk"}
**Verdict.** C* as literally stated is likely false, for a fixable reason. With the head and tail widened to neighbourhoods, I think the "only if" direction is true and provable by pumping. This is a sketch I have not checked against your definitions.

**(a) Only if**

- **Likeliest counterexample to the literal C\*:** a bond with a variable off the line. Take a line that carries two bits (a, b), with x reading a at the top, y reading b in O_v, and z reading a⊕b in a sibling orbit of O_v or a side child of A_1. Then {x, y, z} is a bond of 3, and nothing inside "ancestors ∪ O_v's subtree" need be constrained. Your finding 1 (children) and finding 2 (ancestors) are two cases of this; cousins and side children are the next ones. A second gap: if O_v is not a descendant of the top orbit, the bond passes through levels above k.
- **Repair:** take the head to be all orbits within d blocks of O_u in the tree of blocks, and the tail all orbits within e blocks of O_v.
- **Proof idea for the repaired statement:**
  1. A bond S of size ≤ c occupies ≤ c orbits; the tree they span has ≤ 2c segments with no occupied orbit inside.
  2. Across a segment, the projection onto S only sees a composition of block transfer relations (side subtrees quantified into feasible sets). These live in a finite monoid M, indexed by orbit type.
  3. On any segment longer than B = |M|·|types|, two prefixes share the same product and type. The factor u between them can be deleted or repeated any number of times without changing the projection onto S, so S stays a bond.
  4. Segments off the O_u–O_v path can be shortened freely. On the path, move length in units of B! from every long segment into the longest one (delete B!/|u| loops of one length, repeat a loop B!/|v| times). This keeps s exact, so there is no residue problem.
  5. The result is a bond at the same s with every segment but one of length ≤ K (a constant depending on B), so d, e ≤ cK.
- **So middle clusters can always be moved to an end.** A bounded family never needs one.
- **Where the sketch can break:**
  - Depth tiers below r0: feasible sets have not stabilised, so the tier must be part of the type.
  - The line to O_v is an arbitrary address word, not a periodic descent. The monoid argument covers this; eventual periodicity does not.

**(b) Growth**

- **A head adds nothing to a product hypothesis.** The head's lowest orbit A_d separates O_v from the rest of the head, so "head × O_v is a product" follows from "A_d × O_v is a product". In finding 2 the deeper pair projections never become products, so the head version fails there too.
- **The right hypothesis is weaker than product:** G(d, r) says no bond inside (d-neighbourhood of A) ∪ (d-neighbourhood of B) meets both, for every orbit A and descendant B at least r(d) levels below.
- **Growth then follows from the pumping normal form, not from splicing.** A bond of size c at s normalises to neighbourhoods of extent ≤ cK with gap ≥ s − 2cK. That contradicts G once s − 2cK ≥ r(cK). If r(d) ≤ ρd, then L ≥ s/((2+ρ)K), which is linear; a faster-growing r gives slower growth.
- **This also gives a dichotomy to test on the ten undecided patterns:** either a neighbourhood bond exists for some fixed (d, e), or G holds and the reach grows.

**(c) Word**

I propose **stem**: "the stem of depth d from O_u toward O_v". It fits the parent, child and subtree vocabulary and is not a word from a space of two or three dimensions.

- **Clashes:** none in `INTUITIONS.md` or `COMMON_VERBIAGE.md` (I searched both). In ordinary usage it clashes only with a word's stem.
- **Rejected:** "head" (8 uses in those files, and it pairs with list head/tail); "lineage" (2 uses, and it contains "line", which is heavily used); "trunk" (suggests the root).
- **If you adopt the neighbourhood repair,** the stem is no longer the right object. "The d-neighbourhood of O_u in the tree of blocks" needs no new word.
