Brief cold review (~250 words) of a sampling design replacing a too-costly census. Flaws, overclaims, thresholds?

Object: L_path(s), least bond over all descending paths of copies (min over which SELF call continues, start entry included), members on the path; plus L_path^unc (paths along which no top port is carried into C_s). Per family: class over paths (grows/bounded/mixed/none/lost/unresolved) and uncarried class. Cost: mean 58 s/family, 15% hit the 300 s cap (unresolved), 3 workers; the 32,315 eligible families (two or more SELF calls, not settled) would take days.

Population by first-ray class (census): grows 6,925 distinct (6,989 draws); bounded 18,281 (L_path <= L_ray so bounded over paths by construction; only the carried split is open); none/lost 6,469; other 640.

Design (frozen before any class is seen): uniform samples of DISTINCT families within strata, Random(20261114): G = 400 first-ray growers (excluding the 224 one-definition growers, which are run in full as gate G-last); N = 200 first-ray none/lost; B = 100 first-ray bounded (carried split only). Count shares = sample proportions; weight shares = ratio estimator weighting each sampled family by its draw count; 95% bootstrap over sampled families; unresolved against (low) and for (high).

Predictions (frozen earlier): P1 first-ray growers bounded over paths >= 75% by count and a weight majority (excluding the 224); hold if low band's 2.5% quantile >= threshold, fail if high band's 97.5% < threshold, else undecided; also read on uncarried boundedness. P2 some grower over paths with inequivalent calls (existence; any sampled instance). P3 some none/lost family has a persisting bond over paths (existence). Undecided if unresolved > 5% of a stratum's sample.

Is per-stratum distinct-family uniform sampling with ratio-weighted weight shares sound? Is 400 enough given 15% unresolved? Anything settled by construction I present as a test?
