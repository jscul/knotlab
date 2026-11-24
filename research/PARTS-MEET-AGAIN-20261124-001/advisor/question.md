You are the design advisor for a pre-registered computational study in a research program on "knot growth". Review the design COLD, before it is frozen. You have no tools; everything is below: (1) the questions, (2) the drafter's open questions and table of proposed words, (3) the study's draft definitions, (4) the draft pre-registration, (5) the shared definitions that both extend (cited by line number in the drafts). Do hand work where it helps and say what is hand work. Be adversarial: a wrong argument frozen into the record costs more than a late freeze.

Background in two sentences. Growth proceeds in complete rounds: knots hold distinctions; a member (a knot with a usable loose distinction) joins other members that share a common knot, or makes an offshoot; parts are the connected components of the "joinable" relation. Under every law studied so far, parts that have come apart never meet again; the owner asks whether a law exists under which they do, so that what one part builds depends on whether another part is there, and adds his intuition that two sets of descendants can be joined through a knot both descend from.

The program's rules for words: one word for each meaning; no words from a space of two or three dimensions for the program's own objects; a new word must not reuse a stem the record uses in another sense or have a settled outside meaning the program might cite in another sense; the owner's words keep the owner's sense. Already decided with the owner: "ancestral common knot", "ancestor-taking", "take", "shared = held by two or more".

## What I need from you (answer under these numbers; short lines; no preamble)

1. **The seal argument** ("Settled by construction", arguments 1 to 6 of the pre-registration, with H1 and H2 of the definitions, section 6). Check each step. Is argument 1 a proof as written? Is argument 2 right once a distinction can have three or more holders, and under every treatment (in particular TAKE-SHARED, CANCEL-OFFSHOOT, and a knot that waits while holding shared distinctions that later gain holders)? Do rule Q, TAKE-SHARED and INHERIT really satisfy H1 and H2 under every index? Give a counterexample by hand if you can find one (a small start and rounds), or say which hypothesis would have to be added.
2. **The definitions.** Anything undefined, ambiguous, or impossible to implement as written, especially: the order of births and what "at the start of the round" fixes; TAKE-SHARED; the taking rules AT(k) and NEAR (what if the ancestor k steps up does not exist, or holds no shared distinction the parent lacks; ties between several ancestors k steps up when the parent has two or more parents); the indices SIB and FRESH; the fresh count "by inputs"; the two closings; "sealed apart" (note that if a knot met members of two parts they would be joinable, so is its first clause empty?); "meets again"; run B(ii) (removal: is the structure still well formed; do removed knots' children exist?); the course; the channels.
3. **The paired test and the grades.** Is "the course of X differs between run A and run B(i)" a sound operationalisation of the owner's "a part reads another when its course differs between the two runs"? Does barring Y (B(i)) change anything other than Y's growth that could produce a spurious grade 2 (for instance through the index's order of names, the order of births, demand, or a closing)? Should demand be part of the course? Is the channel classification sound, and is the "supplied or made" criterion defensible and decidable? Is grade 3 by the index (only the first part's takes changed) a meaningful contrast or a tautology?
4. **The ladder.** Is AT(k) a natural rung or contrived? Is the ordering of rungs by what is supplied the right one, and does "the least rung" (P8) mean anything given that ordering? Is there a cheaper law outside H1 that needs NO birth record, for example: a join also takes a shared distinction held by the common knot through which its parents are joinable (and an offshoot one held by a knot its parent meets that is not its parent)? If so, state it precisely enough to register, predict by hand what it does on the three-knot start under (FLOOR1, CANCEL-RETIRE), and say where it belongs on the ladder. Should a ration that reads demand (ORD or CAP-3) be registered in the ladder runs so that a meeting can feed a birth instead of making its members short?
5. **The predictions.** Which are true by construction, which are replications of the drafter's prototype only, which cannot be decided by the registered runs, and which do you expect to fail? Is anything the owner asked for missing: (a) verdicts on rule R, rule Q and the A225 move on the ring that returns and on the two-knot part that copies itself; (b) each start grown with and without the second part; (c) the knot test on every knot made under parity and not-all-equal; (d) every added rule named as a scaffold and swapped; (e) a plain statement of whether a reader was supplied or made; (f) the least law with its cost (the rule, the choice of which shared distinction, any record of who came from whom); (g) his intuition kept apart from the evidence; (h) the index registered, with what supplies it.
6. **The drafter's eight open questions** (below): answer each in one to three lines.
7. **Scope and honesty.** What would a positive show and not show? The prototype's smallest positive case goes through the start's dead knot (a start knot, no recorded ancestor of either part), the meeting makes the first part's members short so that they retire, and nothing is built jointly. Is it honest to call that "a part whose course depends on another"? What is the right plain sentence for the owner? What is the literature's name for what AT(k) is (a back-reference to an ancestor; sharing in term-graph rewriting; anything in L-systems or graph grammars), with the caveat that you cite from memory?
8. **Words.** For each row of the drafter's table: keep, or one better word, in a line. In particular: "sealed apart / sealed" (I rejected "sealed" once already because the program's notebook uses "seal" of a piece of a structure closed off by a birth; candidates: "disjoint", "share nothing", "clean apart"); "root" (the owner's candidate, for the knot a set of knots descends from; can it serve as the plain word for the descent alone, given "root of an equation" in the growth studies and the literature's root of a tree?); "channel" (settled in information theory); "grade"; "course" (the owner's); "the index" (the owner's "index what part"); "parent step"; "meets again" against "meet for the first time"; the labels B-RING, B-COPY, TAKE-SHARED, INHERIT, AT(k), NEAR, RECORD-k, ANY, O, N, SIB, FRESH, EVERY (ANY and EVERY side by side; FRESH against "fresh distinctions").


# (2a) The drafter's open questions

# Open questions the drafter put to the advisor

1. Is the seal argument (argument 1) right as stated, and is "sealed" the right hypothesis? It needs every pair of parts
   sealed, not only the two compared; the prototype's pairwise count found meetings again under HOLD in rosters that were
   not sealed.
2. Under HOLD the earlier laws already let unsealed parts become joinable (seen, never with a grade 2). Should the study's
   question be restricted to sealed parts, as drafted, or should HOLD's case be a registered arm?
3. Is the course the right object for grade 2? The draft leaves the demand D out of it (FLOOR1 ignores D, so a demand
   difference changes nothing built). Including it would turn several "no difference" cases into grade 2.
4. Is the channel classification sound? A take that differs between runs A and B at the first differing round is called
   "rule"; the prototype first misclassified differences that followed an earlier meeting.
5. Is AT(k) the right second arm, or is there a cheaper law outside H1 (for example a birth taking a distinction of a
   common knot of its parent rather than of an ancestor, which needs no birth record)? The draft's ladder is ordered by
   record steps read; a holder-step ordering would put such a law first.
6. In the smallest case the meeting goes through a start knot that is not an ancestor (start knots have no recorded
   parents). Should the start roster's common knot of the founders count as an ancestral common knot, as LOCAL-ROUND's
   start clause treats start knots?
7. The meeting mostly stops the reader (shortness under FLOOR1). Should the ration be swapped for one that reads demand
   (CAP-3 or ORD) in the ladder runs, so that a meeting can feed a birth instead of cancelling it?
8. Is the elimination closing the right primary under parity, given that it and the literal exception differ once a
   distinction has three holders, and that a birth implied by elimination can itself fail the knot test?


# (2b) The drafter's proposed words

# Words proposed by the drafter (for the advisor)

| Proposed word | Meaning here | Second candidate | Why this one |
| --- | --- | --- | --- |
| ancestral common knot | a common knot of two members that is an ancestor of both and not the parent of both | (approved by the owner, 24 November 2026) | names the role (common knot) and the record (ancestor); no space word |
| root | the owner's candidate (24 November 2026) for the knot a set of knots descends from | not adopted | for: the literature's root of a rooted tree, short; against: it names the descent and not the meeting, and the growth studies already use "root" for the root of an equation that gives a rate (the golden ratio as the root of x² = x + 1) |
| ancestor-taking | a birth takes a shared distinction that an ancestor of one of its parents holds | ancestral take | the thread's word; says what is taken and from whom |
| take | the move: a birth takes a distinction, which gains a holder | (approved) | one verb; "re-read" is the other thread's and "reads" is kept for the owner's sense |
| sealed apart; sealed | two parts no knot meets members of both of, whose members do not meet; every two parts so | held apart | the condition of the argument; needs to be different from "past its start", which forbids any member meeting a member |
| meets again | two parts that came apart and were sealed apart have members in one part later | rejoin | the owner's words |
| the index | the rule that says which shared distinction a birth takes | the choice | the owner's word ("index what part"); "convention" names only the fixed indices |
| course | what a part builds round by round: its births and its members up to sameness | history | the owner's word ("its course differs"); "history" is used in the record for a whole run |
| grade | 0 to 3, the strength of the dependence found | level | short; "level" is used for knot substitution |
| channel | how a grade 2 comes about: global, meeting, rule, other | way | short and plain; "route" would be a word of space |
| parent step | one step from a knot to one of its parents in the birth record | generation | "generation" is the definitions' birth-by-birth record (line 121), with another meaning |
| the descendants of g | every knot that has g as an ancestor (g not included unless said) | (the thread's) | "line of descent" is one chain |
| RECORD-k, ANY, INHERIT, AT(k), NEAR, TAKE-SHARED, SIB, FRESH | names of rules and indices | — | labels only; the advisor may prefer plain phrases |

Words avoided: "hub" (the other study's word for a distinction with many holders; here, "a distinction with m holders"),
the owner's two phrases for the ancestral common knot (quoted once, under "The question"), "cluster" and "chunk" (quoted
only), "line of
descent" for all descendants, "depth" (the glossary's depth is another thing; here "parent steps"), "point", "path",
"layer", "window", "route".



# (3) DRAFT DEFINITIONS OF THIS STUDY

# Parts that meet again: definitions (draft for the advisor, not frozen)

Epic `PARTS-MEET-AGAIN-20261124-001`, ticket `PARTS-MEET-AGAIN-20261124-001A`. Draft of 2026-11-24, written by the helper
agent that surveyed the record and wrote a scratch prototype; to be reviewed cold by the advisor and frozen by the
thread. It extends [the shared definitions](../RING-IN-BALANCE-20261123-001/definitions.md) of `RING-IN-BALANCE-20261123-001`
("the definitions" below, cited by line) and changes nothing in them where every distinction has one or two holders.
Words are the glossary's and the definitions'. The canonical K1–K3 test is unchanged.

## 0. Words

- **Kept with their meaning in the definitions:** start, structure, place, loose, live, dead, usable, barred, member, h(u),
  k(u), met set, common knot, joinable, part, past its start, the same, group, owing, short, waits, retires, join,
  offshoot, demand, ration, treatment, round, come apart, returns, ended (definitions lines 9–93).
- **Shared** now means held by two or more knots. The number of holders is given wherever it matters.
- **Take.** A birth takes a distinction; a shared distinction it takes gains a holder. This study's own laws use no other
  verb for that move. The other thread's records call it "re-read" (`REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001`); the word
  is theirs and appears here only in citations.
- **Reads** is kept for the owner's sense only: a part reads another when its course depends on whether the other is there
  (section 5).
- New here, each defined where it first appears: **parent step, ancestor, the descendants of g, ancestral common knot,
  sealed apart, sealed, meets again, taking rule, the index, ancestor-taking, course, the paired test, grade, channel**.
  The words were checked by the advisor (`advisor/`).
- The sentence "a knot meets only its parents and its children" holds **under the earlier laws** (the definitions with
  every distinction held once or twice) and is never used here without that qualifier.

## 1. Structures in which a distinction may have any number of holders

1. A distinction has one or more holders. It is loose with one, shared with two or more (definitions line 12, extended).
   A knot's places are fixed when it is made; later births may add holders to its places, never places to it.
2. Two knots **meet** when they hold a common distinction, whatever its number of holders. So the m holders of one
   distinction meet pairwise. (This is the definitions' line 14, read for any number of holders; it is how the other
   thread's engines read it: `rlaw.py` lines 372–381.)
3. Live, dead, member, h, k, met set, common knot, joinable, part, groups, owing, short: worded exactly as in the
   definitions (lines 14–40), read with this meeting. A met set is the set of members that one knot meets, when there are
   at least two; that knot may itself be a member.
4. **Parents** are written by each birth (definitions lines 49–51; as in `LOCAL-ROUND-20261123-001/definitions.md`
   lines 27–31: the parent relation is a record of the birth, not a reading of the holders). A start knot has none.
   One **parent step** goes from a knot to one of its parents. The **ancestors** of a knot are the knots reached by one or
   more parent steps; the **descendants of g** are the knots that have g as an ancestor (g itself not included unless
   said). Start knots have no ancestors, so two start knots never have a common ancestor.
5. An **ancestral common knot** of two members u and v is a common knot of u and v (some met set contains both) that is
   an ancestor of each, and is not the parent of both. (Approved by the owner, 24 November 2026. His phrase for it was
   "axis point", and afterwards perhaps "access point"; both are his and neither is a term here.)

## 2. One complete round with taking

Steps 1 to 8 of the definitions (lines 34–67), with these additions and readings.

1. **Order of births** (it matters only when a member takes a shared distinction for some births and not for others):
   groups of three or more in sorted order, then pairs in sorted order (the joins), then offshoots by member. This is the
   other thread's order (`rlaw.py` line 416; its deviations A1).
2. **Step 3, a fifth treatment, TAKE-SHARED** (rule R as a treatment; A230, A231): no group is cancelled. A short member
   gives its usable loose distinctions to its first births in the order of item 1 and takes, for each further birth, one
   distinction it holds that is shared at the start of the round, is held at the start of the round by no other parent
   of that birth, and differs from the others it gives this round; the choice among those allowed is the law's index
   (item 5). If some short member has none allowed, no birth is made in the round (a **residual stall**), as under rule R
   (`REREAD-...-001A/preregistration.md` line 45).
3. **Step 5′, the taking rule.** After the joins and offshoots of the round are formed and before any is made, the law's
   taking rule (section 3) adds to some births one shared distinction each, read on the structure at the start of the
   round. Then every birth is made; each distinction it takes gains it as a holder.
4. **Step 6, demand.** As the definitions, with the met sets read from the structure after the takes of item 3 and before
   the fresh distinctions: so a knot that took a shared distinction is already met by that distinction's other holders
   (the other thread's lookahead, `rlaw.py` lines 480–494, and qlaw deviations A4).
5. **The index.** Where a law lets a birth take one of several shared distinctions, **the index** is the rule that says
   which. It is a scaffold of every law here, and every run states what supplies it:
   - **O**, the oldest (smallest name) and **N**, the newest (largest name): fixed conventions (A231, A236). Names grow with
     creation: in a start, the names as written in its stars; fresh names in order of birth.
   - **SIB**: the siblings that take in one round (births of one parent) take different distinctions: the first the oldest,
     the second the next, cycling. This answers A236's challenge ("the first the oldest, the second the next"); the record
     found that under rule Q eight small structures changed only when two births of one parent took different shared
     distinctions, which neither fixed convention gives (`ONE-PARENT-REREAD-20261123-001A/result.md` lines 29–33).
   - **FRESH**: read from the structure: the parent's number of places less its number of parents (what it received at
     birth, the h₀ of `LOCAL-ROUND-20261123-001/definitions.md` line 34), modulo the number of allowed distinctions, counting
     from the oldest.
   - **EVERY**: every allowed choice enumerated (small cases only).
6. **Step 7, fresh distinctions.** The ration's formula with p read as the birth's **number of inputs** (the distinctions
   it takes), as in A235 (`ONE-PARENT-...-001A/preregistration.md` line 47). For a birth that takes no shared distinction
   inputs and parents are equal, so nothing in the definitions changes. Swap: p read as the number of parents.
7. **Closing (parity).** Two forms, both scaffolds:
   - **LITERAL**: the definitions' exception (line 63): a new knot that takes every loose distinction of the structure, as
     the round's only birth, receives none.
   - **ELIMINATION**: a birth receives none when the parity of what it takes lies in the span of the rules of the knots of
     the structure before the round (A230's form, `REREAD-...-001A/preregistration.md` line 47). With every distinction
     held at most twice in a connected structure the two agree (the settled statement of
     `RING-IN-BALANCE-20261123-001A/preregistration.md` lines 100–101); with three or more holders they can differ.
   ELIMINATION is primary, because with a distinction held three times the sum of all knots' rules no longer leaves the
   loose distinctions alone (`REREAD-...-001A/preregistration.md` line 37).

## 3. The laws

### 3.1 The base laws (the two studies' objects, unchanged)

- **B-RING**: (CAP-3, CANCEL-WAIT, RELEASE), "the two added rules" (definitions line 70). Swap: with FILLERS ("the three").
- **B-COPY(t)**: (FLOOR1, t, RELEASE) for t = CANCEL-RETIRE, CANCEL-OFFSHOOT, CANCEL-WAIT. FLOOR1 is primary because every
  birth receives at least one fresh distinction under it (`COPYING-PARTS-20261123-001A/results.md` line 91). Swaps:
  FLOOR0 and ONE-FEWER, under which a join of three parents can receive nothing.
- Under both, with no taking rule, past round 1 a part that has come apart is never joinable again (the earlier laws'
  settled statement, `RING-IN-BALANCE-20261123-001A/preregistration.md` lines 95–99).

### 3.2 Arm A: the record's laws in which a birth takes a shared distinction

- **Q(index)**, rule Q (A235): every offshoot whose parent holds, at the start of the round, a shared distinction also
  takes one of them, by the index (O or N primary; SIB and FRESH as swaps; EVERY on small cases). Siblings take the same
  one under O and N. Applies to every offshoot, a short member's under CANCEL-OFFSHOOT included.
- **TAKE-SHARED(index)**, rule R as the treatment of a short member (section 2, item 2), in place of the base law's
  treatment. Under the ordinary count rule R acts at round 1 only (`REREAD-...-001A/result.md` lines 36–39); under the
  rations of the base laws knots are short every other round, which is why it is run here as a treatment.
- **The A225 move** (a supplied birth takes a distinction already held twice) is not a law and is not run. Its verdict is
  read from the split in section 6: every growth law that states it by taking only distinctions the birth's parents hold
  (rules Q and R and all their indices) is on one side, and ancestor-taking (section 3.3) on the other.

### 3.3 Arm B: the ladder of ancestor-taking

**Ancestor-taking**: a birth also takes a shared distinction that an ancestor of one of its parents holds; the
distinction gains a holder. The rungs are ordered by what is supplied by hand (pre-registration, "What is supplied").
Every rung takes at most one extra distinction per birth and leaves groups, owing, treatment, demand and the ration as in
section 2.

| Rung | Name | The rule | Is it ancestor-taking? |
| --- | --- | --- | --- |
| 0 | **RECORD-k** (k = 2, 3) | Two members are also joinable when the birth record gives them a common ancestor at most k parent steps above each. Nothing is taken. | No: it links nothing in the structure and drops the definitions' requirement that some knot meets both. |
| 0′ | **ANY** (control) | Every two members are joinable. | No: the trivial end. |
| 1 | **Q(index)** | as arm A | Yes, at the parent itself: the distinction is the parent's own place. |
| 1′ | **INHERIT** | Every birth (joins too) takes, for each parent p, the oldest distinction p shares with one of p's own parents (a start parent: its oldest shared distinction). | Yes, at the parent; it carries one distinction to all the descendants of the knot that first held it. |
| 2 | **AT(k, index)** (k = 1, 2) | Every offshoot also takes a shared distinction that the ancestor exactly k parent steps above its parent holds and its parent does not, by the index. | Yes, k parent steps above the parent. |
| 3 | **NEAR(trigger, index)** | Every offshoot also takes, from its parent's nearest ancestor a that meets the trigger, a shared distinction that a holds together with one of its children and that the parent does not hold, by the index (O primary); if there is none, a shared distinction of a that the parent does not hold. Trigger LINES: the member descendants of a descend from two or more of a's children. Trigger PARTS: the member descendants of a lie in two or more parts of the roster. Variant LONE: only the offshoots of a member that is in no group take (the thread's sketch (iii)). | Yes, at any number of parent steps. |

What each rung reads, beyond the parent's own places: rung 0, the record to k parent steps; rung 1′, one parent step;
rung 2, k + 1 parent steps of the record (or, read from holders alone, at least 2(k + 1) holder steps with the direction of
each parent step supplied); rung 3, the record to any number of parent steps and, under PARTS, the parts of the whole
roster. Under NEAR(PARTS) the taking rule itself reads whether another part exists (pre-registration, channel "rule").

## 4. Parts that have come apart, and meeting again

1. **Sealed apart.** After a round, two parts X and Y are sealed apart when no knot meets a member of X and a member of Y
   (they are different parts) and no member of X meets a member of Y. The roster is **sealed** when every two of its parts
   are sealed apart. (Under the earlier laws a roster past its start is sealed; under taking rules members of one part
   may meet one another, and the roster need not be past its start.)
2. **The descendants of X after round s** (X a part after round s): X's members, and every knot made after round s that has
   a parent among them or among their descendants.
3. **Meets again.** Two parts X and Y after round s, that are sealed apart and both have members descended from one part
   after an earlier round, **meet again** at round t > s when a member descended from X and a member descended from Y lie
   in one part after round t. When X and Y have no common part in their ancestry (for example two parts of a start), they
   **meet for the first time**. Both are reported; only meeting again answers the question.
4. **Come apart** keeps the definitions' sense (line 87): the members after round t that descend from a part after round
   s lie in two or more parts.

## 5. The paired test, the course, the grades

1. **Run A** grows the start under the law. For a round s and two parts X and Y after round s that are sealed apart:
   - **Run B(i), the second part barred** (primary): run A to round s; then every usable loose distinction of Y's members is
     barred; Y stays built and makes nothing more; then the same law to the same last round.
   - **Run B(ii), the second part never made** (swap): run A to round s; then the members of Y and their fresh distinctions
     are removed, and each distinction they took becomes loose again and barred; then the same law.
2. **The course of X** after round s is, for each later round t: the multiset of the births of round t all of whose parents
   are descendants of X (X's members included), each recorded by kind, number of parents, number of inputs, number of
   inputs that were shared at the start of the round, fresh count, usable and barred fresh counts; and the members after
   round t that descend from X, with their h and k and the maximal met sets among them, up to sameness (definitions line
   29). The demand D of each birth is recorded beside it but is not part of the course, since it is a reading inside the
   round and some rations ignore it.
3. **Grades**, each the least round at which it holds:
   - **0**: a member descended from X and one descended from Y lie in one part (run A).
   - **1**: a birth of run A has a parent descended from X and a parent descended from Y.
   - **2**: the course of X differs between run A and run B(i). This is "the first part's own course depends on the second
     being there", the owner's stop.
   - **3**: the course of X differs between two runs in which Y differs. Two contrasts: (a) **what Y is**: a start that
     differs only in the holdings of the knot that Y descends from; (b) **the index**: the same start and law, the births
     descended from X taking by a different index (O, N, SIB, FRESH) while all others keep the law's own; whether the
     grade-2 difference is present depends on the index. Reported if seen; the stop does not depend on it.
4. **Channel** of a grade 2 at its first differing round t:
   - **global**: a round-wide rule acts differently in the two runs at round t: STALL (definitions line 42), the residual
     stall of TAKE-SHARED, or the parity closing in either form;
   - **meeting**: a member descended from X and one descended from Y lie in one part after round t − 1, or after round t
     (the demand of round t already reads the meetings its takes make);
   - **rule**: neither, and X's births of round t differ in what they take (the taking rule read Y directly, as NEAR(PARTS)
     does);
   - **other**: none of these.
   A grade 2 through the channel "meeting" is a part whose course depends on another **through the growth's own
   meetings**; through "global" or "rule" it depends on a reader supplied with the law (pre-registration, "Supplied or
   made").

## 6. Two hypotheses that split the laws (stated here; the argument is in the pre-registration)

- **H1, parents only.** Every distinction a new knot takes is held, at the start of its round, by one of its parents; its
  other places are fresh.
- **H2, joinable from the structure.** Two members are joinable only when some knot meets both, and every birth's parents
  lie in one part of the roster its round reads.
- The earlier laws, Q(every index), TAKE-SHARED(every index), INHERIT, and every ration, treatment, release rule and extra
  of the definitions satisfy H1 and H2. RECORD-k and ANY break H2. AT(k ≥ 1) and NEAR break H1.

## 7. The knot test with three or more holders

- **Parity**, two methods that must agree on every knot: (1) **ranks**, the definitions' (line 133): rank H less rank H
  without the columns of the knot's places is one; it needs no limit on holders; (2) **kernel**: a basis of the allowed
  states is computed once, and the knot passes when its projection onto the knot's places has rank |S| − 1. The
  definitions' cut method needs two holders per shared distinction and is not used. Both methods are checked against
  brute-force enumeration on drawn small structures before any run.
- **Not-all-equal**: unchanged (definitions lines 137–139), a SAT solver for each of the 2^|S| assignments of each knot,
  checked against brute force on drawn small structures.
- **Extension**: unchanged (definitions line 140).
- A knot that passes has, in the whole structure, exactly its own rule on its places: constrained as a whole, every part
  free, some state allowed: K1–K3 with forgetting.
- With three or more holders, a birth with a fresh distinction need not pass: its inputs may be constrained together even
  when they are not every loose distinction (the earlier laws' settled statement, `RING-IN-BALANCE-20261123-001A/preregistration.md`
  lines 100–105, needs two holders). Every run tests every knot.

## 8. What is supplied by hand (scaffolds)

Everything the definitions list as supplied (line 157: the complete round, A104; every ration other than ORD and every
treatment other than STALL, the release rule and the extras, A224; the starts; the reading of a part as a thing, A125),
and here: the taking rules (rule Q, A235; TAKE-SHARED from rule R, A230; INHERIT, AT(k), NEAR, RECORD-k and ANY, all new);
the index of each (O, N, SIB, FRESH, EVERY; A231, A236); the order of births; the fresh count read by inputs; the closing
in two forms; the birth record wherever a rung reads it; the paired test's barring and removal, the course, the grades
and the channels; the bounds on rounds and knots.


# (4) DRAFT PRE-REGISTRATION

# Can parts that have come apart meet again, so that one part's course depends on another? Pre-registration (draft)

Ticket `PARTS-MEET-AGAIN-20261124-001A` of epic `PARTS-MEET-AGAIN-20261124-001` (lead B317; goals G15 with G17 and G18;
assumptions A223 and A241). Draft of 2026-11-24, not frozen: for the advisor's cold review and the thread's freeze. The
code will be written by a helper agent that has not seen the drafter's prototype, from this text and
[the definitions](../PARTS-MEET-AGAIN-20261124-001/definitions.md), which extend [the shared definitions](../RING-IN-BALANCE-20261123-001/definitions.md)
of `RING-IN-BALANCE-20261123-001`. The canonical K1–K3 test is unchanged. No claim is made about living things or minds.

## The question

The owner asked on 24 November 2026: "is there a growth law under which parts that have come apart can meet again, so
that what one part builds depends on whether another part is there? Under every law we have studied so far, parts that
come apart act alone for ever, which is why the copies are a population and not a machine." His first step: take the
three laws of the other thread in which a birth may take a distinction that is already shared (rule R, A230; rule Q, A235;
the move recorded in A225), run them on the ring that returns and on the two-knot part that copies itself, and grow each
start twice, once with the second part present and once without it. "A part reads another when its course differs
between the two runs." Stop at one part whose course depends on another, or at a reason this cannot happen under these
laws; and if a part reads another, say whether the reader was supplied by us or made by the growth.

The owner added, the same day, as his intuition and not as evidence (assumption A241): "There's no way it wouldn't work.
It might just cost complexity. Programming is a thing in our reality, there should be a way to reference information like
joining 2 different clusters of child logic from the parent via something like an 'axis point'. So we can essentially
reference chunks of logic." He said afterwards that "access point" may be what he meant. Read in the program's terms: two sets of descendants become joinable through a knot that both
descend from, an **ancestral common knot**. So the study has a second arm, a ladder of laws of **ancestor-taking**, and a
negative for the three recorded laws is a result about those three only; the study then goes on, inside this
pre-registration, to the least rung of the ladder that does let a part's course depend on another, with its cost.

He then carried it further, in his words: "This is why we may need 'function-like' logical operations where we can
reference/sample logic. These are basically meeting patterns that are complex in nature. Maybe even so complex as to the
indexing operation being logic based iterators rather than incremental. So like maybe intelligence as a fold has access to
something like 'the golden ratio', but it needs to index what part of the golden ratio it's looking at?" Read here: a
reference needs an index, which says which part of the other pattern is taken. In every law of this study the index is
the choice of which shared distinction a birth takes. The study registers that choice as **the index** of each law, says
what supplies it, includes two indices read from the structure or from siblings, and asks whether the index decides
whether a part reads another.

**Existence is cheap.** A law under which any two members are joinable, whatever is built, "works" at once. What this
study measures is the cost of the least law under which a part's own births depend on another part through meetings the
growth makes, and whether what it builds are knots.

## In standard terms

In the literature's words, not the program's:

A synchronous hypergraph-rewriting system: knots are hyperedges over distinctions; each step adds hyperedges built from
degree-one vertices of earlier ones, and under the laws studied here a new hyperedge may also attach to a vertex of degree
two or more, raising its degree. The live part splits into components of a "common neighbour" relation. The question is
whether two components that have separated can reconnect, and whether the evolution of one can depend on the presence of
another. Under the earlier laws the components form a context-free substitution system (the literature's 0L system,
Lindenmayer 1968); a dependence between components would be the step to a system with interaction (the literature's 1L
or 2L systems). The main fact found before the freeze is an invariant: if every vertex a new hyperedge attaches to is
already a vertex of one of the hyperedges it is made from, sealed components never reconnect. A rule that reconnects must
attach to a vertex farther back in the birth record: a back-reference to an ancestor, in the spirit of sharing in the
literature's term-graph rewriting (Barendregt, van Eekelen, Glauert, Kennaway, Plasmeijer and Sleep, 1987; cited from
memory, not checked).

## Prior work in the program

Searches, each with `--until 2026-11-24 --exclude PARTS-MEET-AGAIN-20261124-001`:

`python3 -B scripts/track.py objects "parts of the live roster that have come apart become joinable again, meet again" --until 2026-11-24 --exclude PARTS-MEET-AGAIN-20261124-001`

`python3 -B scripts/track.py objects "birth that takes a distinction already shared under a ration and waiting, ring that returns, part that copies itself" --until 2026-11-24 --exclude PARTS-MEET-AGAIN-20261124-001`

`python3 -B scripts/track.py objects "birth takes a distinction an ancestor holds, common knot that is a common ancestor, one part's births differ with and without another part" --until 2026-11-24 --exclude PARTS-MEET-AGAIN-20261124-001`

What they return (run read-only by the drafter on 2026-11-24), one line each:

- First search.
  - `RING-IN-BALANCE-20261123-001/1` (the ring that returns) — the same object: base law B-RING and the ring starts; its
    settled statement that parts act alone "past the start (under RELEASE)" is what this study tests beyond.
  - `RING-IN-BALANCE-20261123-001/2` and `COPYING-PARTS-20261123-001/1` — the same object: the two-knot part that copies
    itself; their counts are this study's gate.
  - `RING-IN-BALANCE-20261123-001/3`, `/4`, `/6`, `/7`, `COPYING-PARTS-20261123-001/3` — relatives: the census of starts,
    what returns, rounds part by part and birth by birth, the census of copying. Not used.
  - `GENERATORS-20261120-001/5` — a relative: under ordinary growth no witnessed part split or merged in 628 steps.
  - `READ-ORIGIN-20261120-001/4` — a relative for the rungs that read the birth record: whether original knots can be
    recognised from holdings.
  - `WALL-READ-20261119-001/1` — unrelated (partnered starts).
  - Other epics: `LOCAL-ROUND-20261123-001` (a relative: the parent relation written by each birth, used here as the
    birth record), `KNOT-FOUNDATION-20261019-001`, `SEPARATE-20261108-001`, `THREEFOLD-SPINSUM-20261030-001`,
    `SEYMOUR-COUNT-20261030-001` (unrelated).
- Second search.
  - `RING-IN-BALANCE-20261123-001/1`, `/2`, `/4`, `/7`, `COPYING-PARTS-20261123-001/1`, `/3` — as above.
  - `THIRD-HOLDER-20261123-001/2` — the source of the A225 move (class S).
  - `ONE-PARENT-REREAD-20261123-001/1` — the same law (rule Q) on other objects (sparse draws, hidden-excess pieces).
  - `COPIES-AND-MEETINGS-20261120-001/6` — the nearest prior positive: one shared distinction added by hand to a prepared
    start turns two separate witnessed parts into a later common birth, under ordinary growth. Supplied by hand.
  - `REVIEW-LEADS-20261123-001/5` — a relative: two copies of a ring clock compete for one donor, one birth at a time; a
    dependence between copies through a shared donor built into the start.
- Third search.
  - `LAST-DISTINCTION-AND-PRIVATE-PULSES-20261121-001/1`, `SPARE-AND-NEXT-PAYMENT-20261122-001/1`,
    `EARLIER-EVENT-AND-LATER-BIRTH-20261122-001/1`, `INFLUENCE-CONE-20261120-001/4` — relatives: dependences through one
    loose distinction or one witness edit in prepared ordinary starts, compared between two starts.
  - `LOCAL-ROUND-20261123-001/3` — a relative: laws that read the present roster one birth at a time (negative).
  - `ONE-PARENT-REREAD-20261123-001/1`, `REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001/2` — the same laws, other objects.
  - `GENERATORS-20261120-001/1`, `SERIAL-REPAIRS-20261120-001/3` — relatives: recurring products and reading the round
    from the whole present under ordinary growth.
  - `COPIES-AND-MEETINGS-20261120-001/6` — as above.
  - Other epics: `BIRTH-RULE-20261109-001`, `KNOT-CIRCUITS-20261020-001`, `ATOM-ONE-20261107-001`, `SPACING-20261109-001`,
    `SHARED-COUNT-20261111-001` — unrelated objects (other growth models and other questions).

The survey of the other thread's three laws, with citations, is [survey.md](../PARTS-MEET-AGAIN-20261124-001/survey.md).

## Prior work outside the program

Lindenmayer's systems (1968): context-free (0L) rewriting is a population whose members never interact; interaction
systems (1L, 2L) let a cell's successor depend on its neighbours. Conway's Life: two patterns interact only when they come
near on the board, and the program has no board. Term-graph rewriting with sharing lets two subterms refer to one node
(cited from memory). What this would add: whether, on a structure that makes its own places and whose every piece passes
the canonical knot test, a reference to an ancestor can be made by a stated growth law, and what it costs. Not searched
further.

## Known before the freeze (disclosed)

The drafter wrote a scratch prototype (`mh.py` and the analysis scripts in its scratch folder; unreviewed; not the study's
engine; its author does not write the study's code) and ran it on every start and law below. Everything it showed is
listed here. "Seen" below means seen in the prototype.

**Checks of the prototype.**
- With no taking rule, its complete rounds equal the ring study's engine (ticket A, imported read-only) knot for knot
  (places, parents, rounds, barred flags, stalls, closings): 300 runs (six starts, both knot laws, 25 laws including HOLD,
  NO-OFFSHOOT, FILLERS), 2,286 rounds, no difference.
- Where they overlap it equals the other thread's engines (imported read-only; their hashes unchanged): rule R
  (`rlaw.Growth`, ordinary count) and rule Q (`qlaw.QGrowth`, ordinary count with STALL), on seven named starts (56 runs)
  and on the first 400 of the review-leads sparse draws per law and convention (3,200 runs, 9,081 rounds; 627 to 640
  payments per rule-R setting, 339 to 376 taking births per rule-Q setting), structure equal after every round up to 5 or 6
  rounds. Rounds whose births would exceed 30,000 fresh distinctions were not compared.
- Its two parity methods (ranks; kernel projection) and the ring engine's rank method agree with brute-force enumeration
  on 600 drawn structures whose distinctions have one to several holders (2,659 knots, 1,729 failing): no disagreement. Its
  not-all-equal test agrees with brute force on 400 drawn structures (1,583 knots, 407 failing).
- The literal and the elimination closing differ, with three or more holders, in 23 of 576 runs (under Q, AT(1) and
  NEAR(LINES)); with at most two holders they never differed.

**The two objects under the record's laws (arm A), not-all-equal, 8 to 10 rounds, at most 3,000 knots.**
- The base laws reproduce the record: the ring of five returns every two rounds with 1, 1, 6, 6, 11, … parts; two-knot
  parts number 2, 4, 8, 16, 32 (retiring), Fibonacci-like (offshoots), Pell-like (waiting) on the small starts and five
  times those on the ring.
- **Under Q (O or N) and under TAKE-SHARED (O or N) the ring never returns and no two-knot part copies itself** on any
  registered start (ring starts through round 10; copier starts: no two-knot part after round 1).
- Hypothesis h1 holds on the three-knot start: under Q the round-1 join and the two offshoots form one group of three in
  round 2, because both offshoots take a distinction of their founder that the start's dead knot also holds, so that
  knot meets both; the roster is then one part, and a chain of one member a round follows. On the two-knot start all four
  round-1 offshoots take distinction 0 (six holders), meet one another directly, are all short in round 2 and retire
  (or wait for ever).
- Hypothesis h2 holds on the three-knot start: under TAKE-SHARED the short join of round 1 takes its second input in round 2
  from a shared distinction (oldest: the one it shares with its first founder); the roster stays one part through round 10
  and grows by one member a round (N) or stops at five members (O).
- Whether parts come apart at all (h3, first half): in 8 rounds, a part comes apart in 32 of 32 runs (11 base laws on
  their starts) with no taking, 2 of 31 under Q-O, 10 of 32 under Q-N, 0 of 32 under Q-SIB, 6 of 32 under Q-FRESH, 0 of 32
  under TAKE-SHARED (either index).
- **No two parts that came apart ever meet again under arm A**: 0 sealed meetings again in every run above, and 0 under
  every choice of the index on the small starts through round 4 (rule Q: every choice enumerated, 24 histories on the
  three-knot start per treatment, 32 on the ring of five under retiring and waiting, 3,000 drawn from larger trees with
  parts coming apart in 2,373 and 2,997 of them; rule R: 64 and 56 complete histories).
- The paired test (reading (i), the first six parts of each round, at most four pairs a round, rounds 1 to 5 of 7) on
  sealed-apart pairs that came apart: no grade 0, 1 or 2 in any pair, under either knot law: earlier laws 373 pairs; Q-N
  84; Q-N with parents' count 146; Q-FRESH 27 (Q-O and Q-SIB never had a pair to test); TAKE-SHARED had no pair that came
  apart (its 45 pairs per index are the two-knot start's two halves, meeting for the first time: no grade either).
- Hypothesis h3, second half, is wrong as worded: waiting does not help, and no later generation helps; under these laws
  "meet again" is unreachable at any round, by the argument below.
- Under the earlier laws with **HOLD** in place of RELEASE (the record's own swap), the roster is not sealed: a member that
  keeps a distinction meets its own child, and they can lie in different parts. Such parts are joinable a round later
  (two-knot and three-knot starts under (FLOOR1, CANCEL-WAIT, HOLD)); their courses never differed with the other barred
  (grade 2 never, both laws). So the record's "parts act alone" holds under RELEASE, as its settled statement says, and
  under HOLD it holds for courses but not for parts.

**The ladder (arm B), the same starts and base laws.**
- RECORD-2 and RECORD-3: parts come apart later (30 and 27 of 32 runs) and never meet again (189 and 116 pairs that came
  apart: no grade).
- ANY: nothing ever comes apart (0 of 32 runs); the roster is one part of bounded size.
- INHERIT (5 rounds, at most 800 knots): nothing comes apart (0 of 32); every descendant holds one distinction, so every
  member meets every other, most runs stop or jam within two rounds; the largest number of holders reached 2,270 in four
  rounds; parity knot failures in 14 of 32 runs (FLOOR1 included); not-all-equal none.
- AT(1): sealed parts meet again in 6 of 32 runs (O), 0 (N), 5 (SIB), 4 (FRESH). Pairs that came apart: grade 0 in 12 of
  47 (O), 0 of 122 (N), 13 of 48 (SIB), 12 of 89 (FRESH); grade 2 in 4, 0, 5, 4 of them, always after a meeting. None of
  the meetings with a grade 2 went through an ancestral common knot (6 of 26 meetings went through one under O, with no
  grade 2).
- AT(2): sealed parts meet again in 28 (O), 15 (N), 25 (SIB), 23 (FRESH) of 32 runs. Pairs that came apart: grade 0 in
  124 of 183 (O), 43 of 199 (N), 119 of 177 (SIB), 61 of 170 (FRESH); grade 1 in 6, 16, 7, 3; grade 2 in 42, 35, 47, 37,
  every one after or with a meeting (under N, two under parity came through a closing). Meetings through an ancestral common knot with a
  grade 2: 10 (O), 5 (N), 8 (SIB), 4 (FRESH).
- NEAR(PARTS): sealed parts meet again in 30 to 31 of 32 runs; grade 2 in 35 (O), 96 (N), 48 (SIB) pairs that came
  apart, about half of them because the taking rule itself read whether the other part exists (channel "rule": 18, 54, 24).
  NEAR(LINES): 3 of 32 runs; 3 grade 2 (O). NEAR with LONE: 2 of 32 runs, grade 0 in 4 pairs, grade 2 never.
- **The smallest case found** (three-knot start, (FLOOR1, CANCEL-RETIRE, RELEASE), AT(2, O), not-all-equal; 20 knots by
  round 5):
  - Round 1: join 3 of knots 1 and 2 (one fresh), offshoots 4 and 5 (two fresh each); one part {3, 4, 5}.
  - Round 2: knot 3 is short and retires; 4 and 5 each make two offshoots: parts {6, 7} (through 4) and {8, 9} (through 5),
    sealed apart. They came apart from the round-1 part {3, 4, 5}.
  - Round 3: each copy makes its join (10, 11) and two offshoots. The offshoots 12, 13 of 6 and 7 take distinction 0,
    which their great-grandparent knot 1 holds with the start's dead knot 0; the offshoots 14, 15 of 8 and 9 take
    distinction 2, which knot 2 holds with knot 0. Distinctions 0 and 2 now have four holders. Knot 0 meets 12, 13, 14 and
    15: **the two copies meet again, through knot 0**, the knot their founders 1 and 2 were joinable through at round 0.
    Knot 0 is a start knot and no recorded ancestor of either: a common knot of their founders, not an ancestral common
    knot.
  - Round 4: groups (10, 12, 13), (11, 14, 15) and the four pairs across; 12 to 15 each owe three and hold one, are short
    and retire; joins 10 and 11 make one offshoot each. With the second copy barred after round 2 (reading (i)), or
    removed (reading (ii)), the first copy's 10, 12 and 13 make one join of three parents instead. **Grade 2 at round 4**,
    channel meeting; no birth with parents from both copies (no grade 1).
  - Every knot passes the knot test under parity (two methods) and not-all-equal at every round through round 6.
  - Grade 3, what the second part is: with knot 2 holding three loose distinctions instead of two
    (`[[0,1,2,3],[0,1,4,5],[2,3,6,7,8]]`), the first copy's offshoots see demand 5 in place of 3 at round 3 and make the
    same births: no grade 3 in what is built.
  - Grade 3, the index (only the first copy's takes changed): with O or SIB the copies meet and the first copy's course
    depends on the second; with N or FRESH the first copy takes a distinction held only by its own ancestors and reads
    nothing. **The index decides whether the part reads the other.**
- **The smallest meeting through an ancestral common knot with a grade 2** under FLOOR1 or the ring law: AT(2, O) on the
  three-knot start under (FLOOR1, CANCEL-WAIT): parts {3} (the waiting join) and {6, 7} after round 2 meet again after
  round 4 through knot 1, an ancestor of both and the parent of neither; grade 2 at round 5; the whole roster then jams
  (every member short and waiting). On the ring of five under the ring law with AT(2, O), when only a given-off part's
  takes use the index FRESH it reads the ring's part (grade 2 at round 4); with O or SIB it meets the ring's part and its
  course does not change through round 6; with N it does not meet it.
- **Knots.** Parity, in the first sweep (14 variants, 448 runs, structures of at most 1,500 knots): 154,673 knot verdicts by
  two methods, all agreeing. Failures only (1) where a birth receives nothing
  (FLOOR0 and ONE-FEWER: the three-parent joins, as in the record; under Q on the three-knot start the round-1 group of
  three gives such a join in round 2, and the start's dead knot fails), (2) INHERIT (above), and (3) one case under FLOOR1:
  NEAR(LINES) on the three-knot start with offshoots, where a three-parent join with one fresh distinction fails at birth
  in round 6, because its three inputs are already constrained together. Not-all-equal: 52,715 knot verdicts (977,304 SAT
  calls) under FLOOR1 and the ring law on structures of at most 250 knots, the fourteen variants of the first sweep and
  INHERIT: none fails. The index variants (ten more, 320 runs) were knot-tested under parity only: 77,703 verdicts, the two
  methods agreeing, failures only under FLOOR0 and ONE-FEWER and in the same NEAR(LINES) case under FLOOR1.
- **Holders.** The largest number of holders of one distinction within 8 rounds: 2 (earlier laws, RECORD, ANY), 128 (Q-O,
  ring of five), 15 (Q-N), 9 and 4 (TAKE-SHARED O, N), 86 (AT(1, O)), 122 (AT(2, O)), 44 (AT(2, N)), 32 (AT(2, SIB)), 80
  (AT(2, FRESH)), 50 (NEAR(PARTS, O)), 200 (NEAR(PARTS, N)).
- **Timings and bounds.** Each sweep of 448 runs took 60 to 75 s on one core; the paired tests 25 to 60 s per knot law; the
  enumeration 16 s; the not-all-equal tests 4.5 s. 33 runs were stopped by the prototype's guard (a round with more than
  20,000 candidate pairs, groups or births, or more than 400,000 distinctions), mostly under Q-O and AT(1, O), where one
  distinction gains many holders; two more ran out of memory before the guard existed.
- Not run before the freeze: D2(5, 3) and Ring(7, 3) under the copier laws; HOLD under the ladder beyond AT(2, O); reading
  (ii) beyond the smallest case; parity knot tests on the index variants beyond 8 rounds; anything past round 10.

## Settled by construction (stated, not tested)

Arguments for the advisor and the referee; the runs check them.

1. **The seal argument.** Let a law satisfy H1 (every distinction a new knot takes is held, at the start of its round, by
   one of its parents; its other places are fresh) and H2 (two members are joinable only when some knot meets both, and
   every birth's parents lie in one part of the roster its round reads); knots never gain places. If the roster after
   round s is **sealed**, then no two of its parts ever have members that meet, or are joinable, or are parents of one
   birth, at any later round. Proof. For a part X let Δ_X be the places of X's members after round s. By induction every
   knot descended from X holds only distinctions of Δ_X and fresh ones made for X's descendants (H1, and every birth's
   parents lie among the descendants of one part). For X ≠ Y, Δ_X and Δ_Y are disjoint (sealed), and fresh distinctions
   are new. So descendants of X and of Y share no distinction. A knot meeting one of each: if made after round s it
   descends from one part Z, and it can share a distinction with a descendant of X only if Z = X (sealing), and with one
   of Y only if Z = Y; if older, its places are
   fixed, so it holds a distinction of Δ_X and one of Δ_Y and met members of both after round s (or is one and met the
   other directly). Either contradicts sealing. So no group contains descendants of two parts (H2). ∎
2. **When the roster is sealed.** Under RELEASE the roster after any round t ≥ 1 is sealed, except when two start knots
   that share a distinction held by those two alone are both members. Two members that meet share a distinction; with
   three or more holders a third holder meets both, so they lie in one part; with exactly two holders one took it from the
   other (parent and child) or both are start knots; under RELEASE a member that makes a birth spends every usable loose
   distinction (definitions step 5; a short member under CANCEL-OFFSHOOT or TAKE-SHARED too; under CANCEL-WAIT and
   CANCEL-RETIRE it makes no birth), so a parent is never a member beside its child. Under HOLD it can be.
3. **So rules Q and R cannot make parts that have come apart meet again**, under any index (O, N, SIB, FRESH, every
   choice), any ration, treatment, release rule, extra or closing form of the definitions: each takes only distinctions
   the birth's own parent holds (H1), and both keep H2. Nor can INHERIT. This is the reason it cannot happen under these
   laws: what a parent holds is already met by everything the parent meets, so taking it can only re-join what is still
   joined. The A225 move, as a growth law, falls on this side whenever the birth's parents are the holders of what it
   takes.
4. **The course.** Under H1, H2 and RELEASE, after a sealed round s the births descended from a part X read only X's
   descendants and the older knots that meet them, except through round-wide rules: STALL (any short member anywhere),
   the residual stall of TAKE-SHARED, and the parity closing (LITERAL reads every loose distinction of the structure;
   ELIMINATION reads the span of every knot's rule). The index's order of names compares only X's own distinctions, whose
   relative order does not depend on other parts. So under not-all-equal with a cancelling treatment runs A and B give
   the same course of X; under parity a grade 2 can come only through the closing, and under STALL or TAKE-SHARED only
   through a stall.
5. **The record rung cannot either.** Under RECORD-k with k fixed, if no member of X and no member of Y have a common
   ancestor within k parent steps of each, no descendants of them ever do: a common ancestor of two later members within k
   steps would lie within k steps of members of X and of Y at round s. So RECORD-k delays coming apart and never lets parts
   that came apart meet again. ANY never lets anything come apart.
6. **What breaks the seal.** A law outside H1, under which a birth takes a distinction held by a knot that none of its
   parents is, can make a knot that already meets the other part's members meet a new knot of this part: ancestor-taking
   above the parent (AT(k ≥ 1), NEAR). A fixed k reads a fixed number of parent steps up the birth record; the meeting it
   makes goes through an older knot that the other part's descendants also reach.
7. **Checks, true by construction** (run and reported, cannot fail unless the code departs from the definitions): with no
   taking rule the engine is the ring study's; under not-all-equal there is no closing; a birth that takes nothing extra
   has as many inputs as parents.

## What is supplied

Everything the definitions supply (A104, A224, A237, the starts, the reading of a part as a thing, A125), and here:
- **The taking rules**, each a scaffold: rule Q (A235), rule R as the treatment TAKE-SHARED (A230), INHERIT, AT(k), NEAR,
  RECORD-k and ANY, all added by hand.
- **The index** of each (A231, A236 and two new ones): O and N are conventions on names, and the names of a start are as its
  stars are written; SIB reads the order of a parent's births in the round; FRESH reads the parent's places and its number
  of parents; EVERY is an enumeration. None is made by the growth.
- **The birth record**: RECORD-k reads it k parent steps up from each member; INHERIT one step from each parent; AT(k)
  k + 1 steps from the new knot; NEAR any number, and NEAR(PARTS) also reads the parts of the whole roster.
- The order of births; the fresh count read by inputs; the closing in two forms; the base laws' rations and treatments;
  the paired test's barring and removal; the course, grades and channels; the bounds.

**The cost of each rung**, as registered:

| Rung | Supplied beyond the base law | Can parts that came apart meet again? | Holders (prototype, 8 rounds) | Knots (prototype) |
| --- | --- | --- | --- | --- |
| 0 RECORD-k | the record, k steps; joinability not read from the structure | no (argument 5) | 2 | pass |
| 0′ ANY | everything joinable | nothing comes apart | 2 | pass |
| 1 Q(index) | the rule; the index | no (argument 3) | up to 128 (O), 15 (N) | pass where every birth has a fresh distinction |
| 1′ INHERIT | the rule; "oldest" as index; one record step | no (argument 3); nothing comes apart | up to 2,270 | parity failures |
| 2 AT(k, index) | the rule; the index; k + 1 record steps | yes (seen) | up to 122 | pass under FLOOR1 and the ring law |
| 3 NEAR(trigger, index) | the rule; the index; the whole record; under PARTS the roster's parts | yes (seen); half its grade 2 is its rule reading the other part | up to 200 | one parity failure under FLOOR1 |

## What a result would and would not show

- **Supplied or made** (frozen criterion). A part reads another **through the growth** when all of the following hold;
  otherwise the reader is **supplied**, and the result says by what:
  1. One start, one law, no birth, attachment, barring or choice placed by hand after round 0 in run A (the barring of run
     B is the experiment, not part of the growth).
  2. The two parts came apart (they descend from one part after an earlier round) and were sealed apart at round s, so
     their meeting is not built into the start (no distinction shared by their members at round s).
  3. The grade 2 is through the channel **meeting**: the parts meet again through a knot that the growth made, or through
     a distinction whose extra holders the growth's births gave it.
  4. It is not through a round-wide rule (STALL, a residual stall, either closing), not through record-only joinability
     (which links nothing in the structure), and not through a taking rule that reads whether the other part exists
     (NEAR(PARTS), and NEAR's triggers generally).
  Under every rung, supplied in any case: the taking rule itself, its index, the birth record it reads, the base law's
  ration and treatment, the start and the complete round. So "made by the growth" means the meeting and the dependence
  are made by births under a stated law; it does not mean the law is the model's.
- **A grade 2 under AT(k) would show** that a stated law, which reads k + 1 steps of the birth record and nothing about the
  other part, lets one part's births depend on another part through a meeting the growth makes, with every knot passing
  the knot test (if they do). Where the common knot is an ancestor of both, it is an ancestral common knot, the knot of
  the owner's picture (A241). It would not show that the dependence carries anything beyond "present or barred", that
  the reader makes a pattern of its own from what it reads (the third property of a fold of emergence, A223), or
  anything about the model's own laws: the rule and its index are supplied.
- **A null for arm A would show** the reason, under these laws: taking what a parent holds cannot reach a part that has come
  apart. It would not show that no law of the record's kind can: it is exact for H1 and H2.
- **What the prototype already suggests about the owner's picture:** the meeting usually stops the reader (its members
  become short and retire, wait or make offshoots); it rarely builds anything jointly (grade 1 in 3 to 16 pairs of up to
  199). A reader that builds from what it reads is not shown.
- **Not shown in any case:** anything about the golden ratio's "parts". The record already has that a knot's own holdings
  give the round it was made in to within three values in the golden-ratio eddy (r = f + 2p − 3 − 2e,
  `RING-IN-BALANCE-20261123-001B/results.md` line 25), so a place in that growth is carried by the structure and nothing
  reads it. A pattern that steps an index, the owner's "logic based iterators", is outside this study and is lead B326.

## Starts (stars)

- **Ring(5, 3)**: `[[4,0,5,6,7],[0,1,8,9,10],[1,2,11,12,13],[2,3,14,15,16],[3,4,17,18,19]]`.
- **Ring(7, 3)**: `[[6,0,7,8,9],[0,1,10,11,12],[1,2,13,14,15],[2,3,16,17,18],[3,4,19,20,21],[4,5,22,23,24],[5,6,25,26,27]]`.
- **D2(5, 3)**: `[[20,21,22,0,1,18,19],[23,24,25,4,5,2,3],[26,27,28,8,9,6,7],[29,30,31,12,13,10,11],[32,33,34,16,17,14,15],[0,1,2,3],[4,5,6,7],[8,9,10,11],[12,13,14,15],[16,17,18,19]]`.
- **The two-knot start**: `[[0,1,2],[0,3,4]]`. Its two knots meet directly and are not joinable: two parts at round 0.
- **The three-knot start**: `[[0,1,2,3],[0,1,4,5],[2,3,6,7]]`: a dead knot and two members joinable through it.
- **The three-knot start, second founder larger** (grade 3, what the second part is): `[[0,1,2,3],[0,1,4,5],[2,3,6,7,8]]`.

Names are as written; the indices O and N compare them.

## Runs (frozen)

Not-all-equal is primary (no closing); every run is repeated under parity with ELIMINATION, and the runs marked (L) also
with LITERAL. RELEASE unless stated. Every run stops at 10 rounds or at the first round that would pass 5,000 knots; a
round that the engine cannot read within the resources below is reported as unread, with the law and start.

| Run | Starts | Laws | Readings |
| --- | --- | --- | --- |
| G | all starts | no taking rule: B-RING, B-RING with FILLERS, B-COPY(t) for the three t, FLOOR0 and ONE-FEWER swaps, HOLD swaps; and the other thread's engines on their overlap: rule R and rule Q under the ordinary count on the seven named starts of the prototype check and the first 400 sparse draws per law and convention | the gate (P0) |
| 1 | ring starts under B-RING; two-knot, three-knot and Ring(5, 3) under B-COPY(t) | none; Q(O), Q(N); TAKE-SHARED(O), TAKE-SHARED(N) | per round: members, parts, sealed, holders, births, takes; come apart; meets again (sealed or not); the knot test at every round (parity up to 3,000 knots, not-all-equal up to 400 knots); returns of the ring (definitions line 87) and the count N(t) of two-knot parts (COPYING-PARTS definitions); the paired test (i) and (ii) on every pair of sealed-apart parts among the first eight parts of each round s ≤ 8 (L) |
| 2 | the two small starts and Ring(5, 3) | Q and TAKE-SHARED with index EVERY through round 4 (every choice; at most 100,000 histories, otherwise drawn by seed 2026112401); Q with SIB and FRESH; fresh by parents; FLOOR0, ONE-FEWER, HOLD, FILLERS swaps | meets again; come apart |
| 3 | as run 1 | RECORD-2, RECORD-3, ANY, INHERIT, AT(1, index), AT(2, index) for index O, N, SIB, FRESH, NEAR(LINES, O), NEAR(PARTS, O), NEAR(LINES, O, LONE) | as run 1, and for every meeting again the common knots through which it goes, classed: ancestral common knot, ancestor of one part only, neither (L) |
| 4 | the smallest case (three-knot, B-COPY(CANCEL-RETIRE), AT(2, O)); three-knot, B-COPY(CANCEL-WAIT), AT(2, O); Ring(5, 3), B-RING, AT(2, FRESH) | as named | round by round: births, met sets, parts; the paired test (i) and (ii); grade 3 by what the second part is (the larger-founder start) and by the index (only the first part's takes changed: O, N, SIB, FRESH) |

**Knot test coverage.** The owner's standard is the knot test on every knot made, under parity and under not-all-equal.
The sweeps of runs 1 to 3 test every knot of every structure up to the sizes in the table. Beyond that, every structure in
which a meeting again or a grade is reported is tested under both knot laws at the round of the report and at the last
round run. A case whose structure is too large for the not-all-equal test is reported as untested there and does not count
towards the stop.

## Predictions (frozen)

Marked (a) already seen in the drafter's scratch runs, (b) a hand prediction not run, (c) open, reported without a
prediction. A **check** is true by construction.

| # | Prediction | Fails when |
| --- | --- | --- |
| P0 (a; a check) | Gate. With no taking rule the engine's complete rounds equal the ring study's engine knot for knot on every run of G; on the overlap it equals rule R's and rule Q's engines after every round; its parity methods and its not-all-equal test agree with brute force on 600 and 400 drawn structures; the two closings agree wherever every distinction has at most two holders. | any fails |
| P1 (a; argument 3) | Arm A: under Q and TAKE-SHARED, every index (EVERY on small cases), every ration, treatment and release rule registered, both knot laws, no two parts that came apart and are sealed apart ever meet again, and no birth has parents descended from both (grades 0 and 1 never). | a sealed meeting again, or such a birth |
| P2 (a; argument 4) | Arm A, the paired test on sealed-apart parts: under not-all-equal no grade 2 in either reading; under parity a grade 2 only through the channel global. | a grade 2 through meeting, rule or other |
| P3 (a) | Under Q and TAKE-SHARED (O and N) the ring never returns (no part after rounds 1 to 10 the same as the start's roster) on the three ring starts, and no two-knot part exists after round 1 on the two-knot, three-knot and Ring(5, 3) starts under B-COPY(t), except the two of round 1 on the two-knot start under TAKE-SHARED. | the ring returns, or a two-knot part appears |
| P4 (a) | h1 and h2 on the three-knot start under B-COPY(t): with Q (O or N) the round-1 join and offshoots form one group of three in round 2 and the roster is one part at every round; with TAKE-SHARED (O or N) the round-1 join is short in round 2 and takes a shared distinction for its second join, and the roster is one part through round 10. | either fails |
| P5 (b) | Arm A under HOLD (run 2): the roster can be unsealed (a member meets its own child); such parts can become joinable (grade 0), and their courses never differ with the other barred (grade 2 never). The prototype saw this under the earlier laws with HOLD only. | a grade 2, or arm A fails P1 under RELEASE |
| P6 (a; argument 5) | RECORD-2 and RECORD-3 make no part that came apart meet again; ANY and INHERIT let nothing come apart. | a meeting again under RECORD-k; a part coming apart under ANY or INHERIT |
| P7 (a) | The smallest case, round by round as disclosed: sealed apart after round 2, meeting again after round 3 through start knot 0 (not an ancestor), grade 2 at round 4 in reading (i) and (ii), no grade 1, every knot passing under both laws through round 6. | any step differs |
| P8 (a) | The least rung of the ladder with a grade 2 through the channel meeting is AT(1) (indices O, SIB or FRESH; not N); the least rung with a grade 2 whose meeting goes through an ancestral common knot is AT(2); NEAR adds no cheaper case, and under NEAR(PARTS) a grade 2 also comes through the channel rule. | a grade 2 through meeting under a rung below AT(1), none under AT(1), or none through an ancestral common knot under AT(2) |
| P9 (a) | Grade 3 by the index (only the first part's takes changed): in run 4's smallest case the first copy's course depends on the second under O and SIB and not under N or FRESH; on Ring(5, 3) under AT(2, O) the given-off part reads the ring's part when its own takes use FRESH, and not under O, N or SIB, through round 6. | otherwise |
| P10 (c) | Grade 3 by what the second part is (the larger-founder start): reported. Seen in the prototype: a different demand at round 3, the same births. | not applicable |
| P11 (a) | The knot test: under FLOOR1 and the ring law every knot passes under not-all-equal in every arm; under parity every knot passes in arm A and under AT(k), and the failures are where a birth receives no fresh distinction, under INHERIT, or under NEAR at a three-parent join whose inputs are constrained together. | a failure elsewhere, or a disagreement of the two parity methods |
| P12 (c) | The number of holders of the most-held distinction by round, under each rung and index: reported. | not applicable |

A result that fails is reported as it is. P1 to P6 test arguments on finitely many runs; the result note states the
arguments for the referee.

## Runs and stop rule

- One engine is written from this text and the definitions. It passes P0 before any other run.
- **Stop** when (a) each of rule Q, rule R and the A225 move has a verdict: parts meet again and a part's course depends on
  another, or the reason it cannot under that law (argument 3, checked by P1, P2 and P5); and (b) the least rung of the
  ladder at which a part's course depends on another through the channel meeting is identified with its cost (what it
  reads, its index, its holders, its knot test), or every registered rung has failed with its reason. Every registered run
  is done and every prediction has a verdict.
- **Disagreements** with the disclosed prototype are replayed birth by birth (parents, inputs, holders of each input,
  fresh count), the listing decides, and the disagreement is reported as a finding.
- **Resources.** Each run is expected to take under ten minutes and 8 GB on one process; anything longer goes through
  the shared runner with a row in the long-running index. A round that the engine cannot read within those limits is
  reported as unread.
- **Deviations** are recorded in `deviations.md` in the experiment family before the affected run.
- **The advisor** (Claude Fable 5.2) reviews this draft cold before the freeze, with the words below.


# (5) THE SHARED DEFINITIONS (frozen, of the earlier study; line numbers as cited)

   1  # A ring in balance: definitions shared by the three studies
   2  
   3  Epic `RING-IN-BALANCE-20261123-001`, 2026-11-23. Frozen with the three pre-registrations, before any of the study's code is
   4  written. Tickets A, B and C cite this file and add only what is their own. The canonical K1–K3 test is unchanged. Words are the
   5  glossary's (Intuitions guide). The growth records' "junction" is a knot and their "growing end" is the live roster. Their
   6  "witness" is here a **common knot**, their "witnessed set" a **met set** and their "adjacent" **joinable**, because the glossary
   7  keeps witness for a helper variable and graph theory uses adjacent for what the program calls meeting.
   8  
   9  ## Structure
  10  
  11  - A **structure** is a finite set of knots, each holding a set of distinctions, its **places**. A distinction has one or two
  12    **holders**. It is **loose** with one holder and **shared** with two. Every knot of a start has at least three places, and so
  13    has every new knot except one that receives no fresh distinction (below).
  14  - Two knots **meet** when they share a distinction. A knot is **live** while it holds a loose distinction and **dead** otherwise.
  15  - A **start** is a structure given before any birth, written as its list of knots, each a list of distinction numbers (the
  16    records' stars).
  17  - A loose distinction is **usable** unless the law has **barred** it: a barred distinction stays loose and is never taken by any
  18    birth. (The Intuitions guide and the site call a barred distinction "never used".)
  19  
  20  ## The live roster
  21  
  22  - The **members** of the live roster are the knots holding at least one usable loose distinction. Write h(u) for the number of
  23    usable loose distinctions member u holds and k(u) for the number of barred ones. A knot holding only barred distinctions is
  24    live and is not a member.
  25  - A **met set** is the set of members that one knot of the structure meets, when it has at least two members. That knot is a
  26    **common knot** of those members; it may be dead or itself a member. Two knots with the same met set count once.
  27  - Two members are **joinable** when some met set contains both. A **part** of the live roster is a connected component of the
  28    relation joinable. The roster is **past its start** when no member meets a member (the records' positive age).
  29  - Two rosters, or two parts, are **the same** when a one-to-one renaming of members carries h, k and the family of
  30    inclusion-maximal met sets of one onto the other.
  31  
  32  ## One complete round
  33  
  34  A **law** is a knot law (parity or not-all-equal), a ration, a treatment and optional extras. One round, on real knots:
  35  
  36  1. **Groups.** First take every inclusion-maximal set of at least three pairwise joinable members that is contained in no
  37     single met set. Then take every joinable pair that is contained in none of the sets just taken. These are the groups
  38     ([ORDINARY-DYNAMICS-20261120-001](../ORDINARY-DYNAMICS-20261120-001/end_operator.md), "The operator on the present end", step 1).
  39  2. **Owing.** Member u owes one usable loose distinction to each group containing it. It is **short** when it owes more than
  40     h(u). Shortness is read once, here, for the whole round.
  41  3. **Treatment of a short member.**
  42     - STALL: if any member is short, no birth is made and the growth has stalled.
  43     - CANCEL-OFFSHOOT: every group containing a short member is cancelled; the short member makes an offshoot from each of its
  44       usable loose distinctions.
  45     - CANCEL-WAIT: every group containing a short member is cancelled; the short member **waits**: it makes nothing and keeps
  46       everything it holds.
  47     - CANCEL-RETIRE: every group containing a short member is cancelled; the short member **retires**: it makes nothing now or
  48       later, and its loose distinctions are barred.
  49  4. **Joins.** Each group that is kept makes one new knot, a **join**, whose parents are its members; it takes one usable loose
  50     distinction from each.
  51  5. **Offshoots and the release rule.** A member that is not short, after paying its kept groups, makes one new knot of one
  52     parent, an **offshoot**, from each usable loose distinction it has left. RELEASE (the default): this includes the
  53     distinctions that its cancelled groups would have taken. HOLD: it keeps those and makes offshoots only from the rest. With
  54     the extra NO-OFFSHOOT it makes no offshoot, and the distinctions an offshoot would have taken are barred.
  55  6. **Demand.** Count every new knot as a member holding one usable loose distinction, whatever it will receive, and keep every
  56     old member that still holds a usable loose distinction after steps 3 to 5 (one that waits; under HOLD, one that keeps what
  57     its cancelled groups would have taken) with what it holds. Form the groups of that roster as in step 1. The **demand** D of
  58     a new knot is the number of those groups that contain it.
  59  7. **Fresh distinctions (the ration).** A new knot with p parents and demand D receives f fresh distinctions, each loose and held
  60     by it alone. With q = max(D, 3 − p, 1), the ordinary count:
  61     - ORD: f = q. CAP-k: f = min(q, k). RATION-k: f = max(k, 3 − p).
  62     - ONE-FEWER: f = min(q, max(3 − p, 0, q − 1)). FLOOR0: f = max(3 − p, 0). FLOOR1: f = max(3 − p, 1).
  63     - **Closing exception** (parity only, every ration): a new knot that takes every loose distinction of the structure receives
  64       none; it may then have fewer than three places. It is then the round's only birth, nothing is barred and no old member
  65       keeps anything. Under not-all-equal there is no exception
  66       ([NAE-GROWTH-20261119-001](../NAE-GROWTH-20261119-001/nae_growth.md): the growth reads the knot law in this one place).
  67  8. **Extra FILLERS.** Of a new knot's f fresh distinctions, min(f, D) are usable and the rest are barred.
  68  
  69  The records' ordinary growth, the cheapest growth of lesson 8.1, is the law (ORD, STALL). **The two added rules** are the law
  70  (CAP-3, CANCEL-WAIT with RELEASE). **The three added rules** are (CAP-3, CANCEL-WAIT with RELEASE, FILLERS). They were added by
  71  hand (assumption A224, a scaffold); RELEASE is part of what was added. The pilot's program counted a short member by all its
  72  loose distinctions; the two readings agree, because a member holding a barred distinction owes exactly its usable count in
  73  the one round it acts. One barred distinction anywhere switches the closing exception off everywhere, since the exception needs
  74  a birth that takes every loose distinction there is.
  75  
  76  A distinction taken by a new knot becomes shared between its old holder and the new knot. Which of a member's usable loose
  77  distinctions goes to which birth makes no difference up to renaming.
  78  
  79  ## Kinds of outcome under complete rounds
  80  
  81  A run is one start grown under one law through a stated number of rounds, or until a stated number of knots. After each round:
  82  
  83  - The growth has **stopped** when the roster has no member, **stalled** (STALL only) when a member is short, and **jammed** when
  84    the roster has members and the round makes no birth.
  85  - A part Y of the roster after round s, past its start, **returns** at round t > s when the members after round t that descend
  86    from Y (through parents; a waiting member descends from itself) include a part that is the same as Y. The other parts those
  87    descendants form have **come apart** from Y, and Y **gives parts off** when there is at least one. Returns are searched with
  88    the least s first and then the least t, and t − s is the period.
  89  - The roster is **in balance** from round s with period T when at least one birth is made in every round and the whole roster
  90    after round t + T is the same as the whole roster after round t for every t ≥ s in the run. The structure still grows.
  91  - A part has **ended** when none of the knots descending from it is a member. It may still hold barred distinctions.
  92  - For a census a run is given one kind, the first that applies: stalled; jammed; stopped; a part returns giving parts off; a
  93    part returns giving none off; grows to the bound with no return found.
  94  
  95  ## One part at a time, and one birth at a time
  96  
  97  - **Part-round law.** A move is one complete round of one part: steps 1 to 8 applied to the members of that part alone, the
  98    other parts left as they are (the closing exception as stated: only for a birth that takes every loose distinction of the
  99    whole structure). The **own time** of a start knot is 0; a new knot's is one more than its parents'; and a member that
 100    waits through a move of its part gains one. So a member's own time is the number of moves its line of descent has taken
 101    part in. A **priority** chooses the part that moves next among the parts that would make a birth:
 102    - ALL-IN-TURN: every part once, then again; this is the complete round.
 103    - UNIFORM: each part with equal chance.
 104    - BY-MEMBERS: each part with chance in proportion to its number of members.
 105    - LARGEST: a part with the most members; SMALLEST: one with the fewest; ties uniform.
 106    - MOST-LOOSE: a part whose members hold the most usable loose distinctions in all; ties uniform.
 107    - LEAST-TIME: a part whose members have the least own time; ties uniform. This priority reads the history, not the structure.
 108  - **Birth-by-birth law** (the present-state reading of [ROUND-FREE-20261119-001](../ROUND-FREE-20261119-001/round_free.md), with
 109    waiting). A move is one birth, and everything is read again after every move.
 110    1. Form the groups of the present roster as in step 1, with every knot allowed as a common knot (ANY) or only dead knots
 111       (DEAD). A group is **open** when no knot already made has all of its members among its parents.
 112    2. A member is short when it is in more open groups than h(u); a short member makes nothing. Under FIRST-COME, used only to
 113       check the engine against the record, no member counts as short.
 114    3. Every open group with no short member is a join move. A member that is not short and holds more usable loose distinctions
 115       than the number of open groups without a short member that contain it has an offshoot move. (Under FIRST-COME: every open
 116       group is a join move, and a member has an offshoot move when h(u) exceeds the number of open groups containing it.)
 117    4. The new knot receives max(3, 3 − p) fresh distinctions (RATION-3), or max(d, 3 − p, 1) (PRESENT-ORD), where d is the number
 118       of open groups containing it immediately after its birth, the new knot counted as a member before it receives anything.
 119       Closing exception, parity only: a move that takes every loose distinction of the structure, with d = 0 where d is read,
 120       receives none.
 121    5. Start knots have **generation** 0 and a new knot has generation one more than the greatest generation of its parents; a
 122       move's generation is the greatest generation of its parents. The next move is chosen uniformly among all moves (UNIFORM)
 123       or among the moves of least generation (BY-GENERATION), with joins first, offshoots first, or uniformly among those. The
 124       generation is the simulator's record of who was made from whom; it is not read from the structure.
 125    - A birth-by-birth run has **jammed at generation g** when no move of generation g or less is available and some member of
 126      generation g or less is short.
 127  
 128  ## The knot test
 129  
 130  - **Parity.** Each knot is the rule that its places have even parity. A knot with place set S passes K1–K3 in the whole
 131    structure when the allowed states of the structure, restricted to S, are exactly the even assignments of S. Two methods are
 132    run and must agree on every knot. Ranks: with H the matrix over the field of two elements with one row for each knot, the
 133    rank of H less the rank of H with the columns of S removed is one (the records' test, ORDINARY-DYNAMICS, `rulers.py`). Cut:
 134    in the graph with one vertex for each knot and one for the outside, an edge between the two holders of each shared
 135    distinction and an edge to the outside for each loose one, deleting the knot leaves the rest connected (the knot is not a cut
 136    vertex; the allowed states are the graph's cycle space).
 137  - **Not-all-equal.** Each knot is the rule that its places are not all equal. A knot passes when the assignments of S that
 138    extend to an allowed state of the whole structure are exactly the assignments that are not constant, decided by a SAT solver
 139    for each of the 2^|S| assignments (the records' test, ORDINARY-DYNAMICS, `source_cert.py`).
 140  - **Extension.** A round, or a move, extends when every allowed state of the structure before it is the restriction of an
 141    allowed state after it.
 142  
 143  ## Named starts
 144  
 145  - **Ring(n, a).** Knots 0 to n − 1. Knot i shares one distinction with knot i + 1 (mod n) and holds a loose distinctions.
 146    Ring(5, 3) is the start of the golden-ratio eddy.
 147  - **Cycle through dead knots, doubled, D2(n, a).** Members 0 to n − 1, each holding a loose distinctions, and dead knots
 148    w_0 to w_{n−1}; w_i shares two distinctions with member i and two with member i + 1 (mod n), so w_i has four places and its
 149    met set is {i, i + 1}.
 150  - **Cycle through dead knots that meet one another, DW(n, a).** As D2 with single meetings: w_i shares one distinction with
 151    member i, one with member i + 1, one with w_{i−1} and one with w_{i+1}.
 152  - **The seven-knot generator.** Stars [0,1,2,9,10,11], [0,1,3], [4,5,12,13,14], [6,7,15,16,17], [2,3,4,6,18,19,20], [7,8,21,22],
 153    [5,8,23,24] ([GENERATORS-20261120-001](../GENERATORS-20261120-001/source.md)).
 154  
 155  ## What is supplied by hand
 156  
 157  The complete round (assumption A104); every ration other than ORD, every treatment other than STALL, the release rule and both
 158  extras (A224); the part-round law, the birth-by-birth laws and every priority; the starts; the reading of a part as a thing (as
 159  in A125); the bounds on rounds, moves and knots; and each weighting named where a share is given. Each study says which of
 160  these it swaps.
