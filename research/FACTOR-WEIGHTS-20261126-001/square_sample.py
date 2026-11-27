"""square_sample.py: the event-ready square on sampled starts (README.md, part C; frozen in preregistration.md). Census
starts (forbid.py's census of 7,075 starts of three to five knots; COUNT drawn uniformly with seed 20261129; one vote per
start), parity growth on the canonical engine for two rounds (or until a round is not funded), under each of the three
arms (ordinary, one fewer, arity floor). A knot's
lineage is its start knot, or the union of its parents' lineages; reader regions are the places of the knots of one
start knot's lineage alone, and of the union of two such lineages against a third; the rest is the middle. For every
pair of regions that no knot joins (and every union against a third that no knot joins): e with the middle unread and
with the middle read for changes (VALUE-CHANGE's css.ebits). Per start: the largest e with the middle read for changes
over its separated pairs (two shared pairs make the square of certainty available, with its supplied pieces).
    square_sample.py COUNT"""
import sys, json, random, itertools, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'FORBID-EDITS-20261126-001')); sys.path.insert(0, str(HERE.parent / 'VALUE-CHANGE-20261126-001'))
import forbid, css            # noqa: E402


def run(count):
    S = forbid.census(); picks = sorted(random.Random(20261129).sample(range(len(S)), count))
    for i in picks:
      for arm in ('ordinary', 'one_fewer', 'arity_floor'):
          st = tuple(tuple(k) for k in forbid.supports_of(S[i]))
          lineage = {k: frozenset([k]) for k in range(len(st))}
          rounds = 0
          for r in range(2):
              new, status, births = forbid.grown(st, 'parity', arm)
              if status != 'funded': break
              for b in births: lineage[b['knot']] = frozenset().union(*(lineage[p] for p in b['parents']))
              st = tuple(tuple(k) for k in new); rounds += 1
          knots = [list(k) for k in st]; n0 = len(forbid.supports_of(S[i]))
          region = {s: sorted({d for u, k in enumerate(knots) if lineage[u] == frozenset([s]) for d in k}) for s in range(n0)}
          row = {'start': i, 'arm': arm, 'rounds': rounds, 'pairs': 0, 'pairs with e >= 1': 0, 'pairs with e >= 2': 0, 'knots': len(knots), 'separated pairs': 0, 'largest e, middle read for changes': 0,
                 'largest e, middle unread': 0}
          cands = [(region[a], region[b]) for a, b in itertools.combinations(range(n0), 2)]
          # a union of two regions lists each distinction once (css.ebits adds bits, so a repeated name would corrupt the set)
          cands += [(sorted(set(region[a]) | set(region[c])), region[b]) for a, b, c in itertools.permutations(range(n0), 3) if a < c]
          row['pairs'] = len(cands)
          for A, B in cands:
              if not A or not B or set(A) & set(B) or not css.separated(knots, A, B): continue
              row['separated pairs'] += 1
              ec = css.ebits(knots, A, B, 'changes')
              row['pairs with e >= 1'] += ec >= 1; row['pairs with e >= 2'] += ec >= 2
              row['largest e, middle read for changes'] = max(row['largest e, middle read for changes'], ec)
              row['largest e, middle unread'] = max(row['largest e, middle unread'], css.ebits(knots, A, B, 'unread'))
          print(json.dumps(row), flush=True)


if __name__ == '__main__':
    run(int(sys.argv[1]))
