"""The registered runs of the pre-registration ("Runs (frozen)", items 2 to 4), as data."""

# a law family: (ration, treatment, release, fillers)
CAP3W = ('CAP-3', 'CANCEL-WAIT', 'RELEASE', False)
CAP3WF = ('CAP-3', 'CANCEL-WAIT', 'RELEASE', True)
CAP3H = ('CAP-3', 'CANCEL-WAIT', 'HOLD', False)
R3H = ('RATION-3', 'CANCEL-WAIT', 'HOLD', False)
F1RH = ('FLOOR1', 'CANCEL-RETIRE', 'HOLD', False)
F1OH = ('FLOOR1', 'CANCEL-OFFSHOOT', 'HOLD', False)
FAMILY_NAMES = {CAP3W: 'CAP3W', CAP3WF: 'CAP3WF', CAP3H: 'CAP3H', R3H: 'R3H', F1RH: 'F1RH', F1OH: 'F1OH'}
NAMES = {v: k for k, v in FAMILY_NAMES.items()}

CAP = 2_000_000          # states, for every search over every order; no time budget

# item 2, the cap
CAP_STARTS = ('D2(4,3)', 'D2(5,3)', 'Ring(5,3)', 'C8X3', 'TWO-KNOT', 'THREE-KNOT')
CAP_LAWS = (CAP3W, CAP3WF)
CAP_GUARDS = ('R1', 'R2', 'R3', 'CONTROL')
CAP_CUTOFFS = (1, 3)

# item 3, T(d) under the cap
TD_STARTS = ('D2(4,3)', 'D2(6,3)')
TD_DS = (2, 3, 4, 5, 6)

# item 4, holding
HOLD_LAWS = (CAP3H, R3H, F1RH, F1OH)
HOLD_STARTS = {'D2(4,3)': (1, 2, 3), 'Ring(5,3)': (1, 2, 3), 'TWO-KNOT': (1, 2, 3, 4), 'THREE-KNOT': (1, 2, 3, 4)}
HOLD_GUARDS = ('R1', 'R2', 'R3', "R3'", 'CONTROL')


def configs():
    """(run id, start, family, cutoff, guard)."""
    out = []
    for fam in CAP_LAWS:
        for start in CAP_STARTS:
            for r in CAP_CUTOFFS:
                for g in CAP_GUARDS:
                    out.append(('%s-%s__r%d__%s' % (FAMILY_NAMES[fam], start, r, g), start, fam, r, g))
    for start in TD_STARTS:
        for d in TD_DS:
            out.append(('TD-%s__r1__T(%d)' % (start, d), start, CAP3W, 1, 'T(%d)' % d))
    for fam in HOLD_LAWS:
        for start, cuts in HOLD_STARTS.items():
            for r in cuts:
                for g in HOLD_GUARDS:
                    out.append(('%s-%s__r%d__%s' % (FAMILY_NAMES[fam], start, r, g.replace("'", 'P')), start, fam, r, g))
    return out


def gate_pairs():
    pairs = {}
    for cid, start, fam, r, g in configs():
        pairs.setdefault((start, fam), set()).add(r)
    return pairs
