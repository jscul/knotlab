# Changes from the first drafts to the second versions, item by item of the advisor's answer

`study/descent_advisor/answer.md`, sections 1 to 14. "Applied" means applied as worded; otherwise the change or the reason
is given. Files: `note_v2.md`, `definitions_v2.md` (DH2), `preregistration_v2.md` (PR2), `history_lines.md`.

## 1. Is (H) an answer or a price?

- It is a price; moved, not removed. **Applied** (note: verdict line; owner sentences).
- The verdict line "shown in the structure's places; written by the law; relative to a start supplied flat". **Applied**.
  "Held by the structure" is used for this result nowhere; the owner's question keeps it in quotation.
- Reading the law's text is too weak; V1 not exhaustive. **Applied**: V1-V3 replaced by the inputs, factoring and restart
  tests, each with exhaustive answers (note, "The three tests"). The advisor's example ration (as many fresh as the parent
  has places, plus one) answers "written" under the inputs test.
- What "made" would require (four items). **Applied** (note).

## 2. BARRED-MOD3

- It is the stamp of A247 in unary in distinctions no birth takes; say so; H3 is its proof. **Applied** ("the stamp of A247
  written in barred distinctions").
- Its write rule without FILLERS is the stamp's word for word. **Applied.**
- It moves condition (a) into "a start has no barred place"; V3 (b) is supplied. **Applied** (DH2 1.2 states it; note).
- "Do nothing" is false outside births; list what changes. **Applied** (live for good; allowed states under parity and
  not-all-equal; the closing exception; SD's sameness and periods), with the cost measured in scratch (share of new knots
  with s > 0: 0.62 under NEXT3-PLACES (barred), 0.78 under NEXT3-BARRED). One wording changed: the advisor wrote "Under
  BARRED-MOD3 the first birth has s = 1"; that holds without FILLERS; with FILLERS the first birth leaves a barred filler or
  s, so the conclusion (the exception never applies) stands.
- The knot test is true by construction for these forms. **Applied** (PR2 P10, a check of the code).
- USABLE is the price, not the count doing something. **Applied.**
- Neither form at the centre; the value is used only in run 6. **Applied** (the note's content is the two arguments).

## 3. M1, the reason

- Sound; exclude NO-OFFSHOOT. **Applied.**
- DH 5.2 "to itself": the distinction is fixed, the places exchanged. **Applied** (DH2 5.2).
- DH 5.1 "the least a" against 11 cases. **Applied** (DH2 5.1: "a number a with F(1, a − 1) = a − 1").
- Scope one start per ration; "every ration of p and D alone" too wide. **Applied**: withdrawn (note).
- The restart lemma. **Applied with a statement of "allowed start"** (DH2 1.2) and with the drafter's own check (below).
- The two-knot named start as an instance. **Applied**; confirmed in scratch: it is the lone three-place knot after its first
  offshoot under ORD, CAP-3, FLOOR1, FLOOR0 and ONE-FEWER.
- Every positive result must name a class not closed under restart; (a) is that class. **Applied.**
- L3 stronger. **Applied.**
- "A later stage breaks the symmetry" true within one known start; what refutes "from then on". **Applied**, and quantified by
  the check below.
- A registered family (one exchanging renaming per round on a start that is not a lone knot). **Not applied**: the
  parents-from-holders record already has such pairs at later rounds (115 on the two-knot start under FLOOR1 with offshoots,
  49 on the ring of five under RATION-3 with waiting, its `whole_pairs.json`), and the note cites them; a new registered
  family would cost an engine part for a statement the record holds. Left to the advisor.

### The restart lemma: the drafter's check, as the coordinator asked

- **Can the conclusion fail?** No, once both members are in the population: it needs only that a structure reached by a
  birth has a parent place (its last new knot's), which is a place between two start knots when the same structure is a
  start. A counterexample can only be to hypothesis (R3), "a reached structure is an allowed start".
- **The search** (`w3_restart.py`, eight laws, six small starts; structures after complete rounds 1 to 3 of at most 40 knots,
  and the half-built structures of the start and a prefix of round 1's new knots of at most 12 knots). Results in
  `out/w3_all.txt`. The run was cut at 20 minutes by the drafter (its renaming search is slow on the symmetric 40-knot
  structures): 26 of the 48 cases of law and start finished, 176 structures. Findings:
  - 173 of the 176 are allowed starts; the 3 that are not carry a barred distinction (FLOOR1 with retiring). By the
    definitions the other ways to fail are FILLERS barring and the closing exception (a knot of fewer than three places).
  - **Most reached structures that are allowed starts have an order recoverable within their own start's history**: no
    renaming of the whole structure exchanges a parent place with a place that is not one, on 148 of the 173 (the other 25
    have such a renaming, among them the lone-knot structures of M1 that were in range). So the lemma is about
    populations that include restarts; on the population of one start's histories alone it says nothing, and the record's
    other results (the parents-from-holders study's growing least distance) carry that case.
  - The restart grows as the continuation (same signature) in 68 of 68 tests (structure after round t handed in as a
    start, 2 more rounds, against round t + 2).
  - **The coordinator's question** ("a recorded law and a reached structure that is an allowed start but whose reaching
    history is recoverable from the structure") has many positive instances inside one start's history, and none once the
    restart is admitted to the population; they do not refute the lemma, they show its population-relative force.
  - **The census holds restarts.** 515 of the 3,348 census starts are themselves reached, after one or more of round 1's
    births, from a census start of at most four knots under some recorded law (145 to 234 by law; `w6_census_restart.py`).
    So the lemma bites on the record's own population.
- **Where "allowed start" needs a statement.** SD lines 11-18 define a start but say only implicitly that a start carries no
  barred distinction ("a loose distinction is usable unless the law has barred it"). Every positive result rests on such a
  statement: condition (a), or "a start has no barred place". Laws with three or more holders would also need to say whether
  a start may hold a distinction three times.
- **One thing the advisor's statement leaves implicit**: its extension to every later structure needs a round that reads only
  the present structure (SD's does). Laws that read the record of parents (the fold study's STEPS-k, the guard of the
  one-birth-at-a-time study) do not continue a restart as they continue the run; the lemma about the one structure still
  holds there.

## 4. L3, H1, H3, H5, H6

- L3: exclude closing births. **Applied.**
- M2: reword; disclose "reaches a knot of generation 3" as chosen after scratch. **Applied** ("three parent steps").
- H1 true as a conditional under RELEASE and HOLD; one c per connected piece; (b) sufficient not necessary; (b) is a sketch
  under RELEASE and an observation on 16 runs under HOLD; (b) decided from the record. **Applied, and strengthened**: (b′)
  "parent steps agree counted in threes" replaces (b), with an exact converse (given (a) and (c), the place rule is right on a
  run exactly when (b′) holds). **And a finding**: the observation under HOLD does not extend to the census: parents at
  different parent steps on 48, 48, 368 and 462 of 3,348 starts under the four holding laws (history lines).
- (c) counted in threes, with the exact effect of h. **Applied**; the effect checked exactly on 16 runs (`w5_retire.py`:
  predicted and actual wrong places equal on every run; h ≡ 0 did not occur).
- H3's three notes (the exception off from the first s > 0; births match through the base's closing round; SD's kinds
  differ). **Applied.**
- DH 3.2 step 5 defect (a two-place knot). **Applied** as the advisor wrote it (F_B as if no closing, s recomputed), with
  the old reading kept as the swap.
- H5 sound; run 4 a check of the code. **Applied.**
- The not-all-equal bound stated three ways. **Applied**: one bound for the test (every structure the runs make, at most
  3,000 knots, by the fold study's exact decomposed method); the direct method only as a check of the code (knots of at most
  7 places in structures of at most 150 knots).
- H6: "first failing birth" depends on the order of joins. **Applied** (round and multiset).

## 5. The start's values

- The honest statement (works from a start that already agrees; supplied). **Applied.**
- 133 of 3,348 with its family and weighting and the counts by size. **Applied**; and (a) exactly at six knots: 804 of
  82,372 kept (scratch, seconds), labelled share 0.5% (1.7% at up to five knots).
- Counting in fives is the least-record result moved; not a law. **Applied** (DH2 3.3, a stated variant).
- The table of the greatest difference by start and round. **Applied** (PR2 part 3, P14); scratch: a greatest difference of 3 seen
  under every waiting law with RELEASE except ORD with waiting, and under three of the four holding laws.
- The history line on the 510 starts. **Applied** (`history_lines.md`), widened to the holding laws.
- The discrepancy (1,753 against 1,243). **Resolved**: the first fives run left out the three added rules; with them,
  1,727 of 1,753.

## 6. H7

- A sentence and one cheap check, not a ticket. **Applied** (PR2 part 6).
- The period formula 2 × 3 / gcd(3, q). **Applied** as T · 3 / gcd(3, q); seen with descent checked on the rings of five
  and seven under the two and three added rules (T = 2, q = 1, period 6 under both barred forms).
- The honest sentence. **Applied**, nearly word for word.
- The note for the count-of-returns study. **Applied.**

## 7. What is left open

- Three or more holders is not the one place left; the restart lemma covers them. **Applied.**
- "Made" with nothing supplied closed by argument once refereed. **Applied** (note).
- What stays open is relative; the smallest honest search; value low, park it. **Applied**: one parked sentence, not designed.

## 8. Sizes

- Ask for neither exception. **Applied.**
- Run 6 tests plumbing. **Applied**: not registered; considered and left to the least-record study's deferred direction 3.
- Six-knot census: (a) exact, (b) a seeded sample of about 3,000. **Applied** (scratch: 493 of 3,000 under the study's
  waiting law).

## 9. Weighting and numberings

- The labelled weighting as the swap, as a reweighting, no direction predicted. **Applied.**
- "Argued for every numbering; no difference found in N runs". **Applied**, N = 89,910.
- An exact isomorphism test on the small starts. **Applied** (PR2 0d).
- The miscount ("five starts"). **Applied**: four starts of at most six distinctions and five others.

## 10. The definitions

- Two meanings of "recovers". **Applied** (DH2 4.2, 4.3).
- Name the population every time. **Applied.**
- "Shown within d" unchanged by renaming. **Applied.**
- The parent-closed part (a construction; which of the least-record study's half-built structures are such parts; marks as
  of when). **Applied.**
- The knot law of each run; the 32 set aside under parity. **Applied**: every run names its knot law; the 32 are set aside
  under parity only; none fails under not-all-equal.
- Parents that differ: the swap replaced by "c and c + 1 give c + 2". **Applied.**
- FRESH-MOD3 a sentence. **Applied** (DH2 3.4); P4 removed.
- H2 has no defined set. **Applied**: H2 removed; replaced by the converse of H1 (P4), the start-place prediction (P5) and the
  exact set under retiring (P6).
- Smaller defects (DH 2.2 garbled; (c) for start knots; "inherit that difference"; USABLE with FILLERS). **Applied.**

## 11. The predictions

- True by construction marked as checks; replications marked. **Applied** (PR2 marks).
- Undecidable H2 and P16. **Applied** (H2 removed; P16 reported).
- P8 and P10 over-pinned. **Applied**: P8 is now PR2's P6 (the exact set); P10 is now PR2's P12, reported with no
  prediction (the price).
- New by run: HOLD bases, swaps, rings 13 and 15, run 6. **Applied with one change**: HOLD bases and swaps are in; two rings
  with descent (as the coordinator's list says), not 13 and 15; run 6 not registered.
- Missing items: the restart control (PR2 part 5, P8); the population of each claim; the knot test on the census structures
  (stated as argued, tested on parts 2 and 6); the cost (P13); counting in twos (a sentence); "written after scratch".
  **Applied.**

## 12. Words

- All applied: "shown within d" with its d; "count in threes"; "parent steps" with the record's "generation" quoted once;
  "value" for the stamp only; "new knot"; arms R and W; NEXT3-PLACES (usable), NEXT3-PLACES (barred), NEXT3-BARRED,
  NEXT5-BARRED; "the guard of the one-birth-at-a-time study". The breaches listed are gone from the second versions (searched:
  "generation" appears only in quotation; "counter", "layer", "congruent", "inherit", "came out", "one side of every" do
  not appear).

## 13 and 14

- The owner sentences. **Applied, adjusted**: the 510 is "under the waiting law of the least-record study" (it is 510 under
  three of the four waiting bases and 223 under FLOOR1 with waiting), and the holding counts are added.
- The verdict (redesign smaller: a checked note with one confirming run). **Applied.**

## Anything in the advisor's answer found wrong

- Nothing material. Two small points: the first birth under BARRED-MOD3 has s = 1 only without FILLERS (section 2; the
  conclusion stands); and the advisor's (b)-under-HOLD "observation on 16 runs" is right as stated but does not extend: the
  census shows it fails (section 4 above). The restart lemma's conclusion is right; its force is population-relative, which
  the advisor's section 3 implies ("on a population holding both") and the check makes explicit.
