# Composition at recurring lags across sizes

Epic `RECUR-PATH-20261108-001` (program foundations), 2026-11-08. A challenge of A34.

## The question

- **Where it comes from.** `PATH-GROWTH-20261108-001` found that no family of paths with one linear rule per ring composes at every
  lag at more than one size, and its stop rule put A34 under challenge. The coordinator relayed the go-ahead on 2026-11-08, asking
  that the meaning of each outcome be recorded in the register before the census ran.
- **A34 and its alternative.** A34 reads composition as the far contact binding the end rings at every lag from the light cone on.
  The alternative reads it at the recurring lags the path itself fixes: the far contact binds the end rings at some lag of its
  eventual cycle, and so at lags recurring with its period. In a linear path composition is arrival
  (`INTERMITTENT-NET-20261108-001A`), so the composing lags come from the dynamics, not from an observer.
- **The discriminator.** Transport. On the growth families of `PATH-GROWTH-20261108-001` (one linear rule per ring and every law;
  four rings growing from 3 to 9 cells with antipodal middle contacts, from 4 to 9 with contacts two apart, or paths growing from 4
  to 9 rings), is there a family that composes at recurring lags at every size?

## The measure

`recur_lib.analyze` gives three readings of each path, each exact by the row-sequence reduction:

| Reading | Every contact | The last contact and the end rings |
| --- | --- | --- |
| Every lag (A34) | binds its two rings at every lag | bound at every lag from the light cone on |
| Recurring, persistent | binds its two rings at every lag | bound at some lag of its eventual cycle, hence at recurring lags |
| Recurring, binding there | binds its two rings at every composing lag of the joint eventual cycle | bound at some lag of its eventual cycle |

Each reading implies the next. The last is `INTERMITTENT-NET-20261108-001`'s native intermittent composition, for paths.

## Pre-registered meaning for A34

Recorded in `docs/ASSUMPTIONS.md` (A34, Challenge) and in the contract before the census ran (21f87ebec):
- **Overturned** if some family composes at recurring lags with every contact persistent at every size of its schedule. The
  recurring reading then replaces A34 as a new entry.
- **Confirmed, kept for the gate,** if such families exist only with contacts that bind at the composing lags and not at every lag.
- **Confirmed** also if no family composes at recurring lags at every size.
- **Back to Assumed** if the best candidates meet a recurring reading at every decided size while some sizes stay undecided.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Composition at recurring lags transports.** 260 families (452 as first counted) compose at recurring lags with every contact persistent at every size of their schedule. 64 (first counted as 256) have contacts two apart on rings of 4 to 9 cells, with rule 60 or 102 on every ring. 196 grow from 4 to 9 rings, with frozen (204) or rule-90 end rings and middle rings on 90, 60 or 102. No undecided case. | exploratory census (E002), exact | A |
| 2 | **Under A34 nothing transports.** In the same census no family composes at every lag at two sizes, as `PATH-GROWTH-20261108-001` found. | exploratory, exact | A |
| 3 | **The weaker reading transports more.** With every contact binding at the composing lags but not necessarily at every lag, 4,096 families (first counted as 16,384) compose at every size with contacts two apart, 1,016 in the longer schedule and 748 with antipodal contacts. | exploratory, exact | A |
| 4 | **The 260 are verified.** An independent computation by path_lib agrees for all of them at every size. The full state spaces agree at the two smallest sizes (every path, each family counted once or more) and for eight families at the third (21 bits). The last contact composes at 12.5% to 62.5% of its cycle, of period 4 to 24. | computed (`verify_recurring.json`) | A |

## Answer

By the pre-registered rule, A34 is overturned. Read at the recurring lags the path itself fixes, with every contact persistent,
composition across time survives every growth tested: rings from 4 to 9 cells and paths from 4 to 9 rings. Read at every lag, as A34
reads it, it survives none. The recurring reading replaces A34 as A37.

## Reading

**Interpretation, not a theorem.**
- **For the network gate.** Two complete contacts form a native network when they compose by a substrate-native law and keep
  composing under the admitted transports. Under A37 the 260 families do both:
  - every contact persists;
  - the composing lags are fixed by the path's own dynamics;
  - composition survives every growth tested.
  
  Recoding by constants changes nothing; restrictions are untested.
- **What A34 did.** It asked the far contact to need both ends at every single lag. In these families it needs them at a fixed share
  of each cycle. A34 read the gate's persistence of contacts as persistence of composition, and that reading is what made composition
  across time look tied to sizes.
- **Corrections.** One earlier reading rested on A34 and is corrected: `INTERMITTENT-NET-20261108-001` kept A34 for the gate because
  "the contact gate asks for persistence, which intermittent composition fails".
- **The recurring family.** Again affine: the one-sided additive rules 60 and 102, rule 90, and frozen rings.

## Stress test

| Claim | Check | Result |
| --- | --- | --- |
| 260 families compose at recurring lags with persistent contacts at every size (A) | independent row sequences (path_lib) at every size; full state spaces at the two smallest sizes and, for eight families, the third | pass: all of them (counted 452 and 904 with repeats); 8 of 8 |
| The census's every-lag reading (A) | its control against `PATH-GROWTH-20261108-001A` | E001 failed (a bug that skipped cycle lags before the light cone); E002, with the fix and nothing else changed, passes |

The schedules stop at 9 cells and 9 rings, the declared one size past the full levels. A proof for every size is the next step.

## Correction (2026-11-08, the count)

Logged in `docs/CORRECTIONS.md` as not a block. The census listed each two-apart family four times: at four cells all four labels of
its positions give the same path, and each copy was followed under all four labels. The distinct counts are 64 two-apart families with
every contact persistent at every size (first counted as 256), 260 in all (452), and 4,096 with contacts binding at the composing
lags (16,384). The antipodal and longer counts were right. The outcome for A34 does not change. `RECUR-PROOF-20261108-001` then proved
the 64 two-apart families at every ring size.

## Literature and provenance

- **Sources.** Linear recurring sequences over GF(2); additive automata on rings (Martin, Odlyzko and Wolfram 1984); strobed
  composition (`INTERMITTENT-NET-20261108-001A`).
- **Classification.** Ticket A: new as far as found, composition at recurring lags across sizes.

## Workspace assumptions

- **Relied on.** A30 (two-time knots), A32 (binding), A34 (under challenge).
- **Overturned.** A34, by the pre-registered rule.
- **Added.** A37: a path composes at the recurring lags its dynamics fixes, with every contact persistent.
- **Scope.** Linear rules, contact laws by their linear parts, the declared families and schedules.

## Ratio

Since the epic opened:
- **Substantive.** One evidence family changed conclusions: A (the census, E001 and its fixed rerun E002, with the independent
  verification).
- **Administrative.** The pre-registration, this note, the closure, and a correction to the long-running index's start time.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — challenge A34 by transport | **Status:** Successful | A34 overturned as pre-registered: 260 families compose at recurring lags at every size, none at every lag |
| Local direction — paths across time | Continue | Under A37 composition transports; a proof for every size and the gate's restrictions are next |
| Broader exploration — G5 with G1 | Known alternatives | Native separation and cycles of rings (B12), now with families that transport; nonlinear paths (B10) |
| Long-term goal — G5 Dynamics (question 4) | Capability gained | Under A37, native networks across time survive growth |

**Corrections:** one, not a block (INTERMITTENT-NET's reason for keeping A34). **Goals:** a G5 checkpoint (capability gained).
**Assumptions:** A34 overturned; A37 added.

- **What the attempt leaves open.**
  - A proof that these families compose at every size, not only to 9.
  - The gate's restrictions, and whether A37's composition is itself read natively by a knot of the path.
  - Separation and cycles of rings on families that transport.
- **The missing bridge to the program's composed topology.** A proved family of native paths across time at every size, then
  separation on it.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Prove recurring composition at every size (G5, with G1) | 3/3 — Major | 2/3 — Testable | For rule 60 on every ring with contacts two apart, write M^T by binomial coefficients mod 2 (Lucas) and show that every contact's row meets its rings at every lag and the last contact's meets the ends at a fixed share of each cycle → a theorem for every ring size, or the size where it fails | Selected · not started |
| 2 | Native separation and cycles of rings on families that transport (backlog B12) | 3/3 — Major | 2/3 — Testable | Parked for its own thread; the 452 families are in this epic's `families.json` | Backlog |
| 3 | The gate's restrictions under A37 (G5) | 2/3 — Substantial | 3/3 — Ready | Restrict the 260 families to admitted subsystems and recheck every reading → which restrictions keep composition | Alternative · deferred |
| 4 | Nonlinear paths at recurring lags (backlog B10) | 2/3 — Substantial | 1/3 — Stated | Parked | Backlog |

1. **Prove it at every size.**
   - **Payoff 3.** A proof turns transport to 9 cells into a native network across time at every size: the first composed topology
     across time that survives the gate's transports, proved.
   - **Concreteness 2.** Rule 60's powers are binomial coefficients mod 2, so the rows have closed forms. The contacts' feedback is the
     open part.
   - **Uncertainty.** Whether the feedback at the contacts keeps a closed form.
2. **Separation on these families.** Ties with direction 1 and runs in its own thread.
3. **Restrictions.** Cheap on the 260 families, and the gate's last open item.
4. **Nonlinear paths.** No method beyond search yet.

**Recommendation.** Continue with direction 1. If the proof stalls on the contacts' feedback, settle for the restrictions
(direction 3) and hand the families to the separation thread.

## Final report as sent

Sent to the owner on 2026-11-08 at 12:56 UTC and copied here verbatim.

A34 is overturned, by the rule pre-registered before the run (epic 0eb8e3cf1, shared docs c40f97323, published). The census found 452 families of paths that compose at every size tested, with every contact persistent at every lag. They compose at recurring lags, which the path's own dynamics fixes. Under A34's every-lag reading, no family composes at even two sizes. A37 replaces A34.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: challenge A34 by transport | Successful | Overturned as pre-registered: 452 families compose at recurring lags at every size, none at every lag |
| Local direction: paths across time | Continue | Under A37 composition transports; next is a proof for every size, then the gate's restrictions |
| Broader exploration: G5 with G1 | Known alternatives | Separation and cycles of rings (B12) now has families that transport; nonlinear paths (B10) |
| Long-term goal: G5 (question 4) | Capability gained | Under A37, native networks across time survive growth |

- **Rings growing:** 256 families on rings of 4 to 9 cells with contacts two apart, every ring on rule 60 or 102 (the one-sided additive rules).
- **Paths growing:** 196 families from 4 to 9 rings, with frozen or rule-90 end rings.
- **Verified:** an independent computation agrees for all 452 at every size, and so do the full state spaces at the two smallest sizes (904 of 904). The far contact composes at 12.5% to 62.5% of each cycle.
- **A slip I caught:** the first run's every-lag control failed because of a bug in that one check. The rerun fixes only that, passes, and gives the same recurring counts.

Next step: Continue, selected #1.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Prove recurring composition at every size | 3/3 | 2/3 | For rule 60 with contacts two apart, write the rows of M^T by binomial coefficients mod 2 (Lucas) → a theorem for every ring size, or the size where it fails | Awaiting go-ahead |
| 2 | Separation and cycles of rings on these families (B12) | 3/3 | 2/3 | Parked for its own thread; the families are in this epic's `families.json` | Backlog |
| 3 | The gate's restrictions under A37 | 2/3 | 3/3 | Restrict the 452 families to admitted subsystems and recheck | Alternative |
| 4 | Nonlinear paths at recurring lags (B10) | 2/3 | 1/3 | Parked | Backlog |

**Corrections:** one, not a block. INTERMITTENT-NET kept A34 because "the gate asks for persistence". The gate asks every contact to persist and the composition to survive transport; it doesn't ask for binding at every lag ([knotlab HISTORY](https://github.com/jscul/knotlab/blob/main/HISTORY.md)).
**Goals:** G5 checkpoint, capability gained.
**Assumptions:** A34 is overturned. A37 is added: a path composes at the recurring lags its dynamics fixes, with every contact persistent.

[Decision note](https://github.com/jscul/knotlab/blob/main/research/RECUR-PATH-20261108-001/recur_path.md)
