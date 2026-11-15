// Exact one-sided affine-cell minimax, adapted from the dependency's small-path kernel.
#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

template<int D> class Search {
    static constexpr int N = 1 << D;
    static constexpr int Words = (N + 63) / 64;


    struct Bits {
        std::array<uint64_t, Words> words{};
        bool operator==(const Bits&) const = default;
        void set(int i) { words[i / 64] |= uint64_t{1} << (i % 64); }
        bool empty() const {
            for (auto word : words) if (word) return false;
            return true;
        }
        int size() const {
            int total = 0;
            for (auto word : words) total += std::popcount(word);
            return total;
        }
    };

    struct Hash {
        size_t operator()(const Bits& bits) const {
            uint64_t hash = 0x9e3779b97f4a7c15ULL;
            for (auto word : bits.words)
                hash = (hash ^ (word + 0x517cc1b727220a95ULL)) * 0x94d049bb133111ebULL;
            return hash ^ (hash >> 32);
        }
    };

    using Basis = std::array<int, D>;
    struct Span {
        int origin = -1;
        int dim = 0;
        Basis rows{};
    };

    int uniform_depth = 0;
    Bits left, right, root;
    std::unordered_map<Bits, Bits, Hash> saved_closures;
    std::array<std::unordered_map<Bits, bool, Hash>, 10> decisions;

    static int parity(int v) { return std::popcount((unsigned)v) & 1; }
    static int dimension(const Bits& cell) {
        return cell.empty() ? -1 : int(std::bit_width((unsigned)cell.size())) - 1;
    }
    static bool insert(Basis& rows, int v) {
        while (v) {
            int j = std::bit_width((unsigned)v) - 1;
            if (!rows[j]) {
                rows[j] = v;
                return true;
            }
            v ^= rows[j];
        }
        return false;
    }
    static int reduce(const Basis& rows, int v) {
        for (int i = D - 1; i >= 0; --i)
            if ((v >> i) & 1) v ^= rows[i];
        return v;
    }
    static Span span(const Bits& points, int ambient_dim) {
        Span basis;
        for (int w = 0; w < Words; ++w) {
            auto word = points.words[w];
            while (word) {
                int i = 64 * w + std::countr_zero(word);
                word &= word - 1;
                if (basis.origin < 0) basis.origin = i;
                else if (insert(basis.rows, i ^ basis.origin)) ++basis.dim;
                if (basis.dim == ambient_dim) return basis;
            }
        }
        return basis;
    }
    static Bits expand(const Span& basis) {
        Bits result;
        if (basis.origin < 0) return result;
        std::array<int, N> points;
        points[0] = basis.origin;
        int count = 1;
        for (auto direction : basis.rows) {
            if (!direction) continue;
            for (int i = 0; i < count; ++i) points[count + i] = points[i] ^ direction;
            count *= 2;
        }
        for (int i = 0; i < count; ++i) result.set(points[i]);
        return result;
    }
    static Bits meet(const Bits& a, const Bits& b) {
        Bits c;
        for (int w = 0; w < Words; ++w) c.words[w] = a.words[w] & b.words[w];
        return c;
    }
    static Bits part(const Bits& cell, const Bits& plane, bool high) {
        Bits c;
        for (int w = 0; w < Words; ++w)
            c.words[w] = cell.words[w] & (high ? plane.words[w] : ~plane.words[w]);
        return c;
    }
    static const auto& planes() {
        static const auto table = [] {
            std::array<Bits, N> result{};
            for (int q = 1; q < N; ++q)
                for (int v = 0; v < N; ++v)
                    if (parity(q & v)) result[q].set(v);
            return result;
        }();
        return table;
    }
    Bits saturate(Bits cell) {
        auto saved = saved_closures.find(cell);
        if (saved != saved_closures.end()) return saved->second;
        Bits start = cell;
        while (!cell.empty()) {
            int dim = dimension(cell);
            auto l = span(meet(left, cell), dim);
            if (l.origin < 0) { cell = {}; break; }
            auto r = span(meet(right, cell), dim);
            if (r.origin < 0) { cell = {}; break; }
            if (l.dim == dim && r.dim == dim) break;
            if (l.dim == dim) cell = expand(r);
            else if (r.dim == dim) cell = expand(l);
            else cell = meet(expand(l), expand(r));
        }
        // Large cells recur often. Computing the remaining cells again saves memory.
        if (dimension(start) >= D - 3) saved_closures.emplace(start, cell);
        return cell;
    }
    static int independent_coordinates(const Bits& cell) {
        auto basis = span(cell, dimension(cell));
        int result = 0;
        for (int i = 0; i < D; ++i) if (basis.rows[i]) result |= 1 << i;
        return result;
    }
    bool within(const Bits& cell, int budget) {
        if (cell.empty()) return true;
        if (budget <= 1) return false;
        int remaining_depth = uniform_depth - (D - dimension(cell));
        if (remaining_depth > 0 && budget < (1 << remaining_depth)) return false;
        auto& memo = decisions[budget];
        auto saved = memo.find(cell);
        if (saved != memo.end()) return saved->second;
        std::array<int, 3> chosen{};
        bool result = split(cell, budget, chosen);
        memo.emplace(cell, result);
        return result;
    }
    bool split(const Bits& cell, int budget, std::array<int, 3>& chosen) {
        int coordinates = independent_coordinates(cell);
        for (int q = coordinates; q; q = (q - 1) & coordinates) {
            auto low = saturate(part(cell, planes()[q], false));
            if (budget == 2 && !low.empty()) continue;
            auto high = saturate(part(cell, planes()[q], true));
            int first = low.empty() ? 1 : 2;
            int last = budget - (high.empty() ? 1 : 2);
            if (low.empty()) last = std::min(last, 1);
            if (high.empty() && !low.empty()) first = last;
            for (int i = first; i <= last; ++i) {
                int j = budget - i;
                bool fits = i <= j
                    ? within(low, i) && within(high, j)
                    : within(high, j) && within(low, i);
                if (fits) {
                    chosen = {q, i, j};
                    return true;
                }
            }
        }
        return false;
    }
    void print_tree(const Bits& cell, int budget) {
        if (cell.empty()) { std::cout << "null"; return; }
        std::array<int, 3> chosen{};
        if (!split(cell, budget, chosen)) throw std::logic_error("no witnessing split");
        auto [q, i, j] = chosen;
        std::cout << "[" << q << ",";
        print_tree(saturate(part(cell, planes()[q], false)), i);
        std::cout << ",";
        print_tree(saturate(part(cell, planes()[q], true)), j);
        std::cout << "]";
    }

public:
    Search(int inputs, const std::vector<int>& table, int fixed_b) {
        if (D != inputs + (fixed_b < 0 ? 2 : 1) || table.size() != (1U << inputs))
            throw std::invalid_argument("wrong input and output dimensions");
        for (int v = 0; v < N; ++v) {
            int x = v & ((1 << inputs) - 1);
            int checksum = parity(x & (x >> 1));
            int s = (v >> inputs) & 1;
            int b = fixed_b < 0 ? v >> (inputs + 1) : fixed_b;
            if (s == checksum) left.set(v);
            if (s != checksum && b == table[x]) right.set(v);
            root.set(v);
        }
        root = saturate(root);
    }

    // Certify the optional shallow lower bound from the actual relations, including all constants.
    // At dimension D the full space must survive unchanged, as must all affine hyperplanes.
    std::array<int, 3> audit_shallow() {
        if (dimension(root) != D) throw std::logic_error("root was already restricted");
        for (int q = 1; q < N; ++q)
            for (bool answer : {false, true}) {
                auto cell = part(root, planes()[q], answer);
                if (saturate(cell) != cell) throw std::logic_error("a hyperplane changed");
            }
        uniform_depth = 2;
        int total = 0, empty = 0, reduced = 0;
        for (int q = 1; q < N; ++q)
            for (int h = q + 1; h < N; ++h) {
                if ((q ^ h) <= h) continue;  // take the smallest two of the three nonzero row forms
                for (bool v : {false, true})
                    for (bool w : {false, true}) {
                        auto cell = part(part(root, planes()[q], v), planes()[h], w);
                        auto fixed = saturate(cell);
                        ++total;
                        if (fixed.empty()) ++empty;
                        else if (fixed != cell) ++reduced;
                    }
            }
        if (empty == 0 && reduced == 0) uniform_depth = 3;
        return {total, empty, reduced};
    }
    bool solve(int budget) {
        if (budget < 1 || budget > 9) throw std::invalid_argument("unsupported terminal budget");
        return within(root, budget);
    }
    void witness(int budget) { print_tree(root, budget); }
};


template<int D> void full_tables(int inputs, int budget) {
    uint64_t truth;
    while (std::cin >> truth) {
        std::vector<int> table(1 << inputs);
        for (unsigned int x = 0; x < table.size(); ++x) table[x] = (truth >> x) & 1;
        Search<D> graph(inputs, table, -1);
        std::cout << truth << " " << graph.solve(budget) << "\n";
    }
}

int main(int argc, char** argv) {
    if (argc < 3) return 1;
    std::string mode = argv[1];
    if (mode == "tables" && argc == 4) {
        int inputs = std::stoi(argv[2]), budget = std::stoi(argv[3]);
        if (inputs == 4) full_tables<6>(inputs, budget);
        else if (inputs == 6) full_tables<8>(inputs, budget);
        else throw std::invalid_argument("packed truth tables use four or six inputs");
    } else if (mode == "fiber" && (argc == 4 || argc == 5)) {
        int b = std::stoi(argv[2]), budget = std::stoi(argv[3]);
        if (b != 0 && b != 1) throw std::invalid_argument("invalid sketch value");
        std::vector<int> even(256);
        for (int x = 0; x < 256; ++x)
            even[x] = std::popcount((unsigned)(x & (x >> 1) & 42)) & 1;
        Search<9> graph(8, even, b);
        auto [cells, empty, changed_live] = graph.audit_shallow();
        bool accepted = graph.solve(budget);
        std::cout << cells << " " << empty << " " << changed_live << " " << accepted;
        if (argc == 5 && std::string(argv[4]) == "--tree" && accepted) {
            std::cout << " ";
            graph.witness(budget);
        }
        std::cout << "\n";
    } else {
        throw std::invalid_argument("use tables INPUTS BUDGET or fiber B BUDGET [--tree]");
    }
}
