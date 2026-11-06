# Re-querying and proof size for Tseitin formulas

Epic `URQUHART-TSEITIN-20261020-001`, closed 2026-10-20.

## What was found

The idea was a size version of graph-searching monotonicity: "re-querying
doesn't save positions". That is Urquhart's conjecture, which says regular
resolution polynomially simulates resolution on Tseitin formulas. It is listed
as open by Itsykson, Riazanov and Smirnov (2022). The width version is the
monotone cops-and-robber theorem of Galesi, Talebanfard and Torán.
[Proof](../../proofs/URQUHART-TSEITIN-20261020-001B/URQUHART-TSEITIN-20261020-001B-P001_hole_faithful/proof.md).

- **It is the same open problem.** For bounded degree, the conjecture on a
  family is equivalent to general resolution needing 2^{Ω(tw)}. So the earlier
  epics already prove it on:
  - graphs with cell systems;
  - minor-free graphs, planar included;
  - linear-treewidth families;
  - families with compact minors.
- **Branching programs stop at regular resolution.** Read-2 programs of size
  2m + 2 compute satisfiable Tseitin formulas, so the route Itsykson et al.
  used for regular resolution cannot reach re-reading.
- **The hole picture gives a bound for one natural class.** Walk a random
  critical assignment down a refutation. Suppose no step forgets a variable
  touching the region where the hole must lie; call such refutations
  hole-faithful.
  - The hole stays uniform on the clause's region.
  - Regions fragment like a size-biased random process, so every walk meets a
    clause with a balanced region.
  - Such a clause is falsified with probability 2^{−Ω(tw)}.

  So hole-faithful refutations need 2^{Ω(tw)}. Davis–Putnam refutations are
  hole-faithful.
- **The diagnosis.** A refutation of size 2^{o(tw)} would have to re-read
  variables, which is the regular bound, and take steps that forget at the
  hole's region (Theorem 4). On every checked graph a single such step makes
  the hole's posterior non-uniform: the walk then knows more about the hole
  than its clause says. That is the precise form of recontamination here, and
  it is exactly where both counting arguments stop.

## Where this leaves the Tseitin line

The general-resolution problem now has two mapped barriers:
- the scrambled wall networks, which defeat restriction methods;
- posterior bias, which defeats counting methods.

Neither has been crossed. The body of results around them is coherent:
- degrees for NS, PC, SoS and SA governed by layouts;
- size 2^{Θ(tw)} on cellular and minor-free graphs for resolution, PCR, SoS
  and SA;
- the equivalence above.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — size monotonicity (Urquhart's conjecture) | **Partially successful** | Identified the open conjecture and its equivalence with the open problem; settled it on four families; proved a lower bound for hole-faithful refutations; located the obstruction. The conjecture is not resolved. |
| Local direction — counting with a random hole | Practically exhausted for a bounded attempt | What remains is to show that posterior bias cannot be exploited cheaply. That is the open problem itself; no cheaper discriminator was found. |
| Broader exploration — Tseitin lower bounds | Two barriers mapped | Restriction methods fail on scrambled walls; counting methods fail under posterior bias. No known technique addresses either. |
| Long-term goal — breaching proof-complexity barriers | Obstruction learned | The open problem is located precisely, from two sides. |
| Next recommendation | **Next step:** Continue, by converting. Write one self-contained note on Tseitin formulas beyond expanders, covering:<br>• the degree characterizations;<br>• the size theorems for cellular graphs;<br>• the equivalence with Urquhart's conjecture and its settled cases;<br>• the two barriers. | The program's strongest and most coherent result set. Completion check: every claim replayed by one script. |
| Interest — that conversion | **2/3, Promising** | Plausibly new as a whole and one story. Pieces may be folklore, and the size results use standard techniques. |
| Execution — that conversion | Deferred to the owner | The alternative is a full pivot to a different barrier, after a bounded scan. |
