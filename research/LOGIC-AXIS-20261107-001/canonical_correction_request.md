# Does a native knot need a native binding?

Status: open
Raised: 2026-11-07
Commitment: The source-aware reading for infinite systems (AGENTS.md, canonical knot test paragraph; docs/FOUNDATIONAL_THESIS.md, "Source condition for infinite systems"): "A knot is native at a solution only when each of its variables is flipped there by some change of finitely many variables."
Decision: Whether a native knot on an infinite system must also be natively bound (a knot of the closure of its solution's finitely-different solutions), or whether claims about distance or locality should only state whether the law has ends, because per-variable nativity does not control where a knot's binding comes from

## Evidence

`LOGIC-AXIS-20261107-001A-P001`, Proposition 5
([proof](../../proofs/LOGIC-AXIS-20261107-001A/LOGIC-AXIS-20261107-001A-P001_rulers_without_ends/proof.md)).

**The law.** There are three distinctions per site of Z^2:
- x obeys Ledrappier's law x(t) + x(t + e_1) + x(t + e_2) = 0, which has no finite moves;
- z is free;
- y = x + z.

**What happens in it.**
- **Every variable is native.** Each y_p and z_p is flipped by the finite move that changes both
  together. So under the source-aware reading every knot of this law is native at every allowed
  state.
- **Yet a knot joins far points.** For every k, the six variables y and z at the sites 0, 2^k e_1 and
  2^k e_2 form a knot. So bond distance between y_0 and y_{2^k e_1} stays at most 5 however large k
  is.
- **Where the binding comes from.** The binding passes through the hidden field x, whose openness is
  supplied entirely by the ends.

**The contrast.** Proposition 2 of the same proof shows that a parity law whose finite moves are dense
(a law without ends) splits. Its knots are chained, so bond distance grows at least linearly with
separation. The relevant condition is a property of the whole law, not of a knot's own variables.

## Options

- **(A) Keep the reading as it is.** Add a sentence: "Per-variable nativity concerns where a knot's
  distinctions are opened, not where its binding comes from. A claim about distance, locality or
  spacing on an infinite system must also state whether the law has ends (finite moves dense or not)."
- **(B) Also require a native binding.** A knot S is *natively bound* at a solution x when S is also a
  knot of the closure of x's homoclinic class: the solutions that differ from x in finitely many
  places.
  - **Parity laws.** That closure is x + closure(F), with F the finite moves. Its own finite moves are
    F and are dense in it, so by Proposition 2 of `LOGIC-AXIS-20261107-001A-P001` it splits, and every
    natively bound knot is chained. So bond distance built from natively bound knots is a ruler in
    every parity law.
  - **Laws without ends.** Nothing changes.
  - **The product law above.** The long-range six-variable knot is not natively bound: on the closure
    of the finite moves it falls apart into three two-place ties (y = z at each site).
  - **Ledrappier's law.** No knot is natively bound, consistent with its frozen label.
  - **Non-linear laws.** The definition applies as stated. Whether natively bound knots are always
    chained there is open.

**Recommendation: (B).** It makes "native" imply "local" for parity laws and adds no new primitive: it
reuses the finite moves that already define the source-aware reading. (A) is the minimal fallback if
the owner prefers not to change the definition.

## Consequences

- **Under (A).** Every earlier source label stands. Future infinite-system claims add one field: ends
  present or absent.
- **Under (B).** Each infinite-system knot gets a third label, natively bound or not.
  - The examples of `FROZEN-WORLDS-20261020-001` and `HOLES-AT-INFINITY-20261020-001` keep their
    verdicts:
    - Tseitin's and the gauge law on Z^2 have no ends, so their native knots are natively bound;
    - Ledrappier's law has no native knot under either reading.
  - Knots whose binding passes through frozen witnesses would be relabelled.

The canonical documents are not edited by this request.
