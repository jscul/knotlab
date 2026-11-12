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

**Words.** Since 2026-11-11 the notebook names the program's own objects in the
words of the glossary of the Intuitions guide (`publication/knotlab/INTUITIONS.md`,
"Glossary"): by distinctions, knots and counts, with each spatial word marked as
the literature's name or as a drawn picture, and with one meaning to each word.
The entries were reworded on that day without changing any claim, number or
verdict; the earlier text is in git history.

## The picture

- **A chain is not enough.** An implication chain only orders its members, and
  strings with loose ends can always be rearranged into one another.
- **A single loop is not enough.** A loop of implications forces all of its
  members to be equal, so it collapses to one distinction. A loop of equal and
  unequal steps collapses to one free bit or contradicts itself.
- **What is real is what lies between bound loops.** The binding belongs to
  the pair, not to either loop. No part smaller than the whole shows it, and
  erasing either loop removes it.
- **A loop is a logical structure that can be entwined.** It is not spatial.
  What it brings to a binding is an open distinction, a bit it leaves free.
- **A knot is not just any hole.** In the free complex of what a system leaves
  free, a knot is a hollow triple: every pair free, the whole not. Pairwise
  ties can make other holes, but never this one (see "Holes and knots").
- **Knots live across alternatives.** A knot leaves every loop's distinction
  open and fixes at most one bit. In a single settled world there is nothing
  to see.
- **2-clauses are logic, not topology.** Everything a 2-clause says is
  pairwise, so 2-clauses that must all hold can never make up a loop or a
  binding. 2-clauses that compete, where the allowed states are those that
  break the fewest, can leave a knot (see "Knots from competing pairs").
- **Witnesses carry information about a loop's interior.** A witness is
  information outside a loop that reports on its interior, for example whether
  two of its distinctions show 00/11 or 01/10. The witness of one binding can take
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

1. **Two loops and a contact have 34 knots, in five classes.** They range from
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
  negation they come in five classes:
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
weakest bond. Five descriptions pick it out, and `knotlab worlds` checks each
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
makes a difference. The atom is the weakest bond: of the relations in which
things constrain one another jointly rather than in pairs, it excludes the
least. Peirce held
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

## Endless chains

Forced worlds make sense for unbounded systems of atoms: the forced world
contains everything that finitely many steps of propagation reach.

- **Everything rests on finitely many loops.** In the chain `L1 ∧ L2 → w1`,
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
- **An endless chain is a tower of finite knots.** Each `wk` binds the
  first k+1 loops, and no contact binds them all. A contact for the whole
  chain would need a limit rule with infinitely many premises, which no
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
  34 relations of five classes. Every mechanism that binds two loops, whether a
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
it allows, form a simplicial complex: the system's free complex. Its bonds are
the knots inside it.

- **A knot is a hole.** A knot on m variables makes its free complex a hollow
  simplex, which the literature draws as an (m − 2)-sphere. The two-loop knot
  is a hollow triple, the literature's circle: three free pairs around a
  missing whole.
- **Bonds compose into a bond or into nothing.** For single clauses this is
  resolution.
- **Paths and separation.** Along a chain of atoms, the smallest bond joining
  the ends grows by one per step.
- **Logic allows every free complex.** Every simplicial complex is the free
  complex of some system, so logic selects no space, and whatever space there
  is comes from the law.
- **Not every hole is a knot.** Two pairwise ties can leave a hollow cycle of
  four, a hole of dimension one. Topology in the knot sense begins at bonds.

So contact structure gives intrinsic holes, paths and separation, but not
space. A law that produces space without having it written in is the open
problem studied by causal sets, quantum graphity and hypergraph rewriting.

### Holes and knots

The two words are easy to confuse. A system's **free complex** is built from
what it leaves free, and the literature draws it so:
- each free distinction as a point;
- each pair of distinctions that can take all four combinations as an edge;
- each free triple as a filled triangle;
- and so on.

A **hole** is any gap in that complex: a cycle of free pairs, or the same at a
larger size (in the drawing, a hollow sphere), that no free sets fill. A
**knot** is the smallest kind of hole: a set whose every part is free but
which is not free itself. In two loops and a contact, it is a hollow triple.
All three pairs are free, and only the whole is missing.

```text
a knot: a hollow triple              a hole made by ties: a hollow
(drawn as an empty triangle)         cycle of four (drawn as a square)

        A                               a ──── b
       / \                              │      │
      B ─ c                             d ──── c

all three pairs are free;            the pairs a–c and b–d are tied,
A, B and c together are not          so they are missing from the complex;
                                     the gap is made of missing pairs, not of
                                     a missing triple
```

| | Hole | Knot |
| --- | --- | --- |
| What it is | Any gap in the free complex, of any size | The smallest gap: every part free, the whole not |
| What it looks like | Any cycle of free sets left unfilled | A hollow triple, or a hollow simplex for more loops |
| What can make it | Pairwise ties can make one (the hollow cycle of four) | Only a constraint on three or more at once; no 2-clause system has one |
| What it means | Some joint pattern among the distinctions | Information held by the whole and by no part |

Every knot is a hole, but not every hole is a knot. A hole that ties can make
can be explained by pairs; a knot cannot. When this document says "topology
begins at the knot", it means knots, not holes in general. Larger holes can
also arise just from taking separate knots together, so to tell whether
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

**Emergence in bits** (`EMERGENCE-BITS-20261021-001`). The bits a relation
hides from its pairs are log₂ of the states its pairs allow, minus log₂ of
the states it allows.
- **What single relations hide.** It is zero exactly for 2-CNF relations,
  log₂(8/7) ≈ 0.19 for one clause, and one bit for parity. No knot hides more
  than one bit.
- **What many distinctions can hide.** n distinctions can hide about
  n − log₂log₂n bits from their pairs (minimum covering arrays).
- **The statistical version.** It is the divergence of the uniform
  distribution from the pairwise model, at most n − log₂(n+1), reached
  exactly by Hadamard designs. On seven distinctions those are the parity
  knots on the lines of the Fano plane, the Fano pattern.

### Knots from competing pairs

Pairwise rules can be combined in two ways:
- **Conjunction.** Every rule must hold. This is logic, and it never makes a
  knot from pairs.
- **Competition.** The rules are preferences, and the allowed states are the
  ones that break the fewest. Preferences that cannot all hold are called
  *frustrated* (Toulouse 1977).

Competition can make a knot from pairs. Take three distinctions and ask each
pair to agree or to differ. With an odd number of "differ"s the preferences
cannot all hold: going around the cycle of three, the differences would have
to cancel, and they cannot. Under conjunction the system allows nothing. Under
competition it allows the six states that break exactly one preference, and
those six form a knot: every pair is free, and the three together are not.
When all three pairs should differ, it is the not-all-equal knot.

Three results, checked in `PatternTest` (`test_competing_pairs_make_knots`):
- **Exactly four knots come from competing pairs alone.** A knot on three
  variables is the set of least states of some energy with only one- and
  two-variable terms exactly when its two excluded states are opposite. These
  are the four frustrated three-cycles (the literature's frustrated
  triangles): 4 of the 34 knots.
- **No knot on four or more variables does.** A frustrated cycle of four or
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
visible, a knot other than the four frustrated three-cycles cannot come from
pairwise terms, even competing ones. With hidden variables, a knot certifies
only that the rules are not pairwise rules that must all hold.

**In statistics the four are silent** (`EMERGENCE-BITS-20261021-001A-P001`).
Take the uniform distribution on a relation's allowed states. Its divergence
from the best pairwise model is zero exactly when the relation is the least
set of a pairwise energy.
- **The frustrated three-cycles** are therefore the only knots whose allowed
  states their pair statistics predict exactly.
- **Every other knot** carries correlations that no pairwise interaction
  explains.

`SIGNED-FRUSTRATION-001D1` recorded the frustrated three-cycle's six tied least
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
- **Weights matter.** Weighting one preference of the frustrated three-cycle
  twice removes the knot. With unequal weights, competition selects a few
  states and leaves no alternatives, and knots need alternatives.
- **Near and far (exact enumeration).** Of 470 uniform pairwise rules around
  a ring, none has near and far under the strict reading. Under competition,
  178 do, but never with more than two separation levels.
- **Growing separation.** On a drawn strip of triangles, a declared layout,
  where each triangle counts its own broken preferences, competition equals
  strict not-all-equal knots on the triangles' triples. Separation then grows
  along the strip, from 3 to 8 on 14 distinctions, like a chain of atoms. Counted once per pair, the same rules
  settle into a few ordered states with at most two levels.

So competition is a law that turns a drawn triangulated layout into a chain
of knots, but it does not supply the layout. No tested rule produced near and far
that its layout lacked.

Two follow-ups from 2026-10-19, checked in `tests/test_knotlab.py`
(`SpaceTest`):

- **Pairwise structure makes only flag complexes.** In a 2-CNF system a set
  is free exactly when all its pairs are free. So 2-clauses can make holes, as
  when two ties leave a hollow cycle of four, but never a hollow triple: three
  distinctions free in every pair yet not free together. That hollow triple is
  exactly a knot. Of 399 random 2-clause systems on six variables, 29 have
  holes and none has a hollow triple.
- **Holes made of holes.** Binding knots raises the dimension, in the
  literature's count, of the free complex's holes. One knot is a hollow
  triple, a hole of dimension one; two knots sharing a distinction leave holes
  of dimension two; a chain of three leaves holes of dimension three.
  - Two unrelated knots taken together also leave a hole of dimension three,
    because the join of two hollow triples has one (the literature's
    3-sphere). So a higher hole alone does not
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

- **A ring excludes exactly the odd loops.** A ring rules out an assignment
  of its distinctions exactly when every table along it is a permutation and
  an odd number of
  them swap. So a ring of knots composes into a knot or into nothing.
- **Only parity carries a loop at full strength.** A knot whose tables are
  all permutations is a parity knot. A ring of parity knots becomes one knot
  on all its distinctions, so the loop becomes a hole, and it keeps one full
  bit at every length.
- **Other knots fade.** Every other knot keeps a trace only through its
  permutation tables. Its share of excluded assignments shrinks exponentially
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
  independent loop, and only parity fills every loop. But frustrated parts
  add up, so other knots can hold many bits in large networks: 1.32 bits on
  the Petersen graph, and an amount growing with the number of vertices on
  drawn grid tori.
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
  - The free complex of the selectors is the nerve of the holonomies'
    fixed-point sets, so every free complex occurs.
  - A tie or knot among loops excludes only the assignment that selects all of
    its loops. Any proper subset of the loops can be on together, but not all
    of them.
  - The transpositions (03), (13) and (23) knot three loops this way, as a
    hollow triple.
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
must hold at once to see a hole
([decision note](../research/DEEP-HOLES-20261020-001/deep_holes.md);
`knotlab depth`). These patterns turn the previous networks around: knots sit
at the vertices of a graph and share its edges as distinctions.
- **Charge patterns.** Parity knots ask each vertex's edges to sum to its
  charge. Such a pattern allows nothing exactly when the total charge is odd:
  a charge hole, a class in H̃₀ rather than a loop in H¹.
- **Local holes say nothing about depth.** Every knot that excludes two or
  more states is already a hole at its own scope. The program's plain hole
  criterion therefore certifies nothing on these patterns.
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

So holes come in two kinds:
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
  - **The half rule.** In a hub-free knot pattern that allows nothing, every knot whose removal leaves the pattern connected allows
    exactly half the states of its distinctions.
  - **Native contradictions are parity contradictions.** Every native contradiction is a parity system joined by forced values, and
    hub-free knot patterns of every law are solved in polynomial time.
  - **Refutation.** Without parity knots, refutations need only clauses of two literals. With parity, they can need exponential
    resolution size (Tseitin).
  - **Three in two directions.** NP-hardness needs a hub as well as a knot: three places per relation and three relations per
    distinction.
    This is the knot-level form of Tovey's theorem (1984).
- **Native counting (2026-10-24, `NATIVE-COUNTING-20261024-001`).**
  - **The gluing criterion is a known recurrence.** The criterion for a knot's count to depend only on a hub-free pattern's cycles
    and open distinctions (the literature's surface), two glued copies symmetric in four legs, is the Fibonacci-gate recurrence of
    holographic algorithms.
  - **Easy exactly for the topological knots.** The four topological knots count every hub-free pattern by a closed formula. Counting
    is #P-hard for the other 30 knots, given Backens's dichotomy, although deciding is easy for all.
  - **Reading.** Emergence is countable exactly when it is topological.
  - **Closed not-all-equal patterns.** They count like an antiferromagnetic Ising model: a determinant when the literature's surface
    is a sphere, with the cost growing with each of its handles.
- **Native approximate counting (2026-10-24, `NATIVE-APPROX-20261024-001`).**
  - **K2 is the terraced condition.** The knot axiom K2 is the hypothesis of McQuillan's winding method. The 26 windable knots, those
    excluding at most two tuples and the parity knots, have approximation schemes given his theorem.
  - **Hard exactly, easy approximately.** With the four topological knots, 28 of 34 knots are settled. For 24 of them emergence is
    hard to count exactly and easy to approximate.
  - **Open where Fibonacci meets a twist.** The six left open are the Fibonacci knot with one or two places negated. Their hub-free
    patterns are Fibonacci patterns with disequality ties, and in the Fibonacci basis a twist is a reflection with a negative entry.
  - **Freezing is not hardness.** A knot freezes every hub-free tree, so that the leaves decide the root either way, exactly when
    its excluded tuples take both values at every place. That holds for 14 knots, including the six, not-all-equal and parity. It
    refuted the predicted decay for the six, but not-all-equal freezes and is approximable.
- **Imitating a hub (2026-10-25, `SOFT-HUB-20261024-001`).**
  - **No exact hub.** No native gadget of any knot is supported exactly on 000 and 111: native supports exclude at most half their
    values.
  - **Only linked pairs make hubs.** Two solutions whose difference does not tie all three terminals together can always be rerouted
    onto off-diagonal values. So windable gadgets stay below a hub ratio of √3 (given McQuillan), and parity and no-lone gadgets
    below 1.
  - **The open knots stay low.** Their non-windable excluded sets are a closed neighbourhood plus its antipode (0, 1 or 3 defects,
    never 2).
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
- **Where counting on 3-manifolds becomes hard (2026-10-25, `HARD-3D-20261025-001`).**
  - **Setting.** These entries concern the literature's 3-manifolds, and their knots, links and knot groups are the classical knots of
    knot theory, not logical knots. On 3-manifolds the native counting laws are group laws, and they count homomorphisms π₁(M) → Γ.
  - **With boundary (proved).** Attach thickened tori to a handlebody along the curves of a planar graph. The count of maps into S₃ is
    a spin model on the graph whose repeated edges recover its 3-colourings, so it is #P-hard.
  - **Closed (proved).**
    - Doubling the handlebody closes it, and the double counts pairs of colourings: exactly 2·P(G, 9)/3^|V| for S₃.
    - The same Potts duality gives #P-hardness for every dihedral group whose order is not a power of 2 at least 16, the quaternion
      group and A₄.
    - The class-2 cases show that the bounded-H² hypothesis of the class-2 algorithm is necessary.
  - **Open.** The dihedral group of order 16, where a collision of growth rates blocks the extraction.
  - **Reading.** On 3-manifolds the easy-hard line is the abelian/non-abelian line, the affine boundary the program found on the
    hub-free patterns that the literature draws as surfaces. S₃ is hard although it is solvable, and it is the smallest non-abelian
    group.
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
    - The program's affine line on 3-manifolds is "pointed versus non-pointed centre": abelian anyons only, or some anyon of
      dimension above 1.
    - Each hard instance hides a colouring of the flux paired with a colouring of the charge.
    - Abelian groups have the same pairs, but no gadget can isolate them, which is why they stay easy.
  - **Next (deferred).** Bounded first homology. Metabelian targets look polynomial there; S₄ is the first open case.
- **Counting with bounded first homology (2026-10-25, `BOUNDED-H1-20261025-001`).**
  - **Knots are hard for S₄ (proved).**
    - Draw a planar graph's alternating classical knot with every edge tripled. A full twist of three crossings is invisible to S₃, so the S₃
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
    - The longitude, the closed curve that bounds the classical knot's Seifert surface, cannot carry the second-level bit of a
      transposition colouring.
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
   - **Natively bound, assumed on 2026-11-07.** A knot native in every
     variable is also assumed natively bound: a knot of the closure of its
     solution's finitely-different solutions. The owner recorded this as an
     assumption rather than a decision, and it can be challenged (A1 of the
     [register of assumptions](ASSUMPTIONS.md);
     [request](../research/LOGIC-AXIS-20261107-001/canonical_correction_request.md)).
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
   binds loops into atoms, in any pattern, at k + 1 witness values for k loops.
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

   **Words in the learning entries.** The learning entries below work on drawn knot patterns (glossary of the Intuitions guide): every
   knot holds three distinctions and every distinction lies in three knots, drawn as a two-coloured triangulation whose triangles of
   one colour are the knots and of the other the distinctions, each distinction in the three knots across its sides; the record's
   faces are the triangulation's vertices (corrected on 2026-11-11, `docs/CORRECTIONS.md`). The knot sphere and the tori, with their faces, corners, handles and genus, belong to that drawing, which
   is declared, not built by the law. Before 2026-11-11 these entries called the knots lines, the distinctions points, the Fano and torus
   pieces atoms and the drawn knot patterns knot spaces; "the point" is still the owner's moving point of dissonance (G15).

   **2026-11-07: steering the knot sphere's dissonance by re-signing** (`RESIGN-STEER-20261107-001`).
   - **The question.** The owner pictures learning as a point with a strength like charge moving through a learned network of knots,
     the learning orienting the logic to guide it to a resolution. On a Kasteleyn-signed knot sphere no change of state removes the
     dissonance: some knot is always violated. Take that forced dissonance as the point and learning as changing signs. Can
     learning move it, and where to?
   - **Rationalization never fails (proved).** Violated knots minus over-agreement plus half the number of even faces is 1 in every
     state and law. One sign change at the violated knot splits the point into two even faces, the law's own marks, and on every
     simplicial sphere every law with two even faces, wherever they sit, has consistent states (Euler's formula and Hall's
     theorem). With four or more even faces every state over-agrees somewhere: rationalizing too much makes the opposite
     dissonance.
   - **The unlearned law prefers no knot (proved).** Every knot is the violated knot of exactly 2 N(T) least-dissonance states,
     with N(T)² = det(B Bᵀ) / (n0 n1 + n1 n2 + n2 n0), B the knot–distinction matrix and n_i the sizes of the classes of the
     distinctions' 3-colouring: 54 on K_2, 24,576 on K_3, 163,840,000 on K_4.
   - **Learning alone steers (proved).** With the state held fixed, sign changes made only at the violated knot or at an even face
     carry the point from any knot to any knot, never holding more than the forced unit. On the sphere a closed walk of sign
     changes equals a block change of state, so what learning adds to behaviour is exactly where the even faces sit. In dimer
     language the point is a trimer, the even faces are monomers, and the walk is the worm algorithm of dimer models, carried by the
     signs.
   - **Measured on the octahedral spheres (exploratory).**
     - **A local rule suffices.** A rule that sees only the knots at one even face and the distance to the target, and never steps
       straight back, reached 2,399 of 2,400 targets on K_2–K_8 and K_10, and 300 of 300 on K_12.
     - **The halves repel and the corners attract.** The number of consistent states is least when the two even faces touch and
       grows like a power near 1/2 of their separation (fitted 0.46 on K_12, 0.49 on K_16, 0.51 on K_20), as for two unit holes in
       lozenge tilings.
     - **Corners are where the halves rest.** A learner that moves the even faces to keep the most states parked both on corners
       in all 150 runs on K_3–K_10.
   - **Reading.** For the owner's picture: rationalization moves the point into the law as two half-charges, learning carries
     them, and rejoining puts the point where it is wanted. The count of consistent states adds a strength of a second kind,
     stability: the halves are least stable when they touch and settle on the corners, where the curvature that forced the
     dissonance sits.
   - **Provenance.** Known: Kasteleyn's theorem, Hall's theorem, Heawood's colouring theorem, monomer correlations (Fisher and
     Stephenson), worm algorithms for dimers (Sandvik and Moessner), Ciucu's electrostatics of holes in lozenge tilings. Not found:
     the uniform count over knots and its closed form.
   - **Next (taken by `LEARN-HANDLES-20261109-001`, below).** Learning in handles: off the sphere, signings with the same even faces differ by a
     homology class that no change of state reaches, so a learning walk around a handle could remove a dissonance that the class
     forces, with no mark left in the law (Payoff 2/3, Concreteness 2/3). The alternatives: many distinctions at once, and layers
     through naming knots ([decision note](../research/RESIGN-STEER-20261107-001/resign_steer.md)).

   **2026-11-09: learning in handles** (`LEARN-HANDLES-20261109-001`).
   - **The question.** On the sphere learning moves the forced dissonance anywhere, but a closed learning walk is a change of state in
     disguise. Off the sphere laws with the same even faces differ by a homology class that no change of state reaches. Can learning
     carry information that no change of state can?
   - **Only χ = 0 can be resolved (proved).** A law and a state are free of dissonance (no violated knot, no over-agreeing face, no
     even face) only on a surface of Euler characteristic 0. On the sphere learning can move the forced dissonance into the law but
     never remove it; at genus 2 or more every state over-agrees somewhere.
   - **The class-forced pair (proved).** On a torus whose Kasteleyn law is in a class no state satisfies (the Fano plane's torus and
     the thin tori of even index), the least dissonance is one violated knot and one face whose three corners agree: two opposite
     charges that no change of state cancels.
   - **Learning resolves it, only by winding (proved).** With the state fixed, one sign change at the violated knot splits it into two
     holes, and walking them along the knots into the over-agreeing face resolves everything, leaving no even face. Every process that
     resolves the pair, whatever the state does, changes the law by a cycle around a handle, into another class: learning carries the
     class, two bits on a torus, and nothing local. Checked by 96,732 walks on the two Fano tori and 57 thin tori up to 40 distinctions.
   - **Measured (computed).** The cheapest walk into each class costs exactly the smallest cycle of its class change (2 the short way
     around a thin torus, about half its distinctions the long way). A local rule that sees only the knots at a hole and an outside distance
     to the over-agreeing face resolved all 9,608 starts, against the pre-registered expectation: any resolving walk winds, so the
     winding is written in the state and the rule needs no plan. The sphere's local rule held one size past.
   - **Reading.** For the owner's picture: a handle turns the point into a pair held apart by the handle, and learning
     can make it vanish only by going around. What learning keeps is which way it went, a memory held by the handle. On the
     sphere learning only moved the dissonance; here it removes one that no change of behaviour can, and that lives in handles, as
     emergence does (question 9).
   - **Provenance.** Known with delta: in dimer language the classes are winding sectors (Kasteleyn's four Pfaffians) and a worm must
     wrap the torus to change sector. New: the reading as learning against change of state, the χ = 0 statement, the pair on the
     class-forced tori, the costs and the local rule.
   - **Next (taken by `NATIVE-TARGET-20261110-001`, below).** A native target for learning (backlog B61; Payoff 2/3, Concreteness 3/3): replace the outside
     distance by a signal the law and state supply. Alternatives: choosing the resolution (B62), learning that grows a handle (sub-goal
     B60), layers (sub-goal B54) ([decision note](../research/LEARN-HANDLES-20261109-001/learn_handles.md)).

   **2026-11-10: a native target for learning** (`NATIVE-TARGET-20261110-001`).
   - **The question.** The local rule above was told the distance to the over-agreeing face by the experimenter. Can a signal that the
     law and the state supply themselves do the same?
   - **Yes (computed, pre-registered).** On the class-forced tori, a learner that sees its own moves one to three ahead, and one that
     keeps the most states sharing the state's dissonance, resolve every run and beat random moves on every torus of at least 10 distinctions:
     at 40 distinctions 12.9 and 17.9 to 19.3 steps, against 64.4 for random moves and 7.5 with the outside distance. One size past, to 46
     distinctions, the same.
   - **Opposite charges attract.** The count of states sharing the dissonance is 2 (the state and its complement) when the holes are
     far from the over-agreeing face and grows as they approach, unevenly at contact. On the sphere same charges repelled; here a hole
     and the face of opposite charge attract. A learner keeping the fewest such states never resolves on the Fano tori.
   - **Reading.** The owner's "strength based on stability" has a native form: the point is drawn to its resolution by keeping its
     options open, with no outside map.
   - **Next (taken by `GROW-HANDLE-20261110-001`, below).** Learning that grows a handle (sub-goal B60; Payoff 3/3, Concreteness 2/3): a sphere's dissonance
     cannot be resolved, and splicing a Fano piece across a 3-edge cut adds exactly one handle (`THREEFOLD-SURFACES-20261030-001`), so
     splice one at the violated knot and learn ([decision note](../research/NATIVE-TARGET-20261110-001/native_target.md)).

   **2026-11-10: learning that grows a handle** (`GROW-HANDLE-20261110-001`).
   - **The question.** A sphere's forced dissonance can be moved but never removed. Can growth add a handle where it sits, so that learning
     then removes it, and does it matter where the handle grows?
   - **The grown pattern (proved).** Splicing a Fano piece (the Fano pattern less a distinction, the knot's own uniform contradiction) at a knot of a
     knot sphere, by one of the three bijections that keep both rotations, makes a torus; the old law extends with no even face, uniquely
     up to gauge.
   - **Growth alone does not resolve (computed, then proved from it).** In the grown class the piece acts exactly as the knot it replaced,
     and in the other three classes it is transparent (540 grown tori, K_2 to K_5). So the grown law is the only class no state satisfies:
     growth changes what forces the dissonance, from the count to the class.
   - **Learning then resolves it, through the new handle (proved).** With the state fixed, learning removes the dissonance completely, and
     every resolution changes a sign in the grown piece: going around the new handle is what makes the piece transparent.
   - **Placement sets the cost (computed).** Grown at the dissonance, the violated knot moves into the piece and learning resolves it in
     3 sign changes on every sphere; grown farther away it costs more (on K_5 a mean of 5.7 one knot away, 15.6 five away).
   - **Reading.** For the owner's picture: growth and learning together remove what neither removes alone, most cheaply when the pattern
     grows where the tension is.
   - **Later (`OTHER-ATOMS-20261110-001`).** Any torus piece whose torus has a class no state satisfies, and is free at its distinction, behaves
     the same way (proved); a piece whose torus satisfies every class is transparent in all four, and growing it deletes the knot's constraint.
   - **Next (taken by `CHOOSE-RES-20261110-001`, below).** Choosing the resolution (backlog B62): which of the classes a pair can end in a native rule can choose
     ([decision note](../research/GROW-HANDLE-20261110-001/grow_handle.md)).

   **2026-11-10: choosing the resolution** (`CHOOSE-RES-20261110-001`).
   - **The question.** A class-forced pair can be resolved into any of three other classes. Given a target, can a learner reach the one it
     is given, and where does a learner without a target end up?
   - **Choosing has a price (proved bound).** A resolution into a class costs at least the smallest cycle of its class change: 2 the short
     way around a thin torus, about half the torus the long way.
   - **A learner told the target reaches it (computed).** Keeping the class its own sign changes have made, it reached the target in
     3,173 of 3,186 runs, every one on the thin tori, within 0.4 sign changes of the cheapest walk; the misses entered the target face in
     the wrong sheet.
   - **Without a target, how it moves decides (computed).** Random moves end in the short class in only 13% of runs on thin tori of at
     least 20 distinctions; sight of radius 3 in 63%; the outside distance in 96 to 99%. The pre-registered default was wrong.
   - **Reading.** For the owner's picture: once there is a handle there is more than one resolution, a learner can pick one if it carries
     the choice, and the far one costs the handle's length.
   - **Next (taken by `GROW-STUCK-20261110-001`, below).** Grow where learning is stuck (backlog B68). Layers (sub-goal B54) became more concrete under the reading that an
     piece is a pattern standing for one knot ([decision note](../research/CHOOSE-RES-20261110-001/choose_res.md)).

   **2026-11-10: grow where learning is stuck** (`GROW-STUCK-20261110-001`).
   - **A floor on dissonance (proved).** Weighed as the count weighs it, violated knots plus over-agreement plus half the even faces is
     at least half the absolute Euler characteristic, in every state of every law: 1 on a sphere, 0 on a torus, g − 1 at genus g. The
     torus is the only drawing surface that forces no dissonance.
   - **One handle is exactly enough (proved).** Each Fano piece lowers χ by 2, so from a sphere one growth reaches the floor 0 and every
     further one adds a unit no learning removes.
   - **The stuck learner (computed).** A learner that steps only when some sequence of at most r steps lowers the dissonance, and grows an
     piece otherwise, is stuck at once on a sphere and grows at the dissonance. Seeing 3 steps ahead it grows once and resolves in 3 sign
     changes; seeing 2 or fewer it cannot see what its new handle offers and keeps growing, never resolving (K_2 to K_6).
   - **Reading.** Growing where you are stuck works only if you look far enough ahead to use what you grew; growing at every impasse piles
     up permanent dissonance.
   - **Next (taken by `ATOM-LAYERS-20261110-001`, below).** Layers through pieces (sub-goal B54) ([decision note](../research/GROW-STUCK-20261110-001/grow_stuck.md)).

   **2026-11-10: layers through pieces** (`ATOM-LAYERS-20261110-001`).
   - **The question.** A Fano piece spliced in for a knot acts from outside as that knot: the sphere is an upper level, each piece a lower
     level standing for one of its knots. With several pieces, where does the dissonance sit, and can learning move it between levels?
   - **Down, yes (computed).** Growing a piece at the dissonance moves it into the piece, and learning resolves it there. Away from the
     dissonance the resolution still passes through the piece, but a learner seeing 4 steps ahead cannot find it and stays stuck above.
   - **Up or across, no (proved).** At genus 2 the remaining unit is one over-agreeing face with no violated knot or even face, so no
     learning step exists there; a learner that holds the state still and never raises the dissonance cannot move it.
   - **Each extra piece carries its own unit (computed).** A second piece holds one over-agreeing face from the moment it is grown, and that is
     where the dissonance ends.
   - **Reading.** The point flows down into named patterns and settles; to move it again something must raise the tension, a moving state
     or a learner that accepts a temporary rise.
   - **Next (taken by `MOVING-STATE-20261110-001`, below).** Let the state move while learning acts (backlog B71), the first challenge of A26
     ([decision note](../research/ATOM-LAYERS-20261110-001/atom_layers.md)).

   **2026-11-10: let the state move while learning acts** (`MOVING-STATE-20261110-001`, the challenge of A26).
   - **The question.** Every learning result so far held the state still. Let the point move: between learning steps the state may flip
     one distinction, never raising the dissonance.
   - **A moving point frees learning (computed).** Where the fixed-state learner made no step, about half the runs now resolve or reach
     the floor (23 of 50 with one piece away, 28 of 50 with two): the point walks to where learning can act.
   - **A settled unit stays in its pattern (computed).** At the genus-2 floor the unit wanders under such flips, but only inside the piece
     it settled in and at that piece's junction faces, never into the other piece or the upper level (exhaustive on K_2).
   - **Verdict.** A26 Overturned as a limit on what learning reaches, by the rule frozen before the run; its fixed-state results stand as
     such, and the moving-state reading is A50.
   - **Reading.** Named patterns are traps at constant tension: a point can move inside one but not out of it.
   - **Next (taken by `RISE-ESCAPE-20261110-001`, below).** A learner that accepts a temporary rise (backlog B72): does a bounded rise let the point leave the trap
     ([decision note](../research/MOVING-STATE-20261110-001/moving_state.md)).

   **2026-11-10: a temporary rise** (`RISE-ESCAPE-20261110-001`).
   - **The question.** Can a unit settled in a piece leave it if the dissonance may rise for a while?
   - **Not by moving the state (computed).** With the law fixed and the state allowed one unit above the floor for as long as it likes,
     the unit never reaches the other piece or the upper level: exhaustively on five of K_2's components (up to 195,264 states each), and
     to a cap of 200,000 states elsewhere. With the state fixed there is no learning step at the floor at all (proved).
   - **Reading (unchecked).** Which piece holds the leftover may be fixed by what was learned, the law's class, so that only learning, at a
     rise where violated knots appear, could move it.
   - **Next (taken by `LAW-HOLDS-20261110-001`, below).** Does the law decide which piece holds the unit (backlog B79)
     ([decision note](../research/RISE-ESCAPE-20261110-001/rise_escape.md)).

   **2026-11-10: the law decides where the leftover lives** (`LAW-HOLDS-20261110-001`).
   - **Exact (SAT over every state).** On 15 genus-2 drawn knot patterns the floor unit can sit only inside a Fano piece that still acts as its knot,
     or at that piece's junctions. Across all 16 sign classes: both pieces acting leaves no floor state (the sphere's contradiction
     returns), one acting holds the unit, both transparent lets it sit in either piece and at the upper level when the pieces are apart.
   - **Reading.** The leftover tension lives in whichever named pattern still stands for its knot. Where it sits is a learned fact, not a
     fact about the point, so only learning can move it.
   - **Next (taken by `LEARN-RISE-20261110-001`, below).** Learning at a rise (backlog B80): swap the two pieces' roles by learning, one unit above the floor
     ([decision note](../research/LAW-HOLDS-20261110-001/law_holds.md)).

   **2026-11-10: learning at a rise** (`LEARN-RISE-20261110-001`).
   - **The question.** The leftover sits in whichever piece acts as its knot. With the state moving and learning acting, one unit above
     the floor, can it be carried to the other piece?
   - **Yes, post hoc (computed).** The pre-registered breadth-first search ran out of room at about four moves. A targeted search over the
     same moves, aimed at a law in which the other piece acts as its knot, found paths from all 9 starts: 16 to 43 moves, 4 to 16 of them
     learning steps. The pieces' roles swap, and the tension follows.
   - **Reading.** The point and learning together move a pattern's tension: the state carries the dissonance around, learning rewrites
     which pattern stands for the contradiction, and the tension settles where learning puts it.
   - **Next (taken by `ADDRESS-20261110-001`, below).** Learning chooses which piece holds the leftover (backlog B81), a learned address
     ([decision note](../research/LEARN-RISE-20261110-001/learn_rise.md)).

   **2026-11-10: a learned address** (`ADDRESS-20261110-001`).
   - **The role swap confirmed.** On six K_3 starts not used before, a frozen prediction held: learning at a rise, with the state moving,
     carried the leftover to the other piece from every one.
   - **Learning writes an address (computed, pre-registered).** With three pieces and two leftover units, every pair of pieces was reached
     as their holders, on all three knot orbits of K_3; the named pieces end acting as their knots, the third transparent.
   - **Reading.** The leftovers behave as a memory: written by learning, held by the law in every state, untouched by the point's own
     motion, and read off by where the tension sits.
   - **Next (taken by `READ-ADDRESS-20261110-001`, below).** Reading the address natively (backlog B85)
     ([decision note](../research/ADDRESS-20261110-001/address.md)).

   **2026-11-10: reading the address** (`READ-ADDRESS-20261110-001`).
   - **Writing holds one size past (computed).** On K_4 with three pieces, the two leftovers were written into every pair on every knot
     orbit (15 of 15; 24 of 24 with K_3).
   - **The law reads it, piece by piece (computed).** In 23 of 24 written configurations the holders are exactly the pieces whose own signs
     make them act as their knots; the read needs no state and no census. The exception had one acting piece for two units.
   - **A random state does not show it.** About one random state in six has its over-agreement in exactly the holder pair.
   - **Next (taken by `ADDRESS-STEER-20261110-001`, below).** Does the stored address steer later learning (backlog B86)
     ([decision note](../research/READ-ADDRESS-20261110-001/read_address.md)).

   **2026-11-10: the stored address steers later learning** (`ADDRESS-STEER-20261110-001`).
   - **The rule (exact on 1,280 classes of 11 drawn knot patterns).** If every piece acts as its knot, no state satisfies every knot; otherwise every
     acting piece holds a unit of the floor dissonance and further units are free. Each piece's role is set by its own handle's class. The
     earlier exception was a class with fewer acting pieces than units.
   - **Four pieces (computed).** Every triple of four pieces was written as the holders on every knot orbit of K_3 (12 of 12).
   - **Memory survives a fresh tension (computed).** After one random flip of the upper level a learner returned to the written acting
     pieces in 240 of 240 runs, and after two or three in 463 of 480.
   - **Reading.** Learning writes which patterns stand for their knots, the law keeps it, and a new disturbance settles back into it. All
     on small cases.
   - **Next.** Several addresses in sequence (B88, taken by `ADDRESS-SEQ-20261110-001`, below), then a proof of the piece rule (B87)
     ([decision note](../research/ADDRESS-STEER-20261110-001/address_steer.md)).

   **2026-11-10: a rewritable address** (`ADDRESS-SEQ-20261110-001`).
   - **Written in turn (computed).** 90 addresses written one after another on 14 drawn knot patterns, from K_3 to K_5 and with three or four pieces,
     each followed by a random disturbance: every write reached its target and every address was held, never reverting to the one before.
   - **The unsettled returns explained (computed).** Of the 17 earlier runs that did not settle back, 7 lost a piece's bit through a
     learning step that wound through its handle, exactly as the rule allows, and 10 stopped one unit above the floor.
   - **Reading.** The learned network holds a register: written by learning, rewritten cleanly, robust to disturbance.
   - **Next (taken by `ATOM-RULE-20261110-001`, below).** A proof of the piece rule (backlog B87)
     ([decision note](../research/ADDRESS-SEQ-20261110-001/address_seq.md)).

   **2026-11-10: the piece rule proved** (`ATOM-RULE-20261110-001`).
   - **The theorem (computer-assisted).** On every octahedral knot sphere with separated Fano pieces, each piece acts as its knot in exactly
     one of the four classes of its own handle, independently of the others; if every piece acts, no state satisfies every knot; otherwise
     every acting piece holds a unit of the floor dissonance.
   - **The proof.** Each piece's handle is a direct summand of the homology and its role depends only on its own signs (by hand); a finite
     local check shows that in the acting class no state of the piece's neighbourhood satisfies its knots with at most one agreeing corner
     at each of its faces (2,700 splices); and knot neighbourhoods come in four types over K_2 to K_8, none new beyond K_3, because the sphere
     is the triangular lattice away from six corners.
   - **Reading.** Which patterns hold the tension is a rule, not an accident of the small cases.
   - **Later (`OTHER-ATOMS-20261110-001`).** The rule holds by hand for every class-forced free torus piece on any Kasteleyn host, pieces
     adjacent or not, so neither the Fano pattern nor separation nor the octahedral sphere is needed.
   - **Next (taken by `LEARN-NOTE-20261110-001`).** A note on the learning line (backlog B95), written up as
     [the learning line](../research/LEARN-NOTE-20261110-001/learning_line.md); its next step, other pieces (backlog B97), was taken by
     `OTHER-ATOMS-20261110-001`, below ([decision note](../research/ATOM-RULE-20261110-001/atom_rule.md)).

   **2026-11-10: any class-forced handle remembers** (`OTHER-ATOMS-20261110-001`).
   - **The question.** Backlog B97, the challenge of A48: every learning result so far grew the Fano piece. Does the memory need the Fano
     pattern?
   - **The theorem (by hand).** A torus piece, a torus drawn knot pattern less a distinction, grown at a knot of any orientable drawn knot pattern with a
     Kasteleyn law, allows on its three outer distinctions what its torus allows with that distinction split in three: the replaced knot's six
     patterns in a class where the torus has no satisfying state, all eight where it has one, provided the torus is free at the distinction
     (flipping any one of the distinction's sides leaves a satisfiable law). Where it acts it holds a unit. So the piece rule holds for such pieces
     on any host, adjacent ones included, with no local check.
   - **Which tori (computed).** Every lattice torus to 30 distinctions is free. The ones with a class no state satisfies are the Fano torus and
     the thin tori of even index, so twenty pieces up to 40 distinctions remember, the smallest with four distinctions; every other piece is transparent
     in every class. Thin-torus pieces wrote and held addresses as the Fano piece does.
   - **Reading.** A handle remembers because its torus has a sign class that no state can satisfy: the bit lives in the class.
   - **Next (taken by `NEST-ATOMS-20261110-001`, below).** Pieces within pieces (backlog B104): a sphere carrying two pieces, less a
     distinction, as one piece ([decision note](../research/OTHER-ATOMS-20261110-001/other_atoms.md)).

   **2026-11-10: pieces within pieces** (`NEST-ATOMS-20261110-001`).
   - **The question.** Backlog B104: is a knot sphere that already carries pieces, less a distinction, a piece of the next level?
   - **The theorem (by hand).** Yes. If the sphere has a state violating any one chosen knot and no other, and its pieces each act in
     exactly one class and are free, the composite acts as its knot exactly where every piece inside acts, whichever distinction is removed, and
     it is again a piece of the same kind, so composites nest to any depth. A composite of genus g holds g − 1 units, g where it acts.
   - **Computed.** The AND held at 274 removed distinctions of seven composites, exactly on 576 classes, and 11 of 12 two-level addresses
     written by learning held after a disturbance, every outer address with them.
   - **Reading.** For the owner's layers: a group of patterns cut off by three sides reads from outside as one pattern, standing for its
     knot only when every pattern inside does. Each level sees the one below as an AND; acting only adds constraints, so no host makes a
     level read anything but a monotone function of the bits below.
   - **Next (taken by `MANY-POINTS-20261110-001`, below).** Many distinctions at once (backlog B3); in knot, whether any host gives an OR
     (backlog B109) ([decision note](../research/NEST-ATOMS-20261110-001/nest_atoms.md)).

   **2026-11-10: many distinctions at once** (`MANY-POINTS-20261110-001`).
   - **The question.** Backlog B3, the owner's parallel picture: can several distinctions of dissonance move through the layered memory with
     no scheduler choosing an order, and where can units of the floor dissonance sit together?
   - **Where units sit (proved, checked exactly).** With two composites and three floor units, no region holds three, the composites
     never act together, and an acting composite holds exactly two, one in each leaf; every placement the rule allows occurs.
   - **Distinctions at once (computed).** Two disturbances in different composites learned away independently in every order of their moves,
     with the address kept, in all 320 sampled pairs. Nearby pairs interacted, mostly by cancelling; after the run it was seen that only
     pairs sharing a knot did.
   - **Reading.** For the owner's "parallelized" picture: distinctions that do not share a knot can be updated in any order, and the memory
     keeps what it was told; distinctions on one knot meet.
   - **Corrected (`COMPOSITE-FN-20261110-001C`).** Not every such pair: one of 1,200 fresh distant pairs met, because one distinction's repair
     reached a knot through the other. Distinctions combine in any order when what each one and its repair touch is disjoint (proved).
   - **Next (taken by `COMPOSITE-FN-20261110-001`, below).** Which functions a composite computes (backlog B109)
     ([decision note](../research/MANY-POINTS-20261110-001/many_points.md)).

   **2026-11-10: the layers only conjoin** (`COMPOSITE-FN-20261110-001`).
   - **The question.** Backlog B109: can some host make a composite read an OR, or anything but the AND of the bits inside it?
   - **The theorem (by hand).** A composite acts where its host, with its transparent pieces' knots deleted, has no satisfying state, so
     it computes an OR of ANDs over the host's minimal unsatisfiable sets of knots. On a knot sphere every knot can be violated alone: any
     set of knots touches at least two more faces than it has knots, and Hall's theorem does the rest. Growth keeps this, so over every
     host built from knot spheres and class-forced lattice tori, a composite computes exactly the AND.
   - **Computed.** Seven branched covers, the frozen search outside that class, had no unsatisfiable class at all.
   - **Reading.** The layers say "all of these": every pattern the program can grow is held together by every one of its knots.
   - **Next (taken by `NATIVE-ATOM-20261110-001`, below).** Which piece a growth law grows (backlog B106)
     ([decision note](../research/COMPOSITE-FN-20261110-001/composite_fn.md)).

   **2026-11-10: which handle grows a memory by itself** (`NATIVE-ATOM-20261110-001`).
   - **The question.** Backlog B106: can a growth rule with nothing designed in grow a handle that remembers where a dissonance sits?
   - **The answer (by hand).** A rule that splices the same torus at every violated knot, with the same signs on every knot, grows a
     remembering handle only if the torus carries the Fano pattern and the signs are constant: the plain law contradicts itself only on the Fano
     pattern (`UNIFORM-FANO-20261107-001`). Every other class-forced handle grows open and lets the dissonance go.
   - **Computed.** All 1,256 uniform laws on 157 lattice tori agree; the growth was checked exactly on K_2 and K_3; and learning wrote and
     held 9 of 9 addresses into two open thin handles.
   - **Reading.** The Fano pattern's torus is the one handle a uniform rule can grow closed; any other handle is memory in waiting, which learning
     closes.
   - **Next (taken by `NAME-LAYERS-20261110-001`, below).** Layers through a naming knot
     ([decision note](../research/NATIVE-ATOM-20261110-001/native_atom.md)).

   **2026-11-10: two ways for one level to speak to the next** (`NAME-LAYERS-20261110-001`).
   - **The question.** A parity name (a variable named by the parity of two below) and a three-edge cut (a group sealed off by three
     sides): one kind of layer, or two? And can a distinction cross levels through each?
   - **The answer (by hand).** Two. Through a cut a contradiction below becomes a constraint above, so a distinction crosses levels. Through a
     name it cannot: the level below keeps its own contradiction, and so does the level above.
   - **Computed.** Names carry something cuts cannot: correlations of the states below that change with the law below, down to a single
     excluded pattern, a clause.
   - **Reading.** A cut tells the level above whether everything inside holds; a name tells it how the parts match. A network with
     both may compute more than conjunctions, which is the next phase's first question (sub-goal B118).
   - **Next (taken by `GATES-20261110-001`, below).** A learned network that computes, sub-goal B118
     ([decision note](../research/NAME-LAYERS-20261110-001/name_layers.md)).

   **2026-11-10: AND and OR, but no NOT yet** (`GATES-20261110-001`).
   - **The question.** Sub-goal B118: do cuts and names together compute every function of the stored bits?
   - **Proved.** If any part of a network holds a contradiction of its own, the whole network does, so every reading says yes wherever
     every stored bit is set; and a stored pattern seen only from outside its three sides can never be read negated.
   - **Computed.** 43,091 small networks read "all of these" and "any of these", single bits and constants, but never "not this".
   - **Reading.** The layered memory reasons monotonically so far. After the run, names were seen to read a finer signal, the parity of
     how a pattern's tension is wound, which is the next place to look for a negation.
   - **Corrected (`NOT-INSIDE-20261110-001`).** That finer signal reads the frame (the particular signing), not the winding.
   - **Next (taken by `CLASS-READ-20261110-001`, below).** Reading the class, not the bit (backlog B122)
     ([decision note](../research/GATES-20261110-001/gates.md)).

   **2026-11-10: the class is read upward only** (`CLASS-READ-20261110-001`).
   - **The question.** Backlog B122: a stored pattern can be wound four ways. Read by names, do all four ways give the missing negation?
   - **Computed.** On new networks, names read only three things about a pattern's winding: it holds the contradiction; it holds the
     contradiction or its states as tightly as possible; anything. Two patterns together give no more.
   - **Reading.** The winding is stored memory, but the network reads it only against two landmarks the law fixes, and only upward, so
     "not this" is still missing.
   - **Corrected (`NOT-INSIDE-20261110-001`).** Those readings read the frame, the particular signing each winding was given, not the
     winding: a reading of the windings alone sees only which patterns hold a contradiction.
   - **Next (taken by `NOT-INSIDE-20261110-001`, below).** Negation inside a cut leaf (backlog B123)
     ([decision note](../research/CLASS-READ-20261110-001/class_read.md)).

   **2026-11-10: "not this" needs a record of the path** (`NOT-INSIDE-20261110-001`).
   - **The question.** Backlog B123, the deciding question for gates: with names reading inside a stored pattern, does a network ever say
     "not this", or is every reading monotone?
   - **Proved.** A reading that looks only at how each pattern ended up, its winding, says yes whenever more patterns hold their
     contradiction, and cannot tell apart two windings that hold none: where a network allows one such winding, it allows the other once
     the pattern's inner distinctions are flipped to match.
   - **Computed.** Fix one exact way of writing each winding, and a network does say "not this" for each of three patterns; write the
     same winding another way and it stops. The earlier readings against two landmarks were readings of that fixed way of writing.
   - **Reading.** The layered memory can say "all of these" and "any of these" about what it stores, and nothing more. To say "not this"
     it has to know how each pattern was wound, not only which way it ended up, and that is a record of the path learning took.
   - **Next (taken by `NATIVE-WRITE-20261110-001`, below).** Native writing (backlog B119), with a frame that learning itself fixes as a
     further question (backlog B126) ([decision note](../research/NOT-INSIDE-20261110-001/not_inside.md)).

   **2026-11-10: the memory writes itself** (`NATIVE-WRITE-20261110-001`).
   - **The question.** Backlog B119: every stored pattern so far was written by a search told exactly what to aim for. Can a learner
     that feels only its own tension, and is told only which patterns should hold, write them?
   - **Proved.** A pattern that holds its contradiction keeps some tension in it in every state, however the distinctions are set. So a
     learner can test whether a pattern holds by letting its distinctions wander without learning: if the tension there ever goes away, the
     pattern does not hold.
   - **Computed.** A learner that runs this test, and changes the law only in the patterns whose answer is wrong, wrote 100 of 100
     requested words exactly on five memories of up to six patterns, and every word survived a disturbance. Reading the tension at a
     single moment instead fooled it 84 times in 100: a loose bit of tension can sit in a pattern that does not hold.
   - **Reading.** A stored 1 is a tension the point cannot walk away. The point both writes the memory and reads it, and no one tells
     it the configuration to aim for.
   - **Next (taken by `IN-OUT-20261110-001`, below).** Inputs and outputs (backlog B120): learning from examples, with the outside holding
     some distinctions ([decision note](../research/NATIVE-WRITE-20261110-001/native_write.md)).

   **2026-11-10: a held knot is a gate** (`IN-OUT-20261110-001`).
   - **The question.** Backlog B120: let the outside hold two distinctions of a stored pattern and read the third. What can the memory compute
     this way, and can it learn a chosen answer from examples?
   - **Proved.** Flipping every distinction at once never changes the tension, so whatever the memory answers for some inputs, it answers the
     opposite for the opposite inputs. That rules out "both", "either" and "exactly one" of two inputs. Flipping one distinction's frame
     negates that input or the answer, so the inputs the outside holds give the memory the frame it lacked for "not this".
   - **Computed.** A pattern that holds its contradiction is a gate: when the two held distinctions agree the third is forced to their
     opposite, otherwise it is free. A learner that feels only its own tension, taught by the outside holding the answer it wants, learned
     such gates from four examples at 53 of 56 single patterns and switched them off, but almost never through a pattern of patterns.
   - **Corrected (`CREDIT-PIN-20261110-001`).** That failure was mostly a stall in the learner; fixed, it reached gates through a pattern
     of patterns about half the time, though at many times the cost.
   - **Reading.** Through a pattern of patterns the examples see only whether every inner pattern holds, so until all do, every example
     looks the same: the learner gets no hint which part to change. Each holding part does keep a tension it cannot walk away, which the
     learner could use as a hint.
   - **Next (taken by `CREDIT-PIN-20261110-001`, below).** Credit from pinned dissonance (backlog B132), tied with three held inputs
     (backlog B133) ([decision note](../research/IN-OUT-20261110-001/in_out.md)).

   **2026-11-10: the memory feels which knots hold** (`CREDIT-PIN-20261110-001`).
   - **The question.** Backlog B132: can the tension a holding knot keeps, which the distinctions cannot walk away, guide the learner to the
     knots inside a knot that the examples cannot point to?
   - **Computed, first.** The learner had stalled, not failed: fixed, it learned gates through a pattern of patterns 10 times in 16, by
     trial, at about thirty times the cost of a single pattern.
   - **Computed, then.** Tension that a wandering of the distinctions never clears sat in a holding knot every one of 4,473 times. Keeping
     those parts fixed made the inner knots faster to find, but the learner did no better on the whole, because its check of an
     answer, holding the inputs and wandering, sometimes misses the wrong answer and says yes too soon.
   - **Reading.** The memory can feel what it stores without being told; what it lacks is a check that never says yes too soon.
   - **Corrected (`STURDY-PROBE-20261110-001`).** With a check that does not say yes too soon, keeping what holds does make it better:
     it then learned every gate through every pattern of patterns.
   - **Next (taken by `STURDY-PROBE-20261110-001`, below).** A probe that is not fooled (backlog B134)
     ([decision note](../research/CREDIT-PIN-20261110-001/credit_pin.md)).

   **2026-11-10: look four times before saying yes** (`STURDY-PROBE-20261110-001`).
   - **The question.** Backlog B134: the learner checks a wanted answer by holding the inputs and the wrong answer and wandering; if it
     never settles, it believes the wrong answer impossible. Too short a wander says yes too soon. Does a longer look fix it?
   - **Computed.** Looking four times, three from somewhere new and each longer, it never said yes too soon in 195 trials, and never
     accepted "both" of two inputs, which no knot can compute. It cost two and a half times the looking.
   - **Reading.** With that check, a learner that feels only its own tension, and keeps the parts whose tension it cannot walk away,
     learned every gate it was asked for, inside patterns of patterns too.
   - **Next (taken by `THREE-IN-20261110-001`, below).** Three held inputs (backlog B133): self-duality allows majority and parity, the
     strongest test of what the held distinctions let the memory compute ([decision note](../research/STURDY-PROBE-20261110-001/sturdy_probe.md)).

   **2026-11-10: three held distinctions never count or vote** (`THREE-IN-20261110-001`).
   - **The question.** Backlog B133: with two held distinctions the memory can only gate, copy or negate. With three, "opposite inputs give
     the opposite answer" still allows a vote (majority) or a count (parity). Does a learned knot compute either?
   - **Exact.** Reading every way of holding three distinctions around a stored pattern, on every law of six drawn knot patterns, nearly three million
     ways: never a vote, never a count, and never an answer that one input pushes both up and down. The only full answers follow one
     input and ignore the other two.
   - **Computed.** A learner asked for a count or a vote never pretended it had one.
   - **Reading.** What the outside holds reaches a learned knot's answer only one way round. Plain logic of this kind can count with hidden
     helpers, so the limit belongs to the drawn knot pattern; whether it holds everywhere is open.
   - **Corrected (`UNATE-20261111-001`).** It does not hold everywhere: a small drawn knot pattern with many handles counts three held distinctions
     exactly. The limit belongs to the learned memories' interfaces, not to drawn knot patterns.
   - **Next (taken by `DEEP-MEM-20261111-001`, below, when the line resumed).** Deeper memories from examples (backlog B135)
     ([decision note](../research/THREE-IN-20261110-001/three_in.md)).

   **2026-11-11: depth is free** (`DEEP-MEM-20261111-001`).
   - **The question.** Backlog B135: can the learner reach a stored pattern buried three levels down, or three patterns that must all
     hold before the outside sees anything?
   - **Computed.** Every time it was asked, 40 times out of 40, from four examples and its own tension. A pattern two levels down was
     as quick to reach as one at the surface; a second pattern beside the first cost about eighteen times the time; a third cost no more.
   - **Reading.** Keeping the parts whose tension cannot be walked away lets the learner build a pattern of patterns one part at a time;
     what still limits the memory is what it can compute: every answer it gives is a gate.
   - **Next (taken by `UNATE-20261111-001`, below).** Are maps of held distinctions unate (backlog B136): whether "never counts, never votes" is
     a theorem ([decision note](../research/DEEP-MEM-20261111-001/deep_mem.md)).

   **2026-11-11: knots can count** (`UNATE-20261111-001`).
   - **The question.** Backlog B136: the memories never counted or voted. Is that true of every drawn knot pattern?
   - **No (exact).** Eight distinctions tied by eight knots on a surface with four handles count exactly: hold any three, and a fourth is forced
     to their parity, every time. Small drawn knot patterns vote (majority) often.
   - **Reading.** The memories never count because of where their knots sit, each pattern of tension in its own handle, not because knots
     cannot. Counting needs many handles close together, crossings that a drawing on a sphere cannot make.
   - **Next (taken by `PARITY-NEEDS-20261111-001`, below).** What a drawn knot pattern needs to count (backlog B147), then whether a learned memory
     can grow such a place (sub-goal B146) ([decision note](../research/UNATE-20261111-001/unate.md)).

   **2026-11-11: one handle is enough to count** (`PARITY-NEEDS-20261111-001`).
   - **The question.** Backlog B147: how many handles does counting need?
   - **Exact.** One. A knot pattern of eight distinctions drawn on a torus, wound into its tightest winding, forces a fourth distinction to the parity of any three
     held ones; sixteen small tori do it, always in their tightest pattern. The first counting pattern, checked again by fresh code with the
     canonical knot test, holds up.
   - **Reading.** A pattern drawn on a sphere cannot count unless every hard problem is easy; one handle suffices. The memories' own pieces are tori too, so
     the question is whether learning can wind one into its tightest pattern with the held distinctions inside it.
   - **Next (taken by `LEARN-PARITY-20261111-001`, below).** A learned memory that computes parity (sub-goal B146)
     ([decision note](../research/PARITY-NEEDS-20261111-001/parity_needs.md)).

   **2026-11-11: the memory learns to count** (`LEARN-PARITY-20261111-001`).
   - **The question.** Sub-goal B146: can the learner, feeling only its own tension and taught by the outside holding the answers, wind a torus
     piece into the winding that counts, and keep it there?
   - **Computed.** Every time: 20 runs of 20, on the torus alone and grown inside a larger memory, it learned the parity of three held
     distinctions from eight examples, kept it when shaken, turned it into its opposite and back.
   - **Reading.** The memory is no longer limited to "all of these", "any of these" and gates: it counts. What it stores is still which
     way the torus is wound; counting is what that winding does to distinctions held inside it.
   - **Next (taken by `PARITY-FIVE-20261111-001`, below).** Whether one torus counts more distinctions (backlog B149), and whether tori can be
     wired into larger functions (sub-goal B148) ([decision note](../research/LEARN-PARITY-20261111-001/learn_parity.md)).

   **2026-11-11: one torus counts three, and two go quiet** (`PARITY-FIVE-20261111-001`).
   - **The question.** Backlog B149: can one torus count five held distinctions into a sixth? (An even number can never be counted: flipping
     every distinction always flips the read distinction, but it leaves the parity of an even number of held distinctions unchanged.)
   - **Exact.** Not among the 421 lattice tori of up to 24 distinctions, in any winding; only tori of 8 to 18 distinctions count even three. This
     is the range searched, not a limit on what one handle can do.
   - **Two tori on one sphere count nothing.** One counting torus piece grown on the knot sphere ties six of the sphere's distinctions into a
     wire that carries its count. Growing a second torus piece at the sphere's other knot unties that wire: no distinction is forced by any others in any
     winding (exact; the wire was found after the run).
   - **Reading.** To count more, tori must be wired together, and the wire has to survive the second torus.
   - **Next (taken by `SHARED-COUNT-20261111-001`, below, re-posed for overlapping bases).** A host where two counting tori stay wired
     (sub-goal B148's first step) ([decision note](../research/PARITY-FIVE-20261111-001/parity_five.md)).

   **2026-11-11: two counting copies that share a distinction count five, and the learner finds it** (`SHARED-COUNT-20261111-001`).
   - **The question.** The owner's direction: knots that overlap freely, not only as a drawing allows. Two copies of the 8-distinction
     counting pattern (2, 0, 4) (a drawn knot pattern, the literature's torus) are made to share one distinction: the distinction the first
     copy reads is an input of the second. Does the pair count five held distinctions, and does the learner learn it?
   - **Exact, by definition.** Yes: the first copy's count feeds the second through the shared distinction, so the read distinction is the
     sum mod 2 of all five held ones, exactly when both copies sit in their tightest class.
   - **Computed.** The learner, feeling only its own tension under the world's held answers, learned the count of five and kept it when
     shaken, 10 runs of 10, its opposite and back again too; it took about fifteen times as many steps as one copy alone. Three copies, the
     count of seven, were not learned within two hours a run.
   - **Reading.** Grown together on one drawing, the same two copies count nothing (the entry above). Sharing a distinction by identity
     leaves nothing to untie: the overlap computes, and is learned, where the drawing failed. The shared distinction lies in six knots, so
     the pair is no longer one drawn pattern; the learner still feels each copy's own drawn faces.
   - **Next (taken by `UNDRAWN-LEARN-20261111-001`, below).** A learner whose tension needs no drawing at all (sub-goal B153)
     ([decision note](../research/SHARED-COUNT-20261111-001/shared_count.md)).

   **2026-11-12: without the drawing, the learner forgets as fast as it learns** (`UNDRAWN-LEARN-20261111-001`).
   - **The question.** Sub-goal B153: the learner felt part of its tension at the faces of a drawing. Feeling tension only at knots that
     are broken, as a base with no drawing allows, does it still learn the counts?
   - **Computed.** No: 0 runs of 10 kept the count, on one copy, on two copies sharing a distinction, and on a base of 6 distinctions and 8
     knots that no drawing fits. When the learner did reach the count and was then shaken, it mended itself by rewriting its own rules as
     readily as by changing its state, and the count washed out.
   - **Exact.** On one copy, 4 of its 512 laws count; with faces the learner can only rest among 4 laws, 1 of which counts. The 6-distinction
     base counts three held distinctions in exactly 1 of its 2,048 laws, with fewer distinctions than any drawn pattern found to count.
   - **Reading.** The drawing did two jobs: it narrowed where the learner could rest, and it made rewriting a rule cost something. That
     cost was the memory. A base in the owner's sense has no drawing, so learning there needs another reason for a rule to stay put.
   - **Next (taken by `LAW-RIGIDITY-20261112-001`, below).** Which of the two jobs learning needs, and a source for it on a base with no
     drawing (sub-goal B158) ([decision note](../research/UNDRAWN-LEARN-20261111-001/undrawn_learn.md)).

   **2026-11-12: a list of rules to settle on, and a reason to keep one** (`LAW-RIGIDITY-20261112-001`).
   - **The question.** Sub-goal B158: the drawing did two jobs. It narrowed where the learner may settle, and it made rewriting a rule cost
     something. Which does learning need, and can a base with no drawing supply it?
   - **Computed, one copy.** Allowed to settle only where the drawing allows, but feeling no more of the drawing than that, the learner
     found the count every time and kept it 4 times in 10. When its repairs could only change its state, never its rules, it kept every
     write. Finding needs the list; keeping needs the reason.
   - **Computed, a base no drawing fits.** A rule needs only the knots: a rule's signs add up to some value around every shortest cyclic
     sequence of knots and distinctions, here two knots sharing two distinctions. Asking for 0 everywhere left the 6-distinction base two rules to
     settle on, one of them counting, and the learner found and kept the count every time, 30 writes of 30. The reason to keep it was
     still ours (repairs change only the state).
   - **Exact.** The same request makes counting impossible on the drawn copy, where every counting rule adds up to 1 around those sequences;
     asking for 1 leaves the undrawn base nothing to settle on. The knots alone did not choose one request for both.
   - *Narrowed (`NATIVE-GRADE-20261112-001`).* On two more undrawn patterns from the same search, no request of this kind leaves a counting
     rule to settle on; the success above belongs to the 6-distinction pattern.
   - **Next (taken by `NATIVE-GRADE-20261112-001`, below).** A reason to keep a rule that comes from the knots too: counting each sequence
     that adds up wrong (sub-goal B160) ([decision note](../research/LAW-RIGIDITY-20261112-001/law_rigidity.md)).

   **2026-11-12: a grade of the knots keeps a count where the knots overlap enough** (`NATIVE-GRADE-20261112-001`).
   - **The question.** Sub-goal B160: can the knots also give the reason to keep a rule? Ask only that the sums around all the shortest
     cyclic sequences agree with one another, no value chosen, and charge for each sequence that would have to change.
   - **Computed.** The learner found the count every time on both patterns. On the 6-distinction pattern, where most of a rule's signs sit
     on two or more of those sequences, it kept it 8 times in 10 at the first count (19 writes of 30). On the drawn copy, where each sign
     sits on one at most, it kept it 6 times in 10: there the grade costs nothing to undo.
   - **Exact.** On two other undrawn patterns, no request of this kind leaves a counting rule to settle on.
   - **Reading.** How many short sequences share a sign sets how much it costs to rewrite it: rigidity is a property of how the knots
     overlap. Which sequences to ask about is still open, and the learner still finds the count no faster than by chance among the rules
     it may settle on.
   - **Next (taken by `SEARCH-AUDIT-20261112-001` and B161, below).** Which cyclic sequences the knots should fix, on every pattern (B161)
     ([decision note](../research/NATIVE-GRADE-20261112-001/native_grade.md)).

   **2026-11-12: the learner was never taught by its examples** (`SEARCH-AUDIT-20261112-001`).
   - **The question.** Did the examples ever help the learner find what it learned faster than drawing rules at random among those it may
     settle on?
   - **Computed.** No, in any of the 91 cases the line called learned: parity, the count of five, gates, memories, written addresses. It
     found its targets no faster than blind draws, and usually slower: in 10 runs of 100, where blind draws would manage 50. It wanders, it
     tries each rule it settles on against the examples, and it stops at one that fits.
   - **Reading.** Everything above that says "learned" means found by a search the examples stop, then kept. Keeping is real; being taught is
     not shown. With a blind search, how many rules the learner may settle on per right rule is the whole cost.
   - **Next (B161 taken by `WHICH-SEQUENCES-20261112-001`, below).** Fewer rules to settle on, chosen by the knots (B161), and a learner its
     examples steer (B165) ([decision note](../research/SEARCH-AUDIT-20261112-001/search_audit.md)).

   **2026-11-12: the knots alone do not choose where to look** (`WHICH-SEQUENCES-20261112-001`).
   - **The question.** Since the learner searches blindly, fewer rules to settle on per right rule is the whole saving. Can the knots, by
     some request about the sums around their short cyclic sequences, made the same way on every pattern, keep the counting rule among the
     few?
   - **Exact.** No, across 13 patterns: of 16 such requests, the best keeps the counting rule on 2 and hides it on the other 11. Random
     targets do no better, so this is not chance.
   - **Symmetry.** On the two undrawn patterns that have symmetries, the counting rule is one the symmetries fix, which few rules are. On the
     drawn copy, whose symmetries move the place where the count is read, it is not; most small patterns have no symmetry at all.
   - **Reading.** Where to look cannot be read off the knots this way; the learner will have to be steered by what it is taught.
   - **Next.** A learner whose examples steer it (sub-goal B165), awaiting a go-ahead
     ([decision note](../research/WHICH-SEQUENCES-20261112-001/which_sequences.md)).

   **2026-11-07: a beginning is a knot, and growth needs a shared coin** (`GROWTH-LAW-20261107-001`).
   - **The question.** Backlog B1: written as a law, with its history as variables, what can a growth order add to a static law?
     No scheduler may supply an input, so a result belongs to the law only if it holds in every growth order.
   - **The order never knots with the grown pattern (proved).**
     - **A fixed pattern.** For a rule that reads only the law, the history and the states of a fixed pattern form a product.
     - **Patterns that vary.** With absent things forgotten, every knot that contains an order variable also contains an existence
       variable. Existence enters as a presence literal: "if this distinction grew, its knot holds" is itself a knot.
     - **The control.** A rule that reads a state does knot the order to the states. That is the input the canonical test
       forbids.
   - **A beginning is a knot (proved).**
     - **The local part is pairwise.** Which neighbour came first: "at most one parent" is a 2-CNF and holds no knot.
     - **The global part is not.** Time without a loop has exactly the pattern's cycles as its knots, each the not-all-equal relation
       on its seams. On a ring the beginning is one knot binding every seam, constrained as a whole and free in every part.
     - **Rings need a closing.** The beginning knot contradicts the pairwise part on a ring, so a ring needs a closing move.
     - **Duality.** The states knot along cuts and the history along cycles, the circuits of two dual matroids.
   - **Euler's count (proved).** A history's beginnings and ends, less its closing moves, give the grown pattern's Euler count. So
     the loose-end rule grows only chains, disc moves grow only patches and zero-pair weaves (the literature's discs and spheres),
     and cycle pairs (handles) need closings.
   - **What the beginning buys (proved).**
     - **One dimension.** No law with bounded hidden labels tells a long chain from a ring (pumping). So the beginning does what no
       bounded witness does: the endless chain's loose ends come from its beginning. A static law would need about log n bits per knot.
     - **Two dimensions.** A law with arbitrarily large six-regular patches excludes the six-regular one-pair weaves (the
       literature's flat tori) only if none of its six-regular configurations is periodic. The seam law allows all of them.
     - **Zero-pair weaves.** The beginning is free, since every zero-pair weave (the literature's two-sphere) can be grown by disc
       moves.
   - **The drawn plane (exploratory).** The pinwheel tiling, drawn in the plane, was grown outward from one tile by its own label-free
     collar law, with coins at its choices.
     - **Every coin run left the pinwheel.** In all 70 runs of four orders it left the pinwheel's own patches. Of these, 66 got
       stuck within 304 tiles, and 4 forced-first runs reached 500 tiles of collar-legal patches that are not pinwheel patches.
     - **Genuine continuations pass.** A genuine continuation is never rejected.
     - **The first wrong move is always a coin.** In 70 of 70 runs it was a choice, never a forced move. Usually only 1 of its
       2 or 3 options was right.
     - **An oracle needs few bits.** An oracle that keeps the right option grew 1,000 tiles from the seed's 54-way choice with
       4 to 10 further real bits, against 46 to 88 bits of apparent choice.
     - **A stronger law does not help.** The radius-2 law got stuck in 40 of 40 runs too.
   - **Reading.**
     - **Question 4.** A process written as a law is a static law on its history, so the static definition survives the change.
       What growth adds is a beginning, which is a knot, and never a knot of the grown pattern.
     - **What grows natively.** In one dimension the beginning grows the endless chain, the literature's number line, in every order.
       Round drawings need more: on drawn spheres a carried bit (`GROW-COIN-20261107-001`), in the drawn plane a few bits of hierarchy
       shared across the whole growing boundary, which independent local coins cannot share.
     - **Harmonies.** Every aperiodic law of the plane has deceptions of all orders (Dworkin and Shieh 1995). Periodic laws have
       polygonal circles (`LOGIC-CIRCLE-20261107-001`). So a law whose growth never gets stuck, in any order, has a polygonal circle,
       a harmony, among its layouts.
     - **Corrected 2026-11-08 (narrowing).** The pinwheel's collar and radius-2 laws are not aperiodic: a periodic plane obeys both
       (`COLLAR-PLANE-20261108-001`, under question 9). So Dworkin and Shieh do not explain their dead ends, which are measured facts
       about coin growth (`docs/CORRECTIONS.md`).
     - **What does not close.** The owner said on 2026-11-08 that our minds are "shapes" that do not close, continuous with the
       "shapes" they touch. Euler's count gives a formal side. A pattern grown by sprouting stays a tree. One grown by disc moves
       stays a patch until its last knot. Closing a ring or a cycle pair (handle) takes a move that joins the pattern to itself.
   - **Provenance.** Classical: products, the topes of graphic oriented matroids, discrete Morse theory, shellability, pumping,
     proof-labeling schemes, aperiodic tile sets, and deceptions (Dworkin and Shieh 1995; Onoda, Steinhardt, DiVincenzo and
     Socolar 1988). New as far as found: their reading under K1–K3, and the pinwheel's outward growth.
   - **Next (taken).** Knots across time (next entry): read Ledrappier's law as the space-time law of the cellular automaton rule
     60, then find the knots across time of rules 90 and 150, of one nonlinear rule and of Conway's Life (Payoff 2/3, Concreteness
     2/3). The alternatives are the collar law off the pinwheel (taken by `COLLAR-PLANE-20261108-001`, under question 9), one
     hierarchy bit per level, and every accretion law ([decision note](../research/GROWTH-LAW-20261107-001/growth_law.md)).

   **Words in the process entries.** The entries from here to the end of question 4 run cellular automata on rings of cells, a ring
   being a loop read as a process, and join the rings at shared contact cells into declared networks (A45), laid out on drawn tilings.
   Their planes, tori, tubes, bands, squares, honeycombs, lattices, faces, corners, cuts and genus belong to that declared layout, not
   to anything the law builds (reworded on 2026-11-11; the earlier text is in git history).

   **2026-11-08: knots across time are minimal decisive sets** (`TIME-KNOTS-20261107-001`).
   - **The question.** Question 4's other half, backlog B7: when states change under a local dynamics, which knots join a cell's
     future to its past, and which processes remember their past only pairwise? A process is read as its space-time law: one
     variable per cell and time step, the first row free, and every later cell its rule applied to the cells below. The allowed
     states are the trajectories, and K1–K3 applies unchanged.
   - **Knots across time are minimal decisive sets (proved).** A set of first-row cells is decisive when some setting of it fixes a
     cell's value T steps on. The knots joining that value to the first row are exactly the value with a minimally decisive set of
     two or more cells. A single deciding cell gives a tie.
   - **Pairwise memory of the first row is a single AND or OR (proved).** A future value has no knot with the first row exactly when
     it is a single conjunction or disjunction of literals. Every other future value needs several first-row cells together,
     constrained as a whole and free in every part.
   - **An AND process still knots its later states (computed; a correction of 2026-11-08).** Rule 128, each cell the AND of three,
     has no knot with its first row at any lag, but it never shows 1 0 1 after a step. So x(1, 1) and x(2, 4) on force x(1, 2) on, a
     knot joining two times through an intermediate row. Rules 136 and 160 do the same, and rule 32 knots one later row. The other
     eleven of the census's fifteen knot-free rules showed no knot in the windows checked.
   - **Linear processes never forget (proved).** A linear rule with polynomial p has one knot with the first row per lag, the
     support of p^T plus the cell: |supp p| + 1 places at every power of two (Frobenius), and 2^popcount(T) + 1 for rule 60
     (Lucas). Through intermediate rows, Ledrappier's law, the space-time law of rule 102, gives 2 + w(T) places inside the light
     cone for T ≤ 6. At T = 7 the least knot leaves the light cone, through a second cell at the later time.
   - **Life (proved).** In one step of Conway's Life the knots are the 70 sets of four neighbours with the cell's next value. There
     are no ties, and the cell's own present value is in no knot.
   - **A census of the 88 elementary automata (exploratory).** Counting knots with the first row to lag 6: 15 rules are knot-free at
     every lag, 8 keep exactly one knot per lag (the linear 60, 90, 105 and 150, and 42, 76, 138 and 200), 49 have counts growing
     at every lag, and 16 do otherwise. The traffic rule 184's knots at lag T are all C(2T + 1, T + 1) sets of T + 1 cells of the
     light cone, checked to T = 7. The knots do not follow Wolfram's classes: the linear class-3 rules have the simplest knotted
     memory, and the class-2 traffic rule the most.
   - **Reading.**
     - **Question 4.** The static definition survives the change to processes. A process written as a law is a static law on its
       trajectories, and K1–K3 reads its memory directly. What a process adds over a law of one moment is knots that join different
       times.
     - **Two sources of knots across time.** A future cell knots with its first row when several past cells must decide it
       together. A process also knots its later states when it never produces some pattern, as AND never produces 1 0 1, even when
       every future cell is decided one past cell at a time.
     - **Life.** The owner's example of emergence emerges under K1–K3 from crowds: four neighbours at a time decide a cell, and its
       own present never enters a knot.
   - **Provenance.** Classical: implicants and certificates of Boolean functions (Buhrman and de Wolf 2002), Lucas's theorem,
     Frobenius over GF(2), Ledrappier's shift (1978), Wolfram's elementary automata (1983), and the patterns a cellular automaton
     never produces, its Garden-of-Eden patterns (Moore 1962, Myhill 1963). New as far as found: their reading under K1–K3, the
     census by knots across time, and the traffic rule's uniform knots.
   - **Next (taken).** Knots between processes (next entry): two rings, each running a dynamics, joined by one contact cell, and
     which contact laws bind both rings' pasts in the contact's future (Payoff 2/3, Concreteness 2/3). The alternatives are learning
     a rule from its knots (G16), the traffic rule's uniform knots, and Life at two steps
     ([decision note](../research/TIME-KNOTS-20261107-001/time_knots.md)).

   **2026-11-08: a contact binds two processes exactly when it is a parity, and sharing it costs persistence**
   (`PROCESS-CONTACT-20261108-001`).
   - **The question.** The program's first emergence is a knot between two loops through one contact. With loops as processes:
     two rings, each running an elementary cellular automaton, and one contact cell, all written as one space-time law. The contact
     *binds both rings* at lag T when every minimally decisive set of its value c(T) over the first row meets both rings.
   - **Binding is the gate, read across time (proved).** The contact binds both rings exactly when neither ring's first row, with
     the contact's own first value, decides c(T). That is also exactly when forgetting either ring leaves c(T) free: two-sided
     essentiality and loss under erasure are one property across time.
   - **A listening contact binds exactly when it is a parity (proved).** Take a contact that reads one cell of each ring and feeds
     nothing back.
     - It binds both rings exactly when it is XOR or XNOR of two contact cells that still depend on their first rows.
     - Its knots join one decisive set of each ring through the contact: one knot or tie of each process becomes one knot between
       them.
     - With memory, binding from the first step still needs one of the four parities a + b, a + b + 1, a + b + c, a + b + c + 1.
     - The contact sees each ring only through the histories that ring can show at its contact cell.
   - **It persists while both rings remember (proved).** Between linear rings the parity contact binds at every lag unless a ring
     polynomial is nilpotent modulo X^m − 1. That happens only for rules 0 and 255, and for rules 60, 102 and 90 and their
     negations on rings of 2^k cells, the nilpotency known from Martin, Odlyzko and Wolfram (1984). A ring that forgets fixes its
     contact value, and an XOR of fixed values is a classifier, not a contact.
   - **Sharing the contact costs persistence (exploratory).** Now let the contact be a cell of both rings, as shared identity asks,
     combining the two rings' proposals.
     - **Lag 1 (elementary).** It binds at lag 1 exactly when it combines by a parity and neither rule is canalizing at its centre.
       Otherwise the contact's own past fixes a proposal.
     - **Later lags.** Of 128,128 configurations, each exact at every lag, 44 bind at every lag, all parities. Sharing breaks 13,068
       of the 13,104 bindings that a listening contact keeps forever, and rescues 8: a rule-60 ring of 4 cells forgets alone but
       not when it shares the contact.
     - **One size past.** The pattern holds, and persistence grows with ring size: 2 to 13 of 176 parity configurations at the
       smaller sizes, 21 at 6 + 7 cells.
   - **Reading.** Read across time the contact gate splits. A listening contact is two-sided, lost under erasure and persistent
     while both rings remember, but it is part of neither loop. A contact that is part of both loops feeds them back, and its own
     past and one ring's steering compete with binding. Few contacts pass every item together at these sizes.
   - **Provenance.** Classical: canalizing functions (Kauffman 1969), composition of certificates, additive automata on rings
     (Martin, Odlyzko and Wolfram 1984). Nearest to the shared model: Boolean automata double-cycles, two cycles sharing one
     automaton, which have exponentially fewer attractors than isolated cycles (Demongeot, Melliti, Noual, Regnault and Sené). New
     as far as found: the reading of the contact gate across time, and the census of shared contacts by binding.
   - **Next (taken).** Shared contacts that do not read themselves, with shared binding as rings grow (next entry): contact laws
     that combine their four ring neighbours without their own value, so that the contact is part of both loops without feeding its
     past to itself (Payoff 2/3, Concreteness 3/3). The alternatives are the whole-law reading of two rings (A30) and learning a rule
     from its knots ([decision note](../research/PROCESS-CONTACT-20261108-001/process_contact.md)).

   **2026-11-08: on larger rings a fifth to a quarter of shared contacts persist** (`SHARED-CONTACT-20261108-001`).
   - **The question.** The previous entry found persistent shared contacts rare on rings of up to 5 + 6 cells. Does a contact that
     does not read its own value persist more often, and is the rarity a property of small rings?
   - **The first step is decided exactly (proved).**
     - **Proposals.** A contact that combines its rings' proposals binds both at lag 1 exactly when it combines by a parity and
       neither rule is canalizing at its centre.
     - **Self-blind contacts.** A contact that both rings read but that does not read itself binds at lag 1 exactly when its 4 × 4
       table has no constant row or column. So its parities u(a_{m−1}, a_1) + v(b_{n−1}, b_1) bind exactly when u and v are
       nonconstant.
     - **The linear case.** With linear rings and an affine contact, binding at lag T is the contact's row of M^T meeting both rings.
   - **Not reading itself barely helps (exploratory).** Self-blind parities persist in 6.4% of 68,992 configurations, against 4.5%
     for proposal parities on the same rings. They do so on 157 rule-size pairs, against 22. The contact's past still returns to it
     two steps later, through the ring cells that read it, and rules canalizing in a neighbour input then rarely persist (1.1%).
   - **Persistence grows with the rings (exploratory).** From 3 + 4 to 8 + 9 cells, exact where the dynamics repeats within 4,096
     lags, the fraction binding at every lag rises from 1.1% to 20.5% for proposal parities and from 3.6% to 26.0% for self-blind
     ones. At 9 + 10 cells it is 21.6% and 27.0%: the growth is levelling off.
   - **Reading.**
     - **The rarity was a small-ring effect.** On rings of 8 and 9 cells, a fifth to a quarter of parity contacts shared by identity
       bind both rings at every lag.
     - **The whole gate across time.** Such a contact is a cell of both loops, shared by identity and essential to both
       recurrences. It is two-sided essential, lost when either ring is erased, a knot through its future, and persistent. So the
       full contact gate can pass across time.
     - **Why small rings fail.** Small rings return the contact's influence to it at once and lose their own first rows.
   - **Provenance.** Canalizing functions (Kauffman 1969); Boolean automata double-cycles (Demongeot, Noual, Sené and coauthors). New
     as far as found: the census by binding and its growth with ring size.
   - **Next (taken).** Two contacts across time (next entry): three rings in a chain sharing two contacts, and whether the chain
     binds its ends through the middle ring, the contact-network gate read across time (Payoff 3/3, Concreteness 2/3). The
     alternatives are why some rules persist, and saturation ([decision note](../research/SHARED-CONTACT-20261108-001/shared_contact.md)).

   **2026-11-08: in uniform chains, two persistent contacts do not compose across time** (`PROCESS-CHAIN-20261108-001`).
   - **Narrowed (2026-11-08).** The census ran one rule on all three rings and one law at both contacts. Chains that mix rules
     and laws do compose persistently (two entries below; `docs/CORRECTIONS.md`).
   - **The question.** Three rings in a chain: ring A and ring B share a contact c1, and ring B and ring C share a contact c2, d
     cells apart on ring B. Can both contacts persist, and does the chain then bind its ends, c2 needing the pasts of both A and C at
     every lag once A's past can reach it? This is the contact-network gate's composition, read across time.
   - **What a chain can carry (proved).**
     - **Listening contacts never compose.** A contact that feeds nothing back is read by no one, so the far contact never depends
       on the far ring. Composition needs shared identity.
     - **The light cone.** In a shared chain the far ring reaches the far contact only from lag d + 1, after crossing the middle
       ring.
     - **The linear case.** Linear chains bind along the supports of their M^T rows.
   - **Persistent contacts do not compose in uniform chains (exploratory).**
     - **The census.** Of 5,632 chains, each exact at every lag, both contacts persist in 182. In none of them does a contact bind
       the end rings at every lag from d + 1 on.
     - **One size past.** With the contacts moved off the opposite cell of the middle ring, 198 more chains keep both contacts and
       none composes.
     - **Why.** In the persistent chains the far ring's influence is absent (rings that read no neighbour, blocking, cancellation
       between the two ways round), fades, or can always be overridden.
   - **Composition comes and goes (exploratory, post hoc).** 195 chains bind their ends at some lags of their eventual cycle, 154
     of them with both contacts binding at those lags. These are mostly shift rules (15, 170) and linear ones (60, 90, 105, 150),
     which carry a contact's past round the middle ring in pulses. None of them keeps both contacts at every lag.
   - **Reading.** In these uniform chains persistence and composition did not coexist. A native network across time is at best intermittent
     here, against the static native networks of laws that compose like cycles (`NATIVE-NETWORK-20261021-001`).
   - **Provenance.** Elementary arguments and light cones; Boolean automata double-cycles share one node, and a chain shares two.
     New as far as found: the census of chains by persistence and composition.
   - **Next (taken).** Intermittent networks, composition at recurring lags (next entry; A34's alternative; Payoff 2/3,
     Concreteness 3/3). The fallback was a middle ring that carries a contact's past without mixing or cancelling it (Payoff 3/3,
     Concreteness 1/3) ([decision note](../research/PROCESS-CHAIN-20261108-001/process_chain.md)).

   **2026-11-08: a native network across time exists only intermittently, on affine substrates** (`INTERMITTENT-NET-20261108-001`).
   - **The question.** 195 chains of the previous entry compose at some lags of their eventual cycle but not at all of them. Is that
     native? The chain itself would have to single out its composing lags, so that no observer supplies them, and the composition
     would have to survive transport to other ring sizes.
   - **What intermittence is (proved).**
     - **A strobed chain.** A chain's composing lags recur with the period of its T-step maps. So the chain observed at one residue
       of that period composes at every observed lag or at none, and the phase is the only input the chain does not fix.
     - **Linear chains.** They compose exactly when the far contact depends on both end rings, so their composing lags are the
       arrival lags of both ends' influence.
     - **Every chain.** Composition always needs that arrival.
   - **Native only on affine substrates (exploratory).** Of 7,040 chains, 244 compose at recurring lags. In 92 the chain singles out
     its composing lags: composition exactly where both ends' influence arrives, with both contacts binding there. Every one of the
     92 runs an affine rule, the shifts 15 and 170 or the additive rules 60, 90, 105 and 150. With a nonlinear rule this never
     happens, because the other cells can override an end that has arrived. Twenty rule-law pairs compose at every tested size, and
     one size past the same pattern holds (24 of 112, all affine).
   - **Reading.**
     - **For the gate.** The contact gate asks for persistence, so A34's strict reading stands. Persistent composition was absent
       in the uniform chains tested, and chains that mix rules and laws have it (next entry; narrowed 2026-11-08).
       - *Corrected on 2026-11-08 (`RECUR-PATH-20261108-001`, four entries below).* The gate asks persistence of contacts, not
         composition at every lag. A34 was overturned: with every contact persistent, composition at recurring lags transports.
     - **What exists instead.** A weaker network: native, intermittent, and only where the substrate is affine.
     - **The recurring answer.** This is the program's recurring family: towers of patterns keep only parity, and static networks
       compose for affine laws.
   - **Provenance.** Eventual periodicity of finite dynamics; additive automata on rings (Martin, Odlyzko and Wolfram 1984). New as
     far as found: the census of intermittent composition by nativeness.
   - **Next (taken).** A middle ring that carries without cancelling, searched among affine chains (next entry; Payoff 3/3,
     Concreteness 2/3). The alternative was the pulse law of affine chains
     ([decision note](../research/INTERMITTENT-NET-20261108-001/intermittent_net.md)).

   **2026-11-08: a persistent native network across time** (`AFFINE-WIRE-20261108-001`).
   - **The question.** Among affine chains, each ring with its own rule and each contact with its own law, can both contacts persist
     while the far contact binds the end rings at every lag from d + 1 on? The coordinator's stop condition was forced gaps.
   - **A finite question (proved).** In an affine chain a contact's value at lag T is the parity of the first-row cells in its row of
     M^T. So persistence and composition are decided exactly by iterating two row vectors until they repeat.
   - **It exists (exploratory, verified).**
     - **The search.** Of 9,216,000 affine chains, 2,376 keep both contacts persistent and compose at every lag from d + 1 on, and in
       380 of them both contacts bind the end rings.
     - **Through the middle ring.** In 430 the contacts are two or three cells apart, so the middle ring carries c1's past across
       its own cells.
     - **The smallest.** Rule 150 on all three rings, 3/5/3 cells, contacts two apart. Each contact reads both of its middle-ring
       neighbours and one neighbour of its end ring. From lag 3 on, c2 holds one fixed parity of cells from all three rings and both
       contacts' first values: a single knot at every lag. It is verified on the full state space, by the generic enumerator, and
       by knotlab check.
     - **One size past.** With a middle ring of 8 cells, 80 chains in 40 of the 337 composing families still compose.
   - **Reading.**
     - **The gate across time.** Two complete contacts between processes coexist, each binds its two rings at every lag, and they
       compose by the substrate's own law, with constants changing nothing. Transport is partial and restrictions are untested.
     - **Why the earlier chains failed.** They were uniform. The constructions mix laws, a contact reading its middle ring on both
       sides and its end ring on one, and many mix rules.
     - **The recurring family.** Again it is the affine one.
   - **Provenance.** Linear recurring sequences over GF(2); additive automata on rings. New as far as found: persistent composition
     of two contacts across time.
   - **Next (taken).** Native paths across time (next entry): chains of four rings and three contacts built from the composing
     families (Payoff 3/3, Concreteness 2/3). The alternatives, the pulse law, nonlinear persistent composition and learning a rule
     from its knots, are parked as backlog B9 to B11 ([decision note](../research/AFFINE-WIRE-20261108-001/affine_wire.md)).

   **2026-11-08: no native path in three restricted families** (`NATIVE-PATH-20261108-001`).
   - **The question.** A path of four rings A, B, C and D joined by three shared contacts is native when every contact binds its own
     two rings at every lag and the last contact binds the end rings at every lag once the first ring can reach it: the first
     composed topology across time.
   - **What a path can carry (proved).** The last contact cannot depend on the first ring before the sum of the middle rings'
     contact distances, plus one. Affine paths reduce to row sequences, as chains do.
   - **None found (exploratory).**
     - **Rule 150 everywhere, with every law.** 900,000 paths, none native.
       - *Corrected on 2026-11-08 (`PATH-GROWTH-20261108-001`, two entries below).* None up to end rings of 5 cells. The wider run
         NATIVE-PATH-S1 finds 48 native paths with rule 150 on every ring, at end rings of 6 cells or a middle ring of 8.
     - **The carrying chains extended by one ring.** 96,840 paths, none native.
     - **The middle contact carries, the second middle ring loses it.** 762 of these paths keep all three contacts persistent. The
       middle contact carries the first ring at every lag in 302 of them, and the loss happens across the second middle ring.
     - **A shift as the second middle ring.** It carries without cancelling, but none of 3,059,280 such paths even keeps all three
       contacts. The shift uses up its own first row within one turn.
   - **Reading.**
     - **A tension.** A middle ring between two contacts must keep its own first row and carry the first ring's influence. The
       additive rules keep the first row but cancel the influence; the shift carries it but forgets its own row. No tested ring does
       both, a candidate obstruction, not a theorem.
       - *Corrected on 2026-11-08 (`PATH-HYBRID-20261108-001`, next entry).* Rule 150 does both as a middle ring between shift end
         rings, and the same paths with rule 150 on their end rings fail at the end rings. The tension is not forced.
     - **Families named.** The absence is for these three families only, as the correction of the same day asks.
   - **Provenance.** Light cones on graphs; linear recurring sequences over GF(2). New as far as found: the searches.
   - **Next (both taken).** A broad sweep of mixed four-ring paths, and middle rings that are not uniform within the ring (next
     entry). The wider run of rule 150 everywhere is folded in, with the correction above
     ([decision note](../research/NATIVE-PATH-20261108-001/native_path.md)).

   **2026-11-08: native paths across time, at particular sizes** (`PATH-HYBRID-20261108-001`).
   - **The question.** Is there a native path of four rings and three contacts when each ring may run any linear rule, or when the
     second middle ring is hybrid, its cells running different rules?
   - **One rule per ring (exploratory, verified).** Of 20,480,000 paths, 16 are native, all one construction (*corrected on
     2026-11-08, next entry:* other ring sizes have other native paths with one rule per ring):
     - **End rings.** 3 cells running a shift. With its contact reading both neighbours, an end ring is a feedback shift register
       with polynomial x³ + x + 1, which never forgets.
     - **Middle rings.** 5 cells running rule 150, their contacts two apart.
     - **The middle contact.** It reads one cell on each middle ring, the one on the short arc toward the other contact: a relay.
     - **Its knot.** The smallest path's last contact has one knot at every lag from 5 to 10, meeting all four rings, and knotlab
       confirms it.
   - **Hybrid middle rings (exploratory, verified).** 1,120 of 3,175,200 paths are native, and each needs its hybrid ring.
   - **Tied to their sizes (stress test).**
     - **The uniform construction.** None of its 11,600 larger versions, or of 512 five-ring versions, is native.
     - **The hybrid paths.** They survive one more cell on the far end ring (928 of 1,120), never on the near end.
     - **Why, as a heuristic.** Every native path found has row cycles of at most 12 lags. Larger rings make cycles of hundreds or
       thousands, and some phase then misses a ring.
       - *Corrected on 2026-11-08 (`PATH-GROWTH-20261108-001`, next entry).* That holds for this construction's larger versions.
         Persistent paths of other families keep short cycles at every size and still do not compose.
   - **Reading.**
     - **Composed topology across time.** Rings A and D share no contact, yet the last contact needs both their pasts at every lag.
       This is an indirect position through two intermediate processes, at these sizes, with no length or metric.
     - **The earlier tension is not forced.** Rule 150 remembers and transmits as a middle ring; NATIVE-PATH's paths failed at their
       end rings (corrected, `docs/CORRECTIONS.md`).
     - **The gate's transport clause is open.** The paths compose but do not survive growth.
     - **Inhomogeneous rings.** They count as native under A36 (added), and the existence of native paths does not rest on it.
   - **Provenance.** Shift registers (Golomb); additive automata on rings. The nearest substrate is the xor-cycle chains of Alcolei,
     Perrot and Sené (2015), studied for their asynchronous dynamics. New as far as found: native paths across time.
   - **Next (taken).** Native paths that survive growth (next entry). Native separation and cycles of rings went to backlog B12, for
     its own thread ([decision note](../research/PATH-HYBRID-20261108-001/path_hybrid.md)).

   **2026-11-08: no native path survives growth** (`PATH-GROWTH-20261108-001`).
   - **The question.** Fix each ring's linear rule and each contact's law and let the path grow, its rings from 3 to 9 cells or its
     length from 4 to 9 rings. Is some family native at every size?
   - **None is (exploratory, exact).**
     - **Equal rings.** With all four rings of 3, 4 or 5 cells, none of 36,864,000 paths is native, under every rule and law.
     - **Longer paths.** The 8 families native at four rings fail at five.
   - **Growth breaks composition, not persistence.** Paths whose three contacts persist exist at every size, mostly with row cycles
     of at most 12 lags, and none of them is native.
   - **Native paths sit at isolated sizes.**
     - **The map.** Of 36 combinations of end-ring and middle-ring sizes, native paths occur at 3: 3/5/5/3, 5/6/6/5 (rule 90 end rings,
       the one-sided additive rules 60 and 102 in the middle) and 4/7/7/5.
     - **Rule 150 on every ring.** 48 native paths, at end rings of 6 cells or a middle ring of 8 (the NATIVE-PATH-S1 run).
     - **Isolated.** No family is native at two sizes of the map, and none of the 128 stays native with one more cell.
   - **Reading.**
     - **A34 under challenge.** Under the every-lag reading, composition across time exists only at isolated sizes and never
       transports. Composition at recurring lags, with the phase fixed by the chain, held at every tested size for three-ring chains
       (`INTERMITTENT-NET-20261108-001`), so the alternative reading is the one to test. (It was, and A34 was overturned: next entry.)
     - **The gate.** The paths pass each contact gate and compose natively, but fail the gate's transport clause.
     - **Corrections.** Two earlier readings are narrowed (`docs/CORRECTIONS.md`).
   - **Provenance.** Linear recurring sequences over GF(2); additive automata on rings. New as far as found: the census by size.
   - **Next (taken).** Challenge A34 with composition at recurring lags across sizes (next entry). Native separation is in backlog
     B12 ([decision note](../research/PATH-GROWTH-20261108-001/path_growth.md)).

   **2026-11-08: composition across time transports at recurring lags; A34 overturned** (`RECUR-PATH-20261108-001`).
   - **The challenge.** A34 read composition as the far contact binding both ends at every lag. The alternative reads it at the
     recurring lags the path's own dynamics fixes, with every contact persistent. What each outcome would mean for A34 was recorded in
     the register before the census ran.
   - **The census (exploratory, exact).** On the growth families (one linear rule per ring, every law), 260 families compose at
     recurring lags with every contact persistent at every size (counts corrected on 2026-11-08: the census had listed each two-apart family four times):
     - **Rings growing.** 64 with contacts two apart on rings of 4 to 9 cells, every ring on rule 60 or 102, the one-sided additive
       rules.
     - **Paths growing.** 196 from 4 to 9 rings, with frozen or rule-90 end rings and middle rings on 90, 60 or 102.
     - **Against A34.** Under the every-lag reading, no family composes at two sizes.
     - **Verified.** An independent computation agrees for all of them at every size, and the full state spaces at the two smallest. The
       far contact composes at 12.5% to 62.5% of its cycle.
   - **A slip caught.** The first run's every-lag control failed on a bug in that check. The rerun fixes it, changes nothing else and
     passes.
   - **Reading.**
     - **A34 overturned, A37 in its place.** A path composes at the recurring lags its dynamics fixes, with every contact persistent.
       Under that reading these families are native networks across time that survive every growth tested.
     - **What A34 did.** It read the gate's persistence of contacts as persistence of composition. One earlier reading that rested on
       it is corrected (`docs/CORRECTIONS.md`).
     - **The recurring family.** Again affine.
   - **Provenance.** Linear recurring sequences over GF(2); strobed composition (`INTERMITTENT-NET-20261108-001A`). New as far as
     found.
   - **Next (taken).** A proof that the rule-60 family composes this way at every ring size (next entry)
     ([decision note](../research/RECUR-PATH-20261108-001/recur_path.md)).

   **2026-11-08: proved, at every ring size and every length** (`RECUR-PROOF-20261108-001`).
   - **A contact and its partners (proved).** If a contact reads two cells that each read only it and themselves, their sum never
     changes, so the contact depends on both of their first values at every lag. Each contact of these paths is such a loop.
   - **The theorem (proved).** In paths whose rings run rule 60 or 102 with contacts two apart, every contact binds both its rings at
     every lag, at every ring size s ≥ 4. The far contact needs the first ring exactly at the lags where C(T − 3, m) is odd, with m
     equal to 2, s − 2 or 2s − 6: a recurring set of density 2^(−w), w the number of ones in m (Lucas). So composition at recurring
     lags holds at every ring size, and composition at every lag at none.
   - **Every length (proved).** With n rings the far contact needs the first ring exactly when C(T − (n − 1), e) is odd, e summing
     k_j − 1 over the middle rings.
   - **Scope.** Rule 102 is covered by mirror symmetry. The rule-90 families are not: their contacts mostly lack two partners, and
     their composing shares, such as 1/3, are not powers of two.
   - **Reading.** Under A37 these are native networks across time that transport, by proof. The census's counts had repeats and are
     corrected (`docs/CORRECTIONS.md`).
   - **Provenance.** Pascal's triangle mod 2 and Lucas' theorem (Lucas 1878; Martin, Odlyzko and Wolfram 1984). Known-with-delta.
   - **Next (taken).** Native separation and cycles of rings on the proved families (next entry)
     ([decision note](../research/RECUR-PROOF-20261108-001/recur_proof.md)).

   **2026-11-08: native separation across time** (`SEPARATE-20261108-001`).
   - **Routes (proved).** A contact's value at lag T depends on a first-row cell exactly when the number of walks of reads of length T
     between them is odd. Cutting a contact, freezing it so that it reads nothing, removes every walk through it.
   - **A cut separates a path (proved).** In the proved paths the far contact needs the first ring at the lags where a binomial
     coefficient is odd. After cutting any one contact it needs the first ring at no lag, and every other contact still binds both of
     its rings: native separation across time, with reachability before the cut and the walks after it accounting for absence.
   - **A cycle needs two cuts (proved).** Four rings closed into a cycle with two routes from R_0 to R_2 keep every contact persistent,
     and R_2's contacts need R_0 at the two routes' binomial lag sets. One cut removes exactly its route's lags; one cut on each route
     separates. The least separating cut has the size of the number of routes (Menger).
   - **Routes come from the laws (computed).** Oriented round the cycle instead, every route passes through one contact and one cut
     separates.
   - **Reading.** Adjacency, native paths and separation now exist across time in one declared substrate, the program's order up to
     distance. Distance waits on the owner's pending ruling on counted length. The cut is a choice of intervention (A38, added).
   - **Provenance.** Menger's theorem (1927); walks counted by matrix powers. Known-with-delta.
   - **Next (taken).** Closed loops of rings, where influence returns to its source (next entry)
     ([decision note](../research/SEPARATE-20261108-001/separate.md)).

   **2026-11-08: closed loops of rings across time** (`LOOP-RINGS-20261108-001`).
   - **The question.** Close rings into a loop so that influence goes all the way round and returns to its source. Can every contact
     still bind both of its rings at every lag?
   - **Yes (exploratory, exact).** Of 295,056 loops of three and four rule-60 rings, 2,707 keep every contact persistent, and all 31
     at the smallest size agree on their full state spaces. In them each contact reads the chains from both neighbouring contacts, so
     every ring carries a circuit through its two contacts.
   - **Round the loop.** In 2,659 of them every contact needs the rings it does not touch at recurring lags, never at every lag.
   - **Sizes.** 54 families of four-ring loops persist at every size from 4 to 16, all with mixed positions; no three-ring family does.
   - **Reading.** The first closed routes of contacts across time. The path proofs relied on influence flowing one way; here it returns,
     and there is no proof for every size yet.
   - **Next (taken).** Prove the four-ring loops persist at every size (next entry)
     ([decision note](../research/LOOP-RINGS-20261108-001/loop_rings.md)).

   **2026-11-08: balanced loops persist at every size** (`LOOP-PROOF-20261108-001`).
   - **Feedback cancels (proved).** Over GF(2), with a = z/(1 + z), each contact's generating function is its own first values plus
     z a^(f) times the contact before it plus z a^(b) times the contact after it. Substituting once, the contact's own term always
     cancels, and the opposite contact's term cancels exactly when the positions sum to 2s: two contacts at cell 2 and two at cell
     s − 2. Then every contact has a closed form, with no feedback left.
   - **Persistence at every size (proved).** In a balanced loop whose partner reads do not overlap the chain ends, every contact binds
     both of its rings at every lag at every ring size, through the ends of the two chains it reads.
   - **Influence returns (proved).** Each contact needs the two rings it does not touch where C(T − 2, m) is odd for m in an interval
     of chain lengths: recurring lags.
   - **Where it stops.** It covers 16 of the 54 families. Overlapping partners (26 families) and one-partner contacts (12) persist
     without its witnesses, and unbalanced loops keep their feedback: none is persistent at sizes 5 to 30.
   - **Reading.** The two ways round the loop to the opposite contact cancel when their chain lengths agree, so balance is a property
     of the whole loop. The first closed routes of contacts across time that hold at every size, by proof.
   - **Next (taken).** Balanced loops of any number of rings (next entry)
     ([decision note](../research/LOOP-PROOF-20261108-001/loop_proof.md)).

   **2026-11-08: balanced loops of any length persist** (`LOOP-ANY-20261108-001`).
   - **The feedback is a shift (proved).** In a loop of r rings, crossing any ring forward and back costs the same, a^(s−2), so the
     feedback is z(A + cA^(−1)): A shifts round the loop through the chains, and c is a scalar.
   - **Balance cancels every return (proved).** When the positions sum to rs/2, every way the influence can return to a contact pairs
     with its mirror image, C(m, j) with C(m, m − j), and cancels mod 2. So every contact binds both of its rings at every lag, at every
     ring size, for every number of rings. The antipodal loops, every contact halfway round, are balanced for every length.
   - **Finite only for powers of two (proved).** The feedback dies out after r/2 steps exactly when r is a power of two and the loop
     is balanced; for other lengths it never ends, yet its returns still cancel.
   - **A census agrees (exploratory).** All 5,354 balanced loops of 5 to 8 rings at sizes 4 to 16 persist to lag 400, and so do 11,322
     unbalanced ones: balance is sufficient, not necessary.
   - **Reading.** Closed routes of contacts of every length now hold at every size, by proof, which completes the cycle side of
     composed topology across time for these loops. The powers of two are characteristic 2 at work, where squaring is linear.
   - **Next (taken).** Networks of loops, rings with three or more contacts (next entry)
     ([decision note](../research/LOOP-ANY-20261108-001/loop_any.md)).

   **2026-11-08: networks of loops** (`LOOP-NET-20261108-001`).
   - **The question.** Give one ring of a loop a third contact, so that two loops share it. Can every contact still bind both of its
     rings at every lag, and what does balance mean now?
   - **The criterion (proved).** A contact keeps the two cells it reads last at every lag exactly when the influence returning to it,
     summed over every closed walk through the network's contacts, cancels.
   - **Positions make a surface (proved).** The order of the contacts round each ring embeds the network in a surface: walks that keep
     to one ring go round rings, and walks that change ring at every contact go round faces. Balance becomes a density, every ring and
     every face carrying the same number of cells per contact. Then a contact's returns cancel exactly when the number of returns of
     each length is even.
   - **Symmetric networks persist (proved).** A symmetry that fixes a contact and exchanges its two rings pairs its returns. So two
     rings sharing three contacts, the five Platonic networks, and square, triangular and honeycomb lattices of rings on a torus keep
     every contact persistent at every lag at every size.
   - **Where a loop meets a larger ring, they cannot (proved).** At a contact joining a two-contact ring to a ring of three or more,
     the short return across the two-contact ring has no partner. Figure-eights and chords, the go-ahead's construction, have such
     contacts. With every ring of one size, none of 170,502 placements cancels its returns some other way (exploratory), and none of
     the equally spaced ones tested persists at every size (computed).
   - **Reading.** Loops can share rings when no ring is special: every contact must look the same from both of its rings. The
     lattices of rings are the first two-dimensional arrangements of contacts that all persist across time at every size, by proof.
     The lattice is given, not grown from a law.
   - **Next (taken).** Composition and separation across a lattice of rings (next entry)
     ([decision note](../research/LOOP-NET-20261108-001/loop_net.md)).

   **2026-11-08: composition and separation across a lattice of rings** (`LATTICE-NET-20261108-001`).
   - **The question.** On a square torus of rings whose contacts all persist, does influence reach every ring, and do rings of cuts
     separate the torus as closed curves separate a surface?
   - **Composition is the four-neighbour sum (proved).** Two steps from a contact land on the four neighbouring contacts of its kind,
     one walk each, so influence spreads by the powers of x + 1/x + y + 1/y over GF(2). A contact needs a ring exactly when an odd
     number of walks lead from one of the ring's contacts to it, first at lag g·k + 1 and then again and again.
   - **Odd sides reach everywhere, even sides never the antipode (proved).** On odd tori every contact needs every ring. On even tori
     the routes round the torus in opposite directions pair up and cancel, so no contact ever needs the ring halfway round both ways.
   - **Rings of cuts (proved).** Cutting the contacts round any set of rings separates it; on odd tori, where every contact needed
     every ring, that is a native separation across time. One ring of cuts round the torus does not separate, since influence goes
     round the other way; two do.
   - **Reading.** Native separation tells a torus from a disc: a ring of cuts that does not bound leaves the lattice in one piece. The
     gap at the antipode is a symmetry, not a range: on rectangular tori it appears only at some proportions (computed). No census was
     used, and no lag cutoff.
   - **Next (taken).** Genus read by rings of cuts (next entry)
     ([decision note](../research/LATTICE-NET-20261108-001/lattice_net.md)).

   **2026-11-08: genus read by rings of cuts** (`GENUS-CUT-20261108-001`).
   - **The question.** Can a network of rings across time count the handles of the surface its contacts make, by how many rings of
     cuts it survives in one piece?
   - **The pieces are read exactly (proved).** After any contacts are frozen, the pieces read from which contacts need which rings are
     the pieces of the ring graph without the cut contacts: every uncut contact needs both of its rings from lag 1, and needs never
     cross a cut.
   - **Two per handle (proved).** A family of rings of cuts keeps the network in one piece exactly when it is independent in the
     surface's homology mod 2. So at most two per handle keep one piece, some two per handle do, and one more always separates. The
     torus cut round both ways stays in one piece and a third ring separates it; on genus 2, four keep one piece and five never do.
   - **A persistent genus-2 lattice (proved).** The regular network of 16 rings with three contacts each, its rotations from GL(2,3),
     keeps every contact persistent at every lag and reads its genus the same way; so does a 56-ring network of genus 3 (stress test).
   - **One piece is not full reach (computed).** On the torus cut open both ways, every contact still needs every ring on sides 3 to 20
     except 8 and 16. No census was used, and no lag cutoff.
   - **Reading.** Adjacency, native paths, separation and the genus of the contacts' surface are now read in one substrate across
     time. What remains of the order, distance, waits on the owner.
   - **Next (taken).** Full reach on the cut-open torus, recorded as a preliminary result (next entry), then growing a network of rings
     from a law ([decision note](../research/GENUS-CUT-20261108-001/genus_cut.md)).

   **2026-11-08: full reach on the cut-open torus, preliminary** (`FULL-REACH-20261108-001`).
   - **Only powers of two fail, to side 48 (exploratory, exact).** After a ring of cuts round the n × n torus in each direction, every
     uncut contact needs every ring on every side from 3 to 48 except 8, 16 and 32, where n − 4 contacts each never need the three rings
     of one corner. No lag cutoff was used.
   - **Reading.** Cutting the torus open removes the cancellation of the two ways round; what remains at the powers of two is a
     cancellation inside the square, of Lucas' kind.
   - **Next (taken).** The proof, after the growth epic, which the coordinator switched to at the owner's interest; taken on 2026-11-09
     ([decision note](../research/FULL-REACH-20261108-001/full_reach.md)).

   **2026-11-08: growing a network of rings from a law** (`GROW-NET-20261108-001`).
   - **The question.** Can a network of rings grow by a local rule while every contact stays persistent at every stage?
   - **Bands and blocks grow (proved).** Every n × m torus of rings with sides at least 3 has a half-turn at every contact that
     exchanges its two rings, so every contact persists. Inserting a whole band of rings round the torus, or splitting every ring into a
     block, keeps every contact persistent at every stage.
   - **Single attached rings do not (proved).** A new ring attached by one contact returns to it at once; by two contacts not side by side on
     one ring, it leaves one unpaired return; as a bubble on a corner p → q, it deletes that corner, and the network stays balanced only
     if no contact is reached from q and reaches p.
   - **In practice none can be added (exploratory, exact).** Of 795,042 single-ring attachments to 16 balanced seeds, none keeps every
     contact persistent beyond the smallest seeds of four rings; truncating or rectifying the Platonic networks loses persistence too.
   - **Reading.** The unit of growth is a band: a single attached ring is a defect whose returns go unpaired. Networks with a flip at every contact
     exist at every size only on the torus, so the flip criterion carries growth only on a flat surface. The law fills a torus it is
     given; making the surface is the open part.
     *Narrowed on 2026-11-09: single rings break persistence when attached; one inserted with the contacts across the gap rejoined
     through it keeps every contact persistent on the twist torus (`GROW-PLAIN-20261109-001`, below; `docs/CORRECTIONS.md`).*
   - **Next (taken).** Make the surface by growing whole bands (next entry)
     ([decision note](../research/GROW-NET-20261108-001/grow_net.md)).

   **2026-11-08: one band makes the torus** (`BAND-SURFACE-20261108-001`).
   - **The question.** Can the band law make the torus from a loop of rings, not only fill a torus it is handed?
   - **Yes, in one step (proved).** Inserting a band into a loop joins each new ring to its partner on both sides, which is the n × 2
     torus. Every n × m torus with n ≥ 3 and m ≥ 2 has a half-turn at every contact, so the loop, the n × 2 torus and every later torus
     keep every contact persistent.
   - **Where the band sits decides the surface (exploratory, exact).** Of 1,813,632 placements of a first band, the balanced ones lie on
     a sphere only once (the cube), on the torus, or on surfaces of genus 2 to 4, mostly with no symmetry. No lag cutoff was used.
   - **Reading.** A band joined to a loop on both sides runs through both of the loop's faces and closes a handle. A uniform local law
     now makes a surface from a loop with every contact a persistent knot across time at every stage; the rule, not the dynamics, says
     where the band goes.
   - **Next (taken).** Higher genus by bands (next entry)
     ([decision note](../research/BAND-SURFACE-20261108-001/band_surface.md)).

   **2026-11-08: higher genus by bands** (`GENUS-BAND-20261108-001`).
   - **The question.** Can bands keep growing a surface of genus 2, or add handles one band at a time, with every contact persistent?
   - **The second band fails (exploratory, exact).** The 20 balanced genus-2 first bands on loops of 5 rings are exactly those with two or
     three twisted columns. None of 770,520 second bands in four families keeps any of them balanced.
   - **No second handle (exploratory, exact).** On the n × 2 tori, of 1,974,904 second bands in the same families only the torus band rule
     keeps every contact persistent, and it keeps genus 1. No lag cutoff was used.
   - **Reading.** "One band per handle" does not extend: one band makes the torus from a loop and later bands only grow it. The balanced
     genus-2 first bands have no flips, and their balance breaks under any further band; the torus keeps a half-turn at every contact.
   - **Next (research directions).** The ready proofs of full reach on the cut-open torus (Payoff 2/3, Concreteness 3/3) and of which
     lattices compose everywhere ([decision note](../research/GENUS-BAND-20261108-001/genus_band.md)).

   **2026-11-08: distance across time** (`DISTANCE-20261108-001`).
   - **The question.** With counted length ruled a native magnitude by the owner (A40), does a network of persistent contacts read a
     distance across time, and does it match graph distance on the lattices?
   - **Counted length is read (frozen test, proved).** Freezing every contact off a route of L contacts makes the far contact first
     need the near ring at lag g·L + 1, g the spacing, and these lags add when routes are joined; at unequal spacing the lag counts
     cells. A40's test, pre-registered before it ran, passed on all 2,250 routes.
   - **Two exact lengths (proved).** The most disjoint cuts that leave two rings in different native pieces is the ring graph's
     distance, on every network. The earliest need any freeze allows is g·δ + 1, δ the contact graph's directed distance: a time of
     flight, directed because influence goes one way round every ring. Between a contact and its translate δ is m/2 times the ring
     graph's distance (m contacts per ring), and on the square lattice the ring graph's distance is ⌈δ/2⌉.
   - **The plain first need is a parity-filtered cone (proved; counts computed).** Without freezing, a contact first needs a ring at δ
     exactly when an odd number of shortest routes arrive: on the square torus, for contacts of one kind at offset (a, b), when
     a AND b = 0; on the plane it never comes at a third of the offsets. It breaks the triangle inequality, so it is not a metric.
   - **Reading.** Adjacency, native paths, separation, genus and now distance are read in one substrate across time. Distance is read
     through freezes (A41): the symmetry that keeps contacts persistent is the one that makes shortest routes cancel. The networks are
     given, not grown. No lag cutoff was used.
   - **Next (taken).** Distance without freezing (next entry); full reach on honeycomb tori, parked as B18,
     which appears to hold exactly when 3 divides the side (computed to side 13)
     ([decision note](../research/DISTANCE-20261108-001/distance.md)).

   **2026-11-08: distance without freezing** (`PLAIN-TIME-20261108-001`).
   - **The question.** For which networks of persistent contacts does the plain first need, with no freezing, always come at the
     directed distance?
   - **Only the sphere, at every size (proved).** Every loop of rings, pair of rings sharing contacts and Platonic network reads its
     distance plainly. The square, triangular and honeycomb planes do not, from distance 4, 6 and 5, and a quotient whose systole is long
     enough inherits the failure, so exactly 26 tori read it: 9 square, 11 triangular, 6 honeycomb, mirror images apart.
     *Corrected on 2026-11-09: the 26 are the regular tori; thin tori of other proportions, the ladders first, read it at every size
     (`GROWN-DISTANCE-20261109-001`, below; `docs/CORRECTIONS.md`).*
   - **The first failing map (exact).** The twisted square torus {4,4}_(2,3), 13 rings: each contact has one late ring, at distance 4,
     first needed at 5. Its mirror image reads every distance plainly, so no rule by type, genus, curvature or size decides finite maps.
   - **The horizon (computed).** In the tiling with rings of m contacts and faces of f, two shortest routes first tie at
     τ = L − L/m − L/f + 1, L = lcm(m, f), once round a ring and once round a face, and the first late ring comes one step later (two
     with triangular faces and larger rings): from 4 on the square lattice to 26 for rings of 13 and triangular faces. Curved networks
     read their distance plainly much further, but not forever. No lag cutoff was used.
   - **Reading.** Freezing does real work wherever a network is two-dimensional and not tiny (A41, confirmed). Chirality is native:
     rule 60 reads leftward, so a network and its mirror image are different substrates.
   - **Next (research directions, paused for the day).** Prove the tie law's lower bound (taken, and proved, on 2026-11-09); find which
     quotients rescue late rings ([decision note](../research/PLAIN-TIME-20261108-001/plain_time.md)).

   **2026-11-09: full reach on honeycomb tori** (`HONEY-REACH-20261109-001`).
   - **The question.** On the square torus every ring needs every ring exactly when the side is odd. On the honeycomb torus the census
     to side 13 said exactly when 3 divides the side. Is that so, and why?
   - **When 3 does not divide the side, never (proved).** Influence between contacts of one kind spreads by the six-neighbour sum of the
     triangular lattice, and every power of it vanishes on the three mirror lines through a ring, because each mirror pairs up the
     walks. The turn of 120° about a ring fixes exactly one ring of the other kind when 3 does not divide the side, and all the points
     that would let influence into it lie on the mirrors: it never needs the first ring, nor the first ring it.
   - **When 3 divides the side, always (computed).** The turn then fixes no ring of the other kind, the mirrors pin nothing (proved
     from side 7), and every ring needs every ring on every side checked, to 300.
   - **How many are missed (computed).** Otherwise one ring per ring on odd sides, and more as the power of 2 in the side grows: 13,
     85, 421, … exactly 2(N − 1)(N − 2) + 1 with N = 2^(v + 1), whatever the odd part.
   - **Reading.** What blocks reach is a rotation of the source: the half-turn's fixed ring (the antipode) on even square tori, the
     turn of order 3's on honeycomb tori whose side 3 does not divide. The lattice is given, not grown. No lag cutoff was used.
   - **Next (research directions).** Which lattices compose everywhere, by the same reduction to mirrors; a proof of the computed half
     ([decision note](../research/HONEY-REACH-20261109-001/honey_reach.md)).

   **2026-11-09: distance in a grown network** (`GROWN-DISTANCE-20261109-001`).
   - **The question.** The band law grows a torus from a loop of n rings: the n × 2 ladder, then n × 3, n × 4, …. Does the grown torus
     read distance the way the fixed torus does, and how do its balls grow as it grows?
   - **Every stage reads both freeze lengths (proved).** The cut length is the ring graph's distance and the time length g·δ + 1 at
     every stage, each stage read as a fixed network (A42).
   - **Only the ladder reads distance without freezing (proved).** Every square torus whose lattice holds (2, 0), the n × 2 ladder and
     its twisted forms, is on time at every size: in its cover each ring's nearest contact has exactly one shortest route, because the
     two rungs pair up every other walk. The n × m torus with 3 ≤ n ≤ m is late except 3 × 3: a tube three rings round already holds
     the plane's first tie of two shortest routes.
   - **The balls are a tube's (proved).** 2r² + 2r + 1 rings out to half the loop, then 2n more per step, for both lengths: dimension 2
     at short range and 1 at long range, with bands added along the seed loop (A43).
   - **A correction (computed).** The square tori holding (2, 1) of one chirality and the triangular tori holding a vector of length √3
     are on time too, to index 100 and 80, so the 26 tori of the previous entry are the regular ones.
   - **Reading.** The plain first need reads distance at every size where a network is one-dimensional at large scale, and freezing is
     needed wherever it is two-dimensional and not tiny. The band law grows a line of loops, not a plane: which way a band goes is not
     said by the law.
   - **Next (taken).** Growth while running (next entry)
     ([decision note](../research/GROWN-DISTANCE-20261109-001/grown_distance.md)).

   **2026-11-09: growth while running** (`GROW-RUN-20261109-001`).
   - **The question.** If the band law inserts a band while the network runs, its cells new open distinctions, does every contact
     still bind both of its rings at every lag, reading the whole history as one law?
   - **What it has not reached is intact (proved).** A ring whose first row has not yet flowed through the contacts the band cuts keeps
     every binding, and every contact binds the band's own rings at every lag.
   - **What it has reached mostly breaks (computed).** 68% of the bindings of reached rings fail; over every insertion lag of 13 tubes
     only lag 0 keeps every contact persistent in every case; the damage spreads from the band one row per row's time length; under
     continual growth only the newest band stays bound. No lag cutoff was used.
   - **Reading.** A growth event has a past light cone, and the knots across time inside it lapse. The band law's balance belongs to
     growth between runs (A42, confirmed); a law that grows in time keeps its knots young, or must grow where its influence has not
     arrived.
   - **Next (selected).** Growth chosen by the dynamics, where influence has not arrived (B23); knots read from the last growth event
     (taken, next entry) ([decision note](../research/GROW-RUN-20261109-001/grow_run.md)).

   **2026-11-09: knots read from the last growth event** (`REBASE-KNOTS-20261109-001`).
   - **The question.** Is the loss of knots under growth while running an artefact of reading from the first row? Read them from the
     row at the insertion instead.
   - **No later row is open (proved).** Every cell is read by exactly two cells, itself and the next one, or the next cell on each of a
     contact's two rings, so from lag 1 on the cells' values sum to 0: each is the sum of the others.
   - **So the reading is not native (proved and computed).** Treating the insertion row as open gives back every stage's persistence,
     but read natively from any later row every contact fails to bind each of its rings at some lag, even in a network that never
     grows. No lag cutoff was used.
   - **Reading.** Knots across time reach back to a beginning: the first row, or the cells a growth event bears. The loss under growth
     while running is real.
   - **Next (research directions).** Growth chosen by the dynamics continues (taken, next entry); an invertible substrate would test
     whether the lapse is rule 60's forgetting, B39 ([decision note](../research/REBASE-KNOTS-20261109-001/rebase_knots.md)).

   **2026-11-09: growth chosen by the dynamics** (`GROW-CHOOSE-20261109-001`).
   - **The question.** If a running tube may add a band, along the loop or across it, only where the band keeps every contact
     persistent, where and which way does it grow, and does it keep growing?
   - **One way (exploratory, exact per decision).** At lags 0 and 1 bands are allowed both ways; once one is in, from lag 3 on every
     allowed insertion runs across the tube, in all 72 runs read, so the network lengthens the way its first band went: a tube.
   - **Then it stops, mostly.** If the cut contact keeps or copies its value, nothing more is allowed after lag 2. If both halves are
     born, one band per lag for 3 to 13 lags, and then no insertion is left, except on tubes three rings round grown along their length,
     which reach the horizon of 12 lags.
   - **All at once grows both ways, briefly.** Filling every allowed insertion together, which needs no order, doubles both sides at lags 0
     and 1; past that the networks were too large to read.
   - **Reading.** The dynamics breaks the symmetry with its first band and keeps it, so the band law, left to itself, grows a line of
     loops; a band across the tube would cut through old influence. A plane would need the order-free rule to keep going (B38).
   - **Next (research directions).** The order-free rule past lag 1 (B38, taken, next entry); an invertible substrate (B39)
     ([decision note](../research/GROW-CHOOSE-20261109-001/grow_choose.md)).

   **2026-11-09: growth by every allowed cut at once** (`GROW-ALL-20261109-001`).
   - **The question.** If the running tube fills every insertion the dynamics allows with a band, all at once, does it keep growing both
     ways past lag 1, or stop?
   - **It doubles (exploratory, exact per decision).** On the 3 × 3, 3 × 4 and 4 × 4 tubes every cut, both ways, stays allowed at lags 0,
     1 and 2, so every ring splits into a 2 × 2 block each lag: 3 × 3, 6 × 6, 12 × 12, 24 × 24, every stage read balanced in the whole
     history. At lag 3 none of the 48 cuts fails within 50,000 lags; none could be confirmed. Checked against actual bits.
   - **The price.** Every contact is cut and reborn each lag, so the rings carry the memory, and the stages, square tori with both sides
     at least 6, read their distance only through freezes. "Plane" is said of the declared rings (A45).
   - **Reading.** One band at a time grows a tube or breaks; a band at every cut grows a plane. The order-free rule, the one the
     doctrine allows since nothing picks among cuts, is the plane-growing one. *Corrected on 2026-11-09: while it doubles every lag no ring
     hears another, so this plane of declared rings reads no distance while it grows (next entry; `docs/CORRECTIONS.md`).*
   - **Next (taken).** Distance and balls while it doubles (next entry)
     ([decision note](../research/GROW-ALL-20261109-001/grow_all.md)).

   **2026-11-09: distance and balls in the doubling network** (`GROW-HORIZON-20261109-001`).
   - **The question.** While the doubling law runs, how far does each original ring's first row reach, in the original lattice's units?
     Pre-registered before reading.
   - **Every lag: no ring hears another (proved).** Every contact is cut and reborn before any cell reads what it computed, so a ring's
     cells only ever hear its own cells and newborn contact values.
   - **Every P lags: a horizon (computed).** Influence crosses contacts between doublings, but the rings between two original rings double
     faster than it travels: an original ring is heard only within 0.8 to 2.4 original spacings for P = 2 to 8, the same on 3 × 3 and
     5 × 5, its growth halving at each doubling, while the contacts inside multiply about fourfold per doubling.
   - **Reading.** Growth that outruns influence confines every ring to a neighbourhood fixed at its birth, and at the fastest rate to
     itself: the plane is divided, not connected, while it grows. A grown space that reads its own distance needs growth slow enough for
     influence to keep up.
   - **Next (taken, B50).** Why doubling keeps every stage balanced (next entry); the horizon as a theorem; growth slow enough to read
     distance ([decision note](../research/GROW-HORIZON-20261109-001/grow_horizon.md)).

   **2026-11-09: why doubling keeps every stage balanced** (`DOUBLE-BALANCE-20261109-001`).
   - **The question.** Why does splitting every ring in four at every lag keep every stage balanced, and what does slower doubling do?
   - **By isolation (proved).** If nothing outside a ring holds its born cells and its own cells hold them independently, its contacts
     bind it exactly as they would from a fresh first row. Doubling every lag isolates every ring, and its own cells evolve invertibly, so
     every stage, a balanced torus, stays balanced at every lag.
   - **Slower doubling (computed).** Every 2, 4, 6 or 8 lags the rings hear each other from the second doubling on, and a stage is
     unbalanced by 24 × 24; every 3 lags, by a cancellation particular to one-cell corners, the rings stay isolated and balanced.
   - **Reading.** While a network grows, its knots across growth and its rings hearing each other exclude each other in every schedule
     read: the doubling law keeps its knots by keeping its rings apart. *Narrowed on 2026-11-09: every schedule read had g = 2; at g = 3
     doubling every 2 or 4 lags keeps both (`ISOLATION-NEED-20261109-001`; `docs/CORRECTIONS.md`).*
   - **Next (research directions).** Another birth rule (B51, taken, next entry); isolation as necessary (B52)
     ([decision note](../research/DOUBLE-BALANCE-20261109-001/double_balance.md)).

   **2026-11-09: another birth rule** (`BIRTH-RULE-20261109-001`).
   - **The question.** A frozen test of A44: if the cells a doubling bears copy the cells they split from, are zero, or add an open
     distinction to a copy, can a growing network keep every stage balanced while its rings hear each other?
   - **Copies cannot be bound (exploratory, exact).** A copied or zeroed ring bears no distinction of its own, so no contact binds it.
   - **Open plus copy holds two doublings.** Each new ring hears its parent from birth and every stage stays balanced through 12 × 12,
     the first growing network in this line balanced while its rings hear each other; at 24 × 24 it fails at every schedule.
   - **Reading.** A beginning must be open, and whatever it inherits spreads the mixtures that break balance. For growth that keeps going,
     knots across growth still need isolated rings (A44 confirmed). *Narrowed on 2026-11-09 to g = 2: at g = 3 open births with doubling
     every 2 or 4 lags keep balance while rings hear each other (`ISOLATION-NEED-20261109-001`).*
   - **Next (taken, B52).** Isolation as necessary (next entry) ([decision note](../research/BIRTH-RULE-20261109-001/birth_rule.md)).

   **2026-11-09: is isolation necessary for balance?** (`ISOLATION-NEED-20261109-001`).
   - **The question.** Pre-registered: does every doubling schedule whose rings hear each other lose balance within two doublings?
   - **No (exploratory, exact).** At g = 3, open births doubling every 2 or every 4 lags keep every stage balanced while hundreds of own
     cells hear another ring, to 24 × 24. At g = 2 the bound holds, and the isolating schedules are P = 1, 3 and 7.
   - **A correction.** The last two entries' exclusion of knots across growth and rings hearing each other was read at g = 2 only.
   - **Reading.** The spacing decides what growth can keep: with two own cells per corner, a ring can hear its neighbours and its contacts
     keep their knots. These are the first native laws read that grow a plane both ways while it runs, keep every stage balanced and let
     rings hear each other. *Narrowed on 2026-11-09: the rings that hear each other are inside one original ring's territory (next entry;
     `docs/CORRECTIONS.md`).*
   - **Next (taken, B53).** Distance in the g = 3 growing plane (next entry)
     ([decision note](../research/ISOLATION-NEED-20261109-001/isolation_need.md)).

   **2026-11-09: distance in the g = 3 growing plane** (`GROW-HEAR-20261109-001`).
   - **The question.** Pre-registered: in the growing planes that keep their knots while rings hear each other, how far does an original
     ring's first row reach?
   - **Only inside its own territory (exploratory, exact).** Its reach converges to half an original spacing, no original ring ever hears
     it, and the contacts that need it grow by a constant per doubling, like the boundary of a region, not its area.
   - **Reading.** The grown plane is a patchwork of territories, one per original ring, each refined and heard inside while it grows,
     none heard across its border; the knots survive because nothing crosses. Between its original rings the plane reads no distance while
     it grows.
   - **Next (taken: B57, next entry; then B55).** Larger spacings; why g = 3 keeps balance, by confinement to territories
     ([decision note](../research/GROW-HEAR-20261109-001/grow_hear.md)).

   **2026-11-09: larger spacings** (`SPACING-20261109-001`).
   - **The question.** Pre-registered: at spacings g = 4 and 5, can a growing plane keep its knots while influence crosses a territory
     border, an original ring heard by another?
   - **No border crossed (exploratory, exact).** Doubling every 1 to 4 lags, no original ring is heard by another at either spacing.
   - **Odd spacings keep balance with hearing.** At g = 5 doubling every 2, 3 and 4 lags keeps every stage balanced while rings hear
     each other inside territories, to 24 × 24; at g = 4 every such schedule fails at 12 × 12. With g = 2 and 3, balance with hearing
     appears exactly at the odd spacings read, whose corners hold an even number of own cells.
   - **Reading.** Territories are the rule at every spacing read; slower doubling at an odd spacing is the one case left where a border
     might be crossed with balance kept (sub-goal B63).
   - **Next (taken: sub-goal B63, next entry; then B55).** Crossing a border at odd spacings; why odd spacings keep balance
     ([decision note](../research/SPACING-20261109-001/spacing.md)).

   **2026-11-10: crossing a territory border with balance** (`CROSS-BORDER-20261110-001`).
   - **The question.** Pre-registered: at g = 3 and 5, does doubling slow enough for influence to cross a territory border keep every
     stage balanced?
   - **Crossing breaks balance (exploratory, exact).** Doubling every 8 to 16 lags at g = 3, or 12 to 16 at g = 5, lets original rings
     hear each other, and every such schedule has an unbalanced stage within two doublings of the crossing.
   - **Reading.** Hearing inside territories is compatible with keeping knots; hearing across them, followed by more growth, is not, in
     every schedule read (g = 2 to 5). While a network grows it keeps its knots or reads distance across its grown plane, not both.
     *Corrected 2026-11-10:* that held for the uniform schedules read only; uneven ones cross with every stage balanced (below).
   - **Next (taken: B56, next entry; B55 deferred).** Why odd spacings keep balance
     ([decision note](../research/CROSS-BORDER-20261110-001/cross_border.md)).

   **2026-11-10: growth that stops** (`GROW-STOP-20261110-001`).
   - **The question.** Backlog B56: grow by doubling for k lags, stop, and read what distance the stopped network reads.
   - **The fixed torus, scaled (proved).** After doubling every lag for k lags and a stop, every need of every ring, with or without
     freezes, is the fixed (n·2^k × m·2^k)-torus's. The stopped plane reads that torus's cut length, time length and plain first need,
     and two original rings D apart are now 2^k·D ring steps apart. Checked at the cell level: 21,456 pairs, 60 lags after the stop.
   - **Hearing before the stop spoils it (computed).** Doubling every 2 or 4 lags at g = 2 and 3 leaves a stopped network whose needs
     differ from the fixed torus's for most pairs; every 3 lags at g = 2, which isolates, reads it exactly.
   - **Reading.** Making and reading are two phases. The law grows a plane that reads no distance while it grows; once it stops, the
     plane reads its own distance as a fixed torus does, the distance between original rings scaled by the growth it went through.
     *Corrected 2026-11-10:* "two phases" holds for the doubling schedules read here, not for every schedule (below).
   - **Next (taken: B39, next entry).** An invertible substrate ([decision note](../research/GROW-STOP-20261110-001/grow_stop.md)).

   **2026-11-10: persistence needs forgetting** (`INVERT-STEP-20261110-001`).
   - **The question.** Backlog B39: on a substrate whose step is invertible every row is open, so growth while running could be read
     from any row. Is there one whose contacts persist?
   - **No, on any finite network (proved).** An invertible step permutes the finite set of states, so some power of it is the identity.
     At that lag every contact holds exactly its own first value, which neither ring decides, and erasing either ring changes nothing:
     no contact persists. So wherever a contact persists the law loses information, and no row after the first is open, for every rule
     and contact law. Checked on 256 linear substrates, first and second order, on five tubes: every invertible one fails by lag 336.
   - **Not in conflict with doubling.** `DOUBLE-BALANCE-20261109-001A` uses an invertible map, but it is a ring's own cells' evolution
     while every contact is reborn, not the step; the step there is rule 60's, which forgets.
   - **Reading.** A finite network whose contacts keep their knots across time has an irreversible law. Growth keeps knots by giving the
     network new beginnings, as the doubling law does, not by reading a later row.
   - **Next (taken: B64, next entry).** The proof pair B55 and B64 for the exclusion while growing; a reversible substrate that never stops
     growing (B67) ([decision note](../research/INVERT-STEP-20261110-001/invert_step.md)).

   **2026-11-10: crossing does not break balance** (`CROSS-WHY-20261110-001`).
   - **The question.** Backlog B64: why does a schedule in which original rings hear each other lose balance? The aim was a lemma that
     would make the exclusion of the last entries exact.
   - **It does not, in general (exploratory, exact, frozen census).** Failures come in two kinds: a ring's own cells stop holding its
     born cells independently (internal), or what other rings heard of it cancels what it holds (heard). Both happen with no crossing
     at all. And a schedule that pauses once, long enough for neighbouring territories to hear each other, then doubles quickly, keeps
     every stage balanced: at g = 3, 21 such schedules to 48 × 48, as [28, 1, 1], where every original ring hears all eight others from
     lag 8. A uniform pause repeated, as every 28 lags, fails at 48 × 48.
   - **Balance is read on one territory (proved).** The law commutes with the original lattice's translations, and rings born at a
     doubling are never the ones that fail.
   - **Reading.** The exclusion was a fact about uniform schedules, not about growth: to the sizes read, a growing plane can keep its
     knots and carry what its territories heard of each other. Only [1, 28, 1], extended by a run of 1 or 2 lags, is confirmed at
     96 × 96; most of the 21 are not known to stay balanced larger, and balance at every size is open. The schedules are declared
     and were found by search; a rule the network could follow to pause on its own is open.
   - **Next (taken: B89, next entry).** Reading distance while growing (sub-goal B89; Payoff 3/3, Concreteness 2/3): on a 5 × 5
     tube, a schedule under which original rings are heard at distance 1 and then 2 with every stage balanced; B55 meanwhile
     ([decision note](../research/CROSS-WHY-20261110-001/cross_why.md)).

   **2026-11-10: reading distance while growing** (`READ-GROW-20261110-001`).
   - **The question.** Sub-goal B89: on a 5 × 5 tube, can the growing plane read its distances, nearest original rings first, while
     every stage keeps its knots? Frozen first: the distance is taxicab on the original torus, and the reading is the lag at which an
     original ring first hears ring (0, 0); a metric needs every ring heard, symmetry and the triangle inequality.
   - **Distances in order (exploratory, exact).** Five schedules keep every stage balanced to 40 × 40 while the four nearest rings hear
     ring (0, 0) before any ring two away. In [12, 28] the plane hears distance 1, doubles, and only then hears distance 2. Two schedules
     were confirmed on the full state and by a second code written independently. One size past, at 80 × 80, [28, 1] and [35, 1]
     extended stay balanced and [12, 28] does not.
   - **What the pause reads.** In one long pause the lags are exactly 8, 20 and 32 at distances 1, 2 and 3: the drawn board's taxicab
     distance, recovered. After a doubling the diagonal ring is heard before the straight one two away: no longer taxicab.
   - **Not a metric.** The rings at distance 4 are never heard while every stage is balanced, and the lags' offset breaks the triangle
     inequality. The board is still declared (A51): the reading recovers it, it does not choose it.
   - **Next (taken: B102, next entry).** A metric while growing (sub-goal B102; Payoff 3/3, Concreteness 2/3): two pauses on the
     5 × 5 and 7 × 7 tubes, lags read without their offset or through freezes
     ([decision note](../research/READ-GROW-20261110-001/read_grow.md)).

   **2026-11-10: a metric only between doublings** (`METRIC-GROW-20261110-001`).
   - **The question.** Sub-goal B102: can a growing plane keep every stage balanced and read a metric on its original rings? Frozen
     first: the time length is read through freezes (A41), from one cell of ring (0, 0) to the same cell of another ring; the round
     trip, out and back, is symmetric by construction; a metric also needs the triangle inequality, with no offset subtracted.
   - **No metric (exploratory, exact).** On the 5 × 5 tube one schedule, [28, 60], keeps every stage balanced to 40 × 40 and reaches
     every original ring out and back, but far rings cost more than the sum of near trips: 60 violations of the triangle inequality,
     such as 138 > 90 + 36.
   - **The growth is what breaks it.** Every violation involves a trip across a doubling; within one stage a route to one ring
     followed by a translated route to the next is a route, so the time length is subadditive there.
   - **Reading.** The plane expands while it is read: the triangle excess is a native measure of growth during a trip. A metric is read
     between doublings, and after growth stops (`GROW-STOP-20261110-001`), not across them. On the 7 × 7 tube, every balanced schedule
     read is deaf beyond distance 4.
   - **Next (taken, next entry).** Expansion as a reading: the triangle excess as a function of the doublings each trip crosses
     ([decision note](../research/METRIC-GROW-20261110-001/metric_grow.md)).

   **2026-11-10: the plane reads its own expansion** (`EXPAND-READ-20261110-001`).
   - **The question.** If the growing plane's time lengths break the triangle inequality because the plane grows during a trip, can the
     plane read that growth, and is it the whole of the excess? Frozen first, on 891 schedules at three spacings.
   - **The scale factor, read exactly (exploratory, exact).** Between rings, crossing one original spacing takes 4g·2^k lags after k
     doublings, in every one of 2,368 readings: each doubling doubles the time to cross, because it doubles the rings to cross and a
     front crosses a ring in 2g lags at every stage.
   - **A metric at the plane's own scale, up to 2.** Count a lag after k doublings as 2^-k of a lag (conformal time, A56). The round trip
     then breaks the triangle inequality in 28 of 891 schedules, by at most 2, where in plain lags it breaks it in 240, by up to 78.
     The expansion is the excess, up to a bounded residual; strictly, both predictions fail on that residual.
   - **Reading.** The network's own crossings keep the conformal clock, so the clock is not only the observer's. The resemblance to
     comoving distance in an expanding space is a resemblance of counting, not a physics claim; the board is still drawn (A51).
   - **Next (taken: B125, next entry).** The conformal metric as a theorem (sub-goal B125; Payoff 3/3, Concreteness 2/3)
     ([decision note](../research/EXPAND-READ-20261110-001/expand_read.md)).

   **2026-11-10: the conformal metric, proved** (`CONF-METRIC-20261110-001`).
   - **The question.** Sub-goal B125: is the growing plane's round trip, in its own clock, a metric up to a constant at every size and
     for every schedule, not only in the schedules read?
   - **Yes (proved).** In one stage, the earliest arrival between cells is a taxicab distance on the lattice of contacts: the contacts
     sit at the midpoints of the rings' sides, a route goes a quarter-turn round a ring from one to the next in g lags, and two such hops
     make exactly one ring step along an axis. Conformal time makes that speed the same in every stage, and what a doubling adds (a ring
     shrinking toward its corner, one possible wait) shrinks with the stage and sums to a constant. So the first arrival between original
     rings is 4g times their taxicab distance up to a constant, and the round trip is a metric up to 42g + 4. In plain lags the excess
     doubles with each doubling a trip crosses (computed).
   - **The 4g·2^k law follows in a line** from the two hops per ring step: it was a consequence of the construction, read by the census.
   - **Reading.** The first proved statement in this line that a uniform local law, growing, reads a distance between its original
     rings in its own clock at every size. It is coarse, the board is still drawn (A51), and the distance read is the drawn board's.
   - **Next (taken instead: B108, next entry).** Sharp constants: the readings stay within 6 below and 4g above, the bounds are 6g and
     9g + 2 ([decision note](../research/CONF-METRIC-20261110-001/conf_metric.md)).

   **2026-11-10: growth does not round the reading** (`ROUND-READ-20261110-001`).
   - **The question.** Backlog B108: does the growing plane read a distance rounder than its board's taxicab one, the diagonal ring
     heard earlier than the axis ring at the same taxicab distance by a margin that grows?
   - **No (exploratory, exact, frozen census).** On 113 schedules, to distance 20, route readings stay taxicab (the diagonal and the axis
     within 9 conformal lags), as the theorem requires. Plain hearing is less round still: on the first stage the diagonal ring at
     distance d is heard only when the axis ring at the next power of two would be, on time exactly at d = 2, 4, 8, 16; growth perturbs
     this but keeps it square.
   - **What the law adds to the board.** Scale and clock (2g lags per ring step, and the expansion), bounded offsets (rule 60 reads
     leftward), and a binary plain reading from Pascal's triangle mod 2. The coarse outline, taxicab, is the drawn board's; roundness
     would have to come from the board.
   - **Next (taken instead: readings on other boards, next entry).** The plain reading's power-of-two law as a theorem
     ([decision note](../research/ROUND-READ-20261110-001/round_read.md)).

   **2026-11-10: the reading is the board's** (`BOARD-READ-20261110-001`).
   - **The question.** Does any drawn board make the route reading rounder than its own graph distance, or is the reading always the
     board's graph metric up to a constant?
   - **Always a polygon (proved).** On every periodic board, the route reading is, up to a constant, a norm whose unit ball is the
     polygon of its cycles' displacement per length: never round. This is a classical fact about periodic graphs, applied here.
   - **The board's own polygon (computed).** On the square, triangular, honeycomb and kagome boards, at every g read, the route reading
     is the board's graph distance times g·d/2, d the ring degree: a route crosses a ring by going half way round it, on average over
     its turns.
   - **The growth line's verdict.** A plane of rings grown by the doubling law reads, in its own clock, the drawn board's distance,
     scaled, up to a constant; the law adds scale, clock, offsets and a binary plain reading, and no outline of its own. A chosen outline
     would need the board itself to follow the rules (sub-goal B92) ([decision note](../research/BOARD-READ-20261110-001/board_read.md)).

   **2026-11-09: which finite maps rescue late rings** (`RESCUE-MAP-20261109-001`).
   - **The question.** Every flat tiling is late from distance 4 to 6, so a torus reads distance plainly only if its wrapping rescues
     the cover's late rings. Which tori do, of every proportion, and why does a short loop rescue while its mirror image does not?
   - **Short loops with one fastest way (proved).** A torus is on time exactly when it holds a short loop along which the fastest way
     to every ring is a single route, or is one of finitely many small tori (23 square, 85 triangular, 15 honeycomb, listed). The
     loops are (2, 0) and (2, 1) on the square lattice, up to the quarter turn, and every vector of length √3 on the triangular one;
     the honeycomb has none. The rescue is not a third route that makes a count odd: it is a strictly shorter route round the loop.
   - **Why the mirror fails (proved).** Along the loop (1, 2) the fastest routes climb two rings per two arcs and can take their side
     step at any of j places, so a closest contact has j routes and is late whenever j is even, first at distance 4. Rule 60 reads one
     way round every ring, so a loop and its mirror image are different substrates.
   - **How it was proved.** The systole lemma holds for every cover, so a late tube makes every thick torus it covers late; the two
     thin tubes are proved on time by local conditions checked on one period; the finitely many tori in between are read exactly.
   - **Reading.** Thin reads plainly, thick needs freezing: apart from small cases, a flat torus reads its own distance without
     intervention only when it is a tube with a unique fastest way along it, as a loop of rings is. No lag cutoff was used.
   - **Next (selected, B21).** Which lattices compose everywhere; rescue on maps of higher genus is backlog B27
     ([decision note](../research/RESCUE-MAP-20261109-001/rescue_map.md)).

   **2026-11-09: which lattices compose everywhere** (`LATTICE-REACH-20261109-001`).
   - **The question.** The odd square n × n tori compose everywhere: every contact needs every ring. Which tori of every proportion, on the
     square, triangular and honeycomb lattices, do?
   - **Digons stop it (proved).** Where two rings meet at two contacts in a row, their walks cancel at once: a factor of the walk
     polynomial vanishes and every contact needs only a handful of rings. The triangular lattice has no such tori.
     *Corrected on 2026-11-09 (wording): the configuration is not a face of two sides but a doubled pair, the same order on both
     rings (`REROUTE-20261109-001A`; `docs/CORRECTIONS.md`).*
   - **At odd index nothing else does, nearly (computed, to index 151).** Every triangular torus of odd index composes everywhere, every
     square one without a digon does, and every honeycomb one without a digon does except the n × n tori whose side 3 does not divide
     (the pinned ring of the earlier entry) and one torus of index 63.
   - **At even index there is no simple rule (computed).** Most tori compose everywhere, but neither the lattice modulo 16, nor the
     2-part of the torus's group, nor its mirrors tell which: squaring the walk polynomial doubles the lattice, and at even index
     doubling folds the torus onto half of itself, so the parity of sums over its halves decides at every scale.
   - **Reading.** Composition fails for a local reason (a digon) or a symmetric one (a pinned ring), and at even index for the prime 2,
     to which walk counts mod 2 are tied. No lag cutoff was used.
   - **Next (selected, B27).** Rescue on maps of higher genus
     ([decision note](../research/LATTICE-REACH-20261109-001/lattice_reach.md)).

   **2026-11-09: full reach on the cut-open torus, the proof** (`FULL-REACH-PROOF-20261108-001`).
   - **The question.** Does full reach on the cut-open torus fail exactly at the powers of two from 8, as computed to side 48?
   - **The box is the torus minus a cross (proved).** Its walk is the uncut torus's with the two lines of cut contacts deleted. It
     commutes with the quarter turn, the mirrors carry it to its transpose, and it plus its transpose is the product of two rule-90
     walks along a side.
   - **At powers of two the torus dies (proved).** When n is a power of two the uncut torus's walk vanishes after n steps, so
     everything the cut-open box does comes from its two cut lines, which behave as circles: its whole spectrum is one 2n × 2n
     determinant.
   - **The collapse (computed, to side 64).** Every eigenvalue is a (2n − 1)-th root of unity at sides 4, 8, 16, 32 and 64 and at no
     other side, and there the eigenvalues come with triangular multiplicities k(k + 1)/2.
   - **Reading.** The failures at powers of two are a boundary effect on two circles. The theorem is not proved, and at other sides the
     spectrum is generic. No lag cutoff was used.
   - **Next (selected, taken by `CONE-COLLAPSE-20261109-001`).** The collapse at every power of two, after the tie law
     ([decision note](../research/FULL-REACH-PROOF-20261108-001/full_reach_proof.md)).

   **2026-11-09: the first tie of shortest routes** (`TIE-LAW-20261109-001`).
   - **The question.** In a tiling with rings of m contacts and faces of f, two shortest routes were computed to first tie at
     τ = L − L/m − L/f + 1, L = lcm(m, f). Why does no tie come earlier?
   - **No tie before τ (proved, every tiling).** Two tied routes enclose a disc. Counting its corners gives its length:
     d = K(1 − 1/m − 1/f) + 1 − n, where K = km = jf counts the ring and face corners and n the contacts inside. A shortest route
     runs along each cell beside it only once and never too long, so n counts the cells neither route touches; such a cell needs a
     whole ring of neighbours inside the disc, which a disc of the smallest size L cannot hold and a larger one pays for in length.
   - **The tie at τ (proved when m = f, computed elsewhere).** Every closed route is at least as long as a cell, so when m = f the
     long way round a ring and the long way round a face tie at m − 1. Elsewhere the tie at τ is read on every cover, to 24.
   - **Reading.** The first tie is a single row of cells, rings along one route and faces along the other: the plain first need reads
     every contact closer than τ on time, on every flat or curved tiling. No lag cutoff was used.
   - **Next (selected, taken by `CONE-COLLAPSE-20261109-001`).** The full-reach collapse at every power of two
     ([decision note](../research/TIE-LAW-20261109-001/tie_law.md)).

   **2026-11-09: the cone behind the collapse at powers of two** (`CONE-COLLAPSE-20261109-001`).
   - **The question.** On the cut-open torus every eigenvalue of the walk is a (2n − 1)-th root of unity exactly at the powers of two
     (computed to side 64). Why?
   - **Two particles (proved).** A contact is a pair of positions on one side: at each step one crosses a bond and the other steps
     right or left, according to the bond crossed.
   - **Four copies of a cone (proved, every side).** The quarter turn moves every contact, so the spectrum is four copies of the
     spectrum of the cone the turn folds the box into. At powers of two the cone's spectrum is one return map of the cut line around
     the corner, a matrix half a side across, and its Smith form is the cone's Jordan data.
   - **A rigid law (computed to 64; the collapse also at 128).** Each eigenvalue λ appears k(k + 1)/2 times with Jordan blocks
     2k − 1, 2k − 5, ..., the pattern of a symmetric square in characteristic 0; the count is odd exactly when the trace of 1/λ is 1;
     and the cones of sides n and 2n agree to degree 2n.
   - **Reading.** The collapse looks like a two-particle state built from one particle per eigenvalue. That particle has not been
     found, and the collapse is not proved. No lag cutoff was used.
   - **Next (selected by the coordinator: the return map digit by digit, taken by `RETURN-DIGITS-20261109-001`).** The single
     particle behind the symmetric square was the recommendation ([decision note](../research/CONE-COLLAPSE-20261109-001/cone_collapse.md)).

   **2026-11-09: the return map digit by digit** (`RETURN-DIGITS-20261109-001`).
   - **The question.** Can the cone's return map at side 2^(m+1) be built from the one at 2^m, and does that prove the collapse?
   - **A recursion (proved).** The return map is a one-dimensional operator on polynomials of degree below n/2; a two-by-two block
     rule builds it digit by digit, starting from the one-by-one matrix [c].
   - **What powers of two do (proved).** Take away one reversal of the cut line and the eigenvalues are c times the elements of
     GF(n) of trace 1. Put it back (it is multiplication by an involution) and the cone polynomial becomes the determinant of the
     trace polynomial of GF(2n), μ + μ² + μ⁴ + ... + μ^n, with its coefficients replaced by matrices over GF(2).
   - **Reading.** For the scalar trace, every root lies in GF(2n) in one line, since Tr² + Tr = μ^(2n) + μ; for the matrix version
     that step is what is left. The trace factor itself divides the cone polynomial once with a square left over, at every side to
     128. No lag cutoff was used.
   - **Next (selected, taken by `LINEAR-ROOTS-20261109-001`).** The roots of the linearized determinant
     ([decision note](../research/RETURN-DIGITS-20261109-001/return_digits.md)).

   **2026-11-10: the roots of the linearized determinant** (`LINEAR-ROOTS-20261109-001`).
   - **The question.** Does every root of the cone polynomial lie in GF(2n), and how often does each one occur?
   - **The multiplicities are Kloosterman sums (computed, exact).** Let K(a) be the sum over x in GF(2n) of (−1)^Tr(x + a/x). Then
     the eigenvalue 1/a occurs K(a)(K(a) − 2)/8 times, with |K(a)|/4 independent eigenvectors, and not at all when K(a) = 0. In
     elliptic-curve terms the eigenvalue is the j-invariant of the curve y² + xy = x³ + a, and its multiplicity is (t² − 1)/8 for that
     curve's trace of Frobenius t. Every eigenvalue matches at sides 4 to 128, and every eigenvector count to side 512.
   - **Why that would be enough (proved).** A classical identity, the second moment of Kloosterman sums, makes these multiplicities
     add up to exactly the size of the cone. So if each eigenvalue in GF(2n) occurs at least that often, nothing is left over for
     eigenvalues outside GF(2n): the collapse would follow.
   - **Where the sum comes from (proved).** The eigenvectors at each eigenvalue are one explicit kernel; on GF(2n) its multiplier is
     y^h Tr(b⁴/y) + b²/y^h, the trace of GF(2n) beside a shift, and the shift itself traces the Kloosterman curve
     Y² + Y = x + c⁻⁴/x.
   - **Reading.** At sides that are not powers of two the eigenvalues are not even in the field of (2n − 1)-th roots of unity: what
     makes powers of two special is the arithmetic of elliptic curves over GF(2n). The lower bounds are not proved. No lag cutoff was
     used.
   - **Next (selected, taken by `KLOOSTERMAN-BOUNDS-20261110-001`).** Prove the lower bounds, starting from that kernel
     ([decision note](../research/LINEAR-ROOTS-20261109-001/linear_roots.md)).

   **2026-11-10: the Kloosterman lower bounds** (`KLOOSTERMAN-BOUNDS-20261110-001`).
   - **The question.** Can the multiplicities be proved, starting with the eigenvectors: at least |K|/4 of them at each eigenvalue?
   - **One polynomial per eigenvalue (proved).** The eigenvectors at an eigenvalue are all one polynomial G times polynomials in
     Y = k² + k. Two short facts give it: the operator is self-adjoint, and any two eigenvectors change by the same factor under the cut
     line's shift. So their number is ⌈(n/2 − deg G)/2⌉.
   - **The count is one degree (computed).** deg G = n/2 − k at every eigenvalue for sides 8 to 512, where k(k + 1)/2 is the
     multiplicity; with the theorem this is the Kloosterman count |K|/4.
   - **Reading.** Proving the eigenvector count now means bounding the degree of one polynomial per eigenvalue; nothing found ties it to
     the Kloosterman sum, and the Jordan chains, which the collapse needs, were not reached. No lag cutoff was used.
   - **Next (selected, taken by `JORDAN-CHAINS-20261110-001`).** The Jordan chains that G·Y^j heads
     ([decision note](../research/KLOOSTERMAN-BOUNDS-20261110-001/kloosterman_bounds.md)).

   **2026-11-10: the Jordan chains from one polynomial** (`JORDAN-CHAINS-20261110-001`).
   - **The question.** Does each eigenvector G·Y^j head a Jordan chain of length 2k − 1 − 4j, so that the multiplicity k(k + 1)/2 follows
     from the degree of G alone?
   - **Yes, wherever tested (computed).** At every eigenvalue for sides 8 to 64, and at nine eigenvalues of side 128 up to the eigenvalue 1
     with k = 15 (the side-128 check, which finished after the epic closed, passed).
   - **Its first order (proved).** The family that carries the spectrum is self-adjoint at every parameter. On the eigenvectors, its first
     derivative is a Hankel matrix of the top coefficients of G's norm G(k)G(k + 1), whose degree n/2 − k makes all but one corner vanish.
     So there is exactly one Jordan block of size 1 when k is odd and none when k is even.
   - **Reading.** An eigenvalue's whole Jordan structure is read off one polynomial's degree; the collapse now rests on that degree (B74) and
     on the chains at every order. No lag cutoff was used.
   - **Next (selected, taken by `CHAIN-ORDERS-20261110-001`).** The chain lemma at every order
     ([decision note](../research/JORDAN-CHAINS-20261110-001/jordan_chains.md)).

   **2026-11-10: the chain lemma at every order** (`CHAIN-ORDERS-20261110-001`).
   - **The question.** Does the chain lemma hold at every order, and why?
   - **One leading form (computed).** Near each eigenvalue the family is a single moment matrix. On the eigenvectors G·Y^j its reduction
     starts, entry by entry, at u^(2k−1−2(i+j)), u = (w − a)/a, with coefficient 1 exactly when k − i − j is a power of two: the Hankel
     matrix of u⁻¹Y^k L(u²/Y), L(x) = x + x² + x⁴ + ⋯. This holds at every eigenvalue for sides 8 to 256.
   - **It is the whole lemma (proved).** That leading matrix has determinant 1 over GF(2) for every k, by halving k, so the form gives
     each eigenvalue's blocks 2k − 1, 2k − 5, …. The form itself is proved for its first three orders: no block of size 2, one of size 1
     when k is odd and one of size 3 when it is even; for k ≤ 2 that is everything.
   - **Reading.** The same linearized polynomial L drives the family and shapes its answer, one term per power of two; its continued
     fraction is what makes a characteristic-0 pattern appear over GF(2). No lag cutoff was used.
   - **Next (selected, taken by `LEADING-FORM-20261110-001`).** The leading form at every order, or halving the index
     ([decision note](../research/CHAIN-ORDERS-20261110-001/chain_orders.md)).

   **2026-11-10: the leading form at every order** (`LEADING-FORM-20261110-001`).
   - **The question.** Can the leading form be proved at every order, either order by order or by halving the index k?
   - **The index does not halve (computed, frozen).** At every eigenvalue with even k ≥ 4 for sides 16 to 64, the reduction mixes the
     even and odd powers of Y below the orders that matter, so an induction on k has nothing to stand on.
   - **The operator is a Wronskian (proved).** Multiplied by G, the kernel operator is (k + 1)·W(G, F), where
     W(A, B) = A(k)B(k + 1) + B(k)A(k + 1) is a polynomial in Y. That makes the second chain vector's Wronskian explicit, and it gives a
     second solution G′ whose Wronskian with G is a single power of Y, like two consecutive convergents of a continued fraction.
   - **Where it stops.** The second vector needs G′, and the cancellation at co-distance 3 (the corrections adding 1 to a pure part of 1)
     was not derived; by the rule frozen beforehand, the attempt ends at order 2. No lag cutoff was used.
   - **Next (selected, taken by `CODIST-THREE-20261110-001`).** The leading form through the pair of solutions, bounded to co-distance 3
     ([decision note](../research/LEADING-FORM-20261110-001/leading_form.md)).

   **2026-11-10: the co-distance-3 cancellation** (`CODIST-THREE-20261110-001`).
   - **The question.** Can the next order of the leading form, its vanishing at co-distance 3, be derived?
   - **The second order is a gap (proved).** The chains' second step exists exactly because N·L(Y), with N = G(k)G(k + 1) and
     L(Y) = Y + Y² + ⋯ + Y^(n/4), has no terms between degree n/2 − k + 1 and n/2 − 2.
   - **Half of the next order (proved), the rest computed.** At co-distance 3 the order-4 coefficient splits into five pieces. Two vanish
     by the gap and because, in characteristic 2, a double sum over pairs of powers of two keeps only its diagonal: that is where the
     leading form's powers of two come from. The other three add to 0 at every pair tested.
   - **Reading.** The rest needs the high coefficients of a quotient by the Padé denominator Q, which were not found; by the rule frozen
     beforehand the collapse line is parked, with the curve behind each eigenvalue (B59) picked first for a restart. No lag cutoff was
     used.
   - **Next (parked).** The collapse line pauses here ([decision note](../research/CODIST-THREE-20261110-001/codist_three.md)).

   **2026-11-11: the corner's row** (`CORNER-ROW-20261110-001`).
   - **The question.** The block matrix that gives the corner's return law gives, in its whole first row, the walks from the corner to
     every contact of the two side walls, and with them the full-reach count (B137). Does that row have a closed form at every power of
     two? The rule was to be found on the sides 4 to 32 and written down before side 64 was computed to test it.
   - **No closed form (computed, exact, side 64 held out).** Rules were found only for the six entries next to the corners, all known
     before the search, and none for the rest of the row. Under the rules frozen beforehand this is a partial rule, and the line stops.
   - **What the row carries instead (computed, exact, 4 to 64).** Each entry is a fraction in s, and across the row the denominators
     vanish exactly at the elements a of GF(2n) whose Kloosterman sum is not zero, the a for which the curve y² + xy = x³ + a does not
     have 2n points. That only those elements occur is the cone's spectrum again, as for any walk in the box; that the corner's walks to
     the walls reach every one of them, as squares with largest exponent 2⌈|K|/8⌉, is the row's own.
   - **Reading.** The reduction to one walk count took the failure of full reach away from the spectrum, but read through the corner row
     the count meets it again. Whether the count itself needs the spectrum is open.
   - **Corrected.** The training verdict named four entries with rules where six have them and called the outcome "no pattern"; the
     entry on both halves of full reach said more than its reduction shows (`docs/CORRECTIONS.md`, 2026-11-11).
   - **Next (parked).** The corner line pauses here by its frozen stop, and the coordinator picks the next line
     ([decision note](../research/CORNER-ROW-20261110-001/corner_row.md)).

   **2026-11-10: the corner return law** (`RETURN-LAW-20261110-001`).
   - **The question.** At a power of two the corner of the cut-open torus returns to itself as 1/(1 + w⁴ + w⁸ + ⋯ + w^(4n)) says, the
     trace polynomial of GF(2n) (computed). Can that be proved, from the quadrant's Catalan law and one far wall up to the box?
   - **Cut where the corner is restricted (proved).** On the first column the corner's walk cannot step north, and in the box the last
     column cannot step south; everywhere else rows and columns move independently. Cutting the walks at those columns turns the count
     into a matrix on the rows alone: one path for the quadrant or a half-strip, a block of two for the box, explicit at a power of two.
   - **Proved at every power of two to 512 (exact computation).** The corner's returns and the law obey linear recurrences of bounded
     order and agree for longer than both, so the law holds exactly at 4, 8, …, 512. For every m it rests on one finite identity per
     side, unproved.
   - **A looped path (proved).** At a power of two the trace polynomial is the determinant of a path of n sites with a loop at one end.
     So, read every four steps, the corner returns exactly as that path's loop end does; in the quadrant the path is endless.
   - **One far wall is invisible at every even side (computed to 80).** Not only at powers of two; at odd sides it is seen at time 4n,
     and with the bottom wall removed too it is seen at every side.
   - **Reading.** The power-of-two effect at the corner is a small one-dimensional object, a quotient of the corner's orbit, but no
     explicit map onto it is known. The full-reach count (B137) lives in the same block matrix, as the corner's whole row.
   - **Next (selected, awaiting the coordinator).** The corner's row of the block inverse (B140)
     ([decision note](../research/RETURN-LAW-20261110-001/return_law.md)).

   **2026-11-10: both halves of full reach** (`REACH-HALVES-20261110-001`).
   - **The question.** The cut-open square torus loses full reach exactly at the powers of two from 8 (computed). Can either half be
     proved: the failure at every power of two, and full reach at every other side?
   - **The failure is one walk count (proved).** If the contact next to a corner never reaches the point half a side away just below the
     diagonal, the contact just above it never reads the corner's ring, and full reach fails. On every other contact the walk is a grid
     walk with a conveyor belt (no step left on the bottom row, none right on the top row), so the failure needs only that walks from one
     corner of that grid to one diagonal point are even in number at every length. That reduction does not use the spectrum, which eight
     epics studied; whether the count needs it is open (corrected 2026-11-11).
   - **A symmetry the box hides (proved).** The box's mirrors swap the walk with its reverse, but the mirror through the corner's
     neighbour and the target is a true symmetry of the walk. Mod 2 it cancels every excursion off that diagonal except those above it
     that reach the left or top wall; in the open plane nothing gets through.
   - **Computed to side 128.** The count vanishes at every power of two from 8 to 128, and there the corner reads every contact but the
     target and a few points like it. The corner returns to itself exactly as the trace polynomial of GF(2n) says: its return series is
     1/(1 + w⁴ + w⁸ + ⋯ + w^(4n)). In the quadrant it returns as often as the Catalan numbers are odd, and the box folds that pattern
     modulo 2n − 1. With either far wall removed the corner's returns are the quadrant's and it does reach the target: all four walls
     are needed.
   - **The other half.** Full reach holds at every side from 3 to 130 except exactly 8, 16, 32, 64 and 128, as predicted before the run,
     but no infinite family is proved; a cyclic contact in every ring would suffice, and that holds only at scattered sides.
   - **Reading.** Why powers of two fail now sits in one corner's walk, where the trace of GF(2n) appears in the plainest form. A proof
     of the return law is the cheapest way in. No lag cutoff was used.
   - **Next (selected, awaiting the coordinator).** The corner return law as a theorem (B138)
     ([decision note](../research/REACH-HALVES-20261110-001/reach_halves.md)).

   **2026-11-09: rescue on maps of higher genus** (`RESCUE-GENUS-20261109-001`).
   - **The question.** Tori read distance plainly when a short loop gives every ring a single fastest way. 141 of 706 regular maps of
     genus at least 2 read it too. Are they rescued the same way?
   - **Yes, out of sample (census, pre-registered).** On seven groups not read before, every one of the 77 on-time maps (of 1,056) has,
     at every ring, a closest contact reached by a single shortest route. On the earlier roster one map in 141, of S6 and genus 61,
     rescues two rings by odd counts of several routes instead.
   - **Ties beside a single route are harmless.** Most on-time maps have rings with a tied closest contact; another closest contact with
     one route rescues them.
   - **Reading.** The plain first need asks only for an odd count, but in practice reading distance plainly means having a unique
     fastest way. What makes a map keep one at every ring is not yet known beyond tori. No lag cutoff was used.
   - **Next (research directions, none selected).** Growing a network that keeps a single fastest way (B34); a criterion on the map
     (B35) ([decision note](../research/RESCUE-GENUS-20261109-001/rescue_genus.md)).

   **2026-11-09: grow a single fastest way** (`GROW-PLAIN-20261109-001`).
   - **The question.** A network reads its distance plainly when every ring keeps a single fastest way. Can a law grow one that does
     at every stage?
   - **Yes, one ring at a time (proved).** Inserting a ring into the twist torus, cutting the three contacts that span the gap and
     rejoining them through the new ring, gives the next twist torus: from 4 rings every stage keeps every contact persistent and
     reads its distance across time with nothing frozen. The band law loses this at its second band.
   - **But only a line (proved).** Any growth through tori that keeps the reading at every stage ends up in a tube, whose balls grow by
     4 rings per step: dimension 1.
   - **The S6 exception (exact).** The one map of higher genus rescued by parity has three routes to a ring's closest contact, each
     round a different handle: three lifts of the target arriving together.
   - **Reading.** A law can grow space that reads its own distance across time without intervention, but on tori only a line; a plane
     read plainly needs another substrate, if one exists. Stages are read as fixed networks (A42). No lag cutoff was used.
   - **Next (research directions, none selected).** A plane read plainly beyond tori (B36); a ring inserted while running (B37)
     ([decision note](../research/GROW-PLAIN-20261109-001/grow_plain.md)).

   **2026-11-09: a ring inserted while running** (`RING-RUN-20261109-001`).
   - **The question.** The twist tube grows one ring at a time and reads its distance plainly at every stage, read as fixed networks.
     What survives if the ring is inserted while the tube runs?
   - **What it has not reached (census, pre-registered).** Every binding of a ring the insertion has not reached survives, and the new
     ring is bound at every lag, as for bands.
   - **What it has reached.** About half of those bindings fail (53% when the rewired contacts keep their values, 51% when they are
     born anew), against 68% for a band. Clean insertion lags are lag 0, or the first lag or two, apart from two tubes.
   - **Reading.** Ring by ring as band by band, a law that grows while it runs keeps only its young knots: growth must come between runs
     (A42). No lag cutoff was used beyond the census's stated cap.
   - **Next (selected, B36).** A plane read plainly beyond tori
     ([decision note](../research/RING-RUN-20261109-001/ring_run.md)).

   **2026-11-09: a plane read plainly beyond tori** (`PLANE-PLAIN-20261109-001`).
   - **The question.** Tori read their distance plainly at large size only as tubes. Is there another flat network of persistent
     contacts that might do it as a plane?
   - **Not among the periodic tilings read (census, pre-registered).** On 13 tilings (the three regular ones, five Archimedean ones
     built by medial and truncation, and their duals), a contact persists exactly when a symmetry fixes it and exchanges its two rings,
     and only the regular tilings have that at every contact. Mixing ring or face sizes takes the symmetry away.
   - **Reading.** A flat network of persistent contacts is a regular lattice, and it reads its own distance only through freezes,
     except as a thin tube. A plane read plainly would have to be non-periodic or keep persistence without that symmetry. No lag cutoff
     was used.
   - **Next (research directions, none selected).** Persistence without a flip (B40); the remaining periodic tilings (B41)
     ([decision note](../research/PLANE-PLAIN-20261109-001/plane_plain.md)).

   **2026-11-09: does persistence need a flip?** (`FLIP-RULE-20261109-001`).
   - **The question.** On 13 periodic tilings a contact persisted exactly when a symmetry fixes it and exchanges its two rings. Is that
     so on every uniform tiling, and on every network?
   - **On every uniform tiling, yes (census, pre-registered).** The snub and elongated tilings and their pentagonal duals obey it too:
     on all 22 Archimedean and Laves tilings persistence is exactly symmetry, and only the regular lattices have it at every contact.
   - **On networks in general, no (census, pre-registered).** Among all maps of up to five contacts, contacts persist without such a
     symmetry from three contacts on, though there only in degenerate ways. On larger maps whose rings and faces all have three or
     more contacts, most persistent contacts have none: their closed walks are simply even in number at every length.
     *Narrowed on 2026-11-09: up to six contacts the walks are paired, by doubled pairs (two arcs from one contact to the same next
     contact) or by symmetries of the contact graph; with no pairing found only from seven (`REROUTE-20261109-001A`;
     `docs/CORRECTIONS.md`).*
   - **Reading.** On a uniform plane only symmetry cancels every return; on small irregular networks counting does. A plane read
     plainly is ruled out among the periodic tilings, not among irregular networks. No lag cutoff was used.
   - **Next (taken, B43 then B42, next entry).** Large networks persistent without flips (B42); why the parity comes out even
     (B43) ([decision note](../research/FLIP-RULE-20261109-001/flip_rule.md)).

   **2026-11-09: large networks persistent without flips** (`REROUTE-20261109-001`).
   - **The question.** Small maps persist without a flip. Why does the smallest example's parity come out even, and do large networks
     keep every contact persistent that way?
   - **The example is paired (proved).** Two of its contacts send both their arcs to one next contact. Every closed walk passes one, and
     switching the arc there pairs the walks. Up to six contacts every case is such a pairing or a symmetry of the contact graph; from
     seven on most cases have neither (computed), and only a parity of cycle families remains.
   - **Persistence belongs to the automaton (proved).** At these contacts a contact reads one cell of each ring and both rings read it,
     so nothing in the law says which way a ring continues through it. Exchanging the continuations at any contacts leaves the automaton
     unchanged, so every contact still persists, and a random exchange leaves no symmetry at all (census, pre-registered).
   - **Reading plainly belongs to the rings (proved for the square).** The square torus's automaton is late when its cells are grouped
     into small rings and on time when they are grouped into lines; no grouping into small rings reads its distance plainly.
   - **Reading.** Persistence never needed a flip because it never saw the rings. How a plane reads its distance depends on how its
     rings are declared (A45): a declared plane of small rings needs freezing, and what reads plainly is again a line. No lag cutoff was
     used.
   - **Next (taken, B45 and B46).** Rings the law can see (B45, `RING-LAW-20261109-001`); a plane of long rings (B46, next entry)
     ([decision note](../research/REROUTE-20261109-001/reroute.md)).

   **2026-11-10: a plane of long rings** (`LONG-RINGS-20261110-001`).
   - **The question.** The square torus's automaton reads its distance plainly only when its rings are long. Could long rings running
     in two directions read it plainly and still form a plane?
   - **Not among the periodic groupings (census, pre-registered).** Of about two million groupings with a small period, every one that
     reads plainly is a family of parallel lines that wind round the torus, along an axis or a diagonal of slope 1, 2, 3, 5, 7 or 5/3.
     Each line touches only its two neighbours, so the rings form a cycle. Where lines of two directions cross, or a ring closes up,
     some reading comes late.
   - **Reading.** Lines of every slope are reached the same way, by a single straight route from each target to the line's nearest
     contact. What reads plainly is one direction of lines, so under this law a plane of rings still needs freezing. No lag cutoff was
     used.
   - **Next (research directions, none selected).** Prove that only lines read plainly (B75); groupings without a period (B76)
     ([decision note](../research/LONG-RINGS-20261110-001/long_rings.md)).
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

   **2026-11-11: what it takes to hold a count** (`HOLD-COUNT-20261111-001`).
   - **The question.** The owner asked whether knapsack, whose choices are summed into one running total, could be a picture of
     what happens where logic emerges. A total is a magnitude, and the knot's own law has no preferred value. Which counts can a
     drawn knot pattern hold?
   - **Only counts that look the same from both sides (proved, refereed).** Flipping every distinction of such a pattern gives
     another allowed state, so c distinctions on looks like n − c on from the other side. Such a pattern reads a count of n held
     distinctions mod m only when m is even and n odd: never in threes, unless the outside fixes a value.
   - **In binary, at the least size (exact).** The 8-distinction pattern drawn on a torus that counts three held distinctions
     mod 2 also reads their majority at another distinction: parity and carry, the two binary digits of the count, a full adder.
   - **One fixed value is not enough here (exact in range).** With a fourth distinction held at 0, no drawn knot pattern up to 20
     distinctions counts in threes. A distinction would have to read whether three held distinctions are not all equal, the knot's own relation, and none does
     ([decision note](../research/HOLD-COUNT-20261111-001/hold_count.md)).

   **2026-11-11: does a drawn knot pattern read its own relation?** (`OWN-RELATION-20261111-001`).
   - **The question.** To count in threes with one fixed value, a distinction would have to read whether three held
     distinctions are not all equal, against a fourth: the knot's own relation, read as a map. Nothing in the rules forbids it,
     and knot systems built freely can do it. Do drawn knot patterns, where every distinction lies in three knots?
   - **None in range (exact, refereed).** On 453 random drawn knot patterns of 16 to 20 distinctions, 180 million sets of four held
     distinctions, the knot's own relation and the parity-majority switch never appear; the readings that do are majorities
     fed by at most one parity.
   - **Bigger is not better.** Past 16 distinctions held distinctions force less: four-distinction readings get rarer, so a
     larger random search would not settle it. Whether any drawn knot pattern reads its own relation is open
     ([decision note](../research/OWN-RELATION-20261111-001/own_relation.md)).

   **2026-11-12: arithmetic of harmonies without a zero** (`HARMONY-ARITH-20261112-001`).
   - **The question.** The owner asked what subtraction and division of logical harmonies are. A running total needs a zero
     the knot law cannot make; a harmony needs none. Read a harmony as a base periodic along one shift whose allowed states all
     repeat (A70). What happens when two are stitched, knot by knot, at every shift?
   - **Stitching multiplies; the shared divisor counts; nothing subtracts (proved, for any law).** A stitched state pairs a
     state of each, so it repeats at their least common multiple; the pairs from two orbits of periods p and q fall into
     gcd(p, q) offsets, each kept or removed whole; no stitched state has period p − q or p mod q.
   - **The knot law's harmonies are even (exact, to span 12; not proved).** Under not-all-equal every harmony among 47,971
     patterns has states of even period only, and where the pattern does not split, each state flips under half its period.
     *Narrowed 2026-11-12 (`ODD-SEARCH-20261112-001`): not at every period. An odd harmony of period 61 exists; no odd one up to
     29, or at 31 or 37.*
     Odd parity makes the periods of linear recurrences, the exactly-one law multiples of 3.
   - **The mirror reads a power of 2 (proved).** Flipping every value pairs the offsets of two such harmonies exactly when
     their periods carry different powers of 2. No stitch reads whether one period divides the other
     ([decision note](../research/HARMONY-ARITH-20261112-001/harmony_arith.md)).

   **2026-11-12: why the knot law's harmonies are even** (`EVEN-PERIOD-20261112-001`).
   - **The question.** Every not-all-equal harmony found has even periods only. Is that the mirror? Flipping every value keeps
     the law, but it only pairs a repeat of odd period with a second, mirrored one: it forbids nothing (proved).
   - **What forbids them is an unseen flip (proved).** In 001 repeating, one 0 can be flipped without any knot kind that 001
     satisfies noticing, so every base allowing 001 also allows a state that does not repeat. A word with such a flip (in itself
     or in a word compatible with it) belongs to no harmony; and a word of odd period without one would itself make a harmony.
   - **To period 29 (computer-assisted, refereed twice).** All 25,328,938 words of odd period 3 to 29 have such a flip, so no
     not-all-equal harmony, at any span and with any number of knot kinds, has an odd period up to 29. Beyond that it is open
     ([decision note](../research/EVEN-PERIOD-20261112-001/even_period.md)).

   **2026-11-12: the first odd harmony, or none** (`ODD-SEARCH-20261112-001`).
   - **The question.** Does every word of odd period have an unseen flip, so that the law's repeats are always even?
   - **No: one of period 61 (proved, refereed).** Forbid three equally spaced equal values with step 1, 2, 11 or 22, counted
     modulo 61: these 12 knot kinds allow exactly 122 states, one repeating word of period 61 with its shifts and its mirror,
     and no two differ in one place, so nothing can flip unseen and every state repeats. 61 is odd, and the base does not split.
   - **None smaller in the searched range.** None up to 29 (proved), none at 31 or 37 (complete search); periods 33, 35 and 39
     to 59 are open. The steps are the four fourth roots of 1 modulo 61 and their doubles: the law's numbers are not all even,
     and where an odd one appears it is pinned by a symmetry of the arithmetic modulo 61
     ([decision note](../research/ODD-SEARCH-20261112-001/odd_search.md)).
     *Narrowed 2026-11-12 (`ODD-FAMILY-20261112-001`, below): the symmetry is in the steps, but it is not shown to pin the word;
     the same steps fail at most other primes.*

   **2026-11-12: which odd periods the knot law makes** (`ODD-FAMILY-20261112-001`).
   - **The question.** 61 was the first odd harmony found. Which numbers does the law make as periods of harmonies, and what
     decides it? Searched in two structured families of steps (unions of cosets of a group of multipliers, and steps with their
     doubles) at every odd period from 33 to 59 and every prime from 61 to 199.
   - **Three numbers: 61, 73 and 193 (proved, refereed twice).** At 73 the steps 1, 2, 27 and 54 (27² = −1 modulo 73) allow 730
     states, five repeating words with their shifts and mirrors; at 193 six steps allow 386, one word with its shifts and mirror.
     No two states of either differ in one place, so each is a harmony, odd and unsplit. Nothing else in range, and nothing at all
     below 61 in these families.
   - **What they share, and what it does not explain.** In each, the steps are unchanged by multiplying by a fourth root of 1, so
     every period found is a prime one more than a multiple of 4. But the steps of 61 and 73 (1, 2 and their multiples by the
     fourth root) make no harmony at 14 of the 16 such primes from 41 to 197, and at 73 four of the five words are not themselves
     symmetric: the symmetry is shared, not shown to be the cause. Neither frozen explanation (the symmetry, or a near-threshold
     count) passed its test, and the counts jump from no state at 53 to over 200,000 at 89
     ([decision note](../research/ODD-FAMILY-20261112-001/odd_family.md)).
7. **Limits.** Does the program need a contact that binds infinitely many
   loops? That would need a declared limit rule, since no set of finite
   clauses defines one.

   **2026-11-12: the owner's limits near the end** (owner's statement, 2026-11-11 Pacific; not tested).
   - **His words.** Of combinations that "go for a while then die": "I get some inkling this is similar to limits. [...] the
     calculus is hard because the results themselves will be "non-spatial" [...]. They are just relative to each other. It's like
     relativity, but for logic."
   - **The coordinator's reading.** A growing knot pattern ends at the first knot after which it allows no state (A72). Near the
     end what the law forces reaches further, and the contradiction that ends a large uniform pattern holds a constant share of it
     (known). It is a limit in the exact sense if the law's own quantities, such as the largest tie class, approach a value as the
     end nears, and not if they jump; `RANDOM-FATES-20261112-001` measures this. "Relativity" is an analogy only: bond distance is
     already relative, and shortcuts are where it parts from steps apart
     ([Intuitions, lesson 7.3](../INTUITIONS.md#73-every-meeting-pattern-none-chosen)).
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
9. **Space from a law.** Logic allows every free complex. Which uniform, local
   law, not written on a space in advance, gives a meeting pattern that looks
   like a space of low dimension? This is open and shared with causal sets, quantum
   graphity and hypergraph rewriting. Since 2026-10-19 there is one necessary
   condition: a law can keep a lasting record of its own loops only if its
   contacts act as group elements on the witnesses ("Which knots remember a
   loop"). A law whose contacts have fixed points can also bind its loops
   into knots ("What networks remember, and knots among loops"), but every
   network so far was laid out by hand. A network's charge hole has a depth
   set by its layout's cut width ("How deep a hole is"): an invariant of a
   whole network's extent, though a width rather than a distance.

   **Words in the early space entries.** The entries from here to the three-regular entries place laws on declared substrates: lattice
   tori and other drawn surfaces, triangulations of three-manifolds, Sierpinski gaskets and simplices, and the triangular lattice, all
   drawn or given (A36, A51). Their tori, cylinders, walls, stripes, staircases, corners, genus, surfaces, gaskets and dimensions are
   the drawings' words. In the census entries a contact is the three-place knot placed on each edge, its visible distinction joined
   to two hidden ones. Where these entries once said that a law or a gluing builds a space, a surface or a topology, the law reproduces
   itself on a substrate that is drawn or given, or a gluing has the meeting pattern of one (reworded on 2026-11-11, `docs/CORRECTIONS.md`;
   the earlier text is in git history).

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

   **2026-10-24: what native gluing makes** (`SURFACE-GLUING-20261024-001`).
   - **Pants decompositions from sharing (proved).** Native contact requires every shared distinction to join exactly two knots.
     - Glued that way, a network has the meeting pattern of a pants decomposition of a compact orientable surface (the literature's):
       each knot a pair of pants and each open distinction a boundary circle, the genus the number of independent cycles.
     - Two-place relations glue only into chains and cycles.
     - A hub is the one case where three sheets meet.
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
   - **Reading.** Native networks see of a triangulated three-manifold only what its two-dimensional skeleton shows, its mod-2 first
     cohomology (reworded on 2026-11-11 from "Native space is two-dimensional topology").

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
     a pattern of patterns. Which laws survive that, in which gadgets, and can a law fix an orientation or a scale?
   - **Only parity survives (proved for every gadget size).**
     - The two parity knots are rebuilt by every native gadget of their copies.
     - Every other three-place knot's gadgets exclude strictly fewer tuples: none for the atoms and not-all-equal types, at most one
       when two tuples at distance two are excluded (only three copies in a cycle, drawn as a triangle), at most two when three are.
     - So towers of patterns of patterns built from one non-parity law reach the free relation within three levels.
     - The proof is the cactus structure of native contradictions (`NATIVE-HARDNESS-20261024-001B`) applied to three legs.
   - **No orientation at three places (proved).** Every three-place knot's symmetry group contains a transposition, so no
     placement orients a vertex.
   - **Four places (exhaustive for gadgets of two and three copies).**
     - 96 of the 742 four-place knots, in 6 classes, can orient a vertex. None of them survives.
     - What survives is parity, and one implication between the parities of two pairs, (x₁ + x₂ → x₃ + x₄). That implication is a
       two-place relation on derived bits, rebuilt exactly by chains, so its towers are chains.
   - **Counting (scoping).** Weighting each tuple by its number of hidden witnesses keeps only a bias at each distinction and pairwise
     bonds under the two smallest substitutions, never a three-way bond.
   - **Background (classical).** In the literature's drawing each knot of a closed native gluing is a pair of pants, a unit of
     negative curvature, so the drawing admits only hyperbolic metrics. Two-place relations are flat and pins are positively curved. The metric itself is left free.
   - **Reading.**
     - Native gluings have the meeting pattern of a two-dimensional drawing and fix its curvature type, and nothing geometric
       survives patterns of patterns. What survives every scale is parity, which draws nothing, or a pairwise law, whose towers are
       chains.
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
   - **Not-all-equal survives through the Fano pattern (proved).**
     - Its copies on the seven knots of the Fano pattern, with one distinction split into the three legs, rebuild it.
     - No gadget of six or fewer copies does, and at seven that split Fano pattern (the literature's punctured Fano plane) is the only
       one (property B: m(3) = 7).
     - Each allowed tuple has exactly five completions. So not-all-equal is an exact counted fixed point, and each level adds
       log₂ 5 bits per copy.
   - **Reading.**
     - With hubs, emergence beyond parity persists across scales.
     - The smallest pattern of patterns of the frustration knot is the Fano pattern, the literature's projective plane of order two,
       picked out by the law's own self-reproduction.
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
   - **What the towers are (proved).** Each law's smallest exact self-reproduction fixes a definite tower, drawn as:
     - the Sierpinski gasket for parity, growth exponent log₂ 3;
     - a triangle subdivided into four with private midpoints for twisted not-all-equal, exponent 2;
     - a tower of Fano patterns for not-all-equal, exponent log₃ 7.
   - **The limit (proved).**
     - Every exact tower is finitely ramified: bounded treewidth, three distinctions cut off any sub-tower. So exact
       self-reproduction never makes separation in two or three dimensions.
     - Its corners are exactly as correlated at distance s^k as at distance 1, but only at the hard law. Softening grows at least
       threefold per level, the classical picture for finitely ramified fractals.
   - **Reading.**
     - The allowed states (the canonical knot test) survive every rebuilding tower.
     - The counted law, a branch-internal measure, survives only exact ones. Set-level emergence can persist where counted
       emergence fades.
   - **Next (taken).** Shared-boundary self-reproduction (next entry).

   **2026-10-29: self-reproduction on the drawn triangular lattice** (`SHARED-SUBDIVISION-20261029-001`).
   - **The test (exact census).**
     - Copies of one knot class sit on the triangular lattice, on up triangles or on all triangles, which gives 122 rules.
     - Every triangle is cut into four, or nine, with new vertices shared between neighbours. This substrate is not finitely ramified.
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
     - On a substrate drawn in two dimensions that is not finitely ramified, exactness keeps a knot only through parity. Everything else that survives is pairwise
       (lines), and all the other knots fail.
     - This is the two/three boundary appearing as a law of self-similarity.
     - The parity families are rigid on the drawn plane, so under the source-aware reading nothing native lives there.
     - Non-linear emergence reproduces itself exactly only on tree-like substrates (the previous entry).
   - **Next (recommended, awaiting the owner).** Is exact self-reproduction on substrates that are not finitely ramified always
     affine (2/3)?
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
   - **What did not change.** On the drawn triangular lattice the answer stays parity: the shared-boundary substitution keeps
     only parity for signed laws constant on rotation orbits on the first three spheres, as `SHARED-SUBDIVISION-20261029-001` found
     with counts on the triangular lattice. Interference revives knots in finitely ramified towers, not yet on substrates drawn in two dimensions without finite ramification.
   - **Their cores, replayed (an exploratory experiment).** The eight-square identity and its 3-versus-6-bit costs, the grouped
     pieces of Anthropic's Lemma 2, the partition pieces of its Theorem B at one to three bits, and the swap-matrix lemmas of
     OpenAI's construction recompute exactly from the papers' statements; the octonion sign table is a Hadamard matrix of order 8.
   - **Reading.** The barrier the refutations break (cut cost on expanders) is the one the program measured for positive and
     linear reasoning; a counted (nonnegative) rewriting cannot lower a crossing's cut cost at all. Cancellation is the
     interference the owner's "harmonies" intuition points to: incommensurable signed parts that cancel into a whole.
   - **Owner decision (2026-10-29).** Cancelling witnesses were adopted as a second reading beside the existential one, reopenable
     (question 2; [record](../research/INTERFERENCE-20261029-001/canonical_correction_request.md)).
   - **Next (taken).** Interference on the drawn triangular lattice (next entry).

   **2026-10-29: interference on the drawn triangular lattice** (`SIGNED-SUBDIVISION-20261029-001`).
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
     - Interference reproduces knots on finitely ramified, tree-like substrates but not on the drawn triangular lattice. There, shared
       midpoints make a cancellation inside one triangle impossible to arrange across the lattice.
     - Exact self-reproduction on substrates that are not finitely ramified is affine under every reading tried: existential,
       counted, signed and real.
   - **A lead (scoping, not evidence).** Take not-all-equal with −1 exactly when the first corner is the odd one out. It reproduces
     itself exactly on the level-k Sierpinski gaskets (copies on the up triangles of a k-subdivided triangle) for k = 2 to 11, with
     factors −1, −4, 13, 85, −634, …, in exact integer arithmetic. These gaskets are finitely ramified, with dimension
     log(k(k+1)/2)/log k → 2. For laws on up triangles, the subdivided plane is these gaskets plus the up triangles that join
     neighbouring ones. So the joining triangles are what breaks exactness.
   - **Next (taken).** Signed not-all-equal on every level-k gasket (next entry).

   **2026-10-29: a knot reproduced on every gasket** (`SIGNED-GASKETS-20261029-001`).
   - **The law.** Signed not-all-equal, −1 exactly when the first corner is the odd one out, can be written three ways.
     - It is (−1)^a times the Legendre symbol of a + b + c modulo 3.
     - It is the multiplication of the Eisenstein numbers.
     - It is a standing wave of two opposite sixth-root phases, sin(πE/3) with E = Σ(−1)^x.
   - **Every level (proved).** On every level-k Sierpinski gasket it reproduces itself exactly, with a factor ≡ ±1 (mod 3) that never
     vanishes.
     - Each copy splits into its two phases. The gasket's two edges from the first corner lock the phases at the three corners
       together, and flipping every phase is odd. So the phases always recombine into the same wave.
     - Modulo 3 the gasket collapses to the law, because the only surviving edge sets are the empty set and the two edges.
   - **So a knot reproduces itself on drawn substrates of every dimension below 2.** The towers of these gaskets are exactly
     self-similar, of dimension
     log(k(k+1)/2)/log k → 2, and their corner relation is the knot (K1–K3).
     - The plane stays out of reach. It is these gaskets plus the triangles joining them, and the joining triangles break exactness
       (the previous entries).
   - **What else reproduces itself (census to level 12).** 68 of the 1,168 signed laws do. Only two mechanisms persist across
     infinitely many levels:
     - the standing wave, with its rotations, relabelings and a twisted variant of period 4 in k;
     - linear parity, at powers of 2.
     The other 42 are single-level coincidences.
   - **Reading.** Harmonies in a precise form. The knot is the point of a family of standing waves where the all-equal states
     cancel exactly, and the substrate it reproduces itself on is one on which its two phases never mix.
   - **Next (taken).** The standing wave in every dimension (next entry).

   **2026-10-29: a knot reproduced on simplices of every dimension** (`SIMPLEX-GASKETS-20261029-001`).
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
     - These knots reproduce themselves on towers whose dimension log C(k+d−1, d)/log k rises towards d.
   - **The second wave.** The cosine wave (−1)^(x₀) cos(θE) keeps its form only when the number of simplices is odd; otherwise it
     turns into the sine wave. Under refinement the sine wave is the attractor. The period-4 family of the plane was the cosine wave.
   - **What persists (censuses in three and four dimensions).** The knots exact at every level computed are exactly standing waves.
     - Everything else follows an arithmetic of k: odd levels, powers of 2, or an odd number of simplices.
     - The rest are single-level coincidences.
     - The wave fails at θ = π/4 at exactly the even levels, where the edges between the other corners frustrate its phases.
   - **Reading.**
     - The gluing is the Sierpinski substitution, chosen rather than derived. What the law supplies is a fixed point of that
       substitution at every scale and in every dimension.
     - These substrates are finitely ramified and the laws signed, so the three-manifold result (bits see only parity) stands.
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
     - On planar substrates that are not finitely ramified, laws stay parity, even with signs.
     - On finitely ramified substrates, standing-wave knots reproduce themselves in every dimension.
     - On three-manifolds, parity plus one phase bit.
     - Coupling through shared faces keeps relations affine, and interference then reads global phases rather than building structure.
       The owner's "incommensurables cancelling" appears literally: classes with a³ = 1 cancel those with a³ = 0, and the cancellation is
       the information.
   - **Next (taken).** Uniqueness of the standing wave (next entry).

   **2026-10-29: is the harmony forced?** (`WAVE-UNIQUENESS-20261029-001`).
   - **Among knots, yes.**
     - On the planar gaskets, a three-place law that reproduces itself at levels 2 to 5 is a standing wave, or a law that couples
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
     - Reproducing itself at every scale while coupling three places requires interference: a cancelling pair of phases.
     - Everything else that reproduces itself at every scale couples at most two places at a time.
   - **Next (taken).** Which gluings carry the harmony (next entry).

   **Words in the three-regular entries.** From here up to the circle entries, apart from the two axis entries (the axis built from
   logic, and growth at loose ends), the entries glue copies of the not-all-equal knot by identifying distinctions of different
   copies, three copies at each shared distinction: copies overlap only at shared distinctions, and nothing is glued along sides. Such
   a gluing that allows no state is a three-regular contradiction (glossary of the Intuitions guide). The entries study it through
   the literature's graphs: its incidence graph, drawn on closed surfaces, and the glue's cubic graphs, such as cubes, prisms,
   ladders, rings and grids. Faces, corners, arcs, handles, genus, surfaces, maps, edges, vertices, squares and planarity belong to
   those graphs and their drawings; planar means, as in the literature, that a graph can be drawn in the plane without crossings, and
   the Fano plane is the literature's name for the Fano pattern. "The knot" is the not-all-equal law, a knot of a pattern is one copy
   of it, and a new or created knot is a knot of what is left after a removal, read on its allowed states. Before 2026-11-11 these
   entries called the copies triangles, the shared distinctions contacts, the knots lines, the distinctions points, the Fano pieces
   atoms or Fano atoms and the contradictions three-fold spaces, knot spaces or spaces; the earlier text is in git history.

   **2026-10-30: which gluings carry the harmony** (`SPACE-SELECTION-20261030-001`).
   - **The law selects by cancellation.**
     - A gluing of copies of the knot carries the wave exactly when six signed sums over phase assignments cancel.
     - Shared distinctions that lock phases make them cancel locally; mirror pairs of assignments and, from six copies, genuine
       identities make them cancel globally.
     - The conjectured local criterion (phase locking plus an odd parity) is refuted: the parity is always odd, and locking is not needed.
   - **It selects many gluings and no dimension.**
     - Up to five copies the knot reproduces itself on 8,584 gluings, 3,082 of them at its own angle only.
     - Exact gluings compose. Bubbles hung from a single distinction keep exactness, so the growth exponents of the towers are unbounded.
     - Other angles (π/4, π/6, π/8, and angles that are not rational multiples of π) have their own gluings, so the knot is not singled
       out by the gluings it admits.
   - **Interference is what makes small gluings.** Without signs a not-all-equal law needs at least seven copies (sharp). With signs it
     needs three, glued as the literature's Sierpinski triangle.
   - **The two/three boundary, inside the gluing.**
     - A distinction shared by two copies locks their phases, an equality.
     - At the knot angle, a distinction shared by three copies, an odd number of which hold it at their sign-carrying place (the
       law's x₀, earlier called the base corner), is itself a not-all-equal knot on their phases.
     - A gluing made only of such knots is the unsigned problem on its dual. The knot then needs seven copies, and the seven-copy
       gluings (corner copies distinct) are exactly the Fano pattern read as a gluing. On it both the signed and the plain knot reproduce
       themselves.
   - **Reading.**
     - The law does not draw a space by itself.
     - Where the gluing is made of the knot's own shared distinctions, the smallest gluing is forced: the Fano pattern, which reads the
       same with copies and shared distinctions exchanged. (Only the smallest. Larger such gluings exist; see the next entry.)
   - **Correction.** The epic's first proof stated the seven-copy bound with a wrong reduction and missed the one-copy case. A later
     ticket in the same epic corrected and sharpened it.
   - **Next (taken).** The knot's three-regular contradictions (next entry). Its premise, that the Fano pattern is the only one, turned out
     to be false.

   **2026-10-30: the knot's three-regular contradictions** (`THREEFOLD-SPACES-20261030-001`).
   - **The premise was wrong.** The Fano pattern is only the smallest three-regular contradiction. Splicing one Fano pattern into
     another gives a 13-knot contradiction, and Fano patterns splice together without limit (7, 13, 19, … knots). A random probe had
     missed these rare cases.
   - **What the knot asks of a three-regular gluing.**
     - At the knot angle, a gluing in which every shared distinction joins three copies of the knot is one of the knot's
       contradictions exactly when two conditions hold for its dual arrangement of triples: it cannot be 2-coloured as a whole, and it
       can once the corner knot is removed.
     - That is the classical even-cycle problem: its sign-nonsingular matrices are those of 2-in 2-out digraphs with no even cycle.
     - Its one indecomposable exception is the Fano plane (McCuaig).
   - **Up to 13 knots (exhaustive).** Only the Fano pattern and its splice.
   - **Beyond: odd cycles of Fano patterns.**
     - A Fano pattern minus a knot forces its three free distinctions to one colour, so a knot that meets it twice says "different".
     - A cycle of an odd number of such blocks cannot be 2-coloured. That gives contradictions with 21, 35, … knots.
     - One sign flip turns an even cycle odd: a 14-distinction twisted system found by SAT, and from two of them a 27-knot contradiction.
   - **Reading.**
     - The knot builds its own contradictions from the two classical obstructions to 2-colouring: the Fano plane (three places) and the
       odd cycle (two places).
     - That is the two/three boundary as a grammar, with a sign deciding the parity.
   - **Also.** Gluings of phase locks and phase knots alone do not exist, because counting sign-carrying places forbids every lock. So
     the planned "mixed" class is empty.
   - **Correction inside the epic.** A first reduction claimed that Fano compositions were everything. The 14-distinction twisted
     system showed the gap: cutting a contradiction into pieces can put a distinction twice in a knot. The reduction was corrected.
   - **Next (taken).** The grammar of three-regular contradictions (next entry). The approved form turned out to be false: odd cycles
     and splices are not the only glue.

   **2026-10-30: the grammar of three-regular contradictions** (`THREEFOLD-GRAMMAR-20261030-001`).
   - **The approved grammar was too small.** Fano blocks, splices and odd cycles do not make every contradiction. Twisted
     14-distinction pieces set on three skew edges of a cube give a 43-knot contradiction whose glue is the cube itself.
   - **Fano pieces and glue (proved).**
     - Cut a three-regular contradiction along its tight three-edge cuts. Every end piece is a Fano pattern with one element removed,
       so every contradiction other than the Fano pattern holds at least two Fano pieces.
     - Everything between the Fano pieces is glue: doubled squares, planar pieces, and pieces glued from planar ones along 4-cycles
       (Robertson–Seymour–Thomas). Non-planar glue does occur, first seen in a 35-knot contradiction.
     - Every planar cubic graph serves as glue. Each of its faces needs a fixed parity of sign flips (Kasteleyn's condition). Twisted pieces
       at the attachments supply them, like a flux through each face.
   - **Sizes up to 22 knots (exhaustive through cores).**
     - Contradictions have exactly 7, 13, 19, 21 or 22 knots: eight in all, each a small core dressed with Fano pieces, six knots at a time.
     - None has 8–12, 14–18 or 20 knots.
   - **Duality is free.** Exchanging knots and shared distinctions maps the knot's contradictions to its contradictions.
   - **Reading.**
     - The knot's own contradictions are planar glue studded with three-place Fano pieces. The glue's planarity is forced by the law's sign
       parity, not drawn.
     - The two/three boundary again: the Fano pieces are the three-place obstruction, and the glue is a two-place parity structure.
   - **Corrections inside the epic.** Two checks predicted wrongly and were fixed by computation:
     - A Fano block can sit on a twisted distinction; that is exactly the 14-distinction twisted piece.
     - The glue can be non-planar, when it is assembled from planar pieces.
   - **Next (taken).** The surfaces that carry three-regular contradictions (next entry). The answer was yes.

   **2026-10-30: the surfaces that carry three-regular contradictions** (`THREEFOLD-SURFACES-20261030-001`).
   - **Each Fano piece is a handle (proved).** Take the incidence graph of a three-regular contradiction's knots and distinctions and
     ask for the least genus of a closed orientable surface that carries it. When the glue is planar, that genus is exactly the number
     of Fano pieces. The glue adds no handles.
   - **Why the Fano pieces keep their handles.**
     - In general, splicing two non-planar pieces along three edges can lose a handle (two K₃,₃ give genus 1, not 2).
     - A Fano piece cannot lose its handle: with one vertex deleted it is still not planar. A piece with that property always adds its
       full genus.
     - The proof follows the faces across the three cut edges. A face that turns back across a cut edge costs a handle.
   - **The surface is canonical.**
     - Its genus is fixed by the contradiction, not chosen.
     - Every minimal map of it is a connected sum of one map, the Heawood map of the Fano plane, with planar maps of the glue. One copy
       comes per Fano piece, each with a handedness.
     - Contradictions have finitely many minimal maps up to symmetry: 1, 2, then 3 to 6 at 19 knots.
   - **The Fano pattern's drawing is the seven-vertex torus.**
     - Its minimal map is unique up to symmetry and chiral.
     - Read dually, it is the seven-vertex triangulation of the torus. Its 14 triangles are the seven knots and the seven shared
       distinctions (the corner counted as one of them), coloured like a checkerboard.
   - **Confirmed by exact computation** up to 180 vertices: the twisted cube has genus 6, the truncated-octahedron glue 12. A non-planar
     glue piece (three cubes glued along a square) adds one handle of its own.
   - **Reading.**
     - This is the first time in the program that one of the knot's own contradictions fixes a canonical topological object: a
       closed surface whose handles are its three-place Fano pieces.
     - It is the topology of an incidence graph, not a native contact topology or a metric.
     - The two/three boundary, once more: the three-place Fano piece becomes a handle, and the two-place glue stays planar.
   - **Next (taken).** The knot's amplitude on its surface (next entry). The answer was yes, and the glue's factor is Tutte's tree count.

   **2026-10-30: the knot's amplitude on its contradictions** (`THREEFOLD-AMPLITUDE-20261030-001`).
   - **Five per handle, a tree count per planar piece (proved).** The factor by which a gadget of the knot reproduces the knot is, up
     to sign, a product over the pieces of its contradiction:
     - 5 for each Fano piece, that is, for each handle of its surface;
     - 1 for each doubled square;
     - for each planar piece of glue, Tutte's tree-trinity number: the spanning trees of the map it is cut from (for glue cut from a map),
       Kálmán's hypertrees in general;
     - the sign is the parity of the number of knots.
   - **Why.** The factor counts the 2-colourings of the contradiction with one shared distinction opened.
     - Across each tight three-edge cut the count splits exactly.
     - On a planar piece, the knot's sign parities (Kasteleyn's condition) turn colourings into Tutte's matchings of faces to shared
       distinctions.
   - **One number for the whole contradiction (proved).** The count is the same whichever shared distinction is opened, and the same
     again when knots and shared distinctions are exchanged. This holds for every three-place system that cannot be 2-coloured, not only
     for the knot's contradictions.
     - The proof counts one weighted sum in two orders. With an Ising weight at half the knot's angle on the incidence graph of knots
       and shared distinctions, summing out either side gives the not-all-equal rule on the other.
     - So each shared distinction's count is the average of its knots' counts and vice versa, and a connected contradiction forces one
       value.
   - **Confirmed by exact computation.**
     - All 2,652 cores up to 10 distinctions.
     - The law at every corner of every contradiction up to 22 knots.
     - Glue cut from 13 maps up to the dodecahedron: 5,184,000 spanning trees, at all 60 shared distinctions.
   - **Non-planar glue depends on its gluing.** Three prisms glued along a square have one amplitude, but it changes with how the square is
     matched (13 or 14 for prisms of sizes 2, 3, 3). The pieces' own amplitudes do not determine it.
   - **Reading.**
     - The knot's own number measures what it builds: handles count 5 each, and planar glue counts trees.
     - The number belongs to the whole contradiction. No shared distinction is privileged, and reading from knots or from shared
       distinctions agrees. That is the relational lesson.
     - The two-way count is a three-place phenomenon: with four places, summing out cannot give not-all-equal.
   - **Next (taken).** The knot's spin structure (next entry). The answer was yes, and the spin structure is even on every handle.

   **2026-10-30: the knot's spin structure** (`THREEFOLD-SPIN-20261030-001`).
   - **The knot's signs are Kasteleyn (proved for planar glue).** On every least-genus surface of a three-regular contradiction, every
     face has length 2 mod 4. So the knot's own signs satisfy Kasteleyn's condition, the extra structure a surface needs before its
     perfect matchings define spin structures.
     - The proof follows faces across each tight three-edge cut. Exactly three faces cross, each made of one face from each side, so the
       parities add.
     - Non-planar glue (three prisms glued along a square) behaves the same on all its surfaces (computed).
   - **The spin structures are even, handle by handle (proved).** Each perfect matching gives a spin structure, and all have Arf
     invariant 0.
     - On the Fano torus the 24 matchings induce exactly the three even spin structures, eight each, never the odd one.
     - A contradiction with h Fano pieces gets exactly 3^h of them: the spin structures even on every handle (9 of the 10 even ones at
       genus 2).
     - Of the four sign classes on the Fano torus, only the knot's counts its 24 matchings exactly. The other three give 8.
   - **Evenness belongs to the least-genus surface.** On larger surfaces carrying the same signs, odd spin structures appear: about 1–2% of
     them, and only from genus 3 on.
   - **Reading.**
     - The law equips the contradiction it builds. Its own signs are exactly a spin structure's raw material on its own surface, and
       what they give is even on every handle.
     - An even spin surface bounds a spin 3-manifold, so each of the knot's surfaces, with its spin structure, is such a boundary.
     - The two/three boundary, once more: the three-place Fano piece carries a handle and its even spin structures; the two-place glue
       carries neither.
   - **Next (taken).** The knot's amplitude as a spin sum (next entry). The answer was no.

   **2026-10-30: the knot's amplitude as a spin sum** (`THREEFOLD-SPINSUM-20261030-001`).
   - **No: every spin structure contributes (proved, with exact values).** The knot's counts split exactly over the spin structures of its
     surface.
     - On the Fano torus, with one shared distinction opened, the three even spin structures give 16 each and the odd one 28. Twice the
       amplitude is (3 · 16 − 28)/2 = 10.
     - The even ones alone would give 12, not 5, and the odd one does not cancel.
     - With two handles the spin pieces do not split handle by handle, though the amplitude is exactly 5 · 5. "Five per handle" belongs to
       the whole count, not to spin pieces.
   - **The contradiction is a balance.**
     - In the closed Fano pattern the odd spin structure's piece, 24, exactly cancels the three even ones, 8 each. That cancellation is the
       knot's non-colourability.
     - Opening a shared distinction unbalances it by twice the amplitude.
   - **The knot's signs are the only contradictory ones.** Of all the sign patterns Kasteleyn's condition allows on its surface, the knot's
     is the only one that cannot be 2-coloured. Every twist of it can.
   - **Reading.**
     - The amplitude and the contradiction are properties of the whole relation, not of local pieces.
     - The spin question is closed. What the work on three-regular contradictions found in the end is linear-algebraic: the knot's
       contradictions sit exactly on Seymour's bound (as many shared distinctions as knots), where impossibility is a determinant
       condition.
   - **Next (taken).** Where counting near-critical instances becomes hard (next entry). The easy side holds.

   **2026-10-30: counting on Seymour's bound** (`SEYMOUR-COUNT-20261030-001`).
   - **Counting is easy on every contradiction the knot builds (proved, and implemented).** The colourings of a three-regular
     contradiction with one shared distinction removed are counted exactly in polynomial time, with no signs.
     - Planar glue is one determinant (Berman's, counting Tutte's matchings).
     - Non-planar glue is built by gluing three pieces along a square (Robertson–Seymour–Thomas). It is cut back into planar pieces,
       and each piece is one weighted determinant: two determinants per piece.
     - Contradictions of 1720 vertices are counted in seconds, where generic elimination would need tables over 30 variables.
   - **The knot reappears one level up (proved).** Each piece's colourings lean to one of the square's two corners, in proportions (α, β).
     - The glued amplitude is ρ₁ρ₂ρ₃ − α₁α₂α₃ − β₁β₂β₃: the knot's not-all-equal rule, applied to the pieces' leanings.
     - Pieces glued further down act only as weights on these two numbers. A piece tells the rest of the contradiction nothing else.
   - **Reading.**
     - The knot's contradictions are where counting stays easy. Their impossibility is a determinant condition, and so is their count
       with one shared distinction removed.
     - The surface never has to be seen. The Kasteleyn route on the surface would need 4^genus Pfaffians; the pieces need none.
     - Provenance: planar counting of this kind is classical (Valiant), and the gluing structure is Robertson–Seymour–Thomas's. The counting
       result on every contradiction was found in no source.
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
     - Proved: a not-all-equal knot forbids only one pattern, so the square's knots can never force two of the host's distinctions into
       a fixed relation without pinning them. No junction is a sharp crossing; the square's distinctions can carry a wire, its knots
       cannot.
     - Computed exactly: twisted truncated-octahedron pieces do let both wires through at once, with a small weight (−192 against 40000),
       outside the planar class. The signs cancel the turning paths exactly and let the crossing path through.
   - **Reading.**
     - Easy counting is a property of the knot's sign class at each junction, not of the graph alone.
     - Interference again does the work: signs cancel what the not-all-equal rule cannot forbid.
     - If the soft crossing can be sharpened, counting becomes hard exactly where twists branch.
   - **Next (taken).** Soft crossings to hardness (next entry). Counting is #P-hard where twists branch.

   **2026-10-31: soft crossings to hardness** (`SOFT-CROSS-20261031-001`).
   - **The soft crossing sharpens (proved).** Repeat the junction of two twisted pieces k times, with plumbing whose spare legs are
     closed by a *dead cap* (a cube minus one edge, whose count is 3 whatever it touches).
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
     - The knot's own graphs show both sides of the boundary. The knot's own signs count by determinants. Twists that run along a path stay
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
   - **Squares are twists (proved).** A cubic planar incidence graph must have at least six square faces (Euler), and at most five can
     touch a given one. On a square the knot's signs need an odd number of negations, and plain signs have none.
     - So every plain planar piece is twisted, and in a plain non-planar brace the twists branch at every square.
   - **The Fano pattern is the exception (proved; likely known).** The Fano pattern's incidence graph has no squares at all; its shortest
     cycles are hexagons, which plain signs allow. It is the only plain brace without twists, and the only plain brace that cannot be
     2-coloured.
   - **Reading.**
     - Without signs, twisting is the default, and the Fano pattern is the one case where it is absent.
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
   - **Plain Pfaffian braces are hard to count (proved).** Draw a hard instance in a planar frame, one vertex per face, and replace every
     crossing by such a ladder. Every instance is then a brace (cyclically 4-edge-connected) and Pfaffian, with no signs at all.
   - **Reading.**
     - Neither connectivity nor Pfaffian-ness protects counting.
     - The plain picture is complete in the worst case: planar pieces are easy, two plain pieces at a square are twisted and soft, and a
       ladder of such squares crosses wires exactly. The Fano pattern is the one plain brace without twists, and with
       planarity the polynomial case found.
     - Provenance: the source hardness is Fan and Cai's, planar tractability Valiant's, and the brace structure Robertson, Seymour and
       Thomas's. The plain crossing inside braces and the weaving lemma (drawing an instance in a planar frame) and the cube junction
       lemma were found in no source.
   - **Next (taken).** A note on the counting arc (next entry).

   **2026-10-31: the counting note** (`COUNT-NOTE-20261031-001`).
   - **The arc is written up.** One self-contained 10-page note states the five results in standard vocabulary:
     - counting is polynomial on every contradiction the knot builds;
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
     - Colouring counts are a three-body Ising model, and the knot's law, not-all-equal, is one coupling in its family.
     - On single pages, the knot's signs keep the count planar (free-fermion) at every coupling.
     - Once two pieces meet at a square inside a larger tree, they keep it planar only at the knot's own coupling and at the trivially easy
       ones. The factors shared by every tested case are exactly those couplings (5 of 6 cases, with one exception).
     - This is not an artifact of the chosen basis.
   - **Does a descent toward fewer colourings find the knot's signs? Only on Fano contradictions (computed).** Every contradiction with
     4-cycles has traps. The descent is imposed, so this is weak.
   - **Is one knot short of Seymour's bound a new regime? No (proved).** It is #P-hard even on connected, sparse systems. Only the knot's
     part is easy.
   - **Reading.**
     - On the knot's contradictions, the signs and the law fit each other, and only each other.
     - This is a selection with nothing imposed but the coupling: the contradiction's signs choose the knot's law.
     - Provenance: planar Ising and matchgates are classical, and the source hardness is Fan and Cai's. A singled-out coupling on Pfaffian
       contradictions was found in no source.
     - *Corrected on 2026-10-31 by the next entry.* The shared couplings also include a point at infinity, the dimer coupling. So the
       knot's law is one of two singled-out laws, not the only one.
   - **Next (taken).** A coupling dichotomy in the knot's class (next entry).

   **2026-10-31: the knot's coupling** (`KNOT-COUPLING-20261031-001`).
   - **Counting on the knot's contradictions is easy at exactly two laws besides the trivial ones (proved).**
     - Weigh each monochromatic knot by λ. On the systems that cannot be 2-coloured, counting is easy at λ = 0 (the knot's law), at
       λ = −3, and at the trivially easy couplings.
     - It is #P-hard at every other coupling, real or complex.
     - At the knot's law every count is 0. At λ = −3 every knot uses exactly two of its distinctions, so the count is the number of perfect
       matchings of the incidence graph: a determinant on the knot's contradictions, a permanent in general. Call this the dimer law.
   - **Why the knot's law is special (proved).**
     - Take a contradiction, remove one incidence, and use it to replace an edge. At the knot's law this gadget is exactly a negation, so it
       cannot change the coupling.
     - At every other coupling the gadget shifts the coupling, and shifted couplings can imitate any twist. That makes counting as hard
       as on general systems.
     - The complex couplings are closed by torsion points on a curve (Beukers and Smyth).
   - **With one knot deleted** the picture is the same, except that the dimer law is left open.
   - **Correction.** The scan's "only the knot's law" missed the dimer law, a point at infinity.
   - **Reading.**
     - The knot's contradictions select their own law natively, and with it one partner. Both come from one fact: the incidence matrix is
       sign-nonsingular.
     - Both easy laws are cancellations: a count that vanishes, and a determinant.
     - Provenance: the tools are classical (gadgets, interpolation, Seymour, Robertson–Seymour–Thomas, Kasteleyn, Beukers–Smyth). No
       dichotomy restricted to these contradictions was found.
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
     - The Fibonacci law prefers its vacuum. A five-knot piece of it pins a distinction; one more knot with that distinction copies a
       variable; copies give unlimited fan-out; and fan-out makes the law hard.
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
     - A pinned distinction turns one knot into an equality, so a variable can be copied without limit.
     - One small skeleton pins every knot that can pin: four distinctions with three knots among them, and two tails.
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
     - Changing basis turns each knot's weight into a simple equality, but it also turns each distinction's equality into a parity
       check. The count becomes a weight count over a code, not a sum over two states.
     - A peer session found the error, citing Fan and Cai (2020, Theorem 2.2).
   - **Parity's weighted family is hard except at six couplings (proved).**
     - Weigh each knot that misses its parity by λ. Counting is easy only at λ = 0, 1, −1, i, −i and ∞, and #P-hard at every other
       coupling, real or complex.
     - The reason is native. Replace each knot by three knots through two new distinctions. Parity's weighting on the new system is the
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
     - Failures select a law back only when they are global. The knot's failures constrain the whole system: a system fails exactly when
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
     - With any signs, not-all-equal on k places never fails on systems where every distinction is in k knots, for every k ≥ 4.
     - The reason is Thomassen's theorem on even cycles. A failure would need a sign-nonsingular pattern, and a digraph whose vertices all
       have in- and out-degree at least three always has an even cycle.
     - At three places the degree is two, such digraphs can avoid even cycles, and the failures are exactly the knot's Pfaffian
       contradictions.
   - **The other value-free four-place laws build equality (proved).**
     - Small pieces of five distinctions force two distinctions equal without any constant.
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
     - composition of the knot's selected contradictions toward native networks.

   **2026-11-01: four-place laws that prefer a value** (`FOUR-PREFER-20261101-001`).
   - **There are twenty kinds of four-place knot (proved).**
     - A four-place relation is a knot exactly when the states it forbids never differ in just one place, i.e. they form an independent
       set of the flip graph of four bits (the literature's 4-cube).
     - That gives 742 relations in twenty kinds, sixteen of which prefer a value.
   - **Every kind that can fail can copy (proved).**
     - A core of three distinctions in four knots turns nine different kinds into the value-free twelve-state kind, and that kind builds
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
     - Provenance: Schaefer, Tovey, Seymour, Thomassen. The twenty-kind census and the three-distinction lift were found in no source
       checked.
   - **Next (taken).** Composition of the knot's contradictions, then the note.

   **2026-11-01: composition of the knot's contradictions** (`KNOT-COMPOSE-20261101-001`).
   - **The parts of a contradiction meet as a knot against a hub (proved).**
     - Cut a contradiction along three incidences. One side always ends in three distinctions and the other in three open knot slots.
     - The knot side behaves exactly as the knot itself (not-all-equal) on its three slots, and the distinction side exactly as one
       distinction (an equality hub). The two fit together as a knot that contains a distinction.
       - *Corrected on 2026-11-01 (`NATIVE-PATHS-20261101-001`, two entries below).* "Exactly" holds only up to signs. In
         contradictions with cycles of Fano blocks, the distinction side forces its three distinctions into one fixed pattern or its
         complement, for example two equal and one opposite. That is an equality hub once one colour is read exchanged, and the knot
         side is the knot read the same way.
   - **Knot meeting knot fails only for parity (proved).**
     - A side that behaves as a knot allows at least half of all patterns.
     - Two such sides can exclude each other only if each is exactly half of all patterns, and an exact half with full projections is
       a parity coset.
     - So every failing composition of the knot's contradictions passes through a hub, and the only hub-free failing composition is
       parity's.
       - *Corrected on 2026-11-01 (`NATIVE-PATHS-20261101-001`).* Not every one. A contradiction with a cycle of Fano blocks can be cut
         along two incidences, and then one side is an equality and the other a negation, with no hub. That two-place parity is exactly
         the hub-free failure predicted here. Across three or more channels, knot never meets knot.
   - **Knot and hub are two sides of one structure.** Swapping distinctions and knots turns a contradiction into a contradiction and
     exchanges the knot side and the hub side of every cut.
   - **Reading.**
     - Knots relate through shared distinctions. A direct knot-to-knot relation, with nothing between, exists only for parity, the law that
       hides one full bit. This matches every earlier result in which only parity survived hub-free composition.
     - Against the native-network gate, the knot's contradictions form a native network of knots joined by network hubs, which the
       owner put in scope on 2026-10-29. They do not form a hub-free contact network.
     - Provenance: the splice calculus and the point lemma are our earlier epics, on Lovász–Plummer and Robertson–Seymour–Thomas. The
       hub reading was found in no source checked.
   - **Next (taken).** The note on native selection. Later: native paths through network hubs (2/3).

   **2026-11-01: a note on native selection** (`SELECTION-NOTE-20261101-001`).
   - **The arc in one note.** A five-page note gathers the results of this question since the coupling dichotomy:
     - the knot's contradictions select its law;
     - the knot is the only three-place law whose failures can be recognised while its count is hard;
     - parity's failures are recognisable but local (with the corrected analysis recorded);
     - three places stay special at four;
     - the knot's contradictions compose only through hubs.
       - *Corrected on 2026-11-01 (`NATIVE-PATHS-20261101-001`).* Across two-incidence cuts they compose by two-place parity, without
         a hub. The note needs an erratum before it is shared.
   - **Checked again.** Every one of the sixteen proofs it cites was rerun from scratch and reproduced its result exactly. Nine headline
     claims were recomputed by separately written code.
   - **Status.** Not externally reviewed and not sent. Sharing it is the owner's decision.
   - **Next (taken).** Native paths and separation through network hubs, the step from first emergence toward composed topology (2/3).
     A side question: whether five weak four-place laws can ever fail (1/3).

   **2026-11-01: native paths in the knot's contradictions** (`NATIVE-PATHS-20261101-001`).
   - **Two kinds of meeting (proved).**
     - **Two incidences.** Cut a contradiction along two incidences where that separates it, as in every odd cycle of Fano blocks and in
       the twisted cube. One side behaves as a wire (equality), the other as a negation: two-place parity, with no hub.
     - **Three incidences.** One side forces its three distinctions into one pattern or its complement, and the other side allows the
       six other patterns: a knot against a hub, up to signs.
     - **A correction.** This corrects the composition entry: the knot's contradictions do not compose only through hubs.
   - **The routes are fixed by the contradiction (proved; laminarity computed on ten contradictions).**
     - Every three-incidence cut is either a genuine splice or a two-incidence cut with one distinction or knot moved across.
     - Genuine splices never cross. So the parts, and the routes between them, are determined by the contradiction itself; no observer
       chooses them.
   - **A route carries one bit at most (proved).**
     - **Through a chain of Fano blocks.** A route remembers only whether its length is even or odd. Two blocks of an odd cycle are
       joined by two routes of opposite parity, and that disagreement is exactly why no state is allowed.
     - **Through a hub.** A route remembers nothing of what lies beyond: the far side acts as one distinction or one knot, whatever it
       contains.
     - **Separation.** Cutting both routes separates two blocks. Cutting one leaves the other route's parity.
     - **Length.** Counting the hidden witnesses gives 5 per block and 5^m for a chain of m blocks. So length appears only as a count,
       not as a relation.
   - **Knot meets knot only pairwise (proved).**
     - Twist some incidences, so that each reads its distinction's colour exchanged. A contradiction stays contradictory exactly when
       the twisted set is a cut of its incidence graph.
     - So two parts can both behave as knots toward each other only across two incidences, as two-place parity, and never across three or
       more.
   - **Reading.**
     - **Fixed, but not native paths.** Routes between the parts of a contradiction are fixed by the contradiction. Each is two-place
       parity or passes a hub, and neither is a contact. In these contradictions the ladder from first emergence stops at hubs.
     - **The 2-versus-3 boundary, seen from composition.** Three-place emergence stays inside the parts. Everything joining the parts is
       pairwise or a hub.
     - **Hubs are where the knot selects.** A system in which every distinction lies in at most two knots never fails (Seymour's bound).
     - **Provenance.** Pfaffian signings, their uniqueness up to switching, and the cactus of two-edge cuts are classical. The
       two-interface theorem with signs, and knot meeting knot only pairwise, were found in no source checked.
   - **Pending the owner.**
     - The note needs an erratum before it is shared.
     - The composition record should be marked superseded, text kept, as was done once before at the owner's request.
   - **Next (taken, together with counted length).** A full pivot to selection versus composition: does any law both select its
     contradictions and compose natively?
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
     - On a contradiction, count the ways each side of a cut can be arranged, given what its channels show.
     - The count is the same for every allowed pattern, and the two sides' counts multiply to the whole.
     - So the logarithm of the count, counted length, adds up over the parts: log 5 for every Fano block (one handle), plus the
       logarithm of the glue's spanning-tree number (log 2 in the twisted cube).
   - **Counting sees what relations hide (proved).**
     - **Along a chain of m blocks.** The relation remembers only whether m is even, but the count is 5^m.
     - **Across a hub.** The relation sees one distinction, but the count sees everything behind it.
     - **In cycles of blocks from different contradictions.** The relation (whether the number of blocks is odd) and the count (the
       product of what each block hides) vary independently.
   - **Reading.**
     - **Two layers.** Relations carry emergence and decide failure, with one bit per route. Counts carry magnitude: how much each part
       hides.
     - **Canonical weights.** Counted length is fixed by the law and the contradiction, and unchanged when distinctions and knots swap.
       It supplies the canonical weights that earlier route values had to choose.
     - **Not a native distance.** The routes it measures are not native paths, so it is a measure, not a native distance. Admitting it
       as a native magnitude would be a change of doctrine.
     - **Provenance.** Our circuit-composition theorem, mutual selection and amplitude results; Post, Schaefer and Valiant. The
       forcing-place hubs, the exclusion statement, factorization across two-incidence cuts, and the cycles of blocks were found in no
       source checked.
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
   - **Where laws fail, and whether globally (proved; all 60 cubic substrates up to 8 distinctions).**
     - **The knot** fails exactly on Pfaffian substrates (8 of 60), and every failure is global.
     - **Parity** fails exactly where the number of perfect matchings is even (38), and never globally, because each distinction sits
       in three knots and three is odd.
     - **Z3** fails everywhere, and globally exactly at Z3-corank 1 (24), because three is zero mod 3.
   - **A bridge at four values, but rigid (proved).**
     - On its corank-1 substrates, blurred Z3 selects in the knot's full sense: its failures are global and recognisable, it is easy to
       count once a knot is removed, and hard in general. It also composes like cycles.
     - But removing a knot leaves one degree of freedom and only ties: its selected contradictions are pairwise.
     - The knot's selected contradictions can keep a knot after a knot is removed: every knot of the Fano pattern, and four other Pfaffian
       substrates.
   - **Reading.**
     - **Three kinds of cancellation.** Parity cannot fail globally on three-regular systems. Z3 fails globally when the whole system
       cancels. The knot fails globally when nothing cancels: all its perfect matchings agree in sign.
     - **What sets the knot apart.** Counting can be made hard without touching relations. The knot's real distinction is relational:
       it selects contradictions that keep emergence inside, which the linear bridge cannot.
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
     - **Fields.** Over a field, a system that fails globally has exactly one dependency among its knots. Removing any knot leaves
       solutions with a single free parameter, so only ties remain, at every number of places.
     - **Blurring.** It keeps this rigidity.
     - **S3 and D_p.** Their knots on full ranges are blurred parity.
     - **Simple three-value laws.** Those that are not affine have no knots on full ranges.
   - **Rigidity fails beyond fields (proved).**
     - **Signed Z4, four places.** It fails globally on a 6-distinction substrate (each knot omits the two ends of one hexagon edge) and
       keeps knots after any knot is removed.
     - **Signed Z4, three places.** It needs 9 distinctions: all 73 cubic substrates up to 8 distinctions, under every signing, leave
       only ties.
     - **Unit-weighted laws.** Z8, Z9, Z25 and Z27 do the same on many small substrates.
   - **Selection spends the top layer (proved).**
     - **The theorem.** Over Z_(p^k), and over any finite chain ring, a system that fails globally leaves, after any removal, solutions
       whose top digits have a single free parameter. That is exactly what a field would leave.
     - **Hence fields are rigid.** Over a field the top digit is everything.
     - **What survives otherwise.** A kept knot has at most one variable taking all values, and hides at most k − 1 of its k digits.
     - **Attained.** The bound is reached over Z4, Z8, Z16, Z9, Z27 and Z25.
   - **A law that composes, selects and keeps emergence (proved).**
     - **The law.** Blurred signed Z4 on five values (0 doubled).
     - **What it does.** It composes like cycles, fails globally and recognisably, counts #P-complete, and keeps knots inside its
       selected contradictions, below its top layer.
   - **Two values (proved).** A two-valued law with knots that composes like cycles is affine, hence rigid. The knot keeps knots
     inside its selected contradictions. So at two values the two exclude each other.
   - **Reading.**
     - **A failure in a carry.** Z4's global failure is solvable mod 2 and fails only mod 4: a cancellation that closes only once
       the carries are counted.
     - **What it spends and keeps.** It spends the top digit, and its kept knots relate lower digits to the single free parameter of
       the top digits. For example, the 2's digits of two variables and the units digit of a third have even parity.
     - **The knot has one layer.** Its failures need no cancellation, and it keeps three-place emergence in its only layer. Of all the
       laws met so far, it alone keeps top-layer emergence inside the contradictions it selects.
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
     - **Declared domains.** Give each distinction one domain, which every knot containing it uses.
     - **The theorem.** After any removal, the leading digits of the variables, each read in its own section, have at most one free
       parameter.
     - **Consequence.** Every kept knot has at most one varying leading digit. This answers last entry's objection: with declared
       domains, each distinction's own section is the right layer.
     - **Two different rings** joined through tops: checked, not proved.
   - **Correction.** The group theorem holds for systems with declared domains. Knots that confine a distinction further are open, though
     every such case met was rigid.
   - **Reading.**
     - **Laws that compose like cycles.** Such a law keeps emergence inside a selected contradiction only through depth: an abelian section
       with two layers, where a digit carries into the next, so at least four values. Even then, only below that section's top.
     - **The knot.** It keeps three-place emergence on two values, in its only layer, with no carry. This is the sense in which the
       knot stands apart.
     - **Selection leaves a hub.** When the knot's contradiction loses a knot, the rest forces that knot all-equal, so its three
       distinctions are tied. In the Fano pattern the four distinctions off it become a new four-place knot.
     - **Provenance.** Commutator theory, Z-groups and Smith forms are classical. The depth theorem, the group list read through our
       circuit theorem, the counterexample and the layer-wise statement were found in no source checked.
   - **Next (taken).** What selection leaves, and how pieces glue (2/3).
     - **The lead.** The knot's contradictions are Fano pieces glued at knots, and a removed knot is exactly a hub of tied distinctions.
     - **The question.** Does gluing selected contradictions at these leftover hubs build the knot's contradictions natively, keeping
       emergence across the glue?

   **2026-11-02: what selection leaves, and how pieces glue** (`HUB-GLUE-20261102-001`).
   - **Selection leaves the gluing interface (proved).**
     - **The hub.** Removing a knot from a contradiction ties its three distinctions. That is exactly the distinction side of the 3-edge
       cuts at which contradictions are glued.
     - **The gluing.** Splicing two contradictions at a knot and a distinction gives a contradiction, for one switching class of signs,
       and every simple cut is such a splice.
     - **With the earlier grammar.** Every contradiction is built this way from Fano pieces and planar glue.
   - **A held hub composes like cycles (proved).**
     - **When it holds.** If the removed knot is not on a cut's hub side, the hub keeps its three distinctions tied: one bit.
     - **The composition.** The knots crossing the cut are then exactly the eliminations (K1 ∪ K2) minus the hub of one knot through
       the hub on each side, ties included: a 2-sum.
     - **The reason** is the knot's symmetry under flipping every value. An OR, which lacks it, fails.
   - **An opened hub creates (proved, with computation).**
     - **When it opens.** If the removed knot lies on the hub's own side, the interface becomes whatever the closed piece allows. It is
       one pair (the hub re-ties and still composes), two pairs (one hub distinction released) or all three (the hub becomes a knot on
       its own three distinctions).
     - **Composition fails.** Then composition breaks down. In the 13-distinction Fano splice, 72 crossing knots arise that no chain of
       eliminations produces, against none through held hubs.
   - **Reading.**
     - **Where the exclusion is lifted.** Selection and cycle-like composition exclude each other as properties of a whole law, but
       inside the knot's own contradictions they meet exactly at the hubs selection leaves.
     - **One removal decides.** The removal that selects a contradiction also decides, cut by cut, whether the glue composes (held) or
       creates (opened).
     - **Still hubs.** The hubs are equality fan-out, so this composes emergence, not contacts: no native path or distance is claimed.
     - **Provenance.** Tight cuts of Pfaffian graphs, sign-nonsingularity and the matroid 2-sum are classical. The relational 2-sum
       through a complement-symmetric hub and the classification of opened hubs were found in no source checked.
   - **Next (taken).** Emergence along the splice tree (2/3).
     - **The question.** In a contradiction of several pieces, are the knots kept after any removal iterated 2-sums along the held
       cuts, with new emergence only at the cuts opened on the way to the removed knot?

   **2026-11-02: emergence along the tree of cuts** (`SPLICE-TREE-20261102-001`).
   - **A removal orients the tree (proved).**
     - **Held and opened.** In a contradiction glued from several pieces, removing a knot holds every cut that points toward it and
       opens every cut that points away.
     - **Locality.** Beyond a held cut nothing depends on which knot was removed.
   - **Held cuts compose exactly (proved).**
     - **The theorem.** The knots crossing only held cuts are exactly the iterated 2-sums, through held hubs, of knots crossing no cut.
     - **So** new emergence lives only across opened cuts.
   - **Opened cuts form one zone (computation, 96 chains of three and four pieces).**
     - **Carried and joint.** New knots of one opened cut are carried across the others, and two or three opened cuts create knots
       jointly.
     - **Hubs decide nothing.** Each of three hub-level rules fails to say where knots are created:
       - touching hubs;
       - a hub distinction in the removed knot;
       - the removed knot's own hub.
     - **Regularities.** Every jointly created knot has three or four distinctions, and chains of the smallest contradiction (K4^(3)) create
       nothing.
   - **Reading.**
     - **Composing and creating.** After a removal, the knot's kept emergence has two sides: a tree of exact compositions on the held
       side, and one zone of creation on the opened side.
     - **A lead toward topology (scouting, not a claim).**
       - **The scout.** Single splices of the census contradictions. New knots appeared only when the opened hub had become a knot and the
         removed knot's side was non-planar: 100 of 160 such removals, against none of the 560 with a planar side.
       - **What it suggests.** Each Fano piece is a handle, so creation may live in the handles while planar glue only composes.
     - **Still hubs.** Hubs are equality fan-out, so no native path or distance is claimed.
     - **Provenance.** Iterated 2-sums along a tree decomposition are standard for matroids. The relational version, the orientation
       reading and the classification of opened-cut interaction are new here; no literature search was run for them.
   - **Next (taken).** Emergence needs a handle (3/3).
     - **The question.** At an opened cut, does new emergence need both a knot on the hub and a non-planar removed side, so that planar
       glue only composes?

   **2026-11-02: emergence needs a handle** (`HANDLE-EMERGENCE-20261102-001`).
   - **Planar glue creates nothing, as far as tested.**
     - **Beyond the census.** 24 planar contradictions were spliced into other contradictions (grown from the cube, prisms, the truncated
       octahedron; 10 to 14 distinctions). No removal on the planar side created a new knot across the opened cut: 1612 removals and
       432,867 crossing knots.
     - **The census.** Planar sides create nothing there either. The Fano pattern and one other non-planar contradiction create.
   - **What a handle creates (computation, with two small lemmas).**
     - **A three-distinction knot through the hub.** Every created knot joins a distinction of the removed knot's hub, one near
       distinction and one far distinction.
     - **How it works.** The hub and the near distinction fix all three gluing ports at once, and the far distinction answers to that whole
       pattern. No single port carries the constraint across, so no elimination produces it.
     - **In the Fano pattern.** Every removed knot meets the gluing knot, so the hub sits on a port.
   - **On a planar contradiction the knot fails by counting faces (proved).**
     - **The odd distinction.** Each knot has one distinction that disagrees with the other two. Say the knot skips the corner opposite that
       distinction.
     - **The face condition.** With Kasteleyn's signs, every face must hold an odd number of skipped corners.
     - **The count.** A planar contradiction with n knots has n + 2 faces (Euler's formula). So the n skips can never cover them, and the
       knot fails.
     - **After a removal.** Every face holds exactly one skipped corner, so the solutions are exactly the perfect matchings of the
       remaining knots to the faces off the removed knot.
     - **Planar interfaces.** A knot meeting the removed knot loses a face to it. So the configuration that creates in the Fano pattern
       never forms on a planar side.
   - **A handle leaves slack (proved count, computed example).**
     - **The count.** Each handle removes two faces and adds two global (homology) parities.
     - **In the Fano pattern.** On its torus embeddings, 14 assignments per removal pass the face test, and the homology parities keep
       only 5 of them. That is where creation lives.
   - **Reading.** Selection on a planar contradiction is a matching of knots to faces, so its emergence only composes. A handle trades
     two faces for two global parities, and those parities let new knots appear. Hubs remain equality fan-out, so no native path or
     distance is claimed.
   - **Open.** A proof that a planar side never creates.
   - **Provenance.**
     - **Classical.** Kasteleyn's face condition, and Moret's theorem that planar not-all-equal 3-SAT is polynomial.
     - **New here, as stated.** The skip model and its genus count. A bounded search found no statement of them.
   - **Next (taken).** Planar glue only composes (2/3).
     - **The question.** Prove from the matching picture that a planar side never creates. Then test whether a handle creates exactly
       what its homology parities add.

   **2026-11-02: planar glue only composes** (`PLANAR-COMPOSE-20261102-001`).
   - **On a planar side the hub reaches the gluing ports (proved in part).**
     - **The tie class (proved).** After a removal, every distinction on the removed knot's faces is tied to its hub. In the matching
       picture, states differ by flipping the distinctions inside closed curves, and those curves never enter the removed knot's faces.
     - **The route (proved).** Suppose the hub and a near distinction fix the gluing pattern. If the hub is also tied to one of the
       pattern's two other ports, or knotted with both in the right way, then every candidate new knot is built from one-sided knots,
       one port at a time, whatever is glued on the far side.
     - **The access lemma (checked, not proved).** One of those two always holds on a planar side: all 9020 cases on 42 planar
       contradictions of up to 20 distinctions (8020 as first recorded; corrected by `PLANAR-THEOREM-20261102-001`). On the Fano
       pattern and census 58 it fails in every case: the Fano pattern's hub sits on the very port it pins as odd.
   - **Cutting a handle open is not canonical (computation).**
     - **Dropping one homology parity** removes about nine tenths of a handle's new knots.
     - **Dropping both** removes all of them for some cut positions and not for others, even within one homology class.
     - **Local distinction flips** remove none.
     - **So** homology carries most of a handle's creation, but "a handle creates exactly what its homology parities add" fails as stated.
   - **Reading.**
     - **A planar side.** Its removed knot always leaves a hub that can reach the ports one at a time. A handle breaks that: its hub lands
       on the port it must not use.
     - **Still hubs.** Hubs remain equality fan-out, so no native path or distance is claimed.
     - **Provenance.** The planar matching structure is classical (Kasteleyn). The tie-class, route and access statements and the
       handle-cut measurements are new here.
   - **Open.**
     - The access lemma in general.
     - That every new knot is a pinned three-distinction knot (true in all 2820 found).
     - Four-pattern removals.
   - **Next (taken).** Finish the planar theorem (2/3).
     - **The plan.** Prove the access lemma from the height picture, then the premise from the matching picture.
     - **The alternative.** Selection as a dimer model on large planar contradictions.

   **2026-11-02: the planar theorem, by discrete convexity** (`PLANAR-THEOREM-20261102-001`).
   - **The access lemma is proved.**
     - **Heights.** After a knot is removed from a planar contradiction, each solution is a matching of knots to faces. Comparing it
       with a fixed matching across every corner gives each distinction an integer height, zero on the removed knot's faces. A
       distinction's value relative to the hub is the parity of its height.
     - **Convexity.** The heights are exactly the solutions of a system of difference constraints. So they are closed under rounding the
       midpoint of any two, up or down.
     - **The gluing knot.** Its three states form a staircase in the heights of its ports.
     - **The argument.** Suppose the hub and a near distinction fix the gluing pattern without reaching the ports. Then rounding
       midpoints between the pinned state and the other states would force the near distinction's height to two different values. So
       the hub is tied to a usable port, or knotted with the other two ports one step away.
   - **The hub is not special (proved).** Re-centring the heights at any distinction keeps them convex. So on a planar side, every pair of
     distinctions that fixes the gluing pattern reaches the ports, and every candidate new knot of that kind is built one port at a time,
     whatever is glued on the far side.
   - **Knots across one port are 2-sums (proved, any contradiction).** A crossing knot whose constraint passes through a single port is two
     one-sided knots eliminated through that port, or a one-sided knot in disguise.
   - **Handles (computation).**
     - **The census.** On the Fano pattern and census 58, no pair of non-port distinctions that fixes the pattern reaches the ports.
     - **Larger contradictions.** The Fano pattern was spliced into planar contradictions, giving 16 distinctions with one handle.
       There, access depends on where the gluing knot sits, not on where the removed knot is. In the planar part every case has it
       (6,056). In the Fano part almost none do (992 of 12,368).
   - **What is left.**
     - **Generated on every splice tested.** One-sided knots and pinned three-distinction knots generate all 58,875 crossing knots, and
       every new knot is a pinned three-distinction knot through the hub.
     - **Unproved.** The remaining 12,102 crossing knots reduce on every splice, but no proof that they always do is known.
   - **Reading.**
     - **Why a planar side composes.** Its selections have convex heights, so a pin can always be taken apart one port at a time.
     - **What a handle does.** It breaks the heights where the selection is read.
     - **Doctrine.** Hubs remain equality fan-out, and the heights are a proof device, not a distance.
   - **Provenance.** Heights of planar matchings (Thurston, Propp) and L-convex sets (Murota) are classical. New here: the access proof,
     its extension to every pinning, the 2-sum lemma and the handle-locality computation.
   - **Next (taken).** Handles seen from a gluing knot (2/3).
     - **The plan.** First prove that access at a gluing knot depends only on a planar neighbourhood of that knot. Then test, with one
       and two Fano pieces, whether creation happens exactly at gluing knots on handles.
     - **The alternatives.** Finish the reduction of the remaining crossing knots (1/3). Selection as a dimer model (2/3).

   **2026-11-03: handles seen from a gluing knot** (`HANDLE-LOCALITY-20261103-001`).
   - **Access is local (proved).**
     - **A wider setting.** Some planar systems have as many knots as odd faces. Each such system behaves like a planar contradiction
       minus a knot: its solutions are matchings of knots to odd faces, with convex heights. So every pinning there reaches the ports.
     - **Splices.** Seen from across a 3-edge cut, an untouched side looks exactly like the distinction or knot it replaced. So a
       planar piece seen through a cut is always such a system.
     - **So** two distinctions of a planar piece that fix a gluing knot's pattern always reach its ports, whatever is removed elsewhere.
   - **Where new knots appear (computation, with one lemma).** The contradictions are one or two Fano patterns in planar glue.
     - **A cut carrying one bit screens (proved).** Creation at a planar gluing knot is then creation on a planar contradiction.
     - **No handle at either knot: nothing is created** (896 cases).
     - **A handle attached at a knot** never creates outside itself.
     - **A handle attached at a distinction, opened by the removal,** creates at planar gluing knots around it, out to distance 5 on
       the contradictions tested. It talks to the planar glue through the distinction's three copies, which carry two bits.
   - **The earlier premise fails.**
     - **Near an opened handle.** Many new knots are not pinned. Two handle distinctions force the gluing knot into two adjacent
       patterns, and a far distinction rules them out.
     - **Inside handles.** Four-distinction new knots appear.
   - **Reading.**
     - **An intact handle is invisible.** It looks like the distinction or knot it replaced.
     - **An opened handle is read twice:** where it sits, and in a halo that the planar glue carries by forced matchings.
     - **Doctrine.** Distances here only describe where creation was found. Hubs remain equality fan-out.
   - **Provenance.** Matching heights and convexity are classical (Kasteleyn, Thurston, Propp, Murota). New here: planar matching systems
     as a common setting, the interface and screening lemmas, and the creation map.
   - **Next (taken).** The halo as dimer forcing (2/3).
     - **The plan.** Characterize, by forcing in the matching picture of the distinction split, which planar gluing knots an opened handle
       reaches. Prove it, and measure the reach on large planar pieces.
     - **The alternatives.** Explain the screened knot-attached handle; finish the planar reduction lemma; classify the new knot types
       (1/3 each).

   **2026-11-03: the halo of an opened handle** (`HALO-FORCING-20261103-001`).
   - **Which knots an opened handle reaches (route lemma proved, converse checked).**
     - **The rule.** A new knot is two distinctions in the handle and one far distinction. It appears exactly when the two handle
       distinctions squeeze the gluing knot into one or two patterns, and no route rebuilds the knot.
     - **A route.** One of the knot's distinctions separates the knot, or a pair of the knot's distinctions carries a two-step
       elimination. The far distinction decides which pairs are usable, so some far sides see farther than others.
     - **The evidence.** The rule held for every case on contradictions with a Fano pattern attached to planar pieces of up to 14
       distinctions: 1,500 new knots, and no routed knot new.
   - **Heights compute it (proved).** Which port patterns and knot patterns occur together is a parity question about heights. Shortest
     paths answer it exactly, so the halo can be computed on planar pieces of hundreds of distinctions.
   - **How far it reaches (computation).**
     - **On a ladder,** all the way: on prisms of up to 80 distinctions, the farthest gluing knot still creates.
     - **On a grid,** three steps: on contradictions of up to 256 distinctions, nothing farther creates. From distance 7 on, a knot in
       the grid is exactly independent of the handle's distinction.
   - **Reading.**
     - **The mechanism.** The planar glue carries a handle's influence by forced matchings. A ladder is frozen and passes it on without
       loss; a grid is liquid and forgets it.
     - **So** where native selection can see a handle depends on the rigidity of the planar glue around it.
     - **Doctrine.** Distances only describe where creation was found. The heights are a proof device. Hubs remain equality fan-out.
   - **Provenance.** Matching heights and the frozen and liquid phases of dimer models are classical (Thurston, Propp, Kenyon, Okounkov,
     Sheffield). New here: the route criterion, the height transfer, and the halo measurements.
   - **Next (taken).** Creation and dimer phases (2/3).
     - **The test.** Build planar pieces where frozen and liquid parts meet. Is the halo exactly the frozen region joined to the handle?
     - **The proofs.** The ladder law and the grid bound.
     - **The alternatives.** The screened knot-attached handle; the planar reduction lemma; other and several handles (1/3 each).

   **2026-11-03: creation and dimer phases** (`PHASE-HALO-20261103-001`).
   - **The claiming lemma (proved).** When a handle's distinction is split open, a port is the odd distinction of its knot exactly when
     that knot takes the one skip of the face opposite the port. So every knot around that face feels whether the port is odd.
   - **Opposite faces carry the halo (computation).**
     - **The test.** The Fano pattern as handle, at 126 attachment distinctions: ladders, thick tubes, a grid, random contradictions,
       and a ladder arm spliced onto a grid.
     - **The result.** Every halo knot beyond three steps lies on a face opposite the attachment distinction. In 124 cases the halo is
       exactly those faces' far knots.
     - **So the phase reading is replaced.** The reach is the size of the faces opposite the handle, not a frozen region as such. A
       ladder's opposite face is a whole cycle; a grid's faces have at most three corners.
   - **The handle matters (computation).** Census 58 as handle can also speak through the distinction's own long face (5 of 24
     distinctions). The general law is "the faces around the attachment distinction".
   - **The ladder law (proved, given the route criterion).** A prism is a cyclic chain of consecutive triples. Its transfer matrix repeats
     with period 2, so a far knot's transfer depends only on its parity, the same on every prism. The halo runs the full opposite face on
     every prism.
   - **The grid law (certified).** A knot with the full transfer is independent of the handle (proved). Every knot in the grid tested
     at distance 9 or more has it, and at 7 or more on the 256-distinction grid (exact certificates). Height ranges between ports and
     knots are 0 at every distance on ladders and grow with distance on grids.
   - **Reading.**
     - **A face is a native long-range constraint.** Exactly one of its knots skips into it, so a handle is seen as far as the faces
       around it extend.
     - **The dimer phase** summarizes face sizes and how rigid the heights are. It is not a separate cause.
     - **Doctrine.** Distances only describe where creation was found. The heights are a proof device. Hubs remain equality fan-out.
   - **Provenance.** Kasteleyn signings, Boolean transfer matrices, matching heights and dimer phases are classical. New here: the
     claiming lemma, the opposite-face law and its dependence on the handle, the chain reduction of the ladder, and the height-range
     measurements.
   - **Next (taken).** Which faces a handle uses (2/3).
     - **The plan.** Classify handles by the faces they speak through, their own or the opposite ones. Explain the Fano pattern against
       census 58 through the handle's port relation. Prove the opposite-face law for the handles that obey it.
     - **The alternatives.** The screened knot-attached handle; the planar reduction lemma; several interacting handles (1/3 each).

   **2026-11-03: which faces a handle uses** (`FACE-CLAIM-20261103-001`).
   - **What each face reads (proved).** Split the planar glue at the attachment distinction. Its three faces there merge into one face
     that takes a single skip, on the arc opposite the port that is odd.
     - **Own arcs.** The arc between two ports is barred exactly when those ports disagree.
     - **Opposite faces.** Whenever two ports agree, the face opposite the third port is claimed by that port's knot.
     - **Frozen knots.** A barred face fixes two distinctions of each of its knots.
   - **Claims (proved).** A frozen knot can still deviate by claiming its face, at either fixed value.
     - **On an own arc,** a claim comes from one port pattern.
     - **On an opposite face,** it comes from two, which share the other two ports.
   - **The claim rule (one direction proved, the other computed).** An opened handle creates at a frozen knot exactly when a pair of
     its distinctions freezes the knot and neither distinction alone excludes either claim. No disagreement appeared against exact
     creation or the pipeline.
   - **Which faces a handle uses (computation).**
     - **The census.** 305 handles from 24 non-planar contradictions, in every port order on a ladder. Nine signatures occur.
     - **The rule.** The faces are decided by the handle's port relation alone.
     - **The Fano pattern.** Each of its single distinctions removes one pattern per other class. That kills every one-pattern claim
       and never a two-pattern one, so it never uses an own arc (proved) and always uses the opposite face.
     - **Census 58** uses its own arc exactly when the bottom port is 0 or 5.
   - **The last law fails (counterexample, exact on a small piece).** Where a ladder arm is spliced onto a grid, a junction distinction
     freezes the arm's far long face with two-pattern claims, and every handle tested creates there. So the halo is not confined to the
     faces around the distinction: it lies on frozen knots whose claims survive the handle's single distinctions.
   - **Reading.**
     - **The bit.** A face reads one bit of the handle: whether two of its ports agree.
     - **The planar glue** carries that bit as far as its frozen structure reaches.
     - **The handle** decides it by how sharply one of its distinctions cuts the port patterns.
     - **The phase reading returns, refined.** The frozen region is the dimer model's frozen region for the ports' boundary condition.
     - **Doctrine.** Distances only describe where creation was found. Hubs remain equality fan-out.
   - **Provenance.** Kasteleyn parities, corner matchings, unit propagation and dimer frozen regions are classical. New here: the arc
     identity, the reading and claim lemmas, the claim rule, the census of handles and the junction counterexample.
   - **Next (taken).** The frozen region by heights, and rigid strips (2/3).
     - **The plan.** Prove that a port pattern freezes exactly the distinctions whose height difference to the ports cannot vary,
       explain the junction as a rigid strip, and test whether long rigid strips through liquid bodies carry the halo.
     - **The alternatives.** The converse of the claim rule as a theorem (2/3); the structure of the nine signatures; the screened
       knot-attached handle (1/3 each).

   **2026-11-03: the frozen region by heights, and rigid strips** (`STRIP-RELAY-20261103-001`).
   - **Frozen means fixed height (proved).** The port class fixes the ports' heights, because the merged face's single skip lies on a
     known arc. Heights with fixed port values are closed under rounded midpoints. So a port pattern freezes exactly the distinctions whose
     height difference to the ports cannot vary.
   - **Collapsing untouched sides (proved for the transfer).** Across a 3-edge cut, a side holding neither the handle nor the gluing
     knot acts as the vertex it lost. Collapsing it leaves creation unchanged, so the faces-around-the-distinction law holds again in
     the collapsed contradiction. The last epic's junction was a ring seeing itself as the closed prism.
   - **Pendant rings (proved, given the ladder law).** From the middle distinction of the ring's removed knot, the halo runs along the
     ring's whole far face, for every ring length.
   - **Rigid strips relay (computation, exact on small pieces).**
     - **The relay.** Between two grids, an opened handle in the strip or the far grid creates in the first grid near its cut. It does so
       from every distance along a rigid strip, at the same knots whatever the strip's length.
     - **Liquid screens.** A grid instead of the strip screens it within three steps.
     - **Direction.** The relay enters only a side split at a distinction there, and a handle leaves only where its grid lost a knot. A
       knot-attached composite handle is screened.
   - **Reading.**
     - **Native channels.** Rigid strips are native channels for a handle's one-bit reading. Native selection sees a handle at the far
       end of a frozen channel, in a liquid region the handle is not in.
     - **Direction.** The channels are directed, from the side that lost a knot to the side that lost a distinction, the direction of a
       handle's own splice.
     - **Doctrine.** Distances only describe where creation was found. A channel carries a reading, not a metric. Hubs remain equality
       fan-out.
   - **Provenance.** L♮-convexity (Murota) and frozen dimer regions are classical. The interface lemma and the screening of
     knot-attached handles are from HANDLE-LOCALITY. New here: the heights lemma, the reduction lemma, the ring law, relays, their
     screening and their direction.
   - **Next (taken).** Relay networks (2/3).
     - **The plan.** Branch and chain rigid strips through small pieces. Test whether one handle's halo reaches several grids, how
       relays from two handles combine where channels meet, and whether directed channels compose into native paths.
     - **The alternatives.** Proofs of the relay's length independence and the composite-handle reading (1/3); the converse of the
       claim rule (2/3).

   **2026-11-04: relay networks** (`RELAY-NET-20261104-001`).
   - **Relays are wires.** After a frozen hop, an opened handle's relay reaches the next cut as an arc signal: two ports fixed and
     disagreeing, the third free.
     - **The arc lemma.** An arc signal freezes exactly the knots with a corner on the own arc between its fixed ports. One direction is
       proved; the other is computed.
     - **Repeaters.** A station passes the signal on exactly when its out-knot lies on that arc. Aligned stations repeat it without
       loss, and the relay reaches a grid four cuts away. A misaligned station ends it.
   - **Broadcast, direction, bypasses (computation, exact on small networks).**
     - **Hubs broadcast.** A hub copies a relay into several receivers at once, so one handle is read at several receivers.
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
     - **The plan.** With several Fano pieces in planar glue, ask whether the creation map over all removals splits into one halo per
       Fano piece, counting and locating the handles.
     - **The alternatives.** The display rule (1/3); the claim rule's converse (2/3).

   **2026-11-04: a native reading of genus** (`NATIVE-GENUS-20261104-001`).
   - **The creation map splits by Fano piece.** Whether a removal creates at a gluing knot depends only on the Fano pieces holding the
     two knots; every other Fano piece acts as the vertex it replaced.
     - **Status.** Proved for Fano pieces attached at a distinction (interface and screening lemmas). Checked exactly for Fano pieces
       attached at a knot (13 designs, 5,130 entries).
     - **So** each removal's halo is its own Fano piece's, and Fano pieces attached at a knot have no halo on planar glue.
   - **Native selection counts and locates separated handles (computation fixed in advance).**
     - **The count.** Take a largest set of knots among which nothing creates. The remaining knots fall into one part per Fano piece, and
       each part is a Fano piece: 416 of 420 separated contradictions with two or three Fano pieces, every placement on two small prisms.
     - **Where it stops.** Fano pieces that touch merge, and so do three Fano pieces on the 4-distinction cube, whose glue keeps one
       knot. On the 32 three-regular contradictions up to 22 distinctions, where Fano pieces mostly touch, the count equals the genus
       in 10. It counts Fano pieces: the one trisum handle in the census is invisible to it.
   - **Blocks (exploratory).** Inside a part, maximal blocks of knots that create at one another equal the genus in 29 of the 32 and
     in all 310 Fano pairs, touching ones included.
     - **They overcount** where two distinction-attached Fano pieces hang from one Fano piece.
     - **Census 58 breaks into many blocks**, because its knots sharing two distinctions (a doubled square) never create at each other.
   - **Wires do not blur the count.** A rigid strip or a hub lands one Fano piece's halo on another Fano piece's cut in every placement
     tested (exact on a 26-distinction strip network). The count stays one part per Fano piece, and each halo stays its Fano piece's:
     the count reads the quiet glue and the knots the glue creates at, which a halo does not change.
   - **Reading.**
     - **Non-planarity is local.** Native selection marks exactly the handles' knots: planar glue never creates, and the glue creates
       at every knot of a Fano piece.
     - **The brace tree, one level down.** Quiet knots for glue, blocks for Fano pieces, one-way creation for a cut's direction, silence for
       doubled squares: native creation may read the whole decomposition.
     - **Doctrine.** Parts and blocks describe placements, not distances; no embedding is used.
   - **Provenance.** Genus = number of Fano pieces (THREEFOLD-SURFACES) and tight cuts (Lovász) are known. New here: the splitting lemma,
     the native count, its exhaustive small tests, blocks, and wires against the count.
   - **Next (taken).** A native reading of the brace tree (2/3).
     - **The plan.** Fix a refined block statistic in advance; test whether blocks, one-way creation and silence recover the
       tight-cut decomposition on the census and on fresh trees of Fano pieces; try to prove the block lemma for Fano pieces.
     - **The alternatives.** Proving that planar glue never creates (2/3); the display rule (1/3).

   **2026-11-05: a native reading of the brace tree** (`BRACE-TREE-20261105-001`).
   - **Fano pieces are blocks.** The Fano pattern's creation map is complete: every removal creates at every other knot.
     - **Fano pieces attached at a knot.** Such a Fano piece creates among its own knots exactly as the Fano pattern does (proved: the
       rest of the contradiction forces the ports constant, and the screening lemma applies).
     - **Fano pieces attached at a distinction.** The same is checked on every design.
   - **Cuts are read in their direction.** A receiver's cut knots and the emitter's knots create at each other; its intact knots create
     one way at the emitter's, never the reverse. This held at all 213 cuts between two Fano pieces.
   - **The dictionary.** Where only Fano pieces join two knots of Fano pieces, their relation is fixed by the tree: 42,090 pairs, none
     off the rules.
     - **Same Fano piece.** Mutual.
     - **Downstream.** Mutual with a receiver's cut knots, one-way with its intact knots.
     - **Siblings.** Mutual.
     - **Co-receivers.** Their intact knots are silent to each other.
     - **Through planar glue.** The relation can depend on more than the tree.
   - **The source rule counts the genus.** Keep a block of mutual creation when one of its knots is blind to everything the others are
     blind to.
     - **The count.** The rule equals the number of Fano pieces, and the genus, on all 157 contradictions without a non-Fano brace. 110
       of them are fresh: every three-regular class of 23 to 26 distinctions.
     - **The plain block count** fails 32 of them, wherever Fano pieces hang from a common Fano piece.
     - **Later (CHAIN-TRANSFER-20261106-001).** On Fano trees the rule holds up to five Fano pieces and fails at six; twins and footprints
       replace it there.
   - **Refuted along the way.**
     - **Determinism through planar glue.**
     - **Silent glue across a Fano piece.** In one class, a Fano piece relays creation from a planar piece to a doubled square.
   - **Not read.** Handles that are not Fano pieces: census 58 (itself a single brace of another kind) and the trisum brace.
   - **Reading.**
     - **The oriented handle tree, natively.** Native selection reads the handle tree: how many handles, where, and which way each
       touching pair is glued. Touching Fano pieces, where the plain count merged them, are resolved.
     - **Doctrine.** Blocks, directions and silence are relations given by creation; a direction is which side of a cut lost a distinction,
       not a direction in space.
   - **Provenance.** Tight cuts (Lovász) and genus = Fano pieces (THREEFOLD-SURFACES) are known. New here: the dictionary, native cut
     directions, the source rule and its fresh test.
   - **Next (taken).** A two-bit screening lemma (2/3).
     - **The plan.** Prove that a side attached at a knot acts as that knot for creation, not just for solutions. That would complete
       the splitting lemma and should give the block lemma for Fano pieces at a distinction and the one-way rule.
     - **The alternatives.** What native creation sees of non-Fano handles (2/3); the source rule beyond 26 distinctions (1/3).

   **2026-11-05: the two-bit screening lemma** (`TWO-BIT-SCREEN-20261105-001`).
   - **The closure is a bootstrap.** New knots are crossing triples that the rule "four classes with two derived knot triples derive
     all their knot triples" cannot reach from the non-crossing ones (proved equal to the elimination closure).
   - **No loss (proved).** An intact Fano side attached at a knot never removes creation.
     - **Off the side.** Its new knots off the side are exactly those of the contradiction with the knot restored.
     - **Through the side.** A generated knot through a hidden distinction has generated port shadows, and no crossing knot meets two hidden
       classes.
     - **Pendant knots.** The same holds for one new distinction in one new knot through two near distinctions.
   - **One statement left.** That the side never adds creation follows from the pendant-knot statement: one new distinction in one new knot
     never adds creation.
     - **Evidence.** It held on 117,344 cases, random systems included.
     - **Not proved, and not easy.** It is not local, and it is not a consequence of the knots alone.
   - **One knot is the limit.**
     - **Two or three knots create.** A distinction in two or three new knots through a knot's distinctions, such as the ports'
       majority, creates where the contradiction without it does not.
     - **Subcube distinctions never did.** No distinction whose exclusions are subcubes changed creation.
     - **Sides cut from contradictions.** Every such side tried, including every three-regular contradiction up to 22 distinctions, has only
       subcube distinctions.
   - **In Fano trees (contradictions built from Fano pieces alone).**
     - **Contraction (proved).** Creation in the chain of Fano pieces between two knots implies creation in the whole contradiction.
     - **Blocks (proved).** So every Fano piece is a block of mutual creation.
     - **The touching rule.** The brace dictionary between Fano pieces collapses to one rule: a removal creates at a knot of another
       Fano piece exactly when that knot touches its Fano piece's cut toward the removal. The removed knot's role never matters.
       - **Checked.** On every chain of two (294) and three (576) Fano pieces, and on paths of four.
       - **Proved half.** Its creating half holds in every Fano tree at distances one and two.
     - **Still computed.** Non-creation at knots that do not touch, and Fano pieces three or more apart.
   - **Reading.**
     - **Two bits made precise.** A side is screened when everything it hides is one-knot information: each hidden Fano distinction, seen
       alone, hangs from one knot through two ports.
     - **The tree, read locally.** A knot is seen from a direction exactly when it touches the cut facing that direction. An emitting
       Fano piece presents all its knots to the cut, and a receiving Fano piece only its three cut knots. That is how creation reads a cut's
       direction.
     - **Doctrine.** Hidden distinctions are witnesses quantified away. Quantifying a Fano side's witnesses away loses no emergence; whether
       it adds none is the open statement.
   - **Provenance.** Bootstrap closures and principal matroid extensions are classical analogues, neither found stating these results.
     New here: the four-class form of the closure (the record's tetrahedron form), the no-loss theorem, the pendant reduction and its
     sharpness, the contraction theorem, and the proofs of the block lemma and nearby creations.
   - **Next (taken).** Prove the pendant-knot statement (2/3), starting from the computed fact that
     eliminating through the gluing knot's distinctions suffices.
     - **The alternative.** The bridge to proof complexity (2/3), still the leading alternative for the next arc.

   **2026-11-06: the pendant-knot statement** (`PENDANT-LINE-20261106-001`).
   - **Creation is decided at the gluing knot, in two rounds (proved).** The closure reaches exactly the crossing knots whose near and
     far parts meet through the gluing knot.
     - **Round one.** A near knot and a far knot sit on the same pair of the knot's distinctions.
     - **Round two.** Two round-one knots share a distinction.
     - **New knots** are the crossing constraints the parts carry together that pass through no pair of the knot's distinctions.
     - **Proof.** The closure was reduced to local configurations, and all 348,376,032 were checked.
   - **One new knot never adds creation (proved).** A new distinction in one new knot through two distinctions, whatever its signs,
     leaves creation unchanged.
     - **Proof.** From the two-round rule, with all 347,149,320 local configurations checked.
     - **Sharpness.** A distinction in two or three such knots can create (TWO-BIT-SCREEN), so one knot is the exact limit.
   - **Completed.**
     - **The two-bit screening lemma.** An intact Fano side acts as its knot for creation, as it does for solutions.
     - **The splitting lemma** for Fano pieces attached at distinctions and at knots.
     - **In Fano trees.** A knot creates at another exactly when it does in the chain of their Fano pieces.
     - **The touching rule up to distance two.** A knot receives creation from another Fano piece at most two away exactly when it touches
       its Fano piece's cut toward it. So native creation provably keeps each Fano piece whole and reads every cut in its direction.
   - **Reading.**
     - **Where emergence is selected.** Native selection picks out emergence exactly where the parts fail to meet at the gluing knot.
     - **"Two bits", made exact.** One knot of hidden information is safe and two are not.
     - **Doctrine.** Directions are which side of a cut lost a distinction, and touching is incidence. No space is assumed.
   - **Provenance.** Reducing a closure to finitely many local configurations is a standard verification route; no statement of these
     results was found.
   - **What is left.** For the source rule to become a theorem, a transfer along chains of four or more Fano pieces. Distance three held on
     the 16 paths of four Fano pieces computed.
   - **Next (taken).** A transfer along chains (2/3): prove the touching rule at every distance in Fano trees.
     - **The alternative.** The bridge to proof complexity (2/3).

   **2026-11-06: the touching rule at every distance** (`CHAIN-TRANSFER-20261106-001`).
   - **The touching rule holds at every distance (proved).** In every contradiction built from Fano pieces alone, a knot receives
     creation from a removal in another Fano piece exactly when it touches its Fano piece's cut facing the removal, however far away
     the removal is.
     - **Proof.** A chain of Fano pieces carries only a finite profile from one cut to the next. There are 47 profiles, none new after three
       Fano pieces, and each was checked with every last Fano piece (12,894 verdicts).
     - **What the profiles show.** A removal leaves the ports of every cut beyond it free. So the receiving Fano piece alone decides
       creation.
   - **The source rule fails (proved).**
     - **Where it holds.** It counts the Fano pieces of every Fano tree of at most five Fano pieces.
     - **Where it fails.** At six Fano pieces: a receiver that takes two loaded cuts and emits the knot through their distinctions has
       no source. Exact creation maps confirm it.
   - **A short rule reads the tree (proved).**
     - **Fano pieces.** Knots that create at each other and at the same other knots form one Fano piece.
     - **Cuts.** Fano pieces that create at a proper subset of a Fano piece's knots lie beyond one of its receiving cuts.
     - **What it reads.** The Fano pieces and the directed tree of every Fano tree whose Fano pieces have at most four cuts.
     - **Not yet through planar glue.** On the census of 23 to 26 distinctions, a glue knot can join a Fano piece's class and a Fano
       piece can split into three pairs.
   - **Reading.**
     - **Openness travels; direction is read at the receiver.** A removal opens every cut beyond it. A knot feels it only if it touches
       its own Fano piece's cut facing it.
     - **A handle is a set of knots seen together.** Its knots create at each other and are created at by the same knots elsewhere.
     - **The tree is read from its receivers.** Every cut has one receiver, whose knots through the lost distinction name the cut.
     - **Doctrine.** Twins and footprints are relations among knots. No space is assumed.
   - **Provenance.** Finite-state transfer along bounded interfaces, and Buneman's theorem that splits determine a tree, are classical.
     No statement of these results was found.
   - **What is left.** Planar glue, non-Fano handles, heavily loaded Fano pieces, and other far sides.
   - **Next (taken).** Reading through planar glue (2/3): add planar pieces to the profile automaton and look for
     one rule that reads the genus of every three-regular contradiction.
     - **The alternatives.** Non-Fano handles (1/3); the bridge to proof complexity (2/3).

   **2026-11-06: reading through planar glue** (`GLUE-READ-20261106-001`).
   - **Creation at a Fano piece is decided by its cut (proved).** Whether a removal creates at a knot of a Fano piece depends only on the
     patterns the removal's side allows on the Fano piece's cut facing it: three ports' worth.
     - **An emitter.** Its knots receive exactly when the ports may be equal.
     - **A receiver.** A cut knot receives exactly when the other two ports are not forced equal. An intact knot receives exactly when
       the side tells the ports apart.
     - **Proof.** Every port relation was checked against every deeper relation at once (8,190 cases). The census agrees at all 47,550
       pairs.
   - **What glue does (computed, 191 contradictions).**
     - **Through Fano pieces.** The cut is always free, so the touching rule holds.
     - **Through glue.** Glue can exclude a pattern pair or tie two ports, and the touching rule fails exactly there.
     - **Its two disturbances are local.** A doubled-square knot through two of a Fano piece's ports joins it. A Fano piece emitting into a
       planar piece splits by its ports, because knots of planar glue see where a removal entered and knots of Fano pieces do not.
   - **Reading the Fano pieces.**
     - **Where it works.** A two-stage twin rule reads every Fano tree with at most four cuts per Fano piece (proved), every census
       contradiction and 57 of 80 random glued contradictions.
     - **Where it stops.** In 15 random contradictions, knots of Fano pieces meeting one planar piece are indistinguishable by whether
       creation occurs, so no such rule can read them.
     - **What survives.** Which far side creates still separates them.
   - **Reading.**
     - **A cut is a Fano piece's whole window.**
     - **Fano pieces are blind to depth; planar glue is not.**
     - **Handles on one planar piece.** Several handles on one planar piece can look alike to whether creation occurs. Only how it
       occurs, which far side completes it, keeps them apart.
     - **Doctrine.** Cuts, ports and far sides are relations among knots. No space is assumed.
   - **Provenance.** Bounding an OR over local configurations, and invariance under automorphisms, are standard. No statement of these
     results was found.
   - **What is left.**
     - A rule using the far sides.
     - The relation a planar piece presents, derived from its faces.
     - Non-Fano handles.
   - **Next (taken).** Reading with the far sides (2/3): on the 191 saved maps, look for a rule that separates
     Fano pieces meeting one planar piece without splitting Fano pieces.
     - **The alternatives.** Glue relations from faces (1/3); non-Fano handles (1/3).

   **2026-11-06: do handles govern counting hardness?** (`HANDLE-COUNT-20261106-001`).
   - **The genus half is classical.** Counting colourings (with any signs and any weight per monochromatic knot) is an even-subgraph sum
     on the incidence graph. On a surface of genus g that takes 4^g determinants (Galluccio–Loebl, Tesler, Cimasoni). So counting is
     fixed-parameter tractable in the genus and never hard at bounded genus. Nothing new is claimed here.
   - **The knot's handles cost nothing (proved).** A Fano piece meets the rest of a contradiction through three edges, and every even
     tensor on three edges is a planar gadget: the first matchgate identity lives at four. So any number of Fano pieces can be counted
     through.
   - **The glue's handles can cost (proved).** Where three planar pieces meet at a square (a Robertson–Seymour–Thomas junction), the
     junction can leave the planar class. Each such junction costs at most a factor 2 on the piece it hangs from, so counting takes
     time 2^(junctions) times a polynomial. At the knot's law only squares with three twisted sides, or above them, cost.
   - **On the knot's own contradictions, Fano pieces pay for the junctions (proved).** Every end piece of the glue needs an odd number
     of signs on a square away from its junction. A plain contradiction has no signs to spend: its signs come only from twisted sides
     of its tight cuts, and those end in Fano pieces. So junctions + planar glue pieces ≤ Fano pieces − 2. The trisum of three cubes
     with three Fano pieces (29 distinctions) attains it.
   - **So on the knot's contradictions counting is fixed-parameter tractable in the number of Fano pieces** (time 2^(number of Fano
     pieces) times a polynomial), and polynomial at any number of Fano pieces when the glue is planar. The knot's hard couplings need
     unboundedly many Fano pieces.
   - **Off the knot's contradictions, signs pay instead.** With signs, or on colourable plain Pfaffian braces, counting is #P-hard with
     no Fano piece.
   - **Computed.** On 257 contradictions (the census to 26 distinctions, 80 random contradictions with planar glue, larger ones and 28
     with trisum glue) the bound holds and 771 exact counts agree two ways. Evaluations grow with junctions, never with Fano pieces.
   - **Reading.**
     - Hardness lives in handles, but not in the knot's: in the glue's junctions.
     - The knot can twist its glue only by spending Fano pieces. Three ports are free; four ports can cost; at the knot's law, three twisted
       sides at a square are what costs.
     - The planar half of the owner's hypothesis holds. Pfaffian glue is not tractable by itself; on the knot's contradictions it is
       paid for.
   - **Provenance.** Genus: classical. Small separations and matchgate splitting: classical techniques. The junction bound and its
     sharpness: no source found.
   - **Next (recommended, awaiting the owner).** Native reading of junction handles (2/3): do exact creation maps read the glue's junctions
     and the Fano pieces that pay for them? Start on the 29-distinction contradiction and the edge-piece chains.
     - **The alternatives.** A hardness bound in the number of Fano pieces (1/3); reading with the far sides (2/3, still pending).

   **2026-11-06: reading with the far sides** (`FAR-READ-20261106-001`).
   - **The far sides nest (computed, 191 contradictions).** The Fano pattern and census 58 create at the same pairs. K4^(3) creates
     only where census 6 does, and census 6 creates without the Fano pattern only at glue knots. So at a knot of a Fano piece creation
     has one of four strengths.
   - **A Fano piece acts as one from outside (computed, 1,065 of 1,065 Fano pieces).** Whichever of its knots is removed, every knot of
     another Fano piece receives the same far-side vector. Its knots differ only on glue knots and in what they receive.
   - **A rule reads the Fano pieces.**
     - **The rule.** Twins; twins among knots of Fano pieces; a split into the finest parts of three or more knots that act as one;
       reattachment of single port knots through the Fano pattern.
     - **Development.** It returns exactly the Fano pieces of all 191 saved contradictions, and every step is needed.
     - **Fresh test.** Frozen, it reads all 86 fresh contradictions within a cost cap fixed in advance (334 Fano pieces). That includes
       the 24 fresh contradictions where whether creation occurs cannot tell Fano pieces apart. The two-stage rule reads 51 of the 86,
       the source rule counts 68.
     - **Not proved.** Neither the rule nor "acts as one" is a theorem.
   - **Reading.**
     - **A handle is one thing from outside.** Its parts are not separately visible to the rest of the contradiction, so a Fano piece
       is atomic in a precise sense.
     - **Why the yes/no relation failed.** A planar piece hides which Fano piece a removal came from. Which far side completes the creation
       does not.
     - **A known structure.** Acting as one is a one-sided module, as in Gallai's modular decomposition and the clans of 2-structures.
       Reading handles as the finest such modules of the creation map is new.
   - **Provenance.** Modules are classical. No source was found for the far-side structure, the rule or its fresh test.
   - **What is left.**
     - A proof that Fano pieces act as one.
     - Non-Fano handles. HANDLE-COUNT's junction handles, where counting hardness on these contradictions lives, are such handles.
     - The cost cap's gaps: census contradictions with three more Fano pieces, and the largest planar contradictions.
   - **Next (taken).** Prove that a Fano piece acts as one from outside (2/3).
     - **The easy case.** A scratch probe found that in 576 of the 731 saved Fano pieces, removing any knot leaves every port pattern
       allowed, so the rest of the contradiction cannot tell which knot went.
     - **The hard case.** The other 155 have five to twelve ports and need the receiving-cut law.
     - **The alternatives.** Non-Fano handles through the receiving-cut law (1/3); glue relations from faces (1/3).

   **2026-11-07: why a Fano piece acts as one** (`ATOM-ONE-20261107-001`).
   - **Every Fano piece, with its closed sides, is the Fano pattern (proved).**
     - **Sides.** A closed side acts as its lost element up to signs (KNOT-COMPOSE A, as corrected by NATIVE-PATHS A).
     - **Signs.** Of the 256 signed Fano patterns, only the plain one is a knot.
   - **A Fano piece with a knot removed is transparent (proved).** With any one of its knots removed, it sends the free relation through
     every one of its cuts. So the rest of the contradiction sees the same port relation whichever knot went.
     - **The knot is needed.** With arbitrary relations on its other cuts, this holds only for Fano pieces with at most one knot-type cut.
   - **Fano pieces see only the port relation (proved).**
     - **Creation.** Deep distinctions of a removal's side never decide whether a Fano piece's knot receives creation, even paired with deep
       distinctions behind the Fano piece's other elements.
     - **Far sides.** They add census 6 or K4^(3) only at a receiving Fano piece's cut knots whose port relation has six patterns.
     - **Pass-through.** A free relation passes through a closed Fano piece unchanged.
   - **So a Fano piece acts as one.**
     - **Proved.** For creation in every contradiction; far side by far side outside that one case; and without exception on Fano trees.
     - **Computed.** On 277 contradictions, saved and fresh, every Fano piece's knot receives exactly its closed verdict at all 154,165
       pairs. The exception occurs at 1,325 receiving cuts and adds nothing. These predictions were written before the run.
   - **Bounding cannot show more.** Deep distinctions behind a Fano piece's own other elements could add creation (56 of 980 abstract
     cases). No actual contradiction ever does.
   - **Reading.**
     - **A handle is all or nothing from outside.** With all its knots, it constrains each cut as one lost element. With any one knot gone,
       it constrains nothing any cut can see.
     - **Where this comes from.** The knot itself: the plain Fano pattern is the only signed Fano knot, and any missing knot frees every
       other element.
     - **Fano pieces are blind to depth.** That is now a theorem for creation and, outside one finite case, for far sides.
     - **Doctrine.** No space is assumed.
   - **Provenance.** The Fano plane as the smallest critical non-2-colourable triple system, and the brace decomposition, are classical.
     No statement of the signed classification, transparency or the corollary was found.
   - **What is left.**
     - A proof of the exception.
     - That no Fano piece splits into smaller parts acting as one.
     - Handles that are not Fano pieces.
   - **Next (taken).** The genus reading on Fano trees (2/3). Prove that FAR-READ B's rule returns exactly the
     Fano pieces of every Fano tree, then add planar glue.
     - **The alternatives.** Whether junction handles act as one (2/3); a proof of the exception (1/3).

   **2026-11-07: the axis built from logic** (`LOGIC-AXIS-20261107-001`).
   - **The owner's picture.** A number line or Cartesian plane whose axes are themselves infinite structures of logic, measured in
     logic. The measure used is bond distance: the least knot through two distinctions, minus one, read from allowed states alone.
   - **Without ends, bond distance is a ruler (proved).**
     - **Chained knots.** If far-apart parts of a law are independent, every knot is chained, so bond distance grows at least
       linearly with separation. Parity laws whose finite moves are dense (laws without ends) have this property.
     - **An endless chain, the literature's number line.** On the endless chain of atoms w(t−1) ∧ L(t) → w(t), the bond distance
       between w_s and w_t is exactly t − s + 1: one unit per loop. A chain of two-place ties has no knot, so it has no spacing.
     - **The drawn lattice.** Tseitin's and the gauge law, placed on a drawn lattice, read its dimension from their allowed states:
       bond balls grow like r^d. On the drawn plane lattice the ruler is taxicab, 2d + 1 to 2d + 7: an x-count plus a y-count, never the
       diagonal.
     - **One bit per cell freezes.** A parity law with one distinction per cell is free or has no finite moves. A native parity law
       on the drawn plane lattice needs a distinction per lattice direction.
     - **Native in every variable is not enough.** Take Ledrappier's law on x, z free and y = x + z. Every variable is flipped by a
       finite move, yet a six-variable knot joins distinctions 2^k apart for every k. A correction request asks whether a native knot must
       also be natively bound. On 2026-11-07 the owner recorded the answer as an assumption: yes, open to challenge (A1 of the
       [register of assumptions](ASSUMPTIONS.md)).
     - **Growth never stretches.** A conservative extension never increases bond distance. A system that keeps its old allowed states
       grows only by adding distinctions, never by moving existing ones apart.
   - **The frozen axis is measured in signed bits (proved; equality conjectured).**
     - **Infinite bond balls.** In Ledrappier's law the three-place knots are exactly the Frobenius triangles of the drawn lattice.
     - **The bound.** Along each line of the drawn lattice, bond distance is at most 1 + w(n), the signed-binary digit count of the
       separation, and it is 2 exactly at powers of two.
     - **Equality** is checked in windows: n <= 128, and all 168 vectors of [−6, 6]^2.
   - **With nothing drawn, towers stretch only through loose ends.**
     - **Proved (hub-free gadgets).** Replacing every knot by a gadget keeps the old knot exactly when the gadget adds no loose end, a
       distinction held by one knot. Every step is then conservative, and the original distinctions stay at bond distance 2 forever.
       The 2026-10-20 refinement is such a gadget, which is why it could not grow space.
     - **Measured (exploratory).** Gadgets with loose ends stretch the ruler by a fixed factor per level: 3^k + 1 for the star and the
       hexagon, 3·4^(k−1) + 1 for the prism. Their growth dimensions, log(copies)/log(stretch), are 1.26, 1.63 and 1.29.
     - **Trees (proved).** On knot graphs that are trees, bond distance is the number of knots on the path plus one.
   - **Reading.**
     - **Where logic measures.** Logic measures space faithfully exactly where nothing is opened by infinity.
     - **Where space expands.** Space expands between existing distinctions exactly where growth adds loose ends. The growth of
       emergent information and the growth of space meet there.
     - **What is still put in.** The dimension comes with the gadget, like a drawing. In no tested law is it derived from a rule
       that does not mention it.
   - **Provenance.** Strong irreducibility and dense homoclinic groups (Lind–Schmidt) underlie the ruler. Ledrappier's non-mixing
     shapes and Masser's unit equations in characteristic p underlie the frozen axis. Wolfram measures dimension by ball growth in
     drawn hypergraphs. No source was found for the bond-distance reading, the signed-binary construction or the loose-end criterion.
   - **Next (recommended, awaiting the owner).** Growth at loose ends (2/3). Let a uniform rule act only where the relation shows a
     loose end, with no chosen gadget design, and measure the growth exponent of bond balls.
     - **The alternatives.** The signed-binary lower bound (1/3); the logical Cartesian product of two chains (1/3).

   **2026-11-07: reading the genus natively** (`GENUS-READ-20261107-001`).
   - **Census 6 depends on how it is glued (proved).**
     - **How the test glues.** It joins a far side's split-distinction knots to the gluing knot's distinctions in the order they are
       written.
     - **Order-free.** K4^(3), the Fano pattern and census 58 have the symmetry that makes the order irrelevant.
     - **Census 6.** It has three inequivalent gluings, and its verdict changed with the order in 8,046 of 11,552 sampled pairs.
     - **Creation.** Whether creation occurs never depends on the order.
   - **Natively a Fano piece is homogeneous (proved).** Count census 6 over its gluings. Then in every Fano tree every ordered pair of
     knots of a Fano piece gets the same far-side vector: no K4^(3), census 6 at one gluing of three, the Fano pattern, census 58.
     Whatever hangs behind its cuts forces it.
   - **So FAR-READ's split step was not native.** Given native vectors, it cuts every Fano piece of six or seven knots: none of 23 Fano
     trees read, against all 23 in the written order. The native reading of Fano trees is the yes/no twin rule, already a theorem.
   - **Through planar glue (computed).**
     - **The information is native.** The order-free far sides tell apart all 372 pairs of Fano pieces that whether creation occurs cannot.
     - **Where it sits.** For 114 pairs it lies only in what the two knots do to glue knots.
     - **The best rule so far.** Native row twins read 234 of 277 contradictions.
   - **Reading.**
     - **A handle is one thing inside and out.** All its knots are alike to each other, and it acts as one from outside.
     - **The structure the split relied on** was how census 6's knots were written down.
     - **Doctrine.** No space, and no listing order, is assumed.
   - **Corrections.** `FAR-READ-20261106-001-D002` and the census-6 sentence of `FAR-READ-20261106-001-D001` carry pending qualifications.
   - **Provenance.** Invariance of a gadget's verdict under its symmetries is standard. No statement of the gluing classification or of
     native homogeneity was found.
   - **Next (taken).** Colour refinement on the native creation map (2/3). It is a canonical, representation-free
     procedure. Does its stable partition ever merge knots of two Fano pieces?
     - **The alternatives.** Junction handles natively (2/3); a native audit of earlier far-side records (1/3).

   **2026-11-07: growth at loose ends** (`OPEN-END-GROWTH-20261107-001`).
   - **The question.** Let a uniform rule act only where the relation shows a loose end, a distinction held by one knot, with no
     chosen design. What space does it grow?
   - **A local rule grows an endless chain, the literature's number line (proved).** Grow only at knots that hold two or more loose
     ends. From one knot this grows exactly the two-way endless chain, whatever choices are made: every unit keeps one open loop,
     and bond distance counts the loops between two distinctions, plus one. The axis goes off to infinity in both directions, grown
     from a single knot by a rule that reads only loose ends.
   - **Closing loose ends freezes or collapses space (proved; census exploratory).**
     - **Bond distance is a boundary.** It is the least boundary of a region connected inside and out, counting seams and the loose
       ends held inside.
     - **Sealing freezes.** A region with no loose ends behind one seam pins that seam, and no knot crosses it. Closing the nearest
       loose ends sealed space into parts frozen apart: no knot for 370 of 374 pairs.
     - **Short boundaries collapse.** Every boundary of a region connected inside and out is a knot. Closing that avoids pins and
       ties left a strip whose bond distance never exceeds 5, at any length.
     - **No closing at all branches.** Random sprouting, and closing loose ends at bond distance six (the face size of a drawing in
       the plane), gave small-world patterns. No rule grew a pattern of dimension two.
   - **The owner's Cartesian plane is a product (proved; exact formula conjectured).** In the product law of two laws, whose allowed
     states are arrays with every column and row allowed, a knot of each axis joined at a corner is a knot. So bond distance is at most
     δx + δy − 1. The product of two chains has no ends, so it is a ruler: taxicab distance, bond balls of order r^2, dimension two
     read from the allowed states. Exactly δx + δy − 1 holds on 855 checked pairs.
   - **Reading.** The chain grows; the owner's plane is the product of chains. Space holds together through loose ends kept inside,
     as along the chain, or through long seams, as on a drawn lattice. Growth that consumes its loose ends freezes or collapses.
     Taxicab distance is not round; whether logic can make round balls is open.
   - **Provenance.** Bonds and bridges are classical (Whitney; Oxley). Product codes and their duals are classical (Elias;
     MacWilliams–Sloane). No source was found for the growth rules' classification, the L-shaped knots or the exact formula.
   - **Next (recommended, awaiting the owner).** Circles from logic (2/3): can bond balls become round? Map the large-scale form of
     bond distance in periodic laws without ends, where polygons are expected, and in random local laws, where roundness could
     appear only as a trend.
     - **The alternatives.** Dimension under products of k chains (1/3); a proof of the exact taxicab formula (1/3).

   **2026-11-07: colour refinement on the native creation map** (`REFINE-READ-20261107-001`).
   - **The planned test was the wrong one.** Colour refinement (1-WL) must give the same colour to knots that a symmetry exchanges, and
     symmetric contradictions exchange whole Fano pieces. It merges knots of two Fano pieces in 87 of 277 contradictions, 14 of the 23
     Fano trees among them, though the twin rule reads every Fano tree.
   - **Native creation fixes the Fano pieces (computed, 277 of 277 contradictions).**
     - **The test.** Pair refinement (folklore 2-WL), on the order-free far sides, never puts a pair within a Fano piece and a pair
       across two Fano pieces in one class.
     - **So** every symmetry of the native creation map maps Fano pieces to Fano pieces, and "same Fano piece" is definable in
       three-variable counting logic in each contradiction.
     - **What does it.** Whether creation occurs alone mixes them in 42 contradictions: the far sides break exactly the symmetries that
       hid the handles.
   - **No uniform rule tried reads every contradiction (computed).**
     - **The counts.** Yes/no twins read 219; native row twins and three refinements of them 234 each.
     - **Where they fail.** Fano pieces meeting one planar piece merge, in 32 of 38 cases as complete twins.
     - **A regularity.** Twin knots of one Fano piece differ at the glue only by whether they create, never by how. Across Fano pieces
       530 of 1,572 twin pairs differ by how.
   - **Reading.**
     - **Native emergence does not hide topology** in any computed contradiction. The handles are determined by native relations; a uniform
       reading is what remains.
     - **In logical terms,** the Fano pieces are definable contradiction by contradiction. Whether one formula serves all
       contradictions is a question of uniform definability.
     - **Doctrine.** Everything is invariant under relabeling knots and re-listing their distinctions.
   - **Provenance.** Weisfeiler–Leman refinement and its equivalence with counting logic (Cai, Fürer, Immerman) are classical. The
     application and the regularity are new here.
   - **Next (taken as `TRISUM-READ-20261107-001`).** Native creation at junction handles (2/3). On HANDLE-COUNT's trisum
     contradictions, does pair refinement show that the native creation map fixes the junctions, where counting hardness lives?
     - **The alternatives.** Uniform definability of the Fano pieces (1/3); a native audit of earlier far-side records (1/3).

   **2026-11-07: junctions in the native creation map** (`TRISUM-READ-20261107-001`).
   - **The question.** HANDLE-COUNT found that counting cost sits at the glue's junctions, where planar pieces meet along squares, and
     REFINE-READ that native creation fixes the Fano pieces. Does native creation also fix the junctions, and do junction knots carry a
     native signature?
   - **Junctions are read, and counted (computed, 18 of 18 contradictions).**
     - **The contradictions.** Plain contradictions from HANDLE-COUNT's trisum generator. Seven small ones trained the reading. Ten
       larger ones (54 to 60 distinctions, up to three junctions) were mapped only after seven statements about them had been frozen.
       One more, with four junctions, was chosen as a stress test before its map was computed.
     - **Fano pieces first.** Yes/no creation reads them: no removal blocks a Fano piece's core knots, and each root is created at by
       exactly its six core knots.
     - **Then junctions.** With the Fano pieces set aside, a junction's two knots are never degenerate, and each is the only removal that
       blocks the other. No other pair is like that.
     - **Pair refinement** of the native map fixes the Fano pieces, the skeleton, the junctions and the leaves.
   - **A control.** Across REFINE-READ's 277 planar-glue contradictions the signature appears once: in design 7, the only one whose
     glue holds a non-planar brace other than Heawood, at that brace's junction.
   - **One frozen statement failed, by a symmetry.** In one three-junction contradiction native creation cannot tell which of a cube
     piece's two knots carries a Fano piece. Its map has a symmetry exchanging them that the contradiction lacks, induced by a symmetry
     of the glue that keeps the signing's switching class but moves the Fano piece.
   - **Reading.**
     - **A junction is a mutual block:** two knots that depend on each other alone. Planar glue never shows it.
     - **Both of HANDLE-COUNT's handles are native.** The Fano pieces, which counting gets for free, and the junctions, which it pays for,
       are read from creation alone, with nothing drawn.
     - **What native creation sees of a signing** may be only its switching class, which is also all that Pfaffian counting uses.
       That is a conjecture from one contradiction.
     - **Doctrine.** Everything is invariant under relabeling knots and re-listing their distinctions.
   - **A side finding.** HANDLE-COUNT's generator depends on Python's hash seed through its Pfaffian signing, so reruns can place the
     Fano pieces differently. HANDLE-COUNT B's stated totals reproduce under two other hash seeds; three to six of its 257
     per-contradiction rows change. Each contradiction used here is reproduced at its seed under a recorded hash seed.
   - **Provenance.** Trisums and trisectors (Robertson, Seymour and Thomas), switching classes (Zaslavsky) and refinement (Weisfeiler
     and Leman; Cai, Fürer and Immerman) are classical. The signature, the held-out test and the hidden symmetry are new here.
   - **Next (taken as `SWITCH-READ-20261108-001`).** Does native creation see the signing only through its switching class (Payoff
     2/3, Concreteness 2/3)? Map a second placement of one contradiction in the same class and compare.
     - **The alternatives.** A proof of the junction signature (2/3, 1/3); one uniform native reading of Fano pieces and junctions
       (1/3, 3/3).

   **2026-11-08: what native creation sees of a signing** (`SWITCH-READ-20261108-001`).
   - **The question.** In the junction epic one frozen statement failed because native creation could not tell two placements of a Fano
     piece apart, placements related by switching the glue's signing. Does native creation see a signing only through its switching
     class?
   - **Placements come for free.** HANDLE-COUNT's generator picks its minimal signing by walking sets, so different hash seeds give 11
     of the 17 trisum glues two or three placements of their Fano pieces: one glue and one switching class, but contradictions that are not
     isomorphic.
   - **No for the whole map, yes between glue knots (computed: five pairs, 38 to 56 distinctions; one size past, all 17 pairs on 11
     glues, to 60 distinctions).**
     - **Between glue knots** native creation is the same in both placements, entry by entry.
     - **Removing a knot of a Fano piece** creates differently at glue knots, so the whole native maps are never isomorphic, with the glue
       held fixed or not.
     - **The junction reading transfers.** The junction epic's seven frozen statements hold on all five other placements, and on
       eight of the nine in the stress test. On the ninth, seed 11's second placement, a symmetry of the glue moves a Fano piece, as in
       the junction epic's seed 5.
   - **Reading.**
     - **Native creation splits in two.** Between glue knots it sees only the switching class, which is also what Pfaffian counting
       sees. Through its Fano pieces it reads where they sit.
     - **Why, as read from earlier results.** An intact Fano piece acts on the glue as one negated incidence, and switching only complements
       distinctions. Removing a knot of a Fano piece frees its incidence, and which incidence is freed is the placement. Not yet proved.
     - **The junction epic's hidden Fano piece** is a placement that a symmetry of the glue moves, so even the Fano-piece removals
       cannot tell its two placements apart. Its record's title said more than that, and is narrowed.
   - **Provenance.** Switching classes of signed graphs (Zaslavsky) are classical. The comparison and the split are new here.
   - **Next (taken as `SWITCH-PROOF-20261108-001`).** Prove that creation between glue knots depends only on the switching class
     (Payoff 2/3, Concreteness 2/3): an intact Fano piece acts as one negation, switching complements distinctions, and the creation
     test should not see complementing.
     - **The alternatives.** The glue block against Pfaffian counting (2/3, 1/3); folding in the nine remaining placements (done:
       the stress test passed).

   **2026-11-08: a theorem on what native creation sees of a signing** (`SWITCH-PROOF-20261108-001`).
   - **Proved.** For every cubic glue, every two signings in one switching class, and every two glue knots, removing one and gluing at
     the other gives the same native creation verdict in the two plain edge-piece systems (a Fano piece on each signed edge of the
     glue), for each far side.
   - **Why.**
     - **An intact Fano piece only negates its incidence.** Its own knots force its three root distinctions to the negation of its glue
       distinction. Its four inner distinctions stay free enough, as an exhaustive check over its 256 assignments shows, that they
       belong to no knot the two-round rule uses.
     - **So creation between glue knots is the signed glue's own creation map.** That held on all 3,500 computed entries.
     - **Switching only complements distinctions,** and complementing distinctions changes no constrained set.
   - **Reading.** Through the glue, native creation reads a signing's switching class, for a bipartite glue the parity of its signs
     around every cycle. Through the Fano pieces it reads where the signs sit. The first is the data Pfaffian counting uses on these
     systems.
   - **Provenance.** Switching classes and balance (Zaslavsky) are classical; the theorem is new here.
   - **Next (taken as `SWITCH-COMPLETE-20261108-001`).** Does the glue block tell every switching class apart (Payoff 2/3,
     Concreteness 3/3)? The smallest glue's 512 classes are computing.
     - **The alternative.** The glue block against Pfaffian counting (2/3, 1/3).

   **2026-11-08: does native creation tell signings apart?** (`SWITCH-COMPLETE-20261108-001`).
   - **The question.** Creation between glue knots depends only on the switching class of the signing. Does it tell every class
     apart?
   - **No, and less so as the glue grows (computed, every class of the 8-knot and the 10-knot trisum glue).**
     - **The smallest glue, nearly.** Its 512 classes give 448 glue blocks, and up to the glue's 24 symmetries all 42 orbits are told
       apart but one pair. That pair's signings differ by moving one sign along a knot, and their signed glues have 40 and 34
       solutions.
     - **One size past, far from it.** The 10-knot glue's 2,048 classes give 1,526 blocks, and 429 on its 576 orbits.
     - **Where nothing creates.** Its largest shared block belongs to the 190 classes at which no far side creates anywhere. They come
       from 66 orbits and have 60 to 110 solutions.
     - **Confirmed.** Colliding pairs have identical glue blocks on their plain systems themselves, and census 6 under every order of
       the gluing knot separates neither.
     - **The contradictory class stands out.** At both sizes the Pfaffian class, whose plain systems are three-regular contradictions,
       is the only class without solutions and has a block of its own.
   - **Reading.**
     - **Creation sees a signing where it creates.** Through the glue it reads the switching class only as far as creation happens;
       through the Fano pieces it reads where the signs sit.
     - **It does not read the count.** Classes with one block differ in their numbers of solutions, the quantity counting computes.
     - **It does read the contradiction.** On both glues the one class that makes the system contradictory is told apart from all others.
     - **The stress test mattered.** The smallest glue suggested near-completeness up to symmetry; one size past overturned that before
       it was published.
   - **Provenance.** Switching classes and the action of automorphisms on them are classical (Zaslavsky); the computations are new here.
   - **Next (taken as `CONTRA-READ-20261108-001`).** Does creation always single out the contradictory class (Payoff 2/3,
     Concreteness 2/3)? Test the five 12-knot glues (corrected from "four", 2026-11-08), following only the classes whose rows
     match the Pfaffian class's.
     - **The alternatives.** Where nothing creates (1/3, 3/3); what of counting creation carries (2/3, 1/3).

   **2026-11-08: native creation reads the contradiction** (`CONTRA-READ-20261108-001`).
   - **The question.** Creation between glue knots does not tell switching classes apart, but on two glues it told the contradictory
     class, the one whose plain systems are three-regular contradictions, from all others. Does it always?
   - **Yes, on every trisum glue of 8 to 12 knots (computed, seven glues).**
     - **One contradictory class.** On each glue exactly one switching class has no solution: the Pfaffian class.
     - **One row is enough.** For every knot a of every one of these glues, creation with a removed, at the other knots, already
       tells the contradictory class's restriction from every other class of the glue without a.
   - **Why.**
     - **The removed knot stays tied.** Every assignment the glue without a allows must break knot a, so a's three distinctions are tied
       there. No other class ties them, since that would give a second contradictory class.
     - **Creation reads the tie.** A knot sharing two distinctions with a cannot then show all six patterns, so gluing there is
       degenerate. At knots that share two distinctions with no other knot, the degenerate gluings alone single the class out; elsewhere
       the knots that far sides add finish it.
   - **Reading.** Native creation reads where the contradiction lives: with any one knot removed, creation at the other knots tells
     whether restoring it closes a contradiction. With the entry above, it reads the contradiction but not the count. (Narrowed
     2026-11-08: on glues whose incidence graph is 3-connected; at knots in a two-vertex cut one row can fail, as the next entry
     shows.)
   - **Provenance.** Switching classes (Zaslavsky) and Pfaffian orientations (Kasteleyn) are classical; the recognition and its
     mechanism are new here.
   - **Next (taken as `CONTRA-PROOF-20261108-001`).** Prove that one row reads the removed knot's tie (Payoff 2/3, Concreteness
     2/3).
     - **The alternatives.** Why there is one contradictory class (2/3, 1/3); the 14-knot glues (1/3, 3/3).

   **2026-11-08: where one row reads the contradiction** (`CONTRA-PROOF-20261108-001`).
   - **The question.** On the trisum glues one row of creation reads the removed knot's tie. Is that so on every glue, and why?
   - **Not on every glue (computed, 19 random cubic glues of 8 to 10 knots with a class without solutions).**
     - **Where it fails.** Exactly at the knots lying in a two-vertex cut of the glue's incidence graph: 16 knots, two on each of the
       8 glues with such cuts. Removing one of the two cut knots leaves a rigid side, K4^(3) without a knot, and nothing creates
       anywhere in the row, in the contradictory class or in another.
     - **Where it holds.** On every 3-connected glue tested: the 11 random ones and the seven trisum glues.
     - **No local shortcut.** Under the tie, the K4^(3) far side stays silent at knots meeting the removed knot once on 25 of the 26
       glues, but not on a 12-knot trisum glue where one row still reads the tie. No single near distinction makes K4^(3) create, and
       distinctions tied to the removed knot are never witnesses (an exhaustive local lemma).
   - **Reading.** Native creation reads the contradiction where the glue cannot be cut at two vertices; a two-vertex cut hides it. The
     previous entry's reading is narrowed accordingly.
   - **Provenance.** Two-vertex cuts and connectivity are classical; the counterexamples, the refined conjecture and the lemma are new
     here.
   - **Next (taken as `CUT-HIDE-20261108-001`).** Why two-vertex cuts hide the tie (Payoff 2/3, Concreteness 2/3): the side K4^(3)
     without a knot, hanging from one distinction once a cut knot is removed, under its eight cycle signings.
     - **The alternatives.** The refined conjecture for 3-connected glues (2/3, 1/3); random 3-connected glues one size past (1/3, 3/3).

   **2026-11-08: why two-vertex cuts hide the contradiction** (`CUT-HIDE-20261108-001`).
   - **Proved.** At a two-knot cut whose side meeting the removed knot once is K4^(3) without a knot, the contradictory class and the
     class with one sign of the other cut knot changed have the same row of creation, and only the first ties the removed knot's
     distinctions.
   - **Why.** That side has one rigid switching class of its eight, and the contradiction must use it. One sign on the other cut knot
     then decides whether the side is coupled to the rest or free, and creation is blind to it: the side's knots are degenerate either
     way, and its distinctions add nothing the cut knot's third distinction does not (six local lemmas, exhaustive).
   - **Reading.** The obstruction found by CONTRA-PROOF is structural: native creation cannot read the contradiction across such a cut.
   - **Next.** Work paused at the owner's request (2026-11-08). Open: a proof for 3-connected glues; the six-distinction hanging sides.

   **Words in the circle and sphere entries.** The circle entries read bond balls of laws placed on drawn layouts (periodic plane
   graphs, arrangements of lines, random tessellations), so their circles, polygons, planes and directions are drawings of those
   balls. In the sphere entries a law declares its knots and its co-lines, cycles of distinctions through which every co-knotted pair
   runs once; knots and co-lines together are a drawn knot pattern that the law supplies itself, and its spheres, tubes, digons,
   corners, discs and flat or round parts belong to the literature's drawing of it. Before 2026-11-11 these entries called the knots
   lines and the distinctions points; the earlier text is in git history.

   **2026-11-07: circles from logic** (`LOGIC-CIRCLE-20261107-001`).
   - **The question.** Do round balls exist among the bond balls of laws on drawn layouts, perhaps only as large-scale trends, and
     does roundness differ in kind from polygons?
     - **A circle** is a bond ball.
     - **Its π** is Gołąb's: half its perimeter measured with its own distance. It is 3.14159… when the circle is round, and between
       3 and 4 for every norm on the plane, with 3 only for hexagons and 4 only for parallelograms.
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
     - **No plane.** A law on a uniformly random planar map, with nothing drawn in advance, does not read as a plane at all. Its bond
       distance grows like n^0.28,
       near the Brownian map's n^(1/4), dimension 4.
   - **Reading.**
     - **Harmonies.** A periodic circle closes after finitely many sides, with a ratio of whole numbers: a harmony. The hexagonal
       layouts, built from three directions, have π = 3: the circumference is exactly three diameters.
     - **A ratio that continues.** The round circle's π never stops. Logic reaches it only through infinitely many directions, or
       through chance with no preferred direction.
     - **Lines are "shapes", in the owner's word.** Every circle here is assembled from drawn lines: straight segments, and with
       coins, arcs that are graphs of functions.
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
   - **The setting.** A law of knots and co-lines supplies its own closed pattern, which the literature draws as a closed surface,
     with nothing drawn in advance: distinctions, knots (triples) and co-lines (cycles), each pair of a knot's distinctions lying in
     exactly one co-line.
     - **The count reads it.** The knot's count (`COUNT-SURFACES-20261107-001`) reads that pattern's Euler characteristic.
       - It forces a violated knot only on a sphere whose co-lines all close under the signs.
       - Negative curvature forces an over-agreeing face instead, and finding it is PPADS-complete, as finding the sphere's violated
         knot is (`COUNT-ANTIVORTEX-20261107-001`).
   - **Uniform laws close into few spheres (proved).**
     - **The formula.** With every distinction alike, of co-line sizes (d1, d2, d3), χ = n(1/d1 + 1/d2 + 1/d3 − 1).
     - **The spheres.** A sphere arises only as an antiprism (2,2,d) or a snub polyhedron of 12, 24 or 60 distinctions; each is
       realized by a law on a group (dihedral, A4, S4, A5).
     - **Otherwise.** The laws are flat, (3,3,3), (2,4,4), (2,3,6), or hyperbolic, such as the Klein quartic's law on PSL(2,7).
   - **Uniform signs never force the contradiction (proved).**
     - **Why.** Positive curvature sits on digons, two knots sharing two distinctions. Under uniform signs every digon stays open, so the
       count never forces a knot to fail on any uniform law.
     - **With non-uniform signs.** Signs that close the digons make the knot fail only on those small spheres or on antiprisms, which
       are chains solved by binary search.
   - **Computed.**
     - **Uniform signs.** The knot is satisfiable on every tested uniform law, and on all circulant laws with n ≤ 48 except the Fano
       plane. The Fano pattern's contradiction is not the count's.
     - **The knot sphere** has exactly two kinds of distinctions.
   - **Reading.** A law that treats every distinction alike can grow flat patterns without end, and negatively curved ones, in the
     literature's words, but not a large sphere. The knot's deep contradiction marks where a law stops treating its distinctions alike:
     two kinds of distinctions and a sign defect at each of six digons.
   - **Provenance.** Vertex-transitive and Cayley maps and the spherical list (antiprisms, snub polyhedra) are classical. The reading of a
     law as a self-built surface, and the bound on uniform contradictions, are new here.
   - **Next (both taken).** Two kinds of distinctions (2/3): which such laws close into large spheres, and can a local
     growth rule place the six digons itself, so that a law grows its own sphere and with it the knot's contradiction?
     - **The alternative.** Large uniform contradictions beyond the Fano plane (1/3).

   **2026-11-07: the only uniform contradiction** (`UNIFORM-FANO-20261107-001`).
   - **Proved.**
     - **Sign patterns.** With non-constant uniform signs the all-zero assignment satisfies every knot, so only equal signs matter: a
       plain 2-colouring.
     - **The brace lemma.** If a law's symmetries are transitive on its distinctions and on its knots, its incidence graph is a brace.
       Two translates of a smallest tight shore share at most one distinction, and counting forces a shore too small to hold a knot.
     - **The conclusion.** By Seymour's dictionary and McCuaig's theorem, the Fano pattern is the only uniform law whose knot
       contradicts itself. 439 Cayley laws agree.
   - **Reading.** Uniform patterns are coherent with one exception, a single handle in the literature's drawing. Every other
     contradiction of the knot, its hardness included, needs a law that treats its distinctions differently.
   - **Next (taken at once, the owner's (i), as `SPHERE-GROWTH-20261107-001`).** How a law can treat its distinctions differently by
     itself. Rated
     Payoff 3/3 (Barrier), Concreteness 1/3 (Stated), so the first step is scoping.

   **2026-11-07: a law that lays out its own round sphere** (`SPHERE-GROWTH-20261107-001`).
   - **The question.** Can a local law place the six digons itself, so that a law grows its own sphere and with it the knot's
     contradiction, with nothing drawn?
   - **Without hidden states, no (proved).**
     - **Tubes look round up close.** A law of radius r cannot tell the octahedral knot sphere K_m (m ≥ 2r + 1) from a long capped tube:
       every ball of the tube already occurs in K_m.
     - **Tubes are easy.** The tube's knot still contradicts itself, but resolution refutes it in width O(m) at every length. So such a
       law cannot force the hard contradiction.
   - **With one hidden bit per incidence, yes (proved).**
     - **The seam law.** Mark each incidence as a seam or not. All four incidences of a digon are seams, and a co-line of three
       distinctions has no seam or one opposite pair, so seams run straight.
     - **What it forces.** The seams cut the sphere into eight equal equilateral triangles forming an octahedron (Gauss–Bonnet on each
       flat face). So a two-kind sphere has a marking exactly when it is K_m, and K_m has one marking.
     - **The contradiction.** Every sphere of the law carries a contradiction that needs resolution width Θ(√n) and size 2^Θ(√n).
   - **Growth.** A growth law without branching grows at most one closed surface, so growing every size needs branching; the seam law
     leaves only the size free. Random local growth closed 60 spheres in 711 tries, and the only round ones were octahedra.
   - **Reading.** The seams are straight lines the law draws for itself, a native ruler, and roundness is those rulers closing up into
     equal triangles. With one witness bit per incidence, quantified away, a uniform local law lays out its own round sphere (a closed
     pattern supplied by the law alone, nothing drawn in advance).
   - **Provenance.** Local views and locally checkable proofs (Göös–Suomela), decorated matching rules (Goodman-Strauss) and flat cone
     spheres (Thurston) are classical. The seam law's characterization of the knot spheres is new as far as found.
   - **Next (taken as `GROW-COIN-20261107-001`).** Grow K_m by a local process, ring by ring from a digon with the seams as signals.
     Rated Payoff 2/3 (Substantial), Concreteness 2/3 (Testable).
     - **The alternatives.** Seams as a native knot (Payoff 2/3, Concreteness 1/3); other round families, the Goldberg–Coxeter
       octahedra (1/3, 2/3); a write-up (1/3, 3/3).
     - **Provenance, added.** In the words of symbolic dynamics, the round knot spheres are sofic (one bit) but not of finite type
       (Mozes 1989; Goodman-Strauss 1998; Fernique–Ollinger 2010).

   **2026-11-07: a growing law needs a shared coin** (`GROW-COIN-20261107-001`).
   - **The question.** A finished sphere cannot be checked as round without a hidden bit on every incidence. Can a growing law do
     without it? No scheduler may supply an input, so a result must hold in every growth order.
   - **Refinement keeps the shape (proved).** Subdividing every triangle of K_m gives K_{2m} or K_{3m}. A split edge forces both its
     triangles to split, so a step is all-or-nothing in every order. A tube refines to a tube: refinement keeps whatever shape the seed
     has and never places a corner.
   - **Accretion must place corners.**
     - **Proved.** Growing annuli around a corner gives K_m exactly when the four turns of one ring become corners together.
     - **Computed.** With turns decided one at a time, the growth also closes lopsided spheres: 38 distinct closures up to 100
       triangles, 3 round, and 12 of 400 random-coin runs non-round, up to 646 triangles.
     - **Proved, windows computed.** Growing one annulus at a time, a turn is decided at a window that is the same in every lap. So a
       label-free rule cannot tie the four equator corners together. One bit kept for one lap does, but that bit is history kept by the
       process: a hidden witness, like the seam bits.
   - **Reading.** Growth does not remove the witness. A law can grow space that is already round by refining it, with nothing
     hidden. To lay out a new round sphere it needs a witness, whether the sphere is checked when finished or grown corner by corner.
   - **Provenance.** Local growth rules that stall without non-local information (Onoda, Steinhardt, DiVincenzo and Socolar 1988),
     capsids assembled by local rules with conformational states (Berger, Shor et al. 1994), and tile complexity in self-assembly are
     classical. The contrast for the knot spheres is new as far as found.
   - **Next (taken as `HARD-FLAT-20261107-001`).** Hardness without roundness: does the knot's contradiction stay hard on spheres whose
     corners are merely far apart? Grown lopsided spheres have elimination width 1.0 to 1.9 √n, against 2.1 √n on K_m (upper bounds
     only). Rated Payoff 2/3 (Substantial), Concreteness 2/3 (Testable).
     - **The alternatives.** A theorem for every accretion law (2/3, 2/3); the fewest hidden bits that single out K_m (1/3, 2/3).

   **2026-11-07: hardness needs a flat disc, not roundness** (`HARD-FLAT-20261107-001`).
   - **The question.** Does the knot's hard contradiction need the round knot sphere, or only corners kept far apart?
   - **Proved.**
     - **Flat states everywhere.** On every two-kind sphere the frames have label holonomy −1 at each of the six corners and are flat
       elsewhere. So a flat state with one violated knot exists, as on the knot sphere.
     - **The Sperner reduction needs only a flat disc.** Sperner's lemma sits inside any corner-free lattice triangle whose boundary
       reaches the corners by disjoint cut paths. So the knot needs resolution width at least a constant times the radius of the
       largest such flat disc, and at most O(√n).
   - **Computed.** Lopsided spheres grown with local coins have flat discs of radius 0.14 to 0.35 √n, against 0.25 √n on the knot
     sphere (8 spheres up to 252 distinctions). On a thin tube the largest disc reaches around the band.
   - **Reading.** Roundness costs a witness, but hardness, as far as resolution width shows, does not. The hard part of the knot's
     contradiction lives in a flat region far from every corner, where Sperner's lemma sits.
   - **Next (paused).** The owner asked to wrap up open lines. The sphere line stops here. When it reopens, candidates are whether
     grown spheres stay fat, and whether resolution size also follows the flat radius.

   **Words in the pinwheel entries.** The pinwheel entries work with Radin's pinwheel tiling, a classical tiling of the drawn plane
   by right triangles, and with periodic tilings of the drawn plane, with knots placed on the tiles: their tiles, patches, collars,
   crystals, lattices, planes and circles are the literature's and the drawing's (reworded on 2026-11-11; the earlier text is in git
   history).

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
       polygon layout; 1:2 continues and becomes round.
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
     - **Where the angle went.** Into the law's large-scale outline, not into any finite part of it.
       - **Not in the counts.** The eight kinds recur in rational proportions, per knot: a 3/11, b 5/22, c 16/55, d 3/55, e 6/55,
         f 1/5, g 17/55, h 27/110.
       - **The only irrational number.** The table's growth rate √5, which is the length scale.
       - **In the limit.** The combinatorics alone recover the triangles (Kenyon and Stephenson). Drawn conformally, which fixes
         the picture up to similarity, clusters of tiles converge in outline to the 1:2:√5 triangles. So the angle, like the round
         circle, is a limit property of the law.
       - **Corrected 2026-11-08.** This bullet first said that the angle appears only if the grown law is drawn in the plane.
   - **Provenance.**
     - **Known in substance.** A coordinate-free pinwheel rule with four-cornered tiles, the fourth corner at the long leg's
       midpoint, and the return of its geometry: Kenyon and Stephenson (Proc. Amer. Math. Soc. 147, 2019).
     - **Classical.** Finite combinatorial descriptions of substitution tilings (collared tiles, Anderson–Putnam complexes; for the
       pinwheel, Barge–Diamond–Hunton–Sadun and Frettlöh–Whitehead–Whittaker) and Whitney's theorems.
     - **Not found.** The radius-2 readability, and the rule's form on knots and distinctions.
     - **Corrected 2026-11-08.** The rule and the census were first listed as not found.
   - **Next (taken in part by `PINWHEEL-ATLAS-20261107-001`: the atlas and the periodic check; outward growth held).** A round
     plane grown at its open ends (Payoff 3/3, Concreteness 2/3), starting with
     atlas growth. From one knot, add knots only where every nearby distinction keeps a radius-2 neighbourhood of the pinwheel's
     atlas. Does growth reach dead ends, or grow pinwheel patches outward as the number line grew?
     - **The alternatives.** Prove radius 2 for every pinwheel tiling; the spectrum of rational π among periodic laws.

   **2026-11-07: the pinwheel's own law** (`PINWHEEL-ATLAS-20261107-001`).
   - **The question.** What is the pinwheel's own local law? Does it force a round plane, and can regrowth drop its labels? This is
     the plane's side of the question shared with the sphere line: how much hidden information does roundness cost?
   - **A finite law that reads itself (proved).**
     - **The closure.** Take each tile with every tile touching it. Over all pinwheel patches these form 193 kinds, closed under the
       cut; 108 are complete.
     - **The atlas.** On every pinwheel tiling, the radius-2 neighbourhoods of darts take exactly 1,168 forms, and each fixes its
       edge's label. At radius 1 there are 198 forms, 9 of them ambiguous.
     - **So regrowth reads only the map.** The eleven-label rule can run on the bare map: inside by theorem, and at the boundary of
       the growing patch at radius 2 on levels 4–7 (measured).
   - **Periodic planes fail (measured).**
     - **The test.** None of 96,474 periodic configurations obeys the law, even at radius 1: rectangle grids, brick rows, every
       domino tiling of small tori with every diagonal choice, and the six two-tile figures tiled by half-turns.
     - **The frame-consistent cut** fails too. It is neither periodic nor round.
   - **Reading.**
     - **Unlike the sphere.** On the sphere, a law without hidden states cannot tell a round sphere from a tube
       (`SPHERE-GROWTH-20261107-001`). In the plane, the pinwheel's own law rejects every tested non-round plane outright.
     - **Corrected 2026-11-08 (narrowing).** The contrast does not hold. Cut once, one of the tested planes, the rhombus lattice,
       obeys the collar law, and cut twice the radius-2 law; no undecorated local law of the pinwheel forces roundness
       (`COLLAR-PLANE-20261108-001`, next entry; `docs/CORRECTIONS.md`).
     - **Why.** Its vertices are mostly T-junctions at long-leg midpoints, which crystalline arrangements of the same triangle do not
       make in the allowed combinations.
     - **The shared question.** For regrowth, roundness costs no hidden information beyond the patch's outline at radius 2. Whether the
       law forces roundness is open.
   - **Provenance.**
     - **Known.** Collared tiles (Anderson–Putnam); the combinatorial rule (Kenyon–Stephenson); undecorated local rules (Levitov,
       Socolar); decorated matching rules (Mozes, Goodman-Strauss, and Radin for the pinwheel).
     - **Not found.** The atlas, the readability theorem and the periodic test.
   - **Next (held, at the owner's request to wrap up current lines).**
     - **Forcing.** Whether the undecorated law forces aperiodicity: a torus search over the law's own vertex stars (Payoff 2/3,
       Concreteness 2/3). Answered by `COLLAR-PLANE-20261108-001`: it does not, at any radius.
     - **Growth.** Outward growth in every growth order (Payoff 2/3, Concreteness 1/3).
     - **The boundary.** Radius 2 at the boundary as a theorem (Payoff 1/3, Concreteness 3/3).

   **2026-11-08: a periodic plane obeys the pinwheel's local laws** (`COLLAR-PLANE-20261108-001`).
   - **The question.** Outward growth by the pinwheel's collar law (one tile around each tile) left the pinwheel. Does a periodic
     plane obey that law? If none did, the plane would need no hidden information for roundness, unlike the sphere.
   - **A crystal passes (proved).**
     - **The witness.** Four tiles around a common right angle make a rhombus. Tile the plane with these rhombi by translation and
       cut once: every tile's collar is one of the pinwheel's 108, with 20 tiles in each period.
     - **Every radius.** The cut keeps the law, and each further cut hides the crystal's seams one level deeper. So for every radius
       a periodic plane obeys the pinwheel's undecorated law of that radius: the 1,168-form radius-2 law after two cuts, the
       radius-3 law after three (stress test).
     - **So.** No undecorated local law of the pinwheel forces aperiodicity, or roundness: the crystal's circles are polygons
       (`LOGIC-CIRCLE-20261107-001`). Radin's decorations are hidden information.
   - **One level is forced (proved).** Each collar names its tile's parent, and touching siblings agree, so every plane that obeys
     the collar law is the cut of a plane of larger triangles. Their collars obey a weaker level-one law: 1,264 collars, 54 of them
     the pinwheel's. The crystal escapes there: it is the cut of the rhombus lattice, whose collar passes the level-one law.
   - **The census (exploratory).** Of the atlas epic's periodic planes, cut one to three times, the rhombus lattice and, on the 4 × 4
     torus, 16 brick-row planes with diagonals of period 4 pass after one cut; six brick-row planes join after two. Growth's
     off-pinwheel patches compose once, and their defect is one level up. (Corrected 2026-11-08: first published as "only the
     rhombus lattice passes after one cut", before the larger tori were run.)
   - **Reading.**
     - **The plane is like the sphere.** On the sphere a law without hidden states cannot tell a round sphere from a capped tube; in
       the plane the pinwheel's own laws, without decorations, cannot tell the pinwheel from a crystal. Roundness costs hidden
       information in both (A25, confirmed for the pinwheel).
     - **Growth.** The collar law is not an aperiodic set, so the deceptions theorem of Dworkin and Shieh does not explain growth's
       dead ends (a correction to the growth-law entry under question 4).
   - **Provenance.** Known: decorated matching rules (Radin 1994; Mozes; Goodman-Strauss 1998), the question of undecorated local
     rules (Levitov 1988), recognizability (Solomyak 1998), and cutting a crystal to defeat local rules as a method. Not found: the
     pinwheel's witness and conclusion, the forced first level and the level-one law.
   - **Next (taken).** The price of roundness in the plane (next entry). Its first step as written, child indices as labels, was
     dropped once Lemma 1 there showed that labels read from the tiling add nothing
     ([decision note](../research/COLLAR-PLANE-20261108-001/collar_plane.md)).

   **2026-11-08: the price of roundness in the plane** (`ROUND-PRICE-20261108-001`).
   - **The question.** No undecorated law of the pinwheel forces roundness. How much hidden information does? Start with one bit per
     tile, set the way every known decoration sets it: Conway's cut gives each child a label fixed by its parent's label and its
     position among the five children.
   - **Labels read from the tiling add nothing (proved).** If a label is a function of a bounded window, the cut crystal, labelled
     the same way, obeys the labelled law at every radius. Child indices, and any finite part of a tile's address in the hierarchy,
     are such labels. A forcing label must carry information no window determines.
   - **One bit mostly fails (proved, exact census).** Of the 1,024 ways to set one bit, 1,008 still let a crystal through, at every
     radius: the cut rhombus lattice, the cut brick rows, or brick rows with period-4 diagonals, each with a periodic labelling.
   - **Sixteen remain (proved, exact).** In these the bit already forces every parent's label. They would force the pinwheel if every
     labelled parent collar that survives a consistency test obeyed the law again; the pairwise test leaves some that do not, so the
     question is open.
   - **Reading.** On spheres one hidden bit per incidence forces roundness. In the plane one bit per tile is not excluded, and for
     most ways of placing it, it fails. In all sixteen survivors, the corner children (at the parent's corners Q and P) carry the bit
     that remembers the parent.
   - **Provenance.** Known: decorated matching rules (Radin 1994; Mozes 1989; Goodman-Strauss 1998), small aperiodic sets (Jeandel
     and Rao 2021). Not found: the census and the forcing test.
   - **Next (taken).** Settle the sixteen (next entry) ([decision note](../research/ROUND-PRICE-20261108-001/round_price.md)).

   **2026-11-08: one hidden bit per tile** (`ONE-BIT-20261108-001`).
   - **The question.** Settle the sixteen one-bit decorations left open: a joint consistency test, which would prove that a
     decoration forces the pinwheel, then a search for crystals that escape.
   - **The joint test settles none (proved).** It is sound, but for each decoration it leaves labelled parent collars outside the
     law, most of them pinwheel collars with labels the decoration never produces.
   - **Fourteen escape (exploratory).** Among all domino tilings of tori up to 4 × 4, 176 are legal after two cuts. A mixed tiling of
     the 4 × 4 torus, with dominoes in both directions, admits most of the open decorations with periodic labels after two to four
     cuts. So one bit per tile, placed this way, lets a crystal through in 1,022 of the 1,024 cases.
   - **One remains.** s(0) = 1 0 1 0 1, s(1) = 0 0 1 1 0 (and its relabelling) resists every crystal tried. If it forces the
     pinwheel, the plane's price of roundness is one bit per tile, as the sphere's is one bit per incidence.
   - **A note** for outside readers, "The pinwheel tilings have no undecorated local rules", is in knotlab's notes with an
     independent replay.
   - **Next (taken).** The last decoration (next entry) ([decision note](../research/ONE-BIT-20261108-001/one_bit.md)).

   **2026-11-08: the last one-bit decoration** (`LAST-BIT-20261108-001`).
   - **The question.** Does s(0) = 1 0 1 0 1, s(1) = 0 0 1 1 0 force the pinwheel? It is the only one-bit decoration no crystal has
     escaped, and its parent labels are forced.
   - **No deeper domino crystals (exploratory).** In the whole domino-torus family no collar needs exactly three cuts to become a
     pinwheel collar: its crystals are legal after one or two cuts or never. So that family is exhausted for this decoration.
   - **The forcing proof stalls (proved).** If every labelled parent collar obeyed the law, a level-by-level argument would prove the
     plane is a pinwheel tiling. But 153 labelled parent collars that are not pinwheel collars survive a joint consistency test and
     exhaustive extension two tiles out at the parent level, and most survive three; 50 pinwheel collars with labels the law does
     not list survive the joint test and were not tested further (corrected 2026-11-08: the entry first asked only for pinwheel
     collars).
   - **Reading.** The question is still open, now sharply posed: either some plane obeys the law while its parents break it,
     probably a crystal outside the domino family, or all those off-law parents die further out and one bit per tile forces the
     pinwheel.
   - **Next (taken).** A crystal built from the surviving parent collars (next entry)
     ([decision note](../research/LAST-BIT-20261108-001/last_bit.md)).

   **2026-11-08: one bit per tile never forces the pinwheel** (`CRYSTAL-UP-20261108-001`).
   - **The question.** Build a crystal one level up for the last decoration, 10101 / 00110: a periodic parent tiling whose labelled
     collars all lie among the parent collars that survived every local test, some of them not pinwheel collars.
   - **It exists (exploratory, then proved).** Growing tori from those collars, on lattices spanned by periods seen in their own
     patches, completes 26 periodic parent tilings of 8 to 40 tiles per period. In each, half the tiles are turned by arctan(4/3),
     twice the pinwheel's angle, from the other half. Their collars include some that are not pinwheel collars, and one cut later
     every labelled collar is the decorated pinwheel's. Independent code checks them, and one escape for each of the other seven
     open classes.
   - **So all 1,024 one-bit decorations fail.** Each lets a periodic plane through at every radius: one hidden bit per tile, placed
     by a decorated substitution, never forces the pinwheel.
   - **Reading.** The price of roundness in the plane is more than one bit per tile, counted as labels a decorated substitution sets.
     The earlier crystals hid their seams in domino tilings; these hide them where two orientations meet, which one cut turns into
     pinwheel collars. A correction rode along: the forcing route of the previous entry needed every off-law parent collar to die,
     not only the non-pinwheel ones (not a block).
   - **Next (taken).** G1's measure itself: is bond distance the only native spacing (next entry)? Two bits per tile and edge
     labels stay in the backlog ([decision note](../research/CRYSTAL-UP-20261108-001/crystal_up.md)).

   **2026-11-08: chains of knots and bond distance** (`BOND-CHAIN-20261108-001`).
   - **The question.** Bond distance, the least bond through two distinctions minus one, has measured every law read for space since
     2026-11-07 (A12). Another measure reads only knots: the shortest chain of knots, each sharing a distinction with the next. Do
     they agree?
   - **On parity laws they do (proved).** A chain of knots always holds a knot through its two ends, by matroid connectivity. So
     counted in knots every joined pair is one step apart (no spacing at all), and counted in distinctions a chain gives back bond
     distance exactly.
   - **Elsewhere they part exactly at gates (proved, exhaustive).** A gate is a shared distinction one value of which satisfies both
     knots it joins. Of the 1,156 laws made of two three-place knots sharing a distinction, a knot joins the far ends exactly when
     the knots do not meet at a gate. A chain of single clauses is spanned by a knot exactly when its clauses chain as implications.
   - **A law only chains see as an endless chain.** The NAND chain, clauses not(s(t−1) ∧ a(t) ∧ s(t)), has no knot beyond its
     clauses, so bond distance sees separate clauses where chain distance counts one step per clause, as along an endless chain. The
     atom chain, the same clauses with the signs of an implication, counts one step per clause for both.
   - **Reading.** By the test frozen before the run, A12 is overturned as a universal statement. The foundation decides between the
     measures: two independent relations on A and k and on B and k make k a common hub, not one touch between A and B. At a gate no
     knot crosses k, and bond distance follows that rule.
     A39 replaces A12 on those terms, and every law measured for space composes, so no result changes.
   - **Next (taken).** Two bits per tile, products of one-bit decorations first (next entry)
     ([decision note](../research/BOND-CHAIN-20261108-001/bond_chain.md)).

   **2026-11-08: two bits per tile, as products** (`TWO-BIT-20261108-001`).
   - **The question.** One hidden bit per tile never forces the pinwheel. Can two? Start with products: a tile carries two bits,
     each passed to the children by its own one-bit decoration.
   - **Most fail (exploratory).** Of the 139,656 classes of products, 136,415 let a known crystal through with a periodic two-bit
     labelling, so they fail at every radius.
   - **No crystal tried gets through 3,241.** In 646 the two bits want different crystals; in 2,595 they share crystals but cannot be
     laid on them together. A second bit can thus shut out every crystal found so far, which one bit never could.
   - **The forcing route stalls on a sample (exploratory).** On 12 of them drawn at random, every parent's labels are forced, but
     local consistency leaves off-law parents in all 12, and bounded torus searches from them found no crystal. One product keeps
     only label defects: no non-pinwheel parent survives.
   - **Reading.** These are candidates, not results: the last one-bit decoration also resisted every crystal tried until a new
     kind turned up one level up. The stop rule, frozen at the start, pauses the line here.
   - **Next (parked).** The forcing route on the product that keeps only label defects, 01101/10001 x 10001/00010, with edge
     labels and hub chains, all in the backlog ([decision note](../research/TWO-BIT-20261108-001/two_bit.md)).

   **2026-11-10: the board as distinctions** (`BOARD-DIST-20261110-001`).
   - **The question.** In every law measured for space the board comes first (A51). The owner asked whether the axes themselves can
     follow rules, governed by an essentially infinite CNF. Here "these two names are one cell" is a distinction of the same CNF as
     the values: names are the words in x, y and their inverses, and the board's own rules say only that naming one cell is an
     equivalence, that it passes to neighbours, and that one cell has one value.
   - **Boards are subgroups (proved, classical).** The boards are exactly the Schreier graphs of the subgroups of the free group: the
     tree, the commuting board (when xy and yx are one cell; the literature's ℤ², drawn as the plane), the boards drawn as lines and
     tori, the collapse, and every other.
   - **No law that declares no cycle chooses the commuting board (proved).** Suppose a law's clauses relate names only at the same
     offset: they say which names are one cell, never that a word comes back. If such a law allows an infinite board, it allows the
     tree. Far from the finitely many cells whose views are unique, every view repeats, and compactness unfolds the board into the tree.
     Such laws can force finite boards, and identity of indiscernibles always makes the board finite.
   - **One declared cycle suffices (proved).** The commutator rule, the commuting cycle declared at every name, with an aperiodic tile
     law forces exactly the commuting board.
   - **Frozen at infinity (proved).** Two boards differ in infinitely many identity distinctions, and off the tree every cell holds
     infinitely many names, so under the source-aware reading no knot involving the board is native.
   - **The census (computed, exact, frozen).**
     - **The predictions.** All 1,024 Life-like one-bit laws obey them with no violation.
     - **What the laws allow.** 768 allow every board, 31 none, and 225 the tree without every board.
     - **Identity boards.** At radius 1 they are finite, and an abelian one like the commuting board always has a non-abelian
       sibling.
     - **The values can forbid a commuting cycle.** In 60 laws the commuting cycle's identity distinction is knotted with the values
       at 1 and xyX, which the cycle makes neighbours; in 56 of them the knot is a single clause of three.
   - **Reading.** "Shapes" have rules, in the owner's words, and here the commuting board's rule is one declared cycle: a law chooses
     the commuting board exactly when it declares the commuting cycle. The
     board a relation-free law always leaves open is the tree, whose balls grow exponentially.
   - **Next (selected).** Leibniz boards: identity of indiscernibles in the limit, beyond the theorem's reach (sub-goal B111)
     ([decision note](../research/BOARD-DIST-20261110-001/board_dist.md)).

   **2026-11-10: Leibniz boards** (`LEIBNIZ-BOARDS-20261110-001`).
   - **The question.** The board theorem needs finitary clauses. Leibniz's rule in full, "names whose views agree at every radius are
     one cell", is one infinitary rule it does not reach. Under it a law's boards are the Schreier graphs of its solutions'
     stabilizers.
   - **Not every board is the tree or finite (proved).** A three-value horofunction law has the board of a 3-cycle with trees
     attached.
   - **Free choices bring the tree back (proved).** A periodic solution with a free choice gives, by independent choices on disjoint
     half-trees, a solution with trivial stabilizer (the tree) and one with an infinite cyclic stabilizer.
   - **The census (computed, exact, frozen).** Every one-bit Life-like law and the atom has no solution (31), finitely many (97) or a
     periodic solution with a free choice (896, and the atom). So Leibniz's rule never forces the commuting board in the family,
     though 891 laws allow it.
   - **Reduced, not proved.** For arbitrary finite alphabets the dichotomy, an infinite board brings the tree, comes down to excluding
     one rigid kind of solution, with its freedom along a single end. The line pauses by its stop rule.
   - **Next (selected).** Rigid finite boards at radius 2 (`BOARD-DIST-20261110-001` direction 2)
     ([decision note](../research/LEIBNIZ-BOARDS-20261110-001/leibniz_boards.md)).

   **2026-11-10: rigid boards at radius 2** (`RIGID-WORLDS-20261110-001`).
   - **The question.** Finite boards can be forced. With identity at radius 2 (names whose radius-2 views agree are one cell), does
     a one-bit Life-like law force every board to be a finite quotient of the commuting board of dimension two (the literature's
     torus), one whose radius-2 balls are the commuting board's?
   - **No law of the family does (computed, exact, frozen).** Of the 994 laws with any board, 769 allow the one-cell board, 223 a thin
     abelian board with at most 8 cells, and two counting laws a non-abelian board with 7 cells; 31 allow none.
   - **Forcing is visible when it happens.** A law that lists the views of one 13-cell such board forces exactly that board, at one
     size. That law draws the board in advance.
   - **Bounded anyway.** At radius 2 a forced such board has at most 256 cells, so a growing family would need a growing radius.
   - **Next (proposed for the morning).** Weakly aperiodic laws under Leibniz's rule
     ([decision note](../research/RIGID-WORLDS-20261110-001/rigid_worlds.md)).

   **2026-11-10: weakly aperiodic laws under Leibniz's rule** (`WEAK-APER-20261110-001`).
   - **The question.** Under Leibniz's rule an infinite board brings the tree for every one-bit Life-like law. Only a law with
     solutions but no finite board could break this. Does such a law still have a solution that repeats nowhere?
   - **Every infinite law does (proved).** Every law with infinitely many solutions on the tree of names, over any finite alphabet
     and with rules of any finite reach, has a solution that no element of the group fixes.
     - Free choices in infinitely many disjoint branches can be made independently, so that nothing repeats.
     - Otherwise the freedom runs toward a few ends in each solution. Over all solutions those ends are every end of the tree,
       including ends no element fixes.
   - **So the identity rule in the limit never forces the commuting board (proved).** The tree is a board exactly when a law has infinitely
     many solutions.
   - **No finite board means a drift (proved after the census).** A three-value level law has solutions but no finite board exactly
     when every cell climbs on balance, with more neighbours one level up than down, or every cell descends. On a finite board
     the steps up and down cancel.
   - **The census (computed, exact, frozen).** Of the 32,768 level laws on three values, 96 have no finite board: 48 drift up and
     48 down. The frozen certificates left 10 laws undecided, mirror images of certified ones, and the mirrored horofunction settles
     them.
   - **Next (selected).** Abstract names: cells named without letters (A54) ([decision note](../research/WEAK-APER-20261110-001/weak_aperiodic.md)).

   **2026-11-10: abstract names** (`BARE-NAMES-20261110-001`).
   - **The question.** The board line named cells by words in two letters (A54). Without letters, with a neighbour distinction for
     each pair of names, what can a law force, and is the board still frozen?
   - **No finite rule can make cells touch (proved).** A law of finitary clauses that allows anything allows a board on which all
     cells are neighbours, or none are (Ramsey). So it can bound the degree but never force a neighbour.
   - **What the letters drew (proved).** Four neighbours a law can address, and one connected board. An infinite clause "every
     cell has a neighbour" can supply a degree, but not neighbours a law can tell apart, and no law of bounded degree forces a
     connected board.
   - **The tree still comes back (proved).** A law that reads only a place and its neighbours allows the tree whenever it allows a
     cycle. A declared commuting cycle with aperiodic tiles gives commuting boards, but only one per component.
   - **The board is no longer frozen (proved).** Two edges with the same pair of values can exchange partners, a change of four
     distinctions. In 90 of the 1,024 one-bit laws one neighbour distinction knots with its two endpoint values (computed, exact,
     frozen).
   - **Renaming is a finite change too.** Exchanging two names flips every distinction at them, so the source-aware condition, as
     read now, excludes nothing (A59).
   - **Next (selected).** Nativeness up to renaming ([decision note](../research/BARE-NAMES-20261110-001/bare_names.md)).

   **2026-11-10: nativeness up to renaming** (`PLACE-FLIP-20261110-001`).
   - **The question.** Without letters, exchanging two names is a finite change, so every distinction passed the source-aware
     condition. With renamings not counted, are the 90 knots between the board and the values still native?
   - **Excluding renamings is not enough (proved).** A cell can be cut out of one part of the board and wired into another by a finite change
     that is no renaming. So the count that means something keeps one kind of distinction fixed while the other changes: values
     with the board kept, or neighbour distinctions with the values kept.
   - **In worlds of finite pieces, every knot is native (proved, computed).** In a world made of copies of a finite board, each of
     the 90 knots has its three distinctions flipped this way, so none rests on renamings.
   - **On the free board most values are frozen (proved).** On the tree a recolouring has to stop somewhere. In 58 of the laws it
     never can, among them those where a flipped cell forces all four neighbours to flip. 26 knots stay native; the other 64 are not
     native on any tree.
   - **Next (selected).** Every accretion law, the one route left that could change the line's verdict
     ([decision note](../research/PLACE-FLIP-20261110-001/place_flip.md)).

   **2026-11-10: every accretion law** (`GROW-FACE-20261110-001`), the board line's deciding epic.
   - **The question.** Static laws choose the commuting board only by declaring a cycle. Can a law that grows the board from a seed do
     it without declaring one?
   - **No, by definition (proved).** A growing rule that closes no cycle grows the seed with trees attached. A local rule that closes
     a cycle declares it, because the cycle runs through what the rule can see. So the escape the epic froze could not exist, which its
     registration should have said (corrected).
   - **With a declared cycle, growth gives the commuting board itself (proved).** A rule that closes commuting cycles, with coordinates
     mod 3 as its only values, grows the square spiral of the literature's drawing one cell at a time, in its only order: its head is
     the only cell whose view looks like a head's. With the same values a static law also allows the commuting board's quotients,
     drawn as cylinders and tori.
   - **Growing everywhere at once, an order splits it (proved).** For every radius and every fixed priority, the rule that fills any
     missing neighbour and closes every commuting cycle it sees can be grown into two long arms, and the slit between them, filled
     from the top, gets two cells at one position.
   - **The line closes and is parked.** A uniform local law, static or growing, chooses the commuting board only by declaring a cycle;
     growth adds one board with no quotient, not a declared cycle ([decision note](../research/GROW-FACE-20261110-001/grow_face.md), with the line's closing summary).

   **2026-11-11: knots alone** (`KNOTS-ALONE-20261111-001`, backlog B144).
   - **The question.** The board line said the commuting board needs a declared cycle. In the knot's own terms a face can be a knot.
     So take knot patterns made of nothing but distinctions and three-place knots, with no board, no names and no declared cycles, put
     one symmetric law on every knot, and ask what the allowed states read of the meeting pattern.
   - **Four knots, four readings (proved).** The clause recovers exactly the knots and relates nothing beyond touching. Parity folds a
     two-fold weave to a 3-colouring, one knot copied everywhere. Not-exactly-one ties every pair to an all-zero state, a hub.
     Curvature, in the literature's word, is just counting (six-regular, the literature's flat, when every distinction is in six
     knots).
   - **Not-all-equal keeps the weave and spaces it (computed, exact, frozen).** It reads 227 of the 229 six-regular weaves in range
     without a triple of pairwise co-knotted distinctions that is not a knot (the literature's non-facial triangle) faithfully: their
     three-place bonds are exactly their knots, with no ties. Bond distance is 2 for a co-knotted pair and 3 two steps apart, from bonds
     around a hidden distinction. Two thin one-pair weaves fail, and at three steps short unfilled cycles can shorten a bond, so the
     frozen predictions failed narrowly and A63 stands. After the run: faithful on every six-regular weave in range whose unfilled
     cycles all have at least 5 pairs.
   - **Where forcing works (computed, exact).** A weave with positive curvature, in the literature's word, has no cover, so a law can
     fix it: with each distinction in five knots, not-all-equal allows only one zero-pair weave, the literature's
     icosahedron. Six-regular weaves always have covers, so no law fixes their size, and not-all-equal allows every non-orientable
     weave of Euler count 0 (the literature's Klein bottle) in range.
   - **What is still put in** is the count of how knots meet (A64). Whether reading the knots faithfully supplies it is the next
     question (sub-goal B145) ([decision note](../research/KNOTS-ALONE-20261111-001/knots_alone.md)).

   **2026-11-11: does a faithful reading supply the two-fold count?** (`NAE-SURFACE-20261111-001`, sub-goal B145).
   - **The question.** Not-all-equal reads almost every six-regular weave of knots alone faithfully, but the two-fold count (each pair
     in two knots, the knots at each distinction one cycle) was given. Does reading the knots faithfully force it?
   - **No (computed, exact, frozen).** Swap two knots of a faithfully read six-regular one-pair weave for two long-range ones: 160 of 822
     such patterns are still read faithfully, though some pairs now lie in one knot and some in three. The smallest has 25 distinctions, checked by independent
     code and knotlab.
   - **But near-weaves are where it works.** Each swap costs faithfulness, and random regular patterns were never read faithfully. So
     the knot law reads which knots there are, not how they meet: the count of how knots meet is an input
     ([decision note](../research/NAE-SURFACE-20261111-001/nae_surface.md)).

   **2026-11-11: the long-loop regime** (`LONG-LOOP-20261111-001`).
   - **The question.** With the two-fold count given, does not-all-equal read every six-regular weave with long unfilled cycles
     natively, and space it?
   - **Yes, in range (computed, exact, frozen).** It reads every orientable six-regular weave with 49 to 80 distinctions and
     non-orientable one with 19 to 40 (the literature's tori and Klein bottles) whose shortest unfilled cycle has at least 5 pairs
     faithfully, 449 weaves. On the 349 orientable ones whose unfilled cycles have at least 6 pairs, bond distance is graph distance + 1
     at every distinction within three steps.
   - **Two steps is a lemma (proved).** Two pairs that each form a knot with a hidden distinction, each fixed to equal values and the
     two to opposite values, force it both ways, so four distinctions two steps apart already form a bond.
   - **So the face can be the knot.** Nothing is named but the knot and its meeting pattern, and the local geometry of six-regular
     weaves (the literature's flat geometry) is read natively; A63 is overturned in this setting. Thinner weaves shortcut, so the ruler
     is local, out to about half the shortest unfilled cycle
     ([decision note](../research/LONG-LOOP-20261111-001/long_loop.md)).

   **2026-11-11: the not-all-equal ruler** (`RULER-20261111-001`).
   - **The question.** Is "bond distance = graph distance + 1" a theorem?
   - **Yes, on the endless six-regular weave (proved, refereed).** On the endless six-regular weave (the literature's triangular
     lattice) under not-all-equal, every pair is free, the knots are the only bonds of three distinctions, and two distinctions d steps
     apart lie together in a bond of exactly d + 2 distinctions and in none smaller. The bond is one side of a triangle of side d in the
     literature's drawing, all equal, with the opposite corner. Every bond is native.
   - **Why.** The states are the ground states of the triangular Ising antiferromagnet, and they carry a height that rises at most one
     per step (known). A pattern of values is forbidden when it asks the height to climb faster than that around a cycle, and each
     distinction can supply at most half a unit of the excess, so spanning d steps takes d + 2 distinctions.
   - **So the knot measures its own endless weave** exactly, as graph distance, and its bond balls read dimension 2. On the closed
     six-regular weaves (the literature's tori and Klein bottles) it stays computed ([decision note](../research/RULER-20261111-001/ruler.md)).

   **2026-11-11: the count from growth** (`GROW-COUNT-20261111-001`).
   - **The question.** The count of how knots meet (two per pair, one link per distinction, six around each) was put in. Can growth
     supply it, if each new knot is kept only while not-all-equal still reads the grown pattern faithfully?
   - **No (computed, frozen).** Wherever the pattern grows, the law accepts pairs in three knots and pinched links; with both named,
     links close at every degree from 3 to 14, never mostly at 6.
   - **The law refuses one meeting pattern (proved).** No pair's two knots may have their third distinctions knotted together: equal
     values on the pair would force a contradiction. So the sharpest cone in the literature's drawing, a link closed at three, fails
     inside any larger pattern, and the zero-pair weave of four knots (the literature's tetrahedron) can never grow.
   - **So how knots meet is an input, static or grown**; the face is still the knot ([decision note](../research/GROW-COUNT-20261111-001/grow_count.md)).

   **2026-11-11: the ruler on six-regular weaves** (`RULER-FLAT-20261111-001`).
   - **The question.** On the endless six-regular weave (every co-knotted pair in two knots, six knots at each distinction, every
     cycle filled; drawn: the triangular lattice) not-all-equal measures bond distance exactly. On a closed one, where a bond can go
     around an unfilled cycle, where does it cheat?
   - **An exact answer on orientable weaves (proved, refereed).** A state's height rises by a fixed winding around each unfilled cycle,
     and the allowed windings satisfy three inequalities. The margin M of the best winding, the least extra cost of going once around
     an unfilled cycle,
     decides everything: states exist exactly when M ≥ 0; bond distance is graph distance + 1 for every distance below M/3 and never
     less than the smaller of the two; and the reading is faithful when M > 3 (drawn: tori).
   - **Non-orientable weaves split in two (proved for one half).** If the co-knotted pairs can be directed so that every knot is a
     directed cycle, the law's heights treat the twist as one more unfilled cycle and the theorem holds word for word. If not, heights flip under the
     twist, and that half stays computed (drawn: Klein bottles, by the direction of the glide mirror).
   - **Only for two-fold weaves.** All of it needs each co-knotted pair in exactly two knots; where pairs lie in three or more knots
     the line has no ruler and no height yet, which is the owner's next question
     ([decision note](../research/RULER-FLAT-20261111-001/ruler_flat.md)).

   **2026-11-11: what not-all-equal makes of overlapping bases** (`OVERLAP-READ-20261111-001`).
   - **The question.** A knot may share distinctions with any number of others. In such a base, what does not-all-equal bind that no
     knot names, and is it local?
   - **Only its own kind (proved).** Nothing is frozen, a tied pair is always equal or always unequal, and every unnamed hollow triple
     is a not-all-equal knot with some distinctions read negated. Four knots arranged as a Pasch configuration (literature) are read
     as all eight of the zero-pair weave on six distinctions (literature: the octahedron).
   - **The law reads pair counts (proved).** Its states depend only on how many knots lie on each pair, so knot patterns with the
     same counts allow the same states: different bases, one relation to it. This is one exact sense of the owner's "compressed" structure.
   - **Overlap is readable, uniform overlap is not (proved and computed).** A pair can lie in any number of knots in a base read
     faithfully, and grown bases reach nine; where every co-knotted pair lies in three knots, no base in range is read faithfully.
   - **Not local (computed, frozen).** The configurations that add a knot grow with size (1, 4, 11, 64 at three to six knots), some
     small bases need seven, and one knot swap in a two-fold weave can bind a triple through half the base
     ([decision note](../research/OVERLAP-READ-20261111-001/overlap_read.md)).

   **2026-11-11: infinite bases with periodic overlap** (`PERIODIC-READ-20261111-001`).
   - **The question.** A base reality in the owner's sense can be infinite: a meeting pattern that repeats without end. Does
     not-all-equal read such bases faithfully when pairs lie in many knots, and what do they show that their finite repeats do not?
   - **Yes, with overlap (computed, frozen).** Repeating along one shift the reading is exact: 73 of 181 patterns are read faithfully,
     with pairs in up to four knots. Repeating along two shifts it is bounded: 134 of 627 are read faithfully, 36 with a pair in three or
     more knots and two with one repeated pair in four, and in every one, pairs two steps apart share a bond of four.
   - **Not its finite repeats.** 25 of those bases have no finite repeat read faithfully, and some value patterns occur only in states
     that pass from one repeating regime to another (literature: a domain wall), which no finite repeat can hold.
   - **The global triples were two halves of a weave (proved, computed).** A two-fold weave whose knots split into two classes meeting
     every co-knotted pair once each is read the same from either class; a knot removed from one class is still held by the other, through
     the whole weave. That accounts for 91 of the 98 global cases ([decision note](../research/PERIODIC-READ-20261111-001/periodic_read.md)).

   **2026-11-11: bond balls on infinite overlapping bases** (`BOND-BALLS-20261111-001`).
   - **The question.** On the 134 infinite bases with a repeating meeting pattern that not-all-equal reads faithfully, does bond
     distance follow steps apart, as on the endless six-regular weave? Steps apart grow as the two shifts dictate; the law's own
     distance need not.
   - **It always reaches the next shell, but sometimes faster (computed, frozen).** Every distinction three steps away lies in a bond of
     at most five with the origin. On 42 bases some lie in a bond of four, and some four steps away too: the law's distance is shorter
     than the meeting pattern's. The six-regular weave, where the ruler is proved, has none.
   - **A direction of no length (computed).** On one base three equal distinctions force the next three over to the other value,
     column after column, so distinctions twelve steps away still share a bond of four with the origin: read by the law alone, that
     direction does not lengthen, a base compressed along one of its shifts
     ([decision note](../research/BOND-BALLS-20261111-001/bond_balls.md)).

   **2026-11-12: a direction the knot law does not lengthen** (`FOLD-20261112-001`).
   - **The question.** Is the folded direction real at every distance, and is it the law's doing or the meeting pattern's?
   - **Real at every distance (proved, refereed).** On that base three equal distinctions force the next three over to the other value,
     column after column, so for every k the origin lies in a bond of four with distinctions k steps away, along a whole line both
     ways. No single far distinction is tied to the origin: the law binds it only jointly with a whole triple.
   - **The law's doing.** Steps apart and bond distance both belong to the base itself, and the step distance grows in two directions; the
     fold runs along the one pair class that two knots share. Its nearest precedent is a known parity rule on the same pattern of
     knots whose constraints appear at doubling distances (literature: Ledrappier's shift).
   - **Fourteen kinds of base fold (computed).** Of the 38 kinds of base with shortcuts, 14 keep bonds of four at five and six steps,
     all among those whose shortcuts reached four steps ([decision note](../research/FOLD-20261112-001/fold.md)).

   **2026-11-12: across the direction the law does not lengthen** (`ACROSS-FOLD-20261112-001`).
   - **The question.** On base 16 the law does not lengthen one shift. How does its bond distance grow across it, and does it read a
     line there?
   - **Heddles travel (proved, refereed).** Three equal distinctions at consecutive across-counts, then every second across-count up
     to y, all at one along-count (a heddle), are passed on intact along the unlengthened shift, so with one far distinction y across
     they form a bond of floor((y+1)/2) + 3, for every y.
   - **What travels keeps itself (proved, with the advisor model).** The law passes a value on only where it has an equal partner one
     more or two fewer across, and lets every other value flip; far along, a pattern at one along-count forces exactly its
     self-keeping part. So the heddle is the least bond of one along-count, and such bonds never reach three or more fewer across.
   - **Both ways at the same rate (computed).** A second along-count passes values two across back, and bonds reach the other way at
     the heddle's sizes, to ten across. Balls grow by two across-counts each way per step of bond distance: no length along one shift,
     one dimension across. That no smaller bond exists beyond one along-count is open; none turned up in the boxes searched
     ([decision note](../research/ACROSS-FOLD-20261112-001/across_fold.md)).

   **2026-11-12: nothing chooses a meeting pattern** (owner's statements, 2026-11-11 Pacific; interpretation, with readings under test).
   - **His words.** "There is no choice. [...] It's just random", with some realities perhaps "statistically more likely than
     others"; other realities are "Different meeting patterns! [...] Both the underlying patterns and even possibly the binding
     patterns"; ours "is indifferent. It's is purely coincidental"; and "some combinations should resolve to nothing, some can go
     for a while then die. Others will go on forever and create sets like the natural numbers."
   - **What it changes.** The entries above that say a meeting pattern is given or put in describe one sample, not a gap: none is
     chosen (A15, applied). Whether a law forces its own meeting pattern (A62) stays a question of its own; beside it stands which
     meeting patterns are typical and which rare, always under a declared weighting (A71), since no chances are equal over
     infinitely many. Other realities are read as other knot patterns of one kind of logic, bound ones as one larger knot pattern
     (A73).
   - **Known.** Random not-all-equal patterns end near 2.1 knots per distinction (exact value for three places open). Not found:
     what the law reads off the ones that live, and the outcomes of other growth processes. Tested by `RANDOM-FATES-20261112-001`;
     the owner's recursion, a base standing in for one distinction, is backlog B164
     ([Intuitions, lesson 7.3](../INTUITIONS.md#73-every-meeting-pattern-none-chosen)).

10. **Competition. Mapped on 2026-10-19, not decided.** Pairwise rules that
    must all hold never make a knot, but pairwise preferences that cannot all
    hold leave knots among their least-violation states ("Knots from
    competing pairs"). Both readings were tested ("Both readings tested"):
    - **Strict reading:** stays presentation-invariant and gives pairs no
      knots.
    - **Competition reading:** needs weights, a declared measure of
      violation. In return, frustrated pairs make one kind of knot, the
      not-all-equal knot (the literature's frustrated triangle).

    Is competition the law that question 9 asks for? Not by itself.
    Competition turns a drawn triangulated layout into a chain of knots whose
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
building from atoms, distinctions, choice and endless chains. `presence`
covers the earlier exploration of presence under the absence reading.
`patterns` covers the original
post: controllers, hidden information and the two readings of erasure.
`choice` covers whether the base has real alternatives. `space` covers bonds,
the free complex and composition. `competition` covers both readings of
rules that cannot all hold. Each exits nonzero if a result changes, so run all
seven after changing a definition.
