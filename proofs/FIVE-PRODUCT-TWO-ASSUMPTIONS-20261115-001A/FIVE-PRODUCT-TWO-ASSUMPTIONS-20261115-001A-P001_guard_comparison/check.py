"""Replay the two specified guards and their cost comparisons on the original nine bits."""
from collections import Counter
from functools import cache
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile


HERE = Path(__file__).resolve().parent
PREDECESSOR_ID = 'FIVE-PRODUCT-TOTAL-WORK-20261115-001B'
PREDECESSOR = HERE.parents[1] / PREDECESSOR_ID / (PREDECESSOR_ID + '-P001_learned_affine_work')
sys.path.insert(0, str(PREDECESSOR))
import sector_audit


def require(condition, message):
    if not condition:
        raise ValueError(message)


UNIVERSE = frozenset(range(512))


def source_rows():
    rich, plain = set(), set()
    for word in UNIVERSE:
        x = [(word >> j) & 1 for j in range(6)]
        s, u, v = [(word >> j) & 1 for j in (6,7,8)]
        products = [l*r for l, r in zip(x, x[1:])]
        total = sum(products) & 1
        if s == total and u == products[0] and v == (products[1] ^ products[2]):
            rich.add(word)
        if s != total:
            plain.add(word)
    return {'R': frozenset(rich), 'P': frozenset(plain)}


SOURCES = source_rows()


@cache
def half(mask, rhs):
    return frozenset(x for x in UNIVERSE if (x & mask).bit_count() % 2 == rhs)


@cache
def hull(points):
    if not points:
        return frozenset()
    origin = min(points)
    span = {origin}
    for x in sorted(points):
        if x not in span:
            span |= {v ^ origin ^ x for v in span}
    return frozenset(span)


def stable(cell, sides):
    while cell:
        smaller = hull(cell & sides['R']) & hull(cell & sides['P'])
        if smaller == cell:
            break
        cell = smaller
    return cell


def visit(tree, cell, sides=SOURCES, guard=None, live=None):
    operator, *arguments = tree
    if operator == 'Q':
        q, no, yes = arguments
        branches = [cell & half(q, b) for b in range(2)]
        require(all(branches), 'constant question')
        return 1 + sum(visit(child, h, sides, guard, live) for child,h in zip((no,yes),branches))
    if operator == 'L':
        require(guard is not None and cell <= guard, 'missing raw premise')
        after = cell & half(1,0)
        before_fixed, after_fixed = stable(cell,sides), stable(after,sides)
        require(bool(after_fixed) and bool(before_fixed-half(1,0)), 'ineffective citation')
        live.append([len(cell),len(before_fixed),len(before_fixed-half(1,0)),len(after_fixed)])
    else:
        require(operator in sides, 'unknown operation')
        after = hull(cell & sides[operator])
    if not arguments:
        require(not after, 'nonempty claimed terminal')
        return 1
    require(len(arguments) == 1 and bool(after), 'bad continuation')
    return 1 + visit(arguments[0], after, sides, guard, live)


def fork(q, body):
    return ('Q', q, body, body)


def training_and_controls():
    x0, v0 = half(1,1), half(256,0)
    tail = fork(16, ('R',('P',)))
    narrow_only = fork(16 ^ 256, ('P',('R',)))
    output = {}
    for a in (0,1):
        broad = x0 & half(4,a)
        narrow = broad & v0
        assert len(broad) == 128 and len(narrow) == 64
        assert visit(tail,narrow) == visit(tail,broad) == visit(narrow_only,narrow) == 5
        try:
            visit(narrow_only,broad)
        except ValueError as exc:
            assert str(exc) == 'nonempty claimed terminal'
        else:
            raise AssertionError('a body specialized to v=0 survived removal of that equation')
        failed = []
        for b in (0,1):
            h = half(16 ^ 256,b) & broad
            after_plain = hull(h & SOURCES['P'])
            failed.append([len(h),len(after_plain),len(after_plain & SOURCES['R'])])
        assert failed == [[64,64,8],[64,64,8]]
        # Embedded ordinary AND conflict on x4,x5,s, directly in original coordinates.
        section = [1 | (a<<2) | ((z&3)<<4) | ((z>>2)<<6) for z in range(8)]
        assert set(section) <= narrow
        errors = []
        for z,w in enumerate(section):
            err = ((z>>2)&1) ^ ((z&1)*((z>>1)&1))
            errors.append(err)
            assert (w in SOURCES['R']) == (err==0) and (w in SOURCES['P']) == (err==1)
        for group in (0,1):
            assert len(hull(frozenset(z for z in range(8) if errors[z]==group))) == 8
        for q in range(1,8):
            assert all({errors[z] for z in range(8) if (q&z).bit_count()%2==b}=={0,1} for b in (0,1))
        output[str(a)] = {'training':5,
                          'narrow_rich_plain':[len(narrow & SOURCES[k]) for k in ('R','P')],
                          'broad_rich_plain':[len(broad & SOURCES[k]) for k in ('R','P')],
                          'failed_unmodified_body_branch_sizes':failed}
    return output


def a_zero_upper():
    tail = fork(16, ('R',('P',)))
    right = fork(1,tail)
    main = ('Q',4,('R',('L',tail)),right)
    guard = half(4,0) & half(256,0)
    live = []
    cost = visit(main, UNIVERSE, guard=guard, live=live)
    assert cost == 19 and len(live) == 1
    try:
        visit(('Q',4,('L',tail),right), UNIVERSE, guard=guard, live=[])
    except ValueError as exc:
        assert str(exc) == 'missing raw premise'
    else:
        raise AssertionError('unearned v=0 was accepted')
    return {'main':cost, 'training':5, 'total':5+cost,
            'citation_raw_fixed_excluded_retained':live[0], 'missing_rich_check':'rejected'}



def a_one_upper():
    guarded_tail = fork(16, ('R',('P',)))
    majority = fork(1, fork(16, ('R',('P',('R',)))))
    main = ('Q',4 ^ 256,majority,('R',('L',guarded_tail)))
    live = []
    cost = visit(main, UNIVERSE, guard=half(4,1) & half(256,0), live=live)
    assert cost == 23 and len(live) == 1
    return {'main':cost, 'training':5, 'total':cost+5, 'citation_raw_fixed_excluded_retained':live[0]}


def in_original(z):
    y1, w1, p1, y2, w2, p2, y3, w3, p3 = [(z>>i)&1 for i in range(9)]
    x1=y1
    x3=x1^w2
    x5=x3^w3
    bits=(w1,x1,y2,x3,y3,x5,p1^p2^p3,p1,p2)
    return sum(bit<<j for j,bit in enumerate(bits))


def residual_bounds():
    result = {}
    for a in (0,1):
        removed=sum(1<<z for z in range(64) if z&2 and not z&32 and (z>>3)&1==a)
        for z in range(512):
            raw=in_original(z)
            assert bool((removed>>(z&63))&1)==(raw in (half(1,1)&half(4,a)&half(256,0)))
        coarse, lower, exact = sector_audit.spectator_bounds(sector_audit.RICH & ~removed, sector_audit.FULL ^ removed)
        assert coarse == lower == (17,18)[a] and exact == {7:(24,68)[a]}
        result[str(a)]={'coarse':coarse,'complement_lower':lower,'compact_seven_unit_cells':exact[7],
                        'bound_before_citations':5+lower}
    # On the exceptional a=1 answer y2+p2=0, no raw point satisfies the named guard.
    d=sum(1<<z for z in range(64) if (z & 40).bit_count()%2==0)
    coarse, lower, exact = sector_audit.spectator_bounds(sector_audit.RICH & d, d)
    assert coarse == lower == 13 and exact == {7:21}
    return result, lower


def exceptional_questions():
    # (a, first query q in triple order, guarded answer, guarded true t,
    # unguarded false t on that answer, unguarded true t on the other answer).
    records=[(0,8,0,0,4,1),(0,48,1,2,3,1),(0,56,0,0,3,1),(1,40,1,1,4,0)]
    output={}
    for a,q,b,good,bad,other in records:
        rich_section, plain_section = set(),set()
        for z in range(64):
            errors = sector_audit.defects(z,2)
            for flag,t in ((0,good),(1,bad)):
                word = (z&7) | (t<<3) | ((z&56)<<3)
                raw = in_original(word)
                assert (word&q).bit_count()%2 == b
                assert (raw in half(4,a) & half(256,0)) == (flag==0)
                r,p = raw in SOURCES['R'],raw in SOURCES['P']
                assert r==(flag==0 and errors==0) and p==bool(flag ^ (errors.bit_count()%2))
                if r: rich_section.add(z|(flag<<6))
                if p: plain_section.add(z|(flag<<6))
            word=(z&7) | (other<<3) | ((z&56)<<3)
            raw=in_original(word)
            assert (word&q).bit_count()%2 != b and raw not in half(4,a) & half(256,0)
            assert (raw in SOURCES['R'])==(errors==0) and (raw in SOURCES['P'])==bool(errors.bit_count()%2)
        assert len(hull(frozenset(rich_section)))==64 and len(hull(frozenset(plain_section)))==128
        output[str(q)]={'a':a,'answer':b,'local_states':[good,bad,other]}
    return output


def all_first_questions(opposite_bound):
    compiler=shutil.which('c++')
    require(compiler is not None, 'a C++20 compiler is required')
    with tempfile.TemporaryDirectory(prefix='two-assumptions-first-question-') as directory:
        exe=Path(directory)/'audit'
        subprocess.run([compiler,'-std=c++20','-O2','-I',str(PREDECESSOR),str(HERE/'first_questions.cpp'),
                        '-o',str(exe)],check=True,capture_output=True)
        proc=subprocess.run([str(exe)],check=True,text=True,capture_output=True)
    rows={0:{},1:{}}
    for line in proc.stdout.splitlines():
        a,q,cost=map(int,line.split())
        assert a in rows and q not in rows[a]
        rows[a][q]=cost
    output={}
    for a in (0,1):
        assert set(rows[a])==set(range(1,512))
        first=Counter(rows[a].values())
        exceptions=sorted(q for q,cost in rows[a].items() if cost==18)
        assert exceptions==([8,48,56],[40])[a]
        for q in exceptions:
            unguarded=opposite_bound if a==1 else 11
            rows[a][q]=max(rows[a][q],1+7+unguarded)
        main=min(rows[a].values())
        assert main==(19,21)[a]
        output[str(a)]={'initial_histogram':dict(sorted(first.items())),
                        'strengthened_questions':exceptions,'main_lower_bound':main,
                        'with_training_lower_bound':5+main}
    return output


def main():
    assert {key:len(value) for key,value in SOURCES.items()} == {'R':64,'P':256}
    assert len({in_original(z) for z in range(512)}) == 512
    for z in range(512):
        err = sector_audit.defects(z,3)
        w = in_original(z)
        assert (w in SOURCES['R']) == (err==0) and (w in SOURCES['P']) == bool(err.bit_count()%2)
    sector, opposite = residual_bounds()
    previous = json.loads((PREDECESSOR/'checks.json').read_text())['one_affine_premise_full_census']
    assert min(map(int,previous['lower_bound_by_all_orientations']))==23
    assert previous['named_v_zero_implies_x0_zero']=={'main_lower_bound':18,'training':7,'total_lower_bound':25}
    result={'status':'passed','original_visible_words':512,'training_and_failed_body':training_and_controls(),
            'optional_rule_optimum_by_a':[23,23],'exact_declared_a_zero':a_zero_upper(), 'live_a_one_upper':a_one_upper(),
            'complement_bounds':sector,'opposite_answer_of_mask_40':opposite,
            'flagged_section_checks':exceptional_questions(),'all_first_questions':all_first_questions(opposite),
            'joint_training_cost':10,'joint_main_lower':18,'joint_total_lower':28}
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=='__main__':
    main()
