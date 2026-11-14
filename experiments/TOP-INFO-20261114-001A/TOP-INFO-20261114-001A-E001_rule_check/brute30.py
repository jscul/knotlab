"""TOP-INFO-20261114-001A, the thread's driver for the frozen brute-force gate (pre-registration addendum): the first 30 in-scope
identity-stratum families among the two-block cases that were not already bounded, in sha256("TOP:" + key) order, each checked by
Codex's independent `two_block_brute.compare_family` at every S-word of length at most 3 and every direct entry."""
import hashlib, json, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "codex"))
import two_block_brute  # noqa: E402

cat = json.load(open(HERE / "codex/catalog.json"))
bounded = set(cat["bounded_controls"])
rows = {r["key"]: r for r in cat["rows"] if isinstance(r, dict) and "key" in r}
cands = [k for k in cat["selected_two_block"] if k not in bounded]
def ok(k):
    r = rows.get(k, {})
    return r.get("in_scope", r.get("scope") == "in") and r.get("stratum") == "I"
cands = sorted((k for k in cands if ok(k)), key=lambda k: hashlib.sha256(("TOP:" + k).encode()).hexdigest())[:30]
log = HERE / "brute30.jsonl"
done = {json.loads(l)["key"]: json.loads(l) for l in open(log)} if log.exists() else {}
out = []
for k in cands:
    if k in done:
        out.append(done[k]); continue
    t0 = time.monotonic()
    try:
        res = two_block_brute.compare_family(k, max_s=3)
        row = dict(key=k, passed=res.get("passed"), complete=res.get("complete"), caps=res.get("caps"),
                   checks=len(res.get("checks", [])), seconds=round(time.monotonic() - t0, 2))
    except Exception as e:  # a cap or limit: the family stays unknown, never passed
        row = dict(key=k, passed=False, complete=False, caps=[repr(e)[:200]], checks=0, seconds=round(time.monotonic() - t0, 2))
    out.append(row)
    with open(log, "a") as f:
        f.write(json.dumps(row) + "\n")
json.dump(dict(selection="first 30 in-scope I two-block cases not already bounded, sha256('TOP:'+key) order", n=len(out),
               passed=sum(bool(o["passed"]) for o in out), complete=sum(bool(o["complete"]) for o in out), rows=out),
          open(HERE / "brute30.json", "w"), indent=1)
