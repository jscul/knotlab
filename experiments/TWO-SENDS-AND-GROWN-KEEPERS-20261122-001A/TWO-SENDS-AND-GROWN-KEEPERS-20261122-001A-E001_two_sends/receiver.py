"""Enabled local actions and receiver-only decoders for the two physical sends."""
from collections import Counter
from dataclasses import dataclass

from substrate import allowed, mask, memberships, read


@dataclass(frozen=True)
class Action:
    actor: int
    kind: str
    swaps: tuple
    sensing: tuple


def exchange(word, pairs):
    for a, b in pairs:
        if ((word >> a) ^ (word >> b)) & 1:
            word ^= (1 << a) | (1 << b)
    return word


def sender_offer(word, device, offer):
    # The intervention is an argument solely to the chosen original sender.
    if read(word, device.offer) == '100':
        return Action(device.source, 'offer', ((device.offer[0], device.offer[offer]),), device.offer)


def relay_action(word, device, conditional):
    offer = read(word, device.offer)
    stage = read(word, device.stage)
    receipt = read(word, device.receipt)
    if receipt != '100' or offer not in ('010', '001'):
        return None
    targets = device.receipt
    guard = device.offer + device.stage + targets
    if stage == '10':
        mid = conditional and offer == '001'
        i = 1 if mid else 2
        return Action(device.witness, 'issue_mid' if mid else 'issue_end',
                      ((targets[0], targets[i]), device.stage), guard)
    if stage == '01' and conditional and offer == '001':
        return Action(device.witness, 'issue_end', ((targets[0], targets[2]),), guard)
    return None


def acknowledge(word, device):
    if read(word, device.receipt) == '010' and read(word, device.memory) == '10':
        return Action(device.receiver, 'acknowledge',
                      ((device.receipt[0], device.receipt[1]), device.memory), device.receipt + device.memory)


def sample(word, device):
    return read(word, device.receipt + device.memory)


def decode_memory(transcript):
    """A rising third receipt mark, followed by a read of the two local memory marks."""
    if not transcript or transcript[0] != '10010':
        return None
    memory_seen = False
    for index, row in enumerate(transcript):
        if len(row) != 5 or row[:3] not in ('100', '010', '001') or row[3:] not in ('10', '01'):
            return None
        if memory_seen and row[3:] != '01':
            return None
        memory_seen |= row[3:] == '01'
        if row[2] == '1':
            if index != len(transcript) - 1 or index == 0:
                return None
            return 2 if memory_seen else 1
    return None


def decode_history(transcript):
    receipts = tuple(row[:3] for row in transcript)
    if receipts == ('100', '001'):
        return 1
    if receipts == ('100', '010', '100', '001'):
        return 2
    return None


def full_tables(stars, devices, law):
    result = []
    for device in devices:
        holding = stars[device.witness]
        n = len(holding)
        # Re-index all physical coordinates onto this actual holding, including unused ones.
        local = {d: i for i, d in enumerate(holding)}
        unit = type(device)(-1, 0, -1, tuple(local[d] for d in device.offer),
                            tuple(local[d] for d in device.stage), tuple(local[d] for d in device.receipt),
                            (), tuple(local[d] for d in device.donor_bundle))
        count = 0
        enabled = Counter()
        erased = [set() for _ in range(n)]
        for word in range(1 << n):
            if not allowed(word.bit_count(), n, law):
                continue
            count += 1
            for i in range(n):
                erased[i].add(word & ~(1 << i))
            for conditional in (False, True):
                act = relay_action(word, unit, conditional)
                if act is not None:
                    after = exchange(word, act.swaps)
                    assert after != word and allowed(after.bit_count(), n, law)
                    enabled[str(conditional) + '-' + act.kind] += 1
        sizes = [len(x) for x in erased]
        assert 0 < count < 1 << n and set(sizes) == {1 << (n - 1)}
        result.append({'holder': device.witness, 'arity': n, 'possible': 1 << n, 'allowed': count,
                       'after_single_forgetting': sizes, 'enabled_moves_by_read': dict(sorted(enabled.items()))})
    return result


def explore(stars, devices, source_p, offer_p, conditional, initial):
    holders = memberships(stars)
    rows = [set(row) for row in stars]
    validity = [(mask(star), len(star)) for star in stars]
    state_actions = {}
    path_rows = []
    for d in devices:
        assert set(stars[d.source]).isdisjoint(stars[d.receiver])
        for bank in (d.offer, d.stage, d.receipt, d.memory):
            assert len(set(holders[name] for name in bank)) == 1
    def check_word(word, law):
        return all(allowed((word & row).bit_count(), count, law) for row, count in validity)
    def census(law):
        def enabled(word):
            if word not in state_actions:
                assert check_word(word, law)
                transitions = []
                for d in devices:
                    selected = offer_p if d.source == source_p else 1
                    options = (sender_offer(word, d, selected), relay_action(word, d, conditional),
                               acknowledge(word, d))
                    for act in options:
                        if act is None:
                            continue
                        assert set(act.sensing) <= rows[act.actor]
                        for a, b in act.swaps:
                            assert holders[a] == holders[b] and act.actor in holders[a]
                        after = exchange(word, act.swaps)
                        assert word != after
                        transitions.append((act, after))
                state_actions[word] = transitions
            return state_actions[word]
        transcripts = Counter()
        terminals = set()
        longest = 0
        def visit(word, route, traces, sources, changes):
            nonlocal longest
            branches = enabled(word)
            if not branches:
                longest = max(len(route), longest)
                terminals.add(word)
                key = tuple(tuple(x) for x in traces)
                transcripts[key] += 1
                assert all(trace[-1][2] == '1' and sum(t[2] == '1' for t in trace) == 1 for trace in traces)
                assert len(sources) == 2 and source_p in sources
                for idx, trace in enumerate(traces):
                    assert decode_memory(trace) == decode_history(trace) and decode_history(trace) in (1, 2)
                    contact, own = changes[idx]
                    assert contact == decode_history(trace) and own == contact - 1
                if len(path_rows) == 0:
                    path_rows.append([{'actor': a.actor, 'action': a.kind, 'physical_swaps': a.swaps,
                                       'sensed_marks': a.sensing} for a in route])
                return
            for act, after in branches:
                altered = [list(entry) for entry in traces]
                moved = [list(x) for x in changes]
                for idx, d in enumerate(devices):
                    obs = sample(after, d)
                    if obs != altered[idx][-1]:
                        assert act.actor in (d.witness, d.receiver)
                        moved[idx][int(act.actor == d.receiver)] += 1
                        altered[idx].append(obs)
                next_sources = set(sources)
                if act.kind == 'offer':
                    assert act.actor not in sources
                    next_sources.add(act.actor)
                assert len(route) <= 8, 'nonterminating or unexpected enabled return'
                visit(after, route + [act], altered, next_sources, moved)
        visit(initial, [], [[sample(initial,d)] for d in devices], set(), [[0,0],[0,0]])
        assert len(transcripts) == len(terminals) == 1
        (traces, total), = transcripts.items()
        graph = []
        for word, options in sorted(state_actions.items()):
            graph.append({'delta_from_initial': hex(initial ^ word), 'enabled': [
                {'actor': act.actor, 'action': act.kind, 'swaps': act.swaps, 'after_delta': hex(initial ^ after)}
                for act, after in options]})
        return {'complete_orders': total, 'states': len(state_actions), 'longest': longest,
                'one_complete_actual_order': path_rows[0], 'all_order_state_graph': graph,
                'receiver_transcripts': traces, 'memory_decoded': [decode_memory(t) for t in traces],
                'history_decoded': [decode_history(t) for t in traces],
                'final_receipt_bank': [t[-1][:3] for t in traces],
                'incoming_changes': [decode_history(t) for t in traces],
                'own_acknowledgments': [decode_history(t) - 1 for t in traces]}
    return census
