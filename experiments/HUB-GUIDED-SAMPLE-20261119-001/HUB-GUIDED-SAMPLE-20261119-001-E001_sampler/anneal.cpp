// Prefix particle counts with uniform-invariant moves on maximal cliques.
// The archived insertion engine already implements the exact binary fibers.
#define main archived_sequential_main
#include "../../NINTH-ROUND-SAMPLE-20261119-001/NINTH-ROUND-SAMPLE-20261119-001-E001_estimate/sequential.cpp"
#undef main
#include <cstdlib>

namespace {
using Clique = std::vector<Id>;

struct SeedPopulation {
    int prefix = 0;
    std::string numerator = "1", denominator = "1";
    std::vector<Clique> samples;
};

struct Prepared {
    Graph graph;
    std::vector<int> position;
    int prefix;
};

Prepared seeded_order(const Roster& input, const std::vector<int>& prefix, const std::string& order, Word seed) {
    std::vector<int> all(input.n);
    std::iota(all.begin(), all.end(), 0);
    Graph closed(input.n);
    closed.add_blocks(input.members, all);
    std::vector<bool> initial(input.n);
    for (int u : prefix) {
        require(u >= 0 && u < input.n && !initial[u], "invalid or duplicate initial name");
        initial[u] = true;
    }
    std::vector<int> outside;
    for (int u : all) if (!initial[u]) outside.push_back(u);
    if (order != "given") {
        require(order == "degree-up" || order == "degree-down" || order == "random", "unknown seeded order");
        std::mt19937_64 rng(seed);
        std::shuffle(outside.begin(), outside.end(), rng);
        if (order != "random") {
            std::vector<int> scores(input.n);
            for (int u : outside) for (int w = 0; w < closed.stride; ++w)
                scores[u] += std::popcount(closed.row(u)[w]);
            const bool ascending = order == "degree-up";
            std::stable_sort(outside.begin(), outside.end(), [&](int a, int b) {
                return ascending ? scores[a] < scores[b] : scores[a] > scores[b];
            });
        }
    }
    all = prefix;
    all.insert(all.end(), outside.begin(), outside.end());
    std::vector<int> position(input.n), representatives;
    std::unordered_map<Word, std::vector<int>> buckets;
    int prefix_size = 0;
    for (int u : all) {
        Word hash = 14695981039346656037ULL;
        for (int w = 0; w < closed.stride; ++w) hash = (hash ^ closed.row(u)[w]) * 1099511628211ULL;
        auto& bucket = buckets[hash];
        int key = -1;
        for (int v : bucket) if (std::equal(closed.row(u), closed.row(u) + closed.stride, closed.row(v))) {
            key = position[v];
            break;
        }
        if (key < 0) {
            key = representatives.size();
            representatives.push_back(u);
            bucket.push_back(u);
            if (initial[u]) ++prefix_size;
        }
        position[u] = key;
    }
    Graph graph(representatives.size());
    graph.add_blocks(input.members, position);
    graph.make_open();
    return {std::move(graph), std::move(position), prefix_size};
}

void validate_clique(const Clique& c, const Graph& graph, int prefix) {
    require(!c.empty() && c.back() < prefix, "seed clique outside prefix");
    std::vector<Word> core((prefix + 63) / 64);
    for (int u : c) core[u / 64] |= Word{1} << (u % 64);
    for (int w = 0; w < int(core.size()); ++w) {
        Word common = before(w, prefix);
        for (int u : c) {
            Word closed = graph.row(u)[w];
            if (w == u / 64) closed |= Word{1} << (u % 64);
            common &= closed;
            if (!common) break;
        }
        require(common == core[w], "seed is not a maximal clique of the indicated prefix");
    }
}

SeedPopulation read_seeds(std::istream& in, const Prepared& data, int population, const std::vector<bool>& initial) {
    SeedPopulation start;
    start.prefix = data.prefix;
    auto positive_integer = [](const std::string& s) {
        return !s.empty() && s.find_first_not_of("0123456789") == std::string::npos &&
               s.find_first_not_of('0') != std::string::npos;
    };
    require(bool(in >> start.numerator >> start.denominator) && positive_integer(start.numerator) && positive_integer(start.denominator),
            "seed empirical mass must be a positive rational");
    for (int i = 0; i < population; ++i) {
        int length, u;
        require(bool(in >> length) && length > 0 && length <= int(initial.size()), "invalid seed clique length");
        Clique c;
        for (int j = 0; j < length; ++j) {
            require(bool(in >> u) && u >= 0 && u < int(initial.size()) && initial[u], "seed name outside original prefix");
            c.push_back(data.position[u]);
        }
        std::sort(c.begin(), c.end());
        c.erase(std::unique(c.begin(), c.end()), c.end());
        validate_clique(c, data.graph, data.prefix);
        start.samples.push_back(std::move(c));
    }
    return start;
}

bool contains(const Clique& clique, int v) {
    return std::binary_search(clique.begin(), clique.end(), v);
}

struct Moves {
    const Graph& graph;
    Clique kept, dropped, extras, result, lost, gained, proposal;
    std::vector<Word> possible;
    Word fiber_tests = 0, fiber_moves = 0, pivot_tests = 0, pivot_moves = 0;
    Word pivot_reversible = 0, changed_names = 0;

    explicit Moves(const Graph& g) : graph(g), possible(g.stride) {}

    void partition(const Clique& c, int v) {
        kept.clear();
        dropped.clear();
        for (Id u : c) {
            if (u == v) continue;
            (graph.meets(u, v) ? kept : dropped).push_back(u);
        }
    }

    // To extend R, keep only names adjacent to every member of R. The caller has
    // already excluded R itself by open neighborhoods (or supplied other exclusions).
    Word intersect(Word candidates, int word, const Clique& members) const {
        for (Id v : members) {
            if (!candidates) break;
            candidates &= graph.row(v)[word];
        }
        return candidates;
    }

    void greedy(const Clique& core, int size, bool reverse = false) {
        const int words = (size + 63) / 64;
        extras.clear();
        for (int step = 0; step < words; ++step) {
            const int w = reverse ? words - 1 - step : step;
            while (possible[w]) {
                const int bit = reverse ? 63 - std::countl_zero(possible[w]) : std::countr_zero(possible[w]);
                const int v = w * 64 + bit;
                extras.push_back(v);
                for (int k = step; k < words; ++k) {
                    const int h = reverse ? words - 1 - k : k;
                    possible[h] &= graph.row(v)[h];
                }
            }
        }
        if (reverse) std::reverse(extras.begin(), extras.end());
        result.clear();
        std::merge(core.begin(), core.end(), extras.begin(), extras.end(), std::back_inserter(result));
    }

    // Return the other member of the v-deletion fiber, when it has size two.
    bool sibling(const Clique& c, int v, int size) {
        const int words = (size + 63) / 64;
        partition(c, v);
        if (dropped.empty()) {
            require(contains(c, v), "maximal clique missed its freely addable pivot");
            bool found = false;
            for (int w = 0; w < words; ++w) {
                Word candidates = before(w, size) & ~graph.row(v)[w];
                if (v / 64 == w) candidates &= ~(Word{1} << (v % 64));
                possible[w] = intersect(candidates, w, kept);
                found |= possible[w] != 0;
            }
            if (found) greedy(kept, size);
            return found;
        }
        // The v-containing child must be maximal, and its lexicographic parent must be c.
        const int last = dropped.back();
        for (int w = 0; w < words; ++w) {
            const Word adjacent = before(w, size) & graph.row(v)[w];
            Word candidates = adjacent | before(w, last);
            if (v / 64 == w) candidates &= ~(Word{1} << (v % 64));
            candidates = intersect(candidates, w, kept);
            if (candidates & adjacent) return false;
            while (candidates) {
                const int y = w * 64 + std::countr_zero(candidates);
                candidates &= candidates - 1;
                if (contains(dropped, y)) continue;
                bool blocked = false;
                for (Id d : dropped) {
                    if (d >= y) break;
                    if (!graph.meets(d, y)) { blocked = true; break; }
                }
                if (!blocked) return false;
            }
        }
        result = kept;
        result.insert(std::lower_bound(result.begin(), result.end(), v), v);
        return true;
    }

    // F_v(c) is a deterministic maximal clique retaining c's neighbors of v.
    void complete_at(const Clique& c, int v, int size, bool reverse) {
        partition(c, v);
        for (int w = 0; 64 * w < size; ++w)
            possible[w] = intersect(before(w, size) & graph.row(v)[w], w, kept);
        kept.insert(std::lower_bound(kept.begin(), kept.end(), v), v);
        greedy(kept, size, reverse);
    }

    bool pivot(const Clique& c, int size, std::mt19937_64& rng) {
        ++pivot_tests;
        if (int(c.size()) == size) return false;
        std::uniform_int_distribution<int> vertex(0, size - 1);
        int v;
        do { v = vertex(rng); } while (contains(c, v));
        const bool reverse = rng() & 1;
        complete_at(c, v, size, reverse);
        proposal = result;
        lost.clear();
        gained.clear();
        std::set_difference(c.begin(), c.end(), proposal.begin(), proposal.end(), std::back_inserter(lost));
        std::set_difference(proposal.begin(), proposal.end(), c.begin(), c.end(), std::back_inserter(gained));
        require(!lost.empty() && !gained.empty(), "distinct maximal sets cannot contain one another");
        const int back = lost[std::uniform_int_distribution<int>(0, lost.size() - 1)(rng)];
        complete_at(proposal, back, size, reverse);
        if (result != c) return false;
        ++pivot_reversible;
        const Word numerator = (size - c.size()) * lost.size();
        const Word denominator = (size - proposal.size()) * gained.size();
        if (numerator < denominator && std::uniform_int_distribution<Word>(0, denominator - 1)(rng) >= numerator)
            return false;
        result = proposal;
        changed_names += lost.size() + gained.size();
        ++pivot_moves;
        return true;
    }

    bool step(Particle& particle, int size, int pivot_percent, std::mt19937_64& rng) {
        bool changed;
        if (std::uniform_int_distribution<int>(0, 99)(rng) < pivot_percent) {
            changed = pivot(particle.members, size, rng);
        } else {
            ++fiber_tests;
            const int v = std::uniform_int_distribution<int>(0, size - 1)(rng);
            changed = sibling(particle.members, v, size);
            if (changed) {
                ++fiber_moves;
                changed_names += std::max(particle.members.size(), result.size()) -
                                 std::min(particle.members.size(), result.size()) + 2;
            }
        }
        if (changed) {
            particle.members.swap(result);
            particle.cache.clear();
            particle.next_cache = 0;
        }
        return changed;
    }
};

#include "anneal_prefix.hpp"

void independent_moves(std::vector<Packed>& particles, Moves& moves, int size, int sweeps,
                       int pivot_percent, std::mt19937_64& rng) {
    // Independently mutate each offspring copy; retain equal unchanged copies compactly.
    std::vector<Packed> after;
    for (auto& original : particles) {
        Word unchanged = 0;
        const auto names = original.list();
        for (Word i = 0; i < original.weight; ++i) {
            Particle copy{names, {}, 0, 1, original.ancestor};
            bool used = false;
            for (int k = 0; k < sweeps; ++k) used |= moves.step(copy, size, pivot_percent, rng);
            if (used && copy.members != names) after.emplace_back(original.names.size(), copy.members, original.ancestor);
            else ++unchanged;
        }
        if (unchanged) {
            original.weight = unchanged;
            after.push_back(std::move(original));
        }
    }
    particles.swap(after);
}

struct Observations {
    const std::vector<int>& position;
    std::vector<std::pair<std::string, std::vector<Word>>> all_of;
    int draws = 0;

    void write(const std::vector<Packed>& active, Word mass, Word seed) const {
        std::cout << ",\"marked_final_mass\":{";
        for (std::size_t i = 0; i < all_of.size(); ++i) {
            const auto& [name, required] = all_of[i];
            Word count = 0;
            for (const Packed& c : active) {
                bool all = true;
                for (std::size_t w = 0; w < required.size(); ++w)
                    if (required[w] & ~c.names[w]) { all = false; break; }
                if (all) count += c.weight;
            }
            if (i) std::cout << ',';
            std::cout << '"' << name << "\":" << count;
        }
        std::cout << "},\"physical_draws\":[";
        // This stream runs after counting and cannot change any evolution draw.
        std::seed_seq schedule{std::uint32_t(seed), std::uint32_t(seed >> 32), 0x504f5354u, 0x47524f55u};
        std::mt19937_64 post(schedule);
        for (int i = 0; i < draws; ++i) {
            Word sampled = std::uniform_int_distribution<Word>(0, mass - 1)(post);
            std::size_t j = 0;
            while (sampled >= active[j].weight) sampled -= active[j++].weight;
            const auto& bits = active[j].names;
            if (i) std::cout << ',';
            std::cout << '[';
            bool first = true;
            for (std::size_t u = 0; u < position.size(); ++u) {
                int v = position[u];
                if ((bits[v / 64] >> (v % 64)) & 1) {
                    if (!first) std::cout << ',';
                    std::cout << u;
                    first = false;
                }
            }
            std::cout << ']';
        }
        std::cout << ']';
    }
};

Observations marks(const Prepared& data, const Roster& input) {
    Observations monitor{data.position, {}, 0};
    if (const char* text = std::getenv("ANNEAL_PROFILE_COUNT")) monitor.draws = std::stoi(text);
    require(monitor.draws >= 0 && monitor.draws <= 1000, "invalid physical sample count");
    const char* text = std::getenv("ANNEAL_MARK_BLOCKS");
    if (!text || !*text) return monitor;
    require(!data.position.empty(), "marked sets require a physical prefix file");
    std::istringstream supplied(text);
    for (std::string token; std::getline(supplied, token, ',');) {
        int a, b;
        char separator;
        std::istringstream parser(token);
        require(bool(parser >> a >> separator >> b) && parser.peek() == std::char_traits<char>::eof() &&
                separator == '+' && a >= 0 && b >= 0 && a < input.blocks && b < input.blocks,
                "use zero-indexed block pairs such as 13+4,35+0");
        std::vector<bool> in_a(input.n);
        for (int u : input.members[a]) in_a[u] = true;
        std::vector<Word> mask(data.graph.stride);
        for (int u : input.members[b]) if (in_a[u]) {
            int v = data.position[u];
            mask[v / 64] |= Word{1} << (v % 64);
        }
        require(std::any_of(mask.begin(), mask.end(), [](Word w) { return w != 0; }), "empty marked intersection");
        monitor.all_of.emplace_back(std::to_string(a) + "+" + std::to_string(b), std::move(mask));
    }
    return monitor;
}

void estimate(const Graph& graph, int target, int spacing, int sweeps, int trigger, int pivot_percent,
              Word seed, int limit, const SeedPopulation* initialization = nullptr, const Observations* observer = nullptr) {
    std::mt19937_64 rng(seed);
    PackedSplitter splitter(graph);
    Moves moves(graph);
    std::vector<Packed> active, spare;
    active.emplace_back(graph.stride);
    std::vector<Word> mass_factors;
    long double scale = 1;
    int first = 0, resamples = 0, mutations = 0;
    Word mass = 1, largest_weight = 0;
    int beginning = 0;
    if (initialization) {
        beginning = first = initialization->prefix;
        active.clear();
        for (int i = 0; i < target; ++i)
            active.emplace_back(graph.stride, initialization->samples[i], i);
        mass = target;
        scale = std::stold(initialization->numerator) / std::stold(initialization->denominator) / target;
    }
    std::vector<std::array<Word, 4>> snapshots;
    for (int v = beginning; v < limit; ++v) {
        splitter.advance(active, spare, v);
        mass = 0;
        for (const auto& row : active) mass += row.weight;
        const bool checkpoint = spacing && (v + 1) % spacing == 0;
        if (mass > Word(target) * trigger || (first && checkpoint && mass > Word(target))) {
            if (!first) {
                first = v + 1;
                for (std::size_t i = 0; i < active.size(); ++i) active[i].ancestor = i;
            }
            std::shuffle(active.begin(), active.end(), rng);
            resample_packed(active, target, mass, std::uniform_int_distribution<Word>(0, mass - 1)(rng));
            scale *= static_cast<long double>(mass) / target;
            mass_factors.push_back(mass);
            mass = target;
            ++resamples;
        }
        if (first && checkpoint && sweeps) {
            independent_moves(active, moves, v + 1, sweeps, pivot_percent, rng);
            ++mutations;
        }
        if (v + 1 == limit || (v + 1) % std::max(1, limit / 4) == 0) {
            std::unordered_map<std::uint32_t, Word> families;
            Word max_family = 0;
            for (const auto& row : active) {
                max_family = std::max(max_family, families[row.ancestor] += row.weight);
                largest_weight = std::max(largest_weight, Word(row.weight));
            }
            snapshots.push_back({Word(v + 1), Word(active.size()), families.size(), max_family});
        }
    }
    std::cout << std::setprecision(18) << "{\"seed\":" << seed << ",\"exact_initial_mass\":[\""
              << (initialization ? initialization->numerator : "1") << "\",\""
              << (initialization ? initialization->denominator : "1") << "\"],\"initial_rows\":"
              << (initialization ? target : 1) << ",\"resample_denominator\":" << target
              << ",\"final_mass\":" << mass << ",\"resample_numerators\":[";
    for (std::size_t i = 0; i < mass_factors.size(); ++i) {
        if (i) std::cout << ',';
        std::cout << mass_factors[i];
    }
    std::cout << "],\"estimate\":\"" << scale * mass
              << "\",\"exact\":" << (first ? "false" : "true") << ",\"first_resampling_prefix\":" << first
              << ",\"resamples\":" << resamples << ",\"mutation_checkpoints\":" << mutations
              << ",\"fiber_tests\":" << moves.fiber_tests << ",\"fiber_moves\":" << moves.fiber_moves
              << ",\"pivot_tests\":" << moves.pivot_tests << ",\"pivot_reverse_hits\":" << moves.pivot_reversible
              << ",\"pivot_moves\":" << moves.pivot_moves << ",\"symmetric_difference_sum\":" << moves.changed_names
              << ",\"largest_recorded_weight\":" << largest_weight << ",\"prefix_rows_ancestors_max_family\":[";
    for (std::size_t i = 0; i < snapshots.size(); ++i) {
        if (i) std::cout << ',';
        const auto& [v, count, families, largest] = snapshots[i];
        std::cout << '[' << v << ',' << count << ',' << families << ',' << largest << ']';
    }
    std::cout << ']';
    if (observer) observer->write(active, mass, seed);
    std::cout << "}\n" << std::flush;
}

Clique literal(int mask, int n) {
    Clique c;
    for (int u = 0; u < n; ++u) if ((mask >> u) & 1) c.push_back(u);
    return c;
}

void test_moves() {
    Word graphs = 0, projections = 0, reversible_pivots = 0;
    for (int n = 1; n <= 5; ++n) {
        std::vector<std::pair<int, int>> edges;
        for (int i = 0; i < n; ++i) for (int j = i + 1; j < n; ++j) edges.emplace_back(i, j);
        for (int mask = 0; mask < (1 << edges.size()); ++mask) {
            Graph g(n);
            for (int i = 0; i < int(edges.size()); ++i) if ((mask >> i) & 1) {
                const auto [a, b] = edges[i];
                g.add(a, b); g.add(b, a);
            }
            std::set<Clique> maximal;
            for (int bits = 1; bits < (1 << n); ++bits) {
                const Clique c = literal(bits, n);
                bool valid = true;
                for (int u = 0; u < n; ++u) {
                    bool compatible = true;
                    for (int v : c) if (u != v && !g.meets(u, v)) compatible = false;
                    if (compatible != contains(c, u)) valid = false;
                }
                if (valid) maximal.insert(c);
            }
            Moves moves(g);
            PackedSplitter insertion(g);
            std::vector<Packed> active, scratch;
            active.emplace_back(g.stride);
            for (int i = 0; i < n; ++i) insertion.advance(active, scratch, i);
            std::set<Clique> recovered;
            for (const auto& state : active) recovered.insert(state.list());
            require(recovered == maximal && recovered.size() == active.size(), "packed children differ from exhaustive sets");
            for (auto const& c : maximal) for (int v = 0; v < n; ++v) {
                ++projections;
                if (moves.sibling(c, v, n)) {
                    const Clique d = moves.result;
                    require(maximal.count(d) && d != c && (contains(c, v) != contains(d, v)), "bad alternative");
                    require(moves.sibling(d, v, n) && moves.result == c, "non-involutive fiber");
                }
                if (contains(c, v)) continue;
                for (bool reverse : {false, true}) {
                    moves.complete_at(c, v, n, reverse);
                    const Clique d = moves.result;
                    require(maximal.count(d) && contains(d, v), "pivot did not give a maximal extension");
                    for (int w : c) if (!contains(d, w)) {
                        moves.complete_at(d, w, n, reverse);
                        if (moves.result == c) ++reversible_pivots;
                    }
                }
            }
            ++graphs;
        }
    }
    std::cout << "{\"graphs\":" << graphs << ",\"tested_fibers\":" << projections
              << ",\"reciprocal_pivot_paths\":" << reversible_pivots << "}\n";
}
}

int main(int argc, char** argv) {
    try {
        if (argc == 2 && std::string(argv[1]) == "--self-test") { test_moves(); return 0; }
        require(argc == 11 || argc == 12,
                "anneal ROSTER ORDER ORDER_SEED POP SEED REPS SPACING SWEEPS PIVOT_PERCENT LIMIT [PREFIX_PARTICLES]");
        const auto input = read(argv[1]);
        const int pop = std::stoi(argv[4]), reps = std::stoi(argv[6]), spacing = std::stoi(argv[7]);
        const int sweeps = std::stoi(argv[8]), pivot = std::stoi(argv[9]);
        std::ifstream bank;
        std::vector<int> prefix;
        std::vector<bool> initial(input.n);
        if (argc == 12) {
            bank.open(argv[11]);
            int n;
            require(bool(bank >> n) && n > 0 && n <= input.n, "invalid prefix size");
            prefix.resize(n);
            for (int& u : prefix) {
                require(bool(bank >> u) && u >= 0 && u < input.n && !initial[u], "invalid initial labels");
                initial[u] = true;
            }
        }
        Prepared data = prefix.empty() ? Prepared{arranged(input, argv[2], std::stoull(argv[3]), true), {}, 0}
                                       : seeded_order(input, prefix, argv[2], std::stoull(argv[3]));
        const auto& graph = data.graph;
        auto observer = marks(data, input);
        const char* profiled = std::getenv("ANNEAL_PROFILE_ISLANDS");
        const int profile_islands = profiled ? std::stoi(profiled) : reps;
        require(profile_islands >= 0, "invalid number of profiled islands");
        require(!data.position.empty() || !observer.draws, "group sampling requires a physical prefix file");
        int limit = std::stoi(argv[10]);
        if (!limit) limit = graph.size;
        require(pop > 0 && pop <= 1'000'000 && reps > 0 && spacing >= 0 && sweeps >= 0 &&
                pivot >= 0 && pivot <= 100 && limit > 0 && limit <= graph.size && limit >= data.prefix,
                "invalid configuration");
        std::cout << "{\"literal\":" << input.n << ",\"classes\":" << graph.size << ",\"limit\":" << limit
                  << ",\"particles\":" << pop << ",\"spacing\":" << spacing << ",\"sweeps\":" << sweeps
                  << ",\"seeded_prefix_classes\":" << data.prefix << ",\"pivot_percent\":" << pivot << "}\n" << std::flush;
        for (int i = 0; i < reps; ++i) {
            if (i >= profile_islands) observer.draws = 0;
            if (prefix.empty()) estimate(graph, pop, spacing, sweeps, 4, pivot, std::stoull(argv[5]) + i, limit);
            else {
                const auto seeds = read_seeds(bank, data, pop, initial);
                estimate(graph, pop, spacing, sweeps, 4, pivot, std::stoull(argv[5]) + i, limit, &seeds, &observer);
            }
        }
        if (!prefix.empty()) { std::string rest; require(!(bank >> rest), "trailing seed data"); }
    } catch (const std::exception& e) { std::cerr << e.what() << '\n'; return 1; }
    return 0;
}
