"""Check API outputs against captured closures of the unmodified BD source."""

import json
from pathlib import Path
import sys
import time

from ray_dp import BD, FamilyDP, INF, close, middle, start_nodes


def main():
    families = BD.families_one_def()
    chosen = [next((idx, defs) for idx, defs in families if defs[0][1] == size)
              for size in range(2, 7)]
    results = []
    for idx, defs in chosen:
        t0 = time.monotonic()
        captured = {}

        def profile(frame, event, arg):
            if event == "return" and frame.f_code is BD.run_family.__code__:
                captured.update(frame.f_locals)

        sys.setprofile(profile)
        try:
            reference = BD.run_family(defs, smax=1)
        finally:
            sys.setprofile(None)
        ctx = FamilyDP(defs)
        starts = ctx.start_nodes()
        assert starts == captured["layer"] == start_nodes(defs)
        for name in ("subsets_first", "subsets_mid", "subsets_last"):
            assert getattr(ctx, name) == captured[name]
        source_advance = captured["advance"]
        samples = list(starts)[:4]
        checks = 0
        for node in samples:
            expected = [(W, source_advance(*node, W, last=False), len(W))
                        for W in captured["subsets_mid"]]
            assert ctx.middle(node) == middle(defs, node) == expected
            best = INF
            for W in captured["subsets_last"]:
                expected_state = source_advance(*node, W, last=True)
                assert ctx.advance(*node, W, True) == expected_state
                F, G = expected_state
                if 0 in F and 0 not in G:
                    best = min(best, len(W))
                checks += 1
            assert ctx.close(node) == close(defs, node) == best
            checks += len(expected)
        best_start = min((cost + ctx.close(node) for node, cost in starts.items()
                          if ctx.close(node) < INF), default=INF)
        assert [best_start] == reference["L"]
        result = dict(idx=idx, locals=defs[0][1], start_nodes=len(starts),
                      transition_checks=checks, seconds=round(time.monotonic()-t0, 6),
                      passed=True)
        results.append(result)
        print(json.dumps(result), flush=True)
    path = Path(__file__).resolve().parent / "refactor_validation.json"
    path.write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    main()
