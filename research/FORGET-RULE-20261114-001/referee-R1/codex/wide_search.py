"""Additional A79 two-definition grid: finite helpers with3..6 ports."""
import argparse,random
import search_counterexamples as S


def wide(seed,count):
    rng=random.Random(seed)
    for j in range(count):
        k=rng.randint(3,6);own=rng.randint(0,6);n=k+own
        body=[['K',rng.sample(range(n),3)] for _ in range(rng.randint(1,9))]
        if k==3 and j%3==0:body.append(['SELF',rng.sample(range(n),3)])
        helper=[k,own,body]
        local=rng.randint(k-3,6);n=3+local;calls=[]
        for _ in range(rng.randint(0,10)):
            callee=rng.choice(['K','K',0,0,'SELF'])
            calls.append([callee,rng.sample(range(n),k if callee==0 else 3)])
        if not any(c=='SELF' for c,a in calls):calls.append(['SELF',rng.sample(range(n),3)])
        yield 'random_two_defs_helper_ports3to6_seed'+str(seed),[helper,[3,local,calls]]

if __name__=='__main__':
    S.f_targeted=lambda seed,count:[]
    S.random_families=wide
    S.run(argparse.Namespace(mode='random',seed=20261116,count=50000,seconds=600,states=10000,name='wide_search',stop_first=False))
