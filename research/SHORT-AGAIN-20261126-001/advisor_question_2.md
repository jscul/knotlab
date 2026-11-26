# The question to the advisor (26 November 2026), before the ring-line and jam studies were run

I would like a colleague's analysis of two small computational studies before I freeze their predictions. Please be
skeptical: say what a result would and would not show, and where a design could mislead.

THE SYSTEM. A structure is a set of knots; each knot holds a list of distinctions; a distinction held by one knot is
loose (usable unless barred), held by two or more is shared. Growth goes in rounds. In a round:
- Members are the knots with at least one usable loose distinction; h(u) is that number.
- Groups: for each knot w, its met set is the set of members sharing a distinction with w; the inclusion-maximal met
  sets (and maximal cliques of the "joinable" relation they induce) are the groups. owe(u) = number of groups holding u.
- u is SHORT when owe(u) > h(u). A group with a short member is cancelled; the others are kept and each makes one
  new knot (a join) holding one loose distinction from each of its members.
- A member that is not short spends ALL its usable loose distinctions: one on each kept join, one on a new
  single-parent knot (an offshoot) for each that is left (the "release rule"). So acting means leaving the roster.
- A short member, by the law's treatment, WAITS (keeps everything, stays a member), RETIRES (its loose distinctions
  are barred; it leaves), or makes offshoots with all it holds.
- Each new knot then receives f fresh loose distinctions, f set by a "ration" from: join or offshoot, p (number of
  distinctions it was given), and D (its demand: the number of groups it will be in next round, read on the
  structure after the births). Ordinary count: f = max(D, 3 - p, 1). Cap of three: min of that and 3. FLOOR1: max(3 -
  p, 1) ("just enough for three places"). The record's ONE-FEWER: min(q, max(3-p, 0, q-1)) with q the ordinary count.
  Two rations made by hand for the study: ONE-FEWER' = max(q - 1, 3 - p, 1) and JOIN-FEWER = q - 1 for a join (same
  floor), q for an offshoot.
- A "pattern" is a small start (a few knots); two patterns A and B are joined at their sites through d - 1 "link
  knots" by "meetings" (a spent knot of three places between two knots, each given one more loose distinction so it
  can afford the join). A knot is "A's own" if all its start ancestors are A's. A CHANGE is one more loose distinction
  added at one knot of B or of the link. A's own knots HEAR a change in the first round their births (name, fresh
  count, number of places) differ from the growth without the change.

THE PRIOR RESULT. Two copies of a seven-knot pattern ("the source") joined this way, under JOIN-FEWER or ONE-FEWER' with
waiting: a change at the other source was heard by A's own knots at round d+3..d+5 for d = 1..8, and a change at the
k-th link knot at round k+3 for every d. With retiring, or under the ordinary count, nothing beyond one step. It was
reported as "a change heard from afar along a line of waiting knots, nearer a fuse than a conversation".

WHAT I FOUND REREADING IT. Without a change, that structure makes NO knot at all after round 1: every member is short
in rounds 2..16 and waits, so nothing ever changes (the record calls a roster with members and no births "jammed").
A change lets one knot pay; it acts and leaves; its neighbours' owe falls; they act; ... and A's own knots make knots
again, later the further away the change. With the change the structure then grows explosively (4,766 knots by round
11 at d = 4). With a stub (a bare three-place knot) in place of B, A is freed too (at d = 3 under JOIN-FEWER, from
round 5). So I now read the far result as the end of a jam, not as anything about what B is.

STUDY 1 (the ring). The ring of five knots (five knots in a cycle, each sharing one distinction with each neighbour,
three loose each) returns every two rounds alone under all four waiting laws (cap of three, record's ONE-FEWER,
ONE-FEWER', JOIN-FEWER), giving off small parts. Question: put the ring at B, the source at A; does a change set at the
ring each time it returns reach A, repeatedly? Design: d = 1..8, meeting or shared-distinction join, the four laws
plus the ordinary count; returns detected as "a part of B's own knots (>= 5 members) after round s whose descendants
after round t include an isomorphic part (usable/barred counts as colours), the part not being the very same knots";
changes at each member of the returned part at each of the first six returns (else after rounds 2,4,...,12 at the
five B-own members nearest the line); "sent again": in the growth with the first heard change, a second change the
round after it was heard, compared with the once-changed growth; then a third. Trial cases: joined by a meeting the
ring no longer returns except under the cap of three at d = 1; under the cap of three A's own births are identical
with the ring and with a stub; under JOIN-FEWER at d = 3 A is jammed rounds 2-5 with the ring and 2-4 with a stub, then
makes the SAME numbers of knots in both, one round later with the ring; no change at the ring after round 2 is heard.
Predictions: (1) the ring returns only under the cap of three and not at every d; (2) under the cap A never feels the
ring; (3) under the one-fewer rations only one number passes, the round A starts making knots again; (4) the line
passes once and stops: no later change heard at d >= 2, nothing sent again.

STUDY 2 (the jam rule). Rule: under waiting, a change two or more steps from A's site is heard by A's own knots only in
a round in which A's own knots are JAMMED (A has members and every one is short and waits) in the growth without the
change or in the one with it. Test: 44 small starts (1-3 knots) plus the source, the ring and a two-knot part that
copies itself, every ordered pair (2,209), d = 3 by a meeting, laws JOIN-FEWER, ONE-FEWER', record's ONE-FEWER, cap of
three, FLOOR1, ordinary count (all waiting) and JOIN-FEWER with retiring as a control; changes at each start knot of B
and each link knot; 12 rounds or 1,500 knots. Trials: source-source as before; under FLOOR1 the source is jammed rounds
2-12 and hears NOTHING; the ring, the two-knot part and small starts that multiply are never jammed and hear nothing
from afar. Predictions: (1) no exception to the rule; (2) every far hearing ends a jam (jammed without, not with),
except perhaps at distance two; (3) jammed is not sufficient (FLOOR1), but under the one-fewer rations most jammed
receivers hear something; (4) the record's ONE-FEWER gives the same far hearings as the made ONE-FEWER', and the cap
of three carries nothing from three steps or more, so the made rations are not needed; (5) retiring: nothing far;
(6) receivers that multiply never hear from afar.

QUESTIONS.
1. Is the jam rule forced by the round's rules (could it be proved, and would that make the test empty), or is it
   a real empirical claim? If provable, sketch why; if not, where could it fail (e.g. a partial jam, the demand D of
   a new knot counting non-own groups)?
2. Is it close to vacuous in some way I have missed, e.g. is "A's own births differ" almost always accompanied by a
   jam for trivial reasons? What weaker or stronger statement would be more informative?
3. Which predictions do you expect to fail, and why? Is there a missing control?
4. Why might FLOOR1 jam but not thaw?
5. Known mechanisms: is this exactly bootstrap percolation / k-core peeling / chip-firing / a deadlock released in a
   resource-allocation graph / an excitable medium with no recovery? Which is the closest exact match, and what
   cheap identity at the smallest size would check it?
6. For a signal that can be sent again, what would the line need (in these terms) after it has passed once? Is my
   "sent again" reading a fair test?
7. Words: is "jammed", said of one pattern's own knots, an acceptable reuse of the record's word for a whole roster,
   or does it need a new word? (The program avoids words from two- or three-dimensional space, and "held" is taken:
   a knot holds distinctions.)
Please answer in under 900 words, numbered.
