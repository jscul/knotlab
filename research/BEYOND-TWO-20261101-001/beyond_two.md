# Selection and composition beyond two values

Epic `BEYOND-TWO-20261101-001` (program topology), 2026-11-01.

## The question

- **The approval.** The owner said "Yes, please continue" to SELECT-COUNT-20261101-001's recommendation: look for a law on three or
  four values that is Mal'tsev, composes like cycles, and is hard to count, so that it would both select and compose.
- **The first check.** The known laws that compose like cycles.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | The laws known to compose like cycles are coset laws, whose fibres all have one size, so they count easily. None selects. | proof; 160 random systems | A |
| 2 | Blurring a law (doubling a value) keeps its failures and circuits, and so its cycle-like composition, and weights its counts. | proof; 240 random systems | B |
| 3 | Every Mal'tsev law on three values composes like cycles: all 531441 Mal'tsev operations have at most one nontrivial congruence. | proof and enumeration | B |
| 4 | Blurred parity (three values) and blurred Z3 (four values) compose like cycles, fail recognisably and count #P-complete (count matrices of rank 2 and 3). So the formal bridge exists from three values on, and the two-value exclusion is exactly two-valued. | proof | B |
| 5 | On connected cubic substrates: the knot fails exactly on Pfaffian ones, always globally; parity (and blurred parity) exactly where the number of perfect matchings is even, never globally; Z3 (and blurred Z3) on every substrate, globally exactly at Z3-corank 1. | proof; all 60 substrates up to 8 points | C |
| 6 | Blurred Z3 on corank-1 substrates selects in the knot's full sense (global, recognisable failures; easy counts after removing a line; hard in general) and composes like cycles: a bridge, at four values. | proof | C |
| 7 | But its selected spaces are rigid: after removing a line, three solutions remain and every circuit is a tie. The knot's can keep a knot (at every line of the Fano plane, and on 4 other Pfaffian substrates). | proof and census | C |

## Answer

- **Yes, beyond two values selection and cycle-like composition can coexist.** The formal version appears at three values. The full
  version needs four: characteristic 3 for global failure (3 = 0 mod 3, so the whole space can cancel) and a doubled value for a hard
  count.
- **The bridge is linear, and its selected spaces are rigid.** Removing any line leaves one degree of freedom and only ties. The knot's
  selected spaces are not rigid in general: emergence (a knot) survives inside them.
- **So no law found here does what the knot does while composing like cycles.**

## Reading

- **Kinds of cancellation.**
  - Parity cannot fail globally on cubic substrates, because three is odd.
  - Z3 fails globally when the whole space cancels (3 = 0).
  - The knot fails globally when nothing cancels: its perfect matchings all agree in sign.
  - This is the owner's "harmonies are incommensurables cancelling", met at the level of failure.
- **The layers again.**
  - Counting (a hidden multiplicity) can make a law hard to count without touching its relations or its composition.
  - Relations decide what fails and what composes.
  - The knot's distinctive feature is relational: it selects spaces that keep emergence inside.
- **The 2-versus-3 boundary, from selection.**
  - The linear bridge's selected spaces collapse to ties, which are pairwise.
  - The knot's keep three-place emergence.

## Literature

- **Ours.**
  - KNOT-CIRCUITS Theorem 1.
  - PINNING C.
  - SELECT-COUNT A and B.
  - THREEFOLD-SPACES Theorem 1.
  - NATIVE-PATHS A and C.
  - The census of MUTUAL-SELECTION C.
- **Classical.**
  - Uniform fibres of cosets.
  - Dyer–Richerby (strong balance) and Bulatov (counting dichotomies).
  - Bulatov–Dalmau (Mal'tsev decision).
  - Congruence permutability.
  - Pfaffian signings (Kasteleyn, Little, Robertson–Seymour–Thomas).
  - det ≡ perm (mod 2).
- **New here.**
  - The blurring lemma as stated.
  - The enumeration of Mal'tsev operations on three values.
  - The formal and full bridges.
  - The three-law census of failing substrates.
  - The Z3 corank dichotomy.
  - The rigidity contrast.

  These are elementary, with moderate folklore risk.

## Pending the owner

Still open from earlier epics:
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- whether counted length should ever count as a native magnitude.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — a law that selects and composes, beyond two values | **Status:** Successful | Found. Formal at three values (blurred parity); full at four (blurred Z3 on corank-1 substrates). Its selected spaces are rigid (only ties), unlike the knot's. |
| Local direction — bridges built by blurring linear laws | Practically exhausted | Every blurred linear law inherits its base's failures, circuits and rigidity. |
| Broader exploration — cycle-like composition with non-rigid selection | Open, with a lead | Laws over fields always give rigid selected spaces: a global failure leaves rank n − 1, so one degree of freedom. Coset laws of other groups (Z4; non-abelian ones that compose like cycles, such as S3) and the simple Mal'tsev laws on three values are untested; their cosets can have two independent directions. |
| Long-term goal — composed topology from a law that selects | Capability gained, obstruction sharpened | Selection and native composition can coexist, but in the cases found the selected spaces lose emergence. |
| Next recommendation — does cycle-like composition force rigid selection? | **Next step:** Continue. Test the remaining Theorem 1 laws (coset laws of Z4, S3 and D_p; simple Mal'tsev laws on three values) for global failures on regular substrates, and for knots surviving the removal of a line. Then try to prove rigidity for every Mal'tsev law. | If every such law is rigid, native composition and emergence-preserving selection exclude each other at every number of values. That would be a clean theorem placing the knot apart. If one is not, it is the first law that composes natively and selects spaces that keep emergence. Alternatives: classify the simple Mal'tsev laws on three values (1/3); the ladder on blurred Z3 (1/3, weakened by rigidity). |
| Interest — that recommendation | **2/3 — Promising** | It is the sharpest remaining form of the bridge question, with a finite first test and a clean theorem either way. Main uncertainty: Mal'tsev decision theory may make rigidity a short corollary, which would be valuable but less of a discovery. |
| Execution — that action | Deferred to the owner | No new epic opened. Bound: groups of order at most 8 and substrates of up to 8 points. Stop when a non-rigid global failure is found, or when a proof covers coset laws. |
