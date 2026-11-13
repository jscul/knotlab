"""Resumable prescribed EVERY-RAY gates; no validation runs at import.

Run from the repository root with .venv/bin/python -B.  --workers includes
the computing parent (at most N-1 children); all outputs stay in CODEX.
G-brute is implemented separately in run_brute.py under addendum A2--A4.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
from contextlib import AbstractContextManager
from fractions import Fraction
import hashlib
import importlib.util
import itertools
import json
import multiprocessing as mp
from multiprocessing.connection import wait
import os
from pathlib import Path
import random
import signal
import threading
import time
import traceback

for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = "1"

import paths_dp as P

HERE, ROOT, C = P.HERE, P.ROOT, P.CENSUS
INF = C.INF
AGGREGATE_MEMORY_BYTES = 7_500_000_000
OWN_MEMORY_BYTES = 3_000_000_000
BRUTE_QUESTIONS = [
    "What exactly defines a Karp graph's preperiod and period for s_max? Karp supplies a cycle mean; the census's residue period/onset_depth are not a specified min-plus preperiod. Supply per-family horizons under a declared definition.",
    "Which relation constrains the full-tree frontier: the usual limit G, TOP, a terminal NAE call, or another stated relation? The ray reference's G frontier does not select the full-tree convention.",
    "Does the full-tree target minimum include all root S calls, or only the first root entry retained by the prescribed unchanged census start? These are different when main has several S calls.",
    "Does the required main endpoint lie in the main ports as in the prescribed census start, or anywhere in C0 as the object paragraph states? Main member sets themselves include ports and own distinctions.",
]
BRUTE_REQUIREMENTS = dict(families=120, at_least_each_available_class=10,
                          at_least_several_definitions=40, at_least_c_ge_3=20,
                          depths="all s=1..(per-family graph preperiod+period)",
                          member_search_through=7, maximum_unfolded_distinctions=22,
                          dp_over_7_agrees_with="none up to 7")


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def permitted(path):
    path = Path(path).resolve()
    if not path.is_relative_to(HERE):
        raise ValueError(f"output must be inside CODEX: {path}")
    return path


def dump(path, value):
    path = permitted(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    tmp.replace(path)


def _sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _file_sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _code_fingerprint(seconds, node_cap):
    modules = (P, C, C.GA, C.L, C.LS, C.REF)
    files = {Path(__file__).resolve(), HERE / "call_symmetry.py",
             *(Path(module.__file__).resolve() for module in modules)}
    return dict(seconds=seconds, node_cap=node_cap,
                code={str(path.relative_to(ROOT)): _file_sha(path) for path in sorted(files)},
                census_archive_sha256=_file_sha(P.CENSUS_RECORDS))


def read_rows(path, *, recover=False):
    path = Path(path)
    if not path.exists():
        return []
    rows, offset = [], 0
    size = path.stat().st_size
    with path.open("rb") as stream:
        for number, line in enumerate(stream, 1):
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                if recover and stream.tell() == size:
                    permitted(path)
                    tail = path.with_name(path.name + ".interrupted_tail." + hashlib.sha256(line).hexdigest() + ".bin")
                    if tail.exists() and tail.read_bytes() != line:
                        raise ValueError("interrupted-tail preservation collision")
                    if not tail.exists():
                        tail.write_bytes(line)
                    with path.open("r+b") as repair:
                        repair.truncate(offset)
                    break
                raise ValueError(f"invalid JSONL at {path}:{number}; no earlier bytes were changed") from exc
            offset += len(line)
    if recover and rows and offset == size and size and not line.endswith(b"\n"):
        with permitted(path).open("ab") as stream:
            stream.write(b"\n")
    return rows


def last_grower_cases(census_records=None):
    """The 224 positives in the original BD 664 panel, with ORIGINAL keys.

    The full A79 census has many more one-definition growers. The original
    panel is the one named by the frozen number 224, not all one-definition
    census records and not the unrelated census g3_keys panel. A positive PR
    cycle mean alone does not make a census grower: three PR-positive cases
    (indices 692,847,1018) are unresolved at the census's tighter resource caps.
    """
    V = _load("_paths_original_gate_validation", P.CENSUS_DIR / "validation.py")
    cases = V.gate664_cases(all_664=True)
    originals = V.DP.LS.families()
    selected = []
    records = P.load_census_records() if census_records is None else census_records
    for case in cases:
        defs = originals[case["idx"]]
        key = C.canonical(defs)
        archived = records.get(key)
        if archived is None:
            raise ValueError(f"original BD panel idx {case['idx']} has no original-key census record")
        if archived.get("class") != "grows":
            continue
        rate = archived.get("lambda")
        if archived.get("complete") is not True or archived.get("status") != "done" or rate is None or Fraction(rate) <= 0:
            raise ValueError(f"census grower idx {case['idx']} fails the complete positive-rate gate")
        selected.append(dict(key=key, idx=case["idx"], gate664_usual_key=case["key"],
                             pr_lambda=case["pr"].get("lambda"), census_lambda=rate,
                             census=archived))
    if len(selected) != 224 or len({r["key"] for r in selected}) != 224:
        raise ValueError(f"original BD panel selects {len(selected)} complete census growers; expected 224 distinct keys")
    return sorted(selected, key=lambda r: r["key"])


def write_last_keys(cases, path=None):
    path = HERE / "gate_last_keys.json" if path is None else permitted(path)
    manifest = dict(keys=[case["key"] for case in cases], count=len(cases),
                    selection="original664 from census validation.gate664_cases(all_664=True), joined by original LS.families()[idx] keys; select archived census class='grows' and require status='done',complete=True,exact lambda>0",
                    selection_audit=dict(original_panel=664, selected_complete_census_growers=224,
                                         PR_positive_rows=227, PR_complete_positive_rows=226,
                                         PR_incomplete_positive_rows=1,
                                         PR_positive_census_unresolved_rows=3,
                                         excluded_PR_positive_but_census_unresolved_indices=[692, 847, 1018],
                                         reason="all3 have incomplete300000-node census graphs; PR's larger cap yields226 complete positives plus1 incomplete positive, which is not the frozen census grower population"),
                    source_paths=dict(validation=str((P.CENSUS_DIR / "validation.py").relative_to(ROOT)),
                                      pr=str((C.PR_DIR / "rates_all.jsonl").relative_to(ROOT)),
                                      original_families="LIMIT-STATE census.LS.families (original LIMIT-ONLY repository archives)",
                                      census_archive=str(P.CENSUS_RECORDS.relative_to(ROOT))),
                    source_sha256=dict(validation=_file_sha(P.CENSUS_DIR / "validation.py"),
                                       pr=_file_sha(C.PR_DIR / "rates_all.jsonl"),
                                       census_archive=_file_sha(P.CENSUS_RECORDS)),
                    cases=[{k: v for k, v in case.items() if k != "census"} for case in cases],
                    archived_first_rows_available=sum(case["census"] is not None for case in cases))
    dump(path, manifest)
    return manifest


class ValidationLimit(RuntimeError):
    pass


class ResourceGuard(AbstractContextManager):
    """One current validation family, with a 3 GB stop and explicit alarm."""
    def __init__(self, seconds):
        self.seconds = seconds
        self.peak = 0
        self.stopping = threading.Event()

    def checkpoint(self):
        self.peak = max(self.peak, C.rss_bytes())
        if self.peak > OWN_MEMORY_BYTES:
            raise ValidationLimit("memory_limit: worker RSS exceeds 3 GB")
        if time.monotonic() - self.started > self.seconds:
            raise ValidationLimit("timeout: per-family validation alarm")

    def __enter__(self):
        self.started = time.monotonic()
        self.old_handlers = {sig: signal.getsignal(sig) for sig in (signal.SIGALRM, signal.SIGUSR1, signal.SIGUSR2)}

        def alarm(*_):
            raise ValidationLimit("timeout: per-family validation alarm")

        def memory(signum, _):
            raise ValidationLimit("aggregate_memory_limit" if signum == signal.SIGUSR1 else "memory_limit")

        signal.signal(signal.SIGALRM, alarm)
        signal.signal(signal.SIGUSR1, memory)
        signal.signal(signal.SIGUSR2, memory)
        signal.setitimer(signal.ITIMER_REAL, self.seconds)

        def watch():
            while not self.stopping.wait(.05):
                self.peak = max(self.peak, C.rss_bytes())
                if self.peak > OWN_MEMORY_BYTES:
                    os.kill(os.getpid(), signal.SIGUSR2)
                    return

        self.thread = threading.Thread(target=watch, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *args):
        while True:
            try:
                original_mask = signal.pthread_sigmask(signal.SIG_BLOCK, set())
                break
            except ValidationLimit:
                continue
        while True:
            try:
                signal.pthread_sigmask(signal.SIG_BLOCK, set(self.old_handlers))
                for sig in self.old_handlers:
                    signal.signal(sig, signal.SIG_IGN)
                break
            except ValidationLimit:
                continue
        signal.setitimer(signal.ITIMER_REAL, 0)
        self.stopping.set()
        self.thread.join()
        signal.pthread_sigmask(signal.SIG_SETMASK, original_mask)
        for sig, handler in self.old_handlers.items():
            signal.signal(sig, handler)
        return False


def _difference(mismatches, field, observed, expected, source, **context):
    if observed != expected:
        mismatches.append(dict(field=field, observed=observed, expected=expected,
                               source=source, **context))


def _graph_summary(graph, closes, zero, starts):
    return dict(nodes=len(graph), edges=sum(map(len, graph)),
                graph_sha256=_sha(graph), closes_sha256=_sha(closes),
                zero_successors_sha256=_sha(zero), starts_sha256=_sha(starts))


def check_reg(case, *, seconds=300, node_cap=300_000):
    """Force both graph builders, not a one_ray carry-over or settled row."""
    start = time.monotonic()
    key, archived = case["key"], case["census"]
    mismatches, pending = [], []
    row = dict(gate="G-reg", key=key, c=1, status="running", mismatches=mismatches,
               pending_comparisons=pending)
    try:
        with ResourceGuard(seconds) as guard:
            prep = C.Preparation(json.loads(key))
            old_ctx = C.FamilyDP(prep, "first", guard.checkpoint)
            old_progress = {}
            old_graph, old_closes, old_empty, old_starts = C.build_graph(old_ctx, old_progress, guard.checkpoint, node_cap)
            del old_ctx
            new_ctx = P.PathFamilyDP(prep, checkpoint=guard.checkpoint)
            new_progress = {}
            graph, closes, zero, starts, labels, states = P.build_path_graph(new_ctx, new_progress, guard.checkpoint, node_cap)
            del new_ctx, states
            old_zero = [tuple(() if successor is None else (successor,)) for successor in old_empty]
            old_summary = _graph_summary(old_graph, old_closes, old_zero, old_starts)
            new_summary = _graph_summary(graph, closes, zero, starts)
            row.update(census_graph=old_summary, path_graph=new_summary,
                       census_complete=old_progress.get("complete"), path_complete=new_progress.get("complete"))
            # Identical deterministic BFS ordering for c=1 makes these complete
            # graph digests compare the graph itself, not merely its metrics.
            for field in old_summary:
                _difference(mismatches, field, new_summary[field], old_summary[field], "fresh census graph")
            if not old_progress.get("complete") or not new_progress.get("complete"):
                pending.append(dict(kind="graph cap", census=old_progress, paths=new_progress))
            else:
                old = dict(old_progress, status="done")
                old.update(C.GA.analyze_graph(old_graph, old_closes, old_empty, True, guard.checkpoint))
                productive, cycles = C.productive_and_cycles(old_graph, old_closes, old_empty)
                exact = C.REF.exact_eventual_bound(old_graph, old_closes, old_starts, productive, cycles)
                old["exact_eventual_boundedness"] = exact
                old.update({field: exact.get(field) for field in ("eventually_bounded", "period", "uniform_cost_bound", "missing_residues")})
                old["class"] = C.classify(old)
                old["L_ray"] = C.recompute_layers(old_graph, old_closes, old_starts, 30, guard.checkpoint)
                new = dict(new_progress, status="done")
                new.update(P.analyze_path_graph(graph, closes, zero, starts, True,
                                               edge_labels=labels, checkpoint=guard.checkpoint))
                new["class"] = P.classify(new)
                new["L_path"] = C.recompute_layers(graph, closes, starts, 30, guard.checkpoint)
                for field in ("lambda", "class"):
                    _difference(mismatches, field, new.get(field), old.get(field), "fresh forced census")
                    _difference(mismatches, field, new.get(field), archived.get(field), "archived first census")
                _difference(mismatches, "L_path", new["L_path"], old["L_ray"], "fresh forced census")
                _difference(mismatches, "L_path", new["L_path"], archived.get("L_ray"), "archived first census")
                row.update(path_lambda=new.get("lambda"), census_lambda=old.get("lambda"),
                           path_class=new.get("class"), census_class=old.get("class"),
                           archived_class=archived.get("class"), L_path=new["L_path"])
            row["peak_rss_bytes"] = guard.peak
        row["status"] = "checked" if not pending else "incomplete"
    except (ValidationLimit, C.FamilyLimit, C.MemoryLimit, MemoryError) as exc:
        row.update(status="resource_stop", error=str(exc))
        pending.append(dict(kind="resource stop", error=str(exc)))
    except Exception as exc:
        row.update(status="error", error=repr(exc), traceback=traceback.format_exc())
        pending.append(dict(kind="execution error", error=repr(exc)))
    row.update(passed=False if mismatches else None if pending else True,
               seconds=time.monotonic() - start)
    return row


def _census_last_layers(key, seconds, node_cap):
    """Census last-call DP, stopping after the 30 required finite layers."""
    began = time.monotonic()
    result = dict(status="running", complete=False, L_ray=[], nodes=0)
    try:
        with ResourceGuard(seconds) as guard:
            prep = C.Preparation(json.loads(key))
            result.update(prep.info())
            if result["main_block_size"] > C.BLOCK_CAP or result["s_block_size"] > C.BLOCK_CAP:
                result["status"] = "block_size"
            else:
                ctx = C.FamilyDP(prep, "last", guard.checkpoint)
                graph, closes, empty, starts = C.build_graph(ctx, result, guard.checkpoint, node_cap)
                del ctx
                result["L_ray"] = C.recompute_layers(graph, closes, starts, 30, guard.checkpoint)
                result["status"] = "finite_layers"
            result["peak_rss_bytes"] = guard.peak
    except (ValidationLimit, C.FamilyLimit, C.MemoryLimit, MemoryError) as exc:
        result.update(status="resource_stop", error=str(exc))
    result["seconds"] = time.monotonic() - began
    return result


def check_last(case, *, seconds=300, node_cap=300_000):
    start = time.monotonic()
    key, archived = case["key"], case.get("census")
    new = P.compute_family(key, census_row=archived, seconds=seconds, node_cap=node_cap,
                           force_dp=True, check_fixed_rays=False, track_carried=False, values_only=True)
    last = _census_last_layers(key, seconds, node_cap)
    mismatches, pending = [], []
    for label, result in (("paths", new), ("last", last)):
        if result.get("status") != "finite_layers" or (label == "last" and result.get("complete") is not True):
            pending.append(dict(kind="computed comparator incomplete", comparator=label,
                                status=result.get("status"), complete=result.get("complete"),
                                nodes=result.get("nodes"), error=result.get("error")))
    if archived is None:
        pending.append(dict(kind="archived original-key first ray missing"))
    values = new.get("L_path", [])
    for label, reference in (("recomputed census last-call ray", last.get("L_ray", [])),
                             ("archived original-key first-call ray", [] if archived is None else archived.get("L_ray", []))):
        for depth in range(1, 31):
            observed = values[depth - 1] if depth <= len(values) else None
            expected = reference[depth - 1] if depth <= len(reference) else None
            if observed is None or expected is None:
                pending.append(dict(kind="required depth missing", source=label, s=depth,
                                    L_path=observed, upper_bound=expected))
            elif label == "recomputed census last-call ray" and not last.get("complete"):
                pending.append(dict(kind="last-ray reference not exact", source=label, s=depth))
            elif observed > expected:
                if new.get("complete"):
                    mismatches.append(dict(field="L_path<=L_ray", source=label, s=depth,
                                           observed=observed, upper_bound=expected))
                else:
                    pending.append(dict(kind="retained-path upper bound does not certify comparison",
                                        source=label, s=depth, retained_upper_bound=observed,
                                        reference=expected))
    return dict(gate="G-last", key=key, idx=case.get("idx"), c=P.self_call_count(key),
                passed=False if mismatches else None if pending else True,
                status="checked" if not pending else "incomplete", mismatches=mismatches,
                pending_comparisons=pending, L_path=values, L_last=last.get("L_ray", []),
                L_path_values_are_upper_bounds=not new.get("complete"),
                L_first=[] if archived is None else archived.get("L_ray", []),
                path_result=new, last_result=last, seconds=time.monotonic() - start)


def _direct_allowed(flat, G, chosen, *, side_top=False):
    allowed = []
    for state in range(1 << flat["V"]):
        good = True
        for call_index, (target, args) in enumerate(flat["calls"]):
            if call_index == chosen:
                continue
            bits = tuple((state >> variable) & 1 for variable in args)
            if target == "K":
                good = not (all(bit == 0 for bit in bits) or all(bit == 1 for bit in bits))
            elif not side_top:
                good = bool(G[target][sum(bit << i for i, bit in enumerate(bits))])
            if not good:
                break
        if good:
            allowed.append(state)
    return allowed


def _direct_full_table(flat, G, chosen, W):
    """Recompute every input relation and W assignment from raw joint states."""
    outgoing = flat["calls"][chosen][1]
    allowed = _direct_allowed(flat, G, chosen)
    table = []
    for incoming_relation in range(256):
        images = set()
        for fixed_members in range(1 << len(W)):
            image = 0
            for state in allowed:
                # The incoming interface is ALWAYS formal ports 0,1,2.
                incoming = sum(((state >> port) & 1) << port for port in range(3))
                if not (incoming_relation >> incoming) & 1:
                    continue
                if any(((state >> variable) & 1) != ((fixed_members >> j) & 1)
                       for j, variable in enumerate(W)):
                    continue
                child_ports = sum(((state >> variable) & 1) << j for j, variable in enumerate(outgoing))
                image |= 1 << child_ports
            images.add(image)
        table.append(sum(1 << image for image in images))
    return tuple(table)


def _table_image(collection, table):
    result = 0
    while collection:
        low = collection & -collection
        result |= table[low.bit_length() - 1]
        collection ^= low
    return result


def check_node():
    cases = [
        ("shared_argument", [(3, 2, [("K", (0, 3, 4)), ("SELF", (0, 3, 1)), ("SELF", (0, 4, 2))])]),
        ("repeated_argument", [(3, 1, [("K", (0, 1, 3)), ("SELF", (0, 0, 3)), ("SELF", (1, 3, 2))])]),
        ("nonchosen_limit_relation", [(3, 1, [("K", (0, 1, 3)), ("SELF", (0, 1, 2)), ("SELF", (0, 3, 2))])]),
    ]
    checks, mismatches = [], []
    rng = random.Random(1113)
    # Complete full/forgotten transfer-table agreement certifies every node;
    # these explicit applications additionally exercise collection indexing.
    nodes = [(0, 0), (1, 0), (1 << 255, 0), ((1 << 256) - 1, (1 << 256) - 1)]
    nodes += [(rng.getrandbits(256), rng.getrandbits(256)) for _ in range(32)]
    for name, defs in cases:
        prep = C.Preparation(defs)
        ctx = P.PathFamilyDP(prep)
        flat = prep.flat(prep.S)
        full_cache = {}
        side_exclusions = {}
        for op in ctx.middle_ops:
            chosen, W = op.flat_call_index, tuple(op.W)
            cache_key = (chosen, W)
            if cache_key not in full_cache:
                full_cache[cache_key] = _direct_full_table(flat, prep.G, chosen, W)
            direct = full_cache[cache_key]
            for relation in range(256):
                _difference(mismatches, "full_transfer", op.full[relation], direct[relation], name,
                            call_index=op.call_index, W=list(W), incoming_relation=relation)
            forgot = [full_cache.setdefault((chosen, W[:i] + W[i + 1:]),
                                           _direct_full_table(flat, prep.G, chosen, W[:i] + W[i + 1:]))
                      for i in range(len(W))]
            forgotten = tuple(__import__("functools").reduce(int.__or__, (table[r] for table in forgot), 0)
                              for r in range(256))
            for relation in range(256):
                _difference(mismatches, "forgotten_transfer", op.forgotten[relation], forgotten[relation], name,
                            call_index=op.call_index, W=list(W), incoming_relation=relation)
            for node_index, node in enumerate(nodes):
                expected = (_table_image(node[0], direct),
                            _table_image(node[1], direct) | _table_image(node[0], forgotten))
                _difference(mismatches, "advance", op.apply(node), expected, name,
                            call_index=op.call_index, W=list(W), node_index=node_index)
            side_exclusions[op.call_index] = len(set(_direct_allowed(flat, prep.G, chosen, side_top=True)) -
                                                 set(_direct_allowed(flat, prep.G, chosen)))
        if name == "nonchosen_limit_relation" and not any(side_exclusions.values()):
            mismatches.append(dict(field="side relation discriminating witness", source=name,
                                   expected="at least one assignment rejected by side G but admitted by TOP",
                                   observed=side_exclusions))
        checks.append(dict(case=name, key=C.canonical(defs), operations=len(ctx.middle_ops),
                           incoming_interface=[0, 1, 2], outgoing_interfaces=[list(flat["calls"][op.flat_call_index][1])
                                                                          for op in ctx.middle_ops if not op.W],
                           all_256_input_relations_checked=True, explicit_nodes_per_operation=len(nodes),
                           side_G_excludes_vs_TOP=side_exclusions))
    return dict(gate="G-node", status="checked", passed=not mismatches,
                cases=checks, mismatches=mismatches, pending_comparisons=[])


def _direct_layers(graph, closes, starts, depths=60):
    layer, values = dict(starts), []
    for _ in range(depths):
        values.append(min((cost + closes[u] for u, cost in layer.items()), default=INF))
        nxt = {}
        for u, cost in layer.items():
            for v, weight in graph[u]:
                nxt[v] = min(nxt.get(v, INF), cost + weight)
        layer = nxt
    return values


def check_zero_controls():
    """Analytic small-graph controls for the branching-zero residue extension."""
    controls = [
        dict(name="branch_away_from_nonclosing_zero_loop", graph=[[(0, 0), (1, 0)], [(1, 0)]],
             closes=[INF, 3], starts={0: 1}, eventual=True, rate="0/1"),
        dict(name="only_odd_depths_accept", graph=[[(1, 0)], [(0, 0)]],
             closes=[2, INF], starts={0: 1}, eventual=False, rate="0/1"),
        dict(name="branching_two_and_three_cycles", graph=[[(1, 0), (2, 0)], [(0, 0)], [(3, 0)], [(0, 0)]],
             closes=[2, INF, INF, INF], starts={0: 1}, eventual=True, rate="0/1"),
        dict(name="positive_cost_self_loop", graph=[[(0, 1)]],
             closes=[2], starts={0: 1}, eventual=False, rate="1/1"),
        dict(name="positive_entry_and_exit_retained", graph=[[(1, 5)], [(1, 0), (2, 7)], []],
             closes=[INF, INF, 4], starts={0: 3}, eventual=True, rate="0/1"),
        dict(name="positive_residue_connector", graph=[[(1, 0), (0, 1)], [(0, 0)]],
             closes=[2, INF], starts={0: 1}, eventual=True, rate="0/1"),
        dict(name="finite_accepting_walks_only", graph=[[(1, 0)], []],
             closes=[INF, 2], starts={0: 1}, eventual=False, rate=None),
    ]
    mismatches, checks = [], []
    for case in controls:
        zero = [tuple(v for v, weight in row if weight == 0) for row in case["graph"]]
        observed = P.analyze_path_graph(case["graph"], case["closes"], zero, case["starts"], True)
        _difference(mismatches, "eventually_bounded", observed.get("eventually_bounded"), case["eventual"], case["name"])
        _difference(mismatches, "lambda", observed.get("lambda"), case["rate"], case["name"])
        checks.append(dict(case=case, result=observed,
                           independently_replayed_depths_1_to_60=_direct_layers(case["graph"], case["closes"], case["starts"])))
    return dict(gate="branching-zero-controls", status="checked", passed=not mismatches,
                cases=checks, mismatches=mismatches, pending_comparisons=[])


def skipped_brute(computed_rows=()):
    unique = {row["key"]: row for row in computed_rows if "key" in row}
    classes = Counter(row.get("class_path", row.get("class", "unresolved")) for row in unique.values())
    return dict(gate="G-brute", status="skipped_ambiguity", passed=None,
                required_panel=BRUTE_REQUIREMENTS, planned_families=120,
                checked_families=0, skipped_families=120, checked_depths=0,
                questions=BRUTE_QUESTIONS, mismatches=[], pending_comparisons=BRUTE_QUESTIONS,
                supplied_computed_candidates=len(unique), supplied_candidate_classes=dict(classes),
                supplied_candidates_several_definitions=sum(len(json.loads(key)) > 1 for key in unique),
                supplied_candidates_c_ge_3=sum(P.self_call_count(key) >= 3 for key in unique),
                panel_selection="not selected while its per-family depth and unfolding semantics are undefined",
                implementation="brute_paths.py; direct full-assignment enumeration, independent of all DP code")


def _perform(job, config):
    gate, case = job
    try:
        row = (check_reg if gate == "G-reg" else check_last)(case, seconds=config["seconds"], node_cap=config["node_cap"])
    except Exception as exc:
        row = dict(gate=gate, key=case["key"], status="error", passed=None,
                   error=repr(exc), traceback=traceback.format_exc(), mismatches=[],
                   pending_comparisons=[dict(kind="uncaught validation execution error", error=repr(exc))])
    row["validation_config"] = config
    return row


def _worker(connection, config):
    signal.signal(signal.SIGUSR1, lambda *_: None)
    while True:
        job = connection.recv()
        if job is None:
            break
        connection.send(_perform(job, config))
    connection.close()


def run_jobs(gate, cases, output, *, workers, config):
    """A computing parent and N-1 children; newline/fsync after every family."""
    if not 1 <= workers <= 3:
        raise ValueError("workers must be 1..3, INCLUDING the computing parent")
    output = permitted(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    existing = read_rows(output, recover=True)
    seen = set()
    for row in existing:
        if row.get("validation_config") != config or row.get("gate") != gate:
            raise ValueError(f"{output} has a different validation configuration; choose a fresh --out-dir")
        if row["key"] in seen:
            raise ValueError(f"duplicate validation key in {output}")
        seen.add(row["key"])
    wanted = {case["key"] for case in cases}
    if len(wanted) != len(cases):
        raise ValueError("duplicate requested family key")
    tasks = deque((gate, case) for case in cases if case["key"] not in seen)
    rows = [row for row in existing if row["key"] in wanted]
    lock, write_lock = threading.Lock(), threading.Lock()
    stopped = threading.Event()
    ctx = mp.get_context("fork")
    children, active = {}, {}
    started = time.monotonic()
    peak = [C.rss_bytes()]
    memory_stops = []
    old_usr1 = signal.signal(signal.SIGUSR1, lambda *_: None)
    parent_busy = [False]

    def take():
        with lock:
            return tasks.popleft() if tasks else None

    try:
        for _ in range(min(workers - 1, max(0, len(tasks) - 1))):
            parent, child = ctx.Pipe()
            process = ctx.Process(target=_worker, args=(child, config))
            process.start()
            child.close()
            children[parent] = process
            job = take()
            parent.send(job)
            active[parent] = job
        with output.open("a", buffering=1) as journal:
            def append(row):
                with write_lock:
                    journal.write(json.dumps(row, sort_keys=True) + "\n")
                    journal.flush()
                    os.fsync(journal.fileno())
                    rows.append(row)
                    print(json.dumps(dict(gate=gate, completed=len(rows), total=len(cases),
                                          last_status=row.get("status"), last_passed=row.get("passed"),
                                          seconds=round(time.monotonic() - started, 3))), flush=True)

            def collect():
                while active and not stopped.is_set():
                    for connection in wait(list(active), timeout=.25):
                        job = active[connection]
                        try:
                            row = connection.recv()
                        except (EOFError, OSError):
                            row = dict(gate=gate, key=job[1]["key"], status="error", passed=None,
                                       mismatches=[], pending_comparisons=[dict(kind="owned child exited without a row")],
                                       validation_config=config)
                        append(row)
                        next_job = take() if children[connection].is_alive() else None
                        if children[connection].is_alive():
                            connection.send(next_job)
                        if next_job is None:
                            active.pop(connection)
                        else:
                            active[connection] = next_job

            def monitor():
                while not stopped.wait(.1):
                    owned = {process.pid: C.rss_bytes(process.pid) for process in children.values() if process.is_alive()}
                    owned[os.getpid()] = C.rss_bytes()
                    total = sum(owned.values())
                    peak[0] = max(peak[0], total)
                    if total > AGGREGATE_MEMORY_BYTES:
                        running = {pid: rss for pid, rss in owned.items() if pid != os.getpid() or parent_busy[0]}
                        if running:
                            pid = max(running, key=running.get)
                            try:
                                os.kill(pid, signal.SIGUSR1)
                                memory_stops.append(dict(pid=pid, aggregate_rss_bytes=total))
                            except ProcessLookupError:
                                pass

            collector = threading.Thread(target=collect, daemon=True)
            watcher = threading.Thread(target=monitor, daemon=True)
            collector.start()
            watcher.start()
            try:
                while (job := take()) is not None:
                    parent_busy[0] = True
                    append(_perform(job, config))
                    parent_busy[0] = False
                collector.join()
            finally:
                parent_busy[0] = False
                stopped.set()
                watcher.join()
                if collector.is_alive():
                    collector.join(timeout=.5)
    finally:
        stopped.set()
        for connection, process in children.items():
            if process.is_alive() and process.exitcode is None:
                # Normal workers have already received None. On interruption
                # terminate only children started by this invocation.
                process.join(timeout=.5)
                if process.is_alive():
                    process.terminate()
            process.join()
            connection.close()
        signal.signal(signal.SIGUSR1, old_usr1)
    mismatches = [dict(key=row["key"], **mismatch) for row in rows for mismatch in row.get("mismatches", [])]
    pending = [dict(key=row["key"], comparison=item) for row in rows for item in row.get("pending_comparisons", [])]
    return dict(gate=gate, requested=len(cases), rows=len(rows), passed=False if mismatches else None if pending or len(rows) != len(cases) else True,
                mismatches=mismatches, pending_comparisons=pending,
                result_path=str(output.relative_to(ROOT)), workers=workers,
                processes_include_parent=True, aggregate_peak_rss_bytes=peak[0],
                memory_stops=memory_stops, seconds=time.monotonic() - started,
                passed_rows=sum(row.get("passed") is True for row in rows),
                failed_rows=sum(row.get("passed") is False for row in rows),
                incomplete_rows=sum(row.get("passed") is None for row in rows))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gates", nargs="+", choices=("reg", "last", "node", "controls", "brute"),
                        default=["node", "controls", "reg", "last", "brute"])
    parser.add_argument("--all", action="store_true", help="explicitly request the complete gate list (the default)")
    parser.add_argument("--workers", type=int, choices=(1, 2, 3), default=1)
    parser.add_argument("--out-dir", type=Path, default=HERE)
    parser.add_argument("--seconds", type=float, default=300)
    parser.add_argument("--node-cap", type=int, default=300_000)
    parser.add_argument("--reg-count", type=int, default=500)
    parser.add_argument("--last-count", type=int, default=224,
                        help="sorted manifest prefix; hand-off two uses 60, full runner uses 224")
    parser.add_argument("--include-earlier-last-failures", action="store_true")
    parser.add_argument("--computed-jsonl", action="append", type=Path, default=[])
    parser.add_argument("--prepare-last-keys", action="store_true",
                        help="write gate_last_keys.json for the exact224, then stop without gates")
    args = parser.parse_args()
    if args.all:
        args.gates = ["node", "controls", "reg", "last", "brute"]
    if args.seconds <= 0 or args.node_cap <= 0 or args.reg_count <= 0:
        parser.error("seconds, node-cap, reg-count must be positive")
    out = permitted(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    records = None
    if args.prepare_last_keys or any(gate in args.gates for gate in ("reg", "last")):
        records = P.load_census_records()
    if args.prepare_last_keys:
        manifest = write_last_keys(last_grower_cases(records))
        print(json.dumps(dict(gate_last_keys=224, archived_first_rows_available=manifest["archived_first_rows_available"])), flush=True)
        return
    config = _code_fingerprint(args.seconds, args.node_cap)
    summary = dict(validation_config=config, gates={})
    for gate in args.gates:
        if gate == "node":
            result = check_node()
        elif gate == "controls":
            result = check_zero_controls()
        elif gate == "brute":
            path = HERE / "brute" / "brute_summary.json"
            result = json.loads(path.read_text()) if path.exists() else dict(
                gate="G-brute", status="run_separately", passed=None, mismatches=[],
                pending_comparisons=["Run run_brute.py after smoke; independent panel output not present."])
        elif gate == "reg":
            keys = sorted(key for key, row in records.items()
                          if P.self_call_count(key) == 1 and row.get("status") == "done"
                          and row.get("complete") is True
                          and row.get("main_block_size", 13) <= 12
                          and row.get("s_block_size", 13) <= 12)
            selected = keys[:args.reg_count]
            cases = [dict(key=key, census=records[key]) for key in selected]
            result = run_jobs("G-reg", cases, out / "validation_reg.jsonl", workers=args.workers, config=config)
            result.update(required_families=500, available_families=len(keys),
                          selection="first500 lexicographically sorted c=1 archived done/complete families within 12-distinction block cap; force both graph builders",
                          selected_keys=selected)
            if len(selected) != 500:
                result["passed"] = None if not result["mismatches"] else False
                result["pending_comparisons"].append(dict(kind="required500 coverage incomplete", selected=len(selected)))
        else:
            manifest = json.loads((HERE / "gate_last_keys.json").read_text())
            keys = sorted(manifest["keys"])
            selected = set(keys[:args.last_count])
            earlier = []
            if args.include_earlier_last_failures:
                earlier = json.loads((HERE / "earlier_last_failed_keys.json").read_text())
                selected.update(earlier)
            lookup = {case["key"]:case for case in manifest["cases"]}
            cases = [dict(lookup.get(key, {}), key=key, census=records[key]) for key in keys if key in selected]
            result = run_jobs("G-last", cases, out / "validation_last.jsonl", workers=args.workers, config=config)
            result.update(required_families=len(cases), full_run_required_families=224,
                          sorted_prefix=args.last_count, earlier_failed_keys=earlier,
                          earlier_failed_keys_found=len(earlier), selection_manifest="gate_last_keys.json",
                          archived_first_rows_available=manifest["archived_first_rows_available"])
        summary["gates"][result["gate"]] = result
        dump(out / ("validation_" + gate + "_summary.json"), result)
        dump(out / "validation_summary.json", summary)
        print(json.dumps(dict(gate=result["gate"], passed=result.get("passed"),
                              mismatches=len(result.get("mismatches", [])),
                              pending=len(result.get("pending_comparisons", [])))), flush=True)


if __name__ == "__main__":
    main()
