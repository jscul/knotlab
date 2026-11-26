"""judge.py OUT.jsonl: the frozen test (README, "Frozen"): on every stage with B != 0 among the census, held-out and
witness stages, every nonzero element of B's span (up to 2^10), split into distinction-disjoint cycles in every way;
a binding is a split into three or more cycles each a class label not read by one knot."""
import sys, json, collections, itertools
sys.path.insert(0, '.')
import split as SP, binding as BD, forced as FD
forbid = FD.forbid


def judge_all(st):
    names, idx, holders, rows, Z, B, moves, local = SP.stage_data(st)
    if not B: return None
    cl = SP.classes
    def label(f): return all(bin(f & m).count('1') % 2 == 0 for m in moves) and any(bin(f & z).count('1') % 2 for z in Z)
    def unread(f): return not any(cl.rank(rows + loc + [f]) == cl.rank(rows + loc) for loc in local)
    k = min(len(B), 10); found = []; parts_max = 0
    for c in range(1, 2 ** k):
        v = 0
        for j in range(k):
            if (c >> j) & 1: v ^= B[j]
        cyc = SP.cycles_in(v, names, holders); n = 0
        for P in SP.partitions(v, cyc):
            n += 1; parts_max = max(parts_max, len(P))
            if len(P) >= 3 and all(label(x) and unread(x) for x in P):
                found.append({'size': bin(v).count('1'), 'parts': len(P)}); break
            if n > 5000: break
    return {'dim B': len(B), 'elements read': 2 ** k - 1, 'most cycles in a split': parts_max, 'bindings': found}


if __name__ == '__main__':
    out = sys.argv[1]
    todo = []
    for fn in ('forced_census.jsonl', 'forced_heldout.jsonl'):
        for l in open(fn):
            x = json.loads(l)
            ts = [r['round'] for r in x['rounds'] if r.get('dim B')]
            if ts: todo.append((x['start'], max(ts), ts))
    S = forbid.census(); held = {}
    with open(out, 'w') as f:
        for name, maxt, ts in todo:
            if name.startswith('census'): sup = forbid.supports_of(S[int(name.split()[1])])
            else:
                n, j = map(int, name.split()[-1].split('-')); sup = forbid.supports_of(forbid.sampled(n, 300, 20261206 + n)[j])
            st = sup
            for t in range(0, maxt + 1):
                if t: st, status, births = forbid.grown(st, 'parity', 'ordinary')
                if t in ts:
                    r = judge_all(st); r.update({'start': name, 'round': t}); f.write(json.dumps(r) + '\n'); f.flush()
        for name, sup in BD.witnesses():
            st = sup
            for t in range(0, 4):
                if t:
                    st, status, births = forbid.grown(st, 'parity', 'ordinary')
                    if status != 'funded': break
                r = judge_all(st)
                if r: r.update({'start': name, 'round': t}); f.write(json.dumps(r) + '\n'); f.flush()
