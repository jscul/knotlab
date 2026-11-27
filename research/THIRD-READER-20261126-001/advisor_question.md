You are consulted read-only from the repository root. Read docs/ADVISOR_HIVEMIND.md first (your entries of today on the
change-read study are there). Attack the design and the argument before I freeze; counterexamples and checks.

Epic THIRD-READER-20261126-001 (research/THIRD-READER-20261126-001/). The coordinator's go-ahead: make the middle of the
joined-ring starts a third reader with two settings, to remove the sorting of VALUE-CHANGE-20261126-001's square. Read
tripartite.py (not run on the families; only a check that the named change is allowed) and real_paradox.py (run: with
real reads only and two settings per reader, no three-reader game of certainty on one or two copies of the shared
triple, 0 of 46,656 setting choices on two copies; with quarter-turn reads, one copy gives Mermin's game).

My argument (attack it): for any readers R1..Rk no two of which share a knot, with everything else unread, the coherent
counting state on their union is a mixture of products: an allowed change supported on the union splits into one
allowed change per reader (each knot meets at most one reader), so every certainty's change part is local; each
reader's parts of the certainties then commute among themselves (x_i . z = 0 for x_i an allowed change and z a law), so
the state is diagonal in a product of local bases. So no table above any classical bound exists for mutually separated
readers, whatever they read, unless a reader in contact conditions it (the sorting) or takes part. The middle reader of
tripartite.py shares knots with both ring readers; its three-reader game would then be among readers in contact.

Predictions I intend to freeze (tripartite.py 2, the five families of VALUE-CHANGE's rings.py, rounds 0-2):
1. g (shared triples, Bravyi-Fattal-Gottesman count) = 1 for every pair of rings with the middle the rest, in every
   family without a loose chain, at every round; 0 for the loose chain's pair; the three ways of computing g agree.
2. Rings 0 and 2 together, ring 1, middle the rest: g = 2.
3. The named game at round 0 of the three detour families: win 1 against 3/4, probabilities nonnegative, no reader or
   pair of readers sees another's setting.
4. (Already computed.) Real reads only: no game of certainty with two settings per reader on one or two triples.

Questions:
1. Is the separability argument right for k readers? Counterexample? Is it known (cite once)?
2. Is a three-reader game whose third reader shares knots with both others a fair test of anything beyond
   contextuality? What classical bound applies when the middle may be in contact (a model in which a reader's answer may
   depend on the settings of readers it shares a knot with)? Compute or bound that model's value for Mermin's game.
3. Is g the right count, and is my formula g = E(X) - e(X,Y) - e(X,Z) right for pure tripartite stabiliser states?
4. real_paradox.py: is the search right (signs, Hermitian phases, two settings), and is "no real game of certainty on
   triples" known (rebits; Mermin's argument needs i)? With three settings per reader, or with a reader holding pairs
   as well as triples, could a real game exist? Cheapest check?
5. Predictions: which are entailed, which wrong? What would a referee press first?
