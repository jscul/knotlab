import sys, json, random
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/f0f2b323-7667-54e0-bff8-c1ab470fc84d/scratchpad/referee_C")
from common import *
OUT = os.path.join(ROOT, "artifacts/RANDOM-FATES-20261112-001C/RANDOM-FATES-20261112-001C-E001_newest_four_count")
def load_bases():
    return [json.loads(l) for l in open(os.path.join(OUT, "bases.jsonl"))]
def regen(q, b, nmax=800):
    rng = random.Random(C.seed_of("C", q, b, "grow"))
    return C.grow_to(q, nmax, rng)
def regen_pairs(q, b):
    prng = random.Random(C.seed_of("C", q, b, "pairs"))
    out = []
    for sidx in range(C.SEQS):
        i = prng.randrange(40, 201)
        for g in C.GAPS:
            j = i + g + prng.randrange(4)
            out.append((sidx, g, i, j))
    return out
