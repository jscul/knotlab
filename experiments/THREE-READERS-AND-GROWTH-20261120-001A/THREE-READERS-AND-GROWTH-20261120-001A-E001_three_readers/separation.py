"""Condition on every unread word and check product support for two and three separate readers."""
from itertools import product
from fractions import Fraction as F
from math import prod
from completions import literal,gram
from three import basic,save,behavior,literal_projectors


def run():
    stars=[[0,1,2],[2,3,4],[4,5,6]]
    out={}
    for law in ("nae","parity"):
        tests={}
        for name,parties in (("two",[[0,1],[5,6]]),("three",[[0,1],[3],[5,6]])):
            marks=sum(parties,[]); f=literal(stars,marks,law)
            den=int(f.sum());unread=sorted(set(range(7))-set(marks))
            pos=0;fields=[];qs=[]
            for p in parties:
                m=((1<<len(p))-1)<<pos
                fields.append((pos,m));qs.append([("X",m),("Z",m)])
                pos+=len(p)
            condition=[]
            for word,row in enumerate(f):
                active=[v for v,a in enumerate(row) if a]
                projections=[sorted({(v&m)>>offset for v in active}) for offset,m in fields]
                assert len(active)==prod(map(len,projections))
                condition.append(dict(unread_word=word,mass=str(F(len(active),den)),local_supports=projections))
            g=f.T @ f
            record=behavior(g,qs);assert record["rows"]==literal_projectors(f,qs) and record["common"]["local"]
            tests[name]=dict(stars=stars,parties=parties,unread=unread,conditional=condition,readings=record)
        out[law]=tests
    save("separation.json",out)
