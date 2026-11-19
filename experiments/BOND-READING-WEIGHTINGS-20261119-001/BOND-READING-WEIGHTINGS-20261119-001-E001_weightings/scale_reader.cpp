// One exact undirected maximum flow and one residual SCC decomposition per holder pair.
#include <algorithm>
#include <cstdint>
#include <limits>
#include <queue>
#include <vector>

namespace {
class Network {
    std::vector<std::vector<int>> adjacent;
    std::vector<int> target, capacity, residual, level, cursor;
    std::vector<int> order, component;
    std::vector<unsigned char> seen;

    bool levels(int source, int sink) {
        std::fill(level.begin(), level.end(), -1);
        std::queue<int> pending;
        pending.push(source);
        level[source] = 0;
        while (!pending.empty()) {
            int u = pending.front();
            pending.pop();
            for (int arc : adjacent[u]) {
                int v = target[arc];
                if (residual[arc] > 0 && level[v] == -1) {
                    level[v] = level[u] + 1;
                    pending.push(v);
                }
            }
        }
        return level[sink] != -1;
    }

    int send(int u, int sink, int available) {
        if (u == sink) return available;
        for (int &i = cursor[u]; i < static_cast<int>(adjacent[u].size()); ++i) {
            int arc = adjacent[u][i], v = target[arc];
            if (residual[arc] > 0 && level[v] == level[u] + 1) {
                int pushed = send(v, sink, std::min(available, residual[arc]));
                if (pushed > 0) {
                    residual[arc] -= pushed;
                    residual[arc ^ 1] += pushed;
                    return pushed;
                }
            }
        }
        return 0;
    }

    void postorder(int u) {
        seen[u] = true;
        for (int arc : adjacent[u]) {
            if (residual[arc] > 0 && !seen[target[arc]]) postorder(target[arc]);
        }
        order.push_back(u);
    }

    void assign_component(int u, int id) {
        component[u] = id;
        for (int arc : adjacent[u]) {
            int v = target[arc];
            if (residual[arc ^ 1] > 0 && component[v] == -1) assign_component(v, id);
        }
    }

    void sink_reachable(int u) {
        seen[u] = true;
        for (int arc : adjacent[u]) {
            int v = target[arc];
            if (residual[arc ^ 1] > 0 && !seen[v]) sink_reachable(v);
        }
    }

public:
    explicit Network(int n): adjacent(n), level(n), cursor(n), component(n), seen(n) {}

    void add(int u, int v, int size) {
        adjacent[u].push_back(static_cast<int>(target.size()));
        target.push_back(v);
        capacity.push_back(size);
        adjacent[v].push_back(static_cast<int>(target.size()));
        target.push_back(u);
        capacity.push_back(size);
    }

    std::uint32_t row(int source, int sink, unsigned char *result) {
        residual = capacity;
        std::uint32_t value = 0;
        while (levels(source, sink)) {
            std::fill(cursor.begin(), cursor.end(), 0);
            while (int more = send(source, sink, std::numeric_limits<int>::max())) value += more;
        }
        // The last level search kept exactly the vertices reachable from source.
        order.clear();
        std::fill(seen.begin(), seen.end(), false);
        for (int i = 0; i < static_cast<int>(adjacent.size()); ++i) if (!seen[i]) postorder(i);
        std::fill(component.begin(), component.end(), -1);
        for (auto i = order.rbegin(); i != order.rend(); ++i) {
            if (component[*i] == -1) assign_component(*i, *i);
        }
        std::fill(seen.begin(), seen.end(), false);
        sink_reachable(sink);
        for (int arc = 0; arc < static_cast<int>(target.size()); ++arc) {
            int a = target[arc ^ 1], b = target[arc];
            if (residual[arc] == 0 && component[a] != component[b] &&
                level[b] == -1 && !seen[a]) {
                int j = arc / 2;
                result[j / 8] |= static_cast<unsigned char>(1u << (j % 8));
            }
        }
        return value;
    }
};
}

extern "C" int marked_minimum_rows(int vertices, int classes, const int *links,
                                   std::uint32_t *sizes, unsigned char *rows) {
    if (vertices <= 0 || classes < 0) return 1;
    std::int64_t total = 0;
    Network network(vertices);
    for (int j = 0; j < classes; ++j) {
        int a = links[3*j], b = links[3*j+1], w = links[3*j+2];
        if (a < 0 || b < 0 || a >= vertices || b >= vertices || a == b || w <= 0) return 1;
        total += w;
        if (total > std::numeric_limits<int>::max() / 2) return 1;
        network.add(a,b,w);
    }
    std::size_t stride = (static_cast<std::size_t>(classes) + 7) / 8;
    for (int i = 0; i < classes; ++i) {
        unsigned char *row = rows + i*stride;
        std::fill(row, row + stride, 0);
        sizes[i] = network.row(links[3*i], links[3*i+1], row);
    }
    return 0;
}
