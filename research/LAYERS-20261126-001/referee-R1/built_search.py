"""Purpose-built starts that challenge the joined-ring claim, with funding controls."""
import argparse
import json
from pathlib import Path
from time import perf_counter

from built_changes import advance, assemble, bits, first_funding, incidences, linked_rings, read, ring
from built_witness import compare_growth, source


def attach_rings(lengths, connect_twice=False):
    """A common knot with no loose distinction; each ring meets it once or twice."""
    center = sum(lengths)
    meetings = []
    joins = []
    labels = []
    offset = 0
    for length in lengths:
        meetings.extend(ring(offset, length))
        labels.append(bits(range(offset, offset + length)))
        joins.append((offset, center))
        if connect_twice:
            joins.append((offset + 2, center))
        offset += length
    meetings.extend(joins)
    demand = first_funding(center + 1, meetings, set(range(center)))
    loose = [max(2, demand[i]) for i in range(center)] + [0]
    return assemble(center + 1, meetings, loose), labels, loose


def summarize(title, data, rounds):
    stage, labels, loose = data
    base = stage
    stages = []
    for t in range(rounds + 1):
        info = read(stage, labels)
        info["round"] = t
        if t == 1:
            owners = incidences(base)
            sources = [{owners[d][0] for d in born if d in owners} for born in stage[len(base):]]
            ring_knots = [set().union(*(set(owners[d]) for d in range(label.bit_length())
                                        if label & (1 << d))) for label in labels]
            info["new_knots_with_parents_in_multiple_rings"] = sum(
                sum(bool(parents & ring) for ring in ring_knots) >= 2 for parents in sources
            )
        stages.append(info)
        if t < rounds:
            stage, reason = advance(stage)
            if not stage:
                stages.append({"end": reason, "requested_round": t + 1})
                break
    return {"construction": title, "source": base, "loose_by_holder": loose, "stages": stages}


def cases():
    for minimum, central in [(2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (1, 0), (3, 0)]:
        yield (f"Two four-knot rings with three different meetings at the connecting knot, "
               f"minimum live-ring funding {minimum}, connector has {central} loose distinctions",
               source(central, minimum)[:3], 2)
    for n, m, extra, multiple, live, bypass, rounds in [
        (5, 5, 2, 2, False, False, 3),
        (5, 5, 2, 2, True, False, 2),
        (5, 5, 2, 1, False, True, 2),
        (4, 4, 2, 1, True, True, 1),
        (5, 7, 2, 2, False, False, 2),
        (4, 5, 1, 2, False, False, 2),
        (4, 4, 1, 2, False, False, 2),
        (3, 4, 2, 2, False, False, 2),
        (5, 5, 0, 2, True, False, 2)
    ]:
        title = (f"Rings of {n} and {m} knots with {extra} intermediate knots, "
                 f"{multiple} shared distinction{'s' if multiple != 1 else ''} per consecutive pair, "
                 f"all connector knots {'funded' if live else 'with no loose distinction'}")
        if bypass:
            title += ", two additional knots at each joined pair with all four meeting singly"
        yield title, linked_rings(n, m, extra, multiple, live, inner_bypass=bypass), rounds
    for lengths, twice, rounds in [
        ((4, 4, 4), False, 3),
        ((4, 4, 5), False, 2),
        ((5, 5, 5), False, 2),
        ((4, 4, 4, 4), False, 2),
        ((4, 4, 4), True, 1),
        ((4, 4, 4, 4), True, 1)
    ]:
        title = (f"Rings with knot counts {list(lengths)}, each meeting the common zero-loose knot "
                 f"at {'two different knots' if twice else 'one knot'}")
        yield title, attach_rings(lengths, twice), rounds


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--compare-growth", action="store_true")
    args = parser.parse_args()
    rows = []
    for i, (title, data, rounds) in enumerate(cases()):
        if args.limit is not None and i == args.limit:
            break
        tick = perf_counter()
        row = summarize(title, data, rounds)
        if args.compare_growth:
            row["comparison_with_the_recorded_growth_engine"] = compare_growth(data[0], rounds)
        row["seconds"] = round(perf_counter() - tick, 5)
        rows.append(row)
        print(i + 1, title, [s.get("whole_held_rank", s.get("end")) for s in row["stages"]], flush=True)
    if args.output:
        args.output.write_text(json.dumps(rows, separators=(",", ":")) + "\n")
