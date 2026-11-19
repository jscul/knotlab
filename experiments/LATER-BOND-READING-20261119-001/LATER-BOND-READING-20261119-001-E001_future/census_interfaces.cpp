// Exact pair and triple minima for split cores with independent attachments.
#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <map>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

using Mask = std::uint64_t;
using Edge = std::pair<int, int>;
using Types = std::vector<int>;
constexpr int Infinite = 120;
constexpr int LastAge = 5;

Mask bit(int n) { return Mask{1} << n; }

int take(Mask& set) {
    int index = std::countr_zero(set);
    set &= set - 1;
    return index;
}

bool connected(const std::vector<Mask>& neighbors, Mask side) {
    if (!side) return false;
    Mask reached = side & -side, pending = reached;
    while (pending) {
        Mask more = neighbors[take(pending)] & side & ~reached;
        reached |= more;
        pending |= more;
    }
    return reached == side;
}

std::vector<Mask> adjacency(int n, const std::vector<Edge>& edges) {
    std::vector<Mask> neighbors(n);
    for (const auto& [a, b] : edges) neighbors[a] |= bit(b), neighbors[b] |= bit(a);
    return neighbors;
}

bool admissible(const std::vector<Mask>& neighbors) {
    Mask all = bit(neighbors.size()) - 1;
    if (!connected(neighbors, all)) return false;
    for (int v = 0; v < int(neighbors.size()); ++v)
        if (!connected(neighbors, all ^ bit(v))) return false;
    return true;
}

template<class Range>
void integers(const Range& values) {
    bool beginning = true;
    std::cout << '[';
    for (int v : values) {
        if (!beginning) std::cout << ',';
        beginning = false;
        std::cout << v;
    }
    std::cout << ']';
}

void names(Mask support) {
    std::vector<int> labels;
    while (support) labels.push_back(take(support));
    integers(labels);
}

struct Core {
    int fixed;
    std::vector<Edge> edges;
    std::vector<int> image;
    std::vector<int> ports;

    int n() const { return fixed + 3; }

    std::vector<Edge> wired_edges() const {
        auto out = edges;
        for (int v : ports) out.emplace_back(v, n());
        return out;
    }

    void json() const {
        std::cout << "{\"fixed_vertices_before_split\":" << fixed << ",\"ordinary_junctions\":" << n()
                  << ",\"edges\":[";
        for (int i = 0; i < int(edges.size()); ++i) {
            if (i) std::cout << ',';
            integers(std::array{edges[i].first, edges[i].second});
        }
        std::cout << "],\"core_permutation\":";
        integers(image);
        std::cout << ",\"ports\":";
        integers(ports);
        std::cout << '}';
    }
};

template<class Visit>
void cores(int fixed, int port_count, Visit visit) {
    int left = fixed, right = fixed + 1, split_hub = fixed + 2;
    std::vector<Edge> possible;
    for (int a = 0; a < fixed; ++a) for (int b = a + 1; b < fixed; ++b)
        possible.emplace_back(a, b);
    for (Mask base = 0; base < bit(possible.size()); ++base) {
        std::vector<Edge> initial;
        for (Mask present = base; present;) initial.push_back(possible[take(present)]);
        for (Mask common = 1; common < bit(fixed); common += 2) for (int twins_meet : {0, 1}) {
            if (std::popcount(common) + twins_meet < 3) continue;
            std::vector<Edge> folded = initial;
            for (Mask contacts = common; contacts;) {
                int v = take(contacts);
                folded.emplace_back(v, left);
                folded.emplace_back(v, right);
            }
            if (twins_meet) folded.emplace_back(left, right);
            std::ranges::sort(folded);
            std::vector<int> image;
            auto exchange = [=](int v) { return v == left ? right : v == right ? left : v; };
            for (const auto& [a, b] : folded) {
                int x = exchange(a), y = exchange(b);
                if (x > y) std::swap(x, y);
                image.push_back(std::ranges::lower_bound(folded, Edge{x, y}) - folded.begin());
            }
            std::vector<int> hub_contacts;
            for (int j = 0; j < int(folded.size()); ++j)
                if (!folded[j].first && folded[j].second < fixed) hub_contacts.push_back(j);
            for (Mask sides = 0; sides < bit(hub_contacts.size()); ++sides) {
                auto split = folded;
                for (int j = 0; j < int(split.size()); ++j)
                    if (split[j] == Edge{0, right}) split[j].first = split_hub;
                for (Mask transferred = sides; transferred;)
                    split[hub_contacts[take(transferred)]].first = split_hub;
                auto ordinary = adjacency(fixed + 3, split);
                if (!connected(ordinary, bit(fixed + 3) - 1)) continue;
                for (Mask extra = 2; extra < bit(fixed); extra += 2) {
                    if (std::popcount(extra) != port_count - 2) continue;
                    std::vector<int> ports{0, split_hub};
                    for (Mask chosen = extra; chosen;) ports.push_back(take(chosen));
                    Mask attached = extra | bit(0) | bit(split_hub);
                    bool any_assignment = true;
                    for (int j = 0; j < fixed + 3; ++j)
                        if (!(attached & bit(j)) && std::popcount(ordinary[j]) < 3) any_assignment = false;
                    if (!any_assignment) continue;
                    Core core{fixed, split, image, ports};
                    if (admissible(adjacency(core.n() + 1, core.wired_edges()))) visit(core, ordinary);
                }
            }
        }
    }
}

struct Bond {
    Mask support;
    int ordinary_cost, virtual_mask;
};

struct Mismatch {
    Mask mark, image;
    int before, after;
};

struct Comparison {
    Mask mark, image;
    std::array<int, 16> left, right;
};

struct Interface {
    int ordinary;
    int ports;
    std::vector<Comparison> pairs, triples;
    bool same_equations;

    explicit Interface(const Core& core) : ordinary(core.edges.size()), ports(core.ports.size()) {
        const auto edges = core.wired_edges();
        const auto adjacent = adjacency(core.n() + 1, edges);
        std::vector<Mask> stars(adjacent.size());
        for (int e = 0; e < int(edges.size()); ++e) {
            stars[edges[e].first] |= bit(e);
            stars[edges[e].second] |= bit(e);
        }
        auto transport = [&](Mask support) {
            Mask moved = support & (bit(ordinary) - 1);
            Mask out = support ^ moved;
            while (moved) out |= bit(core.image[take(moved)]);
            return out;
        };

        std::vector<Mask> cuts(bit(core.n()));
        std::vector<Bond> bonds;
        for (Mask side = 1; side < cuts.size(); ++side) {
            Mask word = stars[std::countr_zero(side)] ^ cuts[side & (side - 1)];
            cuts[side] = word;
            if (connected(adjacent, side) && connected(adjacent, (bit(adjacent.size()) - 1) ^ side))
                bonds.push_back({word, std::popcount(word & (bit(ordinary) - 1)), int(word >> ordinary)});
        }
        std::set<Mask> span(cuts.begin(), cuts.end());
        same_equations = std::ranges::all_of(stars, [&](Mask word) { return span.contains(transport(word)); });
        if (same_equations) return;

        auto append = [&](std::vector<Comparison>& comparisons, Mask mark) {
            Mask image = transport(mark);
            if (mark >= image) return;
            Comparison c{mark, image, {}, {}};
            c.left.fill(Infinite);
            c.right.fill(Infinite);
            for (const Bond& b : bonds) {
                if ((b.support & mark) == mark) c.left[b.virtual_mask] = std::min(c.left[b.virtual_mask], b.ordinary_cost);
                if ((b.support & image) == image) c.right[b.virtual_mask] = std::min(c.right[b.virtual_mask], b.ordinary_cost);
            }
            if (c.left != c.right) comparisons.push_back(c);
        };
        for (int a = 0; a < int(edges.size()); ++a) for (int b = a + 1; b < int(edges.size()); ++b) {
            append(pairs, bit(a) | bit(b));
            for (int c = b + 1; c < int(edges.size()); ++c) append(triples, bit(a) | bit(b) | bit(c));
        }
        auto pure_first = [this](const auto& a, const auto& b) {
            return std::pair{bool(a.mark >> ordinary), a.mark} < std::pair{bool(b.mark >> ordinary), b.mark};
        };
        std::ranges::sort(pairs, pure_first);
        std::ranges::sort(triples, pure_first);
    }

    std::optional<Mismatch> compare(const std::vector<Comparison>& comparisons, const Types& weights) const {
        std::array<int, 16> added{};
        int patterns = 1 << ports;
        for (int mask = 1; mask < patterns; ++mask)
            added[mask] = added[mask & (mask - 1)] + weights[std::countr_zero(unsigned(mask))];
        for (const auto& c : comparisons) {
            int left = Infinite, right = Infinite;
            for (int mask = 0; mask < patterns; ++mask) {
                left = std::min(left, c.left[mask] + added[mask]);
                right = std::min(right, c.right[mask] + added[mask]);
            }
            if (left != right) return Mismatch{c.mark, c.image, left, right};
        }
        return {};
    }
};

Types profile(const Types& kinds, int age) {
    Types out;
    for (int k : kinds) out.push_back(age < std::max(2, k - 1) ? k : 1);
    return out;
}

void mismatch_json(const std::optional<Mismatch>& example) {
    if (!example) {
        std::cout << "null";
        return;
    }
    std::cout << "{\"marks\":";
    names(example->mark);
    std::cout << ",\"image\":";
    names(example->image);
    std::cout << ",\"cardinalities\":[";
    if (example->before == Infinite) std::cout << "null"; else std::cout << example->before;
    std::cout << ',';
    if (example->after == Infinite) std::cout << "null"; else std::cout << example->after;
    std::cout << "]}";
}

struct Verdict {
    std::optional<Mismatch> pair, triple;
};

struct Receipt {
    Core core;
    Types kinds;
    int age, later_age;
    Verdict present, later;

    void json() const {
        std::cout << "{\"core\":";
        core.json();
        std::cout << ",\"branch_kinds\":";
        integers(kinds);
        std::cout << ",\"age\":" << age << ",\"later_age\":" << later_age << ",\"weights\":";
        integers(profile(kinds, age));
        std::cout << ",\"later_weights\":";
        integers(profile(kinds, later_age));
        std::cout << ",\"present_pair_change\":";
        mismatch_json(present.pair);
        std::cout << ",\"present_triple_change\":";
        mismatch_json(present.triple);
        std::cout << ",\"later_pair_change\":";
        mismatch_json(later.pair);
        std::cout << ",\"later_triple_change\":";
        mismatch_json(later.triple);
        std::cout << '}';
    }
};

void independent(int fixed, int port_count) {
    std::map<std::string, std::uint64_t> totals;
    for (const char* name : {"current_pair_preservers", "current_pair_and_triple_preservers", "tested_future_stages",
                             "later_pair_mismatches", "later_triple_only_mismatches"}) totals[name] = 0;
    std::optional<Receipt> example, passing, breaking;
    cores(fixed, port_count, [&](const Core& core, const auto& ordinary) {
        ++totals["core_port_choices"];
        const Interface interface(core);
        if (interface.same_equations) { ++totals["equational_core_choices"]; return; }
        ++totals["non_equational_core_choices"];
        std::map<Types, Verdict> cache;
        auto verdict = [&](const Types& weights) -> const Verdict& {
            auto [row, inserted] = cache.try_emplace(weights);
            if (inserted) {
                row->second.pair = interface.compare(interface.pairs, weights);
                if (!row->second.pair) row->second.triple = interface.compare(interface.triples, weights);
            }
            return row->second;
        };
        Types kinds(port_count);
        auto assignments = [&](auto&& again, int index) -> void {
            if (index < port_count) {
                int minimum = std::max(1, 3 - std::popcount(ordinary[core.ports[index]]));
                for (int k = minimum; k <= 5; ++k) { kinds[index] = k; again(again, index + 1); }
                return;
            }
            ++totals["legal_assignments"];
            for (int age = 1; age < LastAge; ++age) {
                ++totals["eligible_current_stages"];
                const auto current = profile(kinds, age);
                const Verdict& here = verdict(current);
                if (here.pair) continue;
                ++totals["current_pair_preservers"];
                if (!here.triple) ++totals["current_pair_and_triple_preservers"];
                for (int later_age = age + 1; later_age <= LastAge; ++later_age) {
                    const auto after = profile(kinds, later_age);
                    const Verdict& next = verdict(after);
                    if (here.triple) {
                        if (next.pair && !example) example = Receipt{core, kinds, age, later_age, here, next};
                        continue;
                    }
                    ++totals["tested_future_stages"];
                    if (current != after) ++totals["tested_changed_profiles"];
                    if (next.pair) ++totals["later_pair_mismatches"];
                    if (next.triple) ++totals["later_triple_only_mismatches"];
                    if (next.pair || next.triple) {
                        const Mismatch& failure = next.pair ? *next.pair : *next.triple;
                        if (!(failure.mark >> interface.ordinary)) ++totals["later_old_only_mismatches"];
                        if (!breaking) breaking = Receipt{core, kinds, age, later_age, here, next};
                    } else if (!passing && current != after) passing = Receipt{core, kinds, age, later_age, here, next};
                }
            }
        };
        assignments(assignments, 0);
        totals["distinct_weighted_tables_measured"] += cache.size();
    });
    std::cout << "{\"fixed_vertices_before_split\":" << fixed << ",\"ports\":" << port_count << ",\"counts\":{";
    bool first = true;
    for (const auto& [name, count] : totals) {
        if (!first) std::cout << ',';
        first = false;
        std::cout << '"' << name << "\":" << count;
    }
    std::cout << "},\"pair_only_negative_control\":";
    if (example) example->json(); else std::cout << "null";
    std::cout << ",\"changing_profile_preserver\":";
    if (passing) passing->json(); else std::cout << "null";
    std::cout << ",\"first_later_mismatch\":";
    if (breaking) breaking->json(); else std::cout << "null";
    std::cout << "}\n";
}

} // namespace

int main(int argc, char** argv) {
    if (argc != 4) throw std::runtime_error("usage: census_interfaces independent|cores FIXED PORTS");
    std::string mode = argv[1];
    int fixed = std::stoi(argv[2]), ports = std::stoi(argv[3]);
    if (fixed < 3 || fixed > 4 || ports < 3 || ports > 4) throw std::runtime_error("unsupported family");
    if (mode == "independent") independent(fixed, ports);
    else if (mode == "cores") cores(fixed, ports, [](const Core& core, const auto&) { core.json(); std::cout << '\n'; });
    else throw std::runtime_error("unknown mode");
}
