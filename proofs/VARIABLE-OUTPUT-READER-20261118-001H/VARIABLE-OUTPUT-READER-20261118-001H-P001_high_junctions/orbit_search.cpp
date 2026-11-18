// Grade automorphisms of a single presentation, for fixed high-junction families.
#define main interval_compare_main
#include "../../VARIABLE-OUTPUT-READER-20261118-001F/VARIABLE-OUTPUT-READER-20261118-001F-P001_finite_interval/compare.cpp"
#undef main

#include <map>
#include <set>

namespace {

constexpr int FirstWidth = 27;

Set sites(std::initializer_list<int> labels) {
    Set group = 0;
    for (int label : labels) group |= bit(label);
    return group;
}

bool legal_join(const Fixture& source, Set parents) {
    const auto count = std::popcount(parents);
    if (count < 1 || count > 3 || (parents & ~mask(source.count))) return false;
    bool legal = true;
    Set universal = mask(source.count);
    each(parents, [&](int a) {
        legal &= source.loose[a] > 0;
        universal &= source.neighbors[a];
        each(parents & ~mask(a + 1), [&](int b) {
            legal &= (source.neighbors[a] & source.neighbors[b]) != 0;
        });
    });
    return legal && (count < 3 || universal == 0);
}

Fixture adjoin(const Fixture& source, Set parents, int fresh) {
    require(source.count < MaxJunctions && (fresh == 2 || fresh == 3) && legal_join(source, parents),
            "invalid planned extension");
    auto result = source;
    const int newest = result.count++;
    result.width += fresh;
    result.neighbors[newest] = parents;
    result.loose[newest] = fresh;
    for (int i = 0; i < newest; ++i) {
        if (!(parents & bit(i))) continue;
        result.neighbors[i] |= bit(newest);
        --result.loose[i];
    }
    return result;
}

template<class F> void with_counts(const Fixture& source, Set parents, F accept) {
    if (legal_join(source, parents)) {
        for (int fresh : {2, 3}) accept(adjoin(source, parents, fresh));
    }
}

Fixture core(bool offset, unsigned profile) {
    const std::array<Set, 6> symmetric = {
        sites({0}), sites({0}), sites({0}), sites({1, 2}), sites({1, 3}), sites({2, 3})};
    const std::array<Set, 6> staggered = {
        sites({0}), sites({1}), sites({1}), sites({0, 2}), sites({0, 3}), sites({4, 5})};
    Fixture result{};
    result.count = 1;
    result.width = result.loose[0] = 3;
    const auto& choices = offset ? staggered : symmetric;
    for (std::size_t i = 0; i < choices.size(); ++i) {
        result = adjoin(result, choices[i], 2 + (profile >> i & 1));
    }
    return result;
}

bool has_trial_triple(const Fixture& fixture) {
    for (int i = 0; i < fixture.count; ++i)
        for (int j = i + 1; j < fixture.count; ++j)
            for (int k = j + 1; k < fixture.count; ++k)
                if (legal_join(fixture, sites({i, j, k}))) return true;
    return false;
}

Table capped(const Table& source, int horizon) {
    Table result(source.width);
    for (int i = 0; i < source.width; ++i)
        for (int j = 0; j < source.width; ++j)
            result.rows[i][j] = std::min(source.rows[i][j], static_cast<Byte>(horizon));
    result.legal = source.legal;
    fingerprint(result);
    return result;
}

struct Trial {
    Fixture fixture;
    Conflict conflict;
    int horizon;  // Zero denotes agreement at full distance.
};

struct Family {
    std::string name;
    std::set<std::string> seen;
    std::map<int, std::uint64_t> positive_widths, passing_cutoffs;
    std::uint64_t qualified{}, without_legal_triple{}, duplicate{}, exact_calls{}, generators{};
    std::optional<Trial> best;

    bool finished() const { return best && best->horizon == 0; }

    std::optional<Conflict> check(const Table& table) {
        Statistics stats;
        const auto violation = self_conflict(table, stats);
        generators += stats.generators;
        ++exact_calls;
        return violation;
    }

    void consider(const Fixture& fixture) {
        if (finished() || fixture.width < FirstWidth) return;
        bool high = false;
        for (int i = 0; i < fixture.count; ++i) {
            high |= std::popcount(fixture.neighbors[i]) + fixture.loose[i] >= 5;
        }
        if (!high) return;
        if (!seen.insert(fixture.source()).second) {
            ++duplicate;
            return;
        }
        ++qualified;
        if (!has_trial_triple(fixture)) {
            ++without_legal_triple;
            return;
        }
        ++positive_widths[fixture.width];
        const Table full = remeasure(fixture);
        require(!full.legal.empty(), "direct triple tests disagree");
        if (const auto violation = check(full)) {
            best = Trial{fixture, *violation, 0};
            std::cerr << name << ": opposing full-table symmetry at width " << fixture.width << std::endl;
            return;
        }
        int largest = 3;
        for (int i = 0; i < full.width; ++i)
            for (int j = i + 1; j < full.width; ++j) {
                require(full.rows[i][j] < Infinity, "infinite pair minimum");
                largest = std::max(largest, 1 + full.rows[i][j]);
            }
        int smallest_passing = 3;
        for (int k = largest - 1; k >= 3; --k) {
            const auto violation = check(capped(full, k));
            if (!violation) continue;
            const bool better = !best || k > best->horizon
                || (k == best->horizon && fixture.width < best->fixture.width);
            if (better) {
                best = Trial{fixture, *violation, k};
                if (k >= 6) std::cerr << name << ": opposing symmetry through K=" << k
                                      << " at width " << fixture.width << std::endl;
            }
            smallest_passing = k + 1;
            break;
        }
        ++passing_cutoffs[smallest_passing];
    }
};

void competing_caps(const Fixture& source, bool offset, Family& family) {
    const int a = offset ? 2 : 4;
    const int b = offset ? 3 : 5;
    with_counts(source, offset ? sites({4, 5}) : sites({2, 3}), [&](const Fixture& duplicate) {
        with_counts(duplicate, sites({a, b, 6}), [&](const Fixture& first) {
            family.consider(first);
            with_counts(first, sites({a, b, 7}), [&](const Fixture& second) {
                family.consider(second);
                with_counts(second, sites({8, 9}), [&](const Fixture& bridge) {
                    require(legal_join(bridge, sites({6, 7, 10})), "missing bridge triple");
                    family.consider(bridge);
                    for (int anchor : {6, 7, a, b}) {
                        with_counts(bridge, sites({anchor, 10}), [&](const Fixture& asymmetric) {
                            family.consider(asymmetric);
                            const int opposite = anchor == 7 ? 8 : 9;
                            with_counts(asymmetric, sites({opposite, 11}), [&](const Fixture& cross) {
                                family.consider(cross);
                            });
                        });
                    }
                    with_counts(bridge, sites({6, 7, 10}), [&](const Fixture& third_cap) {
                        family.consider(third_cap);
                        for (int old_cap : {8, 9})
                            with_counts(third_cap, sites({old_cap, 11}), [&](const Fixture& cross) {
                                family.consider(cross);
                            });
                    });
                });
            });
        });
    });
}

Fixture start_fan(const Fixture& source) {
    return adjoin(adjoin(source, sites({4, 5}), 3), sites({4, 6}), 3);
}

void pair_fan(const Fixture& source, Family& family) {
    const auto twinned = start_fan(source);
    family.consider(twinned);
    with_counts(twinned, sites({5, 6}), [&](const Fixture& fan) {
        require(legal_join(fan, sites({7, 8, 9})), "missing fan triple");
        family.consider(fan);
        with_counts(fan, sites({7, 8}), [&](const Fixture& first) {
            family.consider(first);
            with_counts(first, sites({8, 9}), [&](const Fixture& second) {
                family.consider(second);
                for (Set group : {sites({7, 8, 9}), sites({4, 10}), sites({6, 11})})
                    with_counts(second, group, [&](const Fixture& final) { family.consider(final); });
            });
        });
    });
}

void opposite_caps(const Fixture& source, Family& family) {
    if (std::min({source.loose[4], source.loose[5], source.loose[6]}) < 3) return;
    for (unsigned profile = 0; profile < 8; ++profile) {
        auto layer = source;
        const std::array<Set, 3> groups{sites({4, 5}), sites({4, 6}), sites({5, 6})};
        for (unsigned i = 0; i < groups.size(); ++i) layer = adjoin(layer, groups[i], 2 + (profile >> i & 1));
        family.consider(layer);
        with_counts(layer, sites({4, 5, 6}), [&](const Fixture& first) {
            family.consider(first);
            with_counts(first, sites({7, 8, 9}), [&](const Fixture& second) {
                family.consider(second);
                with_counts(second, sites({7, 10}), [&](const Fixture& cross_first) {
                    family.consider(cross_first);
                    with_counts(cross_first, sites({8, 10}), [&](const Fixture& cross_second) {
                        require(legal_join(cross_second, sites({11, 12, 13})), "missing cross-layer triple");
                        family.consider(cross_second);
                        for (Set group : {sites({11, 12}), sites({11, 13}), sites({12, 13})})
                            with_counts(cross_second, group, [&](const Fixture& final) { family.consider(final); });
                    });
                });
            });
        });
    }
}

std::vector<Word> literal_checks(const Fixture& fixture) {
    std::vector<Word> supports(fixture.count);
    int name = 0;
    for (int i = 0; i < fixture.count; ++i)
        each(fixture.neighbors[i] & ~mask(i + 1), [&](int j) {
            supports[i] |= bit(name);
            supports[j] |= bit(name++);
        });
    for (int i = 0; i < fixture.count; ++i)
        for (int j = 0; j < fixture.loose[i]; ++j) supports[i] |= bit(name++);
    require(name == fixture.width, "literal names do not encode source width");

    Fixture seen{};
    seen.width = seen.loose[0] = 3;
    seen.count = 1;
    require(std::popcount(supports[0]) == 3, "bad seed support");
    Word introduced = supports[0];
    for (int i = 1; i < fixture.count; ++i) {
        const Set parents = fixture.neighbors[i] & mask(i);
        const auto fresh = std::popcount(supports[i] & ~introduced);
        require(std::popcount(supports[i] & introduced) == std::popcount(parents),
                "literal parent count differs");
        seen = adjoin(seen, parents, fresh);
        introduced |= supports[i];
    }
    require(seen.source() == fixture.source(), "literal replay changed the fixture");
    return supports;
}

std::vector<Word> verify_minima(const Table& full, const std::vector<Word>& supports) {
    std::vector<Word> dual{0};
    for (Word support : supports) {
        const auto size = dual.size();
        for (std::size_t i = 0; i < size; ++i) dual.push_back(dual[i] ^ support);
    }
    std::sort(dual.begin(), dual.end(), [](Word a, Word b) {
        return std::pair{std::popcount(a), a} < std::pair{std::popcount(b), b};
    });
    require(std::adjacent_find(dual.begin(), dual.end()) == dual.end(), "dependent chronological stars");
    std::vector<Word> minimal;
    Table by_span(full.width);
    for (Word word : dual) {
        if (!word || std::any_of(minimal.begin(), minimal.end(), [&](Word small) { return (word & small) == small; }))
            continue;
        minimal.push_back(word);
        const auto d = static_cast<Byte>(std::popcount(word) - 1);
        each(word, [&](int i) {
            each(word & ~mask(i + 1), [&](int j) {
                by_span.rows[i][j] = by_span.rows[j][i] = std::min(by_span.rows[i][j], d);
            });
        });
    }
    require(exact_map(full, by_span, identity(full.width)), "cut and direct span minima disagree");
    return dual;
}

bool verify_controls() {
    const auto example = adjoin(start_fan(core(false, 63)), sites({5, 6}), 2);
    const auto source = remeasure(example);
    verify_minima(source, literal_checks(example));
    require(!source.legal.empty(), "control requires a true triple");
    auto reversal = identity(source.width);
    std::reverse(reversal.begin(), reversal.begin() + source.width);
    Table renamed(source.width);
    for (int i = 0; i < source.width; ++i)
        for (int j = 0; j < source.width; ++j)
            renamed.rows[reversal[i]][reversal[j]] = source.rows[i][j];
    for (Mark triple : source.legal) renamed.legal.push_back(image(triple, reversal));
    std::sort(renamed.legal.begin(), renamed.legal.end());
    fingerprint(renamed);
    require(exact_map(source, renamed, reversal) && !opposing(source, renamed, reversal), "renaming control");
    renamed.legal.pop_back();
    require(opposing(source, renamed, reversal).has_value(), "planted wrong verdict escaped");
    return true;
}

template<class Map> void counts_json(std::ostream& out, const Map& counts) {
    bool comma = false;
    out << '{';
    for (const auto& [key, count] : counts) {
        if (comma) out << ',';
        out << '"' << key << "\":" << count;
        comma = true;
    }
    out << '}';
}

void print_trial(std::ostream& out, const Trial& trial) {
    const auto& fixture = trial.fixture;
    const auto& conflict = trial.conflict;
    const auto full = remeasure(fixture);
    const auto supports = literal_checks(fixture);
    const auto dual = verify_minima(full, supports);
    const Table view = trial.horizon ? capped(full, trial.horizon) : full;
    require(exact_map(view, view, conflict.mapping) && full.permits(conflict.left)
            && !full.permits(conflict.right) && conflict.right == image(conflict.left, conflict.mapping),
            "literal certificate failed");
    if (trial.horizon) {
        const Table next = capped(full, trial.horizon + 1);
        require(!exact_map(next, next, conflict.mapping), "witness also matches at the next horizon");
        Statistics stats;
        require(!self_conflict(next, stats), "some violation survives the alleged first passing horizon");
    }
    const std::set<Word> equations(dual.begin(), dual.end());
    std::vector<int> changed_stars;
    for (std::size_t i = 0; i < supports.size(); ++i) {
        Word mapped = 0;
        each(supports[i], [&](int label) { mapped |= bit(conflict.mapping[label]); });
        if (!equations.contains(mapped)) changed_stars.push_back(i);
    }
    int full_differences = 0;
    std::vector<int> minima;
    for (int i = 0; i < full.width; ++i)
        for (int j = i + 1; j < full.width; ++j) {
            const auto d = full.rows[i][j];
            full_differences += d != full.rows[conflict.mapping[i]][conflict.mapping[j]];
            minima.push_back(1 + d);
        }
    out << "{\"width\":" << fixture.width << ",\"sites\":" << fixture.count
        << ",\"failing_K_horizon\":";
    if (trial.horizon) out << trial.horizon; else out << "null";
    out << ",\"all_full_pairs_checked\":" << minima.size()
        << ",\"full_pairs_changed_by_permutation\":" << full_differences << ",\"legal_mark\":";
    number_array(out, conflict.left.begin(), conflict.left.end());
    out << ",\"forbidden_image\":";
    number_array(out, conflict.right.begin(), conflict.right.end());
    out << ",\"permutation\":";
    number_array(out, conflict.mapping.begin(), conflict.mapping.begin() + full.width);
    out << ",\"changed_junction_equation_indices\":";
    number_array(out, changed_stars.begin(), changed_stars.end());
    out << ",\"chronological_junction_supports\":[";
    for (std::size_t i = 0; i < supports.size(); ++i) {
        if (i) out << ',';
        std::vector<int> labels;
        each(supports[i], [&](int label) { labels.push_back(label); });
        number_array(out, labels.begin(), labels.end());
    }
    out << "],\"full_upper_triangle_K\":";
    number_array(out, minima.begin(), minima.end());
    out << '}';
}

} // namespace

int main() {
    try {
        verify_controls();
        std::array<Family, 4> families;
        families[0].name = "symmetric_competing_caps";
        families[1].name = "staggered_competing_caps";
        families[2].name = "overlapping_pair_fan";
        families[3].name = "opposite_group_caps";
        auto finished = [&] {
            return std::any_of(families.begin(), families.end(), [](const Family& family) { return family.finished(); });
        };
        for (unsigned profile = 0; profile < 64 && !finished(); ++profile) {
            const Fixture symmetric = core(false, profile);
            competing_caps(symmetric, false, families[0]);
            if (!finished()) competing_caps(core(true, profile), true, families[1]);
            if (!finished()) pair_fan(symmetric, families[2]);
            if (!finished()) opposite_caps(symmetric, families[3]);
        }
        std::cout << "{\"complete_design\":" << (finished() ? "false" : "true")
                  << ",\"full_collision_found\":" << (finished() ? "true" : "false")
                  << ",\"renaming_and_planted_verdict_controls_passed\":true,\"families\":[\n";
        for (std::size_t i = 0; i < families.size(); ++i) {
            if (i) std::cout << ",\n";
            const auto& family = families[i];
            std::cout << "{\"family\":";
            quoted(std::cout, family.name);
            std::cout << ",\"high_incidence_records\":" << family.qualified
                      << ",\"no_legal_triples\":" << family.without_legal_triple
                      << ",\"duplicate_literal_records\":" << family.duplicate
                      << ",\"exact_searches\":" << family.exact_calls
                      << ",\"generators_visited\":" << family.generators
                      << ",\"triple_positive_widths\":";
            counts_json(std::cout, family.positive_widths);
            std::cout << ",\"first_preserving_K_horizons\":";
            counts_json(std::cout, family.passing_cutoffs);
            std::cout << ",\"strongest_failure\":";
            if (family.best) print_trial(std::cout, *family.best); else std::cout << "null";
            std::cout << '}';
        }
        std::cout << "]}\n";
    } catch (const std::exception& error) {
        std::cerr << "orbit search: " << error.what() << '\n';
        return 1;
    }
}
