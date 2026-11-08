# Recurring composition at every ring size

Epic `RECUR-PROOF-20261108-001` (program foundations), 2026-11-08.

## The question

- **Where it comes from.** `RECUR-PATH-20261108-001` overturned A34: read at the recurring lags the path itself fixes, with every
  contact persistent, composition across time survived every growth tested, to 9 cells and 9 rings. Its direction 1 was a proof for
  every ring size, writing the rows by binomial coefficients mod 2 (Lucas). The coordinator relayed the go-ahead on 2026-11-08, asking
  also whether the same argument covers the rule-102 and rule-90 families.
- **The question.** Do the two-apart families with rule 60 compose this way at every ring size, or is there a size where they fail?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **A contact and its two partners form a closed loop.** If a contact reads two cells that each read only it and themselves, their sum is constant, and the contact's value is that sum's first value plus its other inputs one lag earlier. So it depends on both partners' first values at every lag. | proved | A |
| 2 | **Every two-apart one-sided path composes at recurring lags, at every ring size.** For each of the 64 families (rule 60 or 102 on each ring, contacts two apart, every ring of s ≥ 4 cells), every contact binds both its rings at every lag, and the last contact binds the end rings exactly at the lags T with C(T − 3, m) odd, where m is 2, s − 2 or 2s − 6. By Lucas' theorem these lags recur with period a power of two and density 2^(−w), w the number of ones in m. So each composes at recurring lags (A37) at every ring size, and at every lag (A34) at none. | proved; checked at every lag for ring sizes 4 to 40 and on full state spaces at 4 and 5 | A |
| 3 | **And at every length.** With n ≥ 3 rings, the last contact binds the first ring exactly when C(T − (n − 1), e) is odd, e the sum of k_j − 1 over the middle rings. | proved; checked for 3 to 10 rings at sizes 4 to 16 | B |
| 4 | **Rule 102 is covered; rule 90 is not.** Every family with a rule-102 ring is the mirror image of a rule-60 family. In the 196 families with rule-90 or frozen rings, the contacts mostly lack two partners, only 32 keep a fixed witness cell, and the composing share is often 1/3, not a power of two. Their composition at recurring lags, which holds to 20 rings, needs another argument. | computed (`rule90_scope.json`) | decision note |

## Answer

The stop rule's first outcome holds: a theorem for every ring size. Paths whose rings run the one-sided additive rules 60 or 102,
with contacts two apart, keep every contact persistent and compose at recurring lags at every ring size and every length. The far
contact needs the first ring exactly at the lags where one binomial coefficient is odd. The argument covers rule 102 by mirror
symmetry, and does not reach the rule-90 families.

## Reading

**Interpretation, not a theorem.**
- **For the network gate across time.** Under A37 these paths are native networks across time that pass the transport clause, now by
  proof:
  - every contact is a closed loop with its two partners;
  - the composing lags are fixed by the path's own Pascal triangle;
  - composition survives every ring size and every length.

  Recoding by constants changes nothing, and restrictions are untested.
- **Why A34 failed here.** The far contact needs the first ring only when C(T − 3, m) is odd, a fixed share of each cycle and never
  all of it. A34 asked for all of it.
- **Lengths and shares.** The composing share 2^(−w) shrinks as positions add binary ones but never reaches zero, at any length.
- **The recurring family.** Affine again: the rules whose powers are Pascal's triangle mod 2.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Every ring size (A) | ring sizes 4 to 40, every lag through the eventual cycle, all 64 families | pass: 228,864 lags, no mismatch |
| Every length (B) | 3 to 10 rings at sizes 4 to 16, every choice of positions, and 400 random mixtures of rules 60 and 102 | pass: 778,914 lags, no mismatch |
| Full state spaces (A, B) | 128 four-ring paths at sizes 4 and 5, and five chains and longer paths | pass |

## Correction

While building the proof, the families of `RECUR-PATH-20261108-001A-E002` turned out to be counted with repeats. Each two-apart
family was listed four times, once for each label of its positions at four cells, where all four labels give the same path. The
distinct counts are 64 two-apart families with every contact persistent at every size, not 256, and 260 in all, not 452. With
contacts binding at the composing lags, they are 4,096, not 16,384. The outcome for A34 is unchanged. Logged in `docs/CORRECTIONS.md`
as not a block.

## Literature and provenance

- **Sources.** Lucas' theorem (Lucas 1878); Pascal's triangle mod 2 as rule 60's powers (Martin, Odlyzko and Wolfram 1984).
- **Classification.**
  - **Tickets A and B.** Known-with-delta: classical ingredients, applied to contacts of paths across time.
  - **The rule-90 scope check.** New as far as found; computed.

## Workspace assumptions

- **Relied on.** A30 (two-time knots), A32 (binding), A37 (composition at recurring lags), with A34's reading shown to fail.
- **Scope.** Linear rules, contact laws as stated, ring sizes s ≥ 4.

## Ratio

Since the epic opened:
- **Substantive.** Two proofs (A, B) and the scope check of the other families.
- **Administrative.** This note, the closure, and the count correction.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — a proof for every ring size | **Status:** Successful | Proved for the 64 two-apart families at every ring size and every length; rule 102 by symmetry |
| Local direction — networks across time | Continue | A proved family that transports is in hand: separation and cycles of rings can now be built on it |
| Broader exploration — G5 with G1 | Known alternatives | The rule-90 families' mechanism; the gate's restrictions; nonlinear paths (B10) |
| Long-term goal — G5 Dynamics (question 4) | Capability gained | Native networks across time of every length and ring size exist, by proof, under A37 |

**Corrections:** one, not a block (RECUR-PATH's repeated counts). **Goals:** a G5 checkpoint (capability gained). **Assumptions:** none
added; a history line on A37.

- **What the attempt leaves open.**
  - Separation and cycles of rings on the proved families.
  - Why the rule-90 families compose at recurring lags, with shares like 1/3.
  - The gate's restrictions under A37.
- **The missing bridge to the program's composed topology.** Native separation across time, on a family that is proved to transport.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Native separation and cycles of rings on the proved families (backlog B12) | 3/3 — Major | 3/3 — Ready | Cut a contact of a proved path and show by the theorem's formula that the far contact stops needing the first ring at every lag; then close four rings into a cycle with two routes → native separation across time, or its obstruction | Selected · for its own thread |
| 2 | Why the rule-90 families compose at recurring lags (G5) | 2/3 — Substantial | 2/3 — Testable | Read their rows over GF(2)[x]/(x^5 − 1) and explain the share 1/3 → a proof for every length, or the length where it fails | Alternative · deferred |
| 3 | The gate's restrictions under A37 (G5) | 2/3 — Substantial | 3/3 — Ready | Restrict the proved families to admitted subsystems and recheck every reading → which restrictions keep composition | Alternative · deferred |
| 4 | Nonlinear paths at recurring lags (backlog B10) | 2/3 — Substantial | 1/3 — Stated | Parked | Backlog |

1. **Separation on the proved families.**
   - **Payoff 3.** Separation is the next step in the program's order, adjacency, paths, separation and then distance, and the proved
     families transport.
   - **Concreteness 3.** The formula C(T − (n − 1), e) tells exactly how a cut changes the far contact.
   - **Uncertainty.** Whether a cycle of rings keeps the closed-loop structure at each contact.
2. **The rule-90 mechanism.** Its shares of 1/3 point to a period-3 structure on 5-cell rings.
3. **Restrictions.** The gate's last open item, cheap on these families.
4. **Nonlinear paths.** No method yet.

**Recommendation.** Continue. Direction 1 is backlog B12, which the coordinator holds for its own thread; hand it the proved
families with the formula. If this thread continues on its own, take direction 3, then direction 2.

## Final report as sent

Sent to the owner on 2026-11-08 at 13:13 UTC and copied here verbatim.

The proof landed. Epic cb5d34f0b and shared docs 81aefd4fe are published. Paths whose rings run rule 60 or 102, with contacts two apart, compose at recurring lags with every contact persistent, at every ring size and every length.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: a proof for every ring size | Successful | Proved for all 64 two-apart families at every ring size s ≥ 4 and every length; rule 102 by mirror symmetry |
| Local direction: networks across time | Continue | A family that is proved to survive growth is in hand, so separation can be built on it |
| Broader exploration: G5 with G1 | Known alternatives | The rule-90 families' mechanism; the gate's restrictions; nonlinear paths (B10) |
| Long-term goal: G5 (question 4) | Capability gained | Native networks across time of every length and ring size exist, by proof, under A37 |

- **Why it works.** Each contact reads two neighbours that read only it and themselves. Their sum never changes, so the contact depends on both of them at every lag.
- **Where composition happens.** The far contact needs the first ring exactly when C(T−3, m) is odd, with m = 2, s−2 or 2s−6. With n rings the condition is C(T−(n−1), e) odd. By Lucas' theorem that's a recurring set of lags, never all of them.
- **Checked:** 1,007,778 lags against exact row sequences (sizes 4 to 40, lengths 3 to 10), and full state spaces at the smallest sizes.
- **Not covered:** the rule-90 families. Their contacts lack the two read-back neighbours, and their shares, like 1/3, aren't powers of two. They still hold computationally out to 20 rings.

Next step: Continue, selected #1.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Native separation and cycles of rings on the proved families (B12) | 3/3 | 3/3 | Cut a contact and use the formula to show the far contact stops needing the first ring; then close four rings into a cycle | For its own thread |
| 2 | Why the rule-90 families compose at recurring lags | 2/3 | 2/3 | Read their rows mod x^5 − 1 and explain the share 1/3 | Alternative |
| 3 | The gate's restrictions under A37 | 2/3 | 3/3 | Restrict the proved families and recheck | Alternative |
| 4 | Nonlinear paths at recurring lags (B10) | 2/3 | 1/3 | Parked | Backlog |

**Corrections:** one, not a block. The recurring-lag census listed each two-apart family four times. The right counts are 64 (not 256), 260 in all (not 452), and 4,096 (not 16,384) with contacts binding only at composing lags. Every verdict and the overturn of A34 stand ([knotlab HISTORY](https://github.com/jscul/knotlab/blob/main/HISTORY.md)).
**Goals:** G5 checkpoint, capability gained.
**Assumptions:** none added; A37 gets a history line for the proof. A34's register entry records the pre-registered rule it was overturned by. The every-lag control slip is in RECUR-PATH's verification section.

[Decision note](https://github.com/jscul/knotlab/blob/main/research/RECUR-PROOF-20261108-001/recur_proof.md)
