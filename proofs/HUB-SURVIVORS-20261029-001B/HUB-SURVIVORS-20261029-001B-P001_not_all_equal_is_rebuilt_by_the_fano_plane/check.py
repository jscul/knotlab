"""Checks for HUB-SURVIVORS-20261029-001B-P001 (not-all-equal is rebuilt by the Fano plane, and by nothing smaller).

  1 the Fano plane: no 2-colouring without a monochromatic line; deleting any line makes it 2-colourable; the punctured Fano
    gadget (one point split into one leg per line through it) has relation NAE, for every choice of the point
  2 exhaustive: no hub gadget of NAE copies with 2 to 6 copies (legs in one copy each) has relation NAE
  3 exhaustive: no wire of NAE copies with 2 to 6 copies (one end in one copy, the other in any number) is an equality or an
    inequality
  4 exhaustive at 7 copies: every hub gadget with relation NAE is a punctured Fano plane (merging the legs gives seven edges on
    seven points with every pair of points in exactly one edge); skipped unless --seven is given (long run)
  6 counts: the punctured Fano gadget has exactly 5 hidden completions for every NAE tuple and none for 000, 111, at every point
  5 controls that must fire: the punctured Fano gadget of a non-NAE knot (OR) is not that knot; a mutated Fano plane (one line
    changed) is 2-colourable and its puncture does not give NAE; a wire search on parity copies finds wires
Run: python3 -B check.py [--write] [--seven]   (numpy)"""
import itertools, json, os, sys, time

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
import nae_lib as N  # noqa: E402
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:1200], flush=True)


def main(write, seven):
    man = json.load(open(os.path.join(HERE, "manifest.json")))
    F = N.FANO_LINES
    pts = list(range(7))
    noncol = not N.two_colourable(F, pts)
    critical = all(N.two_colourable([L for L in F if L != M], pts) for M in F)
    punct = {p: N.punctured_relation(F, p) == N.NAE_SET for p in pts}
    report("1 Fano plane and its puncture", noncol and critical and all(punct.values()),
           {"lines": F, "no 2-colouring": noncol, "every line deletion 2-colourable": critical,
            "punctured relation is NAE at every point": punct})

    counts, hits2 = {}, {}
    for m in range(2, 7):
        c, h = N.rebuilding_gadgets(m)
        counts[m], hits2[m] = c, len(h)
    report("2 no NAE rebuild with at most six copies", all(v == 0 for v in hits2.values()),
           {"gadgets evaluated": counts, "rebuilding gadgets": hits2, "seconds": round(time.time() - T0)})

    wc, wh = {}, {}
    for m in range(2, 7):
        c, h = N.wires_with_hub_end(m)
        wc[m], wh[m] = c, len(h)
    report("3 no NAE wire with at most six copies", all(v == 0 for v in wh.values()),
           {"wire gadgets evaluated": wc, "wires": wh, "seconds": round(time.time() - T0)})

    if seven:
        c, h = N.rebuilding_gadgets(7)
        bad = [x for x in h if not N.is_fano(N.merged_edges(7, *x))]
        report("4 every seven-copy NAE rebuild is a punctured Fano plane", h and not bad,
               {"gadgets evaluated": c, "rebuilding gadgets (labelled)": len(h), "not Fano": len(bad),
                "seconds": round(time.time() - T0)})
    else:
        print("SKIP 4 (run with --seven)")

    OR = {s for s in itertools.product((0, 1), repeat=3) if s != (0, 0, 0)}
    or_punct = N.punctured_relation(F, 0, rel=OR)
    mutated = [L for L in F]
    mutated[6] = (1, 5, 4) if mutated[6] != (1, 4, 5) else (1, 5, 6)
    mutated = [tuple(sorted(L)) for L in mutated]
    mut_col = N.two_colourable(mutated, pts)
    mut_punct = N.punctured_relation(mutated, 0) == N.NAE_SET
    PAR = np.zeros((2, 2, 2), dtype=np.int64)
    for s in itertools.product((0, 1), repeat=3):
        PAR[s] = (sum(s) % 2 == 1)
    saved = N.NAE
    N.NAE = PAR
    c, h = N.wires_with_hub_end(2)
    N.NAE = saved
    report("5 controls fire", or_punct != OR and mut_col and not mut_punct and len(h) > 0,
           {"punctured Fano of OR is OR": or_punct == OR, "mutated plane 2-colourable": mut_col,
            "mutated puncture gives NAE": mut_punct, "parity wires found at two copies": len(h)})

    cnts = {p: N.punctured_counts(F, p) for p in pts}
    uniform = all(all(v == (5 if t in N.NAE_SET else 0) for t, v in cnts[p].items()) for p in pts)
    report("6 counted fixed point", uniform, {"completions per leg tuple at point 0": {"".join(map(str, t)): v for t, v in cnts[0].items()},
                                             "5 for every NAE tuple at every point": uniform})

    status = "Proved" if ok_all else "Failed"
    print("ALL CHECKS PASS" if ok_all else "SOME CHECKS FAIL", f"({time.time() - T0:.0f}s)")
    if write:
        json.dump({"schema_version": 1, "artifact_id": man["artifact_id"], "status": status,
                   "checks": {"ok": ok_all, **out}, "seven_copy_search_run": seven,
                   "seconds": round(time.time() - T0, 1)},
                  open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
    return ok_all


if __name__ == "__main__":
    sys.exit(0 if main("--write" in sys.argv, "--seven" in sys.argv) else 1)
