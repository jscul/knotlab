# Three kinds: what stands

> **Referee report R1, 27 November 2026: confirmed with fixes; Theorem K stands; four Blocks** ([the report](referee-R1/report.md),
> [row audit](referee-R1/row-audit.md)). The referee rebuilt the seven-knot structure (19/9; 43 of 43 rules pass the
> knot test in the whole), every free-sender policy, the two quantum comparisons, the proof step by step (with a second
> normalization and the case without H5 also proved), and the random replay. No checked table needs a fourth kind. Read
> this record with these changes.
> - **Block: a value-reading sender is not needed for the funding signal.** In the whole-stage 9/4 the short holder has
>   one loose distinction and the other two; a sender choosing which holder to supply from holdings alone moves the
>   other reader's birth from 0 to 1/2. "Only an agent outside the model, keying a setting to a value, makes them
>   signal" is withdrawn for kind (b): a choice from holdings, still supplied from outside but not reading values,
>   exposes it. For kind (a) the free sender of Theorem K keys to values.
> - **Block: quantum-compatible tables do not need a read of a change.** Row 20 (17/8, inside the quantum set) passes
>   every policy its declared records allow, and row 8 gives a quantum-compatible 8/3 from a supplied five-to-one
>   weighting. "Every recorded table … inside the quantum set … is of kind (c) with a read of a change and squared
>   weights" is withdrawn.
> - **Block: "no state of the whole" is not the literature's nonlocality.** The literature's criterion is the absence of
>   a joint probability distribution, not of a jointly allowed assignment: the four-type 20/9 has every assignment
>   supported and still has no joint distribution. H1 concerns the protocol's finished word; the README's sentence is
>   withdrawn.
> - **Block: the inventory is not complete.** Missed, each of an existing kind: 19/8 (the funding experiment at weight
>   3/4, kind b), a 4 in the policy proof (kinds b and c), 682/323 (the eighteen-knot removal control, kind a with a record
>   changed), 7/3 from the mixed stages of the 8/3 example, 3778/1863 and 3830/1863 after later one-parent growth, and
>   18 deletion comparisons up to 527/253 and 199/95 (kind a). "Every recorded row is classed" is withdrawn; the three
>   kinds stand.
> - **Narrowings.** Theorem K's contrapositive guarantees *some* revealing policy, needing immunity to every policy in
>   both directions (one direction alone is not enough: a two-bit example has 8/3 with every one-way policy silent); the
>   seven-knot 1/9 is against the first constant policy, the largest change between two policies is 2/9; the record of
>   the eleven-rule replay leaves the third option outside its named distinctions, recoverable from them, so the rows
>   stay kind (a); counting from the start gives 2 on the comparisons satisfying the local-product hypotheses when
>   maximizing over all outcome functions, and 104/45 under supplied orders; of the 1,693 random models above 2 without
>   the filter, 249 satisfy H5; five rows (13, 14, 60, 61, 62), not six, are marked outside H1; row 54's control was not
>   run in its source, row 1 reads values, row 59 is an excess on a different inequality.

Epic `EXCESS-KINDS-20261126-001` (G18, at the coordinator's pick: the advisor's direction 3; register entry A296),
closed 26 November 2026. An argument with a classification of the record and small computed checks; the advisor
consulted twice (for the coordinator's choice and on the draft); referee pending.
[The note](README.md) · [inventory](inventory.md) · [checks](checks.py) ([output](checks_output.txt)) ·
[advisor on the directions](advisor_answer_1.md) · [advisor on the draft](advisor_answer_2.md)

## What stands

1. **Three kinds exhaust the cases under one state of the whole (proved).** For laws that read no values, a recorded
   table above the classical bound needs (a) separate responses whose counting reweights old states by each reader's
   completions, (b) a birth, rule, whole-round event or record that depends on both settings, or (c) a supplied order,
   sign, weighting, reading or settings read from the state. Otherwise it is a local model (Bell; Fine).
2. **Theorem K (proved; checked).** In kind (a), if each reader's births take inputs only from its own record, then a
   reader choosing its setting from its own visible old values (a free sender) changes the other reader's complete
   record whenever the table at fixed settings exceeds 2. The proof turns the absence of such a change into a local
   model. On the seven-knot structure (19/9, hidden) a free sender moves the other record by 1/9; random models agree
   with and without the theorem's H5.
3. **Every recorded row is classed (computed by reading).** 63 rows: kind (a) the settings-as-births line and the
   forbidding edits; kind (b) the funding preparations, the hypothesis-breaking examples and the contact cases; kind (c)
   the change-read, signed, ordered and selector tables; six rows are patterns with no state of the whole, outside the
   statement (the other thread's). Under one state of the whole, no row fits none.
4. **Inside the model, no reader can expose some of these tables (the main result).** A free sender keys a birth to a
   value, which no law reading no values does. So inside the model settings are fixed, and there the record holds
   tables above 2 with every record hidden: the whole-stage 9/4, which lies outside the quantum set (TLM 3.864 > π,
   checked), and the four-type 20/9, whose correlations (5/9, 5/9, 5/9, −5/9) lie inside it (checked).
   Only an agent outside the model, keying a setting to a value, makes them signal, and the classification's force
   rests on that standard (A296).
5. **Counting from the finish (A240)** would let anything able to key a birth to a value detect every excess of
   separate responses, under Theorem K's hypotheses; counting from the start gives exactly 2 on the settings-as-births
   line. A reason to prefer counting from the start for kind (a), not a proof.
6. **What is missing is a reader's question about a change.** Every quantum-looking table with no recorded signal
   beyond fixed settings is of kind (c) with a read of a change and squared weights; with that question supplied, the
   squared-weight chances are counts of pairs of ordinary words (`FREEDOM-CLOCKS-AND-BIRTHS-20261120-001A`).

**Not shown.** H2 for the census parts of the settings line; a general theorem for kind (b); three readers; the
squared-weight studies of 20 to 22 November one by one; anything about patterns with no state of the whole.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — one statement for every recorded excess | **Status:** Successful | Exhaustive under one state of the whole, Theorem K for kind (a), every row classed, no row fits none |
| Local direction — the quantum question on the recorded laws | **STOP** (obstruction learned, with one opening) | Every excess is reweighting, a joint response or supplied; but at fixed settings, which is all the model has, some excesses are hidden and one is inside the quantum set |
| Broader exploration — what an agent inside the model could test | Unmapped | Whether any process the laws make can play a free sender (key a birth to a value) is the question the result leaves |
| Long-term goal — G18 Comparing growth laws | Obstruction learned | The recorded laws give quantum-set tables only with a supplied change read, or with reweighting that an outside free sender exposes |

**Next step:** Research directions — #1 proposed; the choice is the coordinator's

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Is the fixed-settings standard the model's own? An inside sender | 3/3 — decides whether the hidden excesses count | 2/3 — the test is Theorem K's signal; what is open is whether a law can key a birth | Write the conditions under which a law-made process keys a birth to a value (the record says values change no birth; check every recorded law) → one that does, or an argument that none can | Proposed |
| 2 | Theorem K for three readers and with a signal size | 2/3 — closes the three-reader forbidding table and gives a bound like LOCAL-EDIT-POLICIES' | 3/3 — the proof's steps extend | Extend the decomposition to three readers; bound the signal by the excess → a proof or a counterexample | Proposed |
| 3 | Open the census parts for H2 | 1/3 — completes the classification | 3/3 — the code exists | Check each census part's setting-birth inputs against its record → all inside, or a row outside Theorem K | Proposed |

1. If nothing inside the model can key a birth to a value, the hidden excesses of kind (a) are, for every inside
   reader, no-signalling tables, one of them inside the quantum set; whether to count them depends on a standard the
   model does not supply. That is the one opening this stop leaves.
2. and 3. are completions.

**Intuitions (exact links, not evidence).**
- *The detection loophole, made by the counting.* Kind (a) is the literature's local model with setting-dependent
  rejection (Pearle 1970; Gisin and Gisin 1999), the rejection here being the counting's weight. Theorem K is the
  statement that such a model is unmasked by a free choice of setting; the cheapest test of any new excess is a keyed
  sender.
- *No global section.* A table is nonlocal in the literature exactly when its pieces have no common state of the whole
  (Abramsky and Brandenburger 2011); the six rows outside H1 are that case, which is why the other thread's challenge is
  aimed at the one place a fourth kind could live.

**Corrections:** none.
**Goals:** checkpoint row added (G18; obstruction learned, with one opening); no goal changed.
**Assumptions:** A296 entered (the free-sender standard and one state of the whole) with a history line saying the free
sender is outside H0; A240 gets a history line (Theorem K's consequence for counting from the finish).
**Scaffolds:** the free-sender standard (against fixed settings: the result names what changes, the whole-stage 9/4 and
the four-type 20/9 then stand as hidden excesses); the declared records of each study (against the fuller record:
SETTING-AS-REREAD's 20/9 moves to a record changed); the random models' alphabets and seed (a check of the algebra, not
of the model). The classification is about the record under these standards; the theorem is about any model with its
hypotheses.
**Advisor:** used for the coordinator's choice of this direction and on the draft (no counterexample to Theorem K; its
gaps, the rows outside H1, four missed rows, the widened kind (b), the narrowed A240 claim and the outside-agent point
were all checked against the record and adopted; its H5-free route is unverified, the random check without H5 agrees).
