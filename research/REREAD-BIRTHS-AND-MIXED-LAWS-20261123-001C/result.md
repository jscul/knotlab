# Does a birth that takes a shared distinction let growth finish a structure with a hidden excess?: result

Ticket `REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C` (the arm ticket B left for after ticket A; G18 with G17),
2026-11-23. Computed; scientific referee pending.
[Pre-registration](preregistration.md) · [full tables and commands](results_draft.md) ·
[deviations](../../experiments/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C-E001_reread_reach/deviations.md)

**A structure with at most two holders per distinction that sits at exactly 2 is one birth away from a hidden excess,
and the birth is one that takes a shared distinction. Rule R, which re-reads only when a knot is short, does not make
that birth: the starts it repairs are far below 2, and the starts at 2 have no short knot.** A hidden excess is a
four-correlation score above 2 with both complete records unchanged by the far setting, under the supplied setting
births and with every allowed word of the finished structure counted equally. A gain is a hidden excess at a later
stage of a start that has none.

## Arm 1: ticket B's census under rule R

Rule R (ticket A): a knot that owes more loose distinctions than it holds pays the rest with shared ones. It was run
on the starts that stall at round 1 under ordinary growth, with the oldest (O) and the newest (N) allowed shared
distinction paid, and on the two-holder starts under every allowed choice of round 1 where there were at most 64.

| | Starts with at most two holders | Starts with a distinction held three times |
| --- | ---: | ---: |
| Stalled under ordinary growth | 6,312 | 21,575 |
| Grow under R, under O or N | 6,122 | 16,793 |
| Histories tested | 146,044 | 43,150 |
| Tables tested at grown stages | 351.7 million | 52.1 million |
| Starts that gain a hidden excess | **0** | **7** |
| Largest hidden score at a grown stage | 1.692 | 127/63 |

**Two holders: nothing.** No table of any history comes within 10^-6 of 2. The 5,835 two-holder starts that do not
stall have no short knot in any round, so R is ordinary growth on them and ticket B's null stands. Every choice and
every law assignment was enumerated for 3,731 of the 6,312 starts; the rest rest partly on 62 drawn choices or 4,096
drawn assignments and are a sample.

**Three holders: seven starts gain, each through a payment.** All seven are hidden at exactly 2 before the round. The
smallest has 10 knots and 16 distinctions. Its knot even(y2,s1,k) is in two groups and holds one loose distinction, so
it pays its second birth with s1, the distinction it shares with Alice's side. The newborn takes Bob's loose y1 and s1
with one fresh distinction. Not-all-equal, it lifts the score from exactly 2 to **127/63**, hidden; changed to even
parity it leaves 2. Under convention N the same knot pays with k and nothing exceeds 2. Of the 321 tables with a gain,
261 lose it when every birth that took a shared distinction is made even parity; the other 60 come from a birth on
loose distinctions that the round could not make while it stalled.

The rate is low beside ticket B's: 7 of the 16,793 stalled three-holder starts that grow under R gain, against 34 of
7,957 that grow under ordinary growth.

## Arm 2: one added knot

For each of the 12,073 two-holder starts with no hidden excess: one not-all-equal knot on a set T of two, three or
four of its distinctions and one fresh distinction, for every T (31.4 million sets). The knot forbids nothing; it
counts an old word twice when T is not all equal in it.

- **27 starts gain**, through 1,746 sets T. All 27 are hidden at exactly 2; 24 other starts hidden at exactly 2 do
  not gain, and none of the other 12,022 starts (below 2, or not hidden) does.
- **Every T that works takes a shared distinction.** No set of loose distinctions gives a gain (0 of 2.05 million).
  Each working T holds exactly one loose distinction, always Bob's y2 or y3, and one, two or three shared ones.
- **The least T has two distinctions** (162 gains). In 108 of them one knot holds both: the birth takes that knot's
  loose distinction and one of its shared distinctions.
- **Neither rule makes any of them.** All 27 starts have one live knot holding y2 and y3, so round 1 makes two
  one-parent births under ordinary growth and under R alike, and no birth takes any working T.
- The largest score is 55/27. The smallest gain: the start nae(x1,x3,s1), even(x1,h1,h2), nae(x2,x3,s2),
  odd(x2,h1,h2) | even(y1,k1,k2), odd(s1,k1,k2), even(y1,y2,y3,s2), with the knot nae(s1,y2,f) added, gives 109/54.

## Predictions

| # | Verdict | Evidence |
| --- | --- | --- |
| G | Passed | With no short knot the engine gives ticket B's stages and counts on 500 of 500 drawn two-holder starts (and on 500 of 500 three-holder ones); tables agree with word-by-word enumeration on 100 drawn stages and 200 drawn pairs of start and T; allowed observer words never change; the ten known starts reproduce |
| P1 | Held, in what was tested | No two-holder start gains under R; part of the null is a sample |
| P2 | Held | 7 stalled three-holder starts gain through a payment |
| P3 | Held | No T of loose distinctions gives a gain |
| P4 | Held | 808 of the 1,746 gains have a T of two or three distinctions, not the shape seen before the freeze |

**The thread's own check** (separate code; only the recorded scorer and the recorded group rule are shared). Arm 2:
a separate census of every T on 425 starts (400 drawn, the ten known, and every other start with a gain) gives the
same gains and scores as the study on all 425. Arm 1: round 1 replayed on all 6,312 two-holder starts under both
conventions gives the same births, short knots and residual stalls; the round-1 births of every written gain table
(214) equal the replay; 24 gain tables on stages of at most 24 distinctions were enumerated word by word, with the same
score, table and through-a-payment verdict. The counts by class were recounted from the per-start records. The
reading that the 27 starts are 27 of the 51 at exactly 2 is the thread's, made after the results.

## What this is about

About parts of the census's structures, with these supplied: the observers and the setting births; the equal weighting
of finished words; rule R and its conventions; the law of each newborn; and arm 2's knot, which is a knot added by
hand and no growth. The gain in the smallest case of arm 1 appears under one convention and not the other, so it is
about that choice as well. Three-holder starts were grown under the two conventions only.

**Verdict.** The move that gives a hidden excess is now exact for these structures: one not-all-equal birth that takes
a loose distinction together with a shared one, where the structure already sits at 2. Rule R makes such a birth only
by accident of a shortage, and did so in seven starts that ordinary growth could not have made. A law that re-reads
where nothing is short is the missing piece: for example a one-parent birth that takes a shared distinction of its
parent in place of one of its fresh ones.
