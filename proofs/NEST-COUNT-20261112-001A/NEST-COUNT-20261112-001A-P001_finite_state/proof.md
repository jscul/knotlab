# Finite state, and what breaks it

Status: Proved

Ticket `NEST-COUNT-20261112-001A`, 2026-11-12. Statements frozen in `research/NEST-COUNT-20261112-001/preregistration.md` (one
corrected there before this proof, see its amendment). The canonical K1–K3 test is unchanged. Law: NAE on three-place knots on
distinct distinctions. Words as in `LIMIT-ONLY-20261112-001`: a definition's **relation** is the set of states of its ports that
extend to its insides; **depth** t (at depth 1 SELF is a knot); the **bottomless** pattern (SELF never reaches a bottom); the
**usual limit** (the knots present at all but finitely many depths).

## The language

A description has definitions D_0, …, D_{r−1}, the last the main one; D_i has k_i ≤ 6 ports and l_i ≤ 6 own distinctions, and
calls K (a knot), earlier definitions, or (when k_i = 3) SELF, each on distinct arguments drawn from its k_i + l_i distinctions.
There is no cycle of calls apart from SELF. Every relation of a three-port definition here is closed under complement, since NAE is.

## T1 (finite state)

**Statement.** Let S be the self-holding definitions, s = |S|. (a) There is a map Φ, fixed by the description, with X_{t+1} =
Φ(X_t), where X_t is the tuple of the relations of the definitions in S at depth t and X_0 is the knot for each; X_t takes at most
16^s values, so it is eventually periodic with preperiod plus period at most 16^s, and so are every definition's relation at depth
t and whether the depth-t pattern lives. (b) The bottomless pattern lives iff the main relation is non-empty at the greatest fixed
point G of Φ, reached from "nothing" in at most 4s strict decreases. (c) The usual limit is the bottomless pattern of the description
in which each self-holding definition with a SELF call on a permutation of its own ports also has the knot on its ports (the calls
kept), so its life is decided the same way.

**Proof.** (a) Relations are computed bottom-up through the call order: a definition's relation at depth t is the projection onto its
ports of the conjunction, over its calls, of the callees' relations at depth t on the call's arguments (a SELF call uses its own
definition's relation at depth t − 1, a knot at depth 1). This is a function of X_{t−1}, so X_t = Φ(X_{t−1}); each component is one
of the 16 complement-closed relations on three ports. A sequence of a deterministic map on a set of N values repeats within N steps.
(b) Every finite part of the bottomless pattern lies in a bottomless truncation (SELF at depth 1 dropped, i.e. read as "nothing"),
whose relations are Φ^t(TOP); by compactness the bottomless pattern lives iff every Φ^t(TOP)'s main relation is non-empty. Φ is
monotone (a larger relation for a callee allows more), so Φ^t(TOP) decreases, and in the product of s lattices of height 4 it
strictly decreases at most 4s times before reaching the greatest fixed point (Kleene iteration on a finite lattice). (c) A knot of
the bottomless pattern (a K call in a copy at level j) is present at every depth from j + 1 on. A bottom knot at depth t lies on the
arguments of a SELF call made from a copy at level t − 1; at depth t + 1 the same three distinctions carry a bottom knot only through a
SELF call on exactly those three distinctions made inside some copy whose own distinctions are fresh, so they are that copy's ports:
whether it is the new copy itself, a copy reached from it through a call to another definition on the same three ports, or a second
copy on the same triple, the call is a pass-through call of its own definition. *(Wording widened after the referee.)* Any other knot
on them at depth t + 1 is a K call on them, already a knot of the bottomless pattern. So a knot not in the
bottomless pattern is present at all depths from some depth on exactly when it lies on the ports of a copy of a definition with a
pass-through call (then each later depth carries it, down the chain of pass-through copies), and present at only finitely many
otherwise. Adding the knot on the ports of each such definition adds exactly these knots; the pass-through calls stay, since their
copies, with fresh insides, are present at all later depths. ∎

## T2 (no counter in a top window)

**Statement.** For each b ≥ 1, the set of states the depth-t pattern allows on the distinctions of levels below b is determined by
X_{t−b} (for t > b); it takes at most 16^s values and is eventually periodic in t.

**Proof.** The distinctions of levels below b and the knots among them are the same at every depth t > b; the rest of the depth-t
pattern hangs from the SELF calls made from level b − 1 copies, each contributing exactly its definition's relation at depth t − b on
its arguments (the call's insides meet the window only through its arguments). So the allowed set is the projection of a fixed
conjunction and these relations, a function of X_{t−b}, and (a) of T1 applies. ∎

So a bounded window at the top reads depth only modulo the period. Nothing is claimed about windows deep in the pattern, or about
readings inside it, such as least bonds between the top and a deep level.

## P3a (inequality and equality)

**Statement.** x ≠ y iff there are a, b, c with NAE(x,y,a), NAE(x,y,b), NAE(x,y,c), NAE(a,b,c). x = y iff there is m with m ≠ x and
m ≠ y (each by the gadget).

**Proof.** If x = y the first three knots force a = b = c = ¬x, and the fourth fails. If x ≠ y the first three hold for any a, b, c,
and the fourth for a = b ≠ c. Equality: m ≠ x and m ≠ y iff x = y = ¬m. ∎ (check.py K1.)

## P3b (every complement-closed relation)

**Statement.** Every complement-closed Boolean relation is the projection of a pattern of NAE knots on distinct distinctions.

**Proof.** NAE on three places is a base of the co-clone IN₂ of complement-closed relations (Böhler, Reith, Schnoor and Vollmer
2005, bases for Boolean co-clones), whose primitive positive definitions may repeat variables; replace each repeated occurrence by a
fresh distinction tied by equality (P3a). Concretely for the reduction below: read each variable relative to a reference r (true when
it differs from r); a one- or two-literal clause is then r ≠ v or NAE(u, v, r) (a negative literal through an inequality), and a longer
clause is chained, NAE(u₁, u₂, a), then NAE(a′, u₃, …) with a′ ≠ a, ending in r. For three places the 16 relations are, by number of
complementary pairs: 0, a contradiction (the ten knots on five fresh distinctions); 1 or 2, equalities and inequalities; 3, NAE with
the excluded pair's ones flipped through inequalities; 4, nothing. ∎ (check.py K2: all 16 by enumeration.)

## P3c (what breaks T1)

**Statement.** For meeting patterns on Z² that are translation-invariant (a finite fundamental domain whose knots are copied by every
translation), whether the infinite pattern lives is undecidable.

**Proof.** Reduce the domino problem: given Wang tiles (colours on four sides), put at each site a reference r and one bit per tile,
a tile being "on" when its bit differs from r. Per site: r equals the right and the upper neighbours' references (P3a); some tile is
on; no two are on; for each tile pair that does not match across the right (upper) side, not both on (clauses relative to r, P3b).
Every auxiliary is per site, so the pattern is translation-invariant and computable from the tiles. A tiling gives a state (r = 0
everywhere, the tile's bit 1, auxiliaries as in P3a and P3b); a state gives a tiling (all references are equal; at each site exactly
one tile is on, and neighbours match). So the plane is tiled iff the pattern lives, which is undecidable (Berger 1966). Known in this
form: Freedman 1998 (k-SAT on groups). ∎ (check.py K3: 300 random tile sets on 2 × 2 and 3 × 3 tori, the encoding lives iff the tiles
tile the torus, 201 and 99, and decoding gives a tiling.)

With a seed (one site fixed), Turing machines and counters are simulated (Wang 1961). What fails against T1 is the bounded interface:
a patch of the plane meets the rest along a boundary that grows with it, so no finite set of relations summarises it. Substitution
tilings enforced by local rules (Robinson 1971, Mozes 1989) are the nested analogue, by analogy only.

## Scope

T1 and T2 are for the A79 language; nothing here shows that counting needs unbounded interfaces, only that bounded Boolean interfaces
with uniform recursion are finite-state and that one setting with growing interfaces is undecidable.
