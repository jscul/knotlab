#include <algorithm>
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
#include <sstream>
#include <stdexcept>
#include <unordered_map>
#include <vector>

using Word = std::uint64_t;
using Mask = std::vector<Word>;

void set(Mask& mask, int x) {
    mask[x / 64] |= Word{1} << (x % 64);
}

void erase(Mask& mask, int x) {
    mask[x / 64] &= ~(Word{1} << (x % 64));
}

int popcount(const Mask& mask) {
    int size = 0;
    for (Word word : mask) size += std::popcount(word);
    return size;
}

template <typename Callback>
void for_each(const Mask& mask, Callback visit) {
    for (int i = 0; i < static_cast<int>(mask.size()); ++i) {
        for (Word word = mask[i]; word; word &= word - 1) {
            visit(64 * i + std::countr_zero(word));
        }
    }
}

std::uint64_t mask_hash(const Mask& mask) {
    std::uint64_t digest = 14695981039346656037ULL;
    for (Word word : mask) digest = (digest ^ word) * 1099511628211ULL;
    return digest;
}

struct Graph {
    int original_size;
    int blocks;
    int size;
    int width;
    std::vector<Mask> adjacent;

    Graph(const char* filename, bool quotient, bool shuffled, std::mt19937_64& rng) {
        std::ifstream source(filename);
        if (!(source >> original_size >> blocks) || original_size < 1 || blocks < 0) {
            throw std::runtime_error("invalid block-file header");
        }
        int initial_width = (original_size + 63) / 64;
        std::vector<Mask> closed(original_size, Mask(initial_width));
        std::string line;
        std::getline(source, line);
        for (int i = 0; i < original_size; ++i) set(closed[i], i);
        for (int i = 0; i < blocks; ++i) {
            if (!std::getline(source, line)) throw std::runtime_error("missing block");
            Mask members(initial_width);
            std::vector<int> indices;
            std::istringstream block(line);
            for (int x; block >> x;) {
                if (x < 0 || x >= original_size) throw std::runtime_error("bad block index");
                set(members, x);
                indices.push_back(x);
            }
            if (!block.eof() || indices.size() < 2) throw std::runtime_error("invalid block");
            for (int x : indices) {
                for (int j = 0; j < initial_width; ++j) closed[x][j] |= members[j];
            }
        }
        if (source >> line) throw std::runtime_error("extra block data");

        std::vector<int> representatives;
        std::unordered_multimap<std::uint64_t, int> seen;
        for (int x = 0; x < original_size; ++x) {
            if (quotient) {
                auto [first, last] = seen.equal_range(mask_hash(closed[x]));
                auto match = std::find_if(first, last, [&](auto candidate) {
                    return closed[candidate.second] == closed[x];
                });
                if (match != last) continue;
                seen.emplace(mask_hash(closed[x]), x);
            }
            representatives.push_back(x);
        }
        size = static_cast<int>(representatives.size());
        width = (size + 63) / 64;
        std::vector<int> degrees(original_size);
        for (int x = 0; x < original_size; ++x) degrees[x] = popcount(closed[x]);
        if (shuffled) std::shuffle(representatives.begin(), representatives.end(), rng);
        else std::stable_sort(representatives.begin(), representatives.end(), [&](int a, int b) {
            return degrees[a] > degrees[b];
        });
        adjacent.assign(size, Mask(width));
        for (int i = 0; i < size; ++i) {
            const auto& row = closed[representatives[i]];
            for (int j = 0; j < size; ++j) {
                int x = representatives[j];
                adjacent[i][j / 64] |= ((row[x / 64] >> (x % 64)) & 1) << (j % 64);
            }
            erase(adjacent[i], i);
        }
    }
};

struct Search {
    const Graph& graph;
    int pivot_limit;
    int exact_cutoff;
    std::mt19937_64& rng;
    std::vector<long double> rank_score;
    std::vector<long double> rank_total;
    bool order_locally;
    int component_limit;
    std::uint64_t visits = 0;
    int largest_depth = 0;
    int first_branch = -1;
    int first_fanout = -1;
    std::uint64_t generated = 0;
    std::uint64_t retained = 0;
    std::uint64_t component_splits = 0;
    std::uint64_t component_count = 0;
    long double path_probability = 1;

    std::vector<int> children(const Mask& candidates, const Mask& excluded) {
        // If there are no possible vertices, a leaf counts only if X is empty.
        std::vector<int> words;
        for (int w = 0; w < graph.width; ++w) {
            if (candidates[w]) words.push_back(w);
        }
        if (words.empty()) return {};
        int best = std::numeric_limits<int>::max();
        int pivot = -1;
        for (const auto* available : {&excluded, &candidates}) {
            int tested = 0;
            for (int i = 0; i < graph.width && best && tested < pivot_limit; ++i) {
                for (Word bits = (*available)[i]; bits && best && tested < pivot_limit;
                     bits &= bits - 1) {
                    int x = 64 * i + std::countr_zero(bits);
                    int misses = 0;
                    for (int w : words) {
                        misses += std::popcount(candidates[w] & ~graph.adjacent[x][w]);
                        if (misses >= best) break;
                    }
                    if (misses < best) {
                        best = misses;
                        pivot = x;
                    }
                    ++tested;
                }
            }
        }
        std::vector<int> branches;
        branches.reserve(best);
        for (int w : words) {
            Word remaining = candidates[w] & ~graph.adjacent[pivot][w];
            for (; remaining; remaining &= remaining - 1) {
                branches.push_back(64 * w + std::countr_zero(remaining));
            }
        }
        if (order_locally && branches.size() > 1) {
            std::vector<std::pair<int, int>> scored;
            for (int x : branches) {
                int neighbors = 0;
                for (int w : words) neighbors += std::popcount(candidates[w] & graph.adjacent[x][w]);
                scored.emplace_back(-neighbors, x);
            }
            std::sort(scored.begin(), scored.end());
            for (std::size_t i = 0; i < branches.size(); ++i) branches[i] = scored[i].second;
        }
        return branches;
    }

    bool strip_forced(Mask& candidates, Mask& excluded, int limit) {
        Mask forced(graph.width);
        int count = 0;
        std::vector<int> words;
        for (int i = 0; i < graph.width; ++i) {
            if (candidates[i]) words.push_back(i);
        }
        for_each(candidates, [&](int x) {
            if (count >= limit) return;
            for (int w : words) {
                Word missing = candidates[w] & ~graph.adjacent[x][w];
                if (w == x / 64) missing &= ~(Word{1} << (x % 64));
                if (missing) return;
            }
            set(forced, x);
            ++count;
            for (int w = 0; w < graph.width; ++w) excluded[w] &= graph.adjacent[x][w];
        });
        for (int w : words) candidates[w] &= ~forced[w];
        return count > 0;
    }

    long double factor_small_components(Mask& candidates, Mask& excluded, int size, int depth) {
        if (size > component_limit || size <= exact_cutoff) return 1;
        // Outside vertices are domination constraints. Connect one only to
        // the candidates capable of dominating it. They never connect to
        // one another directly.
        Mask left_p = candidates;
        Mask left_x = excluded;
        std::vector<int> words;
        for (int w = 0; w < graph.width; ++w) {
            if (candidates[w] || excluded[w]) words.push_back(w);
        }
        int left_count = size + popcount(excluded);
        std::vector<std::pair<Mask, Mask>> small_components;
        for (int w : words) {
            while (left_p[w]) {
                int start = w * 64 + std::countr_zero(left_p[w]);
                Mask p(graph.width), x(graph.width);
                std::vector<std::pair<int, bool>> queue;
                queue.emplace_back(start, true);
                set(p, start);
                erase(left_p, start);
                --left_count;
                int candidates_here = 1;
                for (std::size_t i = 0; i < queue.size() && left_count; ++i) {
                    const auto [v, from_candidates] = queue[i];
                    for (int j : words) {
                        Word misses = ~graph.adjacent[v][j];
                        Word new_p = left_p[j] & misses;
                        int count_p = std::popcount(new_p);
                        left_count -= count_p;
                        candidates_here += count_p;
                        left_p[j] ^= new_p;
                        p[j] |= new_p;
                        for (; new_p; new_p &= new_p - 1) {
                            queue.emplace_back(j * 64 + std::countr_zero(new_p), true);
                        }
                        if (!from_candidates) continue;
                        Word new_x = left_x[j] & misses;
                        left_count -= std::popcount(new_x);
                        left_x[j] ^= new_x;
                        x[j] |= new_x;
                        for (; new_x; new_x &= new_x - 1) {
                            queue.emplace_back(j * 64 + std::countr_zero(new_x), false);
                        }
                    }
                }
                if (candidates_here <= exact_cutoff) small_components.emplace_back(std::move(p), std::move(x));
            }
        }
        if (left_count) return 0; // An outside vertex cannot be dominated.
        if (small_components.empty()) return 1;
        ++component_splits;
        component_count += small_components.size();
        long double product = 1;
        for (const auto& [p, x] : small_components) {
            product *= count(p, x, true, depth + 1);
            if (!product) return 0;
            for (int w : words) {
                candidates[w] &= ~p[w];
                excluded[w] &= ~x[w];
            }
        }
        return product;
    }

    long double count(Mask candidates, Mask excluded, bool exact, int depth) {
        long double weight = 1;
        while (true) {
            ++visits;
            largest_depth = std::max(largest_depth, depth++);
            int size = popcount(candidates);
            if (!size) return popcount(excluded) ? 0 : weight;
            exact = exact || size <= exact_cutoff;
            if ((depth % 3 == 0 || size <= 2 * exact_cutoff) && !exact && size <= component_limit) {
                weight *= factor_small_components(candidates, excluded, size, depth);
                if (!weight) return 0;
                size = popcount(candidates);
                if (!size) return popcount(excluded) ? 0 : weight;
                exact = size <= exact_cutoff;
            }
            std::vector<int> branches = children(candidates, excluded);
            if (branches.empty()) return 0;
            if (branches.size() == 1 && size > 8 && strip_forced(candidates, excluded, 4096)) {
                // Every universal candidate is needed in every maximal extension.
                continue;
            }
            if (exact && branches.size() > 1) {
                long double subtotal = 0;
                for (int x : branches) {
                    Mask p(graph.width), q(graph.width);
                    for (int w = 0; w < graph.width; ++w) {
                        p[w] = candidates[w] & graph.adjacent[x][w];
                        q[w] = excluded[w] & graph.adjacent[x][w];
                    }
                    subtotal += count(std::move(p), std::move(q), true, depth);
                    erase(candidates, x);
                    set(excluded, x);
                }
                return weight * subtotal;
            }
            std::size_t selected = 0;
            if (branches.size() > 1) {
                // Treat 10% of proposals as uniform and draw the other 90% by rank.
                const long double uniform = 1.L / branches.size();
                long double probability = uniform;
                if (rank_total.empty()) {
                    selected = std::uniform_int_distribution<std::size_t>(0, branches.size() - 1)(rng);
                } else {
                    const long double mix = 0.1L;
                    const long double u = std::generate_canonical<long double, 64>(rng);
                    const long double total = rank_total[branches.size() - 1];
                    if (u < mix) {
                        selected = std::uniform_int_distribution<std::size_t>(0, branches.size() - 1)(rng);
                    } else {
                        const auto stop = rank_total.begin() + branches.size();
                        const auto draw = std::upper_bound(rank_total.begin(), stop, (u - mix) * total / (1 - mix));
                        selected = std::min<std::size_t>(draw - rank_total.begin(), branches.size() - 1);
                    }
                    probability = mix * uniform + (1 - mix) * rank_score[selected] / total;
                }
                weight /= probability;
                path_probability *= probability;
                if (first_fanout < 0) {
                    first_branch = selected;
                    first_fanout = branches.size();
                }
            }
            for (std::size_t j = 0; j < selected; ++j) {
                erase(candidates, branches[j]);
                set(excluded, branches[j]);
            }
            int x = branches[selected];
            for (int w = 0; w < graph.width; ++w) {
                candidates[w] &= graph.adjacent[x][w];
                excluded[w] &= graph.adjacent[x][w];
            }
        }
    }

    struct State {
        Mask candidates;
        Mask excluded;
        long double weight;
        std::vector<int> branches;
    };

    struct Choice {
        int parent;
        int rank;
        long double score;
        int multiplicity = 0;
    };

    State child(const State& parent, int selected, long double weight) const {
        State next{parent.candidates, parent.excluded, weight, {}};
        for (int j = 0; j < selected; ++j) {
            erase(next.candidates, parent.branches[j]);
            set(next.excluded, parent.branches[j]);
        }
        int x = parent.branches[selected];
        for (int w = 0; w < graph.width; ++w) {
            next.candidates[w] &= graph.adjacent[x][w];
            next.excluded[w] &= graph.adjacent[x][w];
        }
        return next;
    }

    long double population_count(const Mask& candidates, const Mask& excluded, int budget, long double mass_power) {
        std::vector<State> states;
        states.push_back({candidates, excluded, 1, {}});
        long double subtotal = 0;
        for (int depth = 0; !states.empty(); ++depth) {
            std::vector<Choice> choices;
            for (int j = 0; j < static_cast<int>(states.size()); ++j) {
                auto& state = states[j];
                for (;;) {
                    int p = popcount(state.candidates);
                    if ((depth % 3 == 0 || p <= 2 * exact_cutoff) && p <= component_limit && p > exact_cutoff) {
                        state.weight *= factor_small_components(state.candidates, state.excluded, p, depth);
                        if (!state.weight) break;
                        p = popcount(state.candidates);
                    }
                    if (p <= exact_cutoff) {
                        subtotal += state.weight * count(state.candidates, state.excluded, true, depth);
                        break;
                    }
                    ++visits;
                    largest_depth = std::max(largest_depth, depth);
                    state.branches = children(state.candidates, state.excluded);
                    if (state.branches.empty()) break;
                    if (state.branches.size() == 1) {
                        if (strip_forced(state.candidates, state.excluded, 4096)) continue;
                        state = child(state, 0, state.weight);
                        continue;
                    }
                    const int fanout = state.branches.size();
                    const long double scale = std::pow(state.weight, mass_power) * std::sqrt(fanout);
                    for (int rank = 0; rank < fanout; ++rank) {
                        long double proposal = 1.L / fanout;
                        if (!rank_total.empty()) {
                            proposal = 0.1L * proposal + 0.9L * rank_score[rank] / rank_total[fanout - 1];
                        }
                        choices.push_back({j, rank, scale * proposal});
                    }
                    break;
                }
            }
            generated += choices.size();
            std::vector<State> next;
            next.reserve(std::min<std::size_t>(choices.size(), budget));
            if (static_cast<int>(choices.size()) <= budget) {
                for (const auto& choice : choices) {
                    const auto& parent = states[choice.parent];
                    next.push_back(child(parent, choice.rank, parent.weight));
                }
            } else {
                // One independent uniform offset yields unbiased multiplicities with
                // mean budget * score / total for each individual child.
                std::shuffle(choices.begin(), choices.end(), rng);
                long double total = 0;
                for (const auto& choice : choices) total += choice.score;
                const long double step = total / budget;
                const long double offset = std::generate_canonical<long double, 64>(rng) * step;
                std::size_t i = 0;
                long double cumulative = choices[0].score;
                for (int k = 0; k < budget; ++k) {
                    const long double position = offset + k * step;
                    while (position >= cumulative && i + 1 < choices.size()) {
                        cumulative += choices[++i].score;
                    }
                    ++choices[i].multiplicity;
                }
                for (const auto& choice : choices) {
                    if (choice.multiplicity) {
                        const auto& parent = states[choice.parent];
                        long double weight = parent.weight * choice.multiplicity * step / choice.score;
                        next.push_back(child(parent, choice.rank, weight));
                    }
                }
            }
            retained += next.size();
            states = std::move(next);
        }
        return subtotal;
    }
};

int main(int argc, char** argv) {
    if (argc != 8 && argc != 10 && argc != 12 && argc != 13) {
        std::cerr << "usage: estimate_bk blocks.txt samples seed pivot-pool exact-cutoff quotient shuffle "
                     "[rank-power local-order [population-budget mass-power [component-limit]]]\n";
        return 2;
    }
    try {
        const int samples = std::stoi(argv[2]);
        const std::uint64_t seed = std::stoull(argv[3]);
        const int pivot_limit = std::stoi(argv[4]);
        const int exact_cutoff = std::stoi(argv[5]);
        const long double rank_power = argc >= 10 ? std::stold(argv[8]) : 0;
        const bool local = argc >= 10 && std::stoi(argv[9]);
        const int population_budget = argc >= 12 ? std::stoi(argv[10]) : 0;
        const long double mass_power = argc >= 12 ? std::stold(argv[11]) : 0;
        const int component_limit = argc == 13 ? std::stoi(argv[12]) : 0;
        if (samples < 0 || pivot_limit < 1 || exact_cutoff < 0 || population_budget < 0 || component_limit < 0) {
            throw std::runtime_error("bad budget");
        }
        std::mt19937_64 rng(seed);
        const bool quotient = std::stoi(argv[6]);
        const bool shuffled = std::stoi(argv[7]);
        Graph graph(argv[1], quotient, shuffled, rng);
        Search search{graph, pivot_limit, exact_cutoff, rng, {}, {}, local, component_limit};
        if (rank_power > 0) {
            long double sum = 0;
            for (int x = 0; x < graph.size; ++x) {
                long double score = std::pow(1.L + x, -rank_power);
                sum += score;
                search.rank_score.push_back(score);
                search.rank_total.push_back(sum);
            }
        }
        Mask root(graph.width), excluded(graph.width);
        for (int x = 0; x < graph.size; ++x) set(root, x);
        std::cout << "{\"n\":" << graph.original_size << ",\"blocks\":" << graph.blocks
                  << ",\"quotient_n\":" << graph.size << ",\"seed\":" << seed
                  << ",\"samples\":" << samples << ",\"pivot_limit\":" << pivot_limit
                  << ",\"exact_cutoff\":" << exact_cutoff << ",\"rank_power\":" << rank_power
                  << ",\"local_order\":" << local << ",\"population_budget\":" << population_budget
                  << ",\"mass_power\":" << mass_power << ",\"component_limit\":" << component_limit
                  << ",\"quotient\":" << quotient << ",\"shuffled\":" << shuffled
                  << "}" << std::endl;
        for (int sample = 0; sample < std::max(1, samples); ++sample) {
            search.visits = 0;
            search.largest_depth = 0;
            search.first_branch = -1;
            search.first_fanout = -1;
            search.generated = 0;
            search.retained = 0;
            search.component_splits = 0;
            search.component_count = 0;
            search.path_probability = 1;
            auto start = std::chrono::steady_clock::now();
            long double weight = population_budget
                ? search.population_count(root, excluded, population_budget, mass_power)
                : search.count(root, excluded, samples == 0, 0);
            auto elapsed = std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count();
            if (!std::isfinite(weight)) throw std::runtime_error("nonfinite weight");
            std::cout << "{\"sample\":" << sample << ",\"weight\":\"" << std::setprecision(21) << weight
                      << "\",\"nodes\":" << search.visits << ",\"depth\":" << search.largest_depth
                      << ",\"first_branch\":" << search.first_branch << ",\"first_fanout\":" << search.first_fanout
                      << ",\"generated\":" << search.generated << ",\"retained\":" << search.retained
                      << ",\"component_splits\":" << search.component_splits
                      << ",\"component_count\":" << search.component_count
                      << ",\"path_probability\":\"" << std::setprecision(21) << search.path_probability << "\""
                      << ",\"seconds\":" << std::setprecision(7) << elapsed << "}\n";
            if (population_budget) std::cout.flush();
        }
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
