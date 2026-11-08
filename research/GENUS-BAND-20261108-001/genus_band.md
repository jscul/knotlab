# Higher genus by bands

Epic `GENUS-BAND-20261108-001` (program foundations), 2026-11-08.

## The question

- **Where it comes from.** `BAND-SURFACE-20261108-001` proved that one band joined to a loop of rings on both sides makes the torus with
  every contact persistent, and its census found balanced first bands on surfaces of genus 2 to 4. The coordinator relayed its direction
  1 on 2026-11-08: add a second band in every way to the balanced genus-2 first bands on loops of 5; stop at a balanced genus-2 network
  after two bands, or the step where every band fails; then say whether a "one band per handle" law extends.
- **The question.** Can bands keep growing a surface of genus 2, or add handles one band at a time, with every contact persistent?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The genus-2 first bands are the twisted ones.** On a loop of 5 rings, the 20 balanced genus-2 first bands are exactly those with two or three twisted columns, a column being twisted when both of its rings reverse their order. | exploratory census, exact | A |
| 2 | **The second band fails.** Of 770,520 second bands in four families (every rung subdivided, a loop stacked by single or double rungs, a loop joined to both rows), none keeps a genus-2 base balanced. | exploratory census, exact | A |
| 3 | **No second handle.** On the n × 2 tori (n = 3 to 5), 1,974,904 second bands in the same families keep every contact persistent only once per n: the torus band rule, which keeps genus 1. | exploratory census, exact | A |

## Answer

The stop rule's second outcome: the second band is the step where every band fails for genus 2, in every declared family. "One band per
handle" does not extend: one band makes the torus from a loop, and after that bands only grow the torus. Higher genus from bands comes
only from a single first band, which then cannot grow.

## Reading

**Interpretation, not a theorem.**
- **Why the torus is special.** The torus band rule keeps a half-turn at every contact, and the balanced genus-2 first bands have none:
  their balance is an accident of parity that any further band breaks. This matches `GROW-NET-20261108-001`: networks with a flip at
  every contact come at every size only on the torus.
- **For G1.** A uniform local law makes and grows one surface, the torus, with every contact persistent. The census finds no band law
  for higher genus; making it would need other moves, or giving up persistence at some contacts.
- **Not a metric.** Nothing here is a length or a distance.

## Lag cutoffs and census-only claims

- **No lag cutoff.** Balance is read exactly.
- **Census-only.** Every conclusion here is an exact census of declared families, not a theorem about all bands.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| No second handle (3) | the 5 × 2 torus, one past the scratch run's every-way case at 3 × 2, by uniform rules and 100,000 random cases | pass |

## Literature and provenance

- **Sources.** Rotation systems of prisms; regular maps and their finiteness in genus at least 2 (Hurwitz).
- **Classification.** New as far as found, a census.

## Workspace assumptions

- **Relied on.** A30, A32, A37.
- **Scope.** Equally spaced networks of rule-60 rings with law (12, 12) contacts; the declared families of second bands.

## Ratio

Since the epic opened:
- **Substantive.** One exact census (A).
- **Administrative.** This note and the closure.

## Pending the owner

- Nothing.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — higher genus by bands | **Status:** Successful | The stop rule's second outcome: every second band fails for genus 2, and no second band adds a handle |
| Local direction — growth from a law | Pivot within the line | Bands make and grow only the torus; higher genus needs other moves |
| Broader exploration — G1 with G5 | Known alternatives | Full reach on the cut-open torus (ready); which lattices compose everywhere (ready); growth chosen by the dynamics |
| Long-term goal — G1 Space from a law (question 9) | Obstruction learned | A band law makes the torus but no surface of higher genus, in the families tried |

**Corrections:** none. **Goals:** a G1 checkpoint with G5 (obstruction learned). **Assumptions:** none added.

- **What the attempt leaves open.**
  - Whether moves other than bands (handles glued from two bands at once, or bands of other lengths) can grow higher genus with every
    contact persistent.
  - Whether the balanced genus-2 first bands have a proof behind their parity, or are accidents.

**Next step:** Research directions — the band line has reached its obstruction; the ready proofs are the natural next work.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Prove full reach on the cut-open torus (`FULL-REACH-20261108-001`) | 2/3 — Substantial | 3/3 — Ready | Images of the doubled torus and the powers of two → a proof, or the first failing side | Alternative · deferred |
| 2 | Which lattices compose everywhere (`LATTICE-NET-20261108-001`) | 2/3 — Substantial | 3/3 — Ready | Rectangular, triangular and honeycomb tori → a characterisation, or the first counterexample | Alternative · deferred |
| 3 | Handles glued from two bands at once (G1) | 2/3 — Substantial | 1/3 — Stated | Glue a band pair across the n × m torus as a handle → a balanced genus-2 network, or none | Alternative · deferred |
| 4 | Growth chosen by the dynamics (G1, with G5) | 2/3 — Substantial | 1/3 — Stated | Let a contact's needs pick where the next band goes → a law, or none | Alternative · deferred |

1. **Full reach.** Ready and bounded.
2. **Which lattices.** Ready and bounded.
3. **Handles by band pairs.** A different move, so not covered by this census.
4. **Dynamics-driven growth.** Open-ended.

**Recommendation.** Research directions, leaning to direction 1, the coordinator's ready fallback.
