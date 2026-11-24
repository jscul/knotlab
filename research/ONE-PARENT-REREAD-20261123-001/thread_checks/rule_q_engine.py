# Thread's separate engine for rule Q (not-all-equal structure rule: every birth has a fresh distinction).
# Groups come from the RECORDED operator's group rule (end_operator.proposals) on ends built here from full holdings;
# the allocation, the re-read choice, the lookahead demand and the fresh counts are this file's own code.
import sys, collections
sys.path.insert(0, 'experiments/REVIEW-LEADS-20261123-001A/REVIEW-LEADS-20261123-001A-E001_operator_test')
import lib
EO = lib.EO
class Q:
    def __init__(self, stars, conv='O', reread=True, choice=None):
        self.stars = [tuple(s) for s in stars]; self.conv = conv; self.reread = reread
        self.choice = choice          # round-1 choice: list of shared distinctions, one per re-reading birth in birth order
        self.n_at = [len(self.stars)]; self.births = []; self.outcome = None
        self.top = max(d for s in self.stars for d in s) + 1
    def holders(self):
        h = collections.defaultdict(list)
        for k, s in enumerate(self.stars):
            for d in s: h[d].append(k)
        return h
    def round(self, max_live=None):
        h = self.holders()
        loose = {k: [d for d in s if len(h[d]) == 1] for k, s in enumerate(self.stars)}
        opens = {k: len(r) for k, r in loose.items() if r}
        if not opens: self.outcome = 'closed'; return False
        if max_live is not None and len(opens) > max_live: self.outcome = 'too large for this check'; return False
        wit = collections.defaultdict(set)
        for k in opens:
            for d in self.stars[k]:
                for j in h[d]:
                    if j != k: wit[j].add(k)
        groups = EO.proposals(EO.End(opens, tuple(tuple(sorted(b)) for b in wit.values())))
        used = collections.Counter(x for g in groups for x in g)
        if any(used[k] > n for k, n in opens.items()): self.outcome = 'stall'; return False
        parents = list(groups) + [(k,) for k in sorted(opens) for _ in range(opens[k] - used[k])]
        pool = {k: list(r) for k, r in loose.items()}
        inputs = []; rr = 0; first = len(self.births) == 0
        for g in parents:
            ins = [pool[p].pop() for p in g]
            if len(g) == 1 and self.reread:
                sh = sorted(d for d in self.stars[g[0]] if len(h[d]) >= 2)
                if sh:
                    if first and self.choice is not None: d = self.choice[rr]
                    else: d = sh[0] if self.conv == 'O' else sh[-1]
                    assert d in sh
                    ins.append(d); rr += 1
            inputs.append(tuple(ins))
        # lookahead demand: every birth live with one opening; a knot witnesses the births it shares a distinction with
        nb = len(inputs); takers = collections.defaultdict(set)
        for i, ins in enumerate(inputs):
            for d in ins: takers[d].add(i)
        blocks = []
        for k, s in enumerate(self.stars):
            b = set()
            for d in s: b |= takers.get(d, set())
            if b: blocks.append(tuple(sorted(b)))
        for i, ins in enumerate(inputs):
            b = set()
            for d in ins: b |= takers[d]
            b.discard(i)
            if b: blocks.append(tuple(sorted(b)))
        look = EO.End(dict.fromkeys(range(nb), 1), tuple(blocks))
        dem = collections.Counter(x for g in EO.proposals(look) for x in g)
        row = []
        for i, ins in enumerate(inputs):
            f = max(dem[i], 3 - len(ins), 1)
            self.stars.append(tuple(ins) + tuple(range(self.top, self.top + f))); self.top += f
            row.append(dict(parents=parents[i], inputs=ins, fresh=f, reread=len(ins) > len(parents[i])))
        self.births.append(row); self.n_at.append(len(self.stars))
        return True
    def max_holders(self):
        return max(len(v) for v in self.holders().values())
