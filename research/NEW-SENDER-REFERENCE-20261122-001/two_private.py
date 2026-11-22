"""Enumerate the one-founder experiment with exact conditional growth weights."""
from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
from itertools import product
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ENGINE = 'ORDINARY-DYNAMICS-20261120-001A'
sys.path.insert(0, str(ROOT/'experiments'/ENGINE/(ENGINE+'-E001_ordinary')))
import end_operator as ordinary


def allowed(law, bits):
    if law == 'parity':
        return sum(bits) % 2 == 0
    return 0 < sum(bits) < len(bits)


def fund(holdings, law):
    turn = ordinary.step(ordinary.from_stars(holdings), law, max_births=32)
    assert turn.status == 'extend'
    owners = defaultdict(list)
    for holder, row in enumerate(holdings):
        for mark in row:
            owners[mark].append(holder)
    loose = defaultdict(list)
    for mark, holders in sorted(owners.items()):
        if len(holders) == 1:
            loose[holders[0]].append(mark)
    available = {holder: iter(marks) for holder, marks in loose.items()}
    next_mark = max(owners) + 1
    rows = []
    for j, (parents, size) in enumerate(zip(turn.parents, turn.fresh, strict=True), len(holdings)):
        paid = tuple(next(available[p]) for p in parents)
        fresh = tuple(range(next_mark, next_mark+size))
        next_mark += size
        rows.append(dict(holder=j,parents=parents,paid=paid,fresh=fresh))
    assert not any(list(left) for left in available.values())
    grown = holdings + [r['paid']+r['fresh'] for r in rows]
    return rows, grown


@cache
def extensions(law, incoming, size):
    return tuple(v for v in product((0,1),repeat=size) if allowed(law,incoming+v))


def grow_words(law, before, rows):
    words = [(before,Fraction(1))]
    for row in rows:
        expanded = []
        for original, weight in words:
            bank = extensions(law,tuple(original[n] for n in row['paid']),len(row['fresh']))
            assert bank
            if row['fresh']:
                assert min(row['fresh']) == len(original)
            expanded.extend((original+v,weight/len(bank)) for v in bank)
        words = expanded
    return words


def fields(word, names):
    return ''.join(str(word[n]) for n in names)


def check_relation(law, width):
    names = [f'd{i}' for i in range(width)]
    illegal = [v for v in product((0,1),repeat=width) if not allowed(law,v)]
    cnf = ';'.join(' '.join(('~' if bit else '')+name for bit,name in zip(v,names,strict=True)) for v in illegal)
    cmd=[sys.executable,'-B','-m','knotlab','check','--loops',*names[:-1],'--contact',names[-1],'--cnf',cnf,'--json']
    raw=subprocess.check_output(cmd,env={**os.environ,'PYTHONPATH':str(ROOT/'tools')},text=True)
    data=json.loads(raw)
    assert data['is_knot']
    return {k: data[k] for k in ('is_knot','binding','loss_on_erasure','coexistence','allowed')}


def exact_dict(table):
    return {str(k):str(v) for k,v in sorted(table.items())}


def run(law):
    holdings = [(0,1,2)]
    cuts = []
    for _ in range(3):
        step, holdings = fund(holdings,law)
        cuts.append(step)
    first,second,finish = cuts
    k = first[0]
    targets = [row for row in second if k['holder'] in row['parents']]
    assert len(k['fresh']) == len(targets) == 2
    target = targets[0]
    q = target['paid'][target['parents'].index(k['holder'])]
    spare, = set(k['fresh'])-{q}
    h, = set(target['paid'])-{q}
    y, = target['fresh']
    assert [c for c in finish if y in c['paid']]
    assert h not in holdings[k['holder']] and y not in holdings[k['holder']]
    assert all(len([c for c in second if d in c['paid']])==1 for d in k['fresh'])
    start_words=extensions(law,(),3)
    prefix_count=Counter()
    full_count=Counter()
    per_ask = {name:Counter() for name in ('hold','exchange')}
    seen = {name:{read:Counter() for read in ('fresh_only','fresh_plus_h')} for name in per_ask}
    mixed_seen = {name:Counter() for name in per_ask}
    joint_prefix=Counter()
    own_finish=Counter()
    incidence_support = [set() for _ in holdings]
    contrasts = []
    for start in start_words:
        for pre,wp in grow_words(law,start,first):
            mass=wp/len(start_words)
            addr=k['paid'][0]
            diff=pre[q]!=pre[spare]
            typ='unequal' if diff else 'equal'
            prefix_count[typ]+=1
            joint_prefix[(pre[addr],typ)]+=mass
            finals_by_action={}
            for ask in per_ask:
                active = ask=='exchange' and diff
                action='exchanged' if active else ('refused_equal' if ask=='exchange' else 'held')
                v=list(pre)
                if active: v[q],v[spare]=v[spare],v[q]
                v=tuple(v)
                assert all(allowed(law,tuple(v[n] for n in row)) for row in holdings[:4])
                per_ask[ask][action]+=mass
                per_ask[ask]['paid_value_changed']+=mass*(v[q]!=pre[q])
                odists=Counter()
                outcomes={}
                for middle,wm in grow_words(law,v,second):
                    for last,wz in grow_words(law,middle,finish):
                        weight=mass*wm*wz
                        assert all(allowed(law,tuple(last[n] for n in row)) for row in holdings)
                        for j,row in enumerate(holdings):
                            incidence_support[j].add(tuple(last[n] for n in row))
                        full_count[ask]+=1
                        own_finish[ask]+=weight
                        rec=str(last[y])
                        seen[ask]['fresh_only'][rec]+=weight
                        seen[ask]['fresh_plus_h'][rec+str(last[h])]+=weight
                        if diff: mixed_seen[ask][rec]+=weight
                        odists[last[y]]+=wm*wz
                        outcomes.setdefault(last[y],{'after_sender':fields(v,range(len(v))),'after_payment':fields(middle,range(len(middle))),'after_finish':fields(last,range(len(last))),'origin_paid':v[q],'hidden_payment_h':last[h],'local_fresh_value':last[y],'local_finish':'sole own fresh mark acquired its first other holder'})
                assert sum(odists.values())==1
                finals_by_action[ask]=outcomes
            if diff and pre[q]==0 and len(contrasts)<1:
                shared=set(finals_by_action['hold']) & set(finals_by_action['exchange'])
                changed=next(((a,b) for a,b in product(sorted(finals_by_action['hold']),sorted(finals_by_action['exchange'])) if a!=b),None)
                assert changed
                contrasts.append({'complete_first_word':fields(start,range(len(start))),
                    'common_pre_action':fields(pre,range(len(pre))),'sender_pre':fields(pre,holdings[k['holder']]),
                    'changed_fresh_example':{ask:finals_by_action[ask][bit] for ask,bit in zip(('hold','exchange'),changed,strict=True)},
                    'common_fresh_answers_for_this_prefix':sorted(shared),
                    'same_allocation_opposite_role_pre':finals_by_action['exchange'][changed[1]]['after_sender']})
    assert all(sum(seen[ask]['fresh_only'].values())==own_finish[ask]==1 for ask in per_ask)
    assert seen['hold']==seen['exchange'] and mixed_seen['hold']==mixed_seen['exchange']
    # Identify the finite realized local relations before any preparation is conditioned upon.
    relations={}
    for row,have in zip(holdings,incidence_support,strict=True):
        full=set(extensions(law,(),len(row)))
        assert have==full,(row,len(have),len(full))
        if len(row) not in relations: relations[len(row)]=check_relation(law,len(row))
    return {'law':law,'named_audit_only':dict(sender=k['holder'],receiver=target['holder'],sender_private=k['fresh'],paid=q,other=spare,companion_paid=h,own_fresh=y),
        'cuts':cuts,'local_laws':relations,'founder_words':len(start_words),'prefix_counts':dict(prefix_count),
        'total_complete_histories_per_request':dict(full_count),'sender_event_mass_given_request':{k:exact_dict(v) for k,v in per_ask.items()},
        'prefix_mass_by_inherited_bit_and_read':{f'{i}|{j}':str(v) for (i,j),v in sorted(joint_prefix.items())},
        'new_receiver_record_given_request':{k:{m:exact_dict(v) for m,v in rows.items()} for k,rows in seen.items()},
        'fresh_only_joint_mass_with_unequal_sender':{k:exact_dict(d) for k,d in mixed_seen.items()},'finish_mass':exact_dict(own_finish),
        'equal_request_prior_accuracy':'1/2','equal_prior_accuracy_given_unequal':'1/2','traces':contrasts,
        'weighting':'Uniform lawful founding word. Uniform lawful fresh completion per birth conditional on actual paid inputs, with shared causes counted once. Requests independently equal. On equal bits exchange refuses locally; refinement as blind literal exchange gives a legal no-op.'}


if __name__=='__main__':
    report={law:run(law) for law in ('parity','nae')}
    (HERE/'two_private.json').write_text(json.dumps(report,indent=2)+'\n')
    for law,result in report.items():
        print(law,result['prefix_counts'],result['sender_event_mass_given_request']['exchange'],result['new_receiver_record_given_request']['hold']['fresh_only'])
