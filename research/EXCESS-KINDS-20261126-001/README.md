# Three kinds: one statement that classes every recorded table above the classical bound

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

Epic `EXCESS-KINDS-20261126-001`, under G18, at the coordinator's pick (the advisor's direction 3, consulted at
extra-high effort for the coordinator). An argument with a classification of the record; the advisor reviewed the
draft; referee pending. [Decision](decision.md) · [inventory](inventory.md) · [checks](checks.py)
([output](checks_output.txt)) · advisor: [directions](advisor_answer_1.md), [draft](advisor_answer_2.md)

> **Revised after the advisor's review, 26 November 2026** ([question](advisor_question_2.md), [answer](advisor_answer_2.md)):
> the proof's gaps written out; three rows moved outside H1 (patterns with no state of the whole) and four rows the first
> inventory missed added; kind (b) widened to records; the claim about counting from the finish narrowed; and the point
> that the free sender is an agent outside H0 made the centre of the result.

## The question

Today's studies found, one by one, that each table above the classical bound in the record either needs a weighting
that reads the settings, or a response to both settings that signals, or something we supply. The coordinator asked
for one statement that classes every such table, with its hypotheses and its definition of a free sender stated, and a
stop at a row that fits none.

## The statement

**Hypotheses.**
- **H0. Laws that read no values.** Every birth is decided by the meeting pattern (which knots share which distinctions)
  and never by a value; both knot laws (parity, not-all-equal) and the record's other value-blind laws.
- **H1. A state of the whole.** Every table is computed from the allowed states of finished structures, one finished
  structure (or family of them) per pair of settings, with each reader's outcome a function of its own record. (This
  excludes patterns whose parts have allowed states and whose whole has none, which the other thread is testing.)
- **The reading.** A table is read from its weighting of states as chances (counting from the finish, counting from
  the start, or another weighting the record names).

**Definition (free sender).** A reader is a free sender when its setting may be any function of its own visible
record: the old values its record holds, before its setting acts. A table **signals** when some free sender's choice
changes the distribution of the other reader's complete record (the declared record of each study: its holders'
distinctions and the fresh distinctions of its own setting births). This is the standard quantum theory meets: a
measuring party may choose its setting from its own earlier outcomes, and the other party's statistics do not change.
Fixed settings, chosen independently of every state, are the special case of constant functions.

**A free sender is outside H0.** Keying a setting birth to a value is exactly what no law under H0 does: "values change
no birth" (`REVIEW-LEADS-20261123-001E`, result, lines 72–75). In the model the settings are births supplied from
outside, and nothing inside it can key one to a value. So signalling to a free sender is a test only an outside agent
can run, as an experimenter runs it in quantum theory. The register entry A296 holds this standard as a choice.

**Claim.** Under H0 and H1, every table whose CHSH value (or Mermin-type value) exceeds the classical bound is of at
least one of three kinds:

- **(a) Separate responses with reweighting.** Each reader's births depend only on its own setting and the old state,
  bring their own fresh distinctions, and multiply an old state's weight by their number of completions; the weighting
  then depends on the settings through that factor (counting from the finish). The table is a local model with partial
  rejection. **Theorem K** below: where each reader's factor is set by its own setting and its own visible old values
  and no setting completes an old value the other setting excludes, a free sender always detects the excess.
- **(b) A joint response.** A birth, a rule, a whole-round event or a record depends on both settings: a shared birth,
  all-or-none funding, a join that forbids for both, a later rule holding both sides' setting distinctions, or a record
  that holds a distinction the other side's setting birth brings. Wherever the record checked, such a table signals, at
  fixed settings or once a free sender may condition on what it sees.
- **(c) Something supplied.** The weighting is not a counting of the states of a structure the laws made, or the
  settings are not chosen: a supplied order of construction, a supplied sign or signed law, a supplied reading (signed
  counts, squared sums, squared weights with a read of a change), supplied keepers, or settings that are distinctions
  of the state on which the table is conditioned.

**Why the three kinds exhaust the cases (proved).** Take the old structure common to the four histories and push each
table onto its old states λ: P(α, β | a, b) = Σ_λ p_ab(λ) P(α, β | a, b, λ). If p_ab(λ) is the same nonnegative
weighting for every setting pair and the response given λ is a product of one reader's response (to its own setting)
and the other's, this is a local model and CHSH is at most 2 (Bell; Fine 1982). With separate responses (each reader's
births depend on its own setting and λ and hold fresh distinctions of their own) the response is a product and
p_ab(λ) ∝ p(λ) t_1(a, λ) t_2(b, λ), with t_i the completions: an excess then needs the factors to vary, which is kind
(a). Without separate responses some birth, rule or record depends on both settings: kind (b). A weighting that is
not a nonnegative counting of states, chances not read from one, or settings that are not chosen, is kind (c).

## Theorem K (kind a): a free sender detects every excess of separate responses

**Setting.** A common old structure with allowed old states; finished structures for the four setting pairs (a, b).
Reader 1's visible old values v and reader 2's u are the old values in their records. Counted from the finish, the
weight of a finished state is a product:

W_ab(state) = [old state] · g_1(a, v, r_1) · g_2(b, u, r_2),

where r_i are reader i's fresh values and g_i ≥ 0 counts reader i's completions (H2: each reader's births take inputs
only from its own record and bring fresh distinctions of its own, which no other birth holds). Write μ(v, u) for the
number of old states with visible values (v, u), t_1(a, v) = Σ_r g_1(a, v, r), F_1(α | a, v) = Σ_{r: outcome α} g_1,
and the same for reader 2. (H5) For each v, t_1(0, v) > 0 exactly when t_1(1, v) > 0, and the same for reader 2.

A **free sender** is a reader whose setting is any function π of its own visible old values. **No free signalling**:
for every such π of reader 1 and every b, the distribution of reader 2's complete record (u, r_2) is the same; and the
same with the readers exchanged.

**Claim.** Under H2 and H5, no free signalling implies the fixed-setting table P(α, β | a, b) is a local model; so its
CHSH value is at most 2.

**Proof.**
1. Let D = {v : t_1(0, v) ≠ t_1(1, v)} and c_v = t_1(·, v) for v ∉ D; likewise D' and c'_u for reader 2.
2. Fix b and a policy; reader 2's record measure is Σ_v s_v μ(v, u) g_2(b, u, r_2), with s_v = t_1(π(v), v). Changing
   π at one v ∈ D changes s_v between two distinct values; the normalized measure (X + sY)/(x + sy) is the same for both
   exactly when Y·x = X·y at every record entry, where Y is slice v's measure and X the rest's. The rest depends on the
   policy at the other values, so vary the policy at a second v′ ∈ D as well and take the difference: every slice of
   D, and the aggregate of the values outside D, has one common profile. So μ(v, u) = m_v k(u) for every v ∈ D on the
   values u where t_2(b, u) > 0; by H5 those values are the same for b = 0 and b = 1, so k is one profile. And
   Σ_{v ∉ D} c_v μ(v, u) is proportional to k(u).
3. By the same argument for reader 2: μ(v, u) = n_u k'(v) for u ∈ D', and Σ_{u ∉ D'} c'_u μ(v, u) ∝ k'(v). On D × D'
   the two forms agree, so the profiles can be scaled with k = n on D' and k' = m on D. If μ vanishes on D × D', the D
   values or the D' values carry no weight wherever the other reader's factor varies, and the table is a product (or
   step 5 with τ_D or σ_D set to 0).
4. Write 𝒜_D(α | a) = Σ_{v∈D} m_v F_1(α | a, v) (total τ_D(a)), 𝒜_N(α | a) = Σ_{v∉D} k'(v) F_1(α | a, v) (total τ_N,
   setting-free), and ℬ_D, ℬ_N with totals σ_D(b), σ_N for reader 2. Then the table's numerator is
   T = 𝒜_D⊗ℬ_D + 𝒜_D⊗ℬ_N + 𝒜_N⊗ℬ_D + 𝓜,
   where 𝓜 = Σ_{v∉D, u∉D'} μ(v, u) F_1 F_2 has setting-free weights μ c c'. Step 2's proportionality gives 𝓜's
   reader-2 marginal κ ℬ_N for a constant κ, and evaluating Σ_{v∉D} c_v μ(v, u) at a value u ∈ D' gives κ = τ_N (if D'
   carries no weight, κ is fixed by the total instead); step 3 likewise gives its reader-1 marginal σ_N 𝒜_N, and its
   total is τ_N σ_N.
5. So P = T / ((τ_D(a) + τ_N)(σ_D(b) + σ_N)), which is the table of this local model: reader 1 tosses its own coin,
   "own" with chance τ_D(a)/(τ_D(a) + τ_N), and then answers from 𝒜_D(· | a) normalized, ignoring the shared variable;
   otherwise it answers from the shared variable of the local model 𝓜/(τ_N σ_N); reader 2 likewise. ∎

**What it says.** Every excess of separate responses is paid for by the counting's reweighting of old states. A reader
who keys its setting to what it sees changes the other reader's record. So the third-holder ceiling
4(1 + ρ²)/(1 + ρ)² is the size of an excess that a free sender always detects. Counting from the start makes every
t constant, so D = D' = ∅ and the table is local at once (the two-countings lemma).

**Checks.** 254 random product-form models with H5 above CHSH 2 (largest 17/6) and 1,693 without it (largest 4): every
one lets a free sender change the other record; 95 and 177 models with no free signalling and every part of the
decomposition weighted were drawn, and none exceeds 2 (`checks.py random`, seed 20261126; floats with a 1e-9 margin). On
the seven-knot structure (THIRD-HOLDER B, 19/9 hidden) a free sender changes the other record by exactly 1/9
(`checks.py seven`). The advisor gives a second route on which H5 is not needed (unverified; the random check without
H5 agrees). Known nearby: local rejection as factorisable measurement dependence (Pearle 1970; Gisin and Gisin 1999;
Hall 2011); this exact statement was not found.

**Where it does not reach.** H2 fails when a reader's birth takes an input outside its own record (then the factor
depends on values the reader cannot key to); none such was found among the rows read (the advisor and this study);
the census parts were not opened. Two readers with two settings only: the three-reader forbidding table is not
covered. It gives no size for the signal, unlike the funding preparations' "an excess δ forces a signal of at least
δ" (LOCAL-EDIT-POLICIES).

## The record, row by row

The [inventory](inventory.md) lists 63 rows of recorded tables above the bound (several rows hold more than one value),
with their records. Under H1 every one is of at least one kind and none fits none. Six rows lie outside H1: patterns
whose parts have allowed states and whose whole has none (the magic-square and perfect-agreement tables of
FOUR-READINGS A, an advisor's sketch, and the tables of `NO-WHOLE-STATE-20261126-001` and `EVENTUAL-R-20261126-001`);
they are the other thread's, and this statement says nothing about them.

| Kind | Rows | What decides it | What signals |
| --- | --- | --- | --- |
| (a) separate responses, reweighted | The settings-as-births line: 19/9, 20/9, 37/18, 55/27, 61/30, 31/15, 109/54, 127/63 and its family, 68/25, 260/81 (THIRD-HOLDER, SETTING-AS-REREAD, REREAD-BIRTHS, ONE-PARENT-REREAD, REVIEW-LEADS C, TWO-COUNTINGS E1); the forbidding-edit tables 4 and 9/4 (FORBID-EDITS) | Counting from the finish multiplies an old state's weight by each reader's completions (1 or ρ); counted from the start every table of the settings-as-births line is exactly 2 (TWO-COUNTINGS); under the forbidding edits counting from the start is undefined, and renormalised it is the finish | Where tested, a keyed setting changes the other record: 1/9 (REVIEW-LEADS C), 2/9 (the 11-rule and 18-knot structures), and **1/9 on the seven-knot structure, checked here**; Theorem K says it always does under H2 and H5. With outright rejection (FORBID-EDITS) the table is local once the rejection is counted as an outcome |
| (a·open) the same, a record changed | 8/3 (REVIEW-LEADS C), 194/91 and 23/10 (128 of the 512 sign assignments), 7/3 (E3); SETTING-AS-REREAD's 20/9 too, if its first observer's record is read in full (the second's setting moves (s1, s2), which the first observer's knots hold, by 1/3) | As (a) without the equal totals that hide the far setting | At fixed settings |
| (b) a joint response | 9/4 and 4 (WHOLE-STAGE-SETTINGS), 9/4 (LOCAL-EDIT-POLICIES), 7/3 and 5/2 (BEYOND-REJECTION), 17/6, 11/4, 5/2, 5/2 (E4–E7), 61/30 (the six-rule counterexample), 173/86 (CONTACT-FORBID) | All-or-none funding of a whole round, a birth or rule holding both sides' setting distinctions, a shared birth, or a record holding the other side's setting distinction (E6) | Every one: at fixed settings (E4–E7, the 61/30, CONTACT-FORBID, the closure) or under a free sender (the funding tables; LOCAL-EDIT-POLICIES proves an excess δ forces a signal of at least δ there) |
| (c) supplied | Every table read with a change and squared weights (Mermin 3, GHZ 64/64, the heralded tables, the coherent reading of TWO-KNOTS-ONE-DECISION; its two central readings are joint rules that signal), every signed reading (the reordering sign, the signed laws, the side-sign R1 and R2, signed counts), supplied orders of construction (104/45, 6117/2470), settings that are distinctions of the state (ENTANGLEMENT-READ, FOUR-READINGS), and supplied joint rules or prescriptions (the pre-knot contexts, calibration models) | The weighting or the reading is not a counting of the states of a structure the laws made | Some signal (the selector tables, writable state); the change-read tables do not |

**The main result: inside the model, the record already has tables above 2 that no reader can use to signal; only an
outside agent, keying a setting to a value, exposes them.** No law under H0 keys a birth to a value, so inside the model every
setting is a fixed, supplied birth, and fixed settings are what remain.
- **Kind (b), beyond quantum theory.** At fixed addresses the whole-stage 9/4 hides every complete record, and its
  correlations (1, 1, 1, 3/4) lie outside the quantum set: three perfect correlations force the fourth in quantum theory,
  and the Tsirelson–Landau–Masanes test gives 3·arcsin 1 − arcsin(3/4) ≈ 3.864 > π (checked against the record's actual
  tables, (7/8, 0, 0, 1/8) three times and (13/16, 1/16, 1/16, 1/16), by the advisor and here). It is made by the
  funding law with a supplied start and weighting, and it is the same under both countings.
- **Kind (a), inside the quantum set.** The four-type 20/9 (REVIEW-LEADS C) has correlations 5/9, 5/9, 5/9, −5/9 with
  fair single values (checked from the record's own formula for it, [check_20_9.txt](check_20_9.txt)); 4·arcsin(5/9) ≈
  2.36 < π, so a quantum state reproduces its correlations at fixed settings (a two-reader state of visibility about
  0.79 does). The 18-knot structure reaches 20/9 in the same family; its tables were not rebuilt here.
- **What separates them.** A free sender: under it both kinds signal (Theorem K for (a), the funding proofs for (b)),
  while quantum theory does not. But a free sender keys a setting to a value, which is outside H0. So the
  classification's force comes from A296, a standard set by an agent the model does not contain.

**Counting from the finish would let anything able to key a birth to a value detect every excess of separate
responses**, under Theorem K's hypotheses: two readers with two settings each, H2 for the declared records, a keyed
setting read with its weight pooled or normalised per setting (A226), and signalling read in the complete declared
record. Counting from the start gives exactly 2 on every table of the settings-as-births line. Neither counting is made
by the laws (TWO-COUNTINGS), and the whole-stage 9/4 signals to a free sender under both, so this is a reason to prefer
counting from the start for kind (a) only, not a proof.

**Where the quantum-looking tables live.** Apart from kind (a) at fixed settings, every recorded table above the bound
that lies inside the quantum set, with no signal recorded beyond fixed settings, is of kind (c) with a read of a change
and squared weights, as it must be by construction (the squared-weight chances of one state, each reader's questions
on its own distinctions). Signalling tests beyond fixed settings are recorded for none of them (rows 15, 16, 22, 44, 46
have none; row 59 is conditional on a flag fixed before the settings). With the second question supplied, the
squared-weight chances of the positive uniform preparation with real questions are counts of pairs of ordinary words
with no negative weight (`FREEDOM-CLOCKS-AND-BIRTHS-20261120-001A`, referee pending; the signed law and the quarter-turned
question of rows 43 and 44 are not covered). So what is missing is better put as "a reader's question about a change"
than as "a sum with cancelling weights".

**What H1 excludes.** H1 asks for one state of the whole. In the literature a table is nonlocal exactly when its local
pieces fit together pairwise but admit no state of the whole (Abramsky and Brandenburger 2011, the sheaf-theoretic
form of Fine's theorem). A pattern whose parts have allowed states and whose whole has none is that situation, so it is
the one place a fourth kind could live, and the other thread's challenge is aimed at it. This statement says nothing
there.

## Not shown

- That every recorded kind-(a) structure satisfies H2 (inputs of a setting birth inside the reader's record): checked
  for the seven-knot structure here, read for the 11-rule structure (its third option is outside the record but forced
  opposite to x1, so its factor is constant) and recorded for the 18-knot and REVIEW-LEADS C structures; the census
  parts (REREAD-BIRTHS, ONE-PARENT-REREAD) not opened.
- The squared-weight studies of 20 to 22 November one by one (NEWBORN-TABLES, CALIBRATIONS-CLOCKS, SPLIT-KNOT-METER,
  SHARED-DONOR, FOUR-READINGS B, THREE-READERS B, TWO-KNOTS B): kind (c) as a group, not opened.
- A general theorem for kind (b): its rows signal case by case, with a proof only for the funding preparations.
- Tables never recorded, and laws that read values (they are outside H0).
- Theorem K was tested on 254 random product-form models above 2 (all signal); that is a check of the algebra, not
  evidence about the model.
