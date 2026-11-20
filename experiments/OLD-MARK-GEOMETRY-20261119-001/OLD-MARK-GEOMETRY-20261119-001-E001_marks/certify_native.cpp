// Packed evaluation of the exact connected separator factors in certify.py.
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <memory>
#include <optional>
#include <set>
#include <stdexcept>
#include <unordered_map>
#include <utility>
#include <vector>

using Word = std::uint64_t;
constexpr int words = 4;
using Mask = std::array<Word, words>;

struct Record {
    int cost = 0;
    Mask inside{};
};

Record combine(const Record& first, const Record& second) {
    Record answer{first.cost + second.cost};
    for (int i = 0; i < words; ++i) answer.inside[i] = first.inside[i] | second.inside[i];
    return answer;
}

using Row = std::unordered_map<Word, Record>;
struct Factor {
    std::vector<Row> rows;
    std::size_t count = 0;
};

void improve(Row& row, Word key, const Record& value) {
    auto [found, inserted] = row.try_emplace(key, value);
    if (!inserted && (value.cost < found->second.cost ||
                      (value.cost == found->second.cost && value.inside < found->second.inside)))
        found->second = value;
}

int component(Word partition, int i) {
    return (partition >> (4 * i)) & 15;
}

Word identify(Word partition, int size, int i, int j) {
    const int a = component(partition, i), b = component(partition, j);
    auto [keep, remove] = std::minmax(a, b);
    if (keep == remove) return partition;
    for (int k = 0; k < size; ++k)
        if (component(partition, k) == remove)
            partition ^= Word(keep ^ remove) << (4 * k);
    return partition;
}

struct Child {
    int index;
    std::vector<int> positions;
};

struct Bag {
    std::vector<int> names;
    std::vector<std::pair<int, int>> edges;
    std::vector<Child> children;
    std::vector<int> scope;
};

std::vector<Bag> make_bags(const std::vector<std::map<int, int>>& graph,
                           const std::vector<int>& order) {
    int n = order.size();
    assert(n <= words * 64 && order.back() == n - 1);
    std::vector<int> position(n);
    for (int i = 0; i < n; ++i) position[order[i]] = i;
    std::vector<std::set<int>> filled(n);
    for (int v = 0; v < n; ++v) {
        for (auto [w, cost] : graph[v]) filled[v].insert(w);
        if (v != n - 1) {
            filled[v].insert(n - 1);
            filled[n - 1].insert(v);
        }
    }
    std::vector<Bag> bags(n);
    std::vector<std::vector<int>> attached(n);
    for (int i = 0; i < n; ++i) {
        auto& b = bags[i];
        int v = order[i];
        b.names.push_back(v);
        int earliest = n;
        for (int u : filled[v]) {
            earliest = std::min(earliest, position[u]);
            if (auto it = graph[v].find(u); it != graph[v].end())
                b.edges.emplace_back(b.names.size(), it->second);
            b.names.push_back(u);
        }
        assert(b.names.back() == n - 1 && b.names.size() <= 15);
        std::set<int> scope(b.names.begin(), b.names.end());
        for (int old : attached[i]) {
            Child child{old, {}};
            for (std::size_t j = 1; j < bags[old].names.size(); ++j) {
                auto it = std::find(b.names.begin(), b.names.end(), bags[old].names[j]);
                assert(it != b.names.end());
                child.positions.push_back(it - b.names.begin());
            }
            b.children.push_back(std::move(child));
            scope.insert(bags[old].scope.begin(), bags[old].scope.end());
        }
        b.scope.assign(scope.begin(), scope.end());
        if (earliest != n) attached[earliest].push_back(i);
        for (int u : filled[v]) {
            filled[u].erase(v);
            for (int w : filled[v])
                if (w != u) filled[u].insert(w);
        }
    }
    return bags;
}

struct Capped {};

class Solver {
    const std::vector<Bag>& bags;
    std::vector<std::unordered_map<Word, std::shared_ptr<Factor>>> cached;
    std::size_t cache_entries = 0;
    std::size_t state_cap;
    int ceiling = 0;

    Word cache_key(const Bag& bag, const std::vector<int>& pins) const {
        Word key = 0;
        for (int v : bag.scope) {
            if (v != int(pins.size()) - 1 && pins[v] >= 0)
                key = (key << 10) | (2 * v + pins[v] + 1);
        }
        return key;
    }

    std::shared_ptr<Factor> factor(int at, const std::vector<int>& pins) {
        const auto& bag = bags[at];
        Word address = cache_key(bag, pins);
        if (auto it = cached[at].find(address); it != cached[at].end()) return it->second;
        const int size = bag.names.size();
        std::vector<std::shared_ptr<Factor>> sub;
        for (const auto& child : bag.children) sub.push_back(factor(child.index, pins));
        auto out = std::make_shared<Factor>();
        out->rows.resize(1 << (size - 2)); // The exterior's bit is always zero.
        int fixed = 0;
        int ones = 0;
        for (int i = 0; i < size; ++i)
            if (pins[bag.names[i]] >= 0) {
                fixed |= 1 << i;
                ones |= pins[bag.names[i]] << i;
            }
        Word singletons = 0;
        for (int i = 0; i < size; ++i) singletons |= Word(i) << (4 * i);
        for (int colors = 0; colors < (1 << (size - 1)); ++colors) {
            if ((colors & fixed) != ones) continue;
            Record local{};
            int v = bag.names.front();
            if (colors & 1) local.inside[v / 64] |= Word(1) << (v % 64);
            Word partition = singletons;
            for (auto [i, weight] : bag.edges) {
                if (((colors >> i) ^ colors) & 1) local.cost += weight;
                else partition = identify(partition, size, 0, i);
            }
            if (local.cost > ceiling) continue;
            Row partial{{partition << 1, local}};
            for (std::size_t i = 0; i < sub.size(); ++i) {
                const auto& where = bag.children[i].positions;
                unsigned projected = 0;
                for (std::size_t j = 0; j < where.size(); ++j)
                    projected |= ((colors >> where[j]) & 1) << j;
                const Row& other = sub[i]->rows.at(projected);
                std::vector<std::pair<Word, const Record*>> ordered;
                ordered.reserve(other.size());
                for (const auto& [key, record] : other) ordered.emplace_back(key, &record);
                std::sort(ordered.begin(), ordered.end(),
                          [](const auto& a, const auto& b) { return a.second->cost < b.second->cost; });
                Row combined;
                for (const auto& [a, left] : partial) {
                    for (const auto& [b, right] : ordered) {
                        if (left.cost + right->cost > ceiling) break;
                        if (++merges > 500000000) throw Capped{};
                        if ((b & 1) && (colors || (a & 1))) continue;
                        Word next = a >> 1;
                        for (std::size_t k = 0; k < where.size(); ++k) {
                            int rep = component(b >> 1, k);
                            if (int(k) != rep) next = identify(next, size, where[k], where[rep]);
                        }
                        improve(combined, (next << 1) | ((a | b) & 1), combine(left, *right));
                    }
                }
                partial.swap(combined);
                if (partial.size() > state_cap) throw Capped{};
            }
            Row& target = out->rows[colors >> 1];
            const auto previous_count = target.size();
            for (const auto& [code, value] : partial) {
                Word parts = code >> 1;
                bool sealed = code & 1;
                int first = component(parts, 0);
                bool remains = false;
                for (int j = 1; j < size; ++j) remains |= component(parts, j) == first;
                if (!remains) {
                    if (colors != 1 || sealed) continue;
                    sealed = true;
                }
                std::array<int, 16> representative;
                representative.fill(-1);
                Word answer = 0;
                for (int j = 1; j < size; ++j) {
                    int rep = component(parts, j);
                    if (representative[rep] < 0) representative[rep] = j - 1;
                    answer |= Word(representative[rep]) << (4 * (j - 1));
                }
                improve(target, (answer << 1) | sealed, value);
            }
            out->count += target.size() - previous_count;
            if (out->count > state_cap) throw Capped{};
        }
        max_factor = std::max(max_factor, out->count);
        if (cache_entries + out->count <= 600000 && cached[at].size() < 120) {
            cached[at][address] = out;
            cache_entries += out->count;
        }
        return out;
    }

public:
    Word merges = 0;
    std::size_t max_factor = 0;

    Solver(const std::vector<Bag>& b, std::size_t cap)
        : bags(b), cached(b.size()), state_cap(cap) {}

    std::optional<Record> solve(const std::vector<int>& pins, int limit) {
        merges = 0;
        max_factor = 0;
        ceiling = limit;
        std::optional<Record> absent = Record{};
        std::optional<Record> present;
        for (const auto& child : bags.back().children) {
            assert(child.positions == std::vector<int>{0});
            auto sub = factor(child.index, pins);
            const auto& row = sub->rows.front();
            auto zero = row.find(0);
            auto one = row.find(1);
            std::optional<Record> next;
            if (absent && one != row.end() && absent->cost + one->second.cost <= ceiling)
                next = combine(*absent, one->second);
            if (present && zero != row.end() && present->cost + zero->second.cost <= ceiling) {
                auto step = combine(*present, zero->second);
                if (!next || step.cost < next->cost || (step.cost == next->cost && step.inside < next->inside))
                    next = step;
            }
            present = next;
            if (absent && zero != row.end() && absent->cost + zero->second.cost <= ceiling)
                absent = combine(*absent, zero->second);
            else absent.reset();
        }
        return present;
    }
};

int main() {
    int n, m, q;
    std::size_t cap;
    if (!(std::cin >> n >> m >> q >> cap)) return 1;
    std::vector<std::map<int, int>> graph(n);
    for (int i = 0; i < m; ++i) {
        int a, b, weight;
        std::cin >> a >> b >> weight;
        graph[a][b] = graph[b][a] = weight;
    }
    std::vector<int> order(n);
    for (int& v : order) std::cin >> v;
    auto bags = make_bags(graph, order);
    Solver engine(bags, cap);
    int previous_limit = 2000000000;
    for (int r = 0; r < q; ++r) {
        int count, limit;
        std::cin >> count >> limit;
        // Cached factors may have been compiled with a larger ceiling only.
        assert(limit <= previous_limit);
        previous_limit = limit;
        std::vector<int> pins(n, -1);
        pins[n - 1] = 0;
        for (int i = 0; i < count; ++i) {
            int v, value;
            std::cin >> v >> value;
            pins[v] = value;
        }
        try {
            auto result = engine.solve(pins, limit);
            if (result) {
                std::cout << "exact " << result->cost;
                for (auto word : result->inside) std::cout << ' ' << word;
            } else {
                std::cout << "infeasible 0 0 0 0 0";
            }
        } catch (const Capped&) {
            std::cout << "capped 0 0 0 0 0";
        }
        std::cout << ' ' << engine.merges << ' ' << engine.max_factor << '\n';
    }
}
