# Advisor answer (NATIVE-SPINE, before the freeze)

## 1. Fairness of the test

**N: the verdict is right but uninformative.** Depth-2 ancestors all sit in round t − 2 and c(t) > c(t − 2), so N fails by arithmetic before any data is read. Record it as "refuted by count, not by evidence", and do not count it as one of three tested rules.

**A native reading of "newest" that is not trivially refuted:** j takes a depth-2 partner when it is forced to, meaning some depth-2 ancestor has j as its only remaining candidate. Otherwise it takes depth 3, and forced choices are propagated. This reads only ancestry and can reach round t − 3. Its ceiling is the set of edges lying in every perfect matching, which you can compute rule-free from one matching plus the strongly connected components of the alternating digraph.

**M and F have three problems as stated:**
- **Depth bias.** Chain counts at depth 3 are probably systematically larger than at depth 2. If so, M leans to round t − 3 and F to round t − 2, and both may fail by count much as N does. Freeze a per-depth or normalised variant alongside, or report the depth split of what each rule keeps.
- **Ties.** Keeping all tied ancestors means "no single partner" can reflect ties rather than a wrong rule. Report tie rates.
- **Wrong side counted.** "Single partner for j" is only half the criterion. Also report collisions (two junctions keeping the same ancestor) and uncovered ancestors.

**Non-uniqueness refutes no rule.** It only says there is something to choose. A more useful readout than unique/not-unique is the fraction of forced edges per round.

**Add a null.** With a dense relation and matching counts, a perfect matching may come cheaply. Check whether a degree-preserving shuffle of the relation also has one; if it does, the matching's existence is weak evidence for the substitution.

## 2. Prediction for all ten starts

- N fails by count at every round.
- M and F pick the spine at no recurrent round on any start.
- M's single-partner fraction keeps falling (pilot: 42% → 25%); F stays under about 12%.
- The matching is non-unique at every recurrent round.

**Risky prediction:** by round 13, M's single-partner picks collide on at least 8 of the ten starts. That would mean M is not merely incomplete but inconsistent with every perfect matching. I am unsure of this; it rests on the depth bias, which I have not seen measured.

## 3. The automorphism test

**It is sound, and your condition is the exact one.** A rule that reads only the ancestry is equivariant, so its output is fixed by every automorphism. If no perfect matching is invariant under the whole group, no native rule picks one.

**Caveats:**
- Automorphisms must preserve everything a rule may read: rounds, the multiplicities m, and any signs.
- The test is silent when the automorphism group is trivial, which may be the generic case.
- An invariant matching existing does not make a simple rule exist.

**Making it checkable without fake symmetries from the window's edge:**
- **Causal rules (reading rounds ≤ t only).** The ancestry from the start to round t is complete, so there is no edge effect. Check for a group-invariant perfect matching by choosing whole edge orbits, which is a small exact-cover or SAT problem. Twins (same parents, same m) are an immediate obstruction.
- **Rules that read the future.** Restricting an automorphism of rounds ≤ T + 1 to rounds ≤ T gives an automorphism, so the symmetry on round t can only shrink as the horizon grows. A window result therefore refutes only rules of horizon ≤ h; report it per h and never as "all rules".
- **All horizons.** Use symmetries of the start itself. Growth is deterministic and equivariant, so a start automorphism extends to every round and no window edge can fake it. If your eddy starts have such symmetries (I do not know whether they do), test whether some perfect matching is invariant under them. A junction fixed by the symmetry with no fixed candidate partner is a one-line obstruction.