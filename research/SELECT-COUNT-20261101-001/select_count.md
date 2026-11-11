# Selection versus composition, and counted length

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a knot space is a three-regular contradiction. Results are unchanged;
the earlier text is in git history.

Epic `SELECT-COUNT-20261101-001` (program topology), 2026-11-01.

## The question

- **The request.** The owner wrote: "Yes, let's test the 5 weak four-place laws, I would also like for you to do counted length as a
  measure." That approves NATIVE-PATHS-20261101-001's recommendation and one of its alternatives.
- **(A) The selection-versus-composition test.** Does any law both select its spaces (mutual selection) and compose its knots like
  cycles (the program's criterion for native composition)? The five weak four-place classes were the only open candidates.
- **(B) Counted length.** Is the count of witnesses along the routes of the knot's contradictions a measure, and what does it measure?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | Every relation of the five weak classes yields a knot with a forcing place, directly for 13, 16 and 17, and after identifying two places for 14 and 15. Two copies sharing that place form a hub, so none composes its knots like cycles. | proof; 288 relations checked | A |
| 2 | A law with a knot whose knots compose like cycles is affine, so its count is 2^(n−r) or 0 and it has no mutual selection. Selection and cycle-like composition exclude each other for every Boolean law with a knot. | proof (KNOT-CIRCUITS Theorem 2 plus two lemmas) | A |
| 3 | A knot-free law, such as signed two-clauses, can select. Selection without knots exists only below three places. | remark (Valiant) | A |
| 4 | On a contradiction, each side of every nontrivial 2- or 3-edge cut has one count on its accepted channel values, and the two counts multiply to the amplitude. So counted length (log of the count) is additive: a measure on the decomposition. | proof; 216 cuts checked | B |
| 5 | Counted length is log 5 per Fano block (one handle) plus the log of the glue's tree-trinity number (log 2 in the twisted cube). It is m log 5 along m units, where relations keep m mod 2. | proof and computation | B |
| 6 | In rings of units cut from different spaces, the relation (parity of the number of units) and the count (product of amplitudes) vary independently. | proof; 7 rings | B |
| 7 | Counted length is unchanged by transposition and isomorphism, but not by relationally equal replacement. It is a law-intrinsic measure on substrate routes, not native extended distance. | proof and reading | B |

## Answer

- **The weak four-place laws do not supply the bridge.** None of them composes its knots like cycles. More generally, among Boolean
  laws with a knot, selection and cycle-like composition exclude each other:
  - the knot selects;
  - parity composes;
  - the affine boundary separates them.
- **Counted length works as a measure.**
  - It is additive over every cut of a contradiction and fixed by the law and the substrate.
  - It counts handles and glue, and it sees what the relations hide.
  - It is a measure on the routes of the declared substrate, not a native distance, because those routes are not native paths.

## Reading

- **Two layers.**
  - The relational layer (K1–K3, witnesses quantified away) carries emergence and decides failure, and it carries one bit along a
    route.
  - The counting layer carries magnitude: how much each part hides.
  - The knot's contradictions separate the two cleanly. The relation counts parts mod 2; the count counts handles.
- **Selection lives where composition ends.**
  - At two values, composing like cycles needs linearity (an affine law), and linearity makes counting easy.
  - The knot's hard count therefore rules out the linearity that cycle-like composition needs.
  - Parity composes because it is linear, and the same linearity makes its counts easy.
- **Ties to the owner's intuitions.**
  - Everything relational is kept to one bit per route.
  - Magnitude enters only by counting what relations hide.
  - Handles (log 5) and glue (log 2) contribute incommensurable amounts.

## Literature

- **Ours.**
  - KNOT-CIRCUITS Theorem 2 and Proposition 3.
  - PINNING C (mutual selection).
  - THREEFOLD-AMPLITUDE (amplitude, point lemma, one amplitude, factorization, five per handle).
  - THREEFOLD-SURFACES (handles).
- **Classical.** Post's lattice, Schaefer, Valiant (#2SAT), the affine count, and exact counting by variable elimination.
- **New here.** The forcing-place hubs, the exclusion statement, factorization across 2-edge cuts, the rings, and the counted-length
  reading. They are elementary, and folklore risk is moderate.

## Pending the owner

- **From NATIVE-PATHS.**
  - The SELECTION-NOTE erratum.
  - Marking `KNOT-COMPOSE-20261101-001-D001` superseded.
- **New.** Whether counted length should ever be admitted as a native magnitude. That would change the canonical doctrine. It is not
  needed now, because native paths are absent.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — selection versus composition; counted length | **Status:** Successful | (A) The weak classes are settled for composition, and the exclusion is proved for every Boolean law with a knot. (B) Counted length is an additive, law-intrinsic measure that counts handles. Whether the weak classes ever fail stays open but no longer matters for the bridge. |
| Local direction — the bridge among Boolean laws | Exhausted (proved) | No Boolean law with a knot both selects and composes like cycles. |
| Broader exploration — laws on more than two values | Known lead | KNOT-CIRCUITS Theorem 1: Mal'tsev laws compose like cycles exactly when every subalgebra has one maximal congruence. Mal'tsev failures are decidable in polynomial time (Bulatov–Dalmau). Counting is #P-hard exactly when the law is not strongly balanced (Dyer–Richerby). These three facts could meet in one law. |
| Long-term goal — the ladder from first emergence to composed topology and distance | Obstruction sharpened; capability gained | With bits, the selecting knot cannot be the composing law. Counting supplies a canonical magnitude, but not yet a native distance. |
| Next recommendation — values beyond two | **Next step:** Continue. Search for a law on more than two values that both selects and composes like cycles: Mal'tsev, one maximal congruence per subalgebra, and not strongly balanced, with knots and a failing class. First discriminator: test the known cycle-composing laws (Z_{p^k}, S3, D_p, the Latin laws of KNOT-IMAGES) for strong balance, then search small Mal'tsev algebras on three and four values. | If such a law exists, it is the first law that both selects its spaces and composes natively; its failures are recognisable, its count hard, and its routes native. If cycle-like composition forces balance, a general exclusion theorem follows. Alternatives: whether the weak four-place classes ever fail (1/3); the note's erratum and reissue (1/3). |
| Interest — values beyond two | **2/3 — Promising** | Three classical criteria meet in one finite search. Main uncertainty: cycle-like composition may force balance, and the program's base thesis is Boolean, so a positive answer would live beyond bits. |
| Execution — that action | Deferred to the owner | No new epic opened. Bound: domains of at most four values; stop if the balance test cannot be decided on the candidate laws. |
