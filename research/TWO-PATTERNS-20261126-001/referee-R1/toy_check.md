# Two patterns in one start, toy check

**Confirmed with fixes.** The pinned checker reproduced all of the comparisons recorded for the toy. The fixes concern the claimed coverage and the explanation of the stub. No Block.

## What holds

The site commit `180a14b` has tree `d55aa4efd9d0`, as recorded in the [toy note](../toy/README.md). Its checker imports `joinedStart` and `twoPatternsRun` from `src/lib/two-patterns.ts`. Growth runs through `law-rounds.ts` and its roster code. The fixture generator executes `bench.build` and `bench.Growth` from the public record at commit `11c7680970`. The bench executes `eng.play_round`, with `pm.py` supplying its guards. I verified that each of the three pinned Python sources matches its hash at study closure `9b6dad2e0c`. The later bench edit adds a law registry to `case()`. Fixture generation calls `build()` and `Growth` directly.

Two separately implemented growth engines run the shared rules on the same starts. The TypeScript implementation follows earlier Python studies, which it credits, and computes the rounds in its own code. The Python results enter the comparison as fixture input to the checker. Regenerating the fixture reproduced the pinned file byte for byte. The checker matched all 72 sets of initial distinction labels and the displayed round count for each of the 792 cases. Across the 6,229 retained rounds, it matched 74,748 numeric values in 12 fields. Those fields cover total knots, short knots, four birth counts by descent, two own-member counts and two pairs of joined and kept group counts.

The checker compares aggregate counts. Per-knot parent records, labels of grown distinctions, identity of short or waiting knots, reasons for stopping, the wording of the round messages and the drawing are outside this comparison. The generator leaves the knot test module out. The [independent fixture count](toy_fixture_audit.json) gives the distribution of retained rounds and the choices tested. At each tested retirement timing, 68 of the 72 cases have a drawn round after that timing.

| Retire the second pattern | Site choices | Cases in the pinned fixture | Retained rounds in the pinned fixture |
| --- | ---: | ---: | ---: |
| Never | 648 | 648 | 5,002 |
| After round 2 | 648 | 72 | 614 |
| After round 4 | 648 | 72 | 613 |
| After round 6 | 648 | 0 | 0 |
| Total | 2,592 | 792 | 6,229 |

In the default setting, two two-knot parts share a distinction under the ordinary count and each makes two own knots per retained round. Births of both run from 2 to 24 in steps of two, in the 12 retained rounds. The view sums the births as knots of both so far.

## Additional check after closure

I extended the copied fixture generator to run all 2,592 menu settings and ran the unchanged checker against them. The earlier 792 traces were identical in both fixture files. The two engines matched all 72 starts and 21,979 retained rounds on the same fields. The round-6 retirement setting contributed 5,422 retained rounds, with 441 of its 648 cases continuing to a drawn round after retirement. These [counts](toy_full_menu_audit.json) include the preset first-knot sites, both supplied joins, and all supplied rations, short-knot treatments, and retirement timings. The one-round [stub probe](toy_stub_probe.json) separately removed the second pattern and its join. That change of scaffold changed the count for a shared distinction as described below.

## Fixes

- **Narrowing.** In [the toy note](../toy/README.md#L24), replace “compares the two on the toy's whole menu” and “with the retiring by hand on a third of the menu” with “compares the 72 joined starts and 6,229 retained rounds of 792 cases. That includes all 648 settings without retirement and the 72 one-step settings with waiting for each of retirement after rounds 2 and 4.” This describes the pinned fixture. Apply the same qualification to the comment in `scripts/check-two-patterns.mjs:5`–`8`.
- **Narrowing.** In [the decision](../decision.md#L27), replace “shows all of this, and its engine agrees with the bench's on 6,229 rounds of 792 cases” with “shows growth by descent and the joined and kept group counts for the selected start. Its counts agree with the bench on 6,229 retained rounds in the 792 cases of the site check.” The toy includes no marks, takes, side-by-side stub run or reading of table places, parents or balls.
- **Narrowing.** In the site source header `180a14b:src/lib/two-patterns.ts:6`, replace “compares every count shown here with that program's” with “compares 12 round counts with that program's.” For example, the check has no column for the total of all cancelled groups, which the site reports in its round sentence when a knot is short.
- **Narrowing.** In the menu text at `180a14b:src/components/intuitions/law-growth-examples/TwoPatternsExample.tsx:141`, replace “A stub is one knot of three places that holds the far end of the join and nothing more: what the first pattern makes beside it is what it makes with no pattern there” with “A stub is one knot of three places standing in for the second pattern so the join stays in place.” A bare two-knot part makes four own knots in the first round under the ordinary count. When the first knot shares a distinction with a stub one step away, one of the second knot's two loose distinctions pays for a kept group with the stub. That leaves three own births. By a meeting the added loose distinction pays, and there are four own births. The pinned site engine [reproduced these counts](toy_stub_probe.json).
- **Not a block.** The line “They agreed on the first run, so the toy's counts rest on two engines written apart” in [the toy note](../toy/README.md#L29) can read “The recorded outputs match between two implementations of the same growth rules.” The fixture and source tree establish the recorded agreement. The order of earlier local runs is unverified.

## What was not run

The release tree and the source of the site's menu were checked. Live HTTP was unavailable in this environment. The replay used the two existing growth engines. Browser rendering and knothood were outside the run.

## How it was checked

The pinned fixture SHA-256 is `0f835043837d3bcba76d786fdbd9f823fa93f0d1d71e2a6f50848627903d93a7`. The expanded fixture SHA-256 is `97bef61bc86b99b13d398e0410a326a36cf7f284d2af71d107a332bafed05847`. Each replay used one computation process under a 2 GiB address-space cap. Before the closure replay, a 132-case run through the generator took 1.62 seconds, projecting about 10 seconds. A 10-case check took 0.28 seconds, projecting about 22 seconds. The respective full runs took 8.34 and 3.94 seconds. Before the full-menu replay, a 432-case run took 4.55 seconds to generate and 2.41 seconds to check, projecting about 42 seconds together. The full runs took 24.24 and 11.09 seconds. Peak resident memory stayed below 142 MiB.

Rerun from the workspace root with the two read-only checkouts.

```bash
set -euo pipefail
toy_scope=research/TWO-PATTERNS-20261126-001/referee-R1
toy_scratch="$toy_scope/toy_replay"
toy_site=/home/jscul/prespatial-org
toy_public=/home/jscul/knotlab
mkdir -p "$toy_scratch/scripts/fixtures" "$toy_scratch/src/lib" "$toy_scratch/tmp"
for toy_file in scripts/check-two-patterns.mjs scripts/generate-two-patterns-fixtures.py \
    src/lib/two-patterns.ts src/lib/law-rounds.ts src/lib/roster-growth.ts src/lib/knot-growth.ts
do
    git -C "$toy_site" show "180a14b:$toy_file" > "$toy_scratch/$toy_file"
done
git -C "$toy_site" show 180a14b:scripts/fixtures/two-patterns.json > "$toy_scratch/original.json"
toy_fixture="$toy_scratch/scripts/fixtures/two-patterns.json"
ulimit -v 2097152
ulimit -c 0
export TMPDIR="$PWD/$toy_scratch/tmp" NODE_DISABLE_COMPILE_CACHE=1 UV_THREADPOOL_SIZE=1
toy_node=(node --disable-wasm-trap-handler --v8-pool-size=1 --max-old-space-size=512 --experimental-strip-types)
.venv/bin/python -B "$toy_scratch/scripts/generate-two-patterns-fixtures.py" --from "$toy_public" --output "$toy_fixture"
cmp "$toy_scratch/original.json" "$toy_fixture"
"${toy_node[@]}" "$toy_scratch/scripts/check-two-patterns.mjs"
.venv/bin/python -B "$toy_scope/toy_fixture_audit.py" "$toy_fixture"
"${toy_node[@]}" "$toy_scope/toy_stub_probe.mjs"
.venv/bin/python -B "$toy_scope/toy_expand_menu.py" "$toy_scratch/scripts/generate-two-patterns-fixtures.py" "$toy_public" "$toy_fixture"
"${toy_node[@]}" "$toy_scratch/scripts/check-two-patterns.mjs"
.venv/bin/python -B "$toy_scope/toy_fixture_audit.py" "$toy_fixture" --full-menu
```
