// Exact finite search on the 64 original inputs. Compile with C++20.
#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <set>
#include <stdexcept>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using PointSet = std::uint64_t;
constexpr PointSet full = ~PointSet{0};

void require(bool ok, const char* reason) {
    if (!ok) throw std::logic_error(reason);
}

int parity(unsigned value) { return std::popcount(value) % 2; }
int total(int x) { return parity(x & (x >> 1)); }
int polar(int x, int y) { return total(x ^ y) ^ total(x) ^ total(y); }
PointSet bit(int x) { return PointSet{1} << x; }

// Translate a set of input words by XORing the j-th coordinate of every word.
PointSet flip(PointSet set, int j) {
    static constexpr std::array<PointSet, 6> zero_positions = {
        0x5555555555555555ULL, 0x3333333333333333ULL, 0x0f0f0f0f0f0f0f0fULL,
        0x00ff00ff00ff00ffULL, 0x0000ffff0000ffffULL, 0x00000000ffffffffULL};
    PointSet mask = zero_positions[j];
    return ((set & mask) << (1 << j)) | ((set & ~mask) >> (1 << j));
}

PointSet translate(PointSet set, unsigned delta) {
    while (delta) {
        set = flip(set, std::countr_zero(delta));
        delta &= delta - 1;
    }
    return set;
}

PointSet input_hull(PointSet set) {
    if (!set) return 0;
    int origin = std::countr_zero(set);
    PointSet hull = bit(origin);
    while (PointSet outside = set & ~hull) {
        int next = std::countr_zero(outside);
        hull |= translate(hull, origin ^ next);
    }
    return hull;
}

// A query on the identified honest points becomes an input linear form plus
// a selected product mask. Constants only exchange the two answers.
PointSet truth_table(int linear, int products) {
    PointSet table = 0;
    for (int x = 0; x < 64; ++x) {
        if (parity(x & linear) ^ parity(x & (x >> 1) & products)) table |= bit(x);
    }
    return table;
}

// Each maximal closing set is indexed by all of its triples for fast containment.
// The separate affine-graph enumeration below checks completeness and maximality.
class ClosingSets {
    std::array<std::vector<PointSet>, 41664> by_triple;
    int triple_index(int a, int b, int c) const {
        return a + b * (b - 1) / 2 + c * (c - 1) * (c - 2) / 6;
    }
public:
    std::set<PointSet> maximal;

    ClosingSets() {
        for (int a = 1; a < 64; ++a) {
            for (int b = a + 1; b < 64; ++b) {
                if ((a ^ b) <= b || polar(a, b)) continue;
                std::array<PointSet, 4> cosets{};
                for (int x = 0; x < 64; ++x) {
                    cosets[polar(x, a) + 2 * polar(x, b)] |= bit(x);
                }
                for (PointSet coset : cosets) {
                    PointSet unused = coset;
                    while (unused) {
                        int t = std::countr_zero(unused);
                        PointSet hole = bit(t) | bit(t ^ a) | bit(t ^ b) | bit(t ^ a ^ b);
                        PointSet kept = coset ^ hole;
                        require(std::popcount(kept) == 12, "wrong maximal closing-set size");
                        require(maximal.insert(kept).second, "duplicate maximal closing set");
                        unused &= ~hole;
                    }
                }
            }
        }
        require(maximal.size() == 5040, "wrong number of maximal closing sets");
        for (PointSet set : maximal) {
            for (PointSet i = set; i; i &= i - 1) {
                for (PointSet j = i & (i - 1); j; j &= j - 1) {
                    for (PointSet k = j & (j - 1); k; k &= k - 1) {
                        int key = triple_index(std::countr_zero(i), std::countr_zero(j), std::countr_zero(k));
                        by_triple[key].push_back(set);
                    }
                }
            }
        }
        for (const auto& list : by_triple) require(!list.empty(), "uncovered input triple");
    }

    bool contains(PointSet subset) const {
        int size = std::popcount(subset);
        if (size <= 3) return true;  // Every triple was checked at construction.
        if (size > 12) return false;
        int a = std::countr_zero(subset);
        PointSet tail = subset & (subset - 1);
        int b = std::countr_zero(tail);
        int c = std::countr_zero(tail & (tail - 1));
        for (PointSet superset : by_triple[triple_index(a, b, c)]) {
            if (!(subset & ~superset)) return true;
        }
        return false;
    }
};

// Cross-check all affine checksum graphs on all input subspaces without using
// the isotropic-subspace formula to decide whether a graph closes.
void audit_affine_graphs(const ClosingSets& closing) {
    std::array<std::set<PointSet>, 7> directions;
    directions[0].insert(bit(0));
    for (int k = 0; k < 6; ++k) {
        for (PointSet space : directions[k]) {
            for (int x = 1; x < 64; ++x) {
                if (!(space & bit(x))) directions[k + 1].insert(space | translate(space, x));
            }
        }
    }
    std::array<PointSet, 64> graphs{};
    for (int m = 0; m < 64; ++m) graphs[m] = truth_table(m, 31);
    std::set<PointSet> seen_maximal;
    int subspaces = 0, graph_count = 0, terminal_graphs = 0;
    for (const auto& dimension : directions) for (PointSet dir : dimension) {
        PointSet remaining = full;
        while (remaining) {
            PointSet domain = translate(dir, std::countr_zero(remaining));
            remaining &= ~domain;
            ++subspaces;
            std::set<PointSet> possible;
            for (PointSet graph : graphs) {
                possible.insert(domain & graph);
                possible.insert(domain & ~graph);
            }
            require(possible.size() == 2u * std::popcount(dir), "missing affine graph");
            for (PointSet honest : possible) {
                ++graph_count;
                if (input_hull(honest) != domain) continue;
                PointSet opposite = domain ^ honest;
                PointSet other_hull = input_hull(opposite);
                if (other_hull == domain) continue;
                require(other_hull == opposite, "a terminal checksum graph partly survives");
                require(closing.contains(honest), "a closing checksum graph was omitted");
                ++terminal_graphs;
                if (std::popcount(honest) == 12) seen_maximal.insert(honest);
            }
        }
    }
    require(seen_maximal == closing.maximal, "a claimed maximum fails the direct graph check");
    std::cout << "graphs " << subspaces << ' ' << graph_count << ' ' << terminal_graphs
              << ' ' << seen_maximal.size() << '\n';
}

struct Search {
    const ClosingSets& closing;
    std::vector<PointSet> questions;
    std::array<std::unordered_map<PointSet, bool>, 8> decisions;
    unsigned long root_splits = 0;

    Search(const ClosingSets& sets, const std::set<int>& masks) : closing(sets) {
        for (int m : masks) for (int linear = 0; linear < 64; ++linear) {
            if (linear || m) questions.push_back(truth_table(linear, m));
        }
        std::set<PointSet> distinct(questions.begin(), questions.end());
        require(distinct.size() == questions.size(), "duplicated formal query");
    }

    int minimum(PointSet points, int size) const {
        if (closing.contains(points)) return 1;
        return std::max(2, (size + 11) / 12);
    }

    bool fits(PointSet points, int leaves, bool root = false) {
        int size = std::popcount(points);
        if (size > 12 * leaves) return false;
        if (closing.contains(points)) return true;
        if (leaves < 2) return false;
        auto& memo = decisions.at(leaves);
        if (auto found = memo.find(points); found != memo.end()) return found->second;
        std::unordered_set<PointSet> partitions;
        for (PointSet truth : questions) {
            PointSet low = points & ~truth;
            PointSet high = points & truth;
            if (!low || !high) continue;
            int low_size = std::popcount(low), high_size = size - low_size;
            if ((low_size + 11) / 12 + (high_size + 11) / 12 > leaves) continue;
            if (low_size > high_size) {
                std::swap(low, high);
                std::swap(low_size, high_size);
            }
            int need_low = minimum(low, low_size), need_high = minimum(high, high_size);
            if (need_low + need_high > leaves) continue;
            if (!partitions.insert(std::min(low, high)).second) continue;
            if (root) ++root_splits;
            for (int budget = need_low; budget <= leaves - need_high; ++budget) {
                if (fits(low, budget) && fits(high, leaves - budget)) {
                    memo.emplace(points, true);
                    return true;
                }
            }
        }
        memo.emplace(points, false);
        return false;
    }
};

std::set<int> span(std::vector<int> generators) {
    std::set<int> result{0};
    for (int g : generators) {
        auto old = result;
        for (int m : old) result.insert(g ^ m);
    }
    return result;
}

int main() {
    const ClosingSets closing;
    audit_affine_graphs(closing);
    for (int a = 1; a < 16; ++a) for (int b = a + 1; b < 16; ++b) {
        if ((a ^ b) <= b) continue;
        Search pair(closing, span({31, a, b}));
        bool seven = pair.fits(full, 7, true);
        std::cout << "pair " << a << ' ' << b << ' ' << (a ^ b) << ' ' << pair.questions.size()
                  << ' ' << seven << ' ' << pair.root_splits << '\n';
    }
}
