"""Frozen blind reader. Input is one anonymous packet on standard input."""

import itertools
import json
import math
import sys

import numpy as np


def read_main(record):
    counts = sorted(record["counts"])
    exponent = None
    slopes = []
    dimension = None
    if len(counts) == 4 and all(r > 0 and count > 0 for r, count in counts):
        intervals = list(zip(counts, counts[1:]))
        if all(r2 > r1 and n2 >= n1 for (r1, n1), (r2, n2) in intervals):
            slopes = [math.log(n2 / n1) / math.log(r2 / r1)
                      for (r1, n1), (r2, n2) in intervals]
            exponent = math.log(counts[-1][1] / counts[0][1]) / math.log(counts[-1][0] / counts[0][0])
            for d in (2, 3):
                if (abs(exponent - d) <= .30 and max(abs(a - d) for a in slopes) <= .50
                        and abs(slopes[-1] - d) <= .35):
                    dimension = d

    witnesses = sorted(record["witnesses"])
    assert all(0 <= hits <= queried for _, queried, hits in witnesses)
    far = witnesses[-1][0] if witnesses else 0
    bounded = bool(witnesses and witnesses[-1][2] and
                   any(radius <= .75 * far and hits for radius, _, hits in witnesses[:-1]))
    local = record.get("local", [])
    local_hits = 0
    for n, adjacent, histogram, degrees in local:
        positive_bins = sorted((value, frequency) for value, frequency in histogram if frequency)
        local_hits += (n == 6 and adjacent == 0 and positive_bins == [(0, 3), (1, 12)]
                       and sorted(degrees) == [1] * 6)
    local_pass = bool(local) and local_hits == len(local)
    call = "inconclusive"
    if bounded:
        call = "bounded-bond separation candidate"
    elif dimension == 3:
        call = "cubic growth candidate"
    return dict(id=record["id"], exponent=exponent, slopes=slopes, dimension=dimension,
                counts=counts, witnesses=witnesses, bounded=bounded, local_hits=local_hits,
                local_total=len(local), local_pass=local_pass,
                cubic_arrangement=dimension == 3 and local_pass, call=call)


def measure_matrix(values):
    if values is None:
        return {"usable": False}
    d = np.asarray(values, dtype=float)
    if (d.shape != (12, 12) or not np.isfinite(d).all() or not np.array_equal(d, d.T)
            or np.any(np.diag(d) != 0) or np.any(d[np.triu_indices(12, 1)] <= 0)):
        return {"usable": False}
    diameter = float(d.max())
    residuals, support, points = [], 0, set()
    for i, j, k, l in itertools.combinations(range(12), 4):
        six = (d[i, j], d[i, k], d[i, l], d[j, k], d[j, l], d[k, l])
        if min(six) < max(2, .12 * diameter) or max(six) < .45 * diameter:
            continue
        a, b, c = sorted((six[0] * six[5], six[1] * six[4], six[2] * six[3]), reverse=True)
        gap = (a - b - c) / a
        residuals.append(float(max(0., gap)))
        support += int(abs(gap) <= .08 and c / a >= .15)
        points.update((i, j, k, l))
    residuals.sort()
    count = len(residuals)
    q95 = residuals[math.ceil(.95 * count) - 1] if count else None
    vmax = residuals[-1] if count else None
    hits = sum(v >= .10 for v in residuals)
    centered = np.eye(12) - np.ones((12, 12)) / 12
    eigenvalues, directions = np.linalg.eigh(-.5 * centered @ (d**2) @ centered)
    top = np.maximum(eigenvalues[-2:], 0.)
    embedding = directions[:, -2:] * np.sqrt(top)
    fit = np.linalg.norm(embedding[:, None, :] - embedding[None, :, :], axis=2)
    error = float(np.linalg.norm(d - fit) / np.linalg.norm(d))
    ratio = float(top[0] / top[1]) if top[1] else 0.
    usable = count >= 40 and len(points) >= 9 and diameter >= 10
    polygonal = usable and vmax >= .16 and hits >= 3 and (q95 >= .065 or error >= .055)
    rounded = usable and ratio >= .12 and support >= 8 and error <= .055 and q95 <= .035 and vmax <= .12
    return dict(usable=usable, diameter=diameter, n=count, points=len(points), q95=q95,
                vmax=vmax, h=hits, t=support, error=error, eigen_ratio=ratio,
                polygonal=polygonal, round=rounded)


def read_shape(record):
    scales = []
    for item in record["scales"]:
        r, bond, meeting = (item["r"], item["bond"], item["meeting"]) if isinstance(item, dict) else item
        scales.append(dict(r=r, bond=measure_matrix(bond), meeting=measure_matrix(meeting)))
    scales.sort(key=lambda item: item["r"])
    call = "inconclusive"
    if len(scales) >= 2 and scales[-1]["r"] > scales[-2]["r"]:
        before, last = [item["bond"] for item in scales[-2:]]
        if before["usable"] and last["usable"]:
            if before["polygonal"] and last["polygonal"] and last["vmax"] >= .65 * before["vmax"]:
                call = "polygonal-limit candidate"
            if before["round"] and last["round"] and last["diameter"] >= 15 and last["error"] <= before["error"] + .015:
                call = "round-limit candidate"
    return dict(id=record["id"], scales=scales, call=call)


if __name__ == "__main__":
    packet = json.load(sys.stdin)
    print(json.dumps(dict(main=[read_main(r) for r in packet["main"]],
                          shape=[read_shape(r) for r in packet["shape"]]),
                     sort_keys=True, indent=2, allow_nan=False))
