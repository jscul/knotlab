// Exact small-width allocation filter. Read biconnected graph6 supports from stdin.
#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <functional>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

using Mask = uint32_t;
using Edge = std::pair<int,int>;
using Tier = std::array<uint64_t,4>;

Mask bit(int x) { return Mask{1} << x; }
int count(Mask s) { return std::popcount(s); }
int first(Mask s) { return std::countr_zero(s); }

bool connected(Mask s, const std::vector<Mask>& neighbors) {
    if (!s) return false;
    Mask seen = 0, pending = s & -s;
    while (pending) {
        Mask x = pending & -pending;
        pending ^= x;
        seen |= x;
        pending |= neighbors[first(x)] & s & ~seen;
    }
    return seen == s;
}

struct Span {
    std::array<Mask,32> rows{};
    int rank = 0;
    void add(Mask word) {
        while (word) {
            int j = std::bit_width(word) - 1;
            if (rows[j]) word ^= rows[j];
            else { rows[j] = word; ++rank; return; }
        }
    }
};

std::vector<Mask> groups(Mask live, const std::vector<Mask>& ordinary) {
    std::vector<Mask> witness, candidates(ordinary.size(), 0), result;
    for (Mask neighbors : ordinary) {
        Mask part = neighbors & live;
        if (count(part) < 2) continue;
        witness.push_back(part);
        for (Mask s = part; s; s &= s-1) candidates[first(s)] |= part ^ bit(first(s));
    }
    std::function<void(Mask,Mask,Mask)> maximal = [&](Mask s, Mask p, Mask x) {
        if (!(p | x)) {
            if (count(s) >= 3 && std::none_of(witness.begin(), witness.end(),
                                            [&](Mask candidate){return (candidate & s) == s;})) result.push_back(s);
            return;
        }
        int pivot = first(p | x);
        for (Mask z = p | x; z; z &= z-1) {
            int u = first(z);
            if (count(p & candidates[u]) > count(p & candidates[pivot])) pivot = u;
        }
        for (Mask z = p & ~candidates[pivot]; z; z &= z-1) {
            int u = first(z);
            maximal(s | bit(u), p & candidates[u], x & candidates[u]);
            p ^= bit(u);
            x |= bit(u);
        }
    };
    maximal(0, live, 0);
    std::vector<Mask> covered(ordinary.size(), 0);
    for (Mask s : result) for (Mask x = s; x; x &= x-1) covered[first(x)] |= s;
    for (Mask s = live; s; s &= s-1) {
        int u = first(s);
        for (Mask z = candidates[u] & (s & (s-1)) & ~covered[u]; z; z &= z-1) result.push_back(bit(u) | bit(first(z)));
    }
    return result;
}

struct Support {
    int n, m, order, least, bound;
    bool native;
    std::vector<Edge> links;
    std::vector<Mask> adj, stars, bonds;
    std::vector<int> weights, degree;
    std::vector<Tier>& tally;
    uint64_t& feasible_roots;

    std::vector<int> predecessor(int out) const {
        Mask live = adj[out];
        if (count(live) < 2) return {};
        Mask core = (bit(n) - 1) & ~live & ~bit(out);
        if (!connected(core, adj)) return {};
        auto ordinary = adj;
        ordinary[out] = 0;
        for (auto& s : ordinary) s &= ~bit(out);
        std::vector<Mask> prior(n, 0);
        Mask prior_live = 0;
        std::vector<int> loose(n, 0);
        for (Mask s = core; s; s &= s-1) {
            int u = first(s);
            prior[u] = ordinary[u] & core;
            if ((loose[u] = count(ordinary[u] & live))) prior_live |= bit(u);
        }
        auto prior_wired = prior;
        prior_wired[out] = prior_live;
        for (Mask s = prior_live; s; s &= s-1) prior_wired[first(s)] |= bit(out);
        for (Mask s = core; s; s &= s-1)
            if (!connected((core ^ bit(first(s))) | bit(out), prior_wired)) return {};
        auto expected = groups(prior_live, prior);
        for (Mask s : expected) for (Mask z = s; z; z &= z-1) if (--loose[first(z)] < 0) return {};
        for (int j=0; j<n; ++j) for (int k=0; k<loose[j]; ++k) expected.push_back(bit(j));
        std::vector<Mask> actual;
        for (Mask s = live; s; s &= s-1) actual.push_back(ordinary[first(s)] & core);
        std::sort(expected.begin(), expected.end());
        std::sort(actual.begin(), actual.end());
        if (expected != actual) return {};
        std::vector<int> demand(n, 0);
        for (Mask s : groups(live, ordinary)) for (Mask z = s; z; z &= z-1) ++demand[first(z)];
        std::vector<int> required;
        for (auto [u,v] : links) {
            if (u == out || v == out) {
                int j = u == out ? v : u;
                required.push_back(std::max({demand[j], 3-count(ordinary[j]), 1}));
            } else required.push_back((live & (bit(u) | bit(v))) ? 1 : 0);
        }
        return required;
    }

    std::vector<int> costs() const {
        std::vector<int> result;
        for (Mask s : bonds) {
            int size = 0;
            for (Mask z = s; z; z &= z-1) size += weights[first(z)];
            result.push_back(size);
        }
        return result;
    }

    Span initial_rank(const std::vector<int>& cost) const {
        Span span;
        std::array<int,32> minimum;
        minimum.fill(bound+1);
        std::array<Mask,32> unique{};
        for (size_t j=0; j<bonds.size(); ++j) {
            Mask s = bonds[j];
            int k = cost[j];
            if (k <= order) span.add(s);
            for (Mask z=s; z; z&=z-1) {
                int i = first(z);
                if (k < minimum[i]) { minimum[i] = k; unique[i] = s; }
                else if (k == minimum[i]) unique[i] = 0;
            }
        }
        if (order == 2) {
            for (Mask s : unique) span.add(s);
            return span;
        }
        for (size_t j=0; j<bonds.size(); ++j) {
            for (Mask z=bonds[j]; z; z&=z-1) if (minimum[first(z)] == cost[j]) { span.add(bonds[j]); break; }
        }
        if (span.rank == n-1) return span;
        std::array<std::array<int,32>,32> price;
        std::array<std::array<Mask,32>,32> pair_unique{};
        for (auto& row : price) row.fill(bound+1);
        for (size_t k=0; k<bonds.size(); ++k) for (Mask s=bonds[k]; s; s&=s-1) {
            int i = first(s);
            for (Mask z=s&(s-1); z; z&=z-1) {
                int j = first(z);
                if (cost[k] < price[i][j]) { price[i][j] = cost[k]; pair_unique[i][j] = bonds[k]; }
                else if (cost[k] == price[i][j]) pair_unique[i][j] = 0;
            }
        }
        for (const auto& row : pair_unique) for (Mask s : row) span.add(s);
        return span;
    }

    void score(int width, Mask roots) {
        if (width < least || !roots) return;
        auto& tier = tally[width];
        tier[0] += count(roots);
        auto rank = initial_rank(costs());
        if (rank.rank == n-1) { tier[1] += count(roots); return; }
        for (Mask z=roots; z; z&=z-1) {
            int out = first(z);
            auto marked = rank;
            marked.add(stars[out]);
            for (Mask s=adj[out]; s; s&=s-1) marked.add(stars[first(s)]);
            if (marked.rank == n-1) { ++tier[2]; continue; }
            ++tier[3];
            std::cout << "R " << out << ' ' << n << ' ' << m;
            for (int j=0; j<m; ++j)
                std::cout << ' ' << links[j].first << ' ' << links[j].second << ' ' << weights[j];
            std::cout << '\n';
        }
    }

    void allocate(const std::vector<int>& free, int i, int width, Mask roots) {
        if (i == int(free.size())) {
            Mask under = 0;
            for (int u=0; u<n; ++u) if (degree[u] < 3) under |= bit(u);
            // All ordinary junctions have arity at least three; the outside has at least two.
            if (count(under) > 1) return;
            if (under) roots &= under;
            if (roots && degree[first(roots)] >= 2) score(width, roots);
            return;
        }
        int j = free[i];
        auto [u,v] = links[j];
        int minimum_extra = i + 1 == int(free.size()) ? std::max(0, least-width) : 0;
        for (int extra=minimum_extra; extra<=bound-width; ++extra) {
            weights[j] += extra;
            degree[u] += extra;
            degree[v] += extra;
            allocate(free, i+1, width+extra, roots);
            weights[j] -= extra;
            degree[u] -= extra;
            degree[v] -= extra;
        }
    }

    void run() {
        adj.assign(n,0); stars.assign(n,0);
        for (int j=0; j<m; ++j) {
            auto [u,v] = links[j];
            adj[u] |= bit(v); adj[v] |= bit(u);
            stars[u] |= bit(j); stars[v] |= bit(j);
        }
        std::vector<std::pair<Mask,std::vector<int>>> plans;
        Mask starts = 0;
        for (int out=0; out<n; ++out) {
            Mask live = adj[out];
            bool independent = true;
            for (Mask s=live; s; s&=s-1) if (adj[first(s)] & live) independent = false;
            if (!independent) continue;
            if (native) {
                auto required = predecessor(out);
                if (required.empty()) continue;
                plans.emplace_back(bit(out), std::move(required));
                ++feasible_roots;
            } else starts |= bit(out);
        }
        if (!native && starts) {
            feasible_roots += count(starts);
            plans.emplace_back(starts, std::vector<int>(m, 0));
        }
        if (plans.empty()) return;
        Mask universe = bit(n) - 1;
        for (Mask s=1; s<bit(n-1); ++s) {
            if (!connected(s, adj) || !connected(universe^s, adj)) continue;
            Mask support = 0;
            for (Mask z=s; z; z&=z-1) support ^= stars[first(z)];
            bonds.push_back(support);
        }
        for (const auto& [roots, required] : plans) {
            weights.resize(m); degree.assign(n,0);
            int start_width = 0;
            std::vector<int> free;
            for (int j=0; j<m; ++j) {
                int w = weights[j] = std::max(1, required[j]);
                if (!required[j]) free.push_back(j);
                start_width += w;
                degree[links[j].first] += w;
                degree[links[j].second] += w;
            }
            if (start_width <= bound) allocate(free, 0, start_width, roots);
        }
    }
};

int main(int argc, char** argv) {
    if (argc != 5) return 2;
    int order = std::stoi(argv[1]), least = std::stoi(argv[2]), bound = std::stoi(argv[3]);
    bool native = std::string(argv[4]) == "native";
    if (!(1 <= least && least <= bound && bound < 32 && (order == 2 || order == 3))) return 2;
    std::vector<Tier> tally(bound+1);
    uint64_t graphs = 0, roots = 0;
    std::string row;
    while (std::getline(std::cin,row)) {
        if (row.rfind(">>graph6<<", 0) == 0) row.erase(0,10);
        if (row.empty()) continue;
        int n = row[0] - 63;
        if (n < 2 || n >= 32 || row.size() < size_t(1+(n*(n-1)/2+5)/6)) return 3;
        std::vector<Edge> links;
        int k = 0;
        for (int v=1; v<n; ++v) for (int u=0; u<v; ++u,++k)
            if (((row[1+k/6]-63)>>(5-k%6)) & 1) links.emplace_back(u,v);
        if (int(links.size()) > bound) return 3;
        ++graphs;
        Support support{n,int(links.size()),order,least,bound,native,std::move(links),{},{},{},{},{},tally,roots};
        support.run();
    }
    std::cout << "C " << graphs << ' ' << roots << '\n';
    for (int k=least; k<=bound; ++k) {
        std::cout << "T " << k;
        for (uint64_t x : tally[k]) std::cout << ' ' << x;
        std::cout << '\n';
    }
}
