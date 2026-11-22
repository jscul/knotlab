"""Compare independent physical histories, canonical small holders and the two sharp bounds."""
from collections import Counter
from fractions import Fraction
import gzip
from itertools import product
import json
import os
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OUT=HERE/'crosscheck.json'


def canonical(law,width):
    names=tuple('abcdefgh'[:width])
    rows=list(product((0,1),repeat=width))
    valid=lambda r: len(set(r))>1 if law=='nae' else sum(r)%2==0
    clauses=[' '.join(('~' if bit else '')+n for n,bit in zip(names,r)) for r in rows if not valid(r)]
    command=[sys.executable,'-B','-m','knotlab','check','--cnf',';'.join(clauses),
             '--loops',*names[:-1],'--contact',names[-1],'--json']
    env={**os.environ,'PYTHONPATH':str(ROOT/'tools')}
    row=json.loads(subprocess.check_output(command,cwd=ROOT,env=env))
    assert row['is_knot'] and row['invisible_in_parts'] and len(row['allowed'])==sum(map(valid,rows))
    return {k:row[k] for k in ('binding','invisible_in_parts','coexistence','is_knot','minimum_width')}


def comparable(native_name,law):
    mode,_,fault=native_name.partition('__')
    special={'single_H_zero':'single_H0','single_H_one':'single_H1','symmetric_one':'some_motion',
             'symmetric_all':'all_motion'}
    n=special.get(mode,mode)
    if n in ('asymmetric_nae_decoder','symmetric_nae_decoder'):
        return None if fault else (n.partition('_')[0]+'/literal_NAE',False)
    if n in ('asymmetric_xor','symmetric_xor'):
        return None if fault else (n.partition('_')[0]+'/calibrated_XOR',False)
    fixed={'off_F1_F2_F3':'all_F_off','off_capture':'comparison_off','off_write':'H_write_off',
           'off_delivery':'delivery_off','off_F1':'F1_off','off_F2':'F2_off','off_F3':'F3_off'}
    inverse=(law=='parity' and n in ('asymmetric','symmetric','restricted','some_motion','all_motion'))
    if not fault:return n,inverse
    if fault=='off_all':return 'none',False
    if fault.startswith('omit_'):return f"{n}/missing{fault.split('_')[1]}",inverse
    return (n+'/'+fixed[fault],inverse) if fault in fixed else None


def independent_limits(law,start):
    """Observe only the nine x values, or the nine x plus their own three paid bits."""
    projections={k:{} for k in ['nine','nine_and_three_paid']}
    for word in start:
        u=word&1
        x=(word>>7)&511
        for k,j in (('nine',x),('nine_and_three_paid',(x,(word>>1)&7))):
            projections[k].setdefault(j,Counter())[u]+=1
    result={k:[sum(count[c] for count in groups.values() if len(count)==1) for c in (0,1)]
            for k,groups in projections.items()}
    assert result==({'nine':[7,7],'nine_and_three_paid':[2401,2401]} if law=='nae'
                    else {'nine':[1024,1024],'nine_and_three_paid':[1024,1024]})
    return result


def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument('--verify',action='store_true')
    args=ap.parse_args()
    native=json.load(gzip.open(HERE/'native.json.gz'))
    physical=json.load(gzip.open(HERE/'signal_records.json.gz'))
    result={}
    for law,old in native['laws'].items():
        ranked=physical['sources'][law]['cases']
        checked={}
        for name,entry in old['controls'].items():
            key=comparable(name,law)
            if not key or key[0] not in ranked:continue
            other,opposite=key
            observed={}
            for c,port,movers,exchanges,n in entry['by_true_u0_result_number_of_moving_siblings_and_elementary_moves']:
                new=str(1-int(port)) if opposite and port!='ready' else port
                observed[f'{c}/{new}/{movers}/{exchanges}']=n
            target=ranked[other]['by_orientation_port_number_of_original_siblings_moving_forward_nonidentity_swaps']
            assert observed==target,(law,name,other)
            checked[name]={'second_census':other,'reverse_nonready_markings':opposite,
                           'compared_nonempty_cells':len(observed)}
        total=len(old['old_complete_words_lsb_name_zero'])
        for name in ('symmetric','some_motion','all_motion','passive','restricted','asymmetric'):
            for c in (0,1):
                port=str(c); x=ranked[name]['retained_tables'][port]
                mass=x['ordinary_launch_mass']
                assert physical['tables'][x['no_focal_tag']]['equals_orientation_pure'][port]
                if law=='nae':
                    for read,expected in [('no_focal_tag','1/14'),('copied_focal_bit','-5/14'),('returned_focal_bit','1/14')]:
                        table=physical['tables'][x[read]]
                        assert table['excess_against_each_c'][c]==expected
                        assert all(sum(map(Fraction,row))==1 for row in table['eight_settings_eight_outcomes'])
                    for tags,branch in physical['sources'][law]['characters_after_writing'][name].items():
                        for h,cells in branch.items():
                            assert Fraction(cells[port]['mass_per_initial_launch'])==Fraction(mass,16*total)
        result[law]={'crossed_censuses':checked,'old_uniform_launches':total,
                     'sharp_unambiguous_complete_projection_counts':independent_limits(law,old['old_complete_words_lsb_name_zero']),
                     'canonical_CLI':{str(w):canonical(law,w) for w in (4,7)},
                     'offers_per_regular_launch':{m:sum(len(block) for stage in old['controls'][m]['ordered_offer_groups'].values()
                                                        for block in stage)
                                                  for m in ('asymmetric','symmetric','symmetric_one','symmetric_all','passive','restricted')}}
    output=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.verify:assert output==OUT.read_text()
    else:OUT.write_text(output)
    print({law:len(r['crossed_censuses']) for law,r in result.items()})


if __name__=='__main__':main()
