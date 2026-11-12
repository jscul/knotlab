# The audit: learning against blind search

Status: Proved (the blind baselines exact; the comparison over recorded runs). `audit.py`, ticket A of
`research/SEARCH-AUDIT-20261112-001/preregistration.md`, frozen with the code in commit `06d0f2a5f` before any comparison. A first full run
reached its 50-minute cap and wrote nothing; the code was then changed only to read each class's maps with one solver and to write each
family as it finishes (the parity family's three cases had been computed once in a foreground test of that function). The rerun finished
in 21 minutes of computation. `pooled.py` adds, after the run, the pooled view below.

## The test

For each case, the classes (or laws) the learner can rest at, and the chance p that one uniform draw of a signing at rest gives the
target, counting the interface's own flips. Blind search needs a geometric number of probes (median the least n with 1 − (1 − p)^n ≥ 1/2).
The learner's probes to find are read from the recorded runs. Frozen readings: learning (median at most half the blind median and 3 of 4
runs within it), search, slower than search (median above twice the blind median).

## Results

| Family | Cases | Learning | Search | Slower than search |
| --- | --- | --- | --- | --- |
| Native writing of addresses | 37 | 2 | 17 | 18 |
| Gates, credit learner with the sturdier probe | 21 | 0 | 2 | 19 |
| Deeper memories | 24 | 0 | 1 | 23 |
| Parity (T1, T2) and the count of five (J2) | 3 | 0 | 0 | 3 |
| Rest-set and graded learners | 6 | 0 | 2 | 4 |
| All | 91 | 2 | 22 | 67 |

The two cases read as learning are single writes (one run each: 2 probes against a blind median of 5, and 9 against 20); blind search
itself finds that fast in about a quarter of tries, so they do not show steering.

Headline cases: parity on T1, blind median 6 probes, learner median 27; on T2, 6 and 16.5; the count of five on J2, 22 and 281; the graded
learner on one copy, 22 and 244.5.

## Pooled, after the run (`pooled.py`)

For each of the 215 runs that found its target, F = 1 − (1 − p)^n is the chance that blind search would have found it within the
learner's probes. Under blind search, F is about uniform: mean 1/2, half within the blind median. The learner: mean F 0.825, and 10.2%
within the blind median (native writing 0.753 and 17.5%; gates and deeper memories 0.927 and 2.2%; parity, the count of five and the
rest-set learners 0.838 and 7.8%).

## What it says

In every family the learner finds its target no faster than drawing laws at rest at random, and usually slower: it probes the same law
many times while it wanders. The examples decide when it stops; they do not steer where it goes. What the record calls learning is a
search over the laws the learner may rest at, stopped by the examples, and then held.
