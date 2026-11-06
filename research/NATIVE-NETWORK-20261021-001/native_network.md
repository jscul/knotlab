# Do knots that compose like cycles form a native contact network?

Epic `NATIVE-NETWORK-20261021-001`, closed 2026-10-21.

## The question

The owner approved the queued contact, network and distance line in two
steps:
1. Check whether two knots sharing one distinction, in a law that composes
   like cycles, pass every native-network gate.
2. Ask whether the law's own matroids fix adjacency, paths and separation
   without a hand-drawn layout.

**The gates** are those of `docs/COMMON_VERBIAGE.md` ("Contact network"), read
through the canonical knot test.

**The evidence:**
- [the gate audit](../../proofs/NATIVE-NETWORK-20261021-001A/NATIVE-NETWORK-20261021-001A-P001_network_gates/proof.md);
- [adjacency, routes and separation](../../proofs/NATIVE-NETWORK-20261021-001B/NATIVE-NETWORK-20261021-001B-P001_native_adjacency/proof.md).

Both have checks next to them.

## 1. The gate audit: a native-network candidate, under declared maps

Take two knots sharing one distinction e, with the same range for e in both,
in a law that composes like cycles.

| Gate | Verdict | Why |
| --- | --- | --- |
| Complete contacts | passes | Each is a knot (K1–K3) |
| One declared substrate | passes | One system of one law |
| Endpoint identity without collapse | passes | Forgetting e gives one knot on all the other distinctions: none lost, none tied |
| Composition by a substrate-native law | passes | The composite is the law's own projection |
| No larger common hub | passes | Composing like cycles is exactly "no hub" |
| Not observer-drawn, not imposed | passes | Every verdict comes from allowed states |
| Recodings | pass | Renaming values or variables changes nothing |
| Restrictions: erasure, the law's own relations | pass | Restricted systems are systems of the same law |
| Restrictions: pinning values | **conditional** | Passes exactly when the law with constants still composes like cycles. Affine laws over finite fields do, and are then tractable; parity beside J and K₄ do not. |
| Transports: isomorphism, pp-definition | pass | Systems unfold into the law's own |
| Transports: homomorphic equivalence, products | **fail** | The lift of K₃ against K₃, and Z₂ × Z₃ = Z₆ |

**So such a pair is a native-network candidate, with these admitted maps:**
- recodings;
- erasure, and restriction by the law's own relations;
- isomorphisms and pp-definitions.

**With pinning admitted,** the class narrows to laws that keep composing like
cycles with constants. That class includes the affine laws over finite fields.

**Two warnings.**
- **A passing pair does not certify a law.** In the 3-net of S₃, every pair
  composes into one knot, yet Thomsen's configuration, doubled, fails.
- **Hubs.** Not-all-three pairs are hubs.

## 2. What the allowed states fix, and what they do not

In a declared substrate (a system) of such a law:
- **Routes compose into contacts.** A route of knots sharing distinctions
  becomes one knot through its ends. So reachability is the matroid's
  connectivity.
  - **The program's earlier picture changes.** It kept paths as traces of
    contacts. Under the canonical test, a path is absorbed into a contact. What
    survives of its length is the size of that contact.
- **Bond distance is an extended metric.**
  - **The definition.** The least size of a knot through two distinctions,
    minus one.
  - **On chains.** It grows by one per atom along a chain. KNOT-FOUNDATION D
    observed this for clause atoms; it now holds for every law that composes
    like cycles.
  - **Where it breaks.** It satisfies the triangle inequality wherever
    composition holds. It fails in a hub, where a route does not compose.
- **Separation is native, and erasing and pinning act in opposite ways.**
  - **A shared distinction:** forgetting it composes the contacts through it,
    and fixing it cuts them.
  - **A private loop:** forgetting it cuts, and fixing it ties its two
    neighbours.
  - Pinning also freezes every distinction tied to the pinned one.
- **The drawing is not recovered.** Three parity contacts in a triangle have
  the matroid of K₄.
  - Its symmetries carry a drawn contact onto the knot that the loop leaves
    among the three contacts.
  - So which knots were "written" and which distinctions are "loops" are not
    properties of the allowed states.
  - The allowed states return K₄, with an apex that the drawing does not show.
- **The law fixes no substrate.**
  - The 3-net of Z_p pp-defines every linear subspace. Its substrates realize
    every F_p-representable matroid:
    - parity has the Fano plane, which no graph has;
    - the 3-net of Z₃ has U(2, 4).
  - The law fixes how adjacency, routes, separation and distance behave, not
    which ones occur.

**Answer to the owner's question.**
- **Within a declared substrate:** yes. Its allowed states fix contact
  adjacency, routes, native separation and an extended bond distance, without
  any drawing.
- **They do not fix the drawing.**
- **At the level of the law:** no. Every representable matroid occurs, so the
  substrate must still be declared.

**The guardrail.** Its preconditions for an extended distance are now met in
the declared substrate. The bond distance is that candidate. It is relative
to the substrate, computed from bond sizes rather than from values, and it
carries no coordinate, dimension or embedding.

**A mathematical non-selection.** The law selecting no substrate is not
evidence for or against the protected modal-plurality interpretation.

## A correction to the previous closure

The loop-homology proof says, under "What this does not show", that a
network's own free sets agreeing with its top image's "is not proved". That
is wrong: the top lemma (`CYCLE-TOPS-20261021-001B-P001`, Theorem 2) proves
it. Every system has exactly the circuits of its top image. So the
twisted-cohomology networks' frame matroids are the networks' own matroids.

The closed note and proof are not edited. This section is the correction.

## Provenance

| Result | Where the idea came from | Novelty |
| --- | --- | --- |
| The gate audit | The verbiage's contact-network definition, read gate by gate on allowed states. The answers come from the composition series. | Elementary given the series; new to the program |
| Pinning and transports decide the verdict | The utility proof's constants failures; the tractability epic's lift; the loop-homology epic's Z₆ | New reading of earlier counterexamples |
| Routes compose into contacts; bond distance is a metric | Matroid connectivity (Whitney) | Classical; the reading is new |
| Chains and the erase/pin duality | The space note's chain observation, and deletion against contraction | Classical mathematics; new to the program |
| The drawing is lost | Testing the "atomic contact" notion on the smallest loop | New to the program; the K₄ symmetry is classical |
| The law fixes no substrate | The Galois connection for the 3-net of Z_p | Classical |

**Did the perspective do real work?** It set the questions and the order of
construction (contact, adjacency, route, separation, distance), as the
guardrails demand. The answers are elementary matroid theory.

**Three findings change how the program should talk about networks:**
- paths dissolve into contacts;
- forgetting and fixing play dual roles;
- the drawing is not recoverable.

**Folklore risk:** high for the mathematics, low for the reading.

**Ratio since the last checkpoint.**
- 2 artifacts are substantive: the two proofs.
- 2 are administrative: this note and the ledger.

So the next step should be substantive work or conversion.

## Recommendation

The network line now reaches an extended distance relative to a declared
substrate. **The open point is precise:** nothing in a law selects or forms
the substrate (open question 9).

| Option | What it would do | For | Against | Interest |
| --- | --- | --- | --- | --- |
| **1. Formed substrates** (recommended) | A bounded direction search over ways a substrate could be formed rather than declared. Three routes: a native update law on systems that keeps composing like cycles (world generation, question 4); least-violation selection (question 10); canonical substrates of a law. | It is the one gap left between contact and space, and each route has a cheap first test. The canonical-substrate route probably fails fast: the full geometry has every two points on a line. | Hard, and shared with causal sets and hypergraph rewriting. Earlier passes rated question 9 at 1/3. | 1/3 |
| 2. Bank the composition and network series | One self-contained note: the characterization, the matroids, tractability, twisted holes, the network gates and the bond distance. Sharing it is the owner's call. | The results now form one story, and a bounded scan found no overlap for the characterization. | It is presentation, and folklore risk remains moderate to high. | 2/3 for reviewability |
| 3. Urquhart's conjecture | Return to resolution size against treewidth. | Open and consequential. | No new lever. | 1/3 |

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — native contact networks in laws composing like cycles | **Successful** | Pairs pass the gate under declared maps, with pinning and transports as the deciding conditions. Allowed states fix adjacency, routes, native separation and a bond distance without a drawing. They do not fix the drawing, and the law fixes no substrate. |
| Local direction — networks inside a declared substrate | Practically complete | Its constructions and their limits are mapped. Further refinements (larger networks, other laws with constants) would not change the picture. |
| Broader exploration — the contact-first program | Known alternatives | (1) Formed substrates. (2) Banking. (3) Urquhart's conjecture. |
| Long-term goal — intrinsic structure from logic | Capability gained, obstruction sharpened | Contact, adjacency, route, separation and an extended distance are now native relative to a declared substrate. What remains is formation or selection of the substrate itself. |
| Next recommendation — formed substrates (bounded direction search) | **Next step:** Research directions. Compare three routes to substrates that are formed rather than declared: a native update law preserving cycle-like composition, least-violation selection, and canonical substrates. Use the cheapest discriminator for each, then pick at most one. | It addresses the single remaining gap. A negative answer on all three would be a clean stopping point for the network line. |
| Interest — that search | **1/3 — Exploratory poking** | The gap is now precise, but every earlier attempt at question 9 found layouts supplied rather than formed. The main uncertainty is whether any native update law preserves cycle-like composition non-trivially. |
| Execution — that search | Deferred to the owner | Not started. The owner chooses among the three options. A search would be bounded to one round of discriminators, and would stop if none of the three routes gives a non-trivial formed substrate. |
