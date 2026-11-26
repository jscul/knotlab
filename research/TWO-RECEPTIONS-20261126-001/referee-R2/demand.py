"""Test implied births directly where changing the knot law changes the published summary."""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import parity
from archive import STUDY, key, read_rows

eng = parity.eng
core = parity.shortage


def selected():
    paired = {key(r): r for r in read_rows(STUDY / 'shortage_runs.jsonl.gz', None)
              if r.get('law', [''])[0] == 'ORD'}
    fields = ('ended', 'rounds', 'linked', 'changes', 'made short')
    return [r for r in read_rows(STUDY / 'parity_runs.jsonl.gz', None) if 'law' in r
            and key(r) in paired and any(r[f] != paired[key(r)][f] for f in fields)]


def rank(words):
    basis = {}
    for word in words:
        while word:
            i = word.bit_length() - 1
            if i not in basis:
                basis[i] = word
                break
            word ^= basis[i]
    return len(basis)


def check(r, rounds):
    a, b, (take, choice) = key(r)
    places, _, _ = core.jam.changed(a, b, 3, None, 'meeting')
    law = core.law_of(*r['law'])
    assert law.knot_law == 'parity'
    s = eng.from_stars(places)
    guard = eng.Guard(4)
    demand = Counter()
    examples = {}
    implied_ranks = Counter()
    births = short = 0
    for _ in range(min(rounds, r['rounds'])):
        previous_basis = tuple(s.basis.values())
        rec = eng.play_round(s, law, guard)
        short += sum(s.made[u] > 0 for u in rec['short'])
        births += len(rec['births'])
        for birth in rec['births']:
            if birth['implied']:
                amount = birth['D']
                assert birth['f'] == 0
                demand[amount] += 1
                support = sum(1 << d for d in birth['inputs'])
                constraints = len(previous_basis) - rank(w & ~support for w in previous_basis)
                implied_ranks[(amount, constraints)] += 1
                if amount not in examples:
                    provisional = [list(g) for g in rec['demand'].groups if birth['id'] in g]
                    examples[amount] = {'round': s.round, 'birth': birth['id'], 'parents': birth['parents'],
                                        'inputs': birth['inputs'], 'fresh': birth['f'], 'groups': provisional}
    return {'receiver': a, 'sender': b, 'setting': [take,choice], 'completed rounds': s.round,
            'recorded rounds': r['rounds'], 'births': births, 'implied by demand': dict(demand),
            'input constraints': [[d,k,n] for (d,k),n in sorted(implied_ranks.items())],
            'first example per demand': examples, 'short made observations': short}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--count', type=int)
    p.add_argument('--rounds', type=int, required=True)
    args = p.parse_args()
    core.receivers.register()
    cases = selected()[:args.count]
    print(json.dumps([check(r, args.rounds) for r in cases], indent=2))
