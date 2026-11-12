# How common folding is among random samples: pre-registration

Epic `COMMON-FOLD-20261112-001` (`ACROSS-FOLD-20261112-001` direction 1; G17 with G1, question 9; program topology, group spacing),
2026-11-12, at the owner's go-ahead ("Sure, do that", relayed by the coordinator). Committed before either registered run. The
canonical K1–K3 test is unchanged. The advisor model (Fable 5.2) was consulted on the design before freezing, under the owner's rule
of 2026-11-12; what it changed is listed below.

## Words

The guide's glossary (`publication/knotlab/INTUITIONS.md`, "Glossary") is the reference: distinction, knot, base, bond, bond
distance, steps apart, periodic, unlengthened shift, along-count, sample, weighting, outcome, tie class, last base. In this record:

- **Knot kind.** Three offsets in ℤ² up to translation; a periodic base has a not-all-equal knot on z + k for every z in ℤ² and every
  kind k it holds (the literature's periodic 3-uniform hypergraph). The kinds used here are the 171 whose offsets fit the box
  [0, 2] × [−2, 2].
- **Tied along t.** Every distinction is tied to its translate by t (the glossary's tie), so to its translate by every multiple of t:
  bond distance 1 at every number of steps along t.
- **Travels along t.** A pattern p on a finite set A forces the same pattern, or its complement, on A + t. It then forces it on
  A + kt for every k (the law and the base are unchanged by the shift, and not-all-equal by complementing every value).
- **Global influence along a shift.** Tied or travelling along some shift: a bounded set whose values decide a distinction
  arbitrarily many steps away. The owner's "globally influential" (2026-11-12) is read this way on periodic bases (A75 below).
- **Travelling base.** A base with a pattern travelling along some shift and tied along none of the shifts searched: what base 16
  has. (The owner's word for what this epic counts is folding, kept for his structure; the record's unlengthened shift is what a
  travelling base has.)

## The question

The owner: base 16 is one sample nobody chose; meeting patterns "can fold in immensely complex ways and can be kind of globally
influential". Is global influence along a shift, and a travelling base in particular, typical or rare among random periodic bases, under a
declared weighting, and how does it change with the number of knot kinds (each distinction lies in 3r knots)? On random finite
samples, where every distinction is within a few steps of every other, how much of a base does the value of a pair or a knot decide,
and how much of that is ties, local propagation, or search?

## The question in standard terms

For random periodic 3-uniform hypergraphs on ℤ² with r edge orbits under not-all-equal (proper 2-colouring), the probability, among
the 2-colourable ones, that some finite pattern forces its own translate (a deterministic direction for a finite pattern), and that a
single vertex forces its translate; and for random 3-uniform hypergraphs grown to non-2-colourability, the size and
graph-distance profile of the backbone under conditioning on an edge or a pair.

## Prior work (bounded search, 2026-11-12)

- **Known.** Random ℤ^d shifts of finite type (McGoff and Pavlov, J. Mod. Dyn. 10, 2016; arXiv 1408.4086) with random forbidden
  blocks: emptiness, entropy and periodic points; finite orbits (Broderick, arXiv 1506.02600). Deterministic and expansive directions
  of two-dimensional shifts of finite type (Boyle and Lind 1997; Zinoviadis, arXiv 1603.05464; a subshift deterministic in every
  direction is finite, arXiv 2301.06868). Failure of strong irreducibility and block gluing (Boyle, Pavlov and Schraudner 2010) and
  of topological strong spatial mixing (Briceño). Backbones and frozen variables in random constraint problems (Monasson et al. 1999;
  Achlioptas and Coja-Oghlan; Molloy; for not-all-equal Ding, Sly and Sun), reconstruction (Montanari, Restrepo and Tetali 2011).
- **Not found.** How often a small random family of not-all-equal knot kinds gives a pattern that forces its own translate, or a
  shift along which every distinction is tied to its translate; the backbone of a pair at the last base of uniform growth split into ties, propagation and search.
- **Sibling census.** `RANDOM-FATES-20261112-001` measures ties, tie reach and bonds of four at 3 steps on the same growth
  processes (and, exactly, bonds on newest-four patterns). The forced set of a pair or knot here sits next to those and is a
  different measure; ties are subtracted to report what a set forces beyond them. Its frozen library `fates.py` is imported, pinned by
  sha256 72d3571ed66dddaa6c517b3ce29ce14ae72c008c025669e2ef071b77b73eba35, with seeds 50000 and up (growth) and 60000 and up (reading),
  disjoint from its seeds.

## What is settled by definition or by proof (checks, not predictions)

- **Degree.** Every distinction of a base with r kinds lies in exactly 3r knots.
- **Travelling gives bonds at unbounded steps (lemma).** If p on A forces σ(p) on A + t, then by the shift and complement symmetry it
  forces it on A + kt, so p forces the value at a + kt for every a in A and k ≥ 1. If A is free, every minimal constrained subset of
  A ∪ {a + kt} contains a + kt, and it meets A because a single distinction is never constrained under not-all-equal; so some bond of at
  most |A| + 1 distinctions holds a + kt and a member of A (which member may depend on k). Steps apart grow linearly in k, so bond
  distance is bounded along t: an unlengthened shift.
- **Tied along t gives ties at every multiple of t** (the same argument with |A| = 1).
- **Nested prefixes.** A sample's bases at r = 1 to 8 are the first r kinds of one random order, so a contradiction at r stays one
  at every larger r (checked). Certificates are not monotone: a free set or an extendable pattern can be lost when a kind is added;
  the census counts how often.
- **The tree control** (ticket B): with no cycle of knots, a pair forces at most the third distinction of its own knot (when equal)
  and a knot's values force nothing else. A violation is a bug.
- **The last base** (ticket B): the three distinctions of the knot that ends the growth are equal in every state of the last base,
  so they lie in one tie class by construction (as in `RANDOM-FATES-20261112-001`).
- **The control base** (ticket A): base 16 must travel (its three-distinction column, along the unlengthened shift) and be tied along
  no listed shift.

## Disclosed before freezing

Pilots outside the registered seeds (seeds 1, 2 and 900 to 939 for ticket A; 0 to 2 and 900 to 901 for ticket B; code in the
session's scratchpad and the frozen code itself on seeds 900 to 939):

- **Ticket A, first pilot** (before ties along a shift were separated): a travelling pattern in 0 of 60 bases at r = 1, rising to about nine in
  ten of the non-contradictions at r = 8. The advisor model pointed out that near contradiction bases may simply be tied along a shift;
  separating that changed the picture.
- **Ticket A, frozen code on seeds 900 to 939** (40 samples): among bases, a travelling base in 0, 0, 4, 10, 11, 3, 0, 0 at
  r = 1 to 8, and tied along a listed shift in 0, 0, 2, 6, 11, 19, 15, 12; contradictions 0, 0, 0, 2, 8, 14, 22, 26 of 40;
  unsettled none; travelling found but not certified by doubly periodic states in 0 to 5 per r. Runtime 103 s on 8 workers.
- **Ticket B** (frozen code, seeds 900 and 901): at half and three quarters of uniform growth a pair forces about one distinction, at
  one step, by propagation; at the last base it forces 68 to 80 per cent of all distinctions, of which all but 1 to 2 per cent are
  ties of the pair's own members, and less than 0.5 per cent by propagation. The tree control forces only the third of the pair's own
  knot.

The predictions below are informed by these pilots: they test whether the picture holds on fresh seeds and more samples.

## Ticket A: travelling and tied bases among random periodic bases (frozen in `experiments/COMMON-FOLD-20261112-001A/`)

**Weighting W(r).** Sample i (i = 0 to 199) is one uniform random order of the 171 kinds (seed 50000 + i); its base at r is the first
r kinds. So each r has the uniform weighting over r-sets of kinds, counted per presentation (bases equal up to a change of basis of ℤ²
or a reflection count separately; the number of classes under the box's four reflections is reported).

**Readings** (each certificate sound): contradiction (no state on a 15 × 19 window); base (a doubly periodic state for periods (P, 0)
and (s, Q), P, Q ≤ 8 axis-parallel or P, Q ≤ 6 sheared); otherwise unsettled. Tied along t for the ten shifts t of `SHIFTS` (window
SAT). Travels along t: A of 2 to 4 cells of the box [0, 1] × [0, 2] holding (0, 0), any pattern, the ten shifts, σ either; certified
when p with σ(p) on A + t is carried by a doubly periodic state and A is free (every pattern carried). The lattice the kinds span
(rank, index) is recorded, and rates are also given on index 1. Wilson 95% intervals throughout. A classification is a lower bound on
global influence: within the searched family F (these sets, shifts and window), never beyond it.

**Predictions.**
- **A1, rare at few kinds.** At r = 1 no base is tied along a shift or travels (0 of 200). At r = 2 the rate of travelling bases
  among bases has a Wilson upper bound below 10%.
- **A2, travelling bases peak in the middle.** The rate of travelling bases among bases is largest at r = 4 or r = 5, with a point estimate of at least 20%
  and a Wilson lower bound of at least 10% there.
- **A3, ties near contradiction.** Bases tied along a shift are at least half of the bases at r = 6 and beyond (Wilson lower bound at
  least 40% at r = 6), and travelling bases at most 20% of the bases at r = 7 and r = 8.
- **A4, global influence typical with many kinds.** Tied or travelling bases are at least 70% of the bases at r ≥ 6.
- **A5, contradictions.** Contradictions are at least 40% of the samples at r = 8, and never decrease along prefixes (a check).
- **A6, the search family.** In the sensitivity part (samples 0 to 49 at r = 2, 3, 4; A of 2 to 4 cells in [0, 2] × [0, 2], twelve
  shifts with entries up to 2, window 21 × 25), the rate of travelling bases among bases rises by at most 10 percentage points at each r.

**Failure criteria.** A1 fails if any r = 1 base is tied along a shift or travels, or r = 2's upper bound reaches 10%; A2 fails if the rates at r = 4 and r = 5 are both below 15%, or the peak lies elsewhere; A3 fails
if tied bases are below half at r = 6; A4 fails if global influence is below 70% at some r ≥ 6; A6 fails if the larger family lifts a
rate by more than 10 points (the search family was the limit, and the rates must be reported as such). The census is
uninterpretable at an r where more than 20% of the samples are unsettled.

## Ticket B: global influence on random finite samples (exploratory, frozen in `experiments/COMMON-FOLD-20261112-001B/`)

**Samples.** Uniform growth U(n) for n = 100, 200, 400, 20 runs each, grown until it ends; the tree control, 20 runs of 300 moves.
Stages: half and three quarters of the last base's knots, and the last base. Readings as in the census's docstring: forced fraction,
beyond ties, by propagation, reach and shell profile, for 20 co-knotted pairs and 20 knots per base.

**Predictions** (exploratory; the rest is measured):
- **B1 (check).** The tree control: a pair's reach is at most 1 and a knot's pattern forces nothing.
- **B2.** At half and three quarters, the mean forced fraction of a pair is at most 2% of the distinctions, for every n.
- **B3.** At the last base, the mean forced fraction of a pair is at least 50% for n = 100, 200 and 400.
- **B4.** At the last base, the mean fraction forced beyond ties and the mean fraction forced by propagation are each at most 5%.

**Failure criteria.** B2 fails if influence before the end is not local; B3 fails at some n (then the last base's global influence
shrinks with size); B4 fails if pairs decide much beyond their members' ties, or if the global influence is propagated locally rather
than found by search.

## Decision rules

- **A1 to A4 hold:** under W(r), travelling bases are rare with few kinds, common (a fifth to a third of the bases) in the middle,
  and give way to ties along a shift near contradiction, while global influence along a shift becomes typical as each distinction joins more knots. Base 16
  (r = 2) is then a rare sample of a kind that is common at r = 4 to 5.
- **A2 fails:** travelling bases are rare at every r under this weighting; base 16 is atypical.
- **B2 to B4 hold:** in finite random samples, influence is local until the last few knots, and at the last base it is global but
  made of ties found only by search.
- Either way, rates are stated with the weighting, the search family and the interval.

## Workspace assumptions

- **Relied on.** A64, A67, A71 (each random process is one weighting of many).
- **Added (to be entered at close, numbered then).** A75: on periodic bases the owner's "globally influential" is read as ties or
  travelling along a shift; on finite samples, as the forced fraction of a small set.

## Changed by the advisor's critique

Ties along a shift separated from travelling (the confound above); nested prefixes, so contradictions are monotone along each sample; the
freeness of the travelling set and complement symmetry made explicit in the lemma; lattice index and reflection classes recorded;
rates reported both over bases and over bases plus unsettled; a sensitivity part with a larger family; and for finite samples the
split into ties, propagation and search, with a shell profile instead of reach alone. The advisor also proposed an exact
point-to-set measure and model counting; these are left out for cost and recorded as possible follow-ups.

## Stop rule

One registered run of each ticket and of the sensitivity part; then the decision note and a hand-off to the referee thread; report
and move on.

## Runtime

Ticket A: about 10 minutes on 8 workers, the sensitivity part about 20; ticket B about 15. Registered in `docs/LONG_RUNNING.md` and
run under `systemd-run --user -p MemoryMax=16G -p MemorySwapMax=0`.
