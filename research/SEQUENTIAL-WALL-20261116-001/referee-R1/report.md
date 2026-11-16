# Referee report SEQUENTIAL-WALL-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.** Theorems 1 to 6 hold and are labelled fairly. Theorem 5's table recomputes exactly, the
pre-registration and frozen code are intact, and the measurements reproduce within sampling noise in fresh code. The fixes are wording:
- Theorem 4's condition is dropped in three summaries, one of them public.
- "Never in NL or L" should read "never NL- or L-complete".
- One sentence of Theorem 4(c) attaches several-way demand to phases instead of hardness.
- P2a's "held" rests on the last, 8-sample size.

**What holds.**
- **Theorem 1** (phase = least Strahler number): both directions were checked step by step. It is the Boolean case of
  Esparza–Kiefer–Luttenberger, as labelled.
- **Theorem 3**, the owner's priority. The minimal-tree argument is correct (§2).
- **Theorems 2, 4(a), 4(b) and 6.** The arguments hold as written.
- **Theorem 5.** The referee's own enumeration gives exactly 34 three-place knots: 2 AC⁰, 2 ⊕L-complete, 14 P-complete and 16
  NP-complete. Every row's closure flags match the table, and all 14 pp-definitions of the atom or its dual are valid (§4).
- **The not-all-equal gadget** is correct by the referee's case analysis.
- **The pre-registration.** It was frozen in cb6144f52 (21:55 UTC) before the run (21:55 to 22:18 UTC), unchanged since. The five
  frozen code files match their contract hashes.

**What needs fixing.**
- **Theorem 4's condition.** "The wall needs both reuse and several-way demand" is stated without "unless P = NC / P = NL" in
  KNOT_INTUITION, RESEARCH_GOALS and the public INTUITIONS glossary. The decision note and proof state it conditionally.
  **Narrowing** (wording).
- **"Never in NL or L"** (proof, decision note, OBJECTS row) is literally false: the two AC⁰ laws are in L. Read "never NL-complete
  or L-complete", which is what Baker–Pixley gives. **Not a block** (wording).
- **Theorem 4(c)'s last sentence.** "Such patterns need … several-way demand (unless P = NL)" refers to patterns needing many
  phases, but the pyramid, given just above, has many phases and no several-way demand. The sentence is right only for hard
  (P-hard) families. **Not a block** (wording).

**How the work was split.**
- **The referee.** Read the proof and the note line by line, wrote `referee_own_knots.py` for Theorem 5, checked the
  pre-registration, the code hashes and the public wording, and ran one literature search.
- **One Claude helper.** Recomputed the rounds and phases scaling, Theorem 1 by brute force, the fringe and the circuits, with fresh
  code (`NOTES.md`).
- **Codex** was not used. **The advisor** was not consulted.

## 1. Theorem 1 and its corollary

- **σ ≥ phase**, by induction on trees. In the case i < j, a ∈ P_(j−1) turns the atom into the rule b → v in phase j. In the case
  i = j, b ∈ P_i is a source in phase i + 1.
- **phase ≥ σ.** Along a phase-t path, each step combines a tree of number at most t with a side tree of number at most t − 1, so the
  number stays at most t. Right.
- **The forcing law is Boolean Newton iteration.** The linearisation of a·b at ν reads b → c when a ∈ ν. The EKL attribution is fair.
- **The corollary** (polylogarithmic phases give NC) is right.

**Not a block.**

## 2. Theorem 3 (the owner's priority)

**The argument is correct.**
- **The minimal tree.** In a minimal derivation tree no label repeats on a path. Two equal labels at incomparable nodes force equal,
  distinct, incomparable parents: the unique atom in which the label demands, and the atom's demanders are distinct.
- **The ascent.** Repeating this gives an endless ascent, since neither node can ever be the root. That already contradicts
  finiteness. The proof's split by equal and unequal depths reaches the same contradiction by a longer road.
- **Hence** all labels are distinct, the leaves are distinct held distinctions, fringe ≤ |H| and σ ≤ log₂ |H|.

**Not a block.** An optional simplification: the depth split can be dropped.

## 3. Theorems 2, 4 and 6

- **Theorem 2(a)** is the standard leaf bound, and (b) is pigeonhole at the parting node of two equal held leaves. Right.
- **Theorem 4(a).** With a unique demanding atom, the derivation tree is forced to be the unfolding, so forcing is two reachability
  questions in coNL = NL. Right.
- **Theorem 4(c)'s last sentence** (the third fix above). Patterns with more than log₂ |H| phases need reuse unconditionally, by
  (b). They need *not* have several-way demand: the pyramid. Several-way demand is needed only by P-hard families, unless P = NL.
- **Theorem 6.** On acyclic patterns the dual law cannot stall: the first unfound unforced distinction in the order has every atom
  dead, so it is a seed. Running both laws and stopping at the first to finish is therefore sound.
- **The NP-completeness of not-all-equal** is right. **Propagation:**
  - In NAE(x, y, g₀) with x, y ∈ {1, unset} and g₀ ∈ {0, unset}, the only firing is x = y = 1 ⇒ g₀ = 0.
  - In NAE(g₀, F, g) the only firing is g₀ = F = 0 ⇒ g = 1.
  - The OR gadget is alike.
  - So the gadget is correct, and P-complete with two held values.

## 4. Theorem 5, recomputed (`referee_own_knots.py`, `referee_own_knots.json`)

**The code.** Fresh. It reads the study's `knots_table.json` only as the claim under test.
- It enumerates every relation on three places that is nonempty, not full and free on every pair of places: exactly **34**.
- It tests closure under and, or, majority and minority, and classifies with constants. The cases:
  - majority: none of the 34;
  - minority: parity;
  - and or or: Horn or dual-Horn, P-complete except the two single-sign clauses;
  - none of the four: NP-complete (Schaefer with constants).
- It replays each pp-definition semantically, with the hidden names quantified.

**Result.**
- **The table.** 2 / 2 / 14 / 16 exactly, with 0 rows whose class or closure flags differ.
- **The definitions.** All 14 define the atom or its dual. None of them needs a held value: variable identification and one hidden
  distinction suffice. So the P-hardness holds even without the held values the table allows.

**The labels are fair.** "Known (Schaefer 1978; Allender et al. 2009), applied here" is right. P membership is Horn-SAT; P-hardness
is by the definitions; AC⁰ for the single-sign clauses is by inspection (a clause fails only when all three members are held
against it); ⊕L is the affine case.

**The wording fix.** "Never in NL or L" should be "never NL- or L-complete": no knot is majority-closed, but AC⁰ ⊆ L.

## 5. Known versus new

**The theorem labels.**
- **Fair:**
  - Theorem 1, known (EKL 2010; Esparza, Luttenberger and Schlund 2014);
  - Theorem 2(a), known (Ullman–Van Gelder);
  - Theorem 3, known-with-delta (formulas are in NC¹);
  - Theorem 5, known;
  - the NAE gadget, known-with-delta (Kasif 1990);
  - Theorem 6, known-with-delta (dual Newton; two-sided circuit evaluation is folklore).
- **The decision note.** "As theory … a restatement" and "adds no algorithm" are accurate.

**The measurements.** "What is new is measured" is fair as far as I could check.
- **What is expected in kind.** n^(1/3) rounds at the jump is what a mean-field saddle-node bottleneck gives: crossing time ε^(−1/2)
  in a critical window ε ~ n^(−2/3). Logarithmic phases at a tangency is Kiefer–Luttenberger–Esparza 2007, which the note cites.
- **What I could not find.** A web search found no statement of the round count at the jump for this random atom model (closest:
  Morrison–Noel, EJP 2021, on hypergraph bootstrap thresholds). So the measured exponents are plausibly new numbers for a known kind
  of behaviour.
- **Not verified.** Whether a physics or bootstrap-percolation paper already gives them.

## 6. The measurements, recomputed (helper; `NOTES.md`)

**The code.** All of it is fresh: generator, rounds, forcing law, exact Strahler numbers, fringe, circuits and dual law. The study's
`atoms.py` was run only as the code under test, and it agrees with the helper's at every distinction.

| Check | Size | Result |
| --- | --- | --- |
| Theorem 1 by brute force: phase against σ, by enumeration of derivation-tree values and by Knuth's generalized Dijkstra, against relaxation | all 65,536 patterns at n = 4, 50,000 random at n = 5..12, pyramids to h = 6, and σ ≤ 13 on the jump runs | 0 failures in 115,542 cases |
| Jump readings: median R* | n = 2^10, 2^12, 2^14, 2^16 (40, 40, 30, 20 samples) and 2^18 (12) | 32, 52.5, 86, 142 against 34, 55, 86, 128 |
| Jump readings: median P* | same | 6, 7, 9, 10 against 6, 8, 9, 10 |
| Readings at k* − 1, k*/n, and α = 0.03 and 0.2 | as above | agree; 2 of 74 Mann–Whitney tests give p < 0.05, as chance predicts |
| Fringe at k*: median log₂ fringe | as above | 10.66, 12.90, 15.17, 17.79 against 10.8, 13.2, 15.2, 17.4; σ ≤ log₂ fringe everywhere |
| Circuits: atom encoding | every input of 240 small circuits | equal at every gate |
| Layered circuits, width 1024 (100 samples): median largest output Strahler number | d = 8, 16, 32, 64 | 4, 5, 6, 9 against 4, 5, 7, 9; at d = 32 the samples split 52 : 45 between 6 and 7, so a 10-sample median is noisy |
| Unlayered circuits | G = 1,024 and 4,096 | 2 and 3, as reported |
| Dual law (Theorem 6) | 30,000 random acyclic patterns | (a) holds; dual phases equal the generalized Strahler number by a DP; a mutant without the +1 disagrees 24,718 times; min(P, P_dual) on layered circuits 5, 6, 8, as reported |

**The slopes.**
- **Over 2^10..2^16.** R* gives 0.358 [0.32, 0.38], against 0.319 on the study's own data over the same range. P* gives 0.70
  [0.55, 0.78] per doubling, against 0.65; the reported 0.57 is over 2^10..2^20.
- **P2a's "held" is fragile.** The 0.302 in [0.29, 0.37] is the fit over 2^14..2^20.
  - Over 2^14..2^18 the study's own medians (86, 128, 176) give 0.258, outside the window.
  - So the verdict rests on the 8-sample point at 2^20 (312.5), whose bootstrap interval for the fit is [0.27, 0.36].
  - The helper's fit over 2^10..2^18 is 0.334 [0.31, 0.35].
  - So the exponent is about 0.30 to 0.36 and n^(1/3) remains plausible, but "held" should say it rests on the last size.
  - **Narrowing.**

**Verdict.** The measurements reproduce within sampling noise. **Not a block**, except the P2a wording.

## 7. Conditional wording (Theorem 4), checked everywhere

| Where | Text | Conditional? |
| --- | --- | --- |
| Decision note, "The answer" | "(Theorem 4, conditional on P ≠ NC and P ≠ NL)" | yes |
| Proof, Theorem 4(c) and "What is not claimed" | "unless P = NC … unless P = NL"; "conditional on P ≠ NC or P ≠ NL" | yes |
| docs/KNOT_INTUITION.md, 2026-11-16 entry | "the wall needs both reuse and several-way demand (known and known-with-delta)" | **no** |
| docs/RESEARCH_GOALS.md, G3 stands-on | "so the wall needs both reuse and several-way demand" | **no** |
| publication/knotlab/INTUITIONS.md, glossary "Reused; demanded several ways; rejoining" (public) | "the sequential wall needs both reuse and several-way demand" | **no** |
| docs/OBJECTS.md rows | no Theorem 4 statement | n/a |

## Fixes for the thread (listed for the owner, not folded in)

1. **Add Theorem 4's condition in the three places above:** "unless P = NC (reuse) and P = NL (several-way demand)". **Narrowing**
   (wording), a correction for docs/CORRECTIONS.md, since the glossary is public.
2. **"Never in NL or L" → "never NL- or L-complete"** in the proof (Theorem 5), the decision note and the OBJECTS row. **Not a
   block.**
3. **Theorem 4(c)'s last sentence.** Say "a P-hard family needs reuse (unless P = NC) and several-way demand (unless P = NL); many
   phases alone need only reuse (Theorem 3)". **Not a block.**
4. **P2a's verdict.** It holds only with the 8-sample 2^20 point: the study's own medians over 2^14..2^18 give 0.258, outside
   [0.29, 0.37]. Say so beside "held", for example "held (0.302 over 2^14..2^20; 0.258 without 2^20; bootstrap [0.27, 0.36])".
   **Narrowing.**

## Files

- `referee_own_knots.py` and `referee_own_knots.json`: the referee's own Theorem 5 check.
- The helper's `referee_*` scripts and outputs, with `NOTES.md`.
