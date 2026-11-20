// Exact threshold feasibility for connected cuts with pinned endpoints.
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <limits>
#include <queue>
#include <utility>
#include <vector>

using Colors = std::vector<std::int8_t>;

struct Arc {
    int to, reverse, capacity;
};

struct Dinic {
    std::vector<std::vector<Arc>> graph;
    std::vector<int> level, cursor;

    explicit Dinic(int size) : graph(size), level(size), cursor(size) {}

    void add(int u, int v, int capacity, int back) {
        const int from = graph[u].size(), to = graph[v].size();
        graph[u].push_back({v, to, capacity});
        graph[v].push_back({u, from, back});
    }

    int send(int u, int sink, int value) {
        if (u == sink) return value;
        for (int& i = cursor[u]; i < int(graph[u].size()); ++i) {
            auto& a = graph[u][i];
            if (!a.capacity || level[a.to] != level[u] + 1) continue;
            const int next = send(a.to, sink, std::min(value, a.capacity));
            if (!next) continue;
            a.capacity -= next;
            graph[a.to][a.reverse].capacity += next;
            return next;
        }
        return 0;
    }

    bool layers(int root, int sink) {
        std::fill(level.begin(), level.end(), -1);
        std::queue<int> queue;
        level[root] = 0;
        queue.push(root);
        while (!queue.empty()) {
            const int u = queue.front();
            queue.pop();
            for (const auto& a : graph[u]) {
                if (!a.capacity || level[a.to] >= 0) continue;
                level[a.to] = level[u] + 1;
                queue.push(a.to);
            }
        }
        return level[sink] >= 0;
    }

    int maximum(int root, int sink) {
        int value = 0;
        while (layers(root, sink)) {
            std::fill(cursor.begin(), cursor.end(), 0);
            while (const int next = send(root, sink, std::numeric_limits<int>::max()))
                value += next;
        }
        return value;
    }
};

struct Link {
    int a, b, capacity;
};

struct ResidualLink {
    int a, b, forward, reverse;
};

struct Capped {};

struct Feasibility {
    const std::vector<std::vector<int>>& near;
    const std::vector<ResidualLink>& residual;
    int outside, root, slack;
    long long limit, work = 0, nodes = 0;
    Colors witness;

    void charge(long long units) {
        work += units;
        if (work > limit) throw Capped{};
    }

    std::vector<int> reachable(const Colors& colors, int from, int side, bool undecided) {
        std::vector<int> depth(colors.size(), -1);
        std::vector<int> queue{from};
        depth[from] = 0;
        for (std::size_t i = 0; i < queue.size(); ++i) {
            const int a = queue[i];
            charge(near[a].size() + 1);
            for (int b : near[a]) {
                if (depth[b] < 0 && (colors[b] == side || (undecided && colors[b] < 0))) {
                    depth[b] = depth[a] + 1;
                    queue.push_back(b);
                }
            }
        }
        return depth;
    }

    bool cost_pressure(Colors& colors, bool& change) {
        std::vector<int> one(colors.size(), 0), zero(colors.size(), 0);
        int committed = 0;
        charge(residual.size() + colors.size());
        for (const auto& e : residual) {
            const auto a = colors[e.a], b = colors[e.b];
            if (a < 0) {
                if (b == 0) one[e.a] += e.forward;
                if (b == 1) zero[e.a] += e.reverse;
            } else if (b < 0) {
                if (a == 0) one[e.b] += e.reverse;
                if (a == 1) zero[e.b] += e.forward;
            } else if (a != b) {
                committed += a == 1 ? e.forward : e.reverse;
            }
        }
        for (std::size_t i = 0; i < colors.size(); ++i)
            if (colors[i] < 0) committed += std::min(one[i], zero[i]);
        if (committed > slack) return false;
        for (std::size_t i = 0; i < colors.size(); ++i) {
            if (colors[i] >= 0) continue;
            if (zero[i] - one[i] > slack - committed) colors[i] = 1;
            if (one[i] - zero[i] > slack - committed) colors[i] = 0;
            if (colors[i] >= 0) change = true;
        }
        return true;
    }

    bool propagate(Colors& colors) {
        for (bool change = true; change;) {
            change = false;
            if (!cost_pressure(colors, change)) return false;
            for (int side : {0, 1}) {
                auto can_reach = reachable(colors, side ? root : outside, side, true);
                for (std::size_t i = 0; i < colors.size(); ++i) {
                    if (can_reach[i] >= 0) continue;
                    if (colors[i] == side) return false;
                    if (colors[i] < 0) {
                        colors[i] = 1 - side;
                        change = true;
                    }
                }
            }
        }
        return true;
    }

    // If two fixed knots of one shore are still separated, every connecting
    // path meets each distance level between the fixed root and the nearest
    // fixed knot outside its present component.
    std::vector<int> connecting_level(const Colors& colors, int anchor, int side) {
        const auto joined = reachable(colors, anchor, side, false);
        const auto possible = reachable(colors, anchor, side, true);
        int first = colors.size();
        // Distances from the whole joined component, rather than its root.
        std::vector<int> level(colors.size(), -1), queue;
        for (std::size_t i = 0; i < colors.size(); ++i)
            if (joined[i] >= 0) {
                level[i] = 0;
                queue.push_back(i);
            }
        for (std::size_t i = 0; i < queue.size() && level[queue[i]] < first; ++i) {
            const int a = queue[i];
            charge(near[a].size() + 1);
            for (int b : near[a]) {
                if (possible[b] < 0 || level[b] >= 0) continue;
                level[b] = level[a] + 1;
                if (colors[b] == side) first = std::min(first, level[b]);
                queue.push_back(b);
            }
        }
        if (first == int(colors.size())) return {};
        std::vector<std::vector<int>> choices(first);
        for (int b : queue)
            if (level[b] > 0 && level[b] < first) {
                assert(colors[b] == -1);
                choices[level[b]].push_back(b);
            }
        assert(first >= 2);
        return *std::min_element(choices.begin() + 1, choices.end(),
                                 [](const auto& a, const auto& b) { return a.size() < b.size(); });
    }

    int total(const Colors& colors) const {
        int cost = 0;
        for (const auto& e : residual) {
            if (colors[e.a] > colors[e.b]) cost += e.forward;
            if (colors[e.a] < colors[e.b]) cost += e.reverse;
        }
        return cost;
    }

    bool complete(Colors colors, int free_side) {
        for (auto& color : colors)
            if (color < 0) color = free_side;
        charge(residual.size());
        if (total(colors) > slack) return false;
        for (int side : {0, 1}) {
            auto depth = reachable(colors, side ? root : outside, side, false);
            for (std::size_t i = 0; i < colors.size(); ++i)
                if (colors[i] == side && depth[i] < 0) return false;
        }
        witness = std::move(colors);
        return true;
    }

    bool search(Colors colors) {
        ++nodes;
        if (!propagate(colors)) return false;
        if (complete(colors, 0) || complete(colors, 1)) return true;
        auto options = connecting_level(colors, root, 1);
        auto other = connecting_level(colors, outside, 0);
        int side = 1;
        if (!other.empty() && (options.empty() || other.size() < options.size())) {
            side = 0;
            options = std::move(other);
        }
        if (options.empty()) {
            // The all-outside completion failed; any different connected
            // inside shore must add some first undecided neighbor.
            std::vector<bool> seen(colors.size(), false);
            for (std::size_t a = 0; a < colors.size(); ++a)
                if (colors[a] == 1)
                    for (int b : near[a])
                        if (colors[b] < 0 && !seen[b]) {
                            options.push_back(b);
                            seen[b] = true;
                        }
        }
        std::sort(options.begin(), options.end(),
                  [&](int a, int b) { return near[a].size() < near[b].size(); });
        for (int a : options) {
            colors[a] = side;
            if (search(colors)) return true;
            colors[a] = 1 - side;
        }
        return false;
    }
};

int main() {
    int n, m, exterior, width;
    if (!(std::cin >> n >> m >> exterior >> width)) return 1;
    std::vector<std::vector<int>> near(n);
    std::vector<Link> base(m);
    for (auto& e : base) {
        std::cin >> e.a >> e.b >> e.capacity;
        near[e.a].push_back(e.b);
        near[e.b].push_back(e.a);
    }
    int threshold, count;
    long long budget;
    while (std::cin >> threshold >> budget >> count && count > 0) {
        Dinic network(n + 2);
        std::vector<int> addresses;
        for (const auto& e : base) {
            addresses.push_back(network.graph[e.a].size());
            network.add(e.a, e.b, e.capacity, e.capacity);
        }
        Colors colors(n, -1);
        colors[exterior] = 0;
        int root = -1;
        for (int i = 0; i < count; ++i) {
            int knot, color;
            std::cin >> knot >> color;
            colors[knot] = color;
        }
        for (int knot = 0; knot < n; ++knot) {
            if (colors[knot] == 1) {
                if (root < 0) root = knot;
                network.add(n, knot, width + 1, 0);
            } else if (colors[knot] == 0) {
                network.add(knot, n + 1, width + 1, 0);
            }
        }
        assert(root >= 0 && colors[exterior] == 0);
        const int lower = network.maximum(n, n + 1);
        std::vector<ResidualLink> residual;
        std::vector<int> balance(n, 0);
        for (std::size_t i = 0; i < base.size(); ++i) {
            const auto& e = base[i];
            const auto& a = network.graph[e.a][addresses[i]];
            const int back = network.graph[e.b][a.reverse].capacity;
            assert(a.capacity >= 0 && back >= 0 && a.capacity + back == 2 * e.capacity);
            residual.push_back({e.a, e.b, a.capacity, back});
            balance[e.a] += e.capacity - a.capacity;
            balance[e.b] -= e.capacity - a.capacity;
        }
        int start = 0, finish = 0;
        for (int i = 0; i < n; ++i) {
            if (colors[i] == 1) start += balance[i];
            else if (colors[i] == 0) finish += balance[i];
            else assert(balance[i] == 0);
        }
        assert(start == lower && finish == -lower);
        if (lower > threshold) {
            std::cout << "excluded " << lower << " 0 0 -1 0\n" << std::flush;
            continue;
        }
        Feasibility search{near, residual, exterior, root, threshold - lower, budget, 0, 0, {}};
        bool found = false;
        const char* status = "excluded";
        try {
            found = search.search(std::move(colors));
            if (found) status = "witness";
        } catch (const Capped&) {
            status = "capped";
        }
        const auto& witness = search.witness;
        const int size = std::count(witness.begin(), witness.end(), 1);
        std::cout << status << ' ' << lower << ' ' << search.nodes << ' ' << search.work << ' '
                  << (found ? lower + search.total(witness) : -1) << ' ' << size;
        for (int i = 0; i < int(witness.size()); ++i)
            if (witness[i] == 1) std::cout << ' ' << i;
        std::cout << '\n' << std::flush;
    }
}
