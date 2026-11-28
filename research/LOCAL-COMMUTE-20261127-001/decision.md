# Commutation fixed at birth: can growth's own closures still close odd?

Epic `LOCAL-COMMUTE-20261127-001`, at the owner's go-ahead on direction 1 of the toy-theory placement. Design, arguments,
frozen predictions, review and results: [README.md](README.md); code [local_commute.py](local_commute.py) and the post hoc
[posthoc_losses.py](posthoc_losses.py); outputs [summary.json](summary.json), [gates.json](gates.json),
[results.jsonl](results.jsonl), [past.jsonl](past.jsonl), [posthoc_losses.json](posthoc_losses.json). Proved arguments
and exact GF(2) counts over the census of 7,075 starts, one vote per start; independent referee pending (brief in
`referee-R1/`).

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — commutation declared and fixed at birth on growth's closures | **Status:** Successful | Birth rules keep a state on every grown structure; odd attainable at 1,177 of the 1,187 closures that are not outerplanar |
| Local direction — the birth rule | Retire (answered) | It loses the odd close only at 10 round-2 closures whose odd needs a pair taken apart one round later |
| Broader exploration — the quantum part under a declared phase | Known alternatives | A principle that selects the sign; readers on grown closures; two-reader excess needs states outside this extension |
| Long-term goal — G18 Comparing growth laws | Capability gained | One declared primitive gives growth's closures the three-reader-type contradiction, but which closures close odd is a free choice |

The extension works as a representation: with commutation declared once at birth, and the closing sign forced by the cost
of reordering, every structure growth makes keeps a stabilizer state, and nearly every closure that can close odd under
any choice can close odd under a choice made at birth. What it does not do is select the sign. At every closure where odd
is attainable, the choices that close odd are exactly half, and the round-by-round random rule closed odd in 163 of 340
runs there. Growth fixes which closures can close odd. A choice the model does not make fixes which do.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A principle that selects the sign: the birth choices with the most failing pairs, as far from classical as a state allows | 3/3 — Barrier | 2/3 — Testable | Exact maximum on each of the 1,177 closures → the sign forced odd there, forced even, or still free | Selected · awaiting go-ahead |
| 2 | Readers on grown closures: do the odd birth choices split into readers, each holding two values that fail to commute, with every two readers commuting? | 2/3 — Substantial | 2/3 — Testable | Search the odd choices of each closure for a reader split → a three-reader game on growth's own closures, or none | Alternative · deferred |
| 3 | A birth rule that knows which live knots can be co-parents (the engine's candidate pairs) | 1/3 — Incremental | 3/3 — Ready | Rerun the 10 lost closures → recovered or not | Alternative · deferred |
| 4 | Intuition link: the birth rule as a causal model, the whole choices as all-at-once ones (Wharton and Argaman) | 1/3 — Incremental | 2/3 — Testable | State the ten losses as all-at-once information → match or mismatch | Alternative · deferred |

1. Payoff 3/3. If a natural principle forces the odd sign at growth's closures, the quantum sign would follow from growth,
   one declared primitive and one principle, which is as close to a native source as this line has come. If it does not,
   the sign is settled as a free bit. Concreteness 2/3. The maximum is an exact optimization over GF(2) choices, small on
   these closures. On the ring the maximum is the readers' matching, which closes odd. The main uncertainty is that no
   linear principle can force odd, since the classical choice always satisfies one. Only a principle that excludes it, such
   as this maximum, can. It adds a principle to the model, so it waits for the owner's word.
2. Payoff 2/3. It would turn the contradiction into the program's reader picture (separated readers with two settings) on
   structures growth makes. Concreteness 2/3: a finite search per closure. A choice whose failing pairs do not split into
   readers is still a contradiction, but not a game between separated readers.
3. Payoff 1/3: a refinement covering 10 closures. Concreteness 3/3: the engine's rule is known, and the lost closures are
   listed.
4. The intuition link for this checkpoint. The birth rule decides from the past only, while the whole choices read the
   finished structure, like the literature's all-at-once accounts. The ten losses are exactly where the odd sign needs the
   next round's grouping. Payoff 1/3 (an interpretation); concreteness 2/3.

**STOP** on the birth rule. Settled: the state is kept on every grown structure (proved, and no dead end in 2,485
round-by-round runs). Odd is attainable at every round-1 closure that is not outerplanar and at 86 of the 96 later ones.
The sign is a free half-and-half choice. Open: a principle that selects the sign (row 1). Two-reader scores also stay at
most 2 inside this extension. Its states are stabilizer states read by products of Pauli-like observables. Two
anticommuting reads on one side cannot both be correlated with a common read on the other, and commuting reads give 2 by
Landau's identity. This is argued here; the toy-theory study checked the two-qubit case (P6a).

**Corrections:** none. One frozen prediction failed (P3′: birth choices lose the odd close at 10 of 70 closures).

**Goals:** checkpoint row added under G18 (capability gained); no goal changed.

**Assumptions:** A314 entered (scaffold: which values commute, declared and fixed at birth). A295 gets a history line: the
declared extension drops A295 and keeps a state everywhere.

**Scaffolds:** A314, tested three ways: the natural birth rule (fails on 97% of starts), uniform round-by-round choices (no
dead ends), and the whole choices (P2). The census starts are hand-built (the census's scaffold); the cap of four rounds
and 40 knots cut 25 starts, which were not run. Round 5 on 200 starts made no closure.

**Basket:** `BOTH-LONG-20261126-001#1` (3/3, 3/3), `VALUE-CHANGE-20261126-001#1` (3/3, 3/3) and B239 (3/3, 2/3). None
was taken: the first belongs to the layer line, the second was answered by the third-reader study, and the third is an
older selected study. This study took the selected direction `TOY-PHASE-20261127-001#1`.

**Advisor:** Fable 5.2 returned a usage limit (logged). An independent reviewer checked the design by hand, read-only,
before the freeze. It settled the three-label closure and gave the lemma A6; seven changes followed, listed in the README.

## What was found

- **A state is kept everywhere.** The birth rule decides each pair at the end of the round in which its later distinction
  is born, never revises it, and lets a pair fail to commute only if one member is already held twice. Under it no knot
  ever holds two failing values (A1). The classical choice keeps a state, so every grown structure has one (A2). Choosing
  round by round never reached a round without a consistent choice, in 2,485 runs on 497 starts.
- **Closures are whole.** Every one of the 1,819 closures is a single implied birth that closes the whole structure (A3).
  Its sign is forced: the classical law times the cost of reordering its checks.
- **Where odd is attainable.** Whole choices attain odd exactly at the 1,187 closures that are not outerplanar (the
  record's R3, confirmed on growth's closures). Birth choices attain odd at all 1,091 such closures in round 1, where the
  two coincide (A5), and at all 26 later closures where three of the closing knot's parents lie in one block (the
  reviewer's lemma). Of the other 70 later closures they attain odd at 60.
- **What fixing at birth costs.** The ten losses are all round-2 closures on a closing knot of two places. Each needs a
  failing pair of two start distinctions that were loose at the start and that round 1 took apart. Looking one round ahead
  would allow that pair.
- **The natural birth rule fails.** Rule R restricted to what is decided at birth loses its state on 4,941 of the 5,086
  starts that grow (97%). It keeps a state at only 145 closures, all in round 1, and closes 53 of those odd.
- **The sign is a free bit.** At closures where odd is attainable, exactly half of the birth choices close odd. The
  round-by-round random rule closed odd in 163 of 340 runs there, and in 0 of 225 runs where odd was not attainable.

## Intuitions (exact links, not evidence)

- **Causal against all-at-once.** The birth rule uses only the past, the whole choices the finished structure. The odd
  close needs the finished structure only where a pair's fate is decided by the next round's grouping. This is the
  literature's contrast between causal hidden-variable accounts and all-at-once ones (Wharton and Argaman, Rev. Mod. Phys.
  92, 021002, 2020), which the record has cited before for weighting a whole history.
- **Half the choices.** A linear condition on GF(2) choices that is not identically zero holds on exactly half of them. So
  any principle that is itself a linear set of choices containing the classical one leaves the sign free. A principle that
  selects the sign must be nonlinear, like a maximum (row 1).
