"""Evaluate exact hub-greedy path weights and archive reproducible group draws.

A draw uses a uniform ticket at each outside/finish choice. Fix a maximal
group C. At that choice the comparison law uses only tickets consistent with
C. If C lies wholly in the current anchor, the only consistent ticket is
finish. Otherwise every outside member of C supplies all its outside tickets.
The comparison law ends at C with probability one. Consequently a draw's
comparison-path probability divided by its proposal-path probability has
mean one per maximal group. A rejected finish contributes zero. In a small
suffix the proposal chooses uniformly among all exact completions and the
comparison law chooses its one required completion.
"""

from argparse import ArgumentParser
from base64 import b64decode, b64encode
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal, localcontext
from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
from statistics import median
import subprocess
from time import perf_counter
from zlib import compress, decompress


def names(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def maximal_masks(adj, mask):
    answer = set()
    subset = mask
    while True:
        if all(subset & ~(adj[u] | (1 << u)) == 0 for u in names(subset)):
            if all(subset & ~adj[u] for u in names(mask ^ subset)):
                answer.add(subset)
        if not subset:
            return answer
        subset = (subset - 1) & mask


def tiny_controls():
    """Exhaust both the overlapping proposal paths and independent subsets."""
    graphs = checks = rejected_leaves = 0
    for n in range(1, 5):
        edges = list(combinations(range(n), 2))
        full = (1 << n) - 1
        for word in range(1 << len(edges)):
            graphs += 1
            adj = [0] * n
            blocks = []
            for i, (u, v) in enumerate(edges):
                if word >> i & 1:
                    adj[u] |= 1 << v
                    adj[v] |= 1 << u
                    blocks.append((1 << u) | (1 << v))
            expected = maximal_masks(adj, full)
            for use_anchors in (False, True):
                bank = blocks[:2] if use_anchors else []
                for tail in (0, 2):
                    for slots in (1, 3):
                        checks += 1

                        def check_path(left, prefix, probability, factors):
                            nonlocal rejected_leaves
                            inside = max((left & b for b in bank), key=int.bit_count, default=0)
                            outside = left ^ inside
                            if outside.bit_count() <= tail:
                                ends = maximal_masks(adj, left)
                                for finish in ends:
                                    yield prefix | finish, probability / len(ends), factors + [(len(ends), 0, 1)]
                                return
                            tickets = slots * outside.bit_count() + bool(inside)
                            if inside:
                                if inside in maximal_masks(adj, left):
                                    yield prefix | inside, probability / tickets, factors + [(tickets, 0, 1)]
                                else:
                                    rejected_leaves += 1
                                    yield None, probability / tickets, ()
                            for v in names(outside):
                                yield from check_path(left & adj[v], prefix | (1 << v), probability * slots / tickets,
                                                      factors + [(tickets, outside, slots)])

                        total = Fraction()
                        tallied = Counter()
                        for group, probability, factors in check_path(full, 0, Fraction(1), []):
                            total += probability
                            if group is None:
                                continue
                            weight = Fraction(1)
                            for numerator, outside, nslots in factors:
                                weight *= Fraction(numerator, nslots * (group & outside).bit_count() if outside else 1)
                            tallied[group] += probability * weight
                        assert total == 1 and dict(tallied) == dict.fromkeys(expected, Fraction(1))
    return {"labelled_graphs": graphs, "exact_probability_checks": checks, "rejected_leaves": rejected_leaves}


def decode_group(record):
    """Decode a full literal group as a bitset over the original row names."""
    return int.from_bytes(decompress(b64decode(record["literal_group_bitset_zlib_base64"])), "little")


def pack_group(record):
    hexwords = record.pop("literal_members_le_hex")
    raw = b"".join(int(hexwords[i:i + 16], 16).to_bytes(8, "little") for i in range(0, len(hexwords), 16))
    record["literal_group_bitset_zlib_base64"] = b64encode(compress(raw)).decode("ascii")


def verify_witnesses(path, records, reference):
    with path.open() as inp:
        n, m = map(int, next(inp).split())
        blocks = [tuple(map(int, line.split())) for line in inp]
    assert len(blocks) == m
    incident = [[] for _ in range(n)]
    masks = []
    for b, block in enumerate(blocks):
        data = bytearray((n + 7) // 8)
        for u in block:
            incident[u].append(b)
            data[u // 8] |= 1 << (u % 8)
        masks.append(int.from_bytes(data, "little"))

    @lru_cache(maxsize=256)
    def neighbors(u):
        union = 1 << u
        for b in incident[u]:
            union |= masks[b]
        return union

    assert all(not (neighbors(u) >> v & 1) for u, v in reference)
    assert all(neighbors(a) >> b & 1 for pair, other in combinations(reference, 2)
               for a in pair for b in other)
    full = (1 << n) - 1
    for r in records:
        group = decode_group(r)
        cover = [(group & b).bit_count() for b in masks]
        top = max(cover, default=0)
        inside_block = masks[cover.index(top)] if top else 0
        inside, outside = group & inside_block, group & ~inside_block
        assert group.bit_count() == r["size"] and top == r["largest_block_intersection"]
        assert sum(c > 0 for c in cover) == r["blocks_met"]
        assert sum(bool(group >> u & 1 or group >> v & 1) for u, v in reference) == r["partner_pairs_met"]
        common = full
        for u in names(outside):
            adjacent = neighbors(u)
            assert group & ~adjacent == 0
            common &= adjacent
        assert common & inside_block == inside
        for k, v in enumerate(names(inside)):
            if k == 12:
                break
            common &= neighbors(v)
        for v in names(common & ~(inside_block | outside)):
            assert inside & ~neighbors(v), "published witness was extendible"
        min_cover = 0 if not top else 1 if top == r["size"] else 3
        if min_cover == 3:
            for i, a in enumerate(cover):
                if 2*a >= r["size"] and any(a+h >= r["size"] and group & ~(masks[i] | masks[j]) == 0
                                             for j,h in enumerate(cover)):
                    min_cover = 2
                    break
        assert min_cover == r["block_cover_1_2_or_at_least_3"]
    return len(records)


def weight(row):
    if not row["maximal"]:
        return Decimal(0)
    value = Decimal(1)
    for a, da, b, db, count in row["weight_progressions"]:
        for i in range(count):
            value *= Decimal(a + i*da) / Decimal(b + i*db)
    return value


def percentile(values, p):
    index = Decimal(p) * (len(values) - 1)
    begin = int(index)
    return values[begin] + (index - begin) * (values[min(len(values)-1, begin+1)] - values[begin])


def moment(values):
    with localcontext() as ctx:
        ctx.prec = 40
        values = sorted(values)
        central = [percentile(values, p) for p in ("0.025", "0.975")]
        total = sum(values)
        return {
            "min": str(values[0]), "max": str(values[-1]),
            "mean": str(total / len(values)),
            "empirical_central_95_percent": [str(x) for x in central],
            "central_ratio": str(central[1] / central[0]) if central[0] else None,
            "top_replicate_share": str(values[-1] / total) if total else None,
        }


def analyze(replicates, metadata, panel):
    estimate = {"raw": [], "large": [], "births": []}
    observed = []
    with localcontext() as ctx:
        ctx.prec = 45
        for replicate in replicates:
            rows = replicate["draws"]
            actual = [r for r in rows if r.get("large_join")]
            weighted = [(r, weight(r)) for r in rows]
            raw = sum(w for _, w in weighted) / len(rows)
            total = sum((w for r, w in weighted if r.get("large_join")), Decimal(0)) / len(rows)
            estimate["raw"].append(raw)
            estimate["large"].append(total)
            if panel.get("exact_addend") is not None:
                estimate["births"].append(total + panel["exact_addend"])
            observed.extend((r, w) for r, w in weighted if r.get("large_join"))
            replicate["weighted_raw_maximal_sets"] = str(raw)
            replicate["weighted_large_joins"] = str(total)
            replicate["rejected_draw_count"] = sum(not r["maximal"] for r in rows)
            replicate["actual_large_join_draws"] = len(actual)
            replicate["max_weight_share"] = str(max(w for _, w in weighted) / (raw * len(rows))) if raw else None

        raw_count = sum(len(r["draws"]) for r in replicates)
        if observed:
            groups, weights = zip(*observed, strict=True)
            size = [r["size"] for r in groups]
            marks = {
                "largest_block_covers_at_least_90_percent":
                    [r["largest_block_intersection"] * 10 >= 9 * r["size"] for r in groups],
                "needs_at_least_three_blocks": [r["block_cover_1_2_or_at_least_3"] >= 3 for r in groups],
                "meets_at_least_one_reference_pair": [r["partner_pairs_met"] > 0 for r in groups],
                "meets_every_reference_pair": [r["partner_pairs_met"] == len(metadata["partner_reference"])
                                                for r in groups],
            }
            weighted_sum = sum(weights)
            shape = {
                "actual_large_join_draws": len(groups),
                "distinct_fingerprints": len({r["fingerprint"] for r in groups}),
                "literal_sizes_min_median_max": [min(size), median(size), max(size)],
                "blocks_met_min_max": [min(r["blocks_met"] for r in groups), max(r["blocks_met"] for r in groups)],
                "partner_pairs_met_min_max": [min(r["partner_pairs_met"] for r in groups),
                                             max(r["partner_pairs_met"] for r in groups)],
                "marks": {
                    label: {
                        "raw_proposal_hits": sum(flag),
                        "raw_proposal_large_join_denominator": len(groups),
                        "weighted_marked_total_estimate": str(sum((w for w, f in zip(weights, flag, strict=True) if f), Decimal(0)) / raw_count),
                        "weighted_share_ratio_estimate": str(sum(w for w, f in zip(weights, flag, strict=True) if f) / weighted_sum),
                    } for label, flag in marks.items()
                },
            }
            if not metadata["partner_reference"]:
                del shape["marks"]["meets_every_reference_pair"]
        else:
            shape = {"actual_large_join_draws": 0}
        moments = {key: moment(values) for key, values in estimate.items() if values}
        for key, summary in moments.items():
            actual = panel.get("truth", {}).get(key)
            if actual is not None:
                summary["exact_truth"] = actual
                summary["signed_mean_error"] = str(Decimal(summary["mean"]) - actual)
        return {"replicate_dispersion": moments, "structural_marks": shape, "attempted_draws": raw_count}


def run_panel(engine, panel, settings):
    source = Path(panel["roster"])
    references = panel.get("reference", "-")
    config = [settings["anchor_count"], settings["exact_outside_limit"], panel["seed"], panel["draws"],
              panel["replicates"], int(panel.get("reverse", False)), panel.get("witnesses", 12), settings["outside_slots"]]
    started = perf_counter()
    run = subprocess.run([engine, source, references, *map(str, config)], check=True, text=True, capture_output=True)
    metadata, *events = map(json.loads, run.stdout.splitlines())
    replicates = []
    witnesses = []
    for event in events:
        if "replicate" in event:
            event["draws"] = []
            replicates.append(event)
        else:
            if "literal_members_le_hex" in event:
                pack_group(event)
                witnesses.append(event)
            replicates[-1]["draws"].append(event)
    assert len(replicates) == panel["replicates"] and all(len(r["draws"]) == panel["draws"] for r in replicates)
    assert all(r["seed"] == panel["seed"] + i for i, r in enumerate(replicates))
    digest = sha256(source.read_bytes()).hexdigest()
    assert digest == panel.get("sha256", digest)
    independently_verified = verify_witnesses(source, witnesses[:1], metadata["partner_reference"]) if witnesses else 0
    return {
        **panel, "roster_sha256": digest, "engine": metadata, "replicate_count": panel["replicates"],
        "replicates": replicates, "elapsed_seconds": round(perf_counter() - started, 3),
        "independently_verified_full_group_witnesses": independently_verified,
        **analyze(replicates, metadata, panel),
    }


def setup(params):
    global job_plan, job_engine
    job_plan = json.loads(Path(params["plan"]).read_text())
    job_engine = Path(params["engine"]).resolve()


def cases():
    for panel in job_plan["panels"]:
        yield panel["label"], panel


def run(case_id, payload):
    assert case_id == payload["label"]
    return run_panel(job_engine, payload, job_plan["settings"])


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("engine", type=Path)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--case-results", type=Path)
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text())
    controls = tiny_controls()
    if args.case_results:
        by_case = {}
        for line in args.case_results.read_text().splitlines():
            row = json.loads(line)
            by_case[row["case"]] = row
        report = [by_case[panel["label"]] for panel in plan["panels"]]
        assert all(r["status"] == "ok" for r in report)
        results = [r["result"] for r in report]
    else:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            jobs = [pool.submit(run_panel, args.engine.resolve(), panel, plan["settings"]) for panel in plan["panels"]]
            results = [job.result() for job in jobs]
    print(json.dumps({
        "freeze": "80b69e48c",
        "plan_sha256": sha256(args.plan.read_bytes()).hexdigest(),
        "settings": plan["settings"],
        "exact_probability_controls": controls,
        "panels": results,
    }, separators=(",", ":"), sort_keys=True))


if __name__ == "__main__":
    main()
