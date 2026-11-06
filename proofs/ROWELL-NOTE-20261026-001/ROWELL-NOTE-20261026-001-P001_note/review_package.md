# External-review package

**Note:** "Counting homomorphisms from knot groups to solvable groups can be #P-hard" (Prespatial Labs, draft of
26 October 2026). PDF: `note/rowell_note.pdf`; source: `note/rowell_note.tex`.

**Status.** Prepared with Claude (Anthropic). Two AI reviews of the underlying proofs have been done; no human expert has
reviewed anything. Nothing has been sent; whether and to whom to send it is the repository owner's decision.

## 1. The claims and their evidence

Paths are relative to the repository root; every proof directory is `proofs/<ticket>/<ticket>-P001_<slug>/` with `proof.md`,
`check.py` and the frozen `result.json`.

| # | Claim | Proved in | Check (runtime) | Independent replay | Novelty and folklore risk |
| --- | --- | --- | --- | --- | --- |
| 0 | On links, H_L(D_n) is #P-hard for n ≥ 3 odd (S₃ = D₃): local torus knots isolate the rotation sector, 2-cables weight it, giving n^(2m) Z_Γ(n, 1); polynomial for metabelian G with boundedly many components | this note, Proposition 1 and Lemma 6; `links/` | about 3 min (`links/run_all.py`) | a separately written brute force of the two smallest instances (228, 1188) | Candidate new; medium (standard tools, no statement found) |
| 1 | Bicycle law: transposition colourings of tripled alternating diagrams = Σ_φ 2^(c + dim B); 12-state model M = J − 2N | `BOUNDED-H1-20261025-001A` | 36 s | `CLOSED-H1-20261025-001A` replayed it | New as far as found; low–medium |
| 2 | Counting transposition colourings of knots by S₄ is #P-hard (series-parallel gadgets, odd tree counts, interpolation to P(H, 12)) | same | same | same | New as far as found; low–medium |
| 3 | H_K(S₄) = 4 + R + 2T, R polynomial; H_K(GL(2,3)) = H_K(2O) = 2 H_K(S₄) | `SL23-BOUNDED-20261025-001B` (uses Livingston 1995, Thm. 9, re-proved in `CLOSED-H1-20261025-001B`) | 2 s, 0.4 s | — | Routine given claim 2; high folklore risk for the identities, none for the consequence |
| 4 | Abelian-by-nilpotent targets are polynomial on knot groups | `BOUNDED-H1-20261025-001B` | 0.6 s | — | Folklore |
| 5 | S₄ is the smallest group with #P-hard knot counting (unless FP = #P) | this note, Theorem 2; check part 3 | 2 s | — | Short consequence of 2–4 and standard group theory |
| 6 | Count over ψ = cocycle factors × kernel count of the twisted triple product; 1 + 128·4^d·N for UT₃(F₄) ⋊ C₃ | `CORRECTIONS-20261026-001A`, `COPRIME-CLASS2-20261026-001B` | 20 s, 37 s | `COPRIME-CLASS2-20261026-001A/replay` (fresh code) | Standard obstruction theory; high folklore risk |
| 7 | Borromean (Y-graph) surgery with leaves in ker ψ adds ε Σ sgn(σ) Π λ to every eigen-component | `CORRECTIONS-20261026-001C`, `COPRIME-CLASS2-20261026-001B` | 3 s | 894 extra configurations in `COPRIME-CLASS2-20261026-001A` | Finite-cover analogue of Moussard 2017; medium–high |
| 8 | Pure leaves (needs ψ onto) | `COPRIME-CLASS2-20261026-001B` (d), with the follow-up review's counterexample for ψ not onto | — | follow-up review | Routine |
| 9 | Four gadget patterns give Potts at (q³, q² − 1) or (q², q − 1) | `COPRIME-CLASS2-20261026-001D` §1, `CORRECTIONS-20261026-001D` Lemma 6 | 59 s, 45 s | follow-up review (30 graph cases, separate code) | Candidate new; elementary |
| 10 | UT₃(F₄) ⋊ C₃ #P-hard on 3-surgeries; knot-group count = surgery count + 63 | `CORRECTIONS-20261026-001D` | 45 s | follow-up review (the +63 identity on six knots) | Candidate new; medium |
| 11 | Heisenberg dichotomy (p odd): polynomial without a hard pair, #P-hard with one, on knot groups and r-surgeries | `COPRIME-CLASS2-20261026-001C`, `COPRIME-CLASS2-20261026-001D` | 0.2 s, 59 s | follow-up review (gadgets, knot-group formula) | Candidate new; medium |
| 12 | Rowell's Conjecture 3.2(b) fails unless FP = #P: on links for the odd dihedral groups, on knots for the groups of 2–4 and 10–11 | Corollary 5 | — | follow-up review confirmed the wording of the conjecture and the knot bridge | No earlier refutation found |
| 13 | Approximating H_K(UT₃(F₄) ⋊ C₃) is #BIS-hard (one query, known constant, Goldberg–Jerrum at Q = 64) | Proposition 18; scouting lane `NEXT-DIRECTION-SCAN-20261026-001B` | 11 s (lane script) | the lane's scripts were rerun in a temporary mirror | Direct consequence; low |

The follow-up review is the untracked file set `research/COPRIME-CLASS2-20261026-001/codex_followup_review_20261026.*` in the
owner's working tree (not committed by this task). The first review is committed in `research/COPRIME-CLASS2-20261026-001A/`.

## 2. How to replay

From the repository root, with Python 3.9 or later (standard library only) and, for the PDF, a TeX installation:

```bash
cd proofs/ROWELL-NOTE-20261026-001/ROWELL-NOTE-20261026-001-P001_note
python3 -B replay.py          # reruns the ten cited checks in a temporary copy; about 200 s; prints ALL OK
(cd links && python3 -B run_all.py)   # the link checks; needs numpy (the workspace .venv is used if present); about 3 min
python3 -B check.py           # ties the note to both replays and recomputes the note's own facts; about 3 s
```

`replay.py` never writes into the repository unless given `--write` (then only `replay_result.json` here). Expected output of
`replay.py`:

```text
ok  BOUNDED-H1-20261025-001A      ~36 s  ALL OK
ok  BOUNDED-H1-20261025-001B       ~1 s  ALL OK
ok  CLOSED-H1-20261025-001B        ~0 s  ALL OK
ok  SL23-BOUNDED-20261025-001B     ~2 s  ALL OK
ok  CORRECTIONS-20261026-001A     ~20 s  ALL OK
ok  CORRECTIONS-20261026-001C      ~3 s  ALL OK
ok  CORRECTIONS-20261026-001D     ~45 s  ALL OK
ok  COPRIME-CLASS2-20261026-001B  ~37 s  ALL OK
ok  COPRIME-CLASS2-20261026-001C   ~0 s  ALL OK
ok  COPRIME-CLASS2-20261026-001D  ~59 s  ALL OK
ALL OK
```

Each row also confirms that the fresh `result.json` equals the frozen one outside timing fields.

## 3. Questions for a reviewer

In order of importance:

1. **Prior art.** Is #P-hardness of H_L(G) or H_K(G) known for any finite solvable G? Has Rowell's Conjecture 3.2(b) been
   refuted, or discussed after Kuperberg–Samperton 2018 §5.3? Is the link reduction of Proposition 1 (local knots plus
   cables) known for S₃ or dihedral groups?
2. **The S₄ argument.** Is the bicycle law (Proposition 10) correct as stated, in particular the claim that the lifts over a
   fixed potential form a nonempty affine space of dimension c(H_φ) + dim B(H_φ)? Is it known, perhaps for the
   transposition quandle of S₄ or as a Potts(12, ½) identity?
3. **Livingston's identity.** Is Theorem 9 of Livingston 1995 applied correctly to all knots, including Fox colourings with
   cyclic image, so that H_K(S₄) = 4 + R + 2T?
4. **Steering.** Is the finite-cover formula (Proposition 15) a direct consequence of Massuyeau's Lemma 3.2 applied in the
   r-fold cover, and is the comparison with Moussard 2017 fair?
5. **Realization.** Are Habiro's Props. 3.3–3.4 applied correctly when the knot is forgotten, including the claim that the
   Seifert framing, and hence the surgery coefficient, is preserved? Are disjoint parallel caps enough when a private
   coordinate is reused by several terms?
6. **Knot exteriors.** In Theorem 4(2), is the transfer from r-surgeries to knot exteriors complete, in particular for terms
   in which one character is trivial on the meridian?
7. **Approximate counting.** Proposition 18 gives #BIS-hardness for UT₃(F₄) ⋊ C₃. Can the Heisenberg reductions be made
   approximation-preserving (two-sided leaves), and can S₄ escape the ferromagnetic region with other tangles?
8. **Links, beyond dihedral groups.** Is the cabling argument of Remark 7 (closed counts from link counts for centreless G),
   combined with Galindo 2026, sound? What is the complexity of H_L(G) for nilpotent G, where the count depends only on the
   linking matrix (for D₄ and Q₈ it is 4^c Σ_S 4^(−cutrank(S)))?

## 4. Known limitations

- The general construction (bands and eigenprojectors) has not been run end to end; the complete graph-to-knot instances use
  leaf configurations found by search, equal to the gadget up to a change of basis. Pattern 1 (needs r ≥ 6) has steering
  checks but no complete instance.
- Extension fields other than F₄, and q = 2^k in patterns 2 and 4, are not covered.
- The converse of the general easy side (hypotheses (K)) is proved only for Heisenberg groups.
- Closed 3-manifolds with bounded homology are covered for the Heisenberg family and for S₄ (H₁ = Z/2, elsewhere in the
  repository), not for GL(2,3) and 2O.
- All hardness statements are under polynomial-time Turing reductions and are conditional: they refute polynomial-time
  algorithms only unless FP = #P.
