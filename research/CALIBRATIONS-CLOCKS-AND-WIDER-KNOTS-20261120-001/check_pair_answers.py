"""Independent finite checks of conditional pair answers and the act that stays lawful."""
from fractions import Fraction
from itertools import product
import json


def check_effect(words, width, flip):
    """Integer amplitudes suffice for both real outcome projections."""
    allowed = set(words)
    paired = sum(word ^ flip in allowed for word in words)
    guard = {word: word ^ flip if word ^ flip in allowed else word for word in words}
    assert set(guard.values()) == allowed and all(guard[guard[w]] == w for w in words)
    outcomes = {}
    for sign in (1, -1):
        amps = [int(w in allowed) + sign * int(w ^ flip in allowed) for w in range(1 << width)]
        norm = sum(v*v for v in amps)
        chance = Fraction(norm, 4*len(allowed))
        assert chance == Fraction(len(allowed) + sign*paired, 2*len(allowed))
        assert all(amps[w ^ flip] == sign*amps[w] for w in range(len(amps)))
        outside = sum(v*v for w,v in enumerate(amps) if w not in allowed)
        if norm and sign == -1:
            assert Fraction(outside,norm) == Fraction(1,2)
        outcomes[str(sign)] = {
            "probability": str(chance),
            "outside_probability_after": str(Fraction(outside,norm)) if norm else None,
            "squared_weights_before_normalizing": [v*v for v in amps],
        }
    return outcomes


def restricted_three(words):
    settings = {}
    for choices in product('XZ', repeat=3):
        question = ''.join(choices)
        answers = {}
        for w in words:
            signs = tuple(1 if q == 'X' or not (w >> j & 1) else -1 for j,q in enumerate(choices))
            key = ','.join(map(str,signs))
            answers[key] = answers.get(key,0) + 1
        settings[question] = {k:str(Fraction(v,len(words))) for k,v in sorted(answers.items())}
    def expectation(key):
        return sum(Fraction(v)*int(x)*int(y)*int(z) for bits,v in settings[key].items()
                   for x,y,z in [bits.split(',')])
    score = expectation('XXX') - sum(expectation(q) for q in ('XZZ','ZXZ','ZZX'))
    return {"score":str(score), "joint_tables":settings}


def split_six():
    """Replace each primitive local flip in the old expression by its lawful permutation."""
    words=[w for w in range(64) if not (w & 7).bit_count()%2 and not (w >> 3).bit_count()%2]
    def together(w, names):
        return (-1)**sum(w >> i & 1 for i in names)
    def nine(z,v):
        # The minus was printed explicitly on the final expression in the old game.
        return (1,1,1,v,z,z*v,v,z,-z*v)
    histogram = {}
    for r,c in product(range(3), repeat=2):
        counts={}
        for w in words:
            assert all((w ^ (1 << bit)) not in words for bit in (0,2,3,5))
            a=nine(together(w,(0,1)),together(w,(3,4)))
            b=nine(together(w,(2,)),together(w,(5,)))
            row=a[3*r:3*r+3];col=b[c::3]
            assert row[c] == col[r]
            signs=row+col;counts[signs]=counts.get(signs,0)+1
        def mass(predicate):
            return str(Fraction(sum(v for signs,v in counts.items() if predicate(signs)),len(words)))
        histogram[f'{r+1},{c+1}']={
            "both_context_signs_and_shared_answer":mass(lambda s: s[0]*s[1]*s[2]==1
                         and s[3]*s[4]*s[5]==(-1 if c==2 else 1) and s[c]==s[3+r]),
            "all_64_cell_numerators":[counts.get(s,0) for s in product((1,-1),repeat=6)],
            "denominator":len(words)
        }
    return histogram


def main():
    supports = checks = 0
    for width in (1,2,3):
        for mask in range(1,1 << (1 << width)):
            words=[w for w in range(1 << width) if mask >> w & 1]
            supports+=1
            for flip in range(1,1 << width):
                check_effect(words,width,flip);checks+=1
    examples={}
    for law,words in [('parity',[0,3,5,6]),('not-all-equal',list(range(1,7)))]:
        examples[law]={"single_change":check_effect(words,3,1),"lawful_primitive_reading":restricted_three(words)}
    return {"finite_supports":supports,"nonempty_flip_checks":checks,"ternaries":examples,
            "parity_six_rule_primitive_replacement":split_six()}

if __name__=='__main__':
    print(json.dumps(main(),indent=2))
