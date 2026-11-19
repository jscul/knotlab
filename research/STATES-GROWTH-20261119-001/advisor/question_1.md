# Advisor question 1 (STATES-GROWTH-20261119-001, design stage)

Analysis please; I will check it. You have no tools in this session, so please do not describe files or runs. Reason from what is
written here only.

**Setting.**
- The program's canonical reading takes a system of constraints as the set of joint states it allows.
- The cheapest growth (FRESH-COUNT-20261118-001) is defined on a presentation instead: junctions and the distinctions each holds,
  every distinction in at most two junctions. Each complete round reads which distinctions are loose (held by one junction), and
  which live junctions are candidates (they share a common neighbour). It makes one junction per group: maximal sets of pairwise
  candidates with no common neighbour for all, plus offshoots for the remaining loose distinctions. Each new junction gets the
  fewest fresh distinctions, max(d, 3 − p, 1), where d is its demand from the next round's groups and p its old distinctions. The
  only exception is an implied junction, which gets d.
- Under parity or not-all-equal, two presentations with the same allowed states can grow differently. Of 2,644 small stages
  (NAE-GROWTH-20261119-001), the share of stages that collide with a stage which joins differently is:
  - **under parity, 60%,** almost all by row operations: replacing a junction by its sum with a neighbour keeps the states;
  - **under not-all-equal, 5%,** almost all through a redundant junction, one implied by the others.

  This is assumption A108: the growth reads the presentation.
- **Precedent.** A99's states-only growth adds one distinction at a time with one to three betweenness knots, keeping every old
  state.

**The go-ahead.** Define a growth that reads only the allowed states. Check it is well defined. Compare it with the cheapest growth
where the states fix the presentation. Say what it does on the same-state pairs that split the cheapest growth.

## Questions

1. **What is the right notion.** Name two or three candidate definitions of a states-only cheapest growth, ordered by how natural
   they are. For instance:
   - (a) the cheapest growth applied to a presentation fixed by the states;
   - (b) a rule whose notions of "loose distinction", "candidate pair" and "group" are read from the states directly, through
     bonds (least non-free sets), pair disagreement counts or minimal constraints;
   - (c) the union, or the intersection, of the cheapest growths over all presentations of the current states.

   For each, say whether it is well defined and what it needs.
2. **States-only loose and candidate notions.** For a not-all-equal presentation with every junction of at least three places and
   every distinction in at most two junctions, can "loose" and "candidate pair" be read from the allowed states? Same question for
   parity.
   - Hint: under NAE, the minimal NAE constraints the states satisfy (sets S such that no state is constant on S, minimal) might
     recover the junctions when no junction is redundant.
   - Under parity, the minimal dual codewords (bonds) contain the junctions but also their sums.
3. **Canonical presentation under NAE.** Is the set of minimal NAE constraints a canonical presentation, and does it equal the
   irredundant presentation when one exists? What about a duplicate pair (two junctions on the same three distinctions), where the
   cheapest growth closes and the lone knot grows?
4. **What to test first,** cheaply and decisively, with predictions I can freeze. Which results would show that a states-only growth
   loses or keeps the eddies and rates of the catalogue (rings with spares, W = y^L (1 + y))?
