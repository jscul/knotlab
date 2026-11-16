"""Independently replay actual public-row witnesses for rejected one-bit cuts.

Each six-integer record is [raw_group_mask, local_a, local_b, local_c,
settings_mask, scheme]. The three distinct local assignments are inserted into
one or two prescribed outside assignments. Three distinct observed signatures
prove at least three residual classes. Only an alternative group with an
exact-oracle threshold of two can use this lower bound.

Both modes use the same exact classifier, globally minimal width and unchanged
physical/cut verification from the predecessor. Pass witnesses=[] to disable
the certificates explicitly. No producer row value or conclusion is accepted.
"""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


SOURCE_DEPENDENCIES = (
    "experiments/FOLD-TWO-OUTPUT-20261115-001/FOLD-TWO-OUTPUT-20261115-001-E001_joint_tables/checker.py",
)


def _predecessor():
    path = Path(__file__).resolve().parents[3] / SOURCE_DEPENDENCIES[0]
    spec = spec_from_file_location("_fixed_probe_immutable_joint_checker", path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.JointChecker


_JointChecker = _predecessor()
COUNTERS = ("included_witnesses", "accepted_witnesses", "effective_witnesses", "exact_alternatives",
            "verifier_row_requests", "verifier_row_reads", "verifier_row_cache_hits",
            "verifier_output_bits_read", "witnesses_one_setting", "witnesses_two_settings",
            "chosen_exact_classifications", "packed_residual_columns", "packed_residual_shifts",
            "packed_residual_masks", "geometry_builds", "classified_groups")


class _Geometry:
    __slots__ = ("group", "raw_mask", "offsets", "packed_mask")

    def __init__(self, owner, group, raw_mask):
        a, b, c = (1 << i for i in group)
        mask = owner.zero[group[0]] & owner.zero[group[1]] & owner.zero[group[2]]
        self.group = group
        self.raw_mask = raw_mask
        self.offsets = (0, a, b, a | b, c, a | c, b | c, raw_mask)
        self.packed_mask = mask | (mask << owner.rows)


class _Replay:
    """Own all value-bearing state for exactly one verification call."""

    def __init__(self, owner, tables, witnesses):
        self.owner, self.n, self.rows = owner, owner.n, owner.rows
        self.zero, self.columns, self.full = owner.zero, owner.columns, owner.full
        self.t0, self.t1 = tables
        self.packed = self.t0 | (self.t1 << self.rows)
        self.witnesses = witnesses
        self.mask_of_common = (1 << self.n) - 1
        self.certified = set()
        self.row_cache = bytearray(self.rows) if witnesses else None
        self.count = dict.fromkeys(COUNTERS, 0)
        self.count["included_witnesses"] = len(witnesses)
        self.misses = 0

    def _essential(self, table):
        result = _JointChecker._essential(self, table)
        if self.witnesses:
            self.mask_of_common &= sum(1 << i for i in result)
        return result

    def _symbol(self, row):
        # Store the independently read 2-bit output plus one; zero is an
        # unread row. The same original row is read at most once in this task.
        value = self.row_cache[row]
        if not value:
            value = 1 + (((self.t0 >> row) & 1) | (((self.t1 >> row) & 1) << 1))
            self.row_cache[row] = value
            self.misses += 1
        return value

    def _validate_records(self):
        records, self.witnesses = self.witnesses, ()
        count = self.count
        symbol = self._symbol
        limits = (1 << self.n) - 1
        for record in records:
            if not isinstance(record, (tuple, list)) or len(record) != 6 or any(type(v) is not int for v in record):
                raise ValueError("a witness needs exactly six integers")
            mask, a, b, c, settings, scheme = record
            if mask <= 0 or mask & ~self.mask_of_common or mask.bit_count() != 3:
                raise ValueError("witness does not address a jointly essential triple")
            if mask in self.certified:
                raise ValueError("duplicate certificate for one alternative")
            if not (0 <= a < 8 and 0 <= b < 8 and 0 <= c < 8) or a == b or a == c or b == c:
                raise ValueError("a witness needs three distinct three-bit local assignments")
            if settings not in (1, 2, 3) or not 0 <= scheme < 4:
                raise ValueError("unknown outside scheme or settings mask")
            geo = self.owner.by_mask.get(mask)
            if geo is None:
                bits = mask
                axes = []
                while bits:
                    bit = bits & -bits
                    axes.append(bit.bit_length() - 1)
                    bits ^= bit
                geo = self._make_geometry(tuple(axes), mask)
            local = geo.offsets
            ra, rb, rc = local[a], local[b], local[c]
            outside = limits ^ mask
            primary = self.owner.settings[scheme] & outside
            first = outside ^ primary if settings == 2 else primary
            x, y, z = symbol(first | ra), symbol(first | rb), symbol(first | rc)
            if settings == 3:
                second = outside ^ primary
                # Each symbol is in 1..4, so three low bits suffice to
                # concatenate the two independent observations injectively.
                x = (x << 3) | symbol(second | ra)
                y = (y << 3) | symbol(second | rb)
                z = (z << 3) | symbol(second | rc)
                count["witnesses_two_settings"] += 1
                count["verifier_row_requests"] += 6
            else:
                count["witnesses_one_setting"] += 1
                count["verifier_row_requests"] += 3
            if x == y or x == z or y == z:
                raise ValueError("cited public rows do not distinguish three joint residuals")
            self.certified.add(mask)
            count["accepted_witnesses"] += 1

    def _make_geometry(self, group, mask):
        geometry = _Geometry(self.owner, group, mask)
        self.owner.by_mask[mask] = self.owner.by_group[group] = geometry
        self.count["geometry_builds"] += 1
        return geometry

    def _exact(self, geo, bound):
        # Concatenating the two public tables gives one shift/mask per joint
        # residual. Offsets select only local coordinates, so the highest row
        # retained in either block cannot spill into the other output.
        mask, offsets = geo.packed_mask, geo.offsets
        packed = self.packed
        first = packed & mask
        reads = 1
        if bound == 2:
            # The common width-two proof only needs a third distinct column.
            second = None
            for shift in offsets[1:]:
                value = (packed >> shift) & mask
                reads += 1
                if value != first:
                    if second is None:
                        second = value
                    elif value != second:
                        classes = 3
                        break
            else:
                classes = 1 if second is None else 2
        else:
            seen = {first}
            for shift in offsets[1:]:
                seen.add((packed >> shift) & mask)
                reads += 1
                if bound is not None and len(seen) > bound:
                    break
            classes = len(seen)
        self.count["packed_residual_columns"] += reads
        self.count["packed_residual_shifts"] += reads - 1
        self.count["packed_residual_masks"] += reads
        return classes

    def _classes(self, outputs, group, stop_above=None):
        # Inherited verify() computes shared essentiality before its first
        # call here. Validate *all* supplied records even if the final width
        # or chosen group makes some of them unnecessary.
        if self.witnesses:
            self._validate_records()
        geo = self.owner.by_group.get(group)
        if geo is None:
            mask = (1 << group[0]) | (1 << group[1]) | (1 << group[2])
            geo = self._make_geometry(group, mask)
        count = self.count
        count["classified_groups"] += 1
        if stop_above is None:
            count["chosen_exact_classifications"] += 1
        elif stop_above == 2 and geo.raw_mask in self.certified:
            count["effective_witnesses"] += 1
            return 3
        else:
            count["exact_alternatives"] += 1
        return self._exact(geo, stop_above)


class PaidVerifier:
    """Geometry persists at fixed arity. Public row observations never cross tasks."""

    def __init__(self, n):
        if type(n) is not int or n < 3:
            raise ValueError("joint verification requires at least three inputs")
        base = _JointChecker(n)
        self.n, self.rows, self.full = n, base.rows, base.full
        self.zero, self.columns = base.zero, base.columns
        self.by_group, self.by_mask = {}, {}
        self.settings = (0, *(sum(1 << i for i in range(n) if (i // stride) % 2 == 0)
                              for stride in (1, 2, 3)))
        self._work = dict.fromkeys(COUNTERS, 0)

    def work_counters(self):
        return self._work.copy()

    def ledger(self):
        return {"counters": self.work_counters(), "group_layouts": len(self.by_group)}

    def verify(self, tables, result, witnesses=None):
        """Validate the global width, physical program, cut, and every claimed witness.

        Explicit [] selects the identical verifier without producer evidence.
        The returned receipt includes the predecessor's exact checks. An
        absent group goes through the packed classifier. A claimed but false
        or structurally invalid record raises ValueError.
        """
        if not isinstance(tables, (tuple, list)) or len(tables) != 2 or any(
                type(t) is not int or not 0 <= t <= self.full for t in tables):
            raise ValueError("verification needs two complete public packed truth tables")
        if witnesses is None:
            witnesses = result.get("witnesses", ())
        if not isinstance(witnesses, (tuple, list)):
            raise ValueError("witnesses must be a sequence of compact records")
        group = result.get("triple")
        if (not isinstance(group, (tuple, list)) or len(group) != 3 or
                any(type(i) is not int or not 0 <= i < self.n for i in group)):
            raise ValueError("invalid chosen raw triple")
        task = _Replay(self, tables, witnesses)
        try:
            receipt = _JointChecker.verify(task, tables, result)
        finally:
            c = task.count
            c["verifier_row_reads"] = task.misses
            c["verifier_output_bits_read"] = 2 * task.misses
            c["verifier_row_cache_hits"] = c["verifier_row_requests"] - task.misses
            for key, value in c.items():
                self._work[key] += value
        receipt.update(task.count)
        return receipt
