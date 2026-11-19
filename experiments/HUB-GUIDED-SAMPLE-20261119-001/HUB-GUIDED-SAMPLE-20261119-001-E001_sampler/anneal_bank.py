"""Draw an exactly weighted initial population from a certified induced-core ranker."""

import argparse
from contextlib import nullcontext
import gzip
import json
from pathlib import Path
from random import Random
import sys

from structure_export import unrank


def read_bdd(path):
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt') as stream:
        first = next(stream)
        if first.startswith('DNNF1 '):
            from structure_rank import load, unrank as unrank_dnnf
            data = load(path)
            return [v for v, _, _ in data['sites']], data['count'], lambda index: unrank_dnnf(data, index)
        _, width, node_count, site_count, root, total = map(int, first.split())
        coords = list(map(int, next(stream).split()))
        assert len(coords) == width
        nodes = [tuple(map(int, next(stream).split())) for _ in range(node_count)]
        sites = []
        for _ in range(site_count):
            v, side, *words = map(int, next(stream).split())
            sites.append((v, side, sum(word << (64 * j) for j, word in enumerate(words))))
        assert not stream.read().strip()
    data = dict(coordinates=coords, root=root, count=total, nodes=nodes, sites=sites)
    return [v for v, _, _ in sites], total, lambda rank: unrank(data, rank)


def make_bank(path, sites, count, decoder, population, replicates, seed, stratified):
    sink = nullcontext(sys.stdout) if str(path) == '-' else path.open('w')
    with sink as stream:
        write_bank(stream, sites, count, decoder, population, replicates, seed, stratified)


def write_bank(stream, sites, count, decoder, population, replicates, seed, stratified):
    print(len(sites), *sites, file=stream)
    for rep in range(replicates):
        rng = Random(f'anneal.initial-prefix.{seed + rep}')
        print(count, 1, file=stream)
        for i in range(population):
            draw = rng.randrange(count)
            rank = (i * count + draw) // population if stratified else draw
            names = decoder(rank)
            stream.write(f'{len(names)} ' + ' '.join(map(str, names)) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ranker', type=Path)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--population', required=True, type=int)
    parser.add_argument('--replicates', required=True, type=int)
    parser.add_argument('--seed', required=True, type=int)
    parser.add_argument('--stratified', action='store_true')
    args = parser.parse_args()
    sites, count, decoder = read_bdd(args.ranker)
    make_bank(args.destination, sites, count, decoder, args.population, args.replicates, args.seed, args.stratified)
    print(json.dumps(dict(induced_names=len(sites), normalizer=count, population=args.population,
                          replicates=args.replicates, seed=args.seed, stratified=args.stratified)),
          file=sys.stderr if str(args.destination) == '-' else sys.stdout)


if __name__ == '__main__':
    main()
