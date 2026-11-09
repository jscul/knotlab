# Intuitions

The contact-first program asks whether logic can build structure, such as
holes, paths and spaces, without assuming a space to start from. Its working
answer begins with one object: the **logical knot**, two or more open
distinctions bound together so that the whole is constrained but no part is.

This page states the intuitions behind that answer in plain terms. Each one is
tied to what has been proved or checked in this repository, and each is
labelled by what kind of claim it is.

The page is written as a textbook, to be read in order. Its seven chapters are
divided into lessons, and each lesson builds on the ones before it. Chapter 1
sets up bits, rules and the notation, including how to read A, B → c, before
anything is built from them.

| Label | Meaning |
| --- | --- |
| **Proved (Lean)** | Kernel-checked in [`lean/`](lean/), core Lean 4, standard axioms only |
| **Proved (note)** | Proved in a note in [`notes/`](notes/), whose numbers a script rechecks |
| **Proved (here)** | A short proof given on this page |
| **Checked** | Verified exhaustively on finite cases by [`tests/test_knotlab.py`](tests/test_knotlab.py) |
| **Classical** | A known theorem the intuition relies on, with its source |
| **Reading** | Our interpretation. It is not a theorem and nothing is proved from it |

Most of the mathematics in Chapters 1 to 4 is classical. What is ours there is
the reading: which questions to ask, and what the known answers mean when asked
this way. Lessons 5.2, 6.2 and 6.3 report results that are new as far as we
found. Lesson 7.1 lists what is classical and what is ours.

To try anything on this page, run commands from the repository root:

```bash
PYTHONPATH=tools python3 -m knotlab demo
```

## Contents

- [Chapter 1. Bits and rules](#chapter-1-bits-and-rules)
  - [1.1 Distinctions and states](#11-distinctions-and-states)
  - [1.2 Rules and what they allow](#12-rules-and-what-they-allow)
  - [1.3 Emergence in the Game of Life](#13-emergence-in-the-game-of-life)
  - [1.4 The picture](#14-the-picture)
  - [1.5 Reading A, B → c](#15-reading-a-b--c)
  - [1.6 Forgetting a variable](#16-forgetting-a-variable)
  - [1.7 What a shape is](#17-what-a-shape-is)
- [Chapter 2. The knot test](#chapter-2-the-knot-test)
  - [2.1 The knot test](#21-the-knot-test)
  - [2.2 Knots on the cube](#22-knots-on-the-cube)
  - [2.3 What a knot hides](#23-what-a-knot-hides)
- [Chapter 3. Pairs and three places](#chapter-3-pairs-and-three-places)
  - [3.1 Two-place rules and the majority vote](#31-two-place-rules-and-the-majority-vote)
  - [3.2 Pairs cannot make a knot; three places can](#32-pairs-cannot-make-a-knot-three-places-can)
  - [3.3 The shape of a system](#33-the-shape-of-a-system)
  - [3.4 Holes and knots](#34-holes-and-knots)
- [Chapter 4. How bindings behave](#chapter-4-how-bindings-behave)
  - [4.1 Easy and hard questions](#41-easy-and-hard-questions)
  - [4.2 Requirement and choice](#42-requirement-and-choice)
  - [4.3 Knots from competing pairs](#43-knots-from-competing-pairs)
  - [4.4 Which knots remember a loop](#44-which-knots-remember-a-loop)
  - [4.5 What networks of loops remember](#45-what-networks-of-loops-remember)
- [Chapter 5. Depth](#chapter-5-depth)
  - [5.1 Proving that nothing is allowed](#51-proving-that-nothing-is-allowed)
  - [5.2 How deep a hole is](#52-how-deep-a-hole-is)
- [Chapter 6. Counting](#chapter-6-counting)
  - [6.1 Counting worlds](#61-counting-worlds)
  - [6.2 The worlds of not-all-equal knots](#62-the-worlds-of-not-all-equal-knots)
  - [6.3 Patterns in three dimensions](#63-patterns-in-three-dimensions)
- [Chapter 7. Sources and questions](#chapter-7-sources-and-questions)
  - [7.1 What is classical and what is ours](#71-what-is-classical-and-what-is-ours)
  - [7.2 Open questions](#72-open-questions)
- [Glossary](#glossary)

## Chapter 1. Bits and rules

Everything later is built from bits and from rules about them. This chapter
sets up that vocabulary and its notation, reads the Game of Life as such rules,
states the picture the program starts from, reads the smallest rule that binds
two loops, and ends with what the guide means by a shape.

### 1.1 Distinctions and states

**Distinctions.** Everything in this guide is built from one material, the
distinction: two alternatives of which exactly one holds. A distinction is one
bit, and its two alternatives are written 0 and 1. Nothing else is assumed.
There is no space, no order and no number beyond the two values.

**Variables.** A variable names a distinction. The guide writes the
distinctions that loops bring (lesson 1.4) as capital letters, such as A and B,
the contact between loops as c, helper variables called witnesses (lesson 1.6)
as w, and any other variables as x, y and z. The letters are only names, and
renaming them changes nothing.

**Joint states.** A joint state, or just a state, gives every variable a value.
A state is written as its values in a fixed order, so with the order A, B, c
the string 110 means A = 1, B = 1 and c = 0. Three variables have eight joint
states:

```text
000  001  010  011  100  101  110  111
```

Each new variable doubles the count, so n variables have 2^n joint states.

**The cube of states.** It helps to draw the eight states as the corners of a
cube, with one direction for each variable: A runs from left to right, B from
front to back, and c from bottom to top.

```text
          011 ─────── 111
         ╱ │         ╱ │
      001 ─────── 101  │
       │  010 ─────│─ 110
       │ ╱         │ ╱
      000 ─────── 100
```

Two states are **neighbours**, joined by an edge of the cube, when they differ
in exactly one variable, as 110 and 111 do. They are **opposite** when they
differ in all three, as 000 and 111 do. Chapters 1 to 3 read many patterns
off this cube. It is a picture of the states, not a space in which the
variables sit.

### 1.2 Rules and what they allow

**Rules and relations.** A rule, or constraint, rules out some joint states. A
**system** of rules allows exactly the states that break none of its rules. The
guide reads a system only through the set of states it allows, which is called
its **relation**. Two systems that allow the same states are the same relation,
however differently they are written.

**Symbols.** Rules are written with these symbols:

| Written | Read aloud | Rules out |
| --- | --- | --- |
| ¬A | not A | A = 1 |
| A ∧ B | A and B | every state except A = B = 1 |
| A ∨ B | A or B, or both | A = B = 0 |
| A → B | if A, then B | A = 1 with B = 0 |
| A = B | A equals B | A = 1 with B = 0, and A = 0 with B = 1 |
| A ≠ B | A differs from B | A = B = 0, and A = B = 1 |
| A ⊕ B ⊕ c = 0 | parity: an even number of A, B and c are 1 (⊕ is addition mod 2) | the four states with an odd number of 1s |
| not-all-equal(A, B, c) | the three are not all the same | 000 and 111 |

**A warning about the arrow.** The arrow causes most misreadings. A → B is the
logician's "if A, then B", and it rules out one case only: A = 1 with B = 0. It
says nothing when A = 0. It is not a step in time, a cause or a computation.

**Clauses and CNFs.** A clause is an "or" of letters, each of which may be
negated, such as ¬A ∨ ¬B ∨ c. Each letter in a clause is a **literal**, and the
number of literals is the clause's **width**. A clause rules out exactly one
assignment of its own variables, the one that makes every literal false: ¬A ∨
¬B ∨ c rules out A = 1, B = 1, c = 0 and allows the other seven states. A list
of clauses that must all hold is a **CNF**, and a CNF whose clauses have at
most two literals each is a **2-CNF** (at most three: a 3-CNF). Every relation
can be written as a CNF, with one clause of full width for each excluded state.
On the knotlab command line, `~` stands for ¬, spaces separate the literals of
a clause, and semicolons separate clauses, so (¬A ∨ c) ∧ (¬B ∨ c) is typed `~A
c; ~B c`. Lesson 1.5 draws CNFs in colour.

**Free and constrained.** Two words carry the rest of the guide. A set of
variables is **free**, or **unconstrained**, when every combination of their
values occurs in some allowed state. Otherwise it is **constrained**. Take A ≠
B, with a third variable c that no rule mentions. It allows 010, 011, 100 and
101, and:

- A alone is free, since A = 0 and A = 1 both occur;
- the pair A, B is constrained, since 00 and 11 never occur;
- the pair A, c is free, since 00, 01, 10 and 11 all occur.

Being free is a statement about what can happen together, not about any single
state.

### 1.3 Emergence in the Game of Life

Conway's Game of Life is the best-known picture of emergence: simple rules on a
grid of cells give patterns that behave like objects. Read with the words of
lesson 1.2, the whole game is one system of rules. *Classical:* Conway's game,
published by Gardner in 1970.

- **Cells are distinctions.** Each cell at each step of time is a variable: 1
  when the cell is alive, 0 when it is dead.
- **The rule is a rule on ten variables.** A cell is alive at the next step
  exactly when three of its eight neighbours are alive now, or when it is
  alive now and two of them are. That links the cell's next value to the
  present values of the cell and its eight neighbours. It allows 512 of the
  1,024 states of those ten variables, and like every rule it can be written
  as a CNF.
- **A history is an allowed state.** Stack the steps in layers, with one
  variable for each cell in each layer. Together, the rules of every cell
  allow exactly the possible histories: the first layer can be anything, and
  every later layer is forced.
- **The famous patterns are solutions.** A still life, such as the block, is a
  state that the rules carry to itself, so it is an allowed state of the rules
  with the next layer equal to the present one. An oscillator, such as the
  blinker, comes back to itself after a fixed number of steps (two for the
  blinker), and a spaceship, such as the glider, comes back moved (one cell
  diagonally every four steps). Each is an allowed state of the same rules
  with time closed into a cycle, shifted in the case of a spaceship.
- **Every rule is local, and what the rules allow is global.** A rule reads
  only one cell and its neighbours, but neighbouring rules share variables, so
  a pattern can be forced or ruled out by rules far away, through the rules
  in between.
- **Contradictions are objects too.** A lone live cell and an empty board both
  become an empty board, so two different patterns have the same successor.
  By the Garden of Eden theorem (Moore 1962; Myhill 1963), some patterns
  therefore have no predecessor at all, and asking for one gives a system of
  rules that allows nothing. Chapter 5 shows that such a system still has
  structure: how much of it a proof must hold at once to see that nothing is
  allowed.

**The grid is drawn in advance.** Each rule of Life mentions one cell and its
eight neighbours, and the grid is what decides which cells those are. Logic
needs no grid. A rule may mention any set of variables, and a variable may
appear in rules with any others; lesson 3.4 shows that every shape, of any
dimension, is the shape of some system of rules. So Life shows patterns
emerging on a space that someone drew. The program asks for more: rules that
make their own neighbourhoods, so that the space emerges too (lesson 7.2,
question 1).

**Reading.** Life is a picture of emergence, not the program's first instance
of it. Its rule cannot be split into two-place rules, even with witnesses
(lesson 3.1 gives the test), and it is not a knot either (lesson 2.1); its
patterns also rest on the drawn grid. The lessons that follow look for the
first thing that a whole allows and no part shows: a binding between two
loops, which lesson 2.1 calls a knot. The game's name is only a name, and
nothing here is a claim about biology.

### 1.4 The picture

**Lines and loops, state by state.** The program starts from a picture of
lines, loops and what lies between loops. Each part of the picture is a
statement about small systems of rules like those of lesson 1.2, so it can be
checked state by state. With states written in the order x, y, z:

- the chain x → y, y → z allows 000, 001, 011 and 111: once a variable is 1,
  every later one is 1, so the chain only orders its members;
- closing the chain into a loop with z → x leaves 000 and 111: the three are
  forced to be equal, so the loop has collapsed to one free bit, as if it were
  a single point;
- a loop of "equal" and "differ" steps does the same or worse:
  x = y, y ≠ z, z ≠ x allows 001 and 110, one free bit again, and
  x = y, y = z, z ≠ x allows nothing.

The picture itself:

- **A line is not enough.** A chain of implications only orders its members,
  and open strings can always be rearranged into one another.
- **A single loop is not enough.** A loop of implications forces all its
  members to be equal, so it collapses to a point. A loop of "equal" and
  "unequal" steps collapses to one free bit, or contradicts itself.
- **What is real is what lies between bound loops.** The binding belongs to
  the pair, not to either loop. No part smaller than the whole shows it, and
  erasing either loop removes it.
- **A loop is a logical structure, not a spatial one.** What it brings to a
  binding is an *open distinction*: a bit it leaves free.

**From loops to A, B and c.** The open strings of the first point are a
comparison with rope: a tangle in a string with free ends can always be slid
off an end, so only closed loops stay knotted. From here on a loop takes part
only through its open distinction. Two loops bring two distinctions, written A
and B, and the place where they are bound is one more variable, the **contact**
c. The next lesson reads the smallest rule that binds them.

### 1.5 Reading A, B → c

**Ways of writing it.** The smallest rule that binds two loops at a contact is
called the **atom**. It is written in several ways, and they all say the same
thing:

| Written | Read aloud |
| --- | --- |
| A ∧ B → c, often shortened to A, B → c | if A and B, then c |
| ¬A ∨ ¬B ∨ c | not A, or not B, or c |
| `~A ~B c` | the same clause, typed for knotlab |

**The one thing to remember is that the atom forbids exactly one state:**
A = 1, B = 1 and c = 0, which is A and B without c. In words, *A and B
together demand c*. Every other state is allowed:

```text
A B c
0 0 0   allowed
0 0 1   allowed
0 1 0   allowed
0 1 1   allowed
1 0 0   allowed
1 0 1   allowed
1 1 0   excluded: A and B without c
1 1 1   allowed
```

Each piece of the notation, in turn:

- **A and B** are the open distinctions of the two loops (lesson 1.4), and
  **c** is the contact. The capital letters mark the variables that come from
  loops and the small letter marks the contact, nothing more.
- **The comma** in A, B → c means "and", as in A ∧ B.
- **The arrow** is the "if …, then" of lesson 1.2. It rules out only the case
  in which A and B hold and c does not. It says nothing about c when A or B is
  0, so c = 1 with A = B = 0 is allowed. It does not mean that A and B come
  first, or that they cause c or compute it.
- **The direction is only a way of reading it.** The clause ¬A ∨ ¬B ∨ c can be
  read from any of its letters: "if A and B, then c", "if A and not c, then
  not B", or "if B and not c, then not A". All three rule out the same state,
  110. The knot test of lesson 2.1 treats the three variables alike.

**Why it binds.** Check the three pairs, with "free" as in lesson 1.2.

- A and B take all four combinations of values, since c = 1 completes each of
  them to an allowed state.
- A and c take all four, since B = 0 completes each of them.
- B and c take all four, since A = 0 completes each of them.

So every pair is free, but the three together are not, since 110 never occurs.
The rule lives in the whole and in no part, which is what this guide means by
a binding. Lesson 2.1 turns that into the knot test.

Two rules look similar but are not the atom:

- **The AND gate** c = A ∧ B makes c exactly "A and B". It rules out four
  states, 001, 011, 101 and 110, and its pair A, c is already constrained,
  since A = 0 with c = 1 never occurs. The atom asks only that A and B
  together bring c.
- **The common hub** (¬A ∨ c) ∧ (¬B ∨ c), "A brings c, and B brings c", rules
  out 010, 100 and 110. Each loop forces c on its own, so the pair A, c is
  constrained: A = 1 with c = 0 never occurs. Lesson 2.1 shows why the hub
  fails the knot test.

Lesson 4.2 reads 1 as "exists". Then A, B → c is a requirement: when A and B
exist, c must exist too, and nothing is required otherwise.

**CNFs in colour.** It helps to give each variable its own colour: 🟥 for A,
🟦 for B and 🟨 for c. Red and blue stand for the open distinctions of two
loops and yellow for their contact (lesson 1.4), so each loop enters a CNF as
one colour. Each clause becomes a row of the colours it mentions, with ¬ before
a negated one, and every row must hold. A row rules out one combination of its
own colours, whatever the other colours are, so a clause ties together exactly
the colours in its row. The three rules of this lesson, one clause to a row:

| Rule | Clause | In colour |
| --- | --- | --- |
| the atom | ¬A ∨ ¬B ∨ c | ¬🟥 ∨ ¬🟦 ∨ 🟨 |
| the AND gate | ¬A ∨ ¬B ∨ c | ¬🟥 ∨ ¬🟦 ∨ 🟨 |
| | A ∨ ¬c | 🟥 ∨ ¬🟨 |
| | B ∨ ¬c | 🟦 ∨ ¬🟨 |
| the common hub | ¬A ∨ c | ¬🟥 ∨ 🟨 |
| | ¬B ∨ c | ¬🟦 ∨ 🟨 |

The atom's one row holds all three colours, so it ties the three together and
no pair of them: it binds the two loops. Each of the hub's rows holds two
colours and ties one loop to the contact. The AND gate has a row of all three,
but its two-colour rows tie the loops to the contact as well, so one full row
is not enough. A CNF binds the loops when it rules something out but ties no
pair of colours. Every row then holds all three colours, since a shorter row
would tie the colours it holds, and lesson 3.2 shows that rows of two colours
never bind loops at all. Lesson 2.1 turns this into the knot test, which reads
the allowed states, never the colours. Lesson 4.4 makes loops out of knots, by
closing copies of one into a ring in which each copy shares a colour with the
next.

### 1.6 Forgetting a variable

**What forgetting does.** The knot test looks at what remains when a variable
is ignored, so it needs an exact way of ignoring one. **Forgetting** a variable
keeps a state of the other variables whenever at least one value of the
forgotten variable completes it to an allowed state. It does not set the
variable to 0 or to 1; it lets the variable take whichever value suits. What
remains is the system's **projection** onto the other variables, also called
its **shadow** on them.

- Forget c in the atom. Each of the four states of A and B is completed by
  c = 1, so the shadow on A and B allows all four: the pair is free.
- Forget B in the common hub. The state A = 1, c = 0 has no completion,
  because ¬A ∨ c rules it out whatever B is. So the shadow on A and c still
  says that A forces c.

The two ideas fit together: a set of variables is free exactly when forgetting
every other variable leaves it unconstrained.

**Witnesses.** Rules sometimes need helper variables. A **witness** is a
variable added to report on something, such as whether two bits differ or
whether two loops are bound. Witnesses are forgotten before any verdict, which
is called quantifying them away. They let short rules state long relations.
Parity on four variables needs only two three-place rules and one witness w:
w = x1 ⊕ x2 and w = x3 ⊕ x4. Forgetting w leaves exactly the states with
x1 ⊕ x2 = x3 ⊕ x4, which is the parity x1 ⊕ x2 ⊕ x3 ⊕ x4 = 0. Lesson 3.2 uses
the same device to bind any number of loops with three-place rules.

### 1.7 What a shape is

**The word.** In the owner's usage, which this guide adopts, a shape is any
structure that rules make. In the owner's words (8 November 2026): "things like
triangles/lines are essentially shapes, and they can run on forever. You can
have an infinitely large circle, and different infinity size circles as well.
Same thing with human minds. [W]e're essentially just a logical shape, or a
pattern that repeats as consciousness in other humans. Our genome is a shape
just like it."

**Shape or pattern.** "People refer to these as 'patterns'. They are, but it's
missing the root of it. Saying that these 'emergent structures' are shapes
allows us to understand them in the context of logic, from which we can create
shapes. They are rules, and rules within rules." So a shape is a pattern
together with the rules that make it. A glider is a pattern on Life's board; as
a shape it is the glider together with the rule that carries it along (lesson
1.3).

**Rules within rules.** Naming a pattern gives it a new variable, a witness,
and the naming is itself a three-place rule (lessons 1.6 and 3.2), so rules
about rules need no new kind of rule. The record also finds a limit. Built from
one three-place law, towers of patterns of patterns keep only parity: every
other law reaches the free relation, which constrains nothing, within three
levels ([GEOMETRY-LAW-20261029-001](research/GEOMETRY-LAW-20261029-001/geometry_from_a_law.md)).

**Shapes that run on forever.** A line has no end, and a circle can be as large
as you like. The record has a shape of this kind built with nothing drawn: a
rule that grows only at knots holding two open ends grows the number line from
a single knot, while a region with no open ends freezes
([OPEN-END-GROWTH-20261107-001](research/OPEN-END-GROWTH-20261107-001/open_end_growth.md)).
Circles depend on the law. Laws on periodic layouts make polygons, whose π is a
rational number, and an exactly round circle came from a random layout with no
preferred direction ([LOGIC-CIRCLE-20261107-001](research/LOGIC-CIRCLE-20261107-001/logic_circle.md)).

**Every bond is finite.** A shape can run on forever, but each binding in it
joins finitely many things. No system of clauses binds infinitely many loops
into one knot, by the compactness theorem, so an infinite thread is a tower of
finite knots ([THEORY.md](THEORY.md#every-bond-is-finite); lesson 7.2,
question 3).

**The board and true base reality.** Life's board is drawn before the game
starts (lesson 1.3). In the owner's words, "we're in a different base reality.
True base reality, where we start with nothing and have to create the
pattern." The guide's version is lesson 1.1's: nothing is assumed except
distinctions, so every shape, space included, has to come from rules (lesson
7.2, question 1).

**Can the rule be learned?** "This doesn't have to be designed, maybe we can
learn the shape of the underlying pattern somehow. But that is to be tested."
That is open: whether a learning rule, shown what a system allows, can find
rules, and rules within rules, that make it.

**Two senses of the word.** From lesson 3.3 on, the guide also uses "shape" in
a narrow sense: the sets of variables a system leaves free, drawn as points,
edges and filled triangles. The narrow shape is one exact view of the broad
one, which shows the holes and knots inside what a system allows.

**Reading.** Apart from the results it cites, this lesson is the owner's
reading. Minds, consciousness and genomes are examples of the word, and nothing
here is a claim about minds or biology.

## Chapter 2. The knot test

Lesson 1.5 found a rule that lives in the whole and in no pair. This chapter
turns that into a test, draws the test on the cube of states, and counts every
knot on three variables.

### 2.1 The knot test

**The setting.** Read a system of constraints as the set of joint states it
allows. Auxiliary "witness" variables may appear, and are quantified away.
Nothing outside the constraints, such as an executor or a scheduler, may supply
an input. A verdict depends only on the allowed states, never on how the
constraints are written.

Each loop contributes an open distinction. The contact is one more variable,
`c`. **Erasing a loop forgets it**: its variable is no longer constrained by
anything.

**The test.** A relation over the loops' distinctions and the contact is a
**knot** when:

- **K1, binding:** it is constrained as a whole;
- **K2, loss on erasure:** forgetting any one variable, a loop's or the
  contact's, leaves the others unconstrained;
- **K3, coexistence:** some joint state is allowed (K2 already implies it).

In short: **constrained as a whole, unconstrained in every part**, like
Borromean rings. Forgetting the contact must free the loops too, so loops tied
directly to each other do not count.

**Knots and non-knots.** Six relations against the test:

| Relation | Knot? | Why |
| --- | --- | --- |
| `¬A ∨ ¬B ∨ c` (the **atom**: if A and B, then c) | yes | excludes one state; every pair is free |
| `A ⊕ B ⊕ c = 0` (**parity**) | yes | excludes four states; every pair is free |
| not-all-equal(A, B, c) | yes | excludes 000 and 111; every pair is free |
| `(¬A ∨ c) ∧ (¬B ∨ c)` (a **common hub**) | no | forget B, and A still forces c |
| `A ≠ B`, with c unused | no | forget c, and A and B stay tied |
| `c = A ⊕ B` with A fixed true | no | A is not open, so it is constrained alone |

```bash
PYTHONPATH=tools python3 -m knotlab check --cnf "~A ~B c" --loops A B --contact c
PYTHONPATH=tools python3 -m knotlab check --cnf "~A c; ~B c" --loops A B --contact c
```

The first command reports a knot. The second reports a hub, and explains which
binding survives each erasure. *Proved (Lean):* `ForgettingKernel.lean`
(`atom_isKnot`, `parity_isKnot`, `hub_not_knot`, `tied_not_knot`).

### 2.2 Knots on the cube

**Free pairs on the cube.** The cube of lesson 1.1 turns the knot test on three
variables into a picture. Mark the states a relation excludes. A pair of
variables, say A and B, is constrained exactly when some combination of their
values never occurs, and that happens exactly when both completions of the
combination are excluded: the state with c = 0 and the state with c = 1. Those
two states differ only in c, so they are neighbours. The same holds for every
pair, so:

**Every pair is free exactly when no two excluded states are neighbours.**

**Which relations are knots.** On three variables, forgetting one variable
leaves a pair. So a relation on three variables is a knot exactly when it
excludes at least one state (K1) and no two of its excluded states are
neighbours (K2).

- The atom excludes the single corner 110, so it is a knot.
- Parity A ⊕ B ⊕ c = 0 excludes the four corners with an odd number of 1s:
  001, 010, 100 and 111. Changing one bit changes the number of 1s by one, so
  no two of these corners are neighbours, and parity is a knot. No knot on
  three variables excludes more corners than parity does.
- Not-all-equal excludes 000 and 111, which are opposite, so it is a knot.
- The common hub excludes 010, 100 and 110, and 110 is a neighbour of both of
  the others, so it is not a knot.

**Independent sets.** A set of corners with no two of them neighbours is called
an independent set of the cube. The knots on three variables are therefore the
nonempty independent sets of excluded states. Two excluded corners of a knot
never differ in just one variable: they differ in two, which is called Hamming
distance two (as 110 and 000 do), or they are opposite. The next lesson counts
these knots: there are 34, in five shapes.

### 2.3 What a knot hides

**The intuition.** A knot is invisible in its parts, so the whole holds
information that no part holds. That information can be measured, and it is
small: a knot hides at most one bit.

**How it is measured.** The measure counts possibilities. A knot's pairs are
all free, so together they rule nothing out and leave all 8 states possible.
The whole allows fewer. If it allows M of the 8 states, it holds log₂(8/M) bits
that no pair holds: the atom allows 7 states and holds log₂(8/7) ≈ 0.193 bits,
and parity allows 4 and holds log₂(8/4) = 1 bit.

- **Two loops and a contact have exactly 34 knots, in five shapes.** *Checked*
  against all 256 relations on three variables:

  | Excluded states | Relations | Bits the whole holds and no pair does |
  | --- | --- | --- |
  | 1 (a single three-literal clause: the atom) | 8 | 0.193 |
  | 2, opposite corners | 4 | 0.415 |
  | 2, at Hamming distance two | 12 | 0.415 |
  | 3 | 8 | 0.678 |
  | 4 (parity, even or odd) | 2 | 1.000 |

  A relation on three variables has every pair free exactly when no two of
  its excluded states differ in one coordinate. So a knot's excluded states
  form a nonempty independent set of the 3-cube. There are 34 such sets, in
  five classes under the cube's 48 symmetries.
- **A knot hides at most one bit, and only parity hides a full bit.**
  *Proved (here).* Forgetting one variable of a knot on m variables leaves all
  2^(m−1) assignments of the others, and each needs at least one allowed
  state. So a knot allows at least half of its states. If it allows exactly
  half, forgetting the last variable is a bijection, so the relation is the
  graph of a function f: the last variable is fixed by the others. Two allowed
  states that differ in one coordinate would make that projection two-to-one,
  so f changes whenever one input bit changes. That makes f parity or its
  complement.
- **The atom is the smallest bond.** It excludes the fewest states. It is
  also what an AND gate adds to its two-place parts: a two-input gate's
  relation is pairwise exactly when the gate ignores an input, so each of the
  ten gates that use both inputs needs a three-place clause, which is an atom
  up to which value of each variable counts as present. *Checked*
  (`knotlab worlds`).

**Reading.** A distinction is the material and an atom is what holds material
together. Digital hardware can build anything because its gates supply atoms.

```bash
PYTHONPATH=tools python3 -m knotlab patterns
```

## Chapter 3. Pairs and three places

Which rules can build a knot? Rules on two variables never can, and rules on
three variables always can. The chapter then draws what a system leaves free
as a shape, and finds the knots among the shape's holes.

### 3.1 Two-place rules and the majority vote

**Two-place rules.** A two-place rule mentions two variables, and every
two-place rule can be written as a 2-CNF: A → B is ¬A ∨ B, A = B is (¬A ∨ B) ∧
(A ∨ ¬B), and A ≠ B is (A ∨ B) ∧ (¬A ∨ ¬B). One test separates what two-place
rules can say from what they cannot, and the test is a vote.

**The vote.** The majority of three states is the state that takes, in each
variable, the value that at least two of the three take. The majority of 010,
100 and 111 is 110: A is 0, 1 and 1, so 1; B is 1, 0 and 1, so 1; and c is 0, 0
and 1, so 0.

- **A 2-CNF is closed under majority**: whenever it allows three states, it
  allows their majority. *Classical* (Schaefer 1978), and the reason is short.
  Each clause of a 2-CNF mentions at most two variables, say x and y, and
  rules out one combination of their values. At least two of the three states
  agree with the majority on x, and at least two agree with it on y, so one of
  the three agrees with it on both. That state is allowed, so it does not have
  the ruled-out combination, and neither does the majority.
- **Witnesses do not help.** When a system is closed under majority, so is its
  shadow on any set of variables: complete three allowed states of the shadow
  to allowed states of the system, and the majority of the completions
  completes the majority of the three. So a 2-CNF stays closed under majority
  with any witnesses forgotten.
- **No knot on three variables is closed under majority.** Take an excluded
  state of a knot, such as the atom's 110. Its three neighbours, 010, 100 and
  111, are allowed (lesson 2.2), and their majority is 110 itself.

So no 2-CNF, with or without witnesses, defines the atom or any other knot on
three variables. The next lesson states the general theorem, and its positive
counterpart for three-place rules.

### 3.2 Pairs cannot make a knot; three places can

**The intuition.** Whatever a two-place rule says, it says about a pair. A
system of two-place rules that must all hold is therefore known from its
pairs. A knot shows nothing in any pair, so pairs can never pin one down.
Three-place rules can.

- **Classical.** Relations definable by 2-CNF, even with witnesses quantified
  away, are exactly those closed under the majority operation (Schaefer
  1978). A majority-closed relation is the conjunction of its two-variable
  projections (Baker and Pixley 1975).
- **Hence no 2-CNF defines a knot.** If one did, the knot would equal the
  conjunction of its pairwise projections. Those are all unconstrained, so it
  would allow everything, contradicting K1. More witnesses do not help.
  *Proved (Lean)* for three variables directly: for any target state, take
  allowed states agreeing with it on each pair; their majority is the target
  (`no_two_cnf_defines_knot`, `majority_with_free_pairs_is_full`).
- **Width 3 binds any number of loops.** A chain of three-literal clauses
  joined by witnesses does it: `w1 ∨ ¬L1 ∨ ¬L2`, then `w2 ∨ ¬w1 ∨ ¬L3`, and so
  on, ending with `¬w(n−2) ∨ ¬Ln ∨ c`. Each witness `wi` is forced exactly when
  the loops before it are all present, so it records that they are bound.
  Naming each partial parity does the same for parity. *Proved (Lean):*
  `chain_defines_knot`, `parity_chain_defines_parity`.
- **Without witnesses, a knot needs full width.** A knot on m variables
  implies no clause on fewer than m of them, because every proper projection
  is unconstrained. *Proved (here)*; Lean checks the three-variable case
  (`no_clause_on_a_b` and its two companions).

So **3 is the exact threshold**. Width 2 is closed: pairwise in, pairwise out.
Width 3 reaches every knot.

**Reading.** Two-place rules are logic, not topology. The first place where
logic binds something that no part shows is the step from two-literal to
three-literal clauses. This is a statement about what can be *expressed*, not
about how hard anything is to compute. There are easy knots: the atom is a
Horn clause, and Horn satisfiability takes linear time (lessons 4.1 and 4.2).
So this boundary is not the boundary between P and NP, and nothing here
addresses that question.

### 3.3 The shape of a system

**Shapes.** Lesson 1.2 asked whether one set of variables is free. Asking it of
every set at once gives a picture, the system's **shape**:

- each free variable is a point;
- each free pair is an edge between two points;
- each free triple is a filled triangle;
- each free set of four is a filled tetrahedron, and so on.

**Simplicial complexes and holes.** Every part of a free set is free, since
each combination of values on the part extends to a combination on the whole
set, and that one occurs. So every side of a filled triangle is drawn too. A
collection of sets that contains every part of each of its sets is called a
**simplicial complex**, and a system's shape is one. Topology studies such
shapes, and in particular their **holes**: a loop of free sets with nothing
free filling it, or in higher dimensions a hollow sphere of them.

**Three examples.** On three variables:

- with no rule at all, every set is free, and the shape is a filled triangle;
- under the atom, the three pairs are free but the triple is not, so the shape
  is a hollow triangle, three edges around a missing face. That is a circle, a
  hole of dimension one;
- under A ≠ B, with c unused, the edge between A and B is missing, so the
  shape is two edges meeting at c, with no hole.

**Flags and joins.** Two terms from topology appear in the next lesson. A shape
is a **flag** shape when every set whose pairs are all edges is filled in, so
that its pairs decide all of it. Two systems on separate variables, set side by
side, have the **join** of their shapes as their shape: a set is free when its
part in each system is free. The join of two circles is a three-dimensional
sphere (*Classical*).

### 3.4 Holes and knots

**Hole or knot.** The two words are easy to confuse. A system's **shape** is
built from what it leaves free: each free distinction is a point, each pair
that takes all four combinations is an edge, each free triple is a filled
triangle, and so on. A **hole** is any gap in that shape. A **knot** is the
smallest kind of hole: a set whose every part is free, but which is not free
itself.

```text
a knot: an empty triangle            a hole made by ties: a square

        A                               a ──── b
       / \                              │      │
      B ─ c                             d ──── c

all three pairs are free;            the pairs a–c and b–d are tied, so
A, B and c together are not          those edges are missing; the gap is
                                     made of missing edges
```

- **Pairwise rules make only "flag" shapes.** In a 2-CNF system a set is free
  exactly when all its pairs are free. So two-place rules can make holes, as
  the square shows, but never an empty triangle. *Checked* (`SpaceTest`; of
  399 random 2-clause systems on six variables, 29 have holes and none has an
  empty triangle).
- **Every knot is a hole, but not every hole is a knot.** To tell whether
  things are bound, look at the knots, not at the size of the holes. Two
  unrelated knots side by side leave a three-dimensional hole, because the
  join of two circles is a 3-sphere, yet nothing binds them.
- **Logic allows every shape.** Every simplicial complex is the shape of some
  system. *Proved (Lean):* `every_complex_is_a_nerve` in `LoopNerve.lean`
  builds one from loops whose contacts permute witness values.

**Reading.** Logic gives intrinsic holes, paths and separation, but it selects
no space. Whatever space there is has to come from a law. Which law gives a
shape that looks like a space of low dimension is open (lesson 7.2,
question 1).

```bash
PYTHONPATH=tools python3 -m knotlab space
```

## Chapter 4. How bindings behave

Knots can be read as requirements or as choices, can come from rules that
compete, and can be joined into rings and networks. The chapter first fixes
the words for easy and hard questions, which these behaviours are measured by.

### 4.1 Easy and hard questions

Some questions about a system can be answered quickly, and some, as far as
anyone knows, cannot. This lesson fixes the words that the rest of the guide
uses for the difference.

- **Time is counted against size.** The size of a system is its number of
  variables and rules. A method runs in **linear time** when its work grows in
  proportion to the size, and in **polynomial time** when the work grows at
  most like a fixed power of the size, such as its square. Questions that
  polynomial time answers form the class **P**, and they count as easy.
- **Deciding** asks whether a system allows any state at all. For a 2-CNF it
  takes linear time (Aspvall, Plass and Tarjan 1979): each loop of
  implications forces its members to be equal, as in lesson 1.4, and the
  system allows nothing exactly when some loop forces a variable to equal its
  own negation. For a 3-CNF it is **NP-complete** (Cook 1971). An allowed
  state, once found, is easy to check, and every question whose answers are
  easy to check translates into this one, so a fast method for it would give
  fast methods for all of them. Such questions form the class **NP**, and a
  question into which all of NP translates is **NP-hard**. Whether P equals NP
  is open, and this guide does not address it.
- **Expressing is not computing.** Lesson 3.2 showed that three places are
  needed to express a knot, but expressing a relation and deciding a system
  of such relations are different questions. Lessons 4.2 and 4.3 show both an
  easy and a hard side.

### 4.2 Requirement and choice

**Worlds.** This lesson reads 1 as "exists" and 0 as "does not exist". A
**world** is then the set of things that exist in an allowed state: the
variables that are 1. A world is **minimal** when no other allowed world lies
inside it, and **least** when it lies inside every allowed world. Requirements
are written as **Horn clauses**, clauses with at most one un-negated letter,
such as ¬A ∨ ¬B ∨ c.

- **A requirement** says what must exist when other things do: `A ∧ B → c`.
  A system of requirements has exactly one least world, and propagation finds
  it in linear time. *Classical:* van Emden and Kowalski 1976; Dowling and
  Gallier 1984.
- **Computation is a forced world.** Carry each bit as which of two things
  exists, "x = 0" or "x = 1". Every gate then becomes four atoms, so every
  circuit runs as a least world. *Classical:* Horn satisfiability and monotone
  circuit value are complete for polynomial time. *Checked:* 4-bit addition
  comes out right for all 256 input pairs.
- **A choice** says that when something exists, one of several things must:
  `c → A ∨ B`. With c present there are two minimal worlds, {A} and {B}, and
  nothing ranks them.
- **Requirement and choice are one knot read two ways.** "A and B require c"
  becomes "c requires A or B" when false is read as "exists". 16 of the 34
  two-loop knots are a pure requirement under one reading and a pure choice
  under the other. The other 18, parity among them, offer choices under both.
  *Checked* (`knotlab choice`).
- **Knots never select.** Every variable of a knot takes both values, and
  fixing one loop's value removes it from the binding.

Propagation, in the first point, starts from the facts and adds whatever a
requirement forces until nothing changes. Complete for polynomial time, in the
second, means that every question in P translates into these two.

**Reading.** Requirements never select, since their world is unique. A choice
leaves alternatives that the constraints do not rank. The program's
interpretive stance is that coherent alternatives are equally real, with no
global selector. The mathematics shows only that the constraints do not
select. It neither proves nor refutes that stance.

### 4.3 Knots from competing pairs

**Conjunction and competition.** Two-place rules can be combined in two ways.
Under **conjunction** every rule must hold, and, as lesson 3.2 shows, pairs
then never make a knot. Under **competition** the rules are preferences, and
the allowed states are those that break the fewest. A state's **energy** counts
the preferences it breaks, possibly with weights, so under competition the
allowed states are those of least energy.

**The intuition.** Ask three distinctions to differ pairwise. Around the
triangle the differences cannot all hold, so the preferences are
*frustrated*. The states that break exactly one preference are the six
not-all-equal states, and those form a knot. Competition can make a knot from
pairs, but only this kind.

- **Exactly four knots come from competing pairs on three variables.** A knot
  on three variables is the set of least states of an energy with only one-
  and two-variable terms exactly when its excluded states are an opposite
  pair. These are the four not-all-equal relations, the frustrated triangles.
- **None on four or more variables.**
- **With hidden variables, competing pairs make every knot.** Ten 2-clauses
  and one hidden variable have the clause `x ∨ y ∨ z` as their best states.
  *Classical:* this is the gadget behind the NP-hardness of MAX-2-SAT (Garey,
  Johnson and Stockmeyer 1976).

*Proved (Lean):* `CompetitionKernel.lean` (`three_variable_classification`,
`no_knot_beyond_three`, `every_relation_by_gadgets`, and 16 more). The
three-variable case is an instance of a known criterion for least sets of
pairwise energies (faces of the correlation polytope; Rauh, Kahle and Ay
2011). We have not found the four-variable statement in print.

MAX-2-SAT, in the third point, asks for a state that satisfies as many
two-literal clauses as possible.

**Why only four** (*proved here*). Every function of Boolean variables is a
unique polynomial with one coefficient per set of variables. A pairwise energy
has no coefficient on three variables. On three variables that top coefficient
is the energy summed over the states with an odd number of ones, minus the sum
over the rest. Shift the energy so its least value is zero. Then only the
excluded states count, each positively, so if they all had the same parity the
top coefficient would not vanish. A knot's excluded states are never
neighbours, and two of opposite parity must be opposite. So the excluded
states are one opposite pair.

For two variables, for example, every function is p + q·A + r·B + s·A·B for
exactly one choice of the numbers p, q, r and s, and s is its coefficient on
the pair.

**Reading.** What a knot certifies depends on what is hidden. With every
variable visible, a knot other than the frustrated triangles cannot come from
pairwise terms, even competing ones. With hidden variables, a knot certifies
only that the rules are not pairwise rules that must all hold.

### 4.4 Which knots remember a loop

**Rings of knots.** A ring of knots is built from copies of one knot. Each copy
has its own distinction x and two witnesses, one shared with the copy before it
and one with the copy after it, and the last copy shares a witness with the
first. Take parity copies, x ⊕ w_in ⊕ w_out = 0: a copy passes the incoming
witness on unchanged when its x is 0, and flipped when its x is 1. Around the
ring the witness has to come back to itself, so the number of flips is even.
With the witnesses forgotten, the ring allows exactly the patterns of x's with
an even number of 1s, which is one parity knot on all of them.

**The intuition.** Join copies of a knot into a ring, each passing a witness
to the next and the last passing back to the first. Then forget the
witnesses. Does the ring still remember that it is a loop? Only if going
around can flip something, and only a contact that acts like a group element
can flip without losing information.

*Proved (Lean):* `RingKernel.lean`, all under the forgetting reading.

- **Transfers.** For fixed values of a copy's other distinctions, the copy
  passes its witness through a 2×2 table. Every such table of a knot is a
  permutation (identity or swap), or misses at most one pair
  (`transfer_cases`).
- **A ring excludes exactly the odd loops.** A ring rules out a pattern
  exactly when every table along it is a permutation and an odd number of
  them swap (`ring_excludes_iff`). So a ring of knots composes into a knot or
  into nothing (`ring_one_flip`).
- **Only parity carries a loop at full strength.** A knot whose tables are all
  permutations is a parity relation (`all_permutations_iff_parity`). A ring of
  parity knots keeps one full bit at every length.
- **Other knots fade.** Their share of excluded patterns shrinks exponentially
  with the ring's length. A ring of not-all-equal knots forgets the loop
  completely.

```bash
PYTHONPATH=tools python3 -m knotlab rings
```

### 4.5 What networks of loops remember

**From rings to networks.** Networks extend this. Put a witness at each vertex
of a graph, and let each edge carry **permutation contact**: a permutation of
the witness values takes the witness at one end to the witness at the other. A
ring is the case of a single cycle. Composing the permutations around a closed
walk gives the walk's **holonomy**, and a value that a permutation leaves
unchanged is one of its **fixed points**. A loop can also be given a selector,
so that it either passes the witness unchanged or applies its holonomy, and a
set of loops is switched on together when all their selectors can be on at
once. The **nerve** of a family of sets is the shape with one point for each
set and a face for each group of sets that share an element.

*Proved (Lean):* `LoopNerve.lean`.

- **Free contact records each loop separately.** When a contact's every
  holonomy that fixes one value fixes all of them, as for parity or addition
  mod q, no two loops ever tie (`free_contact_binds_nothing`). Each
  independent loop then carries its own class, a first cohomology class.
- **Contact with fixed points binds loops, into atoms.** The loops a network
  can switch on together form the nerve of the holonomies' fixed-point sets
  (`shape_is_nerve`). A minimal set of loops that cannot all be on is a knot
  among loops that excludes exactly one pattern: an atom
  (`minimal_nonface_is_knot`).
- **Binding costs witness values.** A knot among k loops needs k + 1 witness
  values (`knot_needs_more_values`). Boolean witnesses cannot even tie two
  loops (`boolean_contact_never_ties`).

The first cohomology class of the first point amounts to one value of the
contact's group for each independent loop of the network.

**Classical background.** Composing tables is the transfer-matrix method. A
parity ring with an odd number of swaps is Tseitin's parity contradiction on a
cycle. Local consistency methods fail exactly on constraints that can simulate
equations over a group (Barto and Kozik 2009), the same dividing line. The
mathematics here is elementary. The reading is ours.

**Reading.** The two extreme knots play opposite roles. Parity, which hides
the most, carries a single loop at full strength. The atom, which hides the
least, binds loops together through fixed points. A law can keep a lasting
record of its own loops only if its contacts act as group elements.

```bash
PYTHONPATH=tools python3 -m knotlab holonomy
```

## Chapter 5. Depth

A network of knots can allow nothing while every small window of it looks
consistent. This chapter asks how much of the network a proof has to hold at
once to see that nothing is allowed.

### 5.1 Proving that nothing is allowed

**Refutations.** When a system allows no state at all, a refutation is a proof
of that fact: a sequence of steps, each of them following from the rules, that
ends in a contradiction. Proof systems differ in what one step may do, and the
cost that matters here is how much a single step must hold at once.

**Proofs by algebra.** Algebra gives the proof system that the next lesson uses.

- **Rules become equations.** Each variable x obeys x·x = x, so its only
  values are 0 and 1. A clause becomes a product that is 0 exactly when the
  clause holds: ¬A ∨ ¬B ∨ c becomes A·B·(1 − c) = 0, since the product is 1 at
  110 and 0 everywhere else.
- **A Nullstellensatz refutation** multiplies each equation by some polynomial
  and adds the results so that everything cancels except the number 1. No
  state can make every equation 0 and the sum 1, so nothing is allowed. Its
  **degree** is the largest degree among the products it adds: roughly, the
  most variables it must multiply together in one term. A refutation of low
  degree sees the contradiction through small windows. *Classical:* the
  Nullstellensatz proof system (Beame, Impagliazzo, Krajíček, Pitassi and
  Pudlák 1996).
- **The numbers matter.** The coefficients come from a field: a number system
  with addition, subtraction, multiplication and division, such as the
  rational numbers or arithmetic mod a prime. A field has **characteristic
  2** when 1 + 1 = 0 in it, as in arithmetic mod 2, which is the arithmetic of
  parity. The rational numbers, and arithmetic mod 3 or mod 5, have other
  characteristics.

### 5.2 How deep a hole is

**The intuition.** Put a parity knot at every vertex of a graph, sharing the
graph's edges as distinctions: each vertex asks its edges to sum to a charge.
Such a network is impossible exactly when the total charge is odd. That is a
hole, but every small window of the network looks perfectly consistent, since
the odd unit of charge can be pushed anywhere by flipping edges along a path.
So how much of the network must an observer hold at once to see the hole? The
answer is a width of the graph: the charge has to be carried across the widest
boundary of the best sweep.

These networks are Tseitin formulas, and "how much an observer must hold"
becomes the degree of a refutation.

**Graph terms.** Three terms about graphs appear below. Lay a graph's vertices
out in a row: each gap in the row is crossed by some edges, the layout's width
is the most edges crossing one gap, and the **cutwidth** is the least width of
any layout. The **maximum degree** is the most edges at one vertex. The **±1
encoding** writes each bit as +1 or −1 instead of 0 or 1.

- **Reasoning mod 2 sees the hole at once.** Summing every vertex's equation
  counts each edge twice, so a refutation of the size of one knot exists.
- **Every other field needs the toggle width.** *Proved (note):* over every
  field of characteristic other than 2, the Nullstellensatz degree of the
  Tseitin formula, written clause by clause, equals the **toggle width** of
  the graph: the cheapest way to grow the empty vertex set into the whole
  graph by adding or removing one vertex at a time, where each step costs the
  edges it must keep track of. On graphs of maximum degree at most three this
  is exactly **cutwidth + 1**. In the ±1 encoding, with degree measured after
  reduction, it is exactly the cutwidth. The upper bound sweeps the charge
  across a layout, and the lower bound is a design whose values are signed
  sums over cuts.
  See [notes/tseitin-nullstellensatz-degree](notes/tseitin-nullstellensatz-degree/).

**Reading.** A hidden bit has a depth: the width an observer must hold to
carry it to where it shows. Holes made by loops of witnesses (lesson 4.5) are
shallow, and local reasoning sees them. Holes made by charges are as deep as
the graph's layout is wide, unless the reasoning computes in the charge's own
group. Related results for other proof systems, with tree layouts in place of
linear ones, are in the full record: see "Holes, depth and Tseitin proof
complexity" in [RESULTS.md](RESULTS.md).

```bash
PYTHONPATH=tools python3 -m knotlab depth
```

## Chapter 6. Counting

Deciding asks whether a network allows any world; counting asks how many
worlds it allows. This chapter sets up the words for counting, then reports
where counting turns hard.

### 6.1 Counting worlds

Deciding whether a network of knots allows any world can be easy while
counting its worlds is hard. Two notes in this repository locate where
counting turns hard.

**Counting words.** The words used for counting follow lesson 4.1. A world here
is an allowed state, as in lesson 4.2.

- **#P** ("sharp P") is the class of counting questions whose objects are easy
  to check, such as how many states a CNF allows, or how many perfect
  matchings a graph has (ways of pairing up all its vertices along its edges).
  A counting question is **#P-hard** when every question in #P translates into
  it. A polynomial-time method for a #P-hard count would also decide every
  question in NP quickly, so none is expected.
- **Counting can be hard when deciding is easy.** Deciding a 2-CNF takes linear
  time, but counting the states it allows is #P-hard; deciding whether a graph
  has a perfect matching takes polynomial time (Edmonds 1965), but counting
  its perfect matchings is #P-hard. *Classical:* Valiant 1979.
- **Planar graphs are the classical exception.** On a graph drawn in the plane
  without crossings, perfect matchings are counted in polynomial time by a
  determinant-like formula, the Pfaffian, once the edges are suitably signed
  (Kasteleyn 1967). A graph that has such a signing is called **Pfaffian**.
  Every planar graph is Pfaffian, and so are some others.

### 6.2 The worlds of not-all-equal knots

**Hypergraphs and colourings.** A hypergraph has points and edges, where an
edge may contain any number of points. In a **3-uniform** hypergraph every edge
has three points, and in a **3-regular** one every point lies in three edges. A
proper **2-colouring** colours each point black or white so that no edge has
all three points the same colour, which is the not-all-equal rule on every
edge. The **incidence graph** has a vertex for each point and one for each
edge, and joins each point to the edges that contain it. The note also signs
some incidences: at a signed incidence, the edge sees the point's colour
reversed. A twist, roughly, is where the signs differ from a Pfaffian signing,
and the note defines when twists branch.

**What the note proves.** A 3-regular 3-uniform hypergraph is a network of
not-all-equal knots in which every distinction sits in exactly three knots. Its
proper 2-colourings are the network's worlds. Networks with no world at all are
where these knots close up on themselves, and the program calls them three-fold
spaces. Counting is #P-hard in general (Fan and Cai) and easy when the
incidence graph is planar (Valiant). The note studies the class in between,
Pfaffian incidence graphs, which contains every network with no world. *Proved
(note):*

- remove any one knot from a connected network with no world, and the worlds
  of what is left can be counted in polynomial time;
- counting stays polynomial under twists that do not branch;
- counting becomes #P-hard once twists branch. It stays #P-hard without any
  signs, and even when the incidence graph is a Pfaffian brace.

See
[notes/pfaffian-hypergraph-colourings](notes/pfaffian-hypergraph-colourings/).

### 6.3 Patterns in three dimensions

**Spaces and their groups.** A 3-manifold is a space that looks like ordinary
three-dimensional space near each of its points, such as the space around a
knotted rope. Its **fundamental group** records its loops: two loops count as
the same when one can be slid into the other, and two loops combine by running
one after the other. A **homomorphism** from the fundamental group to a finite
group labels every loop with an element of the group so that running two loops
one after the other multiplies their labels. For the space around a knot drawn
as a diagram, such a labelling is a colouring of the diagram's arcs that obeys
one rule at each crossing. A group is **solvable** when it is built in finitely
many layers from commutative groups. S₃ is the group of the six permutations of
three things, and S₄ that of the 24 permutations of four. A group's Fitting
height counts its layers of a particular kind, the nilpotent ones, which are
the groups closest to commutative; Heisenberg groups are the simplest nilpotent
groups that are not commutative. A **link** is several closed loops of rope,
possibly tangled with one another, and a knot is a link with one loop.

**What the note proves.** When the laws counted are group laws on a 3-manifold,
counting worlds means counting homomorphisms from its fundamental group to a
finite group. Rowell conjectured in 2009 that this count is computable in
polynomial time for solvable groups. *Proved (note):* unless every #P function
is computable in polynomial time, the conjecture fails. On links it fails
already for S₃. On knots it fails for S₄, the smallest group for which it can,
and for some groups of Fitting height two. For Heisenberg-type groups the note
proves an exact dividing line. See
[notes/knot-group-counting](notes/knot-group-counting/).

**Surgery and characters.** Two more terms appear in the reading below. Surgery
on a link cuts out a thin tube around it and glues the tube back differently,
which makes a new 3-manifold. A character of a commutative group maps it to the
complex numbers of absolute value 1, preserving multiplication.

**Reading.** In the Heisenberg families, hardness appears exactly when the
twisted obstruction joins three nontrivial characters at once, which
three-component, pairwise-unlinked (Borromean) surgeries supply. Everything
pairwise stays countable. This echoes the K2 pattern of lesson 2.1, but it is a
statement about counting complexity, not about knots in our sense. The knot
test cannot tell hard groups from easy ones: every group law, read as the
relation x·y = z, is constrained as a whole and free in every pair.

## Chapter 7. Sources and questions

What the guide takes from classical mathematics, what it adds, and what
remains open.

### 7.1 What is classical and what is ours

- **Classical:**
  - 2-CNF relations are the majority-closed ones (Schaefer 1978) and are
    determined by their pairs (Baker and Pixley 1975);
  - three-place relations build every relation while two-place ones do not
    (Peirce's reduction thesis);
  - least worlds of Horn clauses (van Emden and Kowalski 1976);
  - Post's lattice and the Galois connection behind it (Post 1941; Geiger
    1968; Bodnarčuk, Kalužnin, Kotov and Romov 1969);
  - the compactness theorem;
  - frustration (Toulouse 1977) and the MAX-2-SAT gadget (Garey, Johnson and
    Stockmeyer 1976);
  - Tseitin formulas and their parity contradictions (Tseitin 1968);
  - Borromean and Brunnian links in topology;
  - the background that lessons 4.1, 5.1 and 6.1 define: 2-CNF decided in
    linear time (Aspvall, Plass and Tarjan 1979) and 3-CNF NP-complete (Cook
    1971), counting perfect matchings and 2-CNF solutions #P-hard (Valiant
    1979), planar matchings counted by Pfaffians (Kasteleyn 1967), and the
    Nullstellensatz proof system (Beame, Impagliazzo, Krajíček, Pitassi and
    Pudlák 1996).
- **Ours, as reading:**
  - the knot test K1–K3, read on allowed states with erasure as forgetting;
  - a binding is a constraint with no trace in any part, which vanishes when
    either loop is erased;
  - loops, their open distinctions and their witnesses are the units;
  - emergence begins at the first such binding;
  - distinctions are the material and atoms are the bonds;
  - a hidden bit has a depth.
- **Ours, as results.** The classifications and constants marked as proved
  here or in Lean are elementary. Several are classical facts in new language,
  and we give sources where we know them. The three notes contain results that
  are new as far as our searches found, and each note states its own novelty
  and folklore risk. See [FINDINGS.md](FINDINGS.md).
- **Not implied:**
  - Requirements alone run in linear time, and requirements with choice are
    NP-complete. That locates where hardness enters, but says nothing about
    whether P equals NP.
  - Nothing here is physics.
  - The interpretation that coherent alternatives are co-real is an
    interpretation, and nothing is proved from it.

### 7.2 Open questions

1. **Space from a law.** Logic allows every shape. Which uniform, local law,
   not written on a space in advance, gives a shape that looks like a space of
   low dimension? One necessary condition is known: a law keeps a lasting
   record of its loops only if its contacts act as group elements (lessons
   4.4 and 4.5).
2. **Dynamics.** Are loops better modelled as processes whose outputs over
   time are the data, and does the static test survive that change?
3. **Limits.** No set of finite clauses binds infinitely many loops into one
   contact (by compactness). Does the program need a limit rule that does?
4. **Competition.** If least-violation states count as allowed, frustrated
   pairs make knots (lesson 4.3). Should they count?

## Glossary

- **Distinction.** Two alternatives of which exactly one holds: one bit
  (lesson 1.1).
- **Joint state.** A value for every variable, written as a string such as 110
  (lesson 1.1).
- **Relation.** The set of joint states a system of rules allows. Two systems
  that allow the same states are the same relation (lesson 1.2).
- **Free.** A set of variables is free when every combination of their values
  occurs in some allowed state. The guide also calls such a set
  **unconstrained**, and any other set **constrained** (lesson 1.2).
- **Clause.** An "or" of letters, each possibly negated, such as
  `¬A ∨ ¬B ∨ c`. It rules out one assignment of its own variables, and a list
  of clauses that must all hold is a **CNF** (lesson 1.2).
- **Emergence.** What a system of rules shows as a whole and none of its rules
  shows alone, as the Game of Life's patterns do on a grid (lesson 1.3). The
  program places the first emergence at the first knot.
- **Loop.** A logical structure that leaves a distinction open (lesson 1.4).
- **Contact.** The variable through which loops are bound (lesson 1.4).
- **Atom.** The knot `¬A ∨ ¬B ∨ c`: the smallest bond. It is also written
  A ∧ B → c, or A, B → c, and read "A and B together demand c": it forbids
  only the state with A and B but not c (lesson 1.5).
- **Forgetting.** Ignoring a variable: a state of the others stays allowed when
  some value of the forgotten one completes it. What remains is the
  **projection**, or **shadow**, on the others (lesson 1.6).
- **Witness.** An auxiliary variable that reports on something, such as
  whether two loops are bound. Witnesses are quantified away before a verdict
  (lesson 1.6).
- **Knot.** A relation that is constrained as a whole and unconstrained in
  every part (lesson 2.1).
- **Hub.** One variable shared by several separate relations, such as
  `(¬A ∨ c) ∧ (¬B ∨ c)`. Sharing identity is not a binding (lesson 2.1).
- **Majority.** The state that takes, in each variable, the value at least two
  of three given states take. Systems of two-place rules are closed under it,
  and knots are not (lesson 3.1).
- **Shape.** The simplicial complex of sets of distinctions a system leaves
  free. A **hole** is a gap in it, and a knot is the smallest kind of hole
  (lesson 3.3). In the broad sense of lesson 1.7, any structure that rules make.
- **World.** With 1 read as "exists", the set of things that exist in an
  allowed state (lesson 4.2).
- **Requirement.** A rule saying what must exist when other things do, such as
  `A ∧ B → c`. A **choice** says that when something exists, one of several
  things must, such as `c → A ∨ B` (lesson 4.2).
- **Refutation.** A proof that a system allows no state at all (lesson 5.1).
- **Depth.** How much of a network an observer must hold at once to see a
  hole in it (lesson 5.2).
