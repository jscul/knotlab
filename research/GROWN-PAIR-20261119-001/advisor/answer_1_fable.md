**Verdict:** sound in outline, and complete if you fix the five points under (1). I checked nothing in the repo; this is from your description only.

**(1) Soundness and completeness**
- **Bucketing:** Weisfeiler-Leman is an isomorphism invariant, so buckets lose nothing. Fix the iteration count, give "no bond path" its own label, and use a deterministic hash (not Python's salted `hash`).
- **Cost:** VF2 on complete labelled graphs can blow up on symmetric tables. Seed it with the refined colours as node labels, or use a canonical labelling (nauty) and skip pairwise tests.
- **Table versus history:** if the table depends on the growth history rather than the arrangement alone, one arrangement can carry two tables. Check this first, and report isomorphic arrangements with non-isomorphic tables as a separate finding.
- **Duplicates:** deduplicate arrangements by canonical form before pairing and keep every provenance (start, round, lineage). Otherwise one pair reached many ways inflates the count.
- **Discard rule:** the arrangement isomorphism must colour distinction versus junction as well as loose marks. If growth state holds more than the arrangement (pending joins, round parity), isomorphic arrangements can still grow differently, so compare that state too.
- **Starts:** a start is not reached by growth. Report start–start, start–grown and grown–grown separately, and flag same-lineage pairs; only grown–grown answers the question.
- **Small stages:** tables with few distinctions or all distances equal collide trivially. Report by size so these do not carry the headline.
- **Continuity:** the earlier result used the identity on named distinctions; "up to renaming" is weaker. Say so, and note which pairs also match under a shared naming.

**(2) Predictions** (rough guesses)
- At least one non-isomorphic pair at up to 14 junctions: about 70%. Renaming freedom and 100 times more stages favour it, and most hits are likely small or symmetric.
- At least one grown–grown pair with no table automorphisms: about 30%.
- Among stages where junctions meet once: about 35% for any pair, 15% for a symmetry-free one.
- The earlier rivals mostly stalled, which suggests the table pins reachable arrangements more tightly than legal ones.

**(3) States under the isomorphism**
As phrased it is not well defined: the isomorphisms form a coset φ₀·Aut(T₁), and the answer can vary across it. State it existentially:
- **States agree** if some table isomorphism φ carries S₁ onto S₂.
- **States differ** if none does.

This is independent of the representative. Decide it without enumerating the automorphisms by testing isomorphism of the combined structure, table plus state set. For parity laws the state set is the check-row space with constants, attached as extra coloured vertices.

Also report how many isomorphisms carry the states out of the total. Declare up front whether "same states" allows value flips per distinction or only renaming.