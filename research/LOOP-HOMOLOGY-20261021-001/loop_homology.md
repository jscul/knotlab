# Do holes behave like finite-field homology modulo the tops?

Epic `LOOP-HOMOLOGY-20261021-001`, closed 2026-10-21.

## The question

After the tractability epic, the owner asked for three things:
- **State and test a unified claim:** group-like knots are exactly the ones that
  both remember loops and compose like cycles. Then holes behave like homology
  over finite fields modulo the tops.
- **Tie it to two earlier epics:**
  - `KNOT-LOOPS-20261019-001`: only group-like knots remember a loop;
  - `HOLES-COHOMOLOGY-20261019-001`: one H¹ class per loop.
- **Say what it implies** for contact networks.

**The evidence:** [the proof](../../proofs/LOOP-HOMOLOGY-20261021-001A/LOOP-HOMOLOGY-20261021-001A-P001_loop_homology/proof.md),
with its [checks](../../proofs/LOOP-HOMOLOGY-20261021-001A/LOOP-HOMOLOGY-20261021-001A-P001_loop_homology/result.json).

## The verdict

**As stated, the claim holds for two values and fails beyond.** For a Boolean
knot, five properties coincide:
- it is group-like;
- it keeps a lasting record of a loop;
- no product of its transfers is full;
- it composes like cycles;
- it is parity.

This holds in all 9,108 links of Boolean knots on three and four variables.
With more values, the three properties come apart.

| Knot | Group-like | Lasting record | Composes like cycles |
| --- | --- | --- | --- |
| 3-nets of Z₆ and S₃ | yes | yes | no: ties modulo 2 and 3, or Thomsen's configuration doubled |
| dressed parity (parity on first coordinates, free second coordinates) | no: group-like only modulo its tops | yes, one bit at every length | yes |
| x + y + z = 0 over F₃ | yes | only in the lim sup: odd rings forget | yes |
| 3-net of Z₄ | yes | yes, Z/4 classes | yes, but Z/2 modulo the tops |

**The corrected claim has three parts.**
1. **Remembering a loop needs contact that is group-like modulo blocks**
   (Theorem 1).
   - A knot's transfers either have a full product, and its rings forget, or
     they permute the blocks of a partition, and the record lasts.
   - Permutation transfers are the special case of single-point blocks. With
     two values they are the only case.
2. **Composing like cycles makes the memory homological** (Theorem 3).
   Modulo the tops, in a law that composes like cycles:
   - every three-variable knot whose witnesses share a range has one gain in
     a finite field;
   - a network of copies remembers exactly the twisted first cohomology of its
     graph;
   - its free sets are the frame matroid of the gain graph.

   Untwisted links give the graphic matroid and one class per loop, as in the
   holes-cohomology epic.
   - **So holes do behave like finite-field homology modulo the tops,** with
     two qualifications:
     - the coefficients can be twisted;
     - below the tops they can be a larger p-group. The 3-net of Z₄ remembers
       Z/4 classes, which are Z/2 classes modulo the tops.
3. **For Latin knots** (permutation transfers that cover every pair once),
   composing like cycles holds exactly for isotopes of abelian p-groups (the
   3-net proof).

## The ties

- **To the knot-loops epic.**
  - **Any number of values.** The ring theorem extends from two witness values
    to any number. This uses Protasov and Voynov's theorem on families of
    matrices without positive products (see [Blondel, Jungers and
    Olshevsky](https://arxiv.org/abs/1306.0729), Theorem 12).
  - **A sharper statement.** "Only group-like knots remember a loop" becomes
    "only knots group-like modulo blocks". The dressed parity knot shows the
    blocks are needed.
  - **What "remember" means.** It must be read in the lim sup. Twisted affine
    knots compose like cycles and are group-like, yet forget at every length
    that is not a multiple of their gain's order.
- **To the holes-cohomology epic.** "One H¹ class per loop" is the untwisted
  case. With twisted contact, each loop of gain other than 1 is not a hole by
  itself, but two of them bind into one hole (a handcuff).
  - **Two kinds of binding.** That epic's selector atoms bind loops through
    fixed points, in any shape, and leave cycle-like composition (the selector
    law fails elimination). Inside cycle-like composition, loops bind only
    linearly, as frame-matroid circuits.

## What it implies for contact networks

1. **Homological networks are exactly the cycle-like ones.** In a law that
   composes like cycles, every network computes a finite-field cohomology of
   its graph, modulo the tops.
   - Its holes are the circuits of a frame matroid (graphic if untwisted).
   - Its memory adds up over independent loops.
   - Every other system of the law is linear over a finite field too (the
     affine-tops proof).
2. **Networks alone cannot certify cycle-like composition.** For any group,
   Z₆ and S₃ included, a network of the group's 3-net remembers |G|^{b₁}
   classes with the forests as free sets.
   - **Where the difference shows.** It appears only in systems that are not
     networks: Thomsen's configuration, or splitting coprime orders.
   - **So the test is per law.** A law's networks can look homological while
     the law does not compose like cycles.
3. **One law cannot bind loops both ways.** Linear binding (pairs of twisted
   loops) lives inside cycle-like composition. Atomic binding (a selector
   atom excluding one pattern, in any shape) lives outside it.
4. **No distance follows.** Twisted H¹ counts loops, not lengths.
   - The networks' graphs are laid out by hand. A cycle-like law recognizes a
     graph's cycle space or frame matroid; it does not create the graph. This
     agrees with the knot-space epic's "space recognized, not created".
   - Native adjacency, paths and separation are still unconstructed, so
     extended, path and metric distance remain out of bounds.
5. **What the native-network gate gains.** A native-network candidate must
   compose by a substrate-native law.
   - Composing like cycles is now a characterized law of that kind, with known
     algebra (affine modulo the tops) and known holes (twisted cohomology).
   - Whether its contacts pass the other gates has not been tested: identity,
     persistence, restrictions, transports and recodings.

## Provenance

| Result | Where the idea came from | Novelty |
| --- | --- | --- |
| The dichotomy for any number of values | The ring theorem's fading, pushed beyond two values; recognized during scoping as primitivity of matrix families | Application of Protasov and Voynov; new to the program |
| Two values: the claim holds | The ring theorem with the Boolean case of the knot-circuits epic | A combination of earlier results |
| Twisted cohomology and frame matroids | The affine-tops proof's addition tables, read on rings. Scoping found x + y + z = 0 over F₃ forgetting its odd rings, so the gain had to enter. | Classical gain-graph cohomology (Zaslavsky); the field-scalar gain and the reading are new to the program |
| Twisted loops bind in pairs | Handcuff circuits of the frame matroid, set against the selector atoms of the holes-cohomology epic | Classical object; new reading |
| The claim's three failures | Testing the claim against the 3-net proof and the scoping census | New to the program |

**Did the perspective do real work?** It shaped the questions, not the
answers.
- **The questions were the program's own:** which knots remember loops, and
  what composing like cycles does to holes.
- **The answers are classical mathematics:** primitive matrix families and
  gain-graph cohomology. The affine-tops results connect them.
- **The new content is the connection itself.**
  - The tops are exactly where loop memory stops being linear.
  - Two kinds of binding separate: linear inside cycle-like composition,
    atomic outside it.
- **Folklore risk:** high for the mathematics, low for the connection.

**Ratio since the last checkpoint.**
- 1 artifact is substantive: the proof, with three theorems, a corollary and
  the test.
- 2 are administrative: this note and the ledger.

## Recommendation

The owner asked to keep the contact, network and distance questions in the
queue. The composition series now has a natural endpoint:
- the characterization (affine modulo the tops);
- the matroids (𝓡 over finite fields);
- tractability (with constants or rigid cores);
- holes (twisted finite-field cohomology).

| Option | What it would do | For | Against | Interest |
| --- | --- | --- | --- | --- |
| **1. Contact, network and distance** (recommended) | Audit whether, in a law that composes like cycles, two knots sharing one distinction pass every native-network gate. Then ask what adjacency, paths and separation the law's own matroids supply without a hand-laid graph. | The gate that blocked every earlier candidate, composition by a substrate-native law, now has a characterized instance. A pass would give the program's first native-network candidate; a fail would give a precise obstruction. | Every network so far was a chosen system. The likely answer may again be "recognized, not created". | 2/3 |
| 2. Bank the composition series | Make the characterization, matroids, tractability and holes independently reviewable: a self-contained note, or an expert check, which is the owner's decision. | The bounded scan found no overlap. The results now form one story, and folklore risk is moderate. | It is presentation rather than discovery, and the model-theory analogues may make it known. | 2/3 for reviewability |
| 3. Urquhart's conjecture | Return to resolution size versus treewidth on Tseitin formulas. | Open and consequential. | Hard. The earlier epic reduced it to faithful refutations, and no new lever has appeared. | 1/3 |

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — the unified claim about holes | **Successful** | The claim holds for two values and fails beyond, in three ways. The corrected form is proved: lasting memory needs block-group-like contact, and composing like cycles makes holes twisted finite-field cohomology modulo the tops. |
| Local direction — composition like cycles | Practically complete | Its algebra, matroids, complexity and holes are mapped. Remaining refinements, such as twisted networks of several knots and the matroid below the tops, would not change the picture. |
| Broader exploration — the contact-first program | Known alternatives | (1) Contact, network and distance, the owner's queue. (2) Banking the composition series. (3) Urquhart's conjecture. |
| Long-term goal — intrinsic structure from logic | Capability gained | There is now a characterized substrate-native composition law whose networks are homological. Native adjacency, paths and separation are not constructed; the graph is still supplied. |
| Next recommendation — contact, network and distance (fresh epic) | **Next step:** Full pivot from the composition series to the queued contact, network and distance questions. Start with a gate audit in laws that compose like cycles: two knots sharing one distinction, checked against every native-network gate (completeness, one substrate, endpoint identity, native composition, persistence under restrictions, transports and recodings). Then ask whether the law's own matroids fix adjacency, paths and separation without a layout. | The characterization and its holes are retained as the substrate's known algebra. Reopen the composition series if the audit needs its matroid below the tops. |
| Interest — that next step | **2/3 — Promising** | The gate that used to fail first now has an instance. The main uncertainty is the layout problem: every network is a chosen system, and nothing yet singles one out. |
| Execution — that next step | Deferred to the owner | Not started. The owner asked to study the two directions in order, and both are done. The choice among the three options is the owner's. A first epic would be bounded to the gate audit and one adjacency test. Stop if every adjacency comes from the layout, and record that as the obstruction. |
