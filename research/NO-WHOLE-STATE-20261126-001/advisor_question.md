You are consulted read-only from the repository root. Read docs/ADVISOR_HIVEMIND.md first. I want counterexamples and
checks, not a verdict.

Context: epic NO-WHOLE-STATE-20261126-001 (research/NO-WHOLE-STATE-20261126-001/), challenging the assumption that a
pattern must have a state of the whole, and the narrower one your last answer named (research/MISSING-PIECE-20261126-001/
advisor_answer.md): every two distinctions have a joint value even where no knot holds both ("values commute").

Done so far (read the files):
- parts.py: part-by-part reading (a context's part = the knots wholly inside the read set, counted within the part).
  Three readers (Mermin pattern): certainty, overlaps agree. Square: certainty. Two readers, four three-place knots: CHSH 4.
- fixture.py: your B.5 fixture. The ring of three ((0,1,2),(1,3,4),(3,0,5)) grows one round to (2,4,5), no fresh
  distinction; with the closing sign odd, 64 of 64 probabilities match the three-reader target, overlaps agree, the whole
  has no allowed state; the control gives the opposite parity at every scored triple.
- values_commute.py: your cheapest test. The stored five-knot witness: older four +I, closing −I, places commute,
  reordering cost c = 5. All 115 stored positive witnesses satisfy sum of signs = c mod 2, and their non-commuting pairs
  are all held by no common knot. Four- and eight-knot closures: planar, no signed-identity Pauli reading. Then, reading
  knots as conditions on one state rather than identities, rule R (two values commute exactly when some knot holds both;
  realised as A_i = X_i Z^{j<i unheld}): at the four-knot closure the knot operators commute, a state with the three
  older knots even exists, and the closing value is forced odd (it is the literature's GHZ/Mermin reading); five-knot:
  forced odd; eight-knot: R's knot operators do not commute.
- rule_census.py + preregistration.md: a census of R over the 173 types, NOT yet run; I am about to freeze it.

Questions (answer each with a check or counterexample; mark each claim's status):
1. Is the identity "product of all knot operators = (−1)^c I, c = non-commuting pairs whose occurrences interleave in the
   closing sum" right as used, and is my conclusion "with older knots even, R forces the closing value" right at the
   four-knot closure? Is "older knot operators independent over GF(2) ⇒ a state making them all even exists" right?
2. rule_census.py's R3 linear system: is it the right condition for "some commutation choice gives an odd sum with all
   knots commuting"? Anything missing (realisability as Hermitian involutions, a state making the older knots even,
   repeated meetings)?
3. My working claim for the bound question: part counting (counts within the part) equals the statistics of the state
   stabilised by the signed knot operators exactly when R1 holds and the read places commute, so it stays at quantum
   values there and overshoots (CHSH 4) only where R1 fails. Find the counterexample: a pattern where R1 holds and part
   counting still differs from the stabiliser statistics (my closed-part rule counts single knots inside the read set, not
   products of knots whose cut lies inside it), or where R1 fails and part counting is still quantum.
4. Prior work: is R (anticommute exactly when no constraint holds both) a named construction in the literature
   (Mermin–Peres square, Arkhipov, solution groups, graph states, Kochen–Specker)? Cite once if so; I make no novelty claim.
5. Should any prediction in preregistration.md change before I freeze it? Is there a cheaper discriminator I am missing?
6. Is R native to the model or a supplied rule? Name what in the record (growth laws, the canonical test, A126) would
   have to change for R to be the model's own, and the cheapest test that it could be.
