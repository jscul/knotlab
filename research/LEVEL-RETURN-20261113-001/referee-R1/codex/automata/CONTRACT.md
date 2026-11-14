# Independent R2/R4 computation and proof

Owner: delegated automaton lane of `LEVEL-RETURN-20261113-001` referee R1.
This directory is the lane's only writable artifact family. Existing files
and concurrent work elsewhere are preserved. No scientific producer source
from the level-return experiment or proof is read or imported.

The scientific inputs are the address/word/placement definitions in
`research/ADDR-KNOTS-20261113-001/codex_spec.md` and the two full keys in the
earlier referee's `returns/91c75673….json` and `returns/f4fd01e9….json`.
The current study's prose, preregistration, advisor answer, and proof result
JSON are comparison targets, not executable proof inputs.

For each key, independently enumerate every address at every level 1–22.
The arrays contain the identity word at index 0 exactly. A placement input
is retained only when all three image addresses differ. The measured unit
is one `(key, level, placement)`; record the numbers of retained inputs,
excluded inputs, and retained monochromatic inputs under the stated state.
Check #2's address parity at every odd level from 3 and #3's first-letter
XOR last-letter state at every even level from 2. At #2's even levels from
4, record and deduplicate every violated knot, verifying its generating
placement and its input.

Separately construct a finite deterministic product automaton from scratch.
It retains all three word residuals, a state-computation memory for each
image, three monotone pair-difference bits, length parity, and length capped
at the theorem's minimum length. Its accepting inputs are precisely
retained monochromatic triples in the specified length domain. Prove the
two all-level state statements by empty accepting-state reachability.
For #2 at even lengths >=4, compare the accepting language for placement
`[0,8,10]` with `(00)+1(0|1)` by reachable symmetric-difference states;
prove emptiness for the other two placements. This comparison, rather than
finite counts, decides the exact bad-input language.

Controls: independently evaluate scalar word actions at all addresses
through level 8; test wrong level parity, wrong state, identity replacement,
and removal of the equal-image exclusion. Every negative control must
produce a concrete discrepancy or retained monochromatic witness.

Resource contract: one computation process in this lane at a time, <=3 GB,
each command <=15 minutes, total lane <60 minutes; interpreter is the
workspace `.venv/bin/python -B`. Arrays are regenerated and not retained;
the deliverables are source, compact JSON results, and a readable proof.
Finite enumeration is bounded evidence; the uniform result rests on the
finite-automaton invariant plus exhaustive finite reachability.
