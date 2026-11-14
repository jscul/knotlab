# Direct growth and counterexample audit

Scope: `READ-RULE-20261114-001`, independent referee lane. All files named
below are in this directory. No network, Git mutation, publication, scope
change, or READ producer/checker Python read/import occurred.

**The material result is a counterexample to the literal syntactic converse.**
The parent's construction puts p opposite to q in main, then calls
S(a,b,c) with own x,w and `NAE(a,x,b)`, `NAE(c,x,w)`, `SELF(a,b,x)`.
At every S copy, a and b are carried and syntactically read, but their opposite
tie makes that reading constraint vacuous. The root r and the S-own members
instead form the chain `NAE(r,x_0,w_0), NAE(x_0,x_1,w_1), ...`.

Both wrapper variants independently give **L(d)=d+2** at absolute depths
d=1,...,6, with S-call length d−1: 3,4,5,6,7,8. The positive gadget variant
uses distinct arguments in every constraint and call. Its full key and digest
are in `growth_hand_read_exception_results.json`; its SHA-256 is
`8b467690607dc0175164151d87804573002010d35108da8458413487c227b2fb`.

`growth_hand_read_exception_argument.md` proves the uniform value with members
anywhere: deleting an absent pendant makes a link full and splits root from
target; all d pendants are therefore required, but root plus those pendants is
shattered. The explicit d+2 witness has every single deletion full. The uniform
part is a direct prose argument, distinct from the finite solver checks. This
family falls exactly under Theorem R's exception. It contradicts neither the
exception-free theorem nor the dichotomy. "Effectively read" needs a definition
if it is intended to exclude the exception. No theorem/lifecycle promotion is
made here.

**Q3 independently fails.** In both of the study's variants, at depths 1,...,6,
L=2 globally. The exact isolated gadget relation is u opposite to a; the pair
of root a and the target copy's own u is a bond. Complement closure and the
living usual limit exclude a one-member bond, including members beyond the
unfolded prefix. The a/target-x pair is shattered. The own w occurs in exactly
one NAE constraint and no call. See `q3_results.json` and `q3_audit.py`.

The direct attack found no counterexample to the dichotomy.

| Family key prefix | Wrapper | Absolute depths | Exact global values / retained cap |
| --- | --- | --- | --- |
| a43ab6412097 | no | 7,8,10,12 | 6,7,8,9 |
| 46540117e841 | no | 7,8,10,12 | 6,7,8,9 |
| 4dc882a6a1d7 | yes | 7,8,10,12 | 6,6,timeout,timeout |
| a430c16bc410 | yes | 7,8,10,12 | timeout at all four depths |

These are all-members searches over the entire explicit prefix, with every
covered S-copy at the stated depth eligible as target. For the ten successful
cells, the checked consecutive-triple structure admits the prior referee's
two-blank separator argument. A hypothetical smaller bond has all its members
at depth at most `2B−5+wrapper`, which is inside the searched prefix. Thus their
minima are global, rather than window or moving-prefix minima. The six 30-second
timeouts remain unknown. Full keys, witnesses, origins, and exclusions are in
`growth_deeper_simple.jsonl`; `growth_smoke.jsonl` additionally gives global L=7
at depth 8 for the first family.

Four unresolved census families were tested at absolute depths 2,...,6:
`2c048723bc85`, `a4b93391c243`, `714cdee7811a`, `d418f587a3d6`.
The first gives prefix minima 3,4,4,4,4; the other three give 4,4,4,4,4.
Only the size-3 cell is globally minimal: every possible smaller root-target
pair is already included. The remaining 19 cells are **exact prefix minima**
and global upper witnesses, not global lower bounds or uniform boundedness
proofs. See `growth_unresolved_prefix.jsonl`.

Two explicit sparse-level attempts also failed to give intermediate growth.
The ternary stall/advance family has global L=3 at depths 1,2,4,6,8: a branch
can retain the root arbitrarily long and then use a pendant NAE constraint.
The q=8 fixed-lag diagnostic has full-prefix minima 3,3,4,4,5 at depths
1,7,8,15,16, and exact reduced-prefix minima 3,4,5,6,7 at depths
7,8,16,24,32. Its delay is fixed, rather than increasing with depth.
**The q=8 family is outside the claimed ternary-S scope** and serves only as an
explanatory diagnostic. No global minimum or asymptotic theorem is inferred
from its prefix searches. See `growth_handdesigned.json`.

Validation reused the expressly permitted older direct-CNF search, including
its transitive FREE-TARGET search implementation. It used no per-call relation,
window, or semigroup implementation. Fresh MiniSat22 code enumerated every
successful witness's entire allowed projection and every single deletion;
search uses Cadical/Glucose. Single-deletion fullness implies fullness of all
proper subsets. Six old exact/brute controls agreed, and fresh invalid
shattered-pair, nonminimal-supersupport, and wrong-target controls all rejected.
The main p-q tie in the fresh family also rejects as a covered-target witness.
This is same-task, producer-independent validation, not external replication.

All commands used the workspace `.venv/bin/python -B`, one compute process,
and a 3-GiB address-space limit. One initial positive-gadget d=6 search exhausted
all smaller sizes but timed out finding the already known upper witness; it is
preserved in `growth_hand_read_exception_initial_cap.json` and the initial
script. The rerun searched smaller sizes only and separately checked the
explicit upper witness. No mathematical value was inferred from that timeout.

One source-version caveat is explicit: during the first deeper-simple run,
`growth_search.py` gained only the classification rule for minima at most 3.
Every successful row in that run has minimum at least 6, so the new branch was
unexercised and the search algorithm was unchanged. The exact launch source is
retained as `growth_search_launch_v1.py`; `growth_source_versions.json` binds
both versions and explains completion-time metadata. `growth_manifest.json`
binds outputs, own scripts, context sources, and transitive source hashes.

The literal occupancy count in the written pumping proof also needs the
parent's repair: allocate each W identity to one own block/side component;
its repeated port appearances cannot each count as separate members. The
parent owns the full interface and proof analysis. Finite-L existence should
be stated, or +infinity explicitly assigned to the lower-bound alternative.
