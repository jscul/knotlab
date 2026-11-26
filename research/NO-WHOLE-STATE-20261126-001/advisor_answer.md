# Advisor's answer: rule R before the freeze

Three things should change before you freeze: prediction 3 is entailed, R1 is not the marker of overshoot, and R is not stable under growth. Your identity and both of your conclusions in question 1 hold.

Status marks: *read* = I opened the file at that line; *by hand* = argument, no run (I have no shell); *memory* = a literature citation I did not look up. Everything *by hand* is `unverified` until you run it. I write "sharing pattern" for the census's `sharing`: knots as points, distinctions as the pairs that hold them.

## 1. The identity and the two conclusions

- **The identity is right** (*by hand*). For involutions that pairwise commute or anticommute, a word with every letter twice equals (−1)^c·I. Bringing a letter's two copies together costs −1 per non-commuting letter that occurs once between them, and removing the pair leaves the other interleavings unchanged.
- **It needs each operator to square to +I.** `rule_R` guarantees this: the phase at `values_commute.py` line 93 is always 0 because bit i is never in z. For the 115 stored witnesses nothing in `check_witness` asserts it; add the assert.
- **A second form of c, worth adopting.** With the word written knot by knot, two distinctions with no common knot interleave exactly when their pairs cross in a drawing with the knots in a row. So c is the crossing count of that drawing.
  - Checks: four-knot closure 1; five-knot closure C(5,4) = 5, your stored c; the square (K3,3) 9.
  - Arkhipov's proof (already cited at README line 77) is this same crossing argument.
- **"R forces the closing value" at the four-knot closure: right** (*by hand*). The unheld pairs are exactly (A0,A1), (B0,B1), (C0,C1); c = 1 (only the pairs 02 and 13 interleave). The knots commute: knots that share have 2·2 − 2 = 2 non-commuting cross pairs.
- **"Independent ⇒ a state exists": right, and always true in your realisation** (*by hand*). Commuting Hermitian Pauli products with independent vectors generate no −I. In `rule_R` the X-parts are independent, so a product of a proper subset of knots is a nonempty cut and never a scalar. The flag at line 111 is therefore true for every connected pattern and tests nothing.
- **One caveat on wording.** At the five-knot closure and the square, every knot operator commutes with every value under R, so in an irreducible realisation the knots are signed identities. There "a state with the older knots even exists" depends on the realisation. At the four-knot closure it does not (place 23 fails to commute with exactly one of knot 0's places).
  - Test for a new column: knot u is central iff d_u − (number of ends of f that share with u) is even for every distinction f not at u.

## 2. The R3 system

- **The system and its reduction are right** (*read*, `rule_census.py` 42–64). Each unheld pair contributes to the knot pair's count once (the XOR at line 46 cannot be double-true for an unheld pair). The cost is constant on the solutions iff it lies in the row space, and the top-bit reduction decides that.
- **Nothing is missing on realisability or the state.** Any symmetric pattern is realised by the `rule_R` construction, and the cut argument above gives the state. Repeated meetings are handled by `held`.
- **But R3 cannot fail in the census** (*by hand*).
  - Row (u, v) is exactly the change in the crossing vector when knots u and v swap places in the row. So "odd unattainable" means the crossings can be removed by swaps.
  - Odd attainability passes to larger patterns (give the extra distinctions values that commute with everything) and to subdivisions (give both halves the same value).
  - It holds on K4 (the three pairings of four knots: every knot pair covered twice, one crossing) and on K2,3 (all six unheld pairs: even cover, three crossings).
  - So it holds on every pattern that is not outerplanar, and fails on every outerplanar one. A simple pattern with at least three places per holder is never outerplanar.
- **Where it does fail:** your two-reader pattern, a ring of four with two sharings doubled. *By hand:* the constraints give p = 0 for (b0,b1), and the cost is p alone, so odd is unattainable.
- **Check:** compare the R3 column with an outerplanarity test (no K4 or K2,3 minor) on the census plus a few outerplanar controls with repeated meetings.

## 3. Counterexamples to the working claim

**R1 holds, part counting differs.** Two four-knot closures sharing one knot: seven knots, twelve distinctions. It should be in the census, since `census.py` line 227 keeps every connected atlas graph with at least three places per holder.

- R1 holds (*by hand*): shared knot with a neighbour, 5·2 − 2 = 8; two neighbours on one side, 2·2 − 2 = 2; across sides, 3·3 − 1 = 8.
- Read the shared knot's six places; all commute. Closed part counting has one knot, so 32 words.
- The stabilised state also fixes the parity of each side's three places (the product of the four knots of one side), so 16 words.
- In general the two differ exactly where a product of knots has its cut inside the read set. For a simple pattern that means a knot whose removal disconnects it (*by hand*).
- Under R a commuting read set is only a knot's places or three distinctions held pairwise by three knots. On patterns with no such cut knot, the claim holds but says only "each knot's own law".

**R1 fails, part counting is still quantum.**

- *Trivially:* the six-knot prism with every sign even. R1 fails (two knots of a triangle: 2·2 − 1 = 3), and every part table is a marginal of the uniform whole.
- *With an odd sum:* the eight-knot closure. R1 fails, but your own check found R3 odd attainable. That choice gives a state whose single-knot statistics equal part counting (no cut knot).

**So R1 is not the marker.** The two-reader CHSH 4 is explained by R3 failing, not R1. The record's "no quantum state produces it" on the eight-knot closure (`FOUR-READINGS-…A/results.md` 90–94) depends on the readers' roles.

**Proposed marker (R4):** R3 with one more constraint: every unheld pair split across two readers must commute. R violates that by construction unless every cross-reader pair is held, as it is in the three-reader pattern.

**Scope caveat:** R3 and R4 cover only values that pairwise commute or anticommute. Failing them is not "no quantum model".

## 4. Prior work

- **Arkhipov 2012** (arXiv:1209.3819; you cite it): twice-held parity arrangements have a signed-identity reading iff the sharing pattern is nonplanar. Check: `nx.check_planarity` over the 173 should give exactly the 58 operator-negative types.
- **R holds exactly in Mermin's square and pentagram** (*by hand*, all pairs checked on the standard operators): two observables anticommute iff they share no context.
- **Nearest named constructions** (*memory*, verify before citing):
  - "commute iff on a common line" is the symplectic polar space picture of Pauli operators (Saniga and Planat, 2007);
  - the graph of non-commuting pairs is called the frustration or anticommutation graph; here it is the complement of the line graph of the sharing pattern (for the five-knot closure, the Petersen graph);
  - solution groups (Cleve–Mittal 2014; Cleve–Liu–Slofstra 2017) impose only "held pairs commute". R is one quotient of that group, not the group.
- **Kleitman 1970** (*memory*): the crossing parity of K_n for odd n, and of K_{m,n} for m and n both odd, is the same in every drawing. That is the order-freedom of R2.
- I know no name for the outerplanar statement in section 2.

## 5. The predictions

- **Prediction 3:** move it to "entailed" with the argument, and replace it with "R3 odd unattainable on the two-reader pattern and on outerplanar controls". Delete the "if R3 fails somewhere" reading for the census.
- **Prediction 2** can be derived before the run (*by hand*):
  - R1 with R2 odd: K6 (15 crossings), K7 (35), and a knot joined to all of K3,3 (27).
  - R1 with R2 even: K3,4 (18 crossings). It is nonplanar, so the census should mark it operator-positive. R disagrees with the stored witness there, which is worth a line.
- **Prediction 4** holds by hand: the two-reader knots 00 and 01 have one non-commuting cross pair, (b0, b1). Add its R3 result.
- **Prediction 1:** I cannot count it. The closed form to check `analyse` against, for simple patterns: R1 iff (d_u − 1)(d_v − 1) ≡ t for knots that share, and d_u·d_v ≡ t for knots that do not, t their common neighbours. For K_{m,n} it holds iff m or n is odd.
- **Cheap additions:**
  - a shuffle test (relabel knots and distinctions; R2 must not move where R1 holds);
  - the planarity column;
  - the central-knot column from section 1;
  - a cut-knot flag;
  - R4 on the record's eight-knot roles.

## 6. Is R native

**It is supplied, and as a stage-by-stage rule it contradicts growth** (*by hand*, on your fixture).

- Before the closing birth, the loose distinctions 2, 4, 5 are pairwise unheld, so R makes them non-commuting. The birth (2,4,5) then holds all three.
- A product of three pairwise non-commuting involutions squares to −I, so that knot has no parity.
- R can therefore only be read off the finished pattern ("some knot ever holds both"). That makes it a fact of the whole presentation, like closing itself.

**What would have to change:**

- Values would need an order of composition; the engines have only GF(2) sums (`freelib.py` 44–61, from my last answer).
- The implied test (`startlib.py` 48) would become "closing sum ≡ crossing parity" where R1 holds, and undefined where it fails.
- A126 (*read*, `ASSUMPTIONS.md` 3845–3848) would fail: an odd close forbids every old combination.

**Cheapest tests that it could be the model's own:**

1. The "reached" row of your tally. If R1 fails at reached types, R cannot be universal.
2. The shuffle test. Where R1 holds, the sign is free of the order of the closing sum. That is the one point where it escapes the reorder-sign line's stop ("the sign belongs to the supplied schedule").

## What a referee would press first

1. Prediction 3 being a consequence of the census's own restriction.
2. R1 offered as the marker of overshoot.
3. R changing at a birth.

**Hivemind:** one consultation entry added, `unverified` except the lines read. No standing fact added, since nothing here was run. Nothing touches the publication hold.
