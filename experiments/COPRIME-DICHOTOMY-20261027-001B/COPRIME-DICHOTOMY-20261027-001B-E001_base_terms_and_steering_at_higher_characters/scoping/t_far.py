import sys, glob
import numpy as np
S = "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/6694d27d-4771-575f-adbb-a5c8aaccce97/scratchpad"
ROOT = "/home/jscul/p-vs-np-contact-first"
sys.path.insert(0, S + "/cdB")
sys.path.insert(1, glob.glob(ROOT + "/proofs/COPRIME-DICHOTOMY-20261027-001A/*P001_*")[0])
sys.path.insert(2, glob.glob(ROOT + "/experiments/TRIPLE-SYSTEM-20261027-001B/*E001_*")[0])
sys.path.insert(3, glob.glob(ROOT + "/proofs/COPRIME-CLASS2-20261026-001B/*P001_*")[0])
import gd
from cd_lib import free_graded, pair_failures, triple_failures
for (p, d, gens, c) in [(7, 6, [1, 5, 3], 3), (7, 6, [1, 5, 3], 4), (13, 12, [1, 11, 4, 8], 3), (13, 4, [1, 3, 2], 4), (11, 10, [2, 8, 5, 3], 3)]:
    F = free_graded(p, d, gens, c)
    Q = gd.p2_quotient(F)
    tf = triple_failures(Q)
    far = [(a, b) for (a, b) in tf if b % d not in (a % d, (-a) % d)]
    print(p, d, gens, c, "dim", F.D, "->", Q.D, "pairs", pair_failures(Q), "triples", tf, "far", far)
