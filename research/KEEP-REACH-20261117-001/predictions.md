# KEEP-REACH-20261117-001: predictions

Frozen at the commit that adds this file (its time is the freeze time), after the advisor's review (`advisor_design_answer.md`) and
before `run_census.py` and `run_sample.py` were run. Seen before freezing: the exploratory look at the four non-direct descriptions
that never forget, with two direct ones (`exploratory/look_four.json`: at stable depth, s up to 24, two-orbit bonds of 5, 4, 4 and 6
members at every s from s = 2 or 3 on); the gates (`gate_two_orbit.json`); and the classifier on a9a1c941de1a (both tiers, bounded at 4).

The advisor showed that Conjecture C ("never forgetting implies a two-orbit bond at every distance") can fail in general: a
non-product joint can hide its dependence behind one orbit's own constraint, and the parts outside the window can cut a non-rectangular
relation to a rectangle. So the test records a third class.

- **P1 (the four).** Each of the four has a two-orbit bond from level 3 at every s ≥ 1 at every depth tier, with eventual values
  4, 4, 5 and 6. Then all 46 small-orbit census descriptions that never forget are bounded at every depth, and forgetting decides
  bounded or growing on all 786.
- **P2 (no third class in fresh patterns).** In the fresh sample, drawn until 40 kept draws never forget and are alive at every depth
  (at most 200,000 draws), and among all one-slot mutations of the four, no small-orbit description that is alive at every depth and
  never forgets lacks a two-orbit bond at some s. Zero such third-class descriptions.

Consistency checks, not predictions: no two-orbit bound below a decided census value (gate c); two-orbit bounds agree with Theorem W's
ties and three-member bonds (gate b).
