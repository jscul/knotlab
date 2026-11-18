You are a colleague reviewing a design before it is frozen. Attack the rule and the predictions; be concrete and terse.

Setting (from two finished studies, FRESH-COUNT and FIRST-KNOT, whose results you need not recheck): parity growth by a
complete-round joining rule (live junctions with a common neighbour are candidates; groups = maximal sets of >= 3 pairwise
candidates with no common neighbour, plus pairs in none; each junction gives a loose bit to each group; leftover loose bits become
one-parent junctions, "offshoots"; a junction in more groups than loose bits stalls the round). The fewest rule F gives each new
junction max(d, 3 - p, 1) fresh bits (d = next-round demand, p = parents), or 0 when d = 0 and its parity is implied. Known: under F
an offshoot of demand 1 starts a chain that never ends; an offshoot of demand 0 whose parity is not implied gets 2 fresh bits whose
two offshoots then have demand 1; no other surplus is ever given; later rounds never stall (counts >= demand), so stalls happen only
in round 1, where the start knots' sizes are fixed. Two touching knots grow two copies of N^2; m mutually touching knots of m + 1
places grow m-dimensionally (the m chains share one partner, the group of all m knots).

Census design: every connected arrangement of up to five parity knots of three to five places, each shared distinction in exactly
two knots (a multigraph on the knots with multiplicities, degree <= size; loose = size - degree), counted up to renaming: 3, 22, 154,
1,760 and 24,502 arrangements of 1 to 5 knots (26,441). Each grown under F for up to 30 rounds or 6,000 junctions. Measured dimension:
0 if it closes; otherwise k + 1 for the least k such that the k-th differences of junctions-per-round are constant and nonzero over
the last seven rounds (unsettled if none).

Frozen rule (the general form of the m-knot result, found after a read-out): call a chain birth an offshoot of demand 1 whose parent
is not itself a chain offshoot; group the births of one round by their demand-1 partner (a sibling pair of births, each the other's
partner, is one class of two). Rule: the dimension equals the largest class ever formed (0 if no birth).

Pilot (300 random arrangements of <= 4 knots): closed 69, stall 50, dimension 1: 37, 2: 141, 3: 2, 4: 1; the rule matched every
settled case.

Questions:
1. Is the rule right in general, or can chains born in different classes or rounds combine into a higher dimension (for example two
   N^2 classes in one piece, or a class of 2 meeting a later class of 2)? Give a counterexample arrangement if you can.
2. Is the dimension measurement sound for D <= 4 within 30 rounds / 6,000 junctions? Transients?
3. Predictions to freeze; sharpen: (P1) the rule holds on every settled arrangement; (P2) among growing arrangements, 2 is the most
   common dimension, and dimension >= 3 occurs in under 5% of all arrangements; (P3) the largest dimension is 4 (m mutually touching
   knots of m + 1 places needs m + 1 <= 5); (P4) every stall is in round 1; (P5) by number of knots, the share of dimension 2 among
   growing arrangements rises with the number of knots. What would you predict instead?
4. Is "typical" over distinct arrangements (uniform over isomorphism classes) a fair reading of "nothing chooses an arrangement", or
   should the census also weight by labelled count? I plan to report both.
