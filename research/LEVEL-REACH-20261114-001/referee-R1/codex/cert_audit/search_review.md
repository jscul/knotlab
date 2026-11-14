# Review of the fresh referee search

No logical defect found in the reviewed versions of `fresh_pattern.py` and
`fresh_search.py`. Exact source hashes and controls are recorded in
`search_review_controls.json`. This is a same-task review of the lead's fresh
code, separate from the retained-certificate audit.

The builder applies each word right to left through the previous independent
referee's MSB-first state actions, appends the term letter as the new last
letter, applies the declared address-to-id map, excludes over-depth terms,
and deduplicates triples of distinct ids. Its direct implementation and the
certificate lane's independently written placement implementation agree on
128 descriptions/depth comparisons from the sample plan.

The existence compiler's factor for variable v permits state zero unless the
state-one selector is chosen, and permits state one unless the state-zero
selector is chosen. Thus selecting both permits neither state. Each knot
factor permits exactly the six NAE assignments. Bucket elimination conjoins
all factors sharing an eliminated variable and disjoins its two values; the
remaining factor therefore expresses exactly the existence of a completion.
Both Boolean gate encodings are equivalences, with correct constant and
complement simplifications. The master forces that existence output false.

The master disallows contradictory selectors, equates presence with either
selector, requires a top and target member, and counts presence variables.
`-rhs[k]` from `ITotalizer` imposes at most k selected members. An accepted
candidate is additionally checked against the original formula and every
maximal proper projection. Complement symmetry permits checking the half of
assignments whose first supported variable is zero, because the original
formula consists only of NAE knots and has been shown alive.

Component restriction is sound: an alive formula's state relation is the
product of its constraint-component relations, and any minimally nonfull
support lies in one component. A knot that misses one designated set cannot
be contained in a cross bond, so the native-support blocks are sound. The
later nonfull-support blocks require the ascending-cardinality invariant:
all cross bonds of smaller cardinality would already have been found before
that bound was exhausted. Shrinking a nonfull proper subset reaches a bond;
if that bond met both designated sets, it would contradict the already
exhausted smaller bound. Thus the added block cannot discard a still-unseen
cross bond. This reasoning depends on keeping the ascending-size loop and
the projection checks intact.

Independent controls exhausted all four dual-rail choices per variable on
50 tiny NAE formulas, totaling 61,568 complete selector assignments, and
tested both possible circuit output values. Another ten formulas reached
seven variables for the search checks. The search matched independent brute
relation/support enumeration in 712 endpoint, cap and member-restriction
comparisons, including dead, disconnected, absence and numeric outcomes.
Returned witnesses were separately tested for forbiddenness and minimality.
Flipping the root and flipping one actual gate literal were both detected.

Limits: the code trusts the SAT solver's answers and does not export an
independently checked refutation for every exhausted master query. The
controls establish the tested finite boundary, not a universal theorem of
the implementation. Deadline checks occur between original-formula SAT
calls; an individual such solve is not interrupted, so the query limit is a
soft wall-clock envelope. Compiler width/gate/time failures return
`undecided`, and do not establish absence.
