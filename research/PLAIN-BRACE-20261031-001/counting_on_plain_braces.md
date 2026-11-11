# Counting on plain braces

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a three-fold space is a three-regular contradiction. Results are unchanged;
the earlier text is in git history.

Epic `PLAIN-BRACE-20261031-001`, 2026-10-31.

## The question

- **The owner's request (2026-10-31).** "Yes, let's continue." This approved the recommendation of `PLAIN-COUNT-20261031-001`: decide whether
  counting 2-colourings is #P-hard on plain cubic Pfaffian braces, or whether plain trisum braces hide another tractable structure.
- **Intuitions targeted:**
  - the two/three boundary as emergence, in counting;
  - the knot as the atom of its spaces.

**The evidence:**
- [A plain crossing inside braces](../../proofs/PLAIN-BRACE-20261031-001A/PLAIN-BRACE-20261031-001A-P001_a_plain_crossing_inside_braces/proof.md)
  (A, proof with exact computations);
- [Counting on plain Pfaffian braces is #P-hard](../../proofs/PLAIN-BRACE-20261031-001B/PLAIN-BRACE-20261031-001B-P001_counting_on_plain_pfaffian_braces_is_sharp_p_hard/proof.md)
  (B, proof with exhaustive and exact computations).

## Outcome in one paragraph

**Plain Pfaffian braces are hard to count. Neither connectivity nor Pfaffian-ness protects counting.**
- **A plain crossing inside braces (A, proved).** A single junction of plain pages is never a crossing, but a ladder of them is, after
  interpolation.
  - Run wire B the other way and the site is exactly (NW)^k, with the crossing as its k = 0 term.
  - For two plain cubes, NW has characteristic polynomial (x² − 19x − 1)(x² + 7x + 13). Its roots are a unit of Q(√365) and the two
    Eisenstein primes above 13, which gives the lattice condition.
  - K₃,₃ is counted from plain Pfaffian braces of 20 to 104 vertices.
- **Hardness (B, proved).** A hard source is woven into a prism frame, with every crossing a ladder site.
  - A bond lemma, the ladders and a cube junction lemma make every instance cyclically 4-edge-connected, hence a brace by Hall's condition,
    and Pfaffian by the trisum certificate.
  - So counting on plain Pfaffian braces is #P-hard.
  - The polynomial cases found are planarity and the knot's atom, the Heawood graph (the Fano plane).

## What was proved

| Result | Content |
| --- | --- |
| A, Lemma 1 | The reversed site acts by (NW)^k; the exact crossing is the identity. |
| A, Lemmas 2–3 | The cube junction: NW = [[2,3,2,5],[8,4,8,9],[9,8,4,8],[5,2,3,2]], characteristic polynomial (x²−19x−1)(x²+7x+13); lattice condition from a unit of Q(√365) and the Eisenstein primes above 13. |
| A, Theorem 4, Corollary 5 | An exact crossing by interpolation (rational formula over k = 1, 3, 5, 7); K₃,₃ from plain Pfaffian braces. |
| B, Lemma 1 | Cubic bipartite and cyclically 4-edge-connected implies a brace (Hall). |
| B, Lemmas 2–5 | Sites are ladders; bonds of the planarized drawing; the weaving lemma; the cube junction lemma. |
| B, Theorem 7, Corollary 8 | Counting on plain Pfaffian braces is #P-hard; the plain picture. |

## Reading

- **The plain picture is complete in the worst case.**
  - One plain page is a planar matchgate.
  - Two plain pages at a square are twisted and soft, and never a crossing.
  - A ladder of such squares is an exact crossing, and with it every counting problem: on Pfaffian graphs, on braces, with no signs at all.
  - Planarity and the knot's atom, the one twist-free plain brace, are the polynomial cases.
- **The crossing's arithmetic.** The odd part of the ladder's transfer, x² + 7x + 13, is an Eisenstein norm form, the same form as the knot's
  similitude multiplier α² + αβ + β². That is an observation, not a claim.
- **Provenance.**
  - The source hardness is Fan and Cai's (2020), and its planar tractability Valiant's.
  - The structure of Pfaffian braces is Robertson, Seymour and Thomas's.
  - The braces' Hall characterization is classical.
  - New, with no overlap found: the plain crossing inside braces, the weaving and cube junction lemmas, and hardness on plain Pfaffian
    braces.

## The counting arc, in five epics

| Epic | Result |
| --- | --- |
| `SEYMOUR-COUNT-20261030-001` | Counting is polynomial on every three-regular contradiction (Berman determinants over RST trisum trees). |
| `TWIST-COUNT-20261030-001` | The knot's junction is a similitude; unbranched twists count in polynomial time. |
| `SOFT-CROSS-20261031-001` | Soft crossings sharpen inside Pfaffian graphs; counting under branched twists is #P-hard. |
| `PLAIN-COUNT-20261031-001` | Signs interpolate away; plain pages are always twisted; Fano is the only plain non-colourable brace. |
| `PLAIN-BRACE-20261031-001` | A plain crossing inside braces; counting on plain Pfaffian braces is #P-hard. |

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — counting on plain braces | **Status:** Successful | Plain Pfaffian braces are #P-hard to count. The polynomial cases found are planarity and the knot's atom. |
| Local direction — worst-case counting on the knot's graphs | Practically exhausted | Every natural class is settled: the bound, twists, signed and plain Pfaffian graphs, and plain braces. Further refinements (parameters, few junctions) would not change the picture. |
| Broader exploration — the two/three boundary in counting | Known alternatives | Mapped as above. Unmapped: approximate counting; the Ising reading (#col is the Ising partition function at x² = −1/3, the knot's class its free-fermion sign pattern). |
| Long-term goal — the two/three boundary as emergence | Capability gained | A complete worst-case picture on the knot's own graphs. The knot's signs give determinants; branching twists give universality; the knot's atom is the one twist-free brace. |
| Next recommendation — a note on the counting arc | **Next step:** Continue, as conversion. Write the five epics as one self-contained note, with independent replays of the key checks. Reader: the owner first, then complexity theorists. Completion check: every theorem stated with its proof sketch, provenance and replay. | The arc is complete and mostly new. A note makes it reviewable and gives the program a first external-facing result in counting. It authorizes no submission. |
| Interest — that recommendation | **2/3 — Promising** | Evidence: five proved epics forming one picture, with the source hardness clearly attributed. Main uncertainty: whether the results reach the magnitude the owner wants for a write-up. The polynomial count on every three-regular contradiction and the hardness on plain Pfaffian braces are the strongest. |
| Execution — that next action | Deferred to the owner | A bounded conversion: one note and one replay script. Stop and reassess if the literature check finds the polynomial three-fold count already known. |

**Recommendation.** **Continue**, as conversion: a note on the counting arc (2/3). Two alternatives were considered.
- **A bounded direction scan back toward native emergence (2/3).** It would ask which of the knot's open threads the counting picture can now
  move, for example whether native dynamics favour the twist-free atom. It is speculative until a concrete question emerges.
- **Approximate counting on the knot's graphs (1/3).** It is weakly tied to the knot.
