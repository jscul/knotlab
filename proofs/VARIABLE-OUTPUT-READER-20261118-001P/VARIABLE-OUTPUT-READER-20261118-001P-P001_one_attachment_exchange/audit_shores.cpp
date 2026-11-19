// Independent finite-state check of every size-six shore through the fourth site.
#include <algorithm>
#include <array>
#include <bit>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <limits>
#include <map>
#include <set>
#include <unordered_map>
#include <utility>
#include <vector>

namespace {

using Word = std::uint64_t;
using Index = std::uint32_t;
constexpr int slots = 9;
constexpr int absent = 15;
constexpr int mask_count = 1 << slots;
constexpr Index no_index = std::numeric_limits<Index>::max();
using Key = std::array<Word, 5>;
using Relabel = std::array<int, slots>;

int bit(int i) { return 1 << i; }
int count(int mask) { return std::popcount(static_cast<unsigned>(mask)); }

template<class F>
void each(Word mask, F visit) {
    while (mask) {
        visit(std::countr_zero(mask));
        mask &= mask - 1;
    }
}

struct Subsets {
    std::array<int, 36> pairs{};
    std::array<int, 84> triples{};
    std::array<int, mask_count> pair_index{}, triple_index{};

    Subsets() {
        int p = 0, q = 0;
        for (int m = 0; m < mask_count; ++m) {
            if (count(m) == 2) pair_index[m] = p, pairs[p++] = m;
            if (count(m) == 3) triple_index[m] = q, triples[q++] = m;
        }
        assert(p == 36 && q == 84);
    }
} subsets;

struct Front {
    int n = 0, births = 0, high = absent, child = absent, spending_arity = 0, third_arity = 0, colors = 0;
    std::array<int, slots> loose{};
    Word meetings = 0, retired_pairs = 0;
    std::array<Word, 2> retired_triples{};

    static bool has_pair(Word relation, int m) { return relation >> subsets.pair_index[m] & 1; }
    bool retired_three(int m) const {
        int i = subsets.triple_index[m];
        return retired_triples[i / 64] >> (i % 64) & 1;
    }
    void add_retired(int neighbors) {
        for (int m = neighbors; m; m = neighbors & (m - 1)) {
            if (count(m) == 2) retired_pairs |= Word{1} << subsets.pair_index[m];
            if (count(m) == 3) {
                int i = subsets.triple_index[m];
                retired_triples[i / 64] |= Word{1} << (i % 64);
            }
        }
    }
    std::array<int, slots> neighbors() const {
        std::array<int, slots> result{};
        each(meetings, [&](int k) {
            each(subsets.pairs[k], [&](int i) { result[i] |= subsets.pairs[k] ^ bit(i); });
        });
        return result;
    }
    int loose_total() const {
        int total = 0;
        for (int i = 0; i < n; ++i) total += loose[i];
        return total;
    }
    bool legal(int parents, const std::array<int, slots>& adjacency) const {
        int arity = count(parents);
        if (arity == 1) return true;
        for (int m = parents; m; m = parents & (m - 1)) {
            if (count(m) != 2) continue;
            int a = std::countr_zero(static_cast<unsigned>(m));
            int b = std::countr_zero(static_cast<unsigned>(m ^ bit(a)));
            if (!(adjacency[a] & adjacency[b]) && !has_pair(retired_pairs, m)) return false;
        }
        int across = (1 << n) - 1;
        each(parents, [&](int i) { across &= adjacency[i]; });
        return arity == 2 || !(across || retired_three(parents));
    }
    bool live() const {
        auto adjacency = neighbors();
        for (int m : subsets.triples) {
            if (m >= bit(n)) break;
            if (legal(m, adjacency)) return true;
        }
        return false;
    }
    Key packed() const {
        Word meta = n | (births << 4) | (high << 7) | (child << 11) | (spending_arity << 15) |
                    (third_arity << 17) | (colors << 19);
        for (int i = 0; i < n; ++i) meta |= Word(loose[i]) << (28 + 2 * i);
        return {meta, meetings, retired_pairs, retired_triples[0], retired_triples[1]};
    }
    static Front unpack(const Key& key) {
        auto a = key[0];
        Front f;
        f.n = a & 15; f.births = (a >> 4) & 7; f.high = (a >> 7) & 15;
        f.child = (a >> 11) & 15; f.spending_arity = (a >> 15) & 3;
        f.third_arity = (a >> 17) & 3; f.colors = (a >> 19) & 511;
        for (int i = 0; i < f.n; ++i) f.loose[i] = (a >> (28 + 2 * i)) & 3;
        f.meetings = key[1]; f.retired_pairs = key[2]; f.retired_triples = {key[3], key[4]};
        return f;
    }
};

int image(int m, const Relabel& permutation) {
    int result = 0;
    each(m, [&](int i) { if (permutation[i] != absent) result |= bit(permutation[i]); });
    return result;
}

void map_relations(const Front& old, Front& fresh, const Relabel& map, int kept) {
    auto transfer_pairs = [&](Word input) {
        Word output = 0;
        each(input, [&](int id) {
            int m = subsets.pairs[id];
            if ((m & kept) == m) output |= Word{1} << subsets.pair_index[image(m, map)];
        });
        return output;
    };
    fresh.meetings = transfer_pairs(old.meetings);
    fresh.retired_pairs = transfer_pairs(old.retired_pairs);
    for (int half = 0; half < 2; ++half) {
        each(old.retired_triples[half], [&](int id) {
            int m = subsets.triples[64 * half + id];
            if ((m & kept) != m) return;
            int target = subsets.triple_index[image(m, map)];
            fresh.retired_triples[target / 64] |= Word{1} << (target % 64);
        });
    }
}

Front relabel(const Front& input, const Relabel& permutation) {
    Front output;
    output.n = input.n;
    output.births = input.births;
    output.high = input.high == absent ? absent : permutation[input.high];
    output.child = input.child == absent ? absent : permutation[input.child];
    output.spending_arity = input.spending_arity;
    output.third_arity = input.third_arity;
    output.colors = image(input.colors, permutation);
    for (int i = 0; i < input.n; ++i) output.loose[permutation[i]] = input.loose[i];
    map_relations(input, output, permutation, bit(input.n) - 1);
    return output;
}

std::pair<Key, Relabel> canonical(const Front& f) {
    // Color refinement only limits the permutations. The full packed relations
    // decide equality. Within a class we can skip exact transposition twins.
    auto neighbors = f.neighbors();
    std::array<int, slots> color{};
    for (int i = 0; i < f.n; ++i)
        color[i] = (((f.loose[i] * 2 + (f.colors >> i & 1)) * 2 + (i == f.high)) * 2 + (i == f.child));
    std::array<int, slots> order{};
    for (int i = 0; i < f.n; ++i) order[i] = i;
    int last_classes = 0;
    for (;;) {
        using Signature = std::array<int, 2 * slots + 2>;
        std::array<Signature, slots> signatures{};
        for (int i = 0; i < f.n; ++i) {
            auto& s = signatures[i];
            s[0] = color[i];
            if (last_classes) {
                for (int j = 0; j < f.n; ++j) if (i != j) {
                    s[1 + color[j]] += neighbors[i] >> j & 1;
                    s[1 + slots + color[j]] += Front::has_pair(f.retired_pairs, bit(i) | bit(j));
                }
                for (int m : subsets.triples) {
                    if (m >= bit(f.n)) break;
                    s.back() += (m & bit(i)) && f.retired_three(m);
                }
            }
        }
        std::sort(order.begin(), order.begin() + f.n, [&](int a, int b) { return signatures[a] < signatures[b]; });
        int classes = 1;
        color[order[0]] = 0;
        for (int i = 1; i < f.n; ++i) {
            if (signatures[order[i - 1]] != signatures[order[i]]) ++classes;
            color[order[i]] = classes - 1;
        }
        if (classes == last_classes || classes == f.n) break;
        last_classes = classes;
    }
    std::array<int, slots> class_mask{}, twins{};
    for (int i = 0; i < f.n; ++i) class_mask[color[i]] |= bit(i);
    for (int i = 0; i < f.n; ++i) for (int j = i + 1; j < f.n; ++j) if (color[i] == color[j]) {
        if ((neighbors[i] ^ neighbors[j]) & ~(bit(i) | bit(j))) continue;
        bool same = true;
        for (int a = 0; a < f.n && same; ++a) if (a != i && a != j) {
            same = Front::has_pair(f.retired_pairs, bit(a) | bit(i)) ==
                   Front::has_pair(f.retired_pairs, bit(a) | bit(j));
            for (int b = a + 1; b < f.n && same; ++b) if (b != i && b != j)
                same = f.retired_three(bit(a) | bit(b) | bit(i)) == f.retired_three(bit(a) | bit(b) | bit(j));
        }
        if (same) twins[i] |= bit(j), twins[j] |= bit(i);
    }
    Key best{};
    best.fill(~Word{0});
    Relabel permutation{}, best_map{};
    auto search = [&](auto&& recurse, int next, int used) -> void {
        if (next == f.n) {
            Key current = relabel(f, permutation).packed();
            if (current < best) best = current, best_map = permutation;
            return;
        }
        int examined = 0;
        each(class_mask[color[order[next]]] & ~used, [&](int j) {
            if (examined & twins[j]) return;
            examined |= bit(j);
            permutation[j] = next;
            recurse(recurse, next + 1, used | bit(j));
        });
    };
    search(search, 0, 0);
    return {best, best_map};
}

struct Move {
    Index destination = no_index;
    unsigned short inputs = 0;
    unsigned char fresh = 0, newborn = 0;
    bool is_high = false;
    Relabel old_to_next{};
};

std::pair<Key, Move> advance(const Front& f, const std::array<int, slots>& adjacency, int parents, int fresh) {
    Front g;
    Relabel compact{};
    compact.fill(absent);
    int kept = 0;
    for (int i = 0; i < f.n; ++i) {
        int remaining = f.loose[i] - (parents >> i & 1);
        if (remaining > 0) {
            kept |= bit(i);
            compact[i] = g.n;
            g.loose[g.n++] = remaining;
        }
    }
    int newborn = g.n++;
    assert(g.n <= slots);
    int parent_color = f.colors >> std::countr_zero(static_cast<unsigned>(parents)) & 1;
    assert(parent_color ? (parents & f.colors) == parents : !(parents & f.colors));
    g.colors = image(f.colors, compact) | ((1 - parent_color) << newborn);
    g.loose[newborn] = fresh;
    int arity = count(parents);
    g.births = f.births + (fresh == 3);
    g.third_arity = fresh == 3 && g.births == 3 ? arity : f.third_arity;
    bool high = fresh == 3 && g.births == 4;
    g.high = high ? newborn : f.high == absent ? absent : compact[f.high];
    bool spend = f.high != absent && (parents & bit(f.high));
    g.spending_arity = spend ? arity : f.spending_arity;
    g.child = spend ? newborn : f.child == absent ? absent : compact[f.child];
    map_relations(f, g, compact, kept);
    each(parents & kept, [&](int i) { g.meetings |= Word{1} << subsets.pair_index[bit(compact[i]) | bit(newborn)]; });
    each((bit(f.n) - 1) & ~kept, [&](int i) {
        g.add_retired(image(adjacency[i], compact) | bit(newborn));
    });
    assert(g.loose_total() <= 9);
    auto [key, final_map] = canonical(g);
    Move move;
    move.inputs = parents;
    move.fresh = fresh;
    move.newborn = final_map[newborn];
    move.is_high = high;
    move.old_to_next.fill(absent);
    for (int i = 0; i < f.n; ++i) if (compact[i] != absent) move.old_to_next[i] = final_map[compact[i]];
    return {key, move};
}

struct KeyHash {
    std::size_t operator()(const Key& key) const {
        Word result = 0x9e3779b97f4a7c15ull;
        for (auto word : key) result ^= word + 0x9e3779b97f4a7c15ull + (result << 6) + (result >> 2);
        return result;
    }
};

struct Node {
    Key key;
    std::vector<Move> moves;
    bool target = false;
};

std::vector<Node> formation() {
    Front seed;
    seed.n = 1;
    seed.loose[0] = 3;
    Key first = canonical(seed).first;
    std::vector<Node> nodes{{first, {}, false}};
    std::unordered_map<Key, Index, KeyHash> lookup{{first, 0}};
    for (Index i = 0; i < nodes.size(); ++i) {
        Front f = Front::unpack(nodes[i].key);
        nodes[i].target = f.spending_arity && f.live();
        auto neighbors = f.neighbors();
        for (int parents = 1; parents < bit(f.n); ++parents) {
            int arity = count(parents);
            if (arity > 3 || (f.spending_arity && (parents & bit(f.high)))) continue;
            bool two = f.births >= 2 && arity >= 2;
            bool three = f.births < 2 ? arity == 1 : f.births == 2 || (f.births == 3 && arity == 3);
            if ((!two && !three) || !f.legal(parents, neighbors)) continue;
            for (int fresh : {2, 3}) {
                if (!(fresh == 2 ? two : three)) continue;
                auto [key, move] = advance(f, neighbors, parents, fresh);
                auto [position, inserted] = lookup.try_emplace(key, nodes.size());
                if (inserted) nodes.push_back({key, {}, false});
                move.destination = position->second;
                nodes[i].moves.push_back(move);
            }
        }
    }
    return nodes;
}

std::vector<int> trim(const std::vector<Node>& nodes) {
    std::vector<std::vector<Index>> parents(nodes.size());
    std::vector<int> label(nodes.size(), -1);
    std::vector<Index> queue;
    auto insert = [&](Index i) {
        if (label[i] == -1) label[i] = queue.size(), queue.push_back(i);
    };
    for (Index i = 0; i < nodes.size(); ++i) {
        if (nodes[i].target) insert(i);
        for (const auto& move : nodes[i].moves) parents[move.destination].push_back(i);
    }
    for (std::size_t i = 0; i < queue.size(); ++i)
        for (Index p : parents[queue[i]]) insert(p);
    return label;
}

struct AuditState {
    Index node, previous;
    unsigned short inside, move;
    unsigned char crossings, flags;
    bool newborn_inside;
};

struct Replay {
    std::vector<std::vector<int>> rows;
    std::vector<int> selected, boundary, adjacent_holders, separate_holders;
    std::vector<std::array<int, 3>> legal_triples;
    int high = -1, child = -1;
};

Replay replay(const std::vector<Node>& nodes, const std::vector<AuditState>& states, Index final) {
    std::vector<Index> path;
    for (Index i = final; states[i].previous != no_index; i = states[i].previous) path.push_back(i);
    std::reverse(path.begin(), path.end());
    Index current = path.empty() ? final : states[path.front()].previous;
    Replay result;
    result.rows.push_back({0, 1, 2});
    if (states[current].inside) result.selected.push_back(0);
    std::vector<std::set<int>> full_neighbors(1);
    std::vector<int> full_color{0};
    std::array<std::vector<int>, slots> loose;
    loose[0] = {0, 1, 2};
    Relabel origin{};
    int next_name = 3;
    for (Index id : path) {
        const auto& state = states[id];
        const auto& move = nodes[states[current].node].moves[state.move];
        std::vector<int> row, parents;
        int born = result.rows.size();
        each(move.inputs, [&](int i) {
            assert(!loose[i].empty());
            row.push_back(loose[i].back());
            loose[i].pop_back();
            parents.push_back(origin[i]);
        });
        for (std::size_t i = 0; i < parents.size(); ++i) for (std::size_t j = i+1; j < parents.size(); ++j) {
            bool shared = false;
            for (int w : full_neighbors[parents[i]]) shared |= full_neighbors[parents[j]].contains(w);
            assert(shared);
        }
        if (parents.size() == 3) for (int w : full_neighbors[parents[0]])
            assert(!(full_neighbors[parents[1]].contains(w) && full_neighbors[parents[2]].contains(w)));
        full_neighbors.emplace_back(parents.begin(), parents.end());
        for (int p : parents) full_neighbors[p].insert(born);
        int child_color = 1 - full_color[parents.front()];
        for (int p : parents) assert(full_color[p] != child_color);
        full_color.push_back(child_color);
        if (move.is_high) result.high = born;
        if (std::find(parents.begin(), parents.end(), result.high) != parents.end()) {
            assert(result.child == -1);
            result.child = born;
        }
        std::array<std::vector<int>, slots> following;
        Relabel next_origin{};
        for (int i = 0; i < slots; ++i) if (move.old_to_next[i] != absent) {
            int j = move.old_to_next[i];
            following[j] = std::move(loose[i]);
            next_origin[j] = origin[i];
        }
        for (int i = 0; i < move.fresh; ++i) {
            following[move.newborn].push_back(next_name);
            row.push_back(next_name++);
        }
        next_origin[move.newborn] = born;
        loose = std::move(following);
        origin = next_origin;
        if (state.newborn_inside) result.selected.push_back(born);
        std::sort(row.begin(), row.end());
        result.rows.push_back(row);
        current = id;
    }
    std::set<int> cut;
    for (int i : result.selected) for (int b : result.rows[i])
        if (!cut.erase(b)) cut.insert(b);
    result.boundary.assign(cut.begin(), cut.end());
    assert(result.boundary.size() == 6);
    Front front = Front::unpack(nodes[states[final].node].key);
    assert(origin[front.high] == result.high);
    assert(front.child == absent || origin[front.child] == result.child);
    for (int i = 0; i < front.n; ++i) {
        assert(front.loose[i] == static_cast<int>(loose[i].size()));
        assert((front.colors >> i & 1) == full_color[origin[i]]);
    }
    for (int i = 0; i < front.n; ++i) for (int j = i+1; j < front.n; ++j) for (int k = j+1; k < front.n; ++k) {
        const auto& a = full_neighbors[origin[i]];
        const auto& b = full_neighbors[origin[j]];
        const auto& c = full_neighbors[origin[k]];
        bool ab = false, ac = false, bc = false, common = false;
        for (int w : a) {
            ab |= b.contains(w);
            ac |= c.contains(w);
            common |= b.contains(w) && c.contains(w);
        }
        for (int w : b) bc |= c.contains(w);
        if (ab && ac && bc && !common) for (int x : loose[i]) for (int y : loose[j]) for (int z : loose[k]) {
            std::array<int, 3> proposal{x,y,z};
            std::sort(proposal.begin(), proposal.end());
            result.legal_triples.push_back(proposal);
        }
    }
    assert(!result.legal_triples.empty());
    std::sort(result.legal_triples.begin(), result.legal_triples.end());
    each(states[final].inside, [&](int i) {
        if ((front.colors >> i & 1) == (front.colors >> front.high & 1)) return;
        auto& list = full_neighbors[result.high].contains(origin[i]) ? result.adjacent_holders : result.separate_holders;
        list.push_back(origin[i]);
        for (int b : loose[i]) assert(cut.contains(b));
    });
    for (int b : loose[front.high]) assert(cut.contains(b));
    std::set<int> included(result.selected.begin(), result.selected.end());
    int ordinary_crossings = 0;
    bool incoming = false;
    for (int i : included) for (int j : full_neighbors[i]) if (!included.contains(j)) {
        ++ordinary_crossings;
        incoming |= j < i;
    }
    const auto& end = states[final];
    assert(ordinary_crossings == end.crossings);
    assert(incoming == bool(end.flags & 1));
    assert((included.size() != result.rows.size()) == bool(end.flags & 2));
    return result;
}

template<class V>
void json_list(const V& values) {
    std::cout << '[';
    bool first = true;
    for (auto x : values) {
        if (!first) std::cout << ',';
        first = false;
        std::cout << x;
    }
    std::cout << ']';
}

void print_replay(const Replay& r) {
    std::cout << "{\"high\":" << r.high << ",\"child\":" << r.child << ",\"chronological_rows\":[";
    bool first = true;
    for (const auto& row : r.rows) {
        if (!first) std::cout << ',';
        first = false;
        json_list(row);
    }
    std::cout << "],\"selected_sites\":"; json_list(r.selected);
    std::cout << ",\"boundary\":"; json_list(r.boundary);
    std::cout << ",\"adjacent_holders\":"; json_list(r.adjacent_holders);
    std::cout << ",\"nonadjacent_holders\":"; json_list(r.separate_holders);
    std::cout << ",\"legal_triples\":[";
    first = true;
    for (const auto& mark : r.legal_triples) {
        if (!first) std::cout << ',';
        first = false;
        json_list(mark);
    }
    std::cout << "]}";
}

int audit() {
    const auto nodes = formation();
    const auto label = trim(nodes);
    int retained = *std::max_element(label.begin(), label.end()) + 1;
    assert(label[0] >= 0);
    std::cerr << "Formation states " << nodes.size() << ", co-accessible " << retained << '\n';
    std::vector<std::array<Index, mask_count>> visited(retained);
    std::vector<AuditState> states;
    auto add = [&](AuditState state) {
        Index flag = Index{1} << (state.crossings + 5 * state.flags);
        auto& seen = visited[label[state.node]][state.inside];
        if (seen & flag) return;
        seen |= flag;
        states.push_back(state);
    };
    // The flags record any entering ordinary meeting (1) and any omitted site (2).
    // Both initial memberships are allowed. No parent-closure pruning is used.
    add({0, no_index, 1, 0, 0, 0, true});
    add({0, no_index, 0, 0, 0, 2, false});
    std::array<std::uint64_t, 4> shore_flags{};
    std::map<std::array<int, 4>, int> profiles;
    std::uint64_t transitions = 0, qualifying = 0, with_adjacent = 0, with_separate = 0, violations = 0;
    std::uint64_t one_child_output = 0, one_child_only_opposite_holder = 0;
    std::uint64_t live_cuts_through_high_below_six = 0;
    std::vector<Index> qualifiers;
    std::set<Index> qualified_nodes;
    for (Index index = 0; index < states.size(); ++index) {
        const AuditState state = states[index];
        const Node& node = nodes[state.node];
        if (node.target) {
            Front f = Front::unpack(node.key);
            int boundary = state.crossings;
            each(state.inside, [&](int j) { boundary += f.loose[j]; });
            live_cuts_through_high_below_six += boundary < 6;
            if (boundary == 6) {
                int color = f.colors >> f.high & 1;
                int other_color = color ? (bit(f.n) - 1) ^ f.colors : f.colors;
                int candidates = state.inside & other_color;
                if (candidates) {
                    int adj = f.neighbors()[f.high];
                    int child_loose = f.child == absent ? 0 : f.loose[f.child];
                    ++qualifying;
                    qualifiers.push_back(index);
                    qualified_nodes.insert(state.node);
                    ++shore_flags[state.flags];
                    ++profiles[{f.third_arity, f.loose_total(), f.spending_arity, child_loose}];
                    with_adjacent += bool(candidates & adj);
                    with_separate += bool(candidates & ~adj);
                    if (child_loose == 1) {
                        ++one_child_output;
                        one_child_only_opposite_holder += other_color == bit(f.child);
                    }
                    violations += f.loose_total() != 6 || f.spending_arity != 3 || child_loose == 0;
                }
            }
        }
        for (std::size_t move_id = 0; move_id < node.moves.size(); ++move_id) {
            const Move& move = node.moves[move_id];
            if (label[move.destination] < 0) continue;
            for (bool side : {false, true}) {
                if (!side && move.is_high) continue;
                int altered = move.inputs & (side ? ~state.inside : state.inside);
                int cost = state.crossings + count(altered);
                // Two outputs of the future or current high site must be loose
                // on every target shore. At most four ordinary crossings fit.
                if (cost > 4) continue;
                int inside = image(state.inside, move.old_to_next) | (side ? bit(move.newborn) : 0);
                int flags = state.flags | (side && altered ? 1 : 0) | (!side ? 2 : 0);
                ++transitions;
                add({move.destination, index, static_cast<unsigned short>(inside), static_cast<unsigned short>(move_id),
                     static_cast<unsigned char>(cost), static_cast<unsigned char>(flags), side});
            }
        }
    }
    std::uint64_t unmarked_edges = 0, live_sources = 0;
    for (const auto& n : nodes) unmarked_edges += n.moves.size(), live_sources += n.target;
    std::cout << "{\n  \"unmarked_states\":" << nodes.size() << ",\n  \"unmarked_transitions\":" << unmarked_edges
              << ",\n  \"unmarked_live_one_spent_states\":" << live_sources << ",\n  \"coaccessible_states\":" << retained
              << ",\n  \"marked_states\":" << states.size() << ",\n  \"marked_transitions\":" << transitions
              << ",\n  \"live_cuts_through_high_below_six\":" << live_cuts_through_high_below_six
              << ",\n  \"qualifying_marked_states\":" << qualifying << ",\n  \"different_unmarked_qualifiers\":" << qualified_nodes.size()
              << ",\n  \"qualifying_with_adjacent_holder\":" << with_adjacent << ",\n  \"qualifying_with_nonadjacent_holder\":" << with_separate
              << ",\n  \"qualifying_when_child_has_one_loose_output\":" << one_child_output
              << ",\n  \"of_those_child_is_the_only_loose_holder_of_attachment_color\":" << one_child_only_opposite_holder
              << ",\n  \"marked_qualifiers_by_incoming_and_proper_flags\":";
    json_list(shore_flags);
    std::cout << ",\n  \"profiles_third_arity_loose_spending_arity_child_loose_count\":[";
    bool first = true;
    for (const auto& [p, n] : profiles) {
        if (!first) std::cout << ',';
        first = false;
        std::cout << '[' << p[0] << ',' << p[1] << ',' << p[2] << ',' << p[3] << ',' << n << ']';
    }
    std::cout << "],\n  \"violations\":" << violations << ",\n  \"shortest_replay_for_each_qualifier\":[\n    ";
    first = true;
    for (Index index : qualifiers) {
        if (!first) std::cout << ",\n    ";
        first = false;
        print_replay(replay(nodes, states, index));
    }
    std::cout << "\n  ]\n}\n";
    return violations || live_cuts_through_high_below_six || !with_adjacent || !with_separate;
}

} // namespace

int main() { return audit(); }
