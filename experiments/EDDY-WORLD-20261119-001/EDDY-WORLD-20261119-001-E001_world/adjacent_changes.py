"""Check availability of a local state shift; the growth law selects no shift."""
from collections import defaultdict, deque
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[2] / 'artifacts' / HERE.parent.name / HERE.name


def steps_to(start, adjacency):
    dist = {start:0}
    todo = deque([start])
    while todo:
        v = todo.popleft()
        for w in adjacency[v]:
            if w not in dist:
                dist[w] = dist[v]+1
                todo.append(w)
    return dist


def main():
    stages = json.loads((DATA/'stages.json').read_text())['cases']['J1']['stages']
    previous = None
    fixed = {}
    for age in range(1,len(stages)):
        stars = stages[str(age)]['stars']
        owners = defaultdict(list)
        for j,row in enumerate(stars):
            for name in row:
                owners[name].append(j)
        meetings = {}
        adj = [set() for _ in stars]
        for name,holding in owners.items():
            if len(holding)==2:
                u,v = holding
                meetings[u,v] = meetings[v,u] = name
                adj[u].add(v)
                adj[v].add(u)
        left,right = (steps_to(v,adj) for v in [0,16])
        pulses = []
        for i in [6,7,8]:
            witness, = (adj[i] & adj[i+2]) - {i+1}
            square = [i,i+1,i+2,witness]
            support = {meetings[u,v] for u,v in zip(square,square[1:]+square[:1])}
            assert len(support)==4
            assert all(len(support.intersection(row))%2==0 for row in stars)
            pulses.append(support)
            assert (min(left[v] for v in square),min(right[v] for v in square)) == (i,14-i)
        moves = [v.symmetric_difference(w) for v,w in zip(pulses,pulses[1:])]
        assert all(len(change)==6 and all(len(change.intersection(s))%2==0 for s in stars) for change in moves)
        signature = [sorted(p) for p in pulses]
        if previous is not None: assert signature==previous
        previous=signature
        if not fixed:
            fixed = {'four_distinction_states':signature, 'successive_state_changes':[sorted(s) for s in moves],
                     'junction_steps_to_landmarks':[[6,8],[7,7],[8,6]]}
    fixed.update(case='J1',physical_cluster_sizes_checked=list(range(2,len(stages)+1)),
                 interpretation='Each state and each local change is allowed. There is no specified state-update rule.')
    (DATA/'adjacent_changes.json').write_text(json.dumps(fixed,indent=2)+'\n')
    print('Two six-distinction changes between three allowed localized states, replayed at every positive J1 stage.')


if __name__=='__main__': main()
