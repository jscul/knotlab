"""Independent labelled Prüfer census and exact decorated free-tree multiplicities."""

from argparse import ArgumentParser
from collections import Counter
from itertools import permutations, product
from math import comb, factorial, prod
from pathlib import Path
import gzip
import json
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / 'artifacts' / HERE.parent.name / HERE.name


def save(name, data):
    OUTPUT.mkdir(exist_ok=True, parents=True)
    payload = (json.dumps(data, separators=(',', ':'), sort_keys=True) + '\n').encode()
    (OUTPUT / name).write_bytes(gzip.compress(payload, mtime=0) if name.endswith('.gz') else payload)


def adjacency(n, edges):
    neighbors = [[] for _ in range(n)]
    for u, v in edges:
        neighbors[u].append(v)
        neighbors[v].append(u)
    return neighbors


def colored_code(neighbors, extra):
    """Minimize recursively sorted rooted words; count permutations fixing a minimal root."""
    def visit(u, previous):
        child = [visit(v, u) for v in neighbors[u] if v != previous]
        child.sort()
        types = Counter(code for code, aut in child)
        aut = prod(factorial(k) for k in types.values()) * prod(a for code, a in child)
        return '(' + str(extra[u]) + ''.join(code for code, a in child) + ')', aut
    roots = [visit(u, -1) for u in range(len(neighbors))]
    best = min(code for code, aut in roots)
    equivalent = [aut for code, aut in roots if code == best]
    assert len(set(equivalent)) == 1
    return best, equivalent[0]*len(equivalent)


def leaf_generated_shapes(n):
    """Attach a leaf at every old vertex, quotienting only exact unrooted codes."""
    tree = [()]
    for size in range(2, n+1):
        following = {}
        for old in tree:
            for u in range(size-1):
                edges = (*old,(u, size-1))
                code, _ = colored_code(adjacency(size,edges), (0,)*size)
                following.setdefault(code, edges)
        tree = list(following.values())
    return tree


def prufer_edges(word, n):
    occurrences = [1]*n
    for t in word:
        occurrences[t] += 1
    for v in word:
        leaf = occurrences.index(1)
        yield leaf, v
        occurrences[leaf] -= 1
        occurrences[v] -= 1
    a,b = (u for u,degree in enumerate(occurrences) if degree==1)
    yield a,b


def colored_support(n):
    names = range(n)
    count = n**(n-2)
    location = [[0]*n for _ in names]
    for a in names:
        for b in range(a):
            location[a][b] = location[b][a] = 1 << ((a*(a-1))//2+b)
    classes = {}
    tree_to_shape = {}
    for shape in leaf_generated_shapes(n):
        neighbors = adjacency(n,shape)
        code, aut = colored_code(neighbors,(0,)*n)
        images = Counter()
        for perm in permutations(names):
            mask = sum(location[perm[u]][perm[v]] for u,v in shape)
            images[mask] += 1
        assert len(images)==factorial(n)//aut and set(images.values())=={aut}
        assert not images.keys() & tree_to_shape.keys()
        for mask in images:
            tree_to_shape[mask]=code
        decorated_masks = Counter()
        rooted_orders = {}
        for flag in product((0,1),repeat=n):
            key, symmetry = colored_code(neighbors,flag)
            decorated_masks[key] += 1
            rooted_orders[key] = (symmetry,sum(flag))
        records = {}
        for key, m in decorated_masks.items():
            sym, k = rooted_orders[key]
            assert m*sym == aut
            labelled = len(images)*m
            assert labelled == factorial(n)//sym
            records[key] = {"extra_count":k,"symmetry":sym,"labelled":labelled,"quarter_mass_numerator":labelled*3**(n-k)}
        per_k = Counter()
        for x in records.values():
            per_k[x["extra_count"]]+=x["labelled"]
        assert all(per_k[k]==len(images)*comb(n,k) for k in range(n+1))
        classes[code] = {"representative":shape,"symmetry":aut,"labelled_uncoloured":len(images),"decorated":records}
    assert len(tree_to_shape)==count
    observed = Counter()
    actual = set()
    for word in product(names,repeat=n-2):
        domain = sum(location[u][v] for u,v in prufer_edges(word,n))
        assert domain not in actual
        actual.add(domain)
        observed[tree_to_shape[domain]]+=1
    assert len(actual) == count and actual == tree_to_shape.keys()
    assert all(observed[code] == data["labelled_uncoloured"] for code,data in classes.items())
    per_k = Counter()
    total_quarter = 0
    for shape in classes.values():
        for x in shape["decorated"].values():
            per_k[x["extra_count"]]+=x["labelled"]
            total_quarter+=x["quarter_mass_numerator"]
    assert all(per_k[k] == count*comb(n,k) for k in range(n+1))
    assert total_quarter == count*4**n
    return {"n":n,"distinct_labelled_prufer_words":count,"labelled_trees_and_binary_masks":count*2**n,
            "quarter_denominator":total_quarter,"labelled_pairs_by_extra_count":per_k,
            "uncoloured_tree_classes":len(classes),"decorated_tree_classes":sum(len(x["decorated"]) for x in classes.values()),
            "shapes":classes}


def main():
    parser=ArgumentParser()
    parser.add_argument('--sizes',nargs='+',type=int,default=list(range(4,9)))
    args=parser.parse_args()
    for n in args.sizes:
        started=time.monotonic()
        data=colored_support(n)
        save(f'multiplicities_{n}.json.gz',data)
        print(n,data['distinct_labelled_prufer_words'],data['decorated_tree_classes'],round(time.monotonic()-started,3),flush=True)


if __name__=='__main__':
    main()
