# Novelty and transfer, checked before any proof work

Epic `WIDE-LEFT-20261110-001`, sub-goal B114, 2026-11-10. The coordinator's first condition: say exactly how the 2n-pigeon bit LeftPigeon
differs from what Braun proved, and check line by line that a bound for it gives one for the n + 1 pigeon principle.

## The formulas

For n = 2^l holes:
- **BPHP_m** (Braun; extended to m pigeons in `HOLE-CRITERION-COLOURING-20261019-001B`): pigeon rows f_x of l bits for x < m; clauses
  "f_x ≠ h or f_x′ ≠ h" for x < x′ and every hole h.
- **LP_{n+1}** (the binary left-pigeon principle, PPADS-complete as a search problem, `COUNT-SYSTEMS-20261110-001A`): pigeon rows f_x of
  l bits for x ≤ n and hole rows g_h of l + 1 bits; clauses "f_x ≠ h or g_h,j = x_j" for every pigeon x ≤ n, hole h and bit j ≤ l,
  where x_j is bit j of x written in l + 1 bits (codes above n name no pigeon).
- **WLP_{2n}** (the 2n-pigeon principle): the same with pigeons x < 2n; the hole rows still have l + 1 bits, and now every one of the
  2^{l+1} codes names a pigeon.

## How WLP_{2n} differs from Braun's theorems

- Braun's bound (and its m-pigeon extension) is for BPHP_m, which has pigeon rows only. WLP_{2n} adds the hole rows and replaces the
  collision clauses by "if x is in h, then h names x".
- **WLP_{2n} implies BPHP_{2n}'s clauses cheaply:** if f_x = f_x′ = h with x ≠ x′, resolving "f_x ≠ h or g_h,j = x_j" with
  "f_x′ ≠ h or g_h,j = x′_j" on a bit j where x and x′ differ gives "f_x ≠ h or f_x′ ≠ h" in one step. So any refutation of BPHP_{2n}
  becomes one of WLP_{2n} with n·C(2n, 2) more lines: S(WLP_{2n}) ≤ S(BPHP_{2n}) + poly(n). A lower bound for WLP_{2n} is therefore
  stronger than Braun's (it implies a bound for BPHP_{2n}), and it does not follow from his: his theorem bounds the harder-to-refute
  formula.
- **Not a short corollary of Braun's machinery either:** his §9 criterion applies to any clause set, but needs a separated space for
  the formula's own system, and his separation theorem is for BPHP's base only. For LP_{n+1} the decoder route to such a space is
  closed (`KERNEL-FRAC-20261110-001A`); for WLP_{2n} it is open, and the separation argument it needs (a cube with hole coordinates and
  spare rows) is new.
- **Literature.** Searches on 2026-11-10 (Braun; Efremenko, Garlík and Itsykson; Byramji and Impagliazzo; Alekseev and Itsykson;
  Efremenko and Itsykson; Bhattacharya and Chattopadhyay; Itsykson and Knop) found no Res(⊕) bound of any kind for left-pigeon,
  injective-with-retraction, onto or bijective variants of bit PHP, nor for any PPADS-complete principle.

## The transfer, line by line

Claim: every Res(⊕) refutation of LP_{n+1} is a Res(⊕) refutation of WLP_{2n}, so S(LP_{n+1}) ≥ S(WLP_{2n}).
1. **Hole rows.** Both formulas code pigeons in l + 1 bits: ⌈log2(n + 1)⌉ = ⌈log2(2n)⌉ = l + 1 for n = 2^l ≥ 2. Same variables g_h,j.
2. **Codes.** Pigeon x ≤ n has the same code (x in binary, l + 1 bits) in both.
3. **Pigeon rows.** f_x for x ≤ n are the same variables in both; WLP_{2n} has more (x ≤ 2n − 1).
4. **Clauses.** For x ≤ n, every h and j, the clause "f_x ≠ h or g_h,j = x_j" is the same clause in both. So the clause set of LP_{n+1}
   is a subset of WLP_{2n}'s.
5. **Refutations.** A Res(⊕) refutation of a clause set is a refutation of every superset (its initial lines remain initial clauses;
   extra variables and clauses are unused). Hence S(WLP_{2n}) ≤ S(LP_{n+1}).

So **a lower bound for WLP_{2n} is a lower bound for LP_{n+1}**, in this binary encoding, which is the one `COUNT-SYSTEMS-20261110-001A`
uses. (It is not a statement about every encoding of the search problem: Res(⊕) is not closed under the decision-tree reductions
between encodings.)

## Verdict of the check

The transfer holds and the 2n statement is neither Braun's theorem nor a short corollary of it; the epic proceeds to the frozen target.
Nothing here transfers to the knot sphere's count.
