# Referee report COPIES-AND-MEETINGS-001-R1 (lean)

**Verdict: the timing theorem stands, proved exactly in both directions under both laws. It is a pace of shared descent, not a
speed limit on all influence. No Block, no correction.**

## 1. The timing theorem: proved

- **The definition.** At a complete cut, two live knots are one witnessed step apart when a present knot meets both, that is, they
  are a candidate pair. The distance d is the fewest such steps.
- **Upward (d(I(A), I(B)) ≤ d − 1).** Every candidate pair on a shortest route lies in a funded group, so it has a child.
  Consecutive children share a parent.
- **Downward (≥ d − 1).** The only witnesses between positive-age knots are their parents. So a next route of e steps lifts to an
  old route of at most e + 1 steps through common parents, since members of one group are pairwise candidates.
- **Both directions are proved,** so "exactly d parent steps to the first common descendant" holds on a funded, continuing growing
  end. Separate parts (d = ∞) never share a descendant.
- **The knot laws.** The argument uses only the groups and the continuing assumption, which are the same under parity and
  not-all-equal. Parity's sole closing birth is excluded by "continuing", as the note says.
- **Checked numerically** with the referee's own engine on random pairs of live knots in 300 random starts: d after one step
  equalled max(0, d − 1) on all 1,380 parity pairs and all 1,272 not-all-equal pairs.

## What it is a pace of (for the owner)

The theorem bounds when two families **first share a descendant**. It is not a bound on every way one part of the growth affects
another, and the note says so ("a change of start can also affect another part through the whole-stage funding or closing rule"):
- **Parity's closing rule is global.** A join closes only if it takes every loose distinction of the whole stage. So under parity
  a disconnected part of the growing end can change a fresh count at once. That is the refereed ORDINARY-DYNAMICS result. There is
  no conflict, because it is not parentage.
- **A stall is global under both laws.** One shortage anywhere stops the whole round.
- **Fresh counts read two steps around.** A child's demand depends on its siblings' parent sets. So a family's inclusive
  descendants can have their fresh counts changed one step before any common descendant exists. Pure families are protected, as
  the note proves.

So "the first pace of influence that follows from growth alone" should be worded as **the pace of shared descent**, with these
exceptions named.

## 2. The bound on repeated copies

- **The class it covers.** The identified class, where the fixed-map identification theorem holds: no first valid triple, no
  repeated pair witness, at least two loose distinctions and funded openings. Every knot there is an orbit of a connected set in
  the unrolled incidence.
- **Outside that class it covers only** one-knot releases and products that stay at three knots or fewer throughout.
- **The argument was read in outline.** A lasting packet of bounded width yields an infinite route in a locally finite tree (by a
  compactness choice). At a fixed launch width there are only finitely many repeating parent sequences and continuing chains. It
  is sound in outline; not checked line by line.

## 3. The 21-knot indirect influence (33 fresh instead of 34): not rebuilt

It occurs at release sizes far past affordable literal growth, and the study computes it through the identified map.

## How the work was split

- **The referee:** read `propagation.md`, `bounded.md` and `indirect.md`, and tested the transfer identity with its own engine
  (seconds, run directly).
- **No study code was run.**
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
