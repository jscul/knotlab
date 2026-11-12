# Referee job LOOP-LOCK-R1: the brief

The coordinator handed this job over on 2026-11-12 at 09:53 UTC. It covers `LOOP-LOCK-20261112-001`, closed with its referee
pending. The relevant commits are 7de271937 (epic), e8e45fc21 (documents) and 9e5e46a20 (bounded against every size). The owner's
next step does not depend on the verdict.

## Claims

**Proved:**
- L1: a closed chain of k knots locks exactly when k is below the girth.
- L2: an open chain is free at every length exactly when the step relation has a step.
- L3: for one-orbit harmonies, the girth is a zero-sum length.
- The overlap rules (the advisor's):
  - figure eights lock independently;
  - a theta locks exactly when g > max(1 + b₁, b₂), never collectively;
  - a crossed pair and a circulant can lock collectively.

**Computed:**
- L1 and L2 on 495 cells each;
- the girths;
- figure eights and thetas on 75 cells each;
- the crossed pair and the circulants;
- rings frozen to 12, plus pair-transfer closed walks to 60 after the run: residue classes for some harmonies, finitely many lengths
  for others.

## The coordinator's questions

1. Is ring locking in residue classes provable for every n? What does "locks" mean on a ring?
2. Is collective locking real, or a relabelled shorter loop?
3. Is ring locking just the harmony's own periodicity restated?
4. Which parts are frozen and which are after the run?
