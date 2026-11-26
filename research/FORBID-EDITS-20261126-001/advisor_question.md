# The question to the advisor (26 November 2026), before the census was frozen

Please be a skeptical colleague; short answers. The design is in README.md below (pasted). Four things:

1. **Proof A2.** Is the parity argument right as stated (linear spaces V_xy = W ∩ (S_x × T_y); a reader's record
   support the same for either far setting; three relations force the fourth)? What does it need that growth might
   break (births whose distinctions belong to both readers; middle knots whose births change with one edit; a round
   that stalls)?
2. **A3 and the reading.** The excess in A3 comes from the law making the weighting of old states depend on both
   settings, with each setting pair's worlds counted equally. Is it fair to say this is not "conditioning on settings"
   (the settings are edits, not distinctions) but is measurement dependence, the post-selection mechanism? What should
   the report say plainly that it does not show? Is there a sharper known result I should cite (local post-selection
   with no-signalling complete records reaching 4)?
3. **The census.** Starts of three to five knots, at most 12 distinctions; edits E1 (one more loose distinction or not)
   and E2 (which of two holders gets it); laws A129, A130 and the ordinary count; knot laws not-all-equal and parity;
   weightings U and S; complete records as defined. Is this class big enough to contain a two-sided forbidding (each
   reader's edit making a join of three parents of its own)? What would you change before freezing (the record's
   definition, the readings, a third reader's placement)? Any trap in the "same distribution for either far setting"
   test when a round stalls in some settings and not others?
4. **Predictions.** My three expectations are at the end of the design. Would you predict differently, especially for
   not-all-equal under A129/A130 with complete records required to be unchanged? Give a number or a kind if you can.

# Free edits under joins that forbid

Epic `FORBID-EDITS-20261126-001`, under G18 (Comparing growth laws), at the coordinator's go-ahead after the owner asked
whether the quantum part is being worked on. A check by the thread; design written before the census; computed;
referee pending.

## The question

Under a growth law in which a later join can forbid a state the old knots allowed, with each reader's setting a free
local edit (not a distinction of the state), does any small start give (i) a four-correlation (CHSH) score above 2, or
(ii) a three-reader (Mermin) win above 3/4, while no reader's complete local record changes with another reader's
setting?

## What is known

- **Free readings are bounded.** If the settings only choose which reading is taken on one surviving structure, every
  surviving state answers all four questions, so CHSH ≤ 2 and no three-reader contradiction arises, under any law that
  forbids ([FORBIDDING-JOIN-20261120-001](../FORBIDDING-JOIN-20261120-001/decision.md), refereed). So the settings here
  must change the structure: they are edits.
- **Free edits under ordinary growth** give 9/4 on a built preparation of four starts with fixed addresses, but a sender
  that chooses whether to supply its visible shortage signals; the joint response was the all-or-none funding of a round
  ([WHOLE-STAGE-SETTINGS-20261120-001](../WHOLE-STAGE-SETTINGS-20261120-001/decision.md)).
- **The two forbidding laws** are registered: one fewer fresh distinction where the three-place floor allows (A129), and
  only the fresh distinctions the floor requires (A130). Under either, a join of three or more parents can receive no
  fresh distinction, and its knot law then rules out old combinations of its parents' given distinctions.

## A. What the weighting does (arguments, checked on small cases)

Weight every allowed state of each grown structure equally (**U**), one structure per setting pair. If every birth an
edit causes holds only the editing reader's own distinctions, the four tables take the form

  P(R_A, R_B | x, y) = Σ_λ μ(λ) α_x(λ_A, R_A) β_y(λ_B, R_B) / Z(x, y),

λ the old state, R_A Alice's complete record, α_x the number of her local completions (zero where her edit's join
forbids her old values). A join that forbids makes the weighting of the old states depend on both settings: the
hypothesis of Bell's theorem that the preparation does not depend on the settings fails here, by the law and not by
any reader sorting the states. (This is the literature's measurement dependence, the mechanism of post-selection models:
Pearle, *Physical Review D* 2, 1418, 1970; Gisin and Gisin, *Physics Letters A* 260, 323, 1999.) So:

- **A1.** Where no edit forbids and every old state keeps the same number of completions, the bound 2 holds (Bell).
- **A2 (parity, proved).** Under the parity knot law, with each reader's record a set of its own values and readings
  sums of them, if each reader's complete record has the same support for either far setting, then CHSH ≤ 2. Proof:
  every structure's allowed states form a linear space V_xy = W ∩ (S_x × T_y) (the old space W, each reader's own
  equations S_x, T_y; new local distinctions are coordinates of the reader's own space). A sum of a reader's values is
  constant or balanced on a linear space, so each correlation is 0 or ±1, and three ±1 force the fourth: for
  (α, β) ∈ V_11, the record conditions give (α, β′) ∈ V_10 and (α′, β) ∈ V_01, and their sum (α′, β′) lies in W with
  α′ ∈ S_0 and β′ ∈ T_0, hence in V_00, which carries the fourth relation. Checked by exhaustion on two values a reader
  ([`linear_two.py`](linear_two.py): best 2). Three readers: by exhaustion on one and on two values a reader, the best
  Mermin win is 3/4 ([`linear_three.py`](linear_three.py)); no proof yet.
- **A3 (no general bound).** Eight equally weighted worlds on Alice's values (p, q) and Bob's (r, s), allowed when
  q + s = p·r (mod 2); Alice's edit keeps her worlds with p = x, Bob's those with r = y; each reads its second value:
  CHSH = 4, and each reader's complete record has the same distribution for either far setting
  ([`pr_example.py`](pr_example.py)). So a law that forbids by settings can exceed even the quantum bound 2√2 without
  signalling. Whether not-all-equal growth from a small start does so is the census question.

## B. The census (frozen before it is run)

- **Starts.** Every connected start of three to five knots in the class of the earlier edit studies (each knot's
  distinctions: those it shares with others, at most two holders each, and its loose ones; at least three places a
  knot), shared multiplicities 1 or 2, loose counts 0 to 2, at most 12 distinctions, each counted once up to
  relabelling the knots.
- **Readers.** Two (three for the Mermin game) disjoint sets of holders, no holder of one reader meeting a holder of
  another. **E1:** one holder a reader; the setting is whether it receives one more loose distinction. **E2:** two
  holders a reader; the setting is which of them receives it (the earlier study's fixed addresses).
- **Laws.** One round of growth under A129 and A130 (the two forms), with the ordinary count as the control; knot laws
  not-all-equal and parity.
- **Readings.** The value of a fixed old loose distinction of the reader's (first) holder; under E2 also the value of
  the distinction its edit added.
- **Weightings.** U, and **S**: each old state that survives the setting pair weighted equally, its weight split equally
  over its completions (which removes the effect of not-all-equal completion counts and leaves only forbidding).
- **Read per placement and setting pair:** the four (eight) tables; the largest CHSH over the eight sign conventions
  (Mermin win over relabellings); whether each reader's single value and its complete record (every value of its
  holders and of births with one of its holders as a parent, and the shapes of those births) have the same distribution
  for either far setting; a round that stalls counts as a record (no births).
- **Kinds.** *Excess without signalling*: CHSH > 2 (Mermin > 3/4) with every complete record unchanged by far settings.
  *Excess with signalling*: some record changes. *No excess.*

**Stop rule (the coordinator's).** Stop at an excess without signalling that survives the change of form (A129 ↔ A130)
and of weighting (U ↔ S), or at a census that is clean of one. Any excess is checked again for its source: an excess
under the ordinary count is not the forbidding's.

## Expected (written before the census, before the advisor's review)

1. **Parity: no excess without signalling** under any law (A2). Three readers: none above 3/4.
2. **Not-all-equal, the ordinary count:** under S no excess (A1: nothing forbids); under U, excesses may appear, all with
   signalling (completion counts depend on far values, as in the earlier study's 12/689).
3. **Not-all-equal, A129 and A130:** forbidding happens only where an edit makes a join of three parents near a reader.
   Excesses with a single value unchanged may appear (not-all-equal states come in complementary pairs, so every
   single value is fair), but none with complete records unchanged: forbidding one reader's old values shifts the
   distribution of the far reader's other values. A clean census.

## Not shown, whatever the census gives

An excess here would be a weighting of worlds that the law makes depend on the settings, not a quantum state; the
class it lives in reaches 4 (A3), above the quantum bound, so the quantum value 2√2 is not singled out; and it says
nothing about physical entanglement.
