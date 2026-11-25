# The copier study, ticket C: definitions for the owner's third addition

Epic `MADE-COPIER-20261125-001`, ticket `MADE-COPIER-20261125-001C`. These definitions ("DC section.item") extend
[ticket A's definitions](definitions.md) ("D section.item") and [ticket B's definitions](definitions_b.md) ("DB
section.item"), and through them the fold study's ("FD") and the shared definitions ("SD line n"); they change nothing
in D, DB, FD or SD. They serve [ticket C's claim](claim_c.md) and [its
pre-registration](../MADE-COPIER-20261125-001C/preregistration.md) ("PC"). The starts and the samples are in
[starts_c.json](../MADE-COPIER-20261125-001C/starts_c.json), the scratch's cases, the planted pair and the sample of
negative controls in [cases_c.json](../MADE-COPIER-20261125-001C/cases_c.json). The canonical K1–K3 test is unchanged.
Versions 1 and 2 of this text are filed in the advisor folder as sent; where a reading changed, the change is said where
it is made.

## 0. Words

- **Kept from D 0 and DB 0**, with their rulings (among them: "not of the others"; "the controls of the readings", D's
  placed-by-hand checks of the readings, a different thing from the continuations of DC 4; names "before" and "after";
  "descended from X only, from Y only, from both"; "made by X"; "ended", "returns"; a lone member; conditions written by
  their letters; no "used up", "comes out", "collapse"). DB's W1 to W4 (the start's meetings) are not used here, and no
  weighting of this ticket is named by a letter.
- **Kept from the glossary:** **sample** (one meeting pattern produced by one run of a declared random process) and
  **weighting** (the chance a declared random process gives to each set of meeting patterns). Nothing is called typical,
  rare or likely without its weighting, and "draw" is not used (D 2.7's "drawn" histories are here **sampled**
  histories, the same process). **Barred** is D's and FD's word for what a continuation does to a part; "frozen" is the
  glossary's word for something else and is not used.
- **Seed**: ticket A's word (D 9), the string given to `random.Random` for one sampled growth or continuation.
- **Form**, as a noun: the class of a part (or a roster) under SD lines 29–30, two parts having the same form when a
  one-to-one renaming of members carries h, k and the family of inclusion-maximal met sets of one onto the other.
- **Control**, always in one of three phrases, never alone in another sense: D's "the controls of the readings" (D 3.6,
  placed-by-hand checks of the readings, not run here); "a control of a case" (one of the continuations of DC 4.1 with Y
  barred, with X barred, masked or fully masked, against which the continuations with nothing barred are compared); and
  "the controls of the rate rule" (PC, R0b: the machinery control and the planted case, which the test must see, and the
  negative controls, which it must not confirm).
- **The owner's words** "statistically", "hit", "copier like DNA" and "primordial soup" appear only inside his
  quotation, and in the forms 'his "hit", read' and 'his "primordial soup", read'. DNA and a primordial soup are his
  pictures; no claim is made about living things, minds, physics or time.
- **Defined here, as phrases of words already in use; no new noun:** a sampled growth; the census weighting and the
  labelled weighting (of starts); the take-by-take weighting and the holder weighting (of takes); the family of laws; a
  made pattern; a pair of the growth; the unmet pairs; values, both from X; a reading met after the meeting; the
  continuations of a pair; masked and fully masked; a case; the rates of a case; passes at 100; confirmed; a case met
  more often with Y; the way of a case (through joining; through takes; with Y's births, not through a meeting); a case
  that needs the meeting; a one-history case; the planted case; the machinery control; a candidate; a candidate seen
  again; the rate of cases; the main runs and the conditional runs.

## 1. What is sampled

1. **Starts.** The record's census of every start of three to five knots with single meetings, each once up to
   isomorphism (the ring study's census, rebuilt by the study of parts that copy themselves: connected graphs of
   networkx's graph atlas, a loose count of 0 to 3 on each knot with degree plus loose count at least 3 and at least one
   live knot, each kept when least in its orbit; one shared distinction for each pair of knots the graph joins, in
   sorted order, then the loose distinctions in knot order): 19, 200 and 3,157 starts on three, four and five knots,
   3,376 in all, in the record's order, listed in starts_c.json with their ids `n<knots>-g<atlas index>-<loose counts>`.
   A start is set aside, for a knot law, when a start knot fails the knot test under that law: under parity the record's
   32 (3 of four knots, 29 of five), leaving 3,344; under not-all-equal none (every start knot of the 32 passes). Each
   run reads a prefix of one uniform permutation of the census (DC 1.5); under parity with MET that prefix is every
   start. Six knots (82,056 starts) are a later stage, not registered here.
2. **The weightings of starts.** **The census weighting**: each start of the census once, that is, the uniform weighting
   over the census list. **The labelled weighting** (its swap): each start weighted by its number of numberings of its
   knots (of its knots only, not of its distinctions), n! divided by the number of automorphisms of its graph that keep
   its loose counts. The weights are listed in starts_c.json: over the whole census 63, 2,786 and 254,454 on three, four
   and five knots (257,303); over the 3,344 starts read under parity 63, 2,774 and 253,724 (256,561), at most 120 for
   one start. Where every start of a stratum is read, a rate under the labelled weighting is the weighted mean of the
   starts' rates and nothing is sampled for it; where starts are sampled under a weighting, the rate is the mean over
   the sample.
3. **Laws: the family.** Ration ∈ {FLOOR1 (COPY-LAW), FBP (D 1.6), CAP-2, CAP-3, CAP-4, ORD, RATION-2} (SD lines 58–61)
   × treatment ∈ {CANCEL-RETIRE, CANCEL-OFFSHOOT, CANCEL-WAIT} × taking rule ∈ {MET, STEPS-1} (FD 2.2; D's two taking
   rules) × RELEASE, under both knot laws: 42 laws under each knot law, each read and each reported on its own; no rate
   is averaged over laws. **Swaps** (conditional runs, PC "Runs"): HOLD for RELEASE (the 42) and STEPS-2 for STEPS-1
   (the 21 with STEPS-1), under parity on the starts of three and four knots and on the first 300 five-knot starts of
   the order (DC 1.5), and HOLD with MET under not-all-equal on the starts of three and four knots; run only if a case
   of a claimed reading is confirmed in the main runs. STEPS-1 entered the family after the scratch census, which showed
   that under MET the roster has two parts or more in about 1% of the rounds read (under parity, on the starts of three
   and four knots, under the take-by-take weighting; PC, "Known before the runs"); this favours a positive and is
   disclosed. With no taking rule two patterns made by the growth never meet (FD 3.1), so a growth with no taking rule
   has no meeting after its start; ticket B is the census of that case, and ticket C reads only laws with a taking rule.
4. **Histories: the weightings of takes.** **The take-by-take weighting** (D 2.7): each take of each round, in the order
   the round asks for them (FD 2.1's birth order; for each birth its takes in order), one call
   `rnd.randrange(len(candidates))` on the candidates sorted by name, a take with a single candidate also making its
   call. **The holder weighting** (its swap): the same order, one call `rnd.choices(candidates, weights=h, k=1)[0]` on
   the candidates sorted by name, with h the number of holders of each candidate at the start of the round; a take with
   a single candidate also makes its call. **Seeds**: a growth's seed is `C|<start id>|<ration>|<treatment>|<knot
   law>|<i>`, with the ration one of `FLOOR1 FBP CAP-2 CAP-3 CAP-4 ORD RATION-2`, the treatment one of `CANCEL-RETIRE
   CANCEL-OFFSHOOT CANCEL-WAIT`, the knot law `parity` or `nae`, and i the growth's sample index; then, in this order,
   `|STEPS-1` or `|STEPS-2` when the taking rule is not MET, and `|HOLD` under HOLD; a continuation's seed is its
   growth's seed followed by `|<kind>|<s>|<i>` (DC 4.1); under the holder weighting `|T2` is put last of all. Stage 2
   (DC 5.2) and R8 of PC use sample indices of their own (DC 5.2; PC, "Runs"). One generator per seed. A **sampled
   growth** is one start, one law and one sample of its takes, grown to the bounds.
5. **Bounds, sizes and order.** 8 rounds; a growth stops after the first round past 500 knots; the fold engine's guard
   (DB 3.9's rule) stops a round, which is then not read (PC, Settled 1, says why this does not depend on names).
   **Order of the starts**: every run reads the starts in the order `random.Random('C|order').sample(range(3376), 3376)`
   (indices into the census list; starts set aside under parity skipped), and for each start the laws in the order of DC
   1.3 (ration, treatment, taking rule); so the starts of a run are a prefix of one uniform permutation of the census, a
   sample without replacement under the census weighting. **Sizes** (the owner's limit of 25 November 2026; PC, "Runs",
   gives the measured costs), each with sample index 0: R1a, parity with MET, every start; R1b, parity with STEPS-1, the
   first 2,000 starts of the order; R1c, not-all-equal with MET, the first 1,000; R1d, not-all-equal with STEPS-1, the
   first 120; R2 (the holder weighting, parity), the first 500 under the 42 laws; the conditional runs as PC says. **A
   run cut for time** is cut only to a size registered in advance, the first half or the first quarter of its starts,
   which is still a prefix of the order; a run stopped at any other point is not a registered prefix (its length depends
   on how long its starts ran, so it leans toward starts that grow fast), and any bound from it is given with that said.
   Versions 1 and 2's sizes are replaced by these.
6. **The state** of a growth after a round, from which every reading and every continuation starts: the structure with
   its barred marks, its retired knots, the birth record (each knot's parents, kind and round made), the parity rules
   (under parity) and the round number. "A structure" in this ticket means this state.

## 2. The pairs of a growth

1. **A made pattern**: a part of the roster after a round s ≥ 1 every member of which was made after round 0. At s = 1
   X's members are children of start knots, so X's form is one round from the supplied start; cases are reported by s.
2. **The pairs of a growth**: for each round s from 1 to 4 (and less than the last round read), every ordered pair (X,
   Y) of parts of the roster after round s with X a made pattern, Y another part, and X and Y wholly apart (FD 1.6). Y
   may be a made pattern or hold start knots. When a round has more than eight such pairs, eight are sampled uniformly,
   without replacement, from the list of pairs in lexicographic order of their parts' smallest member names, with
   `random.Random(<the growth's seed> + '|P|<s>').sample(pairs, 8)`. Sampling uniformly keeps the rates independent of
   the numbering (PC, Settled 1); taking the first eight by name, as FD 5.8 does, would not. With each growth the number
   of ordered pairs (X made) that "wholly apart" removes is reported. (A scaffold; its swap, every pair, on the starts
   of three and four knots.)
3. **The meeting round** m of a pair: the first round m > s at which X and Y are one part again or one part for the
   first time (FD 4.3), read in the growth. Under a taking rule the growth makes the meeting.
4. **The unmet pairs**: the pairs with no meeting round by the last round read.

## 3. Descent and the readings

1. **Descent**: D 2.6 with the pair's s (X's own members are from X only). X's form and Y's form are the forms of X and
   Y in the roster after round s.
2. **The readings**, each read at every round t > s:
   - **form** (claimed; ticket A, D 3.1, with D 5.1's condition 3): Y's form is not X's form, and at least two parts are
     the same as Y's form, each containing a member made after round s, every member descended from X only;
   - **from both** (claimed; ticket B, DB 3.4): at least two parts the same as Y's form, each containing a member made
     after round s, every member descended from both;
   - **values, both from X** (claimed), under parity only: two usable loose made distinctions tied to one place v of Y,
     v free and tied to no place of X after round s, **both descended from X only**;
   - **values with one from both** and **values, both from both** (reported apart): the same with the two descended from
     X only and from both, or both from both. With Y barred nothing descends from Y, and masked nothing descends from
     both, so two of the controls of DC 4.3 cannot see these, nor from both (DC 4.3);
   - **ticket A's values reading** (D 3.3, reported with its own verdict, PC): the same with at least one of the two
     descended from X (from X only or from both). The values readings of this list were defined after ticket A's reading
     was seen to pass the Y-barred and X-barred comparisons in the scratch, its second distinction being Y's own (PC,
     "Known before the runs").
   Built structure (D 3.2) is not read: ticket A found no case of it, and its search is the costliest of the readings.
3. **A reading met after the meeting**: met at a round t ≥ m. Each reading is also reported at any round after s.

## 4. Cases

1. **The continuations of a pair** (the paired test of D 4.2, 4.3 and FD 5.6, with takes sampled): from the state after
   round s of the growth (DC 1.6), continuations under the same law, their takes sampled under the growth's weighting,
   through round 8 or to the knot bound, of five kinds, each with its seed (DC 1.4): **nothing barred** (`|BN|<s>|<i>`);
   **Y barred** (`|BY|<s>|<i>`: every usable loose distinction of Y's members barred, FD 5.1); **X barred**
   (`|BX|<s>|<i>`); **masked** (`|BM|<s>|<i>`: FD 5.6, from round s + 1 no member of X or its descendants is joinable
   with a member of Y or its descendants, in the round and in its demand step); and **fully masked** (`|BT|<s>|<i>`:
   masked, and in addition, from round s + 1, no birth with a parent among X and its descendants has among its
   candidates a distinction held at the start of the round by a knot of Y and its descendants, and no birth with a
   parent among Y and its descendants has among its candidates one held by a knot of X and its descendants; the sides
   are FD 4.2's, extended by each new knot with a parent on a side). The masked and fully masked kinds are run at
   confirmation only. A continuation stopped by the knot bound or the guard is read through its last round read, and
   counts as not meeting an event not met by then; the number stopped is reported for each kind, and the rates are also
   given over the continuations not stopped. Continuations of different pairs of one round with the same kind and index
   have the same seed, and with nothing barred they are one continuation; under the family-wise rule of DC 4.4 this is
   harmless.
2. **Y's own**, in a continuation with X barred: two parts the same as Y's form, each containing a member made after
   round s, every member descended from Y only (for the form readings); or two usable loose made distinctions tied to
   one place of Y, both descended from Y only (for the values readings; D 3.5).
3. **A case** (his "hit", read): a pair of a sampled growth whose reading is met after the meeting. A case is one
   sample; whether it is met more often with Y is a comparison of rates. **The rates of a case**, from K′ continuations
   of each kind: q₁, the share with nothing barred in which the reading is met after the meeting, the meeting read in
   the continuation (and, reported, q₁ at any round after s); q₀, the share with Y barred in which the reading is met at
   a round after s; q_Y, the share with X barred in which Y's own is met; q_M and q_T, the shares masked and fully
   masked in which the reading is met at a round after s. The events differ (q₁ after the meeting, the controls at any
   round), and with nothing barred the knot bound is reached sooner; both lean toward the negative, and the test keeps
   them so. For from both and the values readings with a distinction from both, q₀ = q_M = q_T = 0 by construction (with
   Y barred nothing descends from Y; masked, a knot from both would need a join with a parent on each side, and groups
   are pairwise joinable), and only q_Y tests anything.
4. **The test.** For each control, a one-sided Fisher exact test on the 2 × 2 table (met or not; nothing barred against
   the control), the null being that q₁ is not greater than the control's rate. **Passes at 100**: with K′ = 100 of
   nothing barred, Y barred and X barred (i = 0 to 99), q₁ above q₀ and above q_Y, each test at level 0.01, with no
   split of the level between them. **Confirmed**: of the m cases of the claimed readings (form, from both, values both
   from X) that pass at 100 in the main runs (R1a to R1d and R2 of PC), all counted before any confirmation, each is
   read on 1,000 further continuations of each of the five kinds (i = 100 to 1,099); it is confirmed when q₁ is above
   q₀, above q_Y and above q_T, each test on these continuations alone at level 0.01/m. So over the main runs the chance
   of confirming any case whose q₁ is not greater than all three is at most 0.01 (family-wise, not a false-discovery
   rate: one confirmed case would overturn the main prediction). The conditional runs (PC, "Runs"), if run, form a
   family of their own at 0.01, with the cases that pass only at the swap's 300 among them; the reported readings (DC
   3.2) form a third, m′ counted the same way, each at 0.01/m′. **A case met more often with Y**: a confirmed case.
   **The way of a case**, reported with it: **through joining**, q₁ above q_M (one-sided, at 0.01/m); **through takes**,
   confirmed but not above q_M. A case above q₀ and q_Y but not above q_T is not confirmed; it is reported as **with Y's
   births, not through a meeting** (FD 5.7's round-wide trigger) and is not counted. The masked rate is also reported
   against q₁ by a two-sided Fisher exact test, since the joining may lower the rate (version 2's scratch saw 85 against
   58). **A case that needs the meeting**: a case met more often with Y whose reading is met in none of the 1,000
   continuations with Y barred and none of the 1,000 fully masked (each rate below 0.3% at 0.95); X barred does not
   count toward it, since it reads a different event, Y's own, and q_Y is reported beside it. **A one-history case**: a
   case met after the meeting in at most 2 of its 100 continuations with nothing barred, reported with its numbers.
   **Intervals**: every difference q₁ − q is reported with its Agresti–Caffo interval at 0.95 (one success and one
   failure added to each arm); every rate of stage 2 with its exact (Clopper–Pearson) interval at 0.95. **Power, both
   halves**: at 100 a case passes only with about 7 of 100 against 0 (p = 0.007), which is the best case, a control near
   zero; where the control is near one half (the scratch's Y-barred rates for form ran from 11 to 82 of 100) it takes
   about 18 points, and even a true difference of that size passes at 100 about half the time (0.68 against 0.50: 55% by
   simulation). **The swap** (conditional, R6): K′ = 300 at the first stage on the starts of three and four knots, with
   kinds `BN3`, `BY3`, `BX3` in place of `BN`, `BY`, `BX` and i = 0 to 299, in the conditional runs' family.
5. **The rate of cases**, for a law, a knot law and a reading, under a weighting of starts and one of takes: the mean
   over starts, by the weighting, of the share of a start's sampled growths holding a confirmed case; with it the same
   share for cases (any), for cases that pass at 100 and for one-history cases. Each rate is given with its sample size
   and seeds, by stratum (start size), and twice: over all growths, and over the growths with no failing knot (the same
   weighting conditioned on no failing knot, DC 8). No bound is given on a share of met pairs, since the pairs of one
   growth are not independent. **A zero bounds the rate**, each law separately, at 0.95: with K sampled growths of each
   of N starts and p_i the chance for start i, the chance of no case is Π(1 − p_i)^K ≤ exp(−K Σ p_i). Where the N starts
   are every start of the census, a zero bounds the census weighting's mean below 3/(K N) (e^−3 < 0.05). Where they are
   a prefix of the order of DC 1.5, a uniform sample without replacement, a zero bounds it below 3/N whatever K, since
   the growths of one start are not independent samples of the census (sampling without replacement is no worse than
   with it). Under the labelled weighting the mean is at most max w / w̄ times the census weighting's (w̄ the mean
   weight: 76.7 over the 3,344 starts passing under parity, 76.2 over the 3,376; max w = 120), so each bound is
   multiplied by about 1.6. For all 84 laws at once, 7.4 replaces 3 (ln(84/0.05) = 7.4). **The bounded event** is "a
   case that passes at 100" when no case passes at 100; when some pass and none is confirmed, it is "a confirmed case",
   whose bound is stated with the note that m ties the growths of the main runs together. The sentences registered: "No
   growth held a case that passes at 100. Under the [weighting], the rate of growths holding one is below [bound] at
   0.95, each law separately. Smaller differences are not bounded." and, when some pass: "No growth held a confirmed
   case; [k] cases passed at 100 and none was confirmed. Under the [weighting], the rate of growths holding a confirmed
   case is below [bound] at 0.95, each law separately, with the growths tied together by m. Smaller differences are not
   bounded."
6. **The unmet-pair rate**: the share of unmet pairs on which a reading is met by the last round read; a reading met on
   pairs that never meet is not the meeting's doing.
7. **The controls of the rate rule** (PC, R0b; counted toward nothing).
   - **The machinery control**, under its own rule: on ticket A's designs made-4 and made-5 (research/MADE-COPIER-
     20261125-001A/starts.json; X and Y of the design, s = 1) under COPY-LAW(CANCEL-OFFSHOOT) with STEPS-1, parity, the
     growth through round 1 with seed `C|A|<design>|FLOOR1|CANCEL-OFFSHOOT|STEPS-1|parity|0`, the event Y's own values
     (two usable loose made distinctions tied to one place of Y, both descended from Y only) at any round after s, read
     with nothing barred against Y barred only, one one-sided Fisher exact test at level 0.01, at 100 continuations of
     each and again at 1,000 further ones; it must pass both.
   - **The planted case**: the pair of index 13 of cases_c.json (start `n4-g17-3232`, COPY-LAW(CANCEL-OFFSHOOT) with
     MET, parity, sample index 0; s = 3, X the members 19, 20, 22, 23, 24, Y the members 18 and 21, one met set {18,
     21}, each holding one usable loose distinction; meeting round 4), chosen because its continuations nearly always
     meet (99 of 100 in the scratch) and its own rates are low (form after the meeting 2 of 100 with nothing barred, 16
     with Y barred, 0 for Y's own). In a continuation, with chance 0.5, decided by `random.Random(<the continuation's
     seed> + '|PLANT').random() < 0.5`, two parts of Y's form are placed into the state read after round r, r the
     continuation's meeting round if it has one and otherwise the growth's (4), and into no other state: each part is
     two new knots y₁′ and y₂′, each holding one new loose usable distinction of its own, and one new dead knot w′
     holding two new distinctions, one shared with y₁′ and one with y₂′ (so w′'s met set is {y₁′, y₂′}); y₁′ and y₂′ are
     recorded as offshoots made in round r with one parent, member 19 of X, so that by D 2.6 they descend from X only;
     w′ is recorded with kind "placed" and descends from neither. The placed knots are read and never grown: they make
     no birth, are not knot-tested, and the continuation goes on from its unplaced state. Three arms, each at 100
     continuations of each kind and then 1,000 further: **arm 1**, placed in the continuations with nothing barred only:
     must pass at 100 and be confirmed; **arm 2**, placed in every kind: must not pass; **arm 3**, never placed: must
     not pass. The chance 0.5 is the advisor's 0.30 raised: with this pair's own rates, 0.30 would pass at 100 about
     half the time (PC, "Known before the runs").
   - **The negative controls**: made-2 (Y's form is X's) under the six laws COPY-LAW(t) with MET and STEPS-1; the two
     cells of ticket A's made designs where form was met in the scratch (made-4 under RATION-2(CANCEL-OFFSHOOT) and
     FBP(CANCEL-OFFSHOOT), both with STEPS-1); and ten of the 92 MET form cases of cases_c.json, the registered sample
     `sorted(random.Random('C|R0b|ten').sample(form_indices, 10))` (indices 16, 22, 24, 26, 29, 48, 52, 62, 68, 83,
     listed in cases_c.json), each read at 100 and, if it passes, at 1,000: none may be confirmed.

## 5. Candidates

1. **A candidate**: under one law and knot law, one form F of made pattern with cases met more often with Y for at least
   two second-pattern forms G, each other than F (in one growth or in several), under the take-by-take weighting.
2. **A candidate seen again** (his "copier", read under sampling): for each G of the candidate and each start where a
   case (F, G) met more often with Y was seen, 100 further growths of that start under the same law (sample indices
   1,000 to 1,099, seeds as DC 1.4), every pair read; at least 3 of the 100 each hold a case (F, G) met more often with
   Y, confirmed in **stage 2's own family** (its m₂, the cases (F, G) of all stage-2 growths that pass at 100, counted
   before any of them is confirmed, each at level 0.01/m₂); the rate is reported with its exact (Clopper–Pearson)
   interval at 0.95, and no percentage is named. **Not of the others**, read on the same growths and counted by growths,
   not by met pairs (DC 4.5): n growths hold a met pair (F, G), x of them two parts of G's form (any descent, each with
   a member made after round s) after the meeting; for each other form G′ that F met there, n′ growths hold a met pair
   (F, G′), x′ of them two parts of G's form after that meeting. With r the number of such forms G′, G′ is **read** only
   if x′ = 0 would reject at level 0.05/r (a one-sided Fisher exact test of x of n above 0 of n′); otherwise it is
   reported "not read", so that "not for others" is never taken from low power. A read G′ is "not of the others" when
   x/n is above x′/n′ by the same test at 0.05/r. (r counts every G′ met, not only those read, so that the level does
   not depend on which are read.) Also reported, from R1: how many starts make F and meet G under the census weighting.
3. **Again in the same growth**: whether a form F with one case has another case in the same growth, against the forms
   with none (counted under the take-by-take and census weightings, reported).

## 6. Verdicts: three questions

- **Who made the two**: the reading's descent (from X only; from both; in the values readings, the descent of each of
  the two).
- **What fixed the takes**: **sampled** under the take-by-take or the holder weighting: a third answer, D 5.2's stated
  rule and picked history being the other two; a rate does not depend on the start's numbering (PC, Settled 1).
- **Where X, Y and their meeting come from**: X made by births (DC 2.1; at s = 1 its members are children of start
  knots); Y made, or holding start knots; the knots through which they are one part at the meeting round, made by births
  or start knots (FD 5.7's classes).
A case is **made** only when X and Y are both made patterns, the knots through which they meet are made by births, and
the takes are sampled; a case whose Y holds a start knot, or whose meeting runs through a start knot, is reported as
supplied in that part. The claim's section 7 says the same.

## 7. Counts by form

**The counts by form** of a growth: for each round, the number of parts of each form with every member made after round
0. Reported for every law, with the forms left twice. They cannot tell a copier from the law's own making of a form
(the two-knot part's returning every two rounds under COPY-LAW is in every count); only the cases and their
continuations can.

## 8. The knot test and the scaffolds

- **The knot test**: every knot of every sampled growth and of every continuation, tested at the last round read, each
  failure dated by the round its knot was made. Under every law of the family a knot's verdict is fixed in the round it
  is made (ticket A's S1, with takes: PC, Settled 7), so the last round finds every failure; D 8's test at every round
  is kept, in the main study, on R1's growths of the starts of three and four knots (PC, R9). This is a change from D 8
  for the owner's limit on time, smaller than it looks: D 8 already tests comparison runs at their last round only. A
  case in a growth with a failing knot is reported, marked, and does not count toward CC-1 or CC-2. Every failure is
  classified: the knot's kind, its number of parents, whether it took a distinction, whether its birth was implied, and
  its round.
- **Scaffolds**, each with its swap or "no swap": the census of starts (the labelled weighting for the census weighting;
  six knots as a later stage); the family of laws (HOLD; STEPS-2: conditional); the take-by-take weighting (the holder
  weighting: R2, reduced); the pairs' limit of eight sampled (every pair, on the starts of three and four knots:
  conditional); rounds 1 to 4 for s (no swap); K′ = 100 and 1,000 with the levels 0.01, 0.01/m and 0.01/m′ (K′ = 300 at
  the first stage, on the starts of three and four knots: conditional); the planted case's chance 0.5 and pair (no
  swap); K and the stage-2 counts and level (no swap; their bounds are stated); the bounds on rounds and knots (no
  swap); the seeds (no swap: a rate does not depend on them beyond its sampling error, and the numbering does not enter,
  PC Settled 1); the run sizes (no swap: set by the owner's limit on time; the bounds they give are stated).
