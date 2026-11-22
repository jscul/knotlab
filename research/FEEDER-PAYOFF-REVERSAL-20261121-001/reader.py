"""A public-transition reader with a persistent, physically exchanged signed tally.

All controller decisions and credits are offers on the named word. Python
decodes the tally solely for the public report and for supplied interventions.
"""
from functools import lru_cache
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, product
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
source = HERE.parent / "FEEDER-MEMORY-20261121-001" / "keeper.py"
spec = spec_from_file_location("payoff_reversal_archived_keeper", source)
old = module_from_spec(spec)
sys.modules[spec.name] = old
spec.loader.exec_module(old)

BITS = 32
SCHEMA = "feeder-payoff-difference-v1"
ACTION_MARK = old.A[2]
ADDED = {
    "route": 3, "route_slack": 1, "score": 2 * BITS, "score_slack": 1,
    "degree_three": 2, "previous_eat": 2, "training": 2, "probe": 3,
    "arrival_event": 4, "route_buffer": 3, "route_out": 3,
    "credit_energy": 11, "credit_paid": 2,
}
NAMES = dict(old.NAMES)
cursor = len(old.ALL)
for name, width in ADDED.items():
    NAMES[name] = tuple(range(cursor, cursor + width))
    cursor += width
ALL = tuple(range(cursor))
STARS = {
    **old.STARS,
    "H": (*old.STARS["H"], *(n for b in ADDED if b not in ("route_slack", "score_slack")
                               for n in NAMES[b])),
    "R": (*NAMES["route"], *NAMES["route_slack"]),
    "C": (*NAMES["score"], *NAMES["score_slack"]),
}
OWNERS = {n: tuple(h for h, names in STARS.items() if n in names) for n in ALL}
BANK_MASK = {b: sum(1 << n for n in ns) for b, ns in NAMES.items()}
STAR_MASK = {h: sum(1 << n for n in ns) for h, ns in STARS.items()}
LEARNED_MASK = BANK_MASK["score"]
SCORE_PAIRS = tuple(zip(NAMES["score"][::2], NAMES["score"][1::2], strict=True))
ZERO_MARKS = sum(1 << a for a, b in SCORE_PAIRS)
MAGNITUDE_MARKS = sum(1 << b for a, b in SCORE_PAIRS[:-1])
ROUTES = (None, "A", "B")


def lawful(word, law):
    if law not in old.LAW or word < 0 or word >> len(ALL):
        return False
    counts = ((word & mask).bit_count() for mask in STAR_MASK.values())
    if law == "parity":
        return all(n % 2 == 0 for n in counts)
    return all(0 < n < len(names) for n, names in zip(counts, STARS.values(), strict=True))


def index(word, bank):
    occupied = (word & BANK_MASK[bank]) >> NAMES[bank][0]
    if occupied == 0 or occupied & (occupied - 1):
        raise ValueError(f"Invalid one-mark word in {bank}")
    return occupied.bit_length() - 1


def literal(bank, i):
    return NAMES[bank][i], 1


@lru_cache(maxsize=None)
def offer(label, holder, operands, guard=()):
    a, b = operands
    if (a == b or holder not in OWNERS[a] or OWNERS[a] != OWNERS[b]
            or len({n for n, value in guard}) != len(guard)
            or any(n in operands or holder not in OWNERS[n] or value not in (0, 1)
                   for n, value in guard)):
        raise ValueError(f"Unsupported local exchange: {label}")
    return old.Offer(label, holder, operands, guard, sum(1 << n for n, val in guard),
                     sum(val << n for n, val in guard), (1 << a) | (1 << b), True)


def exchange(label, bank, a, b, guard=(), holder="H"):
    return offer(label, holder, (NAMES[bank][a], NAMES[bank][b]), tuple(guard))


def word_swap(label, left, right):
    """Swap two three-symbol one-mark registers with different holding lists."""
    out = []
    for a, b in combinations(range(3), 2):
        x = exchange(label + " left", left, a, b, (literal(right, b),))
        y = exchange(label + " right", right, a, b, (literal(left, b),))
        out.extend((x, y, x))
    return tuple(out)


def action_offer(label, start, end, guard):
    return offer(label, "H", old.difference(old.A, old.ACTION_CODES[start], old.ACTION_CODES[end]),
                 tuple(guard))


BASE = {
    (feeder, ate): action_offer("current feeder and historical action", 0,
                                2 if feeder and not ate else 1,
                                (literal("probe", 0), literal("cue", feeder),
                                 literal("previous_eat", ate)))
    for feeder, ate in product(range(2), repeat=2)
}
CLAMPS = {
    bit: action_offer("explicit public prefix", 0, 1 + bit, (literal("probe", 1 + bit),))
    for bit in range(2)
}
ELIGIBLE = (literal("cue", 1), literal("degree_three", 1), literal("previous_eat", 0))
VETO_COMMON = (literal("training", 0), literal("probe", 0), *ELIGIBLE)
VETO_MASK = sum(1 << n for n, value in VETO_COMMON)
VETO_A = action_offer("negative score declines A", 2, 1,
                      (*VETO_COMMON, literal("route", 1), (SCORE_PAIRS[-1][1], 1)))
VETO_B = tuple(
    action_offer("positive score declines B", 2, 1,
                 (*VETO_COMMON, literal("route", 2), (SCORE_PAIRS[-1][0], 1),
                  (SCORE_PAIRS[j][1], 1), *((pair[0], 1) for pair in SCORE_PAIRS[j + 1:-1])))
    for j in range(BITS - 1)
)
CREDIT = {
    (a, b): exchange("mark comparison-energy receipt", "credit_paid", 0, 1,
                     ((ACTION_MARK, 1), literal("cue", 1), literal("energy_before", a),
                      literal("credit_energy", b)))
    for a in range(1, 11) for b in range(a, 11)
}
CREDIT_GATE = (literal("training", 1), (ACTION_MARK, 1), literal("credit_paid", 1), *ELIGIBLE)
CREDIT_GATE_MASK = sum(1 << n for n, value in CREDIT_GATE)
ADJUST = {
    route: tuple(offer("increment on credited A" if route == 1 else "decrement on credited B",
                       "H", SCORE_PAIRS[j],
                       (*CREDIT_GATE, literal("route", route),
                        *((pair[1 if route == 1 else 0], 1) for pair in SCORE_PAIRS[:j])))
                 for j in reversed(range(BITS)))
    for route in (1, 2)
}
# 0 = stay, 1 = actual unpaired move, 2/3 = actual A/B move.
ROUTE_INPUT = {
    event: exchange("paired departure to route input", "route_buffer", 0, event - 1,
                    (literal("arrival_event", event),)) for event in (2, 3)
}
ROUTE_EXCHANGE = word_swap("exchange new and old local arrival", "route", "route_buffer")
ROUTE_EXPORT = tuple(offer("retire old route", "H", (a, b))
                     for a, b in zip(NAMES["route_buffer"], NAMES["route_out"], strict=True))
MEMORY_TOUCH = tuple(offer("external exchange of matching learned pair", "C", pair)
                     for pair in SCORE_PAIRS)
OLD_DETECT = {(a, b): gate for (a, b), gate in zip(CREDIT, old.DETECT, strict=True)}


@lru_cache(maxsize=2)
def initial_word(law):
    w = old.initial_word(law) | ZERO_MARKS
    for bank in ADDED:
        if bank not in ("route_slack", "score_slack", "score"):
            w |= 1 << NAMES[bank][0]
    if law == "parity":
        for holder, slack in (("R", "route_slack"), ("C", "score_slack"), ("H", "coupler_slack")):
            if (w & STAR_MASK[holder]).bit_count() % 2:
                w ^= 1 << NAMES[slack][0]
    if not lawful(w, law):
        raise AssertionError("Initial physical preparation fails its holding law")
    return w


@lru_cache(maxsize=2048)
def signed_score(raw):
    """Audit accessor. Its argument contains the learned marks and nothing else."""
    val = sum(((raw >> b) & 1) << j for j, (a, b) in enumerate(SCORE_PAIRS))
    return val - (1 << BITS) if val & (1 << (BITS - 1)) else val


def _decode_word(export):
    if not isinstance(export, dict) or export.get("schema") != SCHEMA or export.get("bits") != BITS:
        raise ValueError("Foreign learned-word schema")
    material = export.get("word")
    if (not isinstance(material, str) or len(material) != 2 * BITS
            or any(material[j:j + 2] not in ("10", "01") for j in range(0, len(material), 2))):
        raise ValueError("Each learned physical pair needs exactly one marked alternative")
    raw = old.inject(0, NAMES["score"], material)
    if type(export.get("score")) is not int or signed_score(raw) != export["score"]:
        raise ValueError("Signed audit value disagrees with transported physical word")
    return raw


def _observation_key(obs):
    return bool(obs.feeder), obs.energy, obs.previous, tuple(obs.slots)


class PayoffReader(old.KnotKeeper):
    """A copyable reader. The sole state retained across episodes is the score bank."""
    __slots__ = ("_observation",)

    def __init__(self, law):
        super().__init__(law)
        self._word = initial_word(law)
        self._observation = None

    @property
    def word(self):
        return self._word

    @property
    def training(self):
        return bool(old.get(self._word, NAMES["training"][1]))

    @property
    def route_cue(self):
        return ROUTES[index(self._word, "route")]

    @property
    def score(self):
        return signed_score(self._word & LEARNED_MASK)

    def begin_episode(self, training=False):
        if type(training) is not bool:
            raise ValueError("Episode write-enable is Boolean")
        retained = self._word & LEARNED_MASK
        self._word = (initial_word(self.law) & ~LEARNED_MASK) | retained
        self._load("training", int(training), None)
        self._stage = "idle"
        self._observation = None
        return self

    def export_memory(self):
        return {"schema": SCHEMA, "bits": BITS, "word": old.code(self._word, NAMES["score"]),
                "score": self.score}

    def _mount(self, raw, trace):
        changed = self._word ^ raw
        for a, gate in zip(SCORE_PAIRS, MEMORY_TOUCH, strict=True):
            if changed & (1 << a[0]):
                self._offer(gate, trace=trace)

    @classmethod
    def from_memory(cls, law, exported):
        prepared = cls(law)
        prepared._mount(_decode_word(exported), None)
        return prepared

    @classmethod
    def calibrated(cls, law, preference):
        if preference not in (None, "A", "B"):
            raise ValueError("Fixed calibrated preference must be A, B or neutral")
        prepared = cls(law)
        if preference == "A":
            prepared._offer(MEMORY_TOUCH[0])
        if preference == "B":
            prepared._run(MEMORY_TOUCH)
        return prepared

    def _state(self, include_learned):
        return {"law": self.law, "stage": self._stage, "writer": self.writer, "reader": self.reader,
                "observation": None if self._observation is None else _observation_key(self._observation),
                "word": self._word if include_learned else self._word & ~LEARNED_MASK,
                "banks": {name: old.code(self._word, ns) for name, ns in NAMES.items()
                          if include_learned or name != "score"}}

    def snapshot(self):
        return self._state(True)

    def nonmemory_snapshot(self):
        return self._state(False)

    def _load(self, bank, hot, trace):
        old_hot = index(self._word, bank)
        if old_hot != hot:
            self._offer(exchange("supplied port " + bank, bank, old_hot, hot), trace=trace)

    def checkpoint(self, obs, *, detail=False):
        if self._stage != "idle":
            raise ValueError("Complete or reset the preceding decision before preparing another")
        if (type(obs.energy) is not int or not 1 <= obs.energy <= 10
                or obs.previous not in ("start", "eat", "move", "refused")
                or obs.slots != tuple(range(len(obs.slots)))):
            raise ValueError("Malformed live public observation or anonymous control roster")
        trace = [] if detail else None
        self._run(old.CLEAR_ACTION, trace=trace)
        self._export("action", trace)
        for bank, hot in (("cue", int(bool(obs.feeder))), ("menu", old.menu_type(obs.slots)),
                          ("degree_three", int(len(obs.slots) == 3)),
                          ("previous_eat", int(obs.previous == "eat")), ("energy_before", obs.energy)):
            self._load(bank, hot, trace)
        if self.action_word != old.ACTION_CODES[0]:
            raise AssertionError("The action bank is occupied at preparation")
        self._observation = obs
        self._stage = "ready to read"
        return trace

    def read_prepared(self, *, probe_bit=None, detail=False):
        if self._stage != "ready to read":
            raise ValueError("A physical action requires a prepared observation")
        if probe_bit is not None and (type(probe_bit) not in (int, bool) or probe_bit not in (0, 1)):
            raise ValueError("A declared probe must be a bit")
        trace = [] if detail else None
        self._load("probe", 0 if probe_bit is None else 1 + int(probe_bit), trace)
        probe = index(self._word, "probe")
        if detail:
            self._run((*BASE.values(), *CLAMPS.values(), VETO_A, *VETO_B), trace=trace)
        else:
            # Dispatch only rows with potentially true, unchanged physical guards.
            if probe:
                self._offer(CLAMPS[probe - 1])
            else:
                self._offer(BASE[index(self._word, "cue"), index(self._word, "previous_eat")])
            if self._word & VETO_MASK == VETO_MASK:
                route = index(self._word, "route")
                if route == 1:
                    self._offer(VETO_A)
                elif route == 2 and (occupied := self._word & MAGNITUDE_MARKS):
                    highest = (occupied.bit_length() - 1 - SCORE_PAIRS[0][1]) // 2
                    self._offer(VETO_B[highest])
        self._stage = "issued"
        bit = old.get(self._word, ACTION_MARK)
        return (bit, trace) if detail else bit

    def decide(self, obs, *, probe_bit=None):
        self.checkpoint(obs)
        return self.read_prepared(probe_bit=probe_bit)

    def _route_transition(self, event, trace):
        self._load("arrival_event", event, trace)
        if event:
            if event in ROUTE_INPUT:
                self._offer(ROUTE_INPUT[event], trace=trace)
            self._run(ROUTE_EXCHANGE, trace=trace)
            self._run(ROUTE_EXPORT, trace=trace)
            old_hot = index(self._word, "route_out")
            previous = self._word
            if old_hot:
                self._word ^= (1 << NAMES["route_out"][old_hot]) | (1 << NAMES["route_out"][0])
            if trace is not None:
                trace.append({"external_exchange": "retire private route token and supply ready token",
                              "bank": "route_out", "exported": old.code(previous, NAMES["route_out"]),
                              "incoming": "100", "before": previous, "after": self._word})
        self._load("arrival_event", 0, trace)

    def after_turn(self, obs, bit, outgoing_slot, energy_after, *, credit_override=None, detail=False):
        if self._stage != "issued" or obs != self._observation:
            raise ValueError("Missing issued decision for this public observation")
        if type(bit) not in (int, bool) or bit not in (0, 1) or int(bit) != old.get(self._word, ACTION_MARK):
            raise ValueError("Reported bit disagrees with the issued physical action")
        e = obs.energy
        if type(energy_after) is not int or (energy_after != e - 1 and not
                (bit and obs.feeder and energy_after == min(10, e + 3))):
            raise ValueError("Observed energy contradicts the public ration cost or receipt")
        if outgoing_slot is None:
            if not bit and obs.slots:
                raise ValueError("The public ordinary move must supply its actual outward slot")
            event = 0
        else:
            if bit or type(outgoing_slot) is not int or outgoing_slot not in obs.slots:
                raise ValueError("Outward receipt does not name an actually available move")
            event = 2 + outgoing_slot % 2 if (outgoing_slot ^ 1) in obs.slots else 1
        if credit_override is not None and (not self.training or type(credit_override) not in (int, bool)
                                            or credit_override not in (0, 1)):
            raise ValueError("A replacement comparison receipt requires training and a public bit")
        trace = [] if detail else None
        score_before = self.score
        route = index(self._word, "route")
        eligible = bool(route and all(old.get(self._word, n) == value for n, value in ELIGIBLE))
        first_before = self.memory_word
        probe = index(self._word, "probe")
        credit_energy = energy_after if credit_override is None else (min(10, e + 3) if credit_override else e - 1)
        for bank, value in (("previous_on", int(bit)), ("previous_menu", old.menu_type(obs.slots)),
                            ("energy_after", energy_after), ("credit_energy", credit_energy)):
            self._load(bank, value, trace)
        if detail:
            self._run(old.DETECT, trace=trace)
            self._run(CREDIT.values(), trace=trace)
        else:
            if (true_offer := OLD_DETECT.get((e, energy_after))) is not None:
                self._offer(true_offer)
            if (credit_offer := CREDIT.get((e, credit_energy))) is not None:
                self._offer(credit_offer)
        paid = bool(old.get(self._word, NAMES["paid"][1]))
        credit = bool(old.get(self._word, NAMES["credit_paid"][1]))
        credited = bool(route and self._word & CREDIT_GATE_MASK == CREDIT_GATE_MASK)
        if detail:
            for direction in (1, 2):
                self._run(ADJUST[direction], trace=trace)
        elif credited:
            self._run(ADJUST[route])
        # First memory always receives the true public ration receipt. No
        # substituted credit signal reaches these inherited controlled swaps.
        if paid or detail:
            self._run(old.ADDRESS, trace=trace)
            self._run(old.COMMIT, trace=trace)
        self._export("memory", trace)
        if detail:
            self._run(reversed(CREDIT.values()), trace=trace)
            self._run(reversed(old.DETECT), trace=trace)
        else:
            if credit:
                self._offer(CREDIT[e, credit_energy])
            if paid:
                self._offer(OLD_DETECT[e, energy_after])
        self._route_transition(event, trace)
        for bank in (*old.PUBLIC, "credit_energy", "degree_three", "previous_eat", "probe"):
            self._load(bank, 0, trace)
        self._stage = "idle"
        self._observation = None
        return {"eligible": eligible, "eligible_bite": bool(bit and eligible), "route_cue": ROUTES[route],
                "next_route_cue": self.route_cue, "issued_bit": int(bit),
                "probe_bit": None if probe == 0 else probe - 1, "actual_paid": paid,
                "credit_paid": credit, "credited": credited, "credit_override": credit_override,
                "observed_energy_after": energy_after, "comparison_energy_after": credit_energy,
                "score_before": score_before, "score_after": self.score,
                "memory_before": first_before, "memory_after": self.memory_word,
                **({"offers": trace} if detail else {})}

    def _ready(self):
        if self._stage != "ready to read":
            raise ValueError("Prepare the recipient before a causal intervention")

    def restore_learned(self, exported, *, detail=False):
        self._ready()
        trace = [] if detail else None
        self._mount(_decode_word(exported), trace)
        return trace

    def clear_learned(self, *, detail=False):
        self._ready()
        outgoing = self.export_memory()
        trace = [] if detail else None
        self._mount(ZERO_MARKS, trace)
        return (outgoing, trace) if detail else outgoing

    def swap_learned(self, other, *, detail=False):
        self._ready()
        other._ready()
        if self.law != other.law:
            raise ValueError("Learned transfer requires two copies under the same law")
        left, right = self._word & LEARNED_MASK, other._word & LEARNED_MASK
        a_trace, b_trace = ([], []) if detail else (None, None)
        self._mount(right, a_trace)
        other._mount(left, b_trace)
        return (a_trace, b_trace) if detail else None

    def sham(self, *, detail=False):
        self._ready()
        trace = [] if detail else None
        self._run((MEMORY_TOUCH[0], MEMORY_TOUCH[0]), trace=trace)
        return trace
