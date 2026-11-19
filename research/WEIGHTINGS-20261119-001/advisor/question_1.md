# Question for the advisor (WEIGHTINGS-20261119-001, before the freeze)

You have no tools. Answer only from this text, and say where you are unsure.

**Setting.** For the cheapest parity growth, four refereed proofs give the growth exactly as clusters of the relayed extended map
of joins, under (S0) no stall, (S3) no round-1 group of three, (S4) no two live knots with two common neighbours, and (S6′) at least
two loose distinctions. The growth class is read off piece by piece:
- a finished piece closes if alone, and relays (dimension 2) otherwise;
- a tree core with R chains has dimension R, where a chain comes from a leftover open place at a knot with exactly two open places
  (one chain), or one (two chains); three or more open places give a dead end;
- a bare single cycle (blocks of two, no pendants) has dimension 1;
- any other cycle grows exponentially.

Under SCALE-SHARE's weighting (uniform over labelled descriptions: knots of 3–5 places, any multiplicities, connected), stalls
dominate (45% → 93% from 5 to 20 knots), and in the proved class dimension 2 is 85% → 98% of growers, with three never seen (0 of
12,270). The owner's rule is that every random process is a weighting, and we ask what is typical under each. The question is
whether "two is typical" belongs to the growth or to that weighting.

**Proposed weightings** (frozen before any sample is classified):
1. **tree:** a uniform random labelled tree (Prüfer), every knot at the bare size max(3, shared + round-1 demand), no surplus.
   It never stalls, so it is the weighting where stalls do not dominate.
2. **tree+:** the same, plus r ~ Poisson(1) extra lines between uniformly random non-adjacent pairs, at bare sizes. It has cycles,
   mostly long.
3. **grow:** knots added one at a time (A106's suggested growth process). Each new knot has 3–5 places uniformly and shares one
   distinction with an existing knot chosen in proportion to its open places, and with probability 1/3 one more with a second.
   Places are fixed, so stalls can occur.

Sizes are n = 5, 6, 7, 8, 10, 12, 16, 20, with 2,000 independent samples each, and 30 in-class growers regrown per weighting at
n = 8 and 12.

**Questions.**
1. Are these honest contrasts to SCALE-SHARE's? Is any of them rigged towards or against "two"? Is something missing, for example
   a weighting by random pairing of places (configuration model), or bare sizes with random surplus?
2. From the theorem alone, predict per weighting:
   - the share in the proved class;
   - the dimension shares among in-class growers, including whether three or more, or exponential, becomes common (say above 10%)
     and from what size.

   In bare random trees, a ray comes from each leaf whose neighbour has degree 2, and the dimension is the most such leaves in one
   parity class, or 2 if a class has none.
3. Name the risky predictions to freeze, and the main trap in reading the table.
