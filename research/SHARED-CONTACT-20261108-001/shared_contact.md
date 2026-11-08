# Which shared contacts persist

Epic `SHARED-CONTACT-20261108-001` (program foundations), 2026-11-08.

## The question

- **Where it comes from.** It is the selected next step of `PROCESS-CONTACT-20261108-001`, started at once under the standing
  mandate.
  - **The finding it starts from.** A contact that is a cell of two rings, as the contact gate's shared identity asks, and combines
    the rings' proposals binds both rings at every lag in only 44 of 128,128 configurations, at rings of up to 5 + 6 cells.
  - **Lag 1.** There it fails exactly when its own past fixes a proposal.
- **The question.** Does a contact that does not read itself persist more often? And is the rarity a property of small rings?
- **Two families.**
  - **Proposals** (A31): c(t + 1) = g(f_A(a_{m−1}, c, a_1), f_B(b_{n−1}, c, b_1)).
  - **Self-blind:** c(t + 1) = h(a_{m−1}, a_1, b_{n−1}, b_1), which both rings still read but which does not read itself. Its
    parities are u(a_{m−1}, a_1) + v(b_{n−1}, b_1).

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **At lag 1, binding is decided exactly.** A proposal-combining contact binds both rings at lag 1 exactly when its combiner is XOR or XNOR and neither rule is canalizing at its centre. A self-blind contact binds at lag 1 exactly when its 4 × 4 table has no constant row and no constant column: 22,874 of the 65,536 laws, and the parities u + v exactly when u and v are nonconstant. For linear rings with an affine contact, binding at lag T is the contact's row of M^T meeting both rings. | proved; computed exhaustively on small rings | A |
| 2 | **Not reading itself spreads persistence but barely raises it.** Self-blind parities bind at every lag in 6.4% of 68,992 configurations, against 4.5% for proposal parities on the same rings; without the two rules whose rings never read the contact, 4.2% against 4.7%. They persist on 157 (rule, size) pairs against 22. The contact's past comes back to it through the ring cells that read it: rules canalizing in a neighbour input persist in 1.1% of configurations, the others in 5.8%. | exploratory experiment (H1 fails) | B |
| 3 | **Persistence grows with the rings.** From 3 + 4 to 8 + 9 cells the fraction binding at every lag rises from 1.1% to 20.5% for proposal parities, and from 3.6% to 26.0% for self-blind parities, exact where the dynamics repeats within 4,096 lags. The growth slows at the largest sizes. | exploratory experiment (H1 holds for self-blind, fails narrowly for proposals) | C |

## Answer

- **The rarity was a small-ring effect.** `PROCESS-CONTACT-20261108-001` found persistent shared contacts rare on rings of up to 5
  + 6 cells. On rings of 8 and 9 cells, a fifth to a quarter of parity contacts shared by identity bind both rings at every lag. So
  shared identity and persistence are compatible.
- **What not reading itself buys.** A contact that does not read its own value binds at the first step whenever its parts are
  nonconstant. It persists on many more rules, and it is ahead by 2 to 8 points at every size. It is not the main cause of
  persistence.
- **What decides.** The contact's own past returns to it two steps later, through the ring cells that read it. Rules canalizing in
  a neighbour input then let that past settle what the contact reads, and they rarely persist.

## Reading

**Interpretation, not a theorem.**
- **For the contact gate across time.** The gate's items now meet in one place. A contact that is a cell of both rings is shared
  by identity and essential to both recurrences, since each ring's update reads it. When it binds both rings at every lag, it is
  also two-sided essential, lost when either ring is erased, irreducibly joint (a knot through c(T)), and persistent across time.
  On rings of 8 and 9 cells about a quarter of parity contacts do all of this.
- **Feedback is not fatal.** Small rings return the contact's influence to it quickly and lose their own first rows. Larger rings
  carry more of their own past, and the contact can keep needing both.
- **In line with double-cycles.** Boolean automata double-cycles have fewer attractors than isolated cycles: a shared node makes the
  joint dynamics forget more. This census measures how much each ring's past still matters at the shared node, and that grows with
  ring size.

## Stress test

One size past each computed claim (`stress_test.py` here).

| Claim | One size past | Result |
| --- | --- | --- |
| Theorem 1 on rings to 4 + 5 cells (A) | 5 + 6 cells: every class with itself and 12 random partners, all 16 combiners | pass: 18,304 maps |
| Theorem 2, all laws at 3 + 4 cells (A) | 4 + 5 cells, 3,000 random laws and ring rules | pass |
| Ticket B's comparison at four sizes | ticket C extends it to 8 + 9 for u = v | the self-blind family stays ahead by 2 to 8 points |
| Ticket C's trend to 8 + 9 cells | 9 + 10 cells (262,144 joint states), both families: SHARED-CONTACT-S1 in `docs/LONG_RUNNING.md`, `stress_test_nine.json` | levelling off: 21.6% of proposal parities and 27.0% of self-blind parities bind at every lag (20.5% and 26.0% at 8 + 9), 27 and 51 rules; undecided 13 and 104 of 176 and 1,232; the lag-1 criteria hold on all |

## Literature and provenance

- **Sources.** Canalizing functions (Kauffman, 1969), and Boolean automata double-cycles (Demongeot, Noual, Sené and coauthors;
  Melliti, Noual, Regnault, Sené and Sobieraj, arXiv 1310.5747; the 2022 chapter, arXiv 2204.10686).
- **Classification.**
  - **Ticket A.** Known-with-delta: elementary arguments, read as the contact gate at lag 1.
  - **Tickets B and C.** New as far as found: the census of shared contacts by binding and persistence, and its growth with ring
    size.

## Workspace assumptions

- **Relied on.** A3, A6, A30 (two-time knots), A32 (two-sided essentiality across time is binding).
- **Challenged.** A31, that a shared contact combines its two rings' proposals. The self-blind family persists only a few points
  more often, with the same growth, so the reading that rested on A31 stands, sharpened by the size trend. A31 is confirmed.
- **Taken by default.** Both rings alike in tickets B and C. Mixed rings were run only at 3 + 4 cells, in
  `PROCESS-CONTACT-20261108-001B`.

## Ratio

Since the epic opened:
- **Substantive.** Three evidence families changed conclusions: A (a proof), B and C (exploratory). The size trend changed the
  reading of the previous epic.
- **Administrative.** This note and the closure.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — which shared contacts persist | **Status:** Successful | Lag 1 decided exactly; persistence grows to a fifth or a quarter at 8 + 9 cells |
| Local direction — one contact between processes | Continue | Its gate passes across time for a sizable fraction; composing two contacts is the open step |
| Broader exploration — G5 with G1 | Known alternatives | Two contacts across time; why some rules persist |
| Long-term goal — G5 Dynamics (question 4) | Capability gained | The full contact gate can pass across time, with the contact a cell of both loops |

**Corrections:** none. **Goals:** a G5 checkpoint (capability gained). **Assumptions:** A31 confirmed.

- **What the attempt leaves open.**
  - Whether the fraction saturates: at 9 + 10 cells it rose by about one point in each family (SHARED-CONTACT-S1).
  - Which rules persist, and why.
  - Mixed rings at large sizes.
- **The missing bridge to the program's composed topology.** Two complete contacts between processes that coexist and compose: a
  chain of three rings, A–B–C, joined by two shared contacts.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Two contacts across time (G5, with G1) | 3/3 — Major | 2/3 — Testable | Three rings in a chain sharing two contacts; when both bind at every lag, does the chain bind its ends through the middle ring? → a composition law across time, or its failure | Selected · not started |
| 2 | Why some rules persist (G5) | 2/3 — Substantial | 1/3 — Stated | Relate persistence to how a rule reads its neighbours (canalization, sensitivity) → a criterion that predicts ticket C's lists | Alternative · deferred |
| 3 | Does persistence saturate? (G5) | 1/3 — Incremental | 3/3 — Ready | SHARED-CONTACT-S1 at 9 + 10, then 10 + 11 → the trend | S1 done: levelling off near a fifth and a quarter |
| 4 | Learning a rule from its knots (G16) | 2/3 — Substantial | 1/3 — Stated | Carried from `TIME-KNOTS-20261107-001` | Alternative · deferred |

1. **Two contacts across time.**
   - **Payoff 3.** The program's composed topology starts from two complete contacts that coexist and compose by a native law. A
     chain of processes whose two contacts persist and compose would carry the contact-network gate across time.
   - **Concreteness 2.** The census code extends to three rings. Composition needs a declared test: whether the far rings' pasts
     meet in the knots of one contact's future through the middle ring.
   - **Uncertainty.** Whether binding through a middle ring survives its feedback, and whether composition is native or drawn.
2. **Why some rules persist.**
   - **Payoff 2.** It would explain the census.
   - **Concreteness 1.** No method yet.
3. **Saturation.** SHARED-CONTACT-S1 found the growth levelling off at 9 + 10 cells.
4. **Learning a rule from its knots.** Carried.

## Final report as sent

Sent to the owner on 2026-11-08 at 08:41 UTC and copied here verbatim.

Which shared contacts persist is closed and published. It reverses the previous epic's headline. A contact that is a cell of both rings looked rare to persist because the rings were small. From rings of 3 + 4 cells to 8 + 9 the share that binds both rings at every lag rises from 1% to 20%, and to 26% when the contact ignores its own value. So the full contact gate can pass across time with the contact inside both loops. [Decision note](https://github.com/jscul/knotlab/blob/main/research/SHARED-CONTACT-20261108-001/shared_contact.md)

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt | Successful | First step decided exactly; persistence grows with ring size |
| Local direction | Continue | One contact passes the gate; composing two is the open step |
| G5 Dynamics (question 4) | Capability gained | The full contact gate passes across time |

**Next step:** Continue, with #1 starting.

| # | Direction | Payoff | Concreteness | Status |
| --- | --- | --- | --- | --- |
| 1 | Two contacts across time: three rings in a chain | 3/3 | 2/3 | Starting |
| 2 | Why some rules persist | 2/3 | 1/3 | Deferred |
| 3 | Does persistence saturate? | 1/3 | 3/3 | Running in the background (9 + 10 cells) |
| 4 | Learning a rule from its knots (G16) | 2/3 | 1/3 | Deferred |

**Corrections:** none in this epic. Separately, the collar-plane thread narrowed my growth-as-a-law epic: Dworkin and Shieh's theorem doesn't explain the pinwheel's dead ends, because its local laws aren't aperiodic.
**Goals:** a G5 checkpoint.
**Assumptions:** A31 (a shared contact combines its rings' proposals) is now confirmed.
