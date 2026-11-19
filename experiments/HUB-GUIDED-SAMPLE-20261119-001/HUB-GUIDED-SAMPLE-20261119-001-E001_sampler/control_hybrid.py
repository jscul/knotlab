"""Exact group counts and uniform draws for two certified roster shapes."""

from bisect import bisect_right
from dataclasses import dataclass
from math import comb


def indices(mask):
    while mask:
        first = mask & -mask
        yield first.bit_length() - 1
        mask ^= first


def candidate_rows(n, blocks):
    rows = [0]*n
    for block in blocks:
        if not 0 < block < (1 << n) or block.bit_count() < 2:
            raise ValueError("a block needs two or more distinct roster members")
        for u in indices(block):
            rows[u] |= block
    return tuple(row & ~(1 << u) for u,row in enumerate(rows))


def unheld_word(index, bits, held):
    """The index-th word among all binary words except the distinct held words."""
    low, high = index, (1 << bits) - 1
    while low < high:
        mid = (low+high)//2
        if mid + 1 - bisect_right(held, mid) > index:
            high = mid
        else:
            low = mid+1
    return low


def pair_at(n, index):
    """The index-th lexicographic unordered pair of distinct roster members."""
    low, high = 0, n-2
    while low < high:
        mid = (low+high+1)//2
        earlier = mid*(2*n-mid-1)//2
        if earlier <= index:
            low = mid
        else:
            high = mid-1
    earlier = low*(2*n-low-1)//2
    return low, low+1+index-earlier


@dataclass(frozen=True)
class GroupDraw:
    parents: tuple[int, ...]
    kind: str
    inverse_probability: int
    offshoot_slot: int | None = None


@dataclass(frozen=True)
class Hybrid:
    kind: str
    loose: tuple[int, ...]
    partners: tuple[tuple[int, int], ...]
    held: tuple[int, ...]
    residual: tuple[tuple[int, int], ...]
    demand: tuple[int, ...]

    @property
    def large_groups(self):
        k = len(self.partners)
        return (1 << k)-len(self.held) if k >= 3 else 0

    @property
    def residual_pairs(self):
        return comb(len(self.loose), 2) if self.kind == "single_block" else len(self.residual)

    @property
    def offshoots(self):
        if any(fresh < need for fresh,need in zip(self.loose, self.demand, strict=True)):
            return None
        return sum(fresh-need for fresh,need in zip(self.loose, self.demand, strict=True))

    @property
    def exact_binomial_tail(self):
        n = len(self.loose)
        return self.kind == "single_block" and n >= 3 and self.loose == (n-1,)*n

    @property
    def closes_on_next_birth(self):
        return self.kind == "single_block" and self.loose == (1,1)

    @property
    def births(self):
        return None if self.offshoots is None else self.large_groups+self.residual_pairs+self.offshoots

    def at(self, rank, stratum="groups"):
        """Unrank a joint group, an unheld large group, or an entire next birth."""
        if stratum == "large":
            total = self.large_groups
        elif stratum == "groups":
            total = self.large_groups+self.residual_pairs
        elif stratum == "births":
            total = self.births
        else:
            raise ValueError(stratum)
        if total is None or not 0 <= rank < total:
            raise IndexError("rank is outside the selected group population")
        if rank < self.large_groups:
            word = unheld_word(rank, len(self.partners), self.held)
            parents = tuple(sorted(pair[(word >> j) & 1] for j,pair in enumerate(self.partners)))
            return GroupDraw(parents, "large", total)
        rank -= self.large_groups
        if rank < self.residual_pairs:
            parents = pair_at(len(self.loose), rank) if self.kind == "single_block" else self.residual[rank]
            return GroupDraw(parents, "pair", total)
        rank -= self.residual_pairs
        for p, (loose, demand) in enumerate(zip(self.loose, self.demand, strict=True)):
            if rank < loose-demand:
                return GroupDraw((p,), "offshoot", total, rank)
            rank -= loose-demand
        raise AssertionError("offshoot rank escaped its population")

    def sample(self, rng, stratum="groups"):
        if stratum == "births":
            count = self.births
        elif stratum == "groups":
            count = self.large_groups+self.residual_pairs
        elif stratum == "large":
            count = self.large_groups
        else:
            raise ValueError(stratum)
        if not count:
            raise ValueError("the selected group population is empty or stalled")
        return self.at(rng.randrange(count), stratum)


def classify(loose, blocks):
    """Require the complete classical candidate relation, not a partnered part."""
    n = len(loose)
    if n == 0 and not blocks:
        return Hybrid("closed", (), (), (), (), ())
    if n < 2 or any(x < 1 for x in loose):
        return None
    blocks = tuple(sorted(set(blocks)))
    full = (1 << n)-1
    if any(not 0 < block <= full or block.bit_count() < 2 for block in blocks):
        raise ValueError("a block must lie in the roster and have two or more members")
    if full in blocks:
        return Hybrid("single_block", tuple(loose), (), (), (), (n-1,)*n)
    if n < 4 or n%2:
        return None
    rows = candidate_rows(n, blocks)
    nonneighbors = tuple(full & ~(row | (1 << u)) for u,row in enumerate(rows))
    if any(mask.bit_count() != 1 for mask in nonneighbors):
        return None
    partners = tuple((u,mask.bit_length()-1) for u,mask in enumerate(nonneighbors) if mask > (1 << u))
    k = n//2
    assert len(partners) == k and len({v for pair in partners for v in pair}) == n
    held_masks = [b for b in blocks if b.bit_count() == k]
    assert all(b.bit_count() <= k for b in blocks)
    held = tuple(sorted(sum(((b >> q) & 1) << j for j,(p,q) in enumerate(partners)) for b in held_masks))
    incidence = [0]*n
    for j, block in enumerate(held_masks):
        for u in indices(block):
            incidence[u] |= 1 << j
    residual = []
    # Each compatible pair has exactly 2^(k-2) possible transversal completions.
    each_pair = 1 << (k-2)
    if k == 2 or len(held) >= each_pair:
        for u, row in enumerate(rows):
            for v in indices(row & ~((1 << (u+1))-1)):
                if k == 2 or (incidence[u] & incidence[v]).bit_count() == each_pair:
                    residual.append((u,v))
    demand = [(1 << (k-1)) - h.bit_count() if k >= 3 else 0 for h in incidence]
    for u,v in residual:
        demand[u] += 1
        demand[v] += 1
    return Hybrid("complete_partnered", tuple(loose), partners, held, tuple(residual), tuple(demand))


def binomial_transition(n, k):
    """Census of the transition from k-subsets to (k+1)-subsets of one block."""
    if not 1 <= k < n:
        raise ValueError("source subset size must be positive and below the closing size")
    return {"current_population": comb(n,k), "births": comb(n,k+1), "parents": k+1,
            "fresh_per_birth": n-k-1, "exhausted_at_birth": k+1 == n}


def binomial_draw(n, k, rng):
    """Sample a group in a binomial tail with canonical combinatorial-rank names."""
    transition = binomial_transition(n,k)
    child = tuple(sorted(rng.sample(range(n),k+1)))
    parents = tuple(sorted(sum(comb(v,j) for j,v in enumerate(parent,1))
                           for i in range(k+1) if (parent := child[:i]+child[i+1:])))
    return GroupDraw(parents, "pair" if k == 1 else "large", transition["births"])
