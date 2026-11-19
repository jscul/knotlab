// Count maximal candidate sets by a unique-parent prefix decomposition.
#include <algorithm>
#include <array>
#include <bit>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <random>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using Word = std::uint64_t;
using Id = std::uint16_t;
constexpr int WordBits = 64;

void require(bool ok, const char* message) {
    if (!ok) throw std::runtime_error(message);
}

Word before(int word, int bound) {
    const int width = std::clamp(bound - word * WordBits, 0, WordBits);
    return width == WordBits ? ~Word{0} : (Word{1} << width) - 1;
}

struct Graph {
    int size, stride;
    std::vector<Word> storage;
    std::vector<int> degree;

    explicit Graph(int n) : size(n), stride((n + WordBits - 1) / WordBits),
                            storage(std::size_t(n) * stride), degree(n) {}

    Word* row(int u) { return storage.data() + std::size_t(u) * stride; }
    const Word* row(int u) const { return storage.data() + std::size_t(u) * stride; }
    bool meets(int u, int v) const { return row(u)[v / WordBits] >> (v % WordBits) & 1; }

    void add(int u, int v) { row(u)[v / WordBits] |= Word{1} << (v % WordBits); }

    void add_blocks(const std::vector<std::vector<int>>& blocks, const std::vector<int>& map) {
        std::vector<Word> support(stride);
        for (const auto& block : blocks) {
            std::fill(support.begin(), support.end(), 0);
            for (int raw : block) {
                int u = map[raw];
                support[u / WordBits] |= Word{1} << (u % WordBits);
            }
            for (int raw : block) {
                Word* target = row(map[raw]);
                for (int i = 0; i < stride; ++i) target[i] |= support[i];
            }
        }
        for (int u = 0; u < size; ++u) add(u, u);
    }

    void make_open() {
        for (int u = 0; u < size; ++u) {
            row(u)[u / WordBits] &= ~(Word{1} << (u % WordBits));
            for (int i = 0; i < stride; ++i) degree[u] += std::popcount(row(u)[i]);
        }
    }
};

struct Roster {
    int n, blocks;
    std::vector<std::vector<int>> members;
};

Roster read(const std::string& path) {
    std::ifstream in(path);
    Roster raw{};
    require(bool(in >> raw.n >> raw.blocks) && raw.n > 0 && raw.n <= std::numeric_limits<Id>::max(),
            "invalid roster header");
    std::string line;
    std::getline(in, line);
    for (int i = 0; i < raw.blocks; ++i) {
        require(bool(std::getline(in, line)), "short roster");
        std::istringstream values(line);
        std::vector<int> block;
        for (int u; values >> u;) {
            require(u >= 0 && u < raw.n, "roster label outside range");
            block.push_back(u);
        }
        require(values.eof(), "invalid label");
        raw.members.push_back(std::move(block));
    }
    require(!(in >> line), "trailing roster data");
    return raw;
}

Graph arranged(const Roster& input, const std::string& order, Word seed, bool fold) {
    std::vector<int> original(input.n);
    std::iota(original.begin(), original.end(), 0);
    Graph closed(input.n);
    closed.add_blocks(input.members, original);
    std::vector<int> representative(input.n);
    std::vector<int> labels;
    std::unordered_map<Word, std::vector<int>> hash_buckets;
    for (int u : original) {
        representative[u] = u;
        if (fold) {
            Word hash = 14695981039346656037ULL;
            for (int i = 0; i < closed.stride; ++i) hash = (hash ^ closed.row(u)[i]) * 1099511628211ULL;
            auto& existing = hash_buckets[hash];
            for (int v : existing) {
                if (std::equal(closed.row(u), closed.row(u) + closed.stride, closed.row(v))) {
                    representative[u] = v;
                    break;
                }
            }
            if (representative[u] == u) existing.push_back(u);
        }
        if (representative[u] == u) labels.push_back(u);
    }

    std::mt19937_64 generator(seed);
    if (order == "random" || order == "degree-up" || order == "degree-down")
        std::shuffle(labels.begin(), labels.end(), generator);
    else require(order == "given", "unknown order");
    if (order == "degree-up" || order == "degree-down") {
        std::vector<int> scores(input.n);
        for (int u : labels)
            for (int i = 0; i < closed.stride; ++i) scores[u] += std::popcount(closed.row(u)[i]);
        std::stable_sort(labels.begin(), labels.end(), [&](int a, int b) {
            return order == "degree-up" ? scores[a] < scores[b] : scores[a] > scores[b];
        });
    }
    std::vector<int> positions(input.n);
    for (int i = 0; i < int(labels.size()); ++i) positions[labels[i]] = i;
    for (int u : original) positions[u] = positions[representative[u]];
    Graph result(labels.size());
    result.add_blocks(input.members, positions);
    result.make_open();
    return result;
}

struct Rejection {
    Id witness = 0;
    bool needs_neighbor = true;
    std::vector<Id> blockers;
};

struct Particle {
    std::vector<Id> members;
    std::vector<Rejection> cache;
    std::uint32_t next_cache = 0;
    std::uint32_t weight = 1;
    std::uint32_t ancestor = 0;
};

struct Splitter {
    const Graph& graph;
    std::vector<Id> kept, dropped;
    std::uint64_t cached = 0, examined = 0;

    void remember(Particle& old, Id witness, bool needs_neighbor) const {
        Rejection item{witness, needs_neighbor, {}};
        for (Id j : dropped)
            if (!graph.meets(witness, j)) item.blockers.push_back(j);
        require(!item.blockers.empty(), "old set was extendible");
        constexpr int Capacity = 8;
        if (old.cache.size() < Capacity) old.cache.push_back(std::move(item));
        else old.cache[old.next_cache++ % Capacity] = std::move(item);
    }

    bool secondary(Particle& old, int u) {
        for (const auto& item : old.cache) {
            if ((!item.needs_neighbor || graph.meets(u, item.witness)) &&
                std::none_of(item.blockers.begin(), item.blockers.end(), [&](Id v) { return graph.meets(u, v); })) {
                ++cached;
                return false;
            }
        }

        kept.clear();
        dropped.clear();
        int anchor = -1;
        for (Id v : old.members) {
            if (graph.meets(u, v)) {
                kept.push_back(v);
                if (anchor < 0 || graph.degree[v] < graph.degree[anchor]) anchor = v;
            } else dropped.push_back(v);
        }
        if (dropped.empty()) {
            old.members.push_back(u);
            old.cache.clear();
            old.next_cache = 0;
            return false;
        }

        ++examined;
        // A witness can reject maximality in N(u) or beat a retained
        // greedy choice. Later names cannot beat any greedy choice.
        const int latest_drop = dropped.back();
        for (int i = 0; i * WordBits < u; ++i) {
            const Word adjacent = graph.row(u)[i] & before(i, u);
            Word possible = adjacent | before(i, latest_drop);
            if (anchor >= 0) possible &= graph.row(anchor)[i];
            for (Id v : kept) {
                if (!possible) break;
                if (v != anchor) possible &= graph.row(v)[i];
            }
            if (Word extra = possible & adjacent) {
                remember(old, i * WordBits + std::countr_zero(extra), true);
                return false;
            }
            while (possible) {
                int y = i * WordBits + std::countr_zero(possible);
                possible &= possible - 1;
                if (std::binary_search(dropped.begin(), dropped.end(), y)) continue;
                bool blocked = false;
                for (Id v : dropped) {
                    if (v >= y) break;
                    if (!graph.meets(y, v)) {
                        blocked = true;
                        break;
                    }
                }
                if (!blocked) {
                    remember(old, y, false);
                    return false;
                }
            }
        }
        kept.push_back(u);
        return true;
    }
};

void advance(std::vector<Particle>& current, std::vector<Particle>& next, Splitter& split, int u) {
    next.clear();
    for (auto& parent : current) {
        if (split.secondary(parent, u))
            next.push_back({split.kept, {}, 0, parent.weight, parent.ancestor});
        next.push_back(std::move(parent));
    }
    current.clear();
    current.swap(next);
}

void resample(std::vector<Particle>& particles, Word target, Word mass, Word offset) {
    Word end = 0, assigned = 0;
    std::size_t keep = 0;
    for (auto& particle : particles) {
        end += particle.weight;
        const Word boundary = end * target;
        const Word count = boundary > offset ? (boundary - 1 - offset) / mass + 1 : 0;
        if (count > assigned) {
            particle.weight = count - assigned;
            if (keep != std::size_t(&particle - particles.data())) particles[keep] = std::move(particle);
            ++keep;
            assigned = count;
        }
    }
    require(end == mass && assigned == target, "systematic resampling lost mass");
    particles.resize(keep);
}

void run(const Graph& graph, Word target, Word seed, int limit, int replicate, Word trigger) {
    std::mt19937_64 rng(seed);
    Splitter split{graph, {}, {}};
    std::vector<Particle> active(1), next;
    int exact_prefix = 0, resamples = 0;
    Word exact_count = 1, mass = 1;
    bool exact = true;
    long double estimate = 1;
    std::vector<std::array<Word, 5>> checkpoints;
    std::array<int, 4> checkpoint_positions = {limit / 4, limit / 2, limit * 3 / 4, limit};
    for (int u = 0; u < limit; ++u) {
        advance(active, next, split, u);
        if (exact && (!target || active.size() <= target * trigger)) {
            exact_prefix = u + 1;
            exact_count = active.size();
            mass = exact_count;
            estimate = exact_count;
            require(exact_count <= 2'000'000, "exact live-population ceiling");
        } else {
            if (exact) {
                estimate = active.size();
                for (std::size_t i = 0; i < active.size(); ++i) active[i].ancestor = i;
            }
            mass = 0;
            for (const auto& particle : active) mass += particle.weight;
            if (mass > target * trigger) {
                if (!exact) estimate *= static_cast<long double>(mass) / target;
                std::shuffle(active.begin(), active.end(), rng);
                resample(active, target, mass, std::uniform_int_distribution<Word>(0, mass - 1)(rng));
                ++resamples;
                mass = target;
            }
            exact = false;
        }
        if (std::find(checkpoint_positions.begin(), checkpoint_positions.end(), u + 1) != checkpoint_positions.end()) {
            std::unordered_map<std::uint32_t, Word> families;
            Word largest = 0;
            if (!exact)
                for (const auto& p : active) largest = std::max(largest, families[p.ancestor] += p.weight);
            checkpoints.push_back({Word(u + 1), active.size(), exact ? active.size() : families.size(),
                                   exact ? 1 : largest, mass});
        }
    }
    if (!exact) estimate *= static_cast<long double>(mass) / target;
    Word max_weight = 0;
    int largest = 0;
    for (const auto& particle : active) {
        max_weight = std::max(max_weight, Word(particle.weight));
        largest = std::max(largest, int(particle.members.size()));
    }
    std::cout << std::setprecision(18) << "{\"replicate\":" << replicate << ",\"seed\":" << seed
              << ",\"estimate\":\"" << estimate << "\",\"log10_estimate\":" << std::log10(estimate)
              << ",\"exact\":" << (exact ? "true" : "false") << ",\"exact_prefix\":" << exact_prefix
              << ",\"exact_count_at_prefix\":" << exact_count << ",\"resamples\":" << resamples
              << ",\"largest_sampled_set\":" << largest << ",\"largest_particle_weight\":" << max_weight
              << ",\"cached_rejections\":" << split.cached << ",\"uncached_branch_tests\":" << split.examined
              << ",\"checkpoint_prefix_unique_ancestors_maxfamily_mass\":[";
    for (std::size_t i = 0; i < checkpoints.size(); ++i) {
        if (i) std::cout << ',';
        auto [prefix, unique, ancestors, family, weight] = checkpoints[i];
        std::cout << '[' << prefix << ',' << unique << ',' << ancestors << ',' << family << ',' << weight << ']';
    }
    std::cout << "]}\n";
}

void self_test() {
    int cases = 0, prefixes = 0, folded_cases = 0;
    for (int n = 1; n <= 5; ++n) {
        std::vector<std::pair<int, int>> pairs;
        for (int i = 0; i < n; ++i) for (int j = i + 1; j < n; ++j) pairs.emplace_back(i, j);
        for (int word = 0; word < (1 << pairs.size()); ++word) {
            Graph graph(n);
            Roster roster{n, 0, {}};
            for (int i = 0; i < int(pairs.size()); ++i) if (word >> i & 1) {
                auto [u, v] = pairs[i];
                graph.add(u, v);
                graph.add(v, u);
                roster.members.push_back({u, v});
            }
            graph.make_open();
            Splitter split{graph, {}, {}};
            std::vector<Particle> active(1), next;
            ++cases;
            for (int v = 0; v < n; ++v) {
                ++prefixes;
                advance(active, next, split, v);
                std::set<int> expected, actual;
                for (int s = 1; s < (2 << v); ++s) {
                    bool clique = true;
                    for (int x = 0; x <= v; ++x) if (s >> x & 1)
                        for (int y = x + 1; y <= v; ++y) if ((s >> y & 1) && !graph.meets(x, y))
                            clique = false;
                    if (!clique) continue;
                    bool extendible = false;
                    for (int u = 0; u <= v; ++u) if (!(s >> u & 1)) {
                        if ((graph.row(u)[0] & s) == Word(s)) extendible = true;
                    }
                    if (!extendible) expected.insert(s);
                }
                for (const auto& particle : active) {
                    int s = 0;
                    for (Id x : particle.members) s |= 1 << x;
                    require(actual.insert(s).second, "a maximal set has two parents");
                }
                require(expected == actual, "prefix decomposition lost or added a set");
            }
            Graph folded = arranged(roster, "random", 17, true);
            folded_cases += folded.size < n;
            Splitter folded_split{folded, {}, {}};
            std::vector<Particle> reduced(1), spare;
            for (int v = 0; v < folded.size; ++v) advance(reduced, spare, folded_split, v);
            require(active.size() == reduced.size(), "closed-neighborhood folding changed the count");
        }
    }
    std::array<Word, 3> accumulated{};
    for (Word offset = 0; offset < 7; ++offset) {
        std::vector<Particle> population = {{{0}, {}, 0, 2, 0}, {{1}, {}, 0, 3, 1}, {{2}, {}, 0, 2, 2}};
        resample(population, 4, 7, offset);
        for (const auto& p : population) accumulated[p.ancestor] += p.weight;
    }
    require(accumulated == std::array<Word, 3>{8, 12, 8}, "wrong finite systematic-resampling expectation");
    std::cout << "{\"small_graphs\":" << cases << ",\"prefixes\":" << prefixes
              << ",\"nontrivially_folded_graphs\":" << folded_cases
              << ",\"finite_resampling_expectation\":true}\n";
}

int main(int argc, char** argv) {
    try {
        if (argc == 2 && std::string(argv[1]) == "--self-test") {
            self_test();
            return 0;
        }
        require(argc == 9 || argc == 10, "sequential ROSTER ORDER ORDER_SEED PARTICLES SEED REPLICATES END FOLD [TRIGGER]");
        std::ios::sync_with_stdio(false);
        const auto begin = std::chrono::steady_clock::now();
        Roster input = read(argv[1]);
        const std::string order = argv[2];
        Word order_seed = std::stoull(argv[3]), target = std::stoull(argv[4]), seed = std::stoull(argv[5]);
        int replicates = std::stoi(argv[6]), limit = std::stoi(argv[7]);
        bool fold = std::stoi(argv[8]);
        Word trigger = argc == 10 ? std::stoull(argv[9]) : 1;
        require(replicates > 0 && target <= 1'000'000 && trigger > 0 && trigger <= 16, "invalid run limits");
        Graph graph = arranged(input, order, order_seed, fold);
        if (!limit) limit = graph.size;
        require(limit > 0 && limit <= graph.size, "invalid prefix");
        std::cout << "{\"original_names\":" << input.n << ",\"classes\":" << graph.size << ",\"blocks\":" << input.blocks
                  << ",\"order\":\"" << order << "\",\"order_seed\":" << order_seed << ",\"particles\":" << target
                  << ",\"prefix\":" << limit << ",\"folded\":" << (fold ? "true" : "false")
                  << ",\"resample_mass_multiple\":" << trigger << "}\n" << std::flush;
        for (int i = 0; i < replicates; ++i) {
            run(graph, target, seed + i, limit, i, trigger);
            std::cout << std::flush;
        }
        std::cerr << "seconds " << std::chrono::duration<double>(std::chrono::steady_clock::now() - begin).count() << '\n';
    } catch (const std::exception& failure) {
        std::cerr << failure.what() << '\n';
        return 1;
    }
}
