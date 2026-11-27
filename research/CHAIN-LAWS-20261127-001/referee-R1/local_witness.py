"""Directly count complete assignments for one frozen pass spoiled by a stage bond."""
import argparse
import gzip
from itertools import combinations, product
import json
from pathlib import Path
from time import perf_counter

HERE = Path(__file__).resolve().parent
REFERENCE = ((3,4,5), (11,12,13), (0,1,10), (6,15,16), (7,8,9), (2,14))
CLAUSES = ((0,2,4), (0,3,5), (1,2,5), (1,3,4))
TRIPLES = tuple(product((0,1), repeat=3))


def chain_readings(supports, chain):
    knots = [set(supports[k]) for k in chain]
    shared = [next(iter(a & b)) for a,b in zip(knots,knots[1:])]
    labels = []
    for j, knot in enumerate(knots):
        labels.extend(sorted(knot - set(shared)))
        if j < 7:
            labels.append(shared[j])
    return tuple(tuple(sorted(labels[i] for i in carrier)) for carrier in REFERENCE)


class Assignments:
    """One bit for every assignment, with actual stage identities compressed in order."""
    def __init__(self, supports):
        self.supports = supports
        self.names = sorted(set().union(*supports))
        nbits = 1 << len(self.names)
        self.full = (1 << nbits)-1
        self.columns = {}
        for i, name in enumerate(self.names):
            if i < 3:
                pattern = bytes(((0xaa,0xcc,0xf0)[i],))
            else:
                n = 1 << (i-3)
                pattern = bytes(n) + bytes([255])*n
            self.columns[name] = int.from_bytes(pattern*(nbits//8//len(pattern)), "little")
        self.valid = self.full
        self.fixes = []
        for law in supports:
            self.valid &= ~self.agreement(tuple(law))
        for law in supports:
            blocks = [self.valid]
            for name in law:
                col = self.columns[name]
                blocks = [piece for b in blocks for piece in (b & col, b & ~col) if piece]
            self.fixes.append(blocks)

    def agreement(self, group):
        head = self.columns[group[0]]
        result = self.full
        for name in group[1:]:
            result &= ~(self.columns[name] ^ head)
        return result

    def free_fixes(self, reading):
        return [sum(bool(fix & reading) and bool(fix & ~reading) for fix in choices)
                for choices in self.fixes]

    def counts(self, columns):
        fibres = [self.valid]
        for col in columns:
            fibres = [sub for f in fibres for sub in (f & ~col, f & col)]
        return [f.bit_count() for f in fibres]

    def search(self, chain):
        groups = chain_readings(self.supports,chain)
        cols = [self.agreement(g) for g in groups]
        pairs = [cols[i:i+2] for i in (0,2,4)]
        local = [self.free_fixes(read) for read in cols]
        lower = [self.counts([cols[i] for i in t]) for t in CLAUSES]
        upper = [self.counts([a & b if j==both else a | b for j,(a,b) in enumerate(pairs)]) for both in range(3)]
        if not (all(all(ns[:7]) and ns[7]==0 for ns in lower+upper) and all(min(x)>0 for x in local)):
            return
        for slot in range(3):
            rest = sorted(set(self.names)-set(groups[2*slot])-set(groups[2*slot+1]))
            for size in (2,3):
                for third in combinations(rest,size):
                    z = self.agreement(third)
                    counts = self.counts([*pairs[slot],z])
                    observed = [word for word,n in zip(TRIPLES,counts) if n]
                    if len(observed)==8 or any(len({(w[a],w[b]) for w in observed}) < 4 for a,b in combinations(range(3),2)):
                        continue
                    fixes = self.free_fixes(z)
                    if min(fixes)>0:
                        return dict(source_states=self.valid.bit_count(),supports=self.supports,
                                    chain=chain,carriers=groups,defining_counts_000_to_111=lower,
                                    upper_counts_000_to_111_by_both_role=upper,
                                    pair_index=slot,third_carrier=third,bond_counts_000_to_111=counts,
                                    fixed_source_knot_values_permitting_both_values=[
                                        local[2*slot],local[2*slot+1],fixes])
        return None


def main():
    arg = argparse.ArgumentParser(description=__doc__)
    arg.add_argument("--pilot", action="store_true")
    pilot = arg.parse_args().pilot
    begin = perf_counter()
    attempted = 0
    witness = None
    with gzip.open(HERE/"step_stages.jsonl.gz","rt") as f:
        for line in f:
            row = json.loads(line)
            if len(set().union(*row["supports"])) > 20:
                continue
            attempted += 1
            s = Assignments(row["supports"])
            for j,ch in enumerate(row["chains"][:3]):
                w = s.search(ch)
                if w:
                    witness = dict(stage=row["id"],chain_ordinal=j+1,**w)
                    break
            if witness or pilot:
                break
    if witness:
        with gzip.open(HERE/"step_incidence.jsonl.gz","rt") as f:
            witness["census_occurrences"] = [rec for line in f if (rec:=json.loads(line))["stage"]==witness["stage"]]
    if not pilot:
        assert witness is not None
    from growth import load_census, stage_rows
    prior = HERE.parent.parent/"CLOSED-BY-CUTS-20261127-001"/"referee-R1"/"changed_reading_check.json"
    recorded = json.loads(prior.read_text())
    roster = load_census()
    named = {}
    # Start with one arm in the pilot. This is a fixed earlier witness,
    # separate from the stage search and from the full-census frequencies.
    for arm in (("one_fewer",) if pilot else ("ordinary","one_fewer","arity_floor")):
        stage = next(s for s in stage_rows(roster[recorded["census_index"]],arm)
                     if s.round == recorded["round"])
        s = Assignments(stage.supports)
        readings = [s.agreement(c) for c in recorded["carrier_order"]]
        image = s.counts([readings[0] & readings[1], readings[2] | readings[3], readings[4] | readings[5]])
        expected = recorded["ordinary_upper_counts"] if arm == "ordinary" else recorded["cut"]["upper_counts"]
        assert image == [expected.get("".join(map(str,w)),0) for w in TRIPLES]
        named[arm] = dict(chains=len(stage.chains), states=s.valid.bit_count(), upper_counts_000_to_111=image)
    obj = dict(search="First three chains on stages of up to 20 distinctions in the replay order; stop at first witness.",
               pilot=pilot, stages_inspected=attempted, witness=witness,
               prior_five_knot_census_entry=recorded["census_index"], prior_witness_round=recorded["round"],
               prior_carriers=recorded["carrier_order"], prior_matched_witness=named, seconds=round(perf_counter()-begin,3))
    (HERE/("local_pilot.json" if pilot else "local_witness.json")).write_text(json.dumps(obj,indent=2)+"\n")
    print("stages searched", attempted, "witness",bool(witness),"seconds",obj["seconds"])


if __name__ == "__main__":
    main()
