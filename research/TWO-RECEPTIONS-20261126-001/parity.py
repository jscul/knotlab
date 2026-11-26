"""parity.py: the referee's first Block, followed up: under the parity knot law an implied birth can be owed and receive
nothing, a shortage the recorded laws make with no ration dropped by hand.  Does it carry a far change late?  Third
study of TWO-RECEPTIONS-20261126-001 (README.md, C); shortage.py's census (the same 100 receivers, seed 20261126, and
five senders, a meeting through two link knots, 12 rounds, 1,500 knots or the guard) under the ordinary count with the
parity knot law, with no take and with each recorded take.

    parity.py run I0 I1"""
import sys, os, json, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import shortage
eng = shortage.eng
shortage.law_of = lambda r, take, choice: eng.Law(r, 'CANCEL-WAIT', take, 'parity', choice)
shortage.LAWS = [l for l in shortage.LAWS if l[0] == 'ORD']

if __name__ == '__main__':
    R = shortage.receivers.register()
    sample = sorted(random.Random(shortage.SEED).sample(range(646), 100))
    for i in sample[int(sys.argv[2]):int(sys.argv[3])]:
        for B in shortage.receivers.SENDERS:
            for lw in shortage.LAWS:
                r = shortage.pair(R[i][0], B, lw); r['knot law'] = 'parity'
                print(json.dumps(r), flush=True)
