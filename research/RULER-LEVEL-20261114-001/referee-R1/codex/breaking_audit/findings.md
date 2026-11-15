# Breaking-case referee findings

Five serialized inputs are confirmed exactly at N=6, top level 1, s=1..3:

| Serialized input | Claimed and recomputed profile | Within-level knots containing actual tree siblings |
| --- | --- | --- |
| 1 | [3,3,4] | 4 |
| 2 | [3,4,4] | 10 |
| 3 | [3,3,3] | 10 |
| 4 | [2,2,2] | 26 |
| 5 | [3,4,4] | 33 |

`case_1.json` through `case_5.json` retain the complete rebuilt patterns,
cardinality-exhaustion counts, displayed bonds and every maximal proper
projection's satisfying states. `summary.json` collects their concise results.
All 15 bonds have Glucose4 refutations checked by the separate hint-free RUP
checker and 256 directly evaluated models, recorded in `certificate_audit.json`
and `case_<i>_s<s>.drup`. Proof deletion lines are safely ignored, retaining
only original or already proved clauses. Bogus empty-clause proofs on the live
base, empty-clause erasures and corrupted model states all reject.

The exact search enumerates every support meeting both designated levels in
increasing cardinality, with arbitrary remaining members anywhere among all
127 distinctions. It tests all assignments modulo valid NAE complement
symmetry, and checks every one-member deletion for fullness. A live NAE
relation has no singleton bond. Strict supersets of native triples are skipped
only because they cannot be minimal. Thirty-two comparisons with complete tiny
truth tables and the inherited existence-circuit search pass. The partitioned
candidate enumeration also agrees with plain combinations on all tested sizes.
The five table-based builds agree with direct bitwise builds. Their elimination
widths are 34,32,52,53,54, so no width-eight circuit or incomplete resolution
closure was substituted for exact support exhaustion. Total pattern/search time
was under 18 seconds; maximum process memory was below 61 MiB; one process ran
at a time with a 2300 MiB address-space cap. No prohibited source was opened.

**Block — sixth input absent.** The source log reports six failures at lines
20,21,24,36,45,64 and its totals agree at line 81. Its line 82 serializes only
five keys. The second [3,3,4] occurrence has no separately retained key. Thus
all four profile types are independently confirmed, while the exact six-case
and all-six-sibling claims remain unauditable from the permitted artifacts.
Recover the missing key or explicitly qualify those claims. This evidence gap
does not affect either acyclic theorem.

**Narrowing — finite evidence.** `proof.md:61` says "both ways", and lines
63–64 infer a constant and a halved rate; `ruler_level.md:20` and `:28` repeat
this. Every listed profile is at most [3,4,5], the ruler on this finite range.
These data show shortening and the displayed constant or repeated values only
for s=1,2,3. They establish neither lengthening nor a constant asymptotic bound
nor a half-rate law. Suggested replacement: "At N=6 and s=1..3, added
within-level knots yield profiles [2,2,2], [3,3,3], [3,3,4] and [3,4,4], each
shorter than the ruler at some tested separation." The advisor independently
warns against a general upper bound in `advisor_answer.md:29`.

**Not a block — siblinghood.** For tree placement
{g(w),h1(w)0,h2(w)1}, siblings are h1(w)0 and h2(w)1, sharing parent g(w).
Equivalently, parent(v0)=g(h1^-1(v)) and parent(v1)=g(h2^-1(v)); do not use
word-prefix parenthood (`advisor_answer.md:7`; `proof.md:42`). For example,
serialized input 5 has tree placement [0,2,10], parent 00 (id 3), siblings
001 and 100 (ids 8,11), tree knot [3,8,11], and within-level knot [8,11,12].
These siblings have different word prefixes. Each of the five inputs has
explicit witnesses under the correct definition.

Validation: V2 independent same-task reconstruction and proof checking, not
human review or external replication. There is no uniform theorem about
cyclic patterns in this computation. No lifecycle or canonical definition was
changed. Only this audit directory was written; raw regenerable proof probes
were removed after checked DRUP proofs were retained.
