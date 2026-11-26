"""Matched one-factor swaps on the predecessor's four-knot far end.

Reports the first eligible placement by the archived order, or the nearest
strictly far-owned member if none is linked. All comparisons keep the
receiver's initial naming and compare against their own unchanged growth.
"""
import argparse
import json
from pathlib import Path
from time import perf_counter

from growth import FAR, RECEIVER, build_pair, far_members, first_own_difference, grow, link_status, perturb, roster

HERE = Path(__file__).resolve().parent
FAR_LABEL = "n4:g16:1112@1"
CASES = [
    ("cap three, meeting", "tri:122@0", 3, "meeting", 16000),
    ("one shared distinction per join", "tri:122@0", 3, "share", 16000),
    ("cap four on the same start", "tri:122@0", 4, "meeting", 16000),
    ("ordinary count on the same start", "tri:122@0", None, "meeting", 16000),
    ("cap seven on its matched start", "tri:522@0", 7, "meeting", 16000),
]


def first_count(w, h, t):
    return next((i+1 for i in range(t, min(len(w.rows), len(h.rows)))
                 if len(w.rows[i].own_births) != len(h.rows[i].own_births)), None)


def reading(w, h, t):
    first, n = first_own_difference(w, h, t)
    return dict(hearing=first, first_count_difference=first_count(w,h,t), common_end=n,
                own_counts_at_hearing=None if first is None else
                [len(x.rows[first-1].own_births) for x in (w,h)])


def class_reading(state):
    r = roster(state)
    near = {r.part_of[u] for u in r.members if state.knots[u].roles == RECEIVER}
    far = {r.part_of[u] for u in r.members if state.knots[u].roles == FAR}
    near_d = {d for p in near for u in r.parts[p] for d in state.knots[u].places}
    far_d = {d for p in far for u in r.parts[p] for d in state.knots[u].places}
    return dict(ends_present=bool(near and far), same_part=bool(near & far),
                same_part_or_directly_sharing=bool(near & far or near_d & far_d),
                same_class=link_status(state))


def one(spec):
    name, receiver, cap, join, bound = spec
    start = build_pair(receiver, FAR_LABEL, join)
    w = grow(start, cap, rounds=16, bound=bound)
    members = far_members(w.states[3], linked=True)
    probe = members or far_members(w.states[3])
    case = dict(case=name, receiver=receiver, far=FAR_LABEL, join=join, cap=cap, bound=bound,
                rounds=len(w.rows), knots=len(w.states[-1].knots),
                first_three_readings=[class_reading(s) for s in w.states[1:4]], linked_targets=members,
                linked_at_round_16=link_status(w.states[16]) if len(w.rows)>=16 else "not read",
                changes=[])
    if not probe:
        return case
    u, s = probe[0]
    for sign in ("add","bar"):
        h = perturb(w,3,u,sign=sign)
        effect = reading(w,h,3)
        linked = [link_status(x) for x in h.states[4:]]
        rec = dict(sign=sign, knot=u, sharings=s, set_in_receiver_class=bool(members),
                   link_reading_after_round_4_on=linked, **effect)
        # A change after it has arrived, if a strictly far-owned member remains.
        heard = effect["hearing"]
        if heard and heard < len(h.rows):
            sites = far_members(h.states[heard], linked=True)
            any_sites = sites or far_members(h.states[heard])
            if any_sites:
                v, sv = any_sites[0]
                twice = perturb(h,heard,v)
                rec["after_hearing"] = dict(t0=heard,knot=v,sharings=sv,linked=bool(sites),sign="add",
                                            **reading(h,twice,heard))
            else:
                rec["after_hearing"] = "no strictly far-owned member"
        case["changes"].append(rec)
    return case


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pilot", action="store_true", help="time the first exact case")
    pilot = p.parse_args().pilot
    begin = perf_counter()
    rows = [one(spec) for spec in (CASES[:1] if pilot else CASES)]
    if not pilot:
        (HERE/"swaps.json").write_text(json.dumps(rows,indent=2)+"\n")
    print(f"{len(rows)} configurations in {perf_counter()-begin:.3f} seconds")
