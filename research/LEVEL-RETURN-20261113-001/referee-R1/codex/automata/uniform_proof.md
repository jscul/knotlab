# Independent R2/R4 proof

**Standard statement.** For the two exact keys specified below, address
parity is a state of pattern #2 at every odd level `n >= 3`; first letter
XOR last letter is a state of pattern #3 at every even level `n >= 2`.
At every even level `n >= 4`, parity violates exactly two distinct unordered
knots of pattern #2. They arise from placement `[0,8,10]` at the two inputs
`0^(n-2)10` and `0^(n-2)11`.

**Nearest known result.** Synchronous finite-state maps and finite-state
output tests admit a finite product recognizing their violating inputs.
That standard construction is used here for the two specified keys and an
exact comparison of languages. No external mathematics is admitted as new
proof lineage; novelty is unassessed by this referee lane.

These claims concern the declared finite address patterns and their NAE
states. They do not assert rigidity or unsatisfiability at all even levels.

## Exact definitions and inputs

An address is a binary word read from its first, most significant letter.
A map in state `q` reads `b`, writes `b XOR sw[q]`, and continues in
`d_b[q]`. A word `(q,r)` applies `r` first and then `q`. The word roster is

```
index:  0  1  2  3   4   5   6   7   8   9  10  11  12
word:   I  A  B  C  AA  AB  AC  BA  BB  BC  CA  CB  CC
```

Here `I=()` is exactly the identity, and `A`, `B`, `C` are states `0`, `1`,
`2`. A placement input is retained only when its three full image addresses
are distinct. A state satisfies it precisely when its three values are not
all equal. Deduplicating retained unordered triples does not change whether
a state satisfies the pattern.

| Pattern | swaps | zero successors | one successors | Placements |
| --- | --- | --- | --- | --- |
| #2, `91c75673…` | `[1,0,1]` | `[0,2,2]` | `[2,1,1]` | `[0,8,10]`, `[1,8,12]`, `[1,9,10]` |
| #3, `f4fd01e9…` | `[1,0,1]` | `[0,2,1]` | `[0,1,1]` | `[0,1,11]`, `[0,2,3]`, `[0,2,12]`, `[0,7,9]`, `[1,7,11]`, `[1,9,10]`, `[4,7,10]`, `[5,6,7]`, `[7,9,12]` |

The data were read from the earlier independent referee's two return JSON
files. Their exact paths and hashes are recorded in
[product_results.json](product_results.json). The address semantics come
from `research/ADDR-KNOTS-20261113-001/codex_spec.md`.

## A direct algebraic proof for #2

All sums in this section are XOR, and integers in these sums mean their
parities. Write `P(x)` for address parity, `x_i` for letter `i`, and
`E(x)=1` precisely when `x_1,...,x_(n-1)` are all zero. For `n >= 2`,

```
(Bx)_1 = x_1;
(Cx)_1 = x_1 + 1;
(Bx)_i = (Cx)_i = x_i + x_(i-1) + 1       (i >= 2).

P(Bx) = x_n + n + 1;
P(Cx) = x_n + n;
P(Ax) = x_n + n + 1 + E(x).
```

The first formulas follow immediately from the successors of `B` and `C`.
For `A`, initial zeros are changed to ones; the first one is changed to zero;
the next letter is complemented, after which the same adjacent-letter rule
as `B` applies. Summing telescopes to the displayed formula. The two
exceptional addresses with `E(x)=1` are checked directly.

For `n >= 3`, put `T(x)=x_n+x_(n-1)+n` and let
`S_n={0^(n-2)1b : b in {0,1}}`. Then

```
P(BBx) = P(BCx) = T(x);
P(CCx) = T(x) + 1;
P(CAx) = T(x) + 1                     when x is not in S_n;
P(CAx) = T(x)                         when x is in S_n.
```

For the last two equations, `(Ax)_n` normally equals
`x_n+x_(n-1)+1`. It differs exactly when the first one is at position
`n-1`, which is precisely `S_n`.

Consequently placement `[1,8,12]` (`A,BB,CC`) always has the opposite
values on its last two images. In the other two placements, `BB` or `BC`
and `CA` have opposite values away from `S_n`. For `x=0^(n-2)1b`,

```
P(x) = 1+b;
P(Ax) = P(BBx) = P(BCx) = P(CAx) = b+n+1;
Ax = BCx = 1^(n-2)0(1+b).
```

Thus `[1,9,10]` (`A,BC,CA`) has coinciding first and second images on
the only potentially troublesome inputs, so these inputs are excluded by
the definition. For `[0,8,10]` (`I,BB,CA`), all three parity values agree
on `S_n` exactly when `n` is even. This proves the odd-level state claim
and proves that the only possible even-level violations are the asserted
two generating inputs.

### There are two distinct unordered knots

For `n >= 4` and `x_b=0^(n-2)1b`, the actual images in `[0,8,10]` are

```
I x_b  = 0^(n-2)1b;
BB x_b = 00 1^(n-4)0(1+b);
CA x_b = 0 1^(n-3)0b.
```

The first and second images differ in their penultimate letter. The third
has second letter one; the first two have second letter zero. Hence all
three images are distinct, so the inputs are retained. Moreover, each
unordered knot has a unique image whose second letter is one: `CA x_b`.
These distinguished images have different final letters for `b=0` and
`b=1`. Therefore the two unordered knots are distinct. Every violation
has a generating input, and the preceding case split exhausts those inputs,
so this proves **exactly two unordered knots**, rather than merely two
generating occurrences.

At `n=4` they are `{0001,0010,0100}` and `{0000,0011,0101}`. At `n=22`
their integer forms are `{2,1048573,2097148}` and
`{3,1048572,2097149}`, agreeing with the fresh vectorized computation.

Deleting these two knots therefore leaves parity, and its complement, as
explicit states at **every even `n >= 4`**, including `n=16`. A solver
timeout for finding a reduced-pattern model does not leave this existence
claim open. This establishes no all-level uniqueness claim; rigidity is a
separate question.

## A finite product proves both all-level state statements

The construction in [product_proof.py](product_proof.py) is fresh and
imports no study or earlier referee implementation. For each placement it
tracks:

1. The three residual words after the input prefix. An empty residual is
   the identity and outputs its input letter unchanged. Nonempty words
   process the letter from right to left, saving each item's successor
   according to that item's own input letter.
2. Three output memories: accumulated XOR for parity, or the first and
   most recent letters for the first-XOR-last state.
3. Three bits, one per image pair, recording whether that pair has differed
   in any output letter. All images are distinct exactly when all bits
   are set.
4. The length parity and the length capped at the stated minimum.

Induction on input length proves that these have exactly their stated
meanings. In particular the difference bits compare full image addresses,
not map labels, final transducer states, or state values. An accepting
configuration has the right minimum length and parity, three distinct
images, and three equal state values. It therefore exists precisely when
the proposed state fails on a retained placement input.

There are finitely many configurations. Starting at the empty input, the
code visits each reachable configuration and both of its successors.
The resulting closed reachable set contains the configuration reached by
every finite input, again by induction. The complete state and transition
records are in [product_automata.json](product_automata.json).

| Claim | Reachable configurations, in placement order | Accepting configurations |
| --- | --- | --- |
| #2 parity, odd `n >= 3` | `39,19,27` | zero in every placement |
| #3 first XOR last, even `n >= 2` | `19,27,25,27,35,29,23,27,27` | zero in every placement |

Together with the invariant, these empty accepting sets prove the two
uniform statements; checking finitely many levels alone would not do so.

### Exact comparison of the even-level bad-input language

For #2, even `n >= 4`, the bad-input automata have `47,25,35` reachable
configurations in placement order, with respectively `2,0,0` accepting
configurations. The automaton for `[0,8,10]` is compared with the following
seven-state DFA; `F` alone accepts.

| State and meaning | next on 0 | next on 1 |
| --- | --- | --- |
| `Z0`: no letters | `Z1` | `D` |
| `Z1`: one initial zero | `ZE` | `D` |
| `ZE`: an even positive number of initial zeros | `ZO` | `T` |
| `ZO`: an odd number, at least three, of initial zeros | `ZE` | `D` |
| `T`: those even zeros followed by one | `F` | `F` |
| `F`: one further arbitrary letter | `D` | `D` |
| `D`: permanently rejected | `D` | `D` |

This DFA recognizes `(00)+1(0|1)`. The product of its state with the
bad-input automaton is explored from `(initial,Z0)`, looking for a
configuration where exactly one side accepts. For the other two placements
the target language is empty. The reachable comparison sizes are
`47,27,35`; every symmetric difference has **zero** accepting
configurations. Thus the exact regular language is proved, not inferred
from a sequence of counts. It agrees with the algebraic proof above.

## Direct finite computation and controls

[vector_levels.py](vector_levels.py) separately builds the three generator
permutations by first-letter recursion, then evaluates every indexed word
by array composition. Index zero is explicitly `arange(2**n)`. For each
placement and every input it checks pairwise image distinction before
checking the state. It computes **every `n=1,...,22`** for both keys.

Results in [vector_levels_22.json](vector_levels_22.json):

- #2: zero violations at every odd `n >= 3`; exactly the two stated
  generating inputs and two distinct unordered knots at every even
  `n >= 4`.
- #3: zero violations at every even `n >= 2`. The wrong parity already
  fails at `n=3`.
- A separately written scalar letter-by-letter implementation agrees on
  every word and every address through level 8: 6,630 word values per key.
- The full direct computation took 1.303 seconds; peak RSS was
  410,560 KiB. Only one computation process ran in this lane.

The following controls are all actually rejected by reachable witnesses:

| Deliberate error | Placement | Shortest witness |
| --- | --- | --- |
| #2 parity at even levels | `[0,8,10]` | `0010` |
| #3 first XOR last at odd levels | `[0,2,3]` | `000` |
| #2 first XOR last at its claimed odd levels | `[1,8,12]` | `100` |
| #3 parity at its claimed even levels | `[0,1,11]` | `0000` |
| Omit exclusion of equal image addresses | `[1,9,10]` | `010` |
| Replace the identity word by map `A` | `[0,8,10]` | `010` |

At the equal-image witness, the images are `101,101,000`; their parity
values agree, but this is correctly excluded. Replacing the identity
produces `101,011,000` at the other witness; these are distinct and
monochromatic. The actual identity's one-letter steps return both `0`
and `1` unchanged and retain the empty residual. Exact control records
are in [product_results.json](product_results.json).

[validation.json](validation.json) additionally records a scalar replay of
all six control witnesses, agreement of the displayed three-image formulas
at both inputs for every `n=4,...,22` (38 cases), parsing of the JSON
artifacts, and source/input hash checks. This supplementary check imports
only this lane's scalar implementation.

Replay from the repository root:

```
.venv/bin/python -B research/LEVEL-RETURN-20261113-001/referee-R1/codex/automata/product_proof.py
.venv/bin/python -B research/LEVEL-RETURN-20261113-001/referee-R1/codex/automata/vector_levels.py --max-level 22
.venv/bin/python -B research/LEVEL-RETURN-20261113-001/referee-R1/codex/automata/check_evidence.py
```

## Authority and limitation

The all-level conclusions combine a mathematical invariant with exhaustive
finite reachability. The separate array/scalar computation is bounded
cross-validation through 22/8. This is an independently authored same-task
AI referee computation (V2 relative to the study producer), not human or
external replication and not a trusted-kernel formalization.

The study's result JSON reports successful all-level checks and a count of
27 for each family. The two successful mathematical statements are
independently confirmed here. A reachable-state count depends on the
configuration encoding and aggregation; this lane's encoding has the
counts displayed above. **The study's implementation was forbidden to this
referee lane and was not inspected or imported.** Consequently this audit
cannot certify how that implementation handles its identity word or
coinciding images, nor can it certify the meaning of its reported 27.
It proves the independent statement with both rules explicitly enforced.

No remaining mathematical obligation was found for R2 or the exact
two-knot part of R4. All-even rigidity and all-even death remain separate
from these conclusions.
