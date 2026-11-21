"""Literal physical growth checks, one-loose-name permanence and all outcome counts."""
from collections import Counter
from fractions import Fraction as F
import gzip
import json
import os
import subprocess
import sys

from words import OUT,ROOT,save
from ordinary import experiment,rows_for,singleton,three_count_rows
from completions import literal
import numpy as np


def run():
    results=json.loads(gzip.decompress((OUT/'histories.json.gz').read_bytes()))
    cases={(c['id'],c['law']):c for c in results['cases']};tables=results['tables']
    for t in tables.values():
        g=np.array(t['gram'],dtype=object).reshape(8,8)
        assert t['rows']==three_count_rows(g)==rows_for(g,singleton(3))
    used=set();letters=0;permanent=[];covered=0
    for vote in results['votes']:
        if vote.get('ineligible'):continue
        c=cases[vote['case'],vote['law']];m=vote['marks'];age0=vote['anchor_age'];reference=None;anchor=None
        for age,(row,frm) in enumerate(zip(vote['records'],c['stages'][age0:]),age0):
            new={b for b,k in Counter(b for h in frm for b in h).items() if k==1}
            if reference is None and len(new)==1 and not new.intersection(m) and 'table' in row:
                reference=row['table'];anchor=dict(case=c['id'],law=c['law'],trial=vote['trial'],role=vote['role'],marks=m,age=age,
                                                   interface=next(iter(new)),constant_table=reference,checked_later_ages=[])
                permanent.append(anchor)
            if reference is not None and 'table' in row and age>anchor['age']:
                assert row['table']==reference
                anchor['checked_later_ages'].append(age);covered+=1
            key=(tuple(map(tuple,frm)),tuple(m),c['law'])
            if key in used or max(map(max,frm))>=12 or 'table' not in row:continue
            used.add(key);f=literal(frm,m,c['law']);g=f.T @ f;want=tables[row['table']]['gram']
            assert all(x==y*row['physical_unit'] for x,y in zip(map(int,g.flat),want));letters+=64
    nonneg=json.loads((OUT/'single_questions.json').read_text());combined=json.loads((OUT/'combined_checks.json').read_text())
    gates=[]
    for law in ('parity','nae'):
        for arity in (3,4):
            names=[f'd{i}' for i in range(arity)];bad=(0,(1<<arity)-1) if law=='nae' else [x for x in range(1<<arity) if x.bit_count()%2]
            cnf=';'.join(' '.join(('~' if x>>i&1 else '')+name for i,name in enumerate(names)) for x in bad)
            cmd=[sys.executable,'-B','-m','knotlab','check','--cnf',cnf,'--loops',*names[:-1],'--contact',names[-1],'--json']
            gate=json.loads(subprocess.check_output(cmd,cwd=ROOT,env={**os.environ,'PYTHONPATH':str(ROOT/'tools')}));assert gate['is_knot']
            gates.append(dict(law=law,arity=arity,canonical={k:gate[k] for k in ('binding','loss_on_erasure','coexistence','is_knot')}))
    save('validation.json',dict(canonical=gates,history_tables=len(tables),history_words_literal_cases=len(used),literal_cells=letters,
         single_name_separator_cases=permanent,checked_later_tables=covered,
         disjoint_totals={k:sum(s['counts'][k] for s in nonneg['exhaustive']) for k in nonneg['exhaustive'][0]['counts']},
         combined_totals={k:sum(s['checks'][k] for s in combined) for k in combined[0]['checks']}))
