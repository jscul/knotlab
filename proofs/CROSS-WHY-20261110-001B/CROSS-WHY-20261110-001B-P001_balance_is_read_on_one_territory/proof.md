# Balance is read on one territory

Status: Proved by hand (both lemmas). `check.py` compares the reduced reading with the full-state reading on eleven schedules.

Ticket `CROSS-WHY-20261110-001B`, 2026-11-10.

## Standard statement

- **Networks and growth.** The n × n tube of rule-60 rings of 4g cells with law (12, 12) contacts, every first-row cell open, under the
  doubling law of `BIRTH-RULE-20261109-001A-E001` with open births: at a doubling every ring splits into a 2 × 2 block, the old ring
  keeping its own cells, every contact and every cell of a new ring born open. A **schedule** is the list of runs between doublings, the
  first doubling at lag 0. A contact **binds** a ring when its value depends on one of the ring's own born cells (A32); a **stage**, the
  network fixed from a doubling lag, is **balanced** when every contact binds both of its rings at every later lag.
- **The fundamental domain.** The column and row labels are cyclic lists; the original labels 0, …, n − 1 come first in their blocks,
  and a doubling inserts a new label after each old one. The domain is the set of rings in the first side/n columns and the first
  side/n rows.

**Lemma 1 (one territory suffices).** For every schedule and every stage, a contact c binds a ring R at a lag exactly when c's translate
by any original lattice vector binds R's translate there. Every ring is the translate of one ring of the domain, so the stage is
balanced exactly when every contact of every domain ring binds it at every later lag; and those bindings are decided by the born cells
of domain rings alone.

**Lemma 2 (newborn rings never fail).** At every doubling lag of every schedule, every contact binds every ring born at that lag at every
later lag of the stage. So an unbalanced stage always fails at a ring that lived through a run.

## Proof of Lemma 1

Let τ shift the original labels by one, i ↦ i + 1 mod n, on columns (rows alike). It permutes the rings and contacts of the original
tube, preserving each ring's cyclic order and each contact's positions, so it commutes with the step: rule 60 and law (12, 12) are the
same at every ring and contact. Extend τ to later labels by sending the label inserted after x at lag t to the one inserted after τx at
lag t. The doubling commutes with τ: it keeps the old rings' own cells, whose images are old rings' own cells, and makes every other
cell open. The open first row and the cells born at each doubling are permuted among themselves. So, writing every cell's value as a sum
of born cells, the value of τb at every lag is that of b with each born cell renamed by τ. A contact binds a ring when some born cell of
that ring occurs in it, so c binds R exactly when τc binds τR, at every lag. The domain meets every orbit of the translations.

Each cell's value is a sum over born cells, and the step acts on each born cell's coefficients separately: the coefficients of R's born
cells at a lag depend only on where those born cells were, never on other born cells. So tracking the born cells of domain rings and
nothing else gives every coefficient the reading uses. ∎

## Proof of Lemma 2

At a doubling lag t, a ring X born at t has open own cells, each one of X's born cells, and no other cell holds any part of them: the
contacts are newborn too, and the old cells were computed before X existed. So X's own cells hold its born cells independently and no
other cell holds any. By the transfer lemma (`DOUBLE-BALANCE-20261109-001A`), for every contact c and k ≥ 1, c binds X at lag t + k
exactly when c's value at lag k in the static stage depends on X's own first-row cells. The static stage is a square torus of rings
with both sides at least 6, on which every contact persists (`GROW-NET-20261108-001A`, Theorem 1, at every ring size). ∎

## Remarks

- **Use.** Lemma 1 makes ticket A's census exact while reading one territory, about a ninth of the rings and of the born cells, with the
  state as numpy bit arrays (`territory_lib.py`). Lemma 2 says where to look for a failure: in the rings that ran.
- **What it does not say.** Neither lemma says which old rings fail; ticket A reads that.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | Lemma 1: on eleven schedules (g = 2, 3, 5; one or two runs; 12 × 12 and 24 × 24), the reduced reading's failures equal the full-state reading's on the domain, lag by lag; every failure outside it is the translate of one inside; and the balance verdict agrees with `BIRTH-RULE-20261109-001A-E001`'s `readings()` | pass |
| 2 | Lemma 2: in those eleven, no ring born at the stage's doubling fails | pass |

## Nonclaims

- **The n × n tube and the doubling law with open births** (A44); declared rings (A45). A schedule that doubles only some rings has
  fewer translations, and Lemma 1 then needs its own domain.
