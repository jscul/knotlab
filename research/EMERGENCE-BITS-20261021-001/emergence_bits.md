# Emergence in bits

Epic `EMERGENCE-BITS-20261021-001`, closed 2026-10-21.

## The question

After the base-three epic the owner chose option 1:
- measure in bits how much a whole hides from all its pairs;
- ask how emergence adds up as clauses of three literals build chains, rings
  and networks;
- ask how much n distinctions can hold.

The owner also asked that incorrect documents be corrected along the way.

**The evidence:**
- [Measuring emergence in bits](../../proofs/EMERGENCE-BITS-20261021-001A/EMERGENCE-BITS-20261021-001A-P001_emergence_measures/proof.md)
  (A, proof);
- [How emergence adds up](../../proofs/EMERGENCE-BITS-20261021-001B/EMERGENCE-BITS-20261021-001B-P001_emergence_accounting/proof.md)
  (B, proof);
- [Not-all-equal worlds on surfaces at scale](../../experiments/EMERGENCE-BITS-20261021-001C/EMERGENCE-BITS-20261021-001C-E001_surface_emergence/contract.json)
  (C, confirmatory experiment;
  [result](../../artifacts/EMERGENCE-BITS-20261021-001C/EMERGENCE-BITS-20261021-001C-E001_surface_emergence/result.json)).

## The measure

E(R) = log₂|pair closure of R| − log₂|R|. This is minus log₂ of the chance
that a state consistent with every pair's view is consistent with the whole.
- **Its statistical twin** I(R) is the divergence of the uniform distribution
  on R from the pairwise (Ising) family.
- **The two measures agree on** parity and every other affine relation.
- **They differ on frustration.**

## Results at a glance

| What | Emergence | Evidence |
| --- | --- | --- |
| Anything built from clauses of at most two literals | 0, and forgetting keeps it 0 | A, Theorem 1; B, Theorem 2 |
| One clause of three literals | log₂(8/7) ≈ 0.193 bits (statistically 0.078) | A, Theorem 2 |
| One knot on N bits | −log₂(1 − |Z|/2^N) ≤ 1; only parity reaches 1 | A, Theorem 2 |
| The not-all-equal triangle | 0.415 bits in support, 0 statistically: the only silent knot | A, Theorem 3 |
| n distinctions, logically | up to n − log₂ CAN(2,n,2) ≈ n − log₂log₂n (minimum covering arrays) | A, Theorem 4 |
| n distinctions, statistically | at most n − log₂(n+1), exactly for Hadamard designs; on seven distinctions only the 480 Fano parity networks | A, Theorem 5 |
| n distinctions, affine (parity) worlds | n − ⌈log₂(n+1)⌉ (simplex codes) | A, Theorem 6 |
| A visible chain of k knots | the sum, corrected by the leanings at the joints; k bits for parity | B, Theorem 1 |
| A ring or chain with its joints forgotten | 1 bit at every length for parity; geometric decay otherwise (slowest 0.805 per link) | B, Theorem 3 |
| One contact on N distinctions in a law | 1 bit at every even N with memory; at most −log₂(1 − N·2^(−N)) without | B, Theorem 4 |
| A network with hidden joints | at most one bit per independent cycle, exactly for parity; superadditive over edge-disjoint patches; 0 for links with a vacuum | B, Theorem 5 |
| Not-all-equal on tori | triangular: about 0.40 bits per vertex; honeycomb with an odd side: falls to 0; square with odd sides: about 0.83 bits (1:1) or 1.15 bits (1:2) at every tested size | C |

## How the results fit (theorems and measurements)

**1. Emergence starts exactly at the boundary between two and three
literals.**
- E is zero for every relation definable by clauses of at most two literals,
  and positive for everything else.
- Forgetting distinctions never moves a pairwise world off zero.
- Forgetting distinctions of a three-literal world can create emergence. It
  can even create statistical emergence from parts with none: a cyclic join
  of three statistically silent triples hides parity.

**2. One contact holds at most one bit; large emergence is collective.**
- **A single knot** hides between 2^(−N)/ln 2 and 1 bit, and only parity
  hides the full bit.
- **Yet n distinctions can hide almost everything** from their pairs: about
  n − log₂log₂n bits. The worlds that do so are tiny codes, covering arrays
  and Hadamard designs, with about log n states and many knots among them.
- **On seven distinctions,** the world that hides the most statistically is
  the Fano plane's parity network, and nothing else.

**3. Two ways past pairs.**
- **Conjunction of three-literal clauses** gives emergence in support and in
  statistics.
- **Competition among pairs** (frustration) gives exactly one knot, the
  not-all-equal triangle (the competition epic). Its emergence is visible in
  what is allowed but invisible in pair statistics.
- **With hidden distinctions** both routes reach every relation.

**4. Over distance, only reversible contact carries emergence.**
- Along a chain or ring, parity keeps exactly one bit at every length.
- Every other contact leaks it geometrically.
- In a law, a single contact can hold a full bit at every size exactly when
  the law has memory. This is the base-three memory theorem made
  quantitative.

**5. In networks, emergence lives in cycles, at most one bit each.**
- **Only parity fills every cycle.**
- **Other contact can still hold many bits.** It needs a frustrating patch, a
  small subgraph that can be inconsistent. Patches add up, so this emergence
  grows with the size of the network.
- **Some contact holds nothing.** One-clause contact, and contact with any
  vacuum value, holds nothing in any network with hidden joints.

**6. Where no patch frustrates, emergence comes from global cycles, and on
the square lattice it does not fade.**
- **No local trace.** Not-all-equal contact on a lattice whose faces are all
  even has no frustrating patch: every part of the surface that does not
  wrap around is always consistent.
- **The seam.** On a torus with an odd side, the recolouring of proof B
  shows the hidden joints carry a pair-world: implications pointing in
  uniformly random directions, closed by a seam of two-literal clauses.
- **What the experiment found.**
  - On the honeycomb the global emergence vanishes as the torus grows.
  - On the square lattice it stays at about 0.83 bits on 1:1 tori. The
    slope is 0.003 ± 0.008 bits per doubling, from side 9 to side 41.
  - On 1:2 tori it stays at about 1.15 bits.
  - The amount depends on the shape, not the size.

## The underlying theory (interpretation, not theorem)

**Three-literal contact is a pair-world switched by visible distinctions.**
- **The switch.** A knot on (h, x, h′) is a two-literal relation between h
  and h′ that the visible x selects.
- **The surprise.** A network of such knots with hidden joints is a family of
  pair-worlds on the joints, one for each visible state. Its emergence is
  the surprise that the switched pair-world is consistent.
- **The base-three loops at scale.** This is the base-three reading of
  "pairs make loops, triples join them", now quantitative: the loops are the
  cycles of the hidden pair-world, and emergence is the chance they close
  inconsistently.

**The owner's "infinite cycles of logic that are universally influential".**
There are now three kinds, all at the base:
1. **Equality cycles.** They fix one distinction everywhere and hide nothing
   (base three).
2. **Parity cycles.** Each holds exactly one bit, visible to no part, at any
   length. They are the only cycles that keep a full bit over distance.
3. **Global frustration on the square lattice.** No cycle holds anything by
   itself, and no patch sees anything. Yet the world as a whole hides a fixed
   amount, about 0.83 bits, at every size tested.
   - **Interpretation, not tested.** The amount seems to be set by the shape
     of the world, not its size. This is the signature of a critical point.
     The randomly oriented square lattice behind it has no infinite
     oriented path, which Grimmett (2001) proved by coupling it with critical
     bond percolation.
   - **Why the lattice matters.** The honeycomb loses it, and the triangular
     lattice buries it under local frustration. A uniform law of fair visible
     distinctions on the self-dual lattice lands on a scale-free amount of
     hidden fact.

**Localization becomes quantitative.** A localized observer reads a patch.
- **What a patch misses.** On the square torus it sees none of the global
  emergence, and growing the world does not shrink what stays hidden.
- **Parity worlds.** Each cycle the patch does not contain hides one bit.
- **Worlds with only irreversible contact** hide nothing beyond what they
  hide locally.

This reading is offered as the owner's base-level picture. The theorems are
A and B; the size-independence is an experiment (C) in the tested range only.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| The knot is the unit of emergence | The knot-first framing of the foundation | **Refined.** Emergence is graded. One knot holds at most one bit, while networks of knots can hide almost every bit. Codes, not single contacts, are the most emergent worlds. |
| Competing pairs give genuine knots | `docs/KNOT_INTUITION.md`, "Knots from competing pairs" | **Qualified.** The competition knot is visible in what is allowed, but carries no statistical emergence; every other knot does. |
| Knots other than parity "remember at most a fraction of a bit" in networks | `docs/KNOT_INTUITION.md`, "Which knots remember a loop" (from `KNOT-LOOPS-20261019-001C-E001` on graphs of up to 9 edges) | **Corrected.** That holds on small graphs. Frustrating patches add up, so other knots can hold many bits in large networks (1.32 bits on the Petersen graph), always strictly less than one per cycle. |
| Irreversible contact forgets and is transparent | `research/BASE-THREE-20261021-001/base_three.md`, "Memory is reversibility" | **True along chains and rings, false for networks.** Frustration stores emergence in patches. Global frustration on the square lattice stores a size-independent amount. |
| The universal cycles are equality and parity cycles | The same note, "Two kinds of universal cycle" | **A third kind.** Global frustration on a self-dual surface: no cycle and no patch holds anything, yet the whole hides a fixed amount. |
| Lasting emergence needs memory (affine contact) | The base-three memory theorem | **Right for single contacts and for one-dimensional structures, not for surfaces.** Not-all-equal (no memory as a link, though its law has memory) keeps a fixed amount on the square torus. |

## Provenance and novelty

| Result | Where the idea came from | Novelty |
| --- | --- | --- |
| E = 0 exactly for two-literal relations; I = 0 exactly for facial sets | The owner's framing of the 2/3 boundary; information geometry | Textbook (Baker–Pixley, Schaefer; closure of exponential families) |
| Knot emergence formula; the only silent knots | The competition proof's characterization, read statistically | Elementary; the statistical reading is new to the program |
| Logical capacity n − log₂ CAN(2,n,2) | Asking which worlds hide the most; covering arrays | Classical objects; the identification not found in a bounded search; moderate folklore risk |
| Statistical capacity n − log₂(n+1), equality exactly for Hadamard designs; 480 Fano maximizers | A rank argument on second moments | Related work on divergence maximizers (Rauh; Matúš and Ay) studies all distributions; the uniform-set version not found; moderate folklore risk |
| Visible joins, forgetting, chains and rings | Transfer matrices; the ring theorem | Elementary or restated (ring theorem, Protasov–Voynov) |
| Long contacts in a law | The base-three memory theorem plus the shape of conjunction-closed knots | Elementary; new to the program |
| Network bound b₁, equality only for parity; superadditivity; zeros | Counting with a spanning tree | Classical for parity (coboundaries); the general bound and the equality case not found; new to the program |
| Torus recolouring | The checkerboard gauge | Standard gauge; the reading is new |
| Size-independent emergence on square tori; vanishing on the honeycomb; extensive on the triangular lattice | Scoping probes after the network theorem | Empirical, new to the program; the link to Grimmett's randomly oriented lattice is interpretation |

**Did the base-level lens do work?** Yes.
- **What it chose.** It chose what to measure: bits hidden from pairs, rather
  than knot or no knot.
- **What that exposed.** The silent frustration knot, the capacity gap
  between single contacts and codes, and a correction to the workspace's
  small-graph summary.
- **What it led to.** It also led to the surface experiment, whose
  size-independence was not predicted.
- **Classical pieces.** Most proofs use classical pieces, labelled above.

**Ratio since the last checkpoint.**
- 3 artifacts are substantive: the two proofs and the experiment.
- 2 are administrative: this note and the ledger.

## Recommendation

| Option | What it would do | Interest |
| --- | --- | --- |
| **1. Criticality at the base** (recommended) | Test whether the square-torus value depends only on the shape (more aspect ratios and sheared tori), compare it with wrapping events in Grimmett's randomly oriented lattice, try three dimensions and other self-dual settings, and seek a proof that it stays bounded away from 0 and from infinity | 2/3 |
| 2. Worlds from loops and contacts | Build worlds whose loops are pairwise implication cycles and whose contacts are triples, and measure emergence by layer and by scale | 1/3 to 2/3 |
| 3. Bank "Emergence in bits" | A self-contained note on the measures, the capacities and the network bound; sharing is the owner's call | 2/3 for reviewability |

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — emergence in bits | **Successful** | The measure is exactly zero at two literals. Each knot holds at most one bit, and n distinctions can hold almost n. Networks hold at most one bit per cycle, filled only by parity. The square-lattice result was unexpected. |
| Local direction — the bit measure on Boolean systems | Practically complete for single relations and one-dimensional structures; open on surfaces | The capacities and network bound are proved. What remains is why the square lattice holds a scale-free amount. |
| Broader exploration — the base-level theory | Searching | The surface result suggests the base can sit at a critical point. Whether this is generic or special to the self-dual lattice is unknown. |
| Long-term goal — emergence from logic | Capability gained | The 2/3 boundary now has a currency. Where emergence lives (cycles, patches, global topology) and when it survives at scale are measured, not only named. |
| Next recommendation — criticality at the base | **Next step:** Continue. Fresh epic: aspect-ratio and shear dependence of the square-torus value, the comparison with Grimmett's model, three dimensions, and a proof of uniform bounds | If the value depends only on shape, the base logic has a scale-invariant regime. If it drifts, the result is a slow crossover. |
| Interest — that next step | **2/3 — Promising** | The size-independence held across a factor of 4.6 in size with tight errors, and the randomly oriented square lattice is tied to critical bond percolation by a known coupling. The uncertainty is whether a proof is within reach. |
| Execution — that next step | Deferred to the owner | One bounded epic. Stop if the value drifts with size beyond the tested range, or if no shape dependence appears. |
