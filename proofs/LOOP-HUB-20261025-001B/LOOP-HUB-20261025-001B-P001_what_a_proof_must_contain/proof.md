# What a proof of the arm inequality must contain

Status: Proved

Ticket `LOOP-HUB-20261025-001B`, 2026-10-25.

**What it uses:**
- from `SOFT-HUB-20261024-001A-P001`:
  - Theorem 1: supports of native gadgets are co-independent;
  - Lemma 2: separated pairs number at most s_u;
  - Proposition 6: the non-windable knots are R_c = N[c] ∪ {c̄}, and a linked pair branches at knots with local tuples c and c̄;
- from `SOFT-HUB-20261024-001C-P001`: the arm inequality on tree gadgets, and the arm map;
- from `LOOP-HUB-20261025-001A-E001`: evidence only, quoted in the conjecture.

## Standard statement

**Setting.**
- **The inequality.** For a gadget of R_c, an axis u and a terminal i (the other two are j and k), write lhs_u = F(u)F(ū) and
  rhs_u = s_u + F(u + eᵢ)F(ū) + F(u)F(ū + eᵢ). The *arm inequality* is lhs_u ≤ rhs_u.
- **The two-by-four table.** M[z][w] is F with terminal i equal to z and terminals (j, k) equal to w.
  - Let A = (u_j, u_k), Ā its complement, P = A + e_j and Q = A + e_k.
  - Let M0 and M1 be the rows z = uᵢ and z = 1 − uᵢ.
  - G(w) = M[0][w] + M[1][w] is the gadget with terminal i turned into a free leg.
- **Difference patterns.** A pair (σ, τ) ∈ Conf(u) × Conf(ū) has *difference pattern* d = σ ⊕ τ, the set of edges, terminals and free legs
  where they differ.
  - σ is *compatible with* d when σ and σ ⊕ d are both configurations.
  - d is *linked* when one of its components contains all three terminals.
  - For a linked d, arm(d) is terminal i's difference walk up to the first knot b(d) where all three slots differ. It depends on d
    only.

**Lemma 1 (one pattern at a time).** Let d be linked, and d' = d ⊕ arm(d).
- **The map.** Send σ to σ ⊕ arm(d) if σ is empty at b(d), and leave it unchanged otherwise.
- **What it does.** This maps the configurations compatible with d injectively into the configurations compatible with d' whose
  terminals j and k carry u_j and u_k.
- **Consequence.** If d ↦ d ⊕ arm(d) is injective on linked patterns, the arm inequality holds.
- **Trees.** On tree gadgets that map is injective, which gives a second proof of the tree theorem.

**Proposition 2 (the symmetric form, and no lock).** For every non-negative function F on three bits, write
agree = M0A M0Ā + M1A M1Ā, cross = M0P M1Q + M0Q M1P and minor = M0A M1Ā − M1A M0Ā. Then:
- rhs_u − lhs_u = agree + cross − minor;
- rhs_(u+eᵢ) − lhs_(u+eᵢ) = agree + cross + minor;
- rhs_u − lhs_u = G(A)G(Ā) + F(u + e_j)F(ū + e_j) + F(u + e_k)F(ū + e_k) − 2 lhs_u.

So the arm inequality on the axes u and u + eᵢ together says **|minor| ≤ agree + cross**. For every native gadget, G(w) > 0 for every
pattern w of two terminals.

**Proposition 3 (the natural strengthenings fail).** Four explicit gadgets of two or three knots each satisfy the arm inequality on
every axis and terminal, and fail one strengthening:
- **(a) Per partner.** In a triangle of three knots each carrying a terminal, one configuration τ has 4 linked partners that are empty at
  their branching knot, while F(u + e₁) = 3.
- **(b) Per image pattern.** In a three-knot gadget with a double edge, some image pattern d' receives more configurations than are
  compatible with it.
- **(c) One-sided path flips.** In a three-knot gadget, flipping paths of the difference from terminal i on one side matches at most 4
  of its 5 linked pairs into the two target classes, although the classes have room.
- **(d) Without the agreeing terms.** On a two-knot tree, minor = 1 and cross = 0.

**Corollary 4 (what a proof must contain).** Any proof of the arm inequality for gadgets with cycles must:
- change the partner configuration for some pairs (a);
- send some pairs of one difference pattern away from that pattern's image (b);
- use moves other than one-sided path flips from terminal i, or charge some linked pairs to the split products (c);
- use the pairs that agree at terminal i, even on trees (d).

**Conjecture 5.** The arm inequality holds for every gadget of the open knots.
- **Evidence.** `LOOP-HUB-20261025-001A-E001`: no violation in adversarial annealing up to 40 knots, in chains of double edges, or in
  fully paired cores; the split bounds held on every small gadget.

**Reading.**
- **No copying.** If terminal i copies the axis of the other two exactly (M1A = M0Ā = 0), the agreeing terms vanish, and the inequality
  requires the cross terms to be positive: on the mixed patterns P and Q, terminal i must take both values.
- **No locking.** Co-independence never lets the other two terminals be locked to an antipodal pair (G > 0).
- **No cloning.** So a native network cannot clone one bit onto three terminals: that is the content of the conjecture, and Proposition 3
  shows it cannot be proved one pattern or one partner at a time.

## Nearest known result

- **Splitting by difference patterns** is the standard first step of switching arguments: canonical paths and winding work on the
  symmetric difference of two configurations.
- **The local content** is:
  - the one-sided version, with its injectivity per pattern;
  - the symmetric form;
  - the explicit witnesses that rule out local proofs.
- **Novelty:** elementary; new to the program; folklore risk medium.

## Proof

### Lemma 1

- **Compatible local tuples.** A knot whose differing slots form the set D_v is compatible with these σ_v:
  - D_v = ∅: all of R;
  - D_v = {p}: c and a_p;
  - D_v = {p, q}: R \ {c};
  - all three slots: c and c̄.

  These follow from Proposition 6 of `SOFT-HUB-20261024-001A`: allowed tuples have 0, 1 or 3 defects.
- **Arm knots.** An interior knot of the arm has D_v = {in, out}, so σ_v ∈ R \ {c}, and adding {in, out} permutes R \ {c}.
  - In d' its differing set is empty, so any allowed tuple is compatible there.
  - The image of the empty case equals τ_v, and the other case leaves σ_v.
- **The branching knot.** At b = b(d), σ_b is c or c̄, and in d' the differing set is the two slots other than the arm's slot s.
  - The empty case gives c + e_s = a_s ∈ R \ {c}.
  - The full case keeps c̄ ∈ R \ {c}.
- **Validity of the partner.**
  - In the empty case, σ' ⊕ d' = σ ⊕ d = τ.
  - In the full case, σ ⊕ d' = τ ⊕ arm(d), which is valid: interior arm knots become σ's tuples, and at b, τ_b = c gives a_s.
- **Terminals.** The arm contains terminal i and no other terminal, so terminals j and k keep u_j and u_k.
- **Injectivity.** The two cases give terminal i the values 1 − uᵢ and uᵢ. Within each case the map is a fixed translation, or the
  identity.
- **Consequence.**
  - The configurations compatible with some d' whose terminals j and k carry u_j and u_k are exactly the first coordinates of the pairs
    counted by F(u)F(ū + eᵢ) + F(u + eᵢ)F(ū).
  - If different linked patterns have different images d', their images are disjoint, so link_u ≤ F(u + eᵢ)F(ū) + F(u)F(ū + eᵢ).
    Lemma 2 of ticket A adds s_u.
- **Trees.**
  - In a tree gadget, arm(d) runs along the tree route from terminal i towards the median of the terminal knots.
  - In d', the knots before b on that route have empty differing sets, and b has two differing slots.
  - So b, and with it arm(d), is the first route knot where d' is non-empty, and d is recovered from d'. ∎

### Proposition 2

- **The algebra.** Expand. In the table, lhs_u = M0A M1Ā. The split products are M1A M0Ā + M0P M1Q + M0Q M1P, and the arm terms are
  M1A M1Ā + M0A M0Ā. For the axis u + eᵢ the roles of the rows swap, which changes the sign of the minor.
- **Positivity.** The values with (j, k) = w and terminal i equal to 0 or 1 are adjacent. The support is co-independent (ticket A,
  Theorem 1), so at least one of them is allowed. ∎

### Proposition 3

By exact enumeration of the four stored gadgets in `check.py`. ∎

### Corollary 4

Each item negates the corresponding strengthening, which fails on a gadget where the arm inequality holds. ∎

## Checks

`check.py` uses the standard library only (seed 20261025). It confirms:
- **Lemma 1** on 300 random gadgets, 184 of them trees, covering 15,582 linked difference patterns: images compatible, injective per
  pattern, and d ↦ d' injective on the trees.
- **Proposition 2.**
  - The three identities hold on 20,000 random non-negative functions, for every axis and terminal.
  - G is positive on every pattern of 2,000 random gadgets.
- **Proposition 3.** Each witness fails its strengthening and satisfies the arm inequality.

**Controls.**
- **The side rule matters.** Reversing it (flipping the configuration that is full at b) gives an incompatible image.
- **The matching test can succeed.** On random tree gadgets the path-flip matching does saturate.
- **The symmetric form can fail.** The planted function [10, 1, 1, 1, 1, 1, 1, 10] violates it.

## What this does not show

- **The conjecture itself.** The arm inequality for gadgets with cycles is open.
- **That no proof exists.** Corollary 4 limits the form a proof can take; it does not rule one out.
