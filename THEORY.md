# Theory

The contact-first program asks whether logic can build structure, such as
holes, paths and spaces, without assuming a space to start from. This page
states its thesis and its main claims. Each claim carries one label for how it
is supported, the date it was recorded or adopted, and links to its evidence
in the knotlab repository.

The [intuition guide](INTUITIONS.md) explains the first claims at length, and
the [list of results](RESULTS.md) gives every result with its proof. This page
connects them: what the program assumes, what it has shown, and what is still
open. AI agents (Anthropic's Claude and OpenAI's Codex) did most of this work
under John Cullen's direction. No human expert has reviewed it.

| Label | Meaning |
| --- | --- |
| **Premise** | A commitment of the thesis, or a definition John Cullen adopted. Adopted definitions are dated, and marked reopenable where the decision can be reopened |
| **Proved** | A complete proof is linked: a proof record (a `proof.md` with a `check.py` that recomputes its facts), or a short proof in the linked text |
| **Proved (Lean)** | Kernel-checked in [`lean/`](lean/) |
| **Proved (note)** | Proved in a note in [`notes/`](notes/) or in the record, with scripts that recheck its numbers |
| **Checked** | Computed. The claim states its scope: exhaustive within a bound, or the number of cases |
| **Conjecture** | Supported by the record but not proved |
| **Reading** | Our interpretation. It is not a theorem and nothing is proved from it |
| **Open** | A question the record leaves open |

A claim keeps the status it was recorded with. Where a later result corrects or
qualifies it, the claim says so. A *knot* here is always a logical knot, a
relation among variables, not a knot in space. Since the program is trying to
build space, the page names its own objects by distinctions, knots and counts,
and gives a spatial word only as the literature's name for an object, marked
as such, or for a picture it says is drawn; the
[glossary](INTUITIONS.md#glossary) maps each word to the literature's
(owner, 2026-11-11).

**What this does not claim.** The boundary between two-place and three-place
constraints is a boundary of what can be expressed. It is not the boundary
between P and NP, and nothing here addresses that question. Nothing here is
physics.

## Contents

1. [The thesis](#1-the-thesis)
2. [The first knot](#2-the-first-knot)
3. [Infinite systems](#3-infinite-systems)
4. [Composition and hardness](#4-composition-and-hardness)
5. [Space from a law](#5-space-from-a-law)
6. [Selection](#6-selection)
7. [Where new emergence is created](#7-where-new-emergence-is-created)
8. [Depth and counting](#8-depth-and-counting)
9. [Open questions](#9-open-questions)

## 1. The thesis

The commitments that define the program's question, from the
[foundational thesis](docs/FOUNDATIONAL_THESIS.md). Evidence can support or
challenge them, but no result replaces them silently.

### Logic comes before space

**Premise**

Logical identities and laws presuppose no space, position, direction,
distance or neighbourhood. Before emergence, logical things may be themselves,
but they do not yet exist relative to one another.

Evidence: [the thesis](docs/FOUNDATIONAL_THESIS.md#transcendental-logical-base)

### First emergence is a logical knot

**Premise**

Two independently witnessed loops are joined by one contact. The contact is
shared by identity, irreducibly joint, essential to both loops and persistent
under admitted maps, and erasing either loop destroys it as a contact. One loop
alone forms no topology. One complete knot is the first atomic logical
topology, and its single touch is minimal contact-distance: the smallest unit
of relative existence, with no magnitude, direction, coordinate or metric.
Paths, separation and extended distance come later, from networks of contacts.

Evidence: [the thesis](docs/FOUNDATIONAL_THESIS.md#emergence-atomic-topology-and-distance)

### The knot test K1–K3

**Premise** · 2026-10-19

Read a system of constraints as the set of joint states it allows. Witness
variables are quantified away, and no executor, scheduler or checker supplies
an input. Each loop contributes an open distinction, and erasing a loop forgets
it. A relation over the loops' distinctions and one contact is a knot when it
is constrained as a whole (K1), forgetting any one variable leaves the rest
unconstrained (K2), and some state is allowed (K3). John Cullen adopted this
test, with erasure read as forgetting, on 19 October 2026.

Evidence: [the decision](research/KNOT-FOUNDATION-20261019-001/canonical_correction_request.md), [the thesis](docs/FOUNDATIONAL_THESIS.md#canonical-knot-test), [proof](proofs/KNOT-FOUNDATION-20261019-001E/KNOT-FOUNDATION-20261019-001E-P001_forgetting_reading/proof.md), [Intuitions, lesson 2.1](INTUITIONS.md#21-the-knot-test)

### A shared variable is not a touch

**Proved (Lean)** · 2026-10-19

Two separate attachments A–c and B–c make c a common hub, not one touch
between A and B. In `(¬A ∨ c) ∧ (¬B ∨ c)`, forget B and A still forces c,
which fails K2. Shared identity alone never makes a contact.

Evidence: [`ForgettingKernel.lean`](lean/ForgettingKernel.lean) (`hub_not_knot`), [Intuitions, lesson 2.1](INTUITIONS.md#21-the-knot-test)

### Three places are the minimum

**Proved (Lean)** · 2026-10-19

No 2-CNF, with any number of witnesses, defines a knot, while three-literal
clauses with named intermediate results define every knot. So strict 3-CNF is
the smallest clause language that can state a knot. This concerns what can be
expressed, not how hard anything is to compute. The core is classical
(Schaefer 1978; Baker and Pixley 1975), and the reading is ours.

Evidence: [proof](proofs/KNOT-FOUNDATION-20261019-001E/KNOT-FOUNDATION-20261019-001E-P001_forgetting_reading/proof.md), [`ForgettingKernel.lean`](lean/ForgettingKernel.lean), [`KnotKernel.lean`](lean/KnotKernel.lean), [Intuitions, lesson 3.2](INTUITIONS.md#32-pairs-cannot-make-a-knot-three-places-can)

### Openness in an infinite system has a source

**Premise** · 2026-10-20 · reopenable

In an infinite system an open distinction may come from a finite loop or only
from the system's ends. A knot is native at a solution when each of its
variables is flipped there by some change of finitely many variables, and only
native knots carry emergence. Every claim about an infinite system records its
K1–K3 verdict and the source of each distinction. Finite systems are
unaffected.

Evidence: [the decision](research/HOLES-AT-INFINITY-20261020-001/canonical_correction_request.md), [the thesis](docs/FOUNDATIONAL_THESIS.md#canonical-knot-test)

### Witnesses may cancel

**Premise** · 2026-10-29 · reopenable

A second reading sits beside the existential one: witnesses may carry signs,
and a state is allowed when its signed witness sum is nonzero. The existential
reading stays canonical for K1–K3, and every result records both verdicts.

Evidence: [the decision](research/INTERFERENCE-20261029-001/canonical_correction_request.md), [the knot intuition, question 2](docs/KNOT_INTUITION.md#open-questions)

### Every coherent admissible base is co-real

**Reading**

Every internally coherent admissible base is treated as co-real, and nothing
selects one admissible base or branch as uniquely real. Co-reality is not
simultaneity, and no contact between different admissible bases is inferred.
The mathematics is compatible with this reading but does not prove it.

Evidence: [the thesis](docs/FOUNDATIONAL_THESIS.md#protected-modal-plurality-interpretation)

### Nothing chooses a meeting pattern

**Reading** · 2026-11-12

John Cullen, on 11 November 2026 (Pacific time): "Yes, there is no choice. I
feel like we keep going back to this being a choice. It isn't. It's just
random." Of our reality: "It is indifferent. It's is purely coincidental."
This is the co-reality reading applied to which knots share which
distinctions: no meeting pattern is selected, so one the record writes down is
one sample, not a gap to be closed, and the questions become which meeting
patterns are typical and which rare, and what a law reads off each. Since no
chances can be equal over infinitely many alternatives, typical and rare are
always relative to a declared weighting. His other realities are read as other
knot patterns of the same kind of logic, and bound realities as one larger
knot pattern, never as contact across bases. Whether a law forces its own
meeting pattern stays a separate question.

Evidence: [Intuitions, lesson 7.3](INTUITIONS.md#73-every-meeting-pattern-none-chosen), [the register, A15, A71 and A73](docs/ASSUMPTIONS.md)

## 2. The first knot

What a single binding is. The [intuition guide](INTUITIONS.md) explains each
of these claims with examples. Here each is stated once with its evidence.

### What a knot hides

**Proved** · 2026-10-21

Two loops and a contact have exactly 34 knots, in five classes, from the single
clause `¬A ∨ ¬B ∨ c`, the atom, to parity. Two-literal laws hide nothing from
their pairs, a knot hides at most one bit, and only parity hides a full bit. A
knot pattern with hidden witnesses hides at most one bit per independent
cycle, and only parity fills every cycle.

Evidence: [census proof](proofs/KNOT-FOUNDATION-20261019-001E/KNOT-FOUNDATION-20261019-001E-P001_forgetting_reading/proof.md), [measures](proofs/EMERGENCE-BITS-20261021-001A/EMERGENCE-BITS-20261021-001A-P001_emergence_measures/proof.md), [networks](proofs/EMERGENCE-BITS-20261021-001B/EMERGENCE-BITS-20261021-001B-P001_emergence_accounting/proof.md), [Intuitions, lesson 2.3](INTUITIONS.md#23-what-a-knot-hides)

### Pairwise rules make holes but never knots

**Proved (Lean)** · 2026-10-19

A system's free complex is the complex of sets of distinctions it leaves
free. A hole is a gap in that complex, and a knot is the smallest kind of
hole. Two-place rules can leave holes, but never a knot. Every simplicial
complex is the free complex of some system, so logic selects no space.

Evidence: [`ForgettingKernel.lean`](lean/ForgettingKernel.lean) (`no_two_cnf_defines_knot`), [`LoopNerve.lean`](lean/LoopNerve.lean) (`every_complex_is_a_nerve`), [proof](proofs/HOLES-COHOMOLOGY-20261019-001B/HOLES-COHOMOLOGY-20261019-001B-P001_loop_nerve/proof.md), [Intuitions, lesson 3.4](INTUITIONS.md#34-holes-and-knots)

### Requirement and choice are one knot read two ways

**Checked** · 2026-10-19

"A and B require c" becomes "c requires A or B" when false is read as
"exists". Of the 34 two-loop knots, 16 are a pure requirement under one reading
and a pure choice under the other, and the other 18 offer choices under both.
Knots never select: every variable of a knot takes both values.

Evidence: [decision note](research/KNOT-FOUNDATION-20261019-001/choice.md), [tests](tests/test_knotlab.py), [Intuitions, lesson 4.2](INTUITIONS.md#42-requirement-and-choice)

### Competing pairs make only the not-all-equal knots

**Proved (Lean)** · 2026-10-19

Read as rules that must all hold, pairs make no knot. Read as preferences,
where the allowed states are those that break the fewest, pairs make exactly
the four not-all-equal knots on three variables and none on four or more. With
hidden variables they make every knot. Whether least-violation states should
count as allowed is still open (section 9).

Evidence: [proof](proofs/KNOT-COMPETITION-20261019-001A/KNOT-COMPETITION-20261019-001A-P001_competing_pairs/proof.md), [`CompetitionKernel.lean`](lean/CompetitionKernel.lean), [Intuitions, lesson 4.3](INTUITIONS.md#43-knots-from-competing-pairs)

### Which knots remember a loop

**Proved (Lean)** · 2026-10-19

A ring of knots joined through witnesses keeps a constraint exactly when every
transfer along it is a permutation and an odd number of them swap, so it
composes into a knot or into nothing. Only parity keeps one full bit at every
length. Free contact records each loop separately. Contact with fixed points
binds loops instead, always into atoms, and a knot among k loops needs k + 1
witness values.

Evidence: [ring theorem](proofs/KNOT-LOOPS-20261019-001B/KNOT-LOOPS-20261019-001B-P001_ring_theorem/proof.md), [loop nerves](proofs/HOLES-COHOMOLOGY-20261019-001B/HOLES-COHOMOLOGY-20261019-001B-P001_loop_nerve/proof.md), [`RingKernel.lean`](lean/RingKernel.lean), [`LoopNerve.lean`](lean/LoopNerve.lean), [Intuitions, lesson 4.4](INTUITIONS.md#44-which-knots-remember-a-loop), [lesson 4.5](INTUITIONS.md#45-what-networks-of-loops-remember)

### The two/three boundary is a boundary of positivity

**Proved** · 2026-10-29

With nonnegative weights, no sum over hidden bits of products of pairwise terms
has a three-bit knot as its support, however many hidden bits it uses. With
signed weights, every three-bit knot is such a sum with one hidden bit. So
pairs never make a knot exactly as long as witnesses cannot cancel.

Evidence: [proof](proofs/INTERFERENCE-20261029-001A/INTERFERENCE-20261029-001A-P001_one_cancelling_witness_per_knot/proof.md)

### Two-place rules are logic, not topology

**Reading**

Logic first binds something that no part shows at the step from two-literal to
three-literal clauses, and emergence begins at the first such binding.
Distinctions are the material and atoms are the bonds. Every mechanism that
binds two loops, whether a witness chain, a gate or a circuit, looks from
outside like one of the 34 knots.

Evidence: [Intuitions, lesson 3.2](INTUITIONS.md#32-pairs-cannot-make-a-knot-three-places-can), [the knot intuition](docs/KNOT_INTUITION.md#projection-simulation-and-reality)

## 3. Infinite systems

A finite system has only finite loops. In an infinite system a distinction can
also be held open by infinity, and that possibility led to the source-aware
reading.

### Every bond is finite

**Proved** · 2026-10-19

No set of clauses, each naming finitely many variables, binds infinitely many
loops into one knot, even with infinitely many witnesses. The proof is the
compactness theorem. An endless chain of atoms is a tower of finite knots.

Evidence: [the knot intuition](docs/KNOT_INTUITION.md#endless-chains)

### Ends can open a knot as loops do

**Proved** · 2026-10-20

In infinite parity systems an open distinction comes from a finite loop or from
the system's ends, and no finite part or knot verdict tells the two apart. The
law decides: on the drawn square grid, Tseitin's vertex law has only
loop-supplied openness, while Ledrappier's law, whose rule ties three cells
drawn as a triangle, has no finite loop, and each such triple is a knot opened
by infinity.

Evidence: [ends](proofs/HOLES-AT-INFINITY-20261020-001B/HOLES-AT-INFINITY-20261020-001B-P001_ends_supply_openness/proof.md), [logical ends](proofs/HOLES-AT-INFINITY-20261020-001C/HOLES-AT-INFINITY-20261020-001C-P001_logical_ends/proof.md)

### Emergence depends on the law and on the world

**Proved** · 2026-10-20

Under the source-aware reading a linear law has native knots at every solution
or at none: on ℤ^d, exactly when it has positive entropy. Proper 3-colourings
have frozen solutions, where the star knot is not native, and dense flexible
ones, where it is. Native loops are not enough: the hard-core law is flexible
everywhere but has no knot.

Evidence: [linear laws](proofs/FROZEN-WORLDS-20261020-001B/FROZEN-WORLDS-20261020-001B-P001_linear_laws/proof.md), [frozen and flexible worlds](proofs/FROZEN-WORLDS-20261020-001C/FROZEN-WORLDS-20261020-001C-P001_frozen_and_flexible_worlds/proof.md)

### Native knots end where colourings freeze

**Proved** · 2026-10-20

On the d-regular tree with the broadcast colouring, the star knot "not all q
colours used" exists at every degree but is native only below the freezing
threshold, d = 6, 10 and 15 for q = 3, 4 and 5 (certified exactly). There its
nativity drops discontinuously from 1 to below 0.0011. Planted random regular
graphs matched the tree at every radius measured.

Evidence: [proof](proofs/FREEZING-KNOTS-20261020-001B/FREEZING-KNOTS-20261020-001B-P001_tree_freezing/proof.md)

## 4. Composition and hardness

How knots join into larger structure through shared distinctions, and where
computational hardness enters.

### Two knots on one distinction make a knot or a hub

**Proved** · 2026-10-21

Every law on bits is pairwise, frozen or transmitting. Two knots that share a
distinction compose into one knot exactly when they can force it to opposite
values; otherwise they form a hub. Lasting memory of loops holds exactly when
every polymorphism of the law is affine.

Evidence: [three regimes](proofs/BASE-THREE-20261021-001A/BASE-THREE-20261021-001A-P001_three_regimes/proof.md), [carriers](proofs/BASE-THREE-20261021-001B/BASE-THREE-20261021-001B-P001_regime_carriers/proof.md)

### When knots compose like cycles

**Proved** · 2026-10-21

A law's knots compose like cycles when any two that share a distinction still
leave a constraint once it is forgotten, as circuits of a matroid do. This
happens exactly when every range has a top, ties are bijections modulo the
tops, and one ternary polymorphism is Mal'tsev modulo the tops of the knot
ranges. The tops are then affine over finite fields, and on bits the laws whose
knots compose like cycles are exactly the affine ones. In such laws, networks
remember twisted first cohomology over a finite field, modulo the tops.

Evidence: [circuits](proofs/KNOT-CIRCUITS-20261020-001B/KNOT-CIRCUITS-20261020-001B-P001_circuit_composition/proof.md), [tops](proofs/CYCLE-TOPS-20261021-001B/CYCLE-TOPS-20261021-001B-P001_decided_on_tops/proof.md), [affine tops](proofs/AFFINE-TOPS-20261021-001B/AFFINE-TOPS-20261021-001B-P001_affine_tops/proof.md), [loop homology](proofs/LOOP-HOMOLOGY-20261021-001A/LOOP-HOMOLOGY-20261021-001A-P001_loop_homology/proof.md)

### The first native network

**Proved** · 2026-10-21

Two knots sharing one distinction in a law that composes like cycles pass the
contact-network gates under recodings, erasure, the law's own restrictions and
pp-definitions. Pinning and transports are the deciding conditions. In a
declared substrate the allowed states then fix contact adjacency, routes that
compose into single contacts, native separation and an extended bond distance.
They do not fix the drawing, and the law fixes no substrate.

Evidence: [gates](proofs/NATIVE-NETWORK-20261021-001A/NATIVE-NETWORK-20261021-001A-P001_network_gates/proof.md), [adjacency](proofs/NATIVE-NETWORK-20261021-001B/NATIVE-NETWORK-20261021-001B-P001_native_adjacency/proof.md)

### Hardness needs a hub

**Proved** · 2026-10-24

In a hub-free pattern of three-place knots that allows no state, every knot
whose removal keeps the pattern connected allows exactly half of its states.
So every native contradiction is a set of parity systems joined by forced
values, and hub-free patterns of every law are decided in polynomial time.
NP-hardness needs a hub as well as a knot. The classical neighbour is Tovey
(1984).

Evidence: [hubs carry hardness](proofs/NATIVE-HARDNESS-20261024-001A/NATIVE-HARDNESS-20261024-001A-P001_hubs_carry_hardness/proof.md), [only parity is hard](proofs/NATIVE-HARDNESS-20261024-001B/NATIVE-HARDNESS-20261024-001B-P001_only_parity_is_hard/proof.md), [native contradictions are linear](proofs/NATIVE-HARDNESS-20261024-001C/NATIVE-HARDNESS-20261024-001C-P001_native_contradictions_are_linear/proof.md)

### A knot cannot imitate a hub

**Proved** · 2026-10-25

No native gadget of any knot is an exact hub. The hub ratio of a gadget is
bounded by √3 for windable knots (given McQuillan) and by 1 for parity and
no-lone gadgets. For the six remaining knots, tree gadgets have hub ratio at
most 3.

Evidence: [settled knots](proofs/SOFT-HUB-20261024-001A/SOFT-HUB-20261024-001A-P001_hub_ratios_of_settled_knots/proof.md), [tree gadgets](proofs/SOFT-HUB-20261024-001C/SOFT-HUB-20261024-001C-P001_tree_gadgets_have_bounded_hubs/proof.md)

### Gadgets with loops cannot clone a bit

**Conjecture** · 2026-10-25

For gadgets with loops, adversarial search up to 40 knots never broke the
bound of 3, and often met it exactly, but it is not proved. Any proof must be
global: explicit two- and three-knot gadgets break every local strengthening.

Evidence: [what a proof must contain](proofs/LOOP-HUB-20261025-001B/LOOP-HUB-20261025-001B-P001_what_a_proof_must_contain/proof.md)

## 5. Space from a law

Logic allows every free complex, so whatever space there is must come from a
law. These claims ask what uniform local laws make natively, and what the
literature would draw it as.

### A law recognizes its graph; it does not create it

**Proved** · 2026-10-20

A law's allowed states carry a graph exactly when its knot matroid is graphic,
and a planar graph, which the literature draws on a sphere, when it is also
cographic, determined up to Whitney twists. Tutte's excluded minors decide
whether such a graph is present, not how the law was written. The mathematics
is classical (Tutte, Whitney).

Evidence: [proof](proofs/KNOT-SPACE-20261020-001B/KNOT-SPACE-20261020-001B-P001_recognized_space/proof.md)

### Hub-free knot patterns are the literature's pants decompositions

**Proved** · 2026-10-24

A pattern of three-place knots in which every shared distinction lies in
exactly two knots is, in the literature's terms, a pants decomposition of a
compact orientable surface: each knot a pair of pants, each open distinction a
boundary circle, and the genus the pattern's number of independent cycles.
Two-place relations glued this way make only chains and cycles. Exactly four
knots, counted on such patterns, depend only on the number of independent
cycles and the open distinctions: the parity and Fibonacci fusion rules, with
Verlinde dimensions 2, 5, 15, 50. Hub-free gadgets never create parity, so
memory must be present from the start. This partly overlaps known work
(Verlinde).

Evidence: [surfaces](proofs/SURFACE-GLUING-20261024-001A/SURFACE-GLUING-20261024-001A-P001_surface_gluing/proof.md), [no parity without hubs](proofs/SURFACE-GLUING-20261024-001B/SURFACE-GLUING-20261024-001B-P001_no_parity_without_hubs/proof.md)

### What native laws cannot see

**Proved** · 2026-10-29

Among the 32,768 symmetric bit laws on the edges of a triangulated
three-manifold, a declared substrate from the literature, only the trivial and
parity laws survive the 2–3 and 1–4 moves, so bits see a three-manifold only
through hubs, and then only through its mod-2 first cohomology. Among Boolean
knots glued natively, only parity is rebuilt by gadgets of its own copies. No
three-place knot picks an orientation at a distinction and no orienting
four-place knot survives, so native laws fix topology but neither orientation
nor scale.

Evidence: [mod-2 cohomology](proofs/HUB-DIMENSION-20261024-001A/HUB-DIMENSION-20261024-001A-P001_bits_see_mod2_cohomology/proof.md), [only parity is rebuilt](proofs/GEOMETRY-LAW-20261029-001A/GEOMETRY-LAW-20261029-001A-P001_only_parity_is_rebuilt_by_native_gadgets_of_its_copies/proof.md), [four places](proofs/GEOMETRY-LAW-20261029-001B/GEOMETRY-LAW-20261029-001B-P001_four_place_survivors_are_parity_and_chained_implications/proof.md)

### The not-all-equal knot's contradictions are built from Fano pieces

**Proved** · 2026-10-30

The patterns on which not-all-equal closes up, its three-regular
contradictions (earlier records: three-fold spaces), are the triple systems
that resist 2-colouring as a whole but not once their corner knot is removed.
Each is built from Fano pieces, the Fano pattern (the literature's Fano plane)
with one element removed, joined at three-edge cuts of the incidence graph by
Pfaffian glue made from planar pieces. When the glue is planar, the genus of
the incidence graph, the least genus of an orientable surface that carries it
in the literature's terms, equals the number of Fano pieces: in that drawing
each piece is one handle. The Fano pattern's own drawing is the literature's
seven-vertex torus. The tools are classical (tight cuts, Pfaffian
orientations). (Reworded on 2026-11-11: the first title said that the knot
"builds its own surfaces", but the surfaces are the literature's drawings of
the incidence graph, which the knot does not build.)

Evidence: [built from the Fano plane](proofs/THREEFOLD-SPACES-20261030-001A/THREEFOLD-SPACES-20261030-001A-P001_three_fold_spaces_are_built_from_the_fano_plane/proof.md), [pieces and glue](proofs/THREEFOLD-GRAMMAR-20261030-001A/THREEFOLD-GRAMMAR-20261030-001A-P001_fano_leaves_and_planar_glue/proof.md), [each piece a handle](proofs/THREEFOLD-SURFACES-20261030-001A/THREEFOLD-SURFACES-20261030-001A-P001_fano_atoms_are_handles/proof.md)

### The knot's amplitude and signs

**Proved** · 2026-10-30

Up to sign, the factor by which the knot reproduces itself on a three-regular
contradiction is a product over its pieces: 5 for each Fano piece, Tutte's
tree-trinity number for each planar piece of glue, and, for each non-planar
piece of glue, that piece's own amplitude, which depends on how the piece is
glued. When the glue is planar, every face of a least-genus map of the
incidence graph (the literature's drawing) has length 2 mod 4, so the knot's
own signs satisfy Kasteleyn's condition there.

*Qualification pending: [THREEFOLD-AMPLITUDE-20261030-001-D001](proofs/THREEFOLD-AMPLITUDE-20261030-001A/THREEFOLD-AMPLITUDE-20261030-001A-P001_five_per_handle_tuttes_number_per_planar_piece/proof.md) and this card's first version gave the factor as 5 per Fano piece times Tutte's number per planar piece on every three-regular contradiction. That holds when the glue is planar. A non-planar piece contributes its own amplitude ([one amplitude](proofs/THREEFOLD-AMPLITUDE-20261030-001C/THREEFOLD-AMPLITUDE-20261030-001C-P001_one_amplitude_for_every_non_colourable_cubic_system/proof.md), Corollary 5): 6 for three cubes glued along a square, and 13 or 14 for prisms of sizes 2, 3 and 3, depending on how they are glued.*

Evidence: [amplitude](proofs/THREEFOLD-AMPLITUDE-20261030-001A/THREEFOLD-AMPLITUDE-20261030-001A-P001_five_per_handle_tuttes_number_per_planar_piece/proof.md), [Kasteleyn signs](proofs/THREEFOLD-SPIN-20261030-001A/THREEFOLD-SPIN-20261030-001A-P001_kasteleyn_faces_and_even_spin_structures/proof.md)

### Counting on the knot's contradictions

**Proved (note)** · 2026-10-31

With one knot removed, the colourings of every three-regular contradiction can
be counted in polynomial time. Counting stays polynomial under twists that do not branch,
and becomes #P-hard once twists branch, even without signs and even on
Pfaffian braces.

Evidence: [note](notes/pfaffian-hypergraph-colourings/), [one knot removed](proofs/SEYMOUR-COUNT-20261030-001B/SEYMOUR-COUNT-20261030-001B-P001_polynomial_counting_on_seymours_cubic_bound/proof.md), [branched twists](proofs/SOFT-CROSS-20261031-001B/SOFT-CROSS-20261031-001B-P001_counting_under_branched_twists_is_sharp_p_hard/proof.md), [Intuitions, lesson 6.2](INTUITIONS.md#62-the-worlds-of-not-all-equal-knots)

### Signed knots reproduce themselves on self-similar substrates of every dimension

**Proved** · 2026-10-29

With signs, not-all-equal becomes a signed law, which the record calls a
standing wave, that reproduces itself exactly on every level-k Sierpinski
gasket, a substrate drawn in advance. The wave reproduces itself on every
Sierpinski d-simplex too, and one member of its family is a knot in every
dimension d ≥ 2, so knots reproduce themselves exactly on drawn self-similar
substrates whose dimension, in the literature's count, rises to d. On drawn
two-dimensional triangulations under shared subdivision, by contrast, only
parity reproduces itself with a knot. (Reworded on 2026-11-11: the first
version said that signed knots "build" self-similar space, but the gaskets and
simplices are drawn in advance, and what is proved is that the law reproduces
itself on them.)

Evidence: [gaskets](proofs/SIGNED-GASKETS-20261029-001A/SIGNED-GASKETS-20261029-001A-P001_signed_not_all_equal_reproduces_itself_on_every_gasket/proof.md), [simplices](proofs/SIMPLEX-GASKETS-20261029-001A/SIMPLEX-GASKETS-20261029-001A-P001_the_standing_wave_reproduces_itself_on_every_sierpinski_simplex/proof.md), [shared subdivision](proofs/SHARED-SUBDIVISION-20261029-001A/SHARED-SUBDIVISION-20261029-001A-P001_which_knots_reproduce_themselves_under_shared_subdivision/proof.md)

### Native gluing reads as two-dimensional topology

**Reading**

Hub-free gluing makes what the literature draws as surfaces, and bits see more
only through hubs. Read natively, what hub-free gluing makes is
two-dimensional topology in the literature's sense: each Fano piece of a
not-all-equal contradiction adds one handle to its incidence graph's drawing,
while the native laws found so far fix neither orientation nor scale. How the
knots meet is supplied with the gluing, not chosen by the law (A51, A64).
(Reworded on 2026-11-11: the reading first said that "the space a law builds is
two-dimensional topology" and that the knot "builds one handle per Fano atom";
later records show that how knots meet is an input the law does not supply,
`NAE-SURFACE-20261111-001`.)

Evidence: [the knot intuition, question 9](docs/KNOT_INTUITION.md#open-questions)

## 6. Selection

A law selects, in the sense the records call mutual selection, when the
systems on which it fails are non-empty and recognisable while counting its
worlds stays hard in general. These claims ask which laws select, and how the
contradictions a law selects fit together.

### Selection is special to three places

**Proved** · 2026-11-01

Unless NP-complete problems are polynomial, not-all-equal is the only
three-place knot that selects: parity is affine, the clause never fails, and
the two pinning knots have coNP-complete failures. On plain systems,
unconditionally, it is the only knot that can fail. Of the twenty kinds of
four-place knot, every kind that fails on small 4-regular systems builds
equality and is NP-complete on 4-regular systems. So, under the same
assumption, a selecting four-place knot would have to be one of five weak
kinds, none of which failed in any search.

Evidence: [three places](proofs/PINNING-20261031-001C/PINNING-20261031-001C-P001_the_knot_is_the_only_law_with_mutual_selection/proof.md), [value-free four-place laws](proofs/FOUR-PLACE-20261031-001D/FOUR-PLACE-20261031-001D-P001_no_value_free_four_place_law_has_mutual_selection/proof.md), [every four-place knot](proofs/FOUR-PREFER-20261101-001D/FOUR-PREFER-20261101-001D-P001_mutual_selection_at_four_places/proof.md)

### How the parts of a knot's contradiction meet

**Proved** · 2026-11-01

Across every nontrivial 2-edge cut of the incidence graph of a knot's
contradiction, one side accepts exactly equality and the other exactly
disequality: two-place parity, with no hub. Across every nontrivial 3-edge
cut, the side of the cut's distinction accepts an antipodal pair and the side
of its knot the complement: a knot against a hub, up to signs. If both
sides of a cut accept knots, the cut has two edges, so three-place emergence
never passes between parts without a hub. A route through Fano pieces carries its
length mod 2, and a route through a hub carries nothing more. These are routes
of a declared substrate, not native paths of contacts.

*Qualification pending: [KNOT-COMPOSE-20261101-001-D001](proofs/KNOT-COMPOSE-20261101-001A/KNOT-COMPOSE-20261101-001A-P001_knots_spaces_compose_only_through_hubs/proof.md) states that the knot's contradictions (its spaces, in the record's earlier word) meet only through hubs, exactly as not-all-equal against equality. That is false at 2-edge cuts, where parts meet as two-place parity, and exact only up to signs at 3-edge cuts. This card states the corrected result.*

Evidence: [two kinds of interface](proofs/NATIVE-PATHS-20261101-001A/NATIVE-PATHS-20261101-001A-P001_two_kinds_of_interface/proof.md), [routes](proofs/NATIVE-PATHS-20261101-001B/NATIVE-PATHS-20261101-001B-P001_native_routes_and_separation_without_length/proof.md), [knot meets knot](proofs/NATIVE-PATHS-20261101-001C/NATIVE-PATHS-20261101-001C-P001_knot_meets_knot_only_pairwise/proof.md)

### Selection and cycle-like composition exclude each other

**Proved** · 2026-11-01

A Boolean law with a knot whose knots compose like cycles is affine, so its
count is 2^(n−r) or 0 and it cannot select. Each of the five weak four-place
kinds has a knot with a forcing place, and two copies sharing that place form a
hub, so none of them composes like cycles either.

Evidence: [proof](proofs/SELECT-COUNT-20261101-001A/SELECT-COUNT-20261101-001A-P001_selection_and_cycle_like_composition_exclude_each_other/proof.md)

### Counted length

**Proved** · 2026-11-01

Across every nontrivial 2- or 3-edge cut of a knot's contradiction, each side
has one count, and the two counts multiply to the knot's amplitude. So counted
length, the logarithm of the count, adds up over the decomposition: log 5 per
Fano piece plus the logarithm of each glue piece's amplitude, which for a planar piece is
Tutte's tree-trinity number. It is a measure on the routes of a substrate, not
a native extended distance.

*Interpretation pending: whether counted length is a native magnitude has not been decided; read it as a count, not a distance.*

*Qualification pending: the record gives the glue's part as its tree-trinity logarithm. That holds when the glue is planar; a non-planar glue piece adds the logarithm of its own amplitude, which depends on how it is glued (see THREEFOLD-AMPLITUDE-20261030-001B).*

Evidence: [proof](proofs/SELECT-COUNT-20261101-001B/SELECT-COUNT-20261101-001B-P001_counted_length_is_a_measure/proof.md)

### With more values, a law can compose, select and keep emergence

**Proved** · 2026-11-01

On two values, composing like cycles rules out selection. With more values it
does not: doubling a value keeps a law's failures and circuits but makes its
count #P-complete, so blurred parity and blurred ℤ3 compose like cycles, fail
recognisably and count hard. Blurred signed ℤ4 on five values does all this
and also keeps knots inside the contradictions it selects, below its top
layer.

Evidence: [blurring](proofs/BEYOND-TWO-20261101-001B/BEYOND-TWO-20261101-001B-P001_blurring_makes_counts_hard/proof.md), [keeping emergence](proofs/RIGID-SELECTION-20261101-001C/RIGID-SELECTION-20261101-001C-P001_composition_with_emergence_keeping_selection/proof.md)

### The selection note

**Proved (note)** · 2026-11-01

A five-page note, *Native selection, and why three places*, states these
results in standard vocabulary: which couplings make counting easy on the
knot's failing systems, why not-all-equal is the only three-place law that
selects, why parity's failures are local, what happens at four places, and how
the failing systems compose. A replay reruns the sixteen checks it cites, and
separately written code recomputes nine of its claims. It has not been
externally reviewed.

*Erratum pending: abstract item 5, Section 6 and Theorem 12 say the knot's spaces (its contradictions) compose only through hubs, which is false at 2-edge cuts (see NATIVE-PATHS-20261101-001).*

Evidence: [note folder](proofs/SELECTION-NOTE-20261101-001/SELECTION-NOTE-20261101-001-P001_note/)

## 7. Where new emergence is created

On a three-regular contradiction the knot fails: there is no colouring.
Removing a knot leaves colourings, and the removal can create knots among what
remains that were not there before. These claims ask where creation happens
and whether it reads the contradiction's Fano pieces, which the literature's
drawing shows as handles. In the linked records a line is one of the
contradiction's knots, a point one of its distinctions, in the Fano plane's
words, and a handle or an atom is a Fano piece.

### Creation happens only near Fano pieces

**Checked** · 2026-11-03

On the census contradictions with planar glue and 24 further such
contradictions, no removal on a planar side created a knot across the opened
cut (2,172 removals). New knots appeared only where the gluing knot lies on a
Fano piece, or where the removal opens a Fano piece attached at a distinction,
which then creates at gluing knots of the planar glue out to bond distance 5.

Evidence: [planar sides](proofs/HANDLE-EMERGENCE-20261102-001A/HANDLE-EMERGENCE-20261102-001A-P001_a_planar_removed_side_creates_nothing/proof.md), [how a Fano piece creates](proofs/HANDLE-EMERGENCE-20261102-001B/HANDLE-EMERGENCE-20261102-001B-P001_how_a_handle_creates/proof.md), [where creation happens](proofs/HANDLE-LOCALITY-20261103-001B/HANDLE-LOCALITY-20261103-001B-P001_where_creation_happens/proof.md)

### On planar glue, selection is a matching of knots to faces

**Proved** · 2026-11-02

Draw the planar glue's incidence graph in the plane, as the literature does,
and give it Kasteleyn signs. A solution then makes each knot skip the
distinction opposite its odd distinction, and every face of the drawing hold an
odd number of skipped distinctions, so Euler's count of faces forces a planar
contradiction to fail. After a removal, the solutions are the perfect
matchings of the other knots to the faces off the removed knot. These matchings
carry integer heights that form a discretely convex set, so on a planar side
every pinned knot on three distinctions through the hub is generated, whatever
the far side. A crossing knot that one port separates
is a 2-sum of its two sides, or tie-equivalent to a one-sided circuit. Heights
of planar matchings (Thurston, Propp) and discrete convexity (Murota) are
classical.

Evidence: [faces](proofs/HANDLE-EMERGENCE-20261102-001C/HANDLE-EMERGENCE-20261102-001C-P001_why_a_planar_side_cannot_create/proof.md), [access lemma](proofs/PLANAR-THEOREM-20261102-001A/PLANAR-THEOREM-20261102-001A-P001_the_access_lemma_by_discrete_convexity/proof.md), [one-port 2-sums](proofs/PLANAR-THEOREM-20261102-001B/PLANAR-THEOREM-20261102-001B-P001_knots_separated_by_one_port_are_two_sums/proof.md)

### Which knots an opened Fano piece reaches

**Proved** · 2026-11-03

A route criterion decides which gluing knots an opened Fano piece reaches.
With the piece attached at a distinction of planar pieces and opened by the
removal, the new knots are exactly the candidate knots that no route through
the gluing knot's distinctions generates. So creation depends on the planar
piece only through its transfer.

Evidence: [route criterion](proofs/HALO-FORCING-20261103-001A/HALO-FORCING-20261103-001A-P001_the_route_criterion/proof.md)

### The halo runs along the faces opposite the Fano piece

**Checked** · 2026-11-03

A port is odd on its knot exactly when that knot takes the single skip of the
drawing's face opposite the port (proved). With the Fano pattern as the piece,
every knot reached beyond bond distance 3 lay on a face opposite the
attachment distinction, at all 126 distinctions tested.

*Qualification pending: at a junction, where a ladder arm meets a grid, the halo leaves these faces ([FACE-CLAIM-20261103-001-D003](proofs/FACE-CLAIM-20261103-001C/FACE-CLAIM-20261103-001C-P001_the_frozen_region/proof.md)), so the face law fails there as stated. It holds again after reduction, once sides beyond a 3-edge cut that hold neither the handle nor the gluing line are collapsed ([STRIP-RELAY-20261103-001-D001](proofs/STRIP-RELAY-20261103-001A/STRIP-RELAY-20261103-001A-P001_heights_and_reduction/proof.md)). That also qualifies FACE-CLAIM's refutation of the law.*

Evidence: [opposite faces](proofs/PHASE-HALO-20261103-001A/PHASE-HALO-20261103-001A-P001_opposite_faces_carry_the_halo/proof.md), [the frozen region](proofs/FACE-CLAIM-20261103-001C/FACE-CLAIM-20261103-001C-P001_the_frozen_region/proof.md)

### Rigid strips relay a Fano piece, one way

**Checked** · 2026-11-04

In planar glue drawn as strips and grids, as the records draw it, a rigid strip
relays an opened Fano piece's creation into the next grid from every distance,
while a liquid grid screens it within three steps. Relays act as wires:
aligned stations repeat them without loss, hubs broadcast them, and no relay
ever creates upstream of the piece's own part of the glue. Exact creation maps
confirm this on small contradictions.

Evidence: [strips](proofs/STRIP-RELAY-20261103-001C/STRIP-RELAY-20261103-001C-P001_rigid_strips_relay_a_handle/proof.md), [arc signals](proofs/RELAY-NET-20261104-001A/RELAY-NET-20261104-001A-P001_arc_signals_and_repeaters/proof.md), [broadcast](proofs/RELAY-NET-20261104-001B/RELAY-NET-20261104-001B-P001_broadcast_depth_and_bypasses/proof.md)

### Native selection counts and locates Fano pieces

**Checked** · 2026-11-04

Whether a removal creates at a gluing knot depends only on the Fano pieces
holding the two knots (proved for pieces attached at a distinction). When
planar glue separates the pieces, the knots outside a largest creation-free
set fall into one part per piece, in 416 of 420 contradictions. So native
selection counts the Fano pieces, the literature's handles, and finds where
they are; touching pieces merge.

Evidence: [splitting by piece](proofs/NATIVE-GENUS-20261104-001A/NATIVE-GENUS-20261104-001A-P001_the_creation_map_splits_by_atom/proof.md), [counting the pieces](proofs/NATIVE-GENUS-20261104-001B/NATIVE-GENUS-20261104-001B-P001_counting_and_locating_handles/proof.md)

### The two-bit screening lemma

**Proved** · 2026-11-06

An intact Fano side attached at a knot acts as that knot for creation, as it
does for solutions: it never removes creation, and one new distinction in one
new knot never adds any. Creation is decided at the gluing knot in two rounds,
proved by reducing the closure to local configurations and checking all
348,376,032 of them. One knot is the exact limit: a distinction in two or three
new knots can create.

Evidence: [no loss](proofs/TWO-BIT-SCREEN-20261105-001A/TWO-BIT-SCREEN-20261105-001A-P001_hidden_points_and_the_two_bit_screening_lemma/proof.md), [two rounds](proofs/PENDANT-LINE-20261106-001A/PENDANT-LINE-20261106-001A-P001_creation_is_decided_at_the_gluing_line/proof.md), [one new knot](proofs/PENDANT-LINE-20261106-001B/PENDANT-LINE-20261106-001B-P001_one_new_line_never_adds_creation/proof.md)

### Native creation reads the tree of Fano pieces

**Proved** · 2026-11-06

In every contradiction built from Fano pieces alone, each piece's knots create
at one another, and a knot receives creation from a removal in another piece,
at any distance, exactly when it touches its piece's cut facing the removal. A
chain of pieces carries one of 47 finite profiles from cut to cut, and the
receiving piece alone decides. When every piece has at most four cuts,
creation alone recovers the pieces and every cut with its direction. An
earlier rule that counted pieces by their sources holds up to five pieces and
fails at six.

Evidence: [touching rule](proofs/CHAIN-TRANSFER-20261106-001A/CHAIN-TRANSFER-20261106-001A-P001_creation_along_chains_of_every_length/proof.md), [the source rule fails](proofs/CHAIN-TRANSFER-20261106-001B/CHAIN-TRANSFER-20261106-001B-P001_the_source_rule_on_larger_trees/proof.md), [reading the tree](proofs/CHAIN-TRANSFER-20261106-001C/CHAIN-TRANSFER-20261106-001C-P001_reading_the_tree_from_creation/proof.md), [pieces are blocks](proofs/BRACE-TREE-20261105-001A/BRACE-TREE-20261105-001A-P001_creation_inside_an_atom_and_across_a_cut/proof.md)

### Creation at a Fano piece is decided by its cut

**Proved** · 2026-11-06

For a removal beyond one of a Fano piece's cuts, whether it creates at a knot
of the piece depends only on the patterns the removal's side allows on that
cut's three ports. This was proved over every port relation and every deeper
relation.

Evidence: [proof](proofs/GLUE-READ-20261106-001A/GLUE-READ-20261106-001A-P001_creation_is_decided_by_the_receiving_cut/proof.md)

### Through planar glue, whether creation occurs is not enough

**Checked** · 2026-11-06

On 191 contradictions, the touching rule fails only where planar glue
constrains a cut. A two-stage rule reads the Fano pieces of every census
contradiction and of 57 of 80 random glued ones. In 15 random contradictions,
knots of two pieces that meet one planar piece of glue cannot be told apart by
whether creation occurs, though which far side creates still separates them.

Evidence: [what glue does](proofs/GLUE-READ-20261106-001B/GLUE-READ-20261106-001B-P001_what_plane_glue_does/proof.md), [reading the pieces](proofs/GLUE-READ-20261106-001C/GLUE-READ-20261106-001C-P001_reading_the_atoms_through_glue/proof.md)

### No space is assumed

**Reading**

Directions are which side of a cut lost a distinction, touching is incidence,
and what the literature's drawing shows as a handle is a set of knots seen
together. Native selection picks out emergence exactly where the parts fail to
meet at a gluing knot. Every notion in this section is a relation among knots;
none assumes a space.

Evidence: [the knot intuition, question 9](docs/KNOT_INTUITION.md#open-questions)

## 8. Depth and counting

How much of a knot pattern an observer must hold to see a hidden bit, and
where counting worlds becomes hard.

### Hidden bits have depth

**Proved (note)** · 2026-10-20

A charge pattern that allows nothing looks consistent in every small window. Over every
field of characteristic other than 2, the Nullstellensatz degree of its Tseitin
formula, written clause by clause, equals the graph's toggle width, which is
cutwidth + 1 at maximum degree three. Reasoning mod 2 sees the hole at once.

Evidence: [note](notes/tseitin-nullstellensatz-degree/), [toggle width](proofs/DEEP-HOLES-20261020-001B/DEEP-HOLES-20261020-001B-P001_charge_depth/proof.md), [cutwidth](proofs/CUTWIDTH-DEPTH-20261020-001B/CUTWIDTH-DEPTH-20261020-001B-P001_toggle_cutwidth/proof.md), [Intuitions, lesson 5.2](INTUITIONS.md#52-how-deep-a-hole-is)

### Depth in other proof systems

**Proved** · 2026-10-20

In the ±1 encoding, the polynomial calculus degree of Tseitin formulas lies
between ⌈cvw/2⌉ and ⌊cvw/2⌋ + 1 for carving width cvw, and sum-of-squares
degree is the carving width up to 4. On graphs built from short cycles,
refutations need size 2^Ω(treewidth) in resolution and polynomial calculus,
and 2^Θ(treewidth) in sums of squares and Sherali–Adams. Refutations that never
forget a variable where the hole must lie need size 2^Ω(treewidth); that every
resolution refutation does, at bounded degree, is equivalent to Urquhart's
conjecture, which is open.

Evidence: [polynomial calculus](proofs/PC-DEGREE-20261020-001B/PC-DEGREE-20261020-001B-P001_half_carving_width/proof.md), [short cycles](proofs/CELL-SIZE-20261020-001B/CELL-SIZE-20261020-001B-P001_cell_theorem/proof.md), [sums of squares](proofs/SOS-SIZE-20261020-001B/SOS-SIZE-20261020-001B-P001_tangle_pseudo_expectation/proof.md), [Urquhart](proofs/URQUHART-TSEITIN-20261020-001B/URQUHART-TSEITIN-20261020-001B-P001_hole_faithful/proof.md)

### Emergence is countable exactly when it is topological

**Proved** · 2026-10-24

Gluing topologically is the generalized Fibonacci-gate recurrence, so the four
knots whose count depends only on a hub-free pattern's cycles count every such
pattern by closed formulas, while the other 30 knots are #P-hard to count,
given Backens's dichotomy for Holant problems.

Evidence: [proof](proofs/NATIVE-COUNTING-20261024-001A/NATIVE-COUNTING-20261024-001A-P001_countable_exactly_when_topological/proof.md)

### Counting maps from the groups of classical knots can be hard

**Proved (note)** · 2026-10-26

Counting homomorphisms from the group of a 3-manifold, a classical object, to
a finite group counts the worlds of a group law. Unless every #P function is
computable in polynomial time, Rowell's 2009 conjecture fails: on links already
for S₃, on classical knots for S₄, and for some groups of Fitting height
two. For Heisenberg-type
groups the note proves an exact dividing line.

Evidence: [note](notes/knot-group-counting/), [S₄](proofs/BOUNDED-H1-20261025-001A/BOUNDED-H1-20261025-001A-P001_s4_colourings_of_knots_are_sharp_p_hard/proof.md), [Heisenberg-type groups](proofs/COPRIME-CLASS2-20261026-001Z/COPRIME-CLASS2-20261026-001Z-P001_epic_closure/proof.md), [Intuitions, lesson 6.3](INTUITIONS.md#63-counting-on-classical-3-manifolds)

### Hardness as a three-way interaction

**Reading**

In the Heisenberg families, hardness appears exactly when the twisted
obstruction joins three nontrivial characters at once, which Borromean
surgeries supply, and everything pairwise stays countable. This echoes K2, but
it is a statement about counting: the knot test cannot tell hard groups from
easy ones, since every group law is constrained as a whole and free in every
pair.

Evidence: [Intuitions, lesson 6.3](INTUITIONS.md#63-counting-on-classical-3-manifolds)

## 9. Open questions

What the record leaves open.

### Space from a law

**Open**

Which uniform, local law, not written on a space in advance, gives a meeting
pattern of knots that looks like a space of low dimension, with geometry as
well as topology? Native laws found so far fix
topology but neither orientation nor scale, and see a drawn three-manifold
only through hubs.

Evidence: [the knot intuition, question 9](docs/KNOT_INTUITION.md#open-questions), [Intuitions, lesson 7.2](INTUITIONS.md#72-open-questions)

### Reading every three-regular contradiction

**Open**

Native creation reads the Fano pieces and the directed tree of contradictions
built from Fano pieces, but through planar glue whether creation occurs is not
enough. Still open: a rule that uses which far side creates, the relation a
planar piece presents, derived from the faces of its drawing, and handles in
the literature's drawing that are not Fano pieces.

Evidence: [closure of the latest epic](proofs/GLUE-READ-20261106-001Z/GLUE-READ-20261106-001Z-P001_epic_closure/proof.md)

### Competition

**Open**

Pairwise preferences that cannot all hold leave the not-all-equal knot among
their least-violation states. Should least-violation states count as
allowed? Both readings are mapped. The strict reading keeps the verdict
independent of presentation; the competition reading needs a declared measure
of violation. The decision is John Cullen's.

Evidence: [the knot intuition, question 10](docs/KNOT_INTUITION.md#open-questions), [Intuitions, lesson 7.2](INTUITIONS.md#72-open-questions)

### Dynamics, limits and witnesses

**Open**

Are loops better modelled as processes whose outputs over time are the data,
and does the static test survive that change? Does the program need a declared
limit rule that binds infinitely many loops into one contact? What may a
witness report about a loop's interior, and which structures count as native
loops?

Evidence: [the knot intuition, questions 1, 2, 4 and 7](docs/KNOT_INTUITION.md#open-questions)

### Typical and rare meeting patterns

**Open** · 2026-11-12

Grow a knot pattern one knot at a time under a declared random process. Its
outcome, after John Cullen's three: it resolves to nothing, it ends (allows
states for a while, then none), or it goes on forever. Under not-all-equal
with knots placed uniformly at random, the end comes near 2.1 knots per
distinction (known; the exact value for three-place knots is open), and the
contradiction that ends a large pattern is never local (known). Open: what the
law reads off the patterns that live (ties, faithfulness, bond distance
against steps apart), what other growth processes do, and whether the law's
own quantities approach a limit as a pattern nears its end, which John Cullen
expects ("similar to limits", "relativity, but for logic"). A census is
pre-registered.

Evidence: [Intuitions, lesson 7.3](INTUITIONS.md#73-every-meeting-pattern-none-chosen), [the census's pre-registration](research/RANDOM-FATES-20261112-001/preregistration.md)

### Bases within bases

**Open** · 2026-11-12

John Cullen: "each boolean variable could be its own micro infinite series of
logic, that's bound to others". Tested one way (referee pending): each
distinction an inner harmony, each outer knot a stitch of the inner harmonies
at every place. Then the level above allows exactly the outer states, at every
level, and never ends (proved: every outer state lifts); only the alternation
0101… is one distinction exactly; forced values only multiply the seed's, and
a drawn three-copy nesting forces nothing to level 7. Open: nesting by
substitution, and influence that does not shrink with depth.

Evidence: [bases within bases](research/BASES-WITHIN-20261112-001/bases_within.md), [Intuitions, lesson 7.3](INTUITIONS.md#73-every-meeting-pattern-none-chosen)

### The weak four-place kinds

**Open**

Do any of the five weak kinds of four-place knot ever fail? None failed in any
search. Unless NP-complete problems are polynomial, a four-place knot that
selects would have to be one of them.

Evidence: [every four-place knot](proofs/FOUR-PREFER-20261101-001D/FOUR-PREFER-20261101-001D-P001_mutual_selection_at_four_places/proof.md)
