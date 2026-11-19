// Exact old symmetry groups on two-terminal cores with weighted parallel classes.
#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <map>
#include <numeric>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

using Mask = std::uint64_t;
constexpr int Inf = 9999;
constexpr int MaxSites = 7;
constexpr int MaxClasses = MaxSites * (MaxSites - 1) / 2;

constexpr Mask bit(int n) { return Mask{1} << n; }

int pop(Mask& mask) {
    const int index = std::countr_zero(mask);
    mask &= mask - 1;
    return index;
}

void require(bool yes, const char* message) {
    if (!yes) throw std::runtime_error(message);
}

struct Core {
    int n, width = 0;
    std::array<Mask, MaxSites> graph{};
    std::array<int, MaxSites> degree{};
    std::vector<std::array<int,3>> bundles;
    std::vector<int> bundle_of;

    Core(int order, const std::vector<int>& multiplicities) : n(order) {
        int k = 0;
        for (int a = 0; a < n; ++a) for (int b = a+1; b < n; ++b) {
            int cost = multiplicities[k++];
            if (!cost) continue;
            graph[a] |= bit(b);
            graph[b] |= bit(a);
            degree[a] += cost;
            degree[b] += cost;
            bundle_of.insert(bundle_of.end(), cost, int(bundles.size()));
            bundles.push_back({a,b,cost});
            width += cost;
        }
    }

    bool connected(Mask side, bool virtual_wire=false) const {
        if (!side) return false;
        const Mask terminals = bit(0) | bit(1);
        Mask seen = side & -side, next = seen;
        while (next) {
            const int site = pop(next);
            Mask neighbors = graph[site];
            if (virtual_wire && site < 2) neighbors |= terminals ^ bit(site);
            Mask added = neighbors & side & ~seen;
            seen |= added;
            next |= added;
        }
        return seen == side;
    }

    bool admissible() const {
        const Mask all = bit(n)-1;
        if (!connected(all)) return false;
        for (int a = 0; a < n; ++a) {
            if (a >= 2 && degree[a] < 3) return false;
            if (!connected(all ^ bit(a), true)) return false;
        }
        return true;
    }
};

constexpr int pairs_before(int b) { return b * (b+1) / 2; }
constexpr int triples_before(int c) { return c * (c+1) * (c+2) / 6; }

int triple_index(int a, int b, int c) {
    if (a > b) std::swap(a,b);
    if (b > c) std::swap(b,c);
    if (a > b) std::swap(a,b);
    return triples_before(c) + pairs_before(b) + a;
}

struct Readings {
    const Core& core;
    std::vector<int> separate, together;

    explicit Readings(const Core& initial) : core(initial),
        separate(triples_before(core.bundles.size()), Inf), together(separate) {
        const Mask all = bit(core.n)-1;
        for (Mask side = 1; side <= all; ++side) {
            if (side & bit(1)) continue;
            const bool split = side & bit(0);
            if (!core.connected(side) || !core.connected(all ^ side, !split)) continue;
            std::array<int, MaxClasses> support;
            int size = 0, cost = 0;
            for (int i = 0; i < int(core.bundles.size()); ++i) {
                const auto [a,b,w] = core.bundles[i];
                if (bool(side & bit(a)) != bool(side & bit(b))) support[size++] = i, cost += w;
            }
            auto& table = split ? separate : together;
            for (int c = 0; c < size; ++c) for (int b = 0; b <= c; ++b) for (int a = 0; a <= b; ++a) {
                const int index = triples_before(support[c]) + pairs_before(support[b]) + support[a];
                table[index] = std::min(table[index], cost);
            }
        }
    }

    int index(int a, int b, int c) const {
        return triple_index(core.bundle_of[a], core.bundle_of[b], core.bundle_of[c]);
    }

    int sep(int a, int b, int c) const { return separate[index(a,b,c)]; }

    int min_at_price(int at, int price) const {
        return std::min(together[at], separate[at] + price);
    }

    std::vector<Mask> domains(int price) const {
        auto pair_color = [&](int a, int b) {
            const int at = index(a,b,b);
            return std::pair(separate[at], price ? min_at_price(at,price) : 0);
        };
        const int w = core.width;
        std::vector<int> color(w);
        for (int a = 0; a < w; ++a) color[a] = sep(a,a,a);
        while (true) {
            using Signature = std::vector<std::tuple<int,int,int>>;
            std::map<Signature, int> palette;
            std::vector<int> finer(w);
            for (int a = 0; a < w; ++a) {
                Signature cells;
                for (int b = 0; b < w; ++b) if (a != b) {
                    const auto [split, total] = pair_color(a,b);
                    cells.emplace_back(color[b], split, total);
                }
                std::ranges::sort(cells);
                cells.emplace_back(color[a], -1, -1);
                finer[a] = palette.try_emplace(cells, palette.size()).first->second;
            }
            auto earlier = color;
            std::ranges::sort(earlier);
            const bool stable = std::unique(earlier.begin(), earlier.end()) - earlier.begin() == int(palette.size());
            color = std::move(finer);
            if (stable) break;
        }
        std::vector<Mask> result(w);
        for (int a = 0; a < w; ++a)
            for (int b = 0; b < w; ++b)
                if (color[a] == color[b]) result[a] |= bit(b);
        return result;
    }

    std::vector<bool> possible_prices(const std::vector<Mask>& color_domains) const {
        // Any marked permutation must carry the labeled restriction of the
        // unary and pair separator readings, up to permuting the three names.
        std::map<std::array<int,6>, std::vector<std::pair<int,int>>> classes;
        for (int a = 0; a < core.width; ++a) for (int b = a+1; b < core.width; ++b) for (int c = b+1; c < core.width; ++c) {
            std::array labels{a,b,c};
            std::array<int,6> signature;
            signature.fill(Inf);
            do {
                const auto [x,y,z] = labels;
                std::array key{std::countr_zero(color_domains[x]), std::countr_zero(color_domains[y]),
                               std::countr_zero(color_domains[z]), sep(x,y,y), sep(x,z,z), sep(y,z,z)};
                if (key < signature) signature = key;
            } while (std::next_permutation(labels.begin(), labels.end()));
            const int at = index(a,b,c);
            auto& values = classes[signature];
            const std::pair value{separate[at], together[at]};
            if (std::ranges::find(values, value) == values.end()) values.push_back(value);
        }

        std::vector<bool> candidates(core.width+2, false);
        for (const auto& [key, values] : classes) {
            for (const auto& [l,b] : values) for (const auto& [high_l,high_b] : values) {
                if (!(l < high_l && l+1 < high_b && high_b <= b && high_b != Inf)) continue;
                // The high-L value is B_high at every tied current price.
                // The low-L value can tie once it rises to that level.
                int price = high_b - l;
                candidates[price] = true;
                if (b == high_b) std::fill(candidates.begin()+price, candidates.end(), true);
            }
        }
        return candidates;
    }
};

class Group {
    const Readings& readings;
    const int price;
    const std::vector<Mask> allowed;
    std::vector<int> image;
    Mask all;

    bool agrees(int a, int b, Mask mapped) const {
        for (Mask done = mapped; done;) {
            const int x = pop(done), y = image[x];
            const int from = readings.index(a, x, x), to = readings.index(b, y, y);
            if (readings.separate[from] != readings.separate[to]) return false;
            if (!price) continue;
            if (readings.min_at_price(from,price) != readings.min_at_price(to,price)) return false;
            for (Mask rest = done; rest;) {
                const int z = pop(rest);
                if (readings.min_at_price(readings.index(a,x,z),price) !=
                    readings.min_at_price(readings.index(b,y,image[z]),price)) return false;
            }
        }
        return true;
    }

    bool complete(Mask free, Mask unused) {
        if (!free) return true;
        const Mask mapped = all ^ free;
        int smallest = readings.core.width+1, next = -1;
        Mask best = 0;
        for (Mask left = free; left;) {
            const int a = pop(left);
            Mask options = 0;
            for (Mask candidates = allowed[a] & unused; candidates;) {
                const int b = pop(candidates);
                if (agrees(a,b,mapped)) options |= bit(b);
            }
            if (!options) return false;
            if (int count = std::popcount(options); count < smallest) {
                next = a;
                best = options;
                smallest = count;
            }
        }
        while (best) {
            const int b = pop(best);
            image[next] = b;
            if (complete(free ^ bit(next), unused ^ bit(b))) return true;
        }
        return false;
    }

public:
    Group(const Readings& initial, int current_price)
        : readings(initial), price(current_price), allowed(readings.domains(price)),
          image(readings.core.width, -1), all(bit(readings.core.width)-1) {}

    bool only_parallel_candidates() const {
        const auto& c = readings.core.bundle_of;
        for (int a = 0; a < int(c.size()); ++a)
            for (Mask options = allowed[a]; options;)
                if (c[pop(options)] != c[a]) return false;
        return true;
    }

    const auto& color_domains() const { return allowed; }

    template<class Check>
    void grade(Check check) {
        for (int a = 0; a < int(image.size()); ++a) {
            const Mask later = all & ~(bit(a+1)-1), earlier = bit(a)-1;
            for (Mask candidates = later & allowed[a]; candidates;) {
                const int b = pop(candidates);
                if (!agrees(a,b,earlier)) continue;
                image[a] = b;
                if (complete(later, (later ^ bit(b)) | bit(a)) && !check(image)) return;
            }
            image[a] = a;
        }
    }
};

struct Difference {
    std::array<int,3> source, image;
    int sep_source, sep_image, together_source, together_image;
};

template<class Report>
void compare_triples(const Readings& table, const std::vector<int>& image, Report report) {
    const int width = table.core.width;
    const auto& bundles = table.core.bundle_of;
    for (int a = 0; a < width; ++a) for (int b = a+1; b < width; ++b) for (int c = b+1; c < width; ++c) {
        if (bundles[a] == bundles[image[a]] && bundles[b] == bundles[image[b]] && bundles[c] == bundles[image[c]]) continue;
        const int from = table.index(a,b,c), to = table.index(image[a],image[b],image[c]);
        if (from == to) continue;
        if (!report({{a,b,c}, {image[a],image[b],image[c]}, table.separate[from], table.separate[to],
                     table.together[from], table.together[to]})) return;
    }
}

struct Witness {
    std::vector<int> image;
    Difference difference;
    int price;
};

using Counts = std::map<std::string,std::uint64_t>;

struct Outcome {
    Witness obstruction{}, invisible_separation{};
};

Outcome test(const Readings& table, Counts& counts) {
    ++counts["admissible_cores"];
    const auto& core = table.core;
    Group broad(table, 0);
    if (broad.only_parallel_candidates()) {
        ++counts["only_parallel_domains"];
        return {};
    }
    bool all_sep = true, all_low = true;
    Outcome out;
    broad.grade([&](const auto& image) {
        ++counts["separator_group_generators_examined"];
        compare_triples(table, image, [&](const Difference& d) {
            if (all_sep && d.sep_source != d.sep_image) {
                all_sep = false;
                out.invisible_separation = Witness{image,d,0};
            }
            const int source = std::min(d.together_source, d.sep_source+1);
            const int target = std::min(d.together_image, d.sep_image+1);
            if (source != target) all_low = false;
            return all_sep || all_low;
        });
        return all_sep || all_low;
    });
    if (all_sep) {
        ++counts["same_separator_minima_through_three"];
        return out;
    }
    if (all_low) {
        ++counts["same_triple_minima_at_price_one"];
        return out;
    }
    const auto candidates = table.possible_prices(broad.color_domains());
    if (std::ranges::find(candidates, true) == candidates.end()) {
        ++counts["no_possible_tie_price"];
        return out;
    }
    ++counts["requiring_current_price_search"];
    for (int price = 2; price <= core.width+1; ++price) {
        if (!candidates[price]) continue;
        ++counts["current_prices_tested"];
        Group narrower(table, price);
        if (narrower.only_parallel_candidates()) continue;
        narrower.grade([&](const auto& image) {
            ++counts["current_price_group_generators_examined"];
            compare_triples(table, image, [&](const Difference& d) {
                const int source = std::min(d.together_source, d.sep_source+1);
                const int target = std::min(d.together_image, d.sep_image+1);
                if (source == target) return true;
                out.obstruction = Witness{image,d,price};
                return false;
            });
            return out.obstruction.image.empty();
        });
        if (!out.obstruction.image.empty()) {
            ++counts["breaking_cores"];
            break;
        }
    }
    return out;
}

using Pairs = std::vector<std::pair<int,int>>;

std::vector<std::vector<int>> terminal_relabelings(int n) {
    Pairs pairs;
    std::array<std::array<int,MaxSites>,MaxSites> positions{};
    for (int a = 0; a < n; ++a) for (int b = a+1; b < n; ++b) {
        positions[a][b] = positions[b][a] = pairs.size();
        pairs.emplace_back(a,b);
    }
    std::vector<std::vector<int>> result;
    std::vector<int> image(n);
    std::iota(image.begin(), image.end(), 0);
    do {
        for (int term = 0; term < 2; ++term) {
            std::vector<int> transport;
            for (auto [a,b] : pairs) transport.push_back(positions[image[a]][image[b]]);
            result.push_back(std::move(transport));
            std::swap(image[0],image[1]);
        }
    } while (std::next_permutation(image.begin()+2, image.end()));
    return result;
}

bool canonical(const std::vector<int>& weight, const std::vector<std::vector<int>>& transports) {
    for (std::size_t i = 1; i < transports.size(); ++i) {
        const auto& transport = transports[i];
        for (int j = 0; j < int(weight.size()); ++j) {
            if (weight[transport[j]] < weight[j]) return false;
            if (weight[transport[j]] > weight[j]) break;
        }
    }
    return true;
}

void array_json(const auto& values) {
    std::cout << '[';
    bool first = true;
    for (auto n : values) {
        if (!first) std::cout << ',';
        first = false;
        std::cout << n;
    }
    std::cout << ']';
}

void witness_json(const Core& core, const std::vector<int>& weights, const Witness& witness) {
    const auto& d = witness.difference;
    std::cout << "{\"n\":" << core.n << ",\"width\":" << core.width << ",\"weights\":";
    array_json(weights);
    std::cout << ",\"image\":";
    array_json(witness.image);
    std::cout << ",\"triple\":";
    array_json(d.source);
    std::cout << ",\"triple_image\":";
    array_json(d.image);
    std::cout << ",\"L\":";
    array_json(std::array{d.sep_source,d.sep_image});
    std::cout << ",\"B\":";
    array_json(std::array{d.together_source,d.together_image});
    std::cout << ",\"lambda\":" << witness.price << '}';
}

void sweep(int n, int maximum, std::uint64_t first, std::uint64_t past) {
    require(2 <= n && n <= MaxSites && 0 < maximum && maximum * n * (n-1) / 2 < 63, "unsupported weight panel");
    const auto transports = terminal_relabelings(n);
    std::uint64_t patterns = 1;
    const int pairs = n * (n-1) / 2;
    for (int j = 0; j < pairs; ++j) patterns *= maximum+1;
    past = std::min(past, patterns);
    require(first <= past, "reversed interval");
    Counts counts;
    std::vector<int> weight(pairs);
    bool have_invisible = false;
    for (std::uint64_t code = first; code < past; ++code) {
        std::uint64_t copy = code;
        for (int& x : weight) {
            x = copy % (maximum+1);
            copy /= maximum+1;
        }
        if (!canonical(weight, transports)) continue;
        ++counts["weighted_representatives"];
        const Core core(n, weight);
        if (!core.admissible()) continue;
        const auto result = test(Readings(core), counts);
        if (!result.invisible_separation.image.empty() && !have_invisible) {
            have_invisible = true;
            std::cout << "{\"unrefined_separator_example\":";
            witness_json(core, weight, result.invisible_separation);
            std::cout << "}\n";
        }
        if (!result.obstruction.image.empty()) {
            std::cout << "{\"breaking_example\":";
            witness_json(core, weight, result.obstruction);
            std::cout << "}\n" << std::flush;
        }
    }
    std::cout << "{\"n\":" << n << ",\"maximum_weight\":" << maximum
              << ",\"first_index\":" << first << ",\"past_index\":" << past << ",\"counts\":{";
    bool starting = true;
    for (const auto& [key, count] : counts) {
        if (!starting) std::cout << ',';
        starting = false;
        std::cout << '"' << key << "\":" << count;
    }
    std::cout << "}}\n";
}

void abstract_control() {
    // Artificial min tables exercise the full search path to a reported drop.
    // The supplied values need not be realized by the layout's parity rows.
    const std::vector weights{0,1,1,1,1,0};
    const Core layout(4, weights);
    Readings readings(layout);
    std::fill(readings.together.begin(), readings.together.end(), 6);
    std::fill(readings.separate.begin(), readings.separate.end(), 3);
    for (int a = 0; a < 4; ++a) for (int b = a+1; b < 4; ++b) for (int c = b+1; c < 4; ++c)
        readings.separate[readings.index(a,b,c)] = 5;
    readings.separate[readings.index(0,1,2)] = 4;
    Counts counts;
    const auto out = test(readings, counts);
    require(out.obstruction.price == 2 && counts["breaking_cores"] == 1, "the abstract control missed a drop");
    std::cout << "{\"abstract_pattern_only\":true,\"artificial_drop\":";
    witness_json(layout, weights, out.obstruction);
    std::cout << "}\n";
}

int main(int argc, char** argv) {
    try {
        if (argc == 2 && std::string(argv[1]) == "--abstract-control") {
            abstract_control();
            return 0;
        }
        require(argc == 3 || argc == 5, "usage: weighted_core JUNCTIONS MAX_WEIGHT [FIRST PAST] | --abstract-control");
        const auto first = argc == 5 ? std::stoull(argv[3]) : 0;
        const auto past = argc == 5 ? std::stoull(argv[4]) : ~std::uint64_t{0};
        sweep(std::stoi(argv[1]), std::stoi(argv[2]), first, past);
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
