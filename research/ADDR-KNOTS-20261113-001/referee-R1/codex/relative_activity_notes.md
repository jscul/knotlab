# R1: independent relative activity audit

80 retained descriptions representing distinct nonempty
(pattern hash, relative class) units were checked: 20 from each recorded class
when run with the default arguments. Relative class and degree mismatches:
**0**. Action mismatches:
**0**. Secondary letter class and degree mismatches:
**0**.

## Interface and independence

This is a code-analysis referee check of the exact relative-product activity
labels in the retained key records. This fresh standard-library script imports
no producer or recheck code. Inputs are `codex_spec.md`, its addendum,
`preregistration.md`, and the retained `keys.jsonl.gz`; the supplied proof note
and report were read for claim context. Forbidden producer and recheck paths
were not opened. No network was used. Writes for this lane are the three owned
relative activity files in this directory. The deterministic sample excludes
F0 and is stratified by recorded class; it tests labels and is not an estimate
of population accuracy.

| Recorded class | Keys | State counts s | Distinct placement counts | Degrees |
| --- | ---: | --- | --- | --- |
| finitary | 20 | [2, 3, 4, 5] | [1, 2, 3, 4, 5] | [None] |
| bounded | 20 | [2, 3, 4, 5] | [1, 2, 3, 4, 5, 6, 7, 8, 9] | [0] |
| polynomial | 20 | [3, 4, 5] | [1, 2, 3, 4, 5, 6, 7, 8, 9] | [1, 2, 3] |
| exponential | 20 | [2, 3, 4, 5] | [1, 2, 3, 4, 5, 6, 7, 8, 9] | [None] |

Selection prioritizes available s, placement counts, and polynomial degrees
before adding unrepresented joint cells, with SHA-256 tie breaks using the
salt in the JSON, while never selecting a pattern twice within a class. The
table gives actual coverage: finitary placement counts 6, 7, and 9 are not in
the sample. Finitary placement counts 4, 6, 7, and 9 collectively have only
three distinct nonempty patterns in the retained population, so covering all
of those counts conflicts with the distinct-pattern requirement. Selection
does not use this checker's computed outcomes. The final selection replaces
an initial 80-description feasibility pass that allowed empty and repeated
patterns; only the revised 80-unit sample is used for this retained result.

## Exact procedure and controls

For each sampled key, every ordered pair in every distinct placement is checked.
The fresh product is `target * inverse(source)`, acting right to left; inverse
sections follow the original input recovered from the output letter. Reachable
signed tuples are closed under both letters. A state is removed exactly when
it cannot reach an output swap. A separate finite-behaviour refinement agrees
on every removed state. Iterative Kosaraju components retain both arcs when
the two letter successors coincide. An internally branching cyclic component
gives exponential activity; otherwise the largest number of cyclic components
on a component path gives degree one less, with no cyclic component finitary.

Known controls pass for identity, a root-only swap, an adding machine with
bounded activity, degree-one and degree-two polynomial activity, and a map
with exponential activity. Their exact section counts match analytic formulas
at every level 0 through 160. Both orders of a map times its inverse reduce
behaviourally to identity. Deliberately retaining identity components or
collapsing parallel arcs produces the wrong classifications, as expected.
Deliberately using the wrong inverse section or reversing a noncommuting
relative composition causes action mismatches. Control details are in JSON.

There are 1528 distinct signed product tuples within
the sampled keys, representing 1644 ordered
placement pairs. Each is compared on every address at levels 0 through 8
against raw positive-state actions composed with an explicitly inverted
finite permutation. Counted nonidentity sections are also compared with
explicit address enumeration through level 8. This amounts to
780808 action/address comparisons.

## Validation gap and finite-level limitation

The specification's **V-rel** gate validates finite actions of relative maps;
it does not compare their activity classifications. **V-act-class** applies
the finite-level count discriminator to the original state maps with all maps
included, not to inverse products. Thus the named gates do not directly
validate the primary relative-class labels. This audit independently checks
that primary classification on its stated sample.

The empirical discriminator at level 160 disagrees with the exact component
class on 0 sampled products.
Finite agreement of action or activity counts cannot by itself establish an
asymptotic class: product automata can have more states, longer transients, and
slower growth than the original letter automata. Here the primary result is
the full finite product-automaton component calculation; level-160 counts are
an additional diagnostic, not the source of the class or degree. Polynomial
degree is checked by the component calculation, not by the empirical rule.

## Scope, replay, and resources

This checks only the sampled keys' activity and finite actions. It supplies no
all-level survival conclusion and no native-emergence conclusion. No SAT or
summary-bootstrap computation was repeated. A label-based stratified sample
cannot detect every possible error elsewhere in the retained population.

Replay from the repository root:

```sh
/home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/ADDR-KNOTS-20261113-001/referee-R1/codex/relative_activity.py
```

The process used a 2 GiB address-space cap and no child processes. Measured
wall time: 1.934 seconds; peak resident
memory: 80.750 MiB. Input and script hashes
are retained in JSON. The stop boundary is 80 sampled
keys, with no extrapolation to unchecked records.
