"""Named weighting, law, reader, horizon and denominator summaries of retained draws."""
from collections import Counter, defaultdict
import json
from scipy.stats import beta
from survey import OUT, ROOT


def interval(yes, n):
    if not n:
        return None
    low = 0.0 if not yes else float(beta.ppf(.025, yes, n - yes + 1))
    high = 1.0 if yes == n else float(beta.ppf(.975, yes + 1, n - yes))
    return [low, high]


def triple(yes, unknown, n):
    assert 0 <= yes <= yes + unknown <= n
    cp = interval(yes, n)
    return {'n': n, 'yes': yes, 'no': n - yes - unknown, 'unknown': unknown,
            'yes_fraction': yes/n if n else None, 'identification_count': [yes, yes + unknown],
            'marginal_95_exact_certified': cp,
            'marginal_95_existence_envelope': [cp[0], interval(yes + unknown, n)[1]] if n else None,
            'zero_detector_one_sided_95': 1 - .05**(1/n) if n and not yes else None}


def events(result, horizon, complete):
    parts = result['parts']
    one_end = any(t['certified'] is not None and t['certified'] <= horizon
                  for p in parts for t in p['tip_records'])
    periodic = complete and any(v['age'] <= horizon for p in parts for v in p['periodic_packets'])
    recurrence = any(p['positive'] for p in parts)
    unbounded_open = any(not p['positive'] and not p['bounded'] for p in parts)
    unclosed = any(not p['closed'] for p in parts)
    truncated = any(not p['bounded'] and ((p['cap'] and p['cap']['before_age'] <= horizon-15)
                      or p['unreadable_or_large_candidate']) for p in parts)
    candidate = complete and any(c['age']+2*(len(q['a'])+len(q['b']))-1 <= horizon
                                 for p in parts for c in p['structural_candidates'] for q in c['pairs'])
    # Every returned candidate has been adjudicated. Finite detector zeros count exactly.
    observed = bool(one_end or periodic)
    recognizes = bool(periodic)
    return {'legal': (result['legal'],False), 'funded': (result['funded'],False),
            'one_release_certified': (observed, False),
            'any_release_by_horizon_under_another_reading': (observed, not observed and unclosed),
            'structural_candidate_returned': (bool(candidate), False),
            'structural_candidate_untruncated': (bool(candidate), not candidate and
                 (bool(truncated) if complete else recurrence or unbounded_open)),
            'detected_and_proved': (recognizes,False),
            'reader_indefinite_recurrence': ((recurrence if complete else False),
                 (not recurrence and unbounded_open) if complete else recurrence or unbounded_open),
            'underlying_indefinite_recurrence': (recurrence,not recurrence and unbounded_open)}


def format_event(v, bounds=False):
    lo, hi = v['marginal_95_existence_envelope' if bounds else 'marginal_95_exact_certified']
    a, b = v['identification_count']
    count = f'{a}–{b}' if bounds and a != b else str(a)
    return f'{count}/{v["n"]} ({100*lo:.2f}–{100*hi:.2f}%)'


def main(markdown_output=None):
    groups=defaultdict(list)
    for line in (OUT/'draws.jsonl').open():
        row=json.loads(line)
        groups[row['supply'],row['size_group'],row['extra']].append(row)
    rates=[]
    table=[]
    for key, rows in sorted(groups.items(),key=lambda t:(t[0][0]!='original', t[0][1]!='4-8', t[0][2])):
        supply, size, extra=key
        for law in ('parity','nae'):
            for horizon in (16,32):
                for reader in ('full','witnessed_end'):
                    for denominator in ('all','legal','funded'):
                        selection=[r['laws'][law] for r in rows if denominator=='all' or r['laws'][law][denominator]]
                        counts=defaultdict(Counter)
                        widths=Counter()
                        for result in selection:
                            for name,(yes,unknown) in events(result,horizon,reader=='full').items():
                                counts[name]['yes']+=bool(yes)
                                counts[name]['unknown']+=bool(unknown)
                            for p in result['parts']:
                                widths[1]+=sum(t['certified'] is not None and t['certified']<=horizon for t in p['tip_records'])
                                if reader=='full':
                                    widths.update(v['width'] for v in p['periodic_packets'] if v['age']<=horizon)
                        summary={k:triple(v['yes'],v['unknown'],len(selection)) for k,v in counts.items()}
                        rates.append(dict(supply=supply,size=size,extra=extra,law=law,horizon=horizon,
                                reader=reader,denominator=denominator,events=summary,families_by_width=dict(sorted(widths.items()))))
                        if denominator=='all' and reader=='full':
                            name={'original':'Original','funded_sensitivity':'Demand-based'}[supply]
                            desc=f'{name} · {size} · +{extra} · '+('parity' if law=='parity' else 'not-all-equal')
                            table.append((horizon,'| '+' | '.join([desc]+[format_event(summary[s]) for s in
                                ('legal','funded','one_release_certified','structural_candidate_returned','detected_and_proved')]
                                +[format_event(summary['underlying_indefinite_recurrence'],True)])+' |'))
    (OUT/'rates.json').write_text(json.dumps(rates,indent=1)+'\n')
    parts=['# Frequency tables for the two supplies', '',
        'Each cell gives a count over all independent draws of that size weighting and its two-sided marginal 95% exact binomial interval. The last column gives the identified count interval for indefinite recurrent release under any admissible reader. Its outer sampling interval uses the lower exact limit for proved events and the upper exact limit when every unresolved draw is positive. Indicators for the two laws, two extra-meeting choices and two supplies are paired within a trial. Do not multiply the sample count by the number of laws or pool the two size weightings into one binomial interval.', '',
        'The complete data also give legal and funded denominators, both readers, the number of families of each width, the lower and upper count for each incompletely observed event and the one-sided 95% limit for a zero detector count. The event `reader_indefinite_recurrence` uses the complete through-age-32 adjudication under the named reader at either displayed horizon. The horizon-specific proof column counts a proved source whose first eligible release has already appeared. [Machine-readable rates](../../artifacts/READS-HOLDERS-SOURCES-20261120-001C/READS-HOLDERS-SOURCES-20261120-001C-E001_repeated_release/rates.json)', '']
    for h in (32,16):
        parts.extend([f'## At {h} parent steps','',
            '| Supply · original knots · added meetings · law | Legal | Funded | One or more certified releases | Candidates returned | Detected and proved | Underlying recurrent sources, including unresolved |',
            '| --- | ---: | ---: | ---: | ---: | ---: | ---: |',*[v for k,v in table if k==h],''])
    parts.extend(['Under the original supply, no complete step was capped and all tested starts have a bound on indefinitely many disjoint releases. For zero detections the one-sided 95% upper limits are 0.5834% for 512 observations, 1.1634% for 256 and 3.0724% for 96. The bounds describe their own weighting and event. They allow a positive population rate even when all sampled misses have proofs.', '',
        'The fixed end reading recognizes the same enduring one-parent tips as the complete reader in these starts. No unrestricted continuing periodic label was certified from the witnessed ends alone. The broader end-only bounds keep all five full-reading positives and every undetermined start as possible positives. In the complete data a capped unbounded part remains unresolved for the unrestricted theorem even when its first possible age for the registered candidate falls beyond the displayed horizon. A finite search found no further candidate before its cap. All family counts are distinct launches and omit any unobserved family beyond a cap.', ''])
    markdown_output = markdown_output or ROOT/'research'/OUT.parent.name/'rates.md'
    markdown_output.write_text('\n'.join(parts))


if __name__=='__main__':
    main()
