# Learning in handles

Epic `LEARN-HANDLES-20261109-001` (backlog B6; G15 with G4; program learning), 2026-11-09. Pre-registered in
[preregistration.md](preregistration.md) before any walk on a torus ran. Proof family:
`proofs/LEARN-HANDLES-20261109-001A/LEARN-HANDLES-20261109-001A-P001_learning_resolves_a_class_forced_pair_only_by_winding/`.

## The question

The owner asked on 2026-11-09 whether the learning line had been left. It had stopped after `RESIGN-STEER-20261107-001`, whose
selected next step, B6, was parked awaiting a go-ahead. On the knot sphere learning (changing the law's signs where dissonance shows,
the state held still) moves the forced dissonance anywhere, but a closed learning walk is a change of state in disguise, so learning
adds nothing to behaviour beyond where the law's even faces sit. B6 asks the question that leaves: can learning carry information that
no change of state can? Off the sphere, laws with the same even faces differ by a homology class that no change of state reaches.

## The answer

Yes, and exactly the class. Three theorems, proved by hand from the count and the matching theorem of `COUNT-SURFACES-20261107-001A`:

1. **Only χ = 0 can be resolved.** A law and a state are free of dissonance (no violated line, no over-agreeing face, no even face)
   only on a surface of Euler characteristic 0. On the sphere learning can move the forced dissonance into the law but never remove it;
   on a surface of genus 2 or more every state of every law over-agrees somewhere.
2. **The class-forced pair.** On a torus with a Kasteleyn law in a class that no state satisfies (the Fano plane's torus, the thin tori
   of even index), the least dissonance is one violated line and one face whose three corners all agree: two opposite charges that no
   change of state can cancel.
3. **Learning resolves it, and only by winding.** With the state fixed, one sign change at the violated line splits it into two holes,
   and walking them along the lines into the over-agreeing face resolves everything, leaving no even face and no other local mark. Every
   process that resolves the pair, whatever the state does, changes the law by a cycle that goes around a handle, so the law ends in
   another class. The only trace of learning is that winding: two bits on a torus, which no change of state can carry.

Checked and computed on the two Fano tori and 57 thin tori of even index up to 40 points:
- **E1.** Every class-forced law has states with one violated line; up to 20 points there are 70 on each Fano torus and n² on each thin
  torus (computed), each with exactly one face of deg 3.
- **E2.** From every least state read (all up to 20 points, 200 found by SAT beyond) and each of its three splits, learning reached the
  cheapest matching of every other class: 96,732 walks, every step at a dissonance, every end resolved, every change a winding cycle
  of the predicted class.
- **E4.** The cheapest walk into each class has exactly as many steps as the smallest cycle in its class change, on every torus. On a
  thin torus the short way around costs 2 and the long way about half the points.
- **E5.** A local rule that sees only the lines at a hole and the distance to the over-agreeing face, never stepping straight back,
  resolved all 9,608 starts and mostly went the short way around. Unbiased random moves resolved all 2,806 runs, in at most 69 steps on
  average at 40 points. The pre-registration expected the local rule to fail somewhere and listed success everywhere as the outcome
  against E5: it never failed. Theorem 3 says why. Any walk that resolves the pair winds, so the rule needs no plan to go around the
  handle: the winding is already written in the state.
- **S (stress test).** `RESIGN-STEER-20261107-001B`'s local rule, one size past: 300 of 300 targets on K_14 and K_16, and 2,698 of
  2,700 on nine non-octahedral spheres (one miss on a tube is not reached with ten times the budget). The published line holds.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| Only surfaces of Euler characteristic 0 can be free of dissonance (theorem 1) | proved, by hand, on every closed surface |
| A state with one violated line of a class-forced law has exactly one over-agreeing face (theorem 2) | proved, by hand |
| Such states exist on every tested torus; 70 per Fano torus and n² per thin torus up to 20 points | computed (all states up to 20 points; SAT beyond) |
| From any such state learning at the dissonance, state fixed, resolves the pair via a cheapest perfect matching (theorem 3.1) | proved, by hand |
| Every resolution of a class-forced pair, by any process, winds around a handle into another class (theorem 3.2) | proved, by hand, on every closed surface with χ = 0 |
| Every other class is reached directly from every least state and split: the 96,732 walks | computed (a finite check of theorem 3 and its extension to every class) |
| The cheapest walk into each class meets the cycle bound exactly | computed; the bound itself is proved |
| A local rule with an outside distance resolves every start: the 9,608 starts; random moves: 2,806 runs | computed (exploratory) |
| The sphere's local rule one size past (K_14, K_16, nine other spheres) | computed (stress test) |

## For the owner's picture

The point (a dissonance) on a sphere can be carried anywhere by learning but never made to vanish: the sphere's curvature forces it.
Give the space a handle and two things change. The point becomes a pair of opposite charges held apart by the class of the law, and
learning can now make it vanish completely, but only by carrying half of it once around the handle. What learning keeps from that is
not a mark anywhere in the law but which way it went around: a memory held by the shape of the space. On the sphere learning could only
move the dissonance into the law; here it removes a dissonance that no change of behaviour can remove, and what makes that possible
lives in handles, as emergence does (G4).

## Provenance and novelty

Known with delta. In dimer language a resolved configuration is a perfect matching, the four classes are the torus's winding sectors
(Kasteleyn's four Pfaffians), the holes are a worm algorithm's monomers, and theorem 3.2 is the folklore that local moves keep the
winding sector while a worm must wrap the torus to change it. New here are its reading as learning against change of state, with the
worm acting on the law and the state held fixed; theorem 1's place for χ = 0; the pair on the class-forced tori, which include the Fano
plane; and the costs and the local rule's success.

## Corrections

None. The stress test of `RESIGN-STEER-20261107-001B`'s local rule passed one size past.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — learning in handles (B6) | **Status:** Successful | learning resolves class-forced dissonance, only by winding |
| Local direction — steering by re-signing | Continue | the learner now has a job no state change does |
| Broader exploration — learning program | Known alternatives | native target, chosen resolution, growth, layers |
| Long-term goal — G15 Learning: a point in a learned knot space | Capability gained | learning carries the class, two bits per handle |

The attempt leaves unproved the n² count of least states and the exact match between the cheapest walk and the cycle bound (both
computed), and that every class is reached directly from every least state (computed; proved for the cheapest class).

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A native target for learning (B61) | 2/3 — Substantial | 3/3 — Ready | rerun check 5 with signals the law and state supply → one beats random, or none does | Selected · awaiting go-ahead |
| 2 | Choosing the resolution (B62) | 2/3 — Substantial | 2/3 — Testable | a local rule given a target class on thin tori → every class reached, or the long one needs more | Alternative · deferred |
| 3 | Learning that grows a handle (sub-goal B60) | 3/3 — Barrier | 1/3 — Stated | glue one handle where a sphere's dissonance sits → it resolves by winding, or placement matters | Alternative · deferred |
| 4 | A point moving between layers (sub-goal B54) | 3/3 — Barrier | 1/3 — Stated | smallest two-level network with one dissonance → it crosses levels, or levels stay independent | Alternative · deferred |
| 5 | Many points at once on a torus (B3) | 1/3 — Incremental | 2/3 — Testable | two class-forced pairs, every update order → they resolve independently | Alternative · deferred |

- **#1** moves A26, the last outside input in the learning picture: the distance to the over-agreeing face is supplied by the
  experimenter. The code and the baseline (random moves resolve everything, at most 69 steps on average at 40 points) are in hand. Its
  resource bound is one run like check 5, minutes. The main uncertainty is which native signals exist: the count of consistent states
  (A27) and the face's own visible over-agreement are the first two.
- **#2** reads the owner's "guide the points to some action": the three classes a pair can resolve into are three different
  resolutions. The local rule mostly takes the short way; whether a target class can be reached locally on a long thin torus is open.
- **#3** is the most striking reading of the result. A sphere's dissonance cannot be resolved, a torus's can, so a learner stuck with
  forced dissonance would need to grow a handle. Branched double covers of the knot sphere at four corners are tori in which every class
  is satisfiable (`COUNT-SURFACES-20261107-001A` check 8), but no native move that grows a handle exists in the record
  (`GENUS-BAND-20261108-001`: bands add no handle to the torus), hence 1/3.
- **#4** is recorded as sub-goal B54 with its first step.
- **#5** is narrowed by theorem 3.2, which makes every resolution wind; whether pairs on one torus interact is untested.

**Corrections:** none. **Goals:** G15 checkpoint (capability gained); B6 taken; sub-goal B60 added (learning that grows a handle), B54
carried; backlog B61 (selected, awaiting go-ahead) and B62 added. **Assumptions:** A46 added (an over-agreeing face and an even face are
dissonance); history lines for A20, A21 (the boundary off the sphere) and A26 (theorem 3.2 does not rest on it).

## Final report as sent

Sent to the owner in the project thread on 2026-11-10 (00:08 UTC).

**Learning in handles is done and published, and it's the result the learning line was missing: learning can do something no change of behaviour can, and it only does it around a handle.**

On a sphere the forced contradiction can be moved by learning but never removed. On a torus whose law is in a class no state can satisfy (the Fano plane's torus, and the thin tori), the contradiction is a pair of opposite charges: one violated line and one face where everything over-agrees. Learning removes the pair completely and leaves no local mark, but only by carrying half of it once around the handle. Every way of removing it winds, whatever the state does, so the only thing learning keeps is which way it went around (proved; 96,732 walks checked on 59 tori up to 40 points). A local rule that only heads for the over-agreeing face resolved all 9,608 starts. I had pre-registered that it would sometimes fail; it never did, because the winding is already written in the state. The old sphere result held one size past.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: learning in handles (B6) | **Status:** Successful | learning removes class-forced dissonance, only by winding |
| Local direction: steering by re-signing | Continue | the learner now does what no state change can |
| Broader exploration: learning program | Known alternatives | native target, chosen resolution, growth, layers |
| Long-term goal: G15 a point in a learned knot space | Capability gained | learning carries the class, two bits per handle |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A native target for learning (B61) | 2/3 — Substantial | 3/3 — Ready | rerun the local rule with signals the law and state supply → one beats random, or none does | Selected · awaiting go-ahead |
| 2 | Choosing the resolution (B62) | 2/3 — Substantial | 2/3 — Testable | local rule given a target class on thin tori → all reached, or the long class needs more | Alternative · deferred |
| 3 | Learning that grows a handle (sub-goal B60) | 3/3 — Barrier | 1/3 — Stated | glue one handle where a sphere's dissonance sits → it resolves, or placement matters | Alternative · deferred |
| 4 | A point moving between layers (sub-goal B54) | 3/3 — Barrier | 1/3 — Stated | smallest two-level network with one dissonance → it crosses levels, or not | Alternative · deferred |
| 5 | Many points at once (B3) | 1/3 — Incremental | 2/3 — Testable | two pairs on one torus, every order → they resolve independently | Alternative · deferred |

#1 removes the last outside input: today the experimenter tells the rule where the over-agreeing face is. #3 is the most striking reading. If a sphere's dissonance can't be resolved but a torus's can, a learner stuck with forced dissonance would have to grow a handle. Both 3/3 rows are recorded as sub-goals under G15.

**Corrections:** none. **Goals:** G15 checkpoint (capability gained); B6 taken; sub-goal B60 added, B54 re-rated; B61 and B62 added. **Assumptions:** A46 added (over-agreeing and even faces count as dissonance); history lines on A20, A21, A26.
