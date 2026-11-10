# A search outside the proved class

Status: Computed, exhaustive per host (SAT over every state of every class). `check.py` (1 second), ticket B of
`research/COMPOSITE-FN-20261110-001/preregistration.md`, frozen in commit `36d02b296` before any run.

## What is checked

The frozen family: double covers of K_2 and K_3 branched at four vertices (tori), with three branch sets each, and double covers of the
Fano torus (7,2,1) and the thin torus (4,3,2) branched at vertex 0 and the lowest-index vertex not adjacent to it (genus 2). For each: a
Kasteleyn law (face parities solved over F2), every class, its satisfiability, and in each unsatisfiable class whether every line is
critical.

**One host is undefined under the frozen rule.** The Fano torus is the seven-vertex triangulation of the torus, whose graph is K_7, so
every vertex is adjacent to vertex 0 and the rule names no second branch point. The first launch stopped with an error there; the check
now records the host as undefined, and no substitute was chosen. Six tori and one genus-2 space
were checked.

## Results

| Host | Genus | Points | Classes | Unsatisfiable classes |
| --- | --- | --- | --- | --- |
| cover(K_2; four corners) | 1 | 32 | 4 | 0 |
| cover(K_2; two corners, two regular) | 1 | 32 | 4 | 0 |
| cover(K_2; four regular) | 1 | 32 | 4 | 0 |
| cover(K_3; four corners) | 1 | 72 | 4 | 0 |
| cover(K_3; two corners, two regular) | 1 | 72 | 4 | 0 |
| cover(K_3; four regular) | 1 | 72 | 4 | 0 |
| cover(torus(4,3,2); 0 and 4) | 2 | 16 | 16 | 0 |

Every class of every host is satisfiable, so none of them is a host in the sense of the pre-registration: a composite built over one
never acts (the constant function 0). Prediction S1 holds vacuously, and the search says nothing about an OR. What it does show is that an
unsatisfiable class is rare off the sphere: none of these seven spaces has one. By the frozen stop rule the search ends here.
