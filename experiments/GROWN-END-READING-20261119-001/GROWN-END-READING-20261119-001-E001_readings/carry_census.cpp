// Audit the full marked two- and three-distinction stabilizer against the parity span.
#include <numeric>

#define main archived_reach_bound_main
#include "../../GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds/reach_bound.cpp"
#undef main

namespace carry {

int population(Wide value) {
    return std::popcount(std::uint64_t(value)) + std::popcount(std::uint64_t(value >> 64));
}

struct Marked {
    Rows rows;
    std::vector<int> old_names;
    int movable = 0;

    explicit Marked(const Rows& original) {
        Incidence inc(original);
        std::vector<int> fixed;
        for (int b = 0; b < int(inc.own.size()); ++b) {
            const auto& holders = inc.own[b];
            if (std::ranges::any_of(holders, [&](int j) { return inc.live & bit(j); })) {
                fixed.push_back(b);
            } else {
                require(holders.size() == 2, "an exterior distinction is movable");
                old_names.push_back(b);
            }
        }
        movable = old_names.size();
        old_names.insert(old_names.end(), fixed.begin(), fixed.end());
        std::vector<int> inverse(old_names.size());
        for (int b = 0; b < int(inverse.size()); ++b) inverse[old_names[b]] = b;
        rows = original;
        for (auto& row : rows) {
            for (int& b : row) b = inverse[b];
            std::ranges::sort(row);
        }
    }
};

int triples_before(int c) { return c * (c-1) * (c-2) / 6; }
int pairs_before(int b) { return b * (b-1) / 2; }

class TripleMinima {
    const Table& pairs;
    std::vector<std::uint16_t> minima;

    static int index(int a, int b, int c) {
        return triples_before(c) + pairs_before(b) + a;
    }

public:
    TripleMinima(const Table& table, const Incidence& inc, int movable, int limit, bool all_queries=false)
        : pairs(table), minima(triples_before(int(table.minima.size())), limit == Inf ? Inf : limit+1) {
        const int exterior = inc.ordinary.size();
        const int n = exterior + bool(inc.live);
        const int classes = table.minima.size();
        Adj wired = inc.ordinary;
        wired.resize(n);
        if (inc.live) {
            wired[exterior] = inc.live;
            for (Mask live = inc.live; live;) wired[take(live)] |= bit(exterior);
        }
        std::vector<int> weights(classes);
        for (int endpoint_class : table.cls) ++weights[endpoint_class];
        Wide wanted = 0;
        for (int b = 0; b < (all_queries ? int(table.cls.size()) : movable); ++b)
            wanted |= wide(table.cls[b]);
        Wide singletons = 0;
        for (int i = 0; i < classes; ++i)
            if (weights[i] == 1) singletons |= wide(i);

        const Mask all = bit(n)-1;
        // In an open stage the last holder is the wired exterior. Omitting it
        // chooses precisely one of the two sides of each cut.
        std::vector<Wide> cuts(bit(n-1));
        for (Mask side = 1; side < cuts.size(); ++side) {
            const Wide boundary = table.star[std::countr_zero(side)] ^ cuts[side & (side-1)];
            cuts[side] = boundary;
            if (!(boundary & wanted)) continue;
            int cost = population(boundary & singletons);
            for (Wide plural = boundary & ~singletons; plural;) cost += weights[take_wide(plural)];
            if (cost < 3 || cost > limit || !connected(wired, side) || !connected(wired, all ^ side)) continue;

            std::array<int, 128> names;
            int count = 0;
            for (Wide remaining = boundary; remaining;) names[count++] = take_wide(remaining);
            for (int c = 2; c < count; ++c) {
                for (int b = 1; b < c; ++b) {
                    const Wide upper = wide(names[b]) | wide(names[c]);
                    for (int a = 0; a < b; ++a) {
                        if (!(wanted & (wide(names[a]) | upper))) continue;
                        auto& value = minima[index(names[a], names[b], names[c])];
                        if (cost < value) value = cost;
                    }
                }
            }
        }
    }

    int at(int a, int b, int c) const {
        // Requiring two parallel distinctions is equivalent to requiring either
        // one. Every bond through one necessarily contains both.
        const int x = pairs.cls[a], y = pairs.cls[b], z = pairs.cls[c];
        if (x == y) return pairs.at(a, c);
        if (x == z || y == z) return pairs.at(a, b);
        std::array names{x,y,z};
        std::ranges::sort(names);
        return minima[index(names[0], names[1], names[2])];
    }
};

// A domain for each movable name. The fixed names themselves are never
// permuted. Distinctly named parallel fixed distinctions have identical
// relations to movable names, so only one fixed name per class is needed.
class Stabilizer {
    const Table& pairs;
    const TripleMinima* triples;
    bool existence_only;
    std::vector<int> fixed;
    std::vector<Wide> domains;
    std::vector<int> image;
    Wide all;

    int ternary(int a, int b, int c) const {
        const int reading = triples->at(a, b, c);
        return existence_only ? reading != Inf : reading;
    }

    bool compatible(int a, int b, Wide mapped) const {
        for (Wide earlier = mapped; earlier;) {
            const int x = take_wide(earlier), y = image[x];
            if (pairs.at(a, x) != pairs.at(b, y)) return false;
            if (!triples) continue;
            for (int f : fixed)
                if (ternary(a, x, f) != ternary(b, y, f)) return false;
            for (Wide rest = earlier; rest;) {
                const int u = take_wide(rest);
                if (ternary(a, x, u) != ternary(b, y, image[u])) return false;
            }
        }
        return true;
    }

    bool complete(Wide free, Wide unused) {
        if (!free) return true;
        const Wide mapped = all ^ free;
        Wide best = 0;
        int name = -1, best_count = image.size()+1;
        for (Wide remaining = free; remaining;) {
            const int a = take_wide(remaining);
            Wide options = 0;
            for (Wide candidates = domains[a] & unused; candidates;) {
                const int b = take_wide(candidates);
                if (compatible(a, b, mapped)) options |= wide(b);
            }
            if (!options) return false;
            if (int count = population(options); count < best_count) {
                name = a;
                best_count = count;
                best = options;
            }
        }
        while (best) {
            const int b = take_wide(best);
            image[name] = b;
            if (complete(free ^ wide(name), unused ^ wide(b))) return true;
        }
        return false;
    }

    template<class Signature>
    static auto colors(const std::vector<Signature>& signatures) {
        std::map<Signature, int> palette;
        std::vector<int> partition;
        for (const auto& sig : signatures)
            partition.push_back(palette.try_emplace(sig, palette.size()).first->second);
        return std::pair(std::move(partition), palette.size());
    }

public:
    Stabilizer(const Table& table, int movable, const TripleMinima* triple_table, bool existence)
        : pairs(table), triples(triple_table), existence_only(existence), domains(movable),
          image(movable, -1), all(wide(movable)-1) {
        std::vector<bool> remembered(table.minima.size());
        for (int b = 0; b < int(table.cls.size()); ++b) {
            const int c = table.cls[b];
            if (b < movable) {
                require(!remembered[c], "two movable names share an endpoint class");
            } else if (!remembered[c]) {
                fixed.push_back(b);
            }
            remembered[c] = true;
        }
        std::vector<std::vector<int>> signatures(movable);
        for (int a = 0; a < movable; ++a) {
            for (int f : fixed) signatures[a].push_back(pairs.at(a, f));
            if (triples) {
                for (int i = 0; i < int(fixed.size()); ++i)
                    for (int j = 0; j < i; ++j)
                        signatures[a].push_back(ternary(a, fixed[i], fixed[j]));
            }
        }
        auto [partition, bins] = colors(signatures);
        while (bins < std::size_t(movable)) {
            std::vector<std::vector<std::pair<int,int>>> refine(movable);
            for (int a = 0; a < movable; ++a) {
                for (int b = 0; b < movable; ++b)
                    if (a != b) refine[a].emplace_back(partition[b], pairs.at(a, b));
                std::ranges::sort(refine[a]);
                refine[a].insert(refine[a].begin(), {partition[a], -1});
            }
            auto [next, count] = colors(refine);
            partition = std::move(next);
            if (count == bins) break;
            bins = count;
        }
        for (int a = 0; a < movable; ++a)
            for (int b = 0; b < movable; ++b)
                if (partition[a] == partition[b]) domains[a] |= wide(b);
    }

    template<class Check>
    void generators(Check check) {
        // One representative for each orbit at each level of the stabilizer
        // chain fixing all earlier names. The relations constrain the search
        // from the first choice onward, including when triples are present.
        for (int a = 0; a < int(image.size()); ++a) {
            const Wide previous = wide(a)-1, after = all & ~(wide(a+1)-1);
            for (Wide possible = domains[a] & after; possible;) {
                const int b = take_wide(possible);
                if (!compatible(a, b, previous)) continue;
                image[a] = b;
                if (complete(after, (after ^ wide(b)) | wide(a)) && !check(image)) return;
            }
            image[a] = a;
        }
    }
};

struct GroupGrade {
    int generators = 0;
    int noncarrying = 0;
    bool used_full_triples = false;
    std::vector<int> first_bad;
    std::vector<std::vector<int>> representatives;
};

GroupGrade group_grade(const Table& pairs, int movable, const TripleMinima* triples=nullptr,
                       bool all=false, bool retain=false, bool existence=false) {
    GroupGrade grade;
    Stabilizer(pairs, movable, triples, existence).generators([&](const auto& image) {
        ++grade.generators;
        if (retain) grade.representatives.push_back(image);
        if (carries_equations(pairs, image)) return true;
        ++grade.noncarrying;
        if (grade.first_bad.empty()) grade.first_bad = image;
        return all;
    });
    return grade;
}

using Counts = std::map<std::string, std::uint64_t>;

GroupGrade test(const Marked& marked, Counts& counts, bool existence_only=false) {
    ++counts["stages"];
    const int m = marked.movable;
    if (m < 2) {
        ++counts["fixed"];
        return {};
    }
    Incidence inc(marked.rows);
    std::vector<int> queries(m);
    std::iota(queries.begin(), queries.end(), 0);
    {
        Table clipped(marked.rows, inc, queries, Cutoff);
        auto grade = group_grade(clipped, m);
        counts["pooled_pair_generators_examined"] += grade.generators;
        if (!grade.noncarrying) {
            ++counts["pooled_pair_certificate"];
            if (grade.generators == 0) ++counts["trivial_eligible_group_certified"];
            return grade;
        }
    }
    Table exact(marked.rows, inc, queries, Inf);
    auto pair_grade = group_grade(exact, m);
    counts["exact_pair_generators_examined"] += pair_grade.generators;
    if (!pair_grade.noncarrying) {
        ++counts["exact_pair_certificate"];
        if (pair_grade.generators == 0) ++counts["trivial_eligible_group_certified"];
        return pair_grade;
    }
    if (existence_only) {
        const TripleMinima triples(exact, inc, m, Inf);
        auto grade = group_grade(exact, m, &triples, true, false, true);
        ++counts[grade.noncarrying ? "noncarrying_triple_existence_group" : "triple_existence_certificate"];
        counts["triple_existence_generators_examined"] += grade.generators;
        counts["noncarrying_triple_existence_generators"] += grade.noncarrying;
        if (grade.generators == 0) ++counts["trivial_eligible_group_certified"];
        return grade;
    }
    {
        TripleMinima short_triples(exact, inc, m, Cutoff);
        auto grade = group_grade(exact, m, &short_triples);
        counts["pooled_triple_generators_examined"] += grade.generators;
        if (!grade.noncarrying) {
            ++counts["pooled_triple_certificate"];
            if (grade.generators == 0) ++counts["trivial_eligible_group_certified"];
            return grade;
        }
    }
    TripleMinima all_triples(exact, inc, m, Inf);
    auto grade = group_grade(exact, m, &all_triples, true);
    grade.used_full_triples = true;
    counts["exact_triple_generators_examined"] += grade.generators;
    counts["noncarrying_exact_triple_generators"] += grade.noncarrying;
    if (grade.generators == 0) ++counts["trivial_eligible_group_certified"];
    ++counts[grade.noncarrying ? "noncarrying_exact_triple_group" : "exact_triple_certificate"];
    return grade;
}

// Recompute the number of forced groups plus unused-loose offshoots before
// applying the inherited growth procedure, so we visit the same current bound.
int births(const Incidence& inc, const std::vector<Mask>& groups) {
    const auto use = demands(groups, inc.loose.size());
    int total = groups.size();
    for (int j = 0; j < int(inc.loose.size()); ++j) {
        int remaining = int(inc.loose[j].size()) - use[j];
        if (remaining < 0) return -1;
        total += remaining;
    }
    return total;
}

void print_counts(const Counts& counts) {
    std::cout << '{';
    bool first = true;
    for (const auto& [key, value] : counts) {
        if (!first) std::cout << ',';
        first = false;
        std::cout << '"' << key << "\":" << value;
    }
    std::cout << '}';
}

void print_residual(int id, int age, const Rows& start, const Marked& marked, const GroupGrade& grade,
                    bool existence_only) {
    std::cout << (existence_only ? "{\"existence_counterexample\":" : "{\"full_triple_case\":");
    array_json(std::array{id,age});
    std::cout << ",\"start\":";
    rows_json(start);
    std::cout << ",\"current\":";
    rows_json(marked.rows);
    std::cout << ",\"current_names_to_growth_names\":";
    array_json(marked.old_names);
    std::cout << ",\"noncarrying_movable_permutation\":";
    array_json(grade.first_bad);
    std::cout << ",\"stabilizer_generators\":" << grade.generators
              << ",\"noncarrying_generators\":" << grade.noncarrying;
    std::cout << "}\n";
}

void audit(int current_limit, bool existence_only) {
    require(3 <= current_limit && current_limit <= 16, "unsupported current-junction bound");
    std::map<std::array<int,3>, Counts> origins;
    std::map<std::array<int,5>, Counts> stages;
    int id, width, n, admissible;
    Mask links;
    while (std::cin >> id >> width >> n >> admissible >> links) {
        require(3 <= width && width <= 15 && 1 <= n && n <= 10 && admissible == 1, "unexpected starting row");
        Adj ordinary(n);
        int link = 0;
        for (int a = 0; a < n; ++a) for (int b = a+1; b < n; ++b, ++link) {
            if (links & bit(link)) {
                ordinary[a] |= bit(b);
                ordinary[b] |= bit(a);
            }
        }
        std::vector<int> loose(n);
        int total_loose = 0;
        for (int& count : loose) {
            require(bool(std::cin >> count) && count >= 0, "malformed loose counts");
            total_loose += count;
        }
        require(std::popcount(links) + total_loose == width, "starting width disagrees with incidence");
        auto& origin = origins[{width,n,total_loose}];
        ++origin["starts"];
        const Rows start = start_rows(ordinary, loose);
        Rows current = start;
        for (int age = 0;; ++age) {
            Incidence inc(current);
            if (!inc.live) {
                ++origin[age ? "closed_after_growth" : "closed_at_start"];
                break;
            }
            const auto groups = Rule(inc.ordinary).groups(inc.live);
            if (age) {
                const Marked marked(current);
                auto& counters = stages[{width,n,total_loose,age,int(current.size())}];
                if (groups.empty()) ++counters["only_offshoots_next"];
                counters["max_current_width"] = std::max<std::uint64_t>(counters["max_current_width"], inc.own.size());
                auto grade = test(marked, counters, existence_only);
                if (grade.used_full_triples || grade.noncarrying)
                    print_residual(id, age, start, marked, grade, existence_only);
            }
            int count = births(inc, groups);
            if (count < 0) {
                ++origin[age ? "stall_after_growth" : "stall_at_start"];
                break;
            }
            if (current.size() + count > std::size_t(current_limit)) {
                ++origin["next_outside_current_bound"];
                ++origin["next_outside_age_" + std::to_string(age+1)];
                break;
            }
            current = grow(current, inc, groups);
            require(!current.empty(), "a scheduled complete round did not grow");
        }
    }
    require(std::cin.eof(), "invalid starting row");
    for (const auto& [key, counts] : origins) {
        std::cout << "{\"origin\":";
        array_json(key);
        std::cout << ",\"counts\":";
        print_counts(counts);
        std::cout << "}\n";
    }
    for (const auto& [key, counts] : stages) {
        std::cout << "{\"stage\":";
        array_json(key);
        std::cout << ",\"counts\":";
        print_counts(counts);
        std::cout << "}\n";
    }
}

void literal() {
    const Marked marked(read_rows());
    const Incidence inc(marked.rows);
    int width = inc.own.size();
    const Table pairs(marked.rows, inc, {}, Inf);
    const TripleMinima triples(pairs, inc, marked.movable, Inf, true);
    const auto pair_grade = group_grade(pairs, marked.movable, nullptr, true, true);
    const auto triple_grade = group_grade(pairs, marked.movable, &triples, true, true);
    const auto existence_grade = group_grade(pairs, marked.movable, &triples, true, true, true);
    Counts counts;
    test(marked, counts);
    std::vector<int> pair_values, triple_values;
    for (int a = 0; a < width; ++a) for (int b = a+1; b < width; ++b) {
        pair_values.push_back(pairs.at(a,b));
        for (int c = b+1; c < width; ++c) triple_values.push_back(triples.at(a,b,c));
    }
    std::cout << "{\"current_names_to_literal_names\":";
    array_json(marked.old_names);
    std::cout << ",\"movable\":" << marked.movable;
    std::cout << ",\"pair_K\":";
    array_json(pair_values);
    std::cout << ",\"triple_K\":";
    array_json(triple_values);
    std::cout << ",\"exact_pair_generators\":" << pair_grade.generators;
    std::cout << ",\"noncarrying_pair_generators\":" << pair_grade.noncarrying;
    std::cout << ",\"exact_triple_generators\":" << triple_grade.generators;
    std::cout << ",\"noncarrying_triple_generators\":" << triple_grade.noncarrying;
    std::cout << ",\"noncarrying_existence_generators\":" << existence_grade.noncarrying;
    std::cout << ",\"first_noncarrying_triple_permutation\":";
    array_json(triple_grade.first_bad);
    auto print_representatives = [](const auto& grade) {
        std::cout << '[';
        for (int i = 0; i < int(grade.representatives.size()); ++i) {
            if (i) std::cout << ',';
            array_json(grade.representatives[i]);
        }
        std::cout << ']';
    };
    std::cout << ",\"pair_representatives\":";
    print_representatives(pair_grade);
    std::cout << ",\"triple_representatives\":";
    print_representatives(triple_grade);
    std::cout << ",\"existence_representatives\":";
    print_representatives(existence_grade);
    std::cout << ",\"census_method\":";
    print_counts(counts);
    std::cout << "}\n";
}

} // namespace carry

int main(int argc, char** argv) {
    try {
        std::ios::sync_with_stdio(false);
        std::cin.tie(nullptr);
        if (argc == 3 && (std::string(argv[1]) == "audit" || std::string(argv[1]) == "audit-existence"))
            carry::audit(std::stoi(argv[2]), std::string(argv[1]) == "audit-existence");
        else if (argc == 2 && std::string(argv[1]) == "literal") carry::literal();
        else throw std::runtime_error("usage: carry_census audit[-existence] CURRENT_N | carry_census literal");
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
