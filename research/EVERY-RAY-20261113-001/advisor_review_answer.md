<!-- claude -p --model claude-fable-5-2 --tools "" --output-format json (modelUsage: claude-fable-5-2), 2026-11-13. All points adopted in the spec and predictions below. -->

**Verdict:** L_path is a sound one-sided object and the DP is plausible, but P3 and likely P2 are settled by construction, P1 is not blind, and "defeated/decisive" overclaims.

**Object**
- **Wrong target for "defeated".** Bounded L_path gives bounded L_any, but L_any ≤ L_true says nothing about λ_true. The first-ray copy can stay far while a different copy at the same depth is near. Say "depth is not a bond distance in this family", not that the grower is defeated.
- **Population is conditioned on the first ray.** Families with no persisting first-ray bond but a persisting bond on another path are excluded, though L_path is finite there. Include them, or at least count them.
- **Pass-through calls.** If a SELF call takes S's own ports as arguments, the depth-s copy touches the top directly and boundedness is trivial. Stratify bounded verdicts by whether the zero-mean cycle uses such a call; otherwise P1 mostly measures this.

**DP soundness**
- **Node space.** It stays valid only if the (F,G) node carries nothing tied to the call index and every interface is the same three ports. Check three cases explicitly:
  - two calls sharing an argument distinction;
  - one call receiving the same distinction on two ports;
  - a non-chosen SELF call read as the same fixed-point port relation the census used.
- **Caps are asymmetric.** A truncated graph can only lose cycles, so "bounded" survives a cap and "grows" does not. Branching multiplies nodes by the number of calls, so cap-outs will concentrate where boundedness is likeliest. Record capped families as undecided, by self-call count, and never as growers.

**Predictions**
- **P3** is settled by construction, since the min includes the first ray. Move it to the gates.
- **P2** is probably settled too. Duplicate calls, or calls related by a port symmetry of S, give L_path = L_ray. Restate it as a grower whose calls are inequivalent under S's symmetries, and report the fraction.
- **P1** is not blind. You already have 131/224 (58%) on one alternative ray, and L_path can only do better, so "majority" is nearly foregone. A79 weight also sits on small families, which is the stratum you have already seen. State a point estimate with a failure threshold (for example at least 75% by count), and evaluate it outside the 224.
- **Add one.** Report how many bounded verdicts need a mixed path rather than a fixed-index ray. That is the only place this design goes beyond the earlier stress test.

**Gates**
- The one-self-call gate is a regression check on the same code path. Keep it, but do not count it as validation.
- The last-call gate tests something only if those values come from the earlier stress-test code, not from this DP.
- The brute force must not reuse the ray step. Flatten the unfolding and check member sets with `knotlab check`, even if only to s ≈ 4. Otherwise it tests the min and not the varied-continuation step.
- Depth 8 cannot tell bounded from late-entered growth. Set panel depth per family to at least preperiod plus period of its Karp graph.

**Wording**
- "Decisive" should read "decisive for L_any only".
- The growth reading is correctly hedged; add "and uncapped".