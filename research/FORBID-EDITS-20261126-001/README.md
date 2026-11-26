# Free edits under joins that forbid

Epic `FORBID-EDITS-20261126-001`, under G18 (Comparing growth laws), at the coordinator's go-ahead after the owner asked
whether the quantum part is being worked on. A check by the thread; design written before the census; computed;
referee pending.


> **Refereed (R1, [report](referee-R1/report.md)): confirmed with fixes, one Block.** The parity proof, the two examples and
> every score stand (no archived score above its classical bound; 212 census and extension rows and 32 contact rows
> rebuilt with independent code). **Block:** the census's "splits" flag does not establish A4's hypothesis. It checks
> the round's status and the births with no reader parent, not whether each reader's births are the same for both far
> settings: at a seven-knot sampled start (index 1007, readers (3,6) and (2,0)) Alice's edit changes the inputs of Bob's
> own birth at fixed Bob setting, with every prepared state surviving. A4 holds where the responses actually factor;
> the census does not show that they do on every placement it marked. **Narrowings:** a rejection representation can
> also come from positive completion counts (every state surviving: CHSH 9/4 in a variant of A3), and "local" there
> includes the rejection outcome; with a contact (a birth of two readers), changing either reader's own edit changes the
> forbidden states in 163 one-holder placements under not-all-equal and 68 under parity, and all three in one
> three-reader placement, so "forbidding never answers both readers' settings" holds only for births each owned by one
> reader; the flag and the actual forbidden sets differ once (64 against 65); the stored record omits the values of
> other parents' inputs (no verdict changes); tables were computed on 646 selected extension starts (562 scored), not on
> all 3,000; the built starts' correlations are small but not zero (largest 2601/7295401); Branciard's η is each
> reader's acceptance given the other's (A3: 1/2 each, bound 6, capped at 4). **Not a block:** the small correlations.
> Logged in `docs/CORRECTIONS.md`.
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
  2). Three readers: by exhaustion on one value a reader, and on two values for one reader and
  one for each other, the best Mermin win is 3/4 ([`linear_three.py`](linear_three.py)); *corrected after the run:* the
  case of two values for two readers was started and stopped unfinished (not run), so "two values a reader" was more
  than was checked. No proof yet. What growth can break is the split: a birth with parents of
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

**With a contact (an addendum after A4, written before its run).** A4 leaves a joint response only where a birth or a
stall depends on both settings. The census set aside the placements with a birth of two readers (a contact between
them: 3,587 under E1, 450 under M1). The addendum reads them too (`--shared`, E1 and M1 on the census of starts up to
five knots), with the same tables and record checks. *Expected:* where a newborn knot holds distinctions of both
readers, the far edit changes the near reader's births or values, so every excess there comes with a changed record
(signalling); none without.

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

## What was found

Tables: [census pre-count](census_count.md), [census tables](census_tables.md), [extension pre-count](extension_count.md),
[extension tables](extension_tables.md), [built starts](built_tables.md), [with a contact](shared_tables.md). Runs:
`count_*`, `tables5_*`, `xcount_*`, `xrun_*`, `built_*`, `shared_*` (`.jsonl.gz`).

- **Forbidding never answers both readers' settings in a grown start.** In the census (7,075 starts of three to five
  knots) it answers one reader's in 12 placements (E1, one fewer); in the extension (3,000 sampled starts of six to
  eight knots) in up to 72 (E1, one fewer) and 65 (E2, the arity floor), never in a three-reader placement, never on
  both sides. Most placements stall in every setting pair, since one short knot stalls the round.
- **No table exceeds the classical bound, with or without signalling.** Census: 3,901 (E1), 946 (E2) and 150
  (three-reader) placements read under each of the six laws, both weightings; extension: tables on the 646 starts with
  a placement where forbidding answers a setting, or among the first 200 of each size (2,388, 1,550 and 669
  placements). On placements that split, the largest not-all-equal CHSH is 0.159 and its Mermin win 1/2 (no
  correlation) under every law; parity reaches exactly 2 and 3/4 (readers whose values a chain of parity knots ties),
  as A2 allows.
- **Built starts where both sides forbid carry no correlation.** In the 81 built starts (E1), forbidding answers both
  readers' settings under one fewer in every one, every one splits and every complete record is unchanged by far
  settings; CHSH stays below 0.001, because the join carries old-value correlations below 4 × 10⁻⁴: rejection has
  nothing to select on. Under the arity floor these starts do not forbid by setting. The two E2 built starts do not
  split.
- **With a contact, still no excess.** Of the placements where a newborn knot holds distinctions of two readers (3,587
  under E1, 450 three-reader), the far edit changes the near reader's complete record in most (all under the ordinary
  count), and no table exceeds 2 or 3/4 (largest: not-all-equal 1.06, parity 2, Mermin 3/4).

**So.** On placements that split, forbidding is local rejection (A4) *(R1, Block: only where the responses actually
factor, which the flag does not check)*: whatever its size, no nonlocality in Bell's sense
can come from it. Whether growth gives even a rejection excess was not tested in effect: no grown start forbids on both
sides, and where both sides were built to forbid, the two sides were uncorrelated. That is a "not run in effect", not a
negative, and the census is not called clean. The advisor's view, which I take: with A4 in hand the two-sided question
is worth little, since any excess would be a loophole artefact, so the class is not extended further.

## Expectations, and how they fared

1. *Parity: no excess without signalling; three readers none above 3/4.* Holds (and A2 proves the two-reader case).
2. *Not-all-equal, the ordinary count: under S no excess; under U excesses may appear, all with signalling.* The first
   holds; the second fails: no excess at all, although under U the complete record changes with a far setting in 301
   of 4,642 census placements that split (completion counts that depend on far values).
3. *Not-all-equal under A129/A130: excesses with single values unchanged may appear; a clean census.* No excess of any
   kind; the census tests nothing two-sided, as the advisor said ("mostly by vacuity").

## Literature (cited once; what this adds)

Bell's bound and its loophole forms: Pearle (*Physical Review D* 2, 1418, 1970) and Gisin and Gisin (*Physics Letters
A* 260, 323, 1999) built local models with rejection; Branciard (*Physical Review A* 83, 032123, 2011) gives the bound
4/η − 2 under post-selection. That every no-signalling table has a local model with signed weights is Abramsky and
Brandenburger (*New Journal of Physics* 13, 113036, 2011); that a nonnegative representation is equivalent to a
noncontextual one is Spekkens (*Physical Review Letters* 101, 020401, 2008). This study adds the growth laws' own
answer: with free local edits, a join that forbids acts as a local rejection, and in the starts read it does not even
do that on both sides.
