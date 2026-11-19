"""Read auxiliary fixed-stage checks through exact weights and original physical incidence."""

import argparse
from fractions import Fraction
import gzip
import json
import os
from pathlib import Path
import subprocess
import tempfile

from anneal_panel import distribution, normalizer


def read_rows(path):
    with path.open() as stream:
        header, *rows = map(json.loads, stream)
    return header, rows


class PhysicalCheck:
    def __init__(self, source):
        with source.open() as stream:
            n, number = map(int, next(stream).split())
            blocks = [tuple(map(int, line.split())) for line in stream]
        assert len(blocks) == number
        self.n = n
        self.membership = [[] for _ in range(n)]
        self.blocks = []
        for k, block in enumerate(blocks):
            self.blocks.append(sum(1 << u for u in block))
            for u in block:
                self.membership[u].append(k)
        self.neighbors = {}
        self.full = (1 << n) - 1

    def validate(self, group):
        mask = sum(1 << u for u in group)
        assert mask.bit_count() == len(group)
        common = self.full
        for u in group:
            if u not in self.neighbors:
                closed = 1 << u
                for block in self.membership[u]:
                    closed |= self.blocks[block]
                self.neighbors[u] = closed
            common &= self.neighbors[u]
        assert common == mask
        return dict(size=len(group), held=any(mask & ~b == 0 for b in self.blocks))


def measure(rows):
    exact = all("exact_initial_mass" in r for r in rows)
    masses = [normalizer(r) * r['final_mass'] if exact else Fraction(r["estimate"]) for r in rows]
    named = {}
    for mark in rows[0].get("marked_final_mass", {}):
        marked = [normalizer(r) * r["marked_final_mass"][mark] for r in rows]
        named[mark] = distribution(marked)
    return dict(total=distribution(masses), marked=named, exact_rational_factors=exact, observations=rows)


def marked_control(binary):
    with tempfile.TemporaryDirectory(prefix='anneal-known-mark-') as work:
        folder = Path(work)
        roster, bank = folder / "roster", folder / "bank"
        roster.write_text("6 3\n0 1 2\n1 2 3\n4 5\n")
        bank.write_text("2 1 2\n1 1\n2 1 2\n")
        env = dict(os.environ, ANNEAL_MARK_BLOCKS="0+1,2+2", ANNEAL_PROFILE_COUNT="8")
        lines = subprocess.check_output([binary, roster, "given", "0", "1", "87", "1", "0", "0", "0", "0", bank],
                                        text=True, env=env).splitlines()
        state = json.loads(lines[-1])
        assert normalizer(state) == 1 and state["final_mass"] == 3
        assert state["marked_final_mass"] == {"0+1": 2, "2+2": 1}
        graph = PhysicalCheck(roster)
        for group in state["physical_draws"]:
            graph.validate(group)
        assert {tuple(c) for c in state["physical_draws"]} <= {(0, 1, 2), (1, 2, 3), (4, 5)}
        return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('inputs', type=Path)
    parser.add_argument('binary', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--physical', nargs='*', type=Path, default=[])
    args = parser.parse_args()
    root = args.inputs
    read = lambda name: read_rows(root / ('anneal_' + name + '.jsonl'))[1]
    exhaustive = json.loads(subprocess.check_output([args.binary, "--self-test"]))
    prior = read("exact_age7")[0]
    assert prior["exact"] and normalizer(prior) * prior["final_mass"] == 28099
    old, packed = map(read, ("seed85_n32_base", "seed85_n32_packed"))
    assert len(old) == len(packed) == 3
    for a, b in zip(old, packed):
        assert (a["resample_numerators"], a["final_mass"]) == (b["resample_numerators"], b["final_mass"])
    before, after = map(read, ("paired_marked", "marked_probe"))
    physical = PhysicalCheck(root / "start-03-age08.txt")
    sampled = []
    for a, b in zip(before, after, strict=True):
        assert (a["resample_numerators"], a["final_mass"]) == (b["resample_numerators"], b["final_mass"])
        sampled += [physical.validate(g) for g in b["physical_draws"]]
    heldout = {}
    for path in args.physical:
        with gzip.open(path, "rt") as src:
            rows = json.load(src)
        heldout[path.name] = [dict(island_seed=r["seed"], **physical.validate(r["sampled_actual_live_ids"][0]))
                              for r in rows]
    pilots = {}
    for name in ("pilot_age7", "pilot_age8", "full_n16_packed", "full_n16_moved", "full_n128",
                 "full_n512", "full_degdown", "full_random", "secondary_seed13_4", "secondary_seed13_4_random"):
        pilots[name] = measure(read(name))
    result = dict(small_labeled_graphs=exhaustive, positive_marked_twin_control=marked_control(args.binary),
                  preceding_stage=prior, slow_packed_same_integer_factors=3,
                  unchanged_with_marked_measurement=len(after), pilot_physical_checks=sampled,
                  heldout_physical_checks=heldout,
                  marked_counter_truth={"13+4":"183833974142788"}, exploratory=pilots)
    with args.output.open("x") as stream:
        json.dump(result, stream, separators=(",", ":"))
        stream.write("\n")


if __name__ == "__main__":
    main()
