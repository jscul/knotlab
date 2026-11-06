# Prior art for the S₄ peripheral identities

Ticket `S4-LIFT-PRIOR-ART-20261025-001`, 2026-10-25. Documentation only: a literature comparison, with no new theorem.

**The request.** The owner, through Codex, asked for a theorem-by-theorem comparison of `CLOSED-H1-20261025-001B` (and its use in
`CLOSED-H1-20261025-001C`) with Ishikawa 2025. That required:
- full-text access where possible;
- exact references and notation maps;
- verbatim statements kept apart from easy consequences and inference;
- no non-overlap inferred from an abstract.

**What is out of scope.**
- Codex's independent proof review lives in `research/CLOSED-H1-20261025-001/codex_review_20261025.*` and is not touched here.
- No frozen artifact is edited.

**Labels used below.**
- **[V]** verbatim from a source read in full.
- **[C]** easy consequence, with the argument given.
- **[I]** inference, not verified.

## The main finding

The topological content of `CLOSED-H1-20261025-001B` was already published in 1995. The 2013 equal-count conjecture follows from
it.
- **Livingston 1995** already contains parts (a) and (b) of B, the one-longitude statement, and the existence of 4-cycle lifts.
  - It proves the existence (Theorem 8), conjectured by Perko in 1975 and proved by Rickard in unpublished 1984 notes.
  - It proves equal numbers of 4-cycle and transposition lift classes (Theorem 9), stated earlier in another form by Thistlethwaite.
  - It excludes the transposition-meridian, z-longitude case (Lemma 7, citing Edmonds and Livingston 1984).
- **The 2013 conjecture.** Equal colouring counts for the connected quandles C[6,1] and C[6,2] (Clark, Elhamdadi, Hou, Saito and
  Yeatman) follow from Livingston's Theorem 9 by summing. The Carter–Oshiro–Saito conjecture of 2009 is Livingston's Theorem 8. Both
  were settled before they were posed. No source read here says so.
- **Ishikawa 2025** could not be read in full.
- **The closed-manifold hardness** (`CLOSED-H1-20261025-001C`) appears in none of the sources read. It does not follow from a cited
  complexity result: it needs the knot hardness of `BOUNDED-H1-20261025-001A`.

## Access record

| Source | Access | What was established |
| --- | --- | --- |
| Ishikawa, *Generalization of Galkin quandles and lifting property of dihedral colorings*, Geom. Dedicata 219 (2025), art. 70, DOI [10.1007/s10711-025-01030-5](https://link.springer.com/article/10.1007/s10711-025-01030-5) | **Full text not accessed** | See the list below. |
| Livingston, *Lifting representations of knot groups*, J. Knot Theory Ramifications 4 (1995) 225–234 | **Full text read**: a scanned reprint on the [author's page](https://chuck-livingston.github.io/math/Livingston_papers/1995_lifting%20representations%20of%20knot%20groups.pdf), pages rendered and read | Theorems 6, 8, 9, 11, Lemma 7, Corollary 10, the 10₈₂ remark and the references; see below. |
| Perko, *Octahedral knot covers*, in *Knots, Groups, and 3-Manifolds* (Ann. of Math. Studies 84, 1975) 47–50 | **Full text read**: the scanned volume, with an OCR text layer ([PDF](https://webhomes.maths.ed.ac.uk/~v1ranick/papers/neuwir3.pdf)) | The theorem, Lemmas 1–2 and the conjecture on p. 49. |
| Clark, Elhamdadi, Hou, Saito, Yeatman, Pacific J. Math. 264 (2013), [arXiv:1107.5777](https://arxiv.org/abs/1107.5777) | Full text read (pdftotext) | Table 1 (C[6,1] = G(Z₂, [0]), C[6,2] = G(Z₂, [1])); Remarks 6.1, 6.6 and 6.8. Livingston, Perko and Thistlethwaite are not cited. |
| Clark, Elhamdadi, Saito, Yeatman, JKTR (2014), [arXiv:1312.3307](https://arxiv.org/abs/1312.3307) | HTML read through a summarizer, not verbatim | §5 restates C[6,1] ≈ C[6,2] as a conjecture. |
| Carter, Oshiro, Saito, Topology Appl. 157 (2010), [arXiv:0905.3374](https://arxiv.org/abs/0905.3374) | Abstract-level only | Conjecture: every 3-colourable classical knot is non-trivially R̃₃-coloured, with a virtual counterexample. |
| Thistlethwaite, *Knot tabulations and related topics* (1985), p. 68; Rickard (1984, unpublished); Edmonds and Livingston, Topology Appl. 18 (1984) | **Not read** | Known only through Livingston's citations. |

**The search for Ishikawa's full text.**
- **Places checked.**
  - Springer: a paywall, with a cookie redirect.
  - Semantic Scholar: `isOpenAccess: false`, no PDF.
  - Crossref: no abstract deposited, but the 19-item reference list was obtained.
  - The arXiv author listing for K. Ishikawa: eight papers, none on this topic.
  - The RIMS annual report and the Kyoto researcher pages: title only.
  - KAKEN 20K14309: only the title of a 2021 talk, *Generalizations of Galkin quandles and lifting properties of colorings*.
  - No author manuscript was found.
- **What could be established about Ishikawa's paper:**
  - the title, venue and dates (received 2023-03-08, published 2025-07-30);
  - one abstract sentence [V, through a summarizer]: "any coloring on the dihedral quandle of order 2m + 1 lifts to the (2m +
    1)-dimensional hyper-octahedral quandle";
  - the abstract's description: lifts carry homological information about irregular branched covers, and linking numbers in them are
    computed as quandle 2-cocycle invariants;
  - the reference list, which includes Perko 1975, Livingston 1995, Rickard 1984, Hartley–Murasugi 1977, Carter–Oshiro–Saito 2010
    and Clark et al. 2013.
- **[I]** With m = 1, the hyper-octahedral group B₃ = Z₂ ≀ S₃ ≅ Z₂ × S₄, so the main application presumably generalizes Livingston's
  Theorem 8 from S₃ = D₃ to D_{2m+1}. Whether the paper states counts, or the C[6,1]/C[6,2] equality, is **unknown**.

## Notation map

| This workspace (`CLOSED-H1-20261025-001B`) | Livingston 1995 | Perko 1975 | Clark et al. / Carter–Oshiro–Saito |
| --- | --- | --- | --- |
| φ: π → S₃ with meridians to transpositions (a Fox 3-colouring) | ρ, a representation onto S₃ | h | an R₃ colouring |
| Lift with meridian a transposition t | simple lift, ρ̃(m) = (12) | simple H | a C[6,1] = G(Z₂, [0]) colouring |
| Lift with meridian a 4-cycle c | cyclic lift, ρ̃(m) = (1324) | locally cyclic H | a C[6,2] = G(Z₂, [1]) = R̃₃ colouring |
| z_t = (12)(34) = c² | (12)(34) | — | — |
| Cocycles Z¹(π; V₄), with lifts with a fixed meridian value numbering \|Z¹\|/4 | A-conjugacy classes of lifts ↔ H¹(π; {Z₂ × Z₂}) (Prop. 1) | — | — |

**How the counts translate [C].**
- For surjective φ, B¹ ≅ V₄ acts freely by conjugation, so each A-conjugacy class has 4 lifts.
- The restriction to the meridian splits H¹ into halves: simple and cyclic.
- So "equal numbers of simple and cyclic classes" (Livingston) is equivalent to "for fixed meridian values t and c, |Z¹|/4 lifts
  each" (ours).

## Theorem by theorem

| Our statement (`CLOSED-H1-20261025-001B`) | Prior statement | Label | Status |
| --- | --- | --- | --- |
| **(a)** A transposition colouring has trivial longitude. | Livingston 1995, Theorem 6 (p. 231) lists four peripheral cases, case 3 being ρ̃(m) = (12) and ρ(l) = (12)(34). Lemma 7 (p. 231): "Case 3 cannot occur." Its proof: "In [14] it is proved that no representation of a knot group has these peripheral properties", where [14] is Edmonds–Livingston, Topology Appl. 18 (1984). | [V] | **Known** (1984). Our proof, by lifting to GL(2, 3) or the binary octahedral group, may differ from [14]'s, which was not read. |
| **(b), existence.** Every S₃ colouring has 4-cycle lifts. | Perko 1975, p. 49: "It may be conjectured that every h lifts to a locally cyclic H." Livingston 1995, Theorem 8 (p. 231): "Every surjective representation of a knot group to S₃ has a cyclic lift." Livingston, p. 230: "This was conjectured by Perko [1] and proved by Rickard [9, unpublished]." | [V] | **Known** (Rickard 1984; Livingston 1995). |
| **(b), equal counts.** Over every S₃ colouring, lifts with a fixed transposition and with a fixed 4-cycle meridian are equinumerous. | Livingston 1995, Theorem 9 (p. 231): "The number of conjugacy classes of cyclic lifts of the representation equals the number of conjugacy classes of simple lifts." His proof (p. 232) ends: "half the lifts restrict trivially (are simple) and half the lifts restrict nontrivially (are cyclic)." Livingston, p. 230, credits Thistlethwaite (1985, p. 68) with this in another form: surjective S₃ representations plus surjective simple S₄ representations equal surjective cyclic S₄ representations. | [V] for Livingston; Thistlethwaite through Livingston | **Known** (1985; 1995). The same method: a restriction map of rank one, with surjectivity onto the meridian from Theorem 8. |
| **(b), one longitude.** All 4-cycle lifts of φ share one longitude. | Livingston 1995, Corollary 10 (p. 232): "either every cyclic lift of ρ is trivial on the longitude or every cyclic lift of ρ is non-trivial on the longitude." | [V] | **Known** (1995). |
| **(c)** C[6,1] and C[6,2] colour every classical knot equally (Clark et al. 2013, Remark 6.6, for this pair). | Not stated verbatim in any source read. It follows from Livingston's Theorem 9 summed over all surjective S₃ representations. The non-surjective case, image ⟨t̄⟩, is elementary: one lift per meridian value. The identification of the quandles comes from Clark et al., Table 1, and from the isomorphism check in `CLOSED-H1-20261025-001B` (24 isomorphisms each, none crosswise). | [C] | **Settled implicitly by 1995 work.** The 2013 and 2014 papers do not cite Livingston or Thistlethwaite. Ishikawa 2025 may state it: unknown. |
| **(c), existence.** Every 3-colourable knot has a non-trivial C[6,2] colouring (Carter–Oshiro–Saito 2009). | Livingston 1995, Theorem 8. | [C] | **Settled implicitly by 1995 work.** Probably also in Ishikawa 2025 [I]. |
| Virtual knots break the equality. | Clark et al. 2013, Remark 6.8, and Carter–Oshiro–Saito, with their own example. | [V] for Clark et al. | Known. Our example (the trefoil word with one sign flipped) is another one. |

**The longitude value.**
- **[V]** Livingston, Theorem 11 (p. 232): if the 3-fold irregular branched cover is a Z₂-homology sphere, every cyclic lift is
  non-trivial on the longitude.
- **[V]** Livingston (p. 232): the knot 10₈₂, found by Perko (Invent. Math. 34, 1976), has a branch-curve linking number that is not
  2 mod 4. He writes that it has "a unique surjective S₄ representation (up to conjugacy)", which "is cyclic, and the longitude
  represents trivially".
- **Our check of 10₈₂.** The script `k10_82.py` here uses the Knot Atlas braid word BR(3, {−1, −1, −1, −1, 2, −1, 2, −1, 2, 2}) and
  the Knot Atlas PD code; the two agree. It finds:
  - two surjective S₃ colourings over a fixed meridian image;
  - 4 transposition lifts and 4 cyclic lifts each, all cyclic lifts with trivial longitude;
  - 1 surjective simple class and 2 surjective cyclic classes up to conjugacy.
- **Agreement and discrepancy.** The trivial longitude agrees with Livingston. His "unique surjective S₄ representation" does not match
  our 1 + 2 classes, which do satisfy Thistlethwaite's formula 1 + 1 = 2. The discrepancy is **unresolved**: the cause may be a
  different equivalence relation, or a different table numbering.
- **The parity rule.** The rule observed in `CLOSED-H1-20261025-001` says the 4-cycle longitude is c^{2h}, with 2^h the number of
  transposition lifts.
  - [C] It is consistent with Theorem 11 (a Z₂-homology-sphere cover gives h = 1).
  - It is consistent with our 10₈₂ computation (h = 2, trivial longitude).
  - It stays **unproved**. Livingston relates the longitude to branch-curve linking numbers mod 4 in the cover.

## `CLOSED-H1-20261025-001C` (closed manifolds with H₁ = Z/2)

- **Present in the sources read?** No. None of Livingston 1995, Perko 1975 or Clark et al. 2013 and 2014 contains a complexity
  statement. Ishikawa 2025 was not read, but its abstract has none.
- **Does it follow immediately from a cited complexity result? No.**
  - It needs the #P-hardness of counting transposition colourings of knots, which is `BOUNDED-H1-20261025-001A`, the workspace's own
    candidate result, now under Codex's review.
  - Kuperberg–Samperton cover simple targets.
  - Galindo 2026 and Samperton–Weiß 2026 need growing homology or nilpotent class 2.
- **Its topological inputs** (the B identities) are classical (Livingston 1995), and the surgery bookkeeping is routine.
- **[C]** So C's novelty rests entirely on `BOUNDED-H1-20261025-001A`.

## Consequences for the workspace's records

The two closed epics' artifacts are frozen and are **not edited**. The owner decides on corrections; the precedent is the outdated
`HARD-3D-20261025-001` record.
- **`CLOSED-H1-20261025-001B`.** Its theorem is a rediscovery: (a) is Edmonds–Livingston 1984 and Livingston's Lemma 7; (b) is
  Livingston's Theorems 8–9 and Corollary 10 (with Thistlethwaite 1985 and Rickard 1984); (c) is an easy consequence. Its
  `candidate-local-delta` label and the discovery record `CLOSED-H1-20261025-001-D001` (`frontier_change`) are outdated. The correct
  label is **known (prior art)**.
- **What survives as new [C].** The remark that the 2013 and 2009 quandle conjectures follow from 1995 work. It is a connection, of
  small magnitude.
- **`CLOSED-H1-20261025-001C`.** Unchanged in substance. Its proof should cite Livingston 1995 for the B identities. The discovery record
  `CLOSED-H1-20261025-001-D002` stands, conditional on `BOUNDED-H1-20261025-001A`.
- **The novelty scan's lesson.** The workspace scan searched quandle phrasings ("Galkin", "C[6,1]") but not the 1970s–1990s
  representation phrasing ("cyclic lift", "simple lift", "octahedral covers", "lifting representations of knot groups"). Livingston
  surfaced only through Ishikawa's reference list.

## Reproduction

`k10_82.py` reproduces the 10₈₂ numbers from both Knot Atlas presentations. It imports the frozen check of
`CLOSED-H1-20261025-001B` read-only.
