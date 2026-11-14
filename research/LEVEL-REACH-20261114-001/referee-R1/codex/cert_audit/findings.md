# Certificate audit

All sampled **bond certificates passed**. This validates their displayed
supports as bonds in the rebuilt finite pattern; it does not validate the
search's global least-cardinality or exhaustion claims.

The audit checked 20 `(key,s)` cells: four deterministic cells in each of the
chained, direct, other and undecided strata, plus four requested cells with
below-target members. Every numeric claim nested in those cells was checked:
237 claims using 184 distinct retained CNF/LRAT pairs, including
target-restricted and per-target claims. It checked all 3,236 recorded
state-pool entries and all 4,028 maximal-proper-subset assignment references.
Counts include repeated uses of the same certificate or state.

For every sampled claim:

- The independently rebuilt NAE clauses plus the forbidden assignment's units
  equal the retained CNF as a **clause multiset**, allowing clause reordering.
  The corresponding clause sets also agree.
- The uncompressed CNF and proof SHA-256 digests and proof byte count agree
  with the record. The CNF digest also agrees with the retained filename.
- A fresh LRAT adapter ignored all hints and independently tested every
  addition using the earlier referee's `RUPChecker`: 3,619 addition checks
  passed. Retaining clauses across 154 deletion lines is sound, because every
  retained added clause was already proved. Every proof derived the empty
  clause from the rebuilt CNF and the forbidden assignment's units.
- Every recorded state actually satisfies every rebuilt clause. For each
  maximal proper subset, its referenced states realize all assignments;
  the complete roster contains exactly one subset for each omitted member.
  Reported acceptance booleans were not used as evidence.

The positive control passed. Malformed LRAT, an out-of-range literal, a
purported refutation of a satisfiable formula, a changed CNF clause, and a
one-bit mutation producing an invalid state were rejected. A hint mutation is
deliberately irrelevant to this hint-free audit; this audit does not certify
the correctness of the producer's LRAT hint traversal.

The complete numeric-certificate inventory found 36,213 claims: 2,894
anywhere, 2,891 target-restricted, and 30,428 per-target. All 12,644 referenced
numeric-certificate pairs exist, with no inconsistent repeated digest or byte
metadata. This is a file/provenance inventory, **not** a full proof or state
recheck. The gzip results decompress to the recorded raw SHA-256
`19cc32eed12dccb0c24ae34494e03af5e82063c90a154ed309716e85196c673f`.

**Retention gap:** all 23 dead-union records supply only textual checker
success, timing and solver status, with no CNF digest, proof digest or retained
certificate name. None of the freshly serialized full-union CNFs, with no
symmetry unit or either sign of a minimum-variable symmetry unit, has a
matching retained pair. This filename probe does not exhaust all possible
serializations. The decisive finding is that the records do not bind those
23 dead verdicts to independently retrievable proofs. Numeric-bond retention
is complete; dead-union proof retention is not established.

**Below-target supports are real, while necessity is unshown.** The following
reported anywhere supports and equal-size target-restricted alternatives all
passed the same formula, proof and state checks:

| Key prefix | s | Anywhere support | Target-restricted support |
| --- | --- | --- | --- |
| `58480a08` | 1 | `[7,15,1002]` | `[7,29,30]` |
| `58480a08` | 2 | `[11,44,806]` | `[9,25,41]` |
| `58480a08` | 3 | `[7,63,1021]` | `[11,50,101]` |
| `e1fc9d92` | 1 | `[9,26,40]` | `[7,29,30]` |

The member levels are `floor(log2(id+1))`: the first three anywhere supports
reach level 9, while their targets are levels 4, 5 and 6; the fourth reaches
level 5 with target level 4. Thus the assertion that all returned supports
stay within their target is false. These cases do not show that a
below-target member is necessary: a size-three restricted alternative exists
in each case. Their recorded `L_N = L_target = 3` still relies on search
optimality, beyond what these certificates alone prove.

There are 264 recorded `> 10` claims across the anywhere, restricted and
per-target contexts. Their evidence is search exhaustion, described as an
existential-elimination circuit with an unsatisfiable candidate query; these
are not bond refutations. This certificate audit neither reconstructs those
queries nor certifies their completeness. A bond certificate proves one
support is inclusion minimal, and does not exclude a smaller bond elsewhere.

Reproduce with `.venv/bin/python -B` and `audit_certificates.py` from the
repository root. The completed run took 4.62 seconds with 31.1 MiB peak RSS,
one process, and a 3 GiB address-space cap. The code imports only the allowed
earlier referee's action routines and RUP checker; it reads no study Python
or C source. This is independent same-task AI referee validation, not external
replication. Exact selection, hashes, counts, per-claim checks and controls are
in `selection.json`, `inventory.json`, `sample_results.json`,
`dead_union_metadata.json`, `summary.json` and `controls.json`.
