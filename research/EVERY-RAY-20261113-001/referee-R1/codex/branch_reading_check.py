"""Independent branch/signature, sample-arithmetic, provenance, and wording audit.

Only standard-library code is imported. No producer Python is read or imported.
Run with the workspace .venv/bin/python -B. One process, no subprocesses.
"""
from __future__ import annotations

import collections
import gzip
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import random
import time
import traceback

ROOT = Path('/home/jscul/p-vs-np-contact-first')
OUT = ROOT / 'research/EVERY-RAY-20261113-001/referee-R1/codex'
EXP = ROOT / 'experiments/EVERY-RAY-20261113-001A/EVERY-RAY-20261113-001A-E001_min_over_paths'
SAMPLE = EXP / 'codex/sample'
GATES = EXP / 'codex/gates_full'
BRANCH = ROOT / 'artifacts/BRANCH-DEPTH-20261112-001C/BRANCH-DEPTH-20261112-001C-E001_port_census'
CENSUS = ROOT / 'artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz'
INVENTORY = ROOT / 'research/TRUE-RATE-20261113-001/referee-R1/codex/family_inventory.json'
INF = 10**9
READS = {}
START = time.monotonic()


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def read_json(path):
    READS[str(path.relative_to(ROOT))] = sha(path)
    with path.open() as f:
        return json.load(f)


def read_rows(path):
    READS[str(path.relative_to(ROOT))] = sha(path)
    op = gzip.open if path.suffix == '.gz' else open
    with op(path, 'rt') as f:
        return [json.loads(line) for line in f if line.strip()]


def compact(x):
    return json.dumps(x, separators=(',', ':'), sort_keys=True)


def count(rows, field):
    return dict(collections.Counter(str(r.get(field)) for r in rows))


def wilson(k, n):
    z = 1.959963984540054
    p = k / n
    den = 1 + z*z/n
    center = (p + z*z/(2*n)) / den
    half = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / den
    return [center-half, center+half]


def band(rows, success, unresolved):
    n = len(rows)
    k = sum(success(r) for r in rows)
    u = sum(unresolved(r) for r in rows)
    return dict(n=n, k=k, unresolved=u, low=k/n, high=(k+u)/n,
                wilson_low=wilson(k, n), wilson_high=wilson(k+u, n),
                envelope=[wilson(k,n)[0], wilson(k+u,n)[1]])


def usual(defs):
    """Frozen usual-limit addition, written from the mathematical specification."""
    out = []
    for k, own, calls in defs:
        calls = [[c, list(a)] for c, a in calls]
        if any(c == 'SELF' and sorted(a) == [0,1,2] for c,a in calls):
            calls.append(['K', [0,1,2]])
        out.append([k, own, calls])
    return out


def one_relation(defn, relation, omit=None):
    k, own, calls = defn
    states = []
    for a in range(1 << (k+own)):
        good = True
        for j,(callee,args) in enumerate(calls):
            if j == omit:
                continue
            t = sum(((a >> x) & 1) << q for q,x in enumerate(args))
            if callee == 'K':
                good = t not in (0,7)
            elif callee == 'SELF':
                good = bool(relation & (1 << t))
            else:
                raise ValueError('one-definition signature received another callee')
            if not good:
                break
        if good:
            states.append(a)
    rel = 0
    for a in states:
        rel |= 1 << (a & ((1 << k)-1))
    return rel, states


def signature(defs):
    """Full finite port transition, not an ordinal/idx assumption."""
    if len(defs) != 1 or defs[0][0] != 3:
        return None
    d = usual(defs)[0]
    own = d[1]
    selfcalls = [(j,a) for j,(c,a) in enumerate(d[2]) if c == 'SELF']
    if not selfcalls:
        return None
    r = 255
    for _ in range(257):
        q,_ = one_relation(d, r)
        if q == r:
            break
        r = q
    _, states = one_relation(d, r, omit=selfcalls[0][0])
    args = selfcalls[0][1]
    # A child in the limit must itself have an admissible G-state.  This is
    # material for the single inventory member with non-TOP G.
    transition = sorted({(a & 7, t) for a in states
                         for t in [sum(((a >> x)&1) << j for j,x in enumerate(args))]
                         if (r >> t)&1})
    first_dead = None
    seen = set()
    finite = 126
    for depth in range(1,258):
        finite,_ = one_relation(d, finite)
        if not finite and first_dead is None:
            first_dead = depth
        if finite in seen:
            break
        seen.add(finite)
    obj = dict(own=own, children=len(selfcalls), allowed=[a for a in range(8) if (r >> a)&1],
               transition=[list(t) for t in transition], first_dead=first_dead)
    return obj


def independent_local_symmetry(defs):
    d=usual(defs)[0]
    r=255
    while True:
        q,states=one_relation(d,r)
        if q==r:
            break
        r=q
    allowed=set(states)
    perms=[]
    for p in itertools.permutations(range(3)):
        moved=set()
        for a in allowed:
            b=a & ~7
            for j in range(3):
                b |= ((a>>j)&1)<<p[j]
            moved.add(b)
        if moved==allowed:
            perms.append(p)
    calls=[tuple(a) for c,a in d[2] if c=='SELF']
    classes=[]
    remaining=set(range(len(calls)))
    while remaining:
        i=min(remaining)
        orbit={tuple(p[a] if a<3 else a for a in calls[i]) for p in perms}
        group=sorted(j for j in remaining if calls[j] in orbit)
        classes.append(group)
        remaining.difference_update(group)
    return dict(permutations=[list(p) for p in perms],classes=classes)


def port_signature(row):
    return {k: row.get(k) for k in ('own','children','allowed','transition','first_dead')}


def main_entries(defs, S):
    """Expand ordinary calls only; a SELF call is a recurrence boundary."""
    if len(defs)-1 == S:
        return sum(c == 'SELF' for c,a in defs[S][2])
    memo = {}
    def rec(i):
        if i in memo:
            return memo[i]
        total = 0
        for c,a in defs[i][2]:
            if isinstance(c, int):
                total += 1 if c == S else rec(c)
        memo[i] = total
        return total
    return rec(len(defs)-1)


def audit():
    result = dict(independence='Fresh standard-library audit; no producer Python read/imported.',
                  thread_id=os.environ.get('CODEX_THREAD_ID'), sections={}, errors=[])
    sections = result['sections']
    selection = read_json(SAMPLE/'selection.json')
    sources = {name: read_rows(SAMPLE/(name+'.jsonl'))
               for name in ('G','N','B','B_resume','phase2','brute_panel_source')}
    gates = read_rows(GATES/'validation_reg.jsonl')
    last = read_rows(GATES/'validation_last.jsonl')
    reading = read_json(EXP/'sample_reading.json')
    inventory = read_json(INVENTORY)
    ports = read_json(BRANCH/'port_tables.json')['rows']
    outcomes = read_json(BRANCH/'outcomes.json')['rows']
    branch_outcome = {(r['file'],r['line']):r for r in outcomes}
    final = {name:{r['key']:r for r in sources[name]} for name in ('G','N')}
    final['B'] = {r['key']:r for r in sources['B'] + sources['B_resume']}
    phase2_changes = []
    for r in sources['phase2']:
        name = next((n for n in ('G','N') if r['key'] in final[n]), None)
        if name:
            old = final[name][r['key']]
            phase2_changes.append(dict(key=r['key'],stratum=name,old=old.get('class_path'),
                                       new=r.get('class_path'),old_status=old.get('status'),new_status=r.get('status')))
            final[name][r['key']] = r
    finalrows = {n:[final[n][k] for k in selection[n] if k in final[n]] for n in final}
    allkeys = {r['key'] for rows in sources.values() for r in rows} | {r['key'] for r in gates+last}
    allkeys.update(compact(item['defs']) for item in inventory)
    archive = {}
    pools = {'G':[], 'N':[], 'B':[]}
    eligible_by_class = collections.Counter()
    census_counts = collections.Counter()
    gatekeys = {r['key'] for r in last}
    READS[str(CENSUS.relative_to(ROOT))] = sha(CENSUS)
    with gzip.open(CENSUS,'rt') as f:
        for line in f:
            r = json.loads(line)
            k = r['key']
            if k in allkeys:
                archive[k] = r
            defs = json.loads(k)
            S = r.get('S')
            if S is None:
                continue
            c = sum(q == 'SELF' for q,a in defs[S][2])
            cls = r.get('class','')
            if c < 2 or cls.startswith(('S1','S2','S3')):
                continue
            eligible_by_class[cls] += 1
            group = 'G' if cls == 'grows' else ('N' if cls in ('none at any depth','lost at large depths') else ('B' if cls == 'bounded' else None))
            if group:
                census_counts[group] += 1
                if group != 'G' or k not in gatekeys:
                    pools[group].append(k)
    rng = random.Random(selection['seed'])
    reconstructed = {n:rng.sample(sorted(pools[n]), len(selection[n])) for n in ('G','N','B')}
    sections['selection'] = dict(seed=selection['seed'],recorded_pool_sizes=selection['sizes'],
        reconstructed_pool_sizes={n:len(v) for n,v in pools.items()},census_strata_counts=dict(census_counts),
        eligible_by_class=dict(eligible_by_class),eligible_total=sum(eligible_by_class.values()),
        matches={n:reconstructed[n] == selection[n] for n in reconstructed},
        selected_sizes={n:len(selection[n]) for n in final},
        final_coverage={n:len(finalrows[n]) for n in final},
        duplicate_counts={n:len(sources[n])-len({r['key'] for r in sources[n]}) for n in sources},
        missing={n:sorted(set(selection[n])-set(final[n])) for n in final},
        extra={n:sorted(set(final[n])-set(selection[n])) for n in final})

    G,N,B = (finalrows[n] for n in ('G','N','B'))
    p1rows = [r for r in G if r.get('symmetry_inequivalent') is True]
    inequivalent_missing = [r['key'] for r in G if r.get('symmetry_inequivalent') not in (True,False)]
    unresolved = lambda r:r.get('class_path') == 'unresolved'
    p1 = band(p1rows, lambda r:r.get('class_path') == 'bounded', unresolved)
    unc = band(p1rows,lambda r:r.get('class_path_uncarried') == 'bounded',
               lambda r:r.get('class_path_uncarried') == 'unresolved')
    p3 = band(N,lambda r:r.get('class_path') in ('grows','bounded','mixed by residue'),unresolved)
    verdict = 'holds' if p1['envelope'][0] >= .75 else ('fails' if p1['envelope'][1] < .75 else 'undecided')
    equivalent = [r for r in G if r.get('symmetry_inequivalent') is False]
    bounded = [r for r in p1rows if r.get('class_path') == 'bounded']
    mixed = [r for r in p1rows if r.get('mixed_path_needed') is True]
    grows = [r for r in G+N if r.get('class_path') == 'grows']
    sections['arithmetic'] = dict(G_classes=count(G,'class_path'),N_classes=count(N,'class_path'),
        B_classes=count(B,'class_path'),B_split=count(B,'bounded_split'),
        P1=p1,P1_uncarried=unc,P1_verdict=verdict,P3=p3,
        P3_hit_classes=count([r for r in N if r.get('class_path') in ('grows','bounded','mixed by residue')],'class_path'),
        P1_mixed_path_needed=len(mixed),P1_carried_only=sum(r.get('bounded_split')=='bounded, carried only' for r in bounded),
        P1_uncarried_classes_of_bounded=count(bounded,'class_path_uncarried'),
        P1_carried_only_rows=[{k:r.get(k) for k in ('key','class_path_uncarried','bounded_split','status')} for r in bounded if r.get('bounded_split')=='bounded, carried only'],
        B_uncarried_classes=count(B,'class_path_uncarried'),
        B_carried_only_uncarried_classes=count([r for r in B if r.get('bounded_split')=='bounded, carried only'],'class_path_uncarried'),
        B_corrected_split=dict(bounded_uncarried=sum(r.get('class_path_uncarried')=='bounded' for r in B),
            no_uncarried_bond=sum(r.get('class_path_uncarried')=='none at any depth' for r in B),
            uncarried_unresolved=sum(r.get('class_path_uncarried')=='unresolved' for r in B)),
        symmetry_unknown=inequivalent_missing,
        P2_inequivalent_growers=sum(r.get('symmetry_inequivalent') is True for r in grows),
        P2_all_growers_complete=all(r.get('complete') for r in grows),
        G_grower_lambda=count([r for r in G if r.get('class_path') == 'grows'],'lambda_path'),
        G_grower_uncarried=count([r for r in G if r.get('class_path') == 'grows'],'class_path_uncarried'),
        equivalent_G=[dict(**{k:r.get(k) for k in ('key','first_ray_class','class_path','c','symmetry_equivalence_classes','lambda_path','mixed_path_needed')}, independent_symmetry=independent_local_symmetry(json.loads(r['key']))) for r in equivalent],
        certificate_bound_distribution=count(bounded,'uniform_cost_bound'),
        L30_distribution=dict(collections.Counter(str(r.get('L_path', [None])[-1]) if r.get('L_path') else 'missing' for r in bounded)),
        certificate_bound_outliers=[{k:r.get(k) for k in ('key','uniform_cost_bound','onset_depth','L_path')} for r in bounded if r.get('uniform_cost_bound') is not None and not 3 <= r['uniform_cost_bound'] <= 9],
        weight_recomputation='Not possible from allowed rows/selection/family census: no per-family draw counts. Published weight summaries remain unaudited.',
        reported_reading=reading)
    for n in ('G','N','B'):
        sections['arithmetic'][n+'_by_c'] = {str(c):dict(n=len(z),resolved=sum(not unresolved(r) for r in z),
            grows=sum(r.get('class_path')=='grows' for r in z),bounded=sum(r.get('class_path')=='bounded' for r in z),
            unresolved=sum(unresolved(r) for r in z)) for c,z in ((c,[r for r in finalrows[n] if r['c']==c]) for c in sorted({r['c'] for r in finalrows[n]}))}
    sections['arithmetic']['mixed_fixed_index_issues'] = []
    for r in mixed:
        rays = r.get('fixed_index_rays',[])
        issue = []
        if len(rays) != r.get('fixed_index_pairs_total'):
            issue.append('not all entry/call pairs recorded')
        if any(z.get('class') == 'bounded' for z in rays):
            issue.append('bounded pair contradicts mixed flag')
        if any(not z.get('complete') or z.get('class') == 'unresolved' for z in rays):
            issue.append('unresolved fixed pair')
        if issue:
            sections['arithmetic']['mixed_fixed_index_issues'].append(dict(key=r['key'],issues=issue))

    checked = []
    for r in gates:
        ar = archive.get(r['key'],{})
        S = ar.get('S')
        defs = json.loads(r['key'])
        e = main_entries(defs,S) if S is not None else None
        checked.append(dict(key=r['key'],entries=e,passed=r.get('passed'),
            graph_equal=r.get('path_graph') == r.get('census_graph'),
            class_equal=r.get('path_class') == r.get('census_class'),
            lambda_equal=r.get('path_lambda') == r.get('census_lambda'),
            mismatch_fields=[m['field'] for m in r.get('mismatches',[])]))
    mismatched = [r for r in checked if not r['graph_equal']]
    oneentry = [r for r in checked if r['entries']==1]
    sections['G_reg'] = dict(rows=len(checked),graph_equal=sum(r['graph_equal'] for r in checked),
        one_entry_rows=len(oneentry),one_entry_all_graph_equal=all(r['graph_equal'] for r in oneentry),
        mismatch_rows=mismatched,all_mismatches_multientry=all(r['entries'] is not None and r['entries']>=2 for r in mismatched),
        all_classes_equal=all(r['class_equal'] for r in checked),all_lambdas_equal=all(r['lambda_equal'] for r in checked),
        missing_archive_keys=[r['key'] for r in checked if r['entries'] is None],
        chronology=[
          'Initial spec and prereg required graph/lambda/class equality on c=1.',
          'A1 addendum frees main entry; it still incorrectly says G-reg start fix changes nothing for c=1.',
          'Third prereg clarification, after gate results and before class shares, restricts G-reg to c=1 AND one entry.',
          'Current data retain 9 graph mismatches among 500; reinterpretation is justified for the narrowed gate, not an original-gate pass.' ])

    # Compare every overlap in the allowed sample files, with mathematical fields separated from run telemetry.
    semantic_fields = ['L_path','L_path_uncarried','class_path','class_path_uncarried','lambda_path',
        'bounded_split','mixed_path_needed','first_ray_class','first_ray_carried',
        'symmetry_inequivalent','symmetry_equivalence_class_count','pass_through_zero_cycle',
        'uniform_cost_bound','eventually_bounded','period','onset_depth',
        'exact_eventual_boundedness','uncarried_result','bounded_all','fixed_index_rays',
        'fixed_index_status','fixed_index_pairs_total','literal_duplicate_self_calls',
        'symmetry_equivalence_classes','symmetry_port_permutations','symmetry_flat_allowed_states',
        'symmetry_class_representatives','symmetry_flat_distinctions','first_ray_port_masks',
        'zero_mean_cycle_uses_pass_through','zero_cost_cycle_witnesses','missing_residues',
        'zero_mean','c','S','main_block_size','main_own','s_block_size','s_own','n_defs']
    overlaps = []
    for a,b in itertools.combinations(sources,2):
        aa={r['key']:r for r in sources[a]}
        bb={r['key']:r for r in sources[b]}
        keys=sorted(set(aa)&set(bb))
        diffs=[]
        for k in keys:
            ra,rb=aa[k],bb[k]
            changed={f:[ra.get(f),rb.get(f)] for f in semantic_fields if ra.get(f)!=rb.get(f)}
            completed_a=ra.get('class_path')!='unresolved'
            completed_b=rb.get('class_path')!='unresolved'
            if changed:
                diffs.append(dict(key=k,fields=changed,both_resolved=completed_a and completed_b,
                    kind='resolved_conflict' if completed_a and completed_b else 'cap_or_resolution_difference'))
        overlaps.append(dict(a=a,b=b,n=len(keys),equal=len(keys)-len(diffs),differences=diffs))
    info = {}
    for n in ('G','N','B','B_resume','phase2'):
        d=read_json(SAMPLE/(n+'.jsonl.run_info.json'))
        info[n]={k:d.get(k) for k in ('code_fingerprint','code_sha256','started_at','updated_at','status','requested','written','options')}
    sections['version_consistency'] = dict(pairwise_overlaps=overlaps,run_info=info,semantic_fields=semantic_fields,
        phase2_changes=phase2_changes,
        resolved_conflicts=[dict(a=p['a'],b=p['b'],**d) for p in overlaps for d in p['differences'] if d['both_resolved']],
        limitation='B and B_resume use two paths_dp hashes but have disjoint keys; no same-input successful cross-version replay is established by those files alone.')

    # Exact definition -> prior inventory -> independently recomputed port signature -> branch artifact.
    ports_by_signature=collections.defaultdict(list)
    for r in ports:
        ports_by_signature[compact(port_signature(r))].append(r)
    defs_to_inventory=collections.defaultdict(list)
    inventory_mapping=[]
    for i,item in enumerate(inventory):
        defs=item['defs']
        defs_to_inventory[compact(defs)].append(item)
        defs_to_inventory[compact(usual(defs))].append(item)
        sig=signature(defs)
        candidates=ports_by_signature.get(compact(sig),[])
        old=archive.get(compact(defs),{})
        inventory_mapping.append(dict(idx=item['idx'],signature=sig,archived_class=old.get('class'),
            archived_complete=old.get('complete'),in_G_last=compact(defs) in gatekeys,
            candidates=[dict(file=r['file'],line=r['line'],outcome=branch_outcome.get((r['file'],r['line']),{}).get('outcome')) for r in candidates]))
    map_by_idx={r['idx']:r for r in inventory_mapping}
    family_maps=[]
    for stratum,rows in finalrows.items():
        for r in rows:
            defs=json.loads(r['key'])
            if len(defs)!=1:
                continue
            items={d['idx']:d for d in defs_to_inventory.get(compact(defs),[])+defs_to_inventory.get(compact(usual(defs)),[])}
            links=[map_by_idx[idx] for idx in sorted(items)]
            family_maps.append(dict(key=r['key'],stratum=stratum,class_path=r.get('class_path'),
                first_ray_class=r.get('first_ray_class'),lambda_path=r.get('lambda_path'),
                inventory_indices=sorted(items),branch_links=links,
                bounded_path_vs_fixed_target_linear=bool(r.get('class_path')=='bounded' and any(c['outcome']=='linear' for link in links for c in link['candidates'])) ))
    sections['branch_mapping']=dict(inventory_rows=len(inventory),branch_rows=len(ports),
        independent_signature_match_counts=dict(collections.Counter(str(len(r['candidates'])) for r in inventory_mapping)),
        inventory_mapping=inventory_mapping,sample_one_definition=len(family_maps),
        linear_signature_archive_classes=dict(collections.Counter(str(r['archived_class']) for r in inventory_mapping if any(c['outcome']=='linear' for c in r['candidates']))),
        linear_not_in_G_last=[r for r in inventory_mapping if not r['in_G_last'] and any(c['outcome']=='linear' for c in r['candidates'])],
        sample_exact_inventory_matches=sum(bool(r['inventory_indices']) for r in family_maps),
        sample_unique_port_signature_matches=sum(len(r['branch_links'])==1 and len(r['branch_links'][0]['candidates'])==1 for r in family_maps),
        sample_matches=family_maps,
        fixed_target_linear_path_bounded=[r for r in family_maps if r['bounded_path_vs_fixed_target_linear']],
        identity_limit='Raw source (sample_file,line) -> exact definition bridge is not an allowed input. Port signatures corroborate matching but are not source-record identity. No ordinal zip was used.',
        inequality='L_true <= L_path is not valid generally: L_true fixes the first-ray target, while L_path minimizes over target copies/paths. Valid frozen bounds: L_any <= L_true and L_any <= L_path <= L_ray. Same-target comparisons alone permit L_true <= path-restricted bond.')
    gate_maps=[]
    for r in last:
        defs=json.loads(r['key'])
        items={d['idx']:d for d in defs_to_inventory.get(compact(defs),[])+defs_to_inventory.get(compact(usual(defs)),[])}
        links=[map_by_idx[idx] for idx in sorted(items)]
        candidates=[c for link in links for c in link['candidates']]
        path=r.get('L_path',[])
        gate_maps.append(dict(key=r['key'],reported_idx=r.get('idx'),inventory_indices=sorted(items),
            branch_links=links,passed=r.get('passed'),status=r.get('status'),
            L_path=path,L_first=r.get('L_first'),L_last=r.get('L_last'),
            possible_branch_outcomes=sorted({c['outcome'] for c in candidates}),
            finite_path_bound=max(path) if path and max(path)<INF else None))
    sections['branch_mapping']['G_last']=dict(rows=len(gate_maps),
        exact_inventory_matches=sum(bool(r['inventory_indices']) for r in gate_maps),
        reported_idx_agrees=sum(r['inventory_indices']==[r['reported_idx']] for r in gate_maps),
        unique_signature_matches=sum(len(r['branch_links'])==1 and len(r['branch_links'][0]['candidates'])==1 for r in gate_maps),
        unambiguous_outcome_counts=dict(collections.Counter(r['possible_branch_outcomes'][0] if len(r['possible_branch_outcomes'])==1 else 'ambiguous' for r in gate_maps)),
        linear_target_path_finite_bound_examples=[r for r in gate_maps if r['possible_branch_outcomes']==['linear'] and r['finite_path_bound'] is not None],
        rows_detail=gate_maps,
        limitation='G-last records finite layers only and path_result is deliberately class unresolved; finite bounded prefixes do not prove eventual path boundedness. BRANCH linear is fixed first-branch target, so bounded other-target paths would not contradict it.')

    # Report the text being audited with exact locations, without changing it.
    report=ROOT/'research/EVERY-RAY-20261113-001/every_ray.md'
    prereg=ROOT/'research/EVERY-RAY-20261113-001/preregistration.md'
    for p in (report,prereg):
        READS[str(p.relative_to(ROOT))]=sha(p)
    needles=['at every depth','usually','in families with one self-call','certified bounds','are all bounded',
             'only equivalent calls','along **every**','every path','A80','3 to 9','three to nine','6,925']
    textfind=[]
    for i,line in enumerate(report.read_text().splitlines(),1):
        if any(n in line for n in needles):
            textfind.append(dict(line=i,text=line))
    sections['wording'] = dict(lines=textfind,
        required_narrowings=[
          'Use sample-proportion wording for 600 sampled families; do not silently infer prevalence across all admissible families or substrates.',
          'Bounded L_path means for every sufficiently large finite depth there exists a path/bond with a uniform cost bound. It does not by itself exhibit one infinite path whose every-depth bonds are uniformly bounded.',
          'Saved uniform_cost_bound and depth_threshold are eventual certificates; all-depth bounds need the finite prefix and any infinite-path assertion needs its own coherent witness.',
          'Do not claim all c=1 families grow: c=1 removes call choice, but first-ray classes include bounded/none/lost.',
          'One SELF call alone does not imply one path: multiple main entries remain. One SELF call and one entry is the valid equality domain.',
          'Local port-symmetry equivalence does not imply L_path=L_ray; the four observed equivalent-call G counterexamples directly refute the frozen construction claim.',
          'Correct the bound-range statement or provide additional certificates justifying a tighter range; current saved uniform certificates include 2 and 14.',
          'For P3 label the 12.0–22.8 percent interval as the unresolved-aware Wilson envelope, not a single Wilson interval for 33/200.',
          'G-reg passed only the revised one-entry domain; original 500-family graph-equality gate has 9 preserved mismatches.',
          'A plain-bounded row with unresolved uncarried class is not proved carried-only. Include the extra one G and five B rows in uncarried uncertainty.',
          'The report may state finite-path uniform lower growth on complete graphs; it does not establish members-anywhere, target-free, native distance, or infinite coherent-path claims.' ])
    result['runtime_seconds']=time.monotonic()-START
    result['input_sha256']=READS
    return result


if __name__ == '__main__':
    try:
        result=audit()
    except BaseException as e:
        result=dict(fatal_error=repr(e),traceback=traceback.format_exc(),input_sha256=READS,
                    runtime_seconds=time.monotonic()-START)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'branch_reading_results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    summary={k:v for k,v in result.items() if k in ('fatal_error','runtime_seconds','thread_id')}
    if 'sections' in result:
        s=result['sections']
        summary.update(selection=s['selection'],
            arithmetic={k:s['arithmetic'][k] for k in ('G_classes','N_classes','B_split','P1','P1_uncarried','P1_verdict','P3','P1_mixed_path_needed','P2_inequivalent_growers','certificate_bound_distribution')},
            G_reg={k:v for k,v in s['G_reg'].items() if k not in ('mismatch_rows','chronology')},
            branch={k:s['branch_mapping'][k] for k in ('sample_one_definition','sample_exact_inventory_matches','sample_unique_port_signature_matches','independent_signature_match_counts')},
            overlaps=[{k:v for k,v in p.items() if k!='differences'} for p in s['version_consistency']['pairwise_overlaps']],
            resolved_overlap_conflicts=len(s['version_consistency']['resolved_conflicts']))
    print(json.dumps(summary,indent=2,sort_keys=True))
