# Pre-registration: which atom a growth law grows

Epic `NATIVE-ATOM-20261110-001` (backlog B106, G15 with G16), written on 2026-11-10 before any run, at the coordinator's go-ahead. It is
exploratory: if the first census gives no foothold, the epic stops and reports rather than widening the class.

## The question

Every learning epic grew an atom chosen by the experimenter, with its law chosen too (A52: a class-forced torus atom, brought in its
unsatisfiable class). Can a uniform local growth rule, with nothing designed in, grow an atom that remembers where a dissonance sits?

## The class of rules searched, frozen

A rule **σ(T, p)** fires at a violated line: it removes the line and splices in T less a point, by a compatible splice (as in
`GROW-HANDLE-20261110-001`), the three new sides completed with no even face (forced up to gauge, lemma 1 of `OTHER-ATOMS-20261110-001A`).
T ranges over the lattice-torus types of `OTHER-ATOMS-20261110-001D` (157 types to 30 points, thin tori of even index to 40); the atom's
law is **uniform**: one sign pattern p = (p_0, p_1, p_2) on the three sides of every line by side index, nothing else chosen. That is 8
patterns per type: two constant (the plain law) and six non-constant. The rule is the same at every site and reads nothing but that a line
is violated.

**"Grows an atom that remembers at a dissonance"** means: fired at the violated line of a state violating that line alone (a flat state)
on a knot sphere, the grown atom acts as its replaced line, so the grown space still has no satisfying state and the unit sits in the atom.
By lemma 2 there and ticket D's freeness, this holds exactly when T's uniform law has no satisfying state.

## The claim to prove (ticket A) and the census

- **U (by hand).** σ(T, p) grows an atom that remembers exactly when T is the Fano torus and p is constant. A non-constant pattern is
  satisfied by the all-zero state on every line (theorem 1 of `UNIFORM-FANO-20261107-001A`); a constant pattern is the plain law, and a
  lattice torus is point- and line-transitive, so its plain law is unsatisfiable only on the Fano plane (that record's corollary). So the
  4-point thin atom, and every class-forced atom but Fano, can be grown by a uniform rule only as a transparent atom.
- **Census (computed, exhaustive per type).** For each of the 157 types and 8 patterns: the law is Kasteleyn, and whether it is
  satisfiable. **Expected:** satisfiable in every case except the Fano torus with a constant pattern.
- **Failure line.** A non-Fano type with an unsatisfiable uniform law, or the Fano torus's constant law satisfiable (either contradicts the
  cited theorem or the code).

## Ticket B: growth, then learning (exact, then computed)

- **B1 (exact).** On K_2 and K_3, at the flat state of the first line-orbit representative, fire σ(Fano, 000) and σ(thin (2,1,2), 000):
  the Fano atom acts and no state satisfies every line; the thin atom is transparent and some state does (growth alone resolves).
- **B2 (computed).** A transparent atom can still be written by learning. On K_3 with two uniform thin (2,1,2) atoms grown by σ (at l0 and
  the first line at the largest distance; genus 2, floor one unit), from the first satisfying state of the grown law, the frozen targeted
  search of `ADDRESS-SEQ-20261110-001A` writes each single address ({0}, then {1}, then {0}), with a one-point disturbance and the learner M1
  after each (random.Random(106)), on each line orbit. **Expected:** every address written and held. **Failure:** a write not reached.

## Stop rule (one epic)

If U and the census hold, the answer is stated for the class: within uniform substitution rules on lattice tori, only the Fano atom grows a
memory by growth alone, and any class-forced atom can be made to remember by learning after a uniform growth. The epic then stops; other
classes of growth rules (atoms built from the line's own neighbourhood, rules reading more than one violated line) are recorded, not
searched.

Assumptions in force: A20, A21, A46, A47, A49, A50, A52 (the premise under study). Each check is expected to take under ten minutes.
