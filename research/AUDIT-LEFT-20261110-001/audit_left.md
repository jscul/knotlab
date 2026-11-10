# An audit of the left-pigeon bound

Epic `AUDIT-LEFT-20261110-001` (program complexity), 2026-11-10.

## The question

- **Where it comes from.** `WIDE-LEFT-20261110-001` wrote, in one session, a proof that every dag-like Res(⊕) refutation of the binary
  left-pigeon principle (with 2n pigeons, and so with n + 1) has exp(Ω(n/log⁵ n)) lines, and recommended a note for review (sub-goal
  B116). The coordinator confirmed B116 at max effort as an audit, not a write-up: reword every published sentence as a proof written
  until the audit is done; re-derive the proof with every constant explicit; attack the spare-row lemma, the density count and the
  transfer with fresh reviewers who have not seen the proof; say which of Braun's lemmas are used and which the Lean replay covers;
  check against known upper bounds and small computed sizes; stop when the note survives or names the failing step.
- **The question.** Does the bound survive, and is it what it was said to be?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Every step holds.** Re-derived from Braun's stated results with every constant explicit, and attacked by four fresh reviewers with their own derivations and code, the transfer, the reduction, the spare-row lemma and the density count all hold; the density constant is about five times better than stated, and the bound says nothing below n = 2^48. | proved (V1, conditional on A55) | A |
| 2 | **The Lean replay covers every lemma used.** All eight of Braun's results the proof uses are in the import closure of the aggregate whose fresh-kernel replay passed in October (it imports the generic criterion), and their Lean statements cover the uses: any number of rows, any tagging of a cube. The program's own steps are not formalized. | checked against the sources | A |
| 3 | **Not new in substance.** The 2n-pigeon formula is Pudlák and Thapen's rWPHP_n, and Pang's degree–size relation for Res(⊕) (arXiv 2610.00837, 30 September 2026) gives exp(Ω(n)) for it and for the n + 1 pigeon principle in a few lines, by the affine substitution into graph FPHP that this proof's decoder already is. The same preprint had already improved the program's own more-pigeons bound for linearly many pigeons. | literature, checked in the sources | A |

## Answer

The proof survives: no reviewer and no check found a failing step, and its one presentation gap (a lemma whose side conditions do not
build its stars, which the theorem builds separately) changes nothing. But the result is not what it was said to be. It is a correct,
longer route to a weaker form of a bound that follows in a page from Pang's degree–size relation, for a formula Pudlák and Thapen defined
in 2017. What is left of it is a statement about Braun's criterion: a separated space of useful density for a second formula, which
Braun's Remark 9.3 said no one had.

## Scope

- **The bound itself** stays V1 and conditional on A55; the reviewers are fresh instances of the same model, so this is not an
  independent human review.
- **Nothing reaches the knot sphere's count.** Pang's relation needs F₂ degree well past √n, and the count's is O(√n), as the cap of
  `RES-XOR-COUNT-20261110-001A` already said for Braun's criterion.
- **Not an algorithm.** A lower bound on proof size; the publication hold does not apply.

## Reading

**Interpretation, not a theorem.**
- **For Res(⊕), degree is the whole story here.** Braun's criterion is capped at exp(d²/(36v)) by the PC degree d, and Pang's relation
  gives exp(Ω(D²/n)) from it: both routes see a formula only through its F₂ degree. The decoder line spent four epics building a space
  the criterion could use; Pang's relation needs only the degree, which for these formulas is linear.

## Lag cutoffs and census-only claims

- **No lag cutoff;** not a dynamics epic.
- **Census-only.** The reviewers' exact checks of the spare-row lemma (dim(U_0 ∩ K_k) = 0 at k = 1, 2 up to 32 holes) and of the
  reduction's pieces (l = 2 to 5) are finite; the proof covers all n. The minimum tree-like sizes are at n = 2 only.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| The density count (A, check 2) | l = 201 to 1,000 (checked to 200) | pass: at least 5.17 times 0.005·k/l² |
| The exact density (A, check 2) | l = 31, 32 (checked to 30) | pass: 4.93 and 4.94 times |
| The stars' code (A, check 3) | lengths 13 and 14 (checked to 12) | pass: distance 3 |

The script is `stress_test.py` beside this note, its output `stress_test.json`. It ran in under a second once its exact sum was
computed by prefix sums; a first, naive version was stopped after 16 minutes with no result.

## Literature and provenance

- **Sources.** Braun, arXiv 2609.23015 and its Lean development at commit 8904bf09; Pang, arXiv 2610.00837 (v1 and v2, read in full
  for Theorem 1.1, Corollary 1.3 and Theorem 7.2); Alekseev, Gryaznov, Itsykson, Pitassi, Robere and Tzameret, ECCC TR26-316
  (Theorem 3.2, Corollary 6.14 and its comparison with Pang); Pudlák and Thapen, ECCC TR16-175 (§3.3); Göös et al., *J. ACM*
  2024, and "Further collapses in TFNP" (CCC 2022); Bonacina and Thapen, ECCC TR22-089; Dantchev, Galesi, Ghani and Martin, *SIAM J.
  Comput.* 2024; Mikša and Nordström, *J. ACM* 2024.
- **Classification.** The audit is new; the result it audits is known in substance (conclusion 3). Two corrections are logged.

## Workspace assumptions

- **Relied on.** A55 (Braun's preprint is correct).
- **Changed.** A55 gains evidence, status unchanged: every lemma it lists is in the replayed import closure, and ECCC TR26-316 re-proves
  the main theorem.

## Ratio

Since the epic opened:
- **Substantive.** The re-derivation and its checks (A), four adversarial reviews, the literature check against the sources, one
  stress test.
- **Administrative.** The rewording correction, two novelty corrections, this note and the closure.

## Pending the owner

- **Whether to share anything.** The left-pigeon bound is no longer worth sending as a result; the more-pigeons note
  (`BPHP-MORE-PIGEONS-NOTE-20261019-001`) is worth less now that Pang's preprint and TR26-316 exist. Sharing stays the owner's call.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — an audit of the left-pigeon bound | **Status:** Successful | The note names no failing step; it finds the result known in substance |
| Local direction — the decoder route | Full pivot | Finished, and superseded by Pang's degree–size relation |
| Broader exploration — G3 | Known alternatives | Cutting planes on the count (B82), the parity reduction from PIGEON (B101), a native contradiction with high degree (B121) |
| Long-term goal — G3 Hardness at three places | No demonstrated advance | The bound adds nothing a known theorem does not give more strongly; the count is untouched |

**Corrections:** three, none a block: the bound's headline sentences worded beyond their evidence (reworded first, cac87be1d), its
novelty (the formula is rWPHP; Pang gives more), and the more-pigeons bound's novelty (Pang was earlier for linearly many pigeons).
**Goals:** a G3 checkpoint (no demonstrated advance); B116 taken; sub-goal B121 added. **Assumptions:** A55 gains evidence, status
unchanged.

- **What the attempt leaves open.** An expert's reading of Braun's generic criterion; whether any native contradiction has F₂ degree
  past √n (B121).

**Next step:** Research directions — none started tonight; the owner rested the project after the current epics.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A parity reduction from PIGEON to SINK (sub-goal B101, G3) | 3/3 — Barrier | 1/3 — Stated | As recorded | Recommended |
| 2 | Cutting planes on the count (sub-goal B82, G3) | 3/3 — Barrier | 1/3 — Stated | As recorded | Alternative · deferred |
| 3 | A native contradiction with degree past the square root (sub-goal B121, G3 with G2) | 3/3 — Barrier | 1/3 — Stated | List the native contradictions with a law and bound each one's F₂ degree by its width; compute exact degrees on the smallest cases → a native family with degree ≥ n^{1/2+ε}, or the obstruction that native contradictions live on surfaces | Alternative · deferred |

1. **The parity reduction.** Payoff 3: with Braun's bit-PHP bound it would reach the count in Res(⊕). Concreteness 1. Recommended
   first because the coordinator named B101 or B82 as the line's next step and B101 is the more direct test of the count.
2. **Cutting planes.** As in `COUNT-SYSTEMS-20261110-001`.
3. **High degree.** Payoff 3: Pang's relation would turn it into the first dag-like Res(⊕) bound for a native contradiction.
   Concreteness 1: no candidate, and native networks are blind to three dimensions (`HUB-DIMENSION-20261024-001`).

**Recommendation.** Research directions, B101 recommended, for the coordinator to confirm when work resumes.

## Final report as sent

B116 is closed. The audit found no failing step, but the result turned out not to be new in substance.

Every step of the left-pigeon bound held up: the transfer to n + 1 pigeons, the reduction, the spare-row lemma and the density count. I re-derived each one with explicit constants, and four fresh reviewers attacked them using their own code without seeing my proof. All eight of Braun's lemmas the proof uses were covered by the fresh-kernel Lean replay we ran in October.

The problem is novelty, which I checked in the sources myself. The 2n-pigeon formula is Pudlák and Thapen's rWPHP (2017). Pang's degree–size relation (arXiv 2610.00837, 30 September) gives exp(Ω(n)) for it in a few lines, which beats our exp(Ω(n/log⁵ n)). That same preprint had already beaten our October more-pigeons bound for linearly many pigeons. I logged both as corrections (Not a block), and the public records now carry qualifications.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: audit of the left-pigeon bound | Successful | No failing step; the result is known in substance |
| Local direction: the decoder route | Full pivot | Finished, and superseded by Pang's relation |
| Broader exploration: G3 | Known alternatives | Cutting planes (B82), parity reduction (B101), a high-degree native contradiction (B121) |
| Long-term goal: G3 | No demonstrated advance | Nothing beyond what a known theorem gives more strongly; the sphere's count is untouched |

**Next step:** Research directions, B101 recommended. Nothing is started tonight, as you asked.

| # | Direction | Payoff | Concreteness | First step → stop when |
| --- | --- | --- | --- | --- |
| 1 | Parity reduction from PIGEON to SINK (B101) | 3/3 | 1/3 | As recorded |
| 2 | Cutting planes on the count (B82) | 3/3 | 1/3 | As recorded |
| 3 | Native contradiction with F₂ degree past √n (B121, new) | 3/3 | 1/3 | Bound each native contradiction's degree by its width and compute the smallest cases → a family past √n, or proof that native contradictions live on surfaces |

**Corrections:** three, none a block: the rewording, this bound's novelty, and the more-pigeons novelty. **Goals:** G3 checkpoint (no demonstrated advance); B116 taken; B121 added. **Assumptions:** A55 gains evidence (TR26-316 re-proves Braun's theorem); its status is unchanged.
**Basket:** B101 (3/3, 1/3), B121 (3/3, 1/3), B82 (3/3, 1/3); none taken. The RING-LAW-S1 stress test is still running and stays registered as pending. Nothing went outside the repo; whether to share anything is your call, though the left-pigeon bound is no longer worth sending as a result.
