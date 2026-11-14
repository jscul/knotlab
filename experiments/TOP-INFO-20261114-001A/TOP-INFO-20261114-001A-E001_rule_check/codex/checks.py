"""Exact plain pinning and shattered-side bond-pinning on original Q states."""
from __future__ import annotations
from itertools import combinations
import json
import time
import top_data as data
np = data.window.np


def projection_flags(projection, checkpoint=lambda: None):
    labels, rows = projection['labels'], projection['allowed']
    if not rows:
        raise ValueError('empty allowed relation')
    indices = {v: i for i, v in enumerate(labels)}
    V = tuple(sorted(set(projection['root_labels'])))
    X = tuple(sorted(set(projection['own_labels'])))
    if set(V) & set(X):
        raise ValueError('main ports and end own distinctions unexpectedly overlap')
    values = np.asarray(rows, dtype=np.int64)
    full_cache, count_cache = {(): True}, {(): 1}

    def count(support):
        support = tuple(sorted(support))
        if support not in count_cache:
            checkpoint()
            packed = np.zeros(len(values), dtype=np.int64)
            for j, v in enumerate(support):
                packed |= ((values >> indices[v]) & 1) << j
            count_cache[support] = len(np.unique(packed))
        return count_cache[support]

    def full(support):
        support = tuple(sorted(support))
        if support not in full_cache:
            full_cache[support] = len(values) >= 1 << len(support) and count(support) == 1 << len(support)
        return full_cache[support]

    v_count, x_count = count(V), count(X)
    joint_count = count(V + X)
    pinned = joint_count != v_count * x_count
    answer = dict(plain_pinned=pinned, bond_pinned=False, witness=None,
                  side_counts=[v_count, x_count], joint_count=joint_count)
    if not pinned:
        return answer

    def maximal_shattered(side):
        shattered = {()}
        for size in range(1, len(side) + 1):
            found = False
            for support in combinations(side, size):
                checkpoint()
                if all(support[:j] + support[j + 1:] in shattered for j in range(size)) and full(support):
                    shattered.add(support)
                    found = True
            if not found:
                break
        return sorted((t for t in shattered if t and not any(
            tuple(sorted(t + (x,))) in shattered for x in side if x not in t)), key=lambda t: (len(t), t))

    maxV, maxX = maximal_shattered(V), maximal_shattered(X)
    for T in maxV:
        for D in maxX:
            checkpoint()
            if not full(T + D):
                answer.update(bond_pinned=True, witness=dict(T=list(T), D=list(D), size=len(T)+len(D)))
                return answer
    return answer


def _aggregate(values):
    return dict(some_residue=any(values), every_residue=all(values))


def run_family(row, checkpoint=lambda: None):
    start = time.monotonic()
    raw = data.load_raw(row)
    prep, syn = data.coverage.syntax(row['key'])
    result = dict(key=row['key'], in_scope=row['in_scope'], weight=row['weight'], stratum=row['stratum'],
                  final_verdict=row['final_verdict'], complete=False, residues=[],
                  plain_pinned=dict(some_residue=None, every_residue=None),
                  bond_pinned=dict(some_residue=None, every_residue=None),
                  G2=raw.get('growth', {}).get('G2', {}), caps=[])
    if not raw['window'].get('complete'):
        result.update(skipped='source Q_s repeating part is capped/incomplete', seconds=time.monotonic()-start)
        return result
    phases = data.coverage._q_states(raw, prep, checkpoint)
    actual = data.inputs.load_paths().Preparation(json.loads(row['key']))
    body = data.window.body_allowed(actual, actual.S)
    repeated = sorted(set().union(*phases))
    flags = {}
    candidates = syn['candidates']
    for state in repeated:
        checkpoint()
        projection = data.window.project_state(actual, state, body)
        flag = projection_flags(projection, checkpoint)
        witnesses = []
        for k, x, z in candidates:
            if state[1][prep.k+k] >= prep.k:
                continue
            aliases = projection['end_aliases']
            tie = data.coverage._ties(projection, aliases[k], aliases[x], aliases[z])
            if not tie[3]:
                witnesses.append([k,x,z])
        flag['R_applies'] = bool(witnesses)
        if witnesses:
            flag['R_witness'] = witnesses[0]
        flags[state] = flag
    window = raw['window']
    for i, states in enumerate(phases):
        items = [flags[s] for s in sorted(states)]
        result['residues'].append(dict(residue=i, word_s_mod_period=(window['preperiod']+i)%window['period'],
            absolute_depth_mod_period=(window['preperiod']+i+int(raw['wrapper']))%window['period'],
            U=window['residues'][i]['U'], states=len(states),
            R_applies=any(x['R_applies'] for x in items),
            plain_pinned=any(x['plain_pinned'] for x in items),
            bond_pinned=any(x['bond_pinned'] for x in items),
            pinned_states=sum(x['plain_pinned'] for x in items),
            bond_pinned_states=sum(x['bond_pinned'] for x in items),
            bond_pinning_witness=next((dict(J=hex(q[0]),partition=list(q[1]),**flags[q]['witness']) for q in sorted(states) if flags[q]['bond_pinned']),None)))
    # Reproduce READ's resolved existential flag on its own (possibly coarser) residues.
    for old in row['R']['residues']:
        computed = any(result['residues'][i]['R_applies'] for i in old['Q_residues'])
        if computed != old['applies']:
            raise ValueError('recomputed state-wise existential R disagrees with reused READ ties')
    result.update(complete=True, preperiod=window['preperiod'], period=window['period'],
                  wrapper=raw['wrapper'], unique_repeating_states=len(repeated),
                  plain_pinned=_aggregate([r['plain_pinned'] for r in result['residues']]),
                  bond_pinned=_aggregate([r['bond_pinned'] for r in result['residues']]),
                  R_reproduction=True, seconds=time.monotonic()-start)
    return result
