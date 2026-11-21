# The complete set of physical decorated tree replays

The exact census completes **3,739** decorated tree classes under each ordinary law. The parity closures occur in **four** classes, three from four-holder founders and one from a five-holder founder. Two of the four admit the supplied odd operator reading. All other representatives finish their fourth cut open or have an independently verified funding stall. Not-all-equal keeps a loose distinction on every funded cut. [Frozen design](preregistration.md) · [Lossless representative ledgers](../../artifacts/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B-E001_trees/representatives.json.gz)

## Coverage and physical naming

The five sizes have **2, 3, 6, 11 and 23** uncoloured tree shapes. Applying each shape's full automorphism group to every binary extra-opening mask yields **18, 54, 189, 700 and 2,778** decorated classes. Each class stores its decorated automorphism order $a$, labelled multiplicity $n!/a$, and the integer quarter-law mass $(n!/a)3^{n-k}$, where $k$ is the number of extra openings. For each shape and $k$, the labelled multiplicities sum to the number of labelled copies of the shape times $\binom{n}{k}$. Across a size they sum to $n^{n-2}\binom{n}{k}$. The exact mass denominators are **4,096**, **128,000**, **5,308,416**, **275,365,888** and **17,179,869,184**. [Per-decoration audit](../../artifacts/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B-E001_trees/representatives_audit.json)

The original named supports are lawful by the tree construction. Start with any legal word held by one selected founder. At each adjoining founder just one name is already fixed, so a remaining name can satisfy parity, or a remaining name can differ for not-all-equal. Processing the tree outward extends every allowed local word to the whole. To check essentiality, erase the selected source holder's rule, prescribe a forbidden local word there and use the same extension. The audit also reads literal source projections and essentiality on the named relabel controls.

Relabelling holders carries the old witnessed groups and their demands together. Within one funded group every parent supplies one loose distinction. If two canonical orderings consume different names, a bijection within each parent's loose distinctions aligns its complete list of contributions. Those distinctions have just one holder on the current cut, so the adjustment preserves all current supports. Match newborns by parent groups and fresh count, using a bijection between copies of any repeated group. The required fresh count, including the lookahead demand and any implied zero grant, depends on those same groups and the transported old relation. A bijection of newly minted names then transports all new supports. This induction covers the whole sequence through the measured window, including the failure of any whole funding check. A terminal sign verdict is unchanged by a permutation carrying its actual holder and all shared names. The audit checks **28** independently replayed holder and distinction reversals, covering every realized status and the actual closure strata. It verifies both paid multiplicities and failure shortages. [Relabel receipts and signed examples](../../artifacts/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B-E001_trees/representatives_audit.json)

## Four closing classes

The four cases all have a central holder with no extra opening and joins from that holder to every other founder. Their different outcomes arise from the leaf supplies.

- With **four** founders and **no** extra leaf opening, the age-two terminal has arity three. Its whole has **8 holders and 12 distinctions**. It refuses the supplied odd operator reading and carries integer mass **324**.
- With **four** founders and **one** extra leaf opening, the age-three terminal has arity three. Its whole has **12 holders and 20 distinctions**. It refuses the supplied odd reading and carries mass **324**.
- With **four** founders and **two** extra leaf openings, the age-four terminal has arity three. Its whole has **18 holders and 33 distinctions**. It admits the supplied odd reading and carries mass **108**.
- With **five** founders and **four** extra leaf openings, the age-three terminal has arity four. Its whole has **16 holders and 32 distinctions**. It admits the supplied odd reading and carries mass **15**.

There is no two-place terminal in the exact population. All ordinary closing grants are zero, and in each case the actual closing input set is the entire previous loose set. The stored older-row combination reduces to that very named set. Reversing the closing sign then gives zero complete scalar words in all four cases. The connected-group or planar-rotation certificate gives the operator verdict under the established theorem. A separate Pauli solver on the actual named incidences independently agrees. On both positive cases the stored operators square to the identity, commute within every holder and multiply to the intended sign at every holder. The two planar cases have no solution to the Pauli compatibility system. [Named words, spans and signed certificates](../../artifacts/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B-E001_trees/representatives_audit.json) · [Earlier operator criterion](../FOUR-READINGS-20261120-001A/results.md)

At size four, closure mass is **756/4,096** and admitting closure mass is **108/4,096**. At size five both masses are **15/128,000**. Sizes six through eight have zero closure mass. The equal-size mixture therefore gives **591/16,000** closure, **339/64,000** admitting closure and **113/788** admission conditional on closure. The conditional share is undefined at sizes six through eight. Not-all-equal is unsigned, and its sign comparison is inapplicable.

## Physical replay and reproduction

For each representative, the earlier native engine and the independent witnessed-end calculation agree on every candidate parent group, opening shortfall, funded multiplicity, following demand, fresh count and status. The parity birth check uses the entire older row span. Reconstruct a cut by starting with `founder_rows` and appending the actual `support` of each successive birth, in its stored order. A recorded stall gives the attempted age, all witnessed groups, its named available openings and each shortfall. The final artifact holds **1,248** parity and **1,252** not-all-equal funded cuts, with **12,640** and **12,645** births respectively. The largest ledger has at most **75 holders** and **155 distinctions**. The earlier 512-holder and 4,096-name caps would censor zero mass. The full calculation took **3.93 seconds** under one BLAS/OpenMP thread, with peak memory below **180 MiB**. The independent relabel and coverage audit took **0.86 seconds**. [Audit counts and input digest](../../artifacts/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B-E001_trees/representatives_audit.json)

```bash
scope=IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B
study="experiments/$scope/$scope-E001_trees"
ulimit -v 6291456
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
.venv/bin/python -B "$study/job.py"
.venv/bin/python -B "$study/representatives_audit.py"
```

| Scope | Status | Finding |
| --- | --- | --- |
| This attempt · Physical representatives and operator checks | Complete | All 3,739 classes and both law trajectories replay. Every one of the four closing classes has a named certificate. |
| Local direction · Conditional closure and sign | Exact finite result | Closure occurs on four- and five-holder founders. Two closing types admit a supplied odd sign. |
| Broader exploration · Tree funding and later growth | Scope fixed | Every funded cut through age four is present. The larger or later populations require separate evidence. |
| G5, G17 and G18 · Ordinary closure and supplied signs | Evidence added | Exact labelled masses distinguish observed closure, admitting closure and admission conditional on closure. |

**Next step:** Continue — selected: #1.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- |
| 1 | Reconcile the representative ledger with the independent labelled count | 2/3 — Substantial | 3/3 — Ready | Compare exact per-shape and per-decoration masses → integrate the verified endpoint and sample bridge | Selected · started |

**Corrections:** None to earlier findings.

**Goals:** G5, G17 and G18 gain the uncapped finite physical comparison. Independent scientific referee pending.

**Assumptions:** The ordinary update and the established operator criterion govern the two verdicts. Uniform size and Prüfer laws and independent quarter-weight extras define the probabilities.

**Scaffolds:** The founder law, positive-age window and supplied sign reversal delimit the experiment. Canonical naming supplies an explicit replay, with relabel invariance under the stated physical comparison.
