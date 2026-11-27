"""Check every contact role of the constructed lower and upper relations."""

import argparse
from contextlib import redirect_stdout
from io import StringIO
from itertools import product
import json
from pathlib import Path
import sys


HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[2]/'tools'))
from knotlab.cli import main as knot_check


def exclude(names, word):
    return ' '.join(('~' if bit else '')+name for name,bit in zip(names,word,strict=True))


def from_image(names, allowed):
    return [exclude(names,w) for w in product((0,1),repeat=len(names)) if w not in allowed]


def roles(names,cnf,hidden=()):
    checks=[]
    for contact in names:
        out=StringIO()
        with redirect_stdout(out):
            rc=knot_check(['check','--loops',*(n for n in names if n!=contact),
                           '--contact',contact,'--cnf','; '.join(cnf),'--witnesses',*hidden,'--json'])
        data=json.loads(out.getvalue())
        assert rc==0 and data['is_knot']
        checks.append({k:data[k] for k in ('variables','allowed','is_knot')})
    return checks


def examine(words,bonds,upper,equals):
    size=len(next(iter(words)))
    lower_names=['x'+str(i) for i in range(size)]
    upper_names=['P','Q','R']
    cnf=[]
    first=[]
    for bond in bonds:
        subnames=[lower_names[i] for i in bond]
        allowed={tuple(w[i] for i in bond) for w in words}
        clauses=from_image(subnames,allowed)
        first.append(roles(subnames,clauses))
        cnf+=clauses
    definitions=[]
    for group,v in zip(upper,upper_names,strict=True):
        names=[lower_names[i] for i in group]+[v]
        for w in product((0,1),repeat=len(names)):
            agree=len(set(w[:-1]))==1
            if bool(w[-1])!=(agree if equals else not agree):
                definitions.append(exclude(names,w))
    return {'lower':first,'upper_from_exact_lower_image':roles(upper_names,from_image(lower_names,words)+definitions,lower_names),
            'upper_from_lower_bonds':roles(upper_names,cnf+definitions,lower_names)}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--pilot',action='store_true')
    args=p.parse_args()
    raw={}
    for width in (3,4):
        names=[f'x{i}' for i in range(width)]
        states=list(product((0,1),repeat=width))
        for kind in ('not_all_equal','even_parity'):
            allowed={w for w in states if len(set(w))>1} if kind=='not_all_equal' else {w for w in states if sum(w)%2==0}
            raw[f'{kind}_{width}']=roles(names,from_image(names,allowed))
            if args.pilot: return raw
    out={'source_laws':raw}
    cross=list(product((0,1),(2,3),(4,5)))
    for tag in ('widen','uniform','cap'):
        data=json.loads((HERE/f'arity_positive_{tag}.json').read_text())
        if tag=='widen': data=data['first']
        for i,item in enumerate(data if isinstance(data,list) else [data]):
            words={tuple(map(int,w)) for w in item['source_states_by_lower_word']}
            out[f'{tag}_{i}']=examine(words,cross,[(0,1),(2,3),(4,5)],False)
    for tag in ('parity_witness','uniform_parity_witness'):
        parity=json.loads((HERE/f'arity_{tag}.json').read_text())['replay']
        bonds=parity['exact_lower_presentation']
        words={w for w in product((0,1),repeat=9) if all(sum(w[i] for i in b)%2 for b in bonds)}
        assert len(words)==parity['lower_word_count']
        out[tag]=examine(words,bonds,parity['upper_carriers'],True)
    return out


if __name__=='__main__':
    print(json.dumps(main(),indent=2))
