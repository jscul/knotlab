# One band makes the torus

Status: Proved by hand. The finite claims are checked exactly in `check.py`.

Ticket `BAND-SURFACE-20261108-001A`, 2026-11-08.

## Standard statement

- **Networks.** Rule-60 rings with equally spaced law-(12, 12) contacts, given by rotation systems (`GROW-NET-20261108-001A`). A network
  is **balanced** when every contact persists at every lag; with equal spacing that means every count of returns to every contact is
  even (`LOOP-NET-20261108-001A`, Theorem 2).
- **The band law.** On the n × m torus, inserting a band puts a new loop of n rings between two consecutive rows and joins each new
  ring to the ring below it and the ring above it. A **loop** of n rings is the case m = 1, with no vertical contacts: there the rows
  below and above are the same row, so each new ring is joined to its partner twice, once on each side. The result is the n × 2 torus.

**Theorem 1 (tori with a side of two).** For n ≥ 3 and m ≥ 2, and for n = 2 and m ≥ 3, the half-turn of the n × m torus about the
midpoint of any contact is an orientation-preserving automorphism fixing the contact and exchanging its rings. So every contact persists
at every lag at every ring size.

**Theorem 2 (one band makes the torus).** Start from a loop of n ≥ 3 rings, which is balanced (`LOOP-ANY-20261108-001A`). The band law
gives the n × 2 torus, then the n × 3, n × 4, … tori. Every stage is balanced, and the first insertion turns the sphere of the loop into
a torus. So a uniform local law makes the torus from a loop with every contact persistent at every stage.

## Nearest known result

- **Maps.** The half-turns of the rectangular tori, and the regular maps {4,4} (Coxeter and Moser, ch. 8).
- **Classification.** Known-with-delta: the symmetry is classical; the delta is that a single band insertion into a loop of persistent
  contacts closes a handle while keeping every contact persistent.

## Proof of Theorem 1

The proof of `GROW-NET-20261108-001A`, Theorem 1, applies with one change. For m = 2 the two vertical contacts of ring (i, 0) both join
it to (i, 1), but they are different contacts, and no two corners lead from one contact to the same next contact: on ring (i, 0) the
corners from v(i, 0) and v(i, 1) lead to h(i − 1, 0) and h(i, 0), and on ring (i, 1) to h(i, 1) and h(i − 1, 1). The half-turn
x ↦ 2p + e − x is still an automorphism of Z_n × Z_m preserving the counterclockwise order; about v(p) it exchanges p and p + e2 and
fixes v(p). With equal spacing every corner weighs ω, so `LOOP-NET-20261108-001A`, Theorem 3, gives persistence. The case n = 2 is the
same with the axes exchanged. ∎

## Proof of Theorem 2

The loop of n ≥ 3 equally spaced rings is balanced (`LOOP-ANY-20261108-001A`; equally spaced, its positions sum to rs/2). Inserting a
band into it joins each new ring (i, 1) to its partner (i, 0) by two contacts, one on each side of the loop. In the counterclockwise
order E, N, W, S of each ring these are N and S, which is the n × 2 torus. Inserting a band into the n × m torus gives the n × (m + 1)
torus. By Theorem 1 every torus in the sequence is balanced. The loop's surface is a sphere: n rings, n contacts and two faces. The n × 2 torus has 2n rings, 4n contacts
and 2n faces, so its Euler characteristic is 0 and its genus 1. ∎

## Remark (other first bands)

Where the new contacts sit decides the surface. Ticket B enumerates every rotation of a loop plus one band: with single rungs the
balanced ones lie on a sphere only for n = 4 (the cube), on the torus for n = 4, 6 and 8, and otherwise on surfaces of genus 2 to 4,
most with no symmetry at all; with double rungs they include the n × 2 torus and others of genus 2 to 4.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | Theorem 1: every n × m torus with 2 ≤ n ≤ 10 and 2 ≤ m ≤ 6 (except 2 × 2) has a half-turn at every contact and is balanced | pass: 44 tori |
| 2 | Theorem 2: for n = 3 to 12, the loop (genus 0) and the n × 2, n × 3 and n × 4 tori (genus 1) are balanced | pass |
| 3 | The n × 2 torus is the loop plus a band joined by two contacts per ring (n = 3 to 8) | pass |
| 4 | Cell level, exact: every contact of the n × 2 torus keeps its witnesses at every lag (n = 3, 4, 5) | pass |

## Nonclaims

- **Equally spaced networks**, law (12, 12), rule-60 rings.
- **The torus only.** The theorem makes a torus; surfaces of higher genus from bands are ticket B's census, not a theorem.
- **No distance.** **Two-time knots only** (A30).
