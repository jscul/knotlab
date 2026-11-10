# The learning line, 2026-11-09 to 2026-11-10

Epic `LEARN-NOTE-20261110-001` (backlog B95, goal G15). A plain account of fifteen epics, written for the owner to judge as a whole. Each
claim carries its evidence class:

- **proved**: by hand;
- **computer-assisted**: a proof whose finite part is an exhaustive computation;
- **exact on small cases**: exhaustive (SAT over every state, or every state enumerated) on the stated spaces only;
- **computed**: searches, samples or runs on the stated spaces, not exhaustive.

Every space here is an octahedral knot sphere K_k or a torus built from one, small (K_2 to K_8, 16 to 256 points).

## 1. Where it started

The owner's picture (G15): a point with a strength, moving through a learned network of knots, guided by learning to a resolution. The
program reads the point as a dissonance (A20), learning as changing the law's signs where dissonance shows (A21), and dissonance as violated
lines, over-agreeing faces and even faces (A46), weighed as the count weighs them (A49).

Before this line, `RESIGN-STEER-20261107-001` had shown that on a knot sphere one sign change moves the forced dissonance into the law and
learning carries it anywhere (proved), but that on a sphere a closed learning walk is a change of state in disguise (proved). Its next step,
learning in handles, had waited since 2026-11-07. On 2026-11-09 the owner asked whether the line had been left.

## 2. The line, epic by epic

1. **Learning removes a dissonance only by winding** (`LEARN-HANDLES-20261109-001`). Only a surface of Euler characteristic 0 can be free
   of dissonance (**proved**). On a torus whose law is in a class no state satisfies (the Fano tori, thin tori of even index), the least
   dissonance is one violated line and one fully agreeing face; with the state fixed, learning resolves it, and every resolution by any
   process winds around a handle into another class (**proved**). 96,732 walks on 59 tori up to 40 points reached every other class
   (**computed**, a finite check of the theorem); a local rule with an outside distance resolved 9,608 of 9,608 starts (**computed**).
2. **A native target** (`NATIVE-TARGET-20261110-001`). Without the outside distance, a learner that sees its own moves three ahead, or one
   that keeps the most states sharing its dissonance, resolves every start and beats random moves (**computed**, to 46 points).
3. **Growing a handle** (`GROW-HANDLE-20261110-001`). Splicing a Fano atom (the Fano plane less a point) at a sphere's line makes a torus
   whose law extends with no even face (**proved**). The atom acts as the line it replaced in one class and is transparent in the others
   (**exact on small cases**: 540 grown tori, K_2 to K_5; later **computer-assisted** for every K_k, item 15). Learning then removes the
   sphere's dissonance through the grown handle (**proved**), in 3 sign changes when grown at the dissonance (**computed**).
4. **Choosing the resolution** (`CHOOSE-RES-20261110-001`). A learner told a target class reaches it (3,173 of 3,186), close to the cheapest
   walk (**computed**); a long class costs about half a thin torus (**proved** lower bound).
5. **A dissonance floor** (`GROW-STUCK-20261110-001`). W ≥ |χ|/2 in every state of every law (**proved**): one handle from a sphere is
   exactly enough, and each further one adds a unit no learning removes. A learner that grows only when stuck grows once at the dissonance
   if it sees three steps ahead, and overgrows otherwise (**computed**, K_2 to K_6).
6. **Layers through atoms** (`ATOM-LAYERS-20261110-001`). The dissonance flows down into atoms; at genus 2 the floor unit is one
   over-agreeing face no fixed-state learning step can move (**proved**).
7. **A moving state** (`MOVING-STATE-20261110-001`, the challenge of A26). Letting the state flip one point between learning steps frees a
   stuck learner in about half the runs (**computed**); A26 was overturned as a limit on what learning reaches, replaced by A50.
8. **A rise does not free a settled unit** (`RISE-ESCAPE-20261110-001`). With the law fixed, state flips one unit above the floor never move
   a settled unit out of its atom (**exact** on five K_2 components; capped elsewhere).
9. **The law decides where the leftover lives** (`LAW-HOLDS-20261110-001`). The floor unit sits only in an atom that acts as its line
   (**exact on small cases**, SAT over every state, 15 spaces).
10. **Learning at a rise moves it** (`LEARN-RISE-20261110-001`). The pre-registered search was capped (inconclusive); a targeted search found
    paths on all 9 starts (**computed, post hoc**), confirmed under a frozen prediction on fresh starts in item 11.
11. **A learned address** (`ADDRESS-20261110-001`). Learning places the leftover in any chosen atoms (every pair of three, 9 of 9) and the
    role swap holds on 6 fresh starts (**computed**, pre-registered).
12. **Reading it** (`READ-ADDRESS-20261110-001`). Writing holds at K_4 (15 of 15); the address is read from each atom's own signs in 23 of 24
    written cases (**computed**).
13. **It steers later learning** (`ADDRESS-STEER-20261110-001`). The atom rule (item 15) holds on 1,280 classes of 11 spaces (**exact on
    small cases**); four atoms written (12 of 12); after a fresh tension the learner returns to the written address in 240 of 240 runs at one
    flip and 463 of 480 at two or three (**computed**).
14. **It can be rewritten** (`ADDRESS-SEQ-20261110-001`). 90 addresses written in turn on 14 spaces, K_3 to K_5, each held after a
    disturbance, never reverting to the previous one (**computed**, pre-registered).
15. **The atom rule** (`ATOM-RULE-20261110-001`), **computer-assisted**, scope below.

## 3. The atom rule, exactly

**Statement.** On an octahedral knot sphere K_k, k ≥ 2, with its Kasteleyn law and Fano atoms spliced at lines whose neighbourhoods are
disjoint (separated atoms), with the new sides signed so that no face is even:

1. each atom acts as its replaced line in exactly one of the four classes of its own handle, independently of the other atoms;
2. if every atom acts, no state satisfies every line;
3. otherwise, every state that satisfies every line has a unit of the floor dissonance in each acting atom's region.

**Evidence.** Computer-assisted: the homology decomposition and the locality lemma by hand; a finite local check on 2,700 splices (every
line of K_5 to K_7, every line orbit of K_2 to K_4, every compatible splice); line neighbourhoods classified into four types over K_2 to K_8,
none new beyond K_3, with a structural reason.

**Outside the theorem.**
- Atoms whose neighbourhoods overlap (lines at small distance): only the exact small-case results of item 13 cover them.
- That units beyond the acting atoms are free (when fewer atoms act than there are units): **exact on small cases** only (item 13).
- Spheres other than the octahedral ones (backlog B96), and atoms other than the Fano atom with uniform signs (A48).

## 4. Where the pre-registrations were wrong

Recorded as failed predictions, not hidden:
- A local rule would sometimes fail to resolve a class-forced pair (item 1): it never did, because every resolution winds.
- The atom in the other classes would act as the line re-signed (item 3): it is transparent instead.
- Untargeted learners would default to the short resolution (item 4): random learners mostly take the long way (13% short).
- An overgrown learner would sit at the floor of each new genus (item 5): it sits two above, carrying a pair.
- With one atom away from the dissonance a sight-4 learner would resolve (item 6): it is stuck, the resolution being longer.
- A moving state would carry a settled unit into another atom (items 7, 8): it never does at constant or one-unit-raised dissonance.
- The pre-registered search for learning at a rise (item 10) was too shallow to decide.

## 5. Open observations

- **Stuck returns (B90).** 10 of 480 returns in item 13 stopped one unit above the floor with no move lowering the dissonance. The atom rule
  concerns floor states and does not predict them.
- **Erasures by winding.** 7 of 480 returns in item 13 reached the floor with one or both acting atoms turned transparent: a learning step
  during the return wound through an atom's handle and erased its bit (`ADDRESS-SEQ-20261110-001` ticket B). The rule allows them; what
  makes a return wind is not understood.
- **The trap's mechanism (B78).** A settled unit wanders only inside its atom and its junctions under floor-keeping flips; the local reason
  it cannot pass is not written.
- **Random learners go the long way (B69).** Unexplained beyond a guess.
- **Native reading needs matching counts.** The address reads from each atom's own signs exactly when as many atoms act as there are units.

## 6. Assumptions in force

A20, A21 (confirmed on the sphere, with its boundary off it), A46 (what counts as dissonance), A47 (what counts as a native signal), A48
(a grown handle is a Fano atom with the uniform law), A49 (the weight W), A50 (the state moves without raising W while learning acts); A26
(the state holds still) overturned as a limit by item 7, its fixed-state results standing as such.

## 7. In the owner's words

On a sphere the point's tension can be moved but never removed. A handle lets learning remove it, by going once around. Grown where the
tension sits, a named pattern takes the contradiction over, and learning inside the pattern dissolves it. With several patterns the
leftover tension lives in whichever patterns still stand for their lines: learning writes which ones, the law keeps them in every state,
each pattern carries its own bit in its own signs, a fresh disturbance settles back, and the address can be rewritten. The point moves the
tension around; learning decides where it rests. That much is a theorem on these spheres; the rest is computed on small ones.

## 8. The next research step

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — a note on the learning line (B95) | **Status:** Successful | the line written up; every count checked against its record |
| Local direction — the learned memory in Fano atoms | Practically complete for this phase | written, held, rewritten, read; the rule proved |
| Broader exploration — learning program | Known alternatives | other atoms, capacity, the open observations |
| Long-term goal — G15 Learning: a point in a learned knot space | Capability gained | a learned memory with a proved rule |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Other atoms, a challenge of A48 (B97) | 2/3 — Substantial | 2/3 — Testable | grow a thin-torus atom and other genus-1 gadgets at a sphere's line → they act and turn transparent as the Fano atom does, or the memory needs the Fano plane | Selected · awaiting go-ahead |
| 2 | Capacity of the learned memory (B98) | 1/3 — Incremental | 3/3 — Ready | write every acting subset of three and four atoms, smaller ones included → all 2^g − 1 written and held, or some not | Alternative · deferred |
| 3 | Learner local minima (B90) | 1/3 — Incremental | 3/3 — Ready | list the 10 stuck ends' dissonance, try the targeted search from each → described and escapable, or not | Alternative · deferred |
| 4 | The rule beyond octahedral spheres (B96) | 1/3 — Incremental | 2/3 — Testable | the local check on other spheres → same rule, or a breaking type | Alternative · deferred |
| 5 | Overgrown surfaces (B70) | 1/3 — Incremental | 3/3 — Ready | a far-sighted learner from genus 2 and 3 → reaches the floor, or not | Alternative · deferred |
| 6 | Why random learning goes the long way (B69) | 1/3 — Incremental | 3/3 — Ready | trace both holes → a reason | Alternative · deferred |
| 7 | The cost of writing (B99) | 1/3 — Incremental | 2/3 — Testable | shortest writing paths by bidirectional search → a cost per unit moved | Alternative · deferred |
| 8 | Why the trap holds (B78) | 0/3 — None | 3/3 — Ready | answered by `LAW-HOLDS-20261110-001`: the law pins the unit to an acting atom in every state | Alternative · deferred (closed as answered) |

- **#1** asks whether the memory is a property of the Fano plane or of any atom that stands for a line: every result so far rests on A48.
  It is the one direction here that could change what the line means.
- **#2** turns the rule into a count: g separated atoms would hold one of 2^g − 1 addresses, if every acting subset can be written.
- **#8** is answered and closed.

**Corrections:** none. **Goals:** G15 checkpoint (capability gained); B95 taken; B97 (selected), B98 and B99 added; B78 closed as answered.
**Assumptions:** none new; A48 named as the challenge of B97.

## Final report as sent

Sent to the owner in the project thread on 2026-11-10 (04:02 UTC), summarizing sections 1 to 8 above: the note's location and checks, the
atom rule's scope, the seven failed predictions, the open observations, B78 closed as answered, and the next-steps table of section 8 with
B97 (other atoms, a challenge of A48) selected and awaiting a go-ahead.
