"""Rebuild the food, movement and energy ledgers from an actual spectator record."""
from collections import Counter
from dataclasses import replace
import json
from pathlib import Path
import sys

from game import Game, action_rngs
from world import sample_world


def audit(trace):
    world = sample_world(trace["seed"],trace["law"],rounds=2)
    holdings = [set(row) for row in trace["initial_holdings"]]
    assert holdings == list(map(set,world.stages[0].holdings))
    position = trace["start_holder"]
    assert 0 <= position < len(holdings)
    bank, eaten = set(),set()
    energy,meals,overflow = 6,0,0
    previous = "start"
    for turn,row in enumerate(trace["events"],1):
        assert energy > 0 and turn == row["turn"]
        packet = row["growth"]
        index = {1:0,5:1}.get(turn)
        expected = world.attempts[index] if index is not None and index<len(world.attempts) else None
        assert (packet is not None) == (expected is not None)
        if packet is not None:
            assert packet["status"] == expected.status and packet["formation"] == expected.stage
            assert len(packet["births"]) == len(expected.births)
            for born,actual in zip(packet["births"],expected.births,strict=True):
                h = born["holder"]
                assert h == len(holdings) == actual.holder
                assert born["payments"] == [list(p) for p in actual.payments]
                assert born["grants"] == list(actual.grants) and born["demand"] == actual.demand
                assert all(mark in holdings[p] for p,mark in born["payments"])
                assert set(born["holdings"]) == set(world.stages[expected.stage].holdings[h])
                holdings.append(set(born["holdings"]))
                assert h not in bank|eaten
                bank.add(h)
        owned = Counter(mark for h in holdings for mark in h)
        assert max(owned.values()) <= 2
        degree = sum(owned[mark]==2 for mark in holdings[position])
        food = position in bank
        assert row["holder_before"] == position and row["energy_before"] == energy
        assert row["food_before"] is food and row["previous"] == previous
        assert row["food_sensor"] is (food if trace["sensor_enabled"] else None)
        assert row["available_slots"] == degree
        paid = row["action"] == "eat" and food
        assert row["consumed"] is paid
        if row["action"] == "move":
            other,mark = row["holder_after"],row["distinction"]
            assert other != position and 0<=row["slot"]<degree
            assert mark in holdings[position] and mark in holdings[other] and owned[mark]==2
            position = other
        else:
            assert row["action"]=="eat" and row["holder_after"]==position and row["slot"] is None
            if paid:
                assert position not in eaten
                bank.remove(position)
                eaten.add(position)
                meals+=1
        gross = energy-1+4*paid
        overflow += max(0,gross-10)
        energy=min(gross,10)
        assert row["wasted"]==max(0,gross-10) and row["energy_after"]==energy
        assert row["rations_remaining"]==len(bank) and row["terminal"] is (energy==0)
        previous = row["action"]
    assert energy == trace["energy"] == 0
    assert trace["reason"]=="death" and len(trace["events"])==trace["turns"]==6+4*meals-overflow
    assert trace["meals"]==meals and trace["wasted"]==overflow
    return trace["turns"]


def transported(world):
    """Consistently reverse all distinction names; holders retain their identities."""
    bound=max(n for s in world.stages for h in s.holdings for n in h)
    def names(row):
        return tuple(bound-n for n in row)
    def birth(b):
        return replace(b,payments=tuple((h,bound-d) for h,d in b.payments),grants=names(b.grants))
    stages=tuple(replace(s,holdings=tuple(map(names,s.holdings)),loose=tuple(map(names,s.loose)),
                         links=tuple(tuple((bound-d,h) for d,h in links) for links in s.links))
                 for s in world.stages)
    attempts=tuple(replace(a,births=tuple(map(birth,a.births))) for a in world.attempts)
    return replace(world,stages=stages,attempts=attempts,births=tuple(map(birth,world.births))),bound


def mechanics_checks():
    from policies import get_policy
    for law in ("parity","nae"):
        world=sample_world(3,law,rounds=2)
        recoded,bound=transported(world)
        a,b=Game(world),Game(recoded)
        moving=0
        while not a.done:
            obs=a.observe()
            assert obs==b.observe()==a.observe()
            choice=get_policy("sensing")(obs,*action_rngs(0,a.turns+1))
            counterpart=choice
            if choice:
                mark,other=a._local_ports()[choice-1]
                counterpart=b._local_ports().index((bound-mark,other))+1
                moving+=1
            u,v=a.step(choice),b.step(counterpart)
            for field in ("holder_after","consumed","food_sensor","energy_after","terminal"):
                assert u[field]==v[field]
        assert b.done and moving
        fresh=Game(world)
        before=fresh.observe()
        try:
            fresh.step(len(before.slots)+1)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid move was accepted")
        assert fresh.observe()==before and fresh.turns==0
        assert fresh.available.isdisjoint(set(range(len(world.stages[0].holdings))))
        # A paid empty eat at energy one kills. A meal from energy one survives.
        fresh.energy=1
        assert fresh.step(0)["terminal"]
        for initial,ending in ((1,4),(10,10)):
            fresh=Game(world)
            fresh.observe()
            fresh.holder=min(fresh.available)
            fresh.energy=initial
            assert fresh.step(0)["energy_after"]==ending
            assert fresh.observe().food is False
            turn=fresh.step(0)
            assert not turn["consumed"] and turn["energy_after"]==ending-1
    print("Energy, irreversible consumption, reset, illegal ports and transported moves passed under both laws.")


if __name__=="__main__":
    mechanics_checks()
    for filename in sys.argv[1:]:
        print(filename,audit(json.loads(Path(filename).read_bytes())),"turns verified")
