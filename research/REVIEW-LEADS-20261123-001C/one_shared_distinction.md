# One shared distinction between the sides: hidden settings give a common explanation

Part of `REVIEW-LEADS-20261123-001C`. An argument by the thread, written before the census ran; the census checks it on
every pair with a cut of one. Scientific referee pending.

## Statement

Let a structure consist of Alice's side and Bob's side, and let exactly one two-valued distinction *h* be held on both
sides, by one knot on each. Every other distinction is held on one side only. Each observer has two settings. A setting
may change the knots and distinctions of the observer's own side in any way (any births, any allocation of payments);
it changes nothing on the other side and never removes *h*. For each pair of settings, every allowed word of the
resulting structure has equal weight. An observer's record is any set of distinctions of its own side other than *h*,
which may depend on its setting.

Suppose the settings are hidden: for each setting of Alice her record has the same distribution under both of Bob's
settings, and likewise for Bob. Then the four tables of joint records have a common explanation: one weighting on the
two values of *h*, not depending on the settings, and for each observer a chance of each record given its own setting
and the value of *h*. In particular the four-correlation (CHSH) score of any outcomes computed from the records is at
most 2, and every other inequality of that kind holds as well (Fine 1982).

Nothing in the argument uses which knot laws are present.

## Argument

**The tables are mixtures over *h*.** Fix settings *a* and *b*. Because the two sides share only *h*, the number of
allowed words with *h* = η, Alice's record *r* and Bob's record *s* is a product N_a(r, η) · M_b(s, η), the first
factor counting completions on Alice's side and the second on Bob's. Write Z_a(η) for the sum of N_a(r, η) over *r*,
and W_b(η) likewise for Bob. Then

P(r, s | a, b) = Σ_η q_ab(η) · p_a(r | η) · p_b(s | η),

with p_a(r | η) = N_a(r, η) / Z_a(η), p_b(s | η) = M_b(s, η) / W_b(η), and q_ab(η) proportional to Z_a(η) · W_b(η).
If Z_a(η) = 0, the value η has weight zero at setting *a* and p_a(· | η) is set equal to p_a(· | 1 − η); the same
convention is used for Bob.

**What hiding forces.** Bob's record at (a, b) has distribution Σ_η q_ab(η) p_b(s | η). Hiding says this is the same
for a = 0 and a = 1. Since η takes two values, the difference is

(q_0b(0) − q_1b(0)) · (p_b(s | 0) − p_b(s | 1)) = 0 for every s.

So for each of Bob's settings *b*, either q_0b = q_1b, or p_b(· | 0) = p_b(· | 1). In the second case say that Bob's
record at *b* does not depend on *h*. The same holds for Alice: for each *a*, either q_a0 = q_a1 or her record at *a*
does not depend on *h*.

**A table at a setting whose record does not depend on *h* is a product.** If Alice's record at *a* does not depend on
*h*, then P(r, s | a, b) = p_a(r) · Σ_η q_ab(η) p_b(s | η) = p_a(r) · P_b(s), where P_b(s) is Bob's distribution at
*b*, the same for both *a* by hiding. Likewise for Bob.

**The common explanation.** Let A be the set of Alice's settings at which her record depends on *h*, and B the same
for Bob.

- If A or B is empty, all four tables are products of the two observers' own distributions, which do not depend on the
  far setting. That is a common explanation with no weighting needed.
- Otherwise choose a0 in A and b0 in B and let q = q_{a0 b0}. For any a in A and b in B, q_ab = q_{a0 b} because *b*
  is in B, and q_{a0 b} = q_{a0 b0} because a0 is in A. So every such pair has the same weighting q.
  Give Alice the chances p_a(r | η) at settings in A and the chances p_a(r), not depending on η, at her other setting.
  Give Bob the same. Then:
  - at a pair in A × B the model gives Σ_η q(η) p_a(r | η) p_b(s | η), the actual table;
  - at a pair with *a* outside A and *b* in B the model gives p_a(r) · Σ_η q(η) p_b(s | η). The sum is Bob's
    distribution at (a0, b), which by hiding is his distribution at (a, b), so this is p_a(r) · P_b(s), the actual
    table. The mirrored case is the same;
  - at a pair outside both the model gives p_a(r) · p_b(s), the actual table.

So one weighting on *h* and local chances reproduce all four tables. ∎

## Why two shared distinctions escape the argument

With two shared distinctions η takes four values. Hiding for Bob then says only that Σ_η (q_0b(η) − q_1b(η)) p_b(s | η)
vanishes for every *s*, which no longer forces q_0b = q_1b: the four distributions p_b(· | η) can be linearly
dependent. The four-type distribution of the pre-registration uses exactly this room, and whether knots can make such
side tables is what the census asks.

## What this adds

The bound of 2 for one shared two-valued distinction was proved in the four-readings study for settings read from the
state under one weighting. Here the weighting depends on both settings, through the counts of extensions, and the
bound still holds. The classical ingredient is Fine's theorem (1982), cited once.
