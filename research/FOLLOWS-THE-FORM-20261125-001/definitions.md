# Definitions (FF)

Epic `FOLLOWS-THE-FORM-20261125-001`. Frozen with [the claim](claim.md) and
[the pre-registration](../FOLLOWS-THE-FORM-20261125-001A/preregistration.md). Items are cited as FF n.

## FF 0. Words

Glossary words (distinction, knot, loose, shared, roster, round, birth, join, offshoot) are used as in the guide's
glossary and in the definitions of `WHAT-A-BIRTH-CARRIES-20261125-001` (its `definitions_b.md`, "BD2"), which this
study takes over for the growth. A **seed** is a small set of knots written out by hand. A **chain** is a seed whose
knots are in a row, each sharing one distinction with the next. A **ring** is a chain whose last knot also shares one
distinction with its first. Two knots of a seed are **partners** when they share a distinction. Names such as `path`,
`star3` and `ring` in the data file are labels only; `star3` is a knot with three partners that share nothing among
themselves.

## FF 1. The growth

- The growth is BD2's, with no change: complete rounds, release, the rations FLOOR1 ("just enough for three places"),
  CAP-3 (the cap of three) and ORD (the ordinary count); short knots treated by CANCEL-RETIRE, CANCEL-OFFSHOOT or
  CANCEL-WAIT; the taking rule either none or the take of a sole candidate (BD2 2.1, MET-SOLE); the knot law
  not-all-equal or parity. A **law** here is (ration, treatment, take): 18 laws under each knot law.
- **The growth engine is shared**: ticket B's (`eng.py` of
  `experiments/WHAT-A-BIRTH-CARRIES-20261125-001B/...`), unchanged and read-only, pinned by hash in the contract with
  BD2. This study's program is an **independent reading on the shared engine**: the starts, the descent and every
  reading below are written afresh from this text, and the growth is cross-checked on a sample (run R0).
- **Bounds.** A run is grown for R_max rounds: 9, or 10 for the chains (FF 3). It stops after the first round that
  leaves more than 3,000 knots; that round is read. The engine's guard limits are ticket B's; a round the guard stops
  is not read. A run is **read through** the last round it completed.

## FF 2. Seeds and starts

- A seed is a list of knots, each a list of the seed's own distinction names 0, 1, 2, ... A first seed names one of
  its knots, the **site**; a second seed names one of its knots, the **held knot** (`at` in the data file).
- **The start** of a first seed F and a second seed S: F's knots first, with F's own names; then one new name, the
  **link**, equal to the number of F's names; then S's knots, each of S's names raised by the number of F's names
  plus one. The link is appended to the place list of F's site knot and of S's held knot.
- **The bare start** of F is F alone with the link appended to its site knot, where it is a loose distinction.
- **The unlinked start** of F and S is the start of F and S, except that S's held knot receives, in place of the
  link, a new name of its own (one more than the largest name in the start). The link stays loose on F's site knot.
  The two seeds then share nothing.
- **Three or more places** is counted in the start: every knot of every start and unlinked start has three or more
  places once the link, or the name that replaces it, is added. Loose counts in the seeds' names are counted in the
  seed, before the link is added.
- The seeds are in `seeds.json`, as explicit knots. Three starts written out, for checking:
  - B with `one:2`: `[[0, 1, 2, 6], [0, 3, 4, 5], [7, 8, 6]]`
  - D with `two:1,2`: `[[0, 2, 3, 8], [0, 1, 4], [1, 5, 6, 7], [9, 10, 8], [9, 11, 12]]`
  - the bare start of A: `[[0, 1, 2, 3]]`

## FF 3. Families

Four families of second seeds, in `seeds.json`: `mixed` (50), `chains` (62: every chain of one to five knots with 2 or
3 loose distinctions a knot, held at its first knot), `second` (37) and `fresh` (60). The first three were grown by
the drafter's probe. `fresh` is held out: a sample of 60, drawn with Python's `random.Random(20261125).sample`, of a
written list of 207 forms of the same kinds: every chain of one to four knots held at any knot, every knot with three
partners held at that knot or at a partner, and every ring of three or four knots, with 0 to 3 loose distinctions a
knot, one for each class under the seed's own renamings that keep the held knot, and none equal to a form of the
other three families. Fifteen first seeds, A to O: A to E and F to J were grown by the probe; K to O were not.

## FF 4. Descent

A start knot of the first seed is **of the first**; a start knot of the second seed is **of the second**. A knot made
by a birth is of the first if a parent is, and of the second if a parent is; it may be **of both**. The parents of a
birth are the knots that give it a loose distinction: one for an offshoot, two or more for a join. A knot whose
distinction a birth takes is not thereby a parent, and a take does not change descent. **The first seed's own
descent** is the knots that are of the first and not of the second.

## FF 5. What it makes

For a run read through round R, and each round t from 1 to R: the multiset, over the births of round t that are in
the first seed's own descent, of the entries

    (kind, number of parents, number of places, f, number of takes)

where kind is join or offshoot; the number of places is the length of the newborn's place list, which holds the
distinctions its parents gave it, the distinctions it took and its fresh ones; f is the number of fresh distinctions
it received; and the number of takes is the number of distinctions it took. **What the first seed's descent makes
through round R** is the sequence of these multisets for t = 1, ..., R. Nothing in it is a name.

## FF 5b. The wider record

The same, over every birth of round t that is of the first, whether or not it is also of the second, each entry with
a sixth item saying whether the birth is in the first seed's own descent. Two runs with the same wider record of
round 1 agree at every round-1 birth that has a first-seed ancestor, the joins at the link among them.

## FF 6. Studies, classes, told apart

- A **study** is one knot law, one law, one first seed and one family: its runs are the bare start and one start for
  each second seed of the family.
- **R\*** of a study is the last round that every one of its runs was read through; **L** is the last round any of
  its runs was read through.
- **Classes, at R\*.** Two runs of a study are in one class when what the first seed's descent makes through R\* is
  the same in both. The **classes among the forms** leave the bare start out. Two second seeds are **told apart** when
  they are in different classes. The same with the wider record gives the **classes by the wider record**.
- **First told apart, over the pair's own rounds.** For two second seeds a and b of a study, let r be the smaller of
  the rounds their runs were read through. If what the first seed's descent makes differs through some round up to
  r, they are *first told apart in* the least such round. Otherwise, if r = L, *never*; otherwise *not read further*.
  A pair can be first told apart in a round later than R\* and still share a class at R\*; the two are reported
  separately and each prediction says which it uses.
- **After the first round.** A pair first told apart in round 2 or later whose wider records of round 1 are the same.
- A **row** pools the studies of one taking rule (none or the take) and one treatment of short knots: three rations
  and the first seeds of the run. The distribution of R\* is reported for every row.

## FF 7. Fate

For a study with R\* of 4 or more, and each of its second seeds, let x be the numbers of births in the first seed's
own descent in rounds R\* − 2, R\* − 1 and R\*, and w the numbers of births that are of the first (own descent or of
both) in the same rounds. The first seed's line **ends** if all three of x are 0: *no births* if all three of w are 0
as well, *taken up* otherwise (every birth with a first-seed ancestor is then also of the second). Else it is
**steady** if the three of x are equal; else **grows** if they strictly increase; else **shrinks** if they strictly
decrease; else **other**. In a study with R\* below 4 the fate is **not read**. "Ends" and "grows" mean through the
rounds read.

## FF 8. Start knots in the roster

A knot is a **member** of round t's roster when it holds a usable loose distinction at the start of round t (held by
it alone and not barred). A start knot **acts in round 1 only** in a run when it is a member of no roster after
round 1.

## FF 9. Depth, on the chains

In a study of the family `chains`: a **pair at depth i** is two chains of one length whose loose counts are the same
except at the knot i steps from the held knot, where one has 2 and the other 3. A **pair of lengths n and n + 1** is a
chain of n knots and a chain of n + 1 knots whose first n loose counts are the same; the n-th knot of the longer one
therefore has one more place, the distinction it shares with the new knot, so such a pair differs at the n-th knot as
well as by the new one. For one law, pairs are pooled over the first seeds of the run; a pair is told apart as in
FF 6, at the R\* of its own study.

## FF 10. Renumbering

A renumbering of a start permutes its distinction names, shuffles the place list of every knot and shuffles the order
of its knots, keeping note of which knots are the first seed's. What the first seed's descent makes must not change.

## FF 11. The count profile

For a second seed: **the held knot** is the triple of its number of places in the start, its loose count in the seed
and its number of partners. **The second seed's births by round** is, in its run, the number of births that are of
the second and not of the first, for each round through R\*. In a study, the class is **a function of** a profile
when no two second seeds with the same profile are in different classes.

## FF 12. Supplied by hand (scaffolds)

The built starts and the choice of seeds, sites and families (A258); the take of a sole candidate (A255); the bounds
of FF 1; the readings of FF 5 and FF 5b; the thresholds in the predictions. Swapped within the study: the first seed
(fifteen), the family (four), the ration, the treatment of short knots, the taking rule (none or one), the knot law.
