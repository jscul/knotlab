['claude-fable-5-2']
**Short version:** largest degree is a reasonable states-only rule, but on rings D2 is forced by counting, so the planned freeze cannot tell "largest degree" from "the original choice". The pilot is also explained by a simpler variable than your hub guess. I am reasoning only from your text and do not know the growth rule's exact definition, so the growth claims below are conjectures to test.

## 1. Is largest degree the right invariant?

It is defensible, and there are two better ways to state it.

- **Points are states-only objects.** When G* is three-connected, its points are exactly the non-separating cocircuits of the cycle matroid (Tutte). These are the minimal parity checks whose removal leaves the rest connected. So "junction" and "junction size" can be read from the states without the graph.
- **Dropping the largest point gives the sparsest presentation.** Total places of the presentation that drops v is 2L − deg(v), with L the number of distinctions. So the rule is "among presentations with every distinction in at most two junctions, take the one with fewest places".
- **That phrasing survives twists.** A twist at a two-point cut moves lines between the two cut points and leaves every other star alone, so largest degree is not twist-invariant. Minimising total places over the whole twist class is still well defined, up to ties.

Two caveats to record:

- The rule is states-only only among graph presentations. Other bases of the check space present the same states; the sparsest of those is the stars minus the largest only if no non-star cut is smaller than a star. On a ring with out this holds: the cut around two adjacent four-place knots has 6 lines, against 4.
- Loose lines on one knot are parallel, so the states cannot tell them apart. A states-only growth must be unchanged when they are permuted; that is a cheap check.

## 2. Why do the other choices kill the eddy?

I do not have a proof. Your pilot fits a sharper pattern than "out touches every knot".

After dropping knot v, the loose distinctions are exactly v's lines. They sit on three junctions: one on each ring neighbour, and the rest on the hub. The rest is v's old loose count, 2 or 3.

| Dropped knot's old loose count | Loose lines on the hub | Pilot outcome |
|---|---|---|
| 2 (four-place knot) | 2 | makes 2 a round |
| 3 (the knot with the spare, or any five-place knot) | 3 | closes (5, 3, 3, 1) |

This matches all three rings. In the bare ring the rate is half the loose count for every choice: 10 gives 5 a round, 4 gives 2 a round. So the conjecture is that the growth class after a drop depends only on deg(v) and how v's lines are spread over its neighbours.

The drop cuts the supply of loose lines from 10–15 spread over five junctions to 4–5 concentrated on three. That may be the whole mechanism. Two tests separate it from your hub guess:

- **A knot with no loose line.** Drop another knot; the new hub then does not touch every junction. If the eddy still dies, "touches all" is not the cause.
- **A six-place knot in the ring.** Dropping it puts 4 loose lines on the hub. Record the outcome as a readout; I have no prediction.

## 3. Which of D1 to D3 is weakest?

**D2 is empty on rings.** Out's degree is Σ(sᵢ − 2), which exceeds sᵢ whenever the other knots have more than 2 loose lines in total. That holds for every ring you list, so D2 will pass whatever the growth does.

**D1 is the real claim but is confounded.** On rings the original choice is at once the largest point, the only point adjacent to all others, and the only choice leaving at least 2 loose lines on every junction. Every D1 instance is also the same shape, a ring plus one point joined to all of it.

**D3 is the only place the rule can fail.** As written it reports two frequencies and not their relation.

What I would add:

1. **Ties and inversions.** Include presentations where a knot ties or beats out: few loose lines plus a large internal junction, or knots sharing two lines. For example, five knots with doubled ring lines and loose counts 2, 1, 1, 1, 0 give out 5 against a six-place knot. If the original still grows exponentially there, the degree rule is refuted.
2. **Stratify D3.** Report class change conditional on whether the original is the unique largest point. Also report how many of the 300 are three-connected; elsewhere use the fewest-places rule over the twist class.
3. **Freeze the local conjecture.** State "the class after dropping v depends only on v's star" as a readout, with the six-place test.
4. **Fix the class criterion before the run.** Say how many rounds decide closed, constant per round or exponential, and run one size past it. The bare ring is linear under every choice, so say whether it counts as an eddy and whether a rate change counts as a class change.
