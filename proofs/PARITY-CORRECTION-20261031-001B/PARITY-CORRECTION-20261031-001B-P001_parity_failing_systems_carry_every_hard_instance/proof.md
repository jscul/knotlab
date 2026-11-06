# Parity's failing systems carry every hard instance

Status: Proved

Ticket `PARITY-CORRECTION-20261031-001B`, 2026-10-31.

## Why this is needed

- **The withdrawn reason.** The mutual-selection scan said that parity's failing systems "select nothing" because parity's whole coupling
  family is easy. Ticket A withdraws that reason: the family is #P-hard except at six points.
- **The question this reopens.** Could parity's failing systems, which are recognisable by linear algebra, make some hard member of the
  family easy, as the knot's failing systems make the dimer law easy?
- **The answer.** No. Its failures can be grafted into any system.

## Dependencies

- **`PARITY-CORRECTION-20261031-001A`.** The library (`parity_lib.py`) and the dichotomy: counting parity's coupling on connected simple
  cubic systems without repeated lines is #P-hard at every complex λ outside {0, 1, −1, i, −i, ∞}.
- **The census of `MUTUAL-SELECTION-20261031-001C`.** The piece is graph n = 8, number 11 there.

## Setting

- **The coupling.** As in ticket A: M(H, b; λ) = Σ_c λ^{(number of lines whose colour sum differs from b_ℓ)}.
- **The failing class.** Parity's law fails on (H, b) iff b ∉ D. Equivalently, there is a **certificate**: a set s of lines covering
  every point an even number of times with b·s = 1 (an odd number of negations). Recognising failure is Gaussian elimination.

## Lemma 1 (splice lemma)

**The splice.** Let (Q, b_Q) be a signed cubic piece with a certificate s that avoids a line m, and let q be a point of m. For any host
(H, b_H) and incidence (p, ℓ) of H, swap the incidences: m takes p in place of q, and ℓ takes q in place of p. Signs stay on their lines.

**The claim.** The result is a cubic system, and s is still a certificate in it. So it is parity-unsolvable whatever the host.

**Proof.**
- Every degree is unchanged, so the result is cubic.
- Coverage by s changes only at points of s's lines. Only q left a line (m) and only p joined one (m), and m ∉ s. So every point is still
  covered an even number of times.
- The negations on s's lines are untouched, so b·s = 1 still holds. ∎

**Corollaries.**
- A chain of k pieces in place of one incidence keeps every piece's certificate.
- The splice keeps simplicity and connectivity.
- It creates no repeated line when the host and piece have none: each piece line and each host line gets distinct points.

## Lemma 2 (two calls)

**Notation.**
- F_H(x, y) is the count of the host with the incidence (p, ℓ) cut, p coloured x and ℓ reading y in its place.
- G(x, x′) is the piece's transfer matrix: m reads x from the host point, and q, coloured x′, is delivered onward.
- H_k is the host with the incidence replaced by a chain of k pieces.

**The model.** M(H_k) = Σ_{x,y} F_H(x, y) (G^k)(x, y), and M(H) = Σ_x F_H(x, x).

**The formula.** By Cayley–Hamilton, I = (tr G · G − G²)/det G whenever det G ≠ 0. So

M(H) = (tr G · M(H_1) − M(H_2)) / det G.

**What it needs.** Only det G ≠ 0. No eigenvalue condition is needed.

## Theorem 3

**The piece.** The census piece Q has lines (4,2,5), (4,6,2), (3,2,0), (7,6,1), (1,7,5), (3,0,5), (3,0,6), (4,1,7).
- Line (7,6,1) carries one negation.
- The port is point 4 on line (4,2,5).
- The certificate is the lines (7,6,1), (1,7,5), (3,0,5), (3,0,6).

**Its transfer matrix.**

G = [[8λ(λ+1)³(2λ² − λ + 1), 4λ(λ+1)⁴(λ² + 1)], [4λ(λ+1)⁴(λ² + 1), 8λ²(λ+1)³(λ² − λ + 2)]],

det G = −16 λ² (λ − 1)⁶ (λ + 1)⁶, tr G = 8λ(λ + 1)⁴(λ² + 1).

**Statement.**
- For every complex λ outside {0, 1, −1}, counting parity's coupling on connected simple cubic systems reduces, with two oracle calls, to
  counting it on connected simple parity-unsolvable signed systems. When the host has no repeated lines, neither do the systems called.
- With ticket A, for every λ outside {0, 1, −1, i, −i, ∞}, counting parity's coupling is #P-hard (Turing) on connected simple cubic
  systems without repeated lines on which parity's law fails.
- At the six excluded points it is polynomial everywhere.
- So parity's failing class makes no member of parity's coupling family easy.

**Proof.** Lemmas 1 and 2 with the piece. det G ≠ 0 off {0, ±1}. ticket A supplies the hard hosts, which are θ images: connected, simple,
and without repeated lines. ∎

## Contrast with the knot

- **Global versus local failure.** The knot's failures are global: a connected cubic system fails not-all-equal iff its plain signing is
  Pfaffian (Seymour; Robertson–Seymour–Thomas). On such systems the dimer law is a determinant.
- **So no analogue of Theorem 3 can exist for the knot.** A failure-keeping splice with a recovery formula for every host would make
  perfect matchings of cubic bipartite graphs (Dagum–Luby, #P-complete) polynomial to count.
- **Observed.** Splicing the Fano plane into each 2-colourable census host (n ≤ 6) at an incidence gave a 2-colourable system in all 54
  cases (check 6).
- **The difference.** Parity's failures are local: a certificate lives in a small piece and survives any host. The knot's failures
  constrain the whole space.

## Checks

`check.py` (`result.json`, about 3 s):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; ticket A Proved and passed. | pass |
| 1 | The piece: cubic, simple, connected, no repeated lines, rank 6, unsolvable with the certificate above. | pass |
| 2 | The transfer matrix symbolically; det G and tr G as stated; det G vanishes only at {0, 1, −1}. | pass |
| 3 | 72 spliced systems (12 hosts, plain and signed, two incidences, chains of 1 to 3) are cubic, simple, connected like the host, free of new repeated lines, unsolvable, and keep every piece's certificate. | 72/72 |
| 4 | The transfer model by direct computation (cut host by brute force; spliced system by elimination). | 60/60 |
| 5 | The two-call formula end to end on 12 hosts (including θ(Fano), whose second call has 37 points) at λ ∈ {2, 1/3, −2, 5/7, 1 + i, −3/2 + i/2}. | 72/72 |
| 6 | Contrast: Fano spliced into 2-colourable census hosts stays 2-colourable. | 54/54 |

## What this does not establish

- **Novelty.** Nothing new beyond the correction. Certificate-preserving splices and Cayley–Hamilton interpolation are standard tools.
- **Other laws on parity's failing systems.** Lane B sketched a switching argument for laws symmetric under complement. It is not checked
  here.
- **The knot side.** Its non-transplantation is observational here. The general impossibility is conditional (unless #P-complete
  counting is polynomial).

## Reading

- **What survives.** "Parity's failing systems select nothing" survives with a correct reason: they carry every hard instance.
- **The sharper criterion.** Recognisable failures select a law back only when they are global, constraining the whole space as the
  knot's do. Parity's failures are local.

## Files

- `check.py`, `result.json`: the checks (they use ticket A's `parity_lib.py`).
