# Pre-registration: nativeness up to renaming

Epic `PLACE-FLIP-20261110-001` (`BARE-NAMES-20261110-001` direction 1, the challenge of A59; G1; program topology, group `spacing`),
written on 2026-11-10 before any run, at the coordinator's go-ahead of 18:43 UTC.

## The question

- **A59.** Under abstract names a renaming of finitely many names is a finite change. It flips every distinction, so the source-aware
  condition ("a knot is native only when each of its variables is flipped by a finite change") excludes nothing.
- **The challenge.** Count changes up to renaming. Are the 90 board-value knots of `BARE-NAMES-20261110-001B` still native?

## Known before registration (disclosed)

- **The lemmas.** Ticket A's L1 to L5 were sketched by hand while this registration was written.
- **Transplants.** One of them changes what the count must exclude. When values and neighbour distinctions change together, a place
  can be cut out of one region and wired into another by a finite change that is not a renaming (L4). A count that excludes only
  renamings therefore still excludes little.
- **The control.** Ticket B's code was run on its control, the full law, and on no law of the family.

## Frozen (at the coordinator's request)

- **What counts as a value flip that is not a renaming.** A value s(u) is **flipped in place** at a state x by a finite change of
  values alone that:
  - keeps every neighbour distinction;
  - gives an allowed state and flips s(u);
  - is not a renaming, so the new state is not x ∘ π for any permutation π moving finitely many names;
  - is minimal: no allowed change of a proper subset of its values flips s(u).
- **A neighbour distinction flipped in place.** The same, with neighbour distinctions alone changed and every value kept.
- **The mark.** A law's knot is **native in place** at x when, for some edge {u, v}, n(u, v), s(u) and s(v) are all flipped in place.
  Each of the 90 laws gets two marks, one in a world of finitely large components (copies of a frozen coloured board) and one in a
  tree world (the universal cover of one). The worlds, boards, search bounds and predictions are in ticket B's contract
  (`experiments/PLACE-FLIP-20261110-001B/PLACE-FLIP-20261110-001B-E001_flips_in_place/contract.json`).
- **A59's status.** If every knot is native in place in its world of finite components (C2), A59 becomes Confirmed for these knots:
  they do not rest on renamings. If not, the laws native only through renamings are recorded as resting on A59, which stays Assumed.
- **The canonical test.** No change to it is proposed. If a result bears on it, it goes to the owner as a question, and the epic stops
  there.
- **Stop rule, one epic.** The census runs once, with no extension of the family or the worlds.
