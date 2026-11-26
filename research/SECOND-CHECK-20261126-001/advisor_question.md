# For the advisor (26 November 2026): the second kind of check

Please read `docs/ADVISOR_HIVEMIND.md` first, then the files named. Look for counterexamples and errors; checks, not a
verdict; mark each claim's status.

Files: `research/SECOND-CHECK-20261126-001/dual.py` and `rings_dual.jsonl`; the class map it builds on,
`research/TWO-CLASS-SIGN-20261126-001/` (`classes.py`, `classes2.py`, `README.md`); the motion study
`research/READS-HOLDERS-SOURCES-20261120-001A/motion.md`.

The coordinator's question: in the literature's toric code the second check lives on the dual, where the roles are
exchanged. Here: read each move (a shortest allowed change through a distinction) as a knot holding the distinctions it
changes, the exchanged pattern. Is it lawful, does growth commute with the exchange on rings, does its constraint act as
the ring's long change? If not, would a supplied rule acting by the long change let a local reader's statistics show a
relative sign between the sectors, with free settings and no signalling?

What I found (rings of n knots, two loose distinctions each, parity, one round of ordinary growth):
- Loose values free: the exchanged pattern is not lawful (two-place pieces from loose pairs; a distinction held by up to
  eight moves).
- Loose values pinned, n = 5, 7, 8, 9, 10: it is lawful, a ring of n four-place knots, each distinction held by at most
  two; the least class-changing change has n distinctions (the old ring); at n = 5 the least class label has 3; a least
  class change is an allowed state of the exchanged pattern. n = 4 and 6 pinned have one class.
- Growth does not commute with the exchange: the bare ring's exchanged pattern (pinned) is one n-place knot holding
  exactly the old ring (the long change itself, as a check); growing it gives n + 1 knots of n places, not the grown
  ring's ring of n four-place knots.

My argument for the second step (unverified): the exchanged knots generate the moves' span H, so a weighting invariant
under them is constant on each class, and both signs between the two classes remain allowed: the relative sign is a
preparation, not a check. To show it, a reader's operation must change the class, which takes at least d_change = n
distinctions; a reader holding fewer cannot tell the two signs apart (the literature's code distance). Two readers each
holding a whole ring could each read and change their own ring's class, but a joint state of two rings with a relative
sign needs a joint operation, i.e. a contact between them, and the contact study found every contact signals.

1. Counterexamples or errors in the computation (the move rule, "lawful", the distances, the commuting test).
2. Is the "same law read on the exchanged pattern" a genuine second check here, or does lawfulness with loose values
   pinned make it a scaffold (pinning is a choice)?
3. A counterexample to the argument: a recorded operation or a small supplied rule acting by the long change under which
   a local reader's statistics depend on the relative sign, without signalling.
