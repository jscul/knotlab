# Intuitions

The contact-first program asks whether logic can build structure, such as
holes, paths and spaces, without assuming a space to start from. Its working
answer begins with one object: the **logical knot**, two or more open
distinctions bound together so that the whole is constrained but no part is.

This page states the intuitions behind that answer in plain terms. Each one is
tied to what has been proved or checked in this repository, and each is
labelled by what kind of claim it is.

**The founding premise.** The program's question, whether logic can build
space, rests on a premise the owner states in his own words: "Distance is the
only form of information. That's the entire basis of the 'this versus that'
distinction in the smallest emergent unit." It is his premise and his
interpretation, not a result, and it is under test. Lesson 2.4 states it in
the guide's words, once the knot it speaks of has been defined, and shows how
the later lessons on distance and dimension hang from it.

The page is written as a textbook, to be read in order. Its ten chapters are
divided into lessons, and each lesson builds on the ones before it. Each
chapter opens with a lesson numbered 0, its introduction: an index of the
chapter's lessons, a line or two on each, and under it the chapter's
intuition in one paragraph. Chapter 1 sets up bits, rules and the notation,
including how to read A, B → c, before anything is built from them.

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
  - [1.0 Introduction](#10-introduction)
  - [1.1 Distinctions and states](#11-distinctions-and-states)
  - [1.2 Rules and what they allow](#12-rules-and-what-they-allow)
  - [1.3 Emergence in the Game of Life](#13-emergence-in-the-game-of-life)
  - [1.4 The picture](#14-the-picture)
  - [1.5 Reading A, B → c](#15-reading-a-b--c)
  - [1.6 Forgetting a variable](#16-forgetting-a-variable)
  - [1.7 What rules make](#17-what-rules-make)
- [Chapter 2. The knot test](#chapter-2-the-knot-test)
  - [2.0 Introduction](#20-introduction)
  - [2.1 The knot test](#21-the-knot-test)
  - [2.2 Knots on the cube](#22-knots-on-the-cube)
  - [2.3 What a knot hides](#23-what-a-knot-hides)
  - [2.4 Distance is the only form of information](#24-distance-is-the-only-form-of-information)
- [Chapter 3. Pairs and three places](#chapter-3-pairs-and-three-places)
  - [3.0 Introduction](#30-introduction)
  - [3.1 Two-place rules and the majority vote](#31-two-place-rules-and-the-majority-vote)
  - [3.2 Pairs cannot make a knot; three places can](#32-pairs-cannot-make-a-knot-three-places-can)
  - [3.3 The free complex of a system](#33-the-free-complex-of-a-system)
  - [3.4 Holes and knots](#34-holes-and-knots)
- [Chapter 4. How bindings behave](#chapter-4-how-bindings-behave)
  - [4.0 Introduction](#40-introduction)
  - [4.1 Easy and hard questions](#41-easy-and-hard-questions)
  - [4.2 Requirement and choice](#42-requirement-and-choice)
  - [4.3 Knots from competing pairs](#43-knots-from-competing-pairs)
  - [4.4 Which knots remember a loop](#44-which-knots-remember-a-loop)
  - [4.5 What networks of loops remember](#45-what-networks-of-loops-remember)
  - [4.6 Dimensions from rules](#46-dimensions-from-rules)
  - [4.7 Knots alone](#47-knots-alone)
  - [4.8 How does one level bind another?](#48-how-does-one-level-bind-another)
- [Chapter 5. Depth](#chapter-5-depth)
  - [5.0 Introduction](#50-introduction)
  - [5.1 Proving that nothing is allowed](#51-proving-that-nothing-is-allowed)
  - [5.2 How deep a hole is](#52-how-deep-a-hole-is)
  - [5.3 Forcing in rounds and phases](#53-forcing-in-rounds-and-phases)
- [Chapter 6. Counting](#chapter-6-counting)
  - [6.0 Introduction](#60-introduction)
  - [6.1 Counting worlds](#61-counting-worlds)
  - [6.2 The worlds of not-all-equal knots](#62-the-worlds-of-not-all-equal-knots)
  - [6.3 Counting on classical 3-manifolds](#63-counting-on-classical-3-manifolds)
- [Chapter 7. Sources and questions](#chapter-7-sources-and-questions)
  - [7.0 Introduction](#70-introduction)
  - [7.1 What is classical and what is ours](#71-what-is-classical-and-what-is-ours)
  - [7.2 Open questions](#72-open-questions)
  - [7.3 Every meeting pattern, none chosen](#73-every-meeting-pattern-none-chosen)
- [Chapter 8. How a law grows](#chapter-8-how-a-law-grows)
  - [8.0 What the program is building](#80-what-the-program-is-building)
  - [8.1 Growing in rounds](#81-growing-in-rounds)
  - [8.2 Four kinds of growth](#82-four-kinds-of-growth)
  - [8.3 Reading a blow-up by sampling](#83-reading-a-blow-up-by-sampling)
  - [8.4 What distance carries of what grows](#84-what-distance-carries-of-what-grows)
  - [8.5 Locality before space](#85-locality-before-space)
  - [8.6 Structure and state](#86-structure-and-state)
  - [8.7 Generators and folds of emergence](#87-generators-and-folds-of-emergence)
- [Chapter 9. Time](#chapter-9-time)
  - [9.0 Introduction](#90-introduction)
  - [9.1 A history is one allowed state](#91-a-history-is-one-allowed-state)
  - [9.2 What the rounds count](#92-what-the-rounds-count)
  - [9.3 Births one at a time: the order that is left](#93-births-one-at-a-time-the-order-that-is-left)
  - [9.4 Clocks made by the growth](#94-clocks-made-by-the-growth)
  - [9.5 Priority: which birth is made first](#95-priority-which-birth-is-made-first)
  - [9.6 Is time a fold of emergence?](#96-is-time-a-fold-of-emergence)
- [Chapter 10. Folds of emergence](#chapter-10-folds-of-emergence)
  - [10.0 Introduction](#100-introduction)
  - [10.1 What a fold of emergence would be, and the nearest things in the record](#101-what-a-fold-of-emergence-would-be-and-the-nearest-things-in-the-record)
  - [10.2 The with-and-without test: whether one part's course depends on another](#102-the-with-and-without-test-whether-one-parts-course-depends-on-another)
  - [10.3 Parts that meet again, under laws added by hand](#103-parts-that-meet-again-under-laws-added-by-hand)
  - [10.4 Two studies in design: a made copier and a made count of returns](#104-two-studies-in-design-a-made-copier-and-a-made-count-of-returns)
  - [10.5 What is open](#105-what-is-open)
- [Glossary](#glossary)

## Chapter 1. Bits and rules

### 1.0 Introduction

**The lessons.** What each lesson of this chapter is about:

- [1.1 Distinctions and states](#11-distinctions-and-states): a distinction
  is one bit, and nothing else is assumed. Three of them have eight joint
  states, drawn as the cube of states.
- [1.2 Rules and what they allow](#12-rules-and-what-they-allow): a rule rules
  out joint states, and a system is read only through the states it allows.
  The symbols, and what makes a set of variables free.
- [1.3 Emergence in the Game of Life](#13-emergence-in-the-game-of-life):
  Life's famous patterns are allowed states of one system of rules. Only its
  grid is drawn in advance.
- [1.4 The picture](#14-the-picture): a chain only orders its members, and a
  loop collapses to one free bit, its open distinction. What is real lies
  between bound loops: two loops, A and B, and a contact c.
- [1.5 Reading A, B → c](#15-reading-a-b--c): the atom, "A and B together
  demand c", forbids exactly one state. Every pair stays free while the three
  together are constrained.
- [1.6 Forgetting a variable](#16-forgetting-a-variable): forgetting a
  variable keeps each state of the others that some value of it completes.
  What remains is the system's shadow on them.
- [1.7 What rules make](#17-what-rules-make): rules make structures, and some
  run on forever. The owner calls them shapes; the guide says meeting pattern
  for which knots share which distinctions.

**The intuition.** Everything is built from one material, the distinction,
and from rules that rule out joint states. A system is known by the states it
allows and by nothing else: not by how it is written, and not by a board,
unless one is drawn. What behaves like an object, as a glider does in the Game
of Life, is a pattern among allowed states. The smallest rule that binds two
loops already shows what the guide is after: it constrains three distinctions
as a whole and leaves every pair free.

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
  every later layer is forced. Lesson 9.1 comes back to this.
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
loops, which lesson 2.1 calls a knot.

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
  erasing either loop removes it. The foundation calls this binding
  minimal contact-distance, and the owner's founding premise, that distance is
  the only form of information, is lesson 2.4.
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
Read by the disagreement count instead (lesson 2.4), the same kind of periodic
law gives smooth outlines: on the six-regular weave under not-all-equal the
distinctions of the start's own class within a given count fill a round
outline, and chain grids give outlines just off round
([COUNT-BALLS-20261118-001](research/COUNT-BALLS-20261118-001/count_balls.md),
refereed). Under bond distance every periodic law gives a polygon; under the
count it depends on the law: the diamond on split grids, smooth on chain grids,
round on the critical weave.

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

### 2.0 Introduction

**The lessons.** What each lesson of this chapter is about:

- [2.1 The knot test](#21-the-knot-test): a relation is a knot when it is
  constrained as a whole, forgetting any one variable leaves the rest
  unconstrained, and some state is allowed. Knots overlap by sharing
  distinctions, and which knots share which is their meeting pattern.
- [2.2 Knots on the cube](#22-knots-on-the-cube): on three variables every
  pair is free exactly when no two excluded states are neighbours on the cube
  of states.
- [2.3 What a knot hides](#23-what-a-knot-hides): the whole holds information
  that no pair holds, and never more than one bit. Two loops and a contact
  have 34 knots in five classes; parity hides the most and the atom the least.
- [2.4 Distance is the only form of information](#24-distance-is-the-only-form-of-information):
  the owner's founding premise. A knot's touch is the first distance, and
  distance is all the information there is. What hangs from it, and its open
  test.

**The intuition.** Lesson 1.5 found a rule that lives in the whole and in no
pair. A knot is exactly that: erase any one variable and the binding is gone.
The test says so on allowed states, the cube of states turns it into a
picture, and counting shows how little a knot hides, at most one bit. On the
owner's premise the touch a knot makes between its loops is the first
distance, and distance is the only form of information. The premise is his
interpretation, not a result, and it is under test.

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
Lesson 2.4 gives the owner's premise about what kind of thing the information
of this lesson is.

```bash
PYTHONPATH=tools python3 -m knotlab patterns
```

### 2.4 Distance is the only form of information

**The premise.** On 17 November 2026 the owner stated, in his words, the
premise that the program's question rests on: "Distance is the only form of
information. That's the entire basis of the 'this versus that' distinction in
the smallest emergent unit." It was, he said, "the entire premise of 'space
from logic'", and it "plays in with everything, like the dimensions from logic
too". It is the owner's premise and his interpretation. Nothing in the record
proves it, no result is derived from it, and the register of assumptions holds
it as A97, now under challenge (the last part of this lesson). This lesson
says what it means in the words of lessons 1.1 to 2.3, and which later lessons
hang from it.

**Relative, with an order.** Asked the same day whether his distance includes
which way or only how far, the owner answered:
"Distance is topological, so it will have some starting point, then go off
outward from there. So for example, 0 might be a starting point on the number
line. In my view, there isn't really any such thing as "direction". Everything
is just "relative", but it's also topological, so if you're at 3 on the number
line, you can't just skip 4 to get to 5, so there is an order."
The number line is his illustration, not a space the guide assumes. In the
guide's words, and as the guide's reading rather than his: a distance is
counted outward from a starting distinction, it has no direction, and nothing
farther can be reached without passing what lies between, so the distance
alone gives an order (the literature's betweenness, for a distance built from
unit steps). Along the chain of atoms of lesson 4.6, bond distance has this
property: every bond through w(s) and w(t) contains the loops between them
(proved). Whether the candidate distances of the test at the end of this lesson
have it was checked next (the end of this lesson).

Asked next whether that order already exists before any knot, as a chain of
plain implications has one (lesson 1.4), or comes only with one knot per step,
the owner found the question confusing and answered: "The knots are themselves
the smallest form of spatial topology. "3" as a concept is a topological
structure that exists but with relation to all other numbers, not just
neighbors." In his words, logical topology "is the very first instance of
"this versus that". From that, we can create space, set theory, everything
else", and he counts physics, the genetic code and consciousness among what it
builds, "just like in conways game of life". That wider view is his
interpretation, not a result. The guide reads his answer as putting the knot
first: nothing is his distance before the first knot, so the order that the
disagreement count finds on a chain of plain implications (the end of this
lesson) is not yet his distance, and minimal contact-distance appears with the
first knot. It reads "with relation to all other numbers, not just neighbors"
as distance being a relation over every pair, not only between neighbours; he
did not name one of the candidate distances.

**This versus that.** Lesson 1.1 starts from one material, the distinction:
two alternatives of which exactly one holds, with no space, no order and no
number. It treats a distinction as the least piece of information, since it
tells this from that. The guide reads the premise as saying what kind of thing
that telling apart is: a distance. On this reading nothing has information on
its own, as a value it carries; it has it only in its distance from what it is
told apart from. That continues the owner's stance of 22 October 2026 that
"everything is relational", that there are no values, only relations
([TWIST-RELATIONS-20261022-001](research/TWIST-RELATIONS-20261022-001/twist_relations.md)).
A lone distinction, though, stands apart from nothing. The program's
foundation says that before emergence logical things "may be themselves, but
they do not yet exist relative to one another"
([the thesis](docs/FOUNDATIONAL_THESIS.md#transcendental-logical-base)). So the
guide takes the premise to speak, in the owner's words, of the smallest
emergent unit, not of a lone distinction; whether a lone distinction holds
information on the premise is open.

**The first touch.** The smallest emergent unit is the knot (lessons 1.4
and 2.1): two loops bring open distinctions A and B, a contact c binds them,
and the whole is constrained while no part is. The foundation says what that
one binding makes: A is A, B is B, A differs from B, and c relates them without
making them one. From A's side, B now exists relative to A through c, and from
B's side, A exists relative to B through the same c. The foundation calls this
single touch at once the first atomic logical topology and **minimal
contact-distance**, "the smallest relative existence": one indivisible unit
with no magnitude, direction, coordinate or metric, not a number of anything
([the thesis](docs/FOUNDATIONAL_THESIS.md#emergence-atomic-topology-and-distance)).
Lesson 2.3 measured what such a binding holds that no part holds, in bits:
about 0.193 for the atom and one bit for parity. On the guide's reading, that
information belongs to the knot's touch; whether the bits themselves are a
distance is open (the last part of this lesson). The foundation already read
emergence as joint information, "a difference held by the whole and by no
part" ([the foundation's reading](docs/FOUNDATION_READING.md)), and the touch
as minimal contact-distance. The guide reads the premise as making the two
one, and as saying there is no other kind of information; the owner has not
put it in these words.

**Distances counted in knots.** Every distance the guide counts is counted in
knots, bonds or contacts, and each has its own definition. The touch itself
carries no number; the counts are the guide's.

- **Bond distance (lesson 4.6).** Two distinctions are as far apart as the
  smallest bond that contains them both, read from the allowed states alone,
  so no ruler is drawn. Along a chain of atoms, w(t−1) ∧ L(t) → w(t), the bond
  distance from w(s) to w(t) is t − s + 1, one unit for each loop between them
  (proved,
  [LOGIC-AXIS-20261107-001](research/LOGIC-AXIS-20261107-001/logic_axis.md)).
  It spaces distinctions only where knots compose. Where two knots meet only
  at a gate, a shared distinction one value of which satisfies both, no knot
  crosses it, and the register holds as assumption A39 that distinctions
  joined only through gates are not spaced at all
  ([BOND-CHAIN-20261108-001](research/BOND-CHAIN-20261108-001/bond_chain.md)).
- **Steps apart and the ruler (lesson 4.7).** Steps apart counts co-knotted
  pairs on a meeting pattern, and comes with the pattern. Under the
  not-all-equal law the knots measure it exactly on the endless six-regular
  weave: bond distance is steps apart plus one at every distance (proved and
  refereed, [RULER-20261111-001](research/RULER-20261111-001/ruler.md)). On a
  finite six-regular weave the same is proved while the steps apart stay
  below a third of the weave's margin, a number set by its unfilled cycles
  (for the orientable ones,
  [RULER-FLAT-20261111-001](research/RULER-FLAT-20261111-001/ruler_flat.md)),
  and on small weaves short unfilled cycles do shorten some bonds three steps
  apart
  ([KNOTS-ALONE-20261111-001](research/KNOTS-ALONE-20261111-001/knots_alone.md)).
- **Length across time.** A count of contacts along a route is a magnitude
  the record reads, by the owner's ruling of 8 November 2026 (assumption A40,
  its consequence checked by a frozen test), and distance across time was built from it in
  two exact forms on networks of rings
  ([DISTANCE-20261108-001](research/DISTANCE-20261108-001/distance.md)).

Extended distance along paths, or a metric, comes later still: the foundation
allows it only after paths and separation have been built from many contacts.

**Dimensions from logic.** The owner's idea of 7 November 2026, "a number
line/Cartesian plane where the dimensions themselves expand out in measures of
logic" (lesson 4.6), is the premise turned on the axes themselves. The guide's
meaning of dimension is built from distance alone: the distinctions within a
given bond distance of one of them form a ball, and when balls grow like r^D
the rules have dimension D (lesson 4.6). On the premise, a dimension is then a
property of information (reading): how many distinctions lie within a given
distance of one of them, as the distance grows. Where the record stands, with
this line of work parked:

- **One dimension, with nothing drawn (proved).** A rule that grows only at
  knots holding two loose ends grows an endless chain from a single knot, and
  bond distance counts one per step along it
  ([OPEN-END-GROWTH-20261107-001](research/OPEN-END-GROWTH-20261107-001/open_end_growth.md)).
- **Dimensions read back (proved).** Tseitin's parity law on a drawn grid of D
  steps has balls that grow like r^D, so the allowed states recover the grid's
  dimension (LOGIC-AXIS-20261107-001), and on knots alone the not-all-equal law
  reads dimension two on the endless six-regular weave, with the meeting
  pattern given (lesson 4.7).
- **No tested law selects its own dimension (reading).** Every board of
  dimension two was drawn or declared (assumption A51). When the board itself
  is made of
  distinctions, a law that declares no cycle never forces the commuting board
  (proved,
  [BOARD-DIST-20261110-001](research/BOARD-DIST-20261110-001/board_dist.md)).
- **Three dimensions are open.** The networks of knots studied so far do not
  tell apart some of the literature's different three-manifolds (proved for
  gluings that ignore which places meet,
  [HUB-DIMENSION-20261024-001](research/HUB-DIMENSION-20261024-001/dimension_three.md)), and the
  reading drawn from that, that native space is two-dimensional topology, is
  not proved.

The record is consistent with the premise in one more way, read before the
premise was written down (reading). Along an endless chain of atoms the unit
of bond distance is one loop, one open distinction. Under growth by substitution,
distance between existing distinctions grows exactly where the growth adds
loose ends, and every gadget that lengthened distance added three loose ends
and three open bits at each substitution, while bits added in closed cycles of
knots lengthened nothing (LOGIC-AXIS-20261107-001).

**What the premise does not say.** It does not put distance into logic: lesson
1.1 assumes none, and logic comes before space
([THEORY.md](THEORY.md#logic-comes-before-space)). On the premise, minimal
contact-distance appears with the first knot, where information first stands
relative to anything, and counted distances only where knots compose. It
gives the first touch no number. And it does not settle what a
system below emergence holds. A chain of two-place ties rules out states, as
the chain of lesson 1.4 orders its members, yet it has no knot and so no bond
distance at all (lesson 4.6). The foundation places such a chain below
emergence, where nothing yet exists relative to anything; whether the premise
counts what it rules out as information is the owner's to say.

**The open challenge.** The premise was tested directly on the day it was
recorded, and the test shows that which notion of distance is meant decides
the answer
([DISTANCE-INFO-20261117-001](research/DISTANCE-INFO-20261117-001/distance_info.md);
computed, and refereed with a Block on its first reading,
[referee's report](research/DISTANCE-INFO-20261117-001/referee-R1/report.md)).

- **Bond distance between pairs fails (computed).** On four distinctions,
  three of the four not-all-equal knots on them allow 8 states and all four
  allow 6, yet in both every pair lies in a knot of three, so every pair is at
  bond distance 2. The same distances, different states: read as the guide's
  bond distance, distance is not the only form of information, and that
  reading fails at the smallest size where it could.
- **How often two distinctions differ recovers three-place not-all-equal states (proved).** Count,
  for each pair, the allowed states in which the two take different values:
  the disagreement count. That table, read from the allowed states alone,
  determines the allowed states from four distinctions on when every rule
  imposes not-all-equal on three distinctions. Wider rules change the answer.
  On four distinctions a single four-place rule allows 14 states and the
  unconstrained base allows 16. Each pair differs in eight states in both
  bases because the two constant states contribute zero disagreements. On three
  distinctions it does not: one knot and no knot both give every pair 4, and
  only the rates, 4 of 6 against 4 of 8, tell them apart. It is a count across
  the allowed states, not an extended or metric distance in the program's
  sense, which the foundation allows only after paths and separation are built.

The disagreement counts therefore recover which states a three-place
not-all-equal base allows. The owner's answer above
rules out direction and asks for an order in which nothing is skipped. The
next test found where that order lives
([DISTANCE-ORDER-20261117-001](research/DISTANCE-ORDER-20261117-001/distance_order.md);
proved and computed, referee pending). In the disagreement count, c lies
between a and b exactly when no allowed state has a = b ≠ c, a three-place
constraint. Where the pairs of the three are all free, that constraint is a
knot. It can also follow from two-place rules alone: on the chain of lesson
1.4, x → y → z, which has no knot and "only orders its members", the counts
are 1, 1 and 2, an exact order with nothing skipped. Where the knots form no
cycle, one quantity read from the counts equals steps apart (lesson 4.7), so a
single distance carries the base and goes outward with nothing skipped. On
the thread and the six-regular weave, read with exact additive betweenness, the
two split: the count that carries everything puts no distinction between two
others, and steps apart, which has the order, does not carry everything
(computed). Read only as order, the weave's count does have a local order with
nothing skipped, but a start's nearest neighbours are its six knot-neighbours
and six more of its own class, not the weave's own six (computed by the study's
referee). So the split depends on how order is read, and it is not a property
of cycles. The guide leaves the owner's word open.

The register lists one more question: is the full bit that parity hides a
distance? Not a pairwise one. Under a parity knot every pair takes each of its
four joint values equally often, so no count of pairs sees it (proved, same
study). See A97 and A98 in the
[register](docs/ASSUMPTIONS.md#a97--distance-is-the-only-form-of-information).

**Reading.** Apart from the results it cites, this lesson is the owner's
premise and the guide's reading of it. Lessons 4.6 and 4.7 make its distances
exact, lesson 7.1 lists it among the program's readings, and lesson 7.2 asks
the question it leads to.

## Chapter 3. Pairs and three places

### 3.0 Introduction

**The lessons.** What each lesson of this chapter is about:

- [3.1 Two-place rules and the majority vote](#31-two-place-rules-and-the-majority-vote):
  whenever a system of two-place rules allows three states, it allows their
  majority. No knot on three variables does.
- [3.2 Pairs cannot make a knot; three places can](#32-pairs-cannot-make-a-knot-three-places-can):
  a system of two-place rules is known from its pairs, and a knot shows
  nothing in any pair. Three-place rules bind any number of loops.
- [3.3 The free complex of a system](#33-the-free-complex-of-a-system):
  collect every set of variables a system leaves free into its free complex.
  The gaps in it are holes.
- [3.4 Holes and knots](#34-holes-and-knots): a knot is the smallest kind of
  hole, a set whose every part is free but which is not free itself.
  Two-place rules make holes but never a hollow triple.

**The intuition.** Which rules can build a knot? Whatever a two-place rule
says, it says about a pair, and a knot shows nothing in any pair. So rules on
two variables never build one, and rules on three variables always can: three
places are where binding starts. Collecting what a system leaves free shows
where its knots sit, as the smallest holes. Logic allows every free complex,
so it selects no space; whatever space there is has to come from a law.

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

### 4.0 Introduction

**The lessons.** What each lesson of this chapter is about:

- [4.1 Easy and hard questions](#41-easy-and-hard-questions): the words for
  how hard a question is: linear time, polynomial time, NP-complete.
  Expressing a knot and deciding a system of knots are different questions.
- [4.2 Requirement and choice](#42-requirement-and-choice): read 1 as
  "exists". A requirement forces one least world and a choice leaves
  alternatives, and a knot can be the one under one reading and the other
  under another. Knots never select.
- [4.3 Knots from competing pairs](#43-knots-from-competing-pairs): three
  distinctions asked to differ pairwise cannot all do so. The states that
  break one preference form the not-all-equal knot, the only kind competing
  pairs make without hidden variables.
- [4.4 Which knots remember a loop](#44-which-knots-remember-a-loop): join
  copies of a knot into a ring and forget the witnesses. Only parity carries
  the loop at full strength at every length; other knots fade.
- [4.5 What networks of loops remember](#45-what-networks-of-loops-remember):
  contacts that act freely record each loop separately. Contacts with fixed
  points bind loops together, into atoms.
- [4.6 Dimensions from rules](#46-dimensions-from-rules): bond distance and
  dimension are read from the allowed states alone. An endless chain grows
  with nothing drawn, but every board of dimension two so far was given its
  neighbours in advance.
- [4.7 Knots alone](#47-knots-alone): take the board away. On the endless
  six-regular weave the not-all-equal law gives the meeting pattern back and
  measures it with an exact ruler. The meeting pattern itself is still put in.
- [4.8 How does one level bind another?](#48-how-does-one-level-bind-another):
  two knots that share one bit already bind four bits. Across the levels of a
  pattern with no cycle of knots, the smallest bond gains one member per level
  along a chain of knots.

**The intuition.** Knots behave in a few ways that the later chapters lean
on. A knot can be read as a requirement or as a choice, and it never selects.
Pairs that compete make a knot where pairs that must all hold cannot. Around
a ring only parity keeps the record of a loop at full strength, while atoms
bind loops together. And knots space distinctions apart: the smallest bond
that holds two distinctions gives a distance read from the allowed states
alone, and how fast its balls grow gives a dimension. What no tested law does
yet is supply its own meeting pattern: a board, or which knots share which
distinctions, is still put in. The chapter first fixes the words for easy and
hard questions, which these behaviours are measured by.

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
drawn on could obey rules too. It is his founding premise turned on space
(lesson 2.4): if distance is the only form of information, the axes are made
of that information. This lesson says what of that idea is proved, what is
computed, and what is still only an idea.

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
allowed states alone, so no ruler is drawn. It is the guide's exact measure
of how far apart two distinctions are, and the reading of the owner's premise
(lesson 2.4) that was tested first. On a chain of atoms,
w(t−1) ∧ L(t) → w(t), the bond distance from w(s) to w(t) is exactly
t − s + 1, one unit for each loop between them, and every bond through the
two contains those loops. A chain of two-place ties has no knot, and so no bond distance
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

### 4.8 How does one level bind another?

**Two knots and one shared bit.** Put the same rule on two triples of bits.
Each triple must contain both a 0 and a 1. The triples `(a, p, x)` and
`(x, q, b)` share only `x`. Set `a` and `p` to 0 and `q` and `b` to 1.
What value can the shared bit take? What changes if you forget `p`?

**What the four bits bind.** The first triple requires `x = 1`. The second
requires `x = 0`. So the four outer bits together rule out `0011`, and
reversing every bit rules out `1100` too. Yet every assignment to any three
of the four is possible. For example, if you forget `p`, first choose an
`x` that works with `q` and `b`, then choose `p` to make the first triple
work. The same argument works whichever bit you forget. That makes the four
a bond. Even knowing `a` leaves both values of `b` possible.

**Counting across levels.** Give each distinction an address made of zeros
and ones. Its length is its level. The address `010`, for example, names one
bit at level 3, and that bit can take either value. A placement rule uses
the addresses to specify which triples carry the not-all-equal rule. Here
a triple lies within one level or joins two consecutive levels. Pick two
levels and ask for the smallest bond with a member in each. Its other members
can come from anywhere in the pattern. The census also counts a tied pair
as size two.

**One more member per level (proved).** In a finite pattern of these knots
with no cycle of knots, count the fewest knots on a path joining the two
levels and add two. That is the exact least bond size. If a chain of knots
steps down one level at a time, the sizes for levels one, two, three and
four apart are **3, 4, 5, 6**. If the shortest path needs a detour, the
bond is larger. If no path joins the levels, no bond joins them. This
applies an earlier theorem for patterns with no cycle of knots.
([Proof across levels](research/RULER-LEVEL-20261114-001/ruler_level.md))

**Four targets in one pattern (computed).** Keep the last level fixed at
9. Starting from level 3, read each of levels 4, 5, 6 and 7 in turn.
The study drew pattern descriptions using fair coin flips, so the same
description could occur more than once. Among the 1,412 draws whose
patterns allowed a state, the most common reading was **3, 4, 5, 6**,
at about 43–52%. In 37% at least one target was disconnected from level 3.
In about 5–11% the least size stayed the same across all four targets. The
ranges allow for the draws still undecided.
([Reach census](research/LEVEL-REACH-20261114-001/level_reach.md))

Of the 457 distinct descriptions that gave **3, 4, 5, 6**, the theorem
explains 299 at the levels tested. For 117 of the 457, the placement rule
guarantees that count continues for every finite number of levels. The
remaining 158 descriptions gave those same four sizes despite having
cycles. The tests so far leave open which patterns with cycles do this.
([Theorem and counts](research/RULER-LEVEL-20261114-001/ruler_level.md),
[Tests on patterns with cycles](research/CYCLE-RULER-20261115-001/cycle_ruler.md))

Changing the last level can change the answer even for the same two
levels. In one pattern a bond of three joined levels 3 and 4 when 4 was
the last level. After level 5 was added, no bond of four or fewer joined
levels 3 and 4.
([Referee's counterexample](research/LEVEL-REACH-20261114-001/referee-R1/report.md))

**A tied partner at every level?** The census can use a different upper bit
for each target, and a size that stays the same can be three. A tie makes
a sharper prediction. The two bits agree in every allowed state, or they
differ in every allowed state. If a chain of ties from the same upper bit
continues one level at a time and the pattern still allows a state at every
finite stage, that upper bit fixes a partner's value however many levels
lie between them. Which of the census patterns with constant size keep
such a tie as more levels are added? The next subsection answers part of it.

**Blocks and descents (proved for 54 of 100).** A later study took the
census's constant cases to every depth
([DIRECT-REACH-20261115-001](research/DIRECT-REACH-20261115-001/direct_reach.md),
refereed and confirmed with fixes). A placement rule's maps send each address
to others at its level, and the addresses one address is sent to form its
orbit. Every knot placed at an orbit lies in its **block**: the orbit together
with its children one level down. Blocks meet only a block and the one above
it, so the pattern can be solved block by block, and when orbits stay small
there are finitely many kinds of block, which a finite computation decides at
every depth. When orbits grow, a **descent** can still carry the top down: a
few addresses followed down one letter at a time, the letters eventually
repeating. A **finite-reader state** gives every address its value by a finite
machine that reads the address letter by letter, and so gives the pattern a
state at every depth. With these two arguments, 54 of the 100 descriptions
whose least size stayed constant over four levels are proved to keep it at
every depth and every number of levels apart: 15 at size two, a tie, and 39 at
size at most three. Read to depth 9, one of the 100 leaves its constant at the
fifth level, so constant over four levels is not constant.

## Chapter 5. Depth

### 5.0 Introduction

**The lessons.** What each lesson of this chapter is about:

- [5.1 Proving that nothing is allowed](#51-proving-that-nothing-is-allowed):
  a refutation proves that a system allows no state. Its degree says how much
  one step has to hold at once.
- [5.2 How deep a hole is](#52-how-deep-a-hole-is): a pattern of parity knots
  with an odd total charge allows nothing, yet every small window of it looks
  consistent. Seeing the hole takes the width of the pattern's best order,
  unless the reasoning works mod 2.
- [5.3 Forcing in rounds and phases](#53-forcing-in-rounds-and-phases):
  forcing counted two ways, in rounds and in phases. It has to wait only
  where an atom is used as a knot, with both its loops still open.

**The intuition.** A hidden bit has a depth: how much an observer must hold
at once to carry it to where it shows. A pattern of parity knots can allow
nothing while every small window of it looks consistent, and then a proof has
to hold as much as the pattern is wide, unless it reasons mod 2. Forcing
shows the same thing from the other side: every two-place remainder can be
followed at once, and the order that cannot be avoided sits where a knot is
used as a knot.

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

### 5.3 Forcing in rounds and phases

**The question.** Lesson 4.2 showed that a system of requirements has one
least world, the forced world, which propagation finds in linear time. The
owner asked whether P versus NP is a question about what can be worked on in
parallel. It is not: that question is the literature's P versus NC. But it
raises one of its own. Must forcing in a pattern of atoms go one step after
another, or can most of it be done at once? This lesson gives the two ways the
record counts the stages, says where the knot picture puts the order that
cannot be avoided, and reports what was measured
([SEQUENTIAL-WALL-20261116-001](research/SEQUENTIAL-WALL-20261116-001/sequential_wall.md),
refereed and confirmed with fixes).

**Atom patterns with held distinctions.** Take a pattern of atoms A ∧ B → c,
"A and B together demand c" (lesson 1.5), and let the outside hold some
distinctions at 1. A distinction is forced when it is 1 in every allowed
state, and the forced distinctions make the forced world of lesson 4.2. In the
literature these are Horn clauses with two premises and positive facts, and
the forced set is the least model.

**Rounds.** One **round** forces, all at once, everything demanded by an atom
whose two demanders are already forced. A chain of six atoms, each with one
held helper, takes six rounds. The count of rounds is the height of the
shallowest derivation, and the literature calls the rounds synchronous unit
propagation.

**Phases.** Once one demander of an atom is forced, what is left of the atom is
a two-place rule, from its other demander to what it demands, and a two-place
rule is no knot (lesson 3.2). Two-place rules can all be followed at once, by
reachability. One **phase** does exactly that: it reads every atom with a
forced demander as its two-place rule and forces everything reachable along
those rules. The six-atom chain takes one phase. A distinction's phase is the
first one that forces it, and it equals the least Strahler number of its
derivation trees (proved in the record; the classical statement is Esparza,
Kiefer and Luttenberger's of 2010, in which the phases are Newton iterates).

**Open uses.** An atom whose two demanders are first forced in the same phase
has to wait for the next phase: it is used as a knot, with both its loops still
open. This is an **open use**, and only open uses make the forcing law take
another phase. Two open uses of equal standing, nested, make the next
standing, which is how a Strahler number grows. So the knot picture names
where the order comes from: a knot used as a knot, with both its loops still
open. As theory this restates the classical Strahler and Newton statements,
and it adds no algorithm.

**Where the wall can bite (proved).** Forcing in atom patterns is P-complete,
as monotone circuit value is (classical: Goldschlager 1977). How the atoms
overlap decides when that matters:

- a distinction is **reused** when it demands in two or more atoms, and
  **demanded several ways** when two or more atoms demand it;
- without reuse a pattern needs at most log₂ of its held count phases, and
  more phases than that need a **rejoining**, an atom with one distinction
  below both of its demanders in a derivation;
- the wall needs reuse unless P = NC, and several-way demand unless P = NL.

Being a knot does not decide it. Of the 34 three-place knots, 2 make laws in
AC⁰, 2 make parity laws, 14 make sequential (P-complete) laws and 16 make
NP-complete ones (the known classification, applied).

**What was measured (computed, refereed).**

- On random atom patterns at the jump, where the forced set leaps from about a
  fifth to more than nine tenths of the distinctions, rounds grow like n^0.30
  to n^0.36 (312 rounds at n = 2^20), while phases grow by about 0.57 per
  doubling of n (12 phases at 2^20). The slow cascade is almost all two-place
  work.
- On random monotone circuits with no layers, at most 4 phases were needed, up
  to 65,536 gates.
- On layered random circuits, where every gate reads only the layer below,
  the phase count follows a front at about √d for d layers, and the mean
  standing is about (2/3)√d
  ([LAYER-RANK-20261117-001](research/LAYER-RANK-20261117-001/layer_rank.md),
  narrowed by its referee). Order built into the meeting pattern keeps the
  phase count growing.

**Carrying distinctions (proved, refereed).** The owner pictured working on
several strands at once. Made exact
([CARRY-STRANDS-20261116-001](research/CARRY-STRANDS-20261116-001/carry_strands.md)),
a law for forcing may carry up to w open distinctions in a phase, each a
**carried distinction**, and take an open use while carrying both demanders.
A step either spends what it uses or keeps it to use again (**keep and
spend**). Spending only, the phases fall to exactly ⌈σ/w⌉ for Strahler number
σ, the literature's register allocation, and the rounds never fall below σ.
Keeping, the law reaches in one phase what w black pebbles with sliding reach,
the literature's pebble game, and that pays exactly where strands rejoin: a
ladder of any length takes one phase with two carried distinctions. The
program's random families have little rejoining: in the median sample at the
jump, keeping saves no phase for any distinction forced before the narrowest
phase (9 of 105 samples save some, at most 4.1% of those distinctions). As
theory the strand picture adds nothing to the register and pebbling
statements; what is new is measured.

**On a weave (proved, with a withdrawn reading).** Each phase moves the forced
set at most one step apart (lesson 4.7), because a two-place rule exists only
inside a knot that already has a forced member. So the phases are at least the
steps apart from what is held (proved; the classical locality bound of Linial
1992). On a six-regular weave, a law that grows a region from one place needs
one phase per step of the region's growth: 256 phases on a weave of side 384
([SPACE-ORDER-20261117-001](research/SPACE-ORDER-20261117-001/space_order.md)).
But the phases follow the weave's local overlap structure, every co-knotted
pair in two knots, and not the steps apart: rewiring 0.2% of the knots cuts the
largest steps apart from 256 to 52 and leaves 252 phases. The study's first
reading, "space forces order, and only through steps apart", was withdrawn by
its referee; steps apart is only a lower bound.

**Reading.** The order that forcing cannot avoid sits where a knot is used as a
knot, with both its loops still open; every two-place remainder can be worked
at once. That restates classical results in the program's words. What the
record adds is measured: how far rounds and phases separate on random
patterns, and how little rejoining the program's random families contain.

## Chapter 6. Counting

### 6.0 Introduction

**The lessons.** What each lesson of this chapter is about:

- [6.1 Counting worlds](#61-counting-worlds): the words for counting. Counting
  worlds can be hard where deciding is easy, and the graphs the literature
  calls planar are the classical exception.
- [6.2 The worlds of not-all-equal knots](#62-the-worlds-of-not-all-equal-knots):
  patterns of not-all-equal knots with every distinction in three knots. In
  the class the note studies, counting their worlds stays polynomial under
  twists that do not branch and turns #P-hard once they do.
- [6.3 Counting on classical 3-manifolds](#63-counting-on-classical-3-manifolds):
  a result about the literature's objects, not the program's. Counting the
  labellings of a classical knot's closed paths by a solvable group is hard,
  already for S₄.

**The intuition.** Deciding asks whether a knot pattern allows any world;
counting asks how many worlds it allows. Counting can turn hard where
deciding stays easy, and two notes find where it turns. In the second,
everything pairwise stays countable and hardness enters exactly where three
things are joined at once. That echoes the knot test, but it is a statement
about counting, not about logical knots.

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

### 7.0 Introduction

**The lessons.** What each lesson of this chapter is about:

- [7.1 What is classical and what is ours](#71-what-is-classical-and-what-is-ours):
  which results are classical, which readings are the program's, and which
  results are new as far as we found.
- [7.2 Open questions](#72-open-questions): four questions. Which law gives a
  space, whether loops are processes, whether a limit rule is needed, and
  whether competition counts.
- [7.3 Every meeting pattern, none chosen](#73-every-meeting-pattern-none-chosen):
  the owner's picture of what the program's bases are part of. Nothing
  chooses a meeting pattern, so one written down is one sample; how a growing
  pattern ends, what harmonies do, and the tests on each part.

**The intuition.** Most of the mathematics so far is classical. What is the
program's is the reading, and a few results. The questions left open ask
which law, not written on a space in advance, makes a space. The owner's
picture changes how they are asked: nothing chooses a meeting pattern, so
each pattern the record writes down is one sample, and a claim about what is
typical has to name its weighting.

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
  - distance is the only form of information, the owner's founding premise,
    under challenge as A97 (lesson 2.4);
  - distinctions are the material and atoms are the bonds;
  - a hidden bit has a depth.
- **Ours, as results.** The classifications and constants marked as proved
  here or in Lean are elementary. Several are classical facts in new language,
  and we give sources where we know them. The three notes contain results that
  are new as far as our searches found, and each note states its own novelty
  and folklore risk. See [FINDINGS.md](FINDINGS.md).
- **Further distinctions.** Requirements alone run in linear time, and
  requirements with choice are NP-complete. The co-reality of coherent
  alternatives is an interpretation.

### 7.2 Open questions

1. **Space from a law.** Logic allows every free complex (lesson 3.4). Which
   uniform, local law, not written on a space in advance, gives a meeting
   pattern that looks like a space of low dimension? On the owner's founding
   premise (lesson 2.4), this asks when the distances a law's knots carry,
   all the information the law has, add up to a space.
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
   time are the data, and does the static test survive that change? Lesson
   9.1 gives what the record has found.
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
tests now running on each part. The readings are interpretations open to
challenge; named results identify what is proved.

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
bindings like "time", "space", and "physics")."

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
analogy.

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

[Lesson 4.8, How does one level bind another?](#48-how-does-one-level-bind-another)
asks how many distinctions have to be read together before the upper and
lower levels show a shared restriction.

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
| Two folds beyond one box | computed under three weightings of 738 knot kinds: two certified unlengthened shifts in 88 to 98% of identified travelling bases with a new kind; travelling found less often where larger kinds are favoured | [WEIGHTS-20261112-001](research/WEIGHTS-20261112-001/two_shifts.md), closed and refereed (confirmed with fixes) |
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

## Chapter 8. How a law grows

### 8.0 What the program is building

**The lessons.** What each lesson of this chapter is about. This lesson is
the chapter's introduction: after the index and the intuition it gives the
owner's picture of growth, in his words.

- [8.1 Growing in rounds](#81-growing-in-rounds): a start is a few knots that
  share distinctions. One rule adds a knot wherever open distinctions can
  join, everywhere at once, round by round. Where the lesson's theorem holds,
  the rounds count size, not time.
- [8.2 Four kinds of growth](#82-four-kinds-of-growth): what grows stalls or
  closes, grows in a fixed dimension, feeds itself as an eddy at a fixed rate,
  or explodes where cycles overlap.
- [8.3 Reading a blow-up by sampling](#83-reading-a-blow-up-by-sampling): a
  blow-up is expected, and an unlimited structure is read by sampling it.
  What a sample shows depends on the weighting.
- [8.4 What distance carries of what grows](#84-what-distance-carries-of-what-grows):
  two arrangements can agree in every pair's bond distance and differ one
  round later. Three-way distances tell apart every case found.
- [8.5 Locality before space](#85-locality-before-space): here logic comes
  before space. A whole can hold what no pair holds, but ordinary locality
  and a largest speed have not come out of it.
- [8.6 Structure and state](#86-structure-and-state): the structure grows,
  and its distinctions have a state. Patterns of state travel and loops store
  one, under rules of motion added by hand; the growth law never reads the
  state.
- [8.7 Generators and folds of emergence](#87-generators-and-folds-of-emergence):
  ordinary growth has generators of its own kind, though none makes one fixed
  pattern again and again. Under rules added by hand a ring returns and gives
  parts off, and small parts copy themselves.

**The intuition.** Take a few knots that share distinctions and one fixed
rule, and let it build. Nobody places a knot: which knots share distinctions
decides where the next one goes. Some growth ends, some goes on in a fixed
dimension, and some blows up: it multiplies at a fixed rate such as the
golden ratio, or explodes where cycles overlap. A blow-up is expected, and it
is read by sampling. The chapter then asks what such a structure carries: how
much its distances say of the next round, whether locality and motion come
out of it, and whether it makes things that last, give parts off or copy
themselves.

The lessons state in plain words the picture that the growth studies of 17 to
24 November 2026 support. They build on lessons 2.4 (distance), 4.6
(dimension, read from how fast balls grow) and 7.3 (samples and weightings).
Each claim says whether it is proved, computed or open, and a result is given
as settled only once its referee has confirmed it.

**What the program is building.** On 23 November 2026 the owner was asked
whether the program looks for purely Boolean pieces that, combined, could
explain how atoms interact or why gravity exists. The answer is a fair
introduction to the program and to this chapter: "The combined part is the
challenging part because you need to know how the emergent thing can be
effectively joined with other things (think joining the X axis and Y axis on
a cartesian plane). These are like rules. But you also need to take 'logic'
to infinities, so there's a statistical/irrational part of it." The owner then
showed pictures of growth like the ones the web edition of this guide shows
in this lesson. The paragraphs below take the owner's points in turn. They are
the owner's picture, an interpretation, except where a result is cited. They
are an overview: the words they take from lessons 8.1 and 8.2 each point to
their lesson, and the glossary has them all.

**A structure relative to itself.** A start is a few knots that share
distinctions (lesson 8.1). One fixed rule, applied everywhere at once in
rounds, adds a knot wherever open distinctions can join, and nothing else
decides where knots go. Of the growing eddy in one picture the owner said:
"It's a spatial structure, but not yet like a circle or ring in 'space'. Like
we're spatial creatures so we think of these things in 'space', but it's not
really, it's just a structure that's relative to itself." What a growth holds
is which knots share which distinctions. The levels and bearings of the
pictures are drawing choices, and the distances inside a growth are bond
distances counted from its own knots (lesson 2.4), not lengths in a space
brought from outside. Building space out of such counts is the program's goal,
not its starting point.

**Some growth ends, some never does.** "Some growth is infinite, and some is
deterministic, like this cube." One knot with three open distinctions closes
after three rounds into eight knots, each sharing its three distinctions with
three others; the pictures draw them at the corners of a cube (the
literature's 3-cube) (proved, refereed,
[FRESH-COUNT-20261118-001](research/FRESH-COUNT-20261118-001/fresh_count.md)).
Two three-place knots that share a distinction never stop: the knots made by
round t number about t², a count of dimension two in the sense of lesson 8.2
(proved, refereed,
[FIRST-KNOT-20261118-001](research/FIRST-KNOT-20261118-001/first_knot.md)).
Every growth here is fixed by its start and the rule, the endless ones as much
as the one that closes. Chance enters through the start alone: nothing chooses
a meeting pattern, so a start is one sample (lesson 7.3).

**Joining is the hard part.** The owner's two axes are a question about
joining. One axis can grow from rules with nothing drawn: a rule that grows
only at knots holding two loose ends makes an endless chain, the literature's
number line (lesson 4.6, proved). Two endless chains in one connected part of
a growth give dimension two (lesson 8.2, proved, refereed). But a join can also
make what neither part has: two rings joined together grow at a rate of a new
kind, not at the product of their own (lesson 8.2). And no tested law yet
chooses its own dimension; every board of dimension two measured so far was
given its neighbours in advance (lesson 4.6, reading).

**Taking logic to infinity.** An endless growth is read the way any unlimited
structure is: by its rates, and by samples. The rates are irrational numbers
fixed by small equations: the golden ratio, 1.618…, for the eddy below;
1.0970, the root above one of x⁸ = x + 1, for a ring of seven with a hung
knot; 2.3830 for an eleven-knot start built around two dead knots (lesson
8.2). That such counts blow up is expected rather than a fault, and the
unlimited structure is read by sampling it (assumption A110, lesson 8.3). A
claim about what growth typically does names its weighting, the chances its
random process gives each start (lesson 7.3). That is the statistical part.

**The golden-ratio eddy.** Five knots in a ring, each keeping one leftover
distinction, an open distinction beyond what its joins use (lesson 8.1), make
5, 10, 15, 25, 40, 65, … knots in successive rounds: each round as many as
the two before it together, five times the Fibonacci numbers. So the count
grows by the golden ratio a round, and no ring of live knots within five
places grows faster (proved, refereed,
[RING-CORES-20261119-001](research/RING-CORES-20261119-001/ring_cores.md)).
The owner wondered where such a structure might serve: "if you 'met' this
logical structure with something like a plant's DNA sequence and physical
biology, it could use this for efficiency in growth." The golden ratio does
turn up in the literature on how plants set their leaves (phyllotaxis). The
link is a speculation outside the program: nothing here tests it, and the
guide makes no claim about living things.

**Starts without symmetry.** "And some structures are asymmetrical, like knots
on a branch." A start's symmetries, the renamings of its knots that leave it
unchanged, carry through every round, because the rule reads only which knots
share which distinctions. The pictures of a lone knot, two touching knots and
the eddy are symmetric for that reason. A ring of seven knots with an eighth
hung from one of them is kept only by the renaming that reverses the ring, and
adding one leftover distinction two knots along gives a start that no renaming
keeps; both are drawn lopsided. Yet on a ring the rate depends only on how many
hung knots and leftover distinctions it carries, not on where they sit (proved,
refereed, RING-CORES). Moving that leftover distinction one knot further
changes the first rounds and not the rate, 1.1903 a round (computed from the
proved formula).

**Quantum, and bases.** "And I think some growth is quantum, but I'm not quite
there yet on that one." Lesson 8.5 sets out how far the likeness to quantum
mechanics goes: it is one of structure, not of physics, and the question is
open. The owner's bet for the whole program is the last step: "My bet is that
there's some way to combine several different starting structures, meet them
using some sort of meeting pattern to create base-realities (our reality, a
number line, Cartesian plane)." In the guide's words the aim is a base built
from knots alone, in which space, distance and dimension are earned from
counts rather than assumed. No such base has been built yet.

### 8.1 Growing in rounds

**The picture so far.** Everything is built from distinctions, this versus
that (lesson 1.1). A knot binds open distinctions so that the whole is
constrained while no part is (lesson 2.1). Knots meet only by sharing
distinctions, any knot with any number of others, and which knots share which
distinctions is the meeting pattern. On the owner's founding premise,
"Distance is the only form of information" (lesson 2.4, assumption A97), what
a base holds is how its distinctions stand from one another. And nothing
chooses a meeting pattern: "It's just random" (lesson 7.3). So a pattern the
record writes down is one sample, and every random process that produces
patterns has a weighting, the chances it gives them. A claim that something
is typical has to name its weighting.

**A start.** Growth begins from a **start**: a few knots, some of which share
distinctions with one another, and nothing else. Five knots, each sharing
one distinction with the next and the fifth with the first (a ring), are a
start. A study grows many
starts, some produced at random and some built by hand, and may number them
in the order it found them; such a number says nothing about the start itself.

**Open distinctions.** A distinction that only one knot holds, shared with no
other knot, is open: nothing outside that knot ties it down.

**How a knot is added.** One fixed rule, the same everywhere, adds knots. Take
a set of knots, each holding an open distinction, such that every two of them
share distinctions with some common knot, but no single knot shares with all
of them. The rule makes one new knot for that set. The new knot takes one open
distinction from each knot of the set, so those are no longer open, and it
brings as few fresh open distinctions as it can: enough for the next round's
joins, and enough to make it a knot of at least three places. An open distinction that no
such set wants gets a new knot of its own. The growth studies call every knot
of the growing structure a **junction**, the first knots included: a junction
is simply a knot.

**Rounds.** The rule is applied everywhere at once, and then again. Each pass
is a **round**. The numbers the growth studies report are counts: how many new
knots each round adds.

**Nobody places the knots.** No one decides where a new knot goes. Which knots
share distinctions alone decides: a new knot appears exactly for knots that
already share with a common knot. Three
things are ours and could be otherwise: the rule itself (assumption A104,
under challenge), applying it everywhere at once in rounds, and the start,
which is one sample.

**When it stops.** Growth closes when no open distinction is left. It stalls
when a round would ask some knot for more open distinctions than it has.
Otherwise it goes on without end.

**Why the counts can explode.** When every two knots of a large group share
with some common knot, the group offers far more sets to join than it has
knots, and every such set gets its own new knot.
Nothing rations the joins: in the owner's words, "a simulation, where the
simulator has no limits" (lesson 8.3). So the count of new knots can outgrow
every fixed power of the round number, which lesson 8.3 calls a blow-up. Lesson 8.2 says which
starts do this.

**In the records' words.** A distinction of a junction is **loose** while no
other junction holds it, so it is open. A junction is **live** while it holds
a loose distinction. In each round the law makes new junctions, all at once
(assumption A104):

- **Joins.** Live junctions that can be joined in pairs, each pair meeting a
  common junction, and that have no junction common to all of them, are
  joined by one new junction, which takes one loose distinction from each.
  A join that takes three junctions is a **group of three**.
- **Offshoots.** A loose distinction that no join wants gets a junction of
  its own.
- **Fresh distinctions.** Each new junction adds as few fresh distinctions as
  it can: enough for the joins that will take from it in the next round, and
  enough to make it a knot of at least three places. This is the **cheapest
  growth** ([FRESH-COUNT-20261118-001](research/FRESH-COUNT-20261118-001/fresh_count.md)).

A growth **stalls** when a round cannot be made, because some junction has too
few loose distinctions, and it **closes** when no loose distinction is left.

**The map of joins.** Beside the growth, keep a second record, the **map of
joins**: who can join whom, written down before any round. It has one member
for each live knot. The live knots that share a distinction with one knot can
join through it, so they are grouped together. Each **leftover distinction**,
an open distinction that a knot keeps beyond what its joins use, is one more
member, attached to its knot alone. Following the groups from member to member
can lead back to where it started: a cycle. The **unrolled map** is the same
record with no way back: wherever a cycle would return, a fresh copy is used,
so it goes on without end (the literature's universal cover).

**What a round makes (proved, refereed).** Every junction the law makes is one
connected **cluster** of members of the unrolled map holding at least one knot,
and every such cluster is one junction. The first knots are the clusters of one member, round 1 makes the
clusters of two, and round t the clusters of t + 1, each counted once. Take
away one member so that the rest stays connected, and what is left is one of
the junction's parents. The map also holds the endless chains and relays of
lesson 8.2 ([RING-IDENT-20261119-001](research/RING-IDENT-20261119-001/ring_ident.md),
[CHAIN-IDENT-20261119-001](research/CHAIN-IDENT-20261119-001/chain_ident.md),
[RELAY-IDENT-20261119-001](research/RELAY-IDENT-20261119-001/relay_ident.md)
and [DOUBLE-IDENT-20261119-001](research/DOUBLE-IDENT-20261119-001/double_ident.md),
each confirmed by its referee).

- **How far it reaches.** The theorem holds in a stated class: no stall, at
  least two loose distinctions, no group of three in the first round, and no
  two live knots with two common neighbours. The touch census, every
  arrangement of up to five knots of three to five places, has 15,431 that do
  not stall at once, and the theorem follows 12,473 of them (81%) round by
  round. The other 2,958 lie outside its class, and that is where the fourth
  kind of growth of lesson 8.2 is found.
- **Known, and what is ours.** Counting connected clusters on such a map is
  classical: the literature's lattice animals on tree-like covers (Fisher and
  Essam 1961; Harary and Uhlenbeck 1953). What is ours is that the cheapest
  growth is exactly this count on its own map, junction by junction.

**Rounds are not a clock.** The owner put it as "Time doesn't have ticks". The
rounds turn out to count size: wherever the theorem holds, a junction's round
is its cluster's size less one (proved, refereed,
[ROUND-FREE-20261119-001](research/ROUND-FREE-20261119-001/round_free.md)). So
a round is bookkeeping, not a tick, and a growth's rate is the ratio between
the numbers of junctions of size k + 1 and of size k, with no round needed.
Taking the rounds away shows what they were doing (computed, refereed):

- **One join at a time.** Laws that make one join at a time, reading only
  what is already built, built different things in different orders in 12 of
  14 cases, and none of 280 orders matched the rounds even through round 3.
  The order can
  even decide whether a growth goes on: two three-place knots sharing a
  distinction grow forever in rounds and stopped in 4 of 20 random orders,
  while a lone four-place knot, which closes in rounds, kept growing in 19 of
  20.
- **Why the rounds were needed.** The cheapest count has to know, when a
  junction is made, how many joins will later take from it, and its partners
  may not exist yet. The rounds supply that by making every partner at once.
- **A law with no tick.** Make a junction for a cluster as soon as all its
  parents exist. Every order then reaches the same completed structure, and
  the only before and after left is that a junction comes after its parents.
  But this law reads the whole map of joins in advance, and the map says which
  junctions will join which. It trades the tick for knowledge of the map, and
  it equals the rounds only inside the theorem's class.
- **A law that reads only what is built (proved in its scope, referee
  pending).** A later study found one for ordinary growth: finish the births
  of the earliest unfinished round first, a knot's round found as its fewest
  holder steps to the start knots, working out from what is already built
  what that round would make. Every order of its own moves then builds what
  the rounds build, with no map and no stored round, on starts
  whose first knots can be recognised
  ([SERIAL-REPAIRS-20261120-001](research/SERIAL-REPAIRS-20261120-001/decision.md)).
  It reads the whole of what is built, and where a knot has to wait it stops
  early.
- **A round for each part (computed under added rules, referee pending).**
  Under the rules of lesson 8.7 the round need not be one for the whole: the
  separate parts of what is still growing can take their rounds in any order,
  and the same structure is built. Making one birth at a time, with every knot
  reading again after each, jams.
- **One birth at a time, reading a few steps (computed, referee pending).** A
  later study made the births of one part one at a time. Each birth records
  its parents. A knot is weaned when its parents have finished giving, and its
  brood is every knot made alongside it. A knot that waits until its whole
  brood is weaned, and then works out from the brood as it was at birth what
  the round would have had it do, builds what the rounds build in every order
  searched: where knots wait, where none does, and under ordinary growth. On
  the cycles through dead knots that were tried, of 4, 6, 8 and 12 live knots,
  it is enough to read within four holder steps. Each further time a knot has
  to wait needs one holder step more, so no fixed number serves every case.
  Laws that read what is
  there now, and not the brood as it was made, fail within a few births. The
  round has not gone: the law replays it from the record of parents. What has
  gone is the need for anyone to keep it
  ([LOCAL-ROUND-20261123-001](research/LOCAL-ROUND-20261123-001/decision.md)).
- **What the record of parents is for (computed, referee pending).** Two
  follow-ups. Under the cap of three, as the ring that returns was recorded
  (lesson 8.7), the same guard holds. Where knots hold what they do not use
  it fails: a knot's children are then no longer all made in one round, so
  the knots made alongside one another are no longer one round
  ([GUARD-CAP-AND-HOLD-20261124-001](research/GUARD-CAP-AND-HOLD-20261124-001/decision.md)).
  And the record cannot always be recovered from what is built. In the
  unfinished structures of births made one at a time, a knot and its offshoot
  can look exactly alike; the smallest case has two knots. One finished
  structure of 16 knots does not show which knot came first. On structures
  built by complete rounds, two holder steps are enough where a short knot
  retires and leaves a barred place, and where it makes offshoots the holder
  steps needed are one fewer than the round, so no fixed number is enough
  ([PARENTS-FROM-HOLDERS-20261124-001](research/PARENTS-FROM-HOLDERS-20261124-001/decision.md)).
- **Three values are enough (computed, referee pending).** If every new knot
  writes one of three values, one step on from its parents' value, a knot can
  tell its parents from its children by comparing values with the knots it
  meets, looking one holder step. This gave every parent on every structure tried,
  half-built ones included, wherever the knots that join were made together.
  No two-valued version that was tried does. The value is the order of
  descent cut down to three values, and it is written by hand: the growth does
  not supply it
  ([LEAST-RECORD-20261124-001](research/LEAST-RECORD-20261124-001/decision.md)).
- **The growth lives where parts are joined.** Counted by size, each part of a
  joined start keeps exactly the growth it has alone, and 97% to 99.9% of the
  junctions of size 10 or more span the join.

**One structure, read outward (reading).** Does the structure change over
time, adding logic to itself? As computed, yes: each round adds knots. But
where the theorem above holds, each knot is a cluster of one fixed unrolled
map, and its round is the size of its cluster less one, so nothing has to
change over time. The rounds are then us reading one fixed structure, perhaps
unlimited, outward from its smallest pieces, a layer at a time. The start is
the piece we stand on, and a round is how far we have read. On this reading a
blow-up is the structure getting far richer a little further on, and asking
whether a growth ends asks whether the whole structure is finite.
The owner asked, on 19 November 2026, "The structure changes over time? Like
it adds more logic to itself?", and accepted this reading: "This makes sense,
yes" (assumption A110). It rests on the theorem's class; for the explosive
starts of lesson 8.2 it is open. Chapter 9 gathers what the record holds on
time, from these rounds to the order of births and the clocks of lesson 8.7.

### 8.2 Four kinds of growth

**Sorting what grows.** Count the junctions each round makes. The record sorts
every growth it has read into four kinds, and inside the theorem's class the
first three are now described exactly:

1. Stalls and closings: nothing new forms.
2. A fixed dimension: the count grows like a polynomial.
3. Eddies: steady exponential growth, a cycle of knots feeding itself at a
   fixed rate.
4. Explosive growth: cycles that overlap one another, so that no single rate
   or finite description fits yet.

Outside the class the record has found steady eddies of the same kinds as well
as the explosive kind, and many starts there are not yet read (the last part
of this lesson).

**Nothing new forms.** A growth stalls when a round cannot be made, and it
closes when no loose distinction is left. A start with a single loose
distinction closes at round 1 (proved, refereed, DOUBLE-IDENT). Where a
weighting crowds knots with shared distinctions, most starts stall: 50% to 88%
of them when places are paired at random, and 64% to 99.7% when knots are
attached one at a time (computed, refereed,
[WEIGHTINGS-20261119-001](research/WEIGHTINGS-20261119-001/weightings.md)).

**A fixed dimension.** Here the junctions made up to round t number about
t^D for a whole number D, the growth's dimension, as balls grow like r^D in
lesson 4.6. Two things give it:

- **Endless chains.** Every junction must have at least three places. Where a
  knot keeps a leftover distinction and the law has to top a junction up to
  three places there, each round adds one more junction, without end: an
  **endless chain**. One endless chain makes the same number of
  junctions each round, which is dimension one. Two in one connected part of
  the map make a number that rises steadily, which is dimension two.
- **Relays.** A part of the map with no endless chain would finish. If another
  part is still growing, it does not: it goes on as a **relay**, making k
  junctions in the k-th round after it would have finished, which counts as
  two endless chains.

When the map has no cycle, the dimension is the largest number of endless
chains in one connected part, a relay counting two (proved, refereed,
CHAIN-IDENT and RELAY-IDENT). A bare ring of knots, whose map is one cycle
carrying nothing, makes the same number of junctions every round: dimension
one.

- **At most two when knots are small (proved, refereed).** A knot is **dead**
  when it is not live: every one of its places is shared. If every knot has at
  most five places and none is dead, the knots that share distinctions with
  more than one other form a single chain or a single ring, with single knots
  hanging from it. Then no part of the map carries more than two endless
  chains, and a start whose map has no cycle grows in at most two dimensions,
  at every size
  ([CAP-CHAINS-20261119-001](research/CAP-CHAINS-20261119-001/cap_chains.md)).
- **Five is the threshold.** At six places any number of endless chains fits
  in one part, and a dead knot lifts the bound even at five, since it joins its
  neighbours without costing them a place.

**Eddies.** The word is the owner's, from 18 November 2026: "It's an
interesting idea, loops of logic, then like eddies in a river that are shared
across the universe essentially there are 'core-libs' kind of processing"
(assumption A109). An **eddy** is a cycle of knots that feeds its own growth,
so that each round multiplies the count by about the same rate. Going once
around the cycle multiplies the count by its **lap weight** W, which lists the
ways each lap offers to extend, and the rate is the number x at which that
list balances, W(1/x) = 1.

- **Within five places, with every knot live (proved, refereed).** The eddies
  are exactly the rings of knots that carry something extra: a **hung knot**,
  a single knot that shares distinctions with one ring knot, or a leftover
  distinction. W is a product of three kinds of factor, one for each knot on
  the walk around the ring, one for each leftover distinction and one for each
  hung knot, so the rate depends only on how many of each the ring carries, not
  on where they sit. For a ring of seven with one hung knot the balance is
  x^8 = x + 1, which gives 1.0970: about 10% more junctions each round. No
  such ring grows faster than the golden ratio, 1.618, which a ring whose every
  knot carries a leftover distinction reaches at five knots and at seven or
  more; rings of three, four and six are outside the class
  ([RING-CORES-20261119-001](research/RING-CORES-20261119-001/ring_cores.md)).
- **With dead knots, still within five places (proved, refereed).** The kind
  of growth of each connected part of the map is set by its number of
  independent cycles. None gives a closing or a fixed dimension. One gives a
  constant count or an eddy, with a count that a short recurrence produces
  exactly. Two or more give exponential growth at a rate that a small system of
  equations fixes, computable but given by no formula. The fastest found is an
  eleven-knot start built around two dead knots, at 2.3830 a round; that
  nothing in the class within five places grows faster is a conjecture
  ([DEAD-CAP-20261119-001](research/DEAD-CAP-20261119-001/dead_cap.md)).
- **What this says of the owner's picture.** On one ring, each thing the ring
  carries brings its own factor, wherever it sits, and the factors multiply:
  eddies there are few in kind and act the same wherever they occur. Two rings
  joined together grow at a rate of a new kind (about 2.61 for two rings of
  five), not at a product. A109 stays under challenge because of what lies
  outside: groups of three, two live knots with two common neighbours, and
  knots of six places or more. "Shared across the universe" stays the owner's
  interpretation, which no catalogue can settle.

**Explosive growth.** The theorem's class ends at two kinds of overlap (proved,
refereed, DEAD-CAP): two live knots with two common neighbours, and a first
group of three, which is exactly three knots joined in pairs through three
different knots, with no knot common to all three. There the cycles of the map
overlap one another, and the unrolled map no longer says what grows.

- **What was found there (computed, refereed).** Of the starts read beyond the
  class, 118 of 122 are steady eddies at rates of the same family. A different
  kind also exists, in which the counts leap, running 80, 32, 31, 465, 4,495,
  31,465 in one start, and the largest join jumps or falls back in the last
  rounds reached. No fixed rate has been found to fit it, and whether one does
  is open ([BREAK-EDDIES-20261119-001](research/BREAK-EDDIES-20261119-001/break_eddies.md)).
  A further 626 starts there were still rising fast when the computation ran
  out of memory, so how many of them are steady eddies is open too.
- **The label.** "Explosive" is only the record's name for the kind it cannot
  yet describe, not a fault in the growth. In the record it means a jump in the
  counts seen before a computation stops, not growth without bound.
- **What a sample shows (computed, refereed, EXPLOSIVE).** A first group of three
  acts like a filled cell. Read with each such cycle filled, the map predicts the
  growth wherever groups of three do not overlap. None of 2,191 sampled starts
  within five places jumped within 20 rounds; 16 of 1,000 within seven did,
  every one with overlapping groups of three. Only the smallest was followed to
  its end, and it has a regularity of its own: one join of 309 parents swallows
  its growth, the 9 junctions left join in every way once, and it ends
  ([EXPLOSIVE-20261119-001](research/EXPLOSIVE-20261119-001/explosive.md)). One
  more ends the same way, through a block of 781; the other 14 could not be
  followed far enough (MERGE-BURST, refereed), and followed one or two
  rounds further they were still unread at the WALL-READ stopping point.
  The original sampling rule included two jumping descriptions with an extra
  constraint inside a starting junction. Checking every original draw gives
  14 jumps among 690 qualifying seven-place starts and zero among 1,661
  qualifying within-five draws and census entries at the original stopping
  points. The retained starts include an example with exponentially growing
  births and others that end after a finite burst.
  [Source counts and growth proofs](research/HEAVY-GROWTH-20261119-001/decision.md)
- **One kind that never ends (proved, refereed).** Let the live knots
  come in partner pairs, each able to join every knot but its partner, with the
  open distinctions that needs. Every round keeps that form, and the count runs
  6, 8, 10, 24, 4,086, then 2^2043 − 24: each about two to the power of half
  the one before, which the guide calls **runaway growth**. It never stalls and
  never ends. It is the growth's form of the literature's clique-divergent
  octahedra (Neumann-Lara, 1978), since each round keeps the largest sets of
  knots that can all join one another and that no single knot meets. A
  reading by clusters of the unrolled map counts at most exponentially many
  junctions, so none can follow it: past the edge of the class, the unrolled
  map is not the reading. Its knots need eight places, one more than the
  sample allowed
  ([WALL-READ-20261119-001](research/WALL-READ-20261119-001/wall_read.md)).

### 8.3 Reading a blow-up by sampling

**Blow-up is expected.** A growth **blows up** when its count grows faster than
any polynomial: the eddies and the explosive kind. The owner, on 19 November
2026, of the explosive kind: "When we talk about 'explosive', isn't that kind
of expected? Whenever I envision the intuition, it always blows up. Imagine
it's a simulation, where the simulator has no limits. That is the kind of
system we're dealing with. My thought process was that we would need to do
what amounts to essentially a sampling somehow of the underlying structure. Of
course, this would result in outlier results sometimes I think, but it's the
way I always envisioned it." The register holds this as the owner's direction,
assumption A110: growth that blows up is the expected case, and the unlimited
structure is read by sampling it. The program does not look for harmonies, or
for any other restriction, to keep growth from blowing up.

**Typical depends on the weighting.** To know what an outlier is, a reader
must know what is typical, and typical always names a weighting (lesson 7.3).
The growth studies give a sharp case. On the touch census, 82% of the starts
that grow do so in two dimensions, and that looked like a law of the growth.
It was not: it belonged to how the starts were sampled (computed, refereed,
WEIGHTINGS; narrowed in [HISTORY.md](HISTORY.md), and assumption A106
overturned). With the same proved theorem doing the reading, only the
weighting was changed:

- **Places paired at random, or knots attached one at a time.** Both keep
  knots at three to five places. Most starts stall, and of those that grow
  inside the class, 80% to 100% grow in two dimensions. None grows in three or
  more.
- **Uniform random trees of knots.** The knots' sharing has no cycle, and
  every knot gets the places its joins need, so nothing stalls. Three or more
  dimensions becomes common as starts get larger: 5% of the starts that grow at
  seven knots, 12% at twelve, 24% at sixteen and 37% at twenty, up to six
  dimensions.
- **Trees with random extra shared distinctions.** The extra sharing makes
  cycles, and eddies become common: 11% of the starts that grow inside the
  class at six knots, and 41% at twenty. About half the samples (41% to 62%)
  fall outside the class altogether, mostly at a first group of three, where
  the explosive kind enters.

So lifting the five-place cap raises the dimension, and adding cycles brings
exponential growth. Across all seven weightings tried, none of the 25,133
growing starts in the class whose knots all have at most five places grows in
three dimensions or more (the referee's reading), though 127 of them grow
exponentially. The cap is not a law of growth, though: a start of ten knots of
at most five places, built by hand around a dead knot, grows in three
dimensions.

**What is sampled, and what is not yet.** These studies sample starts: each
sample is one small arrangement of first knots, grown by the law. The owner's
sentence asks for more, a sampling of the underlying structure inside one
unlimited growth. A first step reads part of one growth: any set of live knots,
read exactly, bounds the next round from below, because each largest set of
mutually joinable knots in the part extends to a join of the whole, less one
per block (proved, WALL-READ). On the sampled explosive starts the bound is
weak: the smallest unread one makes 28,065 junctions in round 8, and the bound
on round 9 is 16,019. Reading such a growth by sampling is still open. The register already
holds evidence that weighs on "it always blows up": under the crowded
weightings most starts stall and eddies are rare. A110 would be challenged by
a natural weighting under which blow-up never occurs, or by shares that never
settle as the samples grow, under every weighting tried.

**What lets a blow-up be read (reading).** An eddy can be read exactly because
it repeats: each lap around its cycle multiplies the count by the same lap
weight, so one list says everything about its rate. On the program's reading,
which the owner has not confirmed, that repeat is what the owner's harmonies
do here (lesson 7.3, assumption A70): they let a blow-up be read, and they are
not a way to stop one. Whether the explosive kind has a repeat of its own is
the open question of lesson 8.2: its smallest case ends after one join and one
burst, one member (the partnered start) repeats its form every round and runs
away without end, and most of it is not yet read.

### 8.4 What distance carries of what grows

**The question.** On the premise that distance is the only form of
information (lesson 2.4), the distances between distinctions should carry what
the law builds. The growth studies test that with bond distance, the size of
the smallest bond that holds two distinctions (lesson 4.6). In short: two
arrangements can look identical by every pair distance today and differ
tomorrow. All the studies below are refereed
([line summary](research/HUNT-SHORTEN-20261119-001/line_summary.md)).

- **Pair distances alone lose information (computed).** The law builds pairs
  of arrangements with the same bond distance between every two distinctions
  and different allowed states. It does so from starts whose knots share two
  distinctions
  ([GROWN-PAIR-20261119-001](research/GROWN-PAIR-20261119-001/grown_pair.md)).
  Grown from all 503,039 arrangements of up to seven junctions in which any two
  junctions share at most one distinction, it gave 87 such pairs: 86 carried
  from starts that already had the same distances, and one created by the law,
  which comes apart the next round
  ([GROW-SMALL-20261119-001](research/GROW-SMALL-20261119-001/grow_small.md)).
- **Three-way distances recover it on everything found (computed).** The
  **three-way distance** of three distinctions is the size of the smallest bond
  that holds all three. With it added, every such pair found comes apart
  ([THREE-WAY-20261119-001](research/THREE-WAY-20261119-001/three_way.md),
  [TRIPLE-GROWN-20261119-001](research/TRIPLE-GROWN-20261119-001/triple_grown.md)).
  Pair and three-way distances suffice on all 211,643 grown stages of up to 14
  junctions tested, but not at every size: Codex built a 239-junction stage
  they do not settle. Reading over sets as large as the largest knot always
  suffices ([THREE-RIGID-20261119-001](research/THREE-RIGID-20261119-001/three_rigid.md),
  Theorem M). Codex's later studies, that no fixed number suffices and how the
  number needed grows, are referee pending
  ([LATER-BOND-READING-20261119-001](research/LATER-BOND-READING-20261119-001/decision.md),
  [BOND-READING-SCALE-20261119-001](research/BOND-READING-SCALE-20261119-001/decision.md)).
- **A round reads only the live roster (proved).** One round of the law reads
  only the **live roster**: which junctions hold a loose distinction, how many,
  and which sets of them one junction meets. And a renaming that keeps every
  parity equation the states satisfy, together with the live roster, carries
  every later round
  ([EXTEND-ROUND-20261119-001](research/EXTEND-ROUND-20261119-001/extend_round.md),
  Lemma A and Claim B\*).
- **Distances and the live roster carry the next round on everything tested,
  but not always (computed; the exception proved).** A renaming of the
  distinctions that keeps every bond distance and the live roster carried the
  next round correctly in all 36,060 such renamings of the carried pairs and
  all 1,746,752 of census stages of up to 14 junctions
  ([HUNT-SHORTEN-20261119-001](research/HUNT-SHORTEN-20261119-001/hunt_shorten.md)).
  But Codex built a stage the law reaches where it fails
  ([GROWN-END-SWAP-20261119-001](research/GROWN-END-SWAP-20261119-001/decision.md)).
  From six junctions, some pairs of which share two distinctions, the law grows
  ten. There, exchanging distinctions 0 and 2 keeps all 210 bond distances and
  every live junction's distinctions. After the next round, 0 and 1 are at bond
  distance 2, while their image under the exchange, 2 and 1, stays at 3. So the
  table of bond distances loses which old pair becomes nearer one round ahead.
  A three-way distance already tells the two apart before the round. Codex
  also built one where every two junctions share at most one distinction
  ([GROWN-END-MEET-ONCE-20261119-001](research/GROWN-END-MEET-ONCE-20261119-001/decision.md)).
  From seven junctions the law grows twelve, where exchanging 0 and 1 keeps
  all 253 bond distances and the live roster. One round later 0 and 2 are at
  bond distance 2, while 1 and 2 stay at 3. So sharing at most one
  distinction does not repair it.
- **What grows depends on more than the allowed states (computed; A108
  confirmed).** Under parity the allowed states do not say which junction is
  the one implied by the others, and the eddies depend on it: the same states,
  read with another junction counted as implied, make the same number each
  round, stall or close instead
  ([DROPPED-JUNCTION-20261119-001](research/DROPPED-JUNCTION-20261119-001/dropped_junction.md)).
  Under not-all-equal a growth that reads only the states exists, and it
  differs from the cheapest growth only at redundant knots and at knots with
  more places than their constraint needs
  ([MANY-VALUED-20261119-001](research/MANY-VALUED-20261119-001/many_valued.md)).

**Known mathematics, and what this adds.** The allowed states of a parity
growth are the literature's cut space of its junction graph, and a bond is a
cocircuit. Two arrangements have the same states exactly when their graphs'
cycle matroids agree (Whitney's 2-isomorphism theorem). What the growth
studies add is which of these ambiguities the law actually produces and from
which starts, that three-way distances resolve every one found, and the exact
reading of a round.

**Reading.** On the premise, the clean statement would be that distance and
the live roster carry what grows. That fails whether the first junctions
share two distinctions or at most one. So the premise
turns on a choice that is the owner's to make. If only pair distances count as
distance, it fails on computed cases. If three-way distances count too, it
survives everything found so far. What no distance can show is which junction
holds which distinction, and no reading of the allowed states can show that
either. A97 stays under challenge.

### 8.5 Locality before space

**The owner's question.** On 19 November 2026 (Pacific time) the owner asked:
"This kind of contradicts Einstein's theory of locality/space if true, right?
Similar to quantum mechanics, the logic is not spatial yet." This lesson gives
the program's answer. It is an interpretation, recorded as assumption A112,
not a result.

**Where the remark is right.**

- **Space is not given.** Nothing in the program starts from a space. Which
  knots share distinctions is the only nearness there is to begin with, and
  bond distance is read from the allowed states (lessons 2.4 and 4.6). What is
  near is produced by the logic, not put in.
- **The whole holds what no pair holds.** One parity knot hides a full bit
  from every pair of its distinctions (lesson 2.3). In grown structures, pairs
  of arrangements exist with equal pair bond distances but different allowed
  states, and three-way distances separate every such case found (lesson 8.4,
  refereed). Codex's studies reporting that no fixed number of distinctions
  read together suffices at every size are referee pending.
- **The likeness to quantum mechanics.** Entangled states have this shape
  too: the whole holds facts that no part, and in some cases no pair of parts,
  holds. The literature's GHZ state (Greenberger, Horne and Zeilinger 1989), in
  Mermin's three-particle form (Mermin 1990), is built from parity rules: for
  each of four choices of measurement the product of three outcomes is fixed,
  while every pair of outcomes looks free. What rules out every local
  explanation is that no single definite assignment satisfies all four rules.
  A parity knot is one such rule, with definite states, so it shares the
  hiding and not the impossibility. The likeness is one of structure, not of
  physics.

**Why it is not a contradiction.** Einstein's locality is a rule about space
once there is one: no signal or cause travels faster than light. A theory in
which space is built from something deeper does not break that rule, provided
ordinary locality comes out of it at large scales. So the program need not be
against Einstein's locality; it would sit underneath it, if ordinary locality
comes out. Quantum mechanics already has correlations that ignore distance and
still send no signal faster than light (the literature's no-signalling
theorem). Einstein's stronger demand, that things far apart have separate
definite states (Einstein, Podolsky and Rosen 1935), is the one quantum
mechanics does break (Bell 1964); the program makes no claim about it. Other
programmes also start from relations that are not spatial and let spacetime
come out of them: the literature's causal sets (Bombelli, Lee, Meyer and
Sorkin 1987), which start from a causal order, and spacetime from
entanglement (Van Raamsdonk 2010), argued within the literature's gauge and
gravity duality. What the program does is read nearness from the allowed
states of a definite logic and nothing else.

**What has not been earned.**

- **This is not quantum mechanics.** A state of the program's knots is allowed
  or not, with no probabilities and no amplitudes.
- **Ordinary locality has not come out.** Nothing yet shows that, at large
  scales, the logic gives the locality Einstein's theory needs.
- **The first world experiment found lasting things, but no signal.** Codex attached
  five-knot self-feeding rings to a background growing in dimension two
  ([EDDY-WORLD-20261119-001](research/EDDY-WORLD-20261119-001/decision.md),
  referee pending). The rings kept their identity and stayed attached to the
  same knots. But the growth rule moved nothing in this
  study: travelling state patterns exist among the allowed states, and the
  rule never chooses them. With no signal there is no speed yet, and no largest
  speed.
- **The first real test is open.** If the rules themselves gave a largest
  speed at which a change can spread, that would be the first test of this
  logic against Einstein's locality. Whether they do is open.

**Reading.** On the program's reading the owner's remark is right about the
order of things: here logic comes before space, as some physics programmes put
entanglement or causal order before spacetime. Whether Einstein's locality
comes out at large scales is an open question, not a contradiction.

### 8.6 Structure and state

**Two layers.** Everything the growth studies build has two layers.

- **The structure.** Which knots exist and which distinctions they share.
  This is what grows round by round (lesson 8.1), and it is what has a
  dimension and the cycles that feed eddies (lesson 8.2).
- **The state.** Every distinction sits one way or the other. Each knot is a
  rule on its distinctions, so only some combinations are allowed, and a state
  is one allowed combination of all the distinctions at once (lesson 1.1).

**The owner's question.** On 19 November 2026 (Pacific time) the owner asked:
"So am I understanding correctly? That I was originally under the assumption
that there was some 'state' to the world, but in actuality, what we've found in
practice is that these 'junctions' or developing structure over time works
more effectively." The program's answer: there is a state, as the owner first
assumed. What changed is that the stage is not a given backdrop. The structure
the state lives on is built by the logic too.

**What the state can do (proved and computed, referee pending).** Codex
studied states on grown structures
([MOTION-AT-EDDY-20261119-001](research/MOTION-AT-EDDY-20261119-001/decision.md)
and [EDDY-WORLD-20261119-001](research/EDDY-WORLD-20261119-001/decision.md),
both referee pending):

- **A loop keeps itself.** A self-feeding ring of knots attached to a
  background can be recognised again, stays attached to the same knots and
  keeps its own rate.
- **A pattern can travel.** A pattern of ten distinctions that differ from a
  resting state shifts one knot for every four changes, each the smallest
  change the rules allow, and keeps its shape.
  On a ring of 31 knots it passes all 31 and returns to exactly the same state
  after 124 changes, and so on forever. No clock runs for the whole: each
  change is decided where the pattern is.
- **It passes loops and can stop at cuts.** It passes intact five-knot rings
  at the same pace, and the rings keep their rate. A ring whose cycle has been
  cut can halt it.
- **A loop can store a state, and two loops can hand it over.** In a proved
  class of starts, the state held on one five-knot ring moves to a second
  five-knot ring d steps away in exactly 2d + 10 changes, each the smallest
  possible and each flipping four distinctions. Loose distinctions change
  for a while on the way.
- **Signals and memory.** Patterns that travel and loops that store are the
  two of the ingredients of computing (reading).

**What is ours, and not earned.**

- **The rule that picks the next change was added by hand.** The growth law
  moves nothing. The motion comes from a local update rule and a fixed resting
  state that the study supplied.
- **No largest speed comes out across rules.** For a rule that treats both
  directions alike and reads s knots out, the average shift is at most
  (s − 1)/2 knots per change. So the speed depends on the rule, and nothing yet
  fixes one speed for every rule (lesson 8.5).
- **Order comes back where patterns meet.** Two patterns moving toward each
  other can end differently under different orders of change, even when every
  knot gets its fair turn. With no ticks (the owner's "Time doesn't have
  ticks", lesson 8.1), nothing fixes that order.
- **Steering reads more than distance.** To pass a ring, the rule reads which
  distinctions meet at a knot, which bond distance alone can hide (lesson 8.4).
- **The shrinking belongs to the attachment.** Bond balls near an attached
  ring shrink, and they shrink the same way for a control ring whose cycle is
  cut. So the shrinking comes from the attachment, not from the ring's
  activity.

**How strong "no ticks" is (proved and computed, referee pending).**
Codex's motion-law study
([MOTION-LAW-20261119-001](research/MOTION-LAW-20261119-001/what_is_forced.md),
referee pending) asked what the owner's "Time doesn't have ticks" can mean for
a rule of motion. With no clock, it says that the order of local changes
should not matter, and that can be meant at three strengths. Lesson 9.2 sets
them beside what else the record has on time.

- **Full strength: every two local changes can happen in either order.** Then
  nothing moves. A compact change on a quiet background stays where it began,
  so the largest speed it can keep up is exactly zero, though it can still
  oscillate in place.
- **Middle strength: two changes that are both ready can happen in either
  order, with the same result.** This lets things move. In one small, fully
  classified family, a chain of knots read one step out with a rule that keeps
  the number of neighbouring disagreements, exactly seven rules survive, and a
  lone disagreement moves at most one knot per change. But once rules may read
  farther, on suitably built rings a compact pattern moves any chosen number of
  knots per two changes, so there is no largest speed across rules (lesson
  8.5).
- **Weakest: every fair order of changes reaches the same end.** On the
  program's reading this is the strength that fits, and a switch shows it. A
  pattern arriving at two self-feeding five-knot rings at least four knots
  apart exchanges which ring holds a stored state, and every permitted order of
  changes ends in the same place, clears every temporary change and takes
  exactly 2d + 10 changes for rings d knots apart
  ([decision note](research/MOTION-LAW-20261119-001/decision.md)).
- **Not forced by the growth.** The growth law and renaming alone leave
  infinitely many rules of motion, even among quiet, reversible rules whose
  changes commute. So no rule of motion, and no largest speed like the speed of
  light, comes out of the growth yet.

**The open gap (reading).** The layers talk one way only. The state lives on
the structure, but the growth law never reads the state, and no change of
state changes the growth rates or which knots exist. On the
program's reading, state feeding back into growth is where behaviour like
gravity would have to come from: structure that changes where there is
activity.
Nobody has built that, and it is the first of the leads recorded with this
lesson (backlog B210 to B213, under goal G17). Since then it has been built
only by adding a rule by hand, and for ordinary growth a stored value is
proved, referee pending, to steer nothing (lesson 8.7).

### 8.7 Generators and folds of emergence

**The owner's questions.** On 20 November 2026 the owner wrote: "there are
underlying rules that can exist that don't destroy each other but can create
things. This is kind of like a generator in conway's game of life." On 23
November he asked again, and wider: "have we made generators yet? Like
structures that output other structures that either die, or live, or combine
with other patterns? This is like logic of cellular biology where you have
machines printing stuff, and cells reproducing to receive and send signals".
Of the golden-ratio eddy of lesson 8.0 he asked: "Is there a
way to actually use the golden ratio currently as a means of growth? Like is
there a 'connector' or 'gadget' of sorts we could use?" This lesson says what
the record holds on each question and what it lacks. Its last part records the
picture he asked to have written down, of DNA and intelligence as "folds of
emergence".

**The literature's picture.** Conway's Life (lesson 1.3) has the best-known
generator, the literature's glider gun (Gosper, 1970): 36 live cells that come
back to the same shape every 30 steps, having made one new glider each time.
What a gun makes can go on, end or combine. A glider travels on unchanged. A
glider that meets the literature's eater is destroyed, and the eater is left
as it was. Two gliders that meet can leave nothing, or a new pattern that
stays.
A pattern can also copy itself: under the neighbouring rule HighLife (found by
Thompson and described by Bell, 1994) the literature's replicator becomes two
copies of itself every 12 steps, and where two copies would land on one place
both vanish, so after 12k steps there are two to the power of the number of
ones in k, written in binary, copies. Machines that build copies of themselves
go back to von Neumann's self-reproducing automata (1966). All of this happens
on a board drawn in advance, with a clock that steps every cell at once. The
program gives itself no board (lesson 1.3), and its rounds turn out to be
bookkeeping, not a clock (lesson 8.1). So the question is how much of the
picture the growth of lesson 8.1 has without them.

**A generator in ordinary growth (proved; refereed in part).** Ordinary growth,
the cheapest growth of lesson 8.1 with nothing added, has generators of its
own kind
([GENERATORS-20261120-001](research/GENERATORS-20261120-001/decision.md); its
referee regrew the start below and the verdict stands, with the meeting read,
not recomputed, and the nested case not checked).

- **Packets and release.** A **packet** is a finite set of knots made in one
  round whose later members take every parent from the packet's own earlier
  members. It is **released** in the round from which that holds. Release is
  about parents; it does not mean that a distinction becomes loose. A packet
  **lasts** when it has members in every later round. A start is a
  **generator** when it releases infinitely many packets that last and share
  no member.
- **The smallest one known.** Seven knots holding 25 distinctions, one of the
  knots dead, release a packet in rounds 15, 23 and 31 and in every eighth
  round after (the record counts cluster sizes, one more than the round).
  Seven knots, and then 25 distinctions, are the fewest in the class where
  every knot can be reconstructed from the start (lesson 8.1's theorem);
  outside that class the fewest is open
  ([the generator's note](research/GENERATORS-20261120-001/source.md)). The web edition
  shows this start among the growths of lesson 8.0. Its first
  release lies far past what can be drawn there.
- **Packets can combine while both go on.** In a start of 21 knots two packets
  are released in round 15 and make a shared knot in round 16, while each still
  supplies all its own parents, and descendants of the shared knot can take a
  distinction from one of them at every later round. In a matched start that keeps
  the two apart the shared knot is never made, and a corresponding knot
  receives 15 fresh distinctions where it had received 18.
- **A packet can be a generator.** One packet released in that start keeps
  releasing packets of its own.
- **One ring is not enough.** A ring, however it is decorated, is no
  generator: each of its walks carries at most one packet that lasts, so an
  odd ring carries at most one and an even ring at most two. That includes the
  golden-ratio eddy, for all its births. In this class a generator needs two independent
  cycles of the map of joins in one connected part.

All of this holds under parity and under not-all-equal, with no values, no rule
of motion and no clock supplied.

**What counts as a thing is a reading.** The births, their parents and their
fresh distinctions come from the growth alone. Calling some of them a packet is
a reading of the whole structure, dead knots included, and the reading was
chosen (assumption A125, a scaffold). A reading that returns whole connected
parts of the live roster finds no release at all, because those parts never
come apart (below). A packet is also not independent in a stronger sense: grown
alone from its own holdings it changes its fresh counts at once. In the
referee's words, "'both survive' means two lineage-closed families keep
growing. It does not mean two independent objects."

**Where this falls short of a gun.**

- **Each release is larger than the last.** No fixed pattern is made twice.
- **No packet of fixed width forever (proved; the referee read this proof in
  outline).** From a finite start in the class above, only finitely many
  packets that last can be released with at most w knots apiece, for every w
  and under every reading. Each lasting packet has to keep its own endless
  sequence of knots, each a parent of the next, along which the start's knots
  recur in a fixed repeating order, or its own endless chain, and a finite
  start has finitely
  many of them at each width. The seven-knot
  generator keeps none narrower than four knots and at most two of width four
  ([COPIES-AND-MEETINGS-20261120-001](research/COPIES-AND-MEETINGS-20261120-001/bounded.md)).
  Beyond that class the proof covers packets of one knot and packets that stay
  at three knots or fewer; the rest is open.
- **Holdings grow.** On the seven-knot generator a knot made in round t holds
  at least (t + 9)/5 fresh distinctions, so no pattern with fixed holdings
  comes back at later and later rounds (same note).
- **Nothing is given off (proved).** A gun sheds what it makes. In ordinary
  growth the connected parts of the live roster neither come apart nor merge
  (the literature's components;
  [note](research/GENERATORS-20261120-001/components.md)). And no part ends
  while another goes on: every knot made after the start receives at least one
  fresh distinction, so it has a successor, and the only endings are the whole
  growth closing or stalling.

**Balance (computed under added rules, referee pending).** Told of that limit, the
owner wrote on 23 November 2026: "We need to break this limit. I'm imagining a
system of balance. Similar to life and death cycles." The limit counts packets
that last, so a thing that ends is not counted by it. And ordinary growth
already has one kind of balance: in the live roster every knot is live for
exactly one round, so on a bare ring of five, five knots leave the live roster
and five join it, in the same holdings, round after round. What it lacks is the
giving off and the ending. A pilot on the same day looked for them by changing
the law.

- **Two added rules give a ring that returns and gives off parts.** First, a
  new knot receives at most three fresh distinctions. Second, a knot that owes
  more loose distinctions than it holds makes none of its joins: it waits,
  keeping what it holds, where the ordinary law stalls the whole round, and
  the other parents of those joins make offshoots with the distinctions the
  joins would have taken. Start from a ring of five knots, each sharing a
  distinction with the next and holding three loose distinctions: the start of
  the golden-ratio eddy. Round 1 makes five joins and five offshoots, and each
  join is asked for by four joins of round 2 while holding three distinctions.
  So in round 2 no join is made: the five knots that round 1's joins made
  wait, and each offshoot makes two knots of its own. The live roster is then
  the start's again, exactly, with the waiting knots in the ring's place,
  together with five separate parts of two knots. This repeats every two
  rounds without end, so the live roster has 1, 1, 6, 6, 11, 11, 16, …
  separate parts. Each time the same finite thing comes apart from the ring,
  which ordinary growth cannot do. The same holds for every ring of an odd
  number of knots from five up, and for an even number from eight up as two
  halves that each return; a ring of three, four or six does not return.
- **Scarcity makes the difference.** Under the ordinary law the same start is
  the eddy: each join receives all four distinctions it is asked for, every
  join is made, and the count grows by the golden ratio. With at most three,
  the ring holds itself back and gives parts off. The number three is not
  special: with at most four, five, six or seven the ring also returns, one
  round later for each step. Its knots then hold that many each, and the parts
  that come apart have 5, 9, 14 and 20 knots.
- **Not yet a balance.** Under the two rules each part that came apart is the
  two-ended growth that ordinary growth gives two such knots: it gains one
  knot a round (computed for 40 rounds), so the live roster still grows.
- **A third rule gives one.** Let a fresh distinction that a knot receives only
  to make up three places, or as its least of one, and that no join of the
  next round asks for, never be used. Then each part that came apart makes one
  joint knot in the next round, which holds nothing it may spend, and the part
  makes nothing more. Counting the knots that can still make something, the
  whole pattern repeats every two rounds from round 1 on: over each two rounds
  as many of them stop as start.
- **Checked on real knots (computed, referee pending).** A frozen study
  repeated the pilot with a program written from its text alone, on knots with
  their distinctions
  ([RING-IN-BALANCE-20261123-001](research/RING-IN-BALANCE-20261123-001/decision.md)).
  It agrees with the pilot's two programs round by round, on rings of 5 to 15
  knots. Every knot made passes the knot test in the whole structure: under
  parity by an argument, since a rule with a place of its own is the only
  constraint on its places, checked on 62,280 knots; and under not-all-equal
  on 1,848 knots through round 6, with the same births.
- **What the return needs.** Three things, each tested by swapping it.
  Waiting: if the whole round stalls instead, the ring stalls, and if the
  short knot makes offshoots or gives up, the growth goes on with no ring
  coming back. Release: a knot that is not short spends on offshoots the
  distinctions its cancelled joins would have taken; if it holds them instead,
  the ring jams for good. Offshoots: without them nothing comes apart. The cap
  is the one thing it does not need in any exact form.
- **Small parts that copy themselves (computed, referee pending).** When a new
  knot receives only enough for three places, and a short knot's joins are
  cancelled, a part of two knots becomes two of the same every two rounds,
  with no knot waiting. The two join; their join receives one distinction
  where two will be asked of it; and each of their offshoots makes two
  offshoots of its own. How fast the copies multiply depends on what the short
  join then does. If it gives up, they double every two rounds. If it makes an
  offshoot, one more copy follows a round later and the count grows by the
  golden ratio a round; on the ring of five the counts are five times the
  Fibonacci numbers. If it waits, the counts from one such part are the Pell
  numbers, 1, 2, 5, 12, 29, …. Every knot made passes the knot test under
  both knot laws on the small starts tested, and under the simplest such
  ration a part copies itself in 85 to 97 of every hundred starts of up to
  five knots, each counted once
  ([COPYING-PARTS-20261123-001](research/COPYING-PARTS-20261123-001/decision.md)).
  The copies never meet again, so this is a population with a fixed rule of
  descent, like the literature's Fibonacci rabbits, and not a machine: nothing
  here combines or reads. Nobody predicted these parts; they turned up in the
  table of swapped rules.
- **What is ours here, and not earned.** Every rule here was added by hand
  (assumption A224, a scaffold), the release included. The pilot's search of
  56 combinations of ways to ration fresh distinctions and to treat a knot
  that cannot pay found the return in three, all with waiting. The frozen
  study narrows that: a part the size of the ring returns only with waiting,
  but the small parts above return under other laws, some without. The third
  rule was added to make the parts end, and no other rule that does so is
  known; under it no start of the pilot kept growing, an endless chain
  included. The knots that stop under it still hold a loose distinction that
  is never used, so in the glossary's sense they stay live. The limit above is
  a theorem about ordinary growth, and it stands.

**Anchors and time (the owner's questions; computed, referee pending).** On 23
November 2026 the owner asked two more things of the ring that returns. "What
if some emergent patterns need anchor points, or like a reference. … I think a
structure like this would just make it easier to join things, but I'm not
sure." And: "what if 'time' is a device or pattern just like the other ones?
… I feel like it's not really like a sequencer, but more like a priority
system, if that makes sense. How often updates happen given some property
(maybe mass impacts that). … Then places with nothing going on need less
simulation." The same frozen study took both up. His pictures are recorded as
assumptions A228 and A229, interpretations that no result settles. Chapter 9
takes up both, with what the record has found since; lesson 9.6 takes up his
later question, whether time is itself a fold of emergence.

- **Every join already has a reference.** Two knots can join only when some
  knot meets both (lesson 8.1). A dead knot is the pure case: it makes nothing
  and others join through it. In a start where every knot is live, each knot
  has to be both a partner in joins and the knot its neighbours join through,
  which is why a cycle of pairs that can join is a ring only for an odd number
  of knots. A dead knot lifts that.
- **A dead knot makes returning easier, modestly.** Of all 86,032 starts of up
  to six knots that meet in single distinctions, each counted once, 227 have a
  part that returns giving parts off under the added rules, and none under
  ordinary growth. The share is 0.06% of five-knot starts with no dead knot
  and 0.97% with one; at six knots 0.17%, 0.23% and 0.58% with none, one and
  two. With a dead knot four live knots are enough, where five are needed
  without. No start with three or more dead knots returns. The shares are
  under that one weighting.
- **What lasts.** At the rounds where the ring has n knots it is exactly the
  knots that waited, the only knots under these rules that can still make
  something in two successive rounds. Half a period later the same pattern has
  2n knots, all new. So the pattern passes through lasting knots; it is not
  made of them.
- **A knot can carry the round, sometimes.** The owner asked whether "a certain
  point of the Fibonacci sequence can be sampled to determine growth rate at a
  particular point". In the golden-ratio eddy a knot made in round r with p
  parents and f fresh distinctions has r = f + 2p − 3, − 5 or − 7 (from lesson
  8.1's theorem; checked on 44,333 knots). So one sampled knot gives its round
  to within three values, and with it the growth factor there. Where only some
  knots keep a leftover distinction more values of the round fit, and on a bare ring every
  knot holds the same and carries no round.
- **The round can belong to a part.** The complete round has every knot of
  every part read at one moment (lesson 8.1). Under the added rules that is
  more than is needed. If the separate parts take their rounds one at a time,
  in any order, the same structure is built (726 runs, with an argument), and
  a knot's count of its own part's rounds is its round.
- **How often is a matter of the order.** Counted in births, the ring returns
  more and more slowly under orders that serve every part alike, as the parts
  it has given off pile up and keep growing. It returns every 4n births when
  the largest part is always served first, the small parts then never being
  served at all. And it returns steadily under the third rule, where the parts
  end. The orders were supplied, and nothing in the growth counts births.
- **Inside a part the round is still supplied.** If one birth is made at a
  time and every knot reads again after each, an offshoot that may release
  three distinctions has released two when it reads again, finds itself short
  and stops, and the ring never frees itself. That happens in every order (all
  101,606,400 of them on a cycle of four live knots joined through dead ones).
  A later study found a law that lets the knots of one part read at different
  moments, given a record of each birth's parents (lesson 8.1).

**Using the golden ratio.** The golden ratio can be had on purpose, and there
is a gadget for it, but nothing that carries it from one part to another.

- **The gadget (proved for rings, refereed).** On a ring the lap weight is a
  product of factors (lesson 8.2): y for each knot on the walk, 1 + y for each
  leftover distinction, and 1 + y(1 + y)^b for each hung knot with b leftover
  distinctions. One leftover distinction on every knot turns each knot's factor
  into y(1 + y), and y(1 + y) = 1 is x² = x + 1, the golden ratio's equation. A
  ring of n such knots makes exactly n times the Fibonacci numbers, n, 2n, 3n,
  5n, 8n, …, from the start on, for five knots and for seven or more (rings
  of three, four and six are outside the proved class)
  ([RING-CORES-20261119-001](research/RING-CORES-20261119-001/ring_cores.md);
  recomputed on 23 November 2026 for n = 5, 7, 8, 9, 10 and 11 on two
  independent growth programs).
- **A dial.** On a ring of an odd number n of knots, five or more, with k
  knots keeping a leftover distinction, the rate solves x^(n+k) = (x + 1)^k
  (the proved lap weight, rewritten). It depends only on the share k/n, and
  runs from 1 with none to the golden ratio with all; where the leftover
  distinctions sit changes the first rounds only. Lesson 8.2's ring of seven
  with one hung knot sits on the dial at k = 1, since a hung knot with no
  leftover distinction brings the same factor 1 + y.
- **The same gadget on other starts (computed, not refereed).** Take a start
  in the class of lesson 8.1's theorem and give every knot one leftover
  distinction. By that theorem each knot of the
  new growth is a knot of the old one together with any choice of its leftover
  distinctions, so the new counts are read off the old ones, and a growth of
  rate x becomes a growth of rate x′ with x′² = x(x′ + 1). A bare ring, rate 1,
  becomes the golden ratio. A ring of five with a hung knot goes from 1.1347 to
  1.7743, and two bare rings of five joined by a shared distinction go from
  2.6075 to 3.3792. Two growth programs agree with the rule on every round
  they reached of the five starts tried.
- **What hangs on the eddy (computed, not refereed).** A three-place knot hung
  on the golden ring of five raises the rate to 1.7292. The knots that descend
  from the ring's knots and not from the hung knot keep their counts exactly,
  5, 10, 15, 25, 40, …; the knots that descend from the hung knot grow at the
  higher rate and are 70% of the births by round
  16. Alone, that three-place knot closes after three rounds (lesson 8.0).
  Hung on a bare ring of five its line grows by 1.1347 a round, the rate of
  x⁶ = x + 1. So a part that would finish alone is kept going by a
  ring, at a rate the ring sets.
- **No connector.** Joining does not hand the golden ratio on, and rates do
  not multiply. Two golden rings of five joined by one shared distinction grow
  at 3.3792, not at 1.618² = 2.618. The 2.6075 of two bare rings joined that
  way (lesson 8.2's "about 2.61") is not 2.618 either. Joining by spending the
  ring's own leftover distinctions lowers the rate, to 1.3854 in the case
  tried.
- **With state (a supplied rule).** Under a rule added by hand, in which a
  knot's state can add a fresh distinction, switching on a whole bare ring
  changes its growth factor from one to the golden ratio
  ([STATE-FEEDS-GROWTH-20261119-001](research/STATE-FEEDS-GROWTH-20261119-001/selection.md);
  a result about the added rule, read by its referee and not recomputed).
  Ordinary growth has no such switch (next part).

**Readers and signals so far.**

- **A value steers nothing in ordinary growth (proved, referee pending).** A
  stored value can change which values a later knot may hold. With the same
  holdings, groups and payments it cannot make a knot keep a distinction, pay
  a different child or make a different birth
  ([STORED-BIT-AND-NEXT-ACTION-20261122-001](research/STORED-BIT-AND-NEXT-ACTION-20261122-001/decision.md)).
  The state changes what grows only under rules added by hand (lesson 8.6).
- **Influence inside one growth is shared descent (proved, refereed).** While
  the growth stays funded, two packets first share a descendant after exactly
  as many parent steps as there were steps between them at release. In the
  seven-knot generator two packets released in round 158 first share one in
  round 307 (computed from the proved map). Its referee calls this a
  pace of shared descent, not a limit on all influence
  ([COPIES-AND-MEETINGS-20261120-001](research/COPIES-AND-MEETINGS-20261120-001/decision.md)).
- **A signal that is chosen exists only between two prepared starts.** Under
  parity, one extra loose distinction in one place of a start can decide
  between closing and growing forever in another (refereed,
  [ORDINARY-DYNAMICS-20261120-001](research/ORDINARY-DYNAMICS-20261120-001/decision.md)).
  Nothing inside one growth has been shown to choose it.
- **Every reader was supplied.** The sensors, rewards and rules of every
  reader, learner and agent in the record so far were written by hand. Making
  the one who reads out of the growth itself is open (goal G15).

**"Folds of emergence" (the owner's picture; an interpretation).** On 23
November 2026 the owner asked for this to be recorded: "I'd like to record DNA
as something like 'intelligence' as an emergent structure/pattern. So things
like DNA are kind of like patterns that observe a different pattern but also
have their own growing patterns. This is generalized, so maybe DNA has some
access to things like the golden ratios, and can output structures based on
that." And: "structures like DNA or intelligence should maybe be exceptional,
almost considered folds of emergence." It is recorded as assumption A223, an
interpretation that no result settles.

- **Read in the program's terms.** A "fold of emergence" would be a pattern
  with three properties: the rules make it and nobody places it; what it makes
  depends on another pattern; and it makes a pattern of its own. Emergence is
  then folded once more: something that emerged reads something that emerged.
- **What the record has of each.** Packets are made by the growth, and a
  packet can release packets of its own. Whether two packets are joined or
  kept apart changes what a knot receives, 18 fresh distinctions against 15.
  And a part hung on an eddy grows at a rate the eddy sets, which is the
  nearest thing in the record to the access to the golden ratio that the
  owner pictures.
- **What is missing.** The reading. In each of those cases the dependence is a
  comparison that we make between two starts. No pattern in one growth has
  been shown to take one course or another according to what a second pattern
  is. That is the first test of this picture, and it is open.
- **Parts that meet again (computed under added rules, referee pending).** A
  first step was run on 24 November 2026. Under every law above, and under the
  recorded rules in which a birth takes a distinction that is already shared,
  parts that have come apart and share nothing, even through a third part,
  never become one part again; for those rules there is a reason: a birth that
  takes only what its own parents hold can reach nothing its parents did not
  already meet. Under rules added by hand that reach a little further, a birth
  also taking a distinction from a knot its parent meets or from one or two
  steps back along its own descent, parts that came apart do become one part
  again, and the first then builds differently with the second barred than
  with it growing. In some cases a knot both descend from is among the common
  knots of their members, the owner's "axis point" (glossary, "Ancestral
  common knot"). What crosses is only whether the other part grows or is
  barred, not what it is; each case needs its own ration and a supplied
  convention for which distinction a birth takes; and no part has yet built
  anything from what another part is
  ([PARTS-MEET-AGAIN-20261124-001](research/PARTS-MEET-AGAIN-20261124-001/decision.md)).
  Lesson 10.3 gives the study, and lesson 10.2 the test it ran.
- **No claim about living things.** The guide says nothing about DNA, cells or
  minds. The owner's words name what a base would have to grow before such a
  question could be asked of it.

**What is open.** The ring that returns and the parts that copy themselves
each have a frozen study behind them, with referees pending. Whether the knots
of one part have to read together now has an answer, in lesson 8.1: not if
each birth records its parents, and that record cannot be read back from what
is built, though three values on each knot can stand in for it. Three things
are open. Whether the structure can hold such a count itself (B328, under goal
G5). A first "fold of emergence": under added rules
parts that came apart can now meet again, and one part's course then differs
with another barred, but not with what it is, and no part has built anything
from what the other is (B317, under G15; a made pattern that leaves two of what
it meets is the next step, B327, whose claim is now frozen; lesson 10.5). And
proofs
of what is so far argued or computed: the return for every odd ring, the sizes
of the parts under each cap, and that one leftover distinction on every knot
turns rate x into the x′ of x′² = x(x′ + 1) (B316, under G17).

## Chapter 9. Time

### 9.0 Introduction

**The lessons.** What each lesson of this chapter is about:

- [9.1 A history is one allowed state](#91-a-history-is-one-allowed-state): a
  process whose updates are given, written out update by update, is one system
  of rules, and each of its histories is one state that system allows. Knots
  join later updates to earlier ones.
- [9.2 What the rounds count](#92-what-the-rounds-count): the rounds, as run,
  are a supplied clock. Where lesson 8.1's theorem holds, a knot's round counts
  its size, and the growth does not need them.
- [9.3 Births one at a time: the order that is left](#93-births-one-at-a-time-the-order-that-is-left):
  with the rounds gone, what is left is that a knot comes after its parents. It
  cannot always be recovered from what is built; three values on each knot
  sufficed wherever the knots that join were made together, and one start needs
  five.
- [9.4 Clocks made by the growth](#94-clocks-made-by-the-growth): patterns in
  which an event recurs, and what has been counted against them. Whatever
  counts their ticks has so far been supplied.
- [9.5 Priority: which birth is made first](#95-priority-which-birth-is-made-first):
  the owner's priority among updates, and what the record has on the order of
  births: where it changed only how many births lie between returns, and where
  it changed what is built.
- [9.6 Is time a fold of emergence?](#96-is-time-a-fold-of-emergence): the
  owner's question. An order, a clock and a made count of returns are kept
  apart. Only the last takes anything from another pattern, and the record
  has none yet.

**The intuition.** This chapter makes no claim about physical time. The
program's foundation holds that an order of formation alone is not physical
time ([docs/COMMON_VERBIAGE.md](docs/COMMON_VERBIAGE.md)), and every before and
after below is a relation in an allowed state or in the record of a growth. The
program's logic is given no clock. A system is known by the states it allows
(lesson 1.2), so a whole history of a process whose updates are given is one
allowed state, and before and after are relations inside it. Every round, tick
and order of changes in the program's simulations is supplied by whoever runs
them (assumption A228), and the chapter asks which of them the growth can do
without. Where lesson 8.1's theorem holds, the rounds count size; with the
rounds gone, what is left of before and after is that a knot comes after its
parents, and for births made one at a time that order has to be written down.
On the owner's picture (A228) a clock would then be one more pattern, one in
which an event recurs, and time what one pattern counts of another's returns.
The record has such patterns. Whatever counts them is, so far, supplied.

**The owner's words on time.** By 18 November 2026 (Pacific time; the register
carries 19 November, the date in UTC of the first record that quotes it) the
owner had put it as "Time doesn't have ticks". On 23 November he asked: "Also,
what if 'time' is a device or pattern just like the other ones? Are we able to
simulate things 'over time'? So logic is prior to time as well as space." The
register holds this as his interpretation, assumption A228, the sibling of
A112, which says the same of space (lesson 8.5). The same evening he refined it
into a priority among updates, assumption A229 (lesson 9.5). On 24 November
2026 (Pacific time; the record's tickets carry 25 November, its date in UTC) he
asked for this chapter, and whether time is itself a fold of emergence (lesson
9.6). All of these are interpretations, and no result settles them.

**What this chapter adds.** No new result. Every statement stands in a record.
Where an earlier lesson gives it (lessons 1.3, 2.4, 5.3, 7.3, 8.1, 8.6 and
8.7), the chapter points to that lesson; otherwise it links the study. It also
says what is open.

### 9.1 A history is one allowed state

**A history in the Game of Life.** Lesson 1.3 treats Conway's game as one
system of rules. Each cell at each update is a distinction, and the rules of
every cell, over every update, allow exactly the possible histories: the cells
at the start can be anything, and every later update is forced. An oscillator
such as the blinker, which comes back to itself after two updates, is an
allowed state of the same rules with the updates closed into a cycle, and a
spaceship is one closed into a cycle and shifted (classical: Conway's game,
published by Gardner in 1970). Before and after are then relations among the
distinctions of one state. What is supplied is the grid of cells, drawn in
advance, and the update of every cell at once, a tick of Life's supplied clock.

**The static test applied to a process (reading).** Lesson 7.2 asks, as its
question 2, whether loops are better modelled as processes whose outputs over
time are the data, and whether the static test survives that change. For one
process the record's answer is yes: written as its law over every update, a
process is a static law on its histories, and the knot test K1–K3 applies to it
unchanged
([the study of knots across time](research/TIME-KNOTS-20261107-001/time_knots.md)).
What that study proves, for processes in which each cell's next value is a
fixed rule of earlier ones (the literature's cellular automata):

- **Knots across time are the minimal deciding sets (proved).** A knot that
  joins a cell's value after T updates to its start is exactly a set of
  starting cells that, set suitably, decides the later value while no smaller
  set does, together with that value, when the set holds two or more cells; a
  single deciding cell gives a tie, not a knot. Checked against a direct search
  on the 88 elementary rules (Wolfram, 1983) at one and two updates, and on 300
  rules drawn uniformly from all rules of five inputs and of six, 150 of each.
- **When memory of the start is only pairwise (proved, narrowed).** A later
  value that is not constant has no knot with the start exactly when it is a
  single "and", or a single "or", of starting values, each possibly negated.
  The study takes this to be the boundary between two places and three of
  Chapter 3, across time (reading). A narrowing the same day: such a process
  can still knot later updates together, with no starting cell in the knot.
  Rule 128, each cell the "and" of three, does, because it never makes the
  pattern 1 0 1.
- **What some processes keep (proved).** A linear rule keeps one knot of fixed
  size with its start at every number of updates that is a power of two (the
  literature's Frobenius identity over GF(2)); for rule 60 the knot after T
  updates has 2^w + 1 places, w the number of ones in T written in binary
  (Lucas's theorem). One update of Life knots a cell's next value only to sets
  of four of its neighbours, all 70 of them, and never to the cell's own
  present value (proved by exhaustion).

**Counted length across time.** Lesson 2.4 gives the record's other use of
time. In networks of rings of cells, each ring running the literature's rule
60, the record takes a count of contacts along a route as a magnitude, by the
owner's ruling of 8 November 2026: "I think yes, length can count as magnitude"
(assumption A40, confirmed by a test frozen before it ran). The glossary calls
it counted length. From it the record built two exact forms, proved for every
network of that kind: the most disjoint cuts that separate two rings of cells,
which equal the literature's graph distance between them, and what the study
calls a time of flight, which runs one way round each ring
([the study of lengths across time](research/DISTANCE-20261108-001/distance.md)).
Both are found through freezes (assumption A41); without them, the first update
at which a contact needs a ring can break the literature's triangle inequality.
The automaton's updates are given in advance, as every round, tick and order of
changes in the program's simulations is supplied (A228).

**Open for histories.** Life was examined at one update only, and knots that
run through the updates between were counted only for the linear rules. More
basic: every history here has its updates given, as the updates of a board or
of an automaton. Whether a growth of knots, with no update given, is one
allowed state in the same way is the question of the rest of this chapter;
lesson 9.3 gives one case, an order written as distinctions of its own.

### 9.2 What the rounds count

**The rounds as run.** The cheapest growth adds a knot wherever open
distinctions can join, everywhere at once, round by round (lesson 8.1). As run,
the rounds are a supplied clock (glossary, "Clock; tick"): whoever runs the
growth applies its rule to every live knot at once. Lesson 8.1's "Rounds are
not a clock" means that, inside its theorem's class, the growth does not need
them. The glossary uses "round" in the same way for forcing (lesson 5.3), where
the count of rounds is the height of the shallowest derivation. In both, the
count is fixed by the structure.

**What the rounds supplied (computed, refereed).** The cheapest growth's count
of fresh distinctions has to know, when a knot is made, how many joins will
later take from it, and those partners may not exist yet; making every partner
at once supplies that. Laws that make one join at a time instead read that
count from what is there now, one round too early, and they built different
things in different orders in 12 of 14 cases; none of 280 orders matched the
rounds even through round 3, and the order could decide whether a growth goes
on at all
([the study of growth without rounds](research/ROUND-FREE-20261119-001/round_free.md);
lesson 8.1 gives the counts).

**A knot's round counts its size (proved, refereed).** Wherever lesson 8.1's
theorem holds, each knot is one cluster of the unrolled map, and its round is
its cluster's size less one. So the rounds count size, and a growth's rate is
the ratio between the numbers of knots of size k + 1 and of size k, with no
round needed: the golden ratio of the eddy of lesson 8.0, for one. Counted by
size, each part of a joined start keeps exactly the growth it has alone, and
97% to 99.9% of the knots of size 10 or more have clusters with members of two
or more of the joined parts (computed, and refereed for two of the three
joins; same study).

**One fixed structure, smallest pieces first (reading).** The owner asked on 19
November 2026: "The structure changes over time? Like it adds more logic to
itself?" On the reading he accepted, "This makes sense, yes" (assumption A110),
nothing has to change over time: the rounds go through one fixed structure,
perhaps unlimited, by size, smallest pieces first. The start is the piece taken
first, and a round is how much of it has been gone through (lesson 8.1, "One
structure, read outward"). The reading rests on the theorem's class. For the
explosive starts of lesson 8.2 it is open.

**Rounds taken part by part (computed under added rules, referee pending).**
Under the rules added by hand for the ring that returns (lesson 8.7), the
separate parts of the live roster can take their rounds one at a time, in seven
orders supplied by the study (assumption A237, a scaffold;
[the study of a ring in balance](research/RING-IN-BALANCE-20261123-001/decision.md),
its third ticket). In all 726 runs, the knots made while their part had taken
at most R rounds are the same, up to renaming and round by round, as R complete
rounds build, where R is the fewest rounds taken by any part still able to make
a birth (from 2 to 25 over the runs); an argument written for the referee says
why. Under the two orders that always give its round first to the part with
the most members, or with the most loose distinctions, the parts given off
never take another round, so the check there covers only the rounds they had
taken. So under these rules, in the orders tried, no round had to update every
part at once. Inside one part, a law
that makes one birth at a time, with every knot reading what is built again
after each birth, jams: no birth can be made, and knots that owe more than they
hold remain. It jams in every order, all 101,606,400 of them on a cycle of four
live knots joined through dead ones. Lesson 9.3 says what can take the round's
place there.

**What one knot's holdings give (computed, referee pending).** On rings of
knots where every knot keeps a leftover distinction, the golden-ratio eddy
among them, a knot made in round r with p parents and f fresh distinctions has
r = f + 2p − 3, − 5 or − 7, on all 44,333 knots checked. One knot's holdings
then give its round to within three values. Where only some knots keep a
leftover distinction more values of the round fit, and on a bare ring every
knot holds the same and gives no round (lesson 8.7, "A knot can carry the
round, sometimes").

**Three strengths of no ticks (proved and computed, referee pending).** For
rules of motion added by hand, lesson 8.6 takes "Time doesn't have ticks" to
mean that the order of local changes should not matter. If every two local
changes can come in either order, nothing moves. If two changes that are both
ready can, things move, and no largest speed holds across rules. If every fair
order reaches the same end, the strength that fits on the program's reading, a
stored state can be switched between two rings of knots in every order
([the motion-law study](research/MOTION-LAW-20261119-001/what_is_forced.md)).
Where two moving patterns meet, different orders can end differently, and with
no ticks nothing fixes the order (lesson 8.6).

**Open about rounds.** Whether the explosive starts can be taken by size, as
the theorem's class is. The argument that parts may take their rounds in any
order, which is not yet refereed. And whether anything in the growth, rather
than a check we supply, can find a knot's round from what it holds: so far the
holdings give it to within three values only where every knot keeps a leftover
distinction, and more loosely elsewhere.

### 9.3 Births one at a time: the order that is left

**The order that is left (argued, confirmed by its referee).** Take the rounds
away, and make the knot for a cluster as soon as all its parents exist. Every
fair order then reaches the same completed structure, and in the referee's
words "Only a partial order is left": a knot comes after its parents, and
nothing else is ordered
([the referee's report](research/ROUND-FREE-20261119-001/referee-R1/report.md)).
The law reads the whole map of joins in advance, so it trades the tick for
knowledge of the map; it equals the rounds only inside the theorem's class; and
the order must be fair to every birth that keeps coming ready
([the fairness qualification](research/ROUND-FREE-20261119-001/round_free.md#fairness-qualification-20-november-2026)).

**Earliest round first (proved in its scope, referee pending).** Take ordinary
growth: the cheapest growth with no rule added by hand, its births made in
complete rounds or one at a time. Lesson 8.1 gives a law for it that finishes
the births of the earliest unfinished round first, each knot's round found from
what is built; every order of its own births builds what the rounds build, with
no map, on starts whose start knots can be recognised (lesson 8.1, "A law that
reads only what is built";
[the study of serial repairs](research/SERIAL-REPAIRS-20261120-001/decision.md)).
It reads the whole of what is built.

**The brood guard (computed, referee pending).** Inside a part, lesson 8.1
gives a law that makes one birth at a time, each birth recording its parents
(assumption A242, a scaffold). Under the **brood guard** a knot waits until
every knot made alongside it has parents that have finished giving, then works
out from that brood what the round would have had it do. It built what the
rounds build in every order searched (lesson 8.1, "One birth at a time, reading
a few steps";
[the study of a round read locally](research/LOCAL-ROUND-20261123-001/decision.md)):
126 of 193 searches over all orders finished, and the other orders were chosen
uniformly among the allowed births or held each knot's births back as long as
possible; with waiting, full searches reach round 1 and the others round 3. On
the cycles tried, of 4, 6, 8 and 12 live knots joined through dead ones, the
guard's rule needed to read only within four holder steps (a holder step goes
from a knot to a knot sharing a distinction with it), and each further wait
needs one more. In the cases searched nothing outside the knots keeps the
round; the record of parents, which each birth writes, takes its place.

**Where a brood stops being one round (computed, referee pending).** Under
lesson 8.7's cap of three, a new knot receiving at most three fresh
distinctions, the brood guard still works. Where a knot keeps back what its
cancelled joins would have taken (the study's "holding"), it fails, because a
knot then gives in more than one round and a brood is no longer one round
([the study of the guard under the cap and under holding](research/GUARD-CAP-AND-HOLD-20261124-001/decision.md)).

**The order is not recovered from what is built (computed, referee pending).**
The two holders of a shared distinction do not say which is the parent. In the
unfinished structures that births made one at a time pass through, a place
leading to a parent and a place leading to a child are exchanged by a renaming
of the whole structure, under every law tried; the smallest case has two knots.
One finished structure of 16 knots does not show which knot came first. On
structures built by complete rounds two holder steps recover every parent where
a short knot (one that owes more loose distinctions than it holds) retires, and
where it makes offshoots the holder steps needed are one fewer than the round
(proved by hand, confirmed to round twelve). So, for births one at a time under
every law tried, the order cannot always be recovered from what is built
([the search for parents in what is built](research/PARENTS-FROM-HOLDERS-20261124-001/decision.md)).

**Three values handed down (computed, referee pending).** If every new knot
writes one of three values, one on from its parents' value (assumption A247, a
scaffold), a knot distinguishes its parents from its children by comparing
values across one shared distinction. This gave every parent on every structure
reached, unfinished ones included, under four laws, wherever the knots that
join were made together; on the one start built so that a start knot waits
while a knot it meets makes its births, it fails, and five values repair it
there. No two-valued version tried works under every law. The value is the
number of parent steps from the start counted in threes, the literature's
counter modulo three, written by hand
([the study of the least record](research/LEAST-RECORD-20261124-001/decision.md);
lesson 8.1).

**An order written as distinctions (proved).** An earlier study wrote the order
of a growth into the system as distinctions of their own
([the study of growth as a law](research/GROWTH-LAW-20261107-001/growth_law.md)).
On a fixed knot pattern, for a growth rule that reads only the law, the order
and the states are independent, so no knot joins them. Which of two
neighbouring knots came first is a two-place matter; that the order never comes
back to where it began is, on every cycle of knots, one not-all-equal knot over
the cycle's pairs of neighbours (the literature's acyclic orientations).

**The literature's names for this.** Logical clocks (Lamport, 1978) order
events by what depends on what; traces (Mazurkiewicz, 1977) take orders of
independent events as one; a synchronizer (Awerbuch, 1985) runs a rule of
rounds by local waiting. What the record adds is the growth law's own case:
which orders build the same thing, what has to be written, and how many holder
steps a knot's rule must read. Forcing keeps its own order where an atom is
used as a knot, both loops still open (lesson 5.3).

**Open about the order.** Whether the structure can hold such a count itself,
in a knot's own places or in how they are shared, is sub-goal B328, under goal
G5; no construction is known. A guard for knots that keep back, and a rule for
a start knot that makes its births while one it meets waits, are open. That the
brood guard is exact at every round rests on an argument not yet refereed.

### 9.4 Clocks made by the growth

**Made and supplied clocks.** In the glossary a clock is anything in which one
named event recurs and against which other changes are counted; each recurrence
is a tick. A supplied clock is given by whoever runs a system, as the update of
every cell of the Game of Life at once, or the complete rounds (lesson 9.2). A
made clock is a pattern the growth builds from a supplied start in which the
named event, a return or a release, recurs; the study names the event
(assumption A150, a scaffold). "Made" speaks of the pattern only. On the
owner's picture (A228) such a pattern is "a device or pattern just like the
other ones", and time is what one pattern counts of another.

**Patterns in which an event recurs.** The record has several, each with its
own standing:

- **In Life (classical).** The blinker returns every two updates (lesson 1.3),
  against Life's supplied clock.
- **A pattern of state on a ring of knots (proved and computed, referee
  pending).** Under a rule of motion added by hand, a pattern of ten
  distinctions passes every knot of a ring of 31 and returns to exactly the
  same state after 124 changes, and so on for ever; each change is decided
  where the pattern is (lesson 8.6).
- **A generator's releases (proved, refereed in part).** Under ordinary growth
  the smallest known generator, seven knots holding 25 distinctions, releases a
  packet in rounds 15, 23 and 31 and every eighth round after. Each packet is
  larger than the last, so the release recurs and nothing returns (lesson 8.7).
- **The ring that returns (computed under added rules, referee pending).**
  Under two rules added by hand, a ring of five knots returns to its own live
  roster every two rounds while parts of two knots come apart from it (computed
  for odd rings of 5 to 15 knots, argued for every odd ring from five); a third
  rule, under which the parts given off end, puts the whole live roster in
  balance. At each return the ring is exactly the knots that waited, and half a
  period later the same pattern is made of new knots: the pattern is not a
  fixed set of knots (lesson 8.7).
- **Parts that copy (computed under added rules, referee pending).** Under
  rations that give a new knot only enough for three places (a ration is lesson
  8.7's rule for how many fresh distinctions a new knot receives), and with a
  short knot's joins cancelled, a part of two knots becomes two of the same
  every two rounds (lesson 8.7).

**Two clocks in one growth (proved, referee pending).** In one connected
supplied start of 21 knots under ordinary growth, under both knot laws, two
lasting packets keep releasing packets of their own. With a release counted as
a tick, one ticks every 16 parent steps and the other every 24 (a parent step
goes from a knot to one of its parents), so after the start every 48 parent
steps add three ticks to the first and two to the second. Lengthening the
start's unmarked cycle of knots from four to five changes the periods to 18 and
28 and the limiting ratio of the counts to 14/9. A release never enters an
intact member of the other clock; its first common descendant with that clock's
members is a separate birth
([the study of two clocks](research/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001/decision.md)).

**Intervals counted in a receiver's ticks (proved, referee pending).** In these
studies a receiver is a made clock whose own ticks are counted, in a supplied
start chosen so that a send can reach it; a send is one release of a clock; its
receipt is the first birth of the receiver with a parent that carries the send;
and the passage is the knots of the start that link the two (the record's
"middle"). The study counted, in a receiver's ticks: four ticks fell between
send and receipt through a shorter passage and five through the reference
passage, and four again through an equally short passage of knots whose
descendants come to an end
([the receiver study](research/SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001/decision.md)).
In another study a receiver's tick is a birth in its descent at which the same
start knot comes up again (assumption A169). Between the same two receipts it
counted three such ticks in one supplied start and one in another, the two
differing in which start knots could come up in the receiver's descent
([the study of what changes a receiver's count](research/TICK-BIRTHS-AND-SCARCITY-20261121-001/decision.md)).

**Births per tick (proved, referee pending).** Under a rule that makes births
one at a time and finishes first the oldest births that can be made, one of two
such rules supplied by the study (assumption A168, a scaffold), the clock is a
ring of eight knots, one keeping a leftover distinction, whose tick is a birth
with two parents that comes again every four parent steps. It does so alone and
with one more start knot hung on it. Four parent steps took 81 births alone,
253 when the hung knot's descendants take distinctions from the tick's own
parents, and 141 when they take none there (same study). Counted in births the
clock with a hung knot is slower; counted in parent steps it is not. The guide
draws no reading from this.

**What says a tick has happened.** In every case above, the study's check that
a return or a release has happened, and whatever counts the ticks, was
supplied. In the words of the ring study: "The reader that says 'the ring has
returned' is ours: nothing in the growth reads it." No pattern made by the
growth has been shown to count another's returns.

**Open about clocks.** The clocks of the clock studies are in structures that
keep growing; the ring that returns is the one whose own part keeps the same
number of knots. With no round supplied, births made one at a time under the
brood guard build what the rounds build on the ring of five, its first return
included, in every order tried through round 3, given the record of parents
(lesson 9.3); later returns are untested. A clock that no one supplies, counted
by a pattern that no one supplies, is lesson 9.6's question.

### 9.5 Priority: which birth is made first

**The owner's picture of priority.** On 23 November 2026 the owner wrote:
"Also, for the time thing, I feel like it's not really like a sequencer, but
more like a priority system, if that makes sense. How often updates happen
given some property (maybe mass impacts that). In fact, it's kind of like black
holes are the limit of the compute, or the place that absorbs information, like
a reader. It's almost like the distribution of black holes is a statistical way
of getting a sample of the universe. Please record this idea. Then places with
nothing going on need less simulation." The register holds it as his
interpretation, assumption A229: nothing updates every part at once, each part
is updated as often as some property of it sets, and a part with nothing going
on is not updated. No claim is made about mass, black holes or physics. In the
guide a priority says which of the parts or births that are ready goes first
(glossary, "Priority").

**His question of 24 November.** On 24 November 2026 (Pacific time; the
record's tickets carry 25 November, its date in UTC) the owner asked: "Wait so
these computations themselves can have prioritization, and that's essentially
the same thing as time? Just like prioritization?" The record's cases come
first, and the reading given to him after them.

**Where the order changed only the births between returns (computed, referee
pending).** Under the rules of the ring that returns, the four orders of the
parts that give every part its rounds (in turn, by chance, or the part with the
fewest rounds first) build the rounds' structure as far as every part has gone,
while the ring returns after more and more births as the parts given off grow
in number; under the third rule, where those parts end, it returns every 16 to
25 births on the starts tried
([the ring study's third ticket](research/RING-IN-BALANCE-20261123-001C/results.md)).
Under the brood
guard every order of the allowed births that was searched builds the same thing
(A229; lesson 9.3). Separately, the serial clock study held one priority fixed,
the oldest births first, and hung a knot on the clock: the births between ticks
rose because of the hung knot, not because of any order, and the parent steps
between them stayed four (proved, referee pending; lesson 9.4).

**Where the order changed what is built (proved and computed, referee
pending).** Where births compete, the order decides which are made. Under the
supplied rule that works out everything again after each birth, a different
birth made first can rule out a clock's tick for good, by taking a loose
distinction the tick's parents need, or by already having both of them among
its parents while each still holds two loose distinctions (proved; the study of
what changes a receiver's count). Under the same rule, join two copies of a
clock on one knot that holds one loose distinction fewer than the births of
both take from it: one of those births cannot be made, the last in the order,
so in the case tried the order alone decided which clock lost its tick
([the study of two clocks on one short knot](research/REVIEW-LEADS-20261123-001D/result.md)).
Two other cases have causes of their own: the first one-join-at-a-time laws read from what is there
now how many joins will take from a new knot (lesson 9.2, refereed), and under
holding a brood is no longer one round (lesson 9.3). Orders that never make
some births change what is built for that reason alone: under the two that
always give the largest part its round first, the parts given off never take
another round and the ring returns every 4n births, n the knots of the start;
under the order that gives the smallest part its round first, each part given
off takes rounds until it has more members than the ring, and then never again
(same ticket).

**Which distinction a birth takes (computed, referee pending).** This is not a
priority: it says what a birth takes, not when. A law added by hand that lets a
birth also take an already shared distinction must say which. Under rule R, in
which a short knot gives its births distinctions it already shares, taking the
oldest or the newest gave different births per round on 478 (parity) and 471
(not-all-equal) of the 744 starts that stall at once under ordinary growth
([the study of a short knot that gives shared distinctions](research/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A/result.md)).
In the study of parts that meet again (lesson 10.3), changing which distinction
one part's births take makes that part's dependence on the other appear or go.
All four ways tried pick from the eligible distinctions in the order of their
names: the oldest, the newest, the next in turn among one parent's offshoots,
or the one at a count of the parent's places. None is made by the growth
([the study of parts that meet again](research/PARTS-MEET-AGAIN-20261124-001/decision.md)).

**The reading given to the owner (reading).** The guide takes the cases above
as two kinds of order of births. Where every birth is made in the end, the
order changed how many births lie between returns and not what was made; that
is the kind his question is about. Where births compete, or an order never
makes some births, the order changed what was made. Lesson 7.3 has something
alike for growth one knot at a time: there an outcome belongs to the growth in
its order, not to the pattern it reaches.

**Places with nothing going on.** Growth makes births only at live knots, so a
part with nothing loose has none; this is the record's nearest case to the
owner's "places with nothing going on" (A229). Every priority in the record so
far was supplied, and the candidates for one found from the structure, filed
with sub-goal B320 under G5, are a knot's places, its loose distinctions and
the knots within its bond ball. The owner's idea of a sample has no counterpart
in the record.

**Open about priority.** A priority found from the structure, under which what
is built does not depend on how ties are broken, and under which a part's
births per tick rise as more is joined to it (B320). None is known.

### 9.6 Is time a fold of emergence?

**His question.** On 24 November 2026 (Pacific time; the record's tickets carry
25 November, its date in UTC) the owner asked: "Is time itself a fold like
intelligence/life through DNA?" A fold of
emergence, his phrase of 23 November 2026 (assumption A223; lesson 8.7), would
be a pattern with three properties: the rules make it and nobody places it;
what it makes depends on another pattern; and it makes a pattern of its own.
The answer below is a reading, set against the record; the register keeps it in
the history of A228. No claim is made about living things or minds.

**Three things kept apart (reading).**

- **An order.** A knot comes after its parents. That is kept in the record of
  births, which the births write; it is not a pattern, and it cannot always be
  recovered from what is built (lesson 9.3). It makes nothing, so it is no fold
  of emergence.
- **A clock.** A pattern in which an event recurs (lesson 9.4). The ring that
  returns, under two rules added by hand, takes nothing in: past the start its
  parts grow alone. Clocks inside one connected growth can lose a tick when
  another birth takes a shared knot's last loose distinction, under supplied
  orders (lesson 9.5); in the case tried, two copies of one clock, the order
  alone decided which lost its tick.
- **A made count of returns.** A pattern whose births follow another pattern's
  returns, A228's reading of "time is a pattern". What it makes would depend
  on another pattern, and it would make something of its own, the count. At
  each return it would need from the other pattern only whether it has
  returned, one yes-or-no. Whether that is enough for the second property of
  a fold of emergence, which the register asks for in a fuller sense (lesson
  10.1), is not settled: a count that follows returns would differ between two
  clocks of different periods, and no such comparison has been run.

**What one part has read of another (computed under added rules, referee
pending).** In the study of parts that meet again (lesson 10.3), under laws
added by hand in which a birth also takes a distinction none of its parents
holds, one part's course differed between the run with another part growing
and the run with it barred for 216 pairs that passed the study's checks, and
in none of the 16 pairs asked with what the other part was. That dependence
came about where two parts that had come apart were one part again, directly
or through a third part. Under rule R and rule Q (in which a one-parent birth
also takes a distinction its parent shares), parts that have come apart and
share nothing, even through a third part, never become one part
again, by an argument, and from round 1 the ring never returns and nothing
copies itself
([the study of parts that meet again](research/PARTS-MEET-AGAIN-20261124-001/decision.md)).
A made count of returns would need such a meeting at every return (reading).

**What a made count still lacks.** Two things. Every count of ticks in the
record is supplied (lesson 9.4). And the patterns in which an event recurs come
from laws under which parts that come apart never meet again, while the first
two laws tried that keep would-be parts joined undo the ring. Whether one law
can hold both a pattern that returns and a second pattern that meets it at each
return has not yet been tested.

**Where it is taken up.** Sub-goal B329, under G5 with G15 and G18, files the
question, and a study now being designed takes it up
(TIME-AS-FOLD-20261125-001). As filed, its first step is a census of which
patterns still return under the law of least cost that lets parts meet, with
both of its rations. It has no result. Lesson 10.4 sets it beside the other
study in design, a made copier.

## Chapter 10. Folds of emergence

### 10.0 Introduction

**The lessons.** What each lesson of this chapter is about:

- [10.1 What a fold of emergence would be, and the nearest things in the record](#101-what-a-fold-of-emergence-would-be-and-the-nearest-things-in-the-record):
  the owner's picture in his words, the three properties the program takes
  from it, and what a test of them can show. The nearest things in the record
  each lack a property: a generator's packets, a made clock, the part that
  copies itself, and the studies in which a rule written by hand acts on what
  is taken.
- [10.2 The with-and-without test: whether one part's course depends on another](#102-the-with-and-without-test-whether-one-parts-course-depends-on-another):
  the owner's test as one study measured it. A start is grown, and grown again
  with a second part barred, and further runs check whether a difference went
  through the two parts meeting. It asks whether, never what.
- [10.3 Parts that meet again, under laws added by hand](#103-parts-that-meet-again-under-laws-added-by-hand):
  where a birth takes only what its parents hold, parts that share nothing,
  even through a third part, are never one part again, by an argument. Under
  laws added by hand under which a birth takes a distinction none of its
  parents holds, in
  some of one study's cases they are, and the first part's course then differs
  between the run with the second growing and the run with it barred, and in
  none of the 16 pairs asked with what the second is.
- [10.4 Two studies in design: a made copier and a made count of returns](#104-two-studies-in-design-a-made-copier-and-a-made-count-of-returns):
  two studies in design, one asking for each. The first has frozen its claim,
  predicts that every registered claim fails and has made no registered run;
  the second is not frozen. Neither has a result.
- [10.5 What is open](#105-what-is-open): the open sub-goals, one by one.

**The intuition.** The record has no fold of emergence. A growth that only
repeats or multiplies makes more of what it already is. The owner pictures a
pattern of a further kind, with three properties (lesson 10.1), and calls it a
fold of emergence (assumption A223, an interpretation), with DNA and
intelligence as his pictures of it. The guide makes no claim about living
things or minds in this chapter: the phrase and the pictures are his, and the
properties are the program's reading of them. The program checks the second
property, that what the pattern makes depends on another pattern, by a
comparison: what is built with the other pattern growing against what is built
with it barred. That comparison, the owner's test, settles whether, not what.
Under ordinary growth the connected parts of the live roster (lesson 8.7)
neither come apart nor merge, and under the rules added for the ring that
returns the parts that come apart act alone, so nothing one part makes can
depend on another (lesson 8.7; the register's notes under A223). The chapter
goes through the record from that obstacle to laws added by hand under which,
in some of one study's cases, parts that came apart are one part again, and
says what is still missing.

**No new result.** Every statement stands in a record; where an earlier lesson
gives it, the chapter names that lesson.

**The growth's words used here.** A start knot is a knot of the start, and a
member is a live knot of the live roster (lessons 8.1 and 8.4). A part of the
live roster is a largest set of members any two of which are connected by a
chain of members in which one knot meets each member and the next (lesson
8.7). A part comes apart when the members descended from it lie in two or more
parts. Two parts share nothing when no member of one holds a distinction a
member of the other holds, and are wholly apart when no chain of parts, each
sharing a distinction with the next, joins them. A ration says how many fresh
distinctions a new knot receives (lesson 9.4). A short knot owes more loose
distinctions than it holds; a law says whether it retires, waits or makes
offshoots, and whether a knot that is not short releases to offshoots what its
cancelled joins would have taken or holds it (lesson 8.7). A barred
distinction is one no birth may take; a usable one is loose and not barred. A
knot's ancestors are the knots reached from it by parent steps. A taking rule
is a rule added to a growth law under which a birth also takes one distinction
that is already shared, by a supplied convention for which: under rule R a
short knot gives its births distinctions it already shares, and under rule Q a
one-parent birth also takes a distinction its parent shares (lessons 9.5 and
9.6).

### 10.1 What a fold of emergence would be, and the nearest things in the record

**The picture he asked to record.** On 23 November 2026 the owner asked for a
picture to be recorded, given in full in lesson 8.7. In it things like DNA
"are kind of like patterns that observe a different pattern but also have
their own growing patterns", and "structures like DNA or intelligence should
maybe be exceptional, almost considered folds of emergence." The register
holds it as assumption A223, an interpretation on which no result rests.

**Three properties (reading).** Lesson 8.7 gives them in one sentence (A223).
Here each is given with what would show it:

1. The rules make it and nobody places it: it grows from a supplied start
  under a stated law, and nothing is placed by hand after the start.
2. What it makes depends on another pattern. The register asks for the fuller
  sense: it takes one course or another according to what a second made
  pattern is (A223, "Challenge"; sub-goal B317), not only whether it is
  barred.
3. It makes a pattern of its own from the other pattern (A223; B317).

**What the properties can show.** The record has no fold of emergence. The
properties speak of patterns and the test of lesson 10.2 of parts of the live
roster, so the test applies only to a pattern that is such a part. The first
two properties can be tested, the second by comparing runs. The record has no
registered test for the third, so a new pattern can be shown not to be a fold
of emergence, by failing the first or the second, but cannot yet be shown to
be one.

**The nearest things in the record.** Four kinds of thing come close. Each
lacks at least one property, and the record says what was supplied in each.

- **A generator's packets (proved; refereed in part).** Under ordinary growth,
  from a supplied start, a generator keeps releasing packets that last, and a
  packet can release packets of its own (lesson 8.7): they are made, and they
  make more. After release every parent of a later member comes from its own
  packet, and once each packet has taken all its parents from its own members
  for one round, no later birth has a parent in two packets. Where what a
  packet makes differs with another packet (a knot receiving 18 fresh
  distinctions where two packets are joined and 15 where they are kept apart),
  the difference lies between two prepared starts
  ([the generator study](research/GENERATORS-20261120-001/decision.md)).
  Which knots count as
  a packet is set by a scaffold (assumption A125).
- **A made clock (lesson 9.4).** A pattern the growth builds from a supplied
  start, in which a named event recurs. The ring that returns takes nothing
  from another pattern (lesson 9.6): past the start a part acts alone
  ([the ring study without a supplied round](research/RING-IN-BALANCE-20261123-001C/results.md),
  argued, and its
  consequence checked on 726 runs, referee pending). In the start with two
  clocks no release of one enters the other's packet
  ([the study of two clocks](research/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001/decision.md),
  proved, referee pending); where two copies of one clock share a short knot,
  which one lost its tick was decided by the order of births, which is
  supplied (lesson 9.5). The study's check that a tick has happened, and
  whatever counts the ticks, is supplied.
- **The part that copies itself (computed under added rules, referee
  pending).** It is made and makes two of itself every two rounds under
  rations and treatments added by hand (lesson 8.7; assumption A224, a
  scaffold), taking nothing from another pattern. In its record's words, "The
  copies never meet again", and "Nothing reads the count of copies; the one
  who runs the growth counts them"
  ([the study](research/COPYING-PARTS-20261123-001/decision.md)).

- **The stored bit, the receiver and the learning line (written by hand).** In
  none is the rule for acting on what is taken made by the growth (lesson
  8.7); where the pattern itself is made, as a receiver is, what counts as its
  receipt was supplied. Each study lists what it supplied:
  - the stored-bit study (proved, referee pending): a stored value steers no
    ordinary birth (lesson 8.7); supplied were "the marked preparation,
    payment allocation, local read and probability weighting"
    ([its decision](research/STORED-BIT-AND-NEXT-ACTION-20261122-001/decision.md));
  - the receiver study of lesson 9.4 (proved, referee pending): a receiver is
    a made clock, its tick counts were compared between supplied starts, and
    "The clock frames, sending phase, receiving family, ports and tick reading
    were also supplied"
    ([its decision](research/SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001/decision.md));
  - two studies of the learning line under goal G15, learning in a knot
    pattern (computed, referee pending): in a game played on knots that
    ordinary growth makes, "Food, hunger, the sensor, the cursor, its
    controls, reward and policies are supplied game rules"
    ([the game](research/KNOT-RATION-GAME-20261121-001/decision.md));
    in sorting two
    letters from pixels, "Image layout, patch grouping, translation sharing,
    reward update, binary storage code and mean comparison were supplied"
    ([the letters](research/PIXEL-LETTERS-20261122-001/decision.md)).

**The second property, untested before.** Before the study of lesson 10.3 the
record had no case in which what one made part builds differs between a run
with another made part growing and a run with it barred, with nothing placed
by hand after the start (the register's notes under A223). The owner gave a
test for that property.

### 10.2 The with-and-without test: whether one part's course depends on another

**The test in his words.** By 24 November 2026 (Pacific time) the owner had
set it: "run each start twice, once with the second part present and once
without it. A part reads another when its course differs between the two
runs." This is the guide's one sense of "reads" for a part, and it is his. The
study of parts that meet again (lesson 10.3) fixed how to run it before
running anything
([its definitions](research/PARTS-MEET-AGAIN-20261124-001/definitions.md),
sections
1 and 5), and its records call it the paired test. The register keeps the test
as run as a measure, assumption A246, and the study lists every part of it
among what it supplied by hand.

**When two parts meet.** Two parts meet at a round when one knot meets a
member of each, so that those two members can join through it; parts that came
apart are then one part again, in the study's words, as they can also be
through a third part. "Meet again" is the owner's phrase.

**Three runs, and a fourth.**

- Run A grows the start under the law.
- For a round s after which two parts X and Y are wholly apart, a second run
  repeats run A through round s and then bars every usable loose distinction
  of Y's members: Y stays built and makes no birth, and the same law goes on.
  Removing Y with its fresh distinctions is the registered alternative,
  defined only where it leaves a well-formed structure. Of the 302 pairs of
  lesson 10.3 it was defined for 182, and gave the same result for every one

  ([the study's decision](research/PARTS-MEET-AGAIN-20261124-001/decision.md)).

- The comparison is of X's course, round by round: each birth whose parents
  all lie in X or its descendants, with its parents, what it takes and the
  number of its fresh distinctions, and which sets of their members one knot
  meets, up to a renaming of the knots made after round s. A birth's demand is
  recorded separately and is not part of the course; counted in, the course
  differs a round earlier for 114 of the 302 pairs (A246).
- A masked run repeats run A with no member of X or its descendants able to
  join a member of Y or its descendants from round s + 1. It is the study's
  check of whether a difference went through the two parts meeting: it did
  when X's course there equals its course with Y barred. If not, a fourth run,
  in which Y and its descendants can join nothing, checks whether it went
  through a third part. A difference passes the study's check by either run.

**Four things recorded for each pair.** The study's "marks", facts about run A
and comparisons and not a scale: the first round at which X and Y are one part
again; the first birth with a parent from each; the first round at which X's
course differs with Y barred; and whether X's course differs with what Y is,
between two runs from starts that differ only in the holdings of the start
knot (a knot of the start) that Y descends from. A control asks whether it
matters which distinction a birth takes: only the births of X and its
descendants take by another convention, and the course is compared again.

**Three questions for each difference.** Did it go through the two parts
meeting, or through a third part? At the round they are one part again, is the
common knot of their members one the growth made, or a start knot? And did the
rule that made the difference act on a whole round, read the parts of the
roster to find the other, or join by the record of births alone? The answer is
one of four: through a knot the growth made; through a start knot; by the rule
itself, for those three rules; or, in the study's word, "unconfirmed". In
every case the law's taking rule, its convention for which distinction a birth
takes, any record it reads, the base law, the start and the complete round are
supplied: "made by the growth" means made by births under a stated law, not
that the law is the model's
([the pre-registration](research/PARTS-MEET-AGAIN-20261124-001A/preregistration.md)).


**What the test cannot show.**

- What the other part is. A difference with Y barred is a difference between Y
  growing and Y barred, one yes-or-no. Only the fourth thing recorded asks
  what Y is, and it compares two prepared starts, the comparison the
  with-and-without test otherwise avoids.
- How often parts meet. That needs a weighting over laws and starts, and the
  study, whose laws and starts were set by hand, has none: it can say which of
  its cases meet and how each fares when a scaffold is swapped, not how often
  meeting happens (the register's notes under A241). The owner said the same
  day that he did not "expect these to be common or trivial".
- Whether another measure would agree. The register names three to try:
  removal throughout, demand counted in the course, and dependence on what the
  other part is (A246).
- (reading) It is still a comparison of two runs, both run by whoever runs the
  study. Against the comparisons of lesson 8.7 it gains this: the two runs
  share one start and the same births through round s, so the difference lies
  between the other part growing and the other part barred, not between two
  prepared starts.

### 10.3 Parts that meet again, under laws added by hand

**The study and its question.** By 24 November 2026 (Pacific time) the owner
had asked whether some growth law lets parts that have come apart meet again.
Before the design was frozen he added: "There's no way it wouldn't work. It
might just cost complexity. Programming is a thing in our reality, there
should be a way to reference information like joining 2 different clusters of
child logic from the parent via something like an 'axis point'. So we can
essentially reference chunks of logic." The register keeps this as his
conviction, not as evidence (assumption A241). In the guide's words (glossary)
the knot is an ancestral common knot, "a common knot of two members that is
also a recorded ancestor of both and not the parent of both", and the law is
ancestor-taking, "a law under which a birth also takes a distinction that an
ancestor of one of its parents holds"; "axis point", and afterwards "access
point", stay his phrases; he chose "ancestral common knot for the definition",
and his later "Root" was not adopted (the study's definitions). The study is
one frozen study, computed, a second program agreeing on every pair; referee
pending
([PARTS-MEET-AGAIN-20261124-001](research/PARTS-MEET-AGAIN-20261124-001/decision.md);
[its results](research/PARTS-MEET-AGAIN-20261124-001A/results.md)).

**Taking only from parents (an argument, not yet refereed).** Under rule R
(A230), rule Q (A235) and the move of A225 taken as a law, a birth takes only
what its parents hold, and whatever a parent holds is already met by
everything the parent meets; so such a birth can rejoin only what is still
joined. No run contradicts it: no two parts that share nothing, even through a
third part, were one part again in 504 runs, in about 1,600 pairs got by
switching the rule on after the copies are made, or in 3.57 million histories
so far: in 326 parts of one enumeration every possibility for which
distinction each birth takes, and in each of 32 others 100,000 histories taken
at random under a fixed seed, with two parts still running. Rules R and Q also undo the ring that returns and the part that
copies itself (lesson 9.6).

**Taking what no parent holds (computed under added rules, referee pending).**
Here a birth also takes such a distinction (assumption A245, a scaffold): one
held by a knot its parent meets, or by a recorded ancestor one or two parent
steps from its parent. Taking from a knot the parent meets reads within two
holder steps and no record of births; in the study's order of costs it was
least under the cap of three, on the ring of five, and the rule taking from
one parent step under "just enough for three places", a ranking that turns on
a reading the frozen text left open (its prediction P11). Each needs a
supplied convention for which distinction a birth takes; the four tried all go
by the names (lesson 9.5), and changing it for the first part alone makes the
dependence appear or go. Distinctions gain holders: within eight rounds one
reached 182 under the rule taking from a knot the parent meets, 114 under that
from two parent steps and 128 under rule Q itself, against 2 with no taking
rule.

**What was found.** Counting both knot laws together, 302 pairs of parts that
came apart show the first part's course differing with the second barred. For
216 pairs the difference passed the study's checks, going through births that
made the two one part again: for 178 through the two parts meeting, for 38
through a third part. Of the 216, 180 are through a knot the growth made and
36 through a start knot, a split that can change with the supplied names, as
the smallest case shows. Another 80 are by the rule itself, all under a
control rule that reads the parts of the roster to find the other, and 6 are
"unconfirmed". Of the 216, for 62 an ancestral common knot, always a start
knot, is among the common knots of the two parts' members, and for 6 it is the
only one. For 72, a third, a birth is then made with a parent in each part;
for the rest the meeting only leaves knots short. In none of the 16 pairs
asked does the course differ with what the other part is. The register moved
A241 to Confirmed, with stated limits: under supplied laws, with the ancestral
common knot always a start knot, and not sturdily.

**The smallest case.** Twenty knots: the three-knot start, the ration "just
enough for three places", a short knot retiring, and the oldest distinction
taken from two parent steps from the parent. The two members join in round 1
and each makes an offshoot. In round 2 the join, short, retires and each
offshoot makes two, leaving two parts of two knots that share nothing. In
round 3 their offshoots take distinctions that the start knot each part
descends from shares with the start's dead knot, which then meets all four:
one part again. In round 4 the four, short, retire; with the second part
barred or removed, the first makes a join of three parents instead. Every knot
passes the knot test under both knot laws through round 8. Their common knot
is the start's dead knot, which neither part descends from; with the start
renamed, it is the retired join of round 1, a knot the growth made.

**What swapping the scaffolds leaves.** Each case, a taking rule with its
convention, a base law and a start with a pair that passed the study's checks,
80 in all (33 of parts that came apart and 47 of the two-knot start's halves,
never one part), was rerun with each supplied rule swapped. Swapping the
ration on the same start removes all 33, though each ration has cases
elsewhere; under the cap of three the smallest case's two parts never come
apart. Holding instead of release removes 24, reversed names 12, the demand
counted before the takes 9, a reversed order of births 5, fresh distinctions
counted by parents 4, and the knot law none. The one case that remains under
every swap joins the two-knot start's halves. In the study's words, "nothing
here is yet a property of the model".

### 10.4 Two studies in design: a made copier and a made count of returns

**A copier is a pattern.** On 24 November 2026 the owner wrote: "copying would
not be a law. Laws are for how the knots interact. A copy function, like other
functions, would be a logical structure that has a meeting pattern with other
things. And we would need to prove that the copy/paste pattern can be
generalized." He asked that two things be kept apart in everything written
about it: "a law is the rule the growth follows (which knots join, what a new
knot receives, what a short knot does); a copier is a pattern the growth
makes." The register holds this as assumption A244, a working premise
(sub-goal B327, under goal G15). A copier would meet a second pattern and
leave two of the second; the part that copies itself leaves two of itself.

**The claim, frozen and not yet run.** The study of a made copier,
MADE-COPIER-20261125-001, froze its first ticket on the evening of 24 November
2026 (Pacific time; 25 November in UTC), before its code was written, so no
registered run has been made
([its claim](research/MADE-COPIER-20261125-001/claim.md);
[its pre-registration](research/MADE-COPIER-20261125-001A/preregistration.md)).
The law is fixed before any pattern: the taking rule that takes from a knot the
parent meets, with the rule taking from one parent step as a second, under
stated base laws and each of the four conventions for which distinction a
birth takes. The first pattern is the part of two knots; the second patterns
form small classes set out in advance. His three readings of "two of it", "the
same form, the same built structure, or the same values", become two parts the
same as the second pattern; two sets of made knots each a renaming of the
second pattern's knots; and two usable loose made distinctions each tied to
one place of the second pattern (glossary, "Tie class"). Two things are
settled by argument before any run: under its taking rules with the ration
"just enough for three places" no part with a member holding two loose
distinctions is made except by offshoots of start knots, so the form reading
is tested under other base laws; and under not-all-equal, from a start with no
tie, no made distinction is ever tied to another, so the values reading is
claimed under parity only. Every registered claim is predicted to fail; a
failure would speak of that one first pattern, those rules and those classes
only.

**Consume and output two.** Later the same evening, before the freeze, the
owner wrote: "I have a trick maybe. What if instead of 'copying', we consume
and output 2?" (24 November 2026, Pacific time; the record's tickets carry 25
November). It changes what counts as two. The two patterns would become one
part, births with a parent in each would use up the second pattern's loose
distinctions, the second pattern's own descendants would end, and the two
afterwards would descend from both patterns; the frozen claim counts only two
whose members descend from the first pattern alone. A second ticket of the
same study is being designed for it; nothing of it is frozen or run.

**An inkling that no copier is general.** "the interesting fact here is that
it's actually impossible to generalize a 'copier' for all logic structures. It
might be the case that some logic models are able to over-write the
instructions of the copier and break out." (24 November 2026, Pacific time;
the record's dates carry 25 November.) It is assumption A248, a working
premise kept apart from the evidence. The frozen claim registers it as a
reading (its section 6): no first pattern, law and stated rule leaves two of
every member of a registered class; since the classes are finite, failures
would only support it, and one pattern that works for a whole class would
overturn it for that class. "Over-write the instructions" and "break out" stay
in his words.

**What a made count would be.** A made count of returns would be a pattern the
growth builds whose births follow another pattern's returns; "made" speaks of
the pattern only, as for a made clock (glossary, "Clock; tick"). Lesson 9.6
keeps it apart from an order and a clock, and says what it still lacks. At
each return it would need only whether the other pattern has returned, one
yes-or-no. Whether that is enough for the second property in its fuller sense
is not settled (reading): a count that follows returns would differ between
two clocks of different periods, which is a difference with what the other
pattern is, and no such comparison has been run. Whether a part has returned
is also a different yes-or-no from whether it is barred, and the study of
lesson 10.3 did not ask it.

**What each would ask of the other pattern (reading).** A count needs one
yes-or-no at each return. A copier that leaves two of two different second
patterns would, as the register records the copier study's reading (A248),
need a course that depends on what it meets, and in the 16 pairs of lesson
10.3 no course depended on what the other part is.

**The study of a made count.** TIME-AS-FOLD-20261125-001 (the record's
identifier; its "fold" is short for the owner's phrase) takes sub-goal B329,
under goal G5, dynamics, with G15 and goal G18, comparing growth laws: whether
a pattern the growth makes can count another pattern's returns. It is not
frozen and has no result.

### 10.5 What is open

**The plain answer.** The record has no fold of emergence. In the study of
lesson 10.3 the parts are made one part again by births with nothing placed
after the start, under taking rules, conventions for which distinction a birth
takes, rations and starts that are all supplied. What one part then builds
differs between the run with the other growing and the run with it barred; in
none of the 16 pairs asked does it differ with what the other is; and no part
made a pattern of its own from what it met.

**Open, by sub-goal.**

- **B317's remainder (goal G15).** A part whose course depends on what the
  other part is, and that makes a pattern of its own from it; neither was
  found (B317's note of 25 November). Two directions the study deferred bear
  on it: vary the second part more widely under the rule that takes from a
  knot the parent meets, stopping at one such dependence or at a reason that
  only whether the other grows can matter; and find a base law under which
  parts come apart under both rations, for a case that remains under a change
  of ration.
- **B326, an index made by the growth (G15).** The owner, by 24 November 2026
  (Pacific time): "This is why we may need 'function-like' logical operations
  where we can reference/sample logic. These are basically meeting patterns
  that are complex in nature. Maybe even so complex as to the indexing
  operation being logic based iterators rather than incremental. So like maybe
  intelligence as a fold has access to something like 'the golden ratio', but
  it needs to index what part of the golden ratio it's looking at?" (his
  picture, on which the guide makes no claim; the register's notes under
  A241). In the program's terms what is needed is which part of the other
  pattern is taken (his "indexing"), made by the growth and not kept from
  outside. In the laws of lesson 10.3 that is which distinction a birth takes,
  and every convention for it is supplied. One of them, by count, takes a
  number from the structure but uses it as a position in the list of eligible
  distinctions sorted by the supplied names (the study's results, dated note
  of 25 November). In the golden-ratio eddy a knot's own holdings already give
  the round it was made in to within three values, and no rule reads them
  ([what a reference is](research/RING-IN-BALANCE-20261123-001B/results.md),
  computed, referee pending). The first step as filed: fix the taken
  distinction by something the structure holds, and compare with the supplied
  conventions on the same starts.
- **B327 and B329.** Taken by the two studies of lesson 10.4: the first frozen
  and not run, the second not frozen.
- **B328, where it bears (goal G5, dynamics).** The rules that take from one
  or two parent steps from a parent read the record of births, which each
  birth writes and the study lists as supplied; the rule that takes from a
  knot the parent meets reads no record. For births made one at a time, three
  values on each knot stood in for the record of parents wherever the knots
  that join were made together (lesson 8.1; assumption A247, a scaffold); this
  was not tested for these laws. Whether the structure itself can hold such a
  count of descent is B328. (reading) If it can, ancestor-taking would need no
  written record of descent; which distinction it takes would still go by the
  supplied names.
- **Referee and run.** The argument for the laws that take only from parents,
  and every computed result of lesson 10.3, await their referee. That study
  froze 19 predictions: 16 hold, two fail in one clause each, both in
  controls, and one turns on a reading. It ran six starts for eight rounds,
  about 1,500 knots a run, under laws set by hand, and two parts of one
  registered enumeration were still running on 25 November 2026.

**What would answer it (reading).** By the register's own test, a first
instance would be "one growth in which a made pattern takes one course or
another according to what a second made pattern is, with nothing read or
chosen from outside" (A223), with the masked run of lesson 10.2 showing that
the difference went through the two parts meeting. A fold of emergence would
then also need the third property, for which no test is registered.

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
  not even a place to put them. The owner's founding premise, in his words (17
  November 2026): "Distance is the only form of information. That's the entire
  basis of the 'this versus that' distinction in the smallest emergent unit"
  (lesson 2.4: an interpretation, under challenge as assumption A97).
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
- **Minimal contact-distance.** The foundation's name for the one touch of a
  complete knot: the smallest relative existence, with no magnitude,
  direction, coordinate or metric (lesson 2.4). The intuition: in a knot, A
  and B first exist relative to each other, through c, without becoming one.
  It is not a number. Bond distance and the guide's other counts come later,
  from many knots.
- **Information.** What a system's allowed states tell apart (lesson 2.4).
  The part a whole holds and no part holds is joint information, measured in
  bits in lesson 2.3: about 0.193 bits for the atom, one bit for parity. The
  owner's founding premise is that all information is distance; which notion
  of distance he means is open (lesson 2.4).
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
  comes from the rules and is never drawn. Read as all the information a base
  holds, as the owner's founding premise would have it, bond distance between
  pairs falls short from four distinctions up (lesson 2.4).
- **Disagreement count.** For two distinctions, the number of allowed states
  in which they take different values; as a share of the allowed states it is
  the **disagreement rate**. It is a count across the allowed states, not an
  extended or metric distance. Not-all-equal on three distinctions is a sum of
  their disagreements, so from four distinctions on the table determines the
  allowed states of every base defined by three-place not-all-equal rules. Three distinctions
  are in order exactly when a three-place constraint holds on them (lesson 2.4).
- **Steps apart.** Two distinctions are d steps apart when the shortest row of
  co-knotted pairs leading from one to the other, each pair sharing a
  distinction with the next, has d pairs (lesson 4.7): the literature's graph
  distance. It is a count on the meeting pattern, given with it, and the ruler
  of lesson 4.7 is the theorem that bond distance measures it. On a board, a
  step goes from a cell to a neighbouring cell (lesson 4.6).
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
  subshift. Not the harmony of proof theory. The period of a state (see Return;
  period) is the least shift that returns it to itself, which is not the period
  of the base;
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
- **Round.** One step of propagation in an atom pattern whose held distinctions the outside sets to 1: every atom
  whose two demanders are forced forces the distinction it demands (the literature's synchronous unit propagation).
  The count of rounds is the height of the shallowest derivation (lesson 5.3), as `SEQUENTIAL-WALL-20261116-001`
  found on 16 November 2026. In growth (lesson 8.1), a round is one application of the joining rule to every live
  junction at once; inside the theorem's class a junction's round is its cluster's size less one.
- **Phase.** One stage of the forcing law (lesson 5.3): every atom with a forced demander is read as the two-place rule
  from its other demander to what it demands, and everything reachable along those rules is forced at once. A distinction's
  phase is the first that forces it, and it equals the least Strahler number of its derivation trees (the
  literature's Horton–Strahler number, or tree dimension; the stages are Newton iterates). The dual law's phases
  spread unforcedness the same way, on patterns without cycles. Never "phase transition": the sudden leap of the
  forced set is the jump. The intuition, in the owner's word: a phase untangles everything that comes apart once one
  distinction of a knot is settled, since what is left of the knot is a two-place rule, which is no knot.
- **Open use.** An atom whose two demanders are first forced in the same phase (lesson 5.3): it is used as a knot, both
  its loops still open, and only open uses make the forcing law take another phase.
- **Reused; demanded several ways; rejoining.** In an atom pattern (lesson 5.3), a distinction is reused when it
  demands in two or more atoms, and
  demanded several ways when two or more atoms demand it (not the choice rule above, though in the forced set it
  offers alternative derivations). A rejoining is an atom with one distinction below both of its demanders in a
  derivation tree. Without reuse an atom pattern needs at most log₂ of its held count phases, more phases than that
  need a rejoining, and the sequential wall needs reuse unless P = NC and several-way demand unless P = NL
  (`SEQUENTIAL-WALL-20261116-001`).
- **Carried distinction; keep and spend.** A law for forcing (lesson 5.3) may carry up to w open distinctions in a
  phase and take
  an open use while carrying both demanders. A step spends what it uses, or keeps it to use again; the spend-only law
  needs ⌈σ/w⌉ phases for Strahler number σ (the literature's register allocation), and the keep law reaches in one
  phase what w black pebbles with sliding reach (the literature's pebble game). The intuition, in the owner's words:
  carrying is holding several strands, and keeping lets one strand split into two that later rejoin; splitting pays
  only where strands rejoin (`CARRY-STRANDS-20261116-001`, 16 November 2026).
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
- **History.** One whole run of a process or a growth with nothing left
  open. For a process whose updates are given: the value of every cell at
  every update (lesson 1.3). For a growth: one run, with its order of births
  and which distinction each birth takes fixed. A history of the first kind is
  one allowed state of the process's rules (lessons 1.3 and 9.1); a growth's
  order, written as distinctions of its own, has been treated the same way on
  fixed knot patterns (lesson 9.3), and for a growth with no update given the
  question is open (lesson 9.1). Runs that differ only in the order of births
  are different histories, even when they build the same structure.
- **Move.** One action of a growth that goes one piece at a time, as that
  growth defines it: in the random processes of lesson 7.3, one knot added, or
  nothing when there is nothing left to add; in the laws that make one birth
  at a time, one birth (lesson 9.3); in the part-round law of the study of a
  ring in balance, one part's complete round (lesson 9.2). The processes of
  lesson 7.3 are counted in moves, and the **horizon** is the number of moves
  computed. A count of moves is never called a count of steps (see the row
  for "step").
- **Birth.** The making of one knot by a growth law, in a round or alone
  (lessons 8.1 and 8.7). Its parents are the members it is made from: the
  members of a join's group, or an offshoot's one member (see Junction;
  parent); under some laws added by hand it also takes a distinction that none
  of its parents holds (see Ancestral common knot; ancestor-taking). Its fresh
  distinctions are those it alone holds when it is made. Growth is counted in
  rounds, in births or, in lesson 7.3, in moves; every count names its unit.
  Not the process line's "born" and "birth rule" for bands and cells of a
  network of rings of cells (9 November 2026), kept in that record's words.
- **Junction; parent.** In parity growth by the cubic study's joining rule
  (`CUBIC-FROM-A-KNOT-20261117-001`), a junction is one of the growth's
  parity knots, each placed by the rule on loose distinctions of earlier
  junctions and some fresh ones; its parents are the junctions it took a
  distinction from.
- **Parent step; holder step.** A parent step goes from a knot to one of its
  parents. A holder step goes from a knot to a knot that shares a distinction
  with it, across that distinction. Every parent step is a holder step; which
  holder steps are parent steps cannot always be recovered from what is built
  (lesson 9.3). Counts of parent steps count descent (lessons 8.7 and 9.4);
  counts of holder steps say how much of what is built a law's rule at a knot
  reads (lessons 8.1 and 9.3). Neither is steps apart, which counts
  co-knotted pairs of distinctions.
- **Offshoot.** A junction with exactly one parent: the rule gives a loose
  distinction no join wants a junction of its own
  (`FRESH-COUNT-20261118-001`). The literature's join-irreducible element.
- **Demand; surplus distinctions.** A junction's demand is the number of
  joins of the next round that take a distinction from it; its surplus
  distinctions are the fresh distinctions it has beyond its demand, and each
  becomes an offshoot (`FRESH-COUNT-20261118-001`).
- **Descent order; breadth.** The offshoots of a growth, one below another
  when the second descends from the first through parents; its breadth is
  the most offshoots none of which descends from another (the literature's
  width). The pattern the joining rule grows is the down-closed sets of this
  order (the literature's distributive lattice of ideals). Breadth is not the
  dimension: balls can grow more slowly than the breadth allows.
- **Start.** The few knots a growth begins from, some of which share
  distinctions, and nothing else (lesson 8.1). A study's number for a start
  gives only the order in which it was found. The intuition: the piece of one
  structure that the rounds read outward from.
- **Loose; live; dead knot.** In growth by the joining rule (lesson 8.1), a
  distinction of a junction is loose while no other junction holds it, so it
  is open. A junction or knot is live while it holds a loose distinction, and
  a **dead knot** is one that is not live: every one of its places is shared
  (lesson 8.2).
- **Cheapest growth.** Growth by the joining rule in complete rounds, in which
  each new junction adds as few fresh distinctions as it can: enough for the
  joins that will take from it in the next round, and enough to make it a knot
  of at least three places (lesson 8.1; `FRESH-COUNT-20261118-001`,
  assumptions A104 and A108). It was studied under parity; under not-all-equal
  the same rule gives the same counts wherever parity does not close, and
  where parity closes it goes on in two endless chains
  (`NAE-GROWTH-20261119-001`).
- **Group of three.** A join of the cheapest growth that takes one loose
  distinction from each of three junctions (lesson 8.1). A first group of
  three is three knots joined in pairs through three different knots, with no
  knot common to all three, and it is where the theorem's class ends (lesson
  8.2).
- **Stall; close.** A growth stalls when a round cannot be made, because some
  junction has too few loose distinctions, and it closes when no loose
  distinction is left (lesson 8.1). The intuition: the first of the four kinds
  of growth of lesson 8.2, in which nothing new forms. A growth jams when
  knots remain that owe more loose distinctions than they hold and no birth
  can be made, under a law in which a short knot does not stop the whole round
  (lessons 8.7 and 9.2).
- **Map of joins; unrolled map; cluster.** The map of joins of a growth has
  one member for each live knot, with the live knots that share a distinction
  with one knot grouped together, as the ones that can join through it, and one
  member attached to a knot for each of its leftover distinctions. The
  unrolled map is the same record with no way back: wherever a cycle would
  return, a fresh copy is used (the literature's universal cover). A cluster
  is a connected set of its members. Inside the theorem's class the junctions
  made in round t are exactly the clusters of t + 1 members that hold a knot
  (lesson 8.1). The intuition: the map says in advance who can join whom, so
  the growth is a count on it.
- **Endless chain; relay.** An endless chain is a chain of junctions, one more
  each round without end, where a knot keeps a leftover distinction and the
  law tops a junction up to three places. A relay is how a part of the map of
  joins that would finish goes on while another part grows: k junctions in the
  k-th round after, counted as two endless chains (lesson 8.2).
- **Ring; hung knot; leftover distinction.** A ring of knots is a cycle of
  knots, each sharing a distinction with the next and the last with the first
  (lessons 4.4 and 8.2). A hung knot shares distinctions with a single knot of
  a ring. A leftover distinction is an open distinction that a knot keeps
  beyond what its joins use (lesson 8.1); the growth records call it a spare,
  a word the guide keeps for distinction substitution.
- **Eddy.** The owner's word (18 November 2026, assumption A109): a cycle of
  knots that feeds its own growth, so that the count is multiplied by about
  the same rate each round. Going once around the cycle multiplies the count
  by its **lap weight** W, and the rate x solves W(1/x) = 1 (lesson 8.2). The
  intuition, in the owner's words: "eddies in a river", shared like library
  routines. The owner's "loops of logic" are read as these cycles; they are
  not the guide's loops (lesson 1.4).
- **Explosive growth.** The record's label for the kind of growth it cannot
  yet describe: where cycles of the map of joins overlap, the counts leap and
  no fixed rate has been found to fit (lesson 8.2). It is a label, not a
  defect. A growth **blows up** when its count grows faster than any
  polynomial, as eddies and explosive growth do, and blow-up is expected
  (assumption A110, lesson 8.3).
- **Partnered; runaway growth.** A set of live knots is partnered when they
  come in pairs of partners, each able to join every knot of the set but its
  partner (the literature's cocktail-party graph; for three pairs, the
  octahedron). Runaway growth: each round's count is about two to the power of
  half the one before (the literature's iterated exponential), as in a start
  whose live knots are partnered (lesson 8.2).
- **Generator; packet; release.** The owner's word generator (20 and 23
  November 2026): a start that keeps making separate things. In the record's
  test (assumption A125) a **packet** is a finite set of knots made in one
  round whose later members take every parent from the packet's own earlier
  members; it is **released** in the round from which that holds, which is
  about parents and not about a distinction becoming loose; a packet lasts
  when it has members in every later round; and a start is a generator when it
  releases infinitely many packets that last and share no member (lesson
  8.7). The growth records call the generator a source and a packet a
  product or a family. The literature's picture is the glider gun of Conway's
  Life, which makes one fixed pattern each time; under ordinary growth no start
  is known to keep releasing lasting packets of one fixed width, and in the
  class where every knot can be reconstructed from the start none can.
- **Fold of emergence.** The owner's phrase (23 November 2026, assumption
  A223), always written in full and in his words: a pattern that the rules make,
  where what it makes depends on another pattern, and that makes a pattern of
  its own,
  as he pictures DNA and intelligence. An interpretation. Under laws added by
  hand the record has cases in which what one made part builds differs between
  a run with another made part growing and a run with it barred, but none in
  which it differs with what the other is, or in which a part makes a pattern
  of its own from the other (lessons 8.7, 9.6, 10.1 and 10.3). It is not the
  two-fold of a two-fold weave, which counts knots, and the guide makes no
  claim about living things.
- **Copier.** The owner's word (24 November 2026: "a copier is a pattern the
  growth makes", assumption A244 and sub-goal B327; and "a 'copier'" in his
  inkling of the same evening, assumption A248). In the guide: a pattern the
  growth makes that meets a second made pattern and leaves two of the second.
  A copier is a pattern, never a law: the law (which knots join, what a new
  knot receives, what a short knot does) is supplied and named separately. A
  claim of a copier names the class of second patterns and, in the owner's
  words, whether "two of it" means "the same form, the same built structure,
  or the same values". The record has none. Not the part that copies itself
  (lesson 8.7), which takes nothing from another pattern and leaves two of
  itself, though its record's heading calls it "the copier"; and not the
  literature's replicator under HighLife, which also copies itself. The
  owner's inkling that no copier can be general is A248, a working premise
  (lesson 10.4).
- **Weaned; brood.** In the laws that make one birth at a time (lesson 8.1),
  a knot is weaned when none of its parents is still in the live roster: its
  parents have finished giving. The **brood** of a knot is the smallest set
  that holds it and, with each knot in it, every child of each of that knot's
  parents: the knots made alongside it. The intuition: a brood is one part's
  round, seen from the knots that round made.
- **Ancestral common knot; ancestor-taking.** A common knot of two members
  that is also a recorded ancestor of both and not the parent of both: the
  knot through which two sets of descendants are joined. The owner's phrase
  for it was "axis point", and afterwards perhaps "access point" (24 November
  2026, assumption A241). A **taking rule** is a rule added to a growth law
  under which a birth also takes a distinction that is already shared, by a
  supplied convention for which: rules R and Q take only what a parent holds,
  and the rule that takes from a knot the parent meets takes from no ancestor
  (lessons 10.0 and 10.3). **Ancestor-taking** is a law under which a birth
  also takes a distinction that an ancestor of one of its parents holds, so
  that the distinction gains a holder. Under the laws of lesson 8.1 a shared
  distinction has two holders; where a birth may take a distinction that is
  already shared, shared means held by two or more. In the study of such laws
  ([PARTS-MEET-AGAIN-20261124-001](research/PARTS-MEET-AGAIN-20261124-001/decision.md),
  computed, referee pending) such a knot was among the common knots of the
  members of two parts that had come apart and were one part again for 62
  pairs, and the only one for 6; it was always a start knot (lesson 10.3).
- **Course of a part; with-and-without test.** The **course** of a part X of
  the live roster after round s is what X and its descendants build, round by
  round: each birth whose parents all lie among them, with its parents, what
  it takes and the number of its fresh distinctions, and which sets of their
  members one knot meets, up to a renaming of the knots made after round s. A
  birth's demand is recorded separately and is not part of the course. The
  **with-and-without test** is the owner's test (by 24 November 2026, Pacific
  time: "run each start twice, once with the second part present and once
  without it. A part reads another when its course differs between the two
  runs") as one study measured it (assumption A246, a measure; the records'
  "paired test"). One start is grown under one law, and grown again with every
  usable loose distinction of a second part Y barred from round s, so that Y
  stays built and makes no birth, and X's course is compared between the two
  runs. Removing Y is the registered alternative, used only where it is
  defined; in the study of lesson 10.3 it was defined for 182 of 302 pairs and
  gave the same result for each. A masked run, in which no member of X or its
  descendants can join a member of Y or its descendants, is the study's check
  of whether a difference went through the two parts meeting (lesson 10.2).
  The test shows whether X's course differs with Y barred; it says nothing of
  what Y is. A course is not a history, which is one whole run.
- **Clock; tick.** A clock is anything in which one named event recurs and
  against which other changes are counted; each recurrence is a tick (lesson
  9.4). The guide always says which kind. A **supplied clock** is given by
  whoever runs a system: the update of every cell of the Game of Life at once
  (lesson 1.3), or a round applied to every live knot at once (lesson 8.1). A
  **made clock** is a pattern the growth builds from a supplied start in which
  the named event, a return or a release, recurs; the study names the event
  (assumption A150, a scaffold). "Made" speaks of the pattern only: the law,
  the start and whatever counts the ticks are named separately, and in the
  record so far whatever counts a made clock's ticks is supplied. A tick is
  the event, not the count of it. The owner's words: "Time doesn't have ticks"
  (by 18 November 2026, Pacific time); "what if 'time' is a device or pattern
  just like the other ones?" (23 November 2026, assumption A228).
- **Return; period.** A part of the live roster returns at a later round when
  the members then descending from it, a member that waits counting as its own
  descendant, include a part that is the same as it: the same up to a renaming
  that keeps each member's loose distinctions, usable and never used, and
  which sets of members one knot meets (lesson 8.7). It may be made of the
  same knots, which waited, or of new knots, and the study says which. A state
  returns when every distinction or cell again has its earlier value (lessons
  1.3 and 8.6). The **period** is the count from one return to the next,
  always with its unit: rounds, births, parent steps, updates or changes; a
  state of a harmony has its period in shifts (see Harmony). A release that
  recurs while each packet is larger than the last is not a return. Not the
  foundation's "native return artifact" and "causal return handoff", written
  in full, which are a runner's return of control.
- **Priority.** The owner's word (23 November 2026, assumption A229): "not
  really like a sequencer, but more like a priority system ... How often
  updates happen given some property". In the guide: a rule that says which of
  the parts or births that are ready goes first, by a named property of them
  (a part's number of members, the loose distinctions its members hold, the
  rounds its members have taken, a birth's age or kind), by stated chances, or
  in turn (lesson 9.5). One order of births taken by itself, as in a search
  over every order, is an order of births, not a priority. Which distinction a
  birth takes is not a priority. Every priority in the record so far is
  supplied.
- **Live roster.** What one round of the law reads: which junctions hold a
  loose distinction, how many, and which sets of them one junction meets
  (lesson 8.4). The growth records call it the growing end.
- **Three-way distance.** For three distinctions, the size of the smallest
  bond that holds all three (lesson 8.4).
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
- **Block; descent; finite-reader state.** In patterns placed by maps on
  addresses (lesson 4.8), the addresses one address is sent to by the maps form its
  orbit (the literature's word, as for a state under shifts; see Harmony). A **block**
  is a set of addresses at one level with their children one level down,
  holding the knots placed at that level whose members all lie in it; the
  block of an orbit holds every knot placed at the orbit, and blocks of
  orbits meet only a block and the one above it. A **descent** follows a
  block down the levels, each address extended by one letter, the letters
  eventually periodic (the literature's orbital Schreier graph along a
  rational point). A **finite-reader state** is a state at every depth whose
  value at each address a finite machine outputs after reading the address
  letter by letter (the literature's automatic sequence). The intuition: a
  block is a piece the pattern can be solved in, and a descent is how a few
  distinctions carry the top down without the rest of the level
  (`DIRECT-REACH-20261115-001`, 16 November 2026).
- **Pair projection; product; two-orbit bond; exposed; unexposed dependence.**
  The **pair projection** of two orbits is the projection of the allowed
  states onto them. It is a **product** when every pairing of the two
  orbits' own projections is allowed, so neither orbit says anything about
  the other. A **two-orbit bond** is a bond inside the two orbits that
  contains a distinction of each. An assignment of an orbit is **exposed**
  when some free set of the orbit's addresses takes its values in that
  assignment only. A dependence is **unexposed** when the pair projection is
  not a product but every missing pair has a side that is not exposed: the
  orbits depend on each other, but no bond inside them shows it, because one
  orbit's own constraint stands in the way. The intuition: a two-orbit bond
  is a bond that two orbits far apart hold between themselves alone, and an
  unexposed dependence binds them too, but only a larger set of addresses
  can show it (`KEEP-REACH-20261117-001`, 17 November 2026).
- **Stem.** For an orbit at one level and an orbit some levels below it, the
  stem of depth d is the upper orbit together with the lower orbit's
  ancestor orbits at the d levels below the upper one: the start of the way
  down from the top toward the lower orbit (the advisor's word). A bond inside
  the stem and the lower orbit, holding a distinction of each end, holds the
  top to the lower orbit, as a two-orbit bond does. Stems of depth 2 hold the
  top in three patterns (ten descriptions) where no bond inside two orbits does: their unexposed
  dependence shows once the orbits just below the top are held too
  (`CARRIER-20261117-001`, 17 November 2026).
- **Bracketing; bare bracketing.** A line (the one-order base) of n distinctions presented by the fewest betweenness knots,
  n − 2 of them, is presented exactly when its knots form a **bracketing**: every knot B(a, c, b) has c between a and b, its
  **halves** are the line's steps from a to c and from c to b, and each knot other than the **ends' knot** (the one holding
  both ends) lies directly within a half of exactly one other, while every half holds one knot directly within it or is a
  single step. The **bare bracketing** forgets which half: only which knot lies directly within which. Two knots are
  **step-disjoint** when they share no step, which is the same as neither lying within the other. The literature's bracketing,
  or rooted binary tree, drawn as a triangulation of a polygon rooted at a marked side; the bare one is the unlabelled rooted
  binary tree. The intuition: how the knots meet, read against the line, is a hierarchy of which knot lies within which, and the
  growth that reads which knots meet reads this hierarchy: a fill makes a knot's halves cross, and a second fill keeps two orders
  only when its knot is step-disjoint from the first or joins it to a knot it shares a pair with (`MEET-ORDERS-20261118-001`,
  18 November 2026).
- **Same way, other way.** For knots χ within ν within π of a bracketing, χ lies in ν **the same way** when it sits in ν at the
  same end as ν sits in π, and **the other way** otherwise. With the bare bracketing these choices make up the whole bracketing
  up to mirror image. The shared distinction of the line of five's three knots sits at an end when the chain lies the same way and
  next to an end when it lies the other way (`MEET-ORDERS-20261118-001`).
- **Odd set.** While no new distinction has added a state, each new distinction of a line takes, in every allowed state, the
  parity of an odd set of the line's distinctions: its odd set. The fill of three distinctions a < c < b is their parity (the
  advisor's parity form; `MEET-ORDERS-20261118-001`).
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
  | partnered set | 2k knots in pairs, each able to join every knot of the set but its partner | octahedron (k = 3), cross-polytope; the cocktail-party graph |
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
  | bracketing; bare bracketing; ends' knot | which knot of a fewest-knot presentation of a line lies directly within which half of which, from the knot holding both ends; the same forgetting the halves | triangulation of a polygon with a marked side, rooted binary tree; unlabelled rooted binary tree; the root |
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
  | loop | a logical structure that leaves a distinction open (lesson 1.4) | a cycle of a weave that no patch closes off: unfilled cycle; loop pairs: cycle pairs; a cycle of knots that feeds its own growth (the growth records' self-feeding loop): eddy |
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
  | distance | (unqualified, only in the owner's words: his founding premise, lesson 2.4, whose reach he has yet to settle) | the one touch of a knot: minimal contact-distance; read from the allowed states: bond distance; a count on the meeting pattern: steps apart; contacts along a route across time: counted length (A40), not the quantity THEORY.md's claim "Counted length" (1 November 2026) names, the logarithm of a count of states, read as a count; between states: Hamming distance, the literature's; along paths, or a metric: not yet built |
  | place | an argument position, as in three-place (lesson 3.2) | where a board holds a value: cell; the index of a stitch's members: lag (unlagged stitch, formerly "stitch at one place"); a block's position: its distinction (spare distinction, formerly "loose place") |
  | point | the owner's moving point, a state with a charge-like strength (his picture of learning), and otherwise the literature's | a variable: distinction |
  | line | (only in the owner's words, in the literature's names, such as the number line and a Fano line, and in a line of work, such as the process line and the learning line) | a three-place knot: knot; an open chain: chain; knots each a parent of the next: descent |
  | face | (the literature's only: a face of a map) | a knot of a weave: knot; a cycle a law closes: declared cycle |
  | flat | (only in the owner's "flat structure") | six knots at every distinction: six-regular; drawable without crossings: planar, the literature's |
  | balanced | (the doubling line's balanced stages, not used in the guide) | six knots at every distinction: six-regular |
  | two-sided | (none) | orientable |
  | side | (only in the owner's words: "the continuous edge of the loop", open to any number of others, lesson 7.3) | an edge of a drawn knot: the literature's; knots or bases "side by side": overlapping, or stitched (lesson 7.3), never side by side |
  | thread | (a thread of work, not used in the guide) | an endless chain of atoms: chain |
  | fold | (only in the owner's words: his folded, compressed structure, and his "fold of emergence" of lessons 8.7, 10.1 and 10.3, written in full; never the two-fold of a two-fold weave) | the direction the law does not lengthen: unlengthened shift |
  | copier | the owner's word: a made pattern that meets a second made pattern and leaves two of the second (lesson 10.4) | the two-knot part that makes two of itself (COPYING-PARTS-20261123-001's heading "The copier"): the part that copies itself |
  | source, product | (a source: where a citation or a distinction comes from; a product: of numbers) | a start that keeps releasing packets (the growth records' source): generator; what it releases (the records' product or family): packet |
  | ladder | (the literature's only, such as the n × 2 ladder graph) | three consecutive distinctions and every second one after them (ACROSS-FOLD-20261112-001's pre-registration): heddle; its rungs: the heddle's members after the three |
  | row, column | (a row: a sequence, as in steps apart and chain) | the indices of base 16's drawn frame: across-count, along-count |
  | spare | of a distinction of a block, in distinction substitution (lesson 7.3) | an open distinction a knot keeps beyond what its joins use (the growth records' spare): leftover distinction |
  | round | one step of forcing (lesson 5.3) or of growth (lesson 8.1), everything at once | going once around a cycle (the growth records' round-weight): lap weight |
  | growing end | (not used in the guide) | what one round of the growth law reads (the growth records' word): live roster |
  | clock | anything in which a named event recurs and against which other changes are counted: supplied or made, always said (lesson 9.4) | the process line's "own clock" and "conformal clock", a count of a supplied clock's ticks rescaled by doublings (assumption A56): a rescaled count of the automaton's updates |
  | step | (never alone as a unit of count; always a named kind) | co-knotted pairs between distinctions: steps apart (lesson 4.7); from a cell to a neighbouring cell: a board's step (lesson 4.6); from a knot to a parent: parent step; from a knot to a knot sharing a distinction with it: holder step; one update of every cell of an automaton: an update, a tick of its supplied clock; one birth or one part's round, or nothing: move |
  | lag | the shift of a stitch's member, counted up to a common addend (Stitch) | the process line's count of an automaton's updates since its first row (lesson 2.4's networks of rings of cells; assumptions A40, A41, A56): updates |
  | choice | a rule saying that when something exists, one of several things must (lesson 4.2) | which already shared distinction a birth takes (the study of parts that meet again's "the choice"; assumptions A231, A236, A245): which distinction a birth takes |
- **Older records.** Records written before 11 November 2026 use the older
  words, and a record whose checksum another record pins (a manifest, a result
  or a discovery) is never edited, so it keeps them. Read such a record with the
  table above: a line of a triple system is a knot, a point a distinction, an
  atom of a three-fold space a Fano piece, an atom of a knot space (a torus or
  Fano atom) a piece, a three-fold or knot space a
  three-regular contradiction or a drawn knot pattern, a contact where several
  knots meet a shared distinction, and a world of knots a base, weave or patch.
