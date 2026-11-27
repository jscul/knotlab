"""Aggregate the bounded searches and check the opportunity counts."""

from pathlib import Path
import json


HERE=Path(__file__).resolve().parent
result={}
paths=sorted(HERE.glob('arity_*.jsonl'))
for path in paths:
    all_records=[json.loads(line) for line in path.read_text().splitlines() if line]
    records=[r for r in all_records if 'boxes' in r]
    if not records: continue
    counts={
        'patterns':len(records),
        'with_an_eligible_single_clause':sum(r['single_clause_triples']>0 for r in records),
        'eligible_disjoint_triples':sum(r['eligible_triples'] for r in records),
        'eligible_single_clauses':sum(r['single_clause_triples'] for r in records),
        'boxes':sum(r['boxes'] for r in records),
        'sum_pattern_seconds':round(sum(r['seconds'] for r in records),2),
    }
    if 'contractions' in all_records[-1]:
        counts['coverage']=all_records[-1]
        assert counts['patterns']==counts['coverage']['distinct']
    result[path.name]=counts
print(json.dumps(result,indent=2))
