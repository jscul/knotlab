# The logical knot: bound loops

Working formalization agreed on 2026-10-19 and adopted the same day as the
canonical knot test (`docs/FOUNDATIONAL_THESIS.md`, "Canonical knot test").
The owner settled erasure as forgetting the same day. The proofs are
`KNOT-FOUNDATION-20261019-001E-P001` for that reading and
`KNOT-FOUNDATION-20261019-001A-P001` for the earlier absence reading. This
note keeps the intuition and its definitions in view while work continues. Theorem status still comes from
proof artifacts. The mathematics underneath is classical; what the project
adds is the reading. The sections from "What the atom is" onward explain the
definition further and add checks; they do not change it.

## The picture

- **A line is not enough.** An implication chain only orders its members, and
  open strings can always be rearranged into one another.
- **A single loop is not enough.** A loop of implications forces all of its
  members to be equal, so it collapses to one point. A loop of equal and
  unequal steps collapses to one free bit or contradicts itself.
- **What is real is what lies between bound loops.** The binding belongs to
  the pair, not to either loop. No part smaller than the whole shows it, and
  erasing either loop removes it.
- **A loop is a logical structure that can be entwined.** It is not spatial.
  What it brings to a binding is an open distinction, a bit it leaves free.
- **A knot is not just any hole.** In the shape of what a system leaves free,
  a knot is an empty triangle: every pair free, the whole not. Pairwise ties
  can make other holes, but never this one (see "Holes and knots").
- **Knots live across alternatives.** A knot leaves every loop's distinction
  open and fixes at most one bit. In a single settled world there is nothing
  to see.
- **2-clauses are logic, not topology.** Everything a 2-clause says is
  pairwise, so 2-clauses that must all hold can never make up a loop or a
  binding. 2-clauses that compete, where the allowed states are those that
  break the fewest, can leave a knot (see "Knots from competing pairs").
- **Witnesses carry information about a loop's interior.** A witness is
  information outside a loop that reports on its interior, for example whether
  two of its points show 00/11 or 01/10. The witness of one binding can take
  part in the next binding, which is how bindings compose.

## The working formalization

### Setting

- A system of constraints defines which joint states are allowed. Witness
  variables are allowed and are quantified away.
- No executor, scheduler or checker may supply an input. A rule such as
  "check this loop's condition only while the loop runs" adds the loop's own
  presence as an input, so it must be written as an explicit constraint
  instead.
- A verdict depends only on the allowed states, never on how the constraints
  are written.

Each loop contributes an open distinction: a variable, or a named pattern such
as its parity, that the loop leaves free. The contact is one more variable
`c`. Erasing a loop forgets it, so its distinction is no longer constrained by
anything.

### Definition

A knot of loops L1, …, Ln (n ≥ 2) with contact `c` is a relation over exactly
their distinctions and `c` such that:

- **K1 binding:** the relation is constrained as a whole;
- **K2 loss on erasure:** forgetting any one variable, a loop or the contact,
  leaves the others unconstrained;
- **K3 coexistence:** some joint state is allowed. K2 implies it.

In short: constrained as a whole, unconstrained in every part. Forgetting the
contact must free the loops too, so loops tied directly to each other do not
count.

**The absence reading.** Earlier on 2026-10-19 the test read each loop's
variable as its presence and erasure as setting it to absent:
- K1: with every loop present, the contact is constrained;
- K2: with any loop absent, nothing is constrained;
- K3: all loops can be present together.

That reading keeps only the atom, and every knot it accepts is a knot under
forgetting. It stays available as `check_knot(..., erasure="absence")` and in
`KNOT-FOUNDATION-20261019-001A-P001`.

### Facts

[tests/test_knotlab.py](../tests/test_knotlab.py) checks each fact on finite
cases; the cited results supply the uniform arguments.

1. **Two loops and a contact have 34 knots, in five shapes.** They range from
   a single three-literal clause, the atom `¬A ∨ ¬B ∨ c` (one excluded state,
   0.19 bits), to parity (four excluded states, 1 bit). This is checked
   against all 256 relations on three variables.
2. **A knot is invisible in its parts, and parity hides the most.** This is
   the definition: every shadow on fewer variables is unconstrained, as with
   Borromean rings. A knot on m variables therefore has at least 2^(m−1)
   states and hides at most one bit, and only parity hides a full bit.
3. **2-CNF is pairwise.** Whatever a 2-CNF allows, with any number of
   witnesses, equals what its two-variable shadows allow together (Schaefer
   1978; Baker and Pixley 1975).
4. **So no 2-CNF defines a knot.** A 2-CNF knot would equal the conjunction of
   its pairwise shadows, which Fact 2 makes unconstrained, contradicting K1.
   More witnesses do not help.
5. **Width 3 binds any number of loops.** Two loops need the single clause
   above. For n loops, a chain of three-literal clauses joined by witnesses
   defines the knot: `w1 ∨ ¬L1 ∨ ¬L2`, then `w2 ∨ ¬w1 ∨ ¬L3`, and so on,
   ending with `¬w(n−2) ∨ ¬Ln ∨ c`. Witness `w1` is forced exactly when L1 and
   L2 are both present: it is the witness that the pair is bound. Naming
   each partial match does the same for parity. Without witnesses, a knot on m
   variables implies no clause narrower than m, so it needs full-width
   clauses.
6. **So 3 is the exact threshold.** Width 2 is closed: pairwise in, pairwise
   out. Width 3 reaches every knot.

### What is not a knot

- **Common hub** `(¬A ∨ c) ∧ (¬B ∨ c)`: with B forgotten, A and `c` stay
  tied, which fails K2.
- **Loops tied directly**, such as `A ≠ B` with `c` free: forgetting the
  contact leaves A and B tied.
- **Parity of a value fixed elsewhere**, such as `c = A ⊕ B` with A fixed
  true: A is not open, so it is constrained on its own.
- **The relation the earlier Lean kernel accepted** `(A ↔ B) ∧ (A → c)`: A
  and B are tied.
- **Cross-wired 2-clause guards**, `¬B ∨ c` for A and `¬A ∨ c` for B: they act
  like a knot only when each loop's guard is checked only while that loop runs,
  which supplies the loop's own presence as a third input. Read relationally,
  they are a common hub.

Until the owner settled the forgetting reading on 2026-10-19, this list also
held parity `A ⊕ B ⊕ c = 0` and clauses such as `A ∨ B ∨ c`. Both are knots
now. Parity is the knot that hides the most. Every three-literal clause on
three open distinctions is the atom up to polarity.

## Where it started: patterns, controllers and entwinement

The program began with an observation about two small CNFs.
- `(x∨y∨z)(x∨¬y∨¬z)(¬x∨y∨¬z)(¬x∨¬y∨z)` allows exactly the odd assignments
  001, 010, 100 and 111. The mirror CNF allows the even ones.
- In the odd pattern, x decides whether y and z match. With x = 0 they differ
  (01/10); with x = 1 they match (00/11).
- The odd and even patterns together have no solution.

The original post asked three things:
- whether such patterns can be named by new variables and combined into
  patterns of patterns;
- why 2-SAT cannot do this;
- how much emergent information a CNF can hold.

In precise terms, with every statement checked by `knotlab patterns`:

- **A pattern** is a relation: the joint states it allows. Its *emergent
  information* is what the whole rules out that its two-variable shadows do
  not.
- **A controller** is a variable that changes how two others relate, beyond
  restricting each of them separately. *Controllers need three places.* A
  pattern on three variables has a controller exactly when 2-CNF cannot
  define it, even with witnesses, and then every one of its variables is a
  controller. In 2-CNF a variable can only act on other variables one at a
  time, because 2-CNF relations are determined by their pairs (Baker and
  Pixley 1975). This is the post's "2-SAT can only act against one variable".
- **Hiding from the parts.** On three variables, 34 patterns are
  constrained as a whole but unconstrained in every pair. Up to renaming and
  negation they come in five shapes:
  - one excluded state: a single clause, which is the atom (0.19 bits);
  - two excluded states at distance two or three (0.42 bits);
  - three excluded states (0.68 bits);
  - four excluded states: the odd and even patterns (1 bit).

  No pattern on three variables hides more than one bit from its pairs, and
  only parity hides that much. More generally, a pattern on n variables that
  is unconstrained in every part of n − 1 variables carries at most one bit,
  and only parity does (each part fixes the last variable, so at least
  2^(n−1) states remain; checked exhaustively for n = 4). Hiding only from
  pairs allows much more: a pattern on 10 variables with 6 states hides 7.4
  of its 10 bits from every pair (strength-2 covering arrays; Kleitman and
  Spencer 1973).
- **Patterns of patterns.** Naming a pattern with a new variable is itself a
  three-place pattern: "a says whether y and z match" is parity on a, y and
  z. The post's construction, c = whether the even pattern on x, y, z matches
  the odd pattern on u, v, w, is a parity on all seven variables. That parity
  is unconstrained in every part of six. Naming each partial match keeps
  every clause at three literals. Parity on n variables needs 2^(n−1) clauses
  of width n using only its own variables, but only 4n − 3 clauses of width
  three with n − 1 named matches (the Tseitin encoding, 1968). Naming is how
  width three reaches every pattern.
- **The post's three questions.**
  - *Smallest emergent pattern:* 3 variables and 1 clause of three literals.
    2-CNF has none.
  - *Most hidden information:* the most a pattern can hide from every part of
    n − 1 variables is one bit, and only parity does it.
  - *Growth:* for most patterns on n variables the clause count grows
    exponentially, about 2^n/n even with named intermediates (a counting
    argument, Shannon 1949). For parity it is linear once the matches are
    named.

### Entwinement and two readings of erasure

A loop is not spatial. It is a logical structure that can get entwined with
another logical structure. Formally:

- **Entwinement.** Two structures are entwined through a contact when a
  pattern joins one open distinction of each with the contact, the three
  together are constrained, and no pair of them is.
- **What can be entwined.** A structure can be entwined exactly when it
  carries an open distinction: a bit it leaves free. The bit may be a single
  variable or a named pattern, such as its parity. If the structure fixes
  that bit, the joint pattern constrains a pair and the entwinement fails.
  So "loop" means a structure with an open distinction.
- **Two readings of erasure:**
  - **Forgetting.** Erasing a loop removes it, so its distinction becomes
    unconstrained. A pattern then entwines exactly when it is constrained as
    a whole and unconstrained in every part. That is all 34 patterns above,
    from the atom to the odd and even patterns. The contact plays no special
    role: the three distinctions are bound the way Borromean rings are.
  - **Absence, the earlier reading.** A loop's variable is its presence,
    and erasing the loop sets that variable to absent. Only the atom then
    entwines, because absence must free everything. Parity treats absence
    as information: with A absent, B and c must be equal.

  Both readings exclude the common hub and every 2-CNF pattern, keep width
  three as the threshold, and keep compactness.

The owner chose forgetting as the canonical reading on 2026-10-19 (question 8
below).

## What the atom is

The atom is the single clause `¬A ∨ ¬B ∨ c`, read as a requirement: when A
and B both hold, `c` must hold, and nothing is required otherwise. Of the 34
two-loop knots it is the one that excludes the fewest states, so it is the
smallest bond. Five descriptions pick it out, and `knotlab worlds` checks each
of them:

1. **Relation.** It is the knot that excludes exactly one state. Under the
   earlier absence reading it was the only knot.
2. **Existence.** In the forced world described below, `c` exists exactly when
   A and B both do, and erasing either removes it. A common hub, `A → c` and
   `B → c`, keeps `c` whenever either loop is present.
3. **Shadow.** Every pair among A, B and `c` is unconstrained, so the bond
   shows only in the whole (Fact 2).
4. **Gate.** It is what an AND gate adds to its two-place parts. A two-input
   gate's relation is pairwise exactly when the gate ignores an input, so each
   of the ten gates that use both inputs needs a three-place clause, which is
   an atom up to which value of each variable counts as present. Computers
   are built from such gates.
5. **Projection.** Whatever mechanism binds two loops, keeping only their
   distinctions and the contact shows one of the 34 knots. A mechanism whose
   binding is a requirement shows the atom.

## Distinctions and bonds

A distinction is the smallest thing: two alternatives of which exactly one is
present, which is one bit. Spencer-Brown's *Laws of Form* (1969) begins from
"draw a distinction", and Bateson defined information as a difference that
makes a difference. The atom is the smallest bond: the smallest relation in
which things constrain one another jointly rather than in pairs. Peirce held
that three-place relations cannot be built from two-place ones, while every
relation can be built from three-place ones. Facts 3 and 5 are the Boolean
form of that claim.

Written on presences, a distinction is pairwise: at least one of `x` and `x′`
is present, and not both. Each piece alone is limited, and the two together
build everything:

- **Distinctions alone** stay pairwise (Fact 3). They store bits but bind
  nothing.
- **Atoms alone**, with some presences pinned, define exactly the relations
  closed under AND, which are the relations that requirements (Horn clauses)
  define. The atom is closed under AND; the choice `c → A ∨ B` and parity are
  not.
- **Atoms with distinctions** define every relation. Each of the 256
  relations on three places is rebuilt from atoms over its variables and their
  opposites, with each opposite tied to its variable by a distinction. Adding
  any relation that is not closed under AND to pinned atoms has the same
  effect, because nothing lies between the Horn relations and all relations in
  Post's lattice (Post 1941).

So binary code can build language models and games because the hardware
supplies the bonds: every gate that uses both of its inputs contains an atom.
A distinction is the material, and an atom is what holds material together.

## Requirement and choice

This section reads true as "exists". Whether a knot is a requirement or a
choice depends on that reading. Under the forgetting reading neither value is
privileged, and the base has choices exactly as much as requirements (see
"Does the base have real alternatives?" below).

A requirement says what must exist when other things do: atoms, one-premise
rules `X → Y`, and facts. Given what is present, a system of requirements has
exactly one least world, containing everything required and nothing more,
because the worlds that satisfy requirements are closed under intersection
(van Emden and Kowalski 1976). Propagation computes it in linear time
(Dowling and Gallier 1984). This is the **forced world**; `forced_world`
computes it, and the tests compare it with the intersection of all worlds.

A choice says that when something exists, one of several things must exist:
`c → A ∨ B`. With `c` present it has two minimal worlds, {A} and {B}, and
nothing in the constraints singles out either one.

- **Computation is a forced world.** Carry each bit as which of two things
  exists, "x=0" or "x=1" (dual rail). A gate `z = g(x, y)` becomes four atoms,
  one per pair of inputs, so every circuit runs as a forced world. The tests
  check random circuits, and 4-bit addition comes out right for all 256 pairs
  of inputs. Requirements therefore capture all deterministic computation:
  Horn satisfiability and monotone circuit value are complete for polynomial
  time (Jones and Laaser 1976; Goldschlager 1977).
- **Search is choice.** A distinction left open is a choice: one of "x=0" and
  "x=1" must exist. Run backward, the 3-bit adder asks which of the 64 ways of
  making its six input distinctions reach the sum 5. Six ways do, and the
  rules single out none of them. Checking one way takes one forced world, but
  with atoms and open distinctions together, deciding whether any way works
  is NP-complete, since it is circuit satisfiability (Cook 1971; Schaefer
  1978). Whether some
  method always avoids trying the ways is the P versus NP question, which this
  work does not address.
- **Atoms do compute arithmetic.** Atoms cannot define parity among three
  plain bits, since every atom system stays closed under AND and parity is
  not. On two rails, though, they compute parity, addition and every circuit.
  What atoms lack is choice, not arithmetic.

**Interpretation, not theorem.** Requirements never select, since their world
is unique, while a choice leaves alternatives that the constraints do not
rank. The modal-plurality doctrine treats coherent admissible alternatives as
co-real with no global selector, so choice is where that doctrine first has
work to do. The mathematics shows only that the constraints do not select. It
neither proves nor refutes co-reality.

### Does the base have real alternatives?

Ticket C answered this on 2026-10-19
([decision note](../research/KNOT-FOUNDATION-20261019-001/choice.md);
`knotlab choice`):

- **Yes, wherever it has knots.** Every variable of a knot takes both
  values. A knot on m variables allows at least half of its joint states, so
  it fixes at most one bit and leaves at least m − 1 open. A law with a single
  allowed state has no loop and no knot.
- **Knots never select.** Selecting one loop's value removes it from the
  binding and leaves a two-place relation between the rest: logic, not
  topology.
- **Requirement and choice are one knot read two ways.** "A and B require c"
  read with false as "exists" becomes "c requires A or B".
  - 16 of the 34 two-loop knots are a pure requirement under one reading and
    a pure choice under the other.
  - The other 18, parity among them, offer choices under both readings.
- **Forced outcomes need an added rule.** "Nothing exists unless required"
  selects one world for only 8 knots, and only under the reading it assumes.
- **Search is native.** Every three-literal clause is a knot, so systems of
  knots state any 3-SAT instance. Deciding whether they allow a world is
  NP-complete.

The smallest form of choice is an open distinction, which is what a loop
carries. A knot relates choices without making them. Whether every allowed
state is equally real is the modal-plurality interpretation, which these
results fit but do not prove.

## Infinite threads

Forced worlds make sense for unbounded systems of atoms: the forced world
contains everything that finitely many steps of propagation reach.

- **Everything rests on finitely many loops.** In the thread `L1 ∧ L2 → w1`,
  `wk ∧ L(k+2) → w(k+1)`, the thing `wk` exists exactly when L1, …, L(k+1)
  are all present. Erasing any one of them removes it, and later loops do not
  matter.
- **No contact binds infinitely many loops.** No set of clauses, each naming
  finitely many variables, defines a knot of infinitely many loops, even with
  infinitely many witnesses. *Proof.* By K1 some state is excluded, so by the
  compactness theorem some finite set of the clauses already excludes it.
  Those clauses name finitely many variables, so forget one they do not name.
  The same clauses still exclude every way of filling it back in, but K2 says
  that forgetting a variable leaves the rest unconstrained.
- **An infinite thread is a tower of finite knots.** Each `wk` binds the
  first k+1 loops, and no contact binds them all. A contact for the whole
  thread would need a limit rule with infinitely many premises, which no
  clause can express. Whether the program needs such a rule is open.
- **Earlier repository work agrees.** `INFINITE-CNF-001A1-P001` proved that
  every finite-support knot core of a countable CNF presentation already
  appears at a finite stage.

So arbitrarily complex structure can be built from atoms, but every bond in it
is finite.

## Projection, simulation and reality

- **Projection, precisely.** The relation a system shows on its loops and
  contact is its projection: every other variable is quantified away.
  `Relation.from_cnf` with witnesses, and `Relation.project`, compute it.
- **Projection reveals bonds but never creates them.** Building with
  conjunction and projecting preserves closure properties. Pairwise material
  projects to pairwise relations (Fact 3), requirements project to
  requirements, and parity projects to parity. A knot shows up in a projection
  only if the material already contains three-place bonds. This is the Galois
  connection between relations and their closure operations (Geiger 1968;
  Bodnarčuk, Kalužnin, Kotov and Romov 1969).
- **What every binding looks like from outside.** Two-loop knots come in only
  34 relations of five shapes. Every mechanism that binds two loops, whether a
  witness chain, a logic gate or a circuit built inside a game, therefore
  projects to one of them. A requirement projects to the atom `A ∧ B → c`. In
  this sense the knots are the logical shadow of any binding, whatever
  realizes it.
- **Vocabulary.** The canonical documents use "projection" for maps
  downstream of knot formation, and they list projection among the things
  that are not logical knots. That agrees with the previous points: the knot
  belongs to the material, and projection is how it is seen. Saying "the atom
  is what projection reveals" keeps both.
- **Simulation.** A computer built inside Minecraft computes what a silicon
  computer computes, and nothing inside the computation tells the two apart,
  because both project to the same logic. Simulation can therefore establish
  what every substrate must share when seen through logic, such as the census
  of knots, the width threshold and compactness. It cannot show
  which substrate lies underneath. That logic is the base of our universe is
  a working interpretation, not a result.

## Does contact structure become space-like?

Ticket D answered this on 2026-10-19
([decision note](../research/KNOT-FOUNDATION-20261019-001/space.md);
`knotlab space`). The free sets of a system, the sets whose every assignment
it allows, form a simplicial complex: the system's shape. Its bonds are the
knots inside it.

- **A knot is a hole.** A knot on m variables makes its shape a hollow
  simplex, an (m − 2)-sphere. The two-loop knot is a circle: three free pairs
  around a missing whole.
- **Bonds compose into a bond or into nothing.** For single clauses this is
  resolution.
- **Paths and separation.** Along a chain of atoms, the smallest bond joining
  the ends grows by one per step.
- **Logic allows every shape.** Every simplicial complex is the shape of some
  system, so logic selects no space, and whatever space there is comes from
  the law.
- **Not every hole is a knot.** Two pairwise ties can surround a circle.
  Topology in the knot sense begins at bonds.

So contact structure gives intrinsic holes, paths and separation, but not
space. A law that produces space without having it written in is the open
problem studied by causal sets, quantum graphity and hypergraph rewriting.

### Holes and knots

The two words are easy to confuse. A system's **shape** is built from what it
leaves free:
- each free distinction is a point;
- each pair of distinctions that can take all four combinations is an edge;
- each free triple is a filled triangle;
- and so on.

A **hole** is any gap in that shape: a loop (or a sphere) of free sets with
nothing free filling it. A **knot** is the smallest kind of hole: a set whose
every part is free but which is not free itself. In two loops and a contact,
it is an empty triangle. All three edges are there, and only the whole is
missing.

```text
a knot: an empty triangle            a hole made by ties: a square

        A                               a ──── b
       / \                              │      │
      B ─ c                             d ──── c

all three pairs are free;            the pairs a–c and b–d are tied,
A, B and c together are not          so those edges are missing; the gap is
                                     made of missing edges, not of a missing
                                     triangle
```

| | Hole | Knot |
| --- | --- | --- |
| What it is | Any gap in the shape, of any size | The smallest gap: every part free, the whole not |
| What it looks like | Any loop or sphere left unfilled | An empty triangle, or an empty simplex for more loops |
| What can make it | Pairwise ties can make one (the square) | Only a constraint on three or more at once; no 2-clause system has one |
| What it means | Some joint pattern among the distinctions | Information held by the whole and by no part |

Every knot is a hole, but not every hole is a knot. A hole that ties can make
can be explained by pairs; a knot cannot. When this document says "topology
begins at the knot", it means knots, not holes in general. Larger holes can
also arise just from putting separate knots side by side, so to tell whether
things are bound, look at the knots (bonds), not at the size of the holes.

### Knots and synergy

Information theory calls "the whole holds what no part holds" *synergy*. One
measure is co-information: what two variables share, minus what they share
once the third is known. It is negative when knowing the third makes the two
share more, which is the mark of synergy. Under the uniform distribution on a
knot's allowed states, a probe on 2026-10-19 found the following (checked in
`PatternTest`):

- **Every knot is synergistic.** All 34 two-loop knots have negative
  co-information.
- **Counting possibilities gives an exact match.** When co-information counts
  possibilities instead of using probabilities (Hartley's measure), it equals
  minus the bits the knot hides.
- **Only parity is pure synergy statistically.** In parity every pair is
  statistically independent. In the other 32 knots the pairs still share some
  information.
- **Synergy does not require a knot.** Eight purely pairwise (2-CNF) patterns
  are synergistic, "at most one of three" for example. So is the AND gate,
  which is neither pairwise nor a knot.

The physics literature makes the same point: pairwise mechanisms can produce
synergistic behaviour (Rosas et al., *Nature Physics* 2022; Caprioglio,
Mediano and Berthouze, *Physical Review Letters* 2026). A knot certifies
something narrower than "a higher-order mechanism". No conjunction of
pairwise constraints, even with hidden variables, allows exactly a knot, so a
knot in what a system allows shows that its rules are not all pairwise rules
that must all hold. Pairwise preferences that compete can still leave a knot
(next section). Whether this possibilistic notion of synergy is new has not
been checked beyond a short search. The nearest work to compare is Jansma's
model-free higher-order interactions (arXiv:2205.04440).

**Emergence in bits** (`EMERGENCE-BITS-20261021-001`). The bits a pattern
hides from its pairs are log₂ of the patterns its pairs allow, minus log₂ of
the patterns it allows.
- **What single patterns hide.** It is zero exactly for 2-CNF patterns,
  log₂(8/7) ≈ 0.19 for one clause, and one bit for parity. No knot hides more
  than one bit.
- **What many distinctions can hide.** n distinctions can hide about
  n − log₂log₂n bits from their pairs (minimum covering arrays).
- **The statistical version.** It is the divergence of the uniform
  distribution from the pairwise model, at most n − log₂(n+1), reached
  exactly by Hadamard designs. On seven distinctions those are the Fano
  plane's parity networks.

### Knots from competing pairs

Pairwise rules can be combined in two ways:
- **Conjunction.** Every rule must hold. This is logic, and it never makes a
  knot from pairs.
- **Competition.** The rules are preferences, and the allowed states are the
  ones that break the fewest. Preferences that cannot all hold are called
  *frustrated* (Toulouse 1977).

Competition can make a knot from pairs. Take three distinctions and ask each
pair to agree or to differ. With an odd number of "differ"s the preferences
cannot all hold: going around the triangle, the differences would have to
cancel, and they cannot. Under conjunction the system allows nothing. Under
competition it allows the six states that break exactly one preference, and
those six form a knot: every pair is free, and the three together are not.
When all three pairs should differ, it is the not-all-equal knot.

Three results, checked in `PatternTest` (`test_competing_pairs_make_knots`):
- **Exactly four knots come from competing pairs alone.** A knot on three
  variables is the set of least states of some energy with only one- and
  two-variable terms exactly when its two excluded states are opposite. These
  are the four frustrated triangles: 4 of the 34 knots.
- **No knot on four or more variables does.** A frustrated loop of four or
  more distinctions bonds every three of them, but it is not a knot itself.
- **With hidden variables, competing pairs make every knot.** Ten 2-clauses
  and one hidden variable have the 3-clause x ∨ y ∨ z as their best states
  (Garey, Johnson and Stockmeyer 1976). One such gadget per excluded state
  gives any knot.

Why only four:
- Every function of Boolean variables is a unique polynomial with one
  coefficient per set of variables. An energy with only one- and two-variable
  terms has no coefficient on any larger set.
- On three variables, the top coefficient is the energy summed over the
  states with an odd number of ones, minus the sum over the rest. Shift the
  energy so that its least value is zero. Then only the excluded states
  count, each with a positive value, so if they all have the same parity the
  coefficient is not zero.
- A knot's excluded states are never neighbours, and two such states of
  opposite parity must be opposite. So the excluded states are one opposite
  pair.
- On four or more variables, fixing all but three variables leaves an energy
  of the same kind, so every three-variable slice excludes nothing or one
  opposite pair. Take an excluded state e and four variables i, j, k and l.
  The slice through e on i, j and k excludes e with i, j and k flipped. The
  slice through that state on i, j and l excludes e with k and l flipped. The
  slice through e on i, k and l then excludes two states that are not
  opposite, which is a contradiction.

This is the classical gap between 2-SAT and MAX-2-SAT. Whether 2-clauses can
all hold is decided in linear time (Aspvall, Plass and Tarjan 1979). Finding
the most that can hold is NP-hard, and the proof (Garey, Johnson and
Stockmeyer 1976) is the gadget above: it builds a knot from competing
2-clauses. Competition between agree and differ preferences also needs no
preferred value, since flipping every distinction leaves those preferences
unchanged. The least world of requirements needs one, since it reads true
as "exists" ("Requirement and choice").

So what a knot certifies depends on what is hidden. With every variable
visible, a knot other than the four frustrated triangles cannot come from
pairwise terms, even competing ones. With hidden variables, a knot certifies
only that the rules are not pairwise rules that must all hold.

**In statistics the four are silent** (`EMERGENCE-BITS-20261021-001A-P001`).
Take the uniform distribution on a pattern's allowed states. Its divergence
from the best pairwise model is zero exactly when the pattern is the least
set of a pairwise energy.
- **The frustrated triangles** are therefore the only knots whose allowed
  states their pair statistics predict exactly.
- **Every other knot** carries correlations that no pairwise interaction
  explains.

`SIGNED-FRUSTRATION-001D1` recorded the frustrated triangle's six tied least
states and classed pairwise frustration as false contact, because its factor
table had no registered native recurrence. The knot test reads only allowed
states. If least-violation states count as allowed, those six states are a
knot. Whether they count is open question 10.

#### Both readings tested

At the owner's request, the epic `KNOT-COMPETITION-20261019-001` tested both
readings instead of choosing one
([decision note](../research/KNOT-COMPETITION-20261019-001/competition.md);
`knotlab competition`):
- **Which knots (proved in Lean).** Under competition, rules on pairs make
  exactly the four not-all-equal knots on three variables and none on four or
  more. With hidden variables they make every knot. Under the strict reading
  they make none. The two readings agree whenever some state breaks no rule.
- **Weights matter.** Weighting one preference of the frustrated triangle
  twice removes the knot. With unequal weights, competition selects a few
  states and leaves no alternatives, and knots need alternatives.
- **Near and far (exact enumeration).** Of 470 uniform pairwise rules around
  a ring, none has near and far under the strict reading. Under competition,
  178 do, but never with more than two separation levels.
- **Growing separation.** On a strip of triangles where each triangle counts
  its own broken preferences, competition equals strict not-all-equal knots
  on the triangles. Separation then grows along the strip, from 3 to 8 on 14
  vertices, like a chain of atoms. Counted once per pair, the same rules
  settle into a few ordered states with at most two levels.

So competition is a law that turns a triangulated layout into a chain of
knots, but it does not supply the layout. No tested rule produced near and far
that its layout lacked.

Two follow-ups from 2026-10-19, checked in `tests/test_knotlab.py`
(`SpaceTest`):

- **Pairwise structure makes only flag shapes.** In a 2-CNF system a set is
  free exactly when all its pairs are free. So 2-clauses can make holes, as
  when two ties surround a circle, but never an empty triangle: three
  distinctions free in every pair yet not free together. That empty triangle
  is exactly a knot. Of 399 random 2-clause systems on six variables, 29 have
  holes and none has an empty triangle.
- **Holes made of holes.** Binding knots raises the dimension of the shape's
  holes. One knot is a circle; two knots sharing a distinction leave
  2-dimensional holes; a chain of three leaves 3-dimensional ones.
  - Two unrelated knots side by side also leave a 3-dimensional hole, because
    the join of two circles is a 3-sphere. So a higher hole alone does not
    show binding; the bonds do. Knots sharing a distinction gain a composite
    bond, and separate knots do not.
  - Naming a difference is itself a knot: A, B and w = (A ≠ B) form a parity
    knot. Naming turns information into a distinction that can be bound
    again. Forgetting the names flattens nested knots into one larger knot.

### Which knots remember a loop

Epic `KNOT-LOOPS-20261019-001` asked what happens when copies of a knot are
joined in a ring through witness distinctions
([decision note](../research/KNOT-LOOPS-20261019-001/loops.md);
`knotlab rings`). Each copy passes one witness on to the next, and the last
passes one back to the first. Then the witnesses are forgotten, and the
question is whether the ring still constrains the distinctions that remain.

For one value of a copy's other distinctions, the copy passes its witness
through a small yes/no table. Under the forgetting reading, each table either
permutes the two witness values (identity or swap) or misses at most one pair.
The ring theorem, proved in Lean (`KNOT-LOOPS-20261019-001B-P001`):

- **A ring excludes exactly the odd loops.** A ring rules out a pattern
  exactly when every table along it is a permutation and an odd number of
  them swap. So a ring of knots composes into a knot or into nothing.
- **Only parity carries a loop at full strength.** A knot whose tables are
  all permutations is a parity knot. A ring of parity knots becomes one knot
  on all its distinctions, so the loop becomes a hole, and it keeps one full
  bit at every length.
- **Other knots fade.** Every other knot keeps a trace only through its
  permutation tables. Its share of excluded patterns shrinks exponentially
  with the length of the loop. A not-all-equal ring forgets the loop
  completely.

Beyond rings (`KNOT-LOOPS-20261019-001C-E001`, exploratory):

- **Parity networks count their loops.** A network of parity knots remembers
  exactly one bit per independent loop of the network.
- **Other knots remember little on small graphs.** On those graphs (up to
  nine edges) they remembered at most 0.85 bits, and only where tables that
  forbid one pair can chain like implications and frustrate one another.
  **Corrected on 2026-10-21** (`EMERGENCE-BITS-20261021-001B-P001`). Every
  network of knots with hidden witnesses holds at most one bit per
  independent loop, and only parity fills every loop. But frustrating patches
  add up, so other knots can hold many bits in large networks: 1.32 bits on
  the Petersen graph, and an amount growing with the area on tori.
- **Many-valued tables can remember more, and order.**
  - Witnesses passed through a group of permutations keep a fixed amount at
    every length: log₂3 bits for addition mod 3.
  - When the permutations do not commute (all of S₃), the ring remembers the
    order of its loop.

So among two-valued knots, only group-like contact, which is parity, keeps a
lasting record of a loop.
- **With more values** the exact condition is weaker: contact that is
  group-like modulo the blocks of a partition (`LOOP-HOMOLOGY-20261021-001A-P001`,
  via Protasov and Voynov). The dressed parity knot remembers a loop without
  being group-like.
- **This matches a known dividing line:** local consistency methods fail
  exactly on constraints that can simulate equations over a group (Barto and
  Kozik 2009).

### What networks remember, and knots among loops

Epic `HOLES-COHOMOLOGY-20261019-001` followed the loops into networks
([decision note](../research/HOLES-COHOMOLOGY-20261019-001/holes_cohomology.md);
`knotlab holonomy`). Each edge of a network carries permutation contact: a
permutation of the witness values takes the witness at one end to the witness
at the other. The network allows its permutations exactly when the
permutations composed around its closed walks (the holonomy group) share a
fixed value.

- **Free contact records each loop separately.** Parity and addition mod q
  are free contact: a holonomy that fixes one value fixes all of them. Each
  independent loop then carries its own class, the network's H¹ with
  coefficients in the contact group, and no two loops ever bind.
- **Contact with fixed points binds loops, into atoms.** Give each loop a
  selector, so that the loop either passes the witness unchanged or applies
  its holonomy.
  - The shape of the selectors is the nerve of the holonomies' fixed-point
    sets, so every shape occurs.
  - A tie or knot among loops excludes only the pattern that selects all of
    its loops. Any proper subset of the loops can be on together, but not all
    of them.
  - The transpositions (03), (13) and (23) knot three loops this way, as a
    hollow triangle.
  - So the two extreme knots play opposite roles: parity carries a single loop
    at full strength, and the atom binds loops through fixed points.
  - **Corrected on 2026-10-21** (`LOOP-HOMOLOGY-20261021-001A-P001`). The atom
    is not the only way loops bind. In a law whose knots compose like cycles,
    twisted affine contact binds two loops whose gains are not 1 into one
    hole, a handcuff. One law cannot bind loops both ways: linear binding
    lives inside cycle-like composition, and atomic binding outside it.
- **Binding costs witness values.** A knot among k loops needs k + 1 values
  (Lean, `HOLES-COHOMOLOGY-20261019-001B-P001`). Boolean witnesses cannot even
  tie two loops.
- **These holes are shallow.** Local reasoning that holds three witnesses at
  once, or pins one, sees every impossible network over any coefficients.
  Only unpinned two-witness linear reasoning misses one, exactly when its
  coefficients can write 1 from the holonomy's orbit sizes
  (`HOLES-COHOMOLOGY-20261019-001C-P001`). The smallest integer blind spot is
  a tie between loops with holonomies (01) and (234): 3 − 2 = 1, the
  arithmetic of Lichter and Pago's coprime counterexample without its
  robustness. Holes that defeat local reasoning at every level need contact
  among three or more distinctions.

### How deep a hole is

Epic `DEEP-HOLES-20261020-001` asked how many distinctions local reasoning
must hold at once to see a network's hole
([decision note](../research/DEEP-HOLES-20261020-001/deep_holes.md);
`knotlab depth`). The networks turn the previous ones around: knots sit at
the vertices of a graph and share its edges as distinctions.
- **Charge networks.** Parity knots ask each vertex's edges to sum to its
  charge. Such a network is impossible exactly when the total charge is odd:
  a charge hole, a class in H̃₀ rather than a loop in H¹.
- **Local holes say nothing about depth.** Every knot that excludes two or
  more states is already a hole at its own scope. The program's plain hole
  criterion therefore certifies nothing on these networks.
- **Matched rings see the hole at once.** Reasoning that can compute mod 2 (F₂,
  or the integers) refutes at the size of one knot: summing every vertex
  counts each edge twice.
- **Every other field sees it only at the toggle width.** Over Q, F₃ or F₅
  the depth is exactly the toggle width, whatever the charges:
  - the toggle width is how wide a boundary the best one-vertex-at-a-time
    sweep must hold;
  - the charge has to be carried across that boundary
    (`DEEP-HOLES-20261020-001B-P001`).
- **On cubic graphs that is cutwidth + 1.** On every connected graph of
  maximum degree at most 3 the toggle width is exactly cutwidth + 1
  (`CUTWIDTH-DEPTH-20261020-001B-P001`). It is not a function of treewidth.
  Knots on more distinctions can need more: at higher degree the toggle width
  lies between cutwidth + 1 and cutwidth + ⌊degree/2⌋.
- **In proof-complexity terms.** This depth is the Nullstellensatz degree of
  the Tseitin formula, written as one polynomial per clause
  (`TSEITIN-NS-DEGREE-NOTE-20261020-001-P001`). Written instead as one ±1
  binomial per vertex, with degree measured after reduction, the formula
  needs degree exactly cutwidth.

So network holes come in two kinds:
- **Loop holes**, where contact acts on witnesses. They are shallow over
  every ring.
- **Charge holes**, where knots share distinctions. They are as deep as the
  layout's cut width, unless the reasoning computes in the charge's group.

## What is classical and what is the project's

- **Classical:** relations definable by 2-CNF are exactly the majority-closed
  ones (Schaefer 1978); majority-closed relations are determined by their
  two-variable shadows (Baker and Pixley 1975); implication loops collapse to
  equivalence classes, which is how 2-SAT is solved (Aspvall, Plass and Tarjan
  1979); three-place relations build every relation while two-place ones do
  not (Peirce's reduction thesis); Borromean and Brunnian links in topology.
  Also classical: least worlds of Horn clauses and linear-time propagation
  (van Emden and Kowalski 1976; Dowling and Gallier 1984); dual-rail encoding
  and the completeness of Horn satisfiability and monotone circuit value for
  polynomial time (Jones and Laaser 1976; Goldschlager 1977); the
  NP-completeness of circuit satisfiability (Cook 1971); Post's lattice and the Galois connection behind it (Post 1941;
  Geiger 1968; Bodnarčuk et al. 1969); the compactness theorem. Also
  classical: frustration (Toulouse 1977) and the NP-hardness of MAX-2-SAT,
  proved by building a 3-clause from competing 2-clauses (Garey, Johnson and
  Stockmeyer 1976).
- **The project's reading:** a binding is a constraint with no trace in any
  part that vanishes when either loop is erased; loops and their witnesses are
  the units; emergence begins at the first such binding; distinctions are the
  material and atoms the bonds.
- **Not implied:** atoms alone stay in linear time, and atoms with choice are
  NP-complete. That locates where hardness enters but says nothing about
  whether P equals NP. Nothing here is physics.
- **Native complexity (2026-10-24, `NATIVE-HARDNESS-20261024-001`).**
  - **The half rule.** In a contradictory network without hubs, every knot that does not cut the network allows exactly half the
    states of its edges.
  - **Native contradictions are parity contradictions.** Every native contradiction is a parity system joined by forced values, and
    native networks of every law are solved in polynomial time.
  - **Refutation.** Without parity knots, refutations need only clauses of two literals. With parity, they can need exponential
    resolution size (Tseitin).
  - **Three in two directions.** NP-hardness needs a hub as well as a knot: three places per relation and three relations per place.
    This is the knot-level form of Tovey's theorem (1984).
- **Native counting (2026-10-24, `NATIVE-COUNTING-20261024-001`).**
  - **The gluing criterion is a known recurrence.** The criterion for a knot to see only the surface, two glued copies symmetric in
    four legs, is the Fibonacci-gate recurrence of holographic algorithms.
  - **Easy exactly for the topological knots.** The four topological knots count every native network by a closed formula. Counting
    is #P-hard for the other 30 knots, given Backens's dichotomy, although deciding is easy for all.
  - **Reading.** Emergence is countable exactly when it is topological.
  - **Closed not-all-equal worlds.** They count like an antiferromagnetic Ising model: a determinant on the sphere, with the cost
    growing with each handle.
- **Native approximate counting (2026-10-24, `NATIVE-APPROX-20261024-001`).**
  - **K2 is the terraced condition.** The knot axiom K2 is the hypothesis of McQuillan's winding method. The 26 windable knots, those
    excluding at most two tuples and the parity knots, have approximation schemes given his theorem.
  - **Hard exactly, easy approximately.** With the four topological knots, 28 of 34 knots are settled. For 24 of them emergence is
    hard to count exactly and easy to approximate.
  - **Open where Fibonacci meets a twist.** The six left open are the Fibonacci knot with one or two places negated. Their networks
    are Fibonacci networks with disequality edges, and in the Fibonacci basis a twist is a reflection with a negative entry.
  - **Freezing is not hardness.** A knot freezes every native tree, so that the boundary decides the root either way, exactly when
    its excluded tuples take both values at every place. That holds for 14 knots, including the six, not-all-equal and parity. It
    refuted the predicted decay for the six, but not-all-equal freezes and is approximable.
- **Imitating a hub (2026-10-25, `SOFT-HUB-20261024-001`).**
  - **No exact hub.** No native gadget of any knot is supported exactly on 000 and 111: native supports exclude at most half their
    values.
  - **Only linked pairs make hubs.** Two solutions whose difference does not tie all three terminals together can always be rerouted
    onto off-diagonal values. So windable gadgets stay below a hub ratio of √3 (given McQuillan), and parity and no-lone gadgets
    below 1.
  - **The open knots stay low.** Their non-windable shape is a closed neighbourhood plus its antipode (0, 1 or 3 defects, never 2).
    The best gadget found reaches only 65/53, composing hubs never amplifies them, and tree gadgets are proved to stay at most 3.
    Gadgets with loops remain a conjecture.
  - **Reading.** Emergence cannot fake reuse exactly, and on trees not even approximately: the hardness of the three-literal side
    needs genuine reuse as well as emergence.
- **Hubs with loops (2026-10-25, `LOOP-HUB-20261025-001`).**
  - **No counterexample.** Adversarial search on gadgets with loops, up to 40 knots, never broke the bound behind "hub ratio at most
    3", and often met it exactly.
  - **No local proof.** Rerouting works one difference pattern at a time, but small explicit gadgets show that any proof must be
    global.
  - **No copying.** In symmetric form the bound says a terminal cannot copy the joint value of the other two without mixing on the
    cross patterns, and two terminals are never locked to each other.
- **Where counting in three dimensions becomes hard (2026-10-25, `HARD-3D-20261025-001`).**
  - **Setting.** In three dimensions the native counting laws are group laws, and they count homomorphisms π₁(M) → Γ.
  - **With boundary (proved).** Attach thickened tori to a handlebody along the curves of a planar graph. The count of maps into S₃ is
    a spin model on the graph whose repeated edges recover its 3-colourings, so it is #P-hard.
  - **Closed (proved).**
    - Doubling the handlebody closes it, and the double counts pairs of colourings: exactly 2·P(G, 9)/3^|V| for S₃.
    - The same Potts duality gives #P-hardness for every dihedral group whose order is not a power of 2 at least 16, the quaternion
      group and A₄.
    - The class-2 cases show that the bounded-H² hypothesis of the class-2 algorithm is necessary.
  - **Open.** The dihedral group of order 16, where a collision of growth rates blocks the extraction.
  - **Reading.** In three dimensions the easy-hard line is the abelian/non-abelian line, the affine boundary the program found in two
    dimensions. S₃ is hard although it is solvable, and it is the smallest non-abelian group.
  - **Correction (2026-10-25, `DICHOTOMY-3D-20261025-001`).** These hardness results were already implied by Galindo's Turaev–Viro
    dichotomy (arXiv 2605.06984, May 2026). Their identities stand, but they are an independent elementary route, not a new
    frontier.
- **Toward the full dichotomy (2026-10-25, `DICHOTOMY-3D-20261025-001`).**
  - **The second gadget (proved).** Dehn-fill parallel copies of each edge curve by square roots. No reflection is a square, so the
    reflection channels of the order-16 dihedral group vanish and its collision disappears. The top coefficient is
    4^m·8·P(G, 4)/2^|V|.
  - **The index-p theorem (proved).** It gives explicit chromatic coefficients for every group with an abelian normal subgroup of prime
    index, except one 2-group case.
  - **Already known.** For every finite group, counting is #P-hard exactly when the group is non-abelian. This follows from Galindo's
    2026 dichotomy for Turaev–Viro invariants: the Drinfeld centre of Vec_Γ is pointed only for abelian Γ.
  - **Reading.**
    - The program's affine line in three dimensions is "pointed versus non-pointed centre": abelian anyons only, or some anyon of
      dimension above 1.
    - Each hard instance hides a colouring of the flux paired with a colouring of the charge.
    - Abelian groups have the same pairs, but no gadget can isolate them, which is why they stay easy.
  - **Next (deferred).** Bounded first homology. Metabelian targets look polynomial there; S₄ is the first open case.
- **Counting with bounded first homology (2026-10-25, `BOUNDED-H1-20261025-001`).**
  - **Knots are hard for S₄ (proved).**
    - Draw a plane graph's alternating knot with every edge tripled. A full twist of three crossings is invisible to S₃, so the S₃
      colourings are free vertex potentials.
    - Over each potential, the S₄ lifts number 2 to the number of left-right cycles of the monochromatic subgraph: the bicycle law.
    - The count is a twelve-state spin model. With subdivided edges it is the 12-state Potts model at v = 1/2 (links).
    - Knot-keeping gadgets and interpolation reach the planar chromatic polynomial at 12. So counting the maps from knot groups
      (H₁ = Z) into S₄ that send meridians to transpositions is #P-hard.
  - **One level above abelian stays easy (proved).** Every group with an abelian normal subgroup and a nilpotent quotient, including
    every metabelian group, is polynomial once mod-p homology is bounded. The maps into the quotient are boundedly many, and the lifts
    above them are linear algebra.
  - **Reading.**
    - With growing homology the line is abelian versus non-abelian. With bounded homology it moves up one level of patterns of
      patterns.
    - S₄ is hard because its second level, the V₄ bits, depends non-affinely on an exponential first level, the S₃ potentials.
    - The bits run along bicycles, cycles that are also cuts: loops bound at contacts.
  - **Novelty.** No overlap found in a bounded scan. S₄ would be the first solvable group with hard knot colourings. Folklore risk is
    low to medium for the hardness and high for the polynomial side.
  - **Open.** Closed manifolds with bounded H₁, where surgery must control the longitudes. Settled by `CLOSED-H1-20261025-001` below.
- **S₄ on closed manifolds (2026-10-25, `CLOSED-H1-20261025-001`).**
  - **Replayed.** An independent code path confirms the S₄ knot hardness, and an audit of its proof finds no gap.
  - **The boundary sees half (proved).**
    - A transposition colouring always has trivial longitude. Its lift to GL(2, 3) would otherwise make the commuting meridian and
      longitude anticommute.
    - The boundary torus sees exactly half of the twisted lifting cohomology. So over every S₃ colouring, transposition lifts and
      4-cycle lifts are equinumerous.
    - Hence the two connected quandles of order 6 colour every knot equally, as Clark, Elhamdadi, Hou, Saito and Yeatman conjectured
      in 2013. Every 3-colourable knot is also non-trivially coloured by the 4-cycle quandle (Carter, Oshiro and Saito, 2009).
  - **Closed counts (proved).**
    - Surgery keeps the colourings with μ^p λ = 1.
    - With the peripheral data fixed, C₂ + C₄ = 8 + 3T and 3·C₂(K) + C₂(K # 3₁) = 16 + 12T.
    - So S₄ counting is #P-hard on closed manifolds with H₁ = Z/2, while metabelian targets stay polynomial there.
  - **Reading.**
    - The longitude, the loop that bounds the knot's surface, cannot carry the second-level bit of a transposition colouring.
    - The interior shows its boundary exactly half of its patterns, and that half fixes the counts.
  - **Observed, not proved.** The 4-cycle longitude is c^{2h}, where 2^h is the number of transposition lifts over the S₃ colouring
    with a fixed meridian. It held on 230 of 230 colourings. It looks like an Arf-type parity.
  - **Next (deferred).** SL(2, 3) decides whether the bounded-homology line is "abelian-by-nilpotent" or "Fitting height 2".
  - **Correction (2026-10-25, `S4-LIFT-PRIOR-ART-20261025-001`).** The peripheral facts above were already published by Livingston
    (J. Knot Theory Ramifications, 1995):
    - trivial transposition longitudes (Lemma 7, from Edmonds and Livingston 1984);
    - 4-cycle lifts exist (Theorem 8, conjectured by Perko in 1975, first proved by Rickard);
    - equal numbers of 4-cycle and transposition lifts (Theorem 9, also Thistlethwaite);
    - one longitude per S₃ colouring (Corollary 10).

    So the 2009 and 2013 quandle conjectures were settled implicitly in 1995, and the closed-manifold hardness rests on the knot
    hardness alone.
- **SL(2,3) with bounded first homology (2026-10-25, `SL23-BOUNDED-20261025-001`).**
  - **Polynomial (proved).**
    - SL(2,3)'s maps are A₄ maps, which form an affine space of twisted cocycles over boundedly many maps to Z₃. A sign decides
      whether each lifts through the centre.
    - That sign is a quadratic function of the cocycle, with values in the bounded group H²(M; F₂), and Gauss sums count its zeros.
    - The same holds for every group with a central (Z/2)^m layer over an elementary abelian 2-layer over a nilpotent quotient.
  - **The line moves.**
    - SL(2,3) is not abelian-by-nilpotent, so the bounded-homology line is not "abelian-by-nilpotent".
    - Fitting height 2 (SL(2,3)) is polynomial, and Fitting height 3 is hard: S₄ on closed manifolds, and S₄, GL(2,3) and the
      binary octahedral group on knots.
  - **Reading.** An affine level over a bounded top, with an untwisted quadratic sign on top, stays countable: Gauss sums are the
    quadratic analogue of linear algebra. Counting breaks when a level's dimension depends on the level below, as with S₄'s V₄ bits
    over S₃ colourings.
  - **Open.** Twisted central layers (first test: UT₃(F₄) ⋊ Z₃) and cubic obstructions inside Fitting height 2; closed hardness for
    the double covers of S₄. The twisted case is answered by `TRIPLE-PRODUCT-20261026-001` below.
- **The twisted triple product (2026-10-26, `TRIPLE-PRODUCT-20261026-001`).**
  - **Hard with H₁ = Z/3 (proved).** For UT₃(F₄) ⋊ C₃, of Fitting height 2, counting maps is #P-hard on 3-surgeries of knots.
    - **One cubic form.** By Poincaré duality, the obstruction is the twisted triple product T(a, b, c) = ⟨a ⌣ b ⌣ c, [M]⟩.
    - **Steering.** Borromean moves whose leaves lie in the kernel of the character keep H₁ and add any alternating form
      λ₁ ∧ λ₂ ∧ λ₃.
    - **The gadget.** The edge gadget Σ_{uv} (x_u + x_v) ∧ p_e ∧ s_e turns the kernel count into the 64-state Potts partition
      function, the Tutte polynomial at (79/15, 16).
  - **The line moves again.** It is not the Fitting height.
    - Pairwise obstructions with a bounded target, as for SL(2,3), are countable.
    - Three-way twisted obstructions with a free alternating part are hard.
  - **Reading (intuition, not proof).**
    - The hardness comes from Borromean binding: three loops bound as a whole with no pairwise linking. That is the K2 pattern of
      the canonical knot test.
    - The pairwise data (linking and the Bockstein part) are invariant under these moves and stay countable.
  - **Coupled blocks.** The last probe's blocks are a corank-one twisted Bockstein part plus an alternating part. Their counts depend
    on the alternating part, so no closed form follows from the twisting.
  - **Next (taken).** An independent review, then the coprime class-2 epic below.
  - **Correction from the review (`COPRIME-CLASS2-20261026-001A`).**
    - The steering formula has a rational, infinite-cyclic precursor in Moussard (2017).
    - The hardness shows that bounded H₁ is not enough. It does not answer Samperton–Weiß's twisted question, because their theorem
      assumes bounded twisted H².
- **Coprime class-2-by-cyclic groups (2026-10-26, `COPRIME-CLASS2-20261026-001`).**
  - **A dichotomy (proved).** Take G = H(F_p) ⋊ C_r, with p odd and the generator acting by (αx, βy, αβz). Counting maps with bounded
    H₁ is:
    - polynomial when α, β or αβ is trivial;
    - #P-hard when all three are nontrivial, already on r-surgeries of knots and on knot groups.
  - **What it rests on.**
    - The easy side holds for every coprime class-2 group of class (K) without a "hard pair": elementary abelian layers and an
      equivariant bilinear cocycle (a follow-up review asked to keep this hypothesis explicit).
    - On the hard side, the four ways the three characters can coincide each give a Potts gadget.
  - **The 2-versus-3 reading, now exact for this family.** Hard means a genuinely three-way interaction: three nontrivial characters.
    Borromean moves supply it, and pairwise data stay countable.
  - **Rowell's conjecture.** Rowell's 2009 Conjecture 3.2(b) says exact counting on link groups is polynomial for solvable G. It fails
    on knots for these groups, and for S₄ by the knot results of 2026-10-25, unless every #P function is computable in polynomial
    time. On links it fails more simply, already for S₃ (see the next entry). No earlier refutation was found; Kuperberg–Samperton
    (2018) called it doubtful but open.
  - **Open.**
    - General class-2 groups.
    - Extension fields.
    - Approximate counting, which is Rowell's part (a).
  - **Next (taken).** The note, a corrections epic, and a three-lane scan (next entry).
- **Links versus knots, and the next direction (2026-10-26, `ROWELL-NOTE-20261026-001`, `NEXT-DIRECTION-SCAN-20261026-001`).**
  - **On links, Rowell's part (b) fails already for S₃ (proved).** Tying torus knots into the components isolates the sector where
    every meridian is a rotation, and doubling the edge components weights it, so the count becomes a Potts model; the same holds
    for every dihedral group of order 2n with n odd. It needs unboundedly many components: with boundedly many, metabelian groups
    stay easy.
  - **On knots, derived length three is needed, and S₄ is the smallest hard group (proved).** Every group of order below 24, and
    SL(2,3), is easy on knots. The note "Counting homomorphisms from knot groups to solvable groups can be #P-hard" collects this,
    the UT₃(F₄) ⋊ C₃ case and the Heisenberg dichotomy; nothing has been sent.
  - **Approximation.** For UT₃(F₄) ⋊ C₃ approximating the knot count is #BIS-hard; for the other groups it is open.
  - **The knot test does not see the hard pair (computed).** Every group law is a Latin knot, so K1–K3 cannot tell hard groups from
    easy ones. "Three nontrivial characters" means that the three-way obstruction has no bounded place, not merely three places.
  - **General class-2 groups (scouted).** With the edge gadgets the count is a Bulatov–Grohe partition function whose weight matrix
    has rank one exactly when there is no hard pair; this sketches the dichotomy for class (K) over prime fields.
  - **Next (taken).** The pattern-1 knot was built (`PATTERN1-CHECKPOINT-20261026-001`: 133 and 2737 as predicted), then the
    dichotomy epic (next entry).
- **The class-(K) dichotomy (2026-10-27, `CLASSK-DICHOTOMY-20261026-001`).**
  - **Proved.** Take G = N ⋊ C_r of class (K), with p odd and r | p − 1.
    - **Closed 3-manifolds with |H₁| ≤ C.** Counting maps is polynomial if no cyclic subgroup of order d ≤ C (d | r) sees a hard
      pair, and #P-hard otherwise, already on surgeries of knots.
    - **Knot groups.** The same dichotomy holds, also when commutators involve the trivial character.
    - **Rowell's Conjecture 3.2(b)** therefore fails for every such group with a hard pair, unless every #P function is computable in
      polynomial time.
  - **Mechanism.**
    - The count is a positive sum of one partition function per meridian character.
    - Disjoint unions with a fixed anchor graph separate the characters, by a Vandermonde solve.
    - Bulatov–Grohe makes the hard one #P-hard.
    - The explicit construction was built and measured for all three ways the three characters can coincide, at two primes.
  - **The 2-versus-3 reading, now exact for the whole class.** Hardness comes only from a commutator joining three nontrivial
    characters: an irreducibly three-way twisted obstruction with no bounded place. Everything pairwise stays countable: a trivial
    character, or two characters with trivial product.
  - **Beyond class 2 (sketched, not proved).**
    - **A cross-layer pair.** In a class-3 group, a bracket between a layer-one and a layer-two element of nontrivial characters,
      [y, [x, y]] with x trivial, already gives the hard Heisenberg count. So the criterion lives in the associated graded, not in
      the class-2 quotient.
    - **A four-way case.** x and y have inverse characters, so [x, y] is trivial, and [[x, y], w] gives a triple Massey product. That
      is a four-way interaction among α, α⁻¹, γ, γ⁻¹ with no three-way pair. Whether it is hard decides whether the boundary sits
      exactly at three-way pairs or at "three or more".
  - **Next (taken).** The epic beyond class 2 (next entry).
- **Past class 2 (2026-10-27, `BEYOND-CLASS2-20261027-001`).**
  - **Proved: a cross-layer pair is hard.** The free class-3 group on x (trivial character) and y (α, α² ≠ 1) has, on every
    closed manifold with H₁ = Z/r and in every sector, a count equal to |Z¹| times the Heisenberg (α, α) count. So it is #P-hard,
    while its class-2 quotient has no hard pair and is easy. Past class 2 the criterion lives in the associated graded.
  - **Proved: a four-way interaction is hard where no pair can be.**
    - At r = 2 (H₁ = Z/2) no group has a hard pair, and every coprime class-2 group counts in polynomial time.
    - Yet counting into G_p = U₄(F_p) ⋊ ⟨diag(1, −1, 1, −1)⟩, of order 2p⁶ with p ≥ 5, is #P-hard on 2-surgeries of knots.
    - Its only interaction is a twisted triple Massey product ⟨c_y, c_x, c_w⟩ read against a fourth class. Every sub-bracket has
      the trivial character, so it is cohomologically free.
  - **Mechanism.**
    - Massey products become entries of unitriangular matrices.
    - Fox colourings (Burau at t = −1) preserve a form J. That duality turns the obstruction into an explicit four-linear form.
    - Cabled pure braids whose conjugators lie in the third commutator term change that form exactly by their degree-3 Magnus
      tensor, read on bundle differences of colours.
    - Symmetric powers of dihedral representations make the base form vanish on connected sums.
    - Bulatov–Grohe applies to the squared edge weight.
    - Every step was measured under a frozen contract at four primes and confirmed by an independent group-law count.
  - **The 2-versus-3 reading.**
    - With two values (r = 2), every pairwise bracket stays countable.
    - The first hard interaction is a nested bracket of three classes read against a fourth. So the line is "three or more", not
      three-way pairs.
    - This is a complexity statement, not an emergence result.
  - **Next (taken).** The r = 2 dichotomy in every class (next entry).
- **The Lie triple system decides at r = 2 (2026-10-27, `TRIPLE-SYSTEM-20261027-001`).**
  - **Proved, every class.**
    - Take a p-group of exponent p with an involution, and closed 3-manifolds with no F_p-homology.
    - If the triple product [[a, b], c] of −1 elements vanishes (an abelian Lie triple system), every homomorphism lies in a class-2
      subgroup and the count is a pure dimension formula: polynomial.
  - **Proved, through class 4.** If the triple product survives, counting is #P-hard, already on 2-surgeries of knots. So at r = 2
    counting is polynomial iff the triple system is abelian.
  - **Mechanism.**
    - One-parameter subgroups exp(c(g)A) build every class on the base.
    - Cabled pure braids steer the obstruction by the degree-3 Lie part of their conjugators, evaluated on all free −1 classes,
      including classes from deeper layers. In class 4, every extra correction has the trivial character.
    - The edge weight counts zeros of a trilinear form, so it is never constant when the triple product is nonzero.
    - All of this was measured under a frozen contract for six algebras at three primes.
  - **The 2-versus-3 reading, exact at r = 2.**
    - A bracket of two −1 elements has the trivial character and stays rigid.
    - Hardness is exactly a surviving bracket of three: the curvature of the symmetric pair.
    - This is the cleanest complexity form of "two is easy, three decides" so far, but it is still not an emergence result.
  - **Next (taken).** The general coprime dichotomy for every r (next entry).
- **Pairs supply a parity automorphism, triples decide, at every order (2026-10-27, `COPRIME-DICHOTOMY-20261027-001`).**
  - **Proved, every class.** The pair condition (nontrivial characters bracket only with their inverses) says exactly that the parity
    map (+1 on the fixed part, −1 elsewhere) is an automorphism compatible with the action. The action itself need not factor
    through two values; "collapses to an involution" was corrected after the independent review. With an abelian triple system for
    that parity, the count is a pure dimension formula at every sector order: polynomial.
  - **Proved, through class 4.** If the pairs hold and a triple survives, counting is #P-hard at every sector order. Under the pair
    condition, only "near" triples can survive: a pair of inverse characters and a third element of one of them.
  - **Mechanism.**
    - Slope d/p removes the cross-summand channels, because λ^p acts trivially.
    - Summands whose local Massey forms vanish remove the remaining base terms: negative amphichiral knots at odd orders,
      cables of T(2, p) at even orders.
    - The r = 2 steering generalizes with κ_t = t⁻² − t⁻¹ on bundles of d strands.
    - All of this was measured under a frozen contract at d = 3, 4, 5, 6.
  - **Open.** Pair failures in classes 3 and 4. The earlier proofs are consolidated, with their corrections, in one presentation
    for review.
  - **The 2-versus-3 reading.**
    - Pairs either give the brackets a two-valued parity or are themselves hard (class 2).
    - Once the parity exists, triples decide.
    - Still a complexity statement about action characters, not an emergence result.
  - **Next (taken).** Pair failures in classes 3 and 4 (next entry).
- **Pair failures: reductions, inert layers, clean edges and conserved flows (2026-10-27, `COPRIME-PAIRS-20261027-001`).**
  - **Corrections first.** The independent AI review of the previous entry's epic asked for four corrections, made here:
    - the Fox matrix normalization;
    - the cable exponent;
    - an unused coefficient-independence claim;
    - "a compatible parity automorphism" in place of "collapse to an involution".

    It also asked for two expanded steps. The proof and the presentation were reissued with precise references.
  - **Proved: maps see only the nonzero characters.** On manifolds without F_p-homology, every map over a sector of order d lands
    in the subgroup generated by the nonzero-character part. Trivial-character generators drop out. That is why the earlier
    cross-layer example was hard.
  - **Proved: inert layers transfer hardness.** If a quotient is hard on knots whose twisted cohomology avoids the characters of the
    kernel, the whole group is hard, with the total count recovered across sectors.
  - **Proved: clean edges.** Some pair failures interact with higher layers at the gadget's own characters. They are still hard
    when the edge is clean.
    - Blocks that return exactly to the meridian value make every colour local.
    - On the layer-2 variety, the Borromean insertion acts by central shifts.
    - The edge count is maximal when the two vertex states agree, because the insertion is then trivial, and strictly smaller across
      a pair-failing difference. So the edge matrix has rank at least two, whatever the higher layers do.
    - Brackets landing at character 0 are harmless: they commute with the meridian, so they never move a junction strand.
  - **Proved: conserved flows.** When the leaves' brackets reach the vertex's own characters, each edge carries a flow out of one
    end and into the other, and every vertex conserves it. Fourier duality trades the conservation law for potentials on the
    vertices. When the flow lives only where the two vertex states agree, and is bilinear there, the dual weights are non-negative
    and the same rank argument applies.
  - **Measured.** Two frozen runs on five interacting algebras.
    - The first was refuted. It asked for locality with the neighbouring edge's data off that edge's own solutions, where the
      insertion's layer-2 part really does reach distant blocks.
    - The successor tested locality on the solution variety, which is all the count needs. Every rule held in all five, and the
      controls broke locality where they should.
  - **Census.** Of 850 free graded algebras (two or three generators, classes 3 and 4, d ≤ 12):
    - 10 are polynomial;
    - 511 are hard by the triple theorem;
    - 153 are decided by the reductions;
    - 63 are decided by gadgets: 50 by clean edges, 5 by the character-0 refinement, 8 by conserved flows;
    - 113 stay open. There the edge couples to distant blocks through non-central layer-2 shifts, flows that survive off the
      diagonal, or class-4 layers at active characters. The largest family, 26 class-4 algebras, fails only through the class-4
      layer. In the one example probed, its diagonal flow is conserved with a positive Fourier transform, but at a pair-failing
      difference the two endpoints' terms stop cancelling. One algebra up to coarsening has no layer-1 hard pair at all: its pairs
      bracket layer 1 with layer 3.
  - **The 2-versus-3 reading.**
    - A pair interaction is carried by a three-component, pairwise-unlinked (Borromean) insertion.
    - Higher layers change its weights but cannot cancel it while the count stays local.
    - Still a complexity statement about action characters, not an emergence result.
  - **Next (taken).** Class-4 locality for the 26 algebras blocked only by the class-4 layer (next entry).
- **Linear flows, and locality up to relabeling (2026-10-28, `CLASS4-PAIRS-20261028-001`).**
  - **Proved: linear flows (class 3).** When an edge's leaves bracket into the vertex's own characters, the vertex conservation law
    need not cut the count unevenly. If the dual slot has no layer-1 data, both the flow and the dual slot's constraints are linear
    in that slot's data. Each edge weight of the Fourier dual is then a count of solutions to linear equations, so it is
    non-negative and the rank argument applies. This decides every algebra whose only obstruction was a vertex-root bracket.
  - **Found: class-4 gadgets are local up to relabeling.**
    - An apparent leak between distant edges was a change of coordinates. One edge's degree-3 conjugator moves its junction
      strands, and the move is absorbed upstream as a shift of another edge's degree-3 data.
    - Blocks between moved strands are conjugated uniformly, which is a gauge.
    - For fixed lower data the top equations are affine in the degree-3 data. Global and local systems have the same linear part,
      and constant parts differing by its image, the indeterminacy of a Massey-type product. The counts agree.
    - A frozen experiment (three algebras, graphs up to K₄) supports this; the cumulative design fails it.
    - Unfrozen probes afterwards: the one other edge at d = 5 failing only that condition is exactly local, and edges that are
      not clean break locality.
    - The closest classical analogue is Krushkal's additivity of Milnor's μ̄-invariants under band sums, modulo indeterminacy.
  - **Conditional: class 4.** If that locality holds on every graph, six class-4 census algebras are #P-hard by the same linear-flow
    argument, with independent potentials at the two ends of an edge, since the flows are no longer conserved there.
  - **Census.** 105 of 850 open (26 of class 3, 79 of class 4); 6 of these hard if locality holds.
  - **The 2-versus-3 reading.**
    - The pair interaction survives the passage to the dual: what a vertex must balance becomes a potential on the vertex, and
      linearity keeps the weights positive.
    - Still a complexity statement about action characters, not an emergence result.
  - **Next (taken).** Prove locality modulo indeterminacy, as the class-4 locality epic (next entry).
- **Locality in canonical coordinates (2026-10-28, `CLASS4-LOCALITY-20261028-001`).**
  - **Found: the relabeling was the solver's choice.**
    - The model solves each layer with an arbitrary particular solution, which may carry any multiple of a dual slot's class
      colouring.
    - Measuring that slot's coordinate as the colour difference between its reading and base strands removes the choice. In those
      coordinates the graph gadget's top equations equalled the single-edge ones exactly in all 84 main configurations of a frozen
      experiment (three algebras, graphs up to K₄).
    - The run is invalid under its own rule. One negative control, an edge whose failures are rare, never failed, so the test's
      power is not certified there. One algebra never reached the twisted regime.
  - **Not proved.** Inside the braid presentation each block's equation carries a geometric tail over every strand to its left, and
    the cancellation runs through shared junctions rather than block by block. Beads carrying other edges' fingers cannot be slid
    apart, and canonical coordinates depend on basepoint paths. So the six class-4 census algebras remain conditional.
  - **The 2-versus-3 reading.** The pair interaction stays local in every test; what is missing is a proof technique, not a
    counterexample. Still a complexity statement about action characters, not an emergence result.
  - **Next (taken).** Back to the core program, on the owner's agreement: geometry from a law, with nothing drawn in advance
    (question 9). The census stays open; gluing along spheres around the beads is the recorded route if it resumes.

## Open questions

1. **Native loops.** Settled in form on 2026-10-19. A loop is any logical
   structure with an open distinction. Under the forgetting reading a loop's
   presence is not a variable, so the question of where presence comes from
   no longer arises, and ticket B was retired. Before that, an exploratory
   pass under the absence reading
   ([presence note](../research/KNOT-FOUNDATION-20261019-001/presence.md))
   found that a loop under an update law keeps and reads a distinction:
   running versus frozen, with 01/10 versus 00/11. The question still open is
   which structures the program should count as native loops.
   **Infinite systems, adopted on 2026-10-20 and reopenable.**
   - In an infinite system a distinction can be opened by the system's ends
     rather than by any loop (`HOLES-AT-INFINITY-20261020-001`).
   - The owner adopted the source-aware reading. A native loop's distinction
     is flipped by a change of finitely many variables, and a knot is native
     at a solution when all its variables are.
   - Emergence then depends on the law and on the solution
     (`FROZEN-WORLDS-20261020-001`):
     - linear laws are native everywhere or frozen everywhere;
     - colourings have frozen and flexible worlds.
   - Both verdicts are recorded for every infinite-system claim, so the
     choice can be reopened
     ([request](../research/HOLES-AT-INFINITY-20261020-001/canonical_correction_request.md)).
2. **Witnesses.** Make "information outside a loop about its interior"
   precise, for example output signatures such as 00/11 versus 01/10, and say
   which witnesses may take part in further bindings.
   **Interference, adopted 2026-10-29 as a second reading (reopenable).**
   Witnesses may carry signs; a state is then allowed when its signed witness
   sum is nonzero. Under this reading the two/three boundary is a boundary of
   positivity: every three-bit knot is one cancelling witness away from pairs,
   and most knots survive native patterns of patterns instead of only parity
   (`INTERFERENCE-20261029-001`). The existential reading stays canonical for
   K1–K3, and every result records both verdicts
   ([adoption](../research/INTERFERENCE-20261029-001/canonical_correction_request.md)).
3. **Composition.** When do bindings joined through witnesses form larger
   structure, and does the result depend on the choice of witnesses?
   **Answered for loops on 2026-10-19** ("Which knots remember a loop"). A
   ring composes into a knot or into nothing. It keeps a constraint only
   through permutation tables, and parity alone keeps a full bit at every
   length.
   **Networks, 2026-10-19** ("What networks remember, and knots among
   loops"). Free contact keeps one class per loop. Contact with fixed points
   binds loops into atoms, in any shape, at k + 1 witness values for k loops.
   **Later answers, 2026-10-21.**
   - **On bits** (`BASE-THREE-20261021-001`). Two knots sharing one
     distinction compose into one knot exactly when they can force it to
     opposite values; otherwise they form a hub.
   - **Composing like cycles** (`CYCLE-TOPS-20261021-001`,
     `AFFINE-TOPS-20261021-001`). A law's knots compose like cycles exactly
     when every range has a top, ties are bijections modulo the tops, and one
     ternary polymorphism is Mal'tsev modulo the top of every knot range. The
     tops are then affine over finite fields.
   - **Memory** (`LOOP-HOMOLOGY-20261021-001`). Rings remember exactly when
     their contact is group-like modulo blocks. Networks in cycle-like laws
     remember twisted first cohomology.
   - **Gates** (`NATIVE-NETWORK-20261021-001`). Two knots sharing a
     distinction in such a law pass the contact-network gates under
     recodings, erasure and pp-definitions. Pinning passes only when the law
     with constants still composes like cycles.
   - **Accounting** (`EMERGENCE-BITS-20261021-001`). A network with hidden
     witnesses holds at most one bit per independent loop, and only parity
     fills every loop.
4. **Dynamics.** Are loops better modeled as processes whose outputs over time
   are the data, and does the static definition survive that change?
5. **Repository consequences, resolved on 2026-10-19.** The owner adopted
   K1–K3 as the canonical test with erasure read as forgetting.
   `KNOT-FOUNDATION-20261019-001E-P001` and `KNOT-FOUNDATION-20261019-001A-P001`
   replace Proof 0009's transition semantics and the earlier Lean kernel's
   erasure condition. The
   [foundation triage](../research/KNOT-FOUNDATION-20261019-001/foundation_triage.md)
   labels every foundations and topology record under K1–K3. The choice and
   space questions are tickets C and D of `KNOT-FOUNDATION-20261019-001`.
6. **Choice. Answered on 2026-10-19.** Choice is native wherever knots are.
   Its smallest form is an open distinction, and requirement and choice are
   one knot read two ways
   ([decision note](../research/KNOT-FOUNDATION-20261019-001/choice.md)).
7. **Limits.** Does the program need a contact that binds infinitely many
   loops? That would need a declared limit rule, since no set of finite
   clauses defines one.
8. **Forgetting or absence? Resolved on 2026-10-19: forgetting.** The
   original post entwines patterns by whether they match, which is parity,
   and parity counts only under the forgetting reading. The owner chose
   forgetting, with these consequences:
   - "constrained as a whole, unconstrained in every part" became the knot
     test;
   - parity became the most informative knot;
   - the doctrine that a parity pattern is never a knot was rewritten.

   The record is
   [the decision](../research/KNOT-FOUNDATION-20261019-001/canonical_correction_request.md),
   and the proof is `KNOT-FOUNDATION-20261019-001E-P001`.

   **Where "erasure" came from.** The owner did not introduce it; it was
   already in the agents' gate in the workspace's first commit (2026-07-24).
   `docs/INTUITION.md` gives the purpose:

   > Erasing `B` leaves the `A-k` relation meaningful, so there was never one
   > irreducibly joint touch between the recurrences.

   Erasure was a test for decomposability: remove one loop and see whether
   anything is left between the other loop and the contact. That is the
   forgetting reading. Read that way, the test is not a separate condition.
   It holds exactly when neither loop is tied to the contact by itself, and
   adding that the loops are not tied to each other gives "no pair of the
   three is constrained". The absence reading, with a presence variable set to
   absent, came from the 2026-10-19 formalization, not from the original
   gate.
9. **Space from a law.** Logic allows every shape. Which uniform, local law,
   not written on a space in advance, gives a shape that looks like a space
   of low dimension? This is open and shared with causal sets, quantum
   graphity and hypergraph rewriting. Since 2026-10-19 there is one necessary
   condition: a law can keep a lasting record of its own loops only if its
   contacts act as group elements on the witnesses ("Which knots remember a
   loop"). A law whose contacts have fixed points can also bind its loops
   into knots ("What networks remember, and knots among loops"), but every
   network so far was laid out by hand. A network's charge hole has a depth
   set by its layout's cut width ("How deep a hole is"): an invariant of a
   whole network's extent, though a width rather than a distance.
   **2026-10-21.**
   - **What a declared substrate fixes** (`NATIVE-NETWORK-20261021-001`). Its
     allowed states fix contact adjacency, routes, separation and an extended
     bond distance, without any drawing.
   - **What they do not fix.** The drawing is not recovered, and the law fixes
     no substrate: the substrates of one law realize every representable
     matroid.
   - **What survives growth** (`EMERGENCE-BITS-20261021-001C-E001`, an
     experiment). On declared surfaces woven from not-all-equal knots,
     emergence held only by global cycles vanishes as the honeycomb grows. On
     the square lattice it stays at about 0.83 bits at every tested size.
   - **Why: fairness is criticality** (`BASE-CRITICALITY-20261022-001`).
     - **The mechanism (proved).** Recoloured, fair visible distinctions
       orient the hidden implications by coin flips, and reach through
       coin-flipped implications is bond percolation at exactly 1/2. A world
       with no directed crossing of its cut surface in one direction is
       consistent.
     - **The regimes.** Global emergence vanishes below a lattice's bond
       threshold, stays bounded on the square lattice, where self-duality
       puts the threshold at 1/2, and diverges above it. Cubic 3-tori
       diverge.
     - **The square lattice (an experiment).** The amount depends only on
       shape: it is rotation-invariant and stable under shear, as at a
       conformally invariant critical point.
     - **Still open.** Whether not-all-equal's amount stays bounded away
       from 0.
   - **Which contacts are critical** (`CONTACT-CENSUS-20261022-001`).
     - **The census (proved).** Place one three-variable knot on every edge
       of a square-lattice torus, with the joints hidden and one fair
       visible distinction per edge. The 204 placements fall into 10
       classes:
       - six have a vacuum, a constant joint value that satisfies every
         edge, and hold nothing;
       - parity and swap-or-order frustrate small patches, so they grow with
         the area;
       - exactly two hold a scale-free amount: not-all-equal and "x or
         (h ≠ h′)".
     - **One of them is solved.** "x or (h ≠ h′)" is consistent exactly
       when its disequality edges, bond percolation at 1/2, are bipartite:
       no cluster may contain an odd cycle, and on the square lattice every
       odd cycle winds the torus. So its amount is
       bounded on both sides (proved). Its limit is a winding quantity with
       a conformal formula (Pinson 1994), and the measurements match it on
       six shapes within about 1.5 standard errors (an experiment).
     - **The other is located, not solved** (`NAE-INVARIANT-20261022-001`).
       - **The reduction (proved).** Fixing the visible distinctions leaves a
         world of pairs. Its implications form a random orientation of the
         bipartite double cover, and swapping a variable's two literals
         reverses every arrow. The world is inconsistent exactly when a
         strong component (literals that all reach one another) is mapped to
         itself by the swap. Equivalently, the cyclic edges form a cluster
         wrapping an odd cycle.
       - **The twist (proved).** Going around an odd cycle reverses every
         arrow. That makes primal and dual cyclic edges exactly
         complementary, so P(all contractible) = P(cross), as in ordinary
         percolation.
       - **The class (an experiment).** Strong components of a fair random
         orientation are strongly-connected percolation, a known
         universality class:
         - fractal dimension 1.80;
         - not the backbone, and not two independent percolation arms.
       - **The value.** The amount is scale-free on every shape tried (0.846
         bits on square tori with both sides odd). No Coulomb-gas formula of
         Pinson's kind fits it.
       - **Not half a bit** (`SC-TORUS-EXACT-20261022-001`). On square tori
         with one odd side it is 0.4963 ± 0.0003 bits, so P(consistent) is
         0.7089, not 1/√2. The earlier "half a bit" came from a noisy
         estimator (an experiment).
       - **Directed winding (proved).** The classes of directed closed walks
         fill exactly a convex cone, and the dual orientation's fill its
         polar. On ordinary square tori this makes the published wrapping
         value 3/4 mean: no directed closed walk winds horizontally with
         probability exactly 1/4. That value survives a precise test
         (0.7504 ± 0.0002), but no identity of this kind can force it.
       - **Relations among the twists** (`TWIST-RELATIONS-20261022-001`).
         Twisting the torus one way or both ways gives four amounts.
         - **Shear (proved).** A shear turns part of them like a whole
           harmonic and part like a half-integer one. So "the twists add up"
           holds only in an orthogonal frame, and shearing breaks it.
         - **Odd loops (proved, `ODD-LOOP-20261023-001`).** The chance that
           the only thing wrong is a single odd loop along a direction is the
           same for both twists that make that direction odd, on every torus.
           The loop is its own wall. Every arrow crossing its upper edge
           either feeds the loop from one sheet or leaves it into the other,
           so the other twist can be slid onto that edge without creating or
           destroying any directed cycle. This pairs the configurations of
           the two twists one to one. A contradiction loop is blind to how
           the other direction is twisted. The pairing needs fair coins, and
           the stronger claim that the shear does not matter fails.
         - **Shielding (proved and tested, `LOOP-SHIELD-20261023-001`).** On
           any closed surface a lone contradiction loop along c is blind to
           exactly one change of twist: the twist dual to c, the one that
           counts crossings with the loop. A seam made of edges touching the
           loop can carry no other twist (Lefschetz duality). On genus-2
           surfaces, where eight twists make c odd, exactly the dual pairs
           agree and the rest differ (every orientation counted). In three
           dimensions a loop cannot separate, no wall exists, and no twist is
           shielded (thin and cubic 3-tori). What a contradiction screens is
           dual to its own shape, and it needs codimension one.
         - **Where exact relations come from (proved and tested,
           `TWIST-MAP-20261023-001`).** The number of orientations whose
           cyclic edges form a given skeleton is a product of two small
           counts: orientations of the skeleton with every edge on a cycle,
           and acyclic orientations of the graph with each cluster shrunk to
           a point. This is the cyclic–acyclic decomposition of an oriented
           matroid. A twist reaches a count only through these two pieces,
           so two twists agree whenever the pieces match, after merging
           series edges inside clusters and parallel edges outside. Walls
           are the special case of an odd cluster, a point whose two sheets
           have merged so that no twist around it is visible; for clusters
           of any rank they form the dual of the radical of the cluster's
           lattice. On genus 2, walls and the surface's symmetries leave
           exact equalities unexplained. Every one found holds skeleton by
           skeleton, and most come from matching pieces, often by symmetries
           the surface itself does not have. A few come from two different
           shrunken graphs with the same number of acyclic orientations,
           which no isomorphism explains.
         - **Three places (proved and tested, `TRIPLE-TWIST-20261023-001`).**
           For contacts with three hidden places, a twist is a class only
           when flipping all three places swaps the contact's two relations;
           otherwise a seam is a defect. Not-all-equal on four places stays
           frozen in every twist. When the doubly allowed patterns tile the
           plane, no planar region contradicts, and every minimal
           contradiction on a torus winds, along a class that the twist makes
           odd relative to the tiling's own twist, as two-literal
           contradiction loops do.
         - **The last twist relations (proved,
           `ACYCLIC-COINCIDENCE-20261023-001`).** The few genus-2 relations
           that the twist map left to two different shrunken graphs come from
           one local move. Take a path through points of degree 2 whose ends
           are already joined by links of both signs. It can change its sign
           without changing the number of acyclic orientations. The two links
           already forbid the ends from matching in either sense, which is the
           only thing the path's sign could decide. Every exact twist relation
           found on genus 2 now has an explanation.
         - **Shielding at three places (proved and tested,
           `TRIPLE-SHIELD-20261023-001`).** It does not survive.
           - **Where it holds.** A lone contradiction line is blind to the
             dual twist when each fair coin decides a contact on two places.
             That is a theorem on every torus.
           - **Where it fails.** As soon as one coin decides three places, the
             two twists give different counts on every small torus tested.
             This holds whether the coin sets one three-place relation or two
             two-literal clauses at once. At three places, part of that
             difference turned out to come from directions the count never
             checked (next item).
           - **What separates the two sides.** Shielding is a law of pairwise
             coins. The line falls at how many places one random choice
             reaches, not at how many literals a clause has.
         - **Directions of contradictions (proved and tested,
           `LINE-DETECTOR-20261023-001`).**
           - **Two literals.** A contradiction runs along nothing, along one
             class, or along every class the twist makes odd, whatever the
             coins. The doubly allowed tiling fixes the parity of every closed
             implication walk.
           - **Three places.** A contradiction can run along some odd classes
             and miss others. So a "lone line" checked against three
             directions need not be a line, and most of the largest
             three-place differences came from directions nobody checked.
           - **What remains.** Lines pure among eight classes still differ
             between the two twists, so a three-place line does see the twist
             that crosses it.
           - **Where the clean line falls.** The clean two-versus-three
             contrast is the direction structure, and it falls at clause
             width.
         - **Which contacts are rigid in direction (proved and tested,
           `DIRECTIONAL-RIGIDITY-20261023-001`).** Algebra does not decide it.
           Every three-place tiling contact has only trivial polymorphisms,
           and renaming the three places of one relation can turn a rigid
           contact into a selective one. Geometry decides it. Where a twist
           forces an assignment to change value, it leaves a wall.
           - **Free stripes.** If the doubly allowed patterns let whole
             stripes flip along one edge direction, contradictions can run
             only along that direction (the diagonal), or nowhere (rows and
             columns at once).
           - **Straight walls.** If a coin-pinned wall can never cut off the
             corner at one particular end of the diagonal edge, every wall is
             a straight diagonal staircase. One wall serves every direction at
             once, so a contradiction runs along every odd class or none.
           - **Bending walls.** If walls can cut off the corners at both ends
             of the diagonal edge, they can turn, and the contact is
             selective.
         - **The wall rule (proved and tested,
           `WALLS-WITH-CHOICES-20261024-001`).** For 27 of the 30 three-place
           contacts (the other three have diagonal stripes and are settled
           separately), a direction contradicts exactly when every periodic
           wall that crosses its cylinder would collide with its own copy
           there. Walls with choices obey the same rule. If a cylinder has an
           assignment at all, then some finite cover of it does, and one of
           that cover's walls crosses the cylinder's loop an odd number of
           times.
           - **Walls that move only up or left** keep every direction of the
             open first quadrant together: those directions contradict all
             at once or not at all.
           - **Planted walls.** For eight of the twelve contacts with bending
             walls, one planted staircase makes a configuration selective on
             every torus with both sides at least 3.
           - **The kind left open.** The other four, whose walls turn both
             ways and have a free place, are selective on every torus
             computed. For them walls are almost unavoidable, so no single
             wall can be planted on a quiet background. And a wall that
             serves a direction sometimes has to pass the same state twice,
             winding several times around the torus before it closes, so a
             search over simple cycles misjudges them.
         - **The cost of reading a direction (proved and tested,
           `READING-COST-20261024-001`).** For walls that move only up or
           left, deciding whether a direction contradicts takes polynomial
           time, even when the walls have choices.
           - **Why.** Every move is allowed or not by itself, so two good walls
             combine by taking the higher or the lower of the two at each
             step.
           - **Short walls suffice.** Lining a good wall up with its own
             translates and cutting out loops at repeated squares shortens it
             until it is simple on the cover that undoes the twist. A search
             over simple cycles is then always enough.
           - **Covers say little.** Such walls may still need covers of
             several sheets, so the number of sheets is not what makes a
             direction hard to read.
           - **Where this stops.** Among the contacts with bending walls, only
             the four whose walls turn both ways and have a free place have no
             such rule. Their walls wind, so one wall meets both chiralities
             of the triangle rules and two walls cannot be combined. On 4 × 4
             and 4 × 5 tori simple cycles keep misjudging them.
     - **Still open.** A closed formula for strongly-connected percolation on
       tori; the lower bound, now the probability that directed cycles wind
       in every direction; and, for the four contacts whose walls turn both
       ways with a free place, both selectivity on every large torus and
       whether reading a direction is hard or easy.

   **2026-10-24: what native gluing builds** (`SURFACE-GLUING-20261024-001`).
   - **Surfaces from sharing (proved).** Native contact requires every shared distinction to join exactly two knots.
     - Glued that way, a network is a pants decomposition of a compact orientable surface. Each knot is a pair of pants and each open
       distinction a boundary circle; the genus is the number of independent cycles.
     - Two-place relations glue only into lines and loops.
     - A hub is the one place where three sheets meet.
   - **Laws that see only the surface (proved).** Exactly four knots give witness counts that depend only on the surface:
     - parity, with one hidden bit per handle;
     - the two "no lone value" knots, whose closed counts 2, 5, 15, 50, … grow by the rates (5 ± √5)/2.
   - **What they are (classical).**
     - They are the fusion rules of the two smallest topological theories, each with either value as the vacuum. Parity is the abelian
       one, and "no lone one" is the Fibonacci anyon.
     - Their counts are Verlinde dimensions. Two incommensurable rates cancel into integers.
   - **Memory is not built natively (proved).** Hub-free gadgets of non-parity knots never produce parity, so a law has memory
     natively only if it starts with it.
   - **Still open.** Geometry, and dimension three. Three-dimensional state sums share labels among many pieces, which is hubs.

   **2026-10-24: dimension three** (`HUB-DIMENSION-20261024-001`).
   - **Native networks are blind to it (proved).** A native network of a triangulation, with bits on faces, is only the dual graph
     with slots. The sphere and L(4,1) have one-tetrahedron triangulations with the same native network.
   - **With hubs, bits see little (proved).** Put the bits on edges, each shared by every triangle around its edge.
     - Of 32,768 symmetric laws, only trivial ones and parity survive the moves that relate triangulations of one manifold.
     - Parity counts the mod-2 first cohomology, which the two-dimensional skeleton already determines. So no such law separates the
       sphere from L(5,2).
   - **The Fibonacci rule needs a sign (proved).** To see three-manifolds, it needs a negative weight on the all-τ tetrahedron. Its
     incommensurable rates cancel into counts on surfaces, but in three dimensions they need interference, which no count of hidden
     witnesses supplies.
   - **Reading.** Native space is two-dimensional topology.

   **2026-10-25: twists in three dimensions** (`TWIST-3D-20261025-001`).
   - **Twists add nothing (proved).** Let each triangle read its edges in vertex order, so any triangle rule can be used, the twisted
     Fibonacci knots included, and let tetrahedra depend on orientation. Exactly the same seven laws survive the moves (354 over all
     triangle rules), and each twisted knot keeps only a constant law and its parity law.
   - **The sign survives the twist (proved).** Positive weights for the Fibonacci and twisted Fibonacci rules cannot cover their
     support. They live on constants or on the parity class, where they are pure gauge and count cocycles.
   - **Reading.** Bits see a three-manifold only through its mod-2 first cohomology, twisted or not. Seeing more takes signs, or
     distinctions bigger than a bit: patterns of patterns.

   **2026-10-25: patterns of patterns in three dimensions** (`PATTERN-3D-20261025-001`).
   - **The moves force a groupoid (proved).** Let the long edge of each triangle be a function of its two short edges, on any finite
     set of labels.
     - Such a law survives the moves exactly when its working triangles are the compositions of a groupoid with all components alike.
     - The 2–3 move asks for associativity and the 1–4 move for division.
     - The objects are invisible. They are recovered as the labels that compose with themselves to themselves.
   - **Nothing else on three labels (supported).** All 2²⁷ triangle relations on three labels were tested, functions or not.
     - Every survivor is a groupoid law, possibly with free decorations: one, two or three constants, Z₂, Z₃, or the free laws.
     - On four labels, every surviving multiplication table hides a groupoid: Z₄, Z₂ × Z₂, the pair groupoid, or constants.
   - **What they see (classical).**
     - The count is a sum of |Hom(π₁(M), G)|/|G|: how the loops of space map into a finite symmetry group.
     - Together these counts see exactly the finite quotients of π₁.
     - They never separate lens spaces of equal order, such as L(5,1) and L(5,2), nor the pairs of Funar and Hempel.
   - **Only the knot part sees.**
     - A groupoid's triangle relation is a knot only when it has one object, a group. With more objects, composability constrains
       pairs.
     - The objects cancel from the invariant. So the pairwise part sees nothing, and the group knot does all the seeing.
   - **Reading.** Patterns of patterns that live natively in three dimensions are symmetries. Counting sees space only through its
     loops' finite symmetries; a linking form takes phases.
   - **The complexity edge (cited).**
     - Abelian symmetries count easily, and so do class-2 nilpotent ones (Samperton and Weiß).
     - Non-abelian simple ones are #P-complete (Kuperberg and Samperton).
     - The boundary in between is open.
     - This boundary became an 18-epic side tangent (from `HARD-3D-20261025-001` to `CLASS4-LOCALITY-20261028-001`), listed under
       "What is classical and what is the project's". On 2026-10-28 the owner agreed to return here.

   **2026-10-29: geometry from a law, nothing drawn** (`GEOMETRY-LAW-20261029-001`).
   - **The question.** A uniform law can coarse-grain itself: replace each knot by a native gadget made of copies of the same knot,
     a pattern of patterns. Which laws survive that, in which shapes, and can a law fix an orientation or a scale?
   - **Only parity survives (proved for every gadget size).**
     - The two parity knots are rebuilt by every native gadget of their copies.
     - Every other three-place knot's gadgets exclude strictly fewer tuples: none for the atoms and not-all-equal types, at most one
       when two tuples at distance two are excluded (only the triangle of three copies), at most two when three are.
     - So towers of patterns of patterns built from one non-parity law reach the free relation within three levels.
     - The proof is the cactus structure of native contradictions (`NATIVE-HARDNESS-20261024-001B`) applied to three legs.
   - **No orientation at three places (proved).** Every three-place knot's symmetry group contains a transposition, so no
     placement orients a vertex.
   - **Four places (exhaustive for gadgets of two and three copies).**
     - 96 of the 742 four-place knots, in 6 classes, can orient a vertex. None of them survives.
     - What survives is parity, and one implication between the parities of two pairs, (x₁ + x₂ → x₃ + x₄). That implication is a
       two-place relation on derived bits, rebuilt exactly by chains, so its towers are lines.
   - **Counting (scoping).** Weighting each tuple by its number of hidden witnesses keeps only a bias at each distinction and pairwise
     bonds under the two smallest substitutions, never a three-way bond.
   - **Background (classical).** Each knot of a closed native world is a pair of pants, a unit of negative curvature, so the world
     admits only hyperbolic metrics. Two-place relations are flat and pins are positively curved. The metric itself is left free.
   - **Reading.**
     - Native logic builds two-dimensional topology and fixes its curvature type, and nothing geometric survives patterns of
       patterns. What survives every scale is shapeless (parity) or one-dimensional (pairwise).
     - At the level of patterns of patterns the two/three boundary reappears as "pairwise or parity". Emergent information does not
       grow by naming patterns, except parity's one bit per loop.
     - If anything in the base is universal across scales, it is parity's cycles, the holes. This is a reading of the owner's
       "infinite cycles of logic that are universally influential", not a theorem.
   - **Next (taken).** The owner put hub laws in scope. Scoping showed the fairness test mostly confirms classical percolation, so the
     hub route became the survivors question (next entry).

   **2026-10-29: what survives once hubs are allowed** (`HUB-SURVIVORS-20261029-001`).
   - **The owner's decision.** Hub laws are in scope as a declared substrate. A hub is equality fan-out, pairwise, never a contact
     (the canonical common hub).
   - **Parallel copies (proved by exhaustion within six copies).** Hubs let copies share all their variables, which intersects
     their constraints.
     - Seven of the 16 classes are rebuilt by their own copies: parity, and from four copies "x or (y ≠ z)", the three-excluded
       classes with a symmetry of order two, and twisted not-all-equal. Their intersections reach parity or an equality.
     - The monotone atoms never are.
   - **Not-all-equal survives through the Fano plane (proved).**
     - Its copies on the seven lines of the Fano plane, with one point split into the three legs, rebuild it.
     - No gadget of six or fewer copies does, and at seven the punctured Fano plane is the only one (property B: m(3) = 7).
     - Each allowed tuple has exactly five completions. So not-all-equal is an exact counted fixed point, and each level adds
       log₂ 5 bits per copy.
   - **Reading.**
     - With hubs, emergence beyond parity persists across scales.
     - The smallest pattern of patterns of the frustration knot is a finite projective plane, an incidence geometry produced by the
       law's own self-reproduction.
     - Hubs add nothing to pairwise relations (equalities in parallel stay equalities), but they let three-place knots run in
       parallel.
   - **Next (taken).** Exact self-similar laws (next entry).

   **2026-10-29: laws that reproduce themselves with their counts** (`EXACT-TOWERS-20261029-001`).
   - **Which laws (proved by exhaustion within six copies).** A gadget is exact when it rebuilds its knot and every allowed tuple
     has the same number of hidden completions. Its tower then has the same law at every scale, counts included.
     - Parity is exact for every rebuild, by linearity.
     - Twisted not-all-equal is exact from four copies, and the two three-excluded classes from five.
     - Not-all-equal is exact at seven copies (the Fano plane).
     - "x or (y ≠ z)" is rebuilt but never exact: its counts drift toward a decomposable pair of tuples.
   - **What the towers are (proved).** Each law's smallest exact self-reproduction builds a definite space:
     - the Sierpinski gasket for parity, growth exponent log₂ 3;
     - a triangle subdivided into four with private midpoints for twisted not-all-equal, exponent 2;
     - a tower of Fano planes for not-all-equal, exponent log₃ 7.
   - **The limit (proved).**
     - Every exact tower is finitely ramified: bounded treewidth, three points cut off any sub-tower. So exact self-reproduction
       never builds separation in two or three dimensions.
     - Its corners are exactly as correlated at distance s^k as at distance 1, but only at the hard law. Softening grows at least
       threefold per level, the classical picture for finitely ramified fractals.
   - **Reading.**
     - The allowed states (the canonical knot test) survive every rebuilding tower.
     - The counted law, a branch-internal measure, survives only exact ones. Set-level emergence can persist where counted
       emergence fades.
   - **Next (taken).** Shared-boundary self-reproduction (next entry).

   **2026-10-29: self-reproduction on genuinely two-dimensional space** (`SHARED-SUBDIVISION-20261029-001`).
   - **The test (exact census).**
     - Copies of one knot class sit on the triangular lattice, on up triangles or on all triangles, which gives 122 rules.
     - Every triangle is cut into four, or nine, with new vertices shared between neighbours. This space is not finitely ramified.
     - Only 22 rules reproduce themselves exactly at scale 2, and 6 at scale 3.
     - Every exact rule has an affine solution set and zero entropy density. Not-all-equal (Wannier's antiferromagnet) never does.
   - **Who survives (proved).**
     - **Parity on up triangles**, the Newman–Moore model. Exact at scale 2 because (1 + S)² = 1 + S² over two values, with
       N(2m) = N(m)².
     - **Parity on all triangles**, with the Baxter–Wu ground states. Exact at scale 2 because 2 permutes the three colour classes.
       Twelve three-excluded rules have exactly the same solutions on every torus tested.
     - **Twisted not-all-equal.** Exact at every scale, but only by collapsing into lines of constant value. No triangle then carries
       a knot.
   - **Reading.**
     - On genuine two-dimensional space, exactness keeps a knot only through parity. Everything else that survives is pairwise
       (lines), and all the other knots fail.
     - This is the two/three boundary appearing as a law of self-similarity.
     - The parity families are rigid on the plane, so under the source-aware reading nothing native lives there.
     - Non-linear emergence reproduces itself exactly only on tree-like spaces (the previous entry).
   - **Next (recommended, awaiting the owner).** Is exact self-reproduction on genuine space always affine (2/3)?
     - First test: all 256 relations on three bits on up triangles, and a local criterion that would make it a theorem.
     - Alternative (1/3): how fast not-all-equal's corner correlation decays across scales (Wannier criticality).

   **2026-10-29: interference, after the ETH refutations** (`INTERFERENCE-20261029-001`).
   - **The prompt.** Two October 2026 refutations of the Exponential Time Hypothesis (OpenAI; Anthropic) count k-CNF solutions in
     2^{O(n/√log n)} on sparse inputs, and both get their speed from cancellation: a clause is 1 − Π(1 − ℓ), intermediate sums are
     signed, and the octonion eight-square identity trades two crossing equality contacts for a four-place parity times signs. The
     owner asked what the program can use.
   - **The two/three boundary is a boundary of positivity (proved).** With nonnegative weights, no sum over hidden bits of products
     of two-variable functions has a knot as its support. With signs, every three-bit knot is exactly such a sum with one hidden
     bit (real tensor rank 2; not-all-equal after one pairwise sign; the Fibonacci knots carry the golden ratio), and a 3-CNF is one
     hidden bit per clause. That signed pairwise form is where OpenAI's algorithm starts, and Anthropic's bound in n.
   - **Signed patterns of patterns (proved by exhaustion within five copies).** Counting rebuilds only parity in native gadgets of
     its own copies. With weights ±1, 14 of the 16 classes are rebuilt and 12 exactly; 10 are exact on the native triangle, so the
     Sierpinski gasket carries signed not-all-equal at every level. Signs supply what hubs supplied (identity wires by
     cancellation). The Fibonacci knots are never rebuilt with ±1, and the symmetric atoms never exactly.
   - **What did not change.** On genuine two-dimensional space the answer stays parity: the shared-boundary substitution keeps
     only parity for signed laws constant on rotation orbits on the first three spheres, as `SHARED-SUBDIVISION-20261029-001` found
     with counts on the triangular lattice. Interference revives knots in finitely ramified towers, not yet in two dimensions.
   - **Their cores, replayed (an exploratory experiment).** The eight-square identity and its 3-versus-6-bit costs, the grouped
     pieces of Anthropic's Lemma 2, the partition pieces of its Theorem B at one to three bits, and the swap-matrix lemmas of
     OpenAI's construction recompute exactly from the papers' statements; the octonion sign table is a Hadamard matrix of order 8.
   - **Reading.** The barrier the refutations break (cut cost on expanders) is the one the program measured for positive and
     linear reasoning; a counted (nonnegative) rewriting cannot lower a crossing's cut cost at all. Cancellation is the
     interference the owner's "harmonies" intuition points to: incommensurable signed parts that cancel into a whole.
   - **Owner decision (2026-10-29).** Cancelling witnesses were adopted as a second reading beside the existential one, reopenable
     (question 2; [record](../research/INTERFERENCE-20261029-001/canonical_correction_request.md)).
   - **Next (taken).** Interference on genuine two-dimensional space (next entry).

   **2026-10-29: interference on genuine two-dimensional space** (`SIGNED-SUBDIVISION-20261029-001`).
   - **The test.** The 122 triangular-lattice rules of `SHARED-SUBDIVISION-20261029-001`, now weighted. Weights ±1 give 135,440
     signed rules in 944 gauge classes; arbitrary real weights are read through the interference reading.
   - **Signs (proved by exhaustion).** No new rule reproduces itself, not even its allowed states. The old exact rules keep their
     allowed states under every sign pattern at scale 2. Only some sign classes keep their weights: one of two for parity and the
     frozen laws, and two of eight for twisted not-all-equal (six of eight at scale 3).
   - **Real weights (proved where decidable).**
     - Positive weights see only the counted allowed states, so they add nothing.
     - *Sign-parity obstruction.* Suppose every fine extension of a forbidden coarse state uses each tuple equally often mod 2.
       Then all its terms have one sign and nothing cancels. This rules out 54 of the 100 non-exact rules at scale 2, for every
       real weighting.
     - On the affine rules, real magnitudes add only gauge copies of the ±1 exact laws.
     - Small tori let spurious exact weights through: −2^(±1/9) for parity on up triangles, and the golden ratio and the tribonacci
       constant for twisted not-all-equal. Larger tori remove them. So the golden ratio, the suggested starting point, appears only
       as an artifact.
   - **The densest laws (searched, exploratory).** A search over every sign class found no exact weighting of the 46 densest
     laws. But it failed its own power check, missing two known exact classes, so it counts only as exploratory evidence. Its one
     candidate, at scale 3, was a degenerate point where nearly everything cancels, and it fails on the 3-torus.
   - **Reading.**
     - Interference reproduces knots on finitely ramified, tree-like space but not on genuine two-dimensional space. There, shared
       midpoints make a cancellation inside one triangle impossible to arrange across the lattice.
     - Exact self-reproduction on genuine space is affine under every reading tried: existential, counted, signed and real.
   - **A lead (scoping, not evidence).** Take not-all-equal with −1 exactly when the first corner is the odd one out. It reproduces
     itself exactly on the level-k Sierpinski gaskets (copies on the up triangles of a k-subdivided triangle) for k = 2 to 11, with
     factors −1, −4, 13, 85, −634, …, in exact integer arithmetic. These gaskets are finitely ramified, with dimension
     log(k(k+1)/2)/log k → 2. For laws on up triangles, the subdivided plane is these gaskets plus the up triangles that join
     neighbouring ones. So the joining triangles are what breaks exactness.
   - **Next (taken).** Signed not-all-equal on every level-k gasket (next entry).

   **2026-10-29: a knot that builds every gasket** (`SIGNED-GASKETS-20261029-001`).
   - **The law.** Signed not-all-equal, −1 exactly when the first corner is the odd one out, has three faces.
     - It is (−1)^a times the Legendre symbol of a + b + c modulo 3.
     - It is the multiplication of the Eisenstein numbers.
     - It is a standing wave of two opposite sixth-root phases, sin(πE/3) with E = Σ(−1)^x.
   - **Every level (proved).** On every level-k Sierpinski gasket it reproduces itself exactly, with a factor ≡ ±1 (mod 3) that never
     vanishes.
     - Each copy splits into its two phases. The gasket's two edges from the first corner lock the phases at the three corners
       together, and flipping every phase is odd. So the phases always recombine into the same wave.
     - Modulo 3 the gasket collapses to the law, because the only surviving edge sets are the empty set and the two edges.
   - **So a knot builds space of every dimension below 2.** The towers of these gaskets are exactly self-similar, of dimension
     log(k(k+1)/2)/log k → 2, and their corner relation is the knot (K1–K3).
     - The plane stays out of reach. It is these gaskets plus the triangles joining them, and the joining triangles break exactness
       (the previous entries).
   - **What else reproduces itself (census to level 12).** 68 of the 1,168 signed laws do. Only two mechanisms persist across
     infinitely many levels:
     - the standing wave, with its rotations, relabelings and a twisted variant of period 4 in k;
     - linear parity, at powers of 2.
     The other 42 are single-level coincidences.
   - **Reading.** Harmonies in a precise form. The knot is the point of a family of standing waves where the all-equal states
     cancel exactly, and the space it builds is the space on which its two phases never mix.
   - **Next (taken).** The standing wave in every dimension (next entry).

   **2026-10-29: a knot that builds space in every dimension** (`SIMPLEX-GASKETS-20261029-001`).
   - **Every dimension, every level (proved).** The standing wave (−1)^(x₀) sin(θE)/sin θ reproduces itself exactly on the
     Sierpinski simplex of every dimension d and every level k.
     - The proof is the gasket's: the d edges from the first corner lock the phases of all d + 1 corners, and flipping every phase is
       odd.
     - Its factor is a whole-number polynomial in 2 cos θ, equal to 2^N at θ = 0, where the wave becomes the linear law
       1 + Σ s₀sᵢ. That law's only surviving edge sets are the d edges of the big simplex.
     - So the factor vanishes at finitely many angles per level, and never at an angle jπ/q with q a power of an odd prime.
   - **Knots in every dimension.**
     - The Legendre member (−1)^(x₀)(E | 3) is an exact knot in every dimension d ≥ 2.
     - In odd dimension every member is a knot, because the balanced weight E = 0 always cancels. In three dimensions that knot is
       "not exactly two ones".
     - These knots build towers whose dimension log C(k+d−1, d)/log k rises towards d.
   - **The second wave.** The cosine wave (−1)^(x₀) cos(θE) keeps its form only when the number of simplices is odd; otherwise it
     turns into the sine wave. Under refinement the sine wave is the attractor. The period-4 family of the plane was the cosine wave.
   - **What persists (censuses in three and four dimensions).** The knots exact at every level computed are exactly standing waves.
     - Everything else follows an arithmetic of k: odd levels, powers of 2, or an odd number of simplices.
     - The rest are single-level coincidences.
     - The wave fails at θ = π/4 at exactly the even levels, where the edges between the other corners frustrate its phases.
   - **Reading.**
     - The gluing is the Sierpinski substitution, chosen rather than derived. What the law supplies is a fixed point of that
       substitution at every scale and in every dimension.
     - These spaces are finitely ramified and the laws signed, so the three-manifold result (bits see only parity) stands.
     - What blocks knots is coupling through shared faces, not dimension.
   - **Next (taken).** Interference in three dimensions (next entry).

   **2026-10-29: interference in three dimensions** (`SIGNED-3D-20261029-001`).
   - **The census (exhaustive).** Every signed law with one bit per edge, weights in {−1, 0, 1}, unchanged by the moves of ordered
     triangulations, has one of the seven counting supports.
     - Up to sign changes it is a counting law or the twisted Dijkgraaf–Witten law (−1)^(x₀₁x₁₂x₂₃) on a parity support, or a mix of these.
     - So interference never makes a new relation in three dimensions. It adds a phase on the parity relation.
   - **The twist needs the order.** No twisted law is symmetric under the tetrahedron's vertex permutations. Signs alone add nothing,
     just as order alone added nothing to counting. The phase lives on the path 0–1–2–3 that the order draws through each tetrahedron.
   - **What it sees: one bit.**
     - Summed over a manifold, the phase is a Gauss sum of the cubic form a ↦ a³ on mod-2 classes. That form is linear, so the sum
       cancels completely or not at all.
     - It tells whether the linking form gives 1/2 on an element of order 2. That is not a function of homology: it separates RP³ # RP³ from
       the quaternion space, which counting cannot.
   - **Reading: three regimes.**
     - On genuine planar space, laws stay parity, even with signs.
     - On finitely ramified space, standing-wave knots build space in every dimension.
     - On three-manifolds, parity plus one phase bit.
     - Coupling through shared faces keeps relations affine, and interference then reads global phases rather than building structure.
       The owner's "incommensurables cancelling" appears literally: classes with a³ = 1 cancel those with a³ = 0, and the cancellation is
       the information.
   - **Next (taken).** Uniqueness of the standing wave (next entry).

   **2026-10-29: is the harmony forced?** (`WAVE-UNIQUENESS-20261029-001`).
   - **Among knots, yes.**
     - In the plane, a three-place law that reproduces itself on the gaskets of levels 2 to 5 is a standing wave, or a law that couples
       nothing: a product, a law forcing two corners equal, or one of two frozen laws.
     - The only knot that does so is signed not-all-equal, with its rotations (proved for every symmetric law; for general laws outside
       one degenerate stratum).
   - **It takes four levels to tell.**
     - Two levels admit a whole curve of impostors, real ones included. Three levels admit 16 complex ones. Each fails at the next level.
     - Self-similarity across two scales is not self-similarity.
   - **Implication laws.**
     - General laws add one new family: two-phase laws whose support is a one-way implication ("a = 1 forces c = 1").
     - They reproduce themselves at every level, but they compose like a chain. A change of phase can only sweep through the whole
       gasket, so their factor is that of a path.
     - They are never knots.
   - **Reading.**
     - Building every scale while coupling three places requires interference: a cancelling pair of phases.
     - Everything else that builds every scale couples at most two places at a time.
   - **Next (taken).** Which spaces the harmony builds (next entry).

   **2026-10-30: which spaces the harmony builds** (`SPACE-SELECTION-20261030-001`).
   - **The law selects by cancellation.**
     - A gluing of triangles carries the wave exactly when six signed sums over phase assignments cancel.
     - Contacts that lock phases make them cancel locally; mirror pairs of assignments and, from six triangles, genuine identities make
       them cancel globally.
     - The conjectured local criterion (phase locking plus an odd parity) is refuted: the parity is always odd, and locking is not needed.
   - **It selects many spaces and no dimension.**
     - Up to five triangles the knot reproduces itself on 8,584 gluings, 3,082 of them at its own angle only.
     - Exact gluings compose. Bubbles hung from a single vertex keep exactness, so the growth exponents of the towers are unbounded.
     - Other angles (π/4, π/6, π/8, and angles that are not rational multiples of π) have their own gluings, so the knot is not singled
       out by the spaces it admits.
   - **Interference is what builds small spaces.** Without signs a not-all-equal law needs at least seven triangles (sharp). With signs it
     needs three, the Sierpinski triangle.
   - **The two/three boundary, inside the gluing.**
     - A contact of two triangles locks their phases, an equality.
     - At the knot angle, a contact of three triangles with an odd number of base corners is itself a not-all-equal knot on their phases.
     - A gluing made only of such knots is the unsigned problem on its dual. The knot then needs seven triangles, and the seven-triangle
       spaces (corner triangles distinct) are exactly the Fano plane read as a gluing. On it both the signed and the plain knot reproduce
       themselves.
   - **Reading.**
     - The law does not draw a space by itself.
     - Where the gluing is made of the knot's own contacts, the smallest space is forced: the Fano plane, which reads the same with
       triangles and contacts exchanged. (Only the smallest. Larger such spaces exist; see the next entry.)
   - **Correction.** The epic's first proof stated the seven-triangle bound with a wrong reduction and missed the one-triangle case. A later
     ticket in the same epic corrected and sharpened it.
   - **Next (taken).** The knot's three-fold spaces (next entry). Its premise, that the Fano plane is the only one, turned out to be false.

   **2026-10-30: the knot's three-fold spaces** (`THREEFOLD-SPACES-20261030-001`).
   - **The premise was wrong.** The Fano plane is only the smallest three-fold space. Splicing one Fano plane into another gives a
     13-triangle space, and Fano planes splice together without limit (7, 13, 19, … triangles). A random probe had missed these rare cases.
   - **What the knot asks of a three-fold gluing.**
     - At the knot angle, a gluing whose contacts all join three triangles is a space for the knot exactly when two conditions hold for its
       dual arrangement of triples: it cannot be 2-coloured as a whole, and it can once the corner line is removed.
     - That is the classical even-cycle problem: its sign-nonsingular matrices are those of 2-in 2-out digraphs with no even cycle.
     - Its one indecomposable exception is the Fano plane (McCuaig).
   - **Up to 13 triangles (exhaustive).** Only the Fano plane and its splice.
   - **Beyond: odd cycles of Fano planes.**
     - A Fano plane minus a line forces its three free points to one colour, so a line that meets it twice says "different".
     - A cycle of an odd number of such blocks cannot be 2-coloured. That gives spaces with 21, 35, … triangles.
     - One sign flip turns an even cycle odd: a 14-point twisted system found by SAT, and from two of them a 27-triangle space.
   - **Reading.**
     - The knot builds its own space from the two classical obstructions to 2-colouring: the Fano plane (three places) and the odd cycle
       (two places).
     - That is the two/three boundary as a grammar, with a sign deciding the parity.
   - **Also.** Gluings of phase locks and phase knots alone do not exist, because counting base corners forbids every lock. So the planned
     "mixed" class is empty.
   - **Correction inside the epic.** A first reduction claimed that Fano compositions were everything. The 14-point twisted system showed
     the gap: cutting a space into pieces can put a point twice on a line. The reduction was corrected.
   - **Next (taken).** The grammar of three-fold spaces (next entry). The approved form turned out to be false: odd cycles and splices are
     not the only glue.

   **2026-10-30: the grammar of three-fold spaces** (`THREEFOLD-GRAMMAR-20261030-001`).
   - **The approved grammar was too small.** Fano blocks, splices and odd cycles do not make every space. Twisted 14-point pieces set on
     three skew edges of a cube give a 43-triangle space whose glue is the cube itself.
   - **Atoms and glue (proved).**
     - Cut a three-fold space along its tight three-edge cuts. Every end piece is a Fano plane with one element removed, so every space
       other than the Fano plane holds at least two Fano atoms.
     - Everything between the atoms is glue: doubled squares, planar pieces, and pieces glued from planar ones along 4-cycles
       (Robertson–Seymour–Thomas). Non-planar glue does occur, first seen in a 35-triangle space.
     - Every planar cubic graph serves as glue. Each of its faces needs a fixed parity of sign flips (Kasteleyn's condition). Twisted pieces
       at the attachments supply them, like a flux through each face.
   - **Sizes up to 22 triangles (exhaustive through cores).**
     - Spaces have exactly 7, 13, 19, 21 or 22 triangles: eight in all, each a small core dressed with Fano atoms, six triangles at a time.
     - None has 8–12, 14–18 or 20 triangles.
   - **Duality is free.** Exchanging triangles and contacts maps the knot's spaces to its spaces.
   - **Reading.**
     - The knot's own space is two-dimensional glue studded with three-place atoms. The glue's planarity is forced by the law's sign
       parity, not drawn.
     - The two/three boundary again: the atoms are the three-place obstruction, and the glue is a two-place parity structure.
   - **Corrections inside the epic.** Two checks predicted wrongly and were fixed by computation:
     - A Fano block can sit on a twisted point; that is exactly the 14-point twisted piece.
     - The glue can be non-planar, when it is assembled from planar pieces.
   - **Next (taken).** The surfaces of three-fold spaces (next entry). The answer was yes.

   **2026-10-30: the surfaces of three-fold spaces** (`THREEFOLD-SURFACES-20261030-001`).
   - **Each Fano atom is a handle (proved).** Take the graph of a three-fold space's triangles and contacts and ask for the least genus of a
     closed orientable surface that carries it. When the glue is planar, that genus is exactly the number of Fano atoms. The glue adds no
     handles.
   - **Why the atoms keep their handles.**
     - In general, splicing two non-planar pieces along three edges can lose a handle (two K₃,₃ give genus 1, not 2).
     - A Fano atom cannot lose its handle: with one vertex deleted it is still not planar. A piece with that property always adds its
       full genus.
     - The proof follows the faces across the three cut edges. A face that turns back across a cut edge costs a handle.
   - **The surface is canonical.**
     - Its genus is fixed by the space, not chosen.
     - Every minimal map of it is a connected sum of one map, the Heawood map of the Fano plane, with flat maps of the glue. One copy
       comes per atom, each with a handedness.
     - Spaces have finitely many minimal maps up to symmetry: 1, 2, then 3 to 6 at 19 triangles.
   - **The Fano space is the seven-vertex torus.**
     - Its minimal map is unique up to symmetry and chiral.
     - Read dually, it is the seven-vertex triangulation of the torus. The 14 triangles are the knot's seven triangles and seven contacts
       (the corner line counted as one), coloured like a checkerboard.
   - **Confirmed by exact computation** up to 180 vertices: the twisted cube has genus 6, the truncated-octahedron glue 12. A non-planar
     glue piece (three cubes glued along a square) adds one handle of its own.
   - **Reading.**
     - This is the first place in the program where the knot's own space fixes a canonical topological object: a closed surface whose
       handles are its three-place atoms.
     - It is the topology of an incidence graph, not a native contact topology or a metric.
     - The two/three boundary, once more: the three-place atom becomes a handle, and the two-place glue stays flat.
   - **Next (taken).** The knot's amplitude on its surface (next entry). The answer was yes, and the glue's factor is Tutte's tree count.

   **2026-10-30: the knot's amplitude on its spaces** (`THREEFOLD-AMPLITUDE-20261030-001`).
   - **Five per handle, a tree count per flat piece (proved).** The factor by which a gadget of the knot reproduces the knot is, up to sign,
     a product over the pieces of its space:
     - 5 for each Fano atom, that is, for each handle of its surface;
     - 1 for each doubled square;
     - for each planar piece of glue, Tutte's tree-trinity number: the spanning trees of the map it is cut from (for glue cut from a map),
       Kálmán's hypertrees in general;
     - the sign is the parity of the number of triangles.
   - **Why.** The factor counts the 2-colourings of the space with one contact opened.
     - Across each tight three-edge cut the count splits exactly.
     - On a planar piece, the knot's sign parities (Kasteleyn's condition) turn colourings into Tutte's matchings of faces to contacts.
   - **One number for the whole space (proved).** The count is the same whichever contact is opened, and the same again when triangles and
     contacts are exchanged. This holds for every three-place system that cannot be 2-coloured, not only for the knot's spaces.
     - The proof counts one weighted sum in two orders. With an Ising weight at half the knot's angle on the graph of triangles and
       contacts, summing out either side gives the not-all-equal rule on the other.
     - So each contact's count is the average of its triangles' counts and vice versa, and a connected space forces one value.
   - **Confirmed by exact computation.**
     - All 2,652 cores up to 10 points.
     - The law at every corner of every space up to 22 triangles.
     - Glue cut from 13 maps up to the dodecahedron: 5,184,000 spanning trees, at all 60 contacts.
   - **Non-planar glue depends on its gluing.** Three prisms glued along a square have one amplitude, but it changes with how the square is
     matched (13 or 14 for prisms of sizes 2, 3, 3). The pieces' own amplitudes do not determine it.
   - **Reading.**
     - The knot's own number measures what it builds: handles count 5 each, and flat glue counts trees.
     - The number belongs to the whole space. No contact is privileged, and reading from triangles or from contacts agrees. That is the
       relational point.
     - The two-way count is a three-place phenomenon: with four places, summing out cannot give not-all-equal.
   - **Next (taken).** The knot's spin structure (next entry). The answer was yes, and the spin structure is even on every handle.

   **2026-10-30: the knot's spin structure** (`THREEFOLD-SPIN-20261030-001`).
   - **The knot's signs are Kasteleyn (proved for planar glue).** On every least-genus surface of a three-fold space, every face has length
     2 mod 4. So the knot's own signs satisfy Kasteleyn's condition, the extra structure a surface needs before its perfect matchings define
     spin structures.
     - The proof follows faces across each tight three-edge cut. Exactly three faces cross, each made of one face from each side, so the
       parities add.
     - Non-planar glue (three prisms glued along a square) behaves the same on all its surfaces (computed).
   - **The spin structures are even, handle by handle (proved).** Each perfect matching gives a spin structure, and all have Arf invariant 0.
     - On the Fano torus the 24 matchings induce exactly the three even spin structures, eight each, never the odd one.
     - A space with h atoms gets exactly 3^h of them: the spin structures even on every handle (9 of the 10 even ones at genus 2).
     - Of the four sign classes on the Fano torus, only the knot's counts its 24 matchings exactly. The other three give 8.
   - **Evenness belongs to the least-genus surface.** On larger surfaces carrying the same signs, odd spin structures appear: about 1–2% of
     them, and only from genus 3 on.
   - **Reading.**
     - The law equips the space it builds. Its own signs are exactly a spin structure's raw material on its own surface, and what they give
       is even on every handle.
     - An even spin surface bounds a spin 3-manifold, so each knot surface with its spin structure is such a boundary.
     - The two/three boundary, once more: the three-place atom carries a handle and its even spin structures; the two-place glue carries
       neither.
   - **Next (taken).** The knot's amplitude as a spin sum (next entry). The answer was no.

   **2026-10-30: the knot's amplitude as a spin sum** (`THREEFOLD-SPINSUM-20261030-001`).
   - **No: every spin structure contributes (proved, with exact values).** The knot's counts split exactly over the spin structures of its
     surface.
     - On the Fano torus, with one contact opened, the three even spin structures give 16 each and the odd one 28. Twice the amplitude is
       (3 · 16 − 28)/2 = 10.
     - The even ones alone would give 12, not 5, and the odd one does not cancel.
     - With two handles the spin pieces do not split handle by handle, though the amplitude is exactly 5 · 5. "Five per handle" belongs to
       the whole count, not to spin pieces.
   - **The contradiction is a balance.**
     - In the closed Fano space the odd spin structure's piece, 24, exactly cancels the three even ones, 8 each. That cancellation is the
       knot's non-colourability.
     - Opening a contact unbalances it by twice the amplitude.
   - **The knot's signs are the only contradictory ones.** Of all the sign patterns Kasteleyn's condition allows on its surface, the knot's
     is the only one that cannot be 2-coloured. Every twist of it can.
   - **Reading.**
     - The amplitude and the contradiction are properties of the whole relation, not of local pieces.
     - The spin line is closed. What the three-fold line found in the end is linear-algebraic: the knot's spaces sit exactly on Seymour's
       bound (as many contacts as triangles), where impossibility is a determinant condition.
   - **Next (taken).** Where counting near-critical instances becomes hard (next entry). The easy side holds.

   **2026-10-30: counting on Seymour's bound** (`SEYMOUR-COUNT-20261030-001`).
   - **Counting is easy on every space the knot builds (proved, and implemented).** The colourings of a three-fold space with one contact
     removed are counted exactly in polynomial time, with no signs.
     - Planar glue is one determinant (Berman's, counting Tutte's matchings).
     - Non-planar glue is built by gluing three pieces along a square (Robertson–Seymour–Thomas). It is cut back into planar pieces, and each
       piece is one weighted determinant: two determinants per piece.
     - Spaces of 1720 vertices are counted in seconds, where generic elimination would need tables over 30 variables.
   - **The knot reappears one level up (proved).** Each piece's colourings lean to one of the square's two corners, in proportions (α, β).
     - The glued amplitude is ρ₁ρ₂ρ₃ − α₁α₂α₃ − β₁β₂β₃: the knot's not-all-equal rule, applied to the pieces' leanings.
     - Pieces glued further down act only as weights on these two numbers. A piece tells the rest of the space nothing else.
   - **Reading.**
     - The knot's spaces are where counting stays easy. Their impossibility is a determinant condition, and so is their count with one
       contact removed.
     - The surface never has to be seen. The Kasteleyn route on the surface would need 4^genus Pfaffians; the pieces need none.
     - Provenance: planar counting of this kind is classical (Valiant), and the gluing structure is Robertson–Seymour–Thomas's. The counting
       result on every space was found in no source.
     - The hard side was not attempted.
   - **Next (taken).** Counting one twist off the bound (next entry). Counting stays easy unless twists branch.

   **2026-10-30: counting one twist off the bound** (`TWIST-COUNT-20261030-001`).
   - **The knot's own signs act the same way at every junction (proved).** Where three pieces meet at a square, a piece carrying the knot's
     own signs scales the "planarity defect" of the opposite piece (its matchgate identity) by α² + αβ + β².
     - That number is |α + β e^{iπ/3}|², the knot's own angle applied to the piece's two leanings.
     - So the piece behaves like the square's edges put back: everything stays planar in the counting sense.
   - **Counting stays easy well past one twist (proved).** Change the signs anywhere: counting stays polynomial unless some square has
     twisted pieces on all three of its sides. One twist, or twists along any path of pieces, are all easy.
   - **Where twists branch, a junction can cross wires, but only softly.**
     - Proved: a not-all-equal line forbids only one pattern, so the square's lines can never force two of the host's points into a fixed
       relation without pinning them. No junction is a sharp crossing; the square's points can carry a wire, its lines cannot.
     - Computed exactly: twisted truncated-octahedron pieces do let both wires through at once, with a small weight (−192 against 40000),
       outside the planar class. The signs cancel the turning paths exactly and let the crossing path through.
   - **Reading.**
     - Easy counting is a property of the knot's sign class at each junction, not of the graph alone.
     - Interference again does the work: signs cancel what the not-all-equal rule cannot forbid.
     - If the soft crossing can be sharpened, counting becomes hard exactly where twists branch.
   - **Next (taken).** Soft crossings to hardness (next entry). Counting is #P-hard where twists branch.

   **2026-10-31: soft crossings to hardness** (`SOFT-CROSS-20261031-001`).
   - **The soft crossing sharpens (proved).** Repeat the junction of two twisted pieces k times, with plumbing whose spare legs are closed by
     a *dead cap* (a cube minus one edge, whose count is 3 whatever it touches).
     - The four ways of crossing then grow at four rates, 810000, 7506, −22518 and −432 per step, built from the primes 5, 139 and 3.
     - Because the rates are incommensurable, a few counts separate them, and interpolation recovers an exact crossing.
     - So every cubic counting problem, on any graph, can be read off from the knot's own graphs, with their signs twisted.
   - **Counting is hard where twists branch (proved).** Counting colourings of the knot's graphs (Pfaffian graphs, where perfect matchings
     still count in polynomial time) is #P-hard once the signs are twisted.
     - In the hard instances every junction has twisted pieces on all three of its sides.
     - The source problem, counting 2-colourings of 3-regular 3-uniform hypergraphs, is hard by Fan and Cai (2020). It was found during the
       literature check and is replayed here with merge paths and dead caps, not claimed.
     - The whole chain runs end to end: two small formulas are counted exactly through 44 certified Pfaffian instances.
   - **Reading.**
     - The boundary is two-sided on the knot's own graphs. The knot's own signs count by determinants. Twists that run along a path stay
       easy. Twists that branch make counting universal, and so hard.
     - Two again against three: two twisted sides at a square pass through as a similitude of the knot's angle; three twisted sides make a
       crossing.
     - The hardness is interference. Signs cancel the turning paths, and incommensurable growth rates separate the crossing states, while
       the graph stays Pfaffian throughout.
   - **Next (taken).** Counting on the knot's graphs without signs (next entry). Plain systems are hard too, and twisted by default.

   **2026-10-31: counting the knot's graphs without signs** (`PLAIN-COUNT-20261031-001`).
   - **A sign is a path in disguise (proved).** An unsigned long path, read by interpolation over its length at the value −1, acts as a
     negation.
     - So counting the 2-colourings of plain triple systems (3-regular 3-uniform hypergraphs) whose incidence graphs are Pfaffian is
       #P-hard. No supplied signs are needed.
     - K₃,₃ is counted end to end from 100 plain instances, the largest of 18504 vertices.
   - **Squares are twists (proved).** A cubic plane must have at least six square faces (Euler), and at most five can touch a given one. On a
     square the knot's signs need an odd number of negations, and plain signs have none.
     - So every plain planar piece is twisted, and in a plain non-planar brace the twists branch at every square.
   - **The knot's atom is the exception (proved; likely known).** The Fano plane's incidence graph has no squares at all; its shortest
     cycles are hexagons, which plain signs allow. It is the only plain brace without twists, and the only plain brace that cannot be
     2-coloured.
   - **Reading.**
     - In the plain world twisting is the default, and the knot's atom is the one place where it is absent.
     - Two against three again: one plain page is a planar matchgate, while two plain pages meeting a host at a square always leave the
       matchgate class (2500 of 2500 pairs).
     - Provenance: Euler, Kasteleyn and the nice-cycle condition are classical, and the Fano uniqueness is probably implied by
       Robertson–Seymour–Thomas. Hardness on Pfaffian incidence graphs and the always-twisted pages were found in no source.
   - **Next (taken).** Counting on plain braces (next entry). They are hard to count, too.

   **2026-10-31: counting on plain braces** (`PLAIN-BRACE-20261031-001`).
   - **A plain crossing exists after all (proved).** One junction of two plain cubes is never a crossing. A ladder of them, with rungs
     instead of caps, is: its transfer is a matrix power (NW)^k, and the crossing is its k = 0 term, brought out by interpolation.
     - The ladder's four rates are a unit of Q(√365) and the two Eisenstein primes above 13. The odd part, x² + 7x + 13, is an Eisenstein
       norm form, like the knot's own similitude multiplier α² + αβ + β². That is an observation, not a claim.
     - K₃,₃ is counted from plain braces of 20 to 104 vertices.
   - **Plain Pfaffian braces are hard to count (proved).** Weave a hard instance into a planar frame, one vertex per face, and replace every
     crossing by such a ladder. Every instance is then a brace (cyclically 4-edge-connected) and Pfaffian, with no signs at all.
   - **Reading.**
     - Neither connectivity nor Pfaffian-ness protects counting.
     - The plain picture is complete in the worst case: planar pieces are easy, two plain pieces at a square are twisted and soft, and a
       ladder of such squares crosses wires exactly. The knot's atom, the Fano plane, is the one plain brace without twists, and with
       planarity the polynomial case found.
     - Provenance: the source hardness is Fan and Cai's, planar tractability Valiant's, and the brace structure Robertson, Seymour and
       Thomas's. The plain crossing inside braces and the weaving and cube junction lemmas were found in no source.
   - **Next (taken).** A note on the counting arc (next entry).

   **2026-10-31: the counting note** (`COUNT-NOTE-20261031-001`).
   - **The arc is written up.** One self-contained 10-page note states the five results in standard vocabulary:
     - counting is polynomial on every space the knot builds;
     - it stays polynomial along unbranched twists;
     - it is #P-hard under signs, without signs, and on braces.
   - **How it was checked.**
     - A replay reruns the eleven cited checks in a temporary copy, and all agree.
     - A separately written script recomputes the headline numbers, among them the soft crossing, the cube ladder's
       (x² − 19x − 1)(x² + 7x + 13) and the K₃,₃ counts.
     - Every number quoted in the note is tied to its evidence.
   - **What it does not change.** It adds no new theorem, and nothing has been sent. Sharing it, or asking an expert to review it, is the
     owner's decision.
   - **Next (taken).** A bounded direction scan back toward native emergence (next entry).

   **2026-10-31: back toward native emergence, a scan** (`NEXT-DIRECTION-SCAN-20261031-001`).
   - **Do the knot's signs favour its own law? Yes, on the evidence so far (computed).**
     - Colouring counts are a three-body Ising model, and the knot's law, not-all-equal, is one coupling on its line.
     - On single pages, the knot's signs keep the count planar (free-fermion) at every coupling.
     - Once two pieces meet at a square inside a larger tree, they keep it planar only at the knot's own coupling and at the trivially easy
       ones. The factors shared by every tested case are exactly those couplings (5 of 6 cases, with one exception).
     - This is not an artifact of the chosen basis.
   - **Does a descent toward fewer colourings find the knot's signs? Only on Fano spaces (computed).** Every space with 4-cycles has traps.
     The descent is imposed, so this is weak.
   - **Is one line short of Seymour's bound a new regime? No (proved).** It is #P-hard even on connected, sparse systems. Only the knot's
     part is easy.
   - **Reading.**
     - On the knot's spaces, the signs and the law fit each other, and only each other.
     - This is a selection with nothing imposed but the coupling: the space's signs choose the knot's law.
     - Provenance: planar Ising and matchgates are classical, and the source hardness is Fan and Cai's. A singled-out coupling on Pfaffian
       spaces was found in no source.
     - *Corrected on 2026-10-31 by the next entry.* The shared couplings also include a point at infinity, the dimer coupling. So the
       knot's law is one of two singled-out laws, not the only one.
   - **Next (taken).** A coupling dichotomy in the knot's class (next entry).

   **2026-10-31: the knot's coupling** (`KNOT-COUPLING-20261031-001`).
   - **Counting on the knot's spaces is easy at exactly two laws besides the trivial ones (proved).**
     - Weigh each monochromatic line by λ. On the systems that cannot be 2-coloured, counting is easy at λ = 0 (the knot's law), at
       λ = −3, and at the trivially easy couplings.
     - It is #P-hard at every other coupling, real or complex.
     - At the knot's law every count is 0. At λ = −3 every line uses exactly two of its points, so the count is the number of perfect
       matchings of the incidence graph: a determinant on the knot's spaces, a permanent in general. Call this the dimer law.
   - **Why the knot's law is special (proved).**
     - Take a knot's space, remove one incidence, and use it to replace an edge. At the knot's law this atom is exactly a negation, so it
       cannot change the coupling.
     - At every other coupling the atom shifts the coupling, and shifted couplings can imitate any twist. That makes counting as hard as on
       general systems.
     - The complex couplings are closed by torsion points on a curve (Beukers and Smyth).
   - **With one line deleted** the picture is the same, except that the dimer law is left open.
   - **Correction.** The scan's "only the knot's law" missed the dimer law, a point at infinity.
   - **Reading.**
     - The knot's spaces select their own law natively, and with it one partner. Both are faces of one fact: the incidence matrix is
       sign-nonsingular.
     - Both easy laws are cancellations: a count that vanishes, and a determinant.
     - Provenance: the tools are classical (gadgets, interpolation, Seymour, Robertson–Seymour–Thomas, Kasteleyn, Beukers–Smyth). No
       dichotomy restricted to these spaces was found.
   - **Next (taken).** A bounded scan of mutual selection (next entry).

   **2026-10-31: mutual selection** (`MUTUAL-SELECTION-20261031-001`).
   - **Only the knot has it (among the symmetric three-place laws).**
     - Mutual selection means two things: the systems where a law fails can be recognised, and they make the law easy to count in return.
     - On plain systems, the knot is the only knot that can fail at all. Every other knot allows a constant colouring.
     - With signs, parity fails recognisably but makes nothing new easy; the clauses never fail.
       - *Corrected on 2026-10-31 (`PARITY-CORRECTION-20261031-001`, last entry of this question).* The conclusion stands, but the reason
         given was wrong. The scan said parity's whole weighted family is easy. In fact it is #P-hard except at six couplings.
         Parity's failures make nothing easy because a failure can be grafted into any system.
     - The Fibonacci laws (the no-lone topological knots) do fail. But deciding them is NP-complete (proved by a checked reduction), so
       their failures cannot be recognised unless NP = coNP.
   - **Why: the knot has no preferred value.**
     - It is the only three-place knot that is unchanged when every colour flips. So it can never pin a value: from relations alone it
       cannot make a constant.
     - The Fibonacci law prefers its vacuum. A five-line piece of it pins a point; one more line with that point copies a variable; copies
       give unlimited fan-out; and fan-out makes the law hard.
     - Small pieces of the knot reach only three relations: nothing, everything, and the knot itself. Small Fibonacci pieces reach
       fifteen.
   - **Arity.** On regular systems the knot's law can fail only at three places: every k-regular k-uniform system is 2-colourable for
     k ≥ 4 (Alon–Bregman, Thomassen).
   - **Reading.**
     - "Everything is relational" picks out the knot. It is the one three-place law that never fixes a value, and three is the one arity at
       which such a law can fail.
     - Laws that prefer a value manufacture constants out of relations, and that is where hardness enters.
     - Provenance: the decision facts are classical (Schaefer, Tovey, Gonzalez, Thomassen). The pinning gadget, the rigidity census and
       the reading are ours.
   - **Next (taken).** Pinning across all three-place knots (next entry).

   **2026-10-31: pinning** (`PINNING-20261031-001`).
   - **There are only five three-place knots (proved).**
     - Up to flipping and reordering places, every three-place knot is one of five: parity, the Fibonacci law, not-all-equal,
       x ∨ (y ≠ z) and the clause.
     - Only not-all-equal can fail on plain systems. Only it has no preferred value.
   - **A law that can pin a value is as hard on cubic systems as anywhere (proved).**
     - A pinned point turns one line into an equality, so a variable can be copied without limit.
     - One small skeleton pins every knot that can pin: four points with three lines among them, and two tails.
     - So the Fibonacci law and the asymmetric x ∨ (y ≠ z) are NP-complete to decide. The clause cannot pin: it never fails (Tovey).
   - **The knot is the only three-place law with mutual selection (proved, unless NP-complete problems are polynomial).**
     - Its failures (the Pfaffian signings) can be recognised, and they make its own count and the dimer count easy.
     - On plain systems this holds unconditionally.
     - Checked directly: on all 1.38 million signings of small systems, the knot fails exactly when the signed determinant counts the
       perfect matchings.
   - **Reading.**
     - The knot is singled out natively, by having no preferred value.
     - Every other three-place law either never fails, is affine, or can build a value out of relations alone and become hard.
     - Provenance: Schaefer, Tovey, Seymour, Robertson–Seymour–Thomas. The pinning theorem is close to Dalmau and Ford (2003); the census,
       the uniqueness statement and the shared skeleton were found in no source.
   - **Next (taken, after the parity correction below).** Value-free laws on four places (2/3). Is three the only arity with a mutually
     selecting law?
     - Not-all-equal on four places never fails on 4-regular systems (Thomassen).
     - Other four-place laws with no preferred value, such as not-exactly-two, are open.
     - Alternatives (2/3 each): the knot's pieces at every size; a short note on native selection.

   **2026-10-31: parity's weighted family, a correction** (`PARITY-CORRECTION-20261031-001`).
   - **What was wrong.**
     - The mutual-selection scan claimed that parity's whole weighted family is easy on every system. It is not.
     - Changing basis turns each line's weight into a simple equality, but it also turns each point's equality into a parity check. The
       count becomes a weight count over a code, not a sum over two states.
     - A peer session found the error, citing Fan and Cai (2020, Theorem 2.2).
   - **Parity's weighted family is hard except at six couplings (proved).**
     - Weigh each line that misses its parity by λ. Counting is easy only at λ = 0, 1, −1, i, −i and ∞, and #P-hard at every other
       coupling, real or complex.
     - The reason is native. Replace each line by three lines through two new points. Parity's weighting on the new system is the
       knot's weighting on the old one, at λ + 1/λ − 1. In the knot's even form, its variable is the square of parity's.
   - **Parity's failures make nothing easy (proved).**
     - Where parity fails, a small piece carries the proof of failure, and the piece survives being grafted into any system.
     - So the systems where parity fails contain every hard instance. Two counts on such systems recover any count.
   - **What survives.**
     - Parity's decision and plain count are easy (linear algebra), as before.
     - The knot is still the only three-place law with mutual selection, under both readings.
     - The knot's coupling, the counting note and the pinning results are unaffected.
     - Seventeen dependent statements are marked in the record. Closed records stay as they were.
   - **Reading.**
     - Failures select a law back only when they are global. The knot's failures constrain the whole space: a system fails exactly when
       its signs are Pfaffian. Parity's failures are local.
     - In the owner's terms: the error transformed one side of a two-sided relation. A change of basis acts on every incidence at once.
     - Provenance: Fan–Cai for positive λ, Cai–Fan–Liu for rational λ. The complex case for this family follows from the knot's coupling
       dichotomy and was found in no source checked.
   - **Next (taken).** Value-free laws on four places, with two guards: never infer an easy family from a one-sided transform, and
     test whether failures are local (next entry).

   **2026-10-31: value-free laws on four places** (`FOUR-PLACE-20261031-001`).
   - **At four places, having no preferred value is common (proved).**
     - There are 30 four-place knots that are unchanged when every colour flips, in four kinds: parity, not-exactly-two, a twelve-state
       kind, and not-all-equal.
     - None of them can pin a value.
   - **The four-place knot's law never fails (proved).**
     - With any signs, not-all-equal on k places never fails on systems where every point is on k lines, for every k ≥ 4.
     - The reason is Thomassen's theorem on even cycles. A failure would need a sign-nonsingular pattern, and a digraph whose points all
       have in- and out-degree at least three always has an even cycle.
     - At three places the degree is two, such digraphs can avoid even cycles, and the failures are exactly the knot's Pfaffian spaces.
   - **The other value-free four-place laws build equality (proved).**
     - Small pieces of five points force two points equal without any constant.
     - That makes not-exactly-two and the twelve-state kind as hard as satisfiability on 4-regular systems. Parity stays easy to count.
   - **So no value-free four-place law has mutual selection (proved, unless NP-complete problems are polynomial).**
   - **Reading.**
     - Mutual selection needs a law that is rigid and still fails. Rigid laws stop failing exactly at Thomassen's threshold, so three is
       the only arity where both hold.
     - The two/three boundary reappears one level up: degree two can avoid even cycles, degree three cannot.
     - Provenance: Thomassen (1992), Seymour (1974), Schaefer (1978). The signed form, the census, the link pieces and the four-place
       statement were found in no source checked.
   - **Next (all three taken: the owner asked for all three).**
     - a note on native selection;
     - four-place laws that prefer a value (next entry);
     - composition of the knot's selected spaces toward native networks.

   **2026-11-01: four-place laws that prefer a value** (`FOUR-PREFER-20261101-001`).
   - **There are twenty kinds of four-place knot (proved).**
     - A four-place relation is a knot exactly when the states it forbids never differ in just one place, i.e. they form an independent
       set of the 4-cube.
     - That gives 742 relations in twenty kinds, sixteen of which prefer a value.
   - **Every kind that can fail can copy (proved).**
     - A core of three points on four lines turns nine different kinds into the value-free twelve-state kind, and that kind builds
       equality.
     - So ten kinds that prefer a value are as hard as satisfiability on 4-regular systems, and their failures cannot be recognised
       unless NP-complete problems are polynomial.
   - **The kinds that never fail are weak.**
     - The clause never fails (Tovey). Not-all-equal never fails (Thomassen).
     - Five more kinds, which forbid only two or three states, never failed in any search, but this is not proved.
   - **So no four-place law has mutual selection, apart from five weak kinds whose failures, if any, were never seen (proved, unless
     NP-complete problems are polynomial).**
   - **Reading.**
     - At three places the knot can hide a distinction without being able to copy one. At four places, any law that can fail can also
       copy.
     - Three stays the only arity found with a law that fails and stays rigid. This now holds for every law, not just laws without a
       preferred value.
     - Provenance: Schaefer, Tovey, Seymour, Thomassen. The twenty-kind census and the three-point lift were found in no source checked.
   - **Next (taken).** Composition of the knot's spaces, then the note.

   **2026-11-01: composition of the knot's spaces** (`KNOT-COMPOSE-20261101-001`).
   - **The parts of a knot's space meet as a knot against a hub (proved).**
     - Cut a knot's space along three incidences. One side always ends in three points and the other in three open line slots.
     - The line side behaves exactly as the knot itself (not-all-equal) on its three slots, and the point side exactly as one point (an
       equality hub). The two fit together as a line through a point.
       - *Corrected on 2026-11-01 (`NATIVE-PATHS-20261101-001`, two entries below).* "Exactly" holds only up to signs. In spaces with
         cycles of Fano blocks, the point side forces its three points into one fixed pattern or its complement, for example two equal
         and one opposite. That is an equality hub once one colour is read exchanged, and the line side is the knot read the same way.
   - **Knot meeting knot fails only for parity (proved).**
     - A side that behaves as a knot allows at least half of all patterns.
     - Two such sides can exclude each other only if each is exactly half of all patterns, and an exact half with full projections is
       a parity coset.
     - So every failing composition of the knot's spaces passes through a hub, and the only hub-free failing composition is parity's.
       - *Corrected on 2026-11-01 (`NATIVE-PATHS-20261101-001`).* Not every one. A knot's space with a cycle of Fano blocks can be cut
         along two incidences, and then one side is an equality and the other a negation, with no hub. That two-place parity is exactly
         the hub-free failure predicted here. Across three or more channels, knot never meets knot.
   - **Knot and hub are two sides of one structure.** Swapping points and lines turns a knot's space into a knot's space and exchanges
     the knot side and the hub side of every cut.
   - **Reading.**
     - Knots relate through shared points. A direct knot-to-knot relation, with nothing between, exists only for parity, the law that
       hides one full bit. This matches every earlier result in which only parity survived hub-free composition.
     - Against the native-network gate, the knot's spaces form a native network of knots joined by network hubs, which the owner put in
       scope on 2026-10-29. They do not form a hub-free contact network.
     - Provenance: the splice calculus and the point lemma are our earlier epics, on Lovász–Plummer and Robertson–Seymour–Thomas. The
       hub reading was found in no source checked.
   - **Next (taken).** The note on native selection. Later: native paths through network hubs (2/3).

   **2026-11-01: a note on native selection** (`SELECTION-NOTE-20261101-001`).
   - **The arc in one place.** A five-page note gathers the results of this question since the coupling dichotomy:
     - the knot's spaces select its law;
     - the knot is the only three-place law whose failures can be recognised while its count is hard;
     - parity's failures are recognisable but local (with the corrected analysis recorded);
     - three places stay special at four;
     - the knot's spaces compose only through hubs.
       - *Corrected on 2026-11-01 (`NATIVE-PATHS-20261101-001`).* Across two-incidence cuts they compose by two-place parity, without
         a hub. The note needs an erratum before it is shared.
   - **Checked again.** Every one of the sixteen proofs it cites was rerun from scratch and reproduced its result exactly. Nine headline
     claims were recomputed by separately written code.
   - **Status.** Not externally reviewed and not sent. Sharing it is the owner's decision.
   - **Next (taken).** Native paths and separation through network hubs, the step from first emergence toward composed topology (2/3).
     A side question: whether five weak four-place laws can ever fail (1/3).

   **2026-11-01: native paths in the knot's spaces** (`NATIVE-PATHS-20261101-001`).
   - **Two kinds of meeting (proved).**
     - **Two incidences.** Cut a knot's space along two incidences where that separates it, as in every odd cycle of Fano blocks and in
       the twisted cube. One side behaves as a wire (equality), the other as a negation: two-place parity, with no hub.
     - **Three incidences.** One side forces its three points into one pattern or its complement, and the other side allows the six other
       patterns: a knot against a hub, up to signs.
     - **A correction.** This corrects the composition entry: the knot's spaces do not compose only through hubs.
   - **The routes are fixed by the space (proved; laminarity computed on ten spaces).**
     - Every three-incidence cut is either a genuine splice or a two-incidence cut with one point or line moved across.
     - Genuine splices never cross. So the parts, and the routes between them, are determined by the space itself; no observer chooses
       them.
   - **A route carries one bit at most (proved).**
     - **Through a chain of Fano blocks.** A route remembers only whether its length is even or odd. Two blocks of an odd cycle are
       joined by two routes of opposite parity, and that disagreement is exactly why the space fails.
     - **Through a hub.** A route remembers nothing of what lies beyond: the far side acts as one point or one line, whatever it
       contains.
     - **Separation.** Cutting both routes separates two blocks. Cutting one leaves the other route's parity.
     - **Length.** Counting the hidden witnesses gives 5 per block and 5^m for a chain of m blocks. So length appears only as a count,
       not as a relation.
   - **Knot meets knot only pairwise (proved).**
     - Twist some incidences, so that each reads its point's colour exchanged. A knot's space keeps failing exactly when the twisted set
       is a cut of its incidence graph.
     - So two parts can both behave as knots toward each other only across two incidences, as two-place parity, and never across three or
       more.
   - **Reading.**
     - **Fixed, but not native paths.** Routes between the parts of a knot's space are fixed by the space. Each is two-place parity or
       passes a hub, and neither is a contact. In these spaces the ladder from first emergence stops at hubs.
     - **The 2-versus-3 boundary, seen from composition.** Three-place emergence stays inside the parts. Everything joining the parts is
       pairwise or a hub.
     - **Hubs are where the knot selects.** A system in which every distinction lies in at most two knots never fails (Seymour's bound).
     - **Provenance.** Pfaffian signings, their uniqueness up to switching, and the cactus of two-edge cuts are classical. The
       two-interface theorem with signs, and knot meeting knot only pairwise, were found in no source checked.
   - **Pending the owner.**
     - The note needs an erratum before it is shared.
     - The composition record should be marked superseded, text kept, as was done once before at the owner's request.
   - **Next (taken, together with counted length).** A full pivot to selection versus composition: does any law both select its spaces
     and compose natively?
     - **First test.** The five weak four-place laws, checked for cycle-like composition (2/3).
     - **Alternatives.** The note's erratum and reissue (1/3); counted length as a measure (1/3).

   **2026-11-01: selection versus composition, and counted length** (`SELECT-COUNT-20261101-001`).
   - **The weak four-place laws are not the bridge (proved).**
     - Each of the five laws that might still select at four places contains a knot with a forcing place, where one value allows
       everything.
     - Two copies sharing that place leave everything else free once it is forgotten, so their knots do not compose like cycles.
   - **Selection and composition exclude each other (proved).**
     - On two values, a law with a knot can compose its knots like cycles only if it is linear (affine).
     - A linear law's count is easy, so it cannot select. The knot selects, parity composes, and no law with a knot does both.
     - A law without knots, such as signed two-clauses, can select, but only below three places.
   - **Counted length is a measure (proved).**
     - On a knot's space, count the ways each side of a cut can be arranged, given what its channels show.
     - The count is the same for every allowed pattern, and the two sides' counts multiply to the whole.
     - So the logarithm of the count, counted length, adds up over the parts: log 5 for every Fano block (one handle), plus the
       logarithm of the glue's spanning-tree number (log 2 in the twisted cube).
   - **Counting sees what relations hide (proved).**
     - **Along a chain of m blocks.** The relation remembers only whether m is even, but the count is 5^m.
     - **Across a hub.** The relation sees one point, but the count sees everything behind it.
     - **In rings of blocks from different spaces.** The relation (whether the number of blocks is odd) and the count (the product of
       what each block hides) vary independently.
   - **Reading.**
     - **Two layers.** Relations carry emergence and decide failure, with one bit per route. Counts carry magnitude: how much each part
       hides.
     - **Canonical weights.** Counted length is fixed by the law and the space, and unchanged when points and lines swap. It supplies the
       canonical weights that earlier route values had to choose.
     - **Not a native distance.** The routes it measures are not native paths, so it is a measure, not a native distance. Admitting it
       as a native magnitude would be a change of doctrine.
     - **Provenance.** Our circuit-composition theorem, mutual selection and amplitude results; Post, Schaefer and Valiant. The
       forcing-place hubs, the exclusion statement, factorization across two-incidence cuts, and the rings were found in no source
       checked.
   - **Next (taken).** Values beyond two: a law on three or four values that is Mal'tsev, composes like cycles, and has a hard count
     would both select and compose (2/3).
     - **Alternatives.** Whether the weak four-place laws ever fail (1/3); the note's erratum (1/3).

   **2026-11-01: selection and composition beyond two values** (`BEYOND-TWO-20261101-001`).
   - **The known composing laws count easily (proved).** The laws known to compose like cycles are cosets of groups. Every fibre of a
     coset has one size, so they are easy to count and none selects.
   - **A hidden multiplicity makes counting hard (proved).**
     - Double one value of a law, so that two copies stand for one value. The relations see nothing new: the same systems fail and the
       same variable sets are circuits, so the law still composes like cycles. But every count now weights the doubled value twice,
       and counting becomes #P-complete.
     - Every Mal'tsev law on three values composes like cycles: all 531,441 Mal'tsev operations have at most one nontrivial
       congruence.
     - So blurred parity (three values) and blurred Z3 (four values) compose like cycles, fail recognisably and count hard. Selection,
       as first defined, and composition coexist from three values on. The two-value exclusion is exactly two-valued.
   - **Where laws fail, and whether globally (proved; all 60 cubic substrates up to 8 points).**
     - **The knot** fails exactly on Pfaffian substrates (8 of 60), and every failure is global.
     - **Parity** fails exactly where the number of perfect matchings is even (38), and never globally, because each distinction sits
       in three lines and three is odd.
     - **Z3** fails everywhere, and globally exactly at Z3-corank 1 (24), because three is zero mod 3.
   - **A bridge at four values, but rigid (proved).**
     - On its corank-1 substrates, blurred Z3 selects in the knot's full sense: its failures are global and recognisable, it is easy to
       count once a line is removed, and hard in general. It also composes like cycles.
     - But removing a line leaves one degree of freedom and only ties: its selected spaces are pairwise.
     - The knot's selected spaces can keep a knot after a line is removed: every line of the Fano plane, and four other Pfaffian
       substrates.
   - **Reading.**
     - **Three kinds of cancellation.** Parity cannot fail globally on cubic spaces. Z3 fails globally when the whole space cancels.
       The knot fails globally when nothing cancels: all its perfect matchings agree in sign.
     - **What sets the knot apart.** Counting can be made hard without touching relations. The knot's real distinction is relational:
       it selects spaces that keep emergence inside, which the linear bridge cannot.
     - **Provenance.** Our circuit theorem, the census, Pfaffian signings and Seymour's bound; Dyer–Richerby, Bulatov and Bulatov–Dalmau.
       The blurring lemma, the three-value enumeration, the bridges, the three-law census and the rigidity contrast were found in no
       source checked.
   - **Next (taken).** Does composing like cycles force rigid selection?
     - **The test.** Look at the remaining cycle-composing laws (cosets of Z4, S3, D_p; the simple Mal'tsev laws on three values).
       Check for global failures that keep a knot (2/3).
     - **What it would settle.** A theorem either way: composition and emergence-keeping selection exclude each other everywhere, or
       some law does both.

   **2026-11-01: does composing like cycles force rigid selection?** (`RIGID-SELECTION-20261101-001`).
   - **Where selection is rigid (proved).**
     - **Fields.** Over a field, a system that fails globally has exactly one dependency among its lines. Removing any line leaves a
       single line of solutions, so only ties remain, at every number of places.
     - **Blurring.** It keeps this rigidity.
     - **S3 and D_p.** Their knots on full ranges are blurred parity.
     - **Simple three-value laws.** Those that are not affine have no knots on full ranges.
   - **Rigidity fails beyond fields (proved).**
     - **Signed Z4, four places.** It fails globally on a 6-point substrate (each line omits the two ends of one hexagon edge) and
       keeps knots after any line is removed.
     - **Signed Z4, three places.** It needs 9 points: all 73 cubic substrates up to 8 points, under every signing, leave only ties.
     - **Unit-weighted laws.** Z8, Z9, Z25 and Z27 do the same on many small substrates.
   - **Selection spends the top layer (proved).**
     - **The theorem.** Over Z_(p^k), and over any finite chain ring, a system that fails globally leaves, after any removal, solutions
       whose top digits form a single line. That is exactly what a field would leave.
     - **Hence fields are rigid.** Over a field the top digit is everything.
     - **What survives otherwise.** A kept knot has at most one variable taking all values, and hides at most k − 1 of its k digits.
     - **Attained.** The bound is reached over Z4, Z8, Z16, Z9, Z27 and Z25.
   - **A law that composes, selects and keeps emergence (proved).**
     - **The law.** Blurred signed Z4 on five values (0 doubled).
     - **What it does.** It composes like cycles, fails globally and recognisably, counts #P-complete, and keeps knots inside its
       selected spaces, below its top layer.
   - **Two values (proved).** A two-valued law with knots that composes like cycles is affine, hence rigid. The knot keeps knots
     inside its selected spaces. So at two values the two exclude each other.
   - **Reading.**
     - **A failure in a carry.** Z4's global failure is solvable mod 2 and fails only mod 4: a cancellation that closes only once
       the carries are counted.
     - **What it spends and keeps.** It spends the top digit, and its kept knots relate lower digits to the one shared top line.
       For example, the 2's digits of two variables and the units digit of a third have even parity.
     - **The knot has one layer.** Its failures need no cancellation, and it keeps three-place emergence in its only layer. Of all the
       laws met so far, it alone keeps top-layer emergence inside the spaces it selects.
     - **Precision.** The census lists 60 incidence graphs, which give 73 substrates when read both ways. The earlier census statements
       hold under both readings.
     - **Provenance.** Smith form over chain rings, Goursat, the skew-free property and Dyer–Richerby are classical. The closest
       literature found studies unsolvable modular systems only as an optimisation problem (Min-r-Lin). The rigidity statements, the
       examples, the top-layer theorem and the five-value bridge were found in no source checked.
   - **Next (taken).** Does every law that composes like cycles keep its top layer rigid (2/3)?
     - **The top layer.** It is the image in the algebra's top quotient, by its unique maximal congruence. It cannot be each range's
       own quotient: Z4's kept knot is parity among leading digits.
     - **First test.** Non-abelian groups that compose like cycles, up to order 24, and the non-simple three-value laws.
     - **If true.** The knot stands apart at every number of values.

   **2026-11-02: does every law that composes like cycles keep its top layer rigid?** (`TOP-LAYER-20261102-001`).
   - **Three values (exhaustive at three places).** Every law on three values that composes like cycles is rigid. Each of its knots
     reads one bit from each variable.
   - **Groups (proved).**
     - **Which groups.** A group's law composes like cycles exactly when every subgroup has a unique maximal normal subgroup. Up to
       order 60: the cyclic p-groups, the dihedral groups of order 2p^k, and six others such as C5⋊C4 and C7⋊C3.
     - **Their top.** It is always rigid.
     - **Depth.** They keep knots only below the top, through a cyclic subgroup of order p², as in C5⋊C4 and D9.
   - **Depth is needed (proved).**
     - **Why.** In every law with a Mal'tsev polymorphism, a knot reads only the abelian part of its variables.
     - **The theorem.** If every abelian section has a single layer, every global failure is rigid. This covers every law on three
       values and every non-affine law on four.
     - **Not sufficient.** Two layers are needed but not enough: the triangular module over F2 is rigid on every regular substrate.
   - **The question as phrased is false.**
     - **The example.** A simple Mal'tsev law on five values (Z4 plus one value) composes like cycles. Its top is everything.
     - **Why it fails.** The Z4 examples inside it keep knots in that top.
   - **The right layer (proved for sections from one chain ring).**
     - **Declared domains.** Give each point one domain, which every knot on it uses.
     - **The theorem.** After any removal, the leading digits of the variables, each read in its own section, form at most one line.
     - **Consequence.** Every kept knot has at most one varying leading digit. This answers last entry's objection: with declared
       domains, each point's own section is the right layer.
     - **Two different rings** joined through tops: checked, not proved.
   - **Correction.** The group theorem holds for systems with declared domains. Lines that confine a point further are open, though
     every such case met was rigid.
   - **Reading.**
     - **Laws that compose like cycles.** Such a law keeps emergence inside a selected space only through depth: an abelian section
       with two layers, where a digit carries into the next, so at least four values. Even then, only below that section's top.
     - **The knot.** It keeps three-place emergence on two values, in its only layer, with no carry. This is the sense in which the
       knot stands apart.
     - **Selection leaves a hub.** When the knot's space loses a line, the rest forces that line all-equal, so its three points are tied.
       In the Fano plane the four points off it become a new four-place knot.
     - **Provenance.** Commutator theory, Z-groups and Smith forms are classical. The depth theorem, the group list read through our
       circuit theorem, the counterexample and the layer-wise statement were found in no source checked.
   - **Next (taken).** What selection leaves, and how pieces glue (2/3).
     - **The lead.** The knot's spaces are Fano atoms glued along lines, and a removed line is exactly a hub of tied points.
     - **The question.** Does gluing selected spaces along these leftover hubs build the knot's spaces natively, keeping emergence
       across the glue?

   **2026-11-02: what selection leaves, and how pieces glue** (`HUB-GLUE-20261102-001`).
   - **Selection leaves the gluing interface (proved).**
     - **The hub.** Removing a line from a knot's space ties its three points. That is exactly the point side of the 3-edge cuts along
       which knot spaces are glued.
     - **The gluing.** Splicing two knot spaces at a line and a point gives a knot space, for one switching class of signs, and every
       simple cut is such a splice.
     - **With the earlier grammar.** Every knot space is built this way from Fano atoms and planar glue.
   - **A held hub composes like cycles (proved).**
     - **When it holds.** If the removed line is not on a cut's hub side, the hub keeps its three points tied: one bit.
     - **The composition.** The knots crossing the cut are then exactly the eliminations (K1 ∪ K2) minus the hub of one knot through
       the hub on each side, ties included: a 2-sum.
     - **The reason** is the knot's symmetry under flipping every value. An OR, which lacks it, fails.
   - **An opened hub creates (proved, with computation).**
     - **When it opens.** If the removed line lies on the hub's own side, the interface becomes whatever the closed piece allows. It is
       one pair (the hub re-ties and still composes), two pairs (one hub point released) or all three (the hub becomes a knot on its own
       three points).
     - **Composition fails.** Then composition breaks down. In the 13-point Fano splice, 72 crossing knots arise that no chain of
       eliminations produces, against none through held hubs.
   - **Reading.**
     - **Where the exclusion is lifted.** Selection and cycle-like composition exclude each other as properties of a whole law, but
       inside the knot's own spaces they meet exactly at the hubs selection leaves.
     - **One removal decides.** The removal that selects a space also decides, cut by cut, whether the glue composes (held) or creates
       (opened).
     - **Still hubs.** The hubs are equality fan-out, so this composes emergence, not contacts: no native path or distance is claimed.
     - **Provenance.** Tight cuts of Pfaffian graphs, sign-nonsingularity and the matroid 2-sum are classical. The relational 2-sum
       through a complement-symmetric hub and the classification of opened hubs were found in no source checked.
   - **Next (taken).** Emergence along the splice tree (2/3).
     - **The question.** In a space of several pieces, are the knots kept after any removal iterated 2-sums along the held cuts, with
       new emergence only at the cuts opened on the way to the removed line?

   **2026-11-02: emergence along the tree of cuts** (`SPLICE-TREE-20261102-001`).
   - **A removal orients the tree (proved).**
     - **Held and opened.** In a space glued from several pieces, removing a line holds every cut that points toward it and opens every
       cut that points away.
     - **Locality.** Beyond a held cut nothing depends on which line was removed.
   - **Held cuts compose exactly (proved).**
     - **The theorem.** The knots crossing only held cuts are exactly the iterated 2-sums, through held hubs, of knots crossing no cut.
     - **So** new emergence lives only across opened cuts.
   - **Opened cuts form one zone (computation, 96 chains of three and four pieces).**
     - **Carried and joint.** New knots of one opened cut are carried across the others, and two or three opened cuts create knots
       jointly.
     - **Hubs decide nothing.** Each of three hub-level rules fails to say where knots are created:
       - touching hubs;
       - a hub point on the removed line;
       - the removed line's own hub.
     - **Regularities.** Every jointly created knot has three or four points, and chains of the smallest knot space (K4^(3)) create
       nothing.
   - **Reading.**
     - **Composing and creating.** After a removal, the knot's kept emergence has two sides: a tree of exact compositions on the held
       side, and one zone of creation on the opened side.
     - **A lead toward topology (scouting, not a claim).**
       - **The scout.** Single splices of the census spaces. New knots appeared only when the opened hub had become a knot and the
         removed line's side was non-planar: 100 of 160 such removals, against none of the 560 with a planar side.
       - **What it suggests.** Each Fano atom is a handle, so creation may live in the handles while planar glue only composes.
     - **Still hubs.** Hubs are equality fan-out, so no native path or distance is claimed.
     - **Provenance.** Iterated 2-sums along a tree decomposition are standard for matroids. The relational version, the orientation
       reading and the classification of opened-cut interaction are new here; no literature search was run for them.
   - **Next (taken).** Emergence needs a handle (3/3).
     - **The question.** At an opened cut, does new emergence need both a knot on the hub and a non-planar removed side, so that planar
       glue only composes?

   **2026-11-02: emergence needs a handle** (`HANDLE-EMERGENCE-20261102-001`).
   - **Planar glue creates nothing, as far as tested.**
     - **Beyond the census.** 24 planar knot spaces were spliced into other knot spaces (grown from the cube, prisms, the truncated
       octahedron; 10 to 14 points). No removal on the planar side created a new knot across the opened cut: 1612 removals and
       432,867 crossing knots.
     - **The census.** Planar sides create nothing there either. The Fano plane and one other non-planar space create.
   - **What a handle creates (computation, with two small lemmas).**
     - **A three-point knot through the hub.** Every created knot joins a point of the removed line's hub, one near point and one far
       point.
     - **How it works.** The hub and the near point fix all three gluing ports at once, and the far point answers to that whole
       pattern. No single port carries the constraint across, so no elimination produces it.
     - **In the Fano plane.** Every removed line meets the gluing line, so the hub sits on a port.
   - **On a plane space the knot fails by counting faces (proved).**
     - **The odd point.** Each line has one point that disagrees with the other two. Say the line skips the corner opposite that
       point.
     - **The face condition.** With Kasteleyn's signs, every face must hold an odd number of skipped corners.
     - **The count.** A plane space with n lines has n + 2 faces (Euler's formula). So the n skips can never cover them, and the
       knot fails.
     - **After a removal.** Every face holds exactly one skipped corner, so the solutions are exactly the perfect matchings of the
       remaining lines to the faces off the removed line.
     - **Planar interfaces.** A line meeting the removed line loses a face to it. So the configuration that creates in the Fano plane
       never forms on a plane side.
   - **A handle leaves slack (proved count, computed example).**
     - **The count.** Each handle removes two faces and adds two global (homology) parities.
     - **In the Fano plane.** On its torus embeddings, 14 assignments per removal pass the face test, and the homology parities keep
       only 5 of them. That is where creation lives.
   - **Reading.** Selection on a plane space is a matching of lines to faces, so its emergence only composes. A handle trades two faces
     for two global parities, and those parities let new knots appear. Hubs remain equality fan-out, so no native path or distance is
     claimed.
   - **Open.** A proof that a planar side never creates.
   - **Provenance.**
     - **Classical.** Kasteleyn's face condition, and Moret's theorem that planar not-all-equal 3-SAT is polynomial.
     - **New here, as stated.** The skip model and its genus count. A bounded search found no statement of them.
   - **Next (taken).** Planar glue only composes (2/3).
     - **The question.** Prove from the matching picture that a plane side never creates. Then test whether a handle creates exactly
       what its homology parities add.

   **2026-11-02: planar glue only composes** (`PLANAR-COMPOSE-20261102-001`).
   - **On a plane side the hub reaches the gluing ports (proved in part).**
     - **The tie class (proved).** After a removal, every point on the removed line's faces is tied to its hub. In the matching picture,
       states differ by flipping the points inside closed curves, and those curves never enter the removed line's faces.
     - **The route (proved).** Suppose the hub and a near point fix the gluing pattern. If the hub is also tied to one of the pattern's
       two other ports, or knotted with both in the right way, then every candidate new knot is built from one-sided knots, one port at
       a time, whatever is glued on the far side.
     - **The access lemma (checked, not proved).** One of those two always holds on a plane side: all 9020 cases on 42 plane spaces of up
       to 20 points (8020 as first recorded; corrected by `PLANAR-THEOREM-20261102-001`). On the Fano plane and census 58 it fails in every case: the Fano plane's hub sits on the very port it pins as odd.
   - **Cutting a handle open is not canonical (computation).**
     - **Dropping one homology parity** removes about nine tenths of a handle's new knots.
     - **Dropping both** removes all of them for some cut positions and not for others, even within one homology class.
     - **Local point flips** remove none.
     - **So** homology carries most of a handle's creation, but "a handle creates exactly what its homology parities add" fails as stated.
   - **Reading.**
     - **A plane side.** Its removed line always leaves a hub that can reach the ports one at a time. A handle breaks that: its hub lands
       on the port it must not use.
     - **Still hubs.** Hubs remain equality fan-out, so no native path or distance is claimed.
     - **Provenance.** The plane matching structure is classical (Kasteleyn). The tie-class, route and access statements and the
       handle-cut measurements are new here.
   - **Open.**
     - The access lemma in general.
     - That every new knot is a pinned three-point knot (true in all 2820 found).
     - Four-pattern removals.
   - **Next (taken).** Finish the planar theorem (2/3).
     - **The plan.** Prove the access lemma from the height picture, then the premise from the matching picture.
     - **The alternative.** Selection as a dimer model on large plane spaces.

   **2026-11-02: the planar theorem, by discrete convexity** (`PLANAR-THEOREM-20261102-001`).
   - **The access lemma is proved.**
     - **Heights.** After a line is removed from a plane space, each solution is a matching of lines to faces. Comparing it with a fixed
       matching across every corner gives each point an integer height, zero on the removed line's faces. A point's value relative to
       the hub is the parity of its height.
     - **Convexity.** The heights are exactly the solutions of a system of difference constraints. So they are closed under rounding the
       midpoint of any two, up or down.
     - **The gluing line.** Its three states form a staircase in the heights of its ports.
     - **The argument.** Suppose the hub and a near point fix the gluing pattern without reaching the ports. Then rounding midpoints
       between the pinned state and the other states would force the near point's height to two different values. So the hub is tied to
       a usable port, or knotted with the other two ports one step away.
   - **The hub is not special (proved).** Re-centring the heights at any point keeps them convex. So on a plane side, every pair of
     points that fixes the gluing pattern reaches the ports, and every candidate new knot of that kind is built one port at a time,
     whatever is glued on the far side.
   - **Knots across one port are 2-sums (proved, any space).** A crossing knot whose constraint passes through a single port is two
     one-sided knots eliminated through that port, or a one-sided knot in disguise.
   - **Handles (computation).**
     - **The census.** On the Fano plane and census 58, no pair of non-port points that fixes the pattern reaches the ports.
     - **Larger spaces.** The Fano plane was spliced into plane spaces, giving 16 points with one handle. There, access depends on
       where the gluing line sits, not on where the removed line is. In the plane part every case has it (6,056). In the Fano part
       almost none do (992 of 12,368).
   - **What is left.**
     - **Generated on every splice tested.** One-sided knots and pinned three-point knots generate all 58,875 crossing knots, and every
       new knot is a pinned three-point knot through the hub.
     - **Unproved.** The remaining 12,102 crossing knots reduce on every splice, but no proof that they always do is known.
   - **Reading.**
     - **Why a plane side composes.** Its selections have convex heights, so a pin can always be taken apart one port at a time.
     - **What a handle does.** It breaks the heights where the selection is read.
     - **Doctrine.** Hubs remain equality fan-out, and the heights are a proof device, not a distance.
   - **Provenance.** Heights of plane matchings (Thurston, Propp) and L-convex sets (Murota) are classical. New here: the access proof,
     its extension to every pinning, the 2-sum lemma and the handle-locality computation.
   - **Next (taken).** Handles seen from a gluing line (2/3).
     - **The plan.** First prove that access at a gluing line depends only on a planar neighbourhood of that line. Then test, with one
       and two Fano atoms, whether creation happens exactly at gluing lines on handles.
     - **The alternatives.** Finish the reduction of the remaining crossing knots (1/3). Selection as a dimer model (2/3).

   **2026-11-03: handles seen from a gluing line** (`HANDLE-LOCALITY-20261103-001`).
   - **Access is local (proved).**
     - **A wider setting.** Some plane systems have as many lines as odd faces. Each such system behaves like a plane knot space minus a
       line: its solutions are matchings of lines to odd faces, with convex heights. So every pinning there reaches the ports.
     - **Splices.** Seen from across a 3-edge cut, an untouched side looks exactly like the point or line it replaced. So a plane piece
       seen through a cut is always such a system.
     - **So** two points of a plane piece that fix a gluing line's pattern always reach its ports, whatever is removed elsewhere.
   - **Where new knots appear (computation, with one lemma).** The spaces are one or two Fano planes in plane glue.
     - **A cut carrying one bit screens (proved).** Creation at a plane gluing line is then creation on a plane space.
     - **No handle at either line: nothing is created** (896 cases).
     - **A handle attached at a line** never creates outside itself.
     - **A handle attached at a point, opened by the removal,** creates at plane gluing lines around it, out to distance 5 on the spaces
       tested. It talks to the plane glue through the point's three copies, which carry two bits.
   - **The earlier premise fails.**
     - **Near an opened handle.** Many new knots are not pinned. Two handle points force the gluing line into two adjacent patterns, and
       a far point rules them out.
     - **Inside handles.** Four-point new knots appear.
   - **Reading.**
     - **An intact handle is invisible.** It looks like the point or line it replaced.
     - **An opened handle is read twice:** where it sits, and in a halo that the plane glue carries by forced matchings.
     - **Doctrine.** Distances here only describe where creation was found. Hubs remain equality fan-out.
   - **Provenance.** Matching heights and convexity are classical (Kasteleyn, Thurston, Propp, Murota). New here: plane matching systems
     as a common setting, the interface and screening lemmas, and the creation map.
   - **Next (taken).** The halo as dimer forcing (2/3).
     - **The plan.** Characterize, by forcing in the matching picture of the point split, which plane gluing lines an opened handle
       reaches. Prove it, and measure the reach on large plane pieces.
     - **The alternatives.** Explain the screened line-attached handle; finish the planar reduction lemma; classify the new knot types
       (1/3 each).

   **2026-11-03: the halo of an opened handle** (`HALO-FORCING-20261103-001`).
   - **Which lines an opened handle reaches (route lemma proved, converse checked).**
     - **The rule.** A new knot is two points in the handle and one far point. It appears exactly when the two handle points squeeze the
       gluing line into one or two patterns, and no route rebuilds the knot.
     - **A route.** One of the line's points separates the knot, or a pair of the line's points carries a two-step elimination. The far
       point decides which pairs are usable, so some far sides see farther than others.
     - **The evidence.** The rule held for every case on spaces with a Fano plane attached to plane pieces of up to 14 points: 1,500 new
       knots, and no routed knot new.
   - **Heights compute it (proved).** Which port patterns and line patterns occur together is a parity question about heights. Shortest
     paths answer it exactly, so the halo can be computed on plane pieces of hundreds of points.
   - **How far it reaches (computation).**
     - **On a ladder,** all the way: on prisms of up to 80 points, the farthest gluing line still creates.
     - **On a grid,** three steps: on spaces of up to 256 points, nothing farther creates. From distance 7 on, a grid line is exactly
       independent of the handle's point.
   - **Reading.**
     - **The mechanism.** The plane glue carries a handle's influence by forced matchings. A ladder is frozen and passes it on without
       loss; a grid is liquid and forgets it.
     - **So** where native selection can see a handle depends on the rigidity of the plane around it.
     - **Doctrine.** Distances only describe where creation was found. The heights are a proof device. Hubs remain equality fan-out.
   - **Provenance.** Matching heights and the frozen and liquid phases of dimer models are classical (Thurston, Propp, Kenyon, Okounkov,
     Sheffield). New here: the route criterion, the height transfer, and the halo measurements.
   - **Next (taken).** Creation and dimer phases (2/3).
     - **The test.** Build plane pieces where frozen and liquid parts meet. Is the halo exactly the frozen region joined to the handle?
     - **The proofs.** The ladder law and the grid bound.
     - **The alternatives.** The screened line-attached handle; the planar reduction lemma; other and several handles (1/3 each).

   **2026-11-03: creation and dimer phases** (`PHASE-HALO-20261103-001`).
   - **The claiming lemma (proved).** When a handle's point is split open, a port is the odd point of its line exactly when that line
     takes the one skip of the face opposite the port. So every line around that face feels whether the port is odd.
   - **Opposite faces carry the halo (computation).**
     - **The test.** The Fano plane as handle, at 126 attachment points: ladders, thick tubes, a grid, random spaces, and a ladder arm
       spliced onto a grid.
     - **The result.** Every halo line beyond three steps lies on a face opposite the attachment point. In 124 cases the halo is exactly
       those faces' far lines.
     - **So the phase reading is replaced.** The reach is the size of the faces opposite the handle, not a frozen region as such. A
       ladder's opposite face is a whole cycle; a grid's faces have at most three corners.
   - **The handle matters (computation).** Census 58 as handle can also speak through the point's own long face (5 of 24 points). The
     general law is "the faces around the attachment point".
   - **The ladder law (proved, given the route criterion).** A prism is a cyclic chain of consecutive triples. Its transfer matrix repeats
     with period 2, so a far line's transfer depends only on its parity, the same on every prism. The halo runs the full opposite face on
     every prism.
   - **The grid law (certified).** A line with the full transfer is independent of the handle (proved). Every grid line tested at
     distance 9 or more has it, and at 7 or more on the 256-point grid (exact certificates). Height ranges between ports and lines are 0
     at every distance on ladders and grow with distance on grids.
   - **Reading.**
     - **A face is a native long-range constraint.** Exactly one of its lines skips into it, so a handle is seen as far as the faces
       around it extend.
     - **The dimer phase** summarizes face sizes and how rigid the heights are. It is not a separate cause.
     - **Doctrine.** Distances only describe where creation was found. The heights are a proof device. Hubs remain equality fan-out.
   - **Provenance.** Kasteleyn signings, Boolean transfer matrices, matching heights and dimer phases are classical. New here: the
     claiming lemma, the opposite-face law and its dependence on the handle, the chain reduction of the ladder, and the height-range
     measurements.
   - **Next (taken).** Which faces a handle uses (2/3).
     - **The plan.** Classify handles by the faces they speak through, their own or the opposite ones. Explain the Fano plane against
       census 58 through the handle's port relation. Prove the opposite-face law for the handles that obey it.
     - **The alternatives.** The screened line-attached handle; the planar reduction lemma; several interacting handles (1/3 each).

   **2026-11-03: which faces a handle uses** (`FACE-CLAIM-20261103-001`).
   - **What each face reads (proved).** Split the plane at the attachment point. Its three faces there merge into one face that takes a
     single skip, on the arc opposite the port that is odd.
     - **Own arcs.** The arc between two ports is barred exactly when those ports disagree.
     - **Opposite faces.** Whenever two ports agree, the face opposite the third port is claimed by that port's line.
     - **Frozen lines.** A barred face fixes two points of each of its lines.
   - **Claims (proved).** A frozen line can still deviate by claiming its face, at either fixed value.
     - **On an own arc,** a claim comes from one port pattern.
     - **On an opposite face,** it comes from two, which share the other two ports.
   - **The claim rule (one direction proved, the other computed).** An opened handle creates at a frozen line exactly when a pair of its
     points freezes the line and neither point alone excludes either claim. No disagreement appeared against exact creation or the
     pipeline.
   - **Which faces a handle uses (computation).**
     - **The census.** 305 handles from 24 non-planar knot spaces, in every port order on a ladder. Nine signatures occur.
     - **The rule.** The faces are decided by the handle's port relation alone.
     - **The Fano plane.** Each of its single points removes one pattern per other class. That kills every one-pattern claim and never a
       two-pattern one, so it never uses an own arc (proved) and always uses the opposite face.
     - **Census 58** uses its own arc exactly when the bottom port is 0 or 5.
   - **The last law fails (counterexample, exact on a small piece).** Where a ladder arm is spliced onto a grid, a junction point freezes
     the arm's far long face with two-pattern claims, and every handle tested creates there. So the halo is not confined to the faces
     around the point: it lies on frozen lines whose claims survive the handle's single points.
   - **Reading.**
     - **The bit.** A face reads one bit of the handle: whether two of its ports agree.
     - **The plane** carries that bit as far as its frozen structure reaches.
     - **The handle** decides it by how sharply one of its points cuts the port patterns.
     - **The phase reading returns, refined.** The frozen region is the dimer model's frozen region for the ports' boundary condition.
     - **Doctrine.** Distances only describe where creation was found. Hubs remain equality fan-out.
   - **Provenance.** Kasteleyn parities, corner matchings, unit propagation and dimer frozen regions are classical. New here: the arc
     identity, the reading and claim lemmas, the claim rule, the census of handles and the junction counterexample.
   - **Next (taken).** The frozen region by heights, and rigid strips (2/3).
     - **The plan.** Prove that a port pattern freezes exactly the points whose height difference to the ports cannot vary, explain the
       junction as a rigid strip, and test whether long rigid strips through liquid bodies carry the halo.
     - **The alternatives.** The converse of the claim rule as a theorem (2/3); the structure of the nine signatures; the screened
       line-attached handle (1/3 each).

   **2026-11-03: the frozen region by heights, and rigid strips** (`STRIP-RELAY-20261103-001`).
   - **Frozen means fixed height (proved).** The port class fixes the ports' heights, because the merged face's single skip lies on a
     known arc. Heights with fixed port values are closed under rounded midpoints. So a port pattern freezes exactly the points whose
     height difference to the ports cannot vary.
   - **Collapsing untouched sides (proved for the transfer).** Across a 3-edge cut, a side holding neither the handle nor the gluing line
     acts as the vertex it lost. Collapsing it leaves creation unchanged, so the faces-around-the-point law holds again in the collapsed
     space. The last epic's junction was a ring seeing itself as the closed prism.
   - **Pendant rings (proved, given the ladder law).** From the middle point of the ring's removed line, the halo runs along the ring's
     whole far face, for every ring length.
   - **Rigid strips relay (computation, exact on small pieces).**
     - **The relay.** Between two grids, an opened handle in the strip or the far grid creates in the first grid near its cut. It does so
       from every distance along a rigid strip, at the same lines whatever the strip's length.
     - **Liquid screens.** A grid in the strip's place screens it within three steps.
     - **Direction.** The relay enters only a side split at a point there, and a handle leaves only where its grid lost a line. A
       line-attached composite handle is screened.
   - **Reading.**
     - **Native channels.** Rigid strips are native channels for a handle's one-bit reading. Native selection sees a handle at the far
       end of a frozen channel, in a liquid region the handle is not in.
     - **Direction.** The channels are directed, from the side that lost a line to the side that lost a point, the direction of a
       handle's own splice.
     - **Doctrine.** Distances only describe where creation was found. A channel carries a reading, not a metric. Hubs remain equality
       fan-out.
   - **Provenance.** L♮-convexity (Murota) and frozen dimer regions are classical. The interface lemma and the screening of
     line-attached handles are from HANDLE-LOCALITY. New here: the heights lemma, the reduction lemma, the ring law, relays, their
     screening and their direction.
   - **Next (taken).** Relay networks (2/3).
     - **The plan.** Branch and chain rigid strips through small pieces. Test whether one handle's halo reaches several grids, how
       relays from two handles combine where channels meet, and whether directed channels compose into native paths.
     - **The alternatives.** Proofs of the relay's length independence and the composite-handle reading (1/3); the converse of the
       claim rule (2/3).

   **2026-11-04: relay networks** (`RELAY-NET-20261104-001`).
   - **Relays are wires.** After a frozen hop, an opened handle's relay reaches the next cut as an arc signal: two ports fixed and
     disagreeing, the third free.
     - **The arc lemma.** An arc signal freezes exactly the lines with a corner on the own arc between its fixed ports. One direction is
       proved; the other is computed.
     - **Repeaters.** A station passes the signal on exactly when its out-line lies on that arc. Aligned stations repeat it without
       loss, and the relay reaches a grid four cuts away. A misaligned station ends it.
   - **Broadcast, direction, bypasses (computation, exact on small networks).**
     - **Hubs broadcast.** A hub copies a relay into several receivers at once, so one handle is read in several places.
     - **Downstream only.** No relay ever runs upstream.
     - **Bypasses.** Stations whose two cut vertices are adjacent are no barrier.
   - **A withdrawn guess.** "Relays cross at most two cuts" was an artifact of one cut placement.
   - **Reading.**
     - **One bit, directed.** Native selection reads an opened handle through a directed wiring of frozen arcs. Each wire carries one
       bit, whether two ports agree. Wires branch at hubs and stop where alignment fails.
     - **Display.** The claim rule decides where that bit is shown as creation.
     - **Doctrine.** A wire carries a reading, not a metric. A hub is equality fan-out.
   - **Provenance.** Frozen dimer regions and unit propagation are classical. New here: arc signals, the arc lemma, repeaters, broadcast
     and the depth scan.
   - **Next (taken).** A native reading of genus (2/3).
     - **The plan.** With several Fano atoms in plane glue, ask whether the creation map over all removals splits into one halo per atom,
       counting and locating the handles.
     - **The alternatives.** The display rule (1/3); the claim rule's converse (2/3).

   **2026-11-04: a native reading of genus** (`NATIVE-GENUS-20261104-001`).
   - **The creation map splits by atom.** Whether a removal creates at a gluing line depends only on the atoms holding the two lines;
     every other atom acts as the vertex it replaced.
     - **Status.** Proved for atoms attached at a point (interface and screening lemmas). Checked exactly for atoms attached at a line
       (13 designs, 5,130 entries).
     - **So** each removal's halo is its own atom's, and atoms attached at a line have no halo on plane glue.
   - **Native selection counts and locates separated handles (computation fixed in advance).**
     - **The count.** Take a largest set of lines among which nothing creates. The remaining lines fall into one piece per atom, and
       each piece is an atom: 416 of 420 separated spaces with two or three atoms, every placement on two small prisms.
     - **Where it stops.** Atoms that touch merge, and so do three atoms on the 4-point cube, whose glue keeps one line. On the 32
       three-fold spaces up to 22 points, where atoms mostly touch, the count equals the genus in 10. It counts Fano atoms: the one
       trisum handle in the census is invisible to it.
   - **Blocks (exploratory).** Inside a piece, maximal blocks of lines that create at one another equal the genus in 29 of the 32 and
     in all 310 Fano pairs, touching ones included.
     - **They overcount** where two point-attached atoms hang from one Fano atom.
     - **Census 58 breaks into many blocks**, because its lines sharing two points (a doubled square) never create at each other.
   - **Wires do not blur the count.** A rigid strip or a hub lands one atom's halo on another atom's cut in every placement tested
     (exact on a 26-point strip network). The count stays one piece per atom, and each halo stays its atom's: the count reads the
     quiet glue and the lines the glue creates at, which a halo does not change.
   - **Reading.**
     - **Non-planarity is local.** Native selection marks exactly the handles' lines: plane glue never creates, and the glue creates
       at every Fano line.
     - **The brace tree, one level down.** Quiet lines for glue, blocks for atoms, one-way creation for a cut's direction, silence for
       doubled squares: native creation may read the whole decomposition.
     - **Doctrine.** Pieces and blocks describe placements, not distances; no embedding is used.
   - **Provenance.** Genus = number of Fano atoms (THREEFOLD-SURFACES) and tight cuts (Lovász) are known. New here: the splitting lemma,
     the native count, its exhaustive small tests, blocks, and wires against the count.
   - **Next (taken).** A native reading of the brace tree (2/3).
     - **The plan.** Fix a refined block statistic in advance; test whether blocks, one-way creation and silence recover the
       tight-cut decomposition on the census and on fresh trees of atoms; try to prove the block lemma for Fano atoms.
     - **The alternatives.** Proving that plane glue never creates (2/3); the display rule (1/3).

   **2026-11-05: a native reading of the brace tree** (`BRACE-TREE-20261105-001`).
   - **Atoms are blocks.** The Fano plane's creation map is complete: every removal creates at every other line.
     - **Atoms attached at a line.** Such an atom creates among its own lines exactly as the Fano plane does (proved: the rest of the
       space forces the ports constant, and the screening lemma applies).
     - **Atoms attached at a point.** The same is checked on every design.
   - **Cuts are read in their direction.** A receiver's cut lines and the emitter's lines create at each other; its intact lines create
     one way at the emitter's, never the reverse. This held at all 213 cuts between two atoms.
   - **The dictionary.** Where only atoms join two atom lines, their relation is fixed by the tree: 42,090 pairs, none off the rules.
     - **Same atom.** Mutual.
     - **Downstream.** Mutual with a receiver's cut lines, one-way with its intact lines.
     - **Siblings.** Mutual.
     - **Co-receivers.** Their intact lines are silent to each other.
     - **Through plane glue.** The relation can depend on more than the tree.
   - **The source rule counts the genus.** Keep a block of mutual creation when one of its lines is blind to everything the others are
     blind to.
     - **The count.** The rule equals the number of Fano atoms, and the genus, on all 157 spaces without a non-Fano brace. 110 of them are
       fresh: every three-fold class of 23 to 26 points.
     - **The plain block count** fails 32 of them, wherever atoms hang from a common atom.
     - **Later (CHAIN-TRANSFER-20261106-001).** On Fano trees the rule holds up to five atoms and fails at six; twins and footprints
       replace it there.
   - **Refuted along the way.**
     - **Determinism through plane glue.**
     - **Silent glue across an atom.** In one class, a Fano atom relays creation from a plane piece to a doubled square.
   - **Not read.** Handles that are not Fano atoms: census 58 (itself a single brace of another kind) and the trisum brace.
   - **Reading.**
     - **The oriented handle tree, natively.** Native selection reads the handle tree: how many handles, where, and which way each
       touching pair is glued. Touching atoms, where the plain count merged them, are resolved.
     - **Doctrine.** Blocks, directions and silence are relations given by creation; a direction is which side of a cut lost a point,
       not a direction in space.
   - **Provenance.** Tight cuts (Lovász) and genus = Fano atoms (THREEFOLD-SURFACES) are known. New here: the dictionary, native cut
     directions, the source rule and its fresh test.
   - **Next (taken).** A two-bit screening lemma (2/3).
     - **The plan.** Prove that a side attached at a line acts as that line for creation, not just for solutions. That would complete
       the splitting lemma and should give the block lemma for atoms at a point and the one-way rule.
     - **The alternatives.** What native creation sees of non-Fano handles (2/3); the source rule beyond 26 points (1/3).

   **2026-11-05: the two-bit screening lemma** (`TWO-BIT-SCREEN-20261105-001`).
   - **The closure is a bootstrap.** New knots are crossing triples that the rule "four classes with two derived knot triples derive
     all their knot triples" cannot reach from the non-crossing ones (proved equal to the elimination closure).
   - **No loss (proved).** An intact Fano side attached at a line never removes creation.
     - **Off the side.** Its new knots off the side are exactly those of the space with the line restored.
     - **Through the side.** A generated knot through a hidden point has generated port shadows, and no crossing knot meets two hidden
       classes.
     - **Pendant lines.** The same holds for one new point on one new line through two near points.
   - **One statement left.** That the side never adds creation follows from the pendant-line statement: one new point on one new line
     never adds creation.
     - **Evidence.** It held on 117,344 cases, random systems included.
     - **Not proved, and not easy.** It is not local, and it is not a consequence of the knots alone.
   - **One line is the limit.**
     - **Two or three lines create.** A point on two or three new lines through a line's points, such as the ports' majority, creates
       where the space without it does not.
     - **Subcube points never did.** No point whose exclusions are subcubes changed creation.
     - **Knot-space sides.** Every knot-space side tried, including every three-fold space up to 22 points, has only subcube points.
   - **In Fano trees (spaces built from Fano atoms alone).**
     - **Contraction (proved).** Creation in the chain of atoms between two lines implies creation in the whole space.
     - **Blocks (proved).** So every atom is a block of mutual creation.
     - **The touching rule.** The brace dictionary between atoms collapses to one rule: a removal creates at a line of another atom
       exactly when that line touches its atom's cut toward the removal. The removed line's role never matters.
       - **Checked.** On every chain of two (294) and three (576) atoms, and on four-atom paths.
       - **Proved half.** Its creating half holds in every Fano tree at distances one and two.
     - **Still computed.** Non-creation at lines that do not touch, and atoms three or more apart.
   - **Reading.**
     - **Two bits made precise.** A side is screened when everything it hides is one-line information: each hidden Fano point, seen
       alone, hangs on one line through two ports.
     - **The tree, read locally.** A line is seen from a direction exactly when it touches the cut facing that direction. An emitting
       atom presents all its lines to the cut, and a receiving atom only its three cut lines. That is how creation reads a cut's
       direction.
     - **Doctrine.** Hidden points are witnesses quantified away. Quantifying a Fano side's witnesses away loses no emergence; whether
       it adds none is the open statement.
   - **Provenance.** Bootstrap closures and principal matroid extensions are classical analogues, neither found stating these results.
     New here: the tetrahedron form, the no-loss theorem, the pendant reduction and its sharpness, the contraction theorem, and the
     proofs of the block lemma and nearby creations.
   - **Next (taken).** Prove the pendant-line statement (2/3), starting from the computed fact that
     eliminating through the gluing line's points suffices.
     - **The alternative.** The bridge to proof complexity (2/3), still the leading alternative for the next arc.

   **2026-11-06: the pendant-line statement** (`PENDANT-LINE-20261106-001`).
   - **Creation is decided at the gluing line, in two rounds (proved).** The closure reaches exactly the crossing knots whose near and
     far parts meet through the gluing line.
     - **Round one.** A near knot and a far knot sit on the same pair of the line's points.
     - **Round two.** Two round-one knots share a point.
     - **New knots** are the crossing constraints the parts carry together that pass through no pair of the line's points.
     - **Proof.** The closure was reduced to local configurations, and all 348,376,032 were checked.
   - **One new line never adds creation (proved).** A new point on one new line through two points, whatever its signs, leaves creation
     unchanged.
     - **Proof.** From the two-round rule, with all 347,149,320 local configurations checked.
     - **Sharpness.** A point on two or three such lines can create (TWO-BIT-SCREEN), so one line is the exact limit.
   - **Completed.**
     - **The two-bit screening lemma.** An intact Fano side acts as its line for creation, as it does for solutions.
     - **The splitting lemma** for atoms attached at points and at lines.
     - **In Fano trees.** A line creates at another exactly when it does in the chain of their atoms.
     - **The touching rule up to distance two.** A line receives creation from another atom at most two away exactly when it touches
       its atom's cut toward it. So native creation provably keeps each atom whole and reads every cut in its direction.
   - **Reading.**
     - **Where emergence is selected.** Native selection picks out emergence exactly where the parts fail to meet at the gluing line.
     - **"Two bits", made exact.** One line of hidden information is safe and two are not.
     - **Doctrine.** Directions are which side of a cut lost a point, and touching is incidence. No space is assumed.
   - **Provenance.** Reducing a closure to finitely many local configurations is a standard verification route; no statement of these
     results was found.
   - **What is left.** For the source rule to become a theorem, a transfer along chains of four or more atoms. Distance three held on
     the 16 four-atom paths computed.
   - **Next (taken).** A transfer along chains (2/3): prove the touching rule at every distance in Fano trees.
     - **The alternative.** The bridge to proof complexity (2/3).

   **2026-11-06: the touching rule at every distance** (`CHAIN-TRANSFER-20261106-001`).
   - **The touching rule holds at every distance (proved).** In every space built from Fano atoms alone, a line receives creation from a
     removal in another atom exactly when it touches its atom's cut facing the removal, however far away the removal is.
     - **Proof.** A chain of atoms carries only a finite profile from one cut to the next. There are 47 profiles, none new after three
       atoms, and each was checked with every last atom (12,894 verdicts).
     - **What the profiles show.** A removal leaves the ports of every cut beyond it free. So the receiving atom alone decides
       creation.
   - **The source rule fails (proved).**
     - **Where it holds.** It counts the atoms of every Fano tree of at most five atoms.
     - **Where it fails.** At six atoms: a receiver that takes two loaded cuts and emits the line through their points has no source.
       Exact creation maps confirm it.
   - **A short rule reads the tree (proved).**
     - **Atoms.** Lines that create at each other and at the same other lines form one atom.
     - **Cuts.** Atoms that create at a proper subset of an atom's lines lie beyond one of its receiving cuts.
     - **What it reads.** The atoms and the directed tree of every Fano tree whose atoms have at most four cuts.
     - **Not yet through plane glue.** On the census of 23 to 26 points, a glue line can join an atom's class and an atom can split into
       three pairs.
   - **Reading.**
     - **Openness travels; direction is read at the receiver.** A removal opens every cut beyond it. A line feels it only if it touches
       its own atom's cut facing it.
     - **A handle is a set of lines seen together.** Its lines create at each other and are created at by the same lines elsewhere.
     - **The tree is read from its receivers.** Every cut has one receiver, whose lines through the lost point name the cut.
     - **Doctrine.** Twins and footprints are relations among lines. No space is assumed.
   - **Provenance.** Finite-state transfer along bounded interfaces, and Buneman's theorem that splits determine a tree, are classical.
     No statement of these results was found.
   - **What is left.** Plane glue, non-Fano handles, heavily loaded atoms, and other far sides.
   - **Next (taken).** Reading through plane glue (2/3): add plane pieces to the profile automaton and look for
     one rule that reads the genus of every three-fold space.
     - **The alternatives.** Non-Fano handles (1/3); the bridge to proof complexity (2/3).

   **2026-11-06: reading through plane glue** (`GLUE-READ-20261106-001`).
   - **Creation at an atom is decided by its cut (proved).** Whether a removal creates at a line of a Fano atom depends only on the
     patterns the removal's side allows on the atom's cut facing it: three ports' worth.
     - **An emitter.** Its lines receive exactly when the ports may be equal.
     - **A receiver.** A cut line receives exactly when the other two ports are not forced equal. An intact line receives exactly when
       the side tells the ports apart.
     - **Proof.** Every port relation was checked against every deeper relation at once (8,190 cases). The census agrees at all 47,550
       pairs.
   - **What glue does (computed, 191 spaces).**
     - **Through atoms.** The cut is always free, so the touching rule holds.
     - **Through glue.** Glue can exclude a pattern pair or tie two ports, and the touching rule fails exactly there.
     - **Its two disturbances are local.** A doubled-square line through two of an atom's ports joins it. An atom emitting into a plane
       piece splits by its ports, because plane lines see where a removal entered and atom lines do not.
   - **Reading the atoms.**
     - **Where it works.** A two-stage twin rule reads every Fano tree with at most four cuts per atom (proved), every census space and
       57 of 80 random glued spaces.
     - **Where it stops.** In 15 random spaces, lines of atoms meeting one plane piece are indistinguishable by whether creation occurs,
       so no such rule can read them.
     - **What survives.** Which far side creates still separates them.
   - **Reading.**
     - **A cut is an atom's whole window.**
     - **Atoms are blind to depth; plane glue is not.**
     - **Handles on one plane.** Several handles on one plane can look alike to whether creation occurs. Only how it occurs, which far
       side completes it, keeps them apart.
     - **Doctrine.** Cuts, ports and far sides are relations among lines. No space is assumed.
   - **Provenance.** Bounding an OR over local configurations, and invariance under automorphisms, are standard. No statement of these
     results was found.
   - **What is left.**
     - A rule using the far sides.
     - The relation a plane piece presents, derived from its faces.
     - Non-Fano handles.
   - **Next (taken).** Reading with the far sides (2/3): on the 191 saved maps, look for a rule that separates
     atoms meeting one plane piece without splitting atoms.
     - **The alternatives.** Glue relations from faces (1/3); non-Fano handles (1/3).

   **2026-11-06: do handles govern counting hardness?** (`HANDLE-COUNT-20261106-001`).
   - **The genus half is classical.** Counting colourings (with any signs and any weight per monochromatic line) is an even-subgraph sum
     on the incidence graph. On a surface of genus g that takes 4^g determinants (Galluccio–Loebl, Tesler, Cimasoni). So counting is
     fixed-parameter tractable in the genus and never hard at bounded genus. Nothing new is claimed here.
   - **The knot's handles cost nothing (proved).** A Fano atom meets the rest of a space through three edges, and every even tensor on
     three edges is a planar gadget: the first matchgate identity lives at four. So any number of atoms can be counted through.
   - **The glue's handles can cost (proved).** Where three planar pieces meet at a square (a Robertson–Seymour–Thomas junction), the
     junction can leave the planar class. Each such junction costs at most a factor 2 on the piece it hangs from, so counting takes
     time 2^(junctions) times a polynomial. At the knot's law only squares with three twisted sides, or above them, cost.
   - **On the knot's own spaces, atoms pay for the junctions (proved).** Every end piece of the glue needs an odd number of signs on a
     square away from its junction. A plain space has no signs to spend: its signs come only from twisted sides of its tight cuts, and
     those end in atoms. So junctions + planar glue pieces ≤ atoms − 2. The trisum of three cubes with three atoms (29 points) attains it.
   - **So on the knot's spaces counting is fixed-parameter tractable in the number of atoms** (time 2^atoms times a polynomial), and
     polynomial at any number of atoms when the glue is planar. The knot's hard couplings need unboundedly many atoms.
   - **Off the knot's spaces, signs pay instead.** With signs, or on colourable plain Pfaffian braces, counting is #P-hard with no atom.
   - **Computed.** On 257 spaces (the census to 26 points, 80 random spaces with plane glue, larger ones and 28 with trisum glue)
     the bound holds and 771 exact counts agree two ways. Evaluations grow with junctions, never with atoms.
   - **Reading.**
     - Hardness lives in handles, but not in the knot's: in the glue's junctions.
     - The knot can twist its glue only by spending atoms. Three ports are free; four ports can cost; at the knot's law, three twisted
       sides at a square are what costs.
     - The planar half of the owner's hypothesis holds. Pfaffian glue is not tractable by itself; on the knot's spaces it is paid for.
   - **Provenance.** Genus: classical. Small separations and matchgate splitting: classical techniques. The junction bound and its
     sharpness: no source found.
   - **Next (recommended, awaiting the owner).** Native reading of junction handles (2/3): do exact creation maps read the glue's junctions
     and the atoms that pay for them? Start on the 29-point space and the edge-atom chains.
     - **The alternatives.** A hardness bound in the number of atoms (1/3); reading with the far sides (2/3, still pending).

   **2026-11-06: reading with the far sides** (`FAR-READ-20261106-001`).
   - **The far sides nest (computed, 191 spaces).** The Fano plane and census 58 create at the same pairs. K4^(3) creates only where
     census 6 does, and census 6 creates without the Fano plane only at glue lines. So at an atom line creation has one of four
     strengths.
   - **A Fano atom acts as one from outside (computed, 1,065 of 1,065 atoms).** Whichever of its lines is removed, every atom line
     outside it receives the same far-side vector. Its lines differ only on glue lines and in what they receive.
   - **A rule reads the atoms.**
     - **The rule.** Twins; twins among atom lines; a split into the finest parts of three or more lines that act as one; reattachment
       of single port lines through the Fano plane.
     - **Development.** It returns exactly the Fano atoms of all 191 saved spaces, and every step is needed.
     - **Fresh test.** Frozen, it reads all 86 fresh spaces within a cost cap fixed in advance (334 atoms). That includes the 24 fresh
       spaces where whether creation occurs cannot tell atoms apart. The two-stage rule reads 51 of the 86, the source rule counts 68.
     - **Not proved.** Neither the rule nor "acts as one" is a theorem.
   - **Reading.**
     - **A handle is one thing from outside.** Its parts are not separately visible to the rest of the space, so an atom is atomic in a
       precise sense.
     - **Why the yes/no relation failed.** A plane piece hides which atom a removal came from. Which far side completes the creation
       does not.
     - **A known shape.** Acting as one is a one-sided module, as in Gallai's modular decomposition and the clans of 2-structures.
       Reading handles as the finest such modules of the creation map is new.
   - **Provenance.** Modules are classical. No source was found for the far-side structure, the rule or its fresh test.
   - **What is left.**
     - A proof that atoms act as one.
     - Non-Fano handles. HANDLE-COUNT's junction handles, where counting hardness on these spaces lives, are such handles.
     - The cost cap's gaps: census spaces with three more atoms, and the largest plane spaces.
   - **Next (taken).** Prove that a Fano atom acts as one from outside (2/3).
     - **The easy case.** A scratch probe found that in 576 of the 731 saved atoms, removing any line leaves every port pattern
       allowed, so the rest of the space cannot tell which line went.
     - **The hard case.** The other 155 have five to twelve ports and need the receiving-cut law.
     - **The alternatives.** Non-Fano handles through the receiving-cut law (1/3); glue relations from faces (1/3).

   **2026-11-07: why a Fano atom acts as one** (`ATOM-ONE-20261107-001`).
   - **Every Fano atom, with its closed sides, is the Fano plane (proved).**
     - **Sides.** A closed side acts as its lost element up to signs (KNOT-COMPOSE A, as corrected by NATIVE-PATHS A).
     - **Signs.** Of the 256 signed Fano planes, only the plain one is a knot.
   - **A Fano atom with a line removed is transparent (proved).** With any one of its lines removed, it sends the free relation through
     every one of its cuts. So the rest of the space sees the same port relation whichever line went.
     - **The knot is needed.** With arbitrary relations on its other cuts, this holds only for atoms with at most one line-type cut.
   - **Atoms see only the port relation (proved).**
     - **Creation.** Deep points of a removal's side never decide whether a Fano atom's line receives creation, even paired with deep
       points behind the atom's other elements.
     - **Far sides.** They add census 6 or K4^(3) only at a receiving atom's cut lines whose port relation has six patterns.
     - **Pass-through.** A free relation passes through a closed atom unchanged.
   - **So a Fano atom acts as one.**
     - **Proved.** For creation in every knot space; far side by far side outside that one place; and without exception on Fano trees.
     - **Computed.** On 277 spaces, saved and fresh, every Fano atom's line receives exactly its closed verdict at all 154,165 pairs. The
       exception occurs at 1,325 receiving cuts and adds nothing. These predictions were written before the run.
   - **Bounding cannot show more.** Deep points behind an atom's own other elements could add creation (56 of 980 abstract cases). No real
     space ever does.
   - **Reading.**
     - **A handle is all or nothing from outside.** With all its lines, it constrains each cut as one lost element. With any one line gone,
       it constrains nothing any cut can see.
     - **Where this comes from.** The knot itself: the plain Fano plane is the only signed Fano knot, and any missing line frees every
       other element.
     - **Atoms are blind to depth.** That is now a theorem for creation and, outside one finite place, for far sides.
     - **Doctrine.** No space is assumed.
   - **Provenance.** The Fano plane as the smallest critical non-2-colourable triple system, and the brace decomposition, are classical.
     No statement of the signed classification, transparency or the corollary was found.
   - **What is left.**
     - A proof of the exception.
     - That no atom splits into smaller parts acting as one.
     - Handles that are not Fano atoms.
   - **Next (taken).** The genus reading on Fano trees (2/3). Prove that FAR-READ B's rule returns exactly the
     Fano atoms of every Fano tree, then add plane glue.
     - **The alternatives.** Whether junction handles act as one (2/3); a proof of the exception (1/3).

   **2026-11-07: the axis built from logic** (`LOGIC-AXIS-20261107-001`).
   - **The owner's picture.** A number line or Cartesian plane whose axes are themselves infinite structures of logic, measured in
     logic. The measure used is bond distance: the least knot through two distinctions, minus one, read from allowed states alone.
   - **Without ends, bond distance is a ruler (proved).**
     - **Chained knots.** If far-apart parts of a law are independent, every knot is chained, so bond distance grows at least
       linearly with separation. Parity laws whose finite moves are dense (laws without ends) have this property.
     - **The number line.** On the atom thread w(t−1) ∧ L(t) → w(t), the bond distance between w_s and w_t is exactly t − s + 1: one
       unit per loop. A chain of two-place ties has no knot, so it has no spacing.
     - **The plane.** Tseitin's and the gauge law read the lattice's dimension from their allowed states: bond balls grow like r^d. On
       the plane the ruler is taxicab, 2d + 1 to 2d + 7: an x-count plus a y-count, never the diagonal.
     - **One bit per site freezes.** A parity law with one distinction per site is free or has no finite moves. A native parity plane
       needs a distinction per lattice direction.
     - **Native in every variable is not enough.** Take Ledrappier's law on x, z free and y = x + z. Every variable is flipped by a
       finite move, yet a six-variable knot joins points 2^k apart for every k. A correction request asks whether a native knot must
       also be natively bound.
     - **Growth never stretches.** A conservative extension never increases bond distance. A system that keeps its old allowed states
       grows only at its edges.
   - **The frozen axis is measured in signed bits (proved; equality conjectured).**
     - **Infinite bond balls.** In Ledrappier's law the three-place knots are exactly the Frobenius triangles.
     - **The bound.** Along each lattice line, bond distance is at most 1 + w(n), the signed-binary digit count of the separation, and
       it is 2 exactly at powers of two.
     - **Equality** is checked in windows: n <= 128, and all 168 vectors of [−6, 6]^2.
   - **With nothing drawn, towers stretch only through open ends.**
     - **Proved (hub-free gadgets).** Replacing every knot by a gadget keeps the old knot exactly when the gadget adds no open end, a
       distinction held by one knot. Every step is then conservative, and the original distinctions stay at bond distance 2 forever.
       The 2026-10-20 refinement is such a gadget, which is why it could not grow space.
     - **Measured (exploratory).** Gadgets with open ends stretch the ruler by a fixed factor per level: 3^k + 1 for the star and the
       hexagon, 3·4^(k−1) + 1 for the prism. Their growth dimensions, log(copies)/log(stretch), are 1.26, 1.63 and 1.29.
     - **Trees (proved).** On tree-shaped knot graphs, bond distance is the number of knots on the path plus one.
   - **Reading.**
     - **Where logic measures.** Logic measures space faithfully exactly where nothing is opened by infinity.
     - **Where space expands.** Space expands between existing distinctions exactly where growth adds open ends. The growth of
       emergent information and the growth of space meet there.
     - **What is still put in.** The dimension comes with the gadget, like a drawing. In no tested law is it derived from a rule
       that does not mention it.
   - **Provenance.** Strong irreducibility and dense homoclinic groups (Lind–Schmidt) underlie the ruler. Ledrappier's non-mixing
     shapes and Masser's unit equations in characteristic p underlie the frozen axis. Wolfram measures dimension by ball growth in
     drawn hypergraphs. No source was found for the bond-distance reading, the signed-binary construction or the open-end criterion.
   - **Next (recommended, awaiting the owner).** Growth at open ends (2/3). Let a uniform rule act only where the relation shows an
     open end, with no chosen gadget shape, and measure the growth exponent of bond balls.
     - **The alternatives.** The signed-binary lower bound (1/3); the logical Cartesian product of two threads (1/3).

   **2026-11-07: reading the genus natively** (`GENUS-READ-20261107-001`).
   - **Census 6 depends on how it is glued (proved).**
     - **How the test glues.** It joins a far side's split-point lines to the gluing line's points in the order they are written.
     - **Order-free.** K4^(3), the Fano plane and census 58 have the symmetry that makes the order irrelevant.
     - **Census 6.** It has three inequivalent gluings, and its verdict changed with the order in 8,046 of 11,552 sampled pairs.
     - **Creation.** Whether creation occurs never depends on the order.
   - **Natively a Fano atom is homogeneous (proved).** Count census 6 over its gluings. Then in every Fano tree every ordered pair of
     lines of an atom gets the same far-side vector: no K4^(3), census 6 at one gluing of three, the Fano plane, census 58. Whatever hangs
     behind its cuts forces it.
   - **So FAR-READ's split step was not native.** Given native vectors, it cuts every atom of six or seven lines: none of 23 Fano trees
     read, against all 23 in the written order. The native reading of Fano trees is the yes/no twin rule, already a theorem.
   - **Through plane glue (computed).**
     - **The information is native.** The order-free far sides tell apart all 372 pairs of atoms that whether creation occurs cannot.
     - **Where it sits.** For 114 pairs it lies only in what the two lines do to glue lines.
     - **The best rule so far.** Native row twins read 234 of 277 spaces.
   - **Reading.**
     - **A handle is one thing inside and out.** All its lines are alike to each other, and it acts as one from outside.
     - **The structure the split relied on** was how census 6's lines were written down.
     - **Doctrine.** No space, and no listing order, is assumed.
   - **Corrections.** `FAR-READ-20261106-001-D002` and the census-6 sentence of `FAR-READ-20261106-001-D001` carry pending qualifications.
   - **Provenance.** Invariance of a gadget's verdict under its symmetries is standard. No statement of the gluing classification or of
     native homogeneity was found.
   - **Next (taken).** Colour refinement on the native creation map (2/3). It is a canonical, representation-free
     procedure. Does its stable partition ever merge lines of two atoms?
     - **The alternatives.** Junction handles natively (2/3); a native audit of earlier far-side records (1/3).

   **2026-11-07: growth at open ends** (`OPEN-END-GROWTH-20261107-001`).
   - **The question.** Let a uniform rule act only where the relation shows an open end, a distinction held by one knot, with no
     chosen shape. What space does it grow?
   - **A local rule grows the number line (proved).** Grow only at knots that hold two or more open ends. From one knot this grows
     exactly the two-way thread, whatever choices are made: every unit keeps one open loop, and bond distance counts the loops
     between two points, plus one. The axis goes off to infinity in both directions, grown from a single knot by a rule that reads
     only open ends.
   - **Closing open ends freezes or collapses space (proved; census exploratory).**
     - **Bond distance is a boundary.** It is the least boundary of a two-sided region, counting seams and the open ends held inside.
     - **Sealing freezes.** A region with no open ends behind one seam pins that seam, and no knot crosses it. Closing the nearest open
       ends sealed space into frozen cells: no knot for 370 of 374 pairs.
     - **Short boundaries collapse.** Every two-sided boundary is a knot. Closing that avoids pins and ties left a strip whose bond
       distance never exceeds 5, at any length.
     - **No closing at all branches.** Random sprouting, and closing at the flat face size, gave small worlds. No rule grew a plane.
   - **The Cartesian plane is a product (proved; exact formula conjectured).** In the product law of two laws, whose allowed states
     are grids with every column and row allowed, a knot of each axis joined at a corner is a knot. So bond distance is at most
     δx + δy − 1. The product of two threads has no ends, so it is a ruler: taxicab distance, bond balls of order r^2, dimension two
     read from the allowed states. Exactly δx + δy − 1 holds on 855 checked pairs.
   - **Reading.** The line grows; the plane is the product of lines. Space holds together through open ends kept inside, as on the
     line, or through long seams, as on a lattice. Growth that consumes its open ends freezes or collapses. Taxicab distance is not
     round; whether logic can make round balls is open.
   - **Provenance.** Bonds and bridges are classical (Whitney; Oxley). Product codes and their duals are classical (Elias;
     MacWilliams–Sloane). No source was found for the growth rules' classification, the L-shaped knots or the exact formula.
   - **Next (recommended, awaiting the owner).** Circles from logic (2/3): can bond balls become round? Map the large-scale shape of
     bond distance in periodic laws without ends, where polygons are expected, and in random local laws, where roundness could
     appear only as a trend.
     - **The alternatives.** Dimension under products of k lines (1/3); a proof of the exact taxicab formula (1/3).

   **2026-11-07: colour refinement on the native creation map** (`REFINE-READ-20261107-001`).
   - **The planned test was the wrong one.** Colour refinement (1-WL) must give the same colour to lines that a symmetry exchanges, and
     symmetric spaces exchange whole atoms. It merges lines of two atoms in 87 of 277 spaces, 14 of the 23 Fano trees among them, though
     the twin rule reads every Fano tree.
   - **Native creation fixes the atoms (computed, 277 of 277 spaces).**
     - **The test.** Pair refinement (folklore 2-WL), on the order-free far sides, never puts a pair within an atom and a pair across two
       atoms in one class.
     - **So** every symmetry of the native creation map maps atoms to atoms, and "same atom" is definable in three-variable counting
       logic in each space.
     - **What does it.** Whether creation occurs alone mixes them in 42 spaces: the far sides break exactly the symmetries that hid the
       handles.
   - **No uniform rule tried reads every space (computed).**
     - **The counts.** Yes/no twins read 219; native row twins and three refinements of them 234 each.
     - **Where they fail.** Atoms meeting one plane piece merge, in 32 of 38 cases as complete twins.
     - **A regularity.** Twin lines of one atom differ at the glue only by whether they create, never by how. Across atoms 530 of 1,572
       twin pairs differ by how.
   - **Reading.**
     - **Native emergence does not hide topology** in any computed space. The handles are determined by native relations; a uniform
       reading is what remains.
     - **In logical terms,** the atoms are definable space by space. Whether one formula serves all spaces is a question of uniform
       definability.
     - **Doctrine.** Everything is invariant under relabeling lines and re-listing their points.
   - **Provenance.** Weisfeiler–Leman refinement and its equivalence with counting logic (Cai, Fürer, Immerman) are classical. The
     application and the regularity are new here.
   - **Next (recommended, awaiting the owner).** Native creation at junction handles (2/3). On HANDLE-COUNT's trisum spaces, does pair
     refinement show that the native creation map fixes the junctions, where counting hardness lives?
     - **The alternatives.** Uniform definability of the atoms (1/3); a native audit of earlier far-side records (1/3).

   **2026-11-07: circles from logic** (`LOGIC-CIRCLE-20261107-001`).
   - **The question.** Do round spaces exist among logical spaces, perhaps only as large-scale trends, and does roundness differ in
     kind from polygons?
     - **A circle** is a bond ball.
     - **Its π** is Gołąb's: half its perimeter measured with its own distance. It is 3.14159… when the circle is round, and between
       3 and 4 for every plane, with 3 only for hexagons and 4 only for parallelograms.
   - **Periodic logic makes polygons with rational π (proved).**
     - **The polygon.** On a doubly periodic plane graph, bond distance is twice the dual's graph distance up to a constant. So the
       circle is the dual's velocity polygon, with rational vertices, and its π is rational.
     - **Only two regular circles.** By Niven's theorem, they are the hexagon (π = 3) and the parallelogram (π = 4).
     - **The table.** The 19 laws on Archimedean and Laves tilings have π in {3, 10/3, 16/5, 7/2, 11/3, 4}.
   - **Lines approach the circle as Archimedes did (proved).**
     - **The rule.** With a knot at each crossing of an arrangement of lines, bond distance is twice the number of separating lines,
       plus a bounded amount.
     - **Regular polygons.** With n equally spaced directions, the circle is a regular 2n-gon whose π is Archimedes' inscribed or
       circumscribed value. It is irrational from n = 4 on, and the arrangement is periodic only for n = 2, 3.
     - **Penrose.** De Bruijn's pentagrid gives 5/φ.
   - **Coins bend the circle (proved, citing Seppäläinen).**
     - **The law.** Split each four-place knot of the square law into two three-place knots by a coin.
     - **The circle.** It becomes a square with elliptic corners, quarter circles for fair coins, with π = 3.44120. Its flat lattice
       sides never round off.
     - **No randomness.** All coins one way give the honeycomb law's hexagon.
   - **Only isotropy rounds it (proved; measured).**
     - **Round.** A law of three-place knots on a Poisson–Voronoi tessellation has an exactly round circle. Its measured anisotropy
       is 1.05 at radius 60.
     - **No plane.** A uniformly random planar law, with nothing drawn, is not a plane at all. Its bond distance grows like n^0.28,
       near the Brownian map's n^(1/4), dimension 4.
   - **Reading.**
     - **Harmonies.** A periodic circle closes after finitely many sides, with a ratio of whole numbers: a harmony. The hexagonal
       planes, built from three directions, have π = 3: the circumference is exactly three diameters.
     - **A ratio that continues.** The round circle's π never stops. Logic reaches it only through infinitely many directions, or
       through chance with no preferred direction.
     - **Lines are shapes.** Every circle here is assembled from lines: straight segments, and with coins, arcs that are graphs of
       functions.
   - **Correction.** The axis entry's "What is still chosen" now reads "What is still put in": no law chooses. The question is whether
     a dimension is derived or written in.
   - **Provenance.**
     - **Classical.** Velocity polygons (Fritz; Kotani–Sunada; Eon), Gołąb's bound, self-circumferences of regular polygons (Martini
       and coauthors), Niven, de Bruijn, Seppäläinen's chains, Vahidi-Asl and Wierman's isotropy and the Brownian map.
     - **Not found.** The bond-distance reductions, the rational π of periodic laws, the exact table and the coin law's corners.
   - **Next (taken).** Round without coins: the pinwheel law (2/3). Local matching rules force the pinwheel
     tiling, whose tiles turn through the irrational angle arctan(1/2). Is its law's circle exactly round?
     - **The alternatives.** The spectrum of rational π among periodic laws (1/3); the exact taxicab formula (1/3).

   **2026-11-07: uniform laws and the spheres they can close into** (`UNIFORM-SPHERES-20261107-001`).
   - **The setting.** A law of lines and co-lines builds its own closed surface, with nothing drawn: points, lines (triples) and
     co-lines (cycles), each pair of a line's points lying in exactly one co-line.
     - **The count reads it.** The knot's count (`COUNT-SURFACES-20261107-001`) reads that surface's Euler characteristic.
       - It forces a violated line only on a sphere whose co-lines all close under the signs.
       - Negative curvature forces an over-agreeing face instead, and finding it is PPADS-complete, as finding the sphere's violated
         line is (`COUNT-ANTIVORTEX-20261107-001`).
   - **Uniform laws close into few spheres (proved).**
     - **The formula.** With every point alike, of co-line sizes (d1, d2, d3), χ = n(1/d1 + 1/d2 + 1/d3 − 1).
     - **The spheres.** A sphere arises only as an antiprism (2,2,d) or a snub polyhedron of 12, 24 or 60 points; each is realized by a
       law on a group (dihedral, A4, S4, A5).
     - **Otherwise.** The laws are flat, (3,3,3), (2,4,4), (2,3,6), or hyperbolic, such as the Klein quartic's law on PSL(2,7).
   - **Uniform signs never force the contradiction (proved).**
     - **Why.** Positive curvature sits on digons, two lines sharing two points. Under uniform signs every digon stays open, so the count
       never forces a line to fail on any uniform law.
     - **With non-uniform signs.** Signs that close the digons make the knot fail only on those small spheres or on antiprisms, which
       are chains solved by binary search.
   - **Computed.**
     - **Uniform signs.** The knot is satisfiable on every tested uniform law, and on all circulant laws with n ≤ 48 except the Fano
       plane. The Fano plane's contradiction is not the count's.
     - **The knot sphere** has exactly two kinds of points.
   - **Reading.** A law that treats every place alike can grow flat space without end, and negatively curved space, but not a large
     sphere. The knot's deep contradiction marks where a law stops treating places alike: two kinds of points and a sign defect at each
     of six digons.
   - **Provenance.** Vertex-transitive and Cayley maps and the spherical list (antiprisms, snub polyhedra) are classical. The reading of a
     law as a self-built surface, and the bound on uniform contradictions, are new here.
   - **Next (recommended, awaiting the owner).** Two kinds of points (2/3): which such laws close into large spheres, and can a local
     growth rule place the six digons itself, so that a law grows its own sphere and with it the knot's contradiction?
     - **The alternative.** Large uniform contradictions beyond the Fano plane (1/3).

   **2026-11-07: the only uniform contradiction** (`UNIFORM-FANO-20261107-001`).
   - **Proved.**
     - **Sign patterns.** With non-constant uniform signs the all-zero assignment satisfies every line, so only equal signs matter: a
       plain 2-colouring.
     - **The brace lemma.** If a law's symmetries are transitive on its points and on its lines, its incidence graph is a brace. Two
       translates of a smallest tight shore share at most one point, and counting forces a shore too small to hold a line.
     - **The conclusion.** By Seymour's dictionary and McCuaig's theorem, the Fano plane is the only uniform law whose knot contradicts
       itself. 439 Cayley laws agree.
   - **Reading.** Uniform worlds are coherent with one exception, a single handle. Every other contradiction of the knot, its hardness
     included, needs a law that distinguishes places.
   - **Next (taken at once, the owner's (i)).** How a law can distinguish places by itself. Rated Payoff 3/3 (Barrier), Concreteness 1/3
     (Stated), so the first step is scoping.

   **2026-11-07: round without coins** (`PINWHEEL-ROUND-20261107-001`).
   - **The question.** Can a law with no coins, and no Poisson points, have a round circle?
   - **Already known (Radin–Sadun 1996).** In Conway and Radin's pinwheel tiling, the shortest path along tile edges between points R
     apart has Euclidean length R + o(R). Open was the program's own distance, which counts distinctions and uses no lengths.
   - **The pinwheel's laws are round (proved, citing Radin).**
     - **The principle.** If a space of tilings is rotation-invariant and uniquely ergodic under translations, every covariant bond
       distance grows at one rate in every direction.
     - **Both laws.** So the parity laws with knots at pinwheel tile corners, or on pinwheel tiles, have exactly round circles.
   - **Roundness needs two ingredients (proved; measured).**
     - **The rule.** It cuts a right triangle into copies of itself.
     - **Legs 1:1.** The angle π/4 is a rational part of a turn. The result is the periodic tetrakis triangulation, whose circles are an
       octagon (π = 10/3) and a square (π = 4).
     - **Legs 1:2, cut frame-consistently.** It has the irrational angle arctan(1/2), but all tiles keep one frame, and its measured
       circle keeps a growing four-fold component.
     - **The pinwheel cut.** It has both the irrational angle and mirror-image siblings, which make descendants turn against each other.
   - **Round only as a trend (proved; measured).**
     - **Orientations.** A disc of radius R meets O(log R) orientations: 28 at R = 128.
     - **Anisotropy.** The corner law's falls from 1.106 to 1.030 between R = 8 and 128.
   - **Reading.**
     - **One rule, two outcomes.** It makes a harmony or a continuing ratio depending only on the triangle: 1:1 closes into a periodic
       polygon world; 1:2 continues and becomes round.
     - **Perfect circles are trends.** The circle is round only in the limit, gaining directions logarithmically.
     - **Intrinsic.** Bond distance depends only on which distinctions share knots, so the law's own distance is large-scale Euclidean.
       The drawing is used to prove it, not to state it.
   - **Provenance.**
     - **Classical.** Radin's unique ergodicity, rotational symmetry and matching rules; Radin and Sadun's edge-length result;
       isotropy arguments (Vahidi-Asl–Wierman).
     - **Not found.** The bond-distance version, the two-ingredient contrast and the logarithmic orientation count.
   - **Next (taken).** The pinwheel grown with nothing drawn (Payoff 2/3, Concreteness 2/3). Write the
     substitution as a rule on knots and their shared distinctions, with labels but no coordinates. Does it regrow the pinwheel's
     law exactly?
     - **The alternatives.** The spectrum of rational π among periodic laws; a proved rate for the rounding.

   **2026-11-07: the pinwheel grown with nothing drawn** (`PINWHEEL-NATIVE-20261107-001`).
   - **The question.** Can the pinwheel's rule be stated with no coordinates, no lengths and no angles? Does it need labels from
     outside?
   - **An eleven-label table regrows the law (proved).**
     - **The labels.** Label each distinction by its two knots' side types, where it sits along them, and whether they run the same
       way. Only eleven labels ever occur, eight inside and three on the boundary.
     - **The table.** Every knot splits into five. Every distinction splits as a → g e d e g, b → h c c, c → b b, d → a, e → b,
       f → b, g → a, h → b. Five new distinctions, f, g, c, a, h, appear inside each knot.
     - **Exact.** The law is regrown exactly at every level, identical to the geometry at levels 0–7.
   - **Eight kinds of distinction (proved).**
     - **Whole sides.** Hypotenuse against hypotenuse, either way round; long leg against long leg; short leg against short leg.
     - **Half sides.** Half a long leg against a short leg, or against another half.
     - **So** the only T-junctions are at midpoints of long legs.
   - **The law carries its own labels (measured).**
     - **The map.** The law's graph is 3-connected, so its allowed states determine its planar map up to mirror image (Whitney).
     - **The labels.** Every distinction's label is read from its unlabelled neighbourhood of radius 2: no conflict among up to
       235,394 darts at levels 5–7. Shuffled and non-local labellings conflict.
   - **Reading.**
     - **The rule.** Split every knot into five, read each distinction's kind nearby, and split it by an eleven-letter table. That
       rule grows a law whose own distance is round.
     - **No geometry.** No coordinate, length or angle enters.
     - **Where the angle went.** Into the law's large-scale shape, not into any finite part of it.
       - **Not in the counts.** The eight kinds recur in rational proportions, per knot: a 3/11, b 5/22, c 16/55, d 3/55, e 6/55,
         f 1/5, g 17/55, h 27/110.
       - **The only irrational number.** The table's growth rate √5, which is the length scale.
       - **In the limit.** The combinatorics alone recover the triangles (Kenyon and Stephenson). Drawn conformally, which fixes
         the picture up to similarity, clusters of tiles converge in shape to the 1:2:√5 triangles. So the angle, like the round
         circle, is a limit property of the law.
       - **Corrected 2026-11-08.** This bullet first said that the angle appears only if the grown law is drawn in the plane.
   - **Provenance.**
     - **Known in substance.** A coordinate-free pinwheel rule with four-cornered tiles, the fourth corner at the long leg's
       midpoint, and the return of its geometry: Kenyon and Stephenson (Proc. Amer. Math. Soc. 147, 2019).
     - **Classical.** Finite combinatorial descriptions of substitution tilings (collared tiles, Anderson–Putnam complexes; for the
       pinwheel, Barge–Diamond–Hunton–Sadun and Frettlöh–Whitehead–Whittaker) and Whitney's theorems.
     - **Not found.** The radius-2 readability, and the rule's form on knots and distinctions.
     - **Corrected 2026-11-08.** The rule and the census were first listed as not found.
   - **Next (recommended, awaiting the owner).** A round plane grown at its open ends (Payoff 3/3, Concreteness 2/3), starting with
     atlas growth. From one knot, add knots only where every nearby distinction keeps a radius-2 neighbourhood of the pinwheel's
     atlas. Does growth reach dead ends, or grow pinwheel patches outward as the number line grew?
     - **The alternatives.** Prove radius 2 for every pinwheel tiling; the spectrum of rational π among periodic laws.

10. **Competition. Mapped on 2026-10-19, not decided.** Pairwise rules that
    must all hold never make a knot, but pairwise preferences that cannot all
    hold leave knots among their least-violation states ("Knots from
    competing pairs"). Both readings were tested ("Both readings tested"):
    - **Strict reading:** stays presentation-invariant and gives pairs no
      knots.
    - **Competition reading:** needs weights, a declared measure of
      violation. In return, frustrated pairs make one kind of knot, the
      not-all-equal triangle.

    Is competition the law that question 9 asks for? Not by itself.
    Competition turns a triangulated layout into a chain of knots whose
    separation grows along the layout, but it does not make the layout.
    Whether to admit least-violation states as allowed remains the owner's
    decision.

## Testing ideas

The [knot laboratory](../tools/knotlab/README.md) computes every verdict above
from allowed states:

```bash
PYTHONPATH=tools python3 -B -m knotlab demo
PYTHONPATH=tools python3 -B -m knotlab worlds
PYTHONPATH=tools python3 -B -m knotlab presence
PYTHONPATH=tools python3 -B -m knotlab patterns
PYTHONPATH=tools python3 -B -m knotlab choice
PYTHONPATH=tools python3 -B -m knotlab space
PYTHONPATH=tools python3 -B -m knotlab competition
PYTHONPATH=tools python3 -B -m knotlab rings
PYTHONPATH=tools python3 -B -m knotlab holonomy
PYTHONPATH=tools python3 -B -m knotlab depth
PYTHONPATH=tools python3 -B -m knotlab check --cnf "~A ~B c" --loops A B --contact c
PYTHONPATH=tools python3 -B -m knotlab check --cnf "w ~A ~B; ~w ~C d" \
  --loops A B C --contact d --witnesses w
python3 -B -m unittest tests.test_knotlab
```

`demo` covers the definition and facts. `worlds` covers forced worlds,
building from atoms, distinctions, choice and infinite threads. `presence`
covers the earlier exploration of presence under the absence reading.
`patterns` covers the original
post: controllers, hidden information and the two readings of erasure.
`choice` covers whether the base has real alternatives. `space` covers bonds,
the shape of free sets and composition. `competition` covers both readings of
rules that cannot all hold. Each exits nonzero if a result changes, so run all
seven after changing a definition.
