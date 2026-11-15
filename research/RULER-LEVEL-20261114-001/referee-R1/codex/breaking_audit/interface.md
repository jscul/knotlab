# Breaking-case referee computation

Owner: `recompute_breaking_cases`, scope `RULER-LEVEL-20261114-001`.

Question: do the recorded finite breaking cases have their claimed least bonds,
and do within-level knots contain actual siblings in their tree-type placement?

Branch: code analysis; independent referee validation, not a new study.
Inputs: `exploratory/tree_plus_within.log` (data only), the permitted proof and
notes, and the previous independent referee's address actions and pattern code.
Forbidden inputs: all study/exploratory/proof-family Python named in the brief.
Outputs: reconstructed patterns, exact least-bond results at N=6, k=1,
s=1..3, explicit sibling witnesses and bond projection certificates.

Exact method: enumerate every crossing support by cardinality, partitioning it
uniquely into its members of A, B and their complement. Check all assignments
modulo global complement symmetry using the independently rebuilt NAE relation.
A bond is a non-full support for which each one-member deletion is full. Native
triples and already proved non-full proper subsets may remove only nonminimal
supersets. No finite sample is used to establish a lower bound.

Controls: compare the actual enumeration and inherited exact search with full
truth tables on tiny patterns; reject a deliberately corrupted satisfying state.
An additional complete truth-table control checks the candidate enumeration.

Resource ceiling: one Python process, address space at most 2300 MiB; each
invocation under 20 minutes. Use the existing virtual environment, `python -B`.
Stop when the five serialized inputs are checked or an explicit resource limit
prevents exactness. The sixth reported input has no key in permitted artifacts.

Nonclaims: no asymptotic growth, no general effect of adding knots on bond size,
no audit of the unknown sixth description or the other 74 generated inputs.
The allowed circuit search cannot compile the five N=6 cases at width eight;
their measured elimination widths are 32 to 54. The optional resolution module
is sound pruning, not a complete bounded-implicate enumerator on its own.
