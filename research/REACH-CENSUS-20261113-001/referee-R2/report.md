# Referee report REACH-CENSUS-R2 (light): the carried split

**Verdict: Confirmed, with two wording fixes (both Narrowing).**
- **The split reproduces.** The owner's carried split of the census's first-ray classes (`carried_split.py`) reproduces
  independently on the one-definition families. It is applied symmetrically, to growers as well as bounded families.
- **The measured part.** What is settled by the identity, carried ports making a local bond possible, is set aside correctly. The
  two-thirds share on uncarried bonds is measured, not forced.
- **Two sentences go beyond what is shown.** "The reach grows" needs its ray, and "survives the second ray in about 95%" counts
  non-contradiction as survival.

Referee: the background referee thread, 2026-11-13. `ref_split.py` is my own carried test and recount; it does not use the study's
code. Codex was not used for this light check. The advisor model was not consulted.

## 1. The split, recounted

My carried test follows the ray call's argument map on the port positions: T_1 holds the copy-1 positions that hold a top port, and
T_{k+1} = {j : a_j ∈ T_k}. A top port is carried forever iff the sets stay non-empty, which is the owner's test. I recounted the
one-definition families from `families.jsonl.gz` and the replayed draws.

| Draws (one definition) | Bounded, carried | Bounded, uncarried | Grows, carried | Grows, uncarried | Carried share of bounded | Grows share of uncarried |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| all | 18,626 | 4,115 | 1,693 | 8,375 | 81.9% | 67.1% |
| forever | 18,315 | 4,001 | 1,673 | 8,171 | 82.1% | 67.1% |
| limit-only | 311 | 114 | 20 | 204 | 73.2% | 64.2% |

**How this compares.** It matches the owner's overall figures: 82% of bounded weight carried, and growth about two thirds on uncarried
bonds. The owner's counts include the several-definition families, 11,457 of the 44,266 persisting draws, which I did not re-test.
The 99/32 on the 224 was already reproduced in R1.

**The test is applied symmetrically.** The flag is computed for every persisting first-ray class, so 2,201 carried growers are set
aside along with the carried bounded ones. A carried port does not force a bound: 8% of carried families still grow, since a local
bond also needs the block to constrain the port.

## 2. Settled or measured

**What the identity settles.** Where the ray carries a top port, a bond containing it can be local at every depth. That is a
property of the definition, and setting those families aside is right.

**What is measured.** That about two thirds of the uncarried persisting bonds grow along the first ray, alike in both cells, is not
forced by anything.

**The uncarried bounded bonds are genuine.** They are about a third, with certified bounds, and they transfer to the true least bond
as upper bounds.

## 3. Wording

**The Answer.** "On uncarried bonds the reach grows linearly ... in about two thirds" should say "the first-ray bond grows linearly".
- **Why.** Growth of a ray bond is no lower bound on the true least bond. TRUE-BOND found side branches shortening bonds in at least
  62 of the 226 growers.
- **Where it applies.** The same applies to the Reading's "each level usually adds to the distance".

**The Reading.** "Survives the second ray read in about 95% of the sampled growers once carried ports are set aside" is 1 − 31/645.
In the 3,000-family sample, the 645 first-ray growers split on the last-call ray as follows:
- **297 grow** on both rays.
- **283 are bounded,** but only through a carried port.
- **31 are genuinely bounded,** the only true contradictions.
- **34 are lost, absent or unresolved** on the last-call ray.

So 95% is "not contradicted by a genuine short second-ray bond", and growth is observed on both rays in 46%. Say "a genuinely short
second-ray bond contradicts first-ray growth in only 31 of 645 (4.8%)" and give the 297.

## Fixes

1. **Write "the first-ray bond grows" wherever "the reach grows"** stands for the uncarried split, in the Answer and the Reading.
   Add that growth is ray-only. **Narrowing.**
2. **Replace "survives the second ray in about 95%"** with the four-way split (297, 283, 31, 34), or "contradicted in only 31 of
   645". **Narrowing.**

## Files

`ref_split.py` → `result_split.json`.
