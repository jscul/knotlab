"""Audit complete paired worlds and check existence with one shared-variable SAT query."""
from collections import Counter
from fractions import Fraction
from itertools import product
import gzip
import json
import sys
from pysat.solvers import Minisat22
from constructive import DATA, HERE, PREVIOUS, ROOT, allowed, paid_plan

sys.path.insert(0,str(ROOT/'research'/PREVIOUS))
from by_deletion import canonical


def clauses(law, rows):
    for row in rows:
        if law == 'nae':
            yield [d+1 for d in row]
            yield [-d-1 for d in row]
        else:
            for vals in product((0,1), repeat=len(row)):
                if sum(vals)%2:
                    yield [(-1 if bit else 1)*(d+1) for d,bit in zip(row,vals,strict=True)]


def solver_for_pair(law, rows, changes):
    original = list(clauses(law, rows))
    # A single assignment describes both arms. In the comparison image only
    # the enrolled old literals change sign, with all other variables shared.
    affected = [row for row in rows if set(row) & changes]
    counterfactual = [[-lit if abs(lit)-1 in changes else lit for lit in clause]
                      for clause in clauses(law, affected)]
    return Minisat22(bootstrap_with=original+counterfactual)


def gather(word, marks):
    return ''.join(word[d] for d in marks)


def valid(law, word, rows):
    return all(allowed(law, gather(word,row)) for row in rows)


def main():
    leaf=HERE.name+'A'
    output=ROOT/'artifacts'/leaf/(leaf+'-E001_single_mark')
    main_result=json.loads((output/'results.json').read_text())['laws']
    worlds=json.loads(gzip.decompress((output/'worlds.json.gz').read_bytes()))['laws']
    independent=json.loads((HERE/'constructive.json').read_text())
    old_trace=json.loads(gzip.decompress((DATA/'physical_trace.json.gz').read_bytes()))
    verified={}
    for law in ('parity','nae'):
        trace=old_trace[law]['loaded']
        cohorts=trace['cohorts']
        physical=main_result[law]['physical']
        older=trace['source']+[r['paid']+r['fresh'] for i in range(2,9) for r in cohorts[str(i)]]
        ninth=[r['paid']+r['fresh'] for r in cohorts['9']]
        plan=paid_plan(older+ninth,law)
        assert len(plan)==len(physical['full_size_ten_roster'])==24
        for left,right in zip(plan,physical['full_size_ten_roster'],strict=True):
            assert all(left[k]==right[k] for k in left)
        tenth={key:[] for key in ('archived','swapped_R_private_marks')}
        for r in plan:
            tenth['archived'].append(r['paid']+r['fresh'])
            exchange={263:264,264:263}
            swapped=[exchange.get(d,d) for d in r['paid']]
            tenth['swapped_R_private_marks'].append(swapped+r['fresh'])
        totals=Counter()
        for key, comparison in main_result[law]['comparisons'].items():
            is_compensated=key=='compensated_parity'
            fixed=(183,189,233) if is_compensated else (183,189,232,233)
            change={231,232} if is_compensated else {231}
            checks=independent[law]['compensated' if is_compensated else 'literal']
            assert len(checks)==comparison['strata_tested']
            with solver_for_pair(law,older,change) as both, Minisat22(bootstrap_with=clauses(law,older)) as one:
                for row in checks:
                    bg,cd=row['H_background'],row['companions']
                    name=bg+'|'+cd
                    main_cell=comparison['strata'][name]
                    arms=worlds[law][key][name]
                    pins=[(d+1)*(2*int(v)-1) for d,v in zip((*fixed,214,217),bg+cd,strict=True)]
                    possible=sorted(str(x) for x in (0,1) if one.solve(assumptions=pins+[(2*x-1)*(231+1)]))
                    assert possible==row['old_arms']==sorted(arms['arms'])==sorted(main_cell['available_arms'])
                    paired=both.solve(assumptions=pins+[-(231+1)])
                    assert paired == (len(possible)==2)
                    totals['full_old_pair_SAT_queries']+=1
                    if paired:
                        p,q=[arm['word_through_size_eight'] for _,arm in sorted(arms['arms'].items())]
                        assert {d for d,(i,j) in enumerate(zip(p,q,strict=True)) if i!=j}==change
                        totals['matched_prefix_pairs']+=1
                    for x in possible:
                        runs=arms['arms'][x]
                        word=runs['word_through_size_eight']
                        assert word.startswith(arms['common_word_through_size_seven'])
                        assert gather(word,fixed)==bg and gather(word,(214,217,231))==cd+x
                        assert len(word)==259 and valid(law,word,older)
                        report=main_cell['available_arms'][x]
                        cases=runs['supported_R_fresh_words']
                        assert sorted(cases)==row['fresh_words_through_next_funding'][x]==report['full_support']
                        assert Fraction(report['uniform_probability_per_fresh_word'])==Fraction(1,len(cases))
                        marginal = [Fraction(sum(w[i]=='1' for w in cases),len(cases)) for i in (0,1)]
                        assert marginal == list(map(Fraction,report['probability_of_one_at_263_and_264']))
                        for fresh,records in cases.items():
                            nine=records['word_through_size_nine']
                            assert nine.startswith(word) and gather(nine,(263,264))==fresh and valid(law,nine,ninth)
                            totals['supported_receiver_branches']+=1
                            assert set(records['words_through_size_ten_by_allocation'])==set(tenth)
                            for alloc,full in records['words_through_size_ten_by_allocation'].items():
                                assert full.startswith(nine) and valid(law,full,tenth[alloc])
                                totals['complete_allocation_continuations']+=1
                        collateral=runs['collateral_fresh_witnesses_if_compensated']
                        if is_compensated:
                            assert sorted(collateral)==row['compensating_recipient_fresh_words'][x]
                        for fresh,record in collateral.items():
                            nine=record['word_through_size_nine']; full=record['word_through_size_ten']
                            assert nine.startswith(word) and gather(nine,(279,280,281))==fresh and valid(law,nine,ninth)
                            assert full.startswith(nine) and valid(law,full,tenth['archived'])
                            totals['collateral_continuations']+=1
        examples=independent[law]['examples']
        if law=='nae':
            s0=examples['literal_0']['full_size_ten_word_by_R_fresh_pair']['01']
            s1=examples['literal_1']['full_size_ten_word_by_R_fresh_pair']['01']
            assert len(s0)==len(s1) and {i for i,(p,q) in enumerate(zip(s0,s1)) if p!=q}=={231}
        else:
            s0=examples['compensated_0']['full_size_ten_word_by_R_fresh_pair']['00']
            s1=examples['compensated_1']['full_size_ten_word_by_R_fresh_pair']['01']
            assert s0[263]==s1[263]=='0' and s0[264]=='0' and s1[264]=='1'
        for w in (s0,s1):
            assert valid(law,w,older+ninth+tenth['archived'])
        arities=sorted({len(r) for r in older+ninth+tenth['archived']})
        verified[law]={'scope_counts':dict(totals),'local_relations':[canonical(law,n) for n in arities]}
    assert sum(v['scope_counts']['matched_prefix_pairs'] for v in verified.values())==88
    (HERE/'verification.json').write_text(json.dumps(verified,indent=2)+'\n')
    print({law:v['scope_counts'] for law,v in verified.items()})


if __name__=='__main__':
    main()
