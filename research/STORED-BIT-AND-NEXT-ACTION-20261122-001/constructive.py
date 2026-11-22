"""Construct full paired words by filling ordinary births in parent order.

The only use of an archived value assignment is a common older starting prefix
through size six. The local support enumeration does not sample or solve SAT.
"""
from collections import Counter, defaultdict
from itertools import product
import gzip
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREVIOUS = 'SPARE-AND-NEXT-PAYMENT-20261122-001'
DATA = ROOT/'artifacts'/(PREVIOUS+'A')/(PREVIOUS+'A-E001_payment_trace')
ORDINARY = ROOT/'experiments'/'ORDINARY-DYNAMICS-20261120-001A'/'ORDINARY-DYNAMICS-20261120-001A-E001_ordinary'
sys.path.insert(0, str(ORDINARY))
from end_operator import from_stars, step

X = 231
OTHER = 232
R = 111
FRESH = (263,264)


def all_words(n):
    return [''.join(bits) for bits in product('01',repeat=n)]


def allowed(law, word):
    if law == 'parity':
        return word.count('1') % 2 == 0
    return '0' in word and '1' in word


def extend(law, prefix, births, pinned):
    result = list(prefix)
    for row in births:
        inherited = ''.join(result[k] for k in row['paid'])
        fresh = row['fresh']
        assert fresh == list(range(len(result),len(result)+len(fresh)))
        for word in all_words(len(fresh)):
            if allowed(law,inherited+word) and all(word[i] == pinned.get(k,word[i]) for i,k in enumerate(fresh)):
                result.extend(word)
                break
        else:
            return None
    return ''.join(result)


def paid_plan(past, law):
    payers = defaultdict(list)
    for k,support in enumerate(past):
        for d in support:
            payers[d].append(k)
    queues = defaultdict(list)
    for d,ks in sorted(payers.items()):
        if len(ks)==1:
            queues[ks[0]].append(d)
    plan = step(from_stars(past),law)
    assert plan.status=='extend'
    top = max(payers)+1
    result = []
    for idx,(parents,n) in enumerate(zip(plan.parents,plan.fresh,strict=True),start=len(past)):
        result.append({'knot':idx,'parents':list(parents),'paid':[queues[k].pop(0) for k in parents],
                       'fresh':list(range(top,top+n))})
        top += n
    assert not any(queues.values())
    return result


def run(law, previous, old_values):
    source = previous['source']
    cohorts = {int(k):rows for k,rows in previous['cohorts'].items()}
    through_6 = source + [r['paid']+r['fresh'] for n in range(2,7) for r in cohorts[n]]
    size_6 = old_values[:1+max(k for row in through_6 for k in row)]
    assert all(allowed(law,''.join(size_6[d] for d in row)) for row in through_6)
    through_8 = through_6 + [r['paid']+r['fresh'] for n in (7,8) for r in cohorts[n]]
    through_9 = through_8 + [r['paid']+r['fresh'] for r in cohorts[9]]
    tenth = paid_plan(through_9,law)
    slots = {k:next(row for row in tenth if k in row['paid']) for k in FRESH}
    assert len({row['knot'] for row in slots.values()})==2
    literal,control,examples = [],[],{}
    kinds = ('literal','compensated') if law=='parity' else ('literal',)
    for kind in kinds:
        fixed_H = (183,189,232,233) if kind=='literal' else (183,189,233)
        for bg in all_words(len(fixed_H)):
            a7 = extend(law,size_6,cohorts[7],dict(zip(fixed_H[:2],bg[:2])))
            assert a7 is not None
            for cd in all_words(2):
                prefix = {}
                for x in '01':
                    pins = dict(zip(fixed_H,bg,strict=True))
                    pins.update({X:x,214:cd[0],217:cd[1]})
                    if kind=='compensated':
                        pins[OTHER] = str((bg.count('1')+int(x))%2)
                    old = extend(law,a7,cohorts[8],pins)
                    if old is not None:
                        assert all(allowed(law,''.join(old[d] for d in row)) for row in through_8)
                        prefix[x]=old
                diff=[]
                if len(prefix)==2:
                    diff=[i for i,(l,r) in enumerate(zip(prefix['0'],prefix['1'],strict=True)) if l!=r]
                    assert diff == ([X] if kind=='literal' else [X,OTHER])
                found = {}
                companion = {}
                for x,old in prefix.items():
                    supported, future = [],{}
                    for f in all_words(2):
                        grown = extend(law,old,cohorts[9],dict(zip(FRESH,f,strict=True)))
                        if grown is None:
                            continue
                        assert grown[X] == old[X] and grown[OTHER] == old[OTHER]
                        final = extend(law,grown,tenth,{})
                        assert final is not None and final.startswith(grown)
                        assert all(allowed(law,''.join(final[d] for d in row['paid']+row['fresh'])) for row in tenth)
                        supported.append(f)
                        future[f] = final
                    assert supported == [f for f in all_words(2) if allowed(law,cd+x+f)]
                    found[x]=supported
                    if kind=='compensated':
                        other_row = through_9[118]
                        assert other_row[:2] == [226,232]
                        companion[x] = [f for f in all_words(3) if allowed(law,old[226]+old[232]+f)]
                    if cd=='00' and ((law=='nae' and bg=='0001') or (kind=='compensated' and bg=='000')):
                        examples[kind+'_'+x] = {'H_background':bg,'R_other_paid':cd,'size_eight_prefix':old,
                            'full_size_ten_word_by_R_fresh_pair':future}
                if companion:
                    assert len(companion['0'])==len(companion['1'])==4 and not set(companion['0']) & set(companion['1'])
                cell={'H_background':bg,'companions':cd,'old_arms':sorted(prefix),'complete_old_word_differences':diff,
                      'fresh_words_through_next_funding':found}
                if companion:
                    cell['compensating_recipient_fresh_words'] = companion
                (literal if kind=='literal' else control).append(cell)
    return {'literal':literal,'compensated':control,'examples':examples,'outgoing_R_slots':slots,
            'size_nine_births':len(cohorts[9]),'size_ten_births':len(tenth),'size_ten_total_fresh':sum(len(b['fresh']) for b in tenth)}


def main():
    archived=json.loads(gzip.decompress((DATA/'physical_trace.json.gz').read_bytes()))
    values=json.loads((ROOT/'research'/PREVIOUS/'same_prefix.json').read_text())
    result={}
    for law in ('parity','nae'):
        source=values[law]['extra']['common_prefix_by_H_fresh_word']['000']
        result[law]=run(law,archived[law]['loaded'],source)
        print(law,Counter(''.join(c['old_arms']) for c in result[law]['literal']),len(result[law]['compensated']),
              {k:r['knot'] for k,r in result[law]['outgoing_R_slots'].items()})
    (HERE/'constructive.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':
    main()
