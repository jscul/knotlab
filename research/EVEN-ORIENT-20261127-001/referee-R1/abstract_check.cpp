#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <map>
#include <numeric>
#include <stdexcept>
#include <unordered_map>
#include <unordered_set>
#include <vector>

// A cycle represents one failing pair, with fresh values on its opposite knots.
// Its cross-pair mask is one column of the parity constraints.
using Mask = std::uint32_t;
using CycleWord = std::array<int, 7>;
constexpr int max_knots = 7;
constexpr int max_cross_pairs = 21;
constexpr int max_corners = 28;

struct Cycle {
    std::array<int, 4> knots;
    std::array<int, 4> cross_pairs;
    Mask cross;
    Mask forward;
    Mask used_knots;
    std::array<int, 2> holding_pairs;
    bool cost;
};

template <std::size_t N>
struct BinaryBasis {
    std::array<Mask, N> pivots{};
    int rank = 0;

    bool add(Mask row) {
        while (row) {
            auto pivot = std::bit_width(row) - 1;
            if (!pivots[pivot]) {
                pivots[pivot] = row;
                ++rank;
                return true;
            }
            row ^= pivots[pivot];
        }
        return false;
    }
};

struct CrossPairUse {
    Mask cycles = 0;
    Mask forward_cycles = 0;
    std::array<int, 2> first_occurrences{};
    int count = 0;
};

struct Half {
    CycleWord choices{};
    Mask parity = 0;
    Mask knots = 0;
};

template <std::size_t N>
void print_array(const std::array<int, N>& values) {
    std::cout << '[';
    for (std::size_t i = 0; i < values.size(); ++i) {
        if (i) {
            std::cout << ',';
        }
        std::cout << values[i];
    }
    std::cout << ']';
}

template <std::size_t N>
void print_tally(const std::map<std::array<int, N>, std::uint64_t>& tally) {
    bool first = true;
    std::cout << '[';
    for (const auto& [key, count] : tally) {
        if (!first) {
            std::cout << ',';
        }
        first = false;
        std::cout << '[';
        for (auto value : key) {
            std::cout << value << ',';
        }
        std::cout << count << ']';
    }
    std::cout << ']';
}

class Census {
public:
    Census(int knots, int max_pairs) : knots_(knots), max_pairs_(max_pairs) {
        for (int u = 0; u < knots_; ++u) {
            for (int v = u + 1; v < knots_; ++v) {
                int index = cross_pairs_.size();
                pair_index_[u][v] = pair_index_[v][u] = index;
                cross_pairs_.push_back({u, v});
            }
        }
        for (int u = 0; u < knots_; ++u) {
            for (int v = u + 1; v < knots_; ++v) {
                for (int w = v + 1; w < knots_; ++w) {
                    for (int x = w + 1; x < knots_; ++x) {
                        std::array<int, 3> remaining{v, w, x};
                        do {
                            if (remaining.front() < remaining.back()) {
                                add_cycle({u, remaining[0], remaining[1], remaining[2]});
                            }
                        } while (std::next_permutation(remaining.begin(), remaining.end()));
                    }
                }
            }
        }
        prepare_permutations();
    }

    void run() {
        for (int size = 3; size <= max_pairs_; ++size) {
            size_ = size;
            top_.clear();
            const int split = size / 2;
            subsets({}, 0, 0, split, [&](const Half& half) {
                top_[half.parity].push_back(half);
            });
            for (auto& [parity, bucket] : top_) {
                std::sort(bucket.begin(), bucket.end(), [&](const Half& a, const Half& b) {
                    return a.choices[split - 1] < b.choices[split - 1];
                });
            }
            subsets({}, 0, split, size, [&](const Half& last) {
                const auto found = top_.find(last.parity);
                if (found == top_.end()) {
                    return;
                }
                auto first_later = std::lower_bound(
                    found->second.begin(), found->second.end(), last.choices[split],
                    [&](const Half& first, int index) { return first.choices[split - 1] < index; }
                );
                for (auto first = found->second.begin(); first != first_later; ++first) {
                    if ((first->knots | last.knots) != (1u << knots_) - 1) {
                        continue;
                    }
                    CycleWord choice = last.choices;
                    std::copy_n(first->choices.begin(), split, choice.begin());
                    examine(choice);
                }
            });
        }
        std::cout << "{\"knots\":" << knots_ << ",\"max_pairs\":" << max_pairs_;
        std::cout << ",\"tally\":";
        print_tally(tally_);
        std::cout << ",\"separation\":";
        print_tally(separation_);
        std::cout << ",\"higher_coverage\":";
        print_tally(higher_);
        std::cout << ",\"labels_in_orbits\":" << traced_labels_.size();
        std::cout << ",\"rejected_nonminimal\":" << nonminimal_;
        std::cout << ",\"sign_disagreements\":" << sign_disagreements_ << "}\n";
    }

private:
    int knots_;
    int max_pairs_;
    int size_ = 0;
    std::array<std::array<int, max_knots>, max_knots> pair_index_{};
    std::vector<std::array<int, 2>> cross_pairs_;
    std::vector<Cycle> cycles_;
    std::vector<std::vector<int>> permutation_images_;
    std::unordered_map<Mask, std::vector<Half>> top_;
    std::unordered_set<std::uint64_t> traced_labels_;
    std::map<std::array<int, 8>, std::uint64_t> tally_;
    std::map<std::array<int, 7>, std::uint64_t> separation_;
    std::map<std::array<int, 5>, std::uint64_t> higher_;
    std::uint64_t nonminimal_ = 0;
    std::uint64_t sign_disagreements_ = 0;

    void prepare_permutations() {
        std::unordered_map<Mask, int> by_cross_pairs;
        for (int i = 0; i < static_cast<int>(cycles_.size()); ++i) {
            if (!by_cross_pairs.emplace(cycles_[i].cross, i).second) {
                throw std::logic_error("two cyclic orders have the same cross pairs");
            }
        }
        std::vector<int> perm(knots_);
        std::iota(perm.begin(), perm.end(), 0);
        do {
            std::vector<int> images;
            for (const auto& cycle : cycles_) {
                Mask cross = 0;
                for (int i = 0; i < 4; ++i) {
                    const int u = perm[cycle.knots[i]];
                    const int v = perm[cycle.knots[(i + 1) % 4]];
                    cross |= 1u << pair_index_[u][v];
                }
                images.push_back(by_cross_pairs.at(cross));
            }
            permutation_images_.push_back(std::move(images));
        } while (std::next_permutation(perm.begin(), perm.end()));
    }

    std::uint64_t key(const CycleWord& choice) const {
        std::uint64_t value = 0;
        for (int i = 0; i < size_; ++i) {
            // There are at most 105 cycles. The high extra bit makes lengths
            // distinct and leaves each seven-bit cycle index unambiguous.
            value = (value << 7) | choice[i];
        }
        return value | (std::uint64_t{1} << (7 * size_));
    }

    void add_cycle(std::array<int, 4> knots) {
        Cycle cycle{};
        cycle.knots = knots;
        for (int i = 0; i < 4; ++i) {
            const int u = knots[i];
            const int v = knots[(i + 1) % 4];
            const int pair = pair_index_[u][v];
            cycle.cross_pairs[i] = pair;
            cycle.cross |= 1u << pair;
            cycle.used_knots |= 1u << u;
            if (u < v) {
                cycle.forward |= 1u << pair;
            }
        }
        cycle.holding_pairs = {pair_index_[knots[0]][knots[2]], pair_index_[knots[1]][knots[3]]};
        auto between_first_holders = [&](int w) { return knots[0] < w && w < knots[2]; };
        cycle.cost = between_first_holders(knots[1]) != between_first_holders(knots[3]);
        cycles_.push_back(cycle);
    }

    template <class Visit>
    void subsets(Half half, int least, int pos, int stop, Visit&& visit) const {
        if (pos == stop) {
            visit(half);
            return;
        }
        const int left_to_choose = stop - pos;
        const int last = static_cast<int>(cycles_.size()) - left_to_choose;
        for (int i = least; i <= last; ++i) {
            Half next = half;
            next.choices[pos] = i;
            next.parity ^= cycles_[i].cross;
            next.knots |= cycles_[i].used_knots;
            subsets(next, i + 1, pos + 1, stop, visit);
        }
    }

    void examine(const CycleWord& choice) {
        BinaryBasis<max_cross_pairs> basis;
        for (int i = 0; i < size_; ++i) {
            basis.add(cycles_[choice[i]].cross);
        }
        if (basis.rank != size_ - 1) {
            ++nonminimal_;
            return;
        }

        std::array<CrossPairUse, max_cross_pairs> cross{};
        std::array<int, max_cross_pairs> holdings{};
        bool sign = false;
        bool forward_parity = false;
        int maximum_coverage = 0;
        for (int i = 0; i < size_; ++i) {
            const Cycle& cycle = cycles_[choice[i]];
            sign ^= cycle.cost;
            forward_parity ^= std::popcount(cycle.forward) % 2;
            for (int pair : cycle.holding_pairs) {
                ++holdings[pair];
            }
            for (int j = 0; j < 4; ++j) {
                const int pair = cycle.cross_pairs[j];
                CrossPairUse& uses = cross[pair];
                uses.cycles |= 1u << i;
                if (cycle.forward & (1u << pair)) {
                    uses.forward_cycles |= 1u << i;
                }
                if (uses.count < 2) {
                    uses.first_occurrences[uses.count] = 4 * i + j;
                }
                ++uses.count;
                maximum_coverage = std::max(maximum_coverage, uses.count);
            }
        }

        int doubled_pairs = 0;
        Mask doubled_knots = 0;
        for (std::size_t i = 0; i < cross_pairs_.size(); ++i) {
            if (holdings[i] > 1) {
                ++doubled_pairs;
                auto [u, v] = cross_pairs_[i];
                doubled_knots |= (1u << u) | (1u << v);
            }
        }
        sign_disagreements_ += sign != forward_parity;
        if (maximum_coverage > 2) {
            const bool orientable = brute_balance(cross);
            auto& count = higher_[{size_, maximum_coverage, orientable, sign, doubled_pairs}];
            ++count;
            const bool small_balanced_control = knots_ == 5 && size_ == 5 && orientable;
            if (count == 1 && !sign && (!orientable || small_balanced_control)) {
                print_witness(choice, maximum_coverage, doubled_pairs, orientable);
            }
            return;
        }

        // The constant is placed below all reversal variables. A row with
        // only the constant pivot signals an inconsistent balance system.
        BinaryBasis<8> reversal;
        bool same_order_parity = false;
        for (const auto& uses : cross) {
            if (uses.count == 0) {
                continue;
            }
            if (uses.count != 2) {
                throw std::logic_error("unexpected coverage below two");
            }
            const bool same_order = std::popcount(uses.forward_cycles) != 1;
            same_order_parity ^= same_order;
            // Use the low bit for the constant to prioritize variable pivots.
            reversal.add((uses.cycles << 1) | same_order);
        }
        const bool orientable = reversal.pivots[0] == 0;
        sign_disagreements_ += sign != same_order_parity;

        const auto [separated_knots, original_bipartite, separated_bipartite] =
            separation_data(choice, cross);
        const int euler = separated_knots - size_;
        ++tally_[{knots_, size_, euler, orientable, sign, doubled_pairs > 0,
                   std::popcount(doubled_knots) == knots_, original_bipartite}];
        ++separation_[{size_, separated_knots, orientable, sign, original_bipartite,
                        separated_bipartite, doubled_pairs}];
        if (!traced_labels_.contains(key(choice))) {
            const auto already_traced = traced_labels_.size();
            for (const auto& perm : permutation_images_) {
                CycleWord image;
                image.fill(cycles_.size());
                for (int i = 0; i < size_; ++i) {
                    image[i] = perm[choice[i]];
                }
                std::sort(image.begin(), image.end());
                traced_labels_.insert(key(image));
            }
            print_class(choice, traced_labels_.size() - already_traced, separated_knots,
                        orientable, sign, doubled_pairs, original_bipartite,
                        separated_bipartite);
        }
    }

    bool brute_balance(const std::array<CrossPairUse, max_cross_pairs>& cross) const {
        for (Mask flip = 0; flip < (1u << (size_ - 1)); ++flip) {
            bool balanced = true;
            for (const auto& uses : cross) {
                const int forward = std::popcount(uses.forward_cycles ^ (flip & uses.cycles));
                if (2 * forward != uses.count) {
                    balanced = false;
                    break;
                }
            }
            if (balanced) {
                return true;
            }
        }
        return false;
    }

    static bool bipartite(const std::array<Mask, max_corners>& adjacency, int knots) {
        Mask remaining = (1u << knots) - 1;
        while (remaining) {
            Mask next = remaining & -remaining;
            Mask opposite = 0;
            Mask same = 0;
            while (next) {
                same |= next;
                Mask neighbors = 0;
                for (Mask todo = next; todo; todo &= todo - 1) {
                    neighbors |= adjacency[std::countr_zero(todo)];
                }
                if (neighbors & same) {
                    return false;
                }
                next = neighbors & ~opposite;
                std::swap(same, opposite);
            }
            remaining &= ~(same | opposite);
        }
        return true;
    }

    std::array<int, 3> separation_data(
        const CycleWord& choice, const std::array<CrossPairUse, max_cross_pairs>& cross
    ) const {
        std::array<int, max_corners> parent;
        std::iota(parent.begin(), parent.end(), 0);
        auto root = [&](int node) {
            while (parent[node] != node) {
                node = parent[node];
            }
            return node;
        };
        auto corners_in_increasing_order = [&](int occurrence) {
            int cycle_position = occurrence / 4;
            int j = occurrence % 4;
            int next = (j + 1) % 4;
            if (cycles_[choice[cycle_position]].knots[j] > cycles_[choice[cycle_position]].knots[next]) {
                std::swap(j, next);
            }
            return std::array<int, 2>{4 * cycle_position + j, 4 * cycle_position + next};
        };
        std::array<Mask, max_corners> original_adj{};
        for (std::size_t i = 0; i < cross_pairs_.size(); ++i) {
            if (!cross[i].count) {
                continue;
            }
            const auto [u, v] = cross_pairs_[i];
            original_adj[u] |= 1u << v;
            original_adj[v] |= 1u << u;
            const auto [u1, v1] = corners_in_increasing_order(cross[i].first_occurrences[0]);
            const auto [u2, v2] = corners_in_increasing_order(cross[i].first_occurrences[1]);
            parent[root(u1)] = root(u2);
            parent[root(v1)] = root(v2);
        }
        std::array<int, max_corners> labels;
        labels.fill(-1);
        int separated_knots = 0;
        for (int i = 0; i < 4 * size_; ++i) {
            const int r = root(i);
            if (labels[r] == -1) {
                labels[r] = separated_knots++;
            }
        }
        std::array<Mask, max_corners> separated_adj{};
        for (int i = 0; i < size_; ++i) {
            for (int j = 0; j < 4; ++j) {
                const int a = labels[root(4 * i + j)];
                const int b = labels[root(4 * i + (j + 1) % 4)];
                separated_adj[a] |= 1u << b;
                separated_adj[b] |= 1u << a;
            }
        }
        return {separated_knots, bipartite(original_adj, knots_),
                bipartite(separated_adj, separated_knots)};
    }

    void print_cycles(const CycleWord& choice) const {
        std::cout << ",\"cycles\":[";
        for (int i = 0; i < size_; ++i) {
            if (i) {
                std::cout << ',';
            }
            print_array(cycles_[choice[i]].knots);
        }
        std::cout << "]}\n";
    }

    void print_witness(const CycleWord& choice, int coverage, int doubled, bool orientable) const {
        std::cout << "{\"kind\":\"higher_coverage_witness\",\"knots\":" << knots_
                  << ",\"coverage\":" << coverage << ",\"doubled_pairs\":" << doubled
                  << ",\"orientable\":" << orientable;
        print_cycles(choice);
    }

    void print_class(const CycleWord& choice, std::size_t orbit, int separated_knots, bool orientable,
                     bool sign, int doubled, bool original_bipartite, bool separated_bipartite) const {
        std::cout << "{\"kind\":\"class\",\"knots\":" << knots_ << ",\"pairs\":" << size_
                  << ",\"labelled_copies\":" << orbit << ",\"separated_knots\":" << separated_knots
                  << ",\"orientable\":" << orientable << ",\"sign\":" << sign
                  << ",\"doubled_pairs\":" << doubled << ",\"original_two_colourable\":"
                  << original_bipartite << ",\"separated_two_colourable\":" << separated_bipartite;
        print_cycles(choice);
    }
};

int main(int argc, char* argv[]) {
    const int maximum_knots = argc == 2 ? std::atoi(argv[1]) : max_knots;
    if (argc > 2 || maximum_knots < 4 || maximum_knots > max_knots) {
        std::cerr << "usage: abstract_check_native [maximum knots, from four to seven]\n";
        return 2;
    }
    for (int knots = 4; knots <= maximum_knots; ++knots) {
        Census(knots, 7).run();
    }
}
