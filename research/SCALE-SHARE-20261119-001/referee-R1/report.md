# Referee report SCALE-SHARE-001-R1 (fresh code; the study's chains regenerated as data)

**Verdict: confirmed, with one Narrowing and one improved check. No Block.**
- **The sampler is uniform over labelled descriptions.**
  - Its moves are symmetric. The referee proved them irreducible, and checked that exhaustively at three, four and five knots.
  - Chains started from paths and from dense rings agree.
  - The referee's own fresh sampler gives the same shares.
- **The five-knot check is better than reported.** `merge.py` compares the sample with stale census shares. Against the exact
  labelled shares, χ² is 4.3, not 10.3.
- **P3's stepwise scorer passes, and the note's "failed" is the right reading.** The rate falls 0.017 from ten to twenty knots,
  seven standard errors, in three steps that are each under the scorer's 0.01.
- **The Narrowing.** The cluster rule has a second break, from six knots (addendum to the referee's CLUSTER-ALL report).
  - It occurs once in the study's own 64,000 samples, at seven knots, where the rule calls it a ring. **That sample does not grow
    exponentially.** So the seven-knot ring share (0.01%) is a false ring.
  - Every other ring in the sample, and every three- and four-dimensional sample, grows as the rule says.
  - The shares stand. "Rings stay rare" is, if anything, stronger.

## 1. The sampler's uniformity and irreducibility (the owner's first point)

**Symmetry.** `scale.chain` makes one of two moves:
- with probability 0.7, a uniform pair and a uniform ±1 on its multiplicity;
- with probability 0.3, a uniform knot and a uniform ±1 on its size.

A move is kept when the result is in S_n: sizes 3 to 5, each knot's shared count at most its size, connected. The proposal
probability does not depend on the state and is the same in both directions. So Metropolis with a uniform target accepts every
legal move, and the stationary law is uniform on the class it explores. Rejections make the chain aperiodic.

**Irreducibility, for every n** (the referee's argument):
1. Raise every size to 5. That is always legal.
2. Remove multiplicities down to a spanning tree of the support. Connectivity holds, since the tree stays.
3. Any tree with degrees at most 5 reaches any other through leaf moves. A leaf move attaches a leaf to another vertex of degree
   at most 4, then cuts the leaf's old line. Each intermediate graph is a tree plus one line, so it is connected, with degrees at
   most 5.
   - Shortening the shortest leg at a branch vertex, onto another leaf, ends at a path.
   - Paths reach each other by end rotations (move the end leaf to the other end).
   - Adjacent swaps reach every relabelling: move q₁ onto q₃, then q₂ onto q₁.
4. From the target's spanning tree, add the target's other lines. Each intermediate graph is a subgraph of the target, so its
   degrees stay within the sizes. Then lower the sizes.
5. Every move is reversible, so S_n is one class.

**Exhaustively** (`referee_scale_irreducible.json`): with sizes 5, the multigraphs form one class under the multiplicity moves at
n = 3, 4 and 5 (53, 1,302 and 52,665 multigraphs). |S_5| = 2,590,792 labelled descriptions.

**Mixing** (`referee_scale_chains.json`, per chain, from the recorded classes):
- **Starts agree.** The four path-started and four dense-started chains agree within noise at every n. For example, the non-stall
  share is 0.216 against 0.225 at ten knots and 0.071 against 0.066 at twenty.
- **The between-chain spread** implies effective sample sizes of 5,800 to 23,000 per 8,000 samples. With eight chains this is a
  rough figure, but it is consistent with nearly independent thinned samples.

**An independent sampler** (`referee_scale_mine.json`) was written fresh: the same target and moves, a random-tree start, its
own random streams, 16 chains × 1,000. The rule's classifier (read-only) classified the samples.

| Knots | Non-stall, referee (± SE) | Non-stall, study | Exact |
| --- | --- | --- | --- |
| 5 | 0.5591 ± 0.0039 | 0.5516 | **0.5599** |
| 10 | 0.2306 ± 0.0035 | 0.2205 | — |
| 20 | 0.0665 ± 0.0024 | 0.0680 | — |

The class shares agree similarly. The largest difference is two combined standard errors (non-stall and dimension 1 at ten
knots).

## 2. The five-knot check

`referee_scale_exact5.json`. The exact labelled shares at five knots were computed from the complete census:
- every five-knot arrangement, weighted by 5!/|Aut| with the referee's own brute-force automorphism count;
- the total checks: 2,590,792 = |S_5|;
- each arrangement classified by the rule.

| Class | Exact labelled share | `merge.py`'s reference | Study's sample | z (between-chain SE) |
| --- | --- | --- | --- | --- |
| stall | **0.4402** | 0.436 | 0.4484 | 2.5 |
| closes | **0.1212** | 0.125 | 0.1194 | −0.6 |
| dimension 1 | **0.0792** | 0.081 | 0.0740 | −1.7 |
| dimension 2 | **0.3551** | 0.358 | 0.3529 | −0.4 |

**Against the exact shares, χ² = 4.3 on the four classes, not 10.3.** The reference in `merge.py` dates from before the census's
last 200 arrangements were read. The sample agrees with the measure.

## 3. P3's stepwise reading (the owner's second point)

`merge.py` passes P3 when no step from one n to the next (10→12, 12→16, 16→20) falls by more than 0.01.

| | Rate −ln(non-stall)/n | Per-chain SE |
| --- | --- | --- |
| 10 knots | 0.1512 | 0.0016 |
| 12 | 0.1450 | 0.0024 |
| 16 | 0.1400 | 0.0021 |
| 20 | 0.1344 | 0.0016 |

- **The steps** are −0.006, −0.005 and −0.006: each within 0.01, so the frozen scorer says "held".
- **The fall from ten to twenty** is 0.0168 ± 0.0023: seven standard errors.
- **The frozen text** says the rate "does not fall from n = 10 to 20 (by more than 0.01)". Read as a statement about the range,
  it fails.
- **The note reports "failed" and discloses the scorer's pass.** That is the right reading, and the stricter one. A stepwise test
  with a per-step tolerance cannot see a steady fall made of small steps. **No correction.** If the count "7 of 10" is quoted, it
  should keep the note's sentence that the frozen scorer passed P3.

## 4. The rule's scope at scale, and the false ring

**Spot checks one size past the study** (`referee_scale_spot.json`). The study grew samples at six to twelve knots. The referee
took non-stalled samples from its own chains and grew them 20 rounds with its own engine (FIRST-KNOT-R1, exact GF(2) implication),
against the rule:

| Knots | Grown | Equal at every round | Out of scope | Misses |
| --- | --- | --- | --- | --- |
| 10 | 1,200 | 1,187 | 13 | 0 |
| 12 | 1,200 | 1,189 | 10 | 1: the six-knot break shape (a four-knot block with one pair unlinked) |
| **16** | 1,200 | 1,197 | 2 | **1: a new shape** |

- **The new shape** (`referee_scale_new_shape.json`, `referee_scale_spot_misses.json`). A two-knot block and two first-round groups
  of three form a cycle of blocks, each pair sharing one knot.
  - At 16 knots the growth is 16, 6, 6, 7, 8, …, two-dimensional. The rule gives 16, 6, 8, 11, 15, 20, 27, … and **calls it a
    ring**.
  - The study's own grower (joinlib's `grow`, run read-only) agrees with the referee's counts.
  - The same shape fails at six knots, both ways (a false ring, and a closing start read as dimension 1); see the addendum to the
    referee's CLUSTER-ALL report.

**The study's own samples** (`regen_study.py`, `referee_scale_regen.json`). The 64 chains were regenerated with `scale.chain`,
run read-only only to regenerate the study's data. **Every chain's classes equal the recorded ones.**
- **The new shape occurs once in 64,000 samples, at seven knots.** The rule calls it a ring. The referee's growth reads 7, 8, 9,
  10, 11, 13, 15, 17, 19, 21, …, against the rule's 7, 8, 13, 25, 54, 126, …. **The seven-knot "ring" (0.01%) is false.**
- **The other four rings** (two at five knots, one each at six and twelve) equal the referee's growth for 25 rounds.
- **All 43 samples of dimension 3 or more equal the referee's growth for 40 rounds** (`referee_scale_regen_rare.json`). Their
  measured dimensions are 2.87 to 3.03, and 3.91 for the one four-dimensional sample.

**What changes.**
- **The shares do not move beyond sampling error.** The new shape is about 0.02% of non-stalled starts in the referee's chains.
- **Narrowed:**
  - "The rule's scope holds … the six-knot break shape: one sample in 8,000 at six knots, none at any other size." A second break
    shape exists in scope, and the study's seven-knot sample holds one.
  - "Exponential growth, a ring, is at most 0.1% of growers at every size" stands, since the one false ring only inflated it.
    Rings in the sample: two at five knots, one at six, one at twelve.

## Corrections for the owner (listed, not folded in)

1. **The rule's scope at scale.** The second break of the cluster rule (two first-round groups of three in a cycle of blocks; the
   referee's CLUSTER-ALL addendum, fd3d07eac) occurs once in the study's samples, at seven knots, misclassified as a ring. The
   seven-knot ring share (0.01%) is false. No other class changes. **Narrowing; not a block.**
2. **The five-knot sampler check.** `merge.py`'s reference shares are stale. Against the exact labelled shares from the complete
   census, χ² = 4.3 on four classes (10.3 against the stale ones). "Near agreement, not exact" can be stated as agreement. **Not a
   block (an improved check).**

## How the work was split

- **The referee:**
  - read `scale_share.md`, the pre-registration, `scale.py`, `job.py` and `merge.py`;
  - wrote `referee_scale.py` (irreducible, exact5, chains, mine, spot), `spot_misses.py`, `scan_cycles.py`,
    `hyper_cycle_search.py`, `hyper_cycle_small.py`, `new_shape.py`, `regen_study.py` and `regen_rare.py`.
- **Read-only:**
  - `scale.classify`, the rule's classifier, as the object the shares are read with;
  - `scale.chain`, only to regenerate the study's own samples, checked against the recorded classes;
  - joinlib's `grow`, as a labelled cross-check of the referee's growth on the new shape.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
