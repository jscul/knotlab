"""The lawful starts replayed by the study.  Every start is a tuple of supports (tuples of integers).

Sources (read only, imported by path):
  * seven-knot source: research/GENERATORS-20261120-001/source.md, "The seven-knot construction"
    (meetings 01 twice, 04, 14, 24, 26, 34, 35, 56; loose supply 3,0,3,3,3,2,2; 25 distinctions).
  * five-founder clock: experiments/CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001B/.../phase_clocks.py
    (source_cases()["five_odd"], rebuilt here with the same arithmetic).
  * explosive starts: artifacts/HEAVY-GROWTH-20261119-001/.../sources_audit.json (start-00, -04, -13).
  * smallest stall and smallest parity closing: experiments/WHOLE-STAGE-SETTINGS-20261120-001B/.../edits.py
    (built_cases(): S_cycle_five and C_binary).
  * concealed-shortage preparation (four types): experiments/LOCAL-EDIT-POLICIES-20261123-001C/.../physical.py.
"""

import json
from pathlib import Path

from engine import ROOT, load_module

EDITS = ROOT / ("experiments/WHOLE-STAGE-SETTINGS-20261120-001B/"
                "WHOLE-STAGE-SETTINGS-20261120-001B-E001_ordinary_edits/edits.py")
CONCEALED = ROOT / ("experiments/LOCAL-EDIT-POLICIES-20261123-001C/"
                    "LOCAL-EDIT-POLICIES-20261123-001C-E001_hidden_demand/physical.py")
ARCHIVE = ROOT / ("artifacts/HEAVY-GROWTH-20261119-001/HEAVY-GROWTH-20261119-001-E001_checks/"
                  "sources_audit.json")


def source_from(meetings, opens):
    """GENERATORS fixtures.source_from: shared distinctions first, then each knot's loose supply."""
    stars = [[] for _ in opens]
    for d, (left, right) in enumerate(meetings):
        stars[left].append(d)
        stars[right].append(d)
    top = len(meetings)
    for row, count in zip(stars, opens, strict=True):
        row.extend(range(top, top + count))
        top += count
    return tuple(map(tuple, stars))


def seven_knot_source():
    meetings = [(0, 1), (0, 1), (0, 4), (1, 4), (2, 4), (2, 6), (3, 4), (3, 5), (5, 6)]
    return source_from(meetings, (3, 0, 3, 3, 3, 2, 2))


def five_founder_clock():
    """Two loose distinctions at each of five knots on a ring with multiplicities 2,1,1,1,3."""
    shared = [(0, 1, 2), (1, 2, 1), (2, 3, 1), (3, 4, 1), (4, 0, 3)]
    rows = [[] for _ in range(5)]
    d = 0
    for a, b, multiplicity in shared:
        for _ in range(multiplicity):
            rows[a].append(d)
            rows[b].append(d)
            d += 1
    for knot in range(5):
        rows[knot].extend((d, d + 1))
        d += 2
    return tuple(map(tuple, rows))


def archived_explosive(name):
    row = json.loads(ARCHIVE.read_text())["named_archive_starts"][name]
    return tuple(map(tuple, row["gate"]["literal_supports"]))


_edits = None


def edits_module():
    global _edits
    if _edits is None:
        _edits = load_module(EDITS, "whole_stage_edits")
    return _edits


def built(name):
    for prep in edits_module().built_cases():
        if prep.name == name:
            return prep
    raise KeyError(name)


def stall_start(settings):
    """Smallest two-sided stall (five knots, 13 distinctions) with the two optional additions as set."""
    prep = built("S_cycle_five")
    return tuple(map(tuple, prep.edited(settings)))


def closing_start(settings):
    """Smallest parity closing (three knots, six distinctions) with the optional additions as set."""
    prep = built("C_binary")
    return tuple(map(tuple, prep.edited(settings)))


_concealed = None


def concealed_module():
    global _concealed
    if _concealed is None:
        _concealed = load_module(CONCEALED, "concealed_physical")
    return _concealed


def concealed_start(u, v, x, y):
    """Concealed-shortage preparation of type (u, v) with free settings (x, y); names mapped to integers."""
    m = concealed_module()
    rows, _, _ = m.physical(u, v, "primary", x, y)
    index = {}
    for name in rows:
        for d in rows[name]:
            index.setdefault(d, len(index))
    return tuple(tuple(index[d] for d in rows[name]) for name in rows)


def all_histories():
    """Name -> (stars, kind).  The horizons are attached by the check scripts."""
    out = {}
    out["seven_knot_source"] = (seven_knot_source(), "source")
    out["five_founder_clock"] = (five_founder_clock(), "clock")
    for name in ("start-00", "start-04", "start-13"):
        out["explosive_" + name[-2:]] = (archived_explosive(name), "explosive")
    for settings in ((0, 0), (0, 1), (1, 0), (1, 1)):
        out["stall_%d%d" % settings] = (stall_start(settings), "stall")
        out["closing_%d%d" % settings] = (closing_start(settings), "closing")
    for u in (0, 1):
        for v in (0, 1):
            out["concealed_type_%d%d_funded" % (u, v)] = (concealed_start(u, v, u, v), "concealed")
    return out
