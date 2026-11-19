# Knots touching twice: the identification on most of the census

Status: Proved

Ticket `DOUBLE-IDENT-20261119-001A`, 19 November 2026, by Claude, on the coordinator's go-ahead for `RELAY-IDENT-20261119-001#1`.
This extends `RING-IDENT-20261119-001A-P001`, `CHAIN-IDENT-20261119-001A-P001` and `RELAY-IDENT-20261119-001A-P001` from simple knot
graphs to knot graphs in which two knots may share several distinctions. The advisor checked the statement before the freeze, and
its points are folded in: the hypothesis on distinctions, the implied wording, the round-0 caveat, and reading the conditions with dead
knots. `machine_check.py` is a separate algorithm in the same task. **Refereed:** report R1, confirmed, no Block; its two points folded in
(the no-stall condition named, and the check's structural implied test justified by Lemma M(4)).

## Setting

A start is a set of knots with given places. Each distinction lies in one or two knots (the program's convention; a distinction in
three is not a start). K is the knot multigraph, with one line per shared distinction, and K̄ is its underlying simple graph.
- **Open and live.** For a knot k, open_k = places_k − (its shared distinctions, counted with multiplicity), and k is *live* when
  open_k ≥ 1.
- **Demand.** d_k is the number of round-1 groups containing k, computed among the live knots.

**The extended complex X⁺** is RELAY-IDENT's, read on these data:
- the live knots, with a block N_K̄(w) ∩ live for every knot w, live or not, that has at least two live neighbours;
- s_k = open_k − d_k pendant points per live knot, with R(open_k) rays on each;
- a relay point with two rays on each finite piece when there are two or more pieces.

A dead knot is never a point, but its block stays.

**The class.**
- (S3) No round-1 group of three or more among the live knots. Groups are formed with every knot, dead ones included, as a possible
  common neighbour.
- (S4) No two live knots have two common neighbours in K̄, live or not.
- (S6′) The start holds at least two loose distinctions.
- (S0) No stall: open_k ≥ d_k for every live knot. A start that stalls cannot make round 1; the census's 11,010 stalls are of this kind
  (named after referee R1).

K is connected; it need not be simple.

## Lemma M (what the growth reads)

From round 1 on, the growth reads a start only through two data:
- (i) for each knot w, live or not, its set of live K̄-neighbours;
- (ii) for each live knot, its open count.

Two starts with the same (i) and (ii) have isomorphic growths from round 1: the same junctions, parents and fresh counts round by
round. Absolute counts at round 0, such as the number of distinctions, also read the multiplicities, but nothing the theorems count
does.

*Proof.*
1. **Round 0.** Two junctions are neighbours when they share a distinction, a set relation, so multiplicity changes no neighbour set.
   - The live knots and their loose distinctions are given by (ii).
   - Swapping two loose distinctions of one knot, or two distinctions shared by the same two knots, is a symmetry of the
     presentation.
2. **Round 1.** Candidates (live knots with a common neighbour), valid sets, groups and offshoots depend only on the neighbour sets
   and the open counts. Each live knot gives one loose distinction to each of its groups, and which one is immaterial by the symmetry.
3. **Later rounds.** A new junction shares exactly one distinction with each parent: that parent's loose distinction, loose in no
   other junction. Its other distinctions are fresh. So from round 1 on every neighbour relation is a parent relation, and
   multiplicity never enters again.
4. **The implied test.** The growth's test is that a junction takes every loose distinction of the presentation. More precisely,
   the old part of a new junction, the distinctions it takes, is implied by the equations present. Then its fresh part is frozen,
   which is why the rule gives it no floor.
   - For a connected presentation in which every distinction lies in at most two junctions, the two readings agree. Summing the
     equations of a set S of junctions leaves S's loose distinctions and the distinctions S shares with junctions outside it, each
     once, whatever the multiplicities. So a sum consisting of loose distinctions only comes from S = every junction.
   - So the test depends only on counts. ∎

## Theorem 6 (the identification with multiple touches)

In the class, Theorems 1 and 4, and Theorem 5 for K̄ a tree, hold verbatim:
- round t's junctions are the clusters of t + 1 points of the relayed X⁺ (the orbits, where K̄ has cycles);
- parents are R*, and loose distinctions after birth are the boundary;
- a finite piece relays when there are two or more pieces, and closes when it is the only one.

A start holding a single loose distinction closes at round 1. Its one offshoot takes every loose distinction, so its old part is
implied, and it gets d = 0.

*Proof.* By Lemma M, the growth equals that of any start with the same data (i) and (ii). The proofs of RING-IDENT, CHAIN-IDENT and
RELAY-IDENT use only (i) and (ii), with three exceptions, each repaired here.
1. **Girth, components and pieces.** These are read on K̄ and X⁺.
   - A 4-cycle of I(X⁺) is two live knots with two common neighbours, against (S4).
   - A 6-cycle is three live knots pairwise in blocks N(w_1), N(w_2), N(w_3) with no common neighbour. Such a common neighbour would
     give two of them two common neighbours. So it is a valid round-1 set, against (S3).
   - Dead knots join live ones through their blocks, so pieces are components of X⁺, not of the graph induced on live knots.
2. **Dead knots.** For bare sizes CHAIN-IDENT noted that a dead knot has no candidate. Given places, a dead knot can be a common
   neighbour. It is then a block and never a point, which is how X⁺ is defined. No proof needed dead knots isolated, only that they
   are not points.
3. **(S6′).** For simple K at bare sizes, at least two loose distinctions was automatic. Here it is a hypothesis.
   - With one loose distinction, the start closes at round 1, as stated.
   - With exactly two loose distinctions on two live knots sharing a block (the advisor's example), the pair junction takes every
     loose distinction and is implied. Its demand is 0, since the piece {u, v} is finite and the only one. So the implied rule gives
     d = 0 = |∂|, which RELAY-IDENT's "a lone finite piece closes" already says.
   - Every other use of the implied test in the three proofs is either a case where both readings give d, or covered by RELAY-IDENT's
     invariant over pieces, which reads only counts. ∎

## Remark: what three shared distinctions do

Two knots A and B sharing m distinctions leave |A △ B| = places_A + places_B − 2m distinctions between them. What this does to the
start:
- **|A △ B| = 0** is a duplicate or a contradiction: the start has no loose distinction and does not grow.
- **|A △ B| = 1** freezes that distinction. If it is loose, this is the one-loose case. If it is shared with a third knot C, C holds a
  fixed value and acts as a knot with one place fewer.
- **|A △ B| = 2** ties the two distinctions, so the pair acts as a wire.

By Lemma M none of these changes the counts. They show only as dead knots, which lower their neighbours' open counts and act as pure
blocks, or as the one-loose closure. This is the advisor's analysis. In the census, three or four shared distinctions occur only in
these roles.

## Corollary 7 (the census's growth classes)

Ticket B (`experiments/DOUBLE-IDENT-20261119-001B/`) reads each arrangement's growth class off the relayed X⁺, piece by piece:
- a finite piece closes, or relays (dimension 2);
- a tree core with R rays has dimension R;
- a bare single cycle has dimension 1;
- any other cycle grows exponentially.

The start's class is the largest over its pieces. On every arrangement of the touch census in the class, this equals the measured
class (12,473 of 12,473).

## Validation

**`machine_check.py`.** Every one of the touch census's 26,441 arrangements is classified on the data Lemma M names. It grows with
GF(2) elimination off, using the structural implied test, which Lemma M(4) shows equals GF(2) implication here: every distinction
lies in at most two junctions, and the presentation is connected.

| Class | Arrangements | Result |
| --- | --- | --- |
| In the class | 11,512 | all agree with the relayed cover per round to t = 6, in (parents, fresh) |
| One loose distinction | 727 | all close at round 1 |
| No loose distinction | 234 | not compared |
| Outside (S3) or (S4) | 2,958 | not compared |
| Stall | 11,010 | not compared |

Of the 11,512 in the class, 11,075 have double touches.

**The advisor's risky outcomes did not occur.** It predicted mismatches, if any, in three places: two-loose pairs, live knots
joined only through dead knots, and a later junction taking every loose distinction. No mismatch appeared anywhere in the class, so
none of these went wrong where it occurs in the census.
