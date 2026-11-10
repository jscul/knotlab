# The decoder's kernel at the needed degree

Epic `KERNEL-FRAC-20261110-001` (program complexity), 2026-11-10.

## The question

- **Where it comes from.** `HOLE-SEP-20261110-001` reduced row-linear separation for the binary left-pigeon principle LP_n (n + 1
  pigeons, n = 2^l holes) to the kernel K_k of a decoder into the unary pigeonhole principle, and left as sub-goal B107 whether that
  kernel is small enough at the degree Braun's criterion needs. The coordinator confirmed B107 at max effort and asked for the exact
  statement, the conjecture with predicted dimensions and a one-epic stop rule, frozen first.
- **Frozen first.** `kernel_statement.md` beside this note (1f78913cf): the degree k*, the bound with its constant-factor reading
  written out, the target (T), conjecture C (the kernel is the row-linear part of the inverse-counting identities' ideal) with seven
  predicted dimensions, and stop rules (a) a proof of (T), (b) a family whose share nears 1, (c) a kernel element outside the ideal.
- **Scope.** LP_n only. Nothing here transfers to the knot sphere's count, and nothing is a lower bound.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Conjecture C fails.** At all seven entries the kernel is larger than the identities' ideal, from k = 2 on (173 against 146 at n = 4; 12,287 against 11,422 at n = 32). Stop rule (c). | computed (pre-registered, exact) | B |
| 2 | **The top hole bit is one pigeon.** With n + 1 pigeons coded in l + 1 bits only pigeon n has the top bit, so the top bit of a hole row decodes to the single cell "pigeon n sits here", and two of them on different holes decode to zero. | proved | A |
| 3 | **The decoder route is closed for this encoding.** Those monomials make the separated share at most about (1 + k/(2l))·e^{−k/(2l+3)}, which outruns the criterion's gain e^{k/(15l²)}: through the decoder, Braun's criterion certifies at most 3S + \|J\| ≥ 5.2, at every degree and accuracy. Stop rule (b). | proved | A |
| 4 | **The 2n-pigeon principle escapes it.** Its codes fill all l + 1 bits, so no hole bit belongs to one pigeon, and it contains LP_n's clauses: a Res(⊕) bound for it would be one for LP_n. | proved (the escape); its kernel is not read | A |

## Answer

The kernel is not the identities' ideal, and it is not small: for LP_n with n + 1 pigeons it contains, through the top bit of the hole
rows, almost all of the row-linear space at the degrees that matter, and that closes the decoder route for this encoding. The cause is
the encoding, not the principle. Coding n + 1 pigeons in l + 1 bits leaves the top bit to one pigeon, and the decoder, which empties
every hole no pigeon names, reads that bit as "pigeon n is here", true of one hole at most. The left-pigeon principle with 2n pigeons
fills the codes, has no such bit, and contains LP_n.

## Reading

**Interpretation, not a theorem.**
- **What the decoder sees is the pigeonhole principle's own world.** Every kernel element found so far is a fact about a real placement
  of pigeons in holes (sums over holes equal sums over pigeons; pigeon n is in one hole) that LP_n does not assert, because LP_n lets
  empty holes name any pigeon. The route can only separate what such placements cannot decide.
- **On the stop rules.** Rule (b)'s threshold, a share of 1 − exp(−k*²/(6n)), is the edge of the sufficient condition (T), not of the
  bound itself; the route is closed here by conclusion 3, which bounds every degree and accuracy, not by that threshold.

## Lag cutoffs and census-only claims

- **No lag cutoff;** not a dynamics epic.
- **Census-only.** Conclusion 1 at seven small entries; the partial identification of the extra kernel was found after the run
  (`top_bit_family.py`).

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| The top bit is one pigeon (2) | n = 64 (checked to 32) | pass |
| The cap (3) | l = 31 to 40 (checked to 30) | pass: at most 5.2 |
| The two-top share against the frozen threshold (3) | l = 23, 24 (read to 22) | pass: 0.99999 and 0.9999999996 against 0.008 and 0.014 |

The script is `stress_test.py` beside this note, its output `stress_test.json`; registered before launch as KERNEL-FRAC-S1, it ran
in 148 seconds.

## Literature and provenance

- **Sources.** Braun, arXiv 2609.23015 (§§3–4, 9); `SEP-LEFT-20261110-001A`, `HOLE-SEP-20261110-001A`.
- **Classification.** Conclusions 2 to 4 are new as far as found and elementary; conclusion 1 is a refuted conjecture of this program.
  No lower bound is claimed.

## Workspace assumptions

- **Relied on.** None of the register's entries.
- **Added.** None.

## Ratio

Since the epic opened:
- **Substantive.** One proof (A), one pre-registered computation (B), the post-hoc identification, one stress test.
- **Administrative.** The frozen statement, this note and the closure.

## Pending the owner

- None new.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the decoder's kernel at the needed degree | **Status:** Obstructed | Conjecture C fails, and the top hole bit closes the route for n + 1 pigeons |
| Local direction — the decoder route | Research directions | Closed for n + 1 pigeons; open for 2n pigeons, whose bound would give LP_n's |
| Broader exploration — G3 | Known alternatives | Cutting planes (B82), the parity reduction (B101) |
| Long-term goal — G3 Hardness at three places | Obstruction learned | The decoder separates only what real placements cannot decide; the encoding decides which those are |

**Corrections:** none. **Goals:** a G3 checkpoint (obstruction learned); B107 taken; sub-goal B114 added. **Assumptions:** none.

- **What the attempt leaves open.** The decoder's kernel for the 2n-pigeon principle; the rest of K_2 beyond the identified families.

**Next step:** Research directions — the 2n-pigeon principle recommended.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The decoder route for the 2n-pigeon left-pigeon principle (G3) | 3/3 — Barrier | 2/3 — Testable | Freeze the target first. Then prove a separated space with spare rows: monomials avoiding a set of O(kl) spare holes and pigeons, separated by a cube that parks a hole's pigeon pair in a spare hole; check the cube identities and the kernel's meeting with that space on n = 4, 8 → a lower bound for LP_n through Theorem (R) and Braun's criterion at k ≈ n/(C l³), or the step that fails | Recommended |
| 2 | Cutting planes on the count (sub-goal B82, G3) | 3/3 — Barrier | 1/3 — Stated | As recorded | Alternative · deferred |
| 3 | A parity reduction from PIGEON to SINK (sub-goal B101, G3) | 3/3 — Barrier | 1/3 — Stated | As recorded | Alternative · deferred |

1. **The 2n-pigeon principle.** Payoff 3: a dag-like Res(⊕) lower bound for it is one for LP_n, the first for a PPADS-complete
   principle as far as found. Concreteness 2: the spare-row cube is sketched (it avoids every kernel family found, since those all use
   spare rows or the top bit), but its proof and density count are not written.
2. **Cutting planes.** As in `COUNT-SYSTEMS-20261110-001`.
3. **The parity reduction.** As in `RES-XOR-COUNT-20261110-001`.

**Recommendation.** Research directions, direction 1 recommended and recorded as sub-goal B114 under the owner's rule for untaken 3/3
directions, for the coordinator to confirm.
