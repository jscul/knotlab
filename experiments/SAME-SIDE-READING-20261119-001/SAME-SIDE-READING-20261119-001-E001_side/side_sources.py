"""Build the registered paths and choose marks using only the original source."""
from collections import Counter
from copy import deepcopy
from functools import cache
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CONFIG = json.loads((HERE / "inputs.json").read_text())
OLDER = ROOT / CONFIG["base_reader"]
module_spec = importlib.util.spec_from_file_location("old_mark_sources", OLDER)
old = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(old)
generate = old.generate
growth = old.growth
CAPS = CONFIG["caps"]
AGES = CONFIG["ages"]


def padded(tag, count, seams, doubled=False):
    meetings = [[i, i + 1] for i in range(count)]
    opens = [2] * (count + 1)
    rings, ring_marks = [], []
    for s in seams:
        for v in (s-1, s, s+1):
            opens[v] += 2
        start = len(opens)
        ring = [s, start, start+1, start+2, start+3]
        opens.extend((4,3,2,4))
        rings.append(ring)
        ring_marks.append(list(range(len(meetings), len(meetings)+5)))
        meetings.extend([ring[i],ring[(i+1)%5]] for i in range(5))
    roles = {"background":list(range(count+1)), "rings":rings, "seams":list(seams),
             "ring_spares":[[r[2]] for r in rings], "anchors":list(range(count)),
             "ring_edges":ring_marks, "background_spares":[0,1,count-1,count]}
    if doubled:
        assert len(rings)==1
        roles["additional_ring_edges"] = list(range(len(meetings),len(meetings)+5))
        meetings.extend([*meetings[m]] for m in ring_marks[0])
    degrees = Counter(v for pair in meetings for v in pair)
    return {"id":tag,"sizes":[a+degrees[v] for v,a in enumerate(opens)],"meetings":meetings,
            "ages":list(range(AGES.get(tag,6)+1)),"roles":roles}


@cache
def cases():
    assert sha256((ROOT / CONFIG["source"]).read_bytes()).hexdigest() == CONFIG["sha256"]
    originals = old.cases()
    result = {key:deepcopy(originals[key]) for key in ("J1","T4","T8","J1x2","B")}
    for base in ("J1","T4","T8","J1x2","B"):
        check = padded(base,16,result[base]["roles"]["seams"],doubled=(base=="J1x2"))
        assert check["meetings"] == result[base]["meetings"] and check["sizes"] == result[base]["sizes"], base
    for p in (4,8,16):
        tag = f"P{p}"
        result[tag] = padded(tag,16+2*p,[4+p])
    for gap in (4,8):
        tag = f"PT{gap}"
        result[tag] = padded(tag,24,[8,8+gap])
    result["PX4"] = padded("PX4",24,[8],doubled=True)
    return {key:result[key] for key in CONFIG["cases"]}


def loads(spec):
    if spec["id"] == "PX4":
        return old.loads({**spec,"id":"J1x2"})
    return old.loads(spec)


def marksets(spec, full=False):
    count = len(spec["roles"]["anchors"])
    seams = spec["roles"]["seams"] or [4]
    def accepted(ms):
        return all(ms[-1] < s or ms[0] >= s for s in seams)
    if full:
        return [ms for k in (2,3,4) for ms in combinations(range(count),k) if accepted(ms)]
    chosen=set()
    for seam in seams:
        for off in CONFIG["offsets"]:
            for shape in CONFIG["shapes"]:
                for ms in (tuple(seam+off+i for i in shape),
                           tuple(sorted(seam-1-off-i for i in shape))):
                    if 0 <= ms[0] and ms[-1] < count and accepted(ms):
                        chosen.add(ms)
    return sorted(chosen,key=lambda ms:(len(ms),ms))


def offset(marks,seam):
    return min(min(abs(m-seam),abs(m+1-seam)) for m in marks)

