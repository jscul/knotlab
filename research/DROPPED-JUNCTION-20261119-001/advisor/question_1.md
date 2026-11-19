# Advisor question 1 (DROPPED-JUNCTION-20261119-001, before the freeze)

Analysis please. You have no tools in this session, so reason only from what is written here and do not describe files or runs.

**Setting.** Under parity, a presentation in which every distinction lies in at most two junctions is a graph. Its completed
system G* adds the implied junction "out", which holds every loose distinction. The allowed states are the cycle space of G*, so
any point of G* can be the dropped one: the others are the junctions and its lines are the loose distinctions. The cheapest growth
(fewest counts) reads which distinctions are loose.

**Pilot (disclosed).** On three rings of five knots, I grew every dropped choice under parity:
- **The ring of five with one spare** (sizes 5, 4, 4, 4, 4; out has 11 lines). The original choice (drop out) grows at 1.1347.
  Dropping a ring knot makes out an 11-place junction touching every knot. The growth then closes (5, 3, 3, 1) when the knot with
  the spare is dropped, and makes 2 junctions a round otherwise.
- **Five five-place knots** (out has 15 lines). The original grows by the golden ratio; every other choice closes (5, 3, 3, 1).
- **The bare ring** (out has 10 lines). The original makes 5 a round; every other choice makes 2 a round.

In all three, the original choice is the unique point of largest degree in G*.

**Planned freeze.**
- **D1.** On every eddy (the catalogue's five entries, the census's 13 rings, rings of 9 to 13 with a spare), the original choice is
  the only exponential one.
- **D2.** On each of them, the original is the unique point of largest degree.
- **D3** (readout). On 300 random five-knot census growers: how often the original is the unique largest point, and how often
  another choice changes the growth class.
- A states-only rule would be "drop the unique point of largest degree". It is defined when G* is fixed by the states
  (three-connected, Whitney) and the largest point is unique.

## Questions

1. Is "drop the point of largest degree" a natural states-only rule here, or is there a better invariant? The degree of a point of
   G* is the size of its junction, and the states fix G* only up to twists at two-point cuts.
2. Why should every non-original choice kill the eddy? My guess: the dropped knot's lines become loose and out becomes a hub of
   high degree touching every knot, so the candidate map fills in. Is there a sharp reason, for instance that a junction touching
   all others leaves no loop of candidates?
3. Which of D1 to D3 is weakest, and what would you add?
