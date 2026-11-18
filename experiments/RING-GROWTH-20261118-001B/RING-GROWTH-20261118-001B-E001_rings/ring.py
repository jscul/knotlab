import sys, time
sys.path.append(str(__import__('pathlib').Path(__file__).resolve().parents[3] / 'experiments/FIRST-KNOT-20261118-001B/FIRST-KNOT-20261118-001B-E001_two_knots'))
import startlib as S
F = S.F
def ring(sizes):
    n = len(sizes); stars = []; b = n
    for i in range(n):
        st = [i, (i + 1) % n]          # shares bit i with the next knot... bit i between knot i and i+1
        stars.append(st)
    # fix: knot i holds shared bits (i-1) and i
    stars = [[(i - 1) % n, i] for i in range(n)]
    for i in range(n):
        while len(stars[i]) < sizes[i]:
            stars[i].append(b); b += 1
    return stars
def grow(stars, rounds, maxj=60000):
    P = S.from_junctions(stars)
    P.linalg = False   # connected start: the structural implied test holds (Lemma 0)
    t0 = time.time()
    for r in range(rounds):
        x = P.step(F.fewest, None)
        if x is None or x['new'] == 0 or len(P.bits_of) > maxj: break
    return P
if __name__ == '__main__':
    sizes = [int(x) for x in sys.argv[1].split(',')]; R = int(sys.argv[2])
    t = time.time()
    P = grow(ring(sizes), R)
    c = P.counts_by_round()
    print(sizes, P.rounds, round(time.time() - t), c)
    print('offshoots', P.offshoots_by_round())
