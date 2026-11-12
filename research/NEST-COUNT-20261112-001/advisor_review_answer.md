**Verdict:** the mathematics is essentially sound and known in kind; the errors are in wording, one missing case, and the closing claims.

**T1 — correct, with gaps.**
- The counts are right: 16 complement-closed relations on three ports, lattice height 4, so at most 4s decreases from TOP.
- It assumes the call graph is acyclic apart from SELF and that call arguments are distinct; state both.
- Reaching the greatest fixed point by iteration is Kleene iteration on a finite lattice, not Knaster–Tarski (which gives existence only).
- Usual limit: the final formula is right, but the "only if" is false as worded. The knot also recurs if the body has a knot directly on its ports, or via a sibling or helper call on the same arguments. Both cases are absorbed by the union, so "exactly" survives.
- "Same fixed point" is wrong: it is the fixed point of a modified description (add K(ports) to each pass-through definition, delete the pass-through calls).
- Liveness of the limit pattern can differ from the limit of "depth-t lives"; say so.

**T2 — correct for the top window only.**
- "Ends" is overclaimed: nothing is proved about bottom windows, whose context depends on the path.
- "Distinguishes infinitely many depths" should read: the window takes at most 16^s values, eventually periodically. It does count depth mod the period.

**P3a — correct.** If x=y, then a=b=c=¬x; equality via two inequalities works. Equality needs 7 auxiliary distinctions, more than l=6, so inside A79 it must be nested as two inequality definitions.

**P3b — correct.** Böhler–Reith–Schnoor–Vollmer 2005 gives NAE as a base of IN2. Note that co-clone pp-definitions allow equality, which P3a supplies.

**P3c — sound.**
- Complement symmetry is handled by the tied references, and translation invariance holds because gadget auxiliaries are per-site.
- Add an explicit per-site "valid tile code" constraint.
- Say "tiling exists iff pattern lives", not "preserving".
- The result is known: cite Freedman, "k-SAT on groups and undecidability" (STOC 1998). I am not certain the Marathe et al. attribution for 2-D undecidability is exact; check it.
- Wang 1961 is the seeded (origin-constrained) case only.
- Robinson/Mozes is an analogy, not a theorem about your nested language.

**"Counting needs unbounded interfaces" — overclaimed.**
- Proved: bounded Boolean interfaces with uniform recursion give finite-state behaviour (pigeonhole).
- Proved: one unbounded-interface setting is undecidable.
- Not proved: necessity. Unbounded port alphabets or non-uniform, depth-indexed descriptions are unexcluded alternatives.
- "No pattern counts" also contradicts T2's own parenthetical, which leaves inside-counting open. Restrict it to "no top-window counter beyond mod-p".
