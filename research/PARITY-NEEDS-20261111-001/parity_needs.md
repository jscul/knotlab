# What a knot space needs to compute parity

Epic `PARITY-NEEDS-20261111-001` (backlog B147, G15 with G16; program learning), 2026-11-11, at the coordinator's go-ahead. Pre-registered in
[preregistration.md](preregistration.md), frozen in commit `b6ededb25` before the search ran. Proof family:
`proofs/PARITY-NEEDS-20261111-001A/`.

## The answer

**One handle is enough.** The 8-point lattice torus (2, 0, 4), in its most constrained class, computes the parity of three held points
exactly: hold points 0, 1 and 4, and point 5 is forced to their sum mod 2. Genus 0 cannot carry a parity gadget with its terminals on one
face unless P = NP. So, in the searched range, the least genus for parity is 1.

- **The headline gadget refereed (exact).** `UNATE-20261111-001`'s 8-point genus-4 gadget passed an independent check by fresh code: a valid
  knot space with a Kasteleyn law, every line a knot and the four-point parity relation a knot under the canonical K1–K3 test.
- **The least genus (exact, capped search).** Of 281 lattice tori up to 20 points, 16 (from 8 to 18 points) compute parity; random knot
  spaces steered to genus 2 and 3 compute it too (20 and 12 maps); the 113 steered random tori did not. No other non-unate map occurs.
- **Genus 0 (conditional, by hand).** Planar NAE-3SAT is polynomial (Moret 1988); three four-point parity gates sharing a local reference
  make a crossover (after Lichtenstein 1982), so a planar disk gadget would make planar NAE-3SAT NP-hard.
- **Where parity sits (computed, after the run).** In every one of the 16 tori, parity occurs exactly in the class with the fewest floor
  states, the class where the held points leave nothing free; a small most-constrained class is not enough on its own.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| The 8-point genus-4 gadget is a valid knot space and its parity relation a K1–K3 knot | independent check (fresh code, canonical test) |
| An 8-point lattice torus computes three-input parity; 16 of 281 lattice tori do | exhaustive computation |
| No planar disk parity gadget unless P = NP | proved by hand from Moret 1988 and an XOR crossover |
| Parity sits exactly in the most constrained class of each of the 16 tori | computed, after the run |

## Against the pre-registration

My prediction of no parity on tori was wrong: genus 1 suffices. The search finished in under a minute, far inside its caps; no space or
part was dropped. After the run the summary step read the part files under the wrong key; it was corrected and re-run alone, the search
untouched.

## What it changes

- **Counting needs one handle, not many.** The learned memories' atoms are tori too (the thin torus (2, 1, 2) has 4 points); an 8-point
  lattice torus in the right class counts three held points. Why the memories never count is where their held points sit: on an atom's
  three sides, not inside a torus in its tightest class.
- **The step toward sub-goal B146 is concrete now.** A memory that grows or writes a (2, 0, 4) torus and holds points inside it would
  compute parity; whether learning can reach that class is the open question.

## Assumptions

None added or changed. Relied on: A20, A46, A47, A58.

## Corrections

None.

## In the owner's words

Counting does not need a tangle of handles: one ring of eight points, wound into its tightest pattern, counts any three of them into a
fourth. A flat sheet cannot, unless every hard problem is easy.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: what a knot space needs to compute parity (B147) | **Status:** Successful | least genus 1, smallest an 8-point torus in its most constrained class |
| Local direction: what held points can compute | Exhausted for this phase | the least genus and the place parity sits are found |
| Broader exploration: learning program | Known alternatives | a learned memory that computes parity, the probe as a theorem |
| Long-term goal: G15 Learning: a point in a learned knot space | Capability gained | a single torus in its tightest class counts |

**Next step:** Research directions — selected: #1 (holding, per the coordinator, until a go-ahead)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A learned memory that computes parity (sub-goal B146) | 3/3 — Major | 2/3 — Testable | grow a (2, 0, 4) torus as an atom, hold four of its points as the interface, and ask whether the learner reaches its most constrained class from the parity examples → a learned parity map, or what stops it | Selected · awaiting go-ahead |
| 2 | A probe that is a theorem (B130) | 2/3 — Substantial | 1/3 — Exploratory | as recorded | Alternative · deferred |
| 3 | How learning cost grows with atoms (B143) | 1/3 — Incremental | 3/3 — Ready | as recorded | Alternative · deferred |

B146's concreteness rises to 2/3: the gadget is now an 8-point torus of a known kind, in a known class.

**Corrections:** none. **Goals:** G15 checkpoint (capability gained, with G16); B147 taken; B146's concreteness raised to 2/3.
**Assumptions:** none new or changed.
**Basket:** B146 (a learned memory that computes parity), B130 (a probe that is a theorem); taken: B146 as the selected next step,
awaiting a go-ahead.
