# What a chain of contacts can carry

Status: Proved by hand. The finite claims are checked on small chains (`check.py`).

Ticket `PROCESS-CHAIN-20261108-001A`, 2026-11-08.

## Standard statement

- **The setting.** Three rings in a chain: ring A and ring B are joined by a contact c1, and ring B and ring C by a contact c2. On
  ring B the two contacts are d cells apart, the shorter way round. Every non-contact cell updates by its ring's elementary rule.
  The whole is one space-time law, and the first row is free.
- **Binding.** A contact *binds* two rings X and Y at lag T when every minimally decisive set of its value meets both X's and Y's
  own first-row cells. Equivalently, neither the cells outside X nor the cells outside Y decide it (as in
  `PROCESS-CONTACT-20261108-001A`, Theorem 1). The chain *binds its ends* at c2 when c2 binds A and C.
- **Two kinds of contact.**
  - **Listening:** it reads one cell of each of its rings and feeds nothing back.
  - **Shared:** it is a cell of both of its rings, both of which read it (`SHARED-CONTACT-20261108-001`).

The results:

1. **Theorem 1.** With listening contacts, c2 never depends on ring A and c1 never on ring C. So the chain never binds its ends.
2. **Theorem 2.** With shared contacts, c2(T) does not depend on ring A's first row for T ≤ d, and c1(T) does not depend on ring
   C's. So the ends can be bound only from lag d + 1.
3. **Theorem 3.** With linear or affine rules and affine contact laws, a contact binds two rings at lag T exactly when the support
   of its row of M^T meets both.

## Nearest known result

- **Light cones.** Theorem 2 is the light cone of a cellular automaton on a graph, read at the far contact.
- **Classification.** Known-with-delta. The delta is the reading against the contact-network gate across time: composing two
  contacts needs the middle ring to read the contact it shares.

## Theorem 1 (listening contacts never compose)

*Proof.*
- **Nothing reads a listening contact.** Its update reads its two rings and itself, and no cell reads it.
- **Where c2's inputs come from.** Every value c2 reads is a cell of ring B or ring C, or c2 itself. Ring B's and ring C's cells
  read only their own rings.
- **So the first row splits.** By induction on T, c2(T) is a function of ring B's first row, ring C's first row and c2(0).
- **No binding of the ends.** A full setting of everything outside ring A fixes c2(T), so the cells outside ring A decide it.
- **The mirror case.** The same holds for c1 and ring C. ∎

**Computed (check 1).** On chains of 3, 4 and 3 cells, all 88 rule classes, 14 contact laws each and T = 1 to 6: 7,392 maps, and c2
never depends on ring A.

## Theorem 2 (the light cone of a shared chain)

*Proof.*
- **The tracked set.** Let D_t be the cells whose value at time t can depend on ring A's first row. Ring A's cells themselves are
  set aside.
- **Lag 1.** c1 reads ring A's cells, so c1 may be in D_1. Nothing else outside ring A reads ring A.
- **Spread along ring B.** A cell of ring B reads only its two neighbours on ring B and itself, so D grows by at most one cell of
  ring B per step. Cell b_j can be in D_t only if t ≥ 1 + the distance from b_j to c1 along ring B.
- **Reaching c2.** c2 reads ring C's cells, its ring-B neighbours and possibly itself. Ring C's cells read only ring C and c2, so
  ring A can reach c2 only through c2's ring-B neighbours. They are d − 1 from c1, so they are in D_t only if t ≥ d. Then c2 is
  in D_t only if t ≥ d + 1.
- **The mirror case.** The same argument covers c1 and ring C. ∎

**Computed (check 2).**
- **The bound.** On chains of 3/4/3, 4/6/4 and 5/6/5 cells, contacts opposite on ring B, all 88 classes and three laws, no contact
  depends on the far ring at a lag up to d (2,112 maps).
- **It is usually reached.** In 694 of the 792 configurations, c2 already depends on ring A at lag d + 1.

## Theorem 3 (the linear case)

*Proof.*
- **The system is affine.** With linear or affine rules and affine contact laws, the state map is s ↦ Ms + b. So a contact's value
  at lag T is the parity of the support of its row of M^T, plus a constant.
- **When the outside decides.** A parity of S is fixed by a setting exactly when the setting covers all of S. So the cells outside
  ring X decide the contact exactly when S misses X's own cells. ∎

**Computed (check 3).**
- **The criterion.** The 16 linear and affine rules with affine laws of both families, chains of 3/4/3 and 4/6/4 cells, T = 1 to
  10: 15,360 verdicts, no mismatch.
- **Affinity.** Every such system is affine.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependency artifacts bound by hash; upstream proofs Proved | pass |
| 1 | Theorem 1: 7,392 maps of listening chains | pass |
| 2 | Theorem 2: no dependence before the light cone (2,112 maps); reached at d + 1 in 694 of 792 | pass |
| 3 | Theorem 3: 15,360 verdicts | pass |
| 4 | Two implementations agree; the blockwise test agrees with the grouping test (300 chains) | pass |

## Reading

**Interpretation, not a theorem.**
- **For the contact-network gate.** Two complete contacts form a network candidate only when they compose by a law of the
  substrate. A listening contact persists whenever its rings remember (`PROCESS-CONTACT-20261108-001`), but a chain of them
  carries nothing from one end to the other.
- **What composition needs.** It needs the middle ring to read the contacts it shares. That is shared identity, the gate's own
  requirement, and its cost is the feedback measured in `SHARED-CONTACT-20261108-001`.
- **The order of events.** The far ring's past can reach the far contact only after the time it takes to cross the middle ring.

## Nonclaims

- **Two-time knots only** (A30).
- **No physics.** No physical time or dynamics is claimed.
