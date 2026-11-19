"""Estimate full-stage structural totals from a mass-weighted final group of prespecified islands."""
from fractions import Fraction
from pathlib import Path
import argparse
import gzip
import json
from group_profile import Stage,summary


def run(source,roster):
    stage=Stage(roster)
    samples=json.load(gzip.open(source,'rt'))
    results=[]
    for event in samples:
        weight=Fraction(*map(int,event['island_weight']))
        ids,=event['sampled_actual_live_ids']
        row=stage.profile(ids)
        row.update(batch=event['batch'],seed=event['seed'],weight=[str(weight.numerator),str(weight.denominator)])
        results.append(row)
    def weigh(test):
        # Given the island, the draw has probability proportional to final mass.
        # Multiplying its indicator by the island's exact normalization gives
        # an unbiased unnormalized total over all maximal groups.
        total=sum((Fraction(*map(int,r['weight'])) for r in results if test(r)),Fraction())/len(results)
        return dict(observed=sum(test(r) for r in results),exact_weighted_total=[str(total.numerator),str(total.denominator)],
                    weighted_total=float(total))
    marks={'all':lambda r:True,'unheld_large':lambda r:r['largest_single']<r['size'] and r['size']>=3,
           'three_blocks_needed':lambda r:r['cover_up_to_two'] is None,
           'individually_below_three_quarters':lambda r:4*r['partner_upper']<3*r['size'],
           'witnessed_three_quarters':lambda r:4*r['partner_lower']>=3*r['size']}
    return dict(weighting="One group drawn in proportion to final particle mass from the predetermined first island of each independent batch. An indicator times that island's exact total estimates its stage-wide marked count.",
                draws=len(results),summary=summary(results),marks={k:weigh(fn) for k,fn in marks.items()},rows=results)


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('roster',type=Path)
    ap.add_argument('data',type=Path,nargs='+');ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    value={d.name:run(d,args.roster) for d in args.data}
    args.out.write_text(json.dumps(value,indent=1)+'\n')
    for k,v in value.items():print(k,v['summary'],flush=True)
