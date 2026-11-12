# Pre-registration: why the knot law's harmonies are even

Epic `EVEN-PERIOD-20261112-001` (`HARMONY-ARITH-20261112-001` direction 1, G8 with G1; program mathematics, group arithmetic), written
on 2026-11-12 before the frozen census runs, at the coordinator's go-ahead under the owner's standing mandate. Code frozen with this
file in `proofs/EVEN-PERIOD-20261112-001A/EVEN-PERIOD-20261112-001A-P001_flip_certificates/` (`even_lib.py`, `check.py`,
`even_referee.py`). The canonical K1–K3 test is unchanged.

## Words

As in the guide's glossary and `HARMONY-ARITH-20261112-001`: harmony (A70), the period of a state, orbit, antiperiodic. The bases
have one distinction per whole number and knots of kinds (0, a, b), 0 < a < b, under the plain not-all-equal law. A **word** u of
period p is the repeating state x_i = u[i mod p], and its **residue pairs** G(u) are the pairs (α, β) modulo p such that u is never
constant on (r, r + α, r + β). (These are the literature's terms for a periodic sequence and its residues.)

## The question

`HARMONY-ARITH-20261112-001` found every not-all-equal harmony to have even periods only, on every pattern of up to three knot kinds
to span 12. Why? The coordinator asked first which part follows from the law's symmetry alone, and why no harmony has a repeating
state such as 001, which satisfies the knot kind (0, 1, 2), as its whole allowed set.

## What symmetry gives, and what it does not (proved by hand)

**Lemma 1 (the mirror alone).** Flipping every value keeps every not-all-equal knot satisfied, so it maps allowed states to allowed
states. A state of odd period p is never mapped onto its own orbit: if the flipped state were the state shifted by k, flipping twice
would give the state shifted by 2k, so p would divide 2k, hence k, and the state would equal its own flip, which is impossible. So an
orbit of odd period always comes with a second, mirrored orbit. That is all the symmetry gives: it does not forbid odd periods.
The pattern of the single kind (0, 1, 2) allows the orbit of 001 and its mirror 011, and many states that do not repeat.

**Lemma 2 (the most constrained base).** A kind (0, a, b) is satisfied by a word u of period p exactly when (a mod p, b mod p) is in
G(u). So every base that allows u has all its kinds among the lifts of G(u), and allows fewer states the more of them it has.

**Lemma 3 (flip certificates).** Call a residue r of a p-periodic word c **flippable** for G(u) when no pair (α, β) in G(u), in no
role, puts the two other values of a knot through r equal and different from c[r]: in the first role the residues r + α, r + β; in
the middle role r − α, r − α + β; in the last role r − β, r − β + α. If some word c of period p is never constant on any triple of G(u)
and has a flippable residue r, then every base that allows u also allows c, and allows c with the single value at one position of
residue r flipped. That state does not repeat, so no harmony allows u, at any span and with any number of knot kinds.

*Proof.* Every kind of a base allowing u lifts a pair of G(u) (lemma 2), and c satisfies every such pair, so c is allowed. A knot not
through the flipped position keeps c's values; a knot through it has its two other positions unflipped, with the values of c at their
residues, and is constant after the flip only if those two values are equal and differ from c[r], which flippability excludes. A
sequence that equals a periodic one except at one position does not repeat. ∎

For 001 the residue pairs are (1, 2) and (2, 1), every triple of them meets each residue once, and the residues of the two 0s are
flippable: flipping one 0 of 001 repeating gives a state that every base allowing 001 also allows. So no harmony has 001 among its
states, and not because of the mirror. **What is not proved** is that every word of odd period has a certificate. If one had none,
lemma 3 would say nothing about it, and a harmony with that period could exist at a large span.

## Scoping before the freeze (disclosed)

- For every word of odd period 3 to 19 (one per orbit), the word itself has a flippable residue, except 4 words of period 17 and 9 of
  period 19; each of those has a certificate c at two values' distance from it. So, with lemma 3, no not-all-equal harmony has a state
  of odd period at most 19, at any span (a computer-assisted theorem, to be refereed).
- Before finding lemma 3: the most constrained base of each word of odd period up to 11 is not a harmony at spans up to 14 (exact);
  single switches to the mirror, phase slips and the antiperiodic double do not explain every case; the most constrained base of one
  certificate-by-another word of period 17 has, besides its two orbits, two components of positive entropy up to span 40.
- The referee's lemma check (R4 below) was run once before the freeze as a smoke test and found no violation.

## The census (frozen; exact)

- **Periods 21, 23, 25, 27, 29** (not looked at), and a replay of 3 to 19: every Lyndon word of the period (one per orbit; an orbit and
  its mirror both appear), its residue pairs, whether it has a flippable residue, and if not a certificate found by SAT (one
  satisfiability call per candidate residue).
- **Control.** The 11 orbit words of not-all-equal harmonies found by `HARMONY-ARITH-20261112-001` at spans 2 to 6 (periods 2 to 12)
  must have no certificate at all, since a harmony allows each of them (lemma 3's contrapositive).
- **Caps, set now.** The census part 2 hours and 16 GB, by its systemd unit; registered as long-running.

## Predictions and failure criteria

- **E1.** Every word of odd period 21 to 29 has a certificate. Predicted: holds. With lemma 3, no not-all-equal harmony then has a
  state of odd period at most 29.
- **E2.** The replay finds a certificate for every word of odd period 3 to 19. Must hold (scoped).
- **Control.** No harmony word has a certificate. **If one does, lemma 3 or the code is wrong: stop and find which.**
- **Failure (the coordinator's).** An odd-period harmony that does not split, at any span. A word without a certificate is not yet
  a failure: its most constrained base is then tested at spans up to 3p with the exact sparse method of the scoping, and a harmony
  there is the failure. Until then the word is reported as unsettled.
- **Proof attempt.** A proof that every word of odd period has a certificate, or a family of words without one, is sought alongside;
  it counts only as a proof for every odd p.
- **Answer by rule.** E1, E2, the control, the referee, and the proof attempt's outcome. Stop there; report and hold.

**Referee (fresh code, `even_referee.py`).** R1: periods 3 to 19 recomputed by brute force (all words, certificates searched among all
2^p words). R2: every certificate reported at 21 to 29 checked directly. R3: 300 random words at each period 21 to 29 recomputed with
its own SAT encoding (a different solver). R4: lemma 3 checked on actual bases, every word of odd period up to 11 and every span 3 to
14, by testing every knot near the flip. It is independent code by the same author, not an independent reviewer.

Known mathematics, checked before the freeze: involutions and finite group actions on shifts of finite type and their periodic
points (Adler, Kitchens and Marcus 1985; Boyle and Krieger 1987; Fiebig 1992); finite subshifts; Lyndon words (Duval's algorithm). Not
found: the even-period rule or flip certificates for not-all-equal bases.

Assumptions in force: A70. Nothing here bears on P versus NP.
