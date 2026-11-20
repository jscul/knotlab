"""Draw the registered source/first-layer comparison and the two-copy onset."""
from fractions import Fraction
from pathlib import Path
import json

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[2] / 'artifacts' / HERE.parent.name / HERE.name


def main():
    first = json.loads((DATA / 'bond_first.json').read_text())
    stages = json.loads((DATA / 'fate_series.json').read_text())['cases']
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'axes.labelcolor': '#263747', 'text.color': '#182d3b',
                         'axes.edgecolor': '#a0acb3','xtick.color': '#425563', 'ytick.color': '#425563'})
    fig, (left, right) = plt.subplots(1, 2, figsize=(10, 3.6), layout='constrained')
    for age, color, mark in [(1,'#b95224','s'),(0,'#156c71','o')]:
        row = next(r for r in first['comparisons'] if r['case']=='J1' and r['reference']=='B' and r['age']==age)
        data = row['full_balls']['5']
        offsets = sorted(int(h) for h in data if h.isdigit())
        # A uniform weighting on the source shared distinctions at each offset.
        assert all(data[str(h)]['exact']==data[str(h)]['planned'] for h in offsets)
        values = [float(Fraction(data[str(h)]['mean_signed_delta'])) for h in offsets]
        left.plot(offsets, values, marker=mark, markersize=4.5, color=color, label=f'Cluster size {age+1}', linewidth=2)
    left.axhline(0,linewidth=.7,color='#607481', zorder=0)
    left.set(title='The local change in a radius-five ball',xlabel='Source junction steps from the attachment',
             ylabel='Distinctions gained or lost vs. background')
    left.legend(frameon=False,loc='lower right');left.yaxis.set_major_locator(MaxNLocator(integer=True,nbins=5))
    for name,offset,color,mark in [('T4',4,'#156c71','o'),('T8',8,'#b95224','s')]:
        counts=stages[name]['both_exclusive_by_age'][:6]
        right.plot(range(1,7),counts,marker=mark,markersize=4.5,label=f'{offset} steps apart',color=color,linewidth=2)
        right.annotate(str(counts[-1]),(6,counts[-1]),xytext=(5,0),textcoords='offset points',color=color,va='center')
    right.set(title='Junctions formed from both rings',xlabel='Cluster size',ylabel='Junctions with a source in each ring',xticks=range(1,7),xlim=(.9,6.4))
    right.legend(frameon=False,loc='upper left')
    for ax in (left,right):
        ax.grid(axis='y',color='#dfe6e8',linewidth=.7);ax.set_axisbelow(True);ax.title.set_fontweight('semibold');ax.title.set_fontsize(12)
    fig.savefig(DATA/'world_comparison.png',dpi=160,facecolor='white')
    plt.close(fig)


if __name__=='__main__': main()
