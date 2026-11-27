"""Look for four single-word clauses beyond the fixed alternating assignment."""

import argparse
from collections import Counter
from contextlib import contextmanager
import ctypes
import gzip
from itertools import combinations, product
import json
import os
from pathlib import Path
import random
import subprocess
import sys
from tempfile import NamedTemporaryFile
from time import perf_counter

import numpy as np


HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent.parent
sys.path.insert(0, str(RESEARCH / 'NAE-LAYER-20261127-001/referee-R1'))
from growth_rule import advance, supports_of

SOURCES = RESEARCH / 'FORBID-EDITS-20261126-001/starts.json'
CODE = ctypes.c_uint32
BOUND = tuple(product((0, 1), repeat=2))
WORDS = tuple(product((0, 1), repeat=6))


def kind(f):
    if f in (0, 15):
        return 'five carriers'
    if f in (6, 9):
        return 'alternating'
    if f.bit_count() == 2:
        return 'one index'
    return 'three and one'


def lower_indices(f):
    return [((f >> (2*j+k)) & 1, 2+j, 4+k) for j,k in BOUND]


def upper(w):
    return (w[0] & w[1], w[2] | w[3], w[4] | w[5])


def canonical(row):
    aa, bb, cc = row[0:2], row[2:4], row[4:6]
    clauses = {frozenset((aa[(row[6] >> (2*j+k)) & 1], bb[j], cc[k])) for j,k in BOUND}
    aa = tuple(sorted(aa))
    bb, cc = sorted((tuple(sorted(bb)),tuple(sorted(cc))))
    f = sum(1 << (2*j+k) for j,k in BOUND if frozenset((aa[1],bb[j],cc[k])) in clauses)
    return (*aa,*bb,*cc,f)


@contextmanager
def joins():
    with NamedTemporaryFile(prefix='alternative_join_', suffix='.so', dir=HERE) as target:
        subprocess.run(['g++','-std=c++17','-O3','-fPIC','-shared',str(HERE/'alternative_joins.cpp'),
                        '-o',target.name], check=True, env=dict(os.environ, TMPDIR=str(HERE)))
        lib = ctypes.CDLL(target.name)
        ptr = ctypes.c_void_p
        for fname, restype, atypes in (
            ('find', ptr, [ctypes.POINTER(CODE), ctypes.c_size_t]),
            ('data', ctypes.POINTER(CODE*7), [ptr]), ('size',ctypes.c_size_t,[ptr]),
            ('five',ctypes.c_uint64,[ptr]), ('release',None,[ptr]),
        ):
            function = getattr(lib, 'alternative_'+fname)
            function.restype = restype
            function.argtypes = atypes

        def find(clauses):
            data = np.asarray(clauses, dtype=np.uint32, order='C')
            handle = lib.alternative_find(data.ctypes.data_as(ctypes.POINTER(CODE)), len(clauses))
            try:
                output = lib.alternative_data(handle)
                covers = [canonical(tuple(output[i])) for i in range(lib.alternative_size(handle))]
                if len(covers) != len(set(covers)):
                    raise ValueError('Repeated six-reading certificate')
                return sorted(covers), int(lib.alternative_five(handle))
            finally:
                lib.alternative_release(handle)
        yield find


def pairings(members):
    if not members:
        yield ()
        return
    x = min(members)
    for y in sorted(members - {x}):
        for rest in pairings(members - {x, y}):
            yield ((x,y),*rest)


def brute(clauses):
    known = set(map(frozenset, clauses))
    literals = sorted(set.union(*map(set, clauses)))
    covers = set()
    five = 0
    for count in (5,6):
        for members in combinations(literals,count):
            if any((x>>1) & (y>>1) for x,y in combinations(members,2)):
                continue
            if count == 5:
                for a in members:
                    for b,c in pairings(set(members)-{a}):
                        five += all(frozenset((a,b[j],c[k])) in known for j,k in BOUND)
            else:
                for parts in pairings(set(members)):
                    for q,a in enumerate(parts):
                        b,c = parts[:q]+parts[q+1:]
                        for f in range(1,15):
                            if kind(f) == 'alternating':
                                continue
                            if all(frozenset((a[(f>>(2*j+k))&1],b[j],c[k])) in known for j,k in BOUND):
                                covers.add((*a,*b,*c,f))
    return sorted(covers), five


def controls(find):
    # The six carriers are pairs. Moving one raw place into another carrier
    # below supplies a separate test of disjointness.
    readings = [(3 << (1+2*i)) | (i%2) for i in range(6)]
    tested = 0
    cases = {}
    for f in range(16):
        indices = lower_indices(f)
        clauses = [[readings[i] for i in loc] for loc in indices]
        found = find(clauses)
        assert found == brute(clauses)
        tag = (kind(f),len(found[0]),found[1])
        cases[tag] = cases.get(tag,0)+1
        allowed = [w for w in WORDS if not any(all(w[i] for i in loc) for loc in indices)]
        image = {upper(w) for w in allowed}
        assert len(image) == 7 and (1,1,1) not in image
        for n, loc in enumerate(indices):
            assert len({tuple(w[i] for i in loc) for w in allowed}) == 7
            groups = {s: [upper(w) for w in allowed if tuple(w[i] for i in loc) == s]
                      for s in product((0,1),repeat=3)}
            assert all(any(len({w[p] for w in row}) == 2 for row in groups.values()) for p in range(3))
            assert any(upper(w) == (1,1,1) and not any(all(w[i] for i in o)
                       for i0,o in enumerate(indices) if i0 != n) for w in WORDS)
            assert find(clauses[:n]+clauses[n+1:]) == ([],0)
        tested += 1
    rng = random.Random(20261127)
    extras = sorted(set(readings + [readings[0]^1, readings[3]^1, (3<<2)|1, (3<<6)|1]))
    triples = [x for x in combinations(extras,3) if all(not((a>>1) & (b>>1)) for a,b in combinations(x,2))]
    for trial in range(5):
        planted = rng.sample(triples, 18)
        assert find(planted) == brute(planted)
    return {'labeled assignments checked on all 64 virtual states':tested,
            'four individual clause deletions per assignment':4*tested,
            'extra mixed-sign and overlap controls against exhaustive search':5,
            'by chosen assignment, alternative all-six matches, five-carrier matches':
                [{'assignment':k[0],'all-six matches':k[1],'five-carrier matches':k[2],'cases':v}
                 for k,v in sorted(cases.items())]}


def masks_to_triples(signature):
    return [tuple(i for i in range(mask.bit_length()) if (mask>>i)&1) for mask in signature]


def packed(bits):
    return int.from_bytes(np.packbits(bits,bitorder='little').tobytes(),'little')


class Source:
    def __init__(self, start, grow):
        supports = supports_of(start)
        self.original = len(supports)
        for _ in range(grow):
            result = advance(supports)
            assert result.status == 'funded'
            supports = result.supports
        self.supports = supports
        n = 1+max(max(x) for x in supports)
        self.states = np.arange(0,1<<n,2,dtype=np.uint32)
        failures = np.zeros(len(self.states),dtype=np.uint64)
        for i, supp in enumerate(supports):
            fails = self.agree(sum(1<<j for j in supp))
            failures |= fails.astype(np.uint64) << i
        self.legal = packed(failures==0)
        self.single = [packed(failures==(1<<q)) for q in range(len(supports))]
        self.full = (1<<len(self.states))-1
        self.values = {}
        self.allowed = 2*self.legal.bit_count()

    def agree(self, mask):
        part = self.states & mask
        return (part==0) | (part==mask)

    def value(self, literal):
        if literal not in self.values:
            result = packed(self.agree(literal>>1))
            self.values[literal] = result if literal&1 else self.full^result
        return self.values[literal]

    def upper_properties(self, group):
        a0,a1,b0,b1,c0,c1 = map(self.value,group)
        up = (a0&a1,b0|b1,c0|c1)
        on = up[0]&up[1]&up[2]
        assert not self.legal & on
        present = []
        for word in product((0,1),repeat=3):
            chosen = self.legal
            for bit,mask in zip(word,up):
                chosen &= mask if bit else ~mask
            if chosen:
                present.append(''.join(map(str,word)))
        pair_free = all(len({(w[p],w[q]) for w in present})==4 for p,q in combinations(range(3),2))
        restored = [2*(on & part).bit_count() for part in self.single]
        return up, present, pair_free, restored

    def mixed(self, group, f, up):
        columns = [self.value(r) for r in group]
        mixtures = []
        for loc in lower_indices(f):
            counts = [0,0,0]
            for code in product((0,1),repeat=3):
                mask = self.legal
                for i,v in zip(loc,code):
                    mask &= columns[i] if v else ~columns[i]
                if not mask:
                    continue
                for i,v in enumerate(up):
                    counts[i] += bool(mask & v and mask & ~v)
            mixtures.append(counts)
        return mixtures


def read_stage(start,round_index,clauses,find,archive):
    covers,five = find(clauses)
    totals = Counter()
    examples = {}
    grouped = {}
    for row in covers:
        grouped.setdefault(row[:6],[]).append(row[6])
    valid_groups = set()
    birth_groups = set()
    if covers:
        source = Source(archive[start],round_index)
    for group, masks in grouped.items():
        up, present, pair_free, restored = source.upper_properties(group)
        for f in masks:
            tag = kind(f)
            totals[tag+' covers'] += 1
            mixes = source.mixed(group,f,up)
            valid = pair_free and all(all(row) for row in mixes)
            born = any(restored[source.original:])
            totals[tag+' steps'] += valid
            totals[tag+' birth-essential steps'] += valid and born
            if valid:
                valid_groups.add(group)
                if born:
                    birth_groups.add(group)
            desc = tag + (' birth-essential step' if valid and born else ' step' if valid else ' failed reading')
            if desc not in examples:
                examples[desc] = {'carriers A0,A1,B0,B1,C0,C1':masks_to_triples([r>>1 for r in group]),
                                  'agreement values counted as true':[r&1 for r in group],
                                  'A index for B,C choices 00,01,10,11':[(f>>k)&1 for k in range(4)],
                                  'upper words':present,'free in pairs':pair_free,
                                  'lower-cell counts with each upper reading varying':mixes,
                                  'source laws':source.supports,'source laws before growth':source.original,
                                  'allowed raw states':source.allowed,
                                  '111 states restored by each single source law deletion':restored}
    return {'start':start,'round':round_index,'single-word clauses':len(clauses),
            'five-carrier families':five,'all-six certificates':len(covers),
            'distinct upper reading triples':len(grouped),'distinct upper reading triples passing':len(valid_groups),
            'distinct upper reading triples passing with a birth needed':len(birth_groups),
            'counts':dict(totals),'examples':examples}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', nargs='*', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--limit', type=int)
    parser.add_argument('--controls', action='store_true')
    args = parser.parse_args()
    archive = json.loads(SOURCES.read_text())
    total_time = perf_counter()
    rows = []
    with joins() as find:
        if args.controls:
            check = controls(find)
        for fname in args.input:
            opener = gzip.open if fname.suffix == '.gz' else open
            with opener(fname,'rt') as raw:
                for line in raw:
                    if args.limit is not None and len(rows) >= args.limit:
                        break
                    stage = json.loads(line)
                    start = int(str(stage.get('start', stage.get('census_entry'))).split()[-1])
                    index = stage['round']
                    since = perf_counter()
                    row = read_stage(start,index,stage['clauses'],find,archive)
                    row['seconds'] = round(perf_counter()-since,5)
                    rows.append(row)
    counters = Counter()
    for row in rows:
        counters.update(row['counts'])
    report = {'scope':'Fixed signed readings. Four single-word clauses meet one member of each pair. '
                     'One upper reading requires both members, the other two require either member. '
                     'Only the nonalternating assignments are counted here.',
              'stages':len(rows),'single-word clauses':sum(row['single-word clauses'] for row in rows),
              'five-carrier families':sum(row['five-carrier families'] for row in rows),
              'stages with a five-carrier family':sum(bool(row['five-carrier families']) for row in rows),
              'all-six certificates':sum(row['all-six certificates'] for row in rows),'counts':dict(counters),
              'stages with an all-six certificate':sum(bool(row['all-six certificates']) for row in rows),
              'distinct starts with any new positive':sorted(set(row['start'] for row in rows if row['distinct upper reading triples passing'])),
              'distinct starts with any new birth-essential positive':sorted(set(row['start'] for row in rows if row['distinct upper reading triples passing with a birth needed'])),
              'seconds including input and compilation':round(perf_counter()-total_time,4),'rows':rows}
    if args.controls:
        report['controls'] = check
    args.output.write_text(json.dumps(report, separators=(',',':'))+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('rows','controls')}))


if __name__ == '__main__':
    main()
