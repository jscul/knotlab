# Ticket B: changes from version 2 to version 3

The advisor's last pass (`study/copier_b_advisor2/answer.md`, "A n.m") says "Freeze" with sentence-level fixes. I
checked each against the definitions and the runs before adopting it. One data file changes (`b_starts_v3.json`, for
1.3 and 1.4); `b_rosters_v2.json` does not. No new run was made beyond writing out the renamed starts and one look at
the six runs of the undecided case for 1.10.

## Section 1

- **1.1** Applied (DB 3.0). Checked: ticket A's made designs have s = 1 (D 2.2), and D 4.4 and D 4.6 define the
  replacement and alone runs there.
- **1.2** Applied (DB 1.2, run B3, claim 2): for a start of DB 2 the registered renamings are D 4.5's n1, n2 and n4 with
  `design` the start's name. D's n3 (X's labels after Y's) is not defined for these starts; n2 is, since every start of
  DB 2 holds e.
- **1.3** Applied: starts_b.json's "renaming starts" now writes out the ten renamed starts of each of the 18 starts in full
  (180), with the generator call and the seed string the prototype used; a spot check reproduces the comparison on four
  of them. "Starts and files" lists them, and run B4 points to them.
- **1.4** Applied (DB 5.1; starts_b.json gives every per-law part and every kind its first member and first dead knot).
- **1.5** Applied (DB 3.7). Checked: the scratch recount of (c) already ranged over the members other than Y and other than
  X's own kind.
- **1.6** Applied (DB 3.8).
- **1.7** Applied with a different sentence. The advisor's ("with it removed, every other knot still reaches a loose
  distinction …") rests on a cut criterion for passing that the texts do not state and that I could not check from them.
  What the texts do give is D's S1: with no taking rule every later birth receives a fresh distinction or closes, so the
  allowed states on the places of a knot that exists after a round never change, and K1 to K3 use only those. So a knot's
  verdict is fixed when it is made, the start's knots at round 0. Settled 8 and PB18 now say that under parity a knot of
  arm 1 can fail only as a start knot at round 0 (tested there; none does in the scratch runs).
- **1.8** Applied (PB3: check under RELEASE, seen and predicted under HOLD).
- **1.9** Applied (PB13 and the claim): the prediction is under COPY-LAW only; under CAP-3 R1 and R2 are reported with no
  prediction; R3's alone run is grown under the same base law and knot law.
- **1.10** **Not adopted as worded.** The replacement "In these runs each came from a join holding one that was in no
  group" is false for the X two-23 runs: there the parent, a join holding one, was in one group, the three joins of round 1
  together, which was cancelled because two of them were short. It is true for the X two-22 runs, where the parent is the
  join of three parents, alone in the roster. Version 2's own description of the X two-23 run ("in no group") was wrong in
  the same way. The sentence used: "In these runs each such part came from a member holding one, made by a join: under X
  two-22 one in no group, under X two-23 one whose one group was cancelled because a partner was short; under RELEASE
  either makes one offshoot." The claim's sentence is corrected to match.
- **1.11** Applied: the marks are now the words seen, by hand, reported, check and replication, and the table uses them.

## Section 3, the roster statement

- The three hypotheses are stated (every new knot receives a fresh distinction unless it closes; no extras; a retired
  member is no longer a member).
- The sharper sentence under parity is used, with the advisor's exact condition for a closing from a start of DB 2 under
  RELEASE (the roster is one member holding one, or one kept group whose every member holds one, with no member retired
  before). I checked it against SD's closing and FD 2.8: with no barred distinction in the connected structure, a birth
  takes every loose distinction exactly in those two cases.
- The citation now reads "the record states the unmarked form for its own laws; it is proved here for the six". The ring
  study's statement (its lines 93–99) is written for its own laws, and I could not show from its text that those include
  FLOOR1 with all three treatments.

## Section 4

- DB 2.3 now says that under W1 both members are exchanged when both kinds have one, and gives the 87 as 39 under W1, 24
  under W2 and 24 under W3. Checked against the construction that wrote the starts. These are starts; none was run.
- The knot-test argument is completed by 1.7, in the form above.

## Section 5

DB 4.4, the claim (sections 5 and 6) and PBA now report each failure by census with the clause that failed, and do not
count a failure on (b) alone as bearing on the inkling. **One step further than the advisor's sentence:** in none of the
36 cases does (b) fail literally alone. (a) fails with it, and under W1 to W3 (and under W4 for these Y) (a) is the same
condition as (b) (Settled 6). In 28 of the cases (d) also fails, and (d) is about X alone. So DB 4.4 counts a failure
whose failed clauses are only (b), (d), and (a) where it is (b) as a failure on (b) alone. Otherwise the law's own
doubling of the two-knot part would be counted as evidence about the pair.

## Section 6, the plain sentence

All four replacements made, each checked against the counts:
- in all 36 runs where two were left, (a) and (b) fail, so two of that form were also left by the second pattern alone
  and with the first barred;
- under the cap of three, "with first and second pattern of different kinds" is the disclosed count's scope;
- "under that rule with the first ration none is possible" is Settled 5.

"We tried it your way" stays: it is the advisor's ordinary sentence to the owner, not FD's "way".

## Section 7, words

Every row applied:
- "way" became "the start's meeting" (W1 to W4); FD's "way" is said to keep its meaning (DB 0);
- "the bound" became "the made-knot statement";
- "traced" became "followed birth by birth", and "the traced case" became "version 1's worked case";
- "position of the roster" became "carried to the first member by a renaming of the start roster onto itself" (or "by
  none");
- "the middle member" became "the second member listed";
- "uses names in two places only" became "at two steps only";
- "reads a start distinction by name" became "uses a start distinction's name";
- "ticket A's run 2 output" became "results file";
- "the two-knot part's cycle" became "the two-knot part, returning every two rounds,";
- "lone member" is defined in DB 0 as a member joinable with none;
- "marked by argument / by census" became "reported as";
- "above 400 elements" became "more than 400 elements".

One "(above)" pointing back in the text also became "in this disclosure".

## Not applied, and why

- 1.10's replacement sentence, which is false for half of its runs; the true sentence is used instead (above).
- 1.7's wording, replaced by the argument from S1, which the texts support.

## Files

`b_claim_v3.md`, `b_definitions_v3.md`, `b_preregistration_v3.md`, `b_starts_v3.json` (starts_b.json), `b_changes_v3.md`;
`b_rosters_v2.json` (rosters_b.json) is unchanged.
