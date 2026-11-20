"""Eliminate every hidden physical value and check the equations on the displayed exterior."""
import json
from current import DATA, cases, distances, loads, stages


def insert(row, basis):
    while row:
        pivot = row.bit_length() - 1
        if pivot not in basis:
            basis[pivot] = row
            return True
        row ^= basis[pivot]
    return False


def verify(stage, grades, cutoff, retained):
    visible = {m for m, vs in stage.ends.items() if all(v in retained for v in vs)}
    hidden_mask = sum(1 << m for m in stage.ends if m not in visible)
    equations = [sum(1 << m for m in star) for star in stage.stars]
    hidden_pivots, projected, predicted = {}, {}, {}
    for row in equations:
        while row & hidden_mask:
            key = (row & hidden_mask).bit_length() - 1
            if key not in hidden_pivots:
                hidden_pivots[key] = row
                break
            row ^= hidden_pivots[key]
        else:
            insert(row, projected)
    for v in retained:
        if grades[v] > cutoff:
            assert not equations[v] & hidden_mask
            insert(equations[v], predicted)
    assert len(projected) == len(predicted)
    assert all(not insert(row, predicted) for row in projected.values())
    return [len(retained), len(visible), len(projected)]


def main():
    source = cases()["J1"]
    seam, = source["roles"]["seams"]
    length = len(source["roles"]["anchors"])
    rows = []
    for preparation, occupied in loads(source).items():
        for stage in stages(source, occupied, 4, {}):
            grades = distances(stage.neighbors, [seam])
            for cutoff in range(stage.age+1, max(seam,length-seam)):
                exterior = {v for v, h in grades.items() if h >= cutoff}
                for side, mark in (("left", seam-1-cutoff), ("right", seam+cutoff)):
                    if not 0 <= mark < length:
                        continue
                    root, other = stage.ends[mark]
                    assert {root,other} <= exterior
                    connected = {root}
                    pending = [root]
                    while pending:
                        v = pending.pop()
                        new = (stage.neighbors[v] & exterior) - connected
                        connected.update(new)
                        pending.extend(new)
                    for view, selected in (("union",exterior), ("component",connected)):
                        rows.append([preparation,stage.age,cutoff,side,view,*verify(stage, grades, cutoff, selected)])
    output = {"domain":"all original 16-mark path positions at d greater than the current age, funded ages 0 through 4; both preparations, physical labels used only for evidence",
              "columns":["preparation","age","offset","side","observation","knots","distinctions","projected_rank"],
              "all_projected_row_spaces_equal_predicted_row_spaces":True,"rows":rows}
    (DATA/"projection_check.json").write_text(json.dumps(output,separators=(",",":"))+"\n")
    print(len(rows),"projection comparisons")

if __name__ == "__main__":
    main()
