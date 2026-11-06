# Counting the knot's graphs without signs

Epic `PLAIN-COUNT-20261031-001`, 2026-10-31.

## The question

- **The owner's request (2026-10-31).** "Yes let's continue." This approved the recommendation of `SOFT-CROSS-20261031-001`:
  - remove the signs from the hardness of counting on the knot's graphs;
  - classify plain (unsigned) Pfaffian triple systems by how their own Pfaffian class twists.
- **Intuitions targeted:**
  - the two/three boundary as emergence, in counting;
  - the knot as the atom of its spaces.

**The evidence:**
- [Signs interpolate away](../../proofs/PLAIN-COUNT-20261031-001A/PLAIN-COUNT-20261031-001A-P001_signs_interpolate_away/proof.md)
  (A, proof with exact computations);
- [Plain pages are always twisted](../../proofs/PLAIN-COUNT-20261031-001B/PLAIN-COUNT-20261031-001B-P001_plain_pages_are_always_twisted/proof.md)
  (B, proof with exhaustive and exact computations).

## Outcome in one paragraph

**Plain triple systems with Pfaffian incidence graphs are #P-hard to count, and in the plain world twisting is the default. The only plain
brace without twists is the knot's own atom, the Fano plane.**
- **Signs interpolate away (A, proved).**
  - An unsigned long edge, read at t = −1 by interpolation over its length, acts as a negation.
  - Lengthening edges inside planar pieces keeps the Pfaffian certificate.
  - So counting proper 2-colourings of 3-regular 3-uniform hypergraphs whose incidence graphs are Pfaffian is #P-hard.
  - K₃,₃ is counted end to end from 100 plain Pfaffian instances, the largest with 18504 vertices.
- **Plain pages are always twisted (B, proved).** Euler's formula gives every planar cubic bipartite graph at least six square faces, and at
  most five meet the junction. A Pfaffian signing needs an odd sign on the other squares, and the plain signing has none.
  - So every square of a plain trisum brace has three twisted branches.
- **The knot's atom (B, proved; likely known).** Plain non-colourable systems have no nice cycle of length 0 mod 4. Since a brace's 4-cycles
  are nice, the Heawood graph is the only cubic brace whose plain system cannot be 2-coloured.
- **End-of-epic discriminator (scoping for the next step, not evidence).** All 2500 junctions of pairs of plain pages, among 50 distinct
  page tensors, violate the matchgate identity, while every single plain page satisfies it. Plain junctions are also never crossover-type
  (epic scoping).
  - So on plain trisum braces neither the easy mechanism nor the soft-crossing hardness applies directly.

## What was proved

| Result | Content |
| --- | --- |
| A, Lemma 1 | #col(G_k) = 9^{kL} q((−1/3)^k), deg q ≤ L; q(−1) is the signed count, q(1) the count with the signs dropped. |
| A, Lemmas 2–3 | Pfaffian certificates survive long edges inside planar pieces; the soft crossing switches to 6 negations (exhaustive minimum per page). |
| A, Theorem 4, Corollary 5 | Plain triple systems with Pfaffian incidence graphs are #P-hard to count; 9·#col(K₃,₃) = 54 from plain counts only. |
| B, Lemma 1, Theorem 2 | At least six square faces, at most five meet a square; every plain planar page is twisted. |
| B, Corollary 3 | Plain trisum braces: three twisted branches at every square, no good root. |
| B, Lemma 4, Corollary 5 | Plain non-colourable: every nice cycle has length 2 mod 4; the Heawood graph is the only plain non-colourable brace. |

## Reading

- **A sign is a path in disguise.** Hardness on the knot's graphs needs no supplied signs. The plain signs are already twisted against the
  Pfaffian class, and path lengths can stand in for any further sign.
- **Squares are twists.** A cubic plane needs squares, and a square is exactly where plain signs disagree with the knot's signs.
  - Hexagons, 6 ≡ 2 mod 4, agree.
  - The Fano plane's incidence graph has no squares at all; its shortest cycles are hexagons. That is why it is the only plain brace that
    cannot be 2-coloured.
- **Two against three again.**
  - A single plain page is a matchgate: planar, easy.
  - Two plain pages meeting a host at a square always leave the matchgate class: three twisted sides.
  - The knot's atom is the one brace where no square, and so no twist, appears.
- **Provenance.**
  - Euler, Kasteleyn and the nice-cycle facts are classical.
  - The plain non-colourability criterion is the convertibility condition (Little; Vazirani and Yannakakis).
  - Fano's uniqueness among braces is likely implied by Robertson–Seymour–Thomas.
  - New, with no overlap found: hardness on Pfaffian incidence graphs, plain pages always twisted, and plain trisum braces branched
    everywhere.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — counting the knot's graphs without signs | **Status:** Successful | Plain Pfaffian triple systems are #P-hard to count. Plain pages are always twisted. The Fano plane is the only plain non-colourable brace. |
| Local direction — the counting arc on the knot's graphs | Continue (one open case) | Settled: signed and plain Pfaffian systems in the worst case. Open: plain braces, where the hard instances' caps and long edges (2-edge cuts) are not allowed. |
| Broader exploration — counting near Seymour's bound | Known alternatives | Mapped: the bound, unbranched twists, branched twists (signed and plain). Unmapped: plain braces, approximate counting. |
| Long-term goal — the two/three boundary in counting | Capability gained | The plain picture: planar pages easy, two plain pages at a square always non-matchgate, and the knot's atom the only twist-free brace. |
| Next recommendation — counting on plain braces | **Next step:** Continue, as a fresh epic. Decide whether counting 2-colourings is #P-hard on plain cubic Pfaffian braces, or whether plain trisum braces hide another tractable structure. | It would make the plain-brace picture complete. Planar braces and the knot's atom are easy; trisum braces would be hard, or would reveal a new easy class. |
| Interest — that recommendation | **2/3 — Promising** | Every plain junction is non-matchgate (2500/2500), so the matchgate route fails. But no plain junction is a crossover, so the soft-crossing route needs a new gadget. Plumbing must avoid 2-edge cuts to stay a brace. Main uncertainty: whether series of plain junctions, or a planar-#CSP argument for the non-matchgate junction signature, gives hardness. |
| Execution — that next action | Deferred to the owner (fresh epic) | First discriminator: plain junctions in series (snakes of plain pages with brace plumbing): are they ever crossover-type with nonzero double entry? Stop if plain trisum braces turn out to lie in one holographic class (then look for an algorithm). |

**Recommendation.** **Continue**, as a fresh epic: counting on plain braces (2/3). Two alternatives were considered.
- **A write-up of the counting arc (1/3).** The arc runs Seymour's bound, then twists, then hardness, then plain systems. It is now coherent
  and mostly new. But its strongest unresolved case, plain braces, is the natural endpoint, and the source hardness is known.
- **Approximate counting (1/3).** Exact counting is settled except on plain braces, and approximation is only weakly tied to the knot.
