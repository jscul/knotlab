// Reach a complete round from every admissible simple predecessor within a junction bound.
#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <map>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

using Mask = std::uint64_t;
using Wide = unsigned __int128;
using Rows = std::vector<std::vector<int>>;
using Adj = std::vector<Mask>;
constexpr int Inf = 9999;
constexpr int Cutoff = 6;
constexpr int MaxMeasuredVertices = 23;
constexpr Mask bit(int i) { return Mask{1} << i; }
constexpr Wide wide(int i) { return Wide{1} << i; }

void require(bool test, const char* msg) {
    if (!test) throw std::runtime_error(msg);
}

int take(Mask& m) {
    int i = std::countr_zero(m);
    m &= m - 1;
    return i;
}

int take_wide(Wide& m) {
    auto low = static_cast<std::uint64_t>(m);
    int i = low ? std::countr_zero(low) : 64 + std::countr_zero(static_cast<std::uint64_t>(m >> 64));
    m &= m - 1;
    return i;
}

std::vector<int> indices(Mask m) {
    std::vector<int> out;
    while (m) out.push_back(take(m));
    return out;
}

bool connected(const Adj& graph, Mask side) {
    if (!side) return false;
    Mask todo = side & -side, seen = todo;
    while (todo) {
        Mask added = graph[take(todo)] & side & ~seen;
        todo |= added;
        seen |= added;
    }
    return seen == side;
}

struct Rule {
    const Adj& neighbors;
    Adj candidates;

    explicit Rule(const Adj& rows) : neighbors(rows), candidates(rows.size()) {
        for (int u = 0; u < int(rows.size()); ++u)
            for (int v = u+1; v < int(rows.size()); ++v)
                if (rows[u] & rows[v]) candidates[u] |= bit(v), candidates[v] |= bit(u);
    }

    std::vector<Mask> groups(Mask live, int limit=1000000) const {
        std::vector<Mask> out;
        auto cliques = [&](auto&& again, Mask chosen, Mask available, Mask seen) -> void {
            if (int(out.size()) > limit) return;
            if (!(available | seen)) {
                if (std::popcount(chosen) < 3) return;
                Mask common = ~Mask{0};
                for (Mask left = chosen; left && common;) common &= neighbors[take(left)];
                if (!common) out.push_back(chosen);
                return;
            }
            int pivot = -1, high = -1;
            for (Mask m = available | seen; m;) {
                int v = take(m), score = std::popcount(candidates[v] & available);
                if (score > high) high = score, pivot = v;
            }
            for (Mask left = available & ~candidates[pivot]; left;) {
                int v = take(left);
                again(again, chosen | bit(v), available & candidates[v], seen & candidates[v]);
                available ^= bit(v);
                seen |= bit(v);
            }
        };
        cliques(cliques, 0, live, 0);
        if (int(out.size()) > limit) return out;
        std::ranges::sort(out, [](Mask a, Mask b) { return indices(a) < indices(b); });
        Adj covered(neighbors.size());
        for (Mask group : out) for (Mask left = group; left;) {
            int v = take(left);
            covered[v] |= group ^ bit(v);
        }
        for (Mask left = live; left;) {
            int u = take(left);
            for (Mask right = left & candidates[u] & ~covered[u]; right;) {
                out.push_back(bit(u) | bit(take(right)));
                if (int(out.size()) > limit) return out;
            }
        }
        return out;
    }
};

struct Incidence {
    Adj ordinary;
    std::vector<std::vector<int>> own;
    std::vector<std::vector<int>> loose;
    Mask live = 0;

    explicit Incidence(const Rows& rows) : ordinary(rows.size()), loose(rows.size()) {
        for (const auto& row : rows) for (int b : row) {
            require(b >= 0, "negative distinction");
            if (b >= int(own.size())) own.resize(b+1);
        }
        for (int j = 0; j < int(rows.size()); ++j) for (int b : rows[j]) own[b].push_back(j);
        for (int b = 0; b < int(own.size()); ++b) {
            const auto& v = own[b];
            require(v.size() == 1 || (v.size() == 2 && v[0] != v[1]), "invalid distinction incidence");
            if (v.size() == 1) loose[v[0]].push_back(b), live |= bit(v[0]);
            else ordinary[v[0]] |= bit(v[1]), ordinary[v[1]] |= bit(v[0]);
        }
    }
};

std::vector<int> demands(const std::vector<Mask>& groups, int n) {
    std::vector<int> out(n);
    for (Mask group : groups) while (group) ++out[take(group)];
    return out;
}

Rows grow(const Rows& seed, const Incidence& inc, std::vector<Mask> groups) {
    if (!inc.live) return {};
    int n = static_cast<int>(seed.size());
    int all_loose = 0, next_bit = static_cast<int>(inc.own.size());
    auto need = demands(groups, n);
    for (int u = 0; u < n; ++u) {
        int l = static_cast<int>(inc.loose[u].size());
        if (l < need[u]) return {};
        all_loose += l;
        for (int j = need[u]; j < l; ++j) groups.push_back(bit(u));
    }
    require(groups.size() < 63, "too many newborn sites for look-ahead");
    auto next_groups = Rule(groups).groups(bit(groups.size())-1);
    auto fresh_demand = demands(next_groups, groups.size());
    Rows out = seed;
    std::fill(need.begin(), need.end(), 0);
    for (int j = 0; j < int(groups.size()); ++j) {
        std::vector<int> row;
        for (Mask left = groups[j]; left;) {
            int u = take(left);
            row.push_back(inc.loose[u][need[u]++]);
        }
        int p = static_cast<int>(row.size());
        int f = p == all_loose ? fresh_demand[j] : std::max({fresh_demand[j], 3-p, 1});
        for (int x = 0; x < f; ++x) row.push_back(next_bit++);
        std::ranges::sort(row);
        out.push_back(std::move(row));
    }
    return out;
}

Rows start_rows(const Adj& graph, const std::vector<int>& loose) {
    int n = static_cast<int>(graph.size()), bit_name = 0;
    Rows rows(n);
    for (int a = 0; a < n; ++a) for (int b = a+1; b < n; ++b) if (graph[a] & bit(b)) {
        rows[a].push_back(bit_name);
        rows[b].push_back(bit_name++);
    }
    for (int a = 0; a < n; ++a) for (int k = 0; k < loose[a]; ++k) rows[a].push_back(bit_name++);
    return rows;
}

struct Table {
    std::vector<int> cls;
    std::vector<std::vector<int>> minima;
    std::vector<Wide> star;
    int horizon = 0;

    Table(const Rows& rows, const Incidence& inc, const std::vector<int>& query, int limit, bool rooted_flow=false) {
        int exterior = static_cast<int>(rows.size()), n = exterior + bool(inc.live);
        require(n <= (rooted_flow ? 60 : MaxMeasuredVertices), "table junction cap");
        Adj graph = inc.ordinary;
        graph.resize(n);
        std::map<std::pair<int,int>, int> bundles;
        std::vector<int> counts;
        star.resize(n);
        for (const auto& own : inc.own) {
            int x = own[0], y = own.size() == 1 ? exterior : own[1];
            auto [at, created] = bundles.try_emplace({x,y}, bundles.size());
            int k = at->second;
            require(k < 128, "table endpoint-class cap");
            if (created) counts.push_back(0);
            ++counts[k];
            cls.push_back(k);
            graph[x] |= bit(y);
            graph[y] |= bit(x);
            star[x] |= wide(k);
            star[y] |= wide(k);
        }
        int m = static_cast<int>(counts.size());
        if (rooted_flow) {
            flow_rows(graph, bundles, counts, query);
            return;
        }
        minima.assign(m, std::vector<int>(m, limit == Inf ? Inf : limit+1));
        Wide wanted = 0, singletons = 0, weighted = 0;
        for (int b : query) wanted |= wide(cls[b]);
        for (int i = 0; i < m; ++i) (counts[i] == 1 ? singletons : weighted) |= wide(i);
        if (query.empty()) wanted = singletons | weighted;
        Mask all = bit(n)-1;
        std::vector<Wide> cuts(bit(n-1), 0);
        for (Mask side = 1; side < cuts.size(); ++side) {
            Wide support = star[std::countr_zero(side)] ^ cuts[side & (side-1)];
            cuts[side] = support;
            Wide active = support & wanted;
            if (!active) continue;
            Wide singles = support & singletons;
            int cost = std::popcount(static_cast<std::uint64_t>(singles))
                     + std::popcount(static_cast<std::uint64_t>(singles >> 64));
            for (Wide left = support & weighted; left;) cost += counts[take_wide(left)];
            if (cost > limit || !connected(graph, side) || !connected(graph, all ^ side)) continue;
            while (active) {
                int a = take_wide(active);
                for (Wide right = support; right;) {
                    int b = take_wide(right);
                    int& x = minima[a][b];
                    if (cost < x) x = minima[b][a] = cost;
                }
            }
        }
    }

    int at(int a, int b) const { return a == b ? 0 : minima[cls[a]][cls[b]]; }

private:
    void flow_rows(const Adj& graph, const std::map<std::pair<int,int>,int>& bundles,
                   const std::vector<int>& counts, const std::vector<int>& query) {
        int n = static_cast<int>(graph.size()), m = static_cast<int>(counts.size());
        int root = n-1, width = static_cast<int>(cls.size());
        Mask all = bit(n)-1;
        std::vector<std::pair<int,int>> ends(m);
        using Capacity = std::array<std::array<int,60>,60>;
        Capacity initial{};
        for (const auto& [endpoints, i] : bundles) {
            auto [a,b] = endpoints;
            ends[i] = endpoints;
            initial[a][b] = initial[b][a] = counts[i];
        }
        minima.assign(m, std::vector<int>(m,Inf));
        std::vector<bool> needed(m,query.empty());
        for (int b : query) needed[cls[b]] = true;
        auto exceeds = [&](Mask in, Mask out, int limit) {
            Capacity residual = initial;
            int sent = 0;
            while (sent <= limit) {
                std::array<int,60> path;
                path.fill(-1);
                std::array<int,60> queue;
                int end = 0, hit = -1;
                for (Mask r = in; r;) {
                    int u = take(r);
                    queue[end++] = u;
                    path[u] = u;
                }
                Mask seen = in;
                for (int i = 0; i < end && hit == -1; ++i) {
                    int a = queue[i];
                    for (Mask step = graph[a] & ~seen; step;) {
                        int b = take(step);
                        if (!residual[a][b]) continue;
                        path[b] = a;
                        seen |= bit(b);
                        if (out & bit(b)) {
                            hit = b;
                            break;
                        }
                        queue[end++] = b;
                    }
                }
                if (hit == -1) return false;
                int amount = limit+1-sent;
                for (int v = hit; path[v] != v; v = path[v]) amount = std::min(amount,residual[path[v]][v]);
                for (int v = hit; path[v] != v; v = path[v]) {
                    residual[path[v]][v] -= amount;
                    residual[v][path[v]] += amount;
                }
                sent += amount;
            }
            return true;
        };
        std::vector<bool> finished(m,false);
        for (int limit = std::min(8,width);; limit = std::min(limit+4,width)) {
            horizon = limit;
            bool complete = true;
            for (int q = 0; q < m; ++q) if (needed[q] && !finished[q]) {
                const auto [x,y] = ends[q];
                auto search = [&](auto&& again, Mask in, Mask out, Mask front, Wide cut) -> void {
                    if (exceeds(in,out,limit)) return;
                    if (!front) {
                        if (!connected(graph,all ^ in)) return;
                        int cost = 0;
                        for (Wide bits = cut; bits;) cost += counts[take_wide(bits)];
                        if (cost > limit) return;
                        for (Wide bits = cut; bits;) {
                            int f = take_wide(bits);
                            if (cost < minima[q][f]) minima[q][f] = minima[f][q] = cost;
                        }
                        return;
                    }
                    int node = -1, best = -1;
                    for (Mask options = front; options;) {
                        int a = take(options), score = std::popcount(graph[a] & in);
                        if (score > best) node = a, best = score;
                    }
                    Mask rest = front ^ bit(node), chosen = in | bit(node);
                    again(again,chosen,out,rest | (graph[node] & ~(chosen | out)),cut ^ star[node]);
                    again(again,in,out | bit(node),rest,cut);
                };
                for (auto [u,v] : {std::pair{x,y},std::pair{y,x}}) if (u != root) {
                    Mask out = bit(v) | bit(root);
                    search(search,bit(u),out,graph[u] & ~out,star[u]);
                }
                finished[q] = limit == width || std::ranges::all_of(minima[q],[](int k){ return k != Inf; });
                complete &= finished[q];
            }
            if (complete) break;
        }
    }
};

class Symmetries {
    const Table& table;
    int n;
    std::vector<Mask> allowed;
    std::vector<int> image;

    bool choose(Mask free, Mask unused) {
        if (!free) return true;
        int choice = -1, size = n+1;
        Mask best = 0, mapped = (bit(n)-1) ^ free;
        for (Mask todo = free; todo;) {
            int u = take(todo);
            Mask survivors = 0;
            for (Mask trial = allowed[u] & unused; trial;) {
                int v = take(trial);
                bool good = true;
                for (Mask prev = mapped; prev && good;) {
                    int x = take(prev);
                    good = table.at(u,x) == table.at(v,image[x]);
                }
                if (good) survivors |= bit(v);
            }
            int count = std::popcount(survivors);
            if (!count) return false;
            if (count < size) choice = u, size = count, best = survivors;
        }
        while (best) {
            int v = take(best);
            image[choice] = v;
            if (choose(free ^ bit(choice), unused ^ bit(v))) return true;
        }
        return false;
    }

public:
    Symmetries(const Table& t, int movable) : table(t), n(movable), allowed(n), image(n, -1) {
        auto partition = [](const auto& descriptions) {
            std::map<typename std::decay_t<decltype(descriptions)>::value_type, int> palette;
            std::vector<int> colors;
            for (const auto& d : descriptions) colors.push_back(palette.try_emplace(d, palette.size()).first->second);
            return std::pair(colors, palette.size());
        };
        std::vector<std::vector<int>> sig(n);
        std::vector<int> fixed;
        std::vector<bool> used(t.minima.size());
        for (int i = n; i < int(t.cls.size()); ++i)
            if (!used[t.cls[i]]) fixed.push_back(i), used[t.cls[i]] = true;
        for (int i = 0; i < n; ++i)
            for (int f : fixed) sig[i].push_back(t.at(i,f));
        auto [colors, bins] = partition(sig);
        while (bins < static_cast<std::size_t>(n)) {
            std::vector<std::vector<std::pair<int,int>>> bag(n);
            for (int i = 0; i < n; ++i) {
                for (int j = 0; j < n; ++j) if (i != j) bag[i].emplace_back(colors[j], t.at(i,j));
                std::ranges::sort(bag[i]);
                bag[i].insert(bag[i].begin(), {colors[i],-1});
            }
            auto [more, count] = partition(bag);
            colors = std::move(more);
            if (count == bins) break;
            bins = count;
        }
        for (int i = 0; i < n; ++i)
            for (int j = 0; j < n; ++j) if (colors[i] == colors[j]) allowed[i] |= bit(j);
    }

    template<class Test>
    bool grade(Test test) {
        Mask all = bit(n)-1;
        for (int a = 0; a < n; ++a) {
            Mask after = all & ~(bit(a+1)-1);
            for (Mask images = allowed[a] & after; images;) {
                int b = take(images);
                bool consistent = true;
                for (int i = 0; i < a; ++i)
                    if (table.at(a,i) != table.at(b,i)) consistent = false;
                if (!consistent) continue;
                image[a] = b;
                if (choose(after, (after ^ bit(b)) | bit(a)) && !test(image)) return false;
            }
            image[a] = a;
        }
        return true;
    }
};

bool carries_equations(const Table& table, const std::vector<int>& image) {
    std::array<Wide,128> basis{};
    auto reduce = [&](Wide value, bool add) {
        while (value) {
            auto hi = static_cast<std::uint64_t>(value >> 64);
            int i = hi ? 64 + std::bit_width(hi)-1 : std::bit_width(static_cast<std::uint64_t>(value))-1;
            if (!basis[i]) {
                if (add) basis[i] = value;
                return false;
            }
            value ^= basis[i];
        }
        return true;
    };
    for (Wide row : table.star) reduce(row, true);
    Wide movable = 0;
    for (int i = 0; i < int(image.size()); ++i) movable |= wide(table.cls[i]);
    for (Wide row : table.star) {
        Wide after = row & ~movable;
        for (int i = 0; i < int(image.size()); ++i)
            if (row & wide(table.cls[i])) after |= wide(table.cls[image[i]]);
        if (!reduce(after, false)) return false;
    }
    return true;
}

struct Extension {
    bool possible;
    int first = -1, second = -1, left = -1, right = -1;
};

Extension extends(const Table& after, const std::vector<int>& image, int old_width, bool fresh_search=true) {
    int w = static_cast<int>(after.cls.size());
    std::vector<int> full(w);
    for (int i = 0; i < w; ++i) full[i] = i < int(image.size()) ? image[i] : i;
    for (int a = 0; a < old_width; ++a) for (int b = a+1; b < old_width; ++b)
        if (after.at(a,b) != after.at(full[a],full[b]))
            return {false,a,b,after.at(a,b),after.at(full[a],full[b])};
    bool identity = true;
    for (int a = 0; a < old_width; ++a) for (int b = old_width; b < w; ++b)
        if (after.at(a,b) != after.at(full[a],b)) identity = false;
    if (identity) return {true};
    if (!fresh_search) return {false};
    std::vector<std::vector<int>> candidates(w);
    for (int a = old_width; a < w; ++a) {
        full[a] = -1;
        for (int b = old_width; b < w; ++b) {
            bool equal = true;
            for (int x = 0; x < old_width && equal; ++x) equal = after.at(a,x) == after.at(b,full[x]);
            if (equal) candidates[a].push_back(b);
        }
        if (candidates[a].empty()) return {false};
    }
    std::vector<bool> used(w, false);
    auto search = [&](auto&& again, int remaining) -> bool {
        if (!remaining) return true;
        int u = -1;
        std::vector<int> best;
        for (int a = old_width; a < w; ++a) if (full[a] == -1) {
            std::vector<int> possible;
            for (int b : candidates[a]) if (!used[b]) {
                bool good = true;
                for (int z = old_width; z < w && good; ++z)
                    if (full[z] != -1) good = after.at(a,z) == after.at(b,full[z]);
                if (good) possible.push_back(b);
            }
            if (possible.empty()) return false;
            if (u == -1 || possible.size() < best.size()) u = a, best = std::move(possible);
        }
        for (int b : best) {
            full[u] = b;
            used[b] = true;
            if (again(again, remaining-1)) return true;
            used[b] = false;
            full[u] = -1;
        }
        return false;
    };
    return {search(search,w-old_width)};
}

template<class Vector> void array_json(const Vector& v) {
    std::cout << '[';
    bool first = true;
    for (auto x : v) {
        if (!first) std::cout << ',';
        std::cout << x;
        first = false;
    }
    std::cout << ']';
}

void rows_json(const Rows& rows) {
    std::cout << '[';
    for (int i = 0; i < int(rows.size()); ++i) {
        if (i) std::cout << ',';
        array_json(rows[i]);
    }
    std::cout << ']';
}

enum Count {Stages, Fixed, Offshoot, Short, Full, Successor, Failure, Unknown,
            ShortGen, FullGen, NonEq, Measured, CounterCount};
constexpr std::array<const char*,CounterCount> names = {
    "admissible_histories", "at_most_one_movable", "only_offshoots_next",
    "short_group_equation_certificate", "exact_group_equation_certificate", "exact_successor_certificate",
    "failures", "unresolved", "short_generators_examined", "full_generators_examined",
    "non_equation_full_generators", "successors_measured"
};

struct Witness {
    Rows start, here, after;
    std::vector<int> permutation;
    Extension result;
};

struct Pending {
    Rows start, here, after;
    std::vector<std::vector<int>> maps;
};

struct Tier {
    std::array<std::uint64_t,CounterCount> c{};
    int max_width = 0, max_successor_measured = 0;
    std::optional<Witness> first_failure;
    std::vector<Witness> all_bounded_failures;
    std::vector<Pending> pending;
};

void grade(const Rows& seed, const Rows& here, int movable, Tier& tier, bool retain_failures) {
    auto& c = tier.c;
    ++c[Stages];
    Incidence incidence(here);
    int w = static_cast<int>(incidence.own.size());
    tier.max_width = std::max(tier.max_width, w);
    require(here.size() - seed.size() == std::popcount(incidence.live), "newborns must all be live");
    if (movable <= 1) {
        ++c[Fixed];
        return;
    }
    auto groups = Rule(incidence.ordinary).groups(incidence.live);
    if (groups.empty()) {
        ++c[Offshoot];
        return;
    }
    std::vector<int> query(movable);
    for (int i = 0; i < movable; ++i) {
        query[i] = i;
        for (int holder : incidence.own[i]) require(holder < int(seed.size()), "movable touches newborn");
    }
    {
        Table short_table(here,incidence,query,Cutoff);
        if (Symmetries(short_table,movable).grade([&](const auto& perm) {
            ++c[ShortGen];
            return carries_equations(short_table,perm);
        })) {
            ++c[Short];
            return;
        }
    }
    Table exact(here,incidence,query,Inf);
    Rows after;
    std::optional<Table> next_table;
    bool unknown = false, fail = false;
    Symmetries(exact,movable).grade([&](const auto& perm) {
        ++c[FullGen];
        if (carries_equations(exact,perm)) return true;
        ++c[NonEq];
        if (after.empty()) {
            after = grow(here,incidence,groups);
            require(!after.empty(), "look-ahead cannot stall its own parents");
            Incidence grown(after);
            int classes = 0;
            for (Mask row : grown.ordinary) classes += std::popcount(row);
            if (after.size() + bool(grown.live) > MaxMeasuredVertices ||
                classes/2 + std::popcount(grown.live) > 128) {
                unknown = true;
                tier.pending.push_back({seed,here,after,{}});
            } else {
                next_table.emplace(after,grown,std::vector<int>{},Inf);
                ++c[Measured];
                tier.max_successor_measured = std::max(tier.max_successor_measured, int(after.size()));
            }
        }
        if (unknown) {
            tier.pending.back().maps.push_back(perm);
            return true;
        }
        auto result = extends(*next_table,perm,w);
        if (result.possible) return true;
        fail = true;
        if (!tier.first_failure || Incidence(tier.first_failure->here).own.size() > incidence.own.size())
            tier.first_failure = Witness{seed,here,after,perm,result};
        if (retain_failures) tier.all_bounded_failures.push_back({seed,here,after,perm,result});
        return false;
    });
    ++c[unknown ? Unknown : fail ? Failure : after.empty() ? Full : Successor];
}

void witness_json(const Witness& x) {
    std::cout << "{\"start\":";
    rows_json(x.start);
    std::cout << ",\"current\":";
    rows_json(x.here);
    std::cout << ",\"next\":";
    rows_json(x.after);
    std::cout << ",\"old_movable_permutation\":";
    array_json(x.permutation);
    std::cout << ",\"old_pair\":";
    array_json(std::array{x.result.first,x.result.second});
    std::cout << ",\"successor_K\":";
    array_json(std::array{x.result.left,x.result.right});
    std::cout << '}';
}

Adj decode(const std::string& graph6, int n) {
    Adj edges(n);
    require(graph6[0]-63 == n, "geng order mismatch");
    int i = 0;
    for (int v = 1; v < n; ++v) for (int u = 0; u < v; ++u, ++i)
        if ((graph6.at(1+i/6)-63) & (1 << (5-i%6))) edges[u] |= bit(v), edges[v] |= bit(u);
    return edges;
}

void sweep(int n, int cap, int width_cap) {
    require(n >= 1 && n <= 10 && cap >= n+3 && cap <= 13, "unsupported reached-size tier");
    std::vector<Tier> tiers(cap+1);
    int unlabeled = 0;
    std::string input;
    while (std::cin >> input) {
        if (input == ">>graph6<<") continue;
        ++unlabeled;
        Adj graph = decode(input,n);
        Mask needy = 0;
        std::vector<int> degree(n);
        for (int i = 0; i < n; ++i)
            if ((degree[i] = std::popcount(graph[i])) < 3) needy |= bit(i);
        int movable = 0;
        for (int d : degree) movable += d;
        movable /= 2;
        Rule rules(graph);
        for (Mask live = 1; live < bit(n); ++live) {
            if ((live & needy) != needy) continue;
            Adj wired = graph;
            wired.push_back(live);
            for (Mask todo = live; todo;) wired[take(todo)] |= bit(n);
            Mask all = bit(n+1)-1;
            bool legal = true;
            for (int j = 0; j < n && legal; ++j) legal = connected(wired, all ^ bit(j));
            if (!legal) continue;
            auto groups = rules.groups(live,cap-n);
            int base = static_cast<int>(groups.size());
            if (base > cap-n) continue;
            auto loose = demands(groups,n);
            auto active = indices(live);
            int minimum_extras = 0;
            for (int j : active) {
                int at_least = std::max(1,3-degree[j]);
                if (loose[j] < at_least) minimum_extras += at_least - loose[j], loose[j] = at_least;
            }
            int minimum = n + base + minimum_extras;
            if (minimum > cap) continue;
            int multichild_size = 0;
            for (Mask group : groups) multichild_size += std::popcount(group) + 1;
            auto allocate = [&](auto&& again, int j, int spare, int size) -> void {
                int u = active[j];
                if (j+1 == int(active.size())) {
                    loose[u] += spare;
                    Rows seed = start_rows(graph,loose);
                    Rows current = grow(seed,Incidence(seed),groups);
                    require(int(current.size()) == size, "bounded construction count differs from the round");
                    if (!width_cap || int(Incidence(current).own.size()) <= width_cap)
                        grade(seed,current,movable,tiers[size],width_cap != 0);
                    loose[u] -= spare;
                    return;
                }
                int l = loose[u];
                for (int extra = 0; extra <= spare; ++extra) {
                    loose[u] = l + extra;
                    again(again,j+1,spare-extra,size);
                }
                loose[u] = l;
            };
            for (int m = std::max(minimum,n+3); m <= cap; ++m) {
                if (width_cap && movable + multichild_size + 3*(m-n-base) > width_cap) break;
                allocate(allocate,0,m-minimum,m);
            }
        }
    }
    std::cout << "{\"predecessor_junctions\":" << n << ",\"unlabeled_graphs\":" << unlabeled << ",\"reached_tiers\":[";
    for (int m = n+3; m <= cap; ++m) {
        if (m > n+3) std::cout << ',';
        const auto& t = tiers[m];
        std::cout << "{\"junctions\":" << m << ",\"max_width\":" << t.max_width
                  << ",\"max_measured_successor_junctions\":" << t.max_successor_measured;
        for (int j = 0; j < CounterCount; ++j) std::cout << ",\"" << names[j] << "\":" << t.c[j];
        if (!t.pending.empty()) {
            std::cout << ",\"pending_successors\":[";
            for (int i = 0; i < int(t.pending.size()); ++i) {
                const auto& p = t.pending[i];
                if (i) std::cout << ',';
                std::cout << "{\"start\":";
                rows_json(p.start);
                std::cout << ",\"current\":";
                rows_json(p.here);
                std::cout << ",\"next\":";
                rows_json(p.after);
                std::cout << ",\"non_equation_generators\":[";
                for (int j = 0; j < int(p.maps.size()); ++j) {
                    if (j) std::cout << ',';
                    array_json(p.maps[j]);
                }
                std::cout << "]}";
            }
            std::cout << ']';
        }
        if (t.first_failure) {
            std::cout << ",\"first_failure\":";
            witness_json(*t.first_failure);
        }
        if (!t.all_bounded_failures.empty()) {
            std::cout << ",\"all_failing_histories\":[";
            for (int i = 0; i < int(t.all_bounded_failures.size()); ++i) {
                if (i) std::cout << ',';
                witness_json(t.all_bounded_failures[i]);
            }
            std::cout << ']';
        }
        std::cout << '}';
    }
    std::cout << "]}\n";
}

Rows read_rows() {
    int n;
    require(bool(std::cin >> n) && n > 0, "missing number of sites");
    Rows rows(n);
    for (auto& row : rows) {
        int size;
        require(bool(std::cin >> size) && size > 0, "invalid support size");
        row.resize(size);
        for (int& b : row) require(bool(std::cin >> b), "missing distinction");
    }
    return rows;
}

void control() {
    Rows here = read_rows(), after = read_rows();
    Incidence i(here), j(after);
    Table a(here,i,{},Inf), b(after,j,{},Inf);
    std::vector<int> perm(i.own.size());
    for (int& p : perm) require(bool(std::cin >> p), "missing old-map image");
    auto sorted = perm;
    std::ranges::sort(sorted);
    bool live_fixed = true, old_isometry = true;
    for (int x = 0; x < int(perm.size()); ++x) {
        require(sorted[x] == x, "invalid permutation");
        for (int holder : i.own[x]) if ((i.live & bit(holder)) && perm[x] != x) live_fixed = false;
        for (int y = x+1; y < int(perm.size()); ++y)
            if (a.at(x,y) != a.at(perm[x],perm[y])) old_isometry = false;
    }
    const auto r = extends(b,perm,perm.size());
    std::cout << std::boolalpha << "{\"current_width\":" << perm.size() << ",\"successor_width\":" << j.own.size()
              << ",\"current_junctions\":" << here.size() << ",\"successor_junctions\":" << after.size()
              << ",\"old_table_isometry\":" << old_isometry << ",\"fixes_live_supports\":" << live_fixed
              << ",\"extends\":" << r.possible << ",\"old_pair\":";
    array_json(std::array{r.first,r.second});
    std::cout << ",\"successor_K\":";
    array_json(std::array{r.left,r.right});
    for (const auto& [key,t] : {std::pair{"current_K_upper",&a},std::pair{"successor_K_upper",&b}}) {
        std::vector<int> values;
        for (int x = 0; x < int(t->cls.size()); ++x) for (int y = x+1; y < int(t->cls.size()); ++y)
            values.push_back(t->at(x,y));
        std::cout << ",\"" << key << "\":";
        array_json(values);
    }
    std::cout << "}\n";
}

void wide_successors() {
    int cases;
    require(bool(std::cin >> cases), "missing large successor batch size");
    for (int i = 0; i < cases; ++i) {
        Rows after = read_rows();
        Incidence inc(after);
        int old, m, k;
        require(bool(std::cin >> old >> m >> k) && m >= 2 && k >= 1, "missing map dimensions");
        std::vector<std::vector<int>> maps(k,std::vector<int>(m));
        std::vector<bool> moved(m,false);
        for (auto& image : maps) for (int j = 0; j < m; ++j) {
            require(bool(std::cin >> image[j]) && 0 <= image[j] && image[j] < m, "invalid map image");
            if (image[j] != j) moved[j] = true;
        }
        std::vector<int> needed;
        for (int j = 0; j < m; ++j) if (moved[j]) needed.push_back(j);
        require(!needed.empty(), "no moved distinction for wide cut check");
        Table rows(after,inc,needed,Inf,true);
        std::optional<Table> full;
        int identities = 0, rescued = 0, failed = 0;
        Extension first_failure{true};
        for (const auto& perm : maps) {
            auto r = extends(rows,perm,old,false);
            if (r.possible) {
                ++identities;
                continue;
            }
            if (r.first == -1) {
                if (!full) full.emplace(after,inc,std::vector<int>{},Inf,true);
                r = extends(*full,perm,old);
                if (r.possible) {
                    ++rescued;
                    continue;
                }
            }
            if (!failed) first_failure = r;
            ++failed;
        }
        std::cout << "{\"successor_junctions\":" << after.size() << ",\"successor_width\":" << inc.own.size()
                  << ",\"moved_rows\":" << needed.size() << ",\"last_row_cutoff_K\":" << rows.horizon
                  << ",\"identity_extensions\":" << identities << ",\"other_extensions\":" << rescued
                  << ",\"failed_extensions\":" << failed << ",\"first_failed_old_pair\":";
        array_json(std::array{first_failure.first,first_failure.second});
        std::cout << ",\"first_failed_K\":";
        array_json(std::array{first_failure.left,first_failure.right});
        std::cout << "}\n" << std::flush;
    }
}

void literal_rounds() {
    Rows start = read_rows();
    Incidence s(start);
    Rows current = grow(start,s,Rule(s.ordinary).groups(s.live));
    require(!current.empty(), "the start has no complete round");
    Incidence c(current);
    Rows next = grow(current,c,Rule(c.ordinary).groups(c.live));
    require(!next.empty(), "the reached stage has no complete round");
    std::cout << "{\"current\":";
    rows_json(current);
    std::cout << ",\"next\":";
    rows_json(next);
    std::cout << "}\n";
}

} // namespace

int main(int argc, char** argv) {
    try {
        std::ios::sync_with_stdio(false);
        std::cin.tie(nullptr);
        if ((argc == 4 || argc == 5) && std::string(argv[1]) == "sweep")
            sweep(std::stoi(argv[2]),std::stoi(argv[3]), argc == 5 ? std::stoi(argv[4]) : 0);
        else if (argc == 2 && std::string(argv[1]) == "control") control();
        else if (argc == 2 && std::string(argv[1]) == "wide") wide_successors();
        else if (argc == 2 && std::string(argv[1]) == "rounds") literal_rounds();
        else throw std::runtime_error("usage: reach_bound sweep PREDECESSOR_N CAP | reach_bound control");
    } catch (const std::exception& e) {
        std::cerr << e.what() << '\n';
        return 1;
    }
}
