# Learning that grows a handle

Epic `GROW-HANDLE-20261110-001` (sub-goal B60; G15 with G4 and G1; program learning), 2026-11-10, at the coordinator's go-ahead.
Pre-registered in [preregistration.md](preregistration.md). Proof family:
`proofs/GROW-HANDLE-20261110-001A/GROW-HANDLE-20261110-001A-P001_a_fano_atom_grown_at_the_dissonance/` (the builder, the growth move and
the checks); stress test one size past in [stress_test.py](stress_test.py).

## The question

On a knot sphere learning can move the forced dissonance but never remove it; on a torus it removes a dissonance the class forces, by
winding (`LEARN-HANDLES-20261109-001`). Can a local growth move add the handle where the dissonance sits, so that learning then removes it,
and does it matter where the handle grows?

## The answer

Yes. Grow a Fano atom (the Fano plane less a point, with its uniform signs, the knot's own self-contradiction) at a line of the sphere by a
3-edge splice, and:

1. **The space becomes a torus** (proved). Three of the six ways to join the atom keep both rotations and give a torus; the old law extends
   to the new sides with no even face, uniquely up to gauge.
2. **Growth alone does not remove the dissonance** (computed, then proved from it). In the grown law's class the atom allows on the
   replaced line's three points exactly what the line allowed: it acts as that line, so the sphere's contradiction survives. In the other
   three classes the atom allows everything: it is transparent. So the grown law is the only class no state satisfies. Growth changes what
   forces the dissonance, from the count to the class.
3. **Learning then removes it, through the new handle** (proved). With the state fixed, learning at the dissonance resolves it completely,
   and every resolution changes a sign in the atom or where it was joined: winding around the handle that growth made is what makes the
   atom transparent.
4. **Where the handle grows sets the cost** (computed). Grown at the dissonance, the violated line moves into the atom and learning
   resolves it in 3 sign changes, on K_2, K_3, K_4 and K_5 alike. Grown elsewhere the violated line stays put, and resolving costs more the
   farther away the atom is (on K_5 a mean of 5.7 sign changes one line away, 15.6 five lines away).

The rules of `NATIVE-TARGET-20261110-001` resolved every start: random moves, sight of radius 3, and the outside distance.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| The builder turns rotation systems into knot spaces correctly | checked on six spaces against their own rebuild (check 1) |
| Three bijections give a torus, three give genus 2; the law extends with no even face uniquely up to gauge (theorem 1) | proved by hand; checked on 288 splices |
| The atom acts as the replaced line in the grown class and is transparent in the other three (theorem 2) | computed on 540 grown tori, K_2 to K_5; not proved for every sphere |
| The grown law is the only unsatisfiable class (theorem 3) | proved, given theorem 2 |
| Learning resolves it, every resolution changing a sign in the atom or the new sides (theorem 4) | proved by hand; 2,592 walks checked |
| The extended state's violated line moves into the atom when grown at the dissonance | computed (every case, K_2 to K_5) |
| Cost 3 at the dissonance, growing with distance elsewhere | computed |
| Random moves, sight 3 and the outside distance resolve every start | computed (288 starts) |

## Against the pre-registration

H1, H3, H4 and H5 held. H2 held in its main claim, but its mechanism was wrong: the other three classes were expected to act as the
replaced line re-signed, and instead the atom is transparent in them.

## For the owner's picture

A sphere's dissonance is forced by its shape and no learning removes it. Growing a handle where the dissonance sits does not remove it
either: the new piece takes the contradiction over exactly. But the dissonance now sits in the new handle, and three sign changes,
going once around that handle, dissolve it, leaving the new piece transparent. Growth and learning together do what neither does alone, and
they do it most cheaply when the space grows where the tension is.

## Provenance and novelty

Known with delta. The splice and its genus are `THREEFOLD-SURFACES-20261030-001`; an atom acting as one line from outside echoes
`FAR-READ-20261106-001` and `ATOM-ONE-20261107-001` in the creation reading. New: the atom's transparency in the other classes, growth
turning a count-forced dissonance into a class-forced one, and learning removing it through the grown handle, cheapest at the dissonance.

## Corrections

None.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — learning that grows a handle (B60) | **Status:** Successful | growth plus learning removes what the sphere forces |
| Local direction — steering by re-signing | Continue | learning now has growth as a partner |
| Broader exploration — learning program | Known alternatives | chosen resolution, a native growth trigger, layers |
| Long-term goal — G15 Learning: a point in a learned knot space | Capability gained | the network grows where the point is stuck |

Unresolved: a proof of theorem 2 for every knot sphere, and other atoms or other spaces.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Choosing the resolution (B62) | 2/3 — Substantial | 2/3 — Testable | native rules given a target class on the thin and grown tori → every class reached, or some need more | Selected · started |
| 2 | Grow where learning is stuck (B68) | 2/3 — Substantial | 2/3 — Testable | a rule that grows an atom only where its sight finds no resolution → grows once at the dissonance, or misplaces | Alternative · deferred |
| 3 | Theorem 2 for every knot sphere | 1/3 — Incremental | 3/3 — Ready | the parity at the three merged faces fixes the atom's relation → proof, or a sphere where it fails | Alternative · deferred |
| 4 | A point moving between layers (sub-goal B54) | 3/3 — Barrier | 1/3 — Stated | smallest two-level network with one dissonance → it crosses levels, or not | Alternative · deferred |

- **#1** is next by the coordinator's order. The grown tori now add classes that differ by the new handle, so "which resolution" has a
  place where the choice is made.
- **#2** removes the last design choice in the growth move: here the experimenter chose where to grow.
- **#3** would make theorem 2 a proof.
- **#4** is unchanged, Payoff 3/3, Concreteness 1/3.

**Corrections:** none. **Goals:** G15 checkpoint (capability gained); sub-goal B60 taken; B54 carried; backlog B68 (grow where learning is
stuck) added. **Assumptions:** A48 added (the growth move brings a Fano atom with uniform signs and completes the law with no even face);
history line for A26.
