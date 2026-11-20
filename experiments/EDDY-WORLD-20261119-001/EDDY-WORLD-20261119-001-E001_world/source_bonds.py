"""Check the source path distance formula using literal connected shores.

For two cut path meetings in a source with one-point attachments, the
ordinary shore has its exact path interval forced. Enumerate every way of
choosing its other junctions. Positive loose counts connect the complement
through the exterior. No observation from a later stage is an input.
"""
from itertools import combinations
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / 'artifacts' / HERE.parent.name / HERE.name / 'source_bonds.json'


def connected(vertices, adjacency):
    reached = {next(iter(vertices))}
    todo = list(reached)
    while todo:
        v = todo.pop()
        fresh = (adjacency[v] & vertices) - reached
        reached.update(fresh)
        todo.extend(fresh)
    return reached == vertices


def source_matrix(case):
    path = case['roles']['background']
    n = len(case['sizes'])
    adjacency = [set() for _ in range(n)]
    for v,w in case['meetings']:
        adjacency[v].add(w)
        adjacency[w].add(v)
    loose = [size-len(near) for size,near in zip(case['sizes'],adjacency)]
    assert min(loose)>0
    extras = sorted(set(range(n))-set(path))
    choices = [set(comb) for k in range(len(extras)+1) for comb in combinations(extras,k)]
    expected_baseline = [2]*len(path)
    matrix = [[0]*16 for _ in range(16)]
    for i,j in combinations(range(16),2):
        interval = set(path[i+1:j+1])
        best = None
        for c in choices:
            shore = interval | c
            if not connected(shore,adjacency):
                continue
            reading = sum(loose[v]+len(adjacency[v]-shore) for v in shore)-1
            if best is None or reading<best: best=reading
        shift = sum(2*((s-1) in interval)+4*(s in interval)+2*((s+1) in interval)
                    for s in case['roles']['seams'])
        prediction = 1+sum(expected_baseline[v] for v in interval)+shift
        assert best==prediction, (case['id'],i,j,best,prediction)
        matrix[i][j] = matrix[j][i] = best
    return matrix


def main():
    cases = json.loads((HERE/'inputs.json').read_text())['cases']
    answer = {c['id']:source_matrix(c) for c in cases if c['roles']['background']}
    OUTPUT.write_text(json.dumps({'verified_pairs':len(answer)*120,'matrices':answer},separators=(',',':'))+'\n')
    print('All',len(answer)*120,'marked source pairs verified.')


if __name__ == '__main__':
    main()
