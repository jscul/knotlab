I checked these by hand from your definitions (projection monotonicity, the level bookkeeping at n = N, and how the type evolves); nothing was run. The logic of all three is sound, but there are four gaps to close before stating them.

**Gaps**

1. **Off-by-one at the bottom level (affects 2 and 3').** T_k is computed using W_k, whose e-slot knots have members at level k+1. Those knots exist in P_N only for N ≥ k+1. So a tie reaching level k0+s proved this way holds for N ≥ k0+s+1, not N ≥ k0+s. To get N ≥ k0+s, compute the level-k verdict from W_k0..W_(k−1) plus only the e = none knots of W_k.

2. **The message must carry the anchor (2 and 3').** m_k as stated is a set of assignments of S_k alone, which cannot express "tied to an element at level k0". Either add one bit for the anchor x0 (m_k ⊆ {0,1}^(S_k) × {0,1}), or define T_(k+1) as the elements tied to some element of T_k and use transitivity with signs. "T_k nonempty" defined as ties between adjacent levels only does not chain unless consecutive ties share an element. In (3'), x needs the same marker bit.

3. **The type must be per placement word, not per state.** For a length-2 word, the intermediate image can leave S_k and the composite can return. Track for each element and each word w the target w(x) and the section w|_x, which is a length-2 word of states. Then w(x·c) = w(x)·w|_x(c) is deterministic, and "outside stays outside" holds by prefix preservation.

4. **Periodicity must be joint.** Detect the cycle on the full tuple (type, phase of c, message, product-machine states at S_k, T_k), and check the pre-period as well as the cycle. Separate periods do not suffice.

**Your questions**

- **(2):** Yes. Projections only shrink when knots are added, so a pair confined to {00,11} or {01,10} in the chain is confined in P_N. Life plus complement symmetry then gives exactly two patterns with both singletons free, which is a bond of size 2. Life is the only extra ingredient, and it also rules out a dead window, where everything is vacuously tied. With gaps 1–2 fixed, L = 2 follows.

- **(3):** Yes, "parities not all equal" is the right condition. One machine with x = y and one with x ≠ y, plus complements, gives all four patterns, so the pair is free and neither sign of tie is possible. Since singletons are free under life, L ≥ 3. Two details:
  - y must range over all addresses at the deeper levels, not only descendants of x.
  - Restrict to product configurations reachable at depth > k. Per level k+s is sharper; all deeper is sufficient but could reject spuriously.

- **(3'):** Yes. Constrained in a sub-pattern implies constrained in P_N, with no life needed for that step. With all three pairs free in P_N and singletons free, every proper subset is free, so it is a bond of P_N. Together with (3) this gives L = 3 only at the levels where both checks pass.

- **(1):** I see no flaw, provided the windows satisfy the running-intersection property. They do if each address lies only in its own orbit's window and its parent orbit's window. Stabilisation also has to be taken in remaining depth N − n, since the bottom boundary differs. The scope is ties and two-orbit 3-bonds only.

**Names in the literature**

- **Setting:** automaton (self-similar) groups, after Grigorchuk and Nekrashevych. "Orbits are whole levels" is level-transitive, or spherically transitive. Bounded orbits is the non-level-transitive case.
- **The chain:** the orbital Schreier graph along an eventually periodic (rational) boundary point, with a transfer matrix, i.e. dynamic programming over a path decomposition.
- **Automatic states:** automatic sequences on the tree, or points of a sofic tree shift; the all-level check is a product-automaton safety check.
- **Ties and bonds:** ties are the backbone, or implied binary constraints, in CSP terms; bonds are circuits, i.e. minimal dependent sets.
