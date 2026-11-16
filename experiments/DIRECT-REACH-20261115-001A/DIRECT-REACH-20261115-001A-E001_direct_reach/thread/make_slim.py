"""Slim records of DIRECT-REACH-20261115-001A (the thread's own, 2026-11-16): one line per description of population D and of the U
pilot with the census profile, tie-class summary, threshold reach from top levels 2 and 3, accepted homomorphisms and life to depth 12;
and, separately, every refutation each record cites (SHA-256 of its CNF and LRAT, purpose, checker verdict). The certificates
themselves stay on disk under codex/certificates/ (30 GB)."""
import glob
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CODEX = HERE.parent / 'codex'
ROOT = HERE.parents[3]
OUT = ROOT / 'artifacts/DIRECT-REACH-20261115-001A/DIRECT-REACH-20261115-001A-E001_direct_reach'
OUT.mkdir(parents=True, exist_ok=True)


def lvl(v):
    return (int(v) + 1).bit_length() - 1


slim, hashes = [], {}
for f in sorted(glob.glob(str(CODEX / 'case_results/*/*.json'))):
    d = json.load(open(f))
    ties = d.get('ties', {})
    rec = dict(case=d['case'], pop=d['pop'], key=d['key'], memberships=d['memberships'],
               census_profile=[x['L_N'] for x in d['census']['levels']], relative_class=d['census']['classes']['relative']['class'],
               union_N9=d['union_N9']['verdict'],
               ties=dict(verdict=ties.get('verdict'), forced_pair_count=ties.get('forced_pair_count'),
                         class_levels=[sorted({lvl(v) for v in c}) for c in ties.get('classes', [])],
                         spanning=[[x['k0'], x['s'], x['spanning']] for x in ties.get('summaries', [])]),
               threshold_reach={str(t['k0']): [[lv['s'], lv['L_N']] for lv in t['levels']] for t in d['threshold_reach']},
               homomorphisms=[m['name'] for m in d['homomorphisms']['accepted_maps']],
               life=[[x['N'], x['verdict']] for x in d['life']],
               U_followups=[[(f['levels'][0] if 'levels' in f else f).get('s'), (f['levels'][0] if 'levels' in f else f).get('L_N')]
                            for f in d.get('U_followups', [])],
               seconds=d['seconds'], incomplete_certifications=len(d['incomplete_certifications']))
    slim.append(rec)
    hashes[d['case']] = [[h, r['proof_sha256'], r['purpose'], r['checker']] for h, r in sorted(d['refutations'].items())]
for f in sorted(glob.glob(str(HERE / 'pilot_U_results/*.json'))):
    d = json.load(open(f))
    slim.append(dict(case=d['case'], pop='U-pilot', key=d['key'], census_profile=d['census_levels'], union_N9=d['union_N9'],
                     tie_forced_pairs=d['tie_forced_pairs'], U_followups=[[x['s'], x['L_N']] for x in d['followups']],
                     seconds=d['seconds'], incomplete_certifications=len(d['incomplete'])))
    hashes['pilot:' + d['case']] = [[h, r['proof_sha256'], r['purpose'], r['checker']] for h, r in sorted(d['refutations'].items())]
with gzip.open(OUT / 'records_slim.jsonl.gz', 'wt') as g:
    for rec in slim:
        g.write(json.dumps(rec, sort_keys=True) + '\n')
with gzip.open(OUT / 'certificate_hashes.json.gz', 'wt') as g:
    json.dump(hashes, g)
summary = dict(records=len(slim), by_pop={p: sum(1 for r in slim if r['pop'] == p) for p in ('D', 'U', 'U-pilot')},
               refutations_cited=sum(len(v) for v in hashes.values()),
               distinct_refutations=len({h for v in hashes.values() for h, *_ in v}))
json.dump(summary, open(OUT / 'summary.json', 'w'), indent=1)
print(summary)
