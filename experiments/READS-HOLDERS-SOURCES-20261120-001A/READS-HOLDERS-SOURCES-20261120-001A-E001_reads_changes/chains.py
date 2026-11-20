"""All midpoint outcomes on finite chains. The two end readers each keep two distinctions."""
from fractions import Fraction
from itertools import product
import numpy as np
from operations import LAW, parity, mask, save


def score_two(ex,ez,exz):
    agree=(2*ex+2*ez+ex*ex+ez*ez+2*ex*ez+exz*exz)
    return (9+agree)/18


def chain(length,law):
    # End basis [v0, u1, vL, uL]; then all shared v_i followed by all interior u_i.
    v=[0,*range(4,4+length-1),2]
    u=[1,*range(4+length-1,4+2*length-3),3]
    stars=[[v[i],u[i],v[i+1]] for i in range(length)]
    width=2*length+1;hidden=width-4
    inds=np.arange(1<<width,dtype=np.uint32)
    state=np.ones(len(inds),dtype=np.int64)
    for row in stars:
        word=inds & mask(row)
        if law=="parity":
            state*=1^(((word>>row[0])^(word>>row[1])^(word>>row[2]))&1).astype(np.int64)
        else:
            state*=((word!=0)&(word!=mask(row)))
    total=int(state.sum()); assert total>0
    joined=length-1; answer={}
    for protocol,nx in (("change_shared_read_loose",joined),("all_changes",hidden)):
        vectors=state.reshape(-1,16).copy()
        for h in range(nx):
            vview=vectors.reshape(-1,2,1<<h,16)
            even=vview[:,0].copy();odd=vview[:,1].copy()
            vview[:,0]=even+odd;vview[:,1]=even-odd
        norms=(vectors*vectors).sum(1)
        assert int(norms.sum())==total*(1<<nx)
        signs=np.array([1-2*parity(i) for i in range(16)],dtype=np.int64)
        sx=(vectors*vectors[:,np.arange(16)^5]).sum(1)
        sz=(vectors*vectors*signs).sum(1)
        sxz=(vectors*vectors[:,np.arange(16)^5]*signs).sum(1)
        rec=[]; agg={key:[0,0,0] for key in ("neither","join_only","loose_only","both")}
        perfect_mass=0;perfect_records=0
        for h,(n,a,b,c) in enumerate(zip(norms,sx,sz,sxz)):
            n,a,b,c=map(int,(n,a,b,c));j=parity(h & ((1<<joined)-1));l=parity(h>>joined)
            rec.append([n,a,b,c])
            if n and abs(a)==n and abs(b)==n and c*n==a*b:
                perfect_mass+=n;perfect_records+=1
            for tag,en_j,en_l in (("neither",0,0),("join_only",1,0),("loose_only",0,1),("both",1,1)):
                x=1-2*(j*en_j);z=1-2*(l*en_l)
                for k,d in enumerate((a*x,b*z,c*x*z)):
                    agg[tag][k]+=d
        sums={}
        den=int(norms.sum())
        for tag,vals in agg.items():
            ex,ez,exz=[Fraction(v,den) for v in vals]
            sums[tag]=dict(joint_expectations=list(map(str,(ex,ez,exz))),two_copy_game=str(score_two(ex,ez,exz)))
        answer[protocol]=dict(records=rec,record_columns=["unnormalized mass","joint X signed mass","joint Z signed mass","joint XZ signed mass"],
                              denominator=den,possible_records=int(np.count_nonzero(norms)),all_records=len(norms),
                              correctable_records=perfect_records,correctable_probability=str(Fraction(perfect_mass,den)),messages=sums)
    return dict(length=length,stars=stars,allowed_words=total,end_order=["v0","u1","vL","uL"],outcomes=answer)


def run():
    save("chains.json",{law:{k:chain(k,law) for k in (2,4,8)} for law in LAW})
