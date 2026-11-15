// Decide a leaf budget using exact affine hulls of both complete relations.
#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <unordered_map>

template<int D> class Search {
    static constexpr int N = 1 << D;
    static constexpr int Words = (N + 63) / 64;
    static constexpr int n = D - 3;
    static constexpr int m = n - 1;

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

    int a_mask, b_mask;
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
    bool is_root_representative(int q) const {
        int outputs = q >> n;
        int h = ((outputs & 1) ? (1 << m) - 1 : 0) ^
                ((outputs & 2) ? a_mask : 0) ^ ((outputs & 4) ? b_mask : 0);
        Basis rows{};
        for (int i = 0; i < n; ++i) {
            int row = 0;
            if (i > 0 && ((h >> (i - 1)) & 1)) row ^= 1 << (i - 1);
            if (i < m && ((h >> i) & 1)) row ^= 1 << (i + 1);
            insert(rows, row);
        }
        int x = q & ((1 << n) - 1);
        return reduce(rows, x) == x;
    }

    bool within(const Bits& cell, int budget, bool is_root) {
        if (cell.empty()) return true;
        if (budget <= 1) return false;
        auto& memo = decisions[budget];
        auto saved = memo.find(cell);
        if (saved != memo.end()) return saved->second;
        std::array<int, 3> chosen{};
        bool result = split(cell, budget, is_root, chosen);
        memo.emplace(cell, result);
        return result;
    }
    bool split(const Bits& cell, int budget, bool is_root, std::array<int, 3>& chosen) {
        int coordinates = independent_coordinates(cell);
        for (int q = coordinates; q; q = (q - 1) & coordinates) {
            if (is_root && !is_root_representative(q)) continue;
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
                    ? within(low, i, false) && within(high, j, false)
                    : within(high, j, false) && within(low, i, false);
                if (fits) {
                    chosen = {q, i, j};
                    return true;
                }
            }
        }
        return false;
    }
    void print_tree(const Bits& cell, int budget, bool is_root) {
        if (cell.empty()) { std::cout << "null"; return; }
        std::array<int, 3> chosen{};
        if (!split(cell, budget, is_root, chosen)) throw std::logic_error("no witnessing split");
        auto [q, i, j] = chosen;
        std::cout << "[" << q << ",";
        print_tree(saturate(part(cell, planes()[q], false)), i, false);
        std::cout << ",";
        print_tree(saturate(part(cell, planes()[q], true)), j, false);
        std::cout << "]";
    }

public:
    Search(int a, int b) : a_mask(a), b_mask(b) {
        for (int i = 0; i < N; ++i) {
            int x = i & ((1 << n) - 1), products = x & (x >> 1);
            int s = (i >> n) & 1, av = (i >> (n + 1)) & 1, bv = (i >> (n + 2)) & 1;
            if (s == parity(products) && av == parity(products & a)) left.set(i);
            if (s != parity(products) && bv == parity(products & b)) right.set(i);
            root.set(i);
        }
        root = saturate(root);
    }
    bool solve(int budget) {
        if (budget < 1 || budget > 9) throw std::invalid_argument("unsupported terminal budget");
        return within(root, budget, true);
    }
    void witness(int budget) { print_tree(root, budget, true); }
};

static int reversed(int i, int m) {
    int result = 0;
    for (int j = 0; j < m; ++j) if ((i >> j) & 1) result |= 1 << (m - j - 1);
    return result;
}
static std::pair<int, int> representative(int a, int b, int m) {
    int all = (1 << m) - 1;
    auto standardized = [all](int x, int y) {
        x = std::min(x, x ^ all);
        y = std::min(y, y ^ all);
        return std::pair(std::min(x, y), std::max(x, y));
    };
    return std::min(standardized(a, b), standardized(reversed(a, m), reversed(b, m)));
}

template<int D> void run(int budget, int which_a, int which_b, bool tree) {
    constexpr int m = D - 4;
    std::map<std::pair<int, int>, int> groups;
    for (int a = 0; a < 1 << m; ++a)
        for (int b = 0; b < 1 << m; ++b)
            ++groups[representative(a, b, m)];
    for (const auto& [g, multiplicity] : groups) {
        if (which_a >= 0 && g != representative(which_a, which_b, m)) continue;
        auto [a, b] = g;
        Search<D> model(a, b);
        bool success = model.solve(budget);
        std::cout << a << " " << b << " " << multiplicity << " " << success;
        if (tree && success) { std::cout << " "; model.witness(budget); }
        std::cout << std::endl;
    }
}

int main(int argc, char** argv) {
    if (argc != 3 && argc != 5 && argc != 6) {
        std::cerr << "Use EDGES LEAF_BUDGET [MASK_A MASK_B [--tree]]\n";
        return 1;
    }
    int m = std::stoi(argv[1]), budget = std::stoi(argv[2]);
    int a = argc >= 5 ? std::stoi(argv[3]) : -1;
    int b = argc >= 5 ? std::stoi(argv[4]) : -1;
    bool tree = argc == 6 && std::string(argv[5]) == "--tree";
    if (argc == 6 && !tree) throw std::invalid_argument("unknown option");
    if (m < 1 || m > 5) throw std::invalid_argument("finite census supports one through five edges");
    if (argc >= 5 && (a < 0 || b < 0 || a >= (1 << m) || b >= (1 << m)))
        throw std::invalid_argument("invalid sketch masks");
    switch (m) {
        case 1: run<5>(budget, a, b, tree); break;
        case 2: run<6>(budget, a, b, tree); break;
        case 3: run<7>(budget, a, b, tree); break;
        case 4: run<8>(budget, a, b, tree); break;
        case 5: run<9>(budget, a, b, tree); break;
    }
}
