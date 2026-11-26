# The second question to the advisor (26 November 2026), before the report

Short, skeptical answers please. The study (README.md, pasted below) has run. Results: the census of every start up to
five knots and 3,000 sampled starts of six to eight knots, one round, under both forbidding laws and the ordinary count,
both knot laws, both weightings: no placement where forbidding answers both readers' settings (one side only: up to 72
placements per law); no CHSH above 2 and no Mermin win above 3/4 anywhere, with or without signalling; not-all-equal's
largest CHSH on placements that split is 0.159, its Mermin win 1/2; parity reaches exactly 2 and 3/4 (perfectly
correlated chains). Built starts (two one-sided cases joined through one shared distinction between knots holding
nothing loose; 81 under the one-fewer law, every one answering both settings and splitting): CHSH below 0.001, old-value
correlations below 4e-4.

I added A4 (see the README): when nothing depends on both settings, the tables are a local model with local rejection.
I want to tell the owner: (1) the forbidding route, with settings as local edits, can give at most a detection-loophole
excess, never entanglement in Bell's sense; (2) in the starts read it gives none at all; (3) any nonnegative weighting of
co-real worlds with responses that split gives a local or local-rejection model, so the quantum part needs either a
joint response that does not signal (a contact or a whole-round event, which so far signals) or weights that can cancel
(signed or complex weights, which the program has so far supplied by hand); cite Spekkens, PRL 101, 020401 (2008),
negativity and contextuality, once.

1. Is (1)-(3) right and fairly worded? What would you strike or qualify?
2. Is "the class is too small to test the two-sided question" still the right verdict after the built starts, or is it
   fair to call the line closed (an obstruction learned) given A4?
3. One next direction you would rank first, with a first step.

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
- **A2 (parity, proved; wording fixed after the advisor's review).** Under the parity knot law, when the structure's
  equations split into the old ones W (no setting), Alice's own S_x and Bob's own T_y (each touching only that reader's
  record coordinates, new local distinctions included), with readings sums of a reader's own values: if each reader's
  complete record has the same support for either far setting, then CHSH ≤ 2. Proof: the allowed states of each
  structure form V_xy = W ∩ (S_x × T_y), closed under sums of three points. A sum of a reader's values is constant or
  balanced on such a space, so each correlation is 0 or ±1, and any three constant relations force the fourth: for
  any (α, β) ∈ V_11, the record conditions give (α, β′) ∈ V_10 and (α′, β) ∈ V_01, and the sum of the three points,
  (α′, β′), lies in W with α′ ∈ S_0 and β′ ∈ T_0, so in V_00; the relations on V_00, V_01 and V_10 then give
  a_1(α) = b_0(β′) = a_0(α′) = b_1(β) at every point of V_11. U and S agree under parity (every surviving state has the
  same number of completions). Checked by exhaustion on two values a reader ([`linear_two.py`](linear_two.py): best
  2). Three readers: by exhaustion on one and two values a reader the best Mermin win is 3/4
  ([`linear_three.py`](linear_three.py)); no proof yet. What growth can break is the split: a birth with parents of
  two readers (then a + b = x·y, the literature's PR box, is linear), a birth of the middle that changes with one edit,
  or a round that stalls. Each shows in the census as a placement that does not split.
- **A3 (no general bound).** Eight equally weighted worlds on Alice's values (p, q) and Bob's (r, s), allowed when
  q + s = p·r (mod 2); Alice's edit keeps her worlds with p = x, Bob's those with r = y; each reads its second value:
  CHSH = 4, and each reader's complete record has the same distribution for either far setting
  ([`pr_example.py`](pr_example.py)). So a law that forbids by settings can exceed even the quantum bound 2√2 without
  signalling. The three-reader form ([`pr_three.py`](pr_three.py)) wins the Mermin game with certainty, every one- and
  two-reader record unchanged. This is the literature's "guess your own setting" model of the detection loophole: a
  local model with local rejection. Its bound is CHSH ≤ 4/η − 2 for a local survival fraction η (Branciard, *Physical
  Review A* 83, 032123, 2011, cited from the advisor; to check), which A3 meets at η = 1/2. Whether not-all-equal growth
  from a small start does any of this is the census question.

- **A4 (forbidding that splits is local rejection; written after the pre-count).** When no birth and no stall
  depends on both readers' settings, the tables under U or S are P(R_A, R_B | x, y) = Σ_λ μ(λ) α_x(λ, R_A)
  β_y(λ, R_B) / Z(x, y): a hidden variable λ (the preparation) that does not depend on the settings, and responses
  that each depend on one setting and λ, with rejection (α or β zero) where a join forbids. That is the literature's
  local model with local rejection, exactly the detection loophole's form. So on placements that split, no forbidding
  law can give more than such a model gives: it can exceed 2 only by rejection, and then nothing in it is nonlocal.
  A joint response needs a birth or a stall that depends on both settings, which is a contact between the readers or
  a whole-round event (the earlier study's 9/4 came from the stall).

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
- **Weightings.** The preparation is the start's allowed states, kept through the edits (the start's knots stay in
  force beside the edited ones, the earlier edit study's primary population), so an edit alone moves no weight and only
  growth can. Then U (every allowed state of the grown structure equally) and **S** (every surviving state of the edited
  start equally, its weight split over its completions: this removes the effect of not-all-equal completion counts and
  leaves only forbidding).
- **Read per placement and setting pair:** the four (eight) tables; the largest CHSH over the eight sign conventions
  (Mermin win over relabellings); whether each reader's single value and its complete record (every value of its
  holders and of births with one of its holders as a parent, with the shapes of those births, named from the reader's
  own side) have the same joint distribution for every far setting; the surviving fraction per setting pair.
- **Kinds.** *Shared birth*: a birth with parents of two readers (a contact between them; no tables). *No allowed
  state* in some setting pair (dropping it would be post-selection; no tables). *Does not split*: the round's status, or
  a birth with no reader parent, changes with the settings. Then, among the rest: *excess without signalling*,
  CHSH > 2 (Mermin > 3/4) with every complete record unchanged; *excess with signalling*; *no excess*. Any excess is
  checked against 4/η − 2.
- **Order (the advisor's).** First a structural pre-count with no tables: per law and kind of edit, the placements
  where an edit makes a join with no fresh distinction that removes old states, on one reader's side or on both. If no
  placement forbids on both sides, the class is too small to test the question: say so, not "a clean census", and
  extend the class (larger starts sampled under a named weighting, or a built start recorded as a scaffold).

**Stop rule (the coordinator's).** Stop at an excess without signalling that survives the change of form (A129 ↔ A130)
and of weighting (U ↔ S), or at a census that is clean of one. Any excess is checked again for its source: an excess
under the ordinary count is not the forbidding's.

## The pre-count of the census, and the extension

[`tally_count.py`](tally_count.py) on `count_E1`, `count_E2`, `count_M1` (all 7,075 starts of three to five knots):

| edit | placements read (each law) | shared birth | a reader holder has nothing loose to read | old states removed somewhere: A129 / A130 / ordinary | on both readers' sides |
|---|---|---|---|---|---|
| E1 | 3,901 | 3,587 | 16,629 | 12 / 14 / 0 | 0 |
| E2 | 946 | 736 | 2,686 | 0 / 14 / 0 | 0 |
| M1 (three readers) | 150 | 450 | 1,066 | 0 / 0 / 0 | 0 |

The same under both knot laws. Most placements read stall in every setting pair (E1: 2,944 of 3,901), since one short
knot stalls the round. **No placement forbids on both sides: the class is too small to test the question** (the
advisor's expectation), so per the order above the census is not called clean. Its tables are still computed, as
controls for expectations 1 and 2.

**The extension (frozen before its pre-count was read).** Starts of 6, 7 and 8 knots, 1,000 of each, drawn with
replacement under a named weighting (`sampled()` in [`forbid.py`](forbid.py), seeds 20261132, 20261133, 20261134): each
pair of knots meets with probability 1/3, multiplicity 1 or 2 equally, loose counts 0, 1 or 2 equally; a draw is kept
when connected with three places a knot and at most 18 distinctions. Every placement of E1 and M1; for E2 the first 80
reader choices of an order shuffled with seed 20261126 plus the start's index. New flag: whether each reader's own
setting changes the joins with no fresh distinction on its side while old states are removed (*forbidding that answers
the reader's setting*), and whether that holds for every reader. Tables are computed where it holds on at least one
side, and on all placements of the first 200 starts of each size as controls.

## Expected (written before the census; the advisor's predictions follow)

1. **Parity: no excess without signalling** under any law (A2). Three readers: none above 3/4.
2. **Not-all-equal, the ordinary count:** under S no excess (A1: nothing forbids); under U, excesses may appear, all with
   signalling (completion counts depend on far values, as in the earlier study's 12/689).
3. **Not-all-equal, A129 and A130:** forbidding happens only where an edit makes a join of three parents near a reader.
   Excesses with a single value unchanged may appear (not-all-equal states come in complementary pairs, so every
   single value is fair), but none with complete records unchanged: forbidding one reader's old values shifts the
   distribution of the far reader's other values. A clean census.

**The advisor** ([question](advisor_question.md), [answer](advisor_answer.md)) agrees on 1 and 2, and on 3 expects zero
excesses without signalling in three to five knots "mostly by vacuity": few or no placements forbid on both sides.
Where forbidding is one-sided, it expects excesses with every single value fair and the complete record changed,
between 2 and about 5/2; an excess without signalling in a larger class must respect 4/η − 2 (about 10/3 for a
not-all-equal join that removes a quarter of the weight).

## Not shown, whatever the census gives

An excess here would be a weighting of worlds that the law makes depend on the settings, not a quantum state. Every
table in this class has a local model with local rejection, so nothing in it is nonlocal: Bell's theorem is not beaten,
its hypothesis (a preparation that does not depend on the settings) fails. Counting each setting pair's worlds
separately is itself a choice of weighting. The mechanism, read as discarded runs, is the detection loophole that
experiments closed in 2015; it survives here only read as worlds that never exist, which is nearer the literature's
retrocausal or all-at-once models. The class reaches 4 (A3), above the quantum bound, so 2√2 is not singled out; and
nothing here bears on physical entanglement.
