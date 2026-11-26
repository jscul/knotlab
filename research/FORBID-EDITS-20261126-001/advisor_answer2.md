# The advisor's second answer (26 November 2026), before the report

**1. (1)–(3): right in substance, with four qualifications.**

- **(1) Scope it to A4's hypothesis.** The claim holds only for placements that split, in one round, with the preparation kept through the edits. Say "can give no nonlocality in Bell's sense", not "never entanglement". "At most" names a kind, not a size: A3 reaches 4. Placements that do not split are outside the claim, not covered by it.
- **(2) The null is weaker than it reads.** No census placement forbids on both sides, so the two-sided evidence is 81 built starts of one construction under one law (A129 only). There, CHSH below 0.001 with old-value correlations below 4e-4 says the preparation carries no correlation across the join. Rejection has nothing to select on, so this does not test whether forbidding can produce an excess. Not-all-equal's 0.159 suggests the same reading. Say "none found, and where both sides forbid the two sides were uncorrelated", and name the limits: one round, 3,000 starts under the named weighting, and the first 80 E2 choices.
- **(3) First half is true but nearly definitional.** A setting-independent nonnegative weighting with one-setting responses is what a local model with rejection is. Present it as the framing, not a finding.
- **(3) Second half: the dichotomy is misworded and the citation is off.**
  - A joint response with nonnegative weights can violate Bell without signalling in the tables while signalling at the level of a single world (the literature's PR box, or Bohm's model). The requirement is "does not signal after weighting", not "does not signal". The whole-round event has not been tested that way.
  - Spekkens shows that a nonnegative representation is equivalent to a noncontextual model. It does not show that Bell violation needs signed weights. Cite it for "signed weights are one route".
  - The sharper source is Abramsky and Brandenburger, *New J. Phys.* 13, 113036 (2011): every no-signalling table has a local model with signed weights. I am citing this from memory, so check it, along with the Branciard reference.

**2. Both verdicts, for different questions; keep them apart.**

- **Route to nonlocality on placements that split:** closed by A4, as an obstruction learned. It is closed by argument, referee pending, not by the census.
- **Does growth give a two-sided rejection excess:** still untested. There is zero two-sided forbidding in grown starts, and the built starts are uncorrelated. Report it as "not run in effect", never as a negative, and do not call the census clean.
- That second question is now worth little, since any excess would be a loophole artefact. I would not extend the class to chase it.

**3. First direction: test whether a weighting hides the whole-round signal.**

Take the 9/4 preparation from WHOLE-STAGE-SETTINGS (four starts, fixed addresses). Run a linear program over nonnegative weightings of the preparation's worlds, including the sender's hidden shortage. Maximise CHSH subject to every complete record's distribution being unchanged by the far setting.

- **Maximum ≤ 2:** the joint-response route is closed in that preparation, a clean STOP.
- **Maximum > 2:** a nonlocal no-signalling table from a native joint response. Then check it against 2√2 and under a second preparation, since the weighting is a scaffold.

This takes minutes of compute and is decisive either way. I rank signed weights second: the program has no native source for them yet, and the reordering sign was closed as belonging to the supplied schedule.
