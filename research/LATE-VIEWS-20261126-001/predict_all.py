"""predict_all.py OUT.jsonl.gz: every held-out prediction, made from the starts alone before any grown file is opened
(the advisor's pre-registration).  One line per (set, start, knot law): accepted or why not, the stratum and rare strata,
the predicted dimension D, the predicted settling rounds K0 and K1, and the predicted view through the rounds the set is
grown to.  Sets: the uniform sample of 2,000 six-knot census starts (sample.py), the stratified supplement
(stratified.jsonl), the hand-built starts (handbuilt.jsonl), 1,000 seven-knot starts of the 'grow' weighting
(sample_grow.py), and the 100 starts grown to round 40 (horizon.jsonl, not-all-equal only)."""
import sys, os, json, gzip, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import late, sample, sample_grow, strata


def sets():
    yield 'uniform', [(i, stars) for i, gi, loose, stars in sample.fresh()], ('nae', 'parity'), 24
    yield 'stratified', [(x['index'], x['stars']) for x in map(json.loads, open(os.path.join(HERE, 'stratified.jsonl')))], ('nae', 'parity'), 24
    yield 'handbuilt', [(x['index'], x['stars']) for x in map(json.loads, open(os.path.join(HERE, 'handbuilt.jsonl')))], ('nae', 'parity'), 24
    yield 'grow7', [(i, sample_grow.stars_of(s, e)) for i, (s, e) in enumerate(sample_grow.draws(1000))], ('nae', 'parity'), 24
    yield 'horizon', [(x['index'], x['stars']) for x in map(json.loads, open(os.path.join(HERE, 'horizon.jsonl')))], ('nae',), 40


if __name__ == '__main__':
    out = sys.argv[1]
    with gzip.open(out, 'wt') as f:
        for name, starts, laws, rounds in sets():
            for law in laws:
                for i, stars in starts:
                    st = {}
                    P, why = late.predict(stars, rounds, law, static=st)
                    M, what, rare = strata.read(stars)
                    f.write(json.dumps({'set': name, 'index': i, 'knot law': law, 'read': why,
                                        'stratum': st.get('stratum'), 'rare strata': rare, 'D': st.get('D'),
                                        'K0': st.get('K0'), 'K1': st.get('K1'), 'rows': P}, sort_keys=True) + '\n')
    h = hashlib.sha256()
    with gzip.open(out, 'rb') as f: h.update(f.read())
    print('sha256 of the uncompressed predictions:', h.hexdigest())
