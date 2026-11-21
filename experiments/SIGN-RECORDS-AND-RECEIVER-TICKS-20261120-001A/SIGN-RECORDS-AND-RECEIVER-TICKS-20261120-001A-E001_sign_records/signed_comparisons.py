"""A separate mathematical comparison on exact integer amplitudes and rational two-word effects."""
from collections import Counter
from fractions import Fraction as F
from itertools import product
from physical_histories import ARMS, act, codeword, encode, legal, path, save


def transported(amplitudes,program):
    current=dict(amplitudes)
    for gate in program:
        new={}
        for w,v in current.items():
            target,_=act(w,gate)
            assert target not in new
            new[target]=v
        current=new
    return current


def norm(v):
    return sum(a*a for a in v.values())


def ordinary(v):
    return [[w,str(F(a*a,norm(v)))] for w,a in sorted(v.items()) if a]


def read_r(v):
    return F(sum(a*a for w,a in v.items() if codeword(w)[3]),norm(v))


def expectation(v,mask):
    return F(sum(a*v.get(w^mask,0) for w,a in v.items()),norm(v))


def transfer():
    rows=[]
    for data,reference in product((1,-1),repeat=2):
        preparation={encode(d,m):data**d * reference**m for d,m in product((0,1),repeat=2)}
        after=transported(preparation,'C'); reader=transported(after,'P')
        expected={encode(d,m):(data*reference)**d * reference**m for d,m in product((0,1),repeat=2)}
        assert after==expected and ordinary(after)==ordinary(preparation)
        assert expectation(after,3)==data*reference and expectation(after,12)==reference
        rows.append(dict(input=[data,reference],input_amplitudes=sorted(preparation.items()),output_amplitudes=sorted(after.items()),
                         output_expectation=[str(expectation(after,3)),str(expectation(after,12))],
                         pointer_occupied=str(read_r(reader)),ordinary=ordinary(after)))
    return rows


def crossed():
    rows=[]
    for sign in (1,-1):
        prep={encode(d,0):sign**d for d in (0,1)}
        for name,program in ARMS.items():
            stages=[]
            for k in range(len(program)+1):
                state=transported(prep,program[:k]); stages.append(dict(ordinary=ordinary(state),amplitudes=sorted(state.items())))
            cut=transported(prep,program);out=transported(cut,'P')
            assert all(legal(w,law) for w in out for law in ('parity','nae'))
            assert expectation(cut,3)==sign
            whole_flip=expectation(cut,3)
            rows.append(dict(input_sign=sign,history=name,initial_amplitudes=sorted(prep.items()),stages=stages,
                generator_flip_mean=str(whole_flip),quantum_plus=str((1+whole_flip)/2),ordinary_detector_fired=str(read_r(out)),
                fixed_sign_unoccupied=str(1-read_r(out)),reversed_scorer_unoccupied=str(read_r(out)),
                global_negation_same_ordinary=ordinary(cut)==ordinary({w:-a for w,a in cut.items()})))
    return rows


def mathematical_mixer():
    # The sum/difference step is deliberately supplied here, outside the ordinary act().
    result={}
    for name,weights in [('plus',(1,1)),('minus',(1,-1)),('word0',(1,0)),('word1',(0,1))]:
        a,b=weights; incoming={encode(0,0):a,encode(1,0):b};g={encode(0,0):a+b,encode(1,0):a-b}
        output=transported(g,'CP')
        assert norm(g)==2*norm(incoming)
        result[name]=dict(signed_input=weights,after_mixer_amplitudes=sorted(g.items()),before_pointer=ordinary(g),
                         detector_occupied=str(read_r(output)),detector_unoccupied=str(1-read_r(output)))
    return result


def effect_table():
    # Each row is E00, E11, Re(E01), Im(E01). Every number is an exact rational.
    specs={'record_never':(0,0,0,0),'record_always':(1,1,0,0),'ordinary_word_zero':(1,0,0,0),
           'unbiased_diagonal':(F(1,2),F(1,2),0,0),'imaginary_projector':(F(1,2),F(1,2),0,F(1,2)),
           'real_plus_projector':(F(1,2),F(1,2),F(1,2),0),'real_minus_projector':(F(1,2),F(1,2),-F(1,2),0),
           'tilted_real_projector':(F(4,5),F(1,5),F(2,5),0)}
    inputs={'plus':(1,1),'minus':(1,-1),'singleton0':(1,0),'singleton1':(0,1)}
    rows={}
    for name,raw in specs.items():
        u,v,b,c=map(F,raw);square=b*b+c*c; constraints=[u*v-square,(1-u)*(1-v)-square]
        assert all(k>=0 for k in constraints) and 0<=u<=1 and 0<=v<=1
        ans={}
        for prep,(x,y) in inputs.items():
            p=(x*x*u+y*y*v+2*x*y*b)/(x*x+y*y)
            ans[prep]=dict(event=str(p),complement=str(1-p),selection_if_event=str(p),
                           joint_selection_and_event=str(p),conditional_event='1' if p else None)
        ans['equal_incoherent_mixture']=dict(event=str((u+v)/2))
        assert F(ans['plus']['event'])-F(ans['minus']['event'])==2*b
        rows[name]=dict(effect=list(map(str,raw)),positivity_determinants=list(map(str,constraints)),
                        contrast=str(2*b),square_of_sharp_absolute_contrast_bound=str(4*min(u*v,(1-u)*(1-v))),answers=ans)
    return rows


def transfers_source():
    # Each of two initial words can merge into the same terminal ordinary word. A complete classical
    # merging channel records the old branch in separate Kraus paths. The alternative normalized
    # two-output instrument coherently recombines it with one minus coefficient.
    rows={}
    for label,(a,b) in {'plus':(1,1),'minus':(1,-1),'singleton0':(1,0),'singleton1':(0,1)}.items():
        denominator=a*a+b*b
        qplus=F((a+b)**2,2*denominator);qminus=F((a-b)**2,2*denominator)
        assert qplus+qminus==1
        rows[label]=dict(ordinary_single_terminal='1',classical_branch_probabilities=list(map(str,[F(a*a,denominator),F(b*b,denominator)])),
            raw_unscaled_one_path_coherent_mass=str(F((a+b)**2,denominator)),positive_selected_filter=str(qplus),
            complete_signed_complement=str(qminus),postselected_single_output='1' if qplus else None)
    return rows


def run(check=False):
    cross=crossed(); kickback=transfer(); effects=effect_table();mixer=mathematical_mixer()
    save('signed_comparisons.json',dict(crossed_sign_and_history=cross,controlled_swap_on_supplied_phase=kickback,
         supplied_mixer_and_physical_pointer=mixer,effects=effects,merger_controls=transfers_source()),check)
    return dict(signed_history_cells=len(cross),input_phase_pairs=len(kickback),binary_effects=len(effects),
                algebraic_readout_controls=len(mixer))
