# Aggregate endpoint supplement: bounded exploratory search

This supplement is recorded before its search. It reuses the frozen
exploratory envelope; previous witnesses, verification files and receipt are
immutable inputs to this continuation.

Question: can admitting side-copy distinctions lower the minimum bond size
over all top ports and all own distinctions of the selected depth, rather
than only lower a particular endpoint pair?

## Coverage and stop gate

- Input order: the first 64 of the 664 genuine branching, one-definition,
  limit-only members in the accepted LIMIT-ONLY sample, sorted as before by
  own-distinction count, body-call count, filename and line.
- Depths: 1, 2, 3, 4, subject to at most 18 ray variables. Every top port and
  every own distinction of that depth is eligible; shared identities are
  retained.
- First compute the exact greatest fixed point. Unexpanded calls receive
  that relation. Never substitute free truncation for a non-full summary.
- First exclude supports of sizes two and three for **every** eligible ray
  pair, caching projection tables across pairs. A cheap ray bond of size at
  most three makes a strict 4-to-3 gap impossible at that case.
- For remaining cases, expand each one-side-copy choice at ray levels
  0 through s, in level/call order, subject to at most 21 finite-cut variables.
  Search all three-member supports containing an eligible endpoint pair.
  Direct NAE factors crossing an eligible pair are tested first; this is a
  search-order optimization, not an exclusion of other three-member supports.
- Label ray incidence with/without cycles where the greatest fixed point is
  TOP; otherwise label the raw-incidence comparison inapplicable. Keep case
  omissions and caps explicit.
- Stop at the first strict aggregate shortcut with exact cheaper-ray
  exclusions and an exact whole-pattern bond certificate, or after the stated
  bounded coverage. A four-member ray witness establishes an exact 4-to-3
  comparison when available; otherwise the honest result is ray >=4 against
  unrestricted 3. No-ray-bond requires a separate exact absence argument,
  never merely a support-size cap.

## Validation and reporting

Reconstruct a successful finite cut independently, check all allowed states
by scalar enumeration and SAT where tractable, verify every single deletion,
and call the canonical knotlab K1-K3 checker. Retain all eligible-pair
size-two/three projections, exact limit summaries, allowed-state completions,
coverage and code/input digests in separate supplement files. Do not rewrite
the earlier receipt. Check that side-expanded states project exactly to the
ray relation. Source labels at infinity remain unassessed unless separate
finite-flip witnesses are supplied.

If no gap is found, report the exact cases/caps and whether direct knots or
other three-member bonds between eligible endpoints account for the failures.
This bounded search cannot establish a global no-gap theorem or a growth law.
