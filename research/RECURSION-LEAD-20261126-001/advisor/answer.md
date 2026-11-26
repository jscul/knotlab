# The advisor's answer before the freeze

A colleague's view, checked before use; read in the repository. Model: claude-fable-5-2. [Question](question.md)

Everything below is `unverified` hand argument unless I name the lines I read. I took the growth rule from the referee's rebuild (`SECOND-CHECK-20261126-001/referee-R1/rebuild.py`, lines 38–73); I did not open `forbid.grow`, and I ran nothing.

**(2) The return is bookkeeping (this explains the rest).** A round joins two live knots that have a common neighbour (`rebuild.py` 40–52). On a ring, knots i and i + 2 get one birth with two shared and two fresh loose distinctions. With loose pinned, the only allowed changes of four distinctions are, for each start knot j, its two ring distinctions plus the two shared distinctions of the birth joining its neighbours. Anything else has n or five or more. So each exchanged knot is one start knot with its two loose replaced by that birth's pair, and neighbours share the ring distinction between them: the ring again.

In general, where every group is a pair:
- A start knot with k shared distinctions gives C(k,2) such changes.
- A shared distinction between knots with k and k′ is held by k + k′ − 2 exchanged knots.
- So pinned E∘G is the line graph of the start's shared pattern, read with shared distinctions as distinctions and pairs at one knot as knots.
- It is lawful only when k ≤ 2 along every shared distinction, and it is the start again only on rings (the classical fact that a connected graph equal to its line graph is a cycle).

This accounts for the exploration:
- **Trees and joined rings:** a knot with three shared distinctions puts a distinction in three exchanged knots.
- **Ring of 6:** knots 0, 2, 4 form one group of three, so the pair rule does not apply.
- **Ring of 4:** knots 0 and 2 have two common neighbours.

**(1) Counterexamples and checks.**
- **Chain of 5, two loose each:** by the rule it is lawful and gives a chain of 3 (loose 3, 2, 3), then a single knot with four loose, then nothing. This goes against "every tree: not lawful" if your 12 trees held no chain; it belongs in R3, not R1.
- **Ring of 6 with one loose each:** each knot is in one group only, so by this rule it should not stall. I get six changes of four distinctions, every distinction held twice: a six-knot start with four shared and no loose at each knot. Check this against "rings with one loose each stall".
- **Ring of 3, two loose each:** it should give a ring of 3 with one loose each, which then closes.
- **Mixed loose counts (say 2, 3, 2, 4, 2):** these map to the fixed ring, since the extra loose become one-parent births that lie in no pinned change. R3 should say "every loose count at least two".
- **Hung knot or a doubled shared distinction:** unlawful (three holders, or a two-place change), so no threat to R1.
- **R1:** I found no non-ring return; that is a search by hand, not a proof. Within 3 to 8 knots R1 can only mean n = 5, 7, 8, so name them.
- **R2:** free is unlawful at once whenever a grown knot keeps two loose (those two alone are an allowed change). R2 is only tested on grown stages where every knot keeps at most one; count those and report them apart. On the one-loose ring of 6, each fresh distinction lies in six five-distinction changes, so it is still unlawful.
- **`same`:** it checks loose counts and multiplicities (`fold.py` 27–38 read), which fixes a lawful start up to renaming. It silently drops distinctions with three holders, so it is safe only after `lawful`, as `recur.py` does.
- **Two gaps in `recur.py`:** it discards `missing` from `short_moves` (above `MAX_DIM` the search stops at six distinctions, `classes2.py` 51–57), and E forgets every distinction in no move. Record both counts.

**(3) Pinning from growth.** The ring's return needs only one sum per birth (its two fresh distinctions equal), not each value. An implied birth states a sum of loose values the present knots already force, and only when the piece closes; later rounds move the same need out to the newest births. Pinning amounts to reading the newest births without their fresh places, which the three-place floor forbids.

The one reading with nothing supplied is a closed piece: with no loose left, pinned and free coincide. A ring of 3 with one loose each closes into four knots pairwise sharing, and E of that is itself. I expect the six-knot pattern above and an eight-knot one to exchange into each other. Growth plays no part there, so it is not recursion either. Check whether `forbid.grown` returns the closed stage.

**(4) Names.** Pinned allowed changes are the cycle space of the knot graph, and the knot laws are its cut space. E makes checks out of the shortest cycles:
- **Moves span all cycles and each distinction lies in two:** the plane dual, which is the matroid dual (MacLane).
- **Otherwise:** the vertex–face dual of a two-dimensional cell complex (knots, distinctions, moves), the literature's homological code, with classes as its first homology. Lawfulness is the literature's surface condition, with loose distinctions as the boundary.
- **Free reading:** the code spanned by least-weight words of the dual code; I know no standard name.

In those words the grown odd ring is a Möbius band and the even one an annulus, which may be your odd/even split.

The hivemind entry is added.
