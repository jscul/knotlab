# Phases of the forcing law, and what overlap does to them

Status: Proved (referee pending)

Ticket `SEQUENTIAL-WALL-20261116-001B`, 16 November 2026. Written by Claude in one session; checked by `check.py` beside this
file (exhaustive comparisons on all patterns of four distinctions and on random larger ones) and handed to the referee thread.
The advisor model was consulted on the analysis before it was frozen (see the pre-registration). Every statement is labelled
**known** (prior work, cited), **known-with-delta** (a known argument restated for atom patterns) or **local** (not found stated
elsewhere). No claim about P versus NP or P versus NC is made.

## Setting

An **atom** is the knot `¬a ∨ ¬b ∨ c`, read "a and b together demand c"; a and b are its **demanders**, c the distinction it
**demands**. An **atom pattern** is a finite set of atoms over distinctions V, with a set H ⊆ V **held** at 1 by the outside. A
distinction is **forced** when it is 1 in every allowed state with H at 1. For atoms this is the forward closure of H, the least set
containing H that contains c whenever it contains both demanders of an atom demanding c (known: the least model of a Horn system).
A **derivation tree** of v is a finite binary tree whose leaves are held distinctions and whose every internal node, labelled c,
uses an atom (a, b → c) of the pattern and has children labelled a and b; v is forced exactly when it has one.

**Native law.** S⁰ = H and Sᵗ⁺¹ = Sᵗ ∪ {c : (a, b → c), a, b ∈ Sᵗ}; each step is a **round**, and R counts the rounds that add a
distinction.

**Forcing law.** P₀ = H. In phase t ≥ 1 every atom (a, b → c) with a ∈ Pₜ₋₁ is read as the two-place rule b → c, and every atom
with b ∈ Pₜ₋₁ as a → c. Pₜ is everything reachable from Pₜ₋₁ along these rules, Pₜ₋₁ included. The **phase** of v is the least t
with v ∈ Pₜ, and P counts the phases that add a distinction. Fixing a demander of an atom to 1 leaves a two-place rule, which is no
knot (every two-place relation is a 2-CNF), so a phase does only two-place reasoning. An atom is used **openly** when its two
demanders are first forced in the same phase; only such uses make the law take another phase.

**Strahler number.** For a derivation tree: a leaf has number 0; a node whose children have numbers i and j has max(i, j) if
i ≠ j and i + 1 if i = j (the Horton–Strahler number, with leaves counted 0). The Strahler number of v, σ(v), is the least over its
derivation trees (∞ if it has none). `check.py` computes it by relaxation downward from ∞, which reaches exactly the values of
finite trees. (The numerically least solution of σ(c) = min over atoms of combine(σ(a), σ(b)) would be wrong: with atoms
(h, c → d) and (h, d → c), h held and c, d unforced, it gives c and d the number 1.)

## Theorem 1 (phases are Strahler numbers)

For every distinction v, phase(v) = σ(v). Hence P is the largest Strahler number of a forced distinction.

*Status: known. The forcing law is Newton's method for the Boolean fixed-point system, and Esparza, Kiefer and Luttenberger
(Newtonian program analysis, J. ACM 57(6), 2010) show that the k-th Newton iterate is reached by exactly the derivation trees of
dimension, that is Strahler number, at most k (see also Esparza, Luttenberger and Schlund, A brief history of Strahler numbers,
LATA 2014). The direct proof for atoms follows.*

*Proof.* (σ ≥ phase.) We show v ∈ P_ρ(T) for every derivation tree T of v, ρ(T) its number, by induction on T. A leaf is held, in
P₀. Let T's root use (a, b → v), with subtrees of numbers i and j, so a ∈ Pᵢ and b ∈ Pⱼ. If i < j, then ρ(T) = j and a ∈ Pⱼ₋₁, so in
phase j the atom is the rule b → v; b is reachable in phase j, hence so is v. If i = j, then a, b ∈ Pᵢ, the atom is the rule b → v in
phase i + 1 and b ∈ Pᵢ is a source, so v ∈ Pᵢ₊₁ = P_ρ(T). The case i > j is symmetric.

(phase ≥ σ.) We show by induction on t that every v ∈ Pₜ has a derivation tree of number at most t. For t = 0, v is held. Let v be
reached in phase t along u₀ → u₁ → … → u_L = v with u₀ ∈ Pₜ₋₁, each rule uᵢ → uᵢ₊₁ coming from an atom (uᵢ, wᵢ → uᵢ₊₁) with
wᵢ ∈ Pₜ₋₁. By induction u₀ and every wᵢ have trees of number at most t − 1. Build the tree of uᵢ₊₁ from those of uᵢ and wᵢ. The
tree of u₁ has number combine(≤ t − 1, ≤ t − 1) ≤ t. If uᵢ's tree has number t, then wᵢ's has less, so uᵢ₊₁'s has t; if uᵢ's has
less than t, uᵢ₊₁'s has at most t. A distinction never reached has no derivation tree, and both sides are ∞. ∎

**Corollary (parallel time).** Each phase is one reachability computation on at most n + 2m rules, which takes O(log² n) parallel
time with bounded fan-in, O(log n) with unbounded fan-in, by repeated squaring (known: reachability is in NL ⊆ AC¹). So the forced
set is computed in O(P · log² n) parallel time with polynomially many processors, and **a family of atom patterns whose phase count
is polylogarithmic is decided in NC** (known-with-delta).

## Theorem 2 (the fringe bound, and where phases come from)

(a) A derivation tree of Strahler number k has at least 2ᵏ leaves. Hence σ(v) ≤ log₂ fringe(v), where fringe(v) is the fewest
leaves, counted with multiplicity, of a derivation tree of v.

(b) If σ(v) > log₂ |H|, then every derivation tree of v of number σ(v) or more has a **rejoining**: an atom with one distinction
below both of its demanders.

*Status: (a) known (the classical bound between Strahler number and leaf count); it recovers the polynomial fringe theorem of
Ullman and Van Gelder (Parallel complexity of logical query programs, Algorithmica 3, 1988), sharpened to LOGCFL by Ruzzo (1980).
(b) known-with-delta (pigeonhole).*

*Proof.* (a) A leaf has 1 = 2⁰ leaves. A node of number k has either a child of number k, with at least 2ᵏ leaves, or two children of
number k − 1, with at least 2·2ᵏ⁻¹. A tree of fewest leaves then gives σ(v) ≤ log₂ fringe(v). (b) Such a tree has at least
2^σ(v) > |H| leaves, so two leaves carry one held label; the node where their paths from the root part uses an atom with that
distinction below both demanders. ∎

## Theorem 3 (without reuse, phases are logarithmic)

Call a distinction **reused** when it is a demander in two or more atoms. If no distinction is reused, every forced v has a
derivation tree in which each distinction occurs at most once; so fringe(v) ≤ |H| and σ(v) ≤ log₂ |H|.

*Status: known-with-delta (such a pattern is a monotone formula, whose value is in NC¹: Buss 1987; tree contraction, Miller and
Reif 1985); the statement for atoms and the proof are written here.*

*Proof.* Take a derivation tree T of v with fewest nodes. No label repeats on a root-to-leaf path: replacing the higher subtree by
the lower one would give a smaller tree. Suppose a label u occurs at two distinct nodes x₁, x₂; neither is an ancestor of the
other, so neither is the root, and both have parents. Each parent uses an atom with u as a demander, and u demands in only one
atom α = (u, w → c), so both parents are labelled c and use α. The parents are distinct: otherwise x₁ and x₂ would be the two
children of one node using α, whose demanders u and w differ. Neither parent is an ancestor of the other (that would repeat c on a
path). Repeating, two chains of distinct nodes with equal labels climb one level at a time. If x₁ and x₂ have different depths in
T, the shallower chain reaches the root, labelled v, while the other stands at a non-root node labelled v below the root: a
repeated label on a path. If the depths are equal, the chains reach two distinct children of the root with equal labels, so the
root's atom would have equal demanders, which is impossible. So no label repeats, the leaves are distinct held distinctions, and
Theorem 2(a) gives the bound. ∎

## Theorem 4 (both kinds of overlap are needed for the wall)

Call a distinction **demanded several ways** when two or more atoms demand it.

(a) If no distinction is demanded several ways, forcing is decided in NL: v is forced if and only if, following from v the unique
atom that demands each unheld distinction back to its demanders, one never meets an unheld distinction that no atom demands and
never returns to a distinction already on the way. *Status: known-with-delta (monotone circuits of AND gates).* *Proof.* A
derivation tree must use the unique demanding atom at every unheld node, so it is this unfolding whenever the unfolding is finite
with held leaves; it is finite exactly when no cycle is met, and its leaves are held exactly when no unheld undemanded distinction
is met. Both are reachability questions. ∎ The phase count does not see this: the pyramid of height h has no distinction demanded
several ways and needs h phases.

(b) If no distinction is reused, Theorem 3 gives at most log₂ |H| phases, hence NC.

(c) Monotone circuit value is P-complete (Goldschlager 1977; Cook's path systems, 1974, are atom patterns already), and it reduces
to atom patterns in logarithmic space: an AND gate g = x ∧ y is the atom (x, y → g), an OR gate g = x ∨ y the two atoms (x, t → g)
and (y, t → g) with one held t, true inputs held. Every piece is the atom, which passes K1–K3 (`knotlab check`). OR gates demand a
distinction several ways, fan-out reuses it. *Status: known (also Jones and Laaser 1976 for Horn satisfiability).* So unless
P = NC some atom patterns need more than polylogarithmically many phases (the corollary of Theorem 1 would otherwise put P in NC),
and such patterns need both reuse (unless P = NC, by (b)) and several-way demand (unless P = NL, by (a)).

## Theorem 5 (where the knot laws sit)

With held values available, a law of one three-place knot is in AC⁰, ⊕L-complete, P-complete or NP-complete, and never in NL or L.
Of the 34 three-place knots, 2 are in AC⁰ (the single-sign clauses `a ∨ b ∨ c` and `¬a ∨ ¬b ∨ ¬c`), 2 are ⊕L-complete (parity),
14 P-complete (the atom, its dual and the knots that define one of them with held values) and 16 NP-complete (not-all-equal among
them).

*Status: known (Schaefer 1978; Allender, Bauland, Immerman, Schnoor and Vollmer, J. Comput. Syst. Sci. 2009), applied here.* The
table is `artifacts/.../knots_table.json`: `knots_table.py` lists the 34 knots (each confirmed by `knotlab`), tests closure under
and, or, majority and minority, and for each Horn or dual-Horn knot other than the two single-sign clauses finds an explicit
definition of the atom or its dual from the knot with held values (at most two copies, two hidden distinctions). No knot is closed
under majority (Baker and Pixley 1975: a majority-closed relation is fixed by its two-place shadows, and a knot is free on every
pair), which is why no knot law is in NL. **Being a knot does not decide the class**: `a ∨ b ∨ c` is a knot whose patterns are
decided by inspection, while "a = 1 → b = c" is a knot whose patterns are P-complete.

(b) Not-all-equal. Satisfiability is NP-complete (Schaefer 1978). Forcing by propagation, where two equal members of a
not-all-equal knot force the third to differ, is P-complete with two held distinctions T = 1 and F = 0: an AND gate is
NAE(x, y, g₀) followed by NAE(g₀, F, g), an OR gate is NAE(x, T, g₀) and NAE(y, T, g₀) followed by NAE(g₀, F, g), and each wire is
set to 1 or unset (g₀ wires to 0 or unset). Some held value is needed, since not-all-equal is unchanged by flipping every value and
so forces nothing alone. *Status: known-with-delta (propagation for CNF is P-complete; arc consistency is P-complete, Kasif 1990;
this gadget is written and checked here).* *Proof.* By induction from the inputs, a g wire is set to 1 exactly when its gate is true
and a g₀ wire to 0 exactly when its gate is true; no knot ever has three set members of one value, since g₀ wires are never 1 and g
wires never 0; and no other propagation applies, because every other knot has two set members of different values or fewer than
two set members. `check.py` compares it with circuit evaluation on every input of 192 small circuits. ∎ Fixing one member of a
not-all-equal knot also leaves a two-place rule (fixing x = 1 leaves `¬y ∨ ¬z`, fixing x = 0 leaves `y ∨ z`), so phases apply to
not-all-equal propagation with "both other members first set in the same phase" in place of an open use.

## Theorem 6 (the dual law on patterns without cycles)

On a pattern whose atoms admit an order with every demanded distinction after its demanders, unforcedness spreads by a dual law.
An atom is dead once a demander is known unforced. Phase 0 starts from the unheld distinctions no atom demands and follows, for
every distinction with exactly one atom, the rules "a demander unforced → it unforced"; a later phase starts from every
distinction all of whose atoms are dead, and follows the same rules for distinctions left with exactly one live atom. Then:
(a) every distinction is forced or found unforced; (b) a distinction's dual phase is the least generalized Strahler number of a
derivation of its unforcedness (each atom contributes the lesser number of its two demanders; the node takes the largest, plus one
when the largest occurs at two or more atoms; undemanded unheld distinctions have 0); (c) with P_dual the number of dual
reachability computations, the forced set is computed in O(min(P, P_dual) · log² n) parallel time, by running both laws and stopping
at the first to finish: when one law ends, every distinction it has not settled belongs to the other side.

*Status: known-with-delta (the dual is Newton's method for the greatest fixed point of the negated system; that a monotone circuit
can be evaluated from either side is folklore); proposed by the advisor for this study; the statement and proof for atoms are
written here. On patterns with cycles unforcedness also comes from unsupported cycles (the literature's unfounded sets), which the
dual law does not find, so the theorem is stated only without cycles.*

*Proof.* (a) Along the order, an unheld distinction is unforced exactly when each of its atoms has an unforced demander, and an
undemanded one exactly when unheld; by induction every distinction has either a derivation tree or a well-founded derivation of
unforcedness. (b) As in Theorem 1, with k-ary nodes: a distinction whose atoms die at phases e₁ ≤ … ≤ e_k with e_(k−1) < e_k is
reached in phase e_k along the rule from the demander that kills the last atom; if e_(k−1) = e_k it waits, and all its atoms are
dead at the start of phase e_k + 1, where it is a seed. `check.py` and `gates.py` (G7) compare phases with the relaxation on 720
patterns. (c) By (a), once the forcing law stops, every distinction it did not force is unforced, and once the dual law stops,
every distinction it did not find unforced is forced; each phase is one reachability computation. ∎

On the pyramid and the ladder nothing is unforced, so the dual law ends at once and the two-sided count is 0 reachability
computations beyond the check, though the forcing law needs h and k + 1 phases: the dual law sees what the phase count misses in
Theorem 4(a).

## Why atoms, and not parity, need phases

Parity knots also leave a two-place rule when one member is fixed, but parity patterns are decided by Gaussian elimination, not by
propagation, in O(log² n) parallel time (⊕L ⊆ NC², known), so the phase count is the wrong measure for them. The known form of the
contrast is few subpowers (Berman, Idziak, Marković, McKenzie, Valeriote and Willard 2010): relations closed under parity's
minority, or under majority, have compact descriptions however many distinctions they hold, while relations closed under "and",
the atom's operation, can need exponentially many; an open atom carried forward without waiting for a demander would need such a
description.

## What is not claimed

No claim about P versus NP or P versus NC. Theorem 4's conclusions are conditional on P ≠ NC or P ≠ NL. The phase count is a
one-sided predictor: polylogarithmically many phases give NC, but many phases do not give hardness (the ladder and the pyramid are
decided in NL, and the dual law ends them at once).

## Corrections (16 November 2026, referee `SEQUENTIAL-WALL-R1`)

The text above is kept as written; read it with these two corrections.

- Theorem 5, "never in NL or L", and "which is why no knot law is in NL": read **never NL-complete or L-complete**. The two AC⁰ laws
  are in L. Baker–Pixley shows that no knot is majority-closed, which excludes exactly the NL- and L-complete cases. (Not a block.)
- Theorem 4(c), last sentence: "such patterns" are the P-hard families, not every family needing many phases. Many phases need only
  reuse (Theorem 3), as the pyramid shows, which has many phases and no several-way demand. A P-hard family needs reuse unless
  P = NC and several-way demand unless P = NL. (Not a block.)
