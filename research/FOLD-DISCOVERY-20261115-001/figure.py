"""Plot the bound supplied and learned experiments from their saved receipts."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

ROOT=Path(__file__).resolve().parents[2]
def folder(ticket,slug):
    return ROOT/'artifacts'/ticket/(ticket+'-E001_'+slug)
p1=folder('FOLD-DEPTH-20261115-001','supplied_fold')
p2=folder('FOLD-DISCOVERY-20261115-001','learned_library')
s1=json.loads((p1/'result.json').read_bytes())
s2=json.loads((p2/'result.json').read_bytes())
fig,(left,right)=plt.subplots(1,2,figsize=(10.3,3.6),layout='constrained',gridspec_kw={'width_ratios':[1.05,1]})
for kind,title,color,style in [('positive','Operation recurs','#006a63','o-'),('negative','One occurrence changed','#a45433','s--')]:
    values=[s1['tables']['primary']['cold'][f'{d}-{kind}']['pair_savings']['tests']['fraction']
            for d in (2,3,4)]
    left.plot([2,3,4],values,style,color=color,label=title,lw=2,ms=6)
left.axhline(0,lw=1,color='#353938')
left.set(xlabel='Number of nested operations',ylabel='Search trials saved vs primitives',
         xticks=[2,3,4],xlim=(1.85,4.15),ylim=(-.78,.53),title='Supplied fold on matched rules')
left.yaxis.set_major_formatter(PercentFormatter(xmax=1,decimals=0))
left.legend(frameon=False,fontsize=9,loc='lower right')
cells=s2['totals']['warm']
labels=['Primitive','Learned fold']
spent=[cells[a]['acquisition_ns']/1e6 for a in ('primitive','learned')]
deployed=[cells[a]['downstream_ns']/1e6 for a in ('primitive','learned')]
right.barh(labels,spent,color='#967438',label='Discovery and training',height=.48)
right.barh(labels,deployed,left=spent,color='#266f81',label='Held search, checks and setup',height=.48)
for i,(x,y) in enumerate(zip(spent,deployed)):
    right.text(x+y+1.0,i,f'{x+y:.1f}',va='center',fontsize=10)
right.invert_yaxis()
right.set(xlabel='Total time (ms)',xlim=(0,73),title='Frozen library on 24 unseen rules')
right.legend(frameon=False,fontsize=8.5,loc='lower right',bbox_to_anchor=(1,-.37))
for ax in (left,right):
    ax.spines[['top','right']].set_visible(False)
    ax.title.set_fontweight('bold')
    ax.set_axisbelow(True)
left.grid(axis='y',alpha=.17)
right.grid(axis='x',alpha=.17)
fig.savefig(p2/'fold-scaling.png',dpi=160)
