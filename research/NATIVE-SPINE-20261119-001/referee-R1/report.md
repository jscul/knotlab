# Referee report NATIVE-SPINE-001-R1 (own growth, own relation, networkx's matcher and components, own shuffles)

**Verdict: confirmed. No Block; two wording points.**
- **The rules fail as stated, on all 204 recurrent rounds of the ten.**
  - N, M and F never keep a perfect matching.
  - Their tie counts equal the study's on every rule and round.
  - M keeps no depth-2 ancestor at any round.
- **"Most chains sees only depth 3" is a theorem, not only an observation** (the by-hand check).
  - **The argument.** Every parent chain from j to a depth-2 ancestor a continues to each of a's parents. So m(b, j) ≥ m(a, j) for
    every parent b of a, and the largest chain count at depth 3 is never below the largest at depth 2.
  - **Checked** for every junction of all 204 rounds.
  - **By hand,** on T-028 at round 7: junction 158 has depth-2 ancestors with 1, 2, 2, 1 and 2 chains, and depth-3 ancestors with
    1, 3, 3, 3, 6 and 3. M keeps only the depth-3 ancestor 73, with 6 chains. The next three junctions look alike: maxima 2 against
    6.
- **`forced_fraction` is right, and the forced share is 0 at every round.**
  - **Why the method works.** A matched pair lies in every perfect matching exactly when its two ends are in different strongly
    connected components of the alternating digraph. That is the study's method.
  - **Recomputed independently:** networkx's matching and its components give the study's value at all 204 rounds, 0 each time.
  - **Tested directly:** on the 104 rounds of at most 400 junctions, each matched pair was removed and another perfect matching
    looked for. One was found for every pair, so nothing is forced.
- **`shuffled_has_perfect`, and the null, hold.**
  - **The shuffle** is a valid degree-preserving double swap on the bipartite relation.
  - **The referee's own shuffles,** three per round at rounds 10, 15 and 20 (20 swaps per pair, other seeds), keep every left
    degree. All 90 still have a perfect matching.
  - **So the owner's narrowing of JUNCTION-KINDS is supported.** The pairing's existence follows from the counts and the density of
    the ancestry.

## The checks (`job_spine.py` under `scripts/longrun.py`)

| | Result |
| --- | --- |
| Recurrent rounds of the ten (the study's 204) | 204; a perfect matching at every one |
| N / M / F keep a perfect matching | 0 / 0 / 0 of 204 |
| Ties per rule, equal to the study's | 204 of 204 rounds |
| M's kept ancestors at depth 2 | 0 at every round |
| Largest chain count at depth 3 ≥ at depth 2, every junction | 204 of 204 rounds (by the argument above) |
| Forced share by strongly connected components (networkx) | 0 at every round; equal to the study's at 204 of 204 |
| Forced share by removing each matched pair (rounds of ≤ 400 junctions) | 0 at all 104 |
| Shuffled relations with a perfect matching (3 per round × rounds 10, 15, 20 × 10) | 90 of 90 (left degrees kept in all) |

## Wording points for the owner (listed, not folded in)

1. **"So the spine is not in the growth"** goes beyond what was tested: three rules and the forced reading. A rule of bounded
   radius is not excluded, which is the direction's own other stop case. Say "no rule tried picks it, and nothing forces it".
   **Not a block.**
2. **M's depth bias** can be stated as proved (the chain-count inequality above), not only as the advisor's prediction borne out.
   **Not a block.**

## How the work was split

- **The referee:**
  - read `native_spine.md`, the pre-registration, `rulelib.py` and `job.py`;
  - wrote `job_spine.py`, on its FIRST-KNOT-R1 and TOUCH-CENSUS-R1 code.
- **Read as data:** BREAK-EDDIES' starts and the study's records (`runs/native-spine`).
- **No study code was run.**
- **Where it ran.** Under `scripts/longrun.py` within the 16 GB cap, 3 workers (peak 2.2 GB).
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
