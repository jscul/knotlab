**Caveat.** I don't have the definitions of stall, the relayed map or a chain, so the mechanisms below are arguments from your summary, not derivations.

## 1. Mechanism

- **Flat in-class share.** Stalling is a condition on the whole start, while (S3) and (S4) are local coincidences at the live knots. A coincidence needs a short cycle through a live knot, or three round-1 members together. At fixed places per knot the number of short cycles per start stays bounded as n grows. Once you condition on not stalling, the surviving live part should look much the same at every size, so the violation rate should be roughly constant. I am unsure of this: if the live part of a non-staller grows with n, the share should drift, and I can't say which way.
- **Why three stays rare.** Dimension R ≥ 3 needs a tree core carrying three chains. A tree of n knots with k places each has n(k−2)+2 open places, so more than one open place per knot. The sampler gives √(5/n), which is at most 1 and falling. Tree cores therefore sit in the sampler's tail, and they also need three separately fed chains.
- **What would make three common.** Starts that are tree-like around the live part, with open places per knot at or above about 1 and at least three loose distinctions on distinct branches. Dimension 1 falls for the same reason: a bare single cycle also needs about one open place per knot and nothing else attached.
- **Unsure.** This assumes the core's tree shape reflects the start's. If relaying can turn a cyclic start into a tree core, the bound weakens.

## 2. The predictions

- **Names.** Rename the predictions (P1–P7, say); S3 and S4 collide with hypotheses (S3) and (S4).
- **S3 [0.55, 0.90].** Safe but weak. The pilot's 0.65 at n = 16 rests on roughly 20–40 non-stallers, so it is consistent with a flat 0.78. Narrow the band or add "no monotone trend".
- **S4.** The 80% floor is thin at n = 5: the pilot gives 85% and SCALE-SHARE's all-grower figure is 82%. The "higher at 20 than at 5" half is safe.
- **S5.** If dimension-3 starts are nearly all in class, the in-class share is about 0.4%/0.8 = 0.5%. That leaves only a factor of two under the 1% line, and at n = 16 and 20 the line is a handful of samples.
- **S7 is the risky one.** It makes eight comparisons at 5 points each, and it tests the sampler's selection, not the theorem. It is most exposed at n = 5–8, where the shares are not saturated and the class removes the cycle-bearing starts.
- **A sharper prediction from the theorem alone.** No in-class sample has dimension above its number of independent chains, so a start with exactly two loose distinctions never has dimension 3 or more (zero exceptions). This assumes each chain needs its own loose distinction; check that against the proof.
- **A second one.** In-class samples with isomorphic relayed maps always get the same class.

## 3. Traps in the comparison

- **Selection is correlated with the outcome.** (S4) failures are short cycles, which is where dimension 1, rings and exponential growth come from. The class should therefore inflate dimension 2 and tree cores. Agreement under S7 does not show the class is representative, and disagreement does not count against the theorem.
- **Report the mix instead.** Give the cluster-rule shares for in-class and out-of-class separately, and check that their weighted mix reproduces SCALE-SHARE's figures. That is an identity, and it makes S7 interpretable.
- **Denominators.** Check that "grower" and "stall" mean the same in both readings: whether closers and exponential growers count, and whether (S0) is the cluster rule's stall.
- **(S6′) failures.** The pilot's "half (S3), half (S4)" leaves no room for them. Count them explicitly, along with the overlap of (S3) and (S4).
- **Sample size.** Metropolis samples are autocorrelated, so binomial intervals are too narrow. At n = 16 and 20 there are only a few hundred non-stallers; state counts, not just shares.
- **Independence of S2.** S2 is only evidence if the theorem's reader shares no code with the cluster rule.