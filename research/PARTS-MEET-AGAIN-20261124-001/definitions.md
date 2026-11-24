# Parts that meet again: definitions

Epic `PARTS-MEET-AGAIN-20261124-001`, ticket `PARTS-MEET-AGAIN-20261124-001A`. Frozen on 2026-11-24 with the
pre-registration of ticket A, after the advisor's cold review (`advisor/answer.json`) and the thread's decisions on it. It extends
[the shared definitions](../RING-IN-BALANCE-20261123-001/definitions.md) of `RING-IN-BALANCE-20261123-001` ("the
definitions" below, cited by line) and changes nothing in them where every distinction has one or two holders. Words are
the glossary's and the definitions'. The canonical K1–K3 test is unchanged.

## 0. Words

- **Kept with their meaning in the definitions:** start, structure, place, loose, live, dead, usable, barred, member,
  h(u), k(u), met set, common knot, joinable, part, past its start, the same, group, owing, short, waits, retires, join,
  offshoot, demand, ration, treatment, round, come apart, returns, ended (definitions lines 9–93).
- **Shared** means held by two or more knots. The number of holders is given wherever it matters.
- **Take.** A birth takes a distinction; a shared distinction it takes gains a holder. This study's own laws use no other
  verb for the move. The other thread's records call it "re-read"; the word is theirs and appears only in citations.
- **Reads** is kept for the owner's sense: a part reads another when its course depends on whether the other is there.
  Rules and engines **use** or **look at** what they need.
- **The choice** is the rule that says which of several eligible shared distinctions a birth takes (section 2, item 5).
  The owner's "index" keeps his sense: which part of another pattern is looked at. Under the laws that take from beyond
  the parent (MET and the ancestor-taking laws) the choice decides which knots the new knot meets, and so stands in for
  his index there.
- New here, each defined where it first appears: **parent step, ancestor, the descendants of g, common ancestor,
  ancestral common knot, share nothing, wholly apart, one part again, one part for the first time, eligible, taking
  rule, parent-taking, ancestor-taking, course, trace, the paired test, the four marks of a pair, way**.
- "A knot meets only its parents and its children" holds **under the earlier laws** (the definitions, with every
  distinction held once or twice) and is never used here without that qualifier.
- "Root", the owner's candidate for the knot a set of knots descends from, is not adopted: the birth record is not a
  tree, since a join has two or more parents, and "root" is already used for the root of an equation that gives a rate.

## 1. Structures in which a distinction may have any number of holders

1. A distinction has one or more holders: **loose** with one, **shared** with two or more (definitions line 12,
   extended). A knot's places are fixed when it is made. Two facts used below:
   - **holders never decrease**: a birth adds itself as a holder of what it takes, and nothing removes a holder (run
     B(ii) of the paired test, section 5, is the one construction that does, and it is defined only where stated);
   - **a barred distinction is never unbarred**, and a knot never gains a place, so a knot that is no member never
     becomes one.
2. Two knots **meet** when they hold a common distinction, whatever its number of holders; the m holders of one
   distinction meet pairwise (the definitions' line 14, read for any number of holders; as the other thread's engines
   read it, `rlaw.py` lines 372–381).
3. Live, dead, member, h, k, met set, common knot, joinable, part, groups, owing and short are worded as in the
   definitions (lines 14–40), read with this meeting. **A knot is not in its own met set**: the met set of w is the set of
   members other than w that w meets, when there are at least two.
4. **Parents** are written by each birth (definitions lines 49–51; `LOCAL-ROUND-20261123-001/definitions.md` lines
   27–31): the birth record is not a reading of the holders. A start knot has none. One **parent step** goes from a knot to
   one of its parents. The **ancestors** of a knot are the knots reached by one or more parent steps; the **descendants of
   g** are the knots that have g as an ancestor, g not included; **X and its descendants**, for a set X, includes X.
   Start knots have no ancestors. A **common ancestor** of two knots is an ancestor of both; it says nothing of meeting.
5. An **ancestral common knot** of two members u and v is a common knot of u and v that is a recorded ancestor of each and
   not the parent of both. (The owner approved the term on 24 November 2026.) The start's own common knot of two start
   members, which is no recorded ancestor of their descendants, is not an ancestral common knot and is reported as its
   own class (section 5, item 7).
6. **Share nothing and wholly apart.** Two parts of a roster **share nothing** when no member of one holds a distinction
   that a member of the other holds. Link two parts when they share something; the **classes** of a roster are the sets
   of parts connected by such links. Two parts are **wholly apart** when they lie in different classes: the parts of the
   roster can then be split into two sets, one holding each, such that no part of one set shares anything with a part
   of the other. (A third part may not link them.)

## 2. One complete round with taking

Steps 1 to 8 of the definitions (lines 34–67), with these additions and exact readings.

1. **Order of births and names.** The joins are the kept groups: groups of three or more in lexicographic order of their
   sorted member names, then pairs in the same order. Then the offshoots, in increasing name of the member; a member's
   offshoots in increasing name of the loose distinction each takes. Each member gives its usable loose distinctions, in
   increasing name, to its births in birth order (its joins first). Under HOLD a member keeps the first of its usable
   loose distinctions after those its joins take, and its offshoots take the rest (as the ring study's engine does). New
   knots are named in birth order once every birth of the round is formed; their fresh distinctions are named after the
   demand step, in birth order, each knot's usable ones before its barred ones. A start's distinctions are named by its
   stars' labels in increasing order. The swap "order of births reversed" reverses the whole list of births before any
   distinction is given out.
2. **Eligible.** A distinction is **eligible** for a take when it has two or more holders at the start of the round. A
   distinction loose at the start of the round is never eligible. Several births may take one distinction in one round.
3. **SHORT-TAKES** (rule R, A230, as a treatment of a short member, in place of the base law's treatment). No group is
   cancelled. A short member gives its usable loose distinctions to its first births in birth order and, for each further
   birth, takes one distinction it holds that is eligible, is held at the start of the round by no other parent of that
   birth, and differs from the others it gives this round; which one, by the choice (OLDEST or NEWEST, ALL-CHOICES on small
   cases). A short member owes more than it holds, so it makes no offshoots. If some short member has no allowed
   distinction for one of its births, no birth is made in the round (a **residual stall**); the structure is then
   unchanged, so the residual stall repeats for ever and the run stops.
4. **Step 5′, the taking rule.** After the round's births are formed and before any is made, the law's taking rule (section
   3) adds distinctions to some births, read on the structure at the start of the round, birth by birth in birth order.
   Every taking rule adds at most one distinction to a birth, except CARRY, under which a join takes up to one for each of
   its parents. A take never repeats a distinction the birth already takes; the fresh count uses **distinct** inputs.
5. **The choice.** Among the eligible distinctions a birth may take, sorted by name:
   - **OLDEST**: the smallest name; **NEWEST**: the largest (A231, A236). Both use the names, and so the start's numbering.
   - **IN-TURN**: defined for offshoots: the i-th offshoot of one parent in the round (counting from zero, in birth order)
     takes the i-th, cycling. With one offshoot per parent it equals OLDEST. A join under MET(IN-TURN) takes by OLDEST;
     IN-TURN is not used with SHORT-TAKES.
   - **BY-COUNT**: the taking birth's parent's number of places (for a join, its first parent's, by name), modulo the
     number of eligible distinctions, counting from the oldest at zero. It uses the structure only.
   - **BY-RECEIVED** (a named case only): the parent's number of places less its number of parents, modulo the number of
     eligible distinctions, counting from zero. It uses the birth record.
   - **ALL-CHOICES**: every choice enumerated (small cases).
6. **Step 6, demand.** As the definitions, with the met sets read from the structure after the takes and before the fresh
   distinctions, so that a knot that took a shared distinction is already met by that distinction's other holders (the
   other thread's lookahead, `rlaw.py` lines 480–494). Swap: **demand before the takes**, read on the structure in which
   each birth holds only what it took loose (and, under SHORT-TAKES, what it was given).
7. **Step 7, fresh distinctions.** The ration's formula with p read as the number of distinct distinctions the birth takes
   (A235, `ONE-PARENT-REREAD-20261123-001A/preregistration.md` line 47). For a birth that takes nothing extra this is its
   number of parents, so nothing in the definitions changes. Swap: **fresh by parents**.
8. **Closing (parity).**
   - **IMPLIED** (primary): a birth receives no fresh distinction when the parity of what it takes lies in the span of the
     rules of the knots of the structure before the round (A230's form, `REREAD-...-001A/preregistration.md` line 47).
     Each birth of the round is tested against the structure before the round, not in sequence, so that the result does
     not depend on the order of births within the round. Several births of one round may be implied. The definitions'
     clauses "it is then the round's only birth, nothing is barred and no old member keeps anything" do not apply.
   - **LITERAL**: the definitions' exception (line 63), a swap only, never in a paired test (any barred distinction
     switches it off everywhere, definitions lines 73–74, and run B(i) always bars).
   - With every distinction held at most twice, in a connected structure, the two agree (the settled statement of
     `RING-IN-BALANCE-20261123-001A/preregistration.md` lines 100–101). A birth that IMPLIED leaves with no fresh distinction
     and that then fails the knot test is a failure.

## 3. The laws

### 3.1 The base laws and their swaps

- **RING-LAW**: (CAP-3, CANCEL-WAIT, RELEASE), "the two added rules" (definitions line 70); swap with FILLERS.
- **COPY-LAW(t)**: (FLOOR1, t, RELEASE), t = CANCEL-RETIRE, CANCEL-OFFSHOOT, CANCEL-WAIT. FLOOR1 is primary because every
  birth receives a fresh distinction under it (`COPYING-PARTS-20261123-001A/results.md` line 91). Swaps: FLOOR0 and
  ONE-FEWER (a join of three parents can receive nothing).
- **CAP-3(t)**: (CAP-3, t, RELEASE) on the copier starts, a registered swap in every ladder run: a ration that uses
  demand, so that a meeting can change a birth's fresh count through its demand.
- With no taking rule, after round 0 parts that have come apart are never joinable again (the earlier laws' settled
  statement, `RING-IN-BALANCE-20261123-001A/preregistration.md` lines 95–99, an argument).

### 3.2 Arm A: the record's laws

- **Q(choice)**, rule Q (A235), **parent-taking**: every offshoot whose parent holds an eligible distinction also takes one
  of them, by the choice. Joins do not take (rule Q's wording: a one-parent birth). A short member's offshoots, under
  CANCEL-OFFSHOOT, take.
- **SHORT-TAKES(choice)**: section 2, item 3.
- **Late start**: the base law alone through round s0, and Q or SHORT-TAKES from round s0 + 1; s0 is 2 on the ring starts
  and the three-knot start and 3 on the two-knot start, the first round after which the base law has parts that came
  apart. This arm exists because rules Q and R, from round 1, keep the would-be parts together, so that almost no pair is
  left to test.
- **The A225 move** is not a growth law. It is registered as one supplied control, placed by hand on each object (3.4).

### 3.3 Arm B: the ladder

| Law | The rule | Kind |
| --- | --- | --- |
| **RECORD-k** (k = 2, 3) | Two members are also joinable when the birth record gives them a common ancestor at most k parent steps above each. Nothing is taken. | not taking: it links nothing in the structure and drops the definitions' requirement that some knot meets both |
| **ALL-JOINABLE** | Every two members are joinable. | the trivial end |
| **Q(choice)** | as arm A | parent-taking |
| **CARRY** | Every birth, joins included, takes for each parent p the oldest eligible distinction that p shares with one of p's recorded parents (for a start parent, its oldest eligible distinction). | parent-taking; one distinction of a knot is carried to its descendants |
| **MET(choice)** | Offshoot clause: an offshoot also takes one eligible distinction that is held by a knot its parent meets and is not held by its parent. Join clause: a join also takes one eligible distinction held by a common knot of its parents (a knot that meets every parent) and held by no parent. | record-free; under RELEASE a member makes all its births in one round, so it has no children when it makes them; while every distinction the parent holds has at most two holders, the knots it meets are then its parents, and the offshoot clause is STEPS-1 (for a parent that is not a start knot) |
| **STEPS-k(choice)** (k = 1, 2) | Every offshoot also takes one eligible distinction held by a recorded ancestor exactly k parent steps above its parent and not held by its parent. Several such ancestors: the union of their eligible distinctions, then the choice. No ancestor k steps above, or nothing eligible: no take. | ancestor-taking |
| **UP-TO-k(choice)** (k = 2) | The same with every ancestor 1 to k parent steps above the parent (the union). UP-TO-1 is STEPS-1. | ancestor-taking |
| **FIRST(PARTS)** (one control) | Every offshoot also takes, by the choice, one eligible distinction not held by its parent, held by its parent's nearest recorded ancestors (fewest parent steps) whose member descendants lie in two or more parts of the roster. | ancestor-taking; its trigger looks at the other part |

Joins do not take under Q, STEPS-k, UP-TO-k and FIRST: a join's parents are already joinable, and these rules are meant
to act where a part is founded, which is by offshoots. This is a scaffold. MET and CARRY have join clauses.

**The cost of a law** is a vector, compared component by component:
- holder steps looked at: the largest number of holder steps, from the taking birth's parent, to a knot whose places or
  holders the rule looks at;
- parent steps of the birth record looked at;
- anything looked at across the whole roster;
- what supplies the choice: the names (OLDEST, NEWEST), the order of births (IN-TURN), the structure (BY-COUNT), the
  record (BY-RECEIVED), or an enumeration.

| Law | Holder steps | Record steps | Whole roster | Choice |
| --- | --- | --- | --- | --- |
| Q, SHORT-TAKES | 1 | 0 | no | the choice |
| CARRY | 1 | 1 | no | oldest |
| MET | 2 | 0 | no | the choice |
| STEPS-k, UP-TO-k | at most k + 1 | k | no | the choice |
| FIRST(PARTS) | any | any | yes: the parts | the choice |
| RECORD-k | 0 | k | no | none |
| ALL-JOINABLE | 0 | 0 | yes | none |

### 3.4 The A225 control, placed by hand

After round s, with X and Y two parts that are wholly apart, one knot is placed by hand. It takes two distinctions, each
then held by exactly two knots: one that X's lowest-named member holds with one other knot, and one that Y's
lowest-named member holds with one other knot (the oldest such, by name). It receives one fresh distinction and has no
parents. It is the supplied birth of A225 (`THIRD-HOLDER-20261123-001B/preregistration.md` line 49), placed where it
links two parts that are wholly apart. Nothing in the growth makes it.

### 3.5 The HOLD arm

The base laws with HOLD in place of RELEASE, with no taking rule, with Q and with STEPS-2. Under HOLD a member that keeps a
distinction meets its own child, so parts need not be wholly apart; the paired test is run on every pair of parts,
labelled wholly apart or not. The two-knot start's own two parts (its two knots meet directly and are not joinable) are
labelled the same way.

## 4. Coming apart, and one part again

1. **Come apart** keeps the definitions' sense (line 87): the members after round t descended from a part after round s
   lie in two or more parts.
2. **The descendants of X after round s**, X a part after round s: the knots made after round s that have a parent among X
   and its descendants.
3. Two parts X and Y after round s that are wholly apart, and that descend from one part after an earlier round, are
   **one part again** at round t > s when a member of X or its descendants and a member of Y or its descendants lie in one
   part after round t. When X and Y have no common part in their ancestry they are **one part for the first time**. The
   owner's "meet again" is quoted only in his words.

## 5. The paired test

1. **Runs.** Run A grows the start under the law. For a round s and two parts X and Y after round s:
   - **B(i), the second part barred** (primary): run A through round s; then every usable loose distinction of Y's members
     is barred; Y stays built and makes nothing more; then the same law.
   - **B(ii), the second part never made** (swap): run A through round s; then Y's members are removed with their fresh
     distinctions, and each distinction they took returns to its other holder, loose and barred. It is defined only when
     no knot outside Y holds a fresh distinction of a member of Y and every distinction a member of Y took has exactly one
     other holder; otherwise it is reported "not defined".
   - Runs are compared only through the last round both reached, with the same bounds on rounds and knots.
2. **The trace of X.** For each round t > s: the births of round t all of whose parents are in X or its descendants (a
   joint birth, with a parent outside them, is excluded; its children are included), each with its kind, its parents, what
   it takes, which of those were shared at the start of the round, its fresh count and its usable and barred fresh
   counts; the members after round t in X or its descendants with h and k; and their met sets, each met set intersected
   with X and its descendants first and then reduced to the inclusion-maximal ones. Knots made by round s and
   distinctions existing after round s keep their names; knots made after round s for X and its descendants, and their
   fresh distinctions, are renamed in order of name (an order-preserving renaming); any other new knot or distinction is
   "other". **The course of X** is its trace. The demand of X's births is recorded beside the trace and reported on its
   own line (the first round at which it differs); it is not part of the course.
3. **The four marks of a pair** (facts about run A, and comparisons; not a scale):
   - **one part again**: the first round t > s at which they are one part again (section 4);
   - **a joint birth**: the first round of run A with a birth that has a parent in X or its descendants and a parent in Y
     or its descendants;
   - **the course differs**: X's trace in run A and in run B(i) differ (the first round);
   - **the course differs with what the other is**: X's trace differs between two runs A from starts that differ only in
     the holdings of the start knot Y descends from (renaming every knot and distinction of the trace by first
     appearance, since the two starts are numbered differently).
4. **The choice is necessary** (a control, not a mark): the same start and law, with only the takes of X and its
   descendants using another choice (OLDEST, NEWEST, IN-TURN, BY-COUNT, BY-RECEIVED) while every other birth keeps the
   law's own; reported: whether the course differs under each.
5. **The way** of a "course differs" mark, by the first differing step of the first differing round, in the order of the
   round's own steps: **a group or owing** (the groups containing a member of X or its descendants, or their owing); **a
   round-wide trigger** (a stall, a residual stall or a closing differs between the runs); **a take**; **fresh** (the
   fresh counts, through the demand).
6. **Confirmation through a meeting.** A masked run M is run A in which, from round s + 1, no member of X or its
   descendants is joinable with a member of Y or its descendants (the pair is removed from the joinable relation in the
   round and in its demand step). The difference is **through a meeting** when X's trace in M equals its trace in B(i). If
   not, an isolating run M′ makes no member of Y or its descendants joinable with any other member; when X's trace in M′
   equals B(i), the difference is **through a third part**.
7. **The verdict** of each "course differs" mark:
   - **through a knot the growth made**: confirmed through a meeting (or a third part), and at the round they are one part
     again X's and Y's descendants are joinable using only met sets that have a common knot made after round 0;
   - **through a start knot** (the start's own meeting reopened): confirmed, and joinable only through met sets whose
     common knots are start knots;
   - **supplied**: the way is a round-wide trigger; or the law is FIRST(PARTS) and the way is a take (its rule looked for
     the other part); or the law is RECORD-k or ALL-JOINABLE (the record alone);
   - **unconfirmed**: none of these.
   With each verdict, the class of the knots linking the two at that round: an ancestral common knot (made, or a start
   knot that is a recorded ancestor); a knot made by the growth that is no ancestor of both; a start knot that is no
   recorded ancestor of both (the start's common knot of the founders).
8. **Pairs.** For each round s from 1 to 6: the parts after round s in order of their smallest member name; the first eight;
   every pair (i, j), i < j, in lexicographic order, that is wholly apart, at most four per round. Each pair is labelled as
   having come apart (a common part in its ancestry) or not. In the HOLD arm, and on the two-knot start's own parts, every
   pair is taken and labelled wholly apart or not.

## 6. The two hypotheses that split the laws

- **H1, parents only.** Every distinction a new knot takes is held, at the start of its round, by one of its parents; its
  other places are fresh.
- **H2, joinable from the structure.** Two members are joinable only when some knot meets both, and every birth's parents
  lie in one part of the roster its round reads.
- The earlier laws, Q and SHORT-TAKES (every choice, every start round), CARRY, and every ration, treatment, release rule,
  extra and closing of the definitions satisfy H1 and H2. RECORD-k and ALL-JOINABLE break H2. MET, STEPS-k, UP-TO-k and
  FIRST break H1. The A225 control breaks H1 once, by hand.

## 7. The knot test with three or more holders

- **Parity**, two methods that must agree on every knot: **ranks** (the definitions' line 133), which needs no limit on
  holders; and **kernel**, a basis of the allowed states projected onto the knot's places, rank |S| − 1. The definitions'
  cut method needs two holders per shared distinction and is not used. Both are checked against brute force before any run.
- **Not-all-equal**: a SAT solver for each of the 2^|S| assignments of each knot's places (definitions lines 137–139).
  Under not-all-equal with a ration that gives every birth a fresh distinction (ORD, CAP-k, FLOOR1, RATION-k), every round
  extends (a birth with a fresh distinction forbids no old word), and a knot's relation on its places does not change
  after its birth: a knot tested at any round after its birth is tested for every later round. Under FLOOR0 and ONE-FEWER
  a birth can receive nothing, and every knot is tested at every round.
- **The birth method** (not-all-equal, for knots of any size, where every birth receives a fresh distinction). A knot u
  born in round t passes, at round t and every later round, exactly when its inputs that existed before round t are
  jointly free in the structure before round t (every assignment of them extends to an allowed state). The argument: at
  the end of round t every other birth of the round can be satisfied by one of its own fresh distinctions, which nothing
  else holds yet, so the allowed states on u's places are those whose old part is allowed before round t and which are
  not all equal; and u's own fresh distinction completes any old part to one that is not all equal. Joint freedom of a
  set I is decided exactly by removing, again and again, every knot that has a distinction held by it alone among the
  knots left and not in I (such a knot can always be satisfied); splitting what is left into pieces linked by
  distinctions outside I; and testing, for each piece, every assignment of the distinctions of I it touches (half of them,
  by the symmetry of flipping every distinction). A start knot is tested directly. The method is checked against the
  direct test on every knot of at most 12 places of run A, and on drawn grown structures with failing knots.
- Each run's knots are tested under the run's own knot law. A knot that passes has, in the whole structure, exactly its
  own rule on its places: constrained as a whole, every part free, some state allowed (K1–K3 with forgetting).
- With three or more holders a birth with a fresh distinction need not pass: its inputs may be constrained together. The
  earlier laws' settled statement (`RING-IN-BALANCE-20261123-001A/preregistration.md` lines 100–105) needs two holders.

## 8. What is supplied by hand (scaffolds)

Everything the definitions list as supplied (line 157), and here: every taking rule (rule Q, A235; SHORT-TAKES from rule R,
A230; CARRY, MET, STEPS-k, UP-TO-k, FIRST(PARTS), RECORD-k and ALL-JOINABLE, all new); the choice of each (A231, A236 and
the new ones); the late start and its round s0; the order of births and the naming of the start; the eligibility rule;
reading demand after the takes; the fresh count by distinct inputs; the closing in two forms; the birth record wherever a
law looks at it; the A225 control; the paired test's barring and removal, the trace and its renaming, the masked runs,
the marks, ways and verdicts; the bounds on rounds and knots.
