# No state of the whole: patterns read part by part, and values that need not commute

Epic `NO-WHOLE-STATE-20261126-001`, under G18, at the owner's request ("So are we able to challenge that assumption?
Could you look into that?"; then "Yes, let's continue on with that proposal"). It challenges two assumptions: that a
pattern must have a state of the whole (A126 and wherever a lawful start needs an allowed state), and the narrower one
the advisor found beneath it (`MISSING-PIECE-20261126-001`): that every two distinctions have a joint value even where
no knot holds both, in the literature's words that all values commute (register entry A295). The proposal under test is
the owner's (A294): keep the rule that any one view is consistent; drop the rule that all views fit one whole. The
canonical knot test and every existing record are untouched. Computed; the advisor consulted read-only in the
repository ([question](advisor_question.md), [answer](advisor_answer.md)); refereed (R1, below).

> **Refereed (R1, [report](referee-R1/report.md)): confirmed with fixes, no Block.** The odd fixture's 64 of 64, all 115
> operator witnesses and all 173 census rows under both weightings were rebuilt. **Narrowings:** values commuting is
> sufficient for the even closing sign, not necessary (R itself forces even at five reached types), and the reordering
> count holds for values whose swaps cost ±1; a knot that commutes with every value is a signed identity only after
> restriction to a common eigenspace (not in the full representation); R can be evaluated on each stage, and what the
> birth rules out is a *persistent* R (three old commutation signs change), not R as such; part counting reaching 4 does
> not show that only a state over non-commuting values can bound it, and a stabiliser state with measurements beyond
> products of values gives CHSH 14/5 with every probability a count out of 20, so a numerical excess does not mark a
> state as "not a count". **Not a block:** the even control matches 56 of 64 against one fixed target (the comparison
> changed its target with the sign); K3,4 is not reached (three of the five reached even types do admit odd
> signed-identity readings); which product fixes which triple in the 32-against-16 example; Arkhipov's proof contracts
> rather than swaps; the four-readings referee had already reported. The logged correction is upheld. Logged in
> `docs/CORRECTIONS.md`.

**Prior work.** The record read such wholes part by part from 20 to 23 November, and this study rests on it:
`FOUR-READINGS-20261120-001A` (closed parity patterns with one odd rule; which admit operator readings; which growth
reaches), `ERASURE-AND-CLOSING-SIGNS-20261121-001B` (growth forces the closing sign even) and
`REVIEW-LEADS-20261123-001A` (the operator test on parts met in growth). None of the three had been refereed; their
referees are running. No novelty is claimed for the readings below; what is new is said at each part.

## A. Reading a pattern part by part ([`parts.py`](parts.py))

A **part** is what one context reads: the distinctions read and the knots lying wholly among them (the *closed* rule);
the part is weighted by counting the states the part allows (counts within the part). A second rule, *open*, keeps
every knot that touches the read set and sums the unread distinctions.

| Pattern | Whole has an allowed state | Closed parts: every part allowed, overlaps agree | Score |
|---|---|---|---|
| Three readers: four parity knots on six distinctions, one odd (the literature's Mermin pattern, 1990) | no | yes, yes | 1 (a list of values: 3/4) |
| Nine distinctions, rows even, one column odd (the literature's Mermin–Peres square) | no | yes, yes | 1 |
| Two readers: four three-place knots, odd at one setting pair | no | yes, yes | CHSH 4 (a list of values: 2) |

So dropping the whole does what the owner's picture says: every view is clean and the views agree wherever they meet
(no reader can signal), yet no single list of values fits them all. Under the open rule the first two patterns have
parts with nothing allowed: the part rule is a scaffold and it matters. And with two readers part counting reaches CHSH
4, the no-signalling maximum, past the literature's quantum limit 2√2. Dropping the whole alone holds nothing below 4.

## B. Does growth reach such a pattern? ([`reach.py`](reach.py), [output](reach_out.txt))

Under even parity every pattern allows the all-zero state, so no parity pattern growth makes lacks a whole. Under
not-all-equal, a pattern whose distinctions have at most two holders and whose knots have three or more places always
allows a state (the forbidding-join study's survival proof), so a contradiction needs a join with no fresh distinction
together with a third holder. Sampled: 300 census starts (seed 20261126, uniform over the census), not-all-equal, the
recent line's engine, up to four rounds, under the forbidding laws one fewer (A129) and the arity floor (A130), each with
no take and the recorded takes. **In all 2,400 runs the whole kept an allowed state.** Joins with no fresh distinction
did occur and distinctions reached up to six holders, but no round ended without a state.

## C. The advisor's fixture: growth's smallest closure carries the three-reader contradiction ([`fixture.py`](fixture.py))

The ring of three knots (0,1,2), (1,3,4), (3,0,5), each with one loose distinction, grows one round by ordinary growth
under parity: one birth, the knot (2,4,5), with no fresh distinction, and the round closes the pattern. The result is
four knots on six distinctions with every two knots sharing exactly one: the holder pattern of the three-reader argument.
The three pairs that no knot holds together, (0,4), (1,5) and (2,3), are the three readers, each choosing one of its two
distinctions.

- **With the closing sign as growth makes it (even)** the whole allows the all-zero state and the readers' tables are
  the ordinary ones.
- **With the closing sign odd** the whole has no allowed state, every part read by the three readers is allowed, the
  parts agree on every overlap, and **all 64 probabilities equal the three-reader target** (each scored context uniform
  on the words of its knot's parity, each unscored context uniform on all eight).
- **Control:** at every scored triple the parity the other three knots imply is the opposite of the knot's own.

This is below the five-knot minimum of the 20 November census because that census asked for a stronger reading (each
knot's product a signed identity, no state needed), which the four-knot pattern lacks (part D).

## D. Is the even closing sign entailed, or assumed? ([`values_commute.py`](values_commute.py))

Read each distinction as an operator that squares to the identity, the places of one knot commuting (the census's signed
Pauli products). Write the closing sum knot by knot: every distinction occurs twice. Bringing each distinction's two
occurrences together costs a factor −1 for every pair that does not commute and whose occurrences interleave; call
their number c. So **the product of all the knots' operators is (−1)^c**, and the sum of the knots' signs is c mod 2.
With every value commuting, c = 0 and the closing sign is forced even: exactly the sum of parity rows over GF(2) that
every engine uses. Checked on the stored files:

1. **The stored five-knot witness** (every two of five knots sharing one distinction): the four older knots multiply to
   +I, the closing knot's places commute and its product is −I, and c = 5.
2. **All 115 stored operator witnesses:** the sum of the signs equals c mod 2 in every one, and every pair that does not
   commute is held by no common knot.
3. **The four-knot closure (part C) and the eight-knot closure** (the three-label subsets): both are planar in the
   literature's sense, so no reading with each knot a signed identity exists (Arkhipov, 2012; for the four-knot type the
   census stores a word reduction to I = −I in any dimension).
4. **The engines use only GF(2) rows** (`startlib.py`, `gf2`; `freelib.py`; the closing law's proof).

So **the even closing rule is entailed only by the assumption that values commute**; drop it and the closing sign is a
reordering cost. The advisor's version ("not entailed at the 79 operator-positive reached types, entailed at the rest")
is right for readings with each knot a signed identity, and too narrow once knots are read as conditions on one state:

- **Rule R:** two values commute exactly when some knot holds both. It is stated in holders alone. At the four-knot
  closure the knots' operators commute under R, a state with the three older knots even exists, and the closing value is
  then forced odd (c = 1): R is the literature's three-reader reading (Greenberger, Horne, Shimony and Zeilinger, 1990;
  Mermin, 1990) and the fixture's odd sign is what it forces, not a choice. No knot there commutes with every value, so
  the reading needs a state (it is not a list of signed identities). At the five-knot closure R also forces odd (c = 5),
  and there every knot commutes with every value (a signed-identity reading). At the eight-knot closure R's knot
  operators do not commute, so no state makes all eight definite under R.
- **The cost, counted another way** (the advisor's form, checked): with the closing sum written knot by knot, two
  distinctions held by no common knot interleave exactly when, in the literature's terms, their arcs cross in a one-page
  drawing with the knots in that order, so c is that drawing's crossing count.

**The fold link, plainly.** The advisor's sentence "the closing sign is the cost of reordering the closing sum, −1 per
pair that does not commute" **holds exactly**: it is an identity of operator products, checked at every stored witness and
at the fixture. What is only verbal is the step to the owner's idea of time as a fold: nothing in the model orders the
closing sum (the parity is the same for every order when the knots commute), and which pairs fail to commute is a rule
we supply (R or another), not one growth makes.

## E. Rule R over every closed pattern of the census ([`rule_census.py`](rule_census.py), [preregistration](preregistration.md), [output](rule_census_out.txt))

Frozen before the run, revised after the advisor's reading (its derivations became predictions); **all eight frozen
predictions held.** The census is the 20 November one: 173 closed, twice-held, simple, connected patterns with at least
three places per holder and at most seven knots; 121 of them are closed by ordinary growth from some lawful open start.

| Weighting | Set | Types | R: knots commute (R1) | R forces odd | R forces even | Odd attainable with some commutation choice (R3) |
|---|---|---:|---:|---:|---:|---:|
| one vote per type | all | 173 | 21 | 14 | 7 | 173 |
| one vote per type | reached by growth | 121 | 17 | 12 | 5 | 121 |
| one vote per type | reached, no signed-identity reading | 42 | 4 | 2 | 2 | 42 |
| one vote per labelled pattern | all | 238,811 | 3,425 | 1,165 | 2,260 | 238,811 |
| one vote per labelled pattern | reached by growth | 177,321 | 3,240 | 1,085 | 2,155 | 177,321 |

- **R forces an odd closing sign at 12 of the 121 reached types** (one vote per type), with no sign supplied. Two of
  them have no signed-identity reading and need a state: the four-knot closure of part C and the five-knot pattern on nine
  distinctions (every two of five knots sharing one, but one pair). R forces even at 5 reached types, among them
  types that do admit a signed-identity reading with an odd sign (K3,4, two groups of three and four with every cross pair
  sharing: R and the stored witness disagree there).
- **Where R1 fails** (152 of 173 types) R gives no state that makes every knot definite. So R is a rule for a small set
  of closures, not a law for every closed pattern.
- **An odd sum is attainable at all 173 types** under some choice of which unheld pairs fail to commute. This was
  entailed, not found: the constraints are the swaps of two knots in the order of the closing sum, so an odd sum is
  attainable exactly on patterns that are not outerplanar (the literature's term), and no census pattern is. The four
  outerplanar controls (rings of three, four and five knots with doubled meetings, a ring of four with tripled meetings)
  and the two-reader pattern of part A all fail it.
- **Checks.** R1 agrees with the advisor's closed form on all 173 types; "planar" equals "no signed-identity reading" on
  all 173 (Arkhipov's criterion against the stored verdicts); the forced sign never moved under 420 seeded relabellings
  (seed 20261127) where R1 holds; K6, K7 and one knot meeting all of K3,3 give R1 with an odd sign, K3,4 R1 with an even
  sign, as derived by hand.

## F. What would hold part-by-part patterns below 4?

- **Not part counting itself.** The two-reader pattern of part A reaches CHSH 4 with every part allowed and the parts
  agreeing. Dropping the whole and counting within parts fixes no bound below the no-signalling maximum.
- **What marks the overshoot is R3, not R1** (the advisor's correction of my working claim, checked). The two-reader
  pattern is outerplanar: no choice of values that pairwise commute or anticommute (held pairs commuting) makes all four
  knots definite on one state with the odd sum. Its parts' certainty is the literature's PR box (Popescu and Rohrlich,
  1994), which no quantum state gives. R1 fails on it too, but R1 also fails on the eight-knot closure, where a commutation
  choice from R3 still gives a state whose single-knot statistics equal part counting (by the advisor's argument; the
  record's two-reader table on that closure, with each reader reading a whole knot, has no quantum realisation, so the
  readers' roles decide), so R1 does not mark it.
- **Part counting is not always a state's counts.** On two four-knot closures sharing one knot, R1 holds, yet reading the
  shared knot's six places part counting allows 32 words and the state that R's signed knots fix allows 16: the product
  of one side's four knots constrains the shared knot's three places on that side, and part counting sees only single
  knots. So the part rule is a scaffold that matters: a part's laws must include every product of knots that falls inside
  it, and under R such products carry their reordering signs.
- **So the bound comes from a whole of another kind.** What keeps the literature's quantum patterns below 4 (Tsirelson,
  1980: 2√2) is one state over values that need not commute, not the absence of a whole. On the patterns read here the
  three-reader and square contradictions need only counts with R's signs (the literature's stabiliser fragment, which
  counting reproduces: Gottesman, 1998), and they are certainties, not probabilistic excesses. A CHSH excess between 2 and
  2√2 needs a state that is not a count. Not computed beyond the patterns named.

## G. Is rule R native? No: it changes at a birth

On the fixture, before the closing birth the loose distinctions 2, 4 and 5 sit in three different knots, so R makes
them pairwise non-commuting; the birth (2,4,5) then holds all three. A knot whose three values pairwise anticommute has
a product that squares to −1 (in the literature's terms, X·Y·Z = i), so it has no parity at all. Applied stage by stage, R
therefore forbids the very birth whose closure it would sign odd. R can only be read off the finished pattern ("some knot
ever holds both"): which values commute is then a fact of the whole presentation, as closing itself is. **Dropping the
state of the whole brings a whole back in another form: the finished pattern decides which values commute.** For R to be
the model's own, values would need an order of composition (the engines have only GF(2) sums), the implied test would
read "closing sum ≡ crossing parity" where R1 holds, and A126 would fail at an odd closing (an odd close forbids every
old combination).

## What this does not say

- That growth makes an odd closing: every engine closes even, and R as a growth-time rule contradicts the birth.
- That R is the right commutation rule: it is one rule in holders' terms beside the current one (all commute); R3 shows
  other choices exist on every census type.
- Anything past the census's size (seven knots, simple sharing) beyond the named controls and the eight-knot closure.
- That part counting with R gives quantum statistics for every context; only the patterns named were compared.

## Scaffolds

The part rule (closed: knots wholly inside the read set; open; and, after the advisor, products of knots inside it),
swapped: it decides whether parts are allowed and how many words a part allows. The census's restriction (simple
sharing, three places per holder, at most seven knots), unchanged; controls with repeated meetings added. The order of the
closing sum, swapped by the shuffle test: the forced sign does not depend on it where R1 holds. R itself, beside the
current rule and the free choice of R3. The readers of part C (the three pairs no knot holds together), not swapped. The
sampled starts of part B (seed 20261126, uniform over the census of three-to-five-knot starts).
