# Referee report PROVE-B-001-R1 (Lemmas C and O read line by line; own Proposition X, three-way counts and census sample)

**Verdict: confirmed. Claim B is refuted as stated, and Lemmas C and O are correct. No Block. Two small points, Not a block.**

## The points asked

- **Lemma C, the split formula: correct.** Not a block.
  - **The bonds.** They are the cuts δ′(S ∪ T) with both sides connected, o outside.
  - **Item 1** counts the change from δ(S). For n ∈ T:
    - a taken edge from u ∈ S was in δ(S) and becomes internal (−1);
    - one from u ∉ S becomes a crossing (+1);
    - n's f(n) fresh edges cross.

    For n ∉ T, a taken edge from u ∈ S still crosses, now as u–n. No loose edge of S survives untaken, because a complete round takes
    every loose distinction of the live junctions. That gives |δ(S)| + Σ_{n∈T}(f(n) + |P(n) ∖ S| − |P(n) ∩ S|).
  - **Item 2** is the same membership count.
  - **Item 3.** Components of S meet only through T, since new junctions meet only parents and o. Contracting N ∪ {o} to o shows
    each δ(S_i) is a bond of G.
- **Lemma O, offshoots: correct.** Not a block.
  - **The step.** Dropping an offshoot n with parent u ∈ S keeps both sides connected: n's only neighbour inside is u, and it
    joins o's side through its fresh edges. The cost falls by f(n) − 1, which is at least 1 under the fewest counts.
  - **Items 2 to 4 and Corollary O** follow. So HUNT-SHORTEN's H1 is proved.
  - **One edge case.** An implied offshoot, when the stage has a single loose distinction, can have f = d < 2. Then the drop is ≥ 0,
    not ≥ 1, and "no least bond uses n" becomes "some least bond avoids n". The conclusions are unchanged.
- **The coset search in `reached_job.py` is sound.** It runs VF2 on the full table, with a semantic test forcing images to
  increase inside each holder class. That gives one isometry per coset of holder-class permutations, the ones breaking holder
  classes included. Equation-carrying ones are skipped, and the extension is checked entry by entry. This is the same design as the
  referee's own search in HUNT-SHORTEN-R1.
- **`codex_reproduce.py` reproduces both Codex cases. The referee did the same independently:**
  - the meet-twice case in GROWN-END-SWAP-R1;
  - the meet-once seven- and six-junction histories in GROWN-END-MEET-ONCE-R1, where every reading-keeping, equation-breaking
    symmetry of the marked stage fails (48 of 48 in each).

## The referee's own checks (`job_proveb.py` under `scripts/longrun.py`)

| Check | Result |
| --- | --- |
| Proposition X, built from the proof's text | the swap p₁ q₁ is a table isometry; one round makes the two pair junctions with one fresh distinction each; **all 32** reading-keeping, equation-breaking symmetries fail to extend (P0 holds) |
| Triples whose three-way reading the swap changes | Proposition X 48, meet-twice 68, meet-once 76 (the referee counts every triple t with T(φt) ≠ T(t)) |
| One in ten of the census stages with reading-keeping, equation-breaking symmetries (613 stages from HUNT-SHORTEN-R1's run, holder-breaking ones included) | **56,756** such symmetries tested; **none** keeps every three-way reading (7 stages had more than 2,000, left untested) |

- **The three-way counts differ only by convention.** `codex_reproduce.py` sums over triples that some bond holds, with "none" for
  an image held by none. That counts a pair of triples (t, φt) with one side unheld once, where the referee counts it twice. Its 34
  and 74 are consistent with the referee's 68 and 76. Under both conventions every failing swap breaks three-way readings.
- **The exploratory three-way lead holds on a second, independent population.** In the census stages too, no reading-keeping,
  equation-breaking symmetry keeps the three-way readings, and none in 56,756 extended. Codex's GROWN-END-READING (pending this
  referee) reports a 239-junction reached stage where pair and three-way readings and the growing end are kept and an equation is
  not. If it holds, it refutes three-way rigidity as a premise, though Codex says that renaming still carries every later table.
  Direction #1 should be read with that in view.

## Points for the owner (listed, not folded in)

1. **"1,249,716 symmetries extend"** (the final report) is off by one. `reached.json` has 1,249,716 reading-keeping, equation-
   breaking symmetries and 1,249,715 extending. The remaining one was cut by a stage's alarm (6 stages late), so "no failure among
   those decided" is the exact statement. **Not a block.**
2. **Lemma O's "cheaper by f(n) − 1 ≥ 1"** assumes f(n) ≥ 2. An implied offshoot can have f = d < 2, which weakens item 2 to "some
   least bond avoids n". **Not a block.**

## How the work was split

- **The referee:**
  - read `prove_b.md`, `proof.md` line by line, and `reached_job.py`, `threeway_check.py` and `codex_reproduce.py` with their
    outputs;
  - wrote `job_proveb.py`, with its own engine and tables, HUNT-SHORTEN-R1's coset search and stage test, and THREE-WAY-R1's
    readings.
- **No study code was run.**
- **Where it ran.** Under `scripts/longrun.py` within the 16 GB cap.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
