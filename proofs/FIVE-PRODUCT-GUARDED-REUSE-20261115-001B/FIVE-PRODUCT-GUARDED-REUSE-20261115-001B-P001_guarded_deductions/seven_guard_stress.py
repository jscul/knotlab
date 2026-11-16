"""Run the six-guard construction one rank higher on the original seven-product path."""
from itertools import product
from terminal_library import affine_span

rows = set(range(2048))
def bit(x,i):
    return x>>i&1
def data(x):
    t = x & (x>>1) & 127
    q = t.bit_count()%2
    matches = bit(x,9)==bit(t,0) and bit(x,10)==(bit(t,1)^bit(t,2))
    return q,matches

def values(x):
    d = bit(x,1)^bit(x,3)
    y = (bit(x,4),bit(x,6))
    z = bit(x,8) ^ (y[0] & (bit(x,3)^bit(x,5))) ^ (y[1] & (bit(x,5)^bit(x,7)))
    h = d^bit(x,9)
    a = d if h else z^bit(x,3)
    return y,d,z,h,a
def guard(x,c,i):
    y,d,z,h,a = values(x)
    return y == c and (bit(x,3)==z==0, bit(x,1)==1 and z==bit(x,0), d==1 and z==bit(x,2))[i]
def replay():
    left = {x for x in rows if data(x)[1] and bit(x,8)==data(x)[0]}
    right = {x for x in rows if bit(x,8)!=data(x)[0]}
    library = {(c,i):{x for x in rows if guard(x,c,i)}
               for c in product(range(2),repeat=2) for i in range(3)}
    counts=set()
    for g in library.values():
        assert not affine_span(g & right) & left
        counts.add(len(g & left))
    assert counts=={24}
    for c in product(range(2),repeat=2):
        for h,a in product(range(2),repeat=2):
            leaf={x for x in rows if (values(x)[0],*values(x)[3:])==(c,h,a)}
            assert leaf & left and leaf & right
            assert leaf & left <= library[c,((0,1),(1,2))[h][a]]
    assert len(left)==256 and set.union(*(g & left for g in library.values()))==left
    return {"visible_rows":len(rows),"honest_inputs":len(left),"terminal_applications":16,
            "distinct_guards":len(library),"largest_honest_support":max(counts),
            "lower_bound_on_distinct_guards":(len(left)+24-1)//24}


if __name__ == "__main__":
    import json
    print(json.dumps(replay(),sort_keys=True))
