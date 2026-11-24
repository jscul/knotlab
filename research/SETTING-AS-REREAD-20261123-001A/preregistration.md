# An 11-knot structure whose two setting births the rule makes itself: pre-registration

Ticket `SETTING-AS-REREAD-20261123-001A` of epic `SETTING-AS-REREAD-20261123-001` (sub-goal B321; G18 with G17), 2026-11-23. Frozen before the study's code is written or run. Code by a Claude Opus sub-agent from this note; analysis and verdict by the thread. The canonical K1–K3 test is unchanged.

## The question

In every structure with a hidden excess so far, the two setting births were knots added by hand. Rule Q of the last epic makes a birth of exactly that form: a one-parent birth takes its parent's loose distinction and one distinction the parent shares, and the rule does not say which. Is there a structure on which one round of rule Q makes exactly the two observers' setting births, so that the setting is which shared distinction each birth takes, and the excess stays hidden? The thread built one by hand. This study checks it with an independent implementation and measures what the claim contains: what depends on the far choice, what is left when the old words' distribution is held fixed, and whether any knot can be left out.

## In standard terms

A CHSH test in which the two measurement choices are the two available outcomes of a non-deterministic step of a rewriting rule on a fixed constraint network, the statistics are uniform over the solutions of each resulting network (a local model with setting-dependent post-selection: Pearle 1970; Garg and Mermin 1987), and no-signalling is imposed on each party's four-variable record. Quantities: exact equality of record marginals, the CHSH value over all deterministic response functions, the dependence of the shared variables' distribution on each setting (measurement dependence: Hall 2011), and the value with that distribution held fixed.

## Prior work in the program

`python3 -B scripts/track.py objects "structure on which one round of a growth law makes exactly the two observers' setting births" --until 2026-11-23 --exclude SETTING-AS-REREAD-20261123-001`

`python3 -B scripts/track.py objects "setting read as which shared distinction a birth takes, hidden excess" --until 2026-11-23 --exclude SETTING-AS-REREAD-20261123-001`

`python3 -B scripts/track.py objects "CHSH with settings realised as open choices of a rewriting rule, measurement dependence of the shared variable" --until 2026-11-23 --exclude SETTING-AS-REREAD-20261123-001`

`REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001` — a relative: growth supplies weight and no tie; rule R; the census of one added knot.
`ONE-PARENT-REREAD-20261123-001` — the source of rule Q, and of an exploratory probe that found no recorded structure with both setting births as rule-Q births and a hidden excess.
`THIRD-HOLDER-20261123-001` — the source of the weighting, of the ceiling 20/9 for one birth per setting, and of the 15 recorded sides in which one observer's knot holds its loose distinction and both shared ones.

Seen before this freeze, by the thread's own exploratory checks (`research/SETTING-AS-REREAD-20261123-001/thread_checks/`): the structure below was built by hand from the seven-knot structure's two not-all-equal knots, a parity knot that copies x1, and one of the 15 recorded sides with a copy of its shared distinction. Round 1 under the thread's engine makes two one-parent births with one fresh distinction each. For options (x2, x3) against (y2, y3) each of the four stage-1 structures has 144 allowed words, both complete records are hidden and the largest score over all outcome functions is 20/9; the other eight pairs of option pairs give 19/9 or 37/18, hidden. The joint distribution of every distinction held by Bob's knots does not depend on Alice's choice; that of the distinctions held by Alice's knots does depend on Bob's. Without the copy (Bob's knot holding s1 itself) one knot meets both live knots and the rule makes one joint birth. Nothing else was run.

## Prior work outside the program

Pearle (1970) and Garg and Mermin (1987) for local models with selection; Hall (2011) for relaxed measurement independence. Not found: settings realised as the open choice of a growth rule on a constraint network. The literature was not searched beyond these.

## Settled by construction (stated, not tested)

A one-parent rule-Q birth on a loose distinction and a shared one, not-all-equal with one fresh distinction, is the knot the earlier studies added by hand, so the scores are those of the third-holder epic's weighting and cannot pass its ceiling of 20/9. With parity newborns every old word has one completion and nothing is re-weighted. Under ordinary growth the two births take no shared distinction and there is no choice to read. Rule Q with every newborn not-all-equal cannot grow this structure, which has nine parity knots.

## What is supplied

The structure, ties included; the reading of the rule's open choice as a setting, with each of the four choices a separate structure; the equal weighting of the allowed words of each stage-1 structure; the complete record; the outcome functions. Each is a scaffold and is recorded as one at close.

## Definitions (frozen)

- **The structure.** Alice: even(x1,x2,x3,c), nae(c,x2,s1), nae(c,x3,s2), even(x2,h1,h2), odd(x3,h1,h2). Bob: even(y1,y2,y3,t), even(t,m1,m2), even(s1,m1,m2), even(y2,k1,k2), odd(y3,k1,k2), odd(s2,k1,k2). Eleven knots, 16 distinctions.
- **Rule Q.** As frozen in `ONE-PARENT-REREAD-20261123-001A`, every newborn not-all-equal.
- **Options.** For each observer, the distinctions its live knot shares. An option pair is two of them.
- **Stage-1 structures.** For an option pair per observer, the four structures that round 1 of rule Q gives under the four choices.
- **Weighting.** Every allowed word of a stage-1 structure counts equally.
- **Complete record.** The observer's loose distinction, its two options and its fresh distinction. In the test with three options: the loose distinction, the three options and the fresh distinction.
- **Hidden.** For each of an observer's choices its complete record has exactly the same distribution for every far choice, in exact arithmetic.
- **Scores.** The largest four-correlation value over (i) all two-valued functions of the complete record, (ii) parities of the record's four values, (iii) all two-valued functions of the record's three old values only.
- **Checks.**
  - (a) Round 1 of rule Q on the structure by an engine written or taken independently of the thread's: the births, their parents, the options, the fresh counts and the lookahead demand.
  - (b) All nine pairs of option pairs: allowed words, hidden, the three scores.
  - (c) For the pair (x2, x3) against (y2, y3): the distribution of (s1, s2) under each of the four choices; for each observer, whether the joint distribution of every distinction held by its own knots, with its fresh one, depends on the far choice; and the three scores when the old words' distribution is held fixed at that of each one choice in turn.
  - (d) Three options each: hidden or not for all nine choices; the largest score over its two-by-two sub-tests.
  - (e) Every structure got by leaving out one knot or two knots of the eleven: whether round 1 of rule Q still makes exactly two one-parent births on x1 and y1 with at least two options each, and if so the result of (b).
  - (f) Every assignment of even or odd to the nine parity knots (512): how many give a hidden excess for the pair (x2, x3) against (y2, y3), and the scores.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Checks of the code: the engine used for (a) agrees with the recorded driver with re-reading off on the 280 funded sparse draws of the review-leads epic under not-all-equal; the recorded scorer agrees with word-by-word enumeration on score (ii) and on hiding for all nine pairs. | any fails |
| P1 | Replication: two one-parent births with one fresh distinction each; three options each; for (x2, x3) against (y2, y3) four times 144 words, hidden, score (i) exactly 20/9; the other eight pairs hidden at 19/9 or 37/18. | any differs |
| P2 | With the old words' distribution held fixed at any one choice, every score is at most 2. The distribution of (s1, s2) depends on Bob's choice and not on Alice's. | a score above 2 with the distribution fixed, or another pattern of dependence |
| P3 | With three options each the excess is hidden for all nine choices. | some complete record depends on a far choice |
| P4 | No structure with one or two knots left out meets the conditions of (e) with a hidden excess. | one does: it is reported in full |
| P5 | Score (iii) equals score (i) for the pair (x2, x3) against (y2, y3): the fresh distinction is not needed in the outcome. | score (iii) is smaller |

## Runs and stop rule

One script for the checks and one for the report. The study stops when checks (a) to (f) are done. It reports every table of (b) to (f) in full. Every run stays under ten minutes and under 12 GB. Nothing is tuned after values are seen; a changed definition is reported with both versions. Deviations go in `deviations.md` in the experiment family. Results are referee pending.

**Advisor.** Claude Fable 5.2 reviewed the claim and the design cold before this freeze (`research/SETTING-AS-REREAD-20261123-001/advisor/question.md`, `answer.json`). Its strongest objections: the birth the rule makes is the same knot that was added by hand before, so the number is the old result and the new content is only that a structure can be wired so that the rule makes exactly those two births; the hand has moved to the structure, which rule Q cannot grow; the excess may be only the setting-dependent weighting, the literature's detection loophole; the four choices are four separate structures and no one structure carries the table; a replication already enumerated is foregone, and a lower bound on size cannot rest on a census that does not contain the example. Changes: the first two points are stated above as settled; check (c) measures what depends on the far choice and what is left with the distribution fixed; all nine pairs and three kinds of outcome are reported; the census and the later rounds were dropped, and the question of size is asked only of the structure's own parts.
