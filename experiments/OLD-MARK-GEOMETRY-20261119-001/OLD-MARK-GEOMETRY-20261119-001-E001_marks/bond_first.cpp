#include <algorithm>
#include <bit>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <vector>

using Mask = std::uint64_t;

struct Link {
    int u, v;
};

struct Child {
    int u, v, delta;
};

struct Best {
    int cost = std::numeric_limits<int>::max();
    Mask old = 0;
};

static int next(Mask& mask) {
    const int v = std::countr_zero(mask);
    mask &= mask - 1;
    return v;
}

static Mask bit(int n) { return Mask{1} << n; }

class Search {
    int n;
    std::vector<int> loose;
    std::vector<Link> original;
    std::vector<Child> children;
    std::vector<Mask> adjacent, incident;
    std::vector<int> parent;
    std::vector<std::vector<Best>> best;
    std::uint64_t visited = 0;

    int representative(int u) {
        while (parent[u] != u) {
            parent[u] = parent[parent[u]];
            u = parent[u];
        }
        return u;
    }

    bool merge(int u, int v) {
        u = representative(u);
        v = representative(v);
        parent[u] = v;
        return u != v;
    }

    void add(int v, Mask set, Mask boundary, Mask banned, Mask original_cut, int original_cost) {
        const Mask at = bit(v);
        set |= at;
        boundary |= adjacent[v] & ~(set | banned);
        original_cut ^= incident[v];
        original_cost += loose[v];
        ++visited;

        if (std::popcount(original_cut) >= 2) {
            int cost = original_cost + std::popcount(original_cut);
            int components = std::popcount(set);
            for (Mask remaining = set; remaining;) {
                int u = next(remaining);
                parent[u] = u;
            }
            for (const Link& link : original) {
                if ((set & bit(link.u)) && (set & bit(link.v))) {
                    components -= merge(link.u, link.v);
                }
            }
            for (const Child& child : children) {
                if ((set & bit(child.u)) && (set & bit(child.v))) {
                    const bool needed = merge(child.u, child.v);
                    if (child.delta <= 0 || needed) {
                        cost += child.delta;
                    }
                    components -= needed;
                }
            }
            if (components != 1) std::abort();
            for (Mask row = original_cut; row;) {
                const int i = next(row);
                for (Mask column = row; column;) {
                    Best& cell = best[i][next(column)];
                    if (cost < cell.cost || (cost == cell.cost && set < cell.old)) {
                        cell = {cost, set};
                    }
                }
            }
        }

        while (boundary) {
            const int u = next(boundary);
            add(u, set, boundary, banned, original_cut, original_cost);
            banned |= bit(u);
        }
    }

public:
    Search(int knots, int marks)
        : n(knots), loose(n), original(marks), adjacent(n), incident(n), parent(n),
          best(marks, std::vector<Best>(marks)) {}

    void read(int child_count) {
        for (int& count : loose) std::cin >> count;
        for (int i = 0; i < static_cast<int>(original.size()); ++i) {
            auto& [u, v] = original[i];
            std::cin >> u >> v;
            adjacent[u] |= bit(v);
            adjacent[v] |= bit(u);
            incident[u] |= bit(i);
            incident[v] |= bit(i);
        }
        for (int i = 0; i < child_count; ++i) {
            int u, v, fresh;
            std::cin >> u >> v >> fresh;
            children.push_back({u, v, fresh - 2});
            adjacent[u] |= bit(v);
            adjacent[v] |= bit(u);
        }
        std::stable_sort(children.begin(), children.end(),
                         [](const Child& a, const Child& b) { return a.delta < b.delta; });
    }

    void solve() {
        for (int r = 0; r < n; ++r) add(r, 0, 0, bit(r) - 1, 0, 0);
        std::cout << visited << '\n';
        for (int i = 0; i < static_cast<int>(best.size()); ++i) {
            for (int j = i + 1; j < static_cast<int>(best.size()); ++j) {
                const Best& cell = best[i][j];
                std::cout << i << ' ' << j << ' '
                          << (cell.old ? cell.cost : -1) << ' ' << cell.old << '\n';
            }
        }
    }
};

int main() {
    int knots, marks, children;
    if (!(std::cin >> knots >> marks >> children) || knots < 1 || knots > 25 ||
        marks < 2 || marks > 64 || children < 0) {
        return 2;
    }
    Search search(knots, marks);
    search.read(children);
    search.solve();
}
