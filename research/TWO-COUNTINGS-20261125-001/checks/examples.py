import json, sys
sys.path.insert(0,'.')
from fractions import Fraction as Fr
from myscore import weights, joint, score, change
S=json.load(open('REPO_ROOT/research/TWO-COUNTINGS-20261125-001A/structures.json'))
E=[(l,tuple(p)) for l,p in S['eleven (start)']]
opt={0:'x2',1:'x3'}; optb={0:'y2',1:'y3'}
def run(name, mk, recA, recB):
    Ps={}; kept={}
    for a in (0,1):
        for b in (0,1):
            stages=mk(a,b)
            o,st,W,tot=weights(stages,0)
            Ps[(a,b)]=joint(o,st,W,recA,recB); kept['%d%d'%(a,b)]=str(tot)
    sc=score(Ps)
    # changes separately
    from myscore import marg, tv
    c1=max(tv(marg(Ps[(a,0)],0),marg(Ps[(a,1)],0)) for a in (0,1))
    c2=max(tv(marg(Ps[(0,b)],1),marg(Ps[(1,b)],1)) for b in (0,1))
    print(name, 'score', sc, 'change first', c1, 'second', c2, 'kept', kept)
RA=('x1','x2','x3','za'); RB=('y1','y2','y3','zb')
run('E0', lambda a,b: [E, [('nae',('x1',opt[a],'za')),('nae',('y1',optb[b],'zb'))]], RA, RB)
run('E3', lambda a,b: [E, [('nae',('x1',opt[a],'s1')),('nae',('y1',optb[b],'zb'))]], ('x1','x2','x3','s1'), RB)
run('E4', lambda a,b: [E, [('nae',('x1',opt[a],'z')),('nae',('y1',optb[b],'z'))]], ('x1','x2','x3','z'), ('y1','y2','y3','z'))
run('E5', lambda a,b: [E, [('nae',('x1',opt[a],'za')),('nae',('y1',optb[b],'zb'))], [('even',('za','zb','x1'))]], RA, RB)
run('E6', lambda a,b: [E, [('nae',('x1',opt[a],'za')),('nae',('y1',optb[b],'zb'))]], ('x1','x2','x3','zb'), RB)
run('E7', lambda a,b: [E, [('nae',('x1',opt[a],'za')),('nae',('y1',optb[b],'zb'))], [('even',('zb','w','x1'))]], ('x1','x2','x3','w'), RB)
