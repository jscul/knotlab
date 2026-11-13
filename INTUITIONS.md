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

**A note on words.** The program is trying to build space, so it cannot yet
use words that take space for granted. Triangle, torus, sphere, plane, surface,
edge and face name things that sit in a space of two or three dimensions, and
no such space has been built here. The guide therefore names its own objects
by distinctions, knots and counts, and uses a spatial word only as the
literature's name for a classical object it cites, for a picture it says
outright is drawn, or for space, distance and dimension themselves, each with
its native definition. It also gives each word one meaning and each meaning
one word. Lesson 1.1 states both rules. The [glossary](#glossary) gives every
word's meaning and the intuition behind it, the literature's name for each
object under "Words for space", and the words that earlier records used in two
senses under "One word, one meaning". Spatial reality, if it comes, is to come
later, built in simulations from these rules.

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
found, and lesson 4.7 reports statements that a bounded search did not find,
built with known tools. Lesson 7.1 lists what is classical and what is ours.

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
  - [1.7 What rules make](#17-what-rules-make)
- [Chapter 2. The knot test](#chapter-2-the-knot-test)
  - [2.1 The knot test](#21-the-knot-test)
  - [2.2 Knots on the cube](#22-knots-on-the-cube)
  - [2.3 What a knot hides](#23-what-a-knot-hides)
- [Chapter 3. Pairs and three places](#chapter-3-pairs-and-three-places)
  - [3.1 Two-place rules and the majority vote](#31-two-place-rules-and-the-majority-vote)
  - [3.2 Pairs cannot make a knot; three places can](#32-pairs-cannot-make-a-knot-three-places-can)
  - [3.3 The free complex of a system](#33-the-free-complex-of-a-system)
  - [3.4 Holes and knots](#34-holes-and-knots)
- [Chapter 4. How bindings behave](#chapter-4-how-bindings-behave)
  - [4.1 Easy and hard questions](#41-easy-and-hard-questions)
  - [4.2 Requirement and choice](#42-requirement-and-choice)
  - [4.3 Knots from competing pairs](#43-knots-from-competing-pairs)
  - [4.4 Which knots remember a loop](#44-which-knots-remember-a-loop)
  - [4.5 What networks of loops remember](#45-what-networks-of-loops-remember)
  - [4.6 Dimensions from rules](#46-dimensions-from-rules)
  - [4.7 Knots alone](#47-knots-alone)
- [Chapter 5. Depth](#chapter-5-depth)
  - [5.1 Proving that nothing is allowed](#51-proving-that-nothing-is-allowed)
  - [5.2 How deep a hole is](#52-how-deep-a-hole-is)
- [Chapter 6. Counting](#chapter-6-counting)
  - [6.1 Counting worlds](#61-counting-worlds)
  - [6.2 The worlds of not-all-equal knots](#62-the-worlds-of-not-all-equal-knots)
  - [6.3 Counting on classical 3-manifolds](#63-counting-on-classical-3-manifolds)
- [Chapter 7. Sources and questions](#chapter-7-sources-and-questions)
  - [7.1 What is classical and what is ours](#71-what-is-classical-and-what-is-ours)
  - [7.2 Open questions](#72-open-questions)
  - [7.3 Every meeting pattern, none chosen](#73-every-meeting-pattern-none-chosen)
- [Glossary](#glossary)

## Chapter 1. Bits and rules

Everything later is built from bits and from rules about them. This chapter
sets up that vocabulary and its notation, reads the Game of Life as such rules,
states the picture the program starts from, reads the smallest rule that binds
two loops, and ends with what rules make.

### 1.1 Distinctions and states

**Distinctions.** Everything in this guide is built from one material, the
distinction: two alternatives of which exactly one holds. A distinction is one
bit, and its two alternatives are written 0 and 1. Nothing else is assumed.
There is no space, no order and no number beyond the two values.

**Words for space.** Because no space is assumed, the guide does not call its
objects triangles, tori, spheres, planes, surfaces, edges or faces: those words
belong to a space of two or three dimensions that the program has not built.
It names them by distinctions, by the rules that bind distinctions, and by
counts. The rule that lesson 2.1 calls a knot is not a triangle, and the
patterns that knots form by sharing distinctions (lesson 2.1) are not
surfaces, even where the literature draws them as surfaces.

A spatial word appears in only three ways:

- as the literature's name for a classical object the guide cites, such as a
  planar graph or a 3-manifold, marked as that object and not ours;
- for a picture the guide says outright is drawn, such as the cube of states
  below or the grid of the Game of Life;
- as space, distance or dimension, the things the program is trying to build,
  each with its native definition, such as bond distance (lesson 4.6).

**One word, one meaning.** Each word in the guide has one meaning, and each
meaning has one word. Where earlier records used a word in two senses, such as
"world" for an allowed state and for a pattern of knots, the guide keeps one
sense and gives the other a word of its own. The [glossary](#glossary) gives
every word's meaning and the intuition behind it, the literature's spatial
name for each object under "Words for space", so that results stay findable in
the literature, and the split words under "One word, one meaning". Spatial
reality is what the program hopes to reach later, by building simulations from
these rules.

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

**The cube of states.** Link two states when they differ in exactly one
variable. The eight states and their twelve links form the **flip graph** of
three variables. It helps to draw it, and the usual drawing is a cube, the
cube of states: each state is drawn as a corner, each link as
an edge, and each variable as one direction, with A running from left to
right, B from front to back, and c from bottom to top. The cube is only the
drawing; what it shows is which states differ in one variable.

```text
          011 ─────── 111
         ╱ │         ╱ │
      001 ─────── 101  │
       │  010 ─────│─ 110
       │ ╱         │ ╱
      000 ─────── 100
```

Two states are **neighbours**, linked in the flip graph, when they differ in
exactly one variable, as 110 and 111 do. They are **opposite** when they
differ in all three, as 000 and 111 do. Chapters 1 to 3 read many patterns
off this drawing. It is a picture of the states, not a space in which the
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
appear in rules with any others; lesson 3.4 shows that every simplicial
complex, of any dimension, is the free complex of some system of rules. So
Life shows patterns
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

**Chains and loops, state by state.** The program starts from a picture of
chains, loops and what lies between loops (the owner first called the chains
lines). Each part of the picture is a statement about small
systems of rules like those of lesson 1.2, so it can be checked state by
state. With states written in the order x, y, z:

- the chain x → y, y → z allows 000, 001, 011 and 111: once a variable is 1,
  every later one is 1, so the chain only orders its members;
- closing the chain into a loop with z → x leaves 000 and 111: the three are
  forced to be equal, so the loop has collapsed to one free bit, as if it were
  a single distinction;
- a loop of "equal" and "differ" steps does the same or worse:
  x = y, y ≠ z, z ≠ x allows 001 and 110, one free bit again, and
  x = y, y = z, z ≠ x allows nothing.

The picture itself:

- **A chain is not enough.** A chain of implications only orders its
  members, and strings with loose ends can always be rearranged into one
  another.
- **A single loop is not enough.** A loop of implications forces all its
  members to be equal, so it collapses to a single distinction. A loop of
  "equal" and "unequal" steps collapses to one free bit, or contradicts itself.
- **What is real is what lies between bound loops.** The binding belongs to
  the pair, not to either loop. No part smaller than the whole shows it, and
  erasing either loop removes it.
- **A loop is a logical structure, not a spatial one.** What it brings to a
  binding is an *open distinction*: a bit it leaves free.

**From loops to A, B and c.** The strings of the first item are a
comparison with rope: a tangle in a string with loose ends can always be slid
off an end, so only closed loops stay knotted. From here on a loop takes part
only through its open distinction. Two loops bring two distinctions, written A
and B, and what binds them is one more variable, the **contact** c. The next
lesson reads the smallest rule that binds them.

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

### 1.7 What rules make

**The word.** The owner's word for any structure that rules make is "shape".
In his words (8 November 2026): "things like
triangles/lines are essentially shapes, and they can run on forever. You can
have an infinitely large circle, and different infinity size circles as well.
Same thing with human minds. [W]e're essentially just a logical shape, or a
pattern that repeats as consciousness in other humans. Our genome is a shape
just like it." For the program's own objects the guide does not use the word:
since 11 November 2026 it says **meeting pattern** for which knots share which
distinctions (lesson 2.1), and it keeps "shape" in the owner's own words only.

**More than a pattern.** "People refer to these as 'patterns'. They are, but it's
missing the root of it. Saying that these 'emergent structures' are shapes
allows us to understand them in the context of logic, from which we can create
shapes. They are rules, and rules within rules." So, in the owner's sense, a
"shape" is a pattern together with the rules that make it. A glider is a
pattern on Life's board; as a "shape" it is the glider together with the rule
that carries it along (lesson 1.3).

**Rules within rules.** Naming a pattern gives it a new variable, a witness,
and the naming is itself a three-place rule (lessons 1.6 and 3.2), so rules
about rules need no new kind of rule. The record also finds a limit. Built from
one three-place law, towers of patterns of patterns keep only parity: every
other law reaches the free relation, which constrains nothing, within three
levels ([GEOMETRY-LAW-20261029-001](research/GEOMETRY-LAW-20261029-001/geometry_from_a_law.md)).

**Structures that run on forever.** In the owner's words, a line has no end
and a circle can be as large as you like. The record has a meeting pattern of
this kind built with nothing drawn: a rule that grows only at knots holding two loose ends grows
an endless chain from a single knot, along which bond distance (lesson 4.6)
counts one per step, while a part with no loose ends freezes
([OPEN-END-GROWTH-20261107-001](research/OPEN-END-GROWTH-20261107-001/open_end_growth.md)).
The literature's name for such a chain is the number line. The record's
circles are drawn: on a layout given in advance, the distinctions within a
fixed bond distance of one of them are marked, and their outline is drawn.
That outline depends on the law. Periodic layouts give polygons, whose ratio of
perimeter to diameter (π, in Gołąb's sense) is a rational number, and an
exactly round outline came from a random layout with no preferred direction
([LOGIC-CIRCLE-20261107-001](research/LOGIC-CIRCLE-20261107-001/logic_circle.md)).

**Every bond is finite.** A meeting pattern can run on forever, but each bond
in it joins finitely many distinctions. No system of clauses binds infinitely
many loops into one knot, by the compactness theorem, so an endless chain is a
tower of finite knots ([THEORY.md](THEORY.md#every-bond-is-finite); lesson 7.2,
question 3).

**The board and true base reality.** Life's board is drawn before the game
starts (lesson 1.3). In the owner's words, "we're in a different base reality.
True base reality, where we start with nothing and have to create the
pattern." The guide's version is lesson 1.1's: nothing is assumed except
distinctions, so every structure, space included, has to come from rules
(lesson 7.2, question 1).

**Can the rule be learned?** "This doesn't have to be designed, maybe we can
learn the shape of the underlying pattern somehow. But that is to be tested."
That is open: whether a learning rule, shown what a system allows, can find
rules, and rules within rules, that make it.

**Studying a base from inside.** On 11 November 2026 the owner asked about
"the infinite series of emergent logic idea": "I feel like the emergence
there is essentially like a set of rules, and things that emerge from those
sets of rules can study those patterns in their base reality. So for example,
a set of rules may be the X and Y axis of a Cartesian base, and the rules show
up as essentially functions or meeting pattern." The guide reads the idea in
three parts. A base is knots with their rules, on a meeting pattern that may
be infinite (lesson 2.1); the rules belong to the knot pattern, and the
meeting pattern says only which knots share which distinctions. What emerges
in a base is read as bonds (lesson 4.6) and as named patterns, rules within
rules, and a named pattern can take part in further rules, so the series need
not end. And a part of a base studies the base when witnesses inside it report
on other parts (lesson 1.6). One caution comes first: a witness is part of the
same allowed states, and a knot shows only across those states, never in one
of them (lesson 2.3). Lesson 4.7 gathers what the record says of each part,
once the lessons it needs are in place.

**The free complex.** From lesson 3.3 on, the guide also studies one exact
view of what a system's rules make: the sets of variables it leaves free,
which lesson 3.3 calls the system's free complex and the literature draws as
points, edges and filled triangles. It shows the holes and knots inside what a
system allows. Earlier versions of the guide called it the system's shape;
the guide now keeps "shape" in the owner's own words only.

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

**Knots that overlap.** Knots **overlap** when they share a distinction, and
nothing says how: one knot may share distinctions with every other knot and
another with only a few, and nothing makes knots meet "along their sides", one
neighbour at a time. A distinction that several knots share is a shared
distinction, not a contact: a contact is the variable through which one knot
binds loops. Two distinctions in a common three-place knot are a **co-knotted
pair**. Which knots share which distinctions, finitely or infinitely many
knots, is their **meeting pattern**, with the knots' rules left out. Knots
with their rules, together with their meeting pattern, form a **knot
pattern**, and a knot pattern that allows at least one state is a **base**, in
the sense of the owner's "base reality": different meeting patterns, infinite
ones included, make different bases. In the owner's words (11 November 2026), loops "weave in and
out and around other loops", the whole is "immensely complicated", and the
structure that emerges is "folded" and "compressed".

**One special meeting pattern.** When every co-knotted pair of a meeting
pattern of three-place knots lies in exactly two knots, and the knots at each
distinction form one cycle, each sharing a pair with the next, the meeting
pattern is a **two-fold weave**. The literature draws it as a closed surface, and much of
the record studies it. It is one way of writing an overlap down, not what a
base is. In the owner's words, "we can have a flat structure represent the
folded compressed structure, but the flat structure and emergent structure are
different", and the program is after the emergent one.

### 2.2 Knots on the cube

**Free pairs on the cube.** The flip graph of lesson 1.1, drawn as the cube of
states, turns the knot test on three variables into a picture. Mark the states a relation excludes. A pair of
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

- The atom excludes the single state 110, so it is a knot.
- Parity A ⊕ B ⊕ c = 0 excludes the four states with an odd number of 1s:
  001, 010, 100 and 111. Changing one bit changes the number of 1s by one, so
  no two of these states are neighbours, and parity is a knot. No knot on
  three variables excludes more states than parity does.
- Not-all-equal excludes 000 and 111, which are opposite, so it is a knot.
- The common hub excludes 010, 100 and 110, and 110 is a neighbour of both of
  the others, so it is not a knot.

**Independent sets.** A set of states with no two of them neighbours is called
an independent set of the flip graph (classically, of the cube). The knots on three variables are therefore the
nonempty independent sets of excluded states. Two excluded states of a knot
never differ in just one variable: they differ in two, which is called Hamming
distance two (as 110 and 000 do), or they are opposite. The next lesson counts
these knots: there are 34, in five classes.

### 2.3 What a knot hides

**The intuition.** A knot is invisible in its parts, so the whole holds
information that no part holds. That information can be measured, and it is
small: a knot hides at most one bit.

**How it is measured.** The measure counts possibilities. A knot's pairs are
all free, so together they rule nothing out and leave all 8 states possible.
The whole allows fewer. If it allows M of the 8 states, it holds log₂(8/M) bits
that no pair holds: the atom allows 7 states and holds log₂(8/7) ≈ 0.193 bits,
and parity allows 4 and holds log₂(8/4) = 1 bit.

- **Two loops and a contact have exactly 34 knots, in five classes.** *Checked*
  against all 256 relations on three variables:

  | Excluded states | Relations | Bits the whole holds and no pair does |
  | --- | --- | --- |
  | 1 (a single three-literal clause: the atom) | 8 | 0.193 |
  | 2, opposite states | 4 | 0.415 |
  | 2, at Hamming distance two | 12 | 0.415 |
  | 3 | 8 | 0.678 |
  | 4 (parity, even or odd) | 2 | 1.000 |

  A relation on three variables has every pair free exactly when no two of
  its excluded states differ in one variable. So a knot's excluded states
  form a nonempty independent set of the flip graph (the 3-cube of the
  literature). There are 34 such sets, in five classes under the flip graph's
  48 symmetries: the renamings and negations of the three variables.
- **A knot hides at most one bit, and only parity hides a full bit.**
  *Proved (here).* Forgetting one variable of a knot on m variables leaves all
  2^(m−1) assignments of the others, and each needs at least one allowed
  state. So a knot allows at least half of its states. If it allows exactly
  half, forgetting the last variable is a bijection, so the relation is the
  graph of a function f: the last variable is fixed by the others. Two allowed
  states that differ in one variable would make that projection two-to-one,
  so f changes whenever one input bit changes. That makes f parity or its
  complement.
- **The atom is the weakest bond.** It excludes the fewest states. It is
  also what an AND gate adds to its two-place parts: a two-input gate's
  relation is pairwise exactly when the gate ignores an input, so each of the
  ten gates that use both inputs needs a three-place clause, which is an atom
  up to which value of each variable counts as present. *Checked*
  (`knotlab worlds`).

**A knot lives across states.** Every fact in this lesson is about the set of
allowed states, never about one of them, as lesson 1.2 said of being free. In
any one allowed state each distinction has one value and nothing is hidden:
the atom's state 101 is three values and no more. The knot is the fact that
110 never occurs while every pair takes all four combinations, and only the
allowed states together show it. So a part of a system that reads a knot, a
witness (lesson 1.6), reads it the same way: in each state it has one value,
and what it reports is how that value goes with the others across the states
the system allows.

**Reading.** A distinction is the material and an atom is what holds material
together. Digital hardware can build anything because its gates supply atoms.

```bash
PYTHONPATH=tools python3 -m knotlab patterns
```

## Chapter 3. Pairs and three places

Which rules can build a knot? Rules on two variables never can, and rules on
three variables always can. The chapter then collects what a system leaves
free into its free complex, and finds the knots among the complex's holes.

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

**Reading.** Two-place rules are logic, not topology. Logic first binds
something that no part shows at the step from two-literal to three-literal
clauses. This is a statement about what can be *expressed*, not
about how hard anything is to compute. There are easy knots: the atom is a
Horn clause, and Horn satisfiability takes linear time (lessons 4.1 and 4.2).
So this boundary is not the boundary between P and NP, and nothing here
addresses that question.

### 3.3 The free complex of a system

**Free complexes.** Lesson 1.2 asked whether one set of variables is free.
Asking it of every set at once gives the system's **free complex**: the
collection of all its free sets. The guide names the members of a free complex
by their size, as free singles, free pairs, free triples and so on. The
literature draws them, and the drawing is a useful picture as long as it stays
a picture:

- each free single is drawn as a point;
- each free pair as an edge between two points;
- each free triple as a filled triangle;
- each free set of four as a filled tetrahedron, and so on.

**Simplicial complexes and holes.** Every part of a free set is free, since
each combination of values on the part extends to a combination on the whole
set, and that one occurs. So every part of a free triple is in the free
complex too. A collection of sets that contains every part of each of its sets
is called a **simplicial complex**, and a system's free complex is one, which
gives it its name. Topology studies such collections, and in particular their
**holes**: a cycle of free pairs that no free sets fill in, or the same at a
larger size, which the literature draws as a hollow sphere. A hole's
dimension, in the literature's count, is one less than the size of the sets it
is made of: a cycle of free pairs is a hole of dimension one. (The guide's own
meaning of dimension, a growth rate, comes in lesson 4.6.)

**Three examples.** On three variables:

- with no rule at all, every set is free, and the free complex is the whole
  free triple, drawn as a filled triangle;
- under the atom, the three pairs are free but the triple is not, so the free
  complex is a **hollow triple**: three free pairs closing a cycle around a
  triple that is not free, drawn as an empty triangle. It is a hole of
  dimension one;
- under A ≠ B, with c unused, the pair A, B is not free, so the free complex
  is the two free pairs A, c and B, c, sharing c, with no hole.

**Flags and joins.** Two terms from topology appear in the next lesson. A free
complex is **flag** when every set whose pairs are all free is itself free, so
that its pairs decide all of it. Two systems on separate variables, taken
together, have the **join** of their free complexes as their free complex: a
set is free when its part in each system is free. The join of two hollow
triples has a hole of dimension three, which the literature draws as a
three-dimensional sphere (*Classical*).

### 3.4 Holes and knots

**Hole or knot.** The two words are easy to confuse. A system's free complex
is built from what it leaves free: its free distinctions, its pairs that take
all four combinations, its free triples, and so on. A **hole** is any gap in
that complex. A **knot** is the smallest kind of hole: a set whose every part
is free, but which is not free itself.

```text
a knot: a hollow triple              a hole made by ties: a hollow
(drawn as an empty triangle)         cycle of four (drawn as a square)

        A                               a ──── b
       / \                              │      │
      B ─ c                             d ──── c

all three pairs are free;            the pairs a–c and b–d are tied, so
A, B and c together are not          they are missing from the complex; the
                                     gap is made of missing pairs
```

- **Pairwise rules make only flag complexes.** In a 2-CNF system a set is free
  exactly when all its pairs are free. So two-place rules can make holes, as
  the hollow cycle of four shows, but never a hollow triple. *Checked*
  (`SpaceTest`; of 399 random 2-clause systems on six variables, 29 have holes
  and none has a hollow triple).
- **Every knot is a hole, but not every hole is a knot.** To tell whether
  things are bound, look at the knots, not at the size of the holes. Two
  unrelated knots taken together leave a hole of dimension three, because the
  join of two hollow triples has one (the literature's 3-sphere), yet nothing
  binds them.
- **Logic allows every free complex.** Every simplicial complex is the free
  complex of some system. *Proved (Lean):* `every_complex_is_a_nerve` in
  `LoopNerve.lean` builds one from loops whose contacts permute witness values.

**Reading.** Logic gives intrinsic holes, paths and separation, but it selects
no space. Whatever space there is has to come from a law. Which law gives a
meeting pattern that looks like a space of low dimension is open (lesson 7.2,
question 1).

```bash
PYTHONPATH=tools python3 -m knotlab space
```

## Chapter 4. How bindings behave

Knots can be read as requirements or as choices, can come from rules that
compete, and can be joined into rings and networks. They also space
distinctions apart, so that rules alone can set a distance and a dimension:
first on a board that is given (lesson 4.6), then on knots alone, with only
their meeting pattern given (lesson 4.7).
The chapter first fixes the words for easy and hard questions, which these
behaviours are measured by.

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

Propagation, in the first item, starts from the facts and adds whatever a
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
cycle of three the differences cannot all hold, so the preferences are
*frustrated*. The states that break exactly one preference are the six
not-all-equal states, and those form a knot. Competition can make a knot from
pairs, but only this kind.

- **Exactly four knots come from competing pairs on three variables.** A knot
  on three variables is the set of least states of an energy with only one-
  and two-variable terms exactly when its excluded states are an opposite
  pair. These are the four not-all-equal relations, the frustrated three-cycles
  (the literature's frustrated triangles).
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

MAX-2-SAT, in the third item, asks for a state that satisfies as many
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
variable visible, a knot other than the frustrated three-cycles cannot come from
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
once. The **nerve** of a family of sets is the simplicial complex with one
member for each set, in which a group of members is a set of the complex when
their sets share an element.

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

The first cohomology class of the first item amounts to one value of the
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

### 4.6 Dimensions from rules

**The idea.** In the Game of Life the board comes first: the grid decides
which cells are neighbours, and the rules are read on it (lesson 1.3). The
owner proposed the reverse, on 7 November 2026: "a number line/Cartesian plane
where the dimensions themselves expand out in measures of logic", each axis
"built out of an infinite structure of logic (emergent space)". So the axes X
and Y would follow rules, as Life's cells do, and the rules would be an
essentially infinite CNF. It is the intuition of lesson 1.7 turned on space
itself: in the owner's terms, lines and functions are "shapes", and "shapes"
have rules. A function's
graph already obeys one ("A single input (x-value) cannot have two different
outputs (y-values)", in the owner's words of 8 November), so the axes it is
drawn on could obey rules too. This lesson says what of that idea is proved,
what is computed, and what is still only an idea.

**Infinite CNFs.** A CNF may have infinitely many variables and clauses, as
long as each clause names finitely many variables. A law is **uniform** when
one pattern of clauses is repeated everywhere, as Life repeats its rule at
every cell and step of an infinite board. *Classical:* even whether one
repeated pattern allows any state at all can be undecidable; this is the
domino problem (Berger 1966).

**Every bond stays finite.** No knot joins infinitely many things (lesson 1.7),
so a space that an infinite CNF makes is made of infinitely many finite bonds.
*Classical:* the compactness theorem.

**Distance read from the rules.** A **bond** of a system is a set of its
distinctions on which its allowed states, with every other variable forgotten
(lesson 1.6), form a knot, and its size is its number of distinctions. Two
distinctions are as far apart as the smallest bond that contains them both:
their **bond distance** is that bond's size minus one. It is read from the
allowed states alone, so no ruler is drawn. On a chain of atoms,
w(t−1) ∧ L(t) → w(t), the bond distance from w(s) to w(t) is exactly t − s + 1,
one unit for each loop between them, and every bond through the two contains
those loops. A chain of two-place ties has no knot, and so no bond distance
(proved, [LOGIC-AXIS-20261107-001](research/LOGIC-AXIS-20261107-001/logic_axis.md)).

**Dimension read from the rules.** The distinctions within bond distance r of
one of them form a **ball**. When the number in a ball grows like r^D, the
rules have dimension D: this growth rate is the guide's own meaning of the
word, and a hole's dimension (lesson 3.3) is the literature's. Tseitin's
parity law on a drawn grid with D independent steps (the
literature's ℤ^D) has balls that grow like r^D, and so does the gauge law on
the drawn grid with two steps, x and y, so the allowed states alone recover
the drawn grid's dimension. On that grid both laws count steps in x plus
steps in y, never a step that combines the two (the literature's taxicab
measure; proved, with the gauge law's constants computed on a 41 × 41 block;
the same record).

**The rules can disagree with the grid.** The grid sets a ruler for a parity
law that has no ends: one in which every pattern it allows in a region can be
reached from any allowed state by changing finitely many cells. Bond distance
is then at least the separation divided by the law's range (proved).
Ledrappier's law, in which every cell is the parity of two neighbours in the
row before, has ends. Its three-place knots are exactly its Frobenius triples
(drawn in the literature as triangles), cells 2^k apart are bonded as tightly
as neighbours, and every ball is infinite (proved, the same record). So what
the rules measure need not be the grid they are written on.

**A chain with nothing drawn.** A rule that grows only at knots holding two
loose ends grows exactly an endless chain from a single knot, along which bond
distance counts one per step: the literature's number line (proved,
[OPEN-END-GROWTH-20261107-001](research/OPEN-END-GROWTH-20261107-001/open_end_growth.md)).
Here one of the owner's axes does come from the rules alone.

**Two axes are still drawn.** Every board of dimension two measured so far had
its cells, and which of them are neighbours, given before the rules were
read: a grid, a declared network of rings, a group's table, or a gadget whose
copies and stretch set the dimension. No tested law selects its own dimension
(reading,
[LOGIC-AXIS-20261107-001](research/LOGIC-AXIS-20261107-001/logic_axis.md)).
Under a uniform law, a declared board of rings of dimension two that keeps
doubling and then stops reads the bond distances of a fixed finite board that
closes up in both steps (the literature's torus; proved,
[GROW-STOP-20261110-001](research/GROW-STOP-20261110-001/grow_stop.md)), but its
rings are declared. The register of assumptions records this default as A51,
"Places and their neighbours are given before the rules"
([docs/ASSUMPTIONS.md](docs/ASSUMPTIONS.md)). Lesson 4.7 takes the board
away: on knots alone the knot law reads the endless six-regular weave's
dimension two, with only the meeting pattern given.

**The board as distinctions.** The owner's idea in full asks for more: make
"these two names are one cell" a distinction of the same infinite CNF as the
cells' values, and let one uniform pattern of clauses constrain both. Name the
cells by words in two letters, x and y, and their inverses, so that every name
u has four neighbour names, ux, uy and the two inverse steps. Give each pair of
names a distinction saying whether they name one cell. Three rules make these
distinctions a **board**: naming one cell is an equivalence; it passes to
neighbours (if u and v name one cell, so do ux and vx); and one cell has one
value. *Classical:* the boards are then exactly the Schreier graphs of the
subgroups of the free group on x and y. When no two names are one cell the
board is the tree, whose balls grow exponentially; when xy and yx always are,
it is the **commuting board**, whose balls grow like r², the literature's
grid ℤ², usually drawn as the plane.

- **Rules that declare no cycle never choose the commuting board (proved).**
  Call a law relation-free when its clauses say only which names are one cell,
  never that some word of steps comes back to where it started, which would
  make that word a **declared cycle**. If such a law allows any infinite
  board, it also allows the tree. So it never forces the commuting board, or
  any other infinite board. Far from the few cells that look unique, every
  local view repeats, and the views can be unfolded into the tree. Such a law
  can force a finite board, and the rule "two names that look alike are one
  cell" always makes the board finite
  ([BOARD-DIST-20261110-001](research/BOARD-DIST-20261110-001/board_dist.md)).
- **One declared cycle is enough (proved).** A clause at every name saying
  that the four steps xyx⁻¹y⁻¹ come back to where they started, the
  **commuting cycle** (drawn in the literature as a closing square), forces
  exactly the commuting board when it is joined with an aperiodic tile law,
  the literature's tiles that cover a board but never periodically (the same
  record).
- **The values can forbid a commuting cycle (computed).** In 60 of the 1,024
  Life-like one-bit laws the board is bound to the values beyond "one cell,
  one value". Closing the commuting cycle at a name u makes u and uxyx⁻¹
  neighbours. When a 0 must have only 1s around it, they cannot both be 0, so
  the cycle's distinction and those two values form one clause of three, a
  knot (the same record).
- **A board made of names is frozen (proved).** Two different boards differ in
  infinitely many distinctions, and off the tree every cell holds infinitely
  many names, so no finite change moves a board or its values. The program
  counts a knot as native only where finite changes can flip its variables, so
  no knot that involves the board is native.

**The theorem.** A law that declares no cycle cannot choose the commuting
board: whenever it allows an infinite board, it allows the tree too, so no
such law forces the commuting board. One declared commuting cycle, joined with
an aperiodic tile law, does choose it. The question of which boards local
rules can force is also studied as graph subshifts (Arrighi, Durbec and
Guillon 2023).

**Even in the limit.** Take the identity rule to its limit: names that look
alike at every radius, however far, are one cell. That rule is no longer a
clause of finitely many variables. It still allows the tree for every law
with infinitely many solutions, whatever its finite alphabet of values and
however far, finitely, its rules reach. Such a law always has a solution that
repeats nowhere, so no two names are one cell and the board is the tree. The
rule never forces the commuting board, though that board is allowed for most
one-bit laws
([LEIBNIZ-BOARDS-20261110-001](research/LEIBNIZ-BOARDS-20261110-001/leibniz_boards.md),
[WEAK-APER-20261110-001](research/WEAK-APER-20261110-001/weak_aperiodic.md)).
Some laws have no finite board at all. Among the laws on three values that
count a cell's neighbours one level down, level and one level up, they are
exactly the laws that drift: every cell has more neighbours above it than
below, or every cell more below. On a finite board every step up is a step
down seen from the other end, so a drift cannot close up.

**Without letters.** So far every name came with four neighbour names, its
letters. Take the letters away: names are only names, and whether two of them
are neighbours is one more distinction of the law. A rule of finitely many
variables then cannot make two cells touch: whatever it allows, it also
allows a world in which every cell touches every other, or none does
(Ramsey's theorem). The letters were drawing four neighbours that a rule can
tell apart, and one connected board. Without them the board is no longer
frozen: two links that join the same pair of values can trade partners, and
the board takes part in knots with the values
([BARE-NAMES-20261110-001](research/BARE-NAMES-20261110-001/bare_names.md)).
The values on it can change with the board kept, wherever the board comes in
finite pieces. On the free board a change has to stop somewhere, and
for most of these rules it never can
([PLACE-FLIP-20261110-001](research/PLACE-FLIP-20261110-001/place_flip.md)).
Growing the board from a seed does not escape this either. A growing rule
that closes no cycle grows a tree. One that closes commuting cycles can grow
the whole commuting board, one cell at a time, but it declares each cycle as
it closes it
([GROW-FACE-20261110-001](research/GROW-FACE-20261110-001/grow_face.md)).

**Reading.** Rules can measure a space and read its dimension from what they
allow, and in one dimension they can grow the axis with nothing drawn. When the
board itself is made of distinctions, rules that declare no cycle cannot
choose the commuting board: they always allow the tree. One rule that
declares the commuting cycle can. In the owner's words of lesson 1.7, "shapes"
have rules; here the commuting board's rule is one declared cycle. Lesson
4.7 asks what is left when there is no board at all.

```bash
PYTHONPATH=tools python3 -m knotlab space
```

### 4.7 Knots alone

**The idea.** Lesson 4.6 ended on a board: cells, which of them are neighbours,
and steps x and y between them. There a law fixes the commuting board only by
declaring the commuting cycle, the clause that says xy and yx meet, so the
cycle is part of what the law is given. This lesson takes the board away. A
knot pattern of three-place knots is nothing but distinctions, knots and which
knots share which distinctions, its meeting pattern (lesson 2.1): no cells, no
names, no steps x and y, and no declared cycle. What the literature's drawing
would call a closing cycle is here the knot itself, so nothing is named but the
knot. Put one law on every knot, read the allowed states alone, and ask two
things: do they give the meeting pattern back, and do they space its
distinctions apart? The lesson ends by saying what is still put in.

**Reading a pattern faithfully.** A law reads a knot pattern **faithfully**
when its allowed states freeze no distinction (none takes one value in every
allowed state), tie no pair (every pair is free), and leave no hollow triple
(lesson 3.3) except the pattern's own knots. Then the knots can be read back
from the allowed states: they are exactly the sets of three that are
constrained while every pair is free. The register of assumptions records the
choice to look only at sets of up to three distinctions here as A67
([docs/ASSUMPTIONS.md](docs/ASSUMPTIONS.md)).

**Steps apart.** Two distinctions are **d steps apart** when the shortest row
of co-knotted pairs that leads from one to the other, each pair sharing a
distinction with the next, has d pairs. This count belongs to the meeting
pattern and comes with it. The question is whether the allowed states, which
know nothing of rows of pairs, measure the same thing as bond distance (lesson
4.6).

**Four laws, four readings.** Lesson 2.3 counts the knots on three variables.
Four of them treat their three distinctions alike, up to reading every value
negated: the clause, parity, not-exactly-one and not-all-equal. Put one of them
on every knot of a pattern:

- **The clause gives the knots back and spaces nothing (proved).** It reads
  every pattern faithfully, but its only bonds are its knots, so two
  distinctions that share no knot have no bond distance at all.
- **Parity folds the pattern (proved).** On a two-fold weave whose distinctions
  split into three classes that every knot meets once each, it allows just four
  states, which give each class one value, so distinctions in one class are
  tied. Parity reads no weave faithfully.
- **Not-exactly-one makes a hub (proved).** It ties every pair to the all-zero
  state, a hub in the sense of lesson 2.1: every two distinctions are at bond
  distance 2.
- **Not-all-equal keeps the pattern and spaces it (computed, exact).** It reads
  227 of the 229 six-regular two-fold weaves in range faithfully (those with no
  three pairwise co-knotted distinctions outside a knot), and the two it misses
  have an unfilled cycle of only four pairs. Bond distance is 2 one step apart
  and 3 two steps apart.

([KNOTS-ALONE-20261111-001](research/KNOTS-ALONE-20261111-001/knots_alone.md))

**Long unfilled cycles (computed, exact).** Not-all-equal reads every
six-regular two-fold weave in range whose unfilled cycles all have at least
five pairs faithfully: 449 weaves, the orientable ones with 49 to 80
distinctions and the others with 19 to 40. On the 349 orientable ones whose
unfilled cycles have at least six pairs, two distinctions d steps apart are at
bond distance d + 1 for every d up to 3. Two steps is proved: two co-knotted
pairs that each form a knot with one hidden distinction, each pair held equal
and the two pairs held opposite, force the hidden distinction both ways, so
four distinctions two steps apart already form a bond
([LONG-LOOP-20261111-001](research/LONG-LOOP-20261111-001/long_loop.md)).

**The ruler (proved).** On the endless six-regular weave, the literature's
triangular lattice, which it draws as the plane, not-all-equal reads the weave
faithfully, and two distinctions d steps apart lie together in a bond of
exactly d + 2 distinctions and in no smaller one. So their bond distance is
d + 1 at every d: the knots measure their own meeting pattern exactly. In the
literature's drawing the bond is one side of a triangle of side d together with
the opposite corner. Every bond is native: each of its distinctions can be
flipped by changing finitely many others (lesson 4.6). These three statements
are proved and refereed
([RULER-20261111-001](research/RULER-20261111-001/ruler.md)).

- **Dimension two, as a consequence (proved, from the ruler).** Since bond
  distance is d + 1, the ball of bond distance r around a distinction (lesson
  4.6) is the set of distinctions at most r − 1 steps from it. That set holds
  3r(r − 1) + 1 distinctions, so balls grow like r², and in lesson 4.6's
  meaning of the word the law reads dimension two from its allowed states
  alone. The consequence needs the whole endless weave: on finite weaves the
  ruler holds only below the cutoff M/3 of the next bullet, and how balls grow
  there has not been measured.

- **Why it is exact (reading of the proof).** The allowed states are the ground
  states of the literature's triangular Ising antiferromagnet, and each carries
  what the literature calls a height: with every co-knotted pair given a
  direction, it rises by at most one along each pair (Blöte and Hilhorst 1982).
  A pattern of values is forbidden when it asks the height to rise faster than
  that around a cycle of co-knotted pairs, and each distinction can supply at
  most half a unit of the excess, so spanning d steps takes d + 2 distinctions.
- **On finite weaves (proved for the orientable ones).** On a finite
  six-regular weave the height also winds around each unfilled cycle. On the
  orientable ones one number decides everything: the margin M, the least extra
  cost of going once around an unfilled cycle. States exist exactly when M ≥ 0,
  bond distance is d + 1 whenever d is below M/3, and the reading is faithful
  when M > 3. The weaves that are not orientable come in two kinds: on one the
  same theorem holds word for word, and the other stays computed
  ([RULER-FLAT-20261111-001](research/RULER-FLAT-20261111-001/ruler_flat.md)).
- **What is known.** The height and the way a partial pattern extends are
  known. The sizes of the least forbidden patterns, and so the ruler itself,
  were not found stated in a bounded search, though a specialist could derive
  them quickly from the known criterion.

**From a board to knots alone.** Compare the two lessons. On a board of names,
the steps x and y are given, and a law fixes the commuting board only by
declaring the cycle xyx⁻¹y⁻¹: whether x then y meets y then x is something the
law is told. On knots alone there are no steps x and y to ask that of, and no
cycle is declared. The knot is the only relation, and not-all-equal still
measures an exact ruler and, on the endless weave, reads dimension two. The register records the
reading that a declared cycle is put in, not built, as A63, now overturned in
this setting, and the reading that counting how knots meet declares no cycle as
A64, which that overturning rests on
([docs/ASSUMPTIONS.md](docs/ASSUMPTIONS.md)).

**What is still put in.** The meeting pattern is given: that every co-knotted
pair lies in two knots, that the knots at each distinction form one cycle, and
that six knots meet at every distinction. Two attempts to get it from the law
have failed:

- **A faithful reading does not supply it (computed, exact).** Swap two knots
  of a faithfully read six-regular one-pair weave for two knots that join
  distinctions many steps apart: 160 of 822 such patterns are still read
  faithfully, though in them some pairs lie in one knot and some in three
  ([NAE-SURFACE-20261111-001](research/NAE-SURFACE-20261111-001/nae_surface.md)).
- **Growth does not supply it (computed).** Grow a pattern one knot at a time,
  keeping each new knot only while not-all-equal still reads the pattern
  faithfully. The law accepts pairs in three knots. Even with two knots on
  every pair and one cycle of knots at each distinction imposed, the cycle at a
  distinction closes after anywhere from 3 to 14 knots, not mostly six. It does
  refuse one meeting pattern (proved): the third distinctions of a pair's two
  knots never share a knot, since equal values on the pair would then force a
  contradiction
  ([GROW-COUNT-20261111-001](research/GROW-COUNT-20261111-001/grow_count.md)).

So on six-regular weaves the law reads which knots there are and measures them
exactly, but how they meet is still an input, static or grown, as the board was
in lesson 4.6. On the owner's reading that is not a defect: nothing chooses a
meeting pattern, and one written down is one sample of them (lesson 7.3).

**Knots that overlap freely.** Nothing in lesson 2.1 says that a pair lies in
two knots. In a finite base where knots share distinctions in any pattern, what
does not-all-equal force that no knot names?

- **Only its own kind (proved).** Nothing is frozen, a tied pair is always
  equal or always unequal, and every hollow triple that no knot names is a
  not-all-equal knot, with some of its distinctions read negated. The
  literature knows these relations as the co-clone IN2 of complement-closed
  relations (Böhler, Reith, Schnoor and Vollmer 2005).
- **The law reads pair counts (proved).** Its allowed states depend only on how
  many knots lie on each pair of distinctions. So two different knot patterns
  with the same count on every pair allow the same states: they are different
  bases with one relation.
- **An example.** Put not-all-equal on four triples of six distinctions: abc,
  ayz, xbz and xyc. With x, y and z all 0, the last three knots force a, b and
  c all to 1, which the first forbids, and all 1 is forbidden in the same way.
  Every other combination of x, y and z occurs, so x, y and z form a
  not-all-equal knot that no rule names. The other four triples, xyz, xbc, ayc
  and abz, cover the same twelve pairs once each, and on the same six
  distinctions they allow the same 18 states. The literature calls the first
  four triples a Pasch configuration, and all eight together the octahedron.
- **Overlap is readable, uniform overlap is not (proved and computed).** A pair
  can lie in any number of knots in a base read faithfully, and grown bases
  reach nine. Where every co-knotted pair lies in three knots, no base in range
  is read faithfully.
- **What the law adds is not local (computed).** The smallest arrangements that
  force a knot no rule names number 1, 4, 11 and 64 at three to six knots, some
  small bases need seven knots to force anything, and one knot swap in a
  two-fold weave can bind three distinctions through half the base.

([OVERLAP-READ-20261111-001](research/OVERLAP-READ-20261111-001/overlap_read.md))

```bash
PYTHONPATH=tools python3 -m knotlab check --cnf "a b c; ~a ~b ~c; a y z; ~a ~y ~z; x b z; ~x ~b ~z; x y c; ~x ~y ~c" --loops x y --contact z --witnesses a b c
```

The command forgets a, b and c and reports that x, y and z form a knot.

**Endless bases that overlap.** The bases so far are finite, or two-fold
weaves. Lesson 2.1 allows more: infinitely many knots, overlapping in any
pattern. The record's first such bases are **periodic**: one block of
distinctions and knots repeated at every whole number, one shift, or at every
pair of whole numbers, two shifts, with nothing limiting how many knots lie on
a pair. The literature calls them periodic hypergraphs over ℤ and ℤ². A
**finite repeat** of a periodic base identifies the blocks whose shifts differ
by chosen amounts, the literature's periodic quotient. Put not-all-equal on
every knot:

- **Overlap at infinity is read faithfully (computed).** With one shift the
  reading is exact: 73 of 181 patterns are read faithfully, 23 of them with a
  pair in three or four knots. With two shifts, 134 of 627 are read faithfully,
  36 with a pair in three or more knots and 2 with a pair in four, and 160 stay
  unsettled by the bounds used. In both bases with a pair in four knots, that
  pair, repeated at every shift, carries the four knots, and every other pair
  one.
- **An endless base is not its finite repeats (computed).** 25 of the two-shift
  bases read faithfully have no finite repeat of 9 to 30 blocks read
  faithfully, and over all of them only 7.7% of the finite repeats tried are.
  Most verdicts need states that pass from one repeating pattern of values to
  another (the literature's domain wall), which no finite repeat can hold.
- **The ruler's first step survives (computed).** In every two-shift base read
  faithfully, each pair of distinctions two steps apart lies in a bond of four.
- **Two classes read alike (proved).** If the knots of a finite pattern split
  into two classes that meet every co-knotted pair once each, the two classes
  and their union allow the same states, as the pair-count lemma implies. It
  explains most of the triples above that only a whole base forces: in 91 of
  the 98 such bases made by knot swaps, those triples are knots the swaps
  removed, still held by the knots that remain.

([PERIODIC-READ-20261111-001](research/PERIODIC-READ-20261111-001/periodic_read.md))

**Bond distance on these bases.** Steps apart on a two-shift base grow as the
shifts dictate. Does bond distance follow them?

- **No ball stops at three steps (computed, refereed).** On the 134 two-shift
  bases read faithfully, every distinction three steps from a given one lies in
  a bond of at most five with it.
- **Shortcuts (computed, refereed).** On most of these bases bond distance is
  steps apart plus one, as on the endless six-regular weave. On 42 of them (38
  up to a change of the two shifts) some distinctions three or four steps apart
  lie in a bond of four: a **shortcut**, a pair whose bond distance is less
  than its steps apart plus one. On five heavily overlapping bases some "bond
  of five" verdicts are only upper bounds. The endless six-regular weave, where
  the ruler is proved, has no shortcut.
- **A direction the law does not lengthen (proved).** On one base, three
  equal distinctions force a matching three, one shift over, to the opposite
  value, and those force the next three, and so on. So for every k, three
  distinctions k steps away form a bond of four with the starting one: bond
  distance at most 3 at every distance, along a whole line in both directions,
  while every pair stays free, so no single far distinction is tied to the
  starting one. Steps apart and bond distance both belong to the base itself,
  so the gap is the law's doing, not the meeting pattern's; it runs along the
  one pair class that two knots share. Of the 38 kinds of base with shortcuts,
  14 keep bonds of four at five and six steps (computed). The nearest known
  case is a parity rule on the same pattern of knots whose constraints appear
  at doubling distances (literature: Ledrappier's shift).
- **Across it, one more distinction for every two across (proved one way).**
  Call the direction the law does not lengthen the **unlengthened shift**, and
  count distinctions along it and across it. A **heddle**, three equal
  distinctions at consecutive across-counts and then every second
  across-count up to y, all at one along-count, travels along the
  unlengthened shift intact, so with one distinction y across and far along
  it forms a bond. Among bonds made of one along-count and one distinction
  further along, the heddle bond is the smallest: the law passes a value on
  only where it has an equal partner one more or two fewer across, and what
  such a pattern forces far along is exactly its **self-keeping part**
  (literature: the stable set of a constrained flip dynamics, as in bootstrap
  percolation). Those bonds reach only one way across, but bonds over two
  along-counts reach the other way at the same sizes (computed to ten
  across). So the law's balls, read across the unlengthened shift, grow by
  two across-counts each way for each step of bond distance: one dimension
  across. No smaller bond of any shape turned up in the boxes searched; that
  none exists is open.

([BOND-BALLS-20261111-001](research/BOND-BALLS-20261111-001/bond_balls.md);
[FOLD-20261112-001](research/FOLD-20261112-001/fold.md);
[ACROSS-FOLD-20261112-001](research/ACROSS-FOLD-20261112-001/across_fold.md))

**Studying a base from inside.** Lesson 1.7 asked whether what emerges in a
base can study the base. The record so far:

- **Rules within rules nest to any depth, in one family (proved).** A drawn
  knot pattern with one distinction removed, a **piece**, can stand in for one
  knot of a larger drawn knot pattern. A drawn knot pattern carrying pieces
  gives a piece again when one of its distinctions is removed, and that piece
  acts as its knot exactly where every piece inside it does. So pieces nest to
  any finite depth
  ([NEST-ATOMS-20261110-001](research/NEST-ATOMS-20261110-001/nest_atoms.md)).
- **Towers from one three-place law keep only parity (proved),** as lesson 1.7
  says.
- **A part can read only the relation (reading, from the pair-count lemma).**
  Whatever reads a base from inside, a witness (lesson 1.6), is one more
  distinction of the same allowed states, and a knot shows only across those
  states (lesson 2.3). Under not-all-equal, bases with the same pair counts
  allow the same states, so nothing inside one can tell it from the other. What
  a base can learn of itself is its relation, never which meeting pattern made
  it.
- **A supplied task can be learned in place (computed).** A learning rule that
  sees only which knots its state violates changed the signs of the law on a
  drawn knot pattern until the pattern computed the parity of three held
  distinctions, and kept it through a disturbance, in 20 of 20 runs. The
  learning rule, the law's form and the held inputs all come from the outside
  ([LEARN-PARITY-20261111-001](research/LEARN-PARITY-20261111-001/learn_parity.md)).
- **Open.** Whether a part of a base can find rules that make what it sees,
  with nothing designed in advance (lesson 1.7).

**Reading.** On the endless six-regular weave, with nothing named but the knot,
not-all-equal gives its meeting pattern back and measures it exactly: a ruler
at every distance and dimension two. It does not make the meeting pattern,
which is given, as the board was. On endless bases that overlap, the law still
reads the first steps, but its distance can part from the meeting pattern's: on
some bases it is shorter, and on one a whole combination of the shifts may have
no length to the law at all (computed, open). So the space a law reads need not
be the one its meeting pattern supplies. For the owner's Cartesian plane, one
axis grows from the rules with nothing drawn (lesson 4.6), and a second
dimension is measured by the knot law, on overlaps the record wrote down.
Whether a law forces its own meeting pattern is still open, but on the owner's
reading it need not: nothing chooses a meeting pattern, so the next question is
which meeting patterns are typical and which rare, and what the law reads off
each (lesson 7.3).

```bash
PYTHONPATH=tools python3 -m knotlab space
```

## Chapter 5. Depth

A knot pattern can allow nothing while every small window of it looks
consistent. This chapter asks how much of the pattern a proof has to hold at
once to see that nothing is allowed.

### 5.1 Proving that nothing is allowed

**Refutations.** When a system allows no state at all, a refutation is a proof
of that fact: a sequence of steps, each of them following from the rules, that
ends in a statement no state satisfies. Proof systems differ in what one step may do, and the
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
Such a pattern allows nothing exactly when the total charge is odd. That is a
hole, but every small window of the pattern looks perfectly consistent, since
the odd unit of charge can be pushed anywhere by flipping edges along a path.
So how much of the pattern must an observer hold at once to see the hole? The
answer is a width of the graph: the charge has to be carried across the widest
gap of the best order of the graph's vertices.

These patterns are Tseitin formulas, and "how much an observer must hold"
becomes the degree of a refutation.

**Graph terms.** Three terms about graphs appear below. Put a graph's vertices
in an order: each gap in the order is crossed by the edges that join a vertex
before it to a vertex after it, the order's width is the most edges crossing
one gap, and the **cutwidth** is the least width of any order. The **maximum
degree** is the most edges at one vertex. The **±1 encoding** writes each bit
as +1 or −1 instead of 0 or 1.

- **Reasoning mod 2 sees the hole at once.** Summing every vertex's equation
  counts each edge twice, so a refutation of the size of one knot exists.
- **Every other field needs the toggle width.** *Proved (note):* over every
  field of characteristic other than 2, the Nullstellensatz degree of the
  Tseitin formula, written clause by clause, equals the **toggle width** of
  the graph: the cheapest way to grow the empty vertex set into the whole
  graph by adding or removing one vertex at a time, where each step costs the
  edges it must keep track of. On graphs of maximum degree at most three this
  is exactly **cutwidth + 1**. In the ±1 encoding, with degree measured after
  reduction, it is exactly the cutwidth. The upper bound carries the charge
  along an order, and the lower bound is a design whose values are signed
  sums over cuts.
  See [notes/tseitin-nullstellensatz-degree](notes/tseitin-nullstellensatz-degree/).

**Reading.** A hidden bit has a depth: the width an observer must hold to
carry it to where it shows. Holes made by loops of witnesses (lesson 4.5) are
shallow, and local reasoning sees them. Holes made by charges are as deep as
the graph's best order is wide, unless the reasoning computes in the charge's
own group. Related results for other proof systems, with tree layouts instead
of orders, are in the full record: see "Holes, depth and Tseitin proof
complexity" in [RESULTS.md](RESULTS.md).

```bash
PYTHONPATH=tools python3 -m knotlab depth
```

## Chapter 6. Counting

Deciding asks whether a knot pattern allows any world; counting asks how many
worlds it allows. This chapter sets up the words for counting, then reports
where counting turns hard.

### 6.1 Counting worlds

Deciding whether a knot pattern allows any world can be easy while counting
its worlds is hard. Two notes in this repository locate where
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
- **Planar graphs are the classical exception.** On a graph that can be drawn
  in the plane without crossings, the literature's planar graph, perfect
  matchings are counted in polynomial time by a
  determinant-like formula, the Pfaffian, once the edges are suitably signed
  (Kasteleyn 1967). A graph that has such a signing is called **Pfaffian**.
  Every planar graph is Pfaffian, and so are some others.

### 6.2 The worlds of not-all-equal knots

**Hypergraphs and colourings.** The note uses the literature's words for a
knot pattern. A **hypergraph** has vertices and edges, where an edge may
contain any number of vertices; for a pattern of not-all-equal knots the
vertices are the distinctions and the edges are the knots. In a **3-uniform**
hypergraph every edge has three vertices, so every knot has three
distinctions, and in a **3-regular** one every vertex lies in three edges, so
every distinction lies in three knots. A proper **2-colouring** colours each
vertex black or white so that no edge has all three of its vertices the same
colour, which is an allowed state of the not-all-equal knots. The **incidence
graph** has a vertex for each distinction and one for each knot, and joins
each distinction to the knots that contain it. The note also signs some
incidences: at a signed incidence, the knot sees the distinction's value
reversed. A twist, roughly, is where the signs differ from a Pfaffian signing,
and the note defines when twists branch.

**What the note proves.** A 3-regular 3-uniform hypergraph is a pattern of
not-all-equal knots in which every distinction sits in exactly three knots,
and its proper 2-colourings are the pattern's worlds. Patterns with no world
at all are where these knots close up on themselves, and the program calls
them **three-regular contradictions**; earlier records called them three-fold
spaces. Counting is #P-hard in general (Fan and Cai) and easy when the
incidence graph is planar (Valiant). The note studies the class in between,
Pfaffian incidence graphs, which contains every pattern with no world.
*Proved (note):*

- remove any one knot from a connected pattern with no world, and the worlds
  of what is left can be counted in polynomial time;
- counting stays polynomial under twists that do not branch;
- counting becomes #P-hard once twists branch. It stays #P-hard without any
  signs, and even when the incidence graph is a Pfaffian brace.

See
[notes/pfaffian-hypergraph-colourings](notes/pfaffian-hypergraph-colourings/).

### 6.3 Counting on classical 3-manifolds

**Spaces and their groups.** This lesson reports a result about objects of
classical topology, which are not the program's objects: the program has built
no space, and its words here are the literature's. A 3-manifold is a space
that looks like ordinary three-dimensional space near each of its points, such
as the space around a knotted rope. Its **fundamental group** records its
closed paths, which the literature calls loops; they are not the loops of
lesson 1.4. Two closed paths count as the same when one can be slid into the
other, and two combine by running one after the other. A **homomorphism** from
the fundamental group to a finite group labels every closed path with an
element of the group so that running two of them one after the other
multiplies their labels. For the space around a **classical knot**, a knotted
rope drawn as a diagram, such a labelling is a colouring of the diagram's
arcs that obeys one rule at each crossing. A group is **solvable** when it is built in finitely
many layers from commutative groups. S₃ is the group of the six permutations of
three things, and S₄ that of the 24 permutations of four. A group's Fitting
height counts its layers of a particular kind, the nilpotent ones, which are
the groups closest to commutative; Heisenberg groups are the simplest nilpotent
groups that are not commutative. A **link** is several closed ropes,
possibly tangled with one another, and a classical knot is a link with one
rope.

**What the note proves.** When the laws counted are group laws on a 3-manifold,
counting worlds means counting homomorphisms from its fundamental group to a
finite group. Rowell conjectured in 2009 that this count is computable in
polynomial time for solvable groups. *Proved (note):* unless every #P function
is computable in polynomial time, the conjecture fails. On links it fails
already for S₃. On classical knots it fails for S₄, the smallest group for
which it can,
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
statement about counting complexity, not about the logical knots of lesson 2.1.
The knot
test cannot tell hard groups from easy ones: every group law, read as the
relation x·y = z, is constrained as a whole and free in every pair.

## Chapter 7. Sources and questions

What the guide takes from classical mathematics, what it adds, what
remains open, and the owner's picture of what the program's bases are part of.

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
  - the ground states of the triangular Ising antiferromagnet and their
    height (Wannier 1950; Blöte and Hilhorst 1982), and complement-closed
    relations as a co-clone (Böhler, Reith, Schnoor and Vollmer 2005), which
    lesson 4.7 uses;
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

1. **Space from a law.** Logic allows every free complex (lesson 3.4). Which
   uniform, local law, not written on a space in advance, gives a meeting
   pattern that looks like a space of low dimension?
   One necessary condition is known: a law keeps a lasting record of its
   loops only if its contacts act as group elements (lessons 4.4 and 4.5).
   Lesson 4.6 shows how far the program has got: rules read a drawn grid's
   dimension and grow an endless chain with nothing drawn, but no tested law
   yet forces a board of dimension two, and when the board is made of
   distinctions no law that declares no cycle can. Lesson 4.7 takes the board
   away: on knots alone, with nothing named but the knot, the not-all-equal
   law reads the endless six-regular weave's dimension two exactly, on a
   meeting pattern the record wrote down. On endless bases that overlap, the
   law's distance can be shorter than the meeting pattern's. On the owner's
   reading nothing chooses a meeting pattern, so one written down is one
   sample, and the question becomes which meeting patterns are typical and
   which rare (lesson 7.3).
2. **Dynamics.** Are loops better modelled as processes whose outputs over
   time are the data, and does the static test survive that change?
3. **Limits.** No set of finite clauses binds infinitely many loops into one
   contact (by compactness). Does the program need a limit rule that does?
   The owner also sees a limit where a growing knot pattern nears its end
   (lesson 7.3).
4. **Competition.** If least-violation states count as allowed, frustrated
   pairs make knots (lesson 4.3). Should they count?

### 7.3 Every meeting pattern, none chosen

On the evening of 11 November 2026 (Pacific time; the record's tickets carry
12 November, its date in UTC) the owner set out what the program's bases are
part of. This lesson records his picture in his words, beside the readings of
the coordinator, the agent that runs the program's lines of research, and the
tests now running on each part. The readings are interpretations and can be
challenged; nothing here is proved unless a result is named.

**The owner's picture.** "The intuition is that these structures are
essentially like a permutation of all the possible logical sequences that
could exist. Basically like, binding between infinite spaces is itself
infinite. [...] Basically, the "universe" isn't just the universe,
"everything" includes the base rules which extend outside of our universe into
other universes. We are not the sole extension of logic. We are just the one
that exists in this reality. There may be other realities that have different
rules."

**Nothing chooses.** "Yes, there is no choice. I feel like we keep going back
to this being a choice. It isn't. It's just random. Now, there may be some
realities that are statistically more likely than others, there's nothing to
say that's not possible. Maybe simple realities are more common than
non-simple ones. Or maybe realities are all the same likelihood. I don't
know." And of ours: "It's potentially special because it can create emergence
within that is intelligent and physical matter too, it's possible other base
realities can't. But there is no "special". It is indifferent. It's is purely
coincidental." This is the program's reading that every coherent alternative
is co-real (lesson 7.1), applied to meeting patterns: no meeting pattern is
selected, and ours is one among them. It is an interpretation. A result in
which a law leaves meeting patterns unselected fits it, but is no evidence for
it.

**What it changes in the record's words.** Lessons 4.6 and 4.7 say that a
meeting pattern is given, or put in by us. On the owner's reading that
describes what was studied and is not a defect: a meeting pattern the record
writes down is one **sample** of meeting patterns, none of which is chosen. The
older question, whether some law forces its own meeting pattern, stays a
question of its own, but it is no longer the only way to the owner's base
reality. The questions become which meeting patterns are typical and which are
rare, and what a law reads off each. The register of assumptions records this
wording under A15, the co-reality reading
([docs/ASSUMPTIONS.md](docs/ASSUMPTIONS.md)).

**Other realities are other knot patterns.** Asked whether other realities
have a different law or the same law on a different meeting pattern, the
owner said: "Different meeting patterns! Yes! Both the underlying patterns and
even possibly the binding patterns because there are infinite possibilities
for both." The coordinator reads this as one kind of logic, distinctions and
knots under the knot test of lesson 2.1, with realities differing in which
knots meet and possibly in the rules the knots carry. Where realities bind to
each other, the binding is read as more meeting pattern: knots that share
distinctions of both make one larger knot pattern. Two bases that share no
distinction share no contact, since the program infers no contact across
bases (lesson 7.1). The register records this reading as A73, with how to
challenge it.

**Binding patterns: an open definition.** Asked on 12 November what "binding
patterns" means, the owner said: "This is what we're trying to discover. To
me, it's like injected logic in each clause that binds a series of CNF
together. And this injection could maybe even bind in ways that have influence
distributed between different CNFs in like a non-linear way. It's possible
that clauses themselves have infinite series of CNF that allows for the
"non-linear" distribution." He gave a second picture beside it: "It's
possible though that this isn't truly what bindings are and that bindings are
actually recursive structures. So for example, with fractals, usually fractals
are shown as animated where you can zoom in to reveal identical structures,
but the nested structures depend on the larger structures to know where they
are. It's always present. This is the kind of infinite sequence we're talking
about. The problem too though, is that fractals are spatial. [...] but for
logic, it can hop around. [...] A logic based fractal with emergence as the
guiding principle." So the guide does not define a binding pattern. It is what
the research is to find, with two candidate pictures:

- **Logic carried in each knot.** Each knot binds whole knot patterns
  together, perhaps with an influence spread between them that does not add up
  part by part (his "non-linear"), and a knot may itself hold an endless
  series of knot patterns. A73's working reading, the rules the knots carry
  with bindings read as more meeting pattern, is one way into this picture.
- **Recursion.** Bindings are structures nested without end, in which an
  inner part depends on the larger parts for where it is, with no fixed number
  of dimensions, since a logical structure "can hop around" where a drawn one
  cannot.

He tied both to his word "shape" (lesson 1.7): "humans are shapes like
triangles are. Triangles are simply patterns that exist in some base reality,
and humans are also patterns that exist in this current base reality. We are
closer to triangles than to the limits of what is possible with emergence
(which is very difficult to conceptualize because necessary for humans are
bindings like "time", "space", and "physics")." Nothing here is a claim about
humans or physics.

**Odds over infinitely many (classical).** The owner's "maybe all the same
likelihood" meets a fact of probability: infinitely many finite meeting
patterns cannot all have the same chance. Chances add up to one, and equal
chances on infinitely many alternatives add up to nothing or to too much. So
every random way of producing a meeting pattern has a **weighting**, the
chance it gives to each set of meeting patterns, and the weighting has to be
declared. Two weightings are natural. One counts how short a pattern's
description is, so that simple patterns are more common, as the owner
suggested (the literature's universal prior). The other grows a pattern by a
random process, so that the process sets the chances. The program uses a
weighting as a tool for studying meeting patterns, named in each claim, and
never as the odds of realities: no weighting over all bases is assumed
(lesson 7.1). A census states its result for its own process only (A71 in the
register).

**Three outcomes.** Asked whether combinations that contradict themselves
exist too, the owner said: "Yes, that's kind of the idea. Like some
combinations should resolve to nothing, some can go for a while then die.
Others will go on forever and create sets like the natural numbers." In the
guide's words, grow a knot pattern one knot at a time. Its **outcome** is one
of three:

- **It resolves to nothing:** it allows no state from its first knots on. A
  single knot always allows states, so this happens only to a pattern made
  all at once, or within its first few knots.
- **It ends:** it allows states for a while and then none. It **ends** at the
  first knot after which it allows no state, and its **last base** is the
  pattern before that knot. Adding knots never brings a state back, so an end
  is final. The record reads the owner's "die" as this (A72), and on 12
  November he accepted the reading: "This is fine."
- **It goes on forever:** it is a base at every stage. By the compactness
  theorem (lesson 7.2, question 3) that is the same as the endless pattern it
  grows into being a base. A computation can only report that a pattern is
  still a base at the last knot computed, so the record says "goes on
  forever" only where a proof shows it.

A fixed endless pattern either is a base or is not; "for a while" belongs to a
pattern that grows in some order, so the outcome is a fact about the growth,
not about where it leads.

**What is known about the end.** Put knots of the not-all-equal law on n
distinctions uniformly at random. Below about 2.1 knots per distinction the
pattern almost surely allows a state, and above it almost surely none. The
literature's prediction is 2.107, its exact value for three-place knots is
open, and exact values are proved for knots of many places (random
not-all-equal satisfiability and hypergraph bicolouring: Castellani,
Napolano, Ricci-Tersenghi and Zecchina 2003; Gabrié, Dani, Semerjian and
Zdeborová 2017; Coja-Oghlan and Panagiotou; Ding, Sly and Sun). The end is
never local: at any fixed density the smallest sets of knots that allow no
state hold a constant share of all the distinctions (the expansion argument
behind Chvátal and Szemerédi 1988), and the smallest one of all has seven
knots, the Fano pattern. So "most random patterns with many knots end" is
known. What the law reads off the patterns that live, and what growth
processes other than the uniform one do, were not found in a bounded search.

**Near the end.** "I don't know why, but I get some inkling this is similar to
limits. This is why I tried to research the calculus angle of logic itself.
But the calculus is hard because the results themselves will be "non-spatial"
(at least not in the way that humans normally think). They are just relative
to each other. It's like relativity, but for logic." The coordinator's
reading: as a random pattern nears its end, what the law forces reaches
further, and at the end it spans a share of the whole pattern, as above; that
is a limit in the exact sense if the law's own quantities, such as the largest
set of tied distinctions or how far ties reach, approach a value as the end
nears, and not if they jump. Which happens is under test.

**Only relative.** The record's distance already works the owner's way:
two distinctions are as near as the smallest bond holding both, with nothing
behind them to measure against (lesson 4.6). On some endless bases two such
measures disagree: steps along the meeting pattern say far, and the law says
near, and on one base a whole direction has no length to the law, which is
proved: three distinctions any number of steps away still form a bond of four
with the starting one (lesson 4.7). The coordinator calls the comparison with relativity an
analogy so far and nothing more, and nothing here is physics.

**Harmonies and "fractals".** "I think of fractals and harmonies. Where
harmonies might be something like natural numbers and the fractals are
consequences of rules. If you're asking how we get things like decimals, I
think it's just harmonies and logic fractals to infinity for irrational
numbers." "Fractal" is kept in his own words only, and "harmony" has one
assumed reading, below (glossary). Earlier he used "harmony" for a relation
in which incommensurable parts cancel
("It is ALL relational. There is no real such thing as 'values'", 22 October
2026) and for polygons whose ratio of perimeter to diameter is rational, as
against "a ratio that continues" (7 November 2026). The record has these
pieces that bear on them, none yet tied to his words:

- **One law, the same kind at every level (proved).** Where knots overlap,
  not-all-equal binds triples that no knot names, and each is again a
  not-all-equal knot (lesson 4.7).
- **Towers of named patterns keep only parity (proved).** Built from one
  three-place law, patterns of patterns reach the free relation within three
  levels unless the law is parity (lesson 1.7).
- **Pieces within pieces (proved, drawn).** A drawn knot pattern less a
  distinction can stand in for a knot, and such pieces nest to any depth in
  one family (lesson 4.7).
- **A harmony as a repeat (reading).** For the operations below, the
  coordinator reads a harmony as an endless base along one shift all of whose
  allowed states repeat (A70 in the register). The owner has not confirmed it.

**Bases within bases.** "I imagine it like we could have infinite recursions.
In fact each boolean variable could be its own micro infinite series of logic,
that's bound to others." The coordinator's test: can a whole base stand in for
one distinction of a larger base, with the same law at the level above, and
again at every level? If so, that would be one reading of the owner's
"fractal", and what stays the same from level to level one reading of his
"harmony". A base has many states and a distinction one bit, so the test first
needs a declared way to read one bit from a base's states, and that bit must
be open, free on its own, not a value computed from distinctions fixed
elsewhere, which would only classify them. Two ways of nesting have been
tested (backlog B164):

- **Stitched at one place (proved).** Each distinction of an outer base
  becomes an endless harmony, and each outer knot stitches the three inner
  harmonies at every place. The outer level then allows exactly the outer law's
  states, at every level, nesting never ends, and nothing new is forced; it
  adds only room. Only the alternation 0101… reads as one bit
  ([BASES-WITHIN-20261112-001](research/BASES-WITHIN-20261112-001/bases_within.md)).
- **By substitution (computed; one direction proved).** Each distinction
  becomes a finite block whose own knots bind the copies. Then every
  distinction the block cannot spare is tied across the whole pattern, in 47
  of 87 small blocks, and deeper nesting keeps those ties without adding new
  ones ([SUBST-NEST-20261112-001](research/SUBST-NEST-20261112-001/subst_nest.md)).

The two readings differ in kind, so which one the owner means matters (A75 in
the register). Asked whether nested series are bound to each other beside one
another or inside one another, he said on 12 November: "We need to suss this
out. Side might be misleading here, I guess it makes sense, but these are not
sides in the typical "edge of a triangle" sense. We're not even in spatial
reality yet. The "side" is like the continuous edge of the loop, there is no
limit in what it's in contact with, so the "sides" can overlap where one side
can touch many other sides, it's not a 1:1 thing." So the question stays open,
and the guide does not say that bases or knots lie side by side: a loop's
binding is open to any number of others at once, as overlap already is
(lesson 2.1). His recursion picture above, inner parts placed by the larger
ones, is nearer to substitution, but he has not chosen.

**Operations on harmonies.** "We need to cover things like operations, what is
subtraction of the logical harmonies, what is division? This is why I'm trying
to investigate base realities like mathmatical spatial functions and shapes. I
believe these logical patterns exist "existentially" (to use loaded language)
for our reality." Where the record stands:

- **Counting is native only in part (proved).** A drawn knot pattern under
  not-all-equal can read the count of n held distinctions modulo m only for
  even m and odd n
  ([HOLD-COUNT-20261111-001](research/HOLD-COUNT-20261111-001/hold_count.md)).
- **A running total needs a zero.** Counting further needs a distinction held
  at 0 as a reference, which the law cannot make, so it is supplied from
  outside (A65 in the register). Subtraction and division asked as operations
  on totals wait behind the same need.
- **A route with no zero.** The coordinator suggested reading harmonies by
  their periods: stitch one that repeats every p to one that repeats every q,
  knot by knot at every shift, and ask which periods the law allows
  ([HARMONY-ARITH-20261112-001](research/HARMONY-ARITH-20261112-001/harmony_arith.md)).
- **Stitching multiplies, the shared divisor counts, nothing subtracts
  (proved, for any law).** A stitched state repeats with period the least
  common multiple of p and q; the pairs of states fall into as many offsets as
  the greatest common divisor of p and q, each kept or removed whole; and no
  stitched state repeats every p − q or every p mod q. So on this route
  multiples and shared divisors come by definition, and subtraction does not
  come at all.
- **What the knot law adds (exact to span 12; proved for the mirror).** Under
  not-all-equal every harmony found repeats at even periods only, and flipping
  every value pairs the offsets of two harmonies exactly when their periods
  carry different powers of 2. No stitch reads whether one period divides the
  other, so division as a yes-or-no fact is not read.

**The census.** The test of the outcomes and of the end grows meeting
patterns of not-all-equal knots under four random processes, each with its
own weighting: knots placed uniformly on a fixed set of distinctions; growth
with new distinctions; growth along co-knotted pairs; and **newest-w growth**,
in which each new knot holds only distinctions among the w that arrived last.
Growth is counted in **moves**, each adding one knot, up to a **horizon**. On
the patterns that live and on the last bases it reads the **tie classes**,
sets of distinctions forced equal or unequal, the **minimal contradictions**,
sets of knots that allow no state while every proper part allows one, and how
bond distance compares with steps apart, including how fast **step balls**,
the distinctions within r steps, grow.

**What it found** (computed, under these weightings; refereed). Uniform
patterns away from their end, and growth with rare closings, read as rulers:
two distinctions d steps apart lie in a least bond of d + 2 for nearly every
pair. (Where knots form no cycle that is a theorem; these patterns are full of
cycles, and some living ones carry ties and shortcuts.) Uniform knots end
suddenly: within about twenty knots, consistent with the same number at every
size from 50 to 300 distinctions, the law ties nine tenths of the base into
one class. Growth that keeps adding distinctions, at the closing rates
measured, carries large tie classes for much of its life and ends with no
final jump.
Growth among the newest four distinctions never ends (proved), and the law
counts along it, its least bond growing in proportion to distance, except
where closings are so rare that no bond spans far stretches; where every knot
is present it repeats with period four
([decision note](research/RANDOM-FATES-20261112-001/random_fates.md)).

**What tests each part.**

| Part | Standing | Tested by |
| --- | --- | --- |
| Nothing chooses; ours is coincidental | interpretation (A15); no proof or experiment can settle it | none |
| Other realities are other knot patterns | reading (A73); "binding patterns" an open definition | the census under other laws |
| Typical and rare meeting patterns | computed under four weightings: uniform and rare-closing patterns read as rulers away from an end | [RANDOM-FATES-20261112-001](research/RANDOM-FATES-20261112-001/random_fates.md), closed and refereed (confirmed with fixes) |
| Global influence | computed under one weighting: typical once knots overlap, in three regimes (free, travelling, tied along a shift as states run out) | [COMMON-FOLD-20261112-001](research/COMMON-FOLD-20261112-001/common_fold.md), closed and refereed (confirmed with fixes) |
| What dense overlap reads as | computed: most travelling bases have two unlengthened shifts (at least 130 of 169); base 16's line is rare (3 of 169 grow across); bounded across on certified bonds in about half the rest | [TRAVEL-READ-20261112-001](research/TRAVEL-READ-20261112-001/travel_read.md), closed; refereed, narrowed |
| No length on whole quadrants | proved on one random base (two travel directions); on one-direction bases upper bounds only, compatible with a bound | [FAR-BOUND-20261112-001](research/FAR-BOUND-20261112-001/far_bound.md), closed and refereed (narrowed) |
| Two folds are the rule | computed: 147 of 169 travelling bases have two certified unlengthened shifts; growth only where no cone reaches | [SHIFT-COUNT-20261112-001](research/SHIFT-COUNT-20261112-001/shift_count.md), closed and refereed |
| Three outcomes | computed by process; growth among the newest four never ends and among five or more ends for certain (proved) | the same epic |
| Limits near the end | uniform knots: a jump in the last twenty knots (the known backbone), not a limit; growth that adds distinctions: a tie share that rises over its life and levels off before the end, read early it forecasts nearer ends; what ends it is not the uniform end but its degrees (growth along pairs) or correlations beyond them (closings anywhere) (computed) | the same epic; [LIFE-JUMPS-20261112-001](research/LIFE-JUMPS-20261112-001/life_jumps.md), refereed; [OLD-CORE-20261112-001](research/OLD-CORE-20261112-001/old_core.md), referee pending |
| Only relative | shortcuts computed; the direction of no length proved; relativity an analogy only | [FOLD-20261112-001](research/FOLD-20261112-001/fold.md), closed |
| Harmonies | owner's word; one reading (A70) | `HARMONY-ARITH-20261112-001`, closed: the law's harmonies are even (exact to span 12) |
| Subtraction and division | stitching multiplies and counts shared divisors, nothing subtracts (proved); divisibility not read | `HARMONY-ARITH-20261112-001`, closed; A70's challenge open |
| Bases within bases | two readings computed, differing in kind: stitched, nothing new is forced (proved); by substitution, what a block cannot spare is tied throughout | [BASES-WITHIN-20261112-001](research/BASES-WITHIN-20261112-001/bases_within.md), [SUBST-NEST-20261112-001](research/SUBST-NEST-20261112-001/subst_nest.md); which the owner means is open (A75) |
| Binding patterns | open definition, the owner's two pictures (logic in each knot; recursion) | none yet |

**Reading.** This lesson is the owner's picture and the coordinator's
readings of it. It claims nothing about physics, matter or minds, and none of
its readings is a theorem.

## Glossary

Each word below has the one meaning given here, and the guide uses no other
word for that meaning. Where it helps, an entry also gives the intuition
behind the word. Spatial words follow the rule of lesson 1.1, and the two
tables at the end give the literature's name for each object and the words
that earlier records used in two senses.

- **Distinction.** Two alternatives of which exactly one holds: one bit
  (lesson 1.1). A distinction is open when it is free on its own, taking
  both values; each loop brings an open distinction to a knot. The intuition:
  the least thing that could be otherwise. Everything in the guide is built
  from distinctions and from rules about them, and nothing else is assumed,
  not even a place to put them.
- **Joint state.** A value for every variable, written as a string such as 110
  (lesson 1.1). The guide calls it a state for short.
- **Flip graph.** The states of some variables, two of them linked when they
  differ in exactly one variable. The guide draws the flip graph of three
  variables as the cube of states, and the cube is only that drawing
  (lesson 1.1).
- **Rule.** A constraint: it rules out some joint states, as a clause does
  (lesson 1.2). A **system** is a set of rules, read only through the states it
  allows. A **law** is a rule given once and put everywhere in a pattern: on
  every knot of a knot pattern, as the not-all-equal law of lesson 4.7, or at
  every cell of a board, as a uniform law of lesson 4.6. A law is part of what
  is put in. What the allowed states force beyond it is read as bonds, and the
  guide never calls that a law.
- **Relation.** The set of joint states a system of rules allows. Two systems
  that allow the same states are the same relation (lesson 1.2).
- **Free.** A set of variables is free when every combination of their values
  occurs in some allowed state. The guide also calls such a set
  **unconstrained**, and any other set **constrained** (lesson 1.2). The
  intuition: the rules say nothing about a free set, since whatever it does,
  the other variables can go along with it.
- **Clause.** An "or" of letters, each possibly negated, such as
  `¬A ∨ ¬B ∨ c`. It rules out one assignment of its own variables, and a list
  of clauses that must all hold is a **CNF** (lesson 1.2).
- **Emergence.** What a system of rules shows as a whole and none of its rules
  shows alone, as the Game of Life's patterns do on a grid (lesson 1.3). The
  program places the first emergence at the first knot. The intuition: the
  whole holds something no part holds, so only the whole can show it.
- **Loop.** A logical structure that leaves a distinction open (lesson 1.4).
  The intuition, in the owner's words, is a closed "string" that can "weave in
  and out and around other loops": a tangle slides off a string with loose
  ends, so only closed loops stay knotted. A cycle of co-knotted pairs is not a
  loop; what earlier records called the loops of a two-fold weave are its
  unfilled cycles.
- **Contact.** The variable through which a knot binds loops (lesson 1.4). A
  distinction that several knots share is a shared distinction, not a contact
  (lesson 2.1).
- **Atom.** The knot `¬A ∨ ¬B ∨ c`, also written A ∧ B → c, or A, B → c, and
  read "A and B together demand c": it forbids only the state with A and B
  but not c (lesson 1.5). It excludes fewer states than any other knot, so it
  is the weakest bond (lesson 2.3). It is neither the atomic formula of logic
  nor what earlier records called a Fano atom, now a Fano piece.
- **Forgetting.** Ignoring a variable: a state of the others stays allowed when
  some value of the forgotten one completes it. What remains is the
  **projection**, or **shadow**, on the others (lesson 1.6).
- **Witness.** An auxiliary variable that reports on something, such as
  whether two loops are bound. Witnesses are quantified away before a verdict
  (lesson 1.6). The intuition: a witness is how a system reads itself from
  inside. It is one more distinction of the same system, so what it reports
  holds across the allowed states, and in any one state it has one value
  (lesson 2.3). Whatever supplies an input that the system does not make, such
  as the held inputs of the learning line, is **the outside**, and whoever
  studies a system without being part of it is an **observer** (lesson 5.2).
- **Shape.** The owner's word, kept in his own words only: any structure that
  rules make, together with those rules (lesson 1.7). The intuition, in his
  words: emergent structures "are rules, and rules within rules". For the
  program's own objects the guide says meeting pattern, and for the sets a
  system leaves free, free complex.
- **Knot.** A relation that is constrained as a whole and unconstrained in
  every part (lesson 2.1). The intuition: a binding that lives only in the
  whole. Forget any one variable and nothing is left tied, as in the
  literature's Borromean rings, three rings that hold together though no two
  of them are linked. A knotted rope, the object of classical knot theory, is
  a **classical knot** (lesson 6.3).
- **Hub.** One variable shared by several separate relations, such as
  `(¬A ∨ c) ∧ (¬B ∨ c)`. Sharing identity is not a binding (lesson 2.1).
- **Overlap.** Knots overlap when they share a distinction, a **shared
  distinction**. Nothing limits how many knots one knot overlaps, or which
  (lesson 2.1). The intuition: knots do not sit side by side in a space. They
  meet only by sharing what they bind, as the owner's loops weave in and out
  and around other loops.
- **Meeting pattern.** Which knots share which distinctions, with the knots'
  rules left out; finitely or infinitely many knots, any of which may share
  distinctions with any number of others (lesson 2.1). It is what the record
  calls "how knots meet". The intuition, in the owner's picture: the overlaps
  themselves, loops weaving in and out and around other loops, whatever rules
  the knots carry. The literature writes a meeting pattern as a hypergraph,
  its vertices the distinctions and its edges the knots (lesson 6.2).
- **Knot pattern.** Knots with their rules, finitely or infinitely many,
  together with their meeting pattern (lesson 2.1).
- **Base.** A knot pattern that allows at least one state, in the sense of the
  owner's "base reality": different meeting patterns, infinite ones included,
  make different bases (lesson 2.1). The intuition: a reality built
  from the bottom up, out of nothing but knots and which distinctions they
  share. The foundation's **admissible base** is the general notion, declared
  primitives and native rules of any kind with their semantics, admitted maps
  and a coherence witness
  ([docs/COMMON_VERBIAGE.md](docs/COMMON_VERBIAGE.md)). A base whose
  semantics and admitted maps are declared is an admissible base, and the
  program reads every coherent admissible base as co-real (lesson 7.1). What a
  base can read of itself is its relation, and different bases can allow the
  same one: under the not-all-equal law, knot patterns with the same number of
  knots on every pair allow the same states (lesson 4.7).
- **Co-knotted pair.** Two distinctions in a common three-place knot of a
  meeting pattern (lesson 2.1).
- **Two-fold weave.** A meeting pattern of three-place knots in which every
  co-knotted pair lies in exactly two knots and the knots at each distinction
  form one cycle, each sharing a pair with the next (lesson 2.1). Where no
  other pattern is in view, the record says weave for short. The literature
  draws a two-fold weave as a closed surface. The intuition: the one meeting
  pattern that can be written down flat, in the owner's words a "flat
  structure" that can "represent the folded compressed structure" but is not
  it.
- **Patch.** A finite meeting pattern of three-place knots whose co-knotted pairs all
  lie in two knots except the pairs of one cycle, its **selvage**, which lie
  in one; in which the knots at each distinction form one cycle, or one path
  for a distinction on the selvage; and whose Euler count is 1. The
  literature draws a patch as a disc and its selvage as the disc's boundary.
  Selvage is the weaver's word for the finished border of a cloth.
- **Unfilled cycle.** A cycle of co-knotted pairs of a two-fold weave that is
  the selvage of no patch inside the weave: the literature's non-contractible
  cycle. The fewest pairs in an unfilled cycle is the literature's
  edge-width. The intuition: a way around the weave that no part of it closes
  off.
- **Euler count.** Distinctions minus co-knotted pairs plus knots, for a
  pattern of three-place knots: the literature's Euler characteristic.
- **Orientable.** A two-fold weave is orientable when each knot can be given
  a cyclic order of its three distinctions so that, at every co-knotted pair,
  the two knots that contain it put its two distinctions in opposite orders:
  the literature's orientable surface, drawn as two-sided.
- **Cycle pairs.** In a connected orientable two-fold weave, (2 − Euler
  count) / 2: the number of pairs of independent unfilled cycles, the
  literature's genus, or number of handles. A **zero-pair weave** has Euler
  count 2, the literature's sphere, and a **one-pair weave** has Euler count
  0, the literature's torus.
- **Six-regular.** Every distinction in exactly six knots. A finite
  six-regular two-fold weave has Euler count 0, so a connected one is a
  one-pair weave or a weave of Euler count 0 that is not orientable: the
  literature's flat torus and flat Klein bottle. The **endless six-regular
  weave** is the infinite connected one in which every cycle is filled, the
  selvage of some patch: the literature's triangular lattice, drawn as the
  plane.
- **Majority.** The state that takes, in each variable, the value at least two
  of three given states take. Systems of two-place rules are closed under it,
  and knots are not (lesson 3.1).
- **Free complex.** The collection of all the sets of distinctions a system
  leaves free (lesson 3.3). Every part of a free set is free, so it is a
  simplicial complex; in the literature's terms it is the family of sets that
  the allowed states shatter. A **hole** is a gap in it, and a knot is the
  smallest kind of hole. A **hollow triple** is three free pairs whose triple
  is not free, as under every three-place knot, which the literature draws as
  an empty triangle. The intuition: the free complex records, for every set
  of distinctions, whether the rules leave it alone.
- **World.** With 1 read as "exists", the set of things that exist in an
  allowed state (lesson 4.2), so counting worlds is counting allowed states
  (lesson 6.1). A knot pattern is not a world: what earlier records called
  flat worlds and disc worlds are bases, weaves and patches. The foundation's
  world branch is always written in full.
- **Requirement.** A rule saying what must exist when other things do, such as
  `A ∧ B → c`. A **choice** says that when something exists, one of several
  things must, such as `c → A ∨ B` (lesson 4.2).
- **Bond.** A set of a system's distinctions on which its allowed states, with
  every other variable forgotten, form a knot; its size is its number of
  distinctions (lesson 4.6). A rule of the system that is a knot gives one
  kind of bond, and bonds can also be read off the allowed states where no
  single rule is a knot. Bonds are compared by size, and also by how many
  states they exclude: the atom, which excludes the fewest, is the weakest
  bond (lesson 2.3).
- **Bond distance.** The size of the smallest bond containing two
  distinctions, minus one, read from the allowed states alone. A **ball** is
  the set of distinctions within a given bond distance of one of them, and how
  fast balls grow gives a dimension (lesson 4.6). The intuition: two
  distinctions are as near as the least knot that ties them, so the ruler
  comes from the rules and is never drawn.
- **Steps apart.** Two distinctions are d steps apart when the shortest row of
  co-knotted pairs leading from one to the other, each pair sharing a
  distinction with the next, has d pairs (lesson 4.7): the literature's graph
  distance. It is a count on the meeting pattern, given with it, and the ruler
  of lesson 4.7 is the theorem that bond distance measures it. On a board, a
  step is a move from a cell to a neighbour (lesson 4.6).
- **Faithful.** A law reads a knot pattern faithfully when its allowed states
  freeze no distinction, tie no pair, and leave no hollow triple except the
  pattern's own knots, so that the knots can be read back from the allowed
  states (lesson 4.7). A distinction is **frozen** when it takes one value in
  every allowed state.
- **Periodic.** A base is periodic when one block of distinctions and knots
  repeats at every whole number, one shift, or at every pair of whole numbers,
  two shifts (lesson 4.7): the literature's periodic hypergraph over ℤ or ℤ².
  A **finite repeat** identifies the blocks whose shifts differ by chosen
  amounts, the literature's periodic quotient.
- **Harmony.** The owner's word, read as assumption A70 (open to challenge):
  a base periodic along one shift all of whose allowed states repeat, so that
  it has finitely many states up to shifting; the literature's finite
  subshift. Not the harmony of proof theory. The **period** of a state is the
  least shift that returns it to itself, which is not the period of the base;
  an **orbit** (the literature's word) is a repeating state with all its
  shifts; a state is **antiperiodic** (the literature's word) when flipping
  every value is the same as shifting it by half its period. The intuition: a
  repeat the law makes, not one drawn into the meeting pattern. Under
  not-all-equal no harmony has an odd period up to 29, or at 31
  or 37, and one has period 61 (corrected 2026-11-12). The owner has also
  used the word for a relation in which incommensurable parts cancel (22
  October 2026), for drawn polygons whose ratio of perimeter to diameter is
  rational, against "a ratio that continues" (7 November 2026), and for
  "something like natural numbers" (11 November 2026; lesson 7.3), so the
  reading is one assumption about his word, not its only sense.
- **Stitch.** A knot of one fixed kind, at every shift, holding distinctions
  of two or three harmonies, such as one on (a_{i+s}, a_{i+t}, b_{i+u});
  harmonies with stitches are **stitched**. The members' **lags** s, t, u
  count only up to a common addend; a stitch with all lags equal, such as
  (a_i, b_i, c_i), is **unlagged**, and any other is **lagged** (bases within
  bases, 12 November 2026). (They overlap instead when a_i and b_{i+s} are one
  shared distinction.) The **offset** of two orbits of periods p and q is the
  shift between their states counted modulo gcd(p, q), the literature's
  relative phase; a stitch keeps or removes each offset whole. The intuition:
  stitching multiplies periods into their least common multiple, and the
  shared divisor counts the ways two harmonies can sit against each other.
- **Distinction substitution.** Each distinction v of a pattern is replaced
  by a copy of a block, with distinctions (v, p), and each knot (x, y, z) by
  the **between-copy knots** ((x, p), (y, q), (z, r)) for the **block
  triples** (p, q, r) in a set fixed by the block (its own knots, in every
  order, or every triple of distinct distinctions). A distinction p of the
  block is **spare** when its other distinctions can be given values with
  every knot of the block holding both values without p; p's **part** is the
  distinctions (v, p), and it is tied when they lie in one tie class.
  The intuition: with the block's own knots between copies, a part is pinned
  across the whole pattern exactly when the block cannot spare its
  distinction, that is, when no state of the block survives flipping it alone
  (proved: the pinning theorem, 12 November 2026); the pin is always an
  equality, carried one knot at a time.
- **Knot substitution.** Each knot is replaced by a copy of a **gadget** (the
  complexity literature's word), a pattern glued to the knot at its three
  **terminals**, again and again (the literature's hierarchical lattice). A
  gadget that treats its terminals alike decides every level at the first:
  the law is kept, freed, its terminals forced equal, or the pattern ends.
- **Tie extent.** Of a distinction, the most steps apart to a distinction
  tied to it: how far fixing it forces a value.
- **Locked.** Copies are locked when they are equal, place by place, in every
  allowed state: one copy then fixes all of them (which loops lock, 12
  November 2026).
- **Copy shifts; unmixed and mixed knots.** Copies of a harmony placed at the
  pairs of whole numbers (r, c), repeated n × m; the two shifts of this
  arrangement are the **copy shifts** e₁ and e₂, always told apart from the
  harmony's own shift inside each copy. An **unmixed knot** holds three copies
  one step apart along one copy shift, (x, x + e, x + 2e); the **mixed knot**
  holds (x, x + e₂, x + e₁), one step along each (the literature's three-dot
  shape of Ledrappier's law). The intuition: unmixed knots make rows and
  columns that are rings and nothing more; the mixed knot is the smallest that
  ties both shifts at once (locks across two shifts, 12 November 2026).
- **Stepped state.** A state of copies along two shifts in which each step
  along a copy shift applies one fixed symmetry of the harmony (a shift or a
  flip of every value): X(r, c) = g^r h^c u, the literature's constant
  voltage.
- **Short step.** A step of the copy arrangement of at most two copies along
  each copy shift. A state **repeats along** a step when moving every copy by
  it gives the same state up to one symmetry of the harmony. A state that
  repeats along a short step is read as a walk around one cycle (assumption
  A77); one that repeats along no step at all is two-way.
- **Stitch pairs; ratio subgroup; permutive sub-stitch.** For one orbit of a
  harmony under its shifts and flip, the **stitch pairs** are the pairs of
  symmetries (y, z) for which a state u, y·u, z·u stitched in one order is
  allowed. A **ratio subgroup** is a cyclic group of stitch pairs (g, λg) with
  ratio λ not 0 or 1 at an odd prime (the literature's line through the
  origin); it gives an **additive** automaton, the kind behind Ledrappier's
  law. A **permutive sub-stitch** is a set of allowed triples in which, for
  every two members from its set of states, exactly one third completes a
  triple (the literature's quasigroup or permutive law). A harmony's stitch
  has none (lines in the increments, 12 November 2026).
- **Lifted phase; step pairs; mean steps.** On copies of one orbit along two
  copy shifts, a **lifted phase** counts each copy's shift from a fixed state
  in whole numbers, so that the steps around any four mutually neighbouring
  copies sum to zero (the literature's height function); its **step pairs**
  are the pairs of phase steps along the two copy shifts; its **total steps**
  are the sums around a row and a column of copies, and its **mean steps**
  those divided by the counts. Bounds on the mean steps, fixed by counting the
  copies of each step pair (the literature's slope polygon), decide which
  repeats it fits.
- **Flip-blind parity knot; count r; fixed by count 0.** A **flip-blind
  parity knot** on three copies requires their placewise sum to be all 0s or
  all 1s, through one hidden reference distinction per knot (assumption A78:
  built from not-all-equal knots, unlike plain parity, which needs a zero).
  **Count r** is the set of copies whose count along the first copy shift is r
  (the literature's row of an array). Up to flips, each copy may be flipped on
  its own. Count r is **flip-frozen** when all states share it up to flips;
  **fixed by count 0** when states agreeing on count 0 up to flips agree on
  it; **reached by propagation** when knots with two known members whose
  relation forces the third make all its copies known from count 0. **Fixed
  but unreached**: fixed, not flip-frozen, not reached; **full fixing**: every
  count fixed by count 0 and some count not flip-frozen (a parity knot among
  stitched copies, 12 November 2026).
- **Shortcut.** A pair of distinctions whose bond distance is less than their
  steps apart plus one (lesson 4.7). The endless six-regular weave has none;
  some periodic bases that overlap have many.
- **Unlengthened shift.** A shift of a periodic base along which the law
  keeps distinctions arbitrarily many shifts away within a bounded bond
  distance (lesson 4.7); base 16 has one. Counting from one distinction, the
  others have an **along-count**, how many of that shift, and an
  **across-count**, how many of the other (literature: coordinates, drawn as
  column and row). Earlier records called the direction the fold; the owner's
  folded, compressed structure keeps his own word. The intuition: the law
  reads the base as having no length along that shift.
- **Self-keeping set.** Distinctions at one along-count, with values, in which
  every member has an equal partner in the set one more or two fewer across
  (lesson 4.7). The law then passes every member's value on, flipped, to the
  next along-count, so the set travels along the unlengthened shift forever.
  The largest self-keeping set in a pattern is its **self-keeping part**, and
  far along a pattern forces exactly what its self-keeping part forces.
- **Heddle.** Three distinctions at consecutive across-counts, then every
  second across-count up to a given one, all at one along-count: the least
  self-keeping set reaching that far across (lesson 4.7). With one far
  distinction at its last across-count it is a **heddle bond**. The word is
  the weaver's, for what lifts every other thread. Earlier text called it a
  ladder, which the literature uses for another object.
- **Chain.** Rules in a row, each sharing one distinction with the next: a
  chain of implications (lesson 1.4), of two-place ties, or of knots. Closed
  up, a chain of implications is a loop of the picture of lesson 1.4. Along an
  endless chain of atoms, which earlier records called a thread, bond
  distance grows by one per step, and the literature draws it as the number
  line (lesson 4.6).
- **Board.** Cells, and which cells are neighbours, either given before the
  rules or made of distinctions (lesson 4.6). A **cell** is what holds one
  value, as in the Game of Life. The **commuting board** is the board on which
  the steps xy and yx always reach the same cell: the literature's grid ℤ²,
  drawn as the plane. A **declared cycle** is a word of steps that a law's
  clauses say comes back to where it started, and the **commuting cycle**
  xyx⁻¹y⁻¹ is the declared cycle of the commuting board, which the literature
  draws as a closing square.
- **Refutation.** A proof that a system allows no state at all (lesson 5.1). A
  system that allows no state is a **contradiction**.
- **Depth.** How much of a knot pattern an observer must hold at once to see a
  hole in it (lesson 5.2).
- **Drawn knot pattern.** A knot pattern given together with a drawing on a
  surface, which earlier records called a knot space: every knot holds three
  distinctions and every distinction lies in three knots, and the drawing is a
  two-coloured triangulation whose triangles of one colour are the knots and of
  the other colour the distinctions, each distinction lying in the three knots
  across its three sides. Two distinctions may share one knot or two. The
  triangulation's vertices are the record's faces: the corners of the knots
  around a vertex make one face, where the record reads its even faces. The
  drawing is a declared substrate, so the words that describe it, such as face, corner,
  sphere, torus, handle and genus, are the drawing's and are marked as drawn.
- **Three-regular contradiction.** A pattern of not-all-equal knots in which
  every distinction lies in exactly three knots and that allows no state
  (lesson 6.2); earlier records called it a three-fold space. The record cuts
  one into Fano pieces and the rest, which it calls glue. The **Fano pattern**
  is seven distinctions and seven three-place knots, every two distinctions in
  exactly one knot: the literature's Fano plane, its knots the plane's lines.
  A **Fano piece** is the Fano pattern with one distinction or one knot
  removed, which earlier records called a Fano atom.
- **Piece.** A drawn knot pattern with one distinction removed, grown
  into a larger drawn knot pattern in place of one of its knots (lesson 4.7);
  earlier records of the learning line called it an atom, a torus or Fano
  atom. Depending on the signs of the law, a piece **acts** as the knot it
  replaced, allowing on that knot's three distinctions just what the knot
  allows, or is **transparent**, allowing every combination there. A Fano
  piece is the same idea in a three-regular contradiction.
- **Sample.** One meeting pattern produced by one run of a declared random
  process (lesson 7.3); several runs give samples. A meeting pattern the
  record writes down by hand is also read as one sample, of meeting patterns
  none of which is chosen. The literature's random hypergraph, or a
  realization; probability's "outcome" is this, and the guide never uses
  "outcome" in that sense. The guide does not say "draw", since drawn means
  given with a drawing.
- **Weighting.** The chance a declared random process gives to each set of
  meeting patterns, adding up to one (lesson 7.3): the literature's
  probability distribution. A process has a weighting; two processes can
  share one. No weighting gives infinitely many finite meeting patterns equal
  chances, so each must be declared, and a claim of what is typical or rare
  names its process.
- **Outcome.** What becomes of a knot pattern grown one knot at a time
  (lesson 7.3), one of three: it **resolves to nothing**, allowing no state
  from its first knots; it **ends**, at the first knot after which it allows
  no state, its **last base** being the pattern before that knot; or it
  **goes on forever**, a base at every stage, said only with a proof. A
  computation reports only that a pattern is **still a base at the horizon**.
  The outcome belongs to the growth, in its order, not to the pattern it
  reaches. The intuition: the owner's combinations that "resolve to nothing",
  "go for a while then die" and "go on forever".
- **Move.** One step of a growth: it adds one knot, or nothing when the
  process has nothing left to add (lesson 7.3). Growth is counted in moves,
  never in steps, which belong to steps apart. The **horizon** is the number
  of moves computed.
- **Newest-w growth.** Growth in which every new knot holds only distinctions
  among the w that arrived last (lesson 7.3). The process supplies the order
  of arrival.
- **Tie class.** Two distinctions are **tied** when they are equal in every
  allowed state, or unequal in every allowed state (lesson 4.7). Being tied is
  an equivalence, and a tie class is one of its classes with two or more
  members. Under not-all-equal nothing is frozen, so a tie class is the most
  the law can force.
- **Minimal contradiction.** A set of knots that allows no state while every
  proper part of it allows one, minimal under removal and not necessarily
  smallest (lesson 7.3): the literature's minimal unsatisfiable subformula.
  The smallest for three-place not-all-equal knots is the Fano pattern of
  seven knots.
- **Step ball.** The distinctions within r steps of one distinction: a count
  on the meeting pattern (lesson 7.3). A ball, unqualified, is measured by
  bond distance.
- **Binding pattern.** The owner's word, not yet defined: in his words, "This
  is what we're trying to discover" (lesson 7.3). He offers two pictures,
  logic carried in each knot that binds whole knot patterns together, and
  recursion in which inner parts are placed by the larger ones. Until one is
  chosen the guide uses it only in his words.
- **Fractal.** The owner's word, kept in quotation only: "the fractals are
  consequences of rules", with "logic fractals to infinity for irrational
  numbers" (lesson 7.3). It is not the literature's self-similar set, and the
  record's drawn self-similar substrates keep the literature's names, such as
  the Sierpinski gasket.
- **Words for space.** The guide names its objects by distinctions, knots and
  counts. It keeps spatial words for classical objects it cites, for pictures
  it says are drawn, and for space, distance and dimension themselves, each
  with its native definition (lesson 1.1). The table gives each of the guide's
  words with the name the literature uses, so that results can be found
  there.

  | The guide's word | What it is, by counts alone | The literature's spatial name |
  | --- | --- | --- |
  | distinction | a variable | point, vertex, site |
  | knot (three-place) | a relation on three distinctions passing K1–K3 | triangle, when drawn in a surface; line of a triple system, such as the Fano plane |
  | co-knotted pair | two distinctions in a common three-place knot | edge |
  | meeting pattern | which knots share which distinctions, rules left out | hypergraph |
  | knot pattern | knots with their rules, and their meeting pattern | constraint network on a hypergraph |
  | base | a knot pattern that allows a state | (none; a space is what the program hopes to build from one) |
  | two-fold weave | every co-knotted pair in exactly two knots, the knots at each distinction in one cycle | closed triangulated surface |
  | patch; selvage | a finite pattern of Euler count 1 whose one-knot pairs form one cycle; that cycle | disc; its boundary |
  | unfilled cycle | a cycle of co-knotted pairs that is the selvage of no patch | non-contractible cycle; the shortest one's length is the edge-width |
  | tour | in a graph with a cyclic order at each vertex, the closed walk that leaves each vertex by the edge after the one it came in on | face of a map |
  | Euler count | distinctions − co-knotted pairs + knots | Euler characteristic |
  | orientable | each knot's distinctions ordered so that the two knots at every pair order it oppositely | orientable, two-sided |
  | cycle pairs | (2 − Euler count) / 2, in a connected orientable weave | genus, handles |
  | zero-pair weave | a connected orientable weave of Euler count 2 | sphere |
  | one-pair weave | a connected orientable weave of Euler count 0 | torus |
  | non-orientable weave of Euler count 0 | connected and not orientable, Euler count 0 | Klein bottle |
  | six-regular | every distinction in exactly six knots | flat, 6-regular |
  | six-regular one-pair weave | a one-pair weave with every distinction in six knots | flat torus, triangular-lattice torus |
  | endless six-regular weave | infinite, connected, six-regular, every cycle filled | triangular lattice, drawn as the plane |
  | chain; endless chain of atoms | rules in a row, each sharing one distinction with the next; along atoms, bond distance grows by one per step | path; number line |
  | steps apart | the fewest co-knotted pairs in a row from one distinction to another | graph distance |
  | periodic base; finite repeat | one block repeated at every whole number or pair of whole numbers; that base with blocks identified | periodic hypergraph over ℤ or ℤ²; periodic quotient |
  | ball | the distinctions within a bond distance of one of them | ball, disc |
  | dimension | how fast balls grow: like r^D gives D | dimension |
  | flip graph | states linked when they differ in one variable | cube (of states), hypercube |
  | free complex | the sets a system leaves free | complex of shattered sets, drawn as points, edges and filled triangles |
  | hollow triple | three free pairs whose triple is not free | empty triangle, circle |
  | board; cell | cells and which are neighbours; what holds one value | grid, Schreier graph; site, vertex |
  | commuting board | the board on which the steps xy and yx always meet | grid ℤ², drawn as the plane |
  | declared cycle; commuting cycle | a word of steps that a law says comes back; xyx⁻¹y⁻¹ | face; closing square |
  | drawn knot pattern | every knot holding three distinctions and every distinction in three knots, drawn as a two-coloured triangulation: knots one colour, distinctions the other, faces at its vertices | the record's knot space; its drawing a checkerboard triangulated surface |
  | three-regular contradiction | not-all-equal knots, every distinction in three, no allowed state | non-2-colourable 3-regular 3-uniform hypergraph |
  | Fano pattern; Fano piece | seven distinctions and seven knots, every two distinctions in one knot; that pattern less one element | Fano plane; Fano plane less a point or a line |
  | unlengthened shift; along-count, across-count | a shift the law does not lengthen; how many of each shift separate two distinctions | (none for the shift); coordinates of the sheared frame, drawn as column and row |
  | heddle | three consecutive across-counts and every second one after them, at one along-count | (none; drawn as a column of a grid) |
- **One word, one meaning.** Earlier records used some words in two senses
  (lesson 1.1). The guide keeps one sense of each and gives the other its own
  word. The
  table also lists words the guide keeps only in quotations or for the
  literature's objects.

  | Word | Its one meaning in the guide | Other senses in earlier records, and the word for each now |
  | --- | --- | --- |
  | base | a knot pattern that allows a state (lesson 2.1) | the foundation's general notion: admissible base, written in full; knot patterns that allow the same states: one relation, never one base |
  | world | an allowed state, read with 1 as "exists" (lesson 4.2) | a pattern of knots ("flat world", "disc world", "knot world"): base, weave, patch or drawn knot pattern; the foundation's world branch, written in full |
  | shape | (the owner's word, in his own words only: any structure that rules make, lesson 1.7) | for the program's own objects: meeting pattern; the sets a system leaves free: free complex; the five kinds of three-place knot: classes |
  | loop | a logical structure that leaves a distinction open (lesson 1.4) | a cycle of a weave that no patch closes off: unfilled cycle; loop pairs: cycle pairs |
  | contact | the variable through which a knot binds loops (lesson 1.4) | a distinction several knots share: shared distinction |
  | open | of a distinction, free on its own (lesson 1.4) | the unjoined end of a chain or string: loose end; an open chain: chain |
  | atom | the knot ¬A ∨ ¬B ∨ c (lesson 1.5) | an end piece of a three-regular contradiction: Fano piece; a closed knot space less a point, grown in place of a line (the learning line's torus or Fano atom): piece |
  | knot | a relation constrained as a whole and free in every part (lesson 2.1) | a knotted rope: classical knot |
  | law | a rule put everywhere in a pattern (lesson 4.6) | a regularity the allowed states force: bond |
  | smallest bond | the bond with the fewest distinctions (lesson 4.6) | the knot that excludes the fewest states: weakest bond |
  | bond distance | read from the allowed states (lesson 4.6) | a count of knots or co-knotted pairs in a chain: steps apart (bases within bases and nesting by substitution, 12 November 2026, corrected) |
  | network | a network of loops (lesson 4.5) | a pattern of knots: knot pattern; the foundation's contact network, written in full |
  | space | what the program hopes to build, with native definitions (lesson 7.2) | three-fold space: three-regular contradiction; knot space: drawn knot pattern |
  | dimension | how fast balls grow (lesson 4.6) | the dimension of a hole or of a complex: the literature's, marked as such |
  | place | an argument position, as in three-place (lesson 3.2) | where a board holds a value: cell; the index of a stitch's members: lag (unlagged stitch, formerly "stitch at one place"); a block's position: its distinction (spare distinction, formerly "loose place") |
  | point | the owner's moving point, a state with a charge-like strength (his picture of learning), and otherwise the literature's | a variable: distinction |
  | line | (only in the owner's words and the literature's names, such as the number line and a Fano line) | a three-place knot: knot; an open chain: chain |
  | face | (the literature's only: a face of a map) | a knot of a weave: knot; a cycle a law closes: declared cycle |
  | flat | (only in the owner's "flat structure") | six knots at every distinction: six-regular; drawable without crossings: planar, the literature's |
  | balanced | (the doubling line's balanced stages, not used in the guide) | six knots at every distinction: six-regular |
  | two-sided | (none) | orientable |
  | side | (only in the owner's words: "the continuous edge of the loop", open to any number of others, lesson 7.3) | an edge of a drawn knot: the literature's; knots or bases "side by side": overlapping, or stitched (lesson 7.3), never side by side |
  | thread | (a thread of work, not used in the guide) | an endless chain of atoms: chain |
  | fold | (the owner's folded, compressed structure, in his words) | the direction the law does not lengthen: unlengthened shift |
  | ladder | (the literature's only, such as the n × 2 ladder graph) | three consecutive distinctions and every second one after them (ACROSS-FOLD-20261112-001's pre-registration): heddle; its rungs: the heddle's members after the three |
  | row, column | (a row: a sequence, as in steps apart and chain) | the indices of base 16's drawn frame: across-count, along-count |
- **Older records.** Records written before 11 November 2026 use the older
  words, and a record whose checksum another record pins (a manifest, a result
  or a discovery) is never edited, so it keeps them. Read such a record with the
  table above: a line of a triple system is a knot, a point a distinction, an
  atom of a three-fold space a Fano piece, an atom of a knot space (a torus or
  Fano atom) a piece, a three-fold or knot space a
  three-regular contradiction or a drawn knot pattern, a contact where several
  knots meet a shared distinction, and a world of knots a base, weave or patch.
