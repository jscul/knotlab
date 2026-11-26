# The bench as a toy on the site

> **Referee report R1 (26 November 2026): confirmed with fixes, no block.** Read this note with the narrowings in
> [the decision](../decision.md) and [the report](../referee-R1/report.md).

Second direction of `TWO-PATTERNS-20261126-001`, at the owner's word ([request](../owner_request.md)): the
[bench](../bench/README.md) in the browser, so that he can run it.

**Where.** [prespatial.org/playground/two-patterns](https://prespatial.org/playground/two-patterns), the
playground's toy "Two patterns in one start" (labelled Further; it stands outside the lessons, with a link to
lesson 8.7 at its foot). Site repository commit `180a14b`; live from the release of 26 November 2026 (tree
`d55aa4efd9d0`).

**What it does.** Choose the first pattern (the ring of five, the two-knot part, the seven-knot source), the
second (one of the three, or a stub), how they are joined (a meeting, or a shared distinction), how far apart (one
to three steps), what a new knot receives (the ordinary count, a cap of three, just enough for three places), what
a short knot does (waits, gives up, makes offshoots), and whether the second's descent is retired by hand after
round 2, 4 or 6. It grows the joined start one round at a time, as far as 450 knots or 12 rounds, and draws every
knot: the second's own ringed in blue, the knots that descend from both in violet, short or waiting knots in
amber. Under the picture it gives, for each round, the knots made by descent, the groups that join the first's own
knots to others and how many were kept, and a sentence saying the same.

**What it leaves out.** The marks, the takes, and the comparison with a stub side by side (the stub can be chosen
as the second pattern and the counts compared by eye). It opens on two two-knot parts sharing a distinction under
the ordinary count, the bench's one case of slow joint growth.

**How it is checked.** The site grows its starts with its own engine (`src/lib/law-rounds.ts`, a port of the ring
study's engine); the bench grows them with the shared growth engine of the workspace. The site's check
(`scripts/check-two-patterns.mjs`, part of its content checks) compares the two on the toy's whole menu: the 72
joined starts label for label, and 6,229 rounds of 792 cases count for count (knots, short knots, births by
descent, own members, groups joined and kept for both patterns), with the retiring by hand on a third of the
menu. The goldens are made by `scripts/generate-two-patterns-fixtures.py` from the public record at knotlab
commit `11c7680970`, each program checked against its recorded hash. They agreed on the first run, so the toy's
counts rest on two engines written apart.

**What it showed while it was being built.** At round 6 the toy said "twelve knots descended from both" where the
bench note said two a round: the note had read the joins kept (two a round) as the knots made (2, 4, 6, … a round).
The note was corrected the same hour ([the bench](../bench/README.md), the last point of its answer).

Everything the toy lets one set is supplied by hand, and its caption says so. Its claims are the bench's: computed,
a check by the thread, referee pending.
