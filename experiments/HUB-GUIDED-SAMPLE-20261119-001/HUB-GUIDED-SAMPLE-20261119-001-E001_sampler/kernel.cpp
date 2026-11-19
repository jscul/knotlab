#include <algorithm>
#include <bit>
#include <chrono>
#include <cstdint>
#include <deque>
#include <fstream>
#include <iostream>
#include <limits>
#include <map>
#include <memory>
#include <numeric>
#include <optional>
#include <random>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_map>
#include <utility>
#include <vector>

using Word = std::uint64_t;
using Mask = std::vector<Word>;

// Base-2^32 digits keep counts and sampling masses independent of floating point.
class Integer {
    std::vector<std::uint32_t> digits;

    void normalize() {
        while (!digits.empty() && digits.back() == 0) digits.pop_back();
    }

    Word digit(std::size_t i) const { return i < digits.size() ? digits[i] : 0; }

public:
    Integer(Word value = 0) {
        if (value) digits.push_back(value);
        if (value >> 32) digits.push_back(value >> 32);
    }

    explicit operator bool() const { return !digits.empty(); }
    bool operator==(const Integer& other) const {
        if (digits.size() != other.digits.size()) return false;
        for (std::size_t i = 0; i < digits.size(); ++i) {
            if (digits[i] != other.digits[i]) return false;
        }
        return true;
    }
    bool operator<(const Integer& other) const {
        if (digits.size() != other.digits.size()) return digits.size() < other.digits.size();
        return std::lexicographical_compare(digits.rbegin(), digits.rend(),
                                            other.digits.rbegin(), other.digits.rend());
    }
    bool operator>(const Integer& other) const { return other < *this; }

    Integer& operator+=(const Integer& other) {
        digits.resize(std::max(digits.size(), other.digits.size()));
        Word carry = 0;
        for (std::size_t i = 0; i < digits.size(); ++i) {
            const Word result = digit(i) + other.digit(i) + carry;
            digits[i] = result;
            carry = result >> 32;
        }
        if (carry) digits.push_back(carry);
        return *this;
    }

    Integer& operator-=(const Integer& other) {
        if (*this < other) throw std::runtime_error("negative count");
        Word borrow = 0;
        for (std::size_t i = 0; i < digits.size(); ++i) {
            const Word subtrahend = other.digit(i) + borrow;
            const Word minuend = digit(i);
            digits[i] = minuend - subtrahend;
            borrow = minuend < subtrahend;
        }
        normalize();
        return *this;
    }

    Integer& operator*=(const Integer& other) {
        if (!*this || !other) {
            digits.clear();
            return *this;
        }
        if (other == 1) return *this;
        if (*this == 1) {
            digits = other.digits;
            return *this;
        }
        std::vector<std::uint32_t> product(digits.size() + other.digits.size());
        for (std::size_t i = 0; i < digits.size(); ++i) {
            Word carry = 0;
            for (std::size_t j = 0; j < other.digits.size(); ++j) {
                const Word result = digit(i) * other.digit(j) + product[i + j] + carry;
                product[i + j] = result;
                carry = result >> 32;
            }
            product[i + other.digits.size()] = carry;
        }
        digits = std::move(product);
        normalize();
        return *this;
    }

    friend Integer operator+(Integer a, const Integer& b) { return a += b; }
    friend Integer operator-(Integer a, const Integer& b) { return a -= b; }
    friend Integer operator*(Integer a, const Integer& b) { return a *= b; }

    int bit_length() const {
        if (digits.empty()) return 0;
        return 32 * (digits.size() - 1) + std::bit_width(digits.back());
    }

    Word as_word() const {
        if (digits.size() > 2) throw std::runtime_error("count exceeds a word");
        return (digit(1) << 32) | digit(0);
    }

    static Integer random_bits(int bits, std::mt19937_64& rng) {
        Integer output;
        for (int i = 0; i < bits; i += 32) {
            std::uint32_t word = rng();
            if (bits - i < 32) word >>= 32 - (bits - i);
            output.digits.push_back(word);
        }
        output.normalize();
        return output;
    }

    std::string str() const {
        if (digits.size() <= 2) return std::to_string(as_word());
        auto remaining = digits;
        std::vector<std::uint32_t> group;
        while (!remaining.empty()) {
            Word carry = 0;
            for (auto i = remaining.rbegin(); i != remaining.rend(); ++i) {
                const Word active = (carry << 32) | *i;
                *i = active / 1000000000;
                carry = active % 1000000000;
            }
            group.push_back(carry);
            while (!remaining.empty() && !remaining.back()) remaining.pop_back();
        }
        std::string output = std::to_string(group.back());
        for (auto i = group.rbegin() + 1; i != group.rend(); ++i) {
            const std::string current = std::to_string(*i);
            output += std::string(9 - current.size(), '0') + current;
        }
        return output;
    }

    friend std::ostream& operator<<(std::ostream& out, const Integer& count) { return out << count.str(); }
};

void set_bit(Mask& mask, int v) {
    mask[v / 64] |= Word{1} << (v % 64);
}

void clear_bit(Mask& mask, int v) {
    mask[v / 64] &= ~(Word{1} << (v % 64));
}

bool has_bit(const Mask& mask, int v) {
    return (mask[v / 64] >> (v % 64)) & 1;
}

int count_bits(const Mask& mask) {
    int count = 0;
    for (Word word : mask) count += std::popcount(word);
    return count;
}

int first_bit(const Mask& mask) {
    for (int w = 0; w < static_cast<int>(mask.size()); ++w) {
        if (mask[w]) return w * 64 + std::countr_zero(mask[w]);
    }
    return -1;
}

template<class F>
void for_bits(Word word, F operation) {
    for (; word; word &= word - 1) operation(std::countr_zero(word));
}

std::vector<int> members(const Mask& mask, int limit = std::numeric_limits<int>::max()) {
    std::vector<int> out;
    for (int w = 0; w < static_cast<int>(mask.size()); ++w) {
        for (Word word = mask[w]; word; word &= word - 1) {
            if (static_cast<int>(out.size()) == limit) return out;
            out.push_back(w * 64 + std::countr_zero(word));
        }
    }
    return out;
}

struct Graph {
    int literal = 0;
    int n = 0;
    int width = 0;
    std::size_t cache_limit = 0;
    std::size_t cached = 0;
    std::vector<Mask> blocks;
    std::vector<std::vector<int>> affiliation;
    std::vector<int> block_sizes;
    std::vector<int> largest_blocks;
    std::vector<std::unique_ptr<Mask>> cached_rows;
    Mask scratch_row;

    Graph(const char* path, const std::string& order, std::uint64_t seed, int cache_mib, bool quotient) {
        std::ifstream source(path);
        int count;
        if (!(source >> literal >> count) || literal < 1 || count < 0) {
            throw std::runtime_error("invalid block-file header");
        }
        std::string line;
        std::getline(source, line);
        std::vector<std::vector<int>> original(literal);
        block_sizes.resize(count);
        for (int b = 0; b < count; ++b) {
            if (!std::getline(source, line)) throw std::runtime_error("missing block");
            std::istringstream row(line);
            std::vector<int> values;
            for (int v; row >> v;) {
                if (v < 0 || v >= literal) throw std::runtime_error("invalid index");
                values.push_back(v);
            }
            if (!row.eof()) throw std::runtime_error("invalid block");
            std::sort(values.begin(), values.end());
            if (values.size() < 2 || std::adjacent_find(values.begin(), values.end()) != values.end()) {
                throw std::runtime_error("block must consist of distinct junctions");
            }
            block_sizes[b] = static_cast<int>(values.size());
            for (int v : values) original[v].push_back(b);
        }
        if (source >> line) throw std::runtime_error("extra block data");

        // A common nonempty affiliation implies identical closed candidate
        // rows. Retain each empty-affiliation junction separately.
        std::map<std::vector<int>, int> seen;
        std::vector<int> representatives;
        for (int v = 0; v < literal; ++v) {
            if (quotient && !original[v].empty() && !seen.emplace(original[v], v).second) continue;
            representatives.push_back(v);
        }
        std::vector<std::pair<int, std::uint64_t>> coverage(literal);
        for (int v : representatives) {
            for (int b : original[v]) {
                coverage[v].first = std::max(coverage[v].first, block_sizes[b]);
                coverage[v].second += block_sizes[b];
            }
        }
        std::stable_sort(representatives.begin(), representatives.end(), [&](int a, int b) {
            if (order == "total") {
                return std::tie(coverage[a].second, coverage[a].first) >
                       std::tie(coverage[b].second, coverage[b].first);
            }
            return coverage[a] > coverage[b];
        });
        if (order == "reverse") std::reverse(representatives.begin(), representatives.end());
        else if (order == "shuffle") {
            std::mt19937_64 rng(seed);
            std::shuffle(representatives.begin(), representatives.end(), rng);
        } else if (order != "coverage" && order != "total") {
            throw std::runtime_error("unknown ordering");
        }

        n = static_cast<int>(representatives.size());
        width = (n + 63) / 64;
        blocks.assign(count, Mask(width));
        largest_blocks.resize(count);
        std::iota(largest_blocks.begin(), largest_blocks.end(), 0);
        std::stable_sort(largest_blocks.begin(), largest_blocks.end(), [&](int a, int b) {
            return block_sizes[a] > block_sizes[b];
        });
        affiliation.reserve(n);
        for (int v : representatives) affiliation.push_back(std::move(original[v]));
        for (int v = 0; v < n; ++v) {
            auto& ids = affiliation[v];
            std::stable_sort(ids.begin(), ids.end(), [&](int a, int b) {
                return block_sizes[a] > block_sizes[b];
            });
            for (int b : ids) set_bit(blocks[b], v);
        }
        cached_rows.resize(n);
        scratch_row.resize(width);
        cache_limit = static_cast<std::size_t>(cache_mib) * (1ULL << 20) / (sizeof(Word) * width);
    }

    const Mask& row(int v) {
        if (cached_rows[v]) return *cached_rows[v];
        std::fill(scratch_row.begin(), scratch_row.end(), 0);
        set_bit(scratch_row, v);
        for (int b : affiliation[v]) {
            for (int w = 0; w < width; ++w) scratch_row[w] |= blocks[b][w];
        }
        if (cached < cache_limit) {
            cached_rows[v] = std::make_unique<Mask>(scratch_row);
            ++cached;
            return *cached_rows[v];
        }
        return scratch_row;
    }

    std::pair<int, int> best_block(const Mask& p, int witness, int p_count, bool use_global) const {
        if (!use_global) {
            int tried = 0;
            for (int b : affiliation[witness]) {
                bool contains = true;
                for (int w = 0; w < width; ++w) {
                    if (p[w] & ~blocks[b][w]) {
                        contains = false;
                        break;
                    }
                }
                if (contains) return {b, 0};
                if (++tried == 6) break;
            }
            return {-1, p_count};
        }
        int best = -1;
        int outside = p_count;
        auto inspect = [&](int b) {
            int missing = 0;
            for (int w = 0; w < width; ++w) {
                missing += std::popcount(p[w] & ~blocks[b][w]);
                if (missing >= outside) return;
            }
            best = b;
            outside = missing;
        };
        int tried = 0;
        for (int b : affiliation[witness]) {
            inspect(b);
            if (!outside || ++tried == 6) break;
        }
        if (outside) {
            int scanned = 0;
            for (int b : largest_blocks) {
                inspect(b);
                if (!outside || ++scanned == 8) break;
            }
        }
        return {best, outside};
    }
};

struct Statistics {
    std::uint64_t nodes = 0;
    std::uint64_t splits = 0;
    std::uint64_t pair_splits = 0;
    std::uint64_t block_priority = 0;
    std::uint64_t exact_leaves = 0;
    std::uint64_t empty_leaves = 0;
    std::uint64_t merges = 0;
    std::uint64_t forced = 0;
    std::uint64_t blocks = 0;
    std::uint64_t block_fringe = 0;
    std::uint64_t block_fringe_capped = 0;
    std::uint64_t components = 0;
    std::uint64_t local_states = 0;
    std::uint64_t local_twins = 0;
    std::uint64_t local_forests = 0;
    std::uint64_t local_bipartite = 0;
    std::uint64_t local_capped = 0;
    std::uint64_t local_cache_hits = 0;
};

struct SmallWorkLimit {};
struct SearchWorkLimit {};

struct SmallState {
    Word active;
    std::vector<Word> obligations;
    std::vector<Integer> weight;
};

struct SmallSolver {
    const std::vector<Word>& conflict;
    Statistics& stats;
    int ceiling;
    int worked = 0;
    std::unordered_map<std::string, Integer> cache;

    static void restrict_to(SmallState& state, Word active) {
        state.active = active;
        for (Word& q : state.obligations) q &= active;
    }

    void include(SmallState& state, int v) const {
        Word bit = Word{1} << v;
        state.obligations.erase(std::remove_if(state.obligations.begin(), state.obligations.end(),
                                               [&](Word q) { return q & bit; }), state.obligations.end());
        restrict_to(state, state.active & ~(conflict[v] | bit));
    }

    static void exclude(SmallState& state, int v, Word neighbors) {
        restrict_to(state, state.active & ~(Word{1} << v));
        state.obligations.push_back(neighbors & state.active);
    }

    static void deduplicate(SmallState& state) {
        auto& obligations = state.obligations;
        std::sort(obligations.begin(), obligations.end());
        obligations.erase(std::unique(obligations.begin(), obligations.end()), obligations.end());
        if (obligations.size() > 128) return;
        std::sort(obligations.begin(), obligations.end(), [](Word a, Word b) {
            return std::pair{std::popcount(a), a} < std::pair{std::popcount(b), b};
        });
        std::size_t kept = 0;
        for (Word q : obligations) {
            if (std::none_of(obligations.begin(), obligations.begin() + kept,
                             [q](Word kept_q) { return (q & kept_q) == kept_q; })) {
                obligations[kept++] = q;
            }
        }
        obligations.resize(kept);
    }

    bool reduce(SmallState& state, Integer& multiplicity) {
        deduplicate(state);
        if (!state.obligations.empty() && !state.obligations[0]) {
            multiplicity = 0;
            return false;
        }
        auto forced = std::find_if(state.obligations.begin(), state.obligations.end(),
                                   [](Word q) { return std::has_single_bit(q); });
        if (forced != state.obligations.end()) {
            int v = std::countr_zero(*forced);
            multiplicity *= state.weight[v];
            include(state, v);
            return true;
        }
        for (Word pending = state.active; pending; pending &= pending - 1) {
            int v = std::countr_zero(pending);
            if (conflict[v] & state.active) continue;
            multiplicity *= state.weight[v];
            include(state, v);
            return true;
        }
        // Open twins in the noncandidate relation are selected together.
        // Adjacent closed twins contribute the sum of their select weights.
        for (Word pending = state.active; pending; pending &= pending - 1) {
            int a = std::countr_zero(pending);
            for (Word peers = pending & (pending - 1); peers; peers &= peers - 1) {
                int b = std::countr_zero(peers);
                Word both = (Word{1} << a) | (Word{1} << b);
                if ((conflict[a] ^ conflict[b]) & state.active & ~both) continue;
                if (std::any_of(state.obligations.begin(), state.obligations.end(), [both](Word q) {
                    return std::has_single_bit(q & both);
                })) continue;
                if (conflict[a] & (Word{1} << b)) state.weight[a] += state.weight[b];
                else state.weight[a] *= state.weight[b];
                restrict_to(state, state.active & ~(Word{1} << b));
                ++stats.local_twins;
                return true;
            }
        }
        return false;
    }

    Word connected_part(const SmallState& state) const {
        Word front = state.active & -state.active;
        Word visited = front;
        while (front) {
            Word next = 0;
            for_bits(front, [&](int v) { next |= conflict[v]; });
            for (Word q : state.obligations) {
                if (q & front) next |= q;
            }
            front = next & state.active & ~visited;
            visited |= front;
        }
        return visited;
    }

    std::optional<Integer> forest(const SmallState& state) {
        const int n = static_cast<int>(conflict.size());
        const int orders = std::popcount(state.active) + static_cast<int>(state.obligations.size());
        int edges = 0;
        for_bits(state.active, [&](int v) { edges += std::popcount(conflict[v] & state.active); });
        edges /= 2;
        for (Word q : state.obligations) edges += std::popcount(q);
        if (edges != orders - 1) return std::nullopt;
        std::vector<std::vector<int>> adjacency(n + state.obligations.size());
        for_bits(state.active, [&](int v) {
            for_bits(conflict[v] & state.active, [&](int u) { adjacency[v].push_back(u); });
        });
        for (int q = 0; q < static_cast<int>(state.obligations.size()); ++q) {
            for_bits(state.obligations[q], [&](int v) {
                adjacency[v].push_back(n + q);
                adjacency[n + q].push_back(v);
            });
        }
        // States give the counts for selected, internally dominated, and
        // still requiring a selected parent.
        auto recurse = [&](auto&& self, int v, int parent) -> std::tuple<Integer, Integer, Integer> {
            Integer selected = v < n ? state.weight[v] : Integer(0);
            Integer unrestricted = 1;
            Integer requiring_parent = 1;
            for (int u : adjacency[v]) {
                if (u == parent) continue;
                auto [take, satisfied, pending] = self(self, u, v);
                selected *= satisfied + pending;
                unrestricted *= take + satisfied;
                requiring_parent *= satisfied;
            }
            return {selected, unrestricted - requiring_parent, requiring_parent};
        };
        ++stats.local_forests;
        auto [take, satisfied, pending] = recurse(recurse, std::countr_zero(state.active), -1);
        return take + satisfied;
    }

    std::optional<Integer> bipartite(const SmallState& state) {
        Word left = 0, right = 0;
        Word todo = state.active;
        while (todo) {
            Word front = todo & -todo;
            left |= front;
            todo ^= front;
            bool from_left = true;
            while (front) {
                Word next = 0;
                for_bits(front, [&](int v) { next |= conflict[v]; });
                next &= state.active;
                if (next & (from_left ? left : right)) return std::nullopt;
                front = next & todo;
                if (from_left) right |= front;
                else left |= front;
                todo ^= front;
                from_left = !from_left;
            }
        }
        if (std::popcount(left) > std::popcount(right)) std::swap(left, right);
        if (std::popcount(left) > 10) return std::nullopt;
        ++stats.local_bipartite;
        Integer total = 0;
        for (Word select = left;; select = (select - 1) & left) {
            Word opposite = right;
            for_bits(select, [&](int v) { opposite &= ~conflict[v]; });
            Word blocked = select;
            for_bits(opposite, [&](int v) { blocked |= conflict[v]; });
            if ((left & ~blocked) == 0 &&
                std::all_of(state.obligations.begin(), state.obligations.end(),
                            [select, opposite](Word q) { return q & (select | opposite); })) {
                Integer weight = 1;
                for_bits(select | opposite, [&](int v) { weight *= state.weight[v]; });
                total += weight;
            }
            if (!select) break;
        }
        return total;
    }

    static std::string key(const SmallState& state) {
        std::string out = std::to_string(state.active);
        for (Word q : state.obligations) {
            out += ':';
            out += std::to_string(q);
        }
        out += '|';
        for_bits(state.active, [&](int v) {
            if (state.weight[v] == 1) return;
            out += std::to_string(v);
            out += ':';
            out += state.weight[v].str();
            out += ',';
        });
        return out;
    }

    Integer solve(SmallState state) {
        if (++worked > ceiling) throw SmallWorkLimit{};
        ++stats.local_states;
        Integer factor = 1;
        while (reduce(state, factor)) {}
        if (factor == 0 || !state.active) return factor;
        auto cache_key = key(state);
        if (auto it = cache.find(cache_key); it != cache.end()) {
            ++stats.local_cache_hits;
            return factor * it->second;
        }
        Integer count = 0;
        Word component = connected_part(state);
        if (component != state.active) {
            SmallState part = state;
            part.active = component;
            part.obligations.clear();
            auto end = std::partition(state.obligations.begin(), state.obligations.end(),
                                      [component](Word q) { return (q & component) == 0; });
            part.obligations.assign(end, state.obligations.end());
            state.obligations.erase(end, state.obligations.end());
            state.active &= ~component;
            count = solve(std::move(part));
            if (count) count *= solve(std::move(state));
        } else if (auto tree_count = forest(state)) {
            count = *tree_count;
        } else if (auto bipartite_count = bipartite(state)) {
            count = *bipartite_count;
        } else {
            int branch = -1;
            int degree = -1;
            for_bits(state.active, [&](int v) {
                int current = std::popcount(conflict[v] & state.active);
                if (current > degree) {
                    branch = v;
                    degree = current;
                }
            });
            SmallState selected = state;
            include(selected, branch);
            count = state.weight[branch] * solve(std::move(selected));
            exclude(state, branch, conflict[branch]);
            count += solve(std::move(state));
        }
        if (cache.size() < 4096) cache.emplace(std::move(cache_key), count);
        return factor * count;
    }
};

struct State {
    Mask p;
    Mask x;
    Integer mass = 1;
};

struct Split {
    State state;
    int first;
    int second;
    int candidates;
    int obligations;
};

Integer uniform_below(const Integer& limit, std::mt19937_64& rng) {
    if (!limit) throw std::runtime_error("invalid sampling mass");
    if (limit == 1) return 0;
    const Integer largest = limit - 1;
    const int bits = largest.bit_length();
    if (bits <= 64) {
        return std::uniform_int_distribution<Word>(0, largest.as_word())(rng);
    }
    while (true) {
        Integer value = Integer::random_bits(bits, rng);
        if (value < limit) return value;
    }
}

struct Sampler {
    Graph& graph;
    int pool;
    int local_limit;
    int factor_limit;
    std::uint64_t state_limit;
    std::string policy;
    Statistics stats;
    std::vector<Word> pending_obligations;
    Integer total = 0;
    Integer largest_term = 0;
    Integer largest_mass = 0;
    std::uint64_t prepared_frontier = 0;
    std::uint64_t max_frontier = 0;
    int max_layers = 0;

    Sampler(Graph& graph, int pool, int local_limit, int factor_limit, std::uint64_t state_limit, std::string policy)
        : graph(graph), pool(pool), local_limit(local_limit), factor_limit(factor_limit),
          state_limit(state_limit), policy(std::move(policy)), pending_obligations(graph.n) {}

    void include(State& state, int v) {
        const Mask& row = graph.row(v);
        for (int w = 0; w < graph.width; ++w) {
            state.p[w] &= row[w];
            state.x[w] &= row[w];
        }
        clear_bit(state.p, v);
    }

    static void exclude(State& state, int v) {
        clear_bit(state.p, v);
        set_bit(state.x, v);
    }

    int missing(const Mask& p, int v, int stop = std::numeric_limits<int>::max()) {
        const Mask& row = graph.row(v);
        int degree = 0;
        for (int w = 0; w < graph.width; ++w) {
            degree += std::popcount(p[w] & ~row[w]);
            if (degree >= stop) return degree;
        }
        return degree;
    }

    int first_missing(const Mask& p, int v) {
        const Mask& row = graph.row(v);
        for (int w = 0; w < graph.width; ++w) {
            if (Word found = p[w] & ~row[w]) return w * 64 + std::countr_zero(found);
        }
        throw std::runtime_error("branch requires a missing candidate");
    }

    std::optional<Integer> exact(const Mask& p, const Mask& x) {
        const auto inside = members(p);
        const int n = inside.size();
        if (n > 63) throw std::runtime_error("local kernel received too many candidates");
        if (n == 0) return first_bit(x) < 0 ? Integer(1) : Integer(0);
        std::vector<Word> conflict(n);
        std::vector<Word> obligations;
        const int q = count_bits(x);
        std::vector<int> touched;
        if (q > 2 * n) touched.reserve(q);
        for (int a = 0; a < n; ++a) {
            const Mask& row = graph.row(inside[a]);
            for (int b = 0; b < n; ++b) {
                if (!has_bit(row, inside[b])) conflict[a] |= Word{1} << b;
            }
            if (q <= 2 * n) continue;
            for (int w = 0; w < graph.width; ++w) {
                for_bits(x[w] & ~row[w], [&](int local) {
                    int id = w * 64 + local;
                    if (!pending_obligations[id]) touched.push_back(id);
                    pending_obligations[id] |= Word{1} << a;
                });
            }
        }
        if (q > 2 * n) {
            obligations.reserve(touched.size());
            for (int v : touched) {
                obligations.push_back(pending_obligations[v]);
                pending_obligations[v] = 0;
            }
            if (static_cast<int>(touched.size()) != q) return Integer(0);
        } else {
            for (int v : members(x)) {
                const Mask& row = graph.row(v);
                Word obligation = 0;
                for (int a = 0; a < n; ++a) {
                    if (!has_bit(row, inside[a])) obligation |= Word{1} << a;
                }
                if (!obligation) return Integer(0);
                obligations.push_back(obligation);
            }
        }
        SmallSolver solver{conflict, stats, 8000, 0, {}};
        try {
            return solver.solve({(Word{1} << n) - 1, std::move(obligations), std::vector<Integer>(n, 1)});
        } catch (const SmallWorkLimit&) {
            ++stats.local_capped;
            return std::nullopt;
        }
    }

    int strip_universals(State& state, int limit) {
        std::vector<int> fixed;
        const auto possible = members(state.p, limit);
        for (int v : possible) {
            const Mask& row = graph.row(v);
            bool universal = true;
            for (int w = 0; w < graph.width; ++w) {
                if (state.p[w] & ~row[w]) {
                    universal = false;
                    break;
                }
            }
            if (!universal) continue;
            fixed.push_back(v);
            for (int w = 0; w < graph.width; ++w) state.x[w] &= row[w];
        }
        for (int v : fixed) clear_bit(state.p, v);
        stats.forced += fixed.size();
        return fixed.size();
    }

    // Once the choices off a block are fixed, every compatible candidate
    // inside that block is mandatory. Enumerate small off-block choices.
    std::optional<Integer> exact_block_fringe(const State& state, int block) {
        Mask inside(graph.width), outside(graph.width);
        for (int w = 0; w < graph.width; ++w) {
            inside[w] = state.p[w] & graph.blocks[block][w];
            outside[w] = state.p[w] & ~graph.blocks[block][w];
        }
        const auto fringe = members(outside);
        std::vector<Word> compatible(fringe.size());
        for (int i = 0; i < static_cast<int>(fringe.size()); ++i) {
            const auto& row = graph.row(fringe[i]);
            for (int j = 0; j < static_cast<int>(fringe.size()); ++j) {
                if (has_bit(row, fringe[j])) compatible[i] |= Word{1} << j;
            }
        }
        const auto excluded = members(state.x);
        int work = 0;
        auto recurse = [&](auto&& self, Word pending, Word undominated, const Mask& candidates,
                           const Mask& obligations) -> Word {
            if (++work > 16000) throw SmallWorkLimit{};
            if (!pending) {
                for (Word unresolved = undominated; unresolved; unresolved &= unresolved - 1) {
                    if (++work > 16000) throw SmallWorkLimit{};
                    if (!missing(candidates, fringe[std::countr_zero(unresolved)], 1)) return 0;
                }
                for (int v : excluded) {
                    if (!has_bit(obligations, v)) continue;
                    if (++work > 16000) throw SmallWorkLimit{};
                    if (!missing(candidates, v, 1)) return 0;
                }
                return 1;
            }
            const int v = std::countr_zero(pending);
            const Word bit = Word{1} << v;
            const Word remainder = pending & ~bit;
            Word subtotal = self(self, remainder, undominated, candidates, obligations);
            const auto& row = graph.row(fringe[v]);
            Mask p(graph.width), x(graph.width);
            for (int w = 0; w < graph.width; ++w) {
                p[w] = candidates[w] & row[w];
                x[w] = obligations[w] & row[w];
            }
            subtotal += self(self, remainder & compatible[v],
                             undominated & compatible[v] & ~bit, p, x);
            return subtotal;
        };
        const Word all = (Word{1} << fringe.size()) - 1;
        try {
            return Integer(recurse(recurse, all, all, inside, state.x));
        } catch (const SmallWorkLimit&) {
            ++stats.block_fringe_capped;
            return std::nullopt;
        }
    }

    // Components connect candidate conflicts and obligations to their
    // possible dominators. Obligation-to-obligation pairs are irrelevant.
    bool factor_components(State& state, int p_count, int x_count) {
        Mask left_p = state.p;
        Mask left_x = state.x;
        int left = p_count + x_count;
        std::vector<int> words;
        for (int w = 0; w < graph.width; ++w) {
            if (left_p[w] || left_x[w]) words.push_back(w);
        }
        for (int w : words) {
            while (left_p[w]) {
                const int seed = w * 64 + std::countr_zero(left_p[w]);
                Mask p(graph.width), x(graph.width);
                set_bit(p, seed);
                clear_bit(left_p, seed);
                --left;
                int p_here = 1;
                std::vector<std::pair<int, bool>> queue{{seed, true}};
                for (std::size_t i = 0; i < queue.size() && left; ++i) {
                    const auto [v, candidate] = queue[i];
                    const Mask& row = graph.row(v);
                    for (int k : words) {
                        const Word noncandidate = ~row[k];
                        Word new_p = left_p[k] & noncandidate;
                        const int n_p = std::popcount(new_p);
                        left -= n_p;
                        p_here += n_p;
                        left_p[k] ^= new_p;
                        p[k] |= new_p;
                        for_bits(new_p, [&](int a) { queue.emplace_back(k * 64 + a, true); });
                        if (!candidate) continue;
                        const Word new_x = left_x[k] & noncandidate;
                        left -= std::popcount(new_x);
                        left_x[k] ^= new_x;
                        x[k] |= new_x;
                        for_bits(new_x, [&](int a) { queue.emplace_back(k * 64 + a, false); });
                    }
                }
                if (p_here <= local_limit) {
                    if (auto value = exact(p, x)) {
                        if (*value == 0) return false;
                        state.mass *= *value;
                        ++stats.components;
                        for (int k : words) {
                            state.p[k] &= ~p[k];
                            state.x[k] &= ~x[k];
                        }
                    }
                }
            }
        }
        return left == 0;
    }

    void finish(const Integer& mass, const Integer& count) {
        if (!count) {
            ++stats.empty_leaves;
            return;
        }
        ++stats.exact_leaves;
        Integer contribution = mass * count;
        total += contribution;
        if (contribution > largest_term) largest_term = std::move(contribution);
        if (mass > largest_mass) largest_mass = mass;
    }

    std::optional<Split> prepare(State state, int depth) {
        bool factor_tried = false;
        while (true) {
            if (++stats.nodes > state_limit && state_limit) throw SearchWorkLimit{};
            int p_count = count_bits(state.p);
            int x_count = count_bits(state.x);
            if (!p_count) {
                finish(state.mass, x_count == 0 ? 1 : 0);
                return std::nullopt;
            }
            if (p_count <= local_limit) {
                if (auto value = exact(state.p, state.x)) {
                    finish(state.mass, *value);
                    return std::nullopt;
                }
            } else if (!factor_tried && p_count <= factor_limit && (depth % 3 == 0 || p_count <= 4 * local_limit)) {
                factor_tried = true;
                if (!factor_components(state, p_count, x_count)) {
                    finish(state.mass, 0);
                    return std::nullopt;
                }
                if (count_bits(state.p) != p_count) continue;
            }

            // The shortest sampled domination obligation gets first claim.
            int tight = -1;
            int tight_degree = p_count + 1;
            for (int v : members(state.x, pool)) {
                const int degree = missing(state.p, v, tight_degree);
                if (degree < tight_degree) {
                    tight = v;
                    tight_degree = degree;
                }
                if (!degree) break;
            }
            if (tight_degree == 0) {
                finish(state.mass, 0);
                return std::nullopt;
            }
            if (tight_degree == 1) {
                include(state, first_missing(state.p, tight));
                ++stats.forced;
                continue;
            }
            const auto candidates = members(state.p, pool);
            auto [block, outside] = graph.best_block(state.p, candidates.front(), p_count, policy == "block");
            if (!outside) {
                ++stats.blocks;
                if (x_count) {
                    for (int v : members(state.p)) {
                        const Mask& row = graph.row(v);
                        for (int w = 0; w < graph.width; ++w) state.x[w] &= row[w];
                        if (first_bit(state.x) < 0) break;
                    }
                }
                finish(state.mass, first_bit(state.x) < 0 ? 1 : 0);
                return std::nullopt;
            }
            if (policy == "block" && outside <= 12 && block >= 0) {
                if (auto count = exact_block_fringe(state, block)) {
                    ++stats.block_fringe;
                    finish(state.mass, *count);
                    return std::nullopt;
                }
            }
            if (policy == "block" && block >= 0 && outside * 2 < p_count) {
                if (tight >= 0 && tight_degree <= 4) {
                    const int dominator = first_missing(state.p, tight);
                    return Split{std::move(state), dominator, -1, p_count, x_count};
                }
                Mask fringe(graph.width);
                for (int w = 0; w < graph.width; ++w) fringe[w] = state.p[w] & ~graph.blocks[block][w];
                const auto outside_choices = members(fringe, pool);
                int largest = -1;
                int branch = -1;
                for (int v : outside_choices) {
                    int degree = missing(state.p, v);
                    if (degree > largest) {
                        largest = degree;
                        branch = v;
                    }
                }
                if (!largest) {
                    for (int v : outside_choices) include(state, v);
                    stats.forced += outside_choices.size();
                    continue;
                }
                ++stats.block_priority;
                return Split{std::move(state), branch, -1, p_count, x_count};
            }

            int center = -1;
            int hub = -1;
            int min_degree = p_count + 1;
            int max_degree = -1;
            for (int v : candidates) {
                int degree = missing(state.p, v);
                if (degree < min_degree) {
                    center = v;
                    min_degree = degree;
                }
                if (degree > max_degree) {
                    hub = v;
                    max_degree = degree;
                }
                if (min_degree < 1) break;
            }
            if (!min_degree) {
                if (!strip_universals(state, 4096)) throw std::runtime_error("missing universal");
                continue;
            }
            if (min_degree == 1) {
                ++stats.pair_splits;
                const int other = first_missing(state.p, center);
                return Split{std::move(state), center, other, p_count, x_count};
            }
            if (tight >= 0 && tight_degree <= (policy == "hub" ? 4 : std::max(3, min_degree))) {
                const int dominator = first_missing(state.p, tight);
                return Split{std::move(state), dominator, -1, p_count, x_count};
            }
            return Split{std::move(state), policy == "hub" ? hub : center, -1, p_count, x_count};
        }
    }

    void thin(std::vector<Split>& items, int width, std::mt19937_64& rng) {
        if (static_cast<int>(items.size()) <= width) return;
        // Pair similar residual sizes. Unpaired states keep their mass,
        // and an exact mass-ratio draw leaves each paired term unbiased.
        std::stable_sort(items.begin(), items.end(), [&](const Split& a, const Split& b) {
            return std::tie(a.candidates, a.obligations) < std::tie(b.candidates, b.obligations);
        });
        const int merge_count = static_cast<int>(items.size()) - width;
        std::vector<Split> retained;
        retained.reserve(width);
        for (int i = 0; i < 2 * merge_count; i += 2) {
            auto& a = items[i];
            auto& b = items[i + 1];
            Integer sum = a.state.mass + b.state.mass;
            bool take_a = uniform_below(sum, rng) < a.state.mass;
            Split& winner = take_a ? a : b;
            winner.state.mass = std::move(sum);
            retained.push_back(std::move(winner));
        }
        for (std::size_t i = 2 * merge_count; i < items.size(); ++i) {
            retained.push_back(std::move(items[i]));
        }
        stats.merges += merge_count;
        items = std::move(retained);
    }

    Integer run(int width, std::uint64_t seed) {
        stats = {};
        total = 0;
        largest_term = 0;
        largest_mass = 0;
        prepared_frontier = 0;
        max_frontier = 0;
        max_layers = 0;
        std::mt19937_64 rng(seed);
        State root{Mask(graph.width), Mask(graph.width), 1};
        for (int v = 0; v < graph.n; ++v) set_bit(root.p, v);
        std::vector<Split> frontier;
        if (auto first = prepare(std::move(root), 0)) frontier.push_back(std::move(*first));
        int depth = 0;
        while (!frontier.empty()) {
            ++depth;
            std::vector<Split> next;
            next.reserve(2 * frontier.size());
            for (auto& split : frontier) {
                ++stats.splits;
                State first = split.state;
                include(first, split.first);
                if (auto branch = prepare(std::move(first), depth)) next.push_back(std::move(*branch));
                if (split.second >= 0) include(split.state, split.second);
                else exclude(split.state, split.first);
                if (auto branch = prepare(std::move(split.state), depth)) next.push_back(std::move(*branch));
            }
            max_frontier = std::max<std::uint64_t>(max_frontier, next.size());
            prepared_frontier += next.size();
            thin(next, width, rng);
            frontier = std::move(next);
        }
        max_layers = depth;
        return total;
    }
};

int main(int argc, char** argv) {
    if (argc != 11 && argc != 12 && argc != 13) {
        std::cerr << "usage: kernel blocks.txt runs seed width policy ordering pool local-limit factor-limit cache-MiB [quotient [state-limit]]\n";
        return 2;
    }
    try {
        const int runs = std::stoi(argv[2]);
        const std::uint64_t seed = std::stoull(argv[3]);
        const int width = std::stoi(argv[4]);
        const std::string policy = argv[5];
        const std::string ordering = argv[6];
        const int pool = std::stoi(argv[7]);
        const int local = std::stoi(argv[8]);
        const int factoring = std::stoi(argv[9]);
        const int cache = std::stoi(argv[10]);
        const bool quotient = argc < 12 || std::stoi(argv[11]);
        const std::uint64_t state_limit = argc < 13 ? 0 : std::stoull(argv[12]);
        if (runs < 1 || width < 1 || pool < 1 || local < 0 || local > 63 || factoring < 0 || cache < 0 ||
            (policy != "hub" && policy != "partner" && policy != "block")) {
            throw std::runtime_error("invalid kernel parameters");
        }
        auto init = std::chrono::steady_clock::now();
        Graph graph(argv[1], ordering, seed, cache, quotient);
        Sampler sampler(graph, pool, local, factoring, state_limit, policy);
        auto prep_seconds = std::chrono::duration<double>(std::chrono::steady_clock::now() - init).count();
        std::cout << "{\"n\":" << graph.literal << ",\"quotient_n\":" << graph.n << ",\"blocks\":" << graph.blocks.size()
                  << ",\"runs\":" << runs << ",\"first_seed\":" << seed << ",\"width\":" << width
                  << ",\"policy\":\"" << policy << "\",\"ordering\":\"" << ordering
                  << "\",\"pool\":" << pool << ",\"local_limit\":" << local << ",\"factor_limit\":" << factoring
                  << ",\"cache_mib\":" << cache << ",\"quotient\":" << quotient
                  << ",\"state_limit\":" << state_limit
                  << ",\"prep_seconds\":" << prep_seconds << "}" << std::endl;
        for (int i = 0; i < runs; ++i) {
            auto start = std::chrono::steady_clock::now();
            Integer weight;
            try {
                weight = sampler.run(width, seed + i);
            } catch (const SearchWorkLimit&) {
                auto duration = std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count();
                std::cout << "{\"seed\":" << seed + i << ",\"status\":\"state_limit\",\"nodes\":" << sampler.stats.nodes - 1
                          << ",\"seconds\":" << duration << "}" << std::endl;
                continue;
            }
            auto seconds = std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count();
            const auto& s = sampler.stats;
            std::cout << "{\"seed\":" << seed + i << ",\"weight\":\"" << weight
                      << "\",\"largest_contribution\":\"" << sampler.largest_term
                      << "\",\"largest_terminal_mass\":\"" << sampler.largest_mass
                      << "\",\"nodes\":" << s.nodes << ",\"splits\":" << s.splits
                      << ",\"pair_splits\":" << s.pair_splits << ",\"block_priority\":" << s.block_priority
                      << ",\"exact_leaves\":" << s.exact_leaves
                      << ",\"empty_leaves\":" << s.empty_leaves << ",\"merges\":" << s.merges
                      << ",\"forced\":" << s.forced << ",\"block_finishes\":" << s.blocks
                      << ",\"block_fringe\":" << s.block_fringe << ",\"block_fringe_capped\":" << s.block_fringe_capped
                      << ",\"components\":" << s.components << ",\"local_states\":" << s.local_states
                      << ",\"local_twins\":" << s.local_twins << ",\"local_forests\":" << s.local_forests
                      << ",\"local_bipartite\":" << s.local_bipartite << ",\"local_capped\":" << s.local_capped
                      << ",\"local_cache_hits\":" << s.local_cache_hits << ",\"prepared_frontier\":" << sampler.prepared_frontier
                      << ",\"max_unthinned_frontier\":" << sampler.max_frontier << ",\"layers\":" << sampler.max_layers
                      << ",\"cached_rows\":" << graph.cached << ",\"seconds\":" << seconds << "}" << std::endl;
        }
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
