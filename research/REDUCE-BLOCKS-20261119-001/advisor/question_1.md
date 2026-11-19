# Question for the advisor (REDUCE-BLOCKS-20261119-001, before the freeze)

You have no tools. Answer only from this text, say where you are unsure, and keep it short.

**Setting.** As in the merge-and-burst study you checked. The cheapest growth's round 1 works as follows.
- **Candidates:** pairs of live knots with a common neighbour (any knot).
- **Valid sets:** sets of three or more live knots that are pairwise candidates with no common neighbour.
- **Groups:** the maximal valid sets, plus the candidate pairs inside no such set.
- **Junctions:** each group makes one junction, taking one loose distinction from each member. Leftover loose distinctions become
  offshoots, one-parent junctions.
- **Fresh counts:** max(d, 3 − p, 1) fresh distinctions, or exactly d if the junction is implied. d is the junction's demand next
  round, p its parents. "Implied" is read structurally, as taking every loose distinction, which for connected presentations equals
  GF(2) implication (refereed).
- **Later rounds:** a new junction shares one distinction with each parent and holds only fresh ones otherwise (DOUBLE-IDENT Lemma
  M, step 3, refereed).

**Claim (Lemma R).** From round 1 on, the growth reads a start only through three things:
- its live knots;
- their open counts;
- the down-closure D of the family {N(w) ∩ live : w a knot}.

*Proof.*
1. "u, v are candidates" means {u, v} ∈ D. "S has a common neighbour" means S ∈ D. So valid sets, groups and offshoots are
   functions of (live, open, D).
2. After round 1 no round-0 knot is live: every loose distinction is taken. A round-1 junction's neighbours are its parents.
3. So two round-1 junctions are candidates iff they share a parent. A set has a common neighbour iff its members share a parent.
   Round 2 is therefore a function of round 1's groups. By induction, so is every later round.
4. Demand, parents and the structural implied test read only these, plus counts. ∎

**Corollary.** Let H(X) be the hub realization:
- the same live knots and open counts;
- one dead hub per maximal block of X, sharing one distinction with each of its points;
- dead connectors chaining the hubs, and holding each live knot that is in no block, so that H(X) is connected;
- extra dead-to-dead shares, so that every dead knot has three places.

No live knot touches a live knot, so H(X)'s blocks are X's maximal blocks and its D is X's. So X and H(X) grow identically from
round 1, round by round, in (parents, fresh). If H(X) lies in the proved class, the identification and the branch system read X's
future exactly. That makes MERGE-BURST's two readings proved.

**Pilot (disclosed).** The engine agrees on X and H(X), per-round (parents, fresh) from round 1, on:
- the closed explosive start (8 rounds);
- the ring of seven with a leaf (12 rounds);
- the closed start's 582-junction stage at round 14 against its 11-knot H (9 rounds, through the burst to closing).

**Plan.** Exhaustive on the touch census (every non-stalling arrangement, 6 rounds). 1,000 random starts of 6 to 10 knots within
seven places (6 rounds, junction cap). Stages 1 to 6 of the 16 explosive starts, each against its H (3 rounds, in limited children).
Prediction: equality everywhere.

**Questions.**
1. Is the proof complete? In particular:
   - Is step 2 right that no round-0 knot stays live after round 1?
   - Does the structural implied test in H(X) agree with X's, given that both are connected?
   - Does anything else read round-0 knots: relays, or the floor's "3 − p"?
2. Is H(X) right: can a connector or an extra share create a block, or change an open count?
3. What would you check first to break it?
