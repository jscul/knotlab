# Maps of three held points

Status: Proved (exact census, with lemma G of `IN-OUT-20261110-001` by hand). `check.py` (about two minutes), ticket A of
`research/THREE-IN-20261110-001/preregistration.md`, its design frozen in stage 0 (commit `9387eb515`) before it ran.

## What was computed

On every class of the two dev spaces and S1 to S4 (1,152 classes), at every group (a leaf or a top-level composite), the floor states
were projected exactly onto the group's neighbourhood N(G) (every point of every line through a side). At every interface with three
inputs in N(G) (the three sides; or two sides and one more point) and an output in N(G), the map was read at the eight input patterns.

## Results (exact)

| Kind | Maps |
| --- | --- |
| Never decided (every reading u or x) | 2,025,954 |
| Partial, unate | 935,160 |
| No floor state | 14,068 |
| Total, a single input copied or negated | 1,074 |
| Total majority | 0 |
| Total parity | 0 |
| Partial, non-unate | 0 |

- Every one of the 2,976,256 maps is self-dual (theorem D, checked again).
- The total maps all depend on one input; the other two never reach the output. They sit in a few classes (frozen pairs).

## Why this covers every law

Every Kasteleyn law of a space is its class's representative changed by gauge flips and line complements. By lemma G a gauge flip at an
interface point negates that input or the output, a gauge flip elsewhere or a line complement changes nothing, and negations keep a map
dictator, majority, parity, unate or non-unate. A law with an even face has no floor state. So at these interfaces of these spaces **no
knot law computes parity, majority, or any map that moves an input both ways.**

## Scope

Interfaces inside one group's neighbourhood, on six spaces of up to 90 points. General NAE constraint systems with hidden points can
define parity (external, not checked here: the standard bases of Boolean co-clones give NAE as a base of the relations closed under
complement, and four-point parity is one), so this looks like a property of these knot spaces and interfaces rather than of NAE logic;
whether it holds for every knot space and every interface is open.

**Reproduction.** Re-running `check.py` reproduces every check except check 0: the pre-registration it binds gained the stage-0 result
and stage 1 after this ticket ran.
