"""A supplied reversible, locally guarded receipt writer and action readout.

Only the public transition method accepts game inputs. The physical memory and
action are disjoint named registers. There is no cursor, food ledger, source
label, random stream, fitted parameter, or policy lookup in this device.
"""
from dataclasses import dataclass
from itertools import combinations, product


LAW = ("nae", "parity")
TYPES = ("zero", "one", "many")
MEMORY_CODES = ("110", "101", "011")
ACTION_CODES = ("100", "010", "001")  # ready, OFF, ON; read only position 2
# All public inputs use a single marked place at a time, including their idle
# encoding. Hence refreshing a port can be implemented by local transpositions.
WIDTHS = {
    "m": 3, "memory_slack": 1, "a": 3, "action_slack": 1,
    "t": 3, "m_out": 3, "a_scratch": 3, "a_out": 3, "paid": 2,
    "previous_on": 2, "previous_menu": 3, "energy_before": 11,
    "energy_after": 11, "cue": 2, "menu": 3, "coupler_slack": 1,
}
NAMES = {}
count = 0
for register, width in WIDTHS.items():
    NAMES[register] = tuple(range(count, count + width))
    count += width
M = NAMES["m"]
A = NAMES["a"]
T = NAMES["t"]
ALL = tuple(range(count))
STARS = {
    "M": (*M, *NAMES["memory_slack"]),
    "K": (*A, *NAMES["action_slack"]),
    "H": tuple(n for n in ALL if n not in (*NAMES["memory_slack"], *NAMES["action_slack"])),
}
OWNERS = {n: tuple(h for h, star in STARS.items() if n in star) for n in ALL}
PUBLIC = ("previous_on", "previous_menu", "energy_before", "energy_after", "cue", "menu")


def get(word, n):
    return (word >> n) & 1


def code(word, names):
    return "".join(str(get(word, n)) for n in names)


def inject(word, names, values):
    for n, v in zip(names, values, strict=True):
        word = word | 1 << n if v == "1" else word & ~(1 << n)
    return word


def clauses(names, values):
    return tuple((n, int(v)) for n, v in zip(names, values, strict=True))


def admissible(word, law):
    for star in STARS.values():
        total = sum(get(word, n) for n in star)
        if law == "nae" and total in (0, len(star)):
            return False
        if law == "parity" and total % 2:
            return False
    return True


def menu_type(slots):
    if isinstance(slots, int) and not isinstance(slots, bool):
        n = slots
    else:
        n = len(slots)
    if n < 0:
        raise ValueError("Number of anonymous move controls must be nonnegative")
    return min(2, n)


@dataclass(frozen=True, slots=True)
class Offer:
    label: str
    holder: str
    operands: tuple
    guard: tuple
    guard_mask: int
    guard_word: int
    change_mask: int
    supported: bool


def swap(label, operands, guard=(), holder="H"):
    i, j = operands
    held = STARS[holder]
    guard = tuple(guard)
    supported = (i != j and i in held and j in held and OWNERS[i] == OWNERS[j]
                 and all(n in held and n not in operands and x in (0, 1) for n, x in guard))
    if len({n for n, _ in guard}) != len(guard):
        raise ValueError("A literal appears twice in a guard")
    return Offer(label, holder, (i, j), guard, sum(1 << n for n, _ in guard),
                 sum(v << n for n, v in guard), (1 << i) | (1 << j), supported)


def difference(names, first, second):
    d = tuple(n for n, a, b in zip(names, first, second, strict=True) if a != b)
    if len(d) != 2:
        raise ValueError("A reversible register transposition must change exactly two marks")
    return d


def local_exchange(word, offer, connected=True):
    if not connected:
        return word, "disconnected"
    if not offer.supported:
        return word, "unsupported"
    if word & offer.guard_mask != offer.guard_word:
        return word, "guard refused"
    both = word & offer.change_mask
    if both == 0 or both == offer.change_mask:
        return word, "equal operands"
    return word ^ offer.change_mask, "changed"


def copy_swap(label, left, right, words, gate=()):
    """Swap two encoded finite alphabets despite unequal operand holder lists."""
    sequence = []
    for p, q in combinations(words, 2):
        x = swap(label + ": left", difference(left, p, q), (*gate, *clauses(right, q)))
        y = swap(label + ": right", difference(right, p, q), (*gate, *clauses(left, q)))
        sequence.extend((x, y, x))
    return tuple(sequence)


def writer():
    # Either permitted receipt energy (normal rise or clipped at capacity)
    # activates one disjoint local conjunction. Honest turns always cost one.
    # The schedule never branches on a desired action, world or holder ID.
    paid = NAMES["paid"]
    detect = []
    for before in range(1, 11):
        for after in range(before, 11):
            detect.append(swap("issued ON; nondecreasing public energy", paid,
                               ((NAMES["previous_on"][1], 1),
                                (NAMES["energy_before"][before], 1),
                                (NAMES["energy_after"][after], 1))))
    addressed = []
    commit = []
    for menu in (1, 2):
        gate = ((paid[1], 1), (NAMES["previous_menu"][menu], 1))
        addressed.append(swap("write observed menu to receipt register",
                              difference(T, MEMORY_CODES[0], MEMORY_CODES[menu]), gate))
        commit.extend(copy_swap("exchange physical memory and receipt", M, T, MEMORY_CODES, gate))
    return tuple(detect), tuple(addressed), tuple(commit)


def reader():
    rows = []
    for observed, menu, mem in product((0, 1), range(3), range(3)):
        # These are the pre-enrolled H conjunctions on literal input names.
        # One menu class having been paid does not identify all feeders of that class.
        eat = bool(observed) and not (menu in (1, 2) and mem == menu)
        guard = ((NAMES["cue"][observed], 1), (NAMES["menu"][menu], 1), *clauses(M, MEMORY_CODES[mem]))
        rows.append(swap("couple current cue, menu and stored word to action",
                         difference(A, ACTION_CODES[0], ACTION_CODES[2 if eat else 1]), guard))
    return tuple(rows)


DETECT, ADDRESS, COMMIT = writer()
READ = reader()
CLEAR_ACTION = copy_swap("export previous action for a fresh ready action", A, NAMES["a_scratch"], ACTION_CODES)
EXPORT = {
    "memory": tuple(swap("hand old receipt to exchangeable output bank", p)
                    for p in zip(T, NAMES["m_out"], strict=True)),
    "action": tuple(swap("hand old action to exchangeable output bank", p)
                    for p in zip(NAMES["a_scratch"], NAMES["a_out"], strict=True)),
}
SHAM = swap("physical comparison on memory positions 0 and 1", M[:2], holder="M")
assert all(z.supported for z in (*DETECT, *ADDRESS, *COMMIT, *READ, *CLEAR_ACTION,
                                  *EXPORT["memory"], *EXPORT["action"], SHAM))


def initial_word(law):
    if law not in LAW:
        raise ValueError(f"Unknown knot law {law!r}")
    w = 0
    initial = {"m": "110", "t": "110", "m_out": "110", "a": "100", "a_scratch": "100",
               "a_out": "100", "paid": "10", "memory_slack": "0", "action_slack": "1"}
    for name in PUBLIC:
        initial[name] = "1" + "0" * (len(NAMES[name]) - 1)
    for name, bits in initial.items():
        w = inject(w, NAMES[name], bits)
    # Constant for the preparation in each law. All later regular exchanges
    # preserve the bit count at every holder, so this physical slack is fixed.
    if law == "parity" and sum(get(w, n) for n in STARS["H"]) % 2:
        w |= 1 << NAMES["coupler_slack"][0]
    assert admissible(w, law)
    return w


class KnotKeeper:
    """A copyable deterministic three-holder board on public game values only."""

    __slots__ = ("law", "writer", "reader", "_word", "_stage")

    def __init__(self, law, *, writer=True, reader=True):
        self.law = law
        self.writer = bool(writer)
        self.reader = bool(reader)
        self._word = initial_word(law)
        self._stage = "idle"

    @property
    def memory_word(self):
        return code(self._word, M)

    @property
    def action_word(self):
        return code(self._word, A)

    def snapshot(self):
        """The tuple covers every physical name and all persistent control fields."""
        return (("law", self.law), ("writer", self.writer), ("reader", self.reader), ("stage", self._stage),
                *((name, code(self._word, bank)) for name, bank in NAMES.items()))

    def _offer(self, offered, connected=True, trace=None):
        before = self._word
        self._word, status = local_exchange(before, offered, connected)
        if trace is not None:
            trace.append({"offer": offered.label, "holder": offered.holder, "operands": offered.operands,
                          "guard": offered.guard, "guard_actual": [get(before, n) for n, _ in offered.guard],
                          "status": status, "before": before, "after": self._word,
                          "toggled": [i for i in offered.operands if get(before, i) != get(self._word, i)]})
        return status

    def _run(self, seq, connected=True, trace=None):
        for offered in seq:
            self._offer(offered, connected, trace)

    def _prepare_public(self, register, hot, trace):
        bank = NAMES[register]
        previous = next(i for i, n in enumerate(bank) if get(self._word, n))
        if hot != previous:
            self._offer(swap("supplied raw public input: " + register,
                             (bank[previous], bank[hot])), trace=trace)

    def _reset_public(self, trace):
        for r in PUBLIC:
            self._prepare_public(r, 0, trace)

    def _export(self, kind, trace):
        output = "m_out" if kind == "memory" else "a_out"
        ready = MEMORY_CODES[0] if kind == "memory" else ACTION_CODES[0]
        self._run(EXPORT[kind], trace=trace)
        ejected = code(self._word, NAMES[output])
        # This is an expressly supplied fresh three-name private token replacing
        # the outgoing one. Its old three bits are returned to the experimenter
        # in the trace; no persistent controller field reads them subsequently.
        before_refresh = self._word
        self._word = inject(self._word, NAMES[output], ready)
        if trace is not None:
            trace.append({"external_exchange": "retire private token and supply a ready token", "bank": output,
                          "exported": ejected, "incoming": ready,
                          "before": before_refresh, "after": self._word})
        return ejected

    def checkpoint(self, cue, slots, *, detail=False):
        """Refresh the action and load public inputs without issuing the decision."""
        trace = [] if detail else None
        self._run(CLEAR_ACTION, trace=trace)
        self._export("action", trace)
        self._reset_public(trace)
        self._prepare_public("cue", int(bool(cue)), trace)
        self._prepare_public("menu", menu_type(slots), trace)
        self._stage = "ready to read"
        if self.action_word != ACTION_CODES[0]:
            raise AssertionError("Uncleared action register")
        return trace

    def read_prepared(self, *, detail=False):
        if self._stage != "ready to read":
            raise ValueError("Prepare a fresh decision before reading")
        trace = [] if detail else None
        self._run(READ, self.reader, trace)
        self._stage = "issued"
        bit = get(self._word, A[2])
        return (bit, trace) if detail else bit

    def before_decision(self, cue, slots):
        self.checkpoint(cue, slots)
        return self.read_prepared()

    def after_turn(self, cue, slots, energy_before, action_on, energy_after, *, detail=False):
        """Apply a public turn receipt. A forced diagnostic prefix may supply its own action."""
        if type(energy_before) is not int or type(energy_after) is not int or not (1 <= energy_before <= 10):
            raise ValueError("A live ration decision needs a public energy in 1..10")
        if action_on not in (False, True) or energy_after not in {
                energy_before - 1, min(10, energy_before + 3) if cue and action_on else energy_before - 1}:
            raise ValueError("Public transition contradicts the ration game's action and energy bill")
        trace = [] if detail else None
        before = self.memory_word
        self._reset_public(trace)
        for name, value in (("previous_on", int(action_on)), ("previous_menu", menu_type(slots)),
                            ("energy_before", energy_before), ("energy_after", energy_after)):
            self._prepare_public(name, value, trace)
        self._run(DETECT, self.writer, trace)
        self._run(ADDRESS, self.writer, trace)
        addressed = code(self._word, T)
        detected = bool(get(self._word, NAMES["paid"][1]))
        self._run(COMMIT, self.writer, trace)
        old_record = self._export("memory", trace)
        self._run(reversed(DETECT), self.writer, trace)
        self._reset_public(trace)
        self._stage = "idle"
        if code(self._word, NAMES["paid"]) != "10" or code(self._word, T) != MEMORY_CODES[0]:
            raise AssertionError("Receipt workspace was not cleared")
        return {"memory_before": before, "memory_after": self.memory_word, "detected": detected,
                "addressed_receipt_word": addressed, "exported_previous_memory": old_record,
                **({"offers": trace} if detail else {})}

    def sham(self, *, detail=False):
        if self._stage != "ready to read":
            raise ValueError("Apply interventions at the prepared checkpoint")
        trace = [] if detail else None
        self._run((SHAM, SHAM), trace=trace)
        return trace

    def clamp_memory(self, value, *, detail=False):
        """The supplied intervention modifies only the complete physical memory."""
        if self._stage != "ready to read":
            raise ValueError("Apply interventions at the prepared checkpoint")
        if value in ("ready", "one", "many"):
            value = MEMORY_CODES[("ready", "one", "many").index(value)]
        if value not in MEMORY_CODES:
            raise ValueError("Unknown memory marking")
        trace = [] if detail else None
        if value != self.memory_word:
            pair = difference(M, self.memory_word, value)
            self._offer(swap("matched physical intervention on M", pair, holder="M"), trace=trace)
        return trace

    def exchange_memory(self, other, *, detail=False):
        if self.law != other.law or self._stage != "ready to read" or other._stage != "ready to read":
            raise ValueError("Reciprocal exchange requires two prepared boards of the same law")
        original, counterpart = self.memory_word, other.memory_word
        here = self.clamp_memory(counterpart, detail=detail)
        there = other.clamp_memory(original, detail=detail)
        return (here, there) if detail else None
