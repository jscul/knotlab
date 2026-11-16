"""All scalar affine premises and conclusions, up to symmetry of the three triples."""

from collections import Counter
from pathlib import Path
import json
import shutil
import subprocess
import tempfile


def parity(x):
    return x.bit_count() & 1


def errors(x):
    value = 0
    for i in range(3):
        y, w, p = ((x >> (3*i+j)) & 1 for j in range(3))
        value |= (p ^ (y*w)) << i
    return value


def triple_transposition(x, adjacent):
    good = [0, 1, 2, 7]
    good[adjacent], good[adjacent+1] = good[adjacent+1], good[adjacent]
    shift = good[0]
    cols = [good[1]^shift, good[2]^shift, good[3]^good[1]^good[2]^shift]
    y = shift
    for i, col in enumerate(cols):
        if (x >> i) & 1:
            y ^= col
    return y


def equation_generators():
    maps = []
    for block in range(3):
        shift = 3*block
        mask = 7 << shift
        for adjacent in range(3):
            maps.append([(x & ~mask) | (triple_transposition((x >> shift) & 7, adjacent) << shift)
                         for x in range(512)])
    for block in range(2):
        a, b = 3*block, 3*(block+1)
        maps.append([x ^ ((((x >> a) ^ (x >> b)) & 7) * ((1 << a) | (1 << b))) for x in range(512)])
    generators = []
    for transform in maps:
        assert len(set(transform)) == 512
        assert all((errors(x)==0) == (errors(y)==0) and parity(errors(x)) == parity(errors(y))
                   for x, y in enumerate(transform))
        equations = []
        for equation in range(1024):
            coefficients, rhs = equation & 511, equation >> 9
            constant = rhs ^ parity(transform[0] & coefficients)
            row = sum(parity((transform[1 << j] ^ transform[0]) & coefficients) << j for j in range(9))
            equations.append(row | (constant << 9))
        generators.append(equations)
    return generators


def flat_key(a, b):
    x, y, _ = sorted((a, b, a ^ b))
    return x | (y << 10)


def forbidden_orbits():
    generators = equation_generators()
    groups = {}
    membership = {}
    for a in range(1,512):
        for b in range(a+1,512):
            if a ^ b < b:
                continue
            for rhs in range(4):
                seed = flat_key(a | ((rhs & 1) << 9), b | ((rhs >> 1) << 9))
                if seed in membership:
                    continue
                queue = [seed]
                membership[seed] = seed
                for current in queue:
                    x, y = current & 1023, current >> 10
                    for image in generators:
                        target = flat_key(image[x], image[y])
                        if target not in membership:
                            membership[target] = seed
                            queue.append(target)
                        else:
                            assert membership[target] == seed
                groups[seed] = len(queue)
    assert len(groups) == 126 and len(membership) == sum(groups.values()) == 173740
    return groups


def audit():
    groups = forbidden_orbits()
    compiler = shutil.which('c++')
    if compiler is None:
        raise RuntimeError('a C++20 compiler is required for the one-premise audit')
    source = Path(__file__).with_name('one_premise.cpp')
    lines = ''.join(f'{key} {size}\n' for key, size in groups.items())
    with tempfile.TemporaryDirectory(prefix='five-product-one-premise-') as tmp:
        program = str(Path(tmp) / 'one_premise')
        subprocess.run([compiler, '-std=c++20', '-O2', str(source), '-o', program], check=True)
        result = subprocess.run([program], input=lines, text=True, capture_output=True, check=True)
    triples = {key:set() for key in groups}
    lower_histogram = Counter()
    expanded_histogram = Counter()
    training_histogram = Counter()
    named = None
    for line in result.stdout.splitlines():
        key, multiplicity, guard, conclusion, training, main_bound = map(int, line.split())
        assert multiplicity == groups[key] and guard not in triples[key]
        a, b = key & 1023, key >> 10
        assert guard in (a, b, a^b) and flat_key(guard, conclusion^512) == key
        triples[key].add(guard)
        if key == flat_key(1, 32) and guard == 32:
            # (y,w,p) -> (w+1,y,p+y) on block one sends w1=1 to y1=0.
            assert (training, main_bound) == (7, 18)
            named = {'training':training, 'main_lower_bound':main_bound, 'total_lower_bound':training+main_bound}
        if guard == a:
            training_histogram[training] += 1
        lower_histogram[training + main_bound] += 1
        expanded_histogram[training + main_bound] += multiplicity
    assert len(triples) == 126 and all(len(orientations) == 3 for orientations in triples.values())
    assert sum(expanded_histogram.values()) == 521220
    assert min(lower_histogram) == 23 and lower_histogram[23] == 21
    assert sum(lower_histogram.values()) == 378
    number_of_embeddings = int(result.stderr.strip())
    assert number_of_embeddings == 9216 and named is not None
    return {'named_v_zero_implies_x0_zero':named, 'forbidden_flats':sum(groups.values()), 'symmetry_orbits':len(groups),
            'tested_representative_orientations':sum(lower_histogram.values()),
            'oriented_forbidden_flats':sum(expanded_histogram.values()),
            'original_model_points':512, 'root_question_masks':511,
            'injective_affine_lifts':number_of_embeddings,
            'pointwise_lift_membership_checks':number_of_embeddings * 64,
            'affine_six_bit_cells':26387, 'ordinary_two_triple_cost':11,
            'training_cost_by_flat_orbit':dict(sorted(training_histogram.items())),
            'lower_bound_by_representative_orientation':dict(sorted(lower_histogram.items())),
            'lower_bound_by_all_orientations':dict(sorted(expanded_histogram.items()))}


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2, sort_keys=True))
