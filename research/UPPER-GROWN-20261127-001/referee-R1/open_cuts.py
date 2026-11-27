"""Split shared distinctions in the positive twelve-knot systems and test specified carriers."""

import argparse
import json
import time
from collections import Counter
from itertools import combinations, product
from pathlib import Path

import networkx as nx
from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
PICKS = tuple(product((0, 1), (2, 3), (4, 5)))


def graph_rows():
    examples = {}
    for datafile in sorted((HERE.parent / 'out').glob('cubic_12*.jsonl')):
        for line, content in enumerate(datafile.read_text().splitlines(), 1):
            row = json.loads(content)
            if row['boxes']:
                key = tuple(map(tuple, row['links']))
                examples[key] = (datafile.name, line, row)
    recovered = {}
    for seed in range(1012, 4012):
        graph = nx.random_regular_graph(3, 12, seed=seed)
        ordered = list(graph.edges)
        key = tuple(sorted(ordered))
        if key in examples and key not in recovered:
            file, line, row = examples[key]
            knots = tuple(tuple(x for x, ends in enumerate(ordered) if k in ends) for k in range(12))
            recovered[key] = (file, line, knots, row['example'][0]['box'], row['boxes'], seed)
        if len(recovered) == len(examples):
            break
    assert len(recovered) == len(examples) == 49
    return sorted(recovered.values())


class Source:
    """Evaluate agreement readings directly on allowed states of the complete source."""
    def __init__(self, knots):
        self.knots = tuple(knots)
        self.solver = Solver()
        self.flags = []
        self.readings = {}
        self.unsat = {}
        self.next_id = 2 + max(x for k in knots for x in k)
        for k in knots:
            flag = self.allocate()
            literals = [x+1 for x in k]
            self.solver.add_clause([-flag, *literals])
            self.solver.add_clause([-flag, *(-x for x in literals)])
            self.flags.append(flag)

    def allocate(self):
        value = self.next_id
        self.next_id += 1
        return value

    def reading(self, carrier):
        if carrier not in self.readings:
            members = [x + 1 for x in carrier]
            reading = self.allocate()
            for other in members[1:]:
                self.solver.add_clause([-reading, -members[0], other])
                self.solver.add_clause([-reading, members[0], -other])
            self.solver.add_clause([reading, *members])
            self.solver.add_clause([reading, *(-x for x in members)])
            self.readings[carrier] = reading
        return self.readings[carrier]

    def permits(self, extra, drop=None):
        flags = self.flags if drop is None else [(-f if i == drop else f) for i, f in enumerate(self.flags)]
        return self.solver.solve(assumptions=[*flags, *extra])

    def has_triple(self, signed_readings):
        key = tuple(sorted(signed_readings))
        if key not in self.unsat:
            self.unsat[key] = self.permits(key)
        return self.unsat[key]

    def box_check(self, carriers, signs):
        signed = tuple(self.reading(c) * (1 if sign else -1) for c, sign in zip(carriers, signs, strict=True))
        return all(not self.has_triple([signed[i] for i in p]) for p in PICKS)

    def certify(self, carriers, signs):
        readings = [self.reading(c) for c in carriers]
        lower = []
        for pick in PICKS:
            words = [''.join(map(str, word)) for word in product((0, 1), repeat=3) if self.permits(
                [readings[i] * (1 if b else -1) for i, b in zip(pick, word, strict=True)])]
            lower.append(words)
        upper = {}
        loose = []
        for drop in [None, *range(len(self.knots))]:
            image = set()
            for word in product((0, 1), repeat=6):
                if self.permits([r * (1 if b else -1) for r, b in zip(readings, word, strict=True)], drop):
                    image.add(''.join(str(int((word[s] ^ word[s+1]) != (signs[s] ^ signs[s+1])))
                                      for s in (0, 2, 4)))
            label = 'all laws' if drop is None else str(drop)
            upper[label] = sorted(image)
        for c, r in zip(carriers, readings, strict=True):
            counts = []
            for k in self.knots:
                both = 0
                for bits in product((0, 1), repeat=len(k)):
                    args = [(x + 1) * (1 if b else -1) for x, b in zip(k, bits, strict=True)]
                    both += self.permits([*args, r]) and self.permits([*args, -r])
                counts.append(both)
            loose.append(counts)
        return {'lower_images_in_product_order': lower, 'mixed_fiber_counts_by_reading_and_knot': loose,
                'upper_images_on_source_and_after_each_law_deletion': upper,
                'semantic_box': all(len(w) == 7 and ''.join(str(signs[i]) for i in p) not in w
                                    for w, p in zip(lower, PICKS, strict=True)) and all(min(row) > 0 for row in loose)}


def canonical(carriers, signs):
    parts = [tuple(sorted(((carriers[i], signs[i]), (carriers[i+1], signs[i+1])))) for i in (0, 2, 4)]
    return tuple(sorted(parts))


def substitutions(carriers, cut, single_swap):
    bases = [tuple(tuple(sorted(copy if x == cut else x for x in c)) for c in carriers) for copy in (cut, 18)]
    for base in bases:
        yield 'transport', base
    if single_swap:
        for base in bases:
            for a, b in combinations(range(19), 2):
                if any(a in c and b in c for c in base):
                    continue
                variant = tuple(tuple(sorted(b if x == a else a if x == b else x for x in c)) for c in base)
                yield 'substitution', variant


def inspect(row, single_swap, cap):
    raw, line, knots, box, count, seed = row
    groups = tuple(tuple(sorted(c)) for pair in box for c, _ in pair)
    signs = tuple(s for pair in box for _, s in pair)
    assert len(set(x for c in groups for x in c)) == 18
    source = Source(knots)
    assert source.box_check(groups, signs)
    original = source.certify(groups, signs)
    assert original['semantic_box'] and len(original['upper_images_on_source_and_after_each_law_deletion']['all laws']) == 7
    source.solver.delete()
    tally = Counter()
    splits = []
    for cut in range(min(cap, 18)):
        holder = max(i for i, k in enumerate(knots) if cut in k)
        after = tuple(tuple(18 if x == cut and i == holder else x for x in k) for i, k in enumerate(knots))
        cut_source = Source(after)
        seen = set()
        scores = []
        hits = []
        for kind, proposal in substitutions(groups, cut, single_swap):
            code = canonical(proposal, signs)
            if code in seen:
                continue
            seen.add(code)
            tally[kind] += 1
            if kind == 'transport':
                signed = tuple(cut_source.reading(c) * (1 if s else -1) for c, s in zip(proposal, signs, strict=True))
                scores.append(sum(not cut_source.has_triple([signed[i] for i in p]) for p in PICKS))
            if cut_source.box_check(proposal, signs):
                certificate = cut_source.certify(proposal, signs)
                hits.append({'kind': kind, 'carriers': proposal, 'signs': signs, 'evidence': certificate})
                tally['semantic boxes'] += certificate['semantic_box']
        cut_source.solver.delete()
        splits.append({'split': cut, 'new end at knot': holder, 'inherited lower exclusions by retained copy': scores,
                       'candidate_count': len(seen), 'hits': hits})
    return {'file': raw, 'line': line, 'generator_seed_for_distinction_order': seed,
            'knots_in_raw_order': knots, 'archived_box_count': count, 'archived_carriers': groups, 'signs': signs,
            'tally': dict(tally), 'splits': splits}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--graphs', type=int, default=49)
    parser.add_argument('--cuts', type=int, default=18)
    parser.add_argument('--one-swap', action='store_true')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    start = time.monotonic()
    rows = [inspect(r, args.one_swap, args.cuts) for r in graph_rows()[:args.graphs]]
    totals = sum((Counter(row['tally']) for row in rows), Counter())
    surviving = Counter(v for row in rows for cut in row['splits'] for v in cut['inherited lower exclusions by retained copy'])
    result = {'scope': 'One archived set of six carriers on each system. Two inherited transports per split; '
              'with --one-swap also exchange one pair of the 19 identities, including the one unused identity.',
              'arguments': vars(args) | {'out': args.out.name}, 'totals': dict(totals), 'systems': len(rows),
              'splits': sum(len(r['splits']) for r in rows), 'inherited_lower_exclusion_histogram': dict(surviving),
              'rows': rows, 'elapsed_seconds': round(time.monotonic() - start, 3)}
    args.out.write_text(json.dumps(result, separators=(',', ':')) + '\n')
    print({k: v for k, v in result.items() if k not in ('rows', 'arguments', 'scope')})


if __name__ == '__main__':
    main()
