# Referee report GENERATORS-001-R1 (lean)

**Verdict: stands, with one point about what "on its own" means. No Block, no correction.**

## What was checked

- **The seven-knot, 25-distinction source,** regrown from its literal meetings and loose counts with the referee's own engine.
  Under both laws (parity, and not-all-equal as the same rule without the closing exception) it gives exactly the study's holdings
  at sizes 1 to 5: (7, 25), (15, 50), (27, 92), (46, 167), (78, 307).
- **The source theorem's proof was read.** It works through the identification theorem, refereed earlier: a knot is a window of the
  unrolled incidence. Every window of length 2p_k of the periodic word (A^k B) contains the repeated block with the marker, so all
  p_k phases are released together. After release a packet window's two parents are its two one-end deletions, which are again
  packet windows. The separation bound m − 2p_k + 1 follows from the interval argument. It is sound.
- **Not recomputed:** the meeting at size 17, the 15-against-18 fresh count, the timing proof and the nested source. All lie past
  where literal growth is affordable, and the study computes them through the identified map.

## What "continues on its own" and "both survive" are about

- **About the model:** the parentage. After release, every parent of every packet knot is an earlier packet knot. That is the
  program's own parent relation, not a reading.
- **About the reading** (a scaffold): which knots count as "the source", "a packet" or "a product". These are chosen by a word test
  on the full holdings, spent knots included.
- **Not claimed, and not true:** causal isolation. A packet's knots stay in one connected growing end and share parents with
  outside siblings. As the study itself notes, regrowing a packet alone with its actual loose counts changes its fresh counts at
  the very next step.
- **So "both survive" means two lineage-closed families keep growing.** It does not mean two independent objects.

## How the work was split

- **The referee:** read `source.md`, `meeting.md` and the decision note; regrew the source with its EXPLOSIVE-R1 engine
  (seconds, run directly).
- **No study code was run.**
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
