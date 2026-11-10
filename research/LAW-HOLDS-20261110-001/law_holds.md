# Does the law decide which atom holds the unit?

Epic `LAW-HOLDS-20261110-001` (backlog B79, G15; program learning), 2026-11-10, at the coordinator's go-ahead. Pre-registered in
[preregistration.md](preregistration.md). Proof family: `proofs/LAW-HOLDS-20261110-001A/LAW-HOLDS-20261110-001A-P001_host_faces_by_sign_class/`.

## The question

With the law fixed, a unit settled at the genus-2 floor never left its Fano atom under state flips (`RISE-ESCAPE-20261110-001`). Is that
because no state of that law has it anywhere else?

## The answer (exact, by SAT over every state)

Yes. Under the law learning left, every floor state has the unit inside the atom that still acts as its line, or at that atom's junction
faces; never inside the transparent atom, never at the upper level, on all 15 spaces (K_2 and K_3). Across all 16 sign classes the hosts
follow the atoms' roles: both atoms acting as their lines leaves no floor state (the sphere's contradiction returns); one acting holds the
unit in that atom; both transparent lets it sit in either atom, and at the upper level when the atoms are apart.

So the leftover tension lives in whichever named pattern still stands for its line. Where it sits is decided by what was learned, not by
where the point is, and only a change of law can move it.

## Against the pre-registration

L1 and L2 held in substance. As stated they fail on two details: when the atoms are adjacent, one junction face is shared by both and can
hold the unit; and adjacent atoms that are both transparent never hold it at the upper level.

## Corrections

None. This makes `RISE-ESCAPE-20261110-001`'s capped K_3 cases exact: no state of that law, reachable or not, has the unit elsewhere.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — does the law decide (B79) | **Status:** Successful | the acting atom holds the unit, in every state |
| Local direction — moving the unit | Continue, by changing the law | the trap is the law's, so learning must move it |
| Broader exploration — learning program | Known alternatives | learning at a rise |
| Long-term goal — G15 Learning: a point in a learned knot space | Capability gained | where tension sits is a learned fact |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Learning at a rise (B80) | 2/3 — Substantial | 3/3 — Ready | state and learning steps together, one unit above the floor, until the acting atom turns transparent and the other acts → the unit moves to the other atom, or not | Selected · started |
| 2 | Why the trap holds (B78) | 1/3 — Incremental | 3/3 — Ready | as recorded; now read as the class's constraint | Alternative · deferred |
| 3 | Learning on an overgrown surface (B70) | 1/3 — Incremental | 3/3 — Ready | as recorded | Alternative · deferred |

- **#1** is next by the coordinator's order and is now sharper: the unit moves exactly when the roles of the two atoms swap, which takes
  winding through both handles; B80's concreteness rises to 3/3.

**Corrections:** none. **Goals:** G15 checkpoint (capability gained); B79 taken; B80 re-rated. **Assumptions:** none new.
