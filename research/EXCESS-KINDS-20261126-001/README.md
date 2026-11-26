# Three kinds: one statement that classes every recorded table above the classical bound

Epic `EXCESS-KINDS-20261126-001`, under G18, at the coordinator's pick (the advisor's direction 3, consulted at
extra-high effort for the coordinator). An argument with a classification of the record; the advisor is consulted on
the draft; referee pending. [Inventory](inventory.md) · [checks](checks.py)

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
changes the distribution of the other reader's complete record. This is the standard quantum theory meets: a measuring
party may choose its setting from its own earlier outcomes, and the other party's statistics do not change. Fixed
settings, chosen independently of every state, are the special case of constant functions.

**Claim.** Under H0 and H1, every table whose CHSH value (or Mermin-type value) exceeds the classical bound is of at
least one of three kinds:

- **(a) Separate responses with reweighting.** Each reader's births depend only on its own setting and the old state,
  bring their own fresh distinctions, and multiply an old state's weight by their number of completions; the weighting
  then depends on the settings through that factor (counting from the finish). The table is a local model with partial
  rejection. **Theorem K** below: where each reader's factor is set by its own setting and its own visible old values
  and no setting completes an old value the other setting excludes, a free sender always detects the excess.
- **(b) A joint response.** Some birth, or a whole-round event, depends on both settings (a shared birth, all-or-none
  funding, a join that forbids for both). Wherever the record checked, such a table signals, at fixed settings or once
  a free sender may condition on what it sees.
- **(c) Something supplied.** The weighting is not a counting of the states of a structure the laws made: a supplied
  order of construction, a supplied sign or signed law, a supplied reading (signed counts, squared sums, squared weights
  with a read of a change), supplied keepers.

**Why the three kinds exhaust the cases (proved).** Take the old structure common to the four histories and push each
table onto its old states λ: P(α, β | a, b) = Σ_λ p_ab(λ) P(α, β | a, b, λ). If p_ab(λ) is the same nonnegative
weighting for every setting pair and the response given λ is a product of one reader's response (to its own setting)
and the other's, this is a local model and CHSH is at most 2 (Bell; Fine 1982). With separate responses (each reader's
births depend on its own setting and λ and hold fresh distinctions of their own) the response is a product and
p_ab(λ) ∝ p(λ) t_1(a, λ) t_2(b, λ), with t_i the completions: an excess then needs the factors to vary, which is kind
(a). Without separate responses some birth depends on both settings: kind (b). A weighting that is not a nonnegative
counting of states, or chances not read from one, is kind (c).

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
   π at one v ∈ D changes s_v between two distinct values. (X + sY)/(x + sy) is the same for two values of s exactly
   when Y/y = X/x (or Y = 0). So for every v ∈ D the measure μ(v, ·) is proportional, on the support of g_2(b, ·, ·),
   to the rest; by H5 the supports for b = 0 and b = 1 agree, so μ(v, u) = m_v k(u) for one profile k, for every v ∈ D,
   and Σ_{v ∉ D} c_v μ(v, u) is proportional to k(u) as well.
3. By the same argument for reader 2: μ(v, u) = n_u k'(v) for u ∈ D', and Σ_{u ∉ D'} c'_u μ(v, u) ∝ k'(v). On D × D'
   the two forms agree, so the profiles can be scaled with k = n on D' and k' = m on D.
4. Write 𝒜_D(α | a) = Σ_{v∈D} m_v F_1(α | a, v) (total τ_D(a)), 𝒜_N(α | a) = Σ_{v∉D} k'(v) F_1(α | a, v) (total τ_N,
   setting-free), and ℬ_D, ℬ_N with totals σ_D(b), σ_N for reader 2. Then the table's numerator is
   T = 𝒜_D⊗ℬ_D + 𝒜_D⊗ℬ_N + 𝒜_N⊗ℬ_D + 𝓜,
   where 𝓜 = Σ_{v∉D, u∉D'} μ(v, u) F_1 F_2 has setting-free weights μ c c'. Step 2's proportionality gives 𝓜's
   reader-2 marginal τ_N ℬ_N, step 3's its reader-1 marginal σ_N 𝒜_N, and its total τ_N σ_N.
5. So P = T / ((τ_D(a) + τ_N)(σ_D(b) + σ_N)), which is the table of this local model: reader 1 tosses its own coin,
   "own" with chance τ_D(a)/(τ_D(a) + τ_N), and then answers from 𝒜_D(· | a) normalized, ignoring the shared variable;
   otherwise it answers from the shared variable of the local model 𝓜/(τ_N σ_N); reader 2 likewise. ∎

**What it says.** Every excess of separate responses is paid for by the counting's reweighting of old states. A reader
who keys its setting to what it sees changes the other reader's record. So the third-holder ceiling
4(1 + ρ²)/(1 + ρ)² is the size of an excess that a free sender always detects. Counting from the start makes every
t constant, so D = D' = ∅ and the table is local at once (the two-countings lemma).

**Where it does not reach.** H2 fails when a reader's birth takes an input outside its own record (then the factor
depends on values the reader cannot key to); H5 fails under outright rejection at one setting only (forbidding);
signalling here is about complete records.

## The record, row by row

The [inventory](inventory.md) lists 59 recorded tables above the bound with their records; every one is of at least one
kind, and none fits none.

| Kind | Rows | What decides it | What signals |
| --- | --- | --- | --- |
| (a) separate responses, reweighted | The settings-as-births line: 19/9, 20/9, 37/18, 55/27, 61/30, 31/15, 109/54, 127/63 and its family, 68/25, 260/81 (THIRD-HOLDER, SETTING-AS-REREAD, REREAD-BIRTHS, ONE-PARENT-REREAD, REVIEW-LEADS C, TWO-COUNTINGS E1); the forbidding-edit tables 4 and 9/4 (FORBID-EDITS) | Counting from the finish multiplies an old state's weight by each reader's completions (1 or ρ); counted from the start every one of them is exactly 2 (TWO-COUNTINGS) | Where tested, a keyed setting changes the other record: 1/9 (REVIEW-LEADS C), 2/9 (the 11-rule and 18-knot structures), and **1/9 on the seven-knot structure, checked here**; Theorem K says it always does under H2 and H5. With outright rejection (FORBID-EDITS) the table is local once the rejection is counted as an outcome |
| (a·open) the same, a record changed | 8/3 (REVIEW-LEADS C), 194/91 and 23/10 (half the sign assignments), 7/3 (E3) | As (a) without the equal totals that hide the far setting | At fixed settings |
| (b) a joint response | 9/4 and 4 (WHOLE-STAGE-SETTINGS), 9/4 (LOCAL-EDIT-POLICIES), 7/3 and 5/2 (BEYOND-REJECTION), 17/6, 11/4, 5/2, 5/2 (E4–E7), 61/30 (the six-rule counterexample), 173/86 (CONTACT-FORBID) | All-or-none funding of a whole round, a birth or rule holding both sides' setting distinctions, a shared birth | Every one: at fixed settings (E4–E7, the 61/30, CONTACT-FORBID, the closure) or under a free sender (the funding tables; LOCAL-EDIT-POLICIES proves an excess δ forces a signal of at least δ there) |
| (c) supplied | Every table read with a change and squared weights (Mermin 3, magic square 9/9, GHZ 64/64, the heralded tables), every signed reading (the reordering sign, the signed laws, the side-sign R1 and R2, signed counts), supplied orders of construction (104/45, 6117/2470), settings that are distinctions of the state (ENTANGLEMENT-READ, FOUR-READINGS), and supplied joint rules or prescriptions (the pre-knot contexts, calibration models) | The weighting or the reading is not a counting of the states of a structure the laws made | Some signal (the selector tables, writable state); the change-read tables do not |

**The free sender decides one row's kind, and the record already holds a table outside the quantum set (as the advisor
warned).** At fixed addresses the whole-stage 9/4 hides every complete record, and its correlations (1, 1, 1, 3/4) lie
outside the set of quantum correlations: three perfect correlations force the fourth in quantum theory, and the
Tsirelson–Landau–Masanes test gives 3·arcsin 1 − arcsin(3/4) ≈ 3.864 > π (checked by hand and in one line of arithmetic).
So under fixed settings the record has a no-signalling table beyond quantum theory, made by the funding law with a
supplied start and weighting. Under the free-sender definition it signals (proved for that preparation). The statement
adopts the free-sender definition because quantum theory meets it; the choice is entered as a challengeable assumption.

**Counting from the finish signals wherever it gives an excess of separate responses.** This follows from Theorem K and
is the main new thing here: the program's working counting (A240) produces the settings line's hidden excesses only
together with a free sender's signal, while counting from the start gives exactly 2 on every one of them. Neither
counting is made by the laws (TWO-COUNTINGS), so this is a reason to prefer counting from the start, not a proof.

**Where the quantum-looking tables live.** Every recorded table that is above the bound, signals under no test, and lies
inside the quantum set is of kind (c) with a read of a change and squared weights. With that second question supplied,
the squared-weight chances are counts of pairs of ordinary words with no negative weight
(`FREEDOM-CLOCKS-AND-BIRTHS-20261120-001A`, referee pending). So what is missing is better put as "a reader's question
about a change" than as "a sum with cancelling weights".

**What H1 excludes.** H1 asks for one state of the whole. In the literature a table is nonlocal exactly when its local
pieces fit together pairwise but admit no state of the whole (Abramsky and Brandenburger 2011, the sheaf-theoretic
form of Fine's theorem). A pattern whose parts have allowed states and whose whole has none is that situation, so it is
the one place a fourth kind could live, and the other thread's challenge is aimed at it. This statement says nothing
there.

## Not shown

- That every recorded kind-(a) structure satisfies H2 (inputs of a setting birth inside the reader's record): checked
  for the seven-knot structure here, recorded for the 11-rule, 18-knot and REVIEW-LEADS C structures; the census parts
  (REREAD-BIRTHS, ONE-PARENT-REREAD) not run.
- A general theorem for kind (b): its rows signal case by case, with a proof only for the funding preparations.
- Tables never recorded, and laws that read values (they are outside H0).
- Theorem K was tested on 254 random product-form models above 2 (all signal); that is a check of the algebra, not
  evidence about the model.
