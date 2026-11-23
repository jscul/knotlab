"""Build and hash the fresh panel of REVIEW-LEADS-20261123-001B-E001 (before any learner runs on it).

Run from the repository root:
    timeout 600 prlimit --as=12884901888 .venv/bin/python -B experiments/REVIEW-LEADS-20261123-001B/REVIEW-LEADS-20261123-001B-E001_example_knots/panel.py

Reuses the drawing generator of RELATIVE-PIXEL-READ-20261122-001 (make_drawing, turns, bitmap, normalize; imported
from its panel.py after a hash check, nothing copied or edited).  Differences from that generator's own selection,
all recorded in deviations.md: seed-salted ranking, rotation-class (quarter-turn) exclusion, global greedy choice of
16 L/T pairs instead of the quota table, positions drawn by seed.
"""

import argparse
import glob
import importlib.util
import json
import random
import sys
from collections import Counter
from hashlib import sha256
from itertools import product
from pathlib import Path

FAMILY = Path(__file__).resolve().parent
ROOT = FAMILY.parents[2]
TICKET = "REVIEW-LEADS-20261123-001B"
OUT = ROOT / "artifacts" / TICKET / f"{TICKET}-E001_example_knots" / "panel"

SEED = 2026112302
SHUFFLE_SEED = 2026112303
N_PAIRS = 16                                   # 16 L + 16 T = 32 designs D1..D32
N_POSITIONS = 8
DESIGN_SALT = f"review-leads-20261123-001b-seed-{SEED}-design:"
POSITION_SALT = f"review-leads-20261123-001b-seed-{SEED}-position:"
ORDER_SALT = f"review-leads-20261123-001b-seed-{SEED}-order:"
ANCHORS = tuple(product(range(4), repeat=2))
NARROW_DESIGNS, NARROW_POSITIONS = 4, 8
VARIED_DESIGNS, VARIED_POSITIONS = 16, 2
FIT_TURNS = (0, 1)
HELD_TURNS = (2, 3)

GENERATOR = ROOT / "experiments/RELATIVE-PIXEL-READ-20261122-001/RELATIVE-PIXEL-READ-20261122-001-E001_relative/panel.py"
EARLIER = ("PIXEL-LETTERS-20261122-001", "LEARNED-PATCH-GROUPS-20261122-001",
           "VARIED-LETTER-DRAWINGS-20261122-001", "RELATIVE-PIXEL-READ-20261122-001")


def load_generator():
    spec = importlib.util.spec_from_file_location("relative_pixel_panel", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def hexhash(data: bytes) -> str:
    return sha256(data).hexdigest()


def json_lines(rows) -> bytes:
    return "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows).encode("ascii")


def earlier_panels(g):
    files = []
    for ticket in EARLIER:
        files += sorted(glob.glob(str(ROOT / "experiments" / ticket / "*" / "panel" / "*.jsonl")))
    bitmaps, hashes = set(), {}
    for f in files:
        data = Path(f).read_bytes()
        hashes[str(Path(f).relative_to(ROOT))] = hexhash(data)
        for line in data.splitlines():
            row = json.loads(line)
            if "pixels" in row:
                bitmaps.add(row["pixels"])
    rot = {min(g.turns(g.bitmap_support(p))) for p in bitmaps}
    dih = {g.dihedral(g.bitmap_support(p)) for p in bitmaps}
    return bitmaps, rot, dih, hashes


def rank_key(base, col, bar_steps, stem_steps):
    descriptor = json.dumps([base, col, list(bar_steps), list(stem_steps)], separators=(",", ":"))
    return hexhash((DESIGN_SALT + descriptor).encode("ascii"))


def candidates(g, excluded_rot):
    """All admissible L/T pairs (both bases, every interior stem column), ranked by the seeded hash."""
    pool, seen = [], set()
    for base, (width, height) in g.DIMENSIONS.items():
        for col in range(1, width - 1):
            for bar_steps, stem_steps in product(product((-1, 0, 1), repeat=width - 1),
                                                 product((-1, 0, 1), repeat=height - 1)):
                bends = (any(bar_steps), any(stem_steps))
                if not any(bends):
                    continue
                ld = g.make_drawing(width, height, col, "L", bar_steps, stem_steps)
                td = g.make_drawing(width, height, col, "T", bar_steps, stem_steps)
                if ld is None or td is None:
                    continue
                lrot, trot = min(g.turns(ld.cells)), min(g.turns(td.cells))
                if lrot == trot or lrot in excluded_rot or trot in excluded_rot:
                    continue
                pool.append((rank_key(base, col, bar_steps, stem_steps), base, col, bar_steps, stem_steps,
                             {"horizontal": any(bar_steps) and not any(stem_steps),
                              "vertical": any(stem_steps) and not any(bar_steps)}, ld, td, lrot, trot))
    pool.sort(key=lambda row: (row[0], row[1], row[2], row[3], row[4]))
    unique = []
    for row in pool:                                   # first representative of each ordered pair of rotation classes
        if (row[8], row[9]) in seen:
            continue
        seen.add((row[8], row[9]))
        unique.append(row)
    return unique, len(pool)


def select(unique):
    chosen, used = [], set()
    for row in unique:
        if row[8] in used or row[9] in used:
            continue
        chosen.append(row)
        used.update((row[8], row[9]))
        if len(chosen) == N_PAIRS:
            break
    return chosen


def draw_positions(design_number):
    ranked = sorted(ANCHORS, key=lambda a: (hexhash(f"{POSITION_SALT}{design_number}:{a[0]},{a[1]}".encode("ascii")), a))
    return ranked[:N_POSITIONS]


def build():
    g = load_generator()
    old_bitmaps, rot_old, dih_old, old_hashes = earlier_panels(g)
    unique, raw = candidates(g, rot_old)
    chosen = select(unique)
    info = {"earlier_unique_bitmaps": len(old_bitmaps), "earlier_rotation_classes": len(rot_old),
            "earlier_dihedral_classes": len(dih_old), "candidate_pairs_rotation_exclusion_raw": raw,
            "candidate_pairs_distinct_rotation_class_pairs": len(unique), "pairs_selected": len(chosen)}
    if len(chosen) < N_PAIRS:
        raise SystemExit(f"Only {len(chosen)} fresh L/T pairs available; see deviations.md. info={info}")

    designs, images, keys = [], [], []
    for k, row in enumerate(chosen, 1):
        _, base, col, bar_steps, stem_steps, _, ld, td, lrot, trot = row
        bend = ("horizontal" if any(bar_steps) and not any(stem_steps) else
                "vertical" if any(stem_steps) and not any(bar_steps) else "compound")
        for letter, drawing, rot in (("L", ld, lrot), ("T", td, trot)):
            number = len(designs) + 1                      # D1 = L of pair 1, D2 = T of pair 1, ...
            designs.append({
                "design": number, "pair": k, "letter": letter, "base": base, "T_stem_col": col, "bend": bend,
                "bar_steps": list(bar_steps), "stem_steps": list(stem_steps),
                "cells": [list(p) for p in g.normalize(drawing.cells)], "rotation_class": [list(p) for p in rot],
                "dihedral_class_seen_earlier": g.dihedral(drawing.cells) in dih_old,
                "positions": [list(a) for a in draw_positions(number)],
            })
    # mirror images among the selected designs
    dih_counts = Counter(tuple(g.dihedral([tuple(p) for p in d["cells"]])) for d in designs)
    info["selected_designs_that_are_mirror_images_of_an_earlier_design"] = sum(d["dihedral_class_seen_earlier"] for d in designs)
    info["selected_designs_sharing_a_dihedral_class_with_another_selected_design"] = sum(c for c in dih_counts.values() if c > 1)
    info["base_composition"] = dict(Counter(d["base"] for d in designs[::2]))
    info["bend_composition"] = dict(Counter(d["bend"] for d in designs[::2]))

    for d in designs:
        for rank, (row, col) in enumerate(d["positions"]):
            for q in range(4):
                pixels = g.bitmap([tuple(p) for p in d["cells"]], row, col, q)
                ident = hexhash(pixels.encode("ascii"))
                images.append({"id": ident, "pixels": pixels})
                keys.append({"id": ident, "design": d["design"], "pair": d["pair"], "letter": d["letter"],
                             "label": 1 if d["letter"] == "T" else 0, "row": row, "col": col, "pos_rank": rank, "q": q})
    pixel_set = {i["pixels"] for i in images}
    if len(pixel_set) != len(images) or pixel_set & old_bitmaps:
        raise SystemExit("Panel bitmaps are not unique or overlap an earlier panel")
    for p in pixel_set:
        if p.count("1") not in (6, 7):
            raise SystemExit("Unexpected ink count")
    images.sort(key=lambda r: (hexhash((ORDER_SALT + r["pixels"]).encode("ascii")), r["id"]))
    keys.sort(key=lambda r: r["id"])
    info["images"] = len(images)

    kmap = {k["id"]: k for k in keys}
    pix = {i["id"]: i["pixels"] for i in images}
    order = [i["id"] for i in images]                      # presentation order = hashed order

    def train_ids(n_designs, n_positions):
        return [i for i in order if kmap[i]["design"] <= n_designs and kmap[i]["pos_rank"] < n_positions
                and kmap[i]["q"] in FIT_TURNS]

    def test_rows(arm, n_designs, n_positions, train):
        tset = set(train)
        public, scorer = [], []
        for i in order:
            k = kmap[i]
            if k["design"] > 16 and k["design"] <= 32:
                cond = "c"
            elif k["design"] <= n_designs and k["q"] in HELD_TURNS:
                cond = "b"
            elif k["design"] <= n_designs and k["q"] in FIT_TURNS and k["pos_rank"] >= n_positions:
                cond = "a"
            else:
                continue                                   # trained bitmaps, or untrained designs outside (c)
            if i in tset:
                raise SystemExit("A test bitmap is a training bitmap")
            public.append({"id": i, "pixels": pix[i]})
            scorer.append({"id": i, "label": k["label"], "letter": k["letter"], "condition": cond, "design": k["design"],
                           "q": k["q"], "row": k["row"], "col": k["col"], "pos_rank": k["pos_rank"]})
        return public, scorer

    files = {}
    files["images.jsonl"] = json_lines(images)
    files["key.jsonl"] = json_lines(keys)
    files["designs.json"] = (json.dumps(designs, indent=1, sort_keys=True) + "\n").encode("ascii")
    for arm, (nd, npos) in (("narrow", (NARROW_DESIGNS, NARROW_POSITIONS)), ("varied", (VARIED_DESIGNS, VARIED_POSITIONS))):
        tr = train_ids(nd, npos)
        if len(tr) != 64:
            raise SystemExit(f"{arm} arm has {len(tr)} training images")
        labels = [kmap[i]["label"] for i in tr]
        shuffled = labels[:]
        random.Random(SHUFFLE_SEED).shuffle(shuffled)
        files[f"train_{arm}.jsonl"] = json_lines({"id": i, "pixels": pix[i], "label": lab} for i, lab in zip(tr, labels))
        files[f"train_{arm}_shuffled.jsonl"] = json_lines({"id": i, "pixels": pix[i], "label": lab} for i, lab in zip(tr, shuffled))
        public, scorer = test_rows(arm, nd, npos, tr)
        files[f"test_{arm}.jsonl"] = json_lines(public)
        files[f"scorer_key_{arm}.jsonl"] = json_lines(scorer)
        info[f"{arm}_train"] = len(tr)
        info[f"{arm}_shuffle_label_changes"] = sum(a != b for a, b in zip(labels, shuffled))
        info[f"{arm}_test_by_condition"] = dict(Counter(s["condition"] for s in scorer))
        info[f"{arm}_test_by_condition_letter"] = {f"{c}/{l}": n for (c, l), n in sorted(Counter((s["condition"], s["letter"]) for s in scorer).items())}
    manifest = {
        "ticket": TICKET, "seed": SEED, "shuffle_seed": SHUFFLE_SEED,
        "generator_source": {"path": str(GENERATOR.relative_to(ROOT)), "sha256": hexhash(GENERATOR.read_bytes())},
        "this_script_sha256": hexhash(Path(__file__).read_bytes()),
        "salts": {"design": DESIGN_SALT, "position": POSITION_SALT, "order": ORDER_SALT},
        "earlier_panel_files_sha256": old_hashes, "info": info,
        "designs": [{k: v for k, v in d.items() if k not in ("cells", "rotation_class")} | {"ink": len(d["cells"])} for d in designs],
        "files": {name: {"rows": len(data.splitlines()), "sha256": hexhash(data)} for name, data in files.items()},
    }
    files["manifest.json"] = (json.dumps(manifest, indent=1, sort_keys=True) + "\n").encode("ascii")
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    files = build()
    if OUT.exists():
        bad = [n for n, d in files.items() if not (OUT / n).is_file() or (OUT / n).read_bytes() != d]
        if bad:
            raise SystemExit(f"Panel in {OUT} differs from a fresh build: {bad}")
        print(f"Verified existing panel {OUT}")
    elif args.check:
        raise SystemExit("No panel to check")
    else:
        OUT.mkdir(parents=True)
        for n, d in files.items():
            (OUT / n).write_bytes(d)
        print(f"Wrote {OUT}")
    print("manifest.json sha256", hexhash(files["manifest.json"]))
    for n, d in sorted(files.items()):
        print(f"  {n:34s} {len(d.splitlines()):6d} rows  {hexhash(d)}")
    print(json.dumps(json.loads(files["manifest.json"])["info"], indent=1))


if __name__ == "__main__":
    main()
