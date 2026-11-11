# The learning line, 2026-11-09 to 2026-11-10

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a knot space is a drawn knot pattern; a Fano atom is a Fano piece. Results are unchanged;
the earlier text is in git history.

Epic `LEARN-NOTE-20261110-001` (backlog B95, goal G15). A plain account of fifteen epics, written for the owner to judge as a whole. Each
claim carries its evidence class:

- **proved**: by hand;
- **computer-assisted**: a proof whose finite part is an exhaustive computation;
- **exact on small cases**: exhaustive (SAT over every state, or every state enumerated) on the stated spaces only;
- **computed**: searches, samples or runs on the stated spaces, not exhaustive.

Every space here is an octahedral knot sphere K_k or a torus built from one, small (K_2 to K_8, 16 to 256 points).

## Picking the line up cold (updated 2026-11-11, after `SHARED-COUNT-20261111-001`)

The owner paused this line on 2026-11-10 while one harder direction is tried elsewhere, resumed it on 2026-11-11, and paused new work
again after `PARITY-FIVE-20261111-001` the same day; the owner restarted it the same evening with a new direction, bases where knots
overlap freely (lesson 1.1 of the Intuitions guide, "Words for space"), and `SHARED-COUNT-20261111-001` was its first epic. Since then the
record's words follow the glossary: distinctions, not points; knots, not lines; drawn knot patterns, not knot spaces. This section is
what a new thread needs; the section after it is the full current statement, and sections 1 to 8 the history.

**What a learned knot memory is, in one paragraph.** A drawn knot pattern's law signs its lines; a point's state is a bit per point; dissonance
W counts violated lines and even faces (at a Kasteleyn law, W = |χ| + 4·violated lines + 2·even faces, so the floor states are the
satisfying ones). An atom (a class-forced torus less a point, spliced at a line) acts as that line in one class and lets everything
through in the others; composites of atoms act exactly when all their atoms act (AND). Which atoms act is the stored address. Reading
roles from stored classes is monotone (theorem M); reading held inputs is self-dual (theorem D).

**What is established.**
- *Proved by hand:* the atom rule and units (OTHER-ATOMS, NEST-ATOMS, MANY-POINTS), AND-only composites (COMPOSITE-FN), monotone
  class-level readings (NOT-INSIDE, theorem M), self-duality of maps of held inputs and the frame lemma (IN-OUT, theorem D, lemma G), a
  composite's interface seeing its atoms only through their AND (IN-OUT, lemma C), and an acting atom's dissonance never walking away
  (NATIVE-WRITE, P1).
- *Exact:* an atom acts exactly when its own constraints cannot clear its region (seven spaces); an acting atom held on two sides is a
  gate (18 interfaces); no map of three held points is parity, majority or non-unate at the memories' interfaces (THREE-IN, six spaces,
  every law), but an 8-point drawn knot pattern of genus 4 computes parity of held points (UNATE, independently refereed), and so does the
  8-point lattice torus (2, 0, 4) in its most constrained class (PARITY-NEEDS): one handle is enough; the limit is the memories' shape.
  No lattice torus up to 24 points counts five held points, and only tori of 8 to 18 points count three; two counting tori grown at the
  two lines of K_2 compute no parity map at all, because the second unties the host's wire (PARITY-FIVE).
- *Computed, frozen:* native writing of addresses, 100 of 100 (NATIVE-WRITE); learning gates of held inputs from examples, natively and
  without false stops, at every leaf and composite tested, 84 of 84 with the credit learner and the sturdier probe (STURDY-PROBE), and
  at composites three levels deep and three atoms wide, 40 of 40 (DEEP-MEM); the impossible AND, parity and majority never accepted
  where they were impossible; and the parity of three held points, learned and held in 20 of 20 runs on the torus (2, 0, 4) alone and
  grown inside a memory (LEARN-PARITY), the first learned non-unate map; and the count of five held distinctions on two counting copies
  sharing one distinction, 10 of 10 runs, the first learned map on a base that is not one drawn knot pattern; the count of seven on three
  copies not learned within two hours (SHARED-COUNT).

**The tools** (all frozen, each with a `check.py` that reproduces its result):
- `proofs/NATIVE-WRITE-20261110-001A/.../write_lib.py`: spaces S1 to S5 and the dev spaces (`Space`), the fast incremental dissonance
  `Engine` (about 100,000 moves a second), M1, the native writer and its probe.
- `proofs/IN-OUT-20261110-001A/.../io_lib.py`: interfaces, exact map reading by SAT, the clamped probe, attention that widens.
- `proofs/CREDIT-PIN-20261110-001A/.../fix_lib.py` (the stall fix) and `proofs/CREDIT-PIN-20261110-001B/.../credit_lib.py` (credit
  from pinned dissonance); `proofs/STURDY-PROBE-20261110-001A/.../probe_lib.py` (the sturdier probe; patch `io_lib.probe` to use it);
  `proofs/THREE-IN-20261110-001A/.../census_lib.py` and `proofs/THREE-IN-20261110-001B/.../io3_lib.py` (three held inputs).

**Where to start again** (the basket, best first): a learner whose dissonance needs no drawing (sub-goal B153, 3/3 and 2/3, selected and
started; it challenges A66); the count of seven, where the time goes (B154); learning which distinction to share (sub-goal B155); an
endless chain of counting copies (B156); five-input parity on drawn knot patterns that are not lattice ones (B150); the lattice ones of 25
to 32 distinctions (B151); a probe that is a theorem (B130); copies sharing distinctions are built in
`proofs/SHARED-COUNT-20261111-001A/.../join_lib.py`; how learning cost grows with atoms (B143); the parity spaces and
harness are in `proofs/LEARN-PARITY-20261111-001A/.../parity_lib.py`, and the exact parity-check method, the composed space and the
five-input harness in `proofs/PARITY-FIVE-20261111-001A/.../five_lib.py`;
writing with only the ones named (B131); a frame fixed by learning (B126). The deeper spaces are in
`proofs/DEEP-MEM-20261111-001A/.../deep_lib.py`; random drawn knot patterns and the parity gadget in `proofs/UNATE-20261111-001A/.../unate_lib.py`.

**Lessons from the line's corrections** (`docs/CORRECTIONS.md`): read a role through a second signing before calling it stored memory;
re-run with a defect fixed before reading failures as a property of the system; rule a shared fallible check out before reading a
difference between two learners; every learning count is scored by SAT, so a fooled probe shows as an inexact stop, never as a success.

## The line as it stands (updated 2026-11-10, after `THREE-IN-20261110-001`)

Sections 1 to 8 are the note as written for B95. Fourteen epics since then change its statement; this section is the current one.

**Proved by hand.**
- **Any class-forced atom remembers** (`OTHER-ATOMS-20261110-001`). A torus atom (a torus drawn knot pattern less a point) acts as the line it
  replaced exactly in the classes where its torus has no satisfying state, and lets everything through where it has one, provided the
  torus is free at the removed point; where it acts it holds a unit. So the atom rule of section 3 holds for such atoms on any orientable
  drawn knot pattern with a Kasteleyn law, atoms adjacent or not. The Fano piece is not required (A48 overturned as a limit, replaced by A52).
- **Atoms nest** (`NEST-ATOMS-20261110-001`). A knot sphere carrying such atoms, less a point, is again such an atom: it acts as its line
  exactly where every atom inside acts, at any depth, and a composite of genus g holds g − 1 units, g where it acts.
- **Units sit where the rule says** (`MANY-POINTS-20261110-001`). With two composites and three floor units, no region holds three, the
  composites never act together, and an acting composite holds exactly two units, one per leaf.
- **The layers only conjoin** (`COMPOSITE-FN-20261110-001`). A composite computes the OR, over its host's minimal unsatisfiable sets of
  lines, of the AND of their atoms' bits. Every line of every Kasteleyn knot sphere can be violated alone (a Hall count), and growth keeps
  this, so over every host built from knot spheres and class-forced lattice tori a composite computes exactly the AND.
- **Parallel points** (`COMPOSITE-FN-20261110-001C`). Two disturbances combine in every order, ending at the floor, when the lines and faces
  touched by each flip and its repair are disjoint.
- **A uniform growth rule remembers only with Fano** (`NATIVE-ATOM-20261110-001`). Splicing a lattice torus less a point at a violated
  line, with one sign pattern on every line, grows an atom that holds the dissonance only for the Fano torus with a constant pattern;
  every other class-forced atom grows transparent (from `UNIFORM-FANO-20261107-001`).
- **Two kinds of layer** (`NAME-LAYERS-20261110-001`). Through a three-edge cut a lower level's contradiction becomes the upper level's
  constraint; through a parity name it cannot, and each level keeps its own.
- **No negation from outside** (`GATES-20261110-001`). An unsatisfiable component makes the whole network unsatisfiable, and a cut leaf
  read only from outside is never negated.
- **Every reading of the stored classes is monotone** (`NOT-INSIDE-20261110-001`, theorem M). If a network's reading depends only on
  the stored classes, and not on which signing of a class learning happened to leave, it is non-decreasing in each acting bit and
  cannot tell two non-acting classes apart: where a network allows one signing, it allows another of a class the leaf lets through at
  least as much, once the leaf's inner points are flipped where the completions differ. So the layered memory reads its stored bits
  through AND, OR and their monotone combinations, never through NOT.
- **A stored 1 cannot be walked away** (`NATIVE-WRITE-20261110-001`, P1, from lemma 3). An acting atom's region holds dissonance in every
  state, so a learner that lets its state wander on the floor and sees the dissonance in an atom vanish knows the atom does not act.
- **Maps of held inputs are self-dual** (`IN-OUT-20261110-001`, theorem D). Flipping every point leaves the dissonance unchanged, so a
  map from points held by the world to a point read at the floor answers oppositely for opposite inputs: no AND, OR or XOR of two
  held inputs. A gauge flip negates one input or the output (lemma G), and a composite's interface reads its inner atoms only
  through their AND (lemma C).
  *Not a contradiction with the AND above:* that AND (`COMPOSITE-FN-20261110-001`, B109) is over stored classes, whether each atom
  acts, which the law fixes; theorem D is about values of points the world holds, which are state. A held atom is a gate that is on
  only when the AND of its stored bits is 1, and what it does with the held values is self-dual.

**Computed.**
- Freeness of all 157 lattice-torus types to 30 points (thin tori of even index to 40); the class-forced ones are the Fano torus and the thin
  tori of even index (`OTHER-ATOMS-20261110-001D`). The smallest atom that remembers has four points.
- Exact checks of the rules above on 960, 576 and 512 classes; the AND at 274 removed points of seven composites.
- Writing and returning addresses: with thin leaves, 18 of 18, 6 of 6 and 48 of 48 held. With Fano leaves the two-level result landed
  between its marks twice (5 of 6, 43 of 48), every miss an inexact search; every exact write held.
- Disturbances in different composites combined in every order, 320 of 320; nearby ones mostly cancel.
- Gates: 43,091 networks of cuts and names read AND, OR, single bits and constants, never NOT (`GATES-20261110-001`). A NOT exists only
  in a fixed frame: with one signing fixed per class, explicit networks read NOT a₁ for three cut leaves, and another signing of the
  same class switches it off (`NOT-INSIDE-20261110-001`, census N).
- Native writing (`NATIVE-WRITE-20261110-001`, frozen): told only the address (a bit per atom, each atom given by its region) and seeing
  only its own dissonance, a learner that tests its memory by that walk and learns only on atoms whose answer is wrong wrote 100 of 100
  addresses exactly on five spaces of up to six atoms, and each held; read at one instant instead, 84 of 100 stopped inexactly. An
  atom acts exactly when its own constraints cannot clear its region, on every class of seven spaces (exact).
- Inputs and outputs (`IN-OUT-20261110-001`, frozen): an acting atom read with two sides held is a gate, the NOT gate among them
  (exact, every class of 18 interfaces); a learner that sees only its dissonance under the world's clamps learned 53 of 56 gate
  targets at single atoms and 1 of 16 through composites; its clamped probe was fooled 6 times on the largest space. *Corrected
  (`CREDIT-PIN-20261110-001`): with the learner's stall fixed, 55 of 56 and 10 of 16; depth costs steps, not reach.*
- Credit from pinned dissonance (`CREDIT-PIN-20261110-001`, frozen): lines whose dissonance a state-only walk cannot clear lay in acting
  atoms every time (4,473 of 4,473); kept as credit they helped composite gates (12 of 12 one size past) but not the total (40
  against 41 on S3 and S4, 9 inexact stops against 5). Every inexact stop was the clamped probe missing a reachable wrong value.
  *Corrected (`STURDY-PROBE-20261110-001`): with a sturdier probe, the credit learner learned all 84 of its writes.*
- A probe that is not fooled (`STURDY-PROBE-20261110-001`, frozen): each negative check four 25,000-step walks, three from fresh states;
  no false stop in 156 writes and 39 runs of AND, at 2.5 times the walk steps; every earlier figure, scored by SAT, stays or rises.
- Three held inputs (`THREE-IN-20261110-001`): exact on every class of six spaces, no map of three held points is parity, majority or
  non-unate, and the only total maps copy or negate one input; with the frame lemma this covers every law. The learner never accepted
  parity or majority (8 of 8) and learned the single-input map at 2 of 4 interfaces. *Corrected (`UNATE-20261111-001`): this is a
  property of the memories' interfaces; an 8-point drawn knot pattern of genus 4 computes parity of held points.*
- Deeper memories (`DEEP-MEM-20261111-001`, frozen): composites holding a leaf three levels down and composites of three atoms, 40 of 40
  composite writes learned and held, 55 of 56 leaf writes; depth cost nothing, a second atom about eighteen times the steps.
- Knots can count (`UNATE-20261111-001`, exact): an 8-point drawn knot pattern of genus 4 computes the parity of three held points; majority
  occurs in every size of random drawn knot pattern searched; the deeper memories' interfaces stay unate.
- One handle is enough (`PARITY-NEEDS-20261111-001`, exact): the 8-point lattice torus (2, 0, 4) in its most constrained class counts three
  held points; 16 of 281 lattice tori do; no planar disk gadget unless P = NP.
- The memory learns to count (`LEARN-PARITY-20261111-001`, frozen): the unchanged learner learned and held three-input parity in 20 of 20
  runs, on the torus alone and grown inside a memory; 60 of 60 writes, no false stop.
- One torus counts three, and among lattice tori no more (`PARITY-FIVE-20261111-001`, exact): no lattice torus up to 24 points counts
  five held points, and only tori of 8 to 18 points count three; K_2 with two counting tori grown at its two lines computes no parity map
  at all, because the second torus unties the host's six-point wire (found after the run). Tori of 25 to 32 points undecided.
- An overlap counts where the drawing could not (`SHARED-COUNT-20261111-001`; exact by definition, learning frozen): two copies of the
  drawn knot pattern (2, 0, 4) sharing one distinction count five held distinctions, and the unchanged learner learned and held that count
  in 10 of 10 runs, 30 of 30 writes, at about fifteen times the steps of one copy; three copies (seven) 0 of 10 within the 120-minute cap.
  The shared distinction lies in six knots and the pair has no single drawing; the learner read each copy's own drawn faces (A66).
- **Corrected (frame, not class).** The σ and parity readings of `CLASS-READ-20261110-001` and `GATES-20261110-001` were computed with
  one fixed signing per class; each of the 718 σ-reading networks has a satisfying state under another signing of σ
  (`NOT-INSIDE-20261110-001`, check F; `docs/CORRECTIONS.md`, Narrowing). What they read is the frame, the record of how a class was
  written, not the class.

**Failed as frozen, stated plainly.**
- N2 (`NEST-ATOMS-20261110-001`) failed at all 102 removed points inside a leaf: a leaf cut open by the removed point has no role. The
  closed-composite reading that holds there is a post hoc restatement, covered by the theorem.
- Ticket C of `NEST-ATOMS-20261110-001` and its re-test landed between their marks with Fano leaves (above), not a pass.
- The locality "points interact only through a shared line", read after `MANY-POINTS-20261110-001` ran, failed its frozen re-test on one
  of 1,200 fresh pairs; it is corrected to disjoint supports (`docs/CORRECTIONS.md`, Narrowing).
- The search for a host outside the proved class found none: seven branched covers had no unsatisfiable class at all.

**Open.** Whether every host is critical (B115); capacity (B98); the writing search's stopping rule (B113); whether the native
writer's walk never errs when long enough (B130); writing with only the ones named (B131); how learning cost grows with atoms
(B143); whether a drawn knot pattern that is not a lattice one counts five distinctions (B150); whether separately learned copies can
be wired so that learned gates compose (B148, open after SHARED-COUNT learned the composite whole); whether learning needs the drawing's
faces at all (B153), what it costs to count seven (B154), whether the learner can make its own overlaps (B155) and what an endless chain
of copies counts (B156); and whether
learning could keep a fixed frame, which would make a frame-level NOT a reading of what was written (B126). B106, B119, B120, B132, B133,
B134, B135, B136, B146, B147 and B149 are answered above, and B148 in part.

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
3. **Growing a handle** (`GROW-HANDLE-20261110-001`). Splicing a Fano piece (the Fano plane less a point) at a sphere's line makes a torus
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

**Statement.** On an octahedral knot sphere K_k, k ≥ 2, with its Kasteleyn law and Fano pieces spliced at lines whose neighbourhoods are
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
- Spheres other than the octahedral ones (backlog B96), and atoms other than the Fano piece with uniform signs (A48).

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
(a grown handle is a Fano piece with the uniform law), A49 (the weight W), A50 (the state moves without raising W while learning acts); A26
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
| Local direction — the learned memory in Fano pieces | Practically complete for this phase | written, held, rewritten, read; the rule proved |
| Broader exploration — learning program | Known alternatives | other atoms, capacity, the open observations |
| Long-term goal — G15 Learning: a point in a learned knot pattern | Capability gained | a learned memory with a proved rule |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Other atoms, a challenge of A48 (B97) | 2/3 — Substantial | 2/3 — Testable | grow a thin-torus atom and other genus-1 gadgets at a sphere's line → they act and turn transparent as the Fano piece does, or the memory needs the Fano plane | Selected · awaiting go-ahead |
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
