// Entry points appended to the archived exact connected-cut implementation
// by order_reader.py. Inputs use one weighted class per holder pair.

using WideMask = unsigned __int128;

constexpr WideMask wide_bit(int i) { return WideMask{1} << i; }

int first_wide(WideMask word) {
    if (auto lo = static_cast<std::uint64_t>(word)) return std::countr_zero(lo);
    return 64 + std::countr_zero(static_cast<std::uint64_t>(word >> 64));
}

int take_wide(WideMask& word) {
    int first = first_wide(word);
    word &= word - 1;
    return first;
}

struct WideIncidence {
    std::vector<int> ordinary;
    std::vector<std::vector<int>> own;
    bool live = false;
};

// End of wide declarations.
int main(int argc, char** argv) {
    if (argc != 2) return 2;
    const std::string mode(argv[1]);
    int n, m, q;
    if (!(std::cin >> n >> m >> q) || n < 2 || n > 128 || m < 1 || q < 1 || q > m) return 2;
    std::vector<census::Edge> edges(m);
    std::vector<int> queried(q);
    for (auto& e : edges)
        if (!(std::cin >> e.u >> e.v >> e.weight) || e.u < 0 || e.u >= e.v || e.v >= n || e.weight < 1) return 2;
    for (int& e : queried) if (!(std::cin >> e) || e < 0 || e >= m) return 2;

    if (mode == "unary") {
        census::WidePairTable::Block graph;
        for (const auto& [u, v, w] : edges) {
            graph.neighbors[u] |= census::wide_bit(v);
            graph.neighbors[v] |= census::wide_bit(u);
            graph.capacity[u][v] = graph.capacity[v][u] = w;
        }
        for (int j : queried) {
            const auto& e = edges[j];
            auto [cost, shore] = graph.relax(census::wide_bit(e.u), census::wide_bit(e.v), Inf);
            std::cout << cost << '\n';
        }
    } else if (mode == "pairs") {
        if (n <= 19) {
            for (const auto& row : census::shore_table(n, edges, queried)) {
                for (int size : row) std::cout << size << ' ';
                std::cout << '\n';
            }
            return 0;
        }
        census::WideIncidence parity;
        parity.ordinary.resize(n);
        std::vector<int> start;
        for (const auto& [u, v, w] : edges) {
            start.push_back(parity.own.size());
            for (int j = 0; j < w; ++j) parity.own.push_back({u,v});
        }
        std::vector<int> target;
        for (int j : queried) target.push_back(start[j]);
        const census::WidePairTable table(parity, target);
        for (int label : target) {
            for (int first : start) {
                int size = table.minima[table.cls[label]][table.cls[first]];
                std::cout << (size == Inf ? -1 : size) << ' ';
            }
            std::cout << '\n';
        }
    } else return 2;
}
