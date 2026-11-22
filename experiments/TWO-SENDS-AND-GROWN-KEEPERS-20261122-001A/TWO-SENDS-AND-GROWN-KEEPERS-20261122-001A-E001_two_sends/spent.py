"""Check the two spent offers without the supplied relay on each recorded full board."""
import gzip
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE.parents[2] / 'artifacts' / HERE.parent.name / HERE.name


def bits(w, marks):
    return ''.join(str(w >> m & 1) for m in marks)


def transposed(word, a, b):
    return word ^ ((1 << a) | (1 << b)) if (word >> a ^ word >> b) & 1 else word


def main():
    with gzip.open(OUT / 'sends.json.gz', 'rt') as f:
        raw = json.load(f)
    checks = []
    for law, ldata in raw['laws'].items():
        for crossed, old in raw['originals'].items():
            c8, u8 = old['devices_in_c8_u8_order']
            donor = next(dev for dev in (c8, u8) if dev['source'] == old['source_p'])
            final = old['stars'] + ldata['boards'][crossed]['newborn_stars']
            count_original = len(old['stars'])
            for rev in (0, 1):
                initial = int(ldata['words'][f'{crossed}-{rev}']['complete_after_two_cuts'], 16)
                a, b, c = donor['offer'][::-1] if rev else donor['offer']
                assert bits(initial, (a, b, c)) == '100'
                twins = [transposed(initial, a, d) for d in (b, c)]
                assert transposed(twins[0], b, c) == twins[1]
                wear = [[i for i, star in enumerate(final) if m in star] for m in (a, b, c)]
                assert wear[0] == wear[1] == wear[2] == sorted((old['source_p'], donor['witness']))
                impacts = []
                for i, star in enumerate(final):
                    holds = [bits(word, star) for word in twins]
                    counts = [w.count('1') for w in holds]
                    assert counts[0] == counts[1]
                    assert counts[0] % 2 == 0 if law == 'parity' else 0 < counts[0] < len(star)
                    if holds[0] != holds[1]:
                        impacts.append(i)
                assert impacts == wear[0] and all(i < count_original for i in impacts)
                assert c8['receiver'] not in impacts and u8['receiver'] not in impacts
                checks.append({'law': law, 'crossed': int(crossed), 'reversed_bank': rev,
                               'same_names_at_both_holders_before_and_after_two_cuts': [a, b, c],
                               'permutation_between_offers': [b, c], 'only_changed_whole_holders': impacts,
                               'unchanged_complete_newborn_holdings': len(final) - count_original,
                               'whole_receivers_unchanged': [c8['receiver'], u8['receiver']],
                               'receiver_bank_both_arms': bits(twins[0], c8['receipt'][::-1] if rev else c8['receipt']),
                               'first_end_rise': False})
    (OUT / 'spent.json').write_text(json.dumps({'checks': checks}, sort_keys=True, indent=2) + '\n')
    print(f'Checked {len(checks)} spent-offer couplings.')


if __name__ == '__main__':
    main()
