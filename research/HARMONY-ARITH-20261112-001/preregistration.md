# Pre-registration: arithmetic of harmonies without a zero

Epic `HARMONY-ARITH-20261112-001` (G8 with G1; program mathematics), written on 2026-11-12 before the census runs. The owner asked
what subtraction and division of logical harmonies are, and on 2026-11-12 at 03:07 UTC asked for this test to jump the queue ("Let's
jump it, please continue"); the design follows the coordinator's proposal and is challengeable. Code frozen with this file in
`proofs/HARMONY-ARITH-20261112-001A/HARMONY-ARITH-20261112-001A-P001_binding_and_harmonies/` (`harm_lib.py`, `check.py`,
`harm_referee.py`; the directory's slug predates the word "stitch" below). The canonical K1–K3 test is unchanged.

## Words

As in the guide's glossary (periodic, one shift, base, overlap, shared distinction). New words, chosen with the advisor model (Fable
5.2, consulted on 2026-11-12) and added to the glossary in the commit that closes this epic:

- **Harmony** (the owner's word; this reading is assumption A70, not the harmony of proof theory): a periodic base along one shift all
  of whose allowed states repeat. It then has finitely many states up to shifting. Literature: a finite subshift.
- **Period of a state:** the least shift that returns the state to itself (not the period of the base, which here is 1).
- **Orbit** (the literature's word, as in dynamics): a repeating state together with all its shifts.
- **Stitch:** a knot of one fixed kind, at every shift, holding distinctions of both of two harmonies, such as one on (a_{i+s},
  a_{i+t}, b_{i+u}); two harmonies with stitches are **stitched**. Two harmonies **overlap** at s when a_i and b_{i+s} are one shared
  distinction at every shift.
- **Offset:** for two orbits of periods p and q, the shift between their states counted modulo gcd(p, q) (literature: relative phase).
- **Antiperiodic** (the literature's word): flipping every value of the state is the same as shifting it by half its period.

The bases tested have one distinction x_i at every whole number i and, for each of one to three knot kinds (0, a, b) with
0 < a < b ≤ W, a knot on (x_i, x_{i+a}, x_{i+b}) at every i; W is the span. Literature: a one-dimensional shift of finite type,
read through its transfer (de Bruijn) graph on windows of W values.

## The question

The coordinator's four: (1) stitch or overlap a harmony of period p with one of period q: which periods do the allowed states have,
is one forced (lcm, gcd, other), and does it depend on how they are put together? (2) Does the law read "p divides q" or "p and q
share a divisor" as a yes-or-no fact? (3) Is there a native difference, a harmony of period |p − q| or p mod q left by the stitching
(a beat)? (4) Which of this the law forces, and which is true of any constraint on repeating states (settled by definition)?

## Settled by definition (proved by hand, for any law)

**Lemma S (stitching).** Let harmonies A and B be stitched by stitches of one kind or made to overlap, under any law.
(a) Every allowed state of the stitched base restricts to an allowed state of A and one of B, since all their knots remain.
(b) So every allowed state is a pair (u, v) of repeating states and repeats, with period lcm(per u, per v).
(c) With no stitch at all, the pairs drawn from an orbit of period p and one of period q form exactly gcd(p, q) orbits, one for each
offset, each of period lcm(p, q).
(d) Stitches and overlaps are the same at every shift, so they keep or remove each of those orbits whole: the stitched states drawn
from the two orbits form between 0 and gcd(p, q) orbits, one per surviving offset, each of period lcm(p, q).
(e) So no stitched state drawn from orbits of periods p and q has period |p − q| or p mod q: its period is lcm(p, q), which is at
least max(p, q). A beat can only be a reading made from a stitched state, such as a_i ⊕ b_i, which by the canon is a classifier of
values, not a harmony of the base.

*Proof.* (a) is immediate. (b): a pair sequence returns to itself under a shift exactly when both parts do. (c): the pairs
(u, shift^k v), k = 0 .. q − 1, are permuted by the shift, which adds p to k modulo q on returning u to itself; the orbits of k under
adding p modulo q are the gcd(p, q) residues of k modulo gcd(p, q) (Chinese remainder theorem). (d): shifting a state of the stitched
base gives a state of it, and a stitch holds at every shift of a pair exactly when it holds at every shift of any shift of it. (e)
follows from (b), since lcm(p, q) ≥ max(p, q) > |p − q| and lcm(p, q) ≥ q > p mod q. ∎

**Proposition M (the mirror pairs offsets).** Let the law be not-all-equal, so that flipping every value keeps every knot, stitch and
overlap satisfied, and let both orbits be antiperiodic, with periods p and q and g = gcd(p, q). Flipping every value maps the
stitched states to stitched states and acts on offsets by adding (q − p)/2 modulo g. This is the identity exactly when p and q
carry the same power of 2; otherwise it pairs the offsets two by two, so the number of surviving offsets is even.

*Proof.* Flipping u gives shift^{p/2} u, and flipping v gives shift^{q/2} v, so the flipped pair (shift^{p/2} u, shift^{q/2 + k} v)
is, after shifting back by p/2, the pair (u, shift^{k + (q − p)/2} v): offset k goes to k + (q − p)/2 modulo g. Twice that is
q − p ≡ 0 modulo g, so the map is an involution, and it fixes an offset exactly when (q − p)/2 ≡ 0 modulo g. Writing p = 2^i p₁ and
q = 2^j q₁ with p₁, q₁ odd and i, j ≥ 1: if i = j, then g = 2^i gcd(p₁, q₁) and (q − p)/2 = 2^{i−1}(q₁ − p₁), and q₁ − p₁ is even,
so (q₁ − p₁)/2 is divisible by the odd gcd(p₁, q₁) and g divides (q − p)/2; if i < j, then 2^i divides g, while (q − p)/2 = 2^{i−1}(2^{j−i} q₁ − p₁) carries
exactly 2^{i−1}, so g does not divide it. A fixed-point-free involution pairs the surviving offsets. ∎

So by definition, for any law, stitching multiplies periods (least common multiple), the shared divisor gcd(p, q) counts the offsets,
and nothing subtracts. What the law decides is which harmonies exist, which offsets a stitch keeps, and, for not-all-equal, the
pairing of M.

## Scoping before the freeze (disclosed)

Spans 2 to 6, the four laws below: every not-all-equal harmony state has an even period (2, 4, 6, 8, 10, 12), and 398 of the 400 at
span 6 are antiperiodic, the 2 others in the one pattern whose offsets are all even, which splits into two independent halves. Odd
parity gives periods 1, 3, 6, 7, 9, 14, 15, 21, 31 and 63; exactly-one gives multiples of 3; the clause law no harmony. No stitch or
overlap was computed. Spans 7 to 10 were not looked at.

## The census (frozen; exact)

- **Harmonies.** Every pattern of one to three knot kinds whose largest offset is the span W, for W = 2 to 10, under four laws:
  not-all-equal (the knot's law); odd parity (x ⊕ y ⊕ z = 1, a knot without the mirror; control law); exactly one (not a knot, as it
  fails K2; control law); the clause x ∨ y ∨ z (a knot without the mirror; control law). For each: empty, not a harmony, or a harmony
  with its orbits, their periods, and whether each is antiperiodic. Exact, by the transfer graph's core (`harm_lib.classify`).
- **Stitches.** Every ordered pair of distinct orbits (and each orbit with itself) found at spans 2 to 6 under not-all-equal, and, as
  the control law, under odd parity; 48 stitch kinds, (a_{i+s}, a_{i+t}, b_{i+u}) with s < t ≤ 3 and u ≤ 3, and (a_{i+s}, b_{i+t},
  b_{i+u}) with s ≤ 3 and t < u ≤ 3, under the same law; and 4 overlaps, a_i = b_{i+s} with s ≤ 3. For each, the surviving offsets.
- **Caps, set now.** Each part 60 minutes of wall-clock time and 16 GB, by its systemd unit; a part over its cap is reported as
  dropped and the predictions it bears on as unsettled.

## Predictions and failure criteria

- **H1.** Under not-all-equal every harmony state has an even period, at every span 7 to 10. Predicted: holds. **It fails on any
  harmony state of odd period**, and then the even-period rule was an accident of short spans.
- **H2.** Under not-all-equal, in every harmony whose knot offsets have greatest common divisor 1, every state is antiperiodic, at
  spans 7 to 10. Predicted: holds.
- **H3 (controls).** (a) Under odd parity some harmony state has an odd period at every span 7 to 10. Predicted: yes. (b) Under
  exactly one, every harmony period is a multiple of 3 at spans 7 to 10. Predicted: holds.
- **M (proved).** In every not-all-equal stitch or overlap of two antiperiodic orbits whose periods carry different powers of 2, the
  number of surviving offsets is even. A failure means a bug or an error in the proof: stop and find which.
- **Lemma S checks (referee).** Surviving shifts form whole offsets, and every surviving stitched state has period lcm(p, q).
- **R1.** For some stitch kind and some periods p and q, two different pairs of orbits with those periods keep different numbers of
  offsets: the law reads the orbits, not only their periods. Predicted: yes, if some period has two orbits; otherwise reported as not
  testable.
- **R2.** No stitch kind or overlap allows a stitched state exactly when one period divides the other, across all not-all-equal orbit
  pairs. Predicted: none, weakly.
- **Control law.** Some odd parity stitch of two orbits whose periods carry different powers of 2 keeps an odd number of offsets, so
  M's evenness belongs to the mirror. Predicted: yes.
- **Answer by rule.** The harmonies by law and span, H1 to H3, M, R1, R2 and the control, read against Lemma S. Stop there; report and
  hold.

**Referee (fresh code, `harm_referee.py`).** R1: every verdict and period at spans 2 to 8 under not-all-equal, odd parity and exactly
one recomputed from the window graph as a 0/1 matrix (a harmony when the core is a permutation matrix). R2: every stitch and overlap
recomputed over all q shifts, not only offsets. R3: every surviving stitched state's period computed from the pair sequence.

Known mathematics, checked before the freeze: periodic points of shifts of finite type and the period of a transfer graph as a
greatest common divisor (Lind and Marcus 1995); the Chinese remainder theorem for (c); commensurate and incommensurate locking and
domain walls in periodic models (Frenkel–Kontorova; the ANNNI model's devil's staircase, Bak 1982); the periods of linear recurrences
over two values, which divide 2^k − 1 (Golomb); and forced periods 2a of two-colourings of the whole numbers that avoid monochromatic
translates of certain sets ("Vertex Ramsey problems in the hypercube", arXiv 1211.0168), the nearest work to H1 found. Not found in
that bounded search: the even-period rule for not-all-equal harmonies. Proposition M is elementary and was not searched for.

Assumptions in force: A70 (this epic's reading of "harmony"); A58 is not used. Nothing here bears on P versus NP.
