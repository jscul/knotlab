# Where the model's values sit: Spekkens's toy theory and the phase it lacks

Epic `TOY-PHASE-20261127-001`, under G18 Comparing growth laws, at the owner's go-ahead ("Yes continue with 1") on
direction 1 of the overall assessment of 27 November 2026: place the model against Spekkens's toy theory and the phase
groups of Coecke, Edwards and Spekkens. Design, arguments and predictions frozen before the code was run, after an
independent review (section "Review before the freeze"; the advisor was unavailable). The results follow in sections of
their own; nothing above them changes except by a dated notice. The canonical K1–K3 test is unchanged, and nothing here
searches for a native source.

## The question

The quantum account found that every table above the classical limit needed something supplied, and that the missing
piece is one: a relation between two allowed states that carries a phase. The literature has a classical theory that
reproduces much quantum behaviour without that piece, Spekkens's toy theory, and an exact statement of the one place where
it differs from the stabilizer part of qubit quantum mechanics: the phase group, Z2×Z2 against Z4. This study places the
model against both, on objects the record already has.

1. **One knot.** Is one three-place parity knot exactly one toy bit: its allowed states, distinctions and allowed changes
   the toy bit's underlying states, questions and shifts? Is the owner's picture of a distinction (a choice between 00/11
   and 01/10 for the other two) the toy bit's rule that each question is the sum of the other two?
2. **The phase on one knot.** Among the operations on a knot's allowed states that keep one distinction's value, which
   carry a second read to the third, and what does each give when applied twice? Which of them does the model have?
3. **The closure.** On growth's four-knot closure with its three readers, is the even closure growth makes a toy state,
   and is it a stabilizer state? Which pairings of the distinctions into readers does the toy theory accept?
4. **Two forms.** Does the closing sign follow from the phase group: even when a reader's second read comes from its first
   by a toy phase (order two), odd when it comes by a phase of order four?
5. **The supplied pieces.** In the record's coherent constructions of the three-reader table, do the two reads assigned to
   each reader anticommute, so that their product squares to −1 (in the literature's terms, a phase of order four)? And
   for two readers: what does the sibling study's 2.1078 need beyond that?

## In standard terms

Spekkens's toy theory (2007) is a classical statistical theory. An elementary system, a toy bit, has four underlying states
(the literature's ontic states), written as two bits (q, p); its three nonzero linear questions q, p and q + p are the
analogues of the Pauli Z, X and Y. In the form of Spekkens (2016), which the code applies, a valid state is uniform on the
underlying states consistent with known answers to a set of questions that pairwise commute under the bracket
ω((a, b), (a', b')) = Σⱼ (aⱼb'ⱼ + a'ⱼbⱼ) mod 2, and it is pure when there are n independent known questions for n toy
bits. The theory is local and noncontextual: no Bell violation and no Kochen–Specker contradiction. Coecke, Edwards and
Spekkens (2011) show that, within their framework, it and the qubit stabilizer theory differ in one structure, the phase
group of an observable (Z2×Z2 for the toy bit, Z4 for the qubit), and that the three-reader correlations of the
literature's GHZ state take exactly two forms, one for each group. The population is one three-place parity knot and
growth's closure: four parity knots on six distinctions, every two sharing one, which is the holder pattern of Mermin's
three-reader argument.

## Objects and maps

**The closure.** The three-knot ring ((0, 1, 2), (1, 3, 4), (3, 0, 5)) grown one round by ordinary parity growth with the
archived engine (`research/FORBID-EDITS-20261126-001/forbid.py`), exactly as in the no-whole-state fixture
(`research/NO-WHOLE-STATE-20261126-001/fixture.py`). Its knots are {0, 1, 2}, {1, 3, 4}, {0, 3, 5} and the closing knot
{2, 4, 5}, with the closing law as growth makes it (even). Its readers are the three pairs of distinctions that no knot
holds together, {2, 3}, {0, 4} and {1, 5}: reader i holds the shared distinction sᵢ that parent i does not hold and parent
i's loose distinction lᵢ (the birth-sign study's notation; lᵢ = sⱼ + sₖ). A context is one read per reader; the four
scored contexts are the four whose three reads form a knot: one reader reads its loose distinction (three contexts) or all
three do (the closing knot). The three-reader target is the record's: each scored context uniform on the words of its
knot's parity with the closing knot odd, each unscored context uniform on all eight. The three-reader score is the
record's: the four scored contexts weighted equally, each counting the chance that its parity is the target's.

**Map K, a knot as a toy bit.** An allowed state (A, B, c) of a three-place parity knot goes to the underlying state
(q, p) = (A, B); A, B and c are then the questions q, p and q + p (c relabelled under the odd law). Scaffold: which two
distinctions give the coordinates (six ordered choices).

**Map R, a reader as a toy bit or a qubit.** Each reader's two distinctions go to two distinct nonzero questions of one toy
bit, or to two distinct Paulis of one qubit (six ordered choices per reader, 216 in all, the same under the
correspondence q, p, q + p to Z, X, Y). A knot's law then states the answer to one question of the three toy bits, or an
eigenvalue of one product of Paulis. Scaffolds: the assignment (216 choices) and the pairing (the record's readers against
the other 14 ways of pairing six distinctions into three readers). Both maps are registered as the scaffold A313.

**Phases.** Relative to one read, the toy bit's phase group is the set of permutations of its four underlying states that
keep that read's answer; the qubit's is the set of phases diag(1, iᵏ) in that read's basis (Coecke, Edwards and Spekkens,
whose phase group, the unbiased points under their multiplication, acts through exactly these maps). Every toy phase has
order at most two; the qubit's phase S = diag(1, i) has order four, carries the X read to the Y read and, applied twice,
reverses it. This note calls S and S³ the phases of order four. The third-reader study's "quarter-turn read" is a read built
with such a phase (the literature's Y); the word is not used here for anything else. No new word is introduced: toy bit,
underlying state and phase group are the literature's.

## Prior work in the program

Searched before freezing, each with `--until` this date and `--exclude` this epic:

`python3 -B scripts/track.py objects "closing sign of the four-knot closure read by three readers" --until 2026-11-27 --exclude TOY-PHASE-20261127-001`
`python3 -B scripts/track.py objects "Spekkens toy theory phase group GHZ Mermin" --until 2026-11-27 --exclude TOY-PHASE-20261127-001`
`python3 -B scripts/track.py objects "four knots on six distinctions every two sharing one" --until 2026-11-27 --exclude TOY-PHASE-20261127-001`
`python3 -B scripts/track.py objects "one parity knot allowed changes" --until 2026-11-27 --exclude TOY-PHASE-20261127-001`

- `BIRTH-SIGN-WEIGHT-20261127-001` — same object: the closure's closing sign, the 64-probability target and the coherent
  constructions this study places (P5), and the sibling score of P6; their tables are recomputed here only as a gate.
- `NO-WHOLE-STATE-20261126-001` — same object and population (not a top index row, the source of the fixture): the grown
  closure, its readers and the identity "the closing sign is the cost of reordering"; this study uses its definitions.
- `EVENTUAL-R-20261126-001`, `VALUE-CHANGE-20261126-001` — relatives: rule R (values commute exactly when some knot holds
  both) and reading a change. On the closure rule R makes exactly the readers' pairs fail to commute, which is where the
  toy theory's rule says two questions cannot be known together; this study asks what separates the two readings of that
  same pattern.
- `THIRD-READER-20261126-001` — a relative: the source of the "quarter-turn read"; placed here in the phase group.
- `ENTANGLEMENT-READ-20261120-001` — a relative: readings on one common weighting obey the classical bound (Fine); the toy
  side of this study is a case of it.
- `SPLIT-KNOT-METER-AND-CLOSING-TRIPLE-20261121-001`, `SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001`,
  `JOINT-PARENTS-AND-ERASURE-20261120-001` — relatives on other closures and supplied meters (the cost of reading closing
  signs, receiver ticks); not used.
- `BARE-NAMES-20261110-001`, `TWO-PATTERNS-20261126-001` — unrelated (matched "theory" and "toy" in other senses); no
  program record compares the model with Spekkens's toy theory or the phase groups.
- `REVIEW-LEADS-20261123-001`, `IDLE-PHASE-AND-TREE-CLOSURE-20261121-001`, `KNOTS-ALONE-20261111-001`,
  `SWITCH-RECEIVERS-20261126-001`, `KNOT-LOOPS-20261019-001` — unrelated populations matched on counting words.
- `RECURSION-LEAD-20261126-001`, `TREE-PROOF-20261127-001` — unrelated: allowed changes in another role (exchanges,
  pair costs).

## Prior work outside the program

- R. W. Spekkens, toy theory ([arXiv:quant-ph/0401052](https://arxiv.org/abs/quant-ph/0401052); Phys. Rev. A 75, 032110,
  2007): reproduces complementarity, no-cloning, teleportation, dense coding and interference-like effects; no Bell
  violation and no Kochen–Specker contradiction.
- R. W. Spekkens, "Quasi-quantization" ([arXiv:1409.5041](https://arxiv.org/abs/1409.5041), 2016): the toy theory as a
  classical theory with an epistemic restriction, known questions pairwise commuting under the bracket above.
- M. F. Pusey, "Stabilizer notation for Spekkens' toy theory" ([arXiv:1103.5037](https://arxiv.org/abs/1103.5037), 2012).
- B. Coecke, B. Edwards and R. W. Spekkens, "Phase groups and the origin of non-locality for qubits"
  ([arXiv:1003.5005](https://arxiv.org/abs/1003.5005), ENTCS 270, 2011): Z4 against Z2×Z2; the GHZ correlations take
  exactly two forms.
- A. Fine (Phys. Rev. Lett. 48, 291, 1982): a common joint distribution exists exactly when the Bell inequalities hold.
- N. D. Mermin (1990): the three-reader argument on the GHZ state. L. J. Landau (Phys. Lett. A 120, 54, 1987): the square
  of the two-reader operator is 4 − [A₀, A₁][B₀, B₁], so a score above 2 needs non-commuting reads on both sides.
- R. Horodecki, P. Horodecki and M. Horodecki (1995): the best two-reader score of a two-qubit state from its correlations,
  used by the sibling study for its optimum 2√10/3.

Known: all of the mathematics. Not found: the model's own objects (growth's closure, its readers, its allowed changes, the
record's signed constructions) placed in these terms.

## Settled by construction (stated, not tested)

- Under Map R the toy theory's reading probabilities of a toy state are the marginals of its uniform weighting, so where
  the closure is a toy state its 64 probabilities equal the toy theory's, and its three-reader score is at most 3/4.
- Each of the six distinctions lies in exactly two knots, so the closing sign (the parity of the sum of the four laws) is
  unchanged by relabelling any read; it is the invariant compared below.
- In any theory where every read has a value (the toy theory, the model under A295), the four scored contexts' parities sum
  to zero, so the closing law is even and the three-reader score is at most 3/4 (Fine; Mermin).
- In the closure every knot holds one distinction of each reader and two knots share one distinction, so two knots use
  different reads at exactly two readers: under any assignment of Map R their questions commute, and so do their Paulis.
- P4's toy half repeats P3: the closure under Map R with sᵢ to p and lᵢ to q + p is the toy GHZ state phased on one toy
  bit, and phasing a toy bit is the same as exchanging that reader's two reads.
- In P5, once the reads are written down, the product of the four scored context operators is ±1 as an identity,
  whatever the state; P5 places the constructions and cannot otherwise fail.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gates: the regrown closure is the fixture's (four knots, every two sharing one, readers {2, 3}, {0, 4}, {1, 5}, closing law even); the toy-state test accepts the toy GHZ state written in toy coordinates and rejects a state that knows both questions of one toy bit; the stabilizer computation reproduces the record's target, 64 of 64; the rebuilt birth-sign constructions reproduce its scores (1 and 64 for the signed state with change reads and for the confined reads, 64 for the equal-positive state with rephased reads, 3/4 and 56 for value reads); a mutant that composes the toy phases in Z4 flips the closing sign. | any gate fails |
| P1 | One knot is one toy bit: under Map K, for both parity laws and all six coordinate choices, the four allowed states, three distinctions, three nonzero allowed changes and six one-read states correspond one to one to the toy bit's four underlying states, three questions, three nonzero shifts and six pure states, with every incidence kept (which change flips which distinction; which state answers which read). Each distinction is the sum of the other two (the owner's choice between 00/11 and 01/10). Control: the three-place not-all-equal knot has six allowed states and one nonzero allowed change, so no such correspondence exists, and its third distinction is not a function of the other two. | any incidence breaks under parity, or the not-all-equal control matches |
| P2 | The phase on one knot (even law): of the 24 permutations of the four allowed states, exactly 4 keep the value of A; they form Z2×Z2 and each applied twice gives the identity. Exactly two (the swaps inside one value class of A) carry the B-read to the c-read, one exactly and one up to relabelling (which is which depends on the law). The third, the swap of both classes, is the knot's own allowed change {B, c}; it carries the B-read and the c-read to their negations. So of these four the model has only the identity and {B, c}, and no operation of its own carries one read to another. In the qubit, S = diag(1, i) in the A basis carries the B-read (X) to the c-read (Y), and S² = Z carries X to −X: Z4. | the group is not Z2×Z2, an element has order 4, the counts differ, or S² ≠ Z |
| P3 | The closure under both theories. (a) With the record's readers, under all 216 assignments, the even closure's allowed states form a pure toy state of three toy bits (pairwise commuting laws, three independent known questions, 8 of 64 underlying states), and its 64 reading probabilities equal the toy theory's; the odd closure has no allowed state. (b) Under all 216 assignments of distinct Paulis, the four knot operators commute and their product is −1, so no qubit state has all four laws even: the even closure is a stabilizer state under none of the 216, and the odd closure under every one, where its state reproduces the record's target (score 1). (c) Over all pure toy states of three toy bits (predicted 1,080) the best three-reader score on the record's target is 3/4, attained by the closure's own state. (d) Pairings: exactly 7 of the 15 pairings give a toy state, the record's and the six that keep exactly one pair no knot holds together; in each of the eight with no such pair, the three knots that each hold both distinctions of one reader fail to commute with one another and the fourth knot commutes with all three. The verdict does not depend on the assignment. | an assignment fails (a) or (b), a toy state scores above 3/4, the count is not 7, or the classes or failing knots differ |
| P4 | Two forms on the closure: give reader i's second read by a phase sᵢ applied to its first, and the state a phase g on one toy bit or qubit. In the toy theory, for all 16 choices of s₀, s₁, s₂, g among the two single swaps (the toy phases that change the read), the four scored contexts are certain and the closing sign is even; in the qubit, for all 16 choices among S and S³ (the state phased by S or S³), they are certain and the closing sign is odd. Without the state phase no scored context is certain. In both, the closing phase is twice the sum of the three phases, which Z2×Z2 sends to the identity and Z4 to Z. | any toy choice closes odd, any qubit choice closes even, a scored context is uncertain with the phase, or certain without it |
| P5 | The supplied pieces: in each of the birth-sign study's three coherent constructions (the signed state read with Z_{sᵢ} and the change Tᵢ; the equal-positive state with the rephased reads; the reads Z_{sᵢ}X_{lᵢ} and X_{sᵢ}), the two reads assigned to each reader anticommute, so their product squares to −1, and the product of the four scored context operators is −1. In the first two, a reader's second read also flips the other readers' loose distinctions; in the third, each read stays on the reader's pair but takes every allowed word outside the eight. With the value reads Z_{sᵢ} and Z_{lᵢ} the two commute, the product squares to +1, the context product is +1 and the score is 3/4. Control: dropping the sign from the confined first read (X_{lᵢ} for Z_{sᵢ}X_{lᵢ}) makes the two reads commute, and the score falls to 5/8. | a construction's reads commute, a product squares to +1, a context product is +1, or the control exceeds 3/4 |
| P6 | Two readers. (a) Over all 60 two-qubit stabilizer states and every choice of two signed Pauli reads per reader, the best score is 2. (b) The sibling study's preparation, reduced as in its record to span{11, (01 + 10)/√2} for each reader, has amplitudes (1/√3, 1/√6, 1/√6, 1/√3) and is not a stabilizer state; on it every choice of signed Pauli reads scores at most 2, its reads X, Z and −ZRZ, R with R = (2√2 X − Z)/3 give (2 + 12√2)/9, and the best over all two-valued reads is 2√10/3. (c) With the reads X and Z on both sides, the square of the operator is 4 + 4 Y⊗Y (Landau), so a supplied state reaches 2√2, and that state is not a stabilizer state. (d) Making either reader's two reads commute caps the operator at 2. So the phase of order four on each side carries the three-reader table on a stabilizer state, but a two-reader score above 2 also needs to leave the stabilizer part, in the state or in a read. | any of (a)–(d) fails |

## Runs and stop rule

One script, `toy_phase.py`, exact where the objects allow (integers, bit masks, fractions; matrices whose entries are 0,
±1, ±i or 1/√2, compared to 1e-12 and reported as fractions with denominator at most 64; the irrational reads of P6 in
floating point to 1e-12). Run time under a minute, memory under 1 GiB, run under `prlimit` as in the sibling study; no
long run and no registration. The study stops when every prediction is scored, at the first mismatch for each part; it
runs no census, grows nothing beyond the record's closure, and does not search for a native source of a phase of order
four.

## Review before the freeze

Both advisor versions returned a usage limit, logged in `docs/ADVISOR_HIVEMIND.md`. An independent reviewer (a separate
session, read-only, reasoning by hand with no computation) checked the first draft. It found no wrong count or group and
confirmed by hand the 7-of-15 count, the 1,080 count, P2's four permutations, all 32 choices of P4 and P6's first claim.
Changed before the freeze in response:

1. P3(d): in each of the eight failing pairings three pairs of knots fail to commute, not one; the fourth knot commutes
   with all three.
2. P3(b) added at its suggestion, the sharper discriminator: the even closure is a toy state under every assignment and a
   stabilizer state under none (reader {0, 4} meets the knots in the order P₀P₄P₀P₄).
3. P4: the state phase is required (without it no scored context is certain), now a stated part of the prediction.
4. P5: in the change and rephased constructions a reader's second read acts outside its pair, so "two reads of one reader"
   became "the two reads assigned to each reader"; the control dropping the sign was added.
5. P6 recast: Pauli reads X and Z on both sides reach 2√2 once the state is supplied, so the earlier claim that the
   sibling score needs a read outside the stabilizer part was too strong; leaving the stabilizer part in the state or in a
   read is what it needs. The reduction to the class pair is now stated.
6. Words: "quarter-turn" and "turn" are no longer used as this note's own words (a word for a turn in a plane, already
   used for a read, and the toy elements it named have order two); "span n dimensions" became "n independent known
   questions"; the score's equal weighting of the four scored contexts is named.

The reviewer also noted that the 2007 counting rule, applied only to the parts as they stand, accepts one of the eight
failing pairings, and rejects it once other readers' reads are taken into account; the code applies the 2016 rule
(unverified in general). It judged P1, P3's bound and probabilities, P4's toy half and P5 to follow from the definitions,
and P3's classes and stabilizer count, P4 without the phase, the gates and the enumeration to be the parts that could fail.
