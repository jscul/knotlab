"""Rebuild the archived live rosters without expanding their unread successors."""

from argparse import ArgumentParser
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from functools import cache
import gzip
from hashlib import sha256
import io
from itertools import permutations
import json
from pathlib import Path
import subprocess
import sys
from tempfile import NamedTemporaryFile, TemporaryDirectory, TemporaryFile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARTIFACTS = ROOT / "artifacts" / HERE.parent.name / HERE.name
DEFAULT = Path("/var/tmp/hub-sample-20261119")
WALL = ROOT / "artifacts/WALL-READ-20261119-001B/WALL-READ-20261119-001B-E001_past/results.json"
MERGE = ROOT / "runs/merge-burst/results.jsonl"
PRIOR = ROOT / "artifacts/NINTH-ROUND-SAMPLE-20261119-001/NINTH-ROUND-SAMPLE-20261119-001-E001_estimate"
CONTROLS = ARTIFACTS / "control_rosters.json"
SUMMARY = ARTIFACTS / "stages.json"
UNREAD = tuple(f"start-{i:02d}" for i in range(1, 16) if i != 4)
sys.path.insert(0, str(ROOT / "proofs/WALL-READ-20261119-001A/WALL-READ-20261119-001A-P001_partnered"))
import rosterlib as archived


def vertices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def mask_of(names):
    return sum(1 << n for n in names)


@cache
def archive_inputs():
    sys.path.insert(0, str(ROOT / "scripts"))
    from longrun import load_results

    if MERGE.is_file():
        rows = load_results(MERGE)
        assert all(r["status"] == "ok" for r in rows.values())
        starts = {tag: row["result"]["start"] for tag, row in rows.items()}
    else:
        starts = json.loads(SUMMARY.read_text())["literal_starts"]
    summaries = json.loads(WALL.read_text())["follow"]
    assert set(starts) == set(summaries) == {*UNREAD, "start-00", "start-04"}
    return starts, summaries


def digest(path):
    with path.open("rb") as stream:
        digestor = sha256()
        while block := stream.read(1 << 20):
            digestor.update(block)
    return digestor.hexdigest()


def write_at(path, write, *, compressed=False, preserve_identical=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=path.parent, prefix="stages_pending_", delete=False) as raw:
        pending = Path(raw.name)
        if compressed:
            with gzip.GzipFile(fileobj=raw, filename="", mode="wb", mtime=0, compresslevel=4) as payload:
                with io.TextIOWrapper(payload, encoding="ascii", newline="\n") as stream:
                    write(stream)
        else:
            with io.TextIOWrapper(raw, encoding="ascii", newline="\n") as stream:
                write(stream)
    value = digest(pending)
    if preserve_identical and path.exists():
        try:
            assert value == digest(path), f"Existing shared baseline has different contents: {path}"
        finally:
            pending.unlink()
    else:
        pending.replace(path)
    return value


@dataclass(frozen=True)
class Stage:
    size: int
    blocks: tuple
    parent_masks: tuple | None
    previous_live: int
    births: int | None
    opens: tuple | None = None
    closing_parents: int | None = None


def exact_degrees(n, blocks):
    """One adjacency union at a time, storing only block masks and incidence."""
    profiles = [[] for _ in range(n)]
    masks = []
    for i, block in enumerate(blocks):
        packed = bytearray((n + 7) // 8)
        for v in block:
            packed[v >> 3] |= 1 << (v & 7)
            profiles[v].append(i)
        masks.append(int.from_bytes(packed, "little"))

    cached = {}
    result = [0] * n
    for v, profile in enumerate(profiles):
        key = tuple(profile)
        if key not in cached:
            neighbors = 0
            for i in key:
                neighbors |= masks[i]
            cached[key] = max(0, neighbors.bit_count() - 1)
        result[v] = cached[key]
    return result


def write_stage(folder, tag, age, stage, *, role, known_next=None, engine="archive roster", preserve_blocks=False):
    stem = f"{tag}-age{age:02d}"
    n, blocks = stage.size, stage.blocks

    def put_blocks(stream):
        print(n, len(blocks), file=stream)
        for block in blocks:
            stream.write(" ".join(map(str, block)) + "\n")

    text = folder / (stem + ".txt")
    files = {"blocks": {"name": text.name, "sha256": write_at(text, put_blocks, preserve_identical=preserve_blocks)}}
    degrees = exact_degrees(n, blocks)
    parents = stage.parent_masks
    offshoots = None
    if parents is not None:
        assert len(parents) == n and all(parents)
        name = folder / (stem + ".parents.json.gz")

        def put_parents(stream):
            stream.write("[\n")
            for i, mask in enumerate(parents):
                if i:
                    stream.write(",\n")
                stream.write(json.dumps(list(vertices(mask)), separators=(",", ":")))
            stream.write("\n]\n")

        files["parents"] = {"name": name.name, "sha256": write_at(name, put_parents, compressed=True)}
        single_parent = [[v, degrees[v], max(0, 2 - degrees[v])] for v, mask in enumerate(parents)
                         if mask.bit_count() == 1]
        offshoots = sum(row[2] for row in single_parent) + sum(d == 0 and mask.bit_count() >= 2
                                                              for d, mask in zip(degrees, parents, strict=True))
        incidence = sum(mask.bit_count() for mask in parents)
        arities = dict(sorted(Counter(mask.bit_count() for mask in parents).items()))
    else:
        single_parent = []
        incidence = None
        arities = None
        if stage.opens is not None:
            if len(blocks) == 1 and len(blocks[0]) == n:
                used = dict.fromkeys(range(n), n - 1)
            else:
                groups = archived.groups_of(list(range(n)), [frozenset(b) for b in blocks])
                used = Counter(v for group in groups for v in group)
            assert all(used[v] <= supply for v, supply in enumerate(stage.opens))
            offshoots = sum(supply - used[v] for v, supply in enumerate(stage.opens))

    name = folder / (stem + ".degrees.json.gz")
    files["degrees"] = {"name": name.name, "sha256": write_at(
        name, lambda f: json.dump(degrees, f, separators=(",", ":")), compressed=True)}
    if stage.opens is not None:
        name = folder / (stem + ".opens.json.gz")
        files["opens"] = {"name": name.name, "sha256": write_at(
            name, lambda f: json.dump(stage.opens, f, separators=(",", ":")), compressed=True)}
    meta = {"case": tag, "age": age, "target_round": age + 1, "role": role, "engine": engine,
            "live": n, "births": stage.births, "closed": n == 0, "blocks": len(blocks),
            "largest_block": max(map(len, blocks), default=0),
            "previous_live": stage.previous_live, "parent_sum": incidence, "parent_arities": arities,
            "candidate_pairs": sum(degrees) // 2, "degree_histogram": dict(sorted(Counter(degrees).items())),
            "isolated": degrees.count(0), "single_parent_cases": single_parent, "exact_offshoots": offshoots,
            "known_next_births": known_next, "files": files}
    if parents is not None:
        meta["parent_numbering"] = "zero-based positions in ascending previous live roster order"
        meta["open_count_rule"] = "at open reached junction p: max(number of current groups through p, 3 - parent count, 1)"
    if stage.closing_parents is not None:
        meta["closed_birth_parents"] = list(vertices(stage.closing_parents))
    path = folder / (stem + ".meta.json")
    write_at(path, lambda f: json.dump(meta, f, indent=2, sort_keys=True))
    return meta


def supply_from_next(folder, previous, following):
    """Each next birth spends one loose distinction at each of its parents."""
    n = previous["live"]
    assert n == following.previous_live
    supply = [0] * n
    masks = following.parent_masks if following.closing_parents is None else (following.closing_parents,)
    for mask in masks:
        for i in vertices(mask):
            supply[i] += 1
    assert all(supply)
    stem = f"{previous['case']}-age{previous['age']:02d}"
    sidecar = folder / (stem + ".opens.json.gz")
    previous["files"]["opens"] = {"name": sidecar.name, "sha256": write_at(
        sidecar, lambda f: json.dump(supply, f, separators=(",", ":")), compressed=True)}
    previous["open_sum"] = sum(supply)
    write_at(folder / (stem + ".meta.json"), lambda f: json.dump(previous, f, indent=2, sort_keys=True))


class ReachedTarget(Exception):
    pass


def archive_replay(tag, wanted, callback):
    starts, counts = archive_inputs()
    start, history = starts[tag], counts[tag]
    opens, blocks = archived.roster_of(start["sizes"], start["edges"])
    ages = set(wanted)
    last = max(ages)
    previous = None

    def save(age, points, blocks, parents):
        nonlocal previous
        points = sorted(points)
        ids = {x: i for i, x in enumerate(points)}
        arity = len(points)
        normalized = tuple(sorted(tuple(sorted(ids[v] for v in block)) for block in blocks))
        closed = age > 0 and arity == 1
        if age > 0:
            assert arity == history["counts"][age - 1], (tag, age, arity)
            assert max(map(len, normalized), default=0) == history["largest_block"][age - 1], (tag, age)
            masks = tuple(mask_of(previous[parent] for parent in parents[p]) for p in points)
            previous_live = len(previous)
        else:
            masks = None
            previous_live = 0
        if age in ages:
            frame = Stage(0 if closed else arity, normalized, () if closed else masks,
                          previous_live, arity if age > 0 else None, tuple(opens) if age == 0 else None,
                          masks[0] if closed else None)
            callback(age, frame)
        if age == last:
            raise ReachedTarget
        previous = ids

    try:
        for _ in archived.grow(opens, blocks, last, on_stage=save):
            pass
    except ReachedTarget:
        return
    raise RuntimeError(f"{tag} stopped before archive stage {last}")


def early_start03(folder):
    expected = json.loads((PRIOR / "path_risk.json").read_text())
    emitted = []

    def export(age, stage):
        role = "first_unread" if age == 8 else "exact_control"
        meta = write_stage(folder, "start-03", age, stage, role=role, known_next=28065 if age == 7 else None,
                           preserve_blocks=True)
        assert meta["files"]["blocks"]["sha256"] == expected[f"age{age}"]["sha256"]
        assert meta["exact_offshoots"] == 1
        if age == 7:
            meta["truth"] = {"births": 28065, "large_groups": 28008, "residual_pairs": 56,
                             "offshoots": 1, "raw_maximal_cliques": 28099, "held_maximal_cliques": 91}
            write_at(folder / "start-03-age07.meta.json", lambda f: json.dump(meta, f, indent=2, sort_keys=True))
        prior_parents = folder / f"seed-03-parent-baseline-age{age}.json"
        if prior_parents.exists():
            disjoint = json.loads(prior_parents.read_text())
            names = sorted({p for row in disjoint for p in row})
            translate = {p: i for i, p in enumerate(names)}
            assert len(names) == stage.previous_live
            assert tuple(mask_of(translate[p] for p in row) for row in disjoint) == stage.parent_masks
        if emitted:
            supply_from_next(folder, emitted[-1], stage)
            assert emitted[-1]["open_sum"] == meta["parent_sum"] == 993164
        emitted.append(meta)

    archive_replay("start-03", (7, 8), export)
    return emitted


def compile_native(folder):
    program = folder / "stages-groups"
    subprocess.run(["c++", "-std=c++20", "-O3", str(HERE / "stages_groups.cpp"), "-o", str(program)], check=True)
    return program


def native_groups(binary, path):
    with TemporaryFile(mode="w+t", encoding="ascii") as output:
        subprocess.run([binary, path], stdout=output, check=True)
        output.seek(0)
        return [mask_of(map(int, line.split())) for line in output]


def transpose(parent_masks, previous_live):
    packed = [bytearray((len(parent_masks) + 7) // 8) for _ in range(previous_live)]
    for child, parents in enumerate(parent_masks):
        for p in vertices(parents):
            packed[p][child >> 3] |= 1 << (child & 7)
    candidates = sorted({int.from_bytes(buf, "little") for buf in packed}, key=lambda m: (-m.bit_count(), m))
    maximal = []
    for block in candidates:
        if block.bit_count() < 2:
            break
        if not any(block & other == block for other in maximal):
            maximal.append(block)
    return tuple(sorted(tuple(vertices(block)) for block in maximal))


def read_parents(path):
    with gzip.open(path, "rt", encoding="ascii") as stream:
        assert stream.readline().strip() == "["
        for line in stream:
            row = line.strip().removesuffix(",")
            if row == "]":
                return
            yield mask_of(json.loads(row))
    raise ValueError(f"Unclosed parent file {path}")


def one_native_successor(folder, tag, age, previous):
    """Finish the already archived last birth of start-01 in its precursor numbering."""
    with TemporaryDirectory(prefix="prespatial-stage-native-") as temporary:
        program = compile_native(Path(temporary))
        groups = native_groups(program, folder / previous["files"]["blocks"]["name"])
    parents = tuple(read_parents(folder / previous["files"]["parents"]["name"]))
    demand = Counter(p for group in groups for p in vertices(group))
    for p, mask in enumerate(parents):
        groups.extend([1 << p] * max(0, max(3 - mask.bit_count(), 1) - demand[p]))
    n = len(groups)
    assert (tag, age, len(parents), n) == ("start-01", 10, 1522, 21516)
    return Stage(n, transpose(groups, len(parents)), tuple(groups), len(parents), n)


def export_archive_case(folder, tag):
    _, summaries = archive_inputs()
    history = summaries[tag]
    counts = history["counts"]
    latest = history["last_t"]
    assert latest == len(counts)
    if tag == "start-03":
        return early_start03(folder)
    if tag == "start-00":
        ages = tuple(range(15, latest + 1))
    else:
        ages = tuple(sorted({latest - 1, latest} | ({8} if latest > 8 else set())))
    actual = []

    def export(age, stage):
        if tag == "start-00":
            role = "exact_control"
        elif age == latest:
            role = "first_unread"
        elif age == latest - 1:
            role = "last_built_precursor"
        else:
            role = "earlier_round_nine"
        known = counts[age] if age < latest else 0 if stage.size == 0 else None
        grew_natively = tag == "start-01" and age == latest
        engine = "native exact parent groups" if grew_natively else "archive roster"
        meta = write_stage(folder, tag, age, stage, role=role, known_next=known, engine=engine)
        row = history["stages"][str(age)]
        assert meta["births"] == row["points"] == counts[age - 1]
        assert meta["blocks"] == row["blocks"]
        if "edges" in row:
            assert meta["candidate_pairs"] == row["edges"]
            assert (meta["isolated"] if stage.size else 1) == row["lone"]
        if str(age - 1) in history["double_count"]:
            loose_total, written_parent_total = history["double_count"][str(age - 1)]
            parent_total = meta["parent_sum"] if stage.size else stage.closing_parents.bit_count()
            assert parent_total == loose_total
            assert written_parent_total is None or parent_total == written_parent_total
        archived_groups = next((r["groups_next"] for r in history["checks"] if r["t"] == age), None)
        if archived_groups is not None and known is not None:
            assert meta["exact_offshoots"] == known - archived_groups
        if tag == "start-00":
            legal = archived.groups_of(list(range(stage.size)), [frozenset(b) for b in stage.blocks])
            pairs = sum(len(group) == 2 for group in legal)
            meta["truth"] = {"large_groups": len(legal) - pairs, "residual_pairs": pairs,
                             "offshoots": meta["exact_offshoots"], "births": known}
            assert len(legal) + meta["exact_offshoots"] == known
            write_at(folder / f"{tag}-age{age:02d}.meta.json", lambda f: json.dump(meta, f, indent=2, sort_keys=True))
        if actual and actual[-1]["age"] == age - 1:
            supply_from_next(folder, actual[-1], stage)
            if str(age - 1) in history["double_count"]:
                assert actual[-1]["open_sum"] == history["double_count"][str(age - 1)][0]
        actual.append(meta)

    if tag == "start-01":
        archive_replay(tag, ages[:-1], export)
        export(latest, one_native_successor(folder, tag, latest, actual[-1]))
    else:
        archive_replay(tag, ages, export)
    assert actual[-1]["age"] == latest
    if tag == "start-00":
        assert actual[-1]["closed"] and actual[-1]["known_next_births"] == 0
    return actual


FOLDER = DEFAULT


def setup(params):
    global FOLDER
    FOLDER = Path(params.get("folder", DEFAULT))
    archive_inputs()


def cases():
    for tag in (*UNREAD, "start-00"):
        if tag != "start-03":
            yield tag, tag


def run(case_id, tag):
    assert case_id == tag
    return export_archive_case(FOLDER, tag)


def controls_into(folder):
    selected = []
    for row in json.loads(CONTROLS.read_text()):
        tag, age = row["name"], row["age"]
        if tag == "start-03":
            assert row["truth"]["births"] == 28065
            continue  # The byte-identical archive export supplies its parent arrays.
        n = len(row["loose"])
        stage = Stage(n, tuple(tuple(b) for b in row["blocks"]), None, 0, n if age else None, tuple(row["loose"]))
        truth = row.get("truth", {})
        known = row.get("known_births", truth.get("births"))
        if tag == "partner-5" and age == 1 and known is None:
            assert n == 32 and len(stage.blocks) == 10 and all(len(block) == 16 for block in stage.blocks)
            group_rows = archived.groups_of(list(range(n)), [frozenset(b) for b in stage.blocks])
            assert len(group_rows) == (1 << 16) - 10 and all(len(group) == 16 for group in group_rows)
            known = len(group_rows)
            truth = {"large_groups": known, "residual_pairs": 0, "offshoots": 0,
                     "births": known, "raw_maximal_cliques": 1 << 16, "held_maximal_cliques": 10}
        assert known is not None
        meta = write_stage(folder, tag, age, stage, role="exact_control", known_next=known,
                           engine="independent control replay", preserve_blocks=True)
        assert meta["files"]["blocks"]["sha256"] == row["blocks_sha256"]
        if truth:
            assert meta["exact_offshoots"] == truth["offshoots"]
            meta["truth"] = truth
        if tag == "start-04" and age == 8:
            assert (n, meta["blocks"], meta["candidate_pairs"], meta["exact_offshoots"], known) == (781, 1, 304590, 0, 304590)
            meta["truth"] = {"births": known, "large_groups": 0, "residual_pairs": 304590, "offshoots": 0}
        write_at(folder / f"{tag}-age{age:02d}.meta.json", lambda f: json.dump(meta, f, indent=2, sort_keys=True))
        selected.append(meta)
    return selected


def block_keys(path, image=None):
    with path.open("r", encoding="ascii") as stream:
        n, b = map(int, next(stream).split())
        result = set()
        for line in stream:
            packed = bytearray((n + 7) // 8)
            for x in map(int, line.split()):
                v = x if image is None else image[x]
                packed[v >> 3] |= 1 << (v & 7)
            result.add(int.from_bytes(packed, "little"))
    assert len(result) == b
    return n, result


def lift_parent_map(left, right, previous_map):
    targets = defaultdict(deque)
    for j, parents in enumerate(right):
        targets[parents].append(j)
    image = []
    for parents in left:
        moved = mask_of(previous_map[p] for p in vertices(parents))
        assert targets[moved]
        image.append(targets[moved].popleft())
    assert not any(targets.values())
    return image


def duplicate_audit(folder):
    """Lift a verified five-junction roster renaming to the literal huge inputs."""
    prefix = {}
    for tag in ("start-02", "start-05", "start-08"):
        frames = {}
        archive_replay(tag, range(9), frames.__setitem__)
        prefix[tag] = frames

    base = prefix["start-02"]
    reports = []
    for tag in ("start-05", "start-08"):
        target = prefix[tag]

        def agrees(left, right, image):
            assert left.size == right.size == len(image)
            return {mask_of(image[v] for v in b) for b in left.blocks} == set(map(mask_of, right.blocks))

        assert base[0].size == target[0].size == 5
        initial = next(p for p in permutations(range(5))
                       if base[0].opens == tuple(target[0].opens[v] for v in p) and agrees(base[0], target[0], p))
        image = initial
        for age in range(1, 9):
            left, right = base[age], target[age]
            image = lift_parent_map(left.parent_masks, right.parent_masks, image)
            assert agrees(left, right, image)
        left = folder / "start-02-age09"
        right = folder / f"{tag}-age09"
        at_eight = image
        assert block_keys(folder / "start-02-age08.txt", at_eight) == block_keys(folder / f"{tag}-age08.txt")
        image = lift_parent_map(read_parents(left.with_suffix(".parents.json.gz")),
                                read_parents(right.with_suffix(".parents.json.gz")), at_eight)
        assert len(image) == 102871 and len(set(image)) == len(image)
        assert block_keys(left.with_suffix(".txt"), image) == block_keys(right.with_suffix(".txt"))
        path = folder / f"{tag}-age09.map-from-02.json.gz"
        hashed = write_at(path, lambda f: json.dump(image, f, separators=(",", ":")), compressed=True)
        reports.append({"source": "start-02", "image": tag, "initial_live_map": initial, "age8_live_map": at_eight,
                        "age9_live_map": {"name": path.name, "sha256": hashed}, "matched_live": len(image),
                        "all_true_parent_incidences_and_maximal_blocks_match": True,
                        "byte_identical_labels": digest(left.with_suffix(".txt")) == digest(right.with_suffix(".txt"))})
    return reports


def crosscheck(folder, metas):
    """Replay exact legal multi-parent groups on every target's real precursor."""
    key = {(r["case"], r["age"]): r for r in metas}
    output = {}
    with TemporaryDirectory(prefix="prespatial-stage-audit-") as temporary:
        binary = compile_native(Path(temporary))
        for row in (r for r in metas if r["role"] == "first_unread"):
            previous = key[row["case"], row["age"] - 1]
            assert previous["live"] == row["previous_live"] and previous["known_next_births"] == row["live"]
            grouping = native_groups(binary, folder / previous["files"]["blocks"]["name"])
            groups = Counter(grouping)
            assert len(groups) == len(grouping)
            demand = Counter(p for group in grouping for p in vertices(group))
            with gzip.open(folder / previous["files"]["opens"]["name"], "rt", encoding="ascii") as f:
                supply = json.load(f)
            extras = [amount - demand[p] for p, amount in enumerate(supply)]
            assert min(extras) >= 0 and sum(extras) == previous["exact_offshoots"]
            groups.update({1 << p: extra for p, extra in enumerate(extras) if extra})
            actual = Counter(read_parents(folder / row["files"]["parents"]["name"]))
            assert actual == groups
            output[row["case"]] = {"multi_parent_groups": len(grouping), "offshoots": sum(extras),
                                   "parent_sets_compared": sum(actual.values()),
                                   "independent_from_export": row["engine"] == "archive roster"}
    return output


def collect(folder, output):
    starts, wall = archive_inputs()
    stages = list(controls_into(folder))
    for tag in (*UNREAD, "start-00"):
        allowed = {"first_unread", "last_built_precursor", "earlier_round_nine", "exact_control"}
        first = 15 if tag == "start-00" else 1
        for age in range(first, wall[tag]["last_t"] + 1):
            path = folder / f"{tag}-age{age:02d}.meta.json"
            if path.exists():
                row = json.loads(path.read_text())
                assert row["role"] in allowed
                stages.append(row)
    targets = {r["case"]: r for r in stages if r["role"] == "first_unread"}
    assert set(targets) == set(UNREAD)
    for tag, row in targets.items():
        assert (row["age"], row["live"]) == (wall[tag]["last_t"], wall[tag]["last_count"])
    for row in stages:
        for f in row["files"].values():
            assert digest(folder / f["name"]) == f["sha256"]
    assert {r["age"] for r in stages if r["case"] == "start-00"} == set(range(23))
    assert any(r["case"] == "start-00" and r["age"] == 22 and r["closed"] for r in stages)
    native = crosscheck(folder, stages)
    duplicates = duplicate_audit(folder)
    sources = (WALL, CONTROLS, PRIOR / "path_risk.json",
               Path(archived.__file__), HERE / "stages_groups.cpp", MERGE)
    result = {"literal_starts": starts, "inputs": {str(p.relative_to(ROOT)): digest(p) for p in sources if p.is_file()},
              "stages": sorted(stages, key=lambda r: (r["case"], r["age"])), "unread_cases": list(UNREAD),
              "target_precursor_comparisons": native, "exact_isomorphisms": duplicates}
    write_at(folder / "index.json", lambda f: json.dump(result, f, indent=2, sort_keys=True))
    write_at(output, lambda f: json.dump(result, f, indent=2, sort_keys=True))
    return {"targets": {tag: [r["age"], r["live"], r["target_round"]] for tag, r in targets.items()},
            "stages": len(stages), "native_comparisons": len(native), "isomorphisms": len(duplicates)}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--folder", type=Path, default=DEFAULT)
    sub = parser.add_subparsers(dest="command", required=True)
    single = sub.add_parser("one")
    single.add_argument("case", choices=(*UNREAD, "start-00"))
    sub.add_parser("controls")
    index = sub.add_parser("collect")
    index.add_argument("--output", type=Path, default=SUMMARY)
    args = parser.parse_args()
    if args.command == "one":
        result = [{k: row[k] for k in ("case", "age", "live", "target_round", "exact_offshoots")}
                  for row in export_archive_case(args.folder, args.case)]
    elif args.command == "controls":
        result = {"controls": len(controls_into(args.folder))}
    else:
        result = collect(args.folder, args.output)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
