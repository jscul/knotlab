You are advising on the design of a small computational study before it runs. Be concrete and critical; at most
500 words; a numbered list. Do not praise.

## The growth law

Knots hold distinctions. A distinction held by one knot only is that knot's loose distinction; a member is a knot
with a loose distinction. One round: two members are joinable when some knot shares a distinction with both; groups
are sets of joinable members. owe(u) = number of groups holding u; u is SHORT when owe(u) exceeds its loose
distinctions. A group with a short member is cancelled; each kept group makes a join (a new knot whose parents are
its members). A member that is not short gives one loose distinction to each of its joins and one to an offshoot of
its own for each left over. A short member waits (keeps its loose distinctions and stays a member), or retires, or
makes only offshoots, by the treatment. A new knot holds the p distinctions its parents gave it and f fresh ones,
f set by the RATION, which may read only: whether the knot is a join or an offshoot, p, its demand D (the number of
groups it will be in next round among this round's new knots and the waiting members), and, for an offshoot, o,
the number of joins its parent was owed. The ordinary count is f = max(D, 3 - p, 1). No law may read names,
ancestry or anything global. Nothing but its parents' gifts enters a knot.

## What is known

Two patterns A and B are joined in one start; "A's own knots" are those with only A's start knots among their
ancestors; the joint descent is the knots with both. A "mark" is one more loose distinction at one start knot of
B. Facts (computed, about 20,000 cases):
- A change reaches one of A's own knots only through a cancelled group, which needs a short knot.
- Ordinary count: a new knot is never short. A's own knots are untouched by anything in B; the joint descent hears
  a mark at one step a round; A's own knots keep making joins with the joint descent in every round.
- A cap on f (f = min(ordinary, c)), or "just enough for three places" (f = max(3 - p, 1)): knots are short all
  the time, and the joins between A's own knots and anything else stop within five rounds. No mark is first heard
  by A's own knots after round 6; with a cap, a change one step beyond B's first knot is felt and two steps is not.
- Rations where an offshoot receives by its parent's owing o (several forms), joins receiving max(3 - p, 1): joins
  between the two stop by round 2.
- With waiting, a short knot stays, its partners spend their distinctions on offshoots, and it later joins
  whatever is still waiting.

## The aim

A ration, made by hand and admitted as a scaffold, under which (i) A's own knots go on making joins with the joint
descent for as long as is read, and (ii) knots of the joint descent are short now and then, in a way that depends
on what B is, so that a mark far inside or far beyond B is first heard by A's own knots late, at a round that
grows with its distance. The test: A and B small and slow-growing, joined through a chain of d link knots,
d = 1 to 8, a mark at B; the first round A's own knots differ; 16 rounds.

## Candidates

1. ONE-FEWER (already in the record): f = min(ordinary, max(3 - p, 0, ordinary - 1)), every new knot one fewer
   than it is owed, but enough for three places.
2. ODD-FEWER: one fewer than the ordinary count when D is odd, the ordinary count when D is even (never below
   max(3 - p, 1)).
3. JOIN-FEWER: a join receives one fewer than the ordinary count (never below max(3 - p, 1)); an offshoot the
   ordinary count.
4. THIRD-FEWER: as 2 with D = 2 mod 3.

## Questions

1. Which two would you run first, and why? Is any of them certain to fail (i) or (ii) by the rules above?
2. Is there a better candidate within what a ration may read, for example one that makes a knot short by exactly
   one only when it was made by a join AND its demand exceeds its number of parents, or one using o?
3. Under waiting, a knot short by one loses ALL its groups that round. Does that make (i) hopeless for any ration
   of this family, so that the treatment (what a short knot does) is the thing to redesign instead, for example a
   short knot that cancels only as many groups as it is short by? Say which you would try first.
4. What control would show that a late first hearing is the ration's doing and not an artefact of the mark or of
   the reading (first difference in A's own births)?
