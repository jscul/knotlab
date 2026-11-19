# Question for the advisor (SCALE-THEOREM-20261119-001, before the freeze)

You have no tools. Answer only from this text, and say where you are unsure. Keep it short.

**Setting.** The identification line (four refereed proofs) shows: for the cheapest parity growth, under (S0) no stall, (S3) no
round-1 group of three, (S4) no two live knots with two common neighbours (dead knots counted), (S6′) at least two loose
distinctions, the junctions are the clusters of the relayed extended map of joins, and the growth class is read off it piece by
piece: a finished piece closes (if alone) or relays (dimension 2); a tree core with R chains has dimension R; a bare single cycle
gives dimension 1; any other cycle grows exponentially. On the five-knot touch census this class holds 81% of non-stalling starts and
matches every one.

**The study.** SCALE-SHARE sampled 8,000 starts per size n = 5, 6, 7, 8, 10, 12, 16, 20 (Metropolis over labelled descriptions,
knots of 3–5 places, any multiplicities, connected) and classified them by CLUSTER-ALL's computed cluster rule. Its refereed shares:
stalls rise 45% → 93%; among growers dimension 2 rises 82% → 98%, dimension 1 falls 17% → 2%, dimension 3 stays at most 0.4%,
rings at most 0.1%. Open places per knot fall like √(5/n). Now read the same samples (regenerated exactly) by the proved theorem.

**Pilot (one extra chain, 200–400 samples per size):** in-class share of non-stalling starts 0.82 (n = 5), 0.75 (8), 0.82 (12), 0.65
(16), 0.76 (20); the out-of-class are about half (S3) and half (S4); in the class, dimension 2 is 85% of growers at 5, 91% at 8,
all at 16, 27 of 28 at 20; the theorem's class equals the cluster rule's on every in-class sample; 15 regrown per size at 16 and 20
agree round by round.

**Draft predictions.** S1 the regenerated samples' cluster-rule classes equal SCALE-SHARE's recorded ones; S2 in the class, the
theorem's growth class equals the cluster rule's on every sample; S3 the in-class share of non-stalling starts lies in [0.55, 0.90]
at every size; S4 in the class, dimension 2 is at least 80% of growers at every size and higher at 20 than at 5; S5 dimension three
or more never exceeds 1% of in-class growers; S6 60 regrown in-class samples per size agree round by round to round 6; S7 the
in-class dimension-2 share of growers is within 5 points of SCALE-SHARE's share of all growers at every size.

**Questions.**
1. From the theorem, why should the in-class share stay roughly flat while stalls rise, and why should three stay rare as n grows
   (what would make it common: which configuration, at what open-per-knot)? Give the mechanism in the theorem's terms.
2. Are S3–S7 sensibly set, and which is the risky one? Suggest one sharper prediction derivable from the theorem without the pilot.
3. Any trap in comparing in-class shares with SCALE-SHARE's all-sample shares (selection by the class)?
