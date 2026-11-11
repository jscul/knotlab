# Four-point maps on larger knot spaces, and a reason

Status: Proved (the four classes and the reasoning of section 1; an exact census, refereed by fresh code). Ticket A of
`research/OWN-RELATION-20261111-001/preregistration.md`, frozen with the code in commit `bce78f40c` before any run.
`check.py --part control|census|export|summary|referee` reproduces each part; `referee_parallel.py` runs the frozen referee's functions
unchanged over the exported spaces in parallel (added after the freeze for time).

Words. A knot space's points are its distinctions and its lines its knots (each a not-all-equal relation on three distinctions); every
distinction lies in three knots. The spaces below are random such worlds whose drawn picture is a surface of genus 2, 3 or 4, that is,
with 4, 6 or 8 independent loops of distinctions that no patch of knots fills (the literature's genus, used here only as a label).

## 1. The question and why it is not forced

A decided total map of four held distinctions is self-dual (theorem D of `IN-OUT-20261110-001`). The self-dual maps that use all four
form exactly four classes under permuting and negating inputs and negating the output (exhaustion of the 256 self-dual maps; recomputed
by the referee), each a majority of parities:

| Class | Map | As majorities of parities | Can give a mod-3 bit with one input fixed |
| --- | --- | --- | --- |
| A | [2a + b + c + d ≥ 3] | maj(a, b, maj(a, c, d)) | no |
| B | maj(a, b, a ⊕ c ⊕ d) | one parity among the three | no |
| C | parity of a, b, c if d = a, else their majority | maj(a, a ⊕ b ⊕ c, maj(b, d, a ⊕ b ⊕ c)) | yes |
| D | a ⊕ NAE(b, c, d), the knot's own relation | maj(a, a ⊕ b ⊕ c, a ⊕ b ⊕ d): two parities | yes |

Not forced by self-duality (all four are self-dual), nor by the law alone: not-all-equal with negations and hidden distinctions defines
every relation closed under flipping every point (a CNF of the relation, one hidden distinction added to every clause, long clauses
split; Schaefer 1978), so general signed not-all-equal systems realise C and D.

## 2. The census (exact, frozen)

900 jobs (n = 16, 18, 20 distinctions; genus 2, 3, 4; seeds 0 to 99); 453 reached their genus and were read, none dropped (the slowest
space took 594 of its 1,200 seconds; the part took 32 minutes). 179,559,422 free sets of four held distinctions (all 16 patterns occur).

| Size, genus | Spaces | A | B | C | D |
| --- | --- | --- | --- | --- | --- |
| 16, 2 | 23 | 352 | 4 | 0 | 0 |
| 16, 3 | 93 | 1,149 | 5 | 0 | 0 |
| 16, 4 | 100 | 1,859 | 15 | 0 | 0 |
| 18, 2 | 2 | 69 | 0 | 0 | 0 |
| 18, 3 | 50 | 357 | 4 | 0 | 0 |
| 18, 4 | 96 | 477 | 5 | 0 | 0 |
| 20, 3 | 12 | 14 | 0 | 0 | 0 |
| 20, 4 | 77 | 26 | 0 | 0 | 0 |

- **Positive control (run first): passed.** Synthetic floor states realising each of A, B, C and D were read as that class.
- **P1 holds: neither C nor D occurs** anywhere in the range. With `HOLD-COUNT-20261111-001`'s 1,128 spaces, no knot space of up to 20
  distinctions in either census reads the knot's own relation against a fourth distinction, or the switch.
- **P2 fails:** B per space at genus 3 is 0.054, 0.080 and 0 at 16, 18 and 20 distinctions, not growing. Decided four-point readings of
  every kind get rarer past 16 distinctions at fixed genus (A: 1,859 at 16 and genus 4, 26 at 20), the reverse of their growth from 10 to
  14 in `HOLD-COUNT-20261111-001`.
- **Seen after the run.** The B readings sit on few incidences: the 33 lie in 15 spaces built on 9 incidences (7 at 16 distinctions, 2 at 18), and the same
  incidence gives B at several genera (seeds 20 and 34 at 16 distinctions give it at genus 2, 3 and 4), so the reading belongs to which distinctions share
  knots more than to how the world is drawn.
- **Referee (`own_referee.py`, fresh code).** R1 recomputes the four classes by closing under generators and confirms that only C and D
  can give a mod-3 bit. R2 recomputes the A to D counts on every tenth space read (46 spaces) from the lines and signs alone. Result in
  section 4.

## 3. The proof attempt: not found

No proof that C and D never occur was found. What was learned:
- **The affine picture.** Modulo the global flip, a floor state is a choice of one odd side on each knot: a point of an affine space W over
  F2 in which each knot carries a vector of odd weight, with the points where some knot carries 111 removed. Every held difference and
  every output is an affine function on W. A decided non-affine map therefore needs every fibre over a forbidden (pattern, value) to lie
  inside the removed sets, each cut out by two coordinates; nothing in this alone separates {A, B} from {C, D}.
- **The composition reading.** As majorities of parities, A needs no parity, B one parity among the three, D two, and C a nested
  majority over parities. The spaces show majorities fed by at most one parity of held distinctions. A conjecture to test, not a result:
  a decided reading of held distinctions is a majority with at most one parity input.
- **A possible route.** Floor-state counts with held distinctions are sums of 4^g Pfaffian (matchgate) signatures in the drawn picture
  (`HANDLE-COUNT-20261106-001`); matchgate identities constrain one signature, so a bound on what a few handles can read may exist.

## 4. The referee: passed

R1: 256 self-dual maps, four orbits using all four inputs (A, B, C, D), and only C and D can give a mod-3 bit. R2: on all 46 sampled
spaces (every tenth read, by label; no space had a C or D instance to add) the fresh counts equal the census's: 160 readings of A, none
of B, C or D in the sample. The sample holds no B reading, so B's 33 census readings rest on the census code alone, which the positive
control and `HOLD-COUNT-20261111-001`'s cross-check (the same 20 A and 3 B on one space) cover. Run through `referee_parallel.py`
(8 minutes).

## What this establishes

- Proved: all four kinds are self-dual and realisable in general not-all-equal systems, so their absence is not forced by the law.
- Exact in the range (453 spaces of 16 to 20 distinctions, genus 2 to 4, with 1,128 smaller ones before): no knot space reads its own
  relation, or the switch, from four held distinctions; four-point readings thin out past 16 distinctions.
- Not established: whether any knot space at any size reads D or C.
