# Two patterns as one part at the start, and two of the second left from both? Pre-registration

Ticket `MADE-COPIER-20261125-001B` of epic `MADE-COPIER-20261125-001` (lead B327; assumptions A244 and A248). The code
will be written by a helper agent that has not seen the drafter's prototype, from this text ("PB"), [ticket B's
definitions](../MADE-COPIER-20261125-001/definitions_b.md) ("DB"), [ticket B's claim](../MADE-COPIER-20261125-001/claim_b.md),
[ticket A's definitions](../MADE-COPIER-20261125-001/definitions.md) ("D"), [ticket A's
pre-registration](../MADE-COPIER-20261125-001A/preregistration.md) ("P"; nothing in it is changed), the fold study's and the
shared definitions ("FD", "SD"), the data files of this folder ([starts_b.json](starts_b.json),
[rosters_b.json](rosters_b.json)) and ticket A's [starts.json](../MADE-COPIER-20261125-001A/starts.json). The engine will
extend the fold study's engine
(`experiments/PARTS-MEET-AGAIN-20261124-001A/PARTS-MEET-AGAIN-20261124-001A-E001_meet_again/pm.py`) without editing it,
and may share ticket A's engine for the readings both tickets use. The canonical K1–K3 test is unchanged. Versions 1 and 2 of
this text are filed in the advisor folder as sent; where a reading changed, the change is said where it is made. No claim
is made about living things, minds, physics or time.

**Frozen on 2026-11-25 (UTC; the evening of 24 November 2026, Pacific time), after the advisor's two passes on this
ticket and before its code is written.** Ticket A's frozen text is not changed by anything here.

## The question

The owner's second addition, 24 November 2026 (Pacific time; the record's tickets carry 25 November, its date in UTC),
after hearing that the scratch runs had no copier even for one pattern once the start is renumbered: "I have a trick
maybe. What if instead of 'copying', we consume and output 2?" It is recorded, with how the thread reads it, in
[his request](../MADE-COPIER-20261125-001/owner_request.md), "The owner's second addition". His standing words, his four
steps and his stop are those of P, "The question". His stop is read here: stop at a first pattern X and a law under which
CB-1 holds for a second pattern (DB 4.1), or CB-2 for the class (DB 4.2), with the three verdicts; or at a reason none can
under that law; and otherwise at the bounded report of "What a result would and would not show".

**What is tested** (claim, section 5): CB-1, the second pattern with the first (his sentence read literally; the
literature's autocatalysis reading), and CB-2, the first pattern for the class (the thread's stricter reading), in arm 1
(no taking rule; a census of marked start rosters, the meeting supplied by the start, W1 to W4) and arm 2 (MET under CAP-3(t) and
FBP(t)). Settled by argument and checked: the renaming statement, the roster statement and the marked start roster, the made-knot statement under COPY-LAW(t) (the fold study's name for (FLOOR1, t, RELEASE), not a law of copying) without a taking rule, and
that nothing of the classes is left from both under MET with COPY-LAW(t).

## In standard terms

In the literature's words, not the program's: the system of P, "In standard terms", without the taking step, so that
each new hyperedge attaches only to degree-one vertices of its parents. The reading asks for a reaction X + Y → 2Y′, with
each Y′ the same as Y on h, k and the inclusion-maximal met sets of its members, and every member of each Y′ derived from
both inputs.

## Prior work in the program

Searches, each with `--until 2026-11-25 --exclude MADE-COPIER-20261125-001`:

`python3 -B scripts/track.py objects "two patterns joined and used up together, two parts the same as the second made by their joint births" --until 2026-11-25 --exclude MADE-COPIER-20261125-001`

`python3 -B scripts/track.py objects "a part that copies itself only when it meets another part, an input used up" --until 2026-11-25 --exclude MADE-COPIER-20261125-001`

`python3 -B scripts/track.py objects "renaming invariance of a round with no taking rule, which loose distinction goes to which birth" --until 2026-11-25 --exclude MADE-COPIER-20261125-001`

(The search strings are as run, version 1's words included.) What they return (run read-only by the drafter on
2026-11-24), the top rows, in order:
- First search: `PARTS-MEET-AGAIN-20261124-001/2` (one part's course differing with another part barred; "none depends
  on what the other part is"); `COPYING-PARTS-20261123-001/2` (the knot test while small parts copy themselves);
  `EARLIER-EVENT-AND-LATER-BIRTH-20261122-001/1` (a relative, not used); `PARTS-MEET-AGAIN-20261124-001/1`;
  `RING-IN-BALANCE-20261123-001/4`; `SERIAL-REPAIRS-20261120-001/1`, `TWO-CHOICE-IMPLICATIONS-20261115-001/1`
  (unrelated).
- Second search: **`COPYING-PARTS-20261123-001/3`, used**: of the record's census of 3,344 starts of up to five knots
  with single meetings, each counted once up to isomorphism, 93, 97 and 85 percent come to hold a part that copies
  itself by round 10 under FLOOR1 with retiring, offshoots and waiting (lower bounds;
  `research/COPYING-PARTS-20261123-001A/results.md` lines 66–74); `RING-IN-BALANCE-20261123-001/2` (a two-member part
  returns with a copy of itself every two rounds); `PARTS-MEET-AGAIN-20261124-001/1`, `/2`; the rest unrelated.
- Third search: `SETTING-AS-REREAD-20261123-001/1`, `PARTS-MEET-AGAIN-20261124-001/1`; **`REVIEW-LEADS-20261123-001/6`,
  used**: "an allocation changes no birth and no count of words and is a renaming"
  (`research/REVIEW-LEADS-20261123-001E/result.md`, checks R3 and R4; the correction of 2026-11-23 in
  `docs/CORRECTIONS.md`, "Which loose distinction a knot pays is a renaming, not a setting"; and its correction "a
  newborn's parity sign is a renaming only until a later birth takes its fresh distinction", the reason the renaming
  of "Settled by construction" is carried through every later knot); `REVIEW-LEADS-20261123-001/5`; `ONE-PARENT-REREAD-20261123-001/1`;
  `PARENTS-FROM-HOLDERS-20261124-001/2` (not used); `REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001/1`.
The epics of the rows in the top three of each search: `COPYING-PARTS-20261123-001`,
`EARLIER-EVENT-AND-LATER-BIRTH-20261122-001`, `PARTS-MEET-AGAIN-20261124-001`, `REVIEW-LEADS-20261123-001`,
`RING-IN-BALANCE-20261123-001`, `SETTING-AS-REREAD-20261123-001`.

- **Used, found by reading** the record the shared definitions cite: the ring study's settled statements
  (`research/RING-IN-BALANCE-20261123-001A/preregistration.md` lines 93–105): "The roster is enough", "Parts act alone
  past the start (under RELEASE)", and that under parity a set of loose distinctions is constrained only when it is all
  of them and every knot that receives a fresh distinction passes the knot test. Ticket B's roster statement is the
  first with descent marks added.

## Prior work outside the program

Each from memory, the literature's, not checked, and not leaned on:
- **Interaction nets** (Lafont, 1990) and **interaction combinators** (Lafont, 1997): when two cells meet at their
  principal ports, a rule of the system replaces both. Two cells of one kind annihilate; a duplicator meeting a
  constructor commutes with it: two constructors and two duplicators are left, each new constructor linked to both new
  duplicators. But there a rule for each pair of cell kinds is part of the system's law, which the owner's premise
  excludes; here the law is one rule for every knot, and X and Y are parts it grows.
- **Sharing graphs with indexed fans** (Lamping, 1990): fans of one index annihilate, of different indices commute and
  duplicate; the same remark.
- **Autocatalysis** in chemistry, A + B → 2B, with B the one that increases: CB-1 is this reading, Y increased on X.
  Condition (c) is what separates "X leaves two of what it meets" (CB-2) from "Y increases on X" (CB-1).

What this would add: whether, under a uniform growth law in which every piece passes the canonical knot test, a part
whose members are marked first and second leaves two of the second's form, each descended from both, with fewer than
two without either pattern; and how much of that is the law's own making of the same forms.

## Known before the runs (disclosed)

The drafter's scratch prototype (in its scratch folder: `b_common.py`, `b_census.py`, `b_anyform.py`, `b_invariance.py`,
`b_invariance_quick.py`, `b2_checks.py`, `b2_recount.py`, `b2_ended.py`, `b2_class.py`, with ticket A's `v2_common.py`;
unreviewed; not the study's engine). "Seen" means seen in the prototype; counts are computed and bounded. **Version 1's
counts were on nine base laws, three of them repeats (F1, Settled 2); every count here is on the six.** Version 1's
"162" swap runs was also an addition error: the nine-law count was 186, which is 93 on six laws. The scratch census was
run to 6 rounds; the registered bound is 8, and 10 under CAP-3.

**Ticket A's runs re-read** (P's run 2 in the prototype, `out/v2_main.jsonl`, 1,584 runs, MET and STEPS-1 under
COPY-LAW(t), CAP-3(t) and FBP(t)): parts the same as the run's own Y descend from X only (86 pairs of a run and a round)
or Y only (150), **never from both and never mixed**.

**Arm 1** (3,072 runs: eight kinds of X × eight of Y over the start's meetings W1 to W4, six laws, both knot laws, 6 rounds; 1,728 of
them with D's six kinds and 1,344 with pairs-3 or pairs-4; no run stopped; no knot failed):
- **Two parts the same as Y, each descended from both**, X other than Y: 36 runs, all under COPY-LAW: Y the two-knot part
  (28: offshoots 24, retiring 2, waiting 2) or one-2 (8, offshoots). (a) and (b) fail in every one; (d) in 28; (c) in all
  36. CB-1 holds in none.
- At the first round with such two parts: exactly two in all 36; no other part in 2; the knots descended from Y only had
  all ended in 14 (each by giving its usable loose distinctions to births: none barred, none closed); the knots descended
  from X only had ended in 6; X returned (from X only) in none; a part of X's form descended from both was left in 6.
- **Under CAP-3**: no such case; parts of Y's form of mixed descent in 44 pairs of a run and a round (waiting 36,
  retiring 4, offshoots 4).
- **Every form left twice from both** (1,728 runs with D's six kinds): under COPY-LAW the two-knot part (220 runs), a
  join holding one joinable with each of two members holding two (the two-knot part one round on; 174), a lone member
  holding two (58); under CAP-3, three to six members in consecutive pairs (20, 18, 18 and 12 runs), only in the
  controls (X and Y of one kind), each part gaining a member a round.
- **(a) against (b)**, per round, on all 3,072 runs: equal in every run under W1 to W3; under W4 equal except for Y of
  pairs-3 (48 runs) or pairs-4 (16).
- **Version 1's swaps**, on six laws (3,024 runs: the last member used; HOLD): 93 runs with two parts of Y's form each
  descended from both, the same two forms under COPY-LAW; (a) and (b) fail in every one. For every kind but two-23 the
  last member is carried to the first by a renaming of the start roster onto itself (DB 2.3), so that swap tested little;
  the other-member swap is registered instead, not run by the drafter.

**The undecided case** (Y = one-2 under COPY-LAW(CANCEL-RETIRE); eight kinds of X × W1 to W4 × both knot laws, 8 rounds;
64 runs): never two parts of one-2's form descended from both; one such part in 6 runs (X two-22 under W2 and W4,
not-all-equal, round 3; X two-23 under W2 and W4, both knot laws, round 2). Followed birth by birth (X two-23, W2): at
round 1 three joins, two of them first joint births, and an offshoot; at round 2 the three joins, each holding one, are
one group of three, cancelled because two of them are short (they retire); the third (of X's first member and Y's
member), not short, makes one offshoot holding two: a lone member holding two, descended from both; at round 3 it makes
two offshoots, a two-knot part. Under retiring the two-knot part, returning every two rounds, never leaves a lone
member. In these runs each such part came from a member holding one, made by a join: under X two-22 one in no group (the
join of three parents of version 1's worked case), under X two-23 one whose one group was cancelled because a partner was
short; under RELEASE either makes one offshoot.

**Version 1's worked case, to round 8** (X one-2, Y the two-knot part, W3, COPY-LAW(CANCEL-RETIRE)): its round-0
roster is three-222's (rosters_b.json). Under not-all-equal it gives, at rounds 4, 6 and 8, 1, 2 and 4 two-knot parts,
every member descended from both, and three-222 alone gives the same counts round by round; under parity run A's round-2
join of three parents takes every loose distinction there is, closes, and nothing is left, while three-222 alone (e
barred) cannot close.

**The checks of the settled statements** (`b2_checks.py`; 8 rounds, 10 under CAP-3):
- **F1** (Settled 2): COPY-LAW(t) against FBP(t), no taking rule, the 256 starts, three treatments, both knot laws: 1,536
  pairs of runs, identical at every round, structure for structure.
- **The roster statement** (Settled 3): 55,244 steps from a round to the next over the 256 starts, six laws, both knot
  laws, RELEASE and HOLD; 27,734 distinct (law, closing or not, marked roster before); every one of the 27,510 repeats
  gives the same marked roster after; no conflict; 174 steps close (parity).
- **The marked start roster** (Settled 3): the 256 starts give 78 round-0 rosters and 189 marked rosters (rosters_b.json);
  29 have the roster of an alone start of a kind (two-23 8, pairs-4 5, two-22 4, pairs-3 4, three-222 4, two-33 4); in all
  636 classes of starts that share a marked roster, a law and a knot law, the per-round readings agree.
- **The knot laws** (Settled 7): 1,536 pairs of runs, identical up to the first closing in every one; 87 parity runs close
  (COPY-LAW 12, CAP-3 75).
- **Renaming** (Settled 1; `b_invariance.py`): 5,184 renamed runs on version 1's nine laws (3,456 distinct, F1), 36,288
  rounds compared: none differs, 35,632 by exact isomorphism of the labelled incidence and 656 **not refuted** (compared by
  hash only, more than 400 elements). The two further renamings (two usable loose distinctions of one member exchanged; the
  order of the knots reversed, which changes the order of groups): 864 renamed runs, 6,048 rounds, all exact, none
  differs. The control under MET (OLDEST and NEWEST, COPY-LAW(t) and CAP-3(t)): 1,860 of 3,456 renamed runs differ (a
  different hash is a different structure).

**The per-law class** (`b2_class.py`), fixed from those alone runs: 10, 10 and 12 forms under COPY-LAW with retiring,
offshoots and waiting; 12, 12 and 13 under CAP-3; each built by DB 5.1's rule and checked to have that form
(starts_b.json, "per-law class").

**Arm 2** (`b_census.py MET`: the 144 starts of D's six kinds under MET with COPY-LAW(t) and CAP-3(t), four rules, both
knot laws, 6 rounds: 6,912 runs): **no two parts of Y's form descended from both** in any run. The
starts under MET with FBP(t) were not run by the drafter; ticket A's runs under MET with FBP(t), re-read in this disclosure, have none.

**Not run by the drafter:** the registered bounds (8 and 10 rounds) on the census; the other-member swap; the per-law
class's runs; the reading of PB13; arm 2 with FBP(t) on the starts of DB 2; built structure and values (not read in
ticket B). **Left out:** a search of the record's runs for made parts the same as a start roster of DB 2 (it would say
whether any meeting of arm 1 is ever made); the record keeps its runs' rosters only inside each study's engine, so the
search would need every one of those engines rerun, which is a study of its own.

## Settled by construction (stated, not tested)

1. **The renaming statement (DB 7).** Let the law have no taking rule (DB 1.1, RELEASE or HOLD, either knot law), S a
   start and σ a renaming of its knots and distinctions. By induction on rounds there is, after each round t, a renaming
   σ_t of S_t onto the structure grown from σ(S) that agrees with σ on the start's knots and on the distinctions shared or
   barred at the start, and on each member's usable loose distinctions up to a permutation of them. The step: a round uses
   names at two steps only. (i) **The order of births and names** (FD 2.1): it names new knots and fresh distinctions and
   fixes nothing about which births are made; groups, owing, shortness, treatments, offshoots, demand (CAP-3's count among
   the knots made together, read on the roster of new and kept members) and the fresh count are read from h, k, met sets
   and counts, so σ_t carries each onto its counterpart; a join of three or more parents is one per group, named by its
   parent set. (ii) **Which of a member's usable loose distinctions goes to which of its births**, and under HOLD which it
   keeps (the number kept is the number of its cancelled groups): those distinctions are held by the member alone and are
   not barred, so any permutation of them is a renaming of the structure that fixes every knot; under parity it maps the
   row space onto itself, under not-all-equal each knot's condition onto itself, so the IMPLIED test (against the
   structure before the round, so the order of births does not enter) and the knot test are carried along; a member's
   offshoots are exchanged with each other, with equal demand. Compose σ_t with that permutation, map new knots to births
   of the same kind and parents, and fresh distinctions in order: that is σ_{t+1}. The bounds on rounds and knots and the
   guard are counts. Version 1 said σ_t agrees with σ on all the start's distinctions; that is false (DB 7 gives the
   counterexample), and no reading of ticket B depends on it. With a taking rule the step fails: the candidates of a take
   are shared distinctions, not interchangeable, and every stated rule picks among them by name.
2. **F1: one law.** With no taking rule every birth's inputs are one usable loose distinction from each parent, so its
   number of distinct inputs is its number of parents, and FBP(t) and COPY-LAW(t) give the same fresh count to every birth
   (FD 2.7). Arm 1 has six base laws.
3. **The roster statement, and the marked start roster.** Its hypotheses: no taking rule and RELEASE; every new knot
   receives a fresh distinction unless it closes (COPY-LAW and CAP-3 both give at least one); no extras (FILLERS,
   NO-OFFSHOOT). The record states the unmarked form for its own laws (the ring study's "The roster is enough", lines
   93–94); it is proved here for the six. (i) Every step of a round reads only h, k and the inclusion-maximal met sets of
   the roster; (ii) a new knot holds one usable loose distinction of each parent and its fresh distinctions, so it meets
   only its parents; every parent that made a birth has given every usable loose distinction and is no longer a member; a
   member that retired is barred and is no longer a member; a waiting member made nothing and keeps its places; so no
   member meets a member (true at round 0 for every start of DB 2,
   whose members share only with dead knots), and the maximal met sets after the round are the sets of one parent's
   children (two or more) and the restrictions to the waiting members of the old maximal met sets (the restriction of a
   met set lies in that of a maximal one containing it); (iii) a new knot's mark is the union of its parents' marks.
   **So the marked roster after a round is, up to the same, a function of the marked roster before it** under
   not-all-equal, and **under parity a function of the marked roster before it and of whether the round closes; a round
   that closes leaves no member** in its connected structure (in a start of DB 2, none at all). A closing (with at most two
   holders, which no rule of arm 1 exceeds: a birth that takes every loose distinction of its connected structure, none
   barred there; FD 2.8) also reads the barred distinctions of knots that are not members; from a start of DB 2 under
   RELEASE a round closes exactly when its roster is one member holding one, or one kept group whose every member holds
   one, and no member has retired before. Under HOLD a member that keeps
   distinctions after making births meets its offshoots, so the roster is not past its start; the statement is checked
   there (run B5), not argued. **The marked start roster**: a start of DB 2 is one connected structure with no barred
   distinction, and barred distinctions are then made only by retiring, a roster event; so whether a birth takes every
   loose distinction there is, none barred, is read from the roster's history. By induction, two starts of DB 2 with the
   same marked round-0 roster give marked rosters that are the same after every round, under both knot laws: **a start of
   arm 1 is one start roster with its members marked first or second, and its run is that roster's run.** An alone start
   with the same roster gives the same rosters under not-all-equal, and under parity up to run A's first closing (an alone
   start never closes: its e is barred).
4. **The made-knot statement under COPY-LAW without a taking rule** (RELEASE or HOLD). f = max(3 − p, 1): an offshoot receives two and a
   join one. A birth takes only loose distinctions of its parents, which are shared once it is made, and h never
   increases (FD 1.1). So every knot made after round 0 holds at most two loose distinctions, and one that holds two is an
   offshoot that has given none of them; it meets no knot but its parent (its one input is held by its parent and itself
   only, and no later birth takes anything but its own parents' loose distinctions). So a part whose members are all made
   and all hold two lies in one met set, its common parent's. Hence no part the same as one-3, two-23, two-33, pairs-3 or
   pairs-4 has every member made after round 0; three or more members holding two in one met set are offshoots of a
   parent that held three, a start knot, and descend from one pattern only. Of the class only one-2 and two-22 can be left
   from both; **CB-2 fails under COPY-LAW for every X and start's meeting** (at least five members other than the control are
   excluded), and CB-1 fails for the six other members.
5. **MET with COPY-LAW** (from P's S4). Every knot made by a birth other than an offshoot of a start knot receives one
   fresh distinction and holds at most one loose distinction; an offshoot of a start knot has one parent, a start knot,
   and descends from one pattern only. Every member of a class form holds two or more loose distinctions. So no part the
   same as a member of the classes is descended from both: CB-1 and CB-2 fail there.
6. **(a) is (b) under W1 to W3** (from 3). With X barred after round 0, X's members are no longer members, so the start's
   common knot of X and Y (W1) and X's first dead knot (W2) meet one member of Y, and Y's first dead knot (W3) meets Y's
   members as in Y alone: B_X's round-0 roster is Y alone's. Neither can close under parity (X's barred distinctions lie in
   B_X's connected structure; e is barred in Y alone). So the counts of parts of Y's form agree at every round. Under W4
   the new dead knot keeps all of Y's members in one met set, and B_X's roster differs from Y alone's exactly when Y's
   members are not already in one maximal met set: Y of pairs-3 or pairs-4. Likewise (d) and B(i).
7. **The knot laws agree until a closing** (SD lines 63–66; FD 2.8). With no taking rule only the IMPLIED closing reads the
   knot law, so the runs under parity and not-all-equal are identical up to the first closing. Y alone, X alone and B_X
   never close under parity, while run A can: wherever (a), (b) and (d) are read under parity, the comparison runs cannot
   close and run A can, and that is said with every case.
8. **The knot test of arm 1, under parity.** With no taking rule no distinction has more than two holders. Every knot
   that receives a fresh distinction passes and keeps passing (the ring study's settled statement, lines 102–105). A
   knot made by a closing receives nothing and holds every loose distinction of its connected structure, none barred;
   their sum is then a rule (K1, K3), and no smaller set of loose distinctions is constrained (the ring study, line 100),
   so forgetting any one of its places leaves the rest unconstrained (K2): it passes too. The start's knots are tested at
   round 0, and no knot's verdict changes afterwards: every later birth receives a fresh distinction or closes, so by D's
   S1 the allowed states on the places of a knot that exists after a round are the same at every later round, and K1 to
   K3 use only those. So under parity a knot of arm 1 can fail only as a start knot at round 0 (none does in the scratch
   runs). Under not-all-equal the verdicts are likewise fixed when a knot is made; whether every made knot passes is not
   argued here (PB18).

## What is supplied

Everything P, "What is supplied", lists for the readings used, and here: the eight kinds as parts and their labels; the
shared distinction e between the two first dead knots; the start's meeting and the member it uses; the class, the list of first
patterns and the per-law class; the conditions; the bounds. **In arm 1 the meeting is supplied in every case**, and a
start of arm 1 is a start roster with marks.

## What a result would and would not show

- **The expected result, arm 1**: under COPY-LAW, two parts of Y's form each descended from both are left only when that
  form is the two-knot part or a lone member holding two, by argument; whenever they are, they are also left in Y alone
  and with X barred, so CB-1 fails by census on (b), a fact about the law and Y, for those two, and by argument for the
  rest; the undecided case (one-2 under
  COPY-LAW(CANCEL-RETIRE)) is predicted to give no case. Under CAP-3 no case is predicted, and nothing is argued. With the
  renaming and roster statements this is about the law and the start rosters, not the numbering.
- **The expected result, arm 2**: no case under MET with CAP-3(t) or FBP(t); none possible under MET with COPY-LAW(t).
- **A positive** would show, in arm 1, a marked start roster under which the second pattern's form is left twice from
  both and fewer than twice without either pattern (CB-1), or a first pattern doing so for the class (CB-2); never made,
  since the meeting is supplied. In arm 2, the same with the meeting made through takes, surviving the renamings.
- **The form readings say nothing past the bounds**, and nothing about classes, start's meetings or rounds not registered; no
  sameness across second patterns is claimed without its counts.
- **The plain sentence for the owner** (the advisor's, with the recounts): "We tried it your way: the first and second
  pattern start as one part, and what is left descends from both. With no rule for taking shared distinctions, the
  outcome cannot depend on how the start is numbered; that is proved, and it is new (the record had it for one round).
  But the meeting then has to be built into the start, and a start built so is one start pattern with its members marked
  first or second. Under the ration under which the two-knot part copies itself, two parts of the second pattern's form,
  each descended from both, can be left only when that form is the two-knot part or a lone member holding two; no other
  form of our list can be left from both under that ration, by argument. In every run seen where two were left, two of
  that form were also left by the second pattern alone and with the first pattern barred, so the first pattern was not
  needed. Under the cap of three, with first and second pattern of different kinds, no two parts of the second pattern's
  form descended from both were seen, through the rounds run; nothing is argued there. Under the taking rule that lets
  parts meet, none was seen either, and under that rule with the first ration none is possible."

## Starts and files

- [starts_b.json](starts_b.json): the parts of each of the eight kinds for X (labels from 0) and Y (labels from 100), with
  first and other member; the 256 starts of W1 to W4 and the 87 of the other-member swap, each with X, Y and s = 0; X
  alone and Y alone for each kind; the per-law class (forms and parts, with their first member and first dead knot);
  the 18 renaming starts, each with its ten renamed starts written out in full (label maps and knot orders).
- [rosters_b.json](rosters_b.json): for each of the 256 starts, the class of its round-0 roster (78 classes) and of its
  marked roster (189), and the kinds whose alone start has the same roster.
- Ticket A's designs for arm 2: ticket A's starts.json, each with its own s.

## Runs

Both knot laws in every run. **Bounds**: 8 rounds, 10 under CAP-3(t); a run stops after the first round past 2,000 knots;
the fold engine's guard limits multiplied by ten (DB 3.9). Knot tests as D 8.

| Run | Starts | Laws | Readings |
| --- | --- | --- | --- |
| BG | the controls of the readings: Y alone of two-22 and of one-2; version 1's worked case | COPY-LAW(t), no taking rule | parts of Y's form per round (PB16); the worked case's births, descents and its sameness with three-222 alone (PB16) |
| B0 | ticket A's run 2 results file, from ticket A's engine | as P | DB 3.4 and 3.5 on ticket A's readings by descent (PB17) |
| B1 | the 256 starts; X alone, Y alone, B_X, B(i) for each; the per-law class with every X and start's meeting | the six base laws, no taking rule | DB 3.4 to 3.7 at every round; the round t of each case and its reports; CB-1 and CB-2 with each failure reported as by argument or by census, with the clause that failed; the reading of PB13; verdicts |
| B2 | the 87 starts of the other-member swap; the 256 under HOLD | as B1 | as B1 |
| B3 | ticket A's designs (their own s); the 256 starts | MET under CAP-3(t) and FBP(t), four rules; MET under COPY-LAW(t) as the check row | as B1; every case under every renaming registered for its design (D 4.5; for a start of DB 2, n1, n2 and n4, DB 1.2) |
| B4 | the 18 starts of the renaming check (starts_b.json, "renaming starts") | the six base laws, no taking rule, RELEASE and HOLD; MET(OLDEST) and MET(NEWEST) under COPY-LAW(t) and CAP-3(t) as the control | the structure after every round against the renamed start's, by exact isomorphism of the labelled incidence (where exact comparison does not finish, "not refuted"), for the ten renamed starts of each listed in starts_b.json (names reversed; three seeded permutations of the labels; three of the order of the knots; one of both; two usable loose distinctions of one member exchanged; the order of the knots reversed) (PB1) |
| B5 | the 256 starts | the six base laws, no taking rule, RELEASE and HOLD | F1 (PB2); the roster statement (PB3); the marked start roster against rosters_b.json (PB4); the knot laws until a closing (PB8) |

## Predictions

Marks, in words: **seen** (seen and predicted), **by hand** (a hand prediction not run), **reported**, **check** (true by
construction), **replication** (a count of the prototype that an independent engine is expected to reproduce; a miss is a
finding about the engines, not about the claim). Every failure of CB-1 or CB-2 is reported as **by argument** or **by
census**, the latter with the clause that failed (DB 4.4).

| # | Prediction | Fails when |
| --- | --- | --- |
| PB1 (check; Settled 1) | Under the six base laws with no taking rule, RELEASE and HOLD, both knot laws, every renamed start's run is, after every round, a renaming of the original run as DB 7 states (exact comparison). Under MET some renamed runs differ (replication: 1,860 of 3,456). | a renamed run under no taking rule differs |
| PB2 (check; Settled 2) | COPY-LAW(t) and FBP(t) give identical runs with no taking rule. | they differ |
| PB3 (check under RELEASE, Settled 3; seen and predicted under HOLD) | With no taking rule, the marked roster after a round is a function of the marked roster before it under not-all-equal, and of it and whether the round closes under parity; a round that closes leaves no member. | two equal marked rosters, under one law, give different next ones in a round with no closing |
| PB4 (check; Settled 3) | The round-0 roster classes of rosters_b.json (78 and 189); starts with the same marked roster give the same readings at every round under each law and knot law. | a class differs, or two such starts differ |
| PB5 (check; Settled 4) | Under COPY-LAW(t) with no taking rule no knot made after round 0 holds three loose distinctions; every made knot holding two is an offshoot meeting only its parent; no part of the form of one-3, two-23, two-33, pairs-3 or pairs-4 has every member made; three-222's form is left only from start knots. | otherwise |
| PB6 (check; Settled 5) | Under MET with COPY-LAW(t) no part of a class form is descended from both. | one is |
| PB7 (check; Settled 6) | (a) and (b) give the same counts at every round under W1 to W3, and under W4 except for Y of pairs-3 or pairs-4. | otherwise |
| PB8 (check; Settled 7) | The two knot laws give identical runs up to the first closing; the runs that close are listed (seen: 87 of 1,536 parity runs). | they differ before a closing |
| PB9 (check; Settled 4) | CB-2 fails under COPY-LAW(t) with no taking rule for every X and start's meeting, by argument. | it holds |
| PB10 (seen) | Arm 1 under COPY-LAW(t): CB-1 fails for every X, start's meeting, knot law and Y: by argument for the six members of Settled 4, by census for one-2 and two-22 (seen: 36 cases of two parts each descended from both; the clauses that failed: (b) with (a), one condition there (Settled 6), in all 36, and (d) in 28). **The undecided case**, Y = one-2 under COPY-LAW(CANCEL-RETIRE), gives no round t (seen: at most one such part, in 6 of 64 runs, 8 rounds). | a case of CB-1 |
| PB11 (seen) | Arm 1 under CAP-3(t): CB-1 and CB-2 fail, by census (seen: no two parts of Y's form each descended from both, X other than Y). | a case |
| PB12 (seen) | Arm 2, MET under CAP-3(t) and FBP(t): CB-1 and CB-2 fail, by census (seen: none on ticket A's designs, none on the starts under MET with CAP-3(t)). | a case surviving its renamings |
| PB13 (by hand) | For each X, law, start's meeting and knot law: the list, round by round, of the forms of parts descended from both with their counts, for each Y (R0); R1, the number of distinct lists across the eight Y; R2, the forms descended from both with one Y and at no round with any other Y′; R3, the first round after which run A's whole roster (unmarked) is the same as the roster of an alone run of the eight kinds or of the per-law class, under the same base law and knot law, at some round, and which. Predicted under COPY-LAW: the lists differ with Y in counts and rounds (R1 > 1 wherever two Y's runs differ at all); R2 is empty; the forms present twice are the two-knot part, a join holding one joinable with each of two members holding two, and one-2; the reason is Settled 3 with Settled 4, and it holds for this class, these start's meetings and these rounds. Under CAP-3, R1 and R2 are reported, with no prediction. | under COPY-LAW, R2 not empty or another form present twice |
| PB14 (reported) | With every case: exactly two and the other parts; how the knots descended from Y only ended (given to births, barred, closed); the knots descended from X only ended; X returns or a part of X's form descended from both is left; the first joint births; parts of Y's form of mixed descent (seen: as disclosed). | not applicable |
| PB15 (reported) | The per-law class (fixed after the scratch lists were seen): CB-1 on each of its forms as Y, with every X and start's meeting, and PB13's lists. Expected, by hand: no case. | not applicable |
| PB16 (replication) | The controls of the readings: Y alone of two-22 under COPY-LAW(t) gives, after rounds 1 to 8, 0, 2, 0, 4, 0, 8, 0, 16 (retiring), 0, 2, 1, 4, 4, 9, 12, 22 (offshoots), 0, 2, 0, 5, 0, 12, 0, 29 (waiting) parts of its form; one-2 gives 0 at every round (retiring), 0, 0, 1, 0, 2, 1, 4, 4 (offshoots), 0, 0, 0, 1, 0, 2, 0, 5 (waiting); version 1's worked case gives its listed births and, under not-all-equal, the counts of three-222 alone. | any differs |
| PB17 (replication) | B0: in ticket A's run 2 results file, no part the same as the run's own Y is descended from both or mixed. | one is |
| PB18 (check, and seen) | The knot test in arm 1: under parity no knot fails unless a start knot fails at round 0 (check, Settled 8); no start knot fails at round 0, and under not-all-equal no knot fails (seen: none in 3,072 runs). Under MET, knots fail only at joins under parity (seen). | otherwise |
| **PBA (the owner's, A248)** | As P's POA (i), on this class: CB-2 fails for every X, law and start's meeting; only the failures by census that are not on (b) alone bear on his first sentence, supporting it on this class and not proving it; "some members and not all" (DB 4.3) is reported apart; his second sentence is not read here. | a case of CB-2 |

## Runs and stop rule

- One engine is written from this text and the definitions; it passes PB1 to PB4 and PB16 before any other run.
- **Stop**, read: at a case of CB-1 or CB-2 with its three verdicts; or at a reason none can (Settled 4 for six members
  under COPY-LAW; Settled 5 for MET with COPY-LAW); or, where neither is reached (one-2 and two-22 under COPY-LAW;
  everything under CAP-3; arm 2 under CAP-3 and FBP), the bounded report of "What a result would and would not show";
  every registered run made and every prediction given a verdict.
- **Disagreements** with the disclosed prototype are replayed birth by birth; the listing decides.
- **Resources.** Each run under ten minutes and 8 GB on one process; anything longer through the shared runner.
- **Deviations** in `deviations.md` in the experiment family before the affected run.

## What the advisor's passes changed

Two passes by the advisor model on this ticket, each on the whole text as it then stood; the questions and answers are
in [the advisor folder](../MADE-COPIER-20261125-001/advisor/README.md).

- **First pass: "freeze after listed changes".** With no taking rule the two rations with the first count of fresh
  distinctions are one law, so arm 1 has six base laws; the roster statement and the marked start roster were stated,
  proved or checked and tabled, and arm 1 became a census of start rosters whose members are marked first or second; the
  renaming statement was reworded and its check made exact; the claim was split into two readings, with whole-class
  failures under the first ration reported as by argument; a condition for the first pattern alone was added; arm 2
  gained the base law where ticket A's one-fresh-distinction argument fails; the rounds were raised; a reading of what
  is left from both for each second pattern was registered. The drafter's account:
  `advisor/changes_b_after_first_pass.md`.
- **Second pass: "freeze", with sentence-level fixes**, all applied except two replacement sentences that the drafter
  showed were not true of the runs or could not be checked from the text, for which it gave the sentences that are.
  The drafter's account: `advisor/changes_b_after_second_pass.md`.

