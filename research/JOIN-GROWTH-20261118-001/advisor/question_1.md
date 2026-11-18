# Advisor question 1 (JOIN-GROWTH-20261118-001, before the freeze)

You are a colleague advising on a combinatorics study. Please give analysis, not encouragement: derivations, counter-readings,
predictions we can freeze and test, and anything that looks wrong.

## The growth (fixed, from earlier records)

Parity growth by a complete-round joining rule. A start is a set of parity constraints ("knots") on bits; a bit lies in at most
two constraints. Each round: the live junctions (constraints holding loose bits, i.e. bits in one constraint only) are joined.
Two live junctions are candidates when they have a common neighbour (neighbours share a bit). Groups are the maximal sets of
at least three pairwise candidates with no neighbour common to all, plus every candidate pair in no such set. Each live junction
gives one loose bit to each group containing it; every remaining loose bit gets a one-parent junction (an offshoot). Each new
junction then gets fresh bits by the "fewest" rule: its demand d (how many groups of the next round will contain it), raised to
make it at least a three-bit constraint (max(d, 3 − parents, 1)), except 0 when its parity is already implied. If some live
junction is in more groups than it has loose bits, the round stalls.

Known (proved in earlier records): a ring of five four-bit knots (consecutive knots share one bit; two loose bits each) grows
five junctions every round (an unrolled cylinder). Each extra loose bit on a ring knot (a "surplus distinction", our word; the
ring record said "spare") gives the cone above it one more independent direction per lap around the ring: for the ring of four
four-bit knots and one five-bit knot the junctions per round satisfy c(t) = c(t − 5) + c(t − 6) (rate the root of x^6 = x + 1),
via your earlier (v, S) model: junction = cylinder position v with a set S of lifts of the surplus bit's knot below v, round
h(v) + |S|. In general, with j surplus bits on a clean ring of n knots, c(t) = Σ_i C(j, i) c(t − n − i), rate root of
x^(n + j) = (1 + x)^j (a general proof is being written elsewhere; please don't redo it).

## This study: joins

We attach a second part to a ring knot r and ask whether each part keeps its own growth. A join raises the round-1 demand of r
and of its two ring neighbours (the new neighbour is a candidate of both through r), so the start must give them more bits or it
stalls in round 1. Our "bare" convention: every knot gets max(3, shared bits + round-1 demand) bits, plus any surplus bits we list.
(A consequence: any join at a ring knot needs a knot of at least five or six bits there, outside the earlier census's sizes 3–5,
which is why the census never saw these.)

Exact data (Berlekamp–Massey on 20–40 rounds; every recurrence below has at least twice its order in clean terms):

| Start (ring of five four-bit knots, bare, unless said) | Junctions per round, recurrence | Rate |
| --- | --- | --- |
| + a lone knot touching r (3 bits: 1 shared + 2 for its groups with r ± 1) | the counts of the ring with one surplus bit, shifted one round earlier exactly: x^6 = x + 1 | 1.1347 |
| same on a ring of seven | x^8 = x + 1 | 1.0970 |
| + two lone knots (on r and r + 2, or on r and r + 1) | x^7 = (1 + x)^2 (BM finds the factor x^5 − x^4 + x^2 − x − 1, or it times x^2 + x + 1) | 1.2628 |
| + lone knot on r and one surplus bit on r, or on r + 2 | x^7 = (1 + x)^2 | 1.2628 |
| + a lone knot with s surplus bits of its own, s = 1 | x^7 = x^2 + x + 1 | 1.2032 |
| s = 2 | x^8 = x^3 + x^2 + 2x + 1 | 1.2825 |
| s = 2, and one surplus bit on ring knot r + 1 | x^9 = (1 + x)(x^3 + x^2 + 2x + 1) | 1.3974 |
| s = 3, and one surplus bit on a ring neighbour of r | x^10 = (1 + x)(x^4 + (1 + x)^3) = x^5 + 2x^4 + 4x^3 + 6x^2 + 4x + 1 | 1.4771 |

Reading I propose: write y = 1/x. Each thing attached at a ring knot has a "delay series" F(y), and the rate solves the lap
equation y^n Π F_i(y) = 1. A surplus bit has F = 1 + y; a bare lone knot also F = 1 + y; a lone knot with s surplus bits has
F = 1 + y(1 + y)^s (I found this on s = 0, 1, 2; the s = 3 run, already computed, fits it and does not fit the other reading
F_s = F_(s−1) + y^2 F_(s−2), which also fits s ≤ 2). In words: the attached knot is one more direction (y) whose own surplus bits
are directions available only once it is taken. That suggests a recursive law F(node) = 1 + y Π F(children), "rules within
rules".

Growing parts (not finite):

| Start | Recurrence | Rate |
| --- | --- | --- |
| bare ring + two touching knots hanging from r (A touches r, B touches A; A 4 bits, B 3 bits: the floor gives B one surplus bit) | (x − 1)(x^6 − x^5 − x − 1), i.e. 1 − y = y^5 (1 + y): F = (1 + y)/(1 − y)? | 1.4196 |
| ring with one surplus bit on r, + A, B with surplus bits A: 1, B: 2 | (x^2 + 1)(x^8 − x^6 + x^4 − x^3 − 3x^2 − 3x − 1) | 1.4506 |
| same, A: 2, B: 2 | no recurrence of order ≤ 9 in 21 rounds; ratio 1.613–1.626, flat | ≈ 1.62 |
| ring of five four-bit knots (no surplus) + A, B with A: 2, B: 2 | none found in 24 rounds; ratio 1.512–1.517 | ≈ 1.515 |

Two rings of five four-bit knots joined by one shared bit (bare): counts 10, 14, 24, 42, 78, 154, 310, 638, 1346, 2888, 6278,
13822, 30776, 69168, 156748, 357928 (rounds 0 to 15). Ratios rise slowly: 2.06, 2.11, 2.15, 2.17, 2.20, 2.23, 2.25, 2.27, 2.28.
A fit log c = a + t log λ + α log t on rounds 9–15 gives λ ≈ 2.51, α ≈ −1.35 (residual 4e-4); a second join (other knots, other
surplus bits) gives λ ≈ 2.65, α ≈ −1.2. Two two-fold pieces (two pairs of touching knots) joined by one shared bit grow at most
two-dimensionally (junction counts by round), not four.

## Questions

1. Can you derive the lap equation from the (v, S) model: why does an attached part act as one multiplicative factor F(y) at its
   knot, independent of position (r, r + 1, r + 2 all gave the same), and why is a bare lone knot exactly a surplus bit one round
   early? Is F = 1 + y(1 + y)^s right, and what is the general law for a finite attached part (a tree of knots? a knot sharing two
   bits with r? two lone knots on the same ring knot? a knot touching two ring knots, which makes a second cycle)?
2. The growing attached parts: derive F for the hanging pair (is it (1 + y)/(1 − y)?), and predict the two that BM did not settle
   (A: 2, B: 2 with and without the ring's own surplus bit).
3. Two joined rings: is the growth series algebraic rather than rational (a square-root branch point, c(t) ~ C λ^t t^(−3/2)), as a
   system F_1 = G(y, F_2), F_2 = G(y, F_1) would give? Can you predict λ for the bare pair of five-rings (≈ 2.5?) and say what the
   general rule is (two rings of lengths n, m; with surplus bits; a ring of three rings)? A model we could compute to many rounds
   would be the most useful thing you could give.
4. What should we freeze? We want a test set disjoint from the data above: other ring lengths, other attached parts, several
   attachments, and two rings, with exact recurrences or rates predicted in advance. Which predictions are sharp and which risky?
5. Words: the program avoids words from a two- or three-dimensional world for its own objects (no "surface", "edge", "pendant" if
   it reads as spatial). We currently say "attached part", "delay series", "lap equation". Better choices?

Please be concrete; formulas we can check by computer are best.
