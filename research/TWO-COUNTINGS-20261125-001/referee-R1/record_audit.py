"""Audit the comparison table, selection, prior work and reporting denominators."""
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import product
import json
from hashlib import sha256
from pathlib import Path
import random
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STUDY = HERE.parent
TICKET = STUDY.with_name(STUDY.name + "A")
RAW = next((ROOT / "artifacts" / TICKET.name).iterdir())


def read(path):
    return json.loads(path.read_text())


def prior_work(pilot):
    args = [sys.executable, "-B", "scripts/track.py"]
    reg = TICKET / "preregistration.md"
    gate = subprocess.run(args + ["objects-gate", str(reg)], cwd=ROOT, capture_output=True, text=True)
    section = reg.read_text().split("## Prior work in the program")[1].split("## Prior work outside")[0]
    queries = re.findall(r'track\.py objects "([^"]+)"', section)
    queries.extend(["control weighting setting births keep old distribution hidden score",
                    "knot tested in whole setting births hidden score control weighting smallest excess",
                    "recursive division uniform reached pair disagreement rate tables explosive 150 births"])
    if pilot:
        queries = queries[:1]
    hits = {}
    for query in queries:
        cmd = args + ["objects", query, "--until", "2026-11-25", "--exclude", STUDY.name, "--limit", "3", "--json"]
        out = json.loads(subprocess.check_output(cmd, cwd=ROOT, text=True))
        hits[query] = [dict(epic=row["epic"], record=row["record"]) for row in out["index"]]
    return {"gate": gate.stdout.strip(), "exit": gate.returncode, "index_hits": hits}


def table_inventory():
    reg = {r['id']: r for r in read(STUDY / 'table.json')['rows']}
    filed = {r['id']: r for r in read(RAW / 'summary.json')['table']}
    assert reg.keys() == filed.keys()
    groups = defaultdict(list)
    discrepancies = []
    for name, r in filed.items():
        copied = 'not recomputed here' in r['source']
        groups['copied' if copied else 'recomputed'].append(name)
        if copied:
            for key in ('from the finish', 'from the start', 'knots in the whole', 'statement'):
                if r[key] != reg[name][key]:
                    discrepancies.append([name, key])
        for key in ('from the finish', 'from the start'):
            if not r[key]:
                groups['empty_' + key].append(name)
            if r[key] == 'see record':
                groups['reference_only_' + key].append(name)
    return {'rows': dict(groups), 'copied_fields_different': discrepancies}


def selection(pilot):
    orders = read(TICKET / 'construction_orders.json')
    shuffles = {}
    for name in sorted(orders.keys() - {'about'}):
        x = orders[name]
        rng = random.Random(x['seed'])
        n = 3 if pilot else len(x['orders'])
        matches = 0
        for entry in x['orders'][:n]:
            generated = list(range(x['k']))
            rng.shuffle(generated)
            matches += generated == entry
        shuffles[name] = {'checked': n, 'seed_matches': matches,
                          'distinct_orders': len({tuple(p) for p in x['orders'][:n]})}
    sample = read(TICKET / 'census_index.json')
    ids = [s['census_index'] for s in sample['starts']]
    regenerate = sorted(random.Random('TWO-COUNTINGS|census|5|v2').sample(range(sample['census_size']), 100))
    return {'orders': shuffles, 'seeded_census_ids_agree': ids == regenerate,
            'census_frame': sample['census_size'], 'census_count': len(ids),
            'grow_again_census_ids': ids[:10]}


def archive_scores(pilot):
    records = read(RAW / 'part2_lemma.json')['records']
    if pilot:
        records = records[:5]
    comparisons = defaultdict(Counter)
    mixed = Counter()
    rule_sets = defaultdict(set)
    for record in records:
        source = record['record']['source']
        old_score = Fraction(record['record']['eval'][-1])
        variant, = record['variants']
        final = variant['rows']['from the finish']
        row = comparisons[source]
        row['histories'] += 1
        for metric in ('score_all', 'score_parity', 'score_parity_abs'):
            row[metric + '_equals_record'] += Fraction(final[metric]) == old_score
        for label, obj in variant['rows'].items():
            if label.startswith('mixed'):
                mixed[(obj['score_all'], obj['hidden'])] += 1
        key = tuple(tuple(sorted(rules)) for _, rules in sorted(variant['finished'].items()))
        rule_sets[source].add(key)
    return {'policy_comparisons': comparisons,
            'distinct_named_fours_by_archive': {k: len(v) for k, v in rule_sets.items()},
            'distinct_named_fours_combined':len(set().union(*rule_sets.values())),
            'mixed_in_archives': [{'score':s,'hidden':h,'rows':n} for (s,h),n in sorted(mixed.items())]}


def endpoint_agreement():
    # Two successive private not-all-equal births on the two opposite input choices.
    # Generate the actual start by enumerating even(x,h,k), odd(y,h,k), and even(t,l,m).
    base = [o for o in product(range(2), repeat=7)
            if (o[1] + o[3] + o[4]) % 2 == 0 and (o[2] + o[3] + o[4]) % 2 == 1
            and (o[0] + o[5] + o[6]) % 2 == 0]
    weights = {s: Fraction(1,len(base)) for s in base}
    result = []
    for old in (1,2):
        nxt = {}
        for state, weight in weights.items():
            fresh = [v for v in (0,1) if len({state[0],state[old],v}) > 1]
            for v in fresh:
                nxt[state + (v,)] = weight / len(fresh)
        weights = nxt
        result.append({'states':len(nxt), 'weights':dict(Counter(map(str,nxt.values()))),
                       'total_variation_from_finish':str(sum(abs(w - Fraction(1,len(nxt))) for w in nxt.values())/2)})
    return result


def frozen_inputs():
    contract = read(next((ROOT / 'experiments' / TICKET.name).glob('*/contract.json')))
    inputs = dict(contract['data_files'])
    for key, digest in contract.items():
        if key.endswith('_sha256'):
            inputs[contract[key.removesuffix('_sha256')]] = digest
    return {name: sha256((ROOT / name).read_bytes()).hexdigest() == digest for name, digest in inputs.items()}


def main():
    pilot = sys.argv[1:] == ["--pilot"]
    result = {'frozen_input_digests_agree': frozen_inputs(), 'prior_work': prior_work(pilot), 'table':table_inventory(), 'selection':selection(pilot),
              'archive_fields':archive_scores(pilot), 'endpoint_agreement_example':endpoint_agreement()}
    if pilot:
        print("Checked a prior-work query, three shuffles per order list, and five records.")
    else:
        (HERE / 'record_counts.json').write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
