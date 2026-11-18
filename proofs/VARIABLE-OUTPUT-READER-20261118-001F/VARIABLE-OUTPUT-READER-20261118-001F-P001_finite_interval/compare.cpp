// Compare full bond-distance tables and three-parent verdicts.
// Bit names: increasing unordered pairs of ordinary junctions, then
// consecutive loose names at each junction in input order.

#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include <charconv>
#include <chrono>
#include <compare>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <functional>
#include <iostream>
#include <mutex>
#include <numeric>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <tuple>
#include <unordered_map>
#include <utility>
#include <vector>
#include <unistd.h>

namespace {

constexpr int MaxJunctions = 15;  // The interval uses at most 12. Replay also uses a 15-junction control.
constexpr int MaxWidth = 64;
constexpr int MaxCuts = 1 << MaxJunctions;
constexpr std::uint8_t Infinity = 255;
using Word = std::uint64_t;
using Set = std::uint16_t;
using Byte = std::uint8_t;
using Mark = std::array<int, 3>;
using Permutation = std::array<int, MaxWidth>;

Word bit(int i) { return Word{1} << i; }
Word low(Word set) { return set & (Word{0} - set); }
Word mask(int n) { return n == MaxWidth ? ~Word{0} : bit(n) - 1; }

void require(bool value, std::string_view message) {
    if (!value)
        throw std::runtime_error(std::string(message));
}

template<class F> void each(Word bits, F function) {
    while (bits) {
        const Word next = low(bits);
        bits ^= next;
        function(std::countr_zero(next));
    }
}

struct Fixture {
    std::uint64_t line{};
    int count{}, width{};
    std::array<Set, MaxJunctions> neighbors{};
    std::array<Byte, MaxJunctions> loose{};

    auto graph_key() const { return std::tie(count, neighbors); }
    std::string source() const {
        std::ostringstream out;
        out << count;
        for (int i = 0; i < count; ++i)
            out << ' ' << neighbors[i];
        for (int i = 0; i < count; ++i)
            out << ' ' << static_cast<int>(loose[i]);
        return out.str();
    }
};

Fixture parse(const std::string& raw, std::uint64_t line) {
    Fixture result;
    result.line = line;
    auto p = raw.data();
    const auto end = p + raw.size();
    auto space = [&] {
        while (p != end && (*p == ' ' || *p == '\t' || *p == '\r'))
            ++p;
    };
    auto read = [&] {
        space();
        int value = 0;
        auto [next, error] = std::from_chars(p, end, value);
        if (error != std::errc() || value < 0)
            throw std::runtime_error("invalid integer at input line " + std::to_string(line));
        p = next;
        return value;
    };
    const int count = read();
    require(count >= 1 && count <= MaxJunctions, "invalid junction count");
    result.count = count;
    for (int i = 0; i < count; ++i) {
        const int adjacent = read();
        require(adjacent < (1 << count) && !(adjacent & bit(i)), "invalid ordinary adjacency");
        result.neighbors[i] = static_cast<Set>(adjacent);
    }
    int degrees = 0;
    int loose = 0;
    for (int i = 0; i < count; ++i) {
        const int free = read();
        const int degree = std::popcount(result.neighbors[i]);
        require(free <= 3 && degree + free >= 3 && degree + free <= 6, "invalid junction support");
        result.loose[i] = static_cast<Byte>(free);
        degrees += degree;
        loose += free;
        each(result.neighbors[i], [&](int j) {
            require((result.neighbors[j] & bit(i)) != 0, "ordinary adjacency must be symmetric");
        });
    }
    space();
    if (p != end)
        throw std::runtime_error("trailing input at line " + std::to_string(line));
    result.width = degrees / 2 + loose;
    require(result.width <= MaxWidth && loose >= 1, "invalid bit count or no outside attachment");
    return result;
}

struct Cut {
    Word shared;
    Set selected;
    Byte shared_count;
    Byte complement_count;
    std::array<Set, MaxJunctions> complement_parts;
};

class Graph {
public:
    explicit Graph(const Fixture& fixture) : adjacent(fixture.neighbors), count(fixture.count) {
        for (int i = 0; i < count; ++i)
            each(adjacent[i] & ~mask(i + 1), [&](int j) {
                const Word edge = bit(shared_count++);
                shared_at[i] |= edge;
                shared_at[j] |= edge;
            });
        const auto all = static_cast<Set>(mask(count));
        require(flood(all) == all, "disconnected ordinary source");
        std::vector<Word> boundary(all + 1);
        for (Set selected = 1; selected <= all; ++selected) {
            const Set first = static_cast<Set>(low(selected));
            boundary[selected] = boundary[selected ^ first] ^ shared_at[std::countr_zero(first)];
            if (flood(selected) != selected)
                continue;
            Cut cut{};
            cut.shared = boundary[selected];
            cut.selected = selected;
            cut.shared_count = static_cast<Byte>(std::popcount(cut.shared));
            Set complement = all ^ selected;
            while (complement) {
                const Set part = flood(complement);
                cut.complement_parts[cut.complement_count++] = part;
                complement ^= part;
            }
            cuts.push_back(cut);
        }
    }

    const std::vector<std::uint16_t>& valid_cuts(Set live) {
        auto [result, inserted] = valid_by_live.try_emplace(live);
        if (inserted) {
            for (std::size_t i = 0; i < cuts.size(); ++i) {
                const Cut& cut = cuts[i];
                const auto end = cut.complement_parts.begin() + cut.complement_count;
                // The outside connects exactly the complement components with
                // a loose distinction. Multiplicity does not affect this test.
                if (std::all_of(cut.complement_parts.begin(), end, [&](Set part) { return (part & live) != 0; }))
                    result->second.push_back(static_cast<std::uint16_t>(i));
            }
        }
        return result->second;
    }

    int shared_count = 0;
    std::vector<Cut> cuts;

private:
    Set flood(Set pool) const {
        Set frontier = static_cast<Set>(low(pool));
        Set seen = frontier;
        while (frontier) {
            const auto vertex = std::countr_zero(frontier);
            frontier &= frontier - 1;
            const Set added = static_cast<Set>(adjacent[vertex] & pool & ~seen);
            seen |= added;
            frontier |= added;
        }
        return seen;
    }

    std::array<Set, MaxJunctions> adjacent;
    int count;
    std::array<Word, MaxJunctions> shared_at{};
    std::unordered_map<Set, std::vector<std::uint16_t>> valid_by_live;
};

struct Signature {
    Word first{}, second{};
    auto operator<=>(const Signature&) const = default;
};

struct Table {
    explicit Table(int size) : width(size) {
        for (int i = 0; i < width; ++i) {
            std::fill_n(rows[i].begin(), width, Infinity);
            rows[i][i] = 0;
        }
    }

    int width;
    std::array<std::array<Byte, MaxWidth>, MaxWidth> rows;
    std::array<Word, MaxWidth> colors{};
    std::vector<Mark> legal;
    Signature signature;

    bool permits(Mark mark) const {
        return std::binary_search(legal.begin(), legal.end(), mark);
    }
};

Word mix(Word value) {
    value = (value ^ (value >> 30)) * 0xbf58476d1ce4e5b9ULL;
    value = (value ^ (value >> 27)) * 0x94d049bb133111ebULL;
    return value ^ (value >> 31);
}

void fingerprint(Table& table) {
    table.signature = {};
    static const auto salts = [] {
        std::array<Word, 256> result{};
        for (int i = 0; i < 256; ++i)
            result[i] = mix(0x9e3779b97f4a7c15ULL * (i + 1));
        return result;
    }();
    std::array<Word, MaxWidth> first{};
    for (int i = 0; i < table.width; ++i)
        for (int j = 0; j < table.width; ++j)
            first[i] += salts[table.rows[i][j]];
    for (int i = 0; i < table.width; ++i) {
        Word color = mix(first[i] ^ 0xb492b66fbe98f273ULL);
        for (int j = 0; j < table.width; ++j)
            color += mix(first[j] ^ salts[table.rows[i][j]]);
        table.colors[i] = color;
        table.signature.first += mix(color);
        table.signature.second += mix(color ^ 0x91e10da5c79e7b1dULL);
    }
    table.signature.first ^= mix(table.width);
    table.signature.second ^= mix(17 + table.width);
}

Table measure(const Fixture& fixture, Graph& graph) {
    Table result(fixture.width);
    const int n = fixture.width;
    std::array<Word, MaxJunctions> loose_bits{};
    Set live = 0;
    Set twice = 0;
    Set thrice = 0;
    int fresh = graph.shared_count;
    for (int i = 0; i < fixture.count; ++i) {
        const int number = fixture.loose[i];
        if (number >= 1)
            live |= static_cast<Set>(bit(i));
        if (number >= 2)
            twice |= static_cast<Set>(bit(i));
        if (number >= 3)
            thrice |= static_cast<Set>(bit(i));
        if (number)
            loose_bits[i] = mask(number) << fresh;
        fresh += number;
    }
    require(fresh == n, "inconsistent bit labels");
    const auto& cuts = graph.valid_cuts(live);
    std::array<std::uint16_t, MaxCuts> ordered;
    std::array<Byte, MaxCuts> weights;
    std::array<std::size_t, MaxWidth + 2> offsets{};
    for (std::size_t i = 0; i < cuts.size(); ++i) {
        const Cut& cut = graph.cuts[cuts[i]];
        const int weight = cut.shared_count
            + std::popcount(static_cast<Set>(live & cut.selected))
            + std::popcount(static_cast<Set>(twice & cut.selected))
            + std::popcount(static_cast<Set>(thrice & cut.selected));
        require(weight >= 3 && weight <= n, "unexpected short or empty bond");
        weights[i] = static_cast<Byte>(weight);
        ++offsets[weight + 1];
    }
    std::partial_sum(offsets.begin(), offsets.end(), offsets.begin());
    auto cursor = offsets;
    for (std::size_t i = 0; i < cuts.size(); ++i)
        ordered[cursor[weights[i]]++] = cuts[i];
    std::array<Word, MaxWidth> unassigned;
    for (int i = 0; i < n; ++i)
        unassigned[i] = mask(n) & ~mask(i + 1);
    int remaining = n * (n - 1) / 2;
    for (int weight = 3; remaining && weight <= n; ++weight) {
        for (std::size_t i = offsets[weight]; remaining && i < offsets[weight + 1]; ++i) {
            const Cut& cut = graph.cuts[ordered[i]];
            Word support = cut.shared;
            each(cut.selected & live, [&](int site) { support |= loose_bits[site]; });
            each(support, [&](int a) {
                const Word pending = support & unassigned[a];
                unassigned[a] ^= pending;
                remaining -= std::popcount(pending);
                each(pending, [&](int b) { result.rows[a][b] = result.rows[b][a] = static_cast<Byte>(weight - 1); });
            });
        }
    }
    for (int a = 0; a < fixture.count; ++a) {
        if (!loose_bits[a])
            continue;
        for (int b = a + 1; b < fixture.count; ++b) {
            const Set common = fixture.neighbors[a] & fixture.neighbors[b];
            if (!common || !loose_bits[b])
                continue;
            for (int c = b + 1; c < fixture.count; ++c) {
                const Set neighbors = fixture.neighbors[c];
                if (!loose_bits[c] || !(fixture.neighbors[a] & neighbors)
                    || !(fixture.neighbors[b] & neighbors) || (common & neighbors))
                    continue;
                each(loose_bits[a], [&](int i) {
                    each(loose_bits[b], [&](int j) {
                        each(loose_bits[c], [&](int k) { result.legal.push_back({i, j, k}); });
                    });
                });
            }
        }
    }
    std::sort(result.legal.begin(), result.legal.end());
    fingerprint(result);
    return result;
}

using Profile = Word;

class MarkProfiles {
public:
    explicit MarkProfiles(const Table& table) {
        auto colors = table.colors;
        std::sort(colors.begin(), colors.begin() + table.width);
        const auto last = std::unique(colors.begin(), colors.begin() + table.width);
        for (int i = 0; i < table.width; ++i)
            ranks[i] = static_cast<unsigned>(std::lower_bound(colors.begin(), last, table.colors[i]) - colors.begin());
    }

    Profile key(const Table& table, Mark mark) const {
        const auto [a, b, c] = mark;
        std::array<unsigned, 3> decorated{
            (ranks[a] << 8) | table.rows[b][c], (ranks[b] << 8) | table.rows[a][c],
            (ranks[c] << 8) | table.rows[a][b]};
        if (decorated[0] > decorated[1])
            std::swap(decorated[0], decorated[1]);
        if (decorated[1] > decorated[2])
            std::swap(decorated[1], decorated[2]);
        if (decorated[0] > decorated[1])
            std::swap(decorated[0], decorated[1]);
        return (Word{decorated[0]} << 32) | (Word{decorated[1]} << 16) | decorated[2];
    }

    std::vector<Profile> positive(const Table& table) const {
        std::vector<Profile> result;
        result.reserve(table.legal.size());
        for (Mark mark : table.legal)
            result.push_back(key(table, mark));
        std::sort(result.begin(), result.end());
        result.erase(std::unique(result.begin(), result.end()), result.end());
        return result;
    }

    bool homogeneous(const Table& table) const {
        const auto allowed = positive(table);
        for (int a = 0; a + 2 < table.width; ++a)
            for (int b = a + 1; b + 1 < table.width; ++b)
                for (int c = b + 1; c < table.width; ++c) {
                    const Mark choice{a, b, c};
                    const auto profile = key(table, choice);
                    if (std::binary_search(allowed.begin(), allowed.end(), profile) && !table.permits(choice))
                        return false;
                }
        return true;
    }

private:
    std::array<unsigned, MaxWidth> ranks{};
};

Permutation identity(int n) {
    Permutation result{};
    std::iota(result.begin(), result.begin() + n, 0);
    return result;
}

Mark image(Mark mark, const Permutation& permutation) {
    for (int& i : mark)
        i = permutation[i];
    std::sort(mark.begin(), mark.end());
    return mark;
}

struct Conflict {
    Permutation mapping;
    Mark left, right;
    bool left_legal;
};

bool exact_map(const Table& left, const Table& right, const Permutation& mapping) {
    if (left.width != right.width)
        return false;
    Word seen = 0;
    for (int i = 0; i < left.width; ++i) {
        if (mapping[i] < 0 || mapping[i] >= left.width || (seen & bit(mapping[i])))
            return false;
        seen |= bit(mapping[i]);
        for (int j = 0; j < i; ++j)
            if (left.rows[i][j] != right.rows[mapping[i]][mapping[j]])
                return false;
    }
    return true;
}

std::optional<Conflict> opposing(const Table& left, const Table& right, const Permutation& mapping) {
    for (Mark mark : left.legal) {
        const Mark transported = image(mark, mapping);
        if (!right.permits(transported)) {
            require(exact_map(left, right, mapping), "computed map fails the full table");
            return Conflict{mapping, mark, transported, true};
        }
    }
    if (left.legal.size() == right.legal.size())
        return std::nullopt;
    Permutation inverse{};
    for (int i = 0; i < left.width; ++i)
        inverse[mapping[i]] = i;
    for (Mark mark : right.legal) {
        const Mark transported = image(mark, inverse);
        if (!left.permits(transported)) {
            require(exact_map(left, right, mapping), "computed map fails the full table");
            return Conflict{mapping, transported, mark, false};
        }
    }
    throw std::logic_error("bijective map failed to explain different menu counts");
}

class Quotient {
public:
    explicit Quotient(const Table& source) : table(source) {
        for (int i = 0; i < table.width; ++i) {
            auto own = std::find_if(blocks.begin(), blocks.end(), [&](const auto& block) {
                const int other = block.front();
                if (table.colors[i] != table.colors[other])
                    return false;
                for (int j = 0; j < table.width; ++j)
                    if (j != i && j != other && table.rows[i][j] != table.rows[other][j])
                        return false;
                return true;
            });
            if (own == blocks.end())
                blocks.push_back({i});
            else
                own->push_back(i);
        }
        for (const auto& block : blocks) {
            colors.push_back({table.colors[block.front()], block.size(),
                block.size() > 1 ? table.rows[block[0]][block[1]] : 0});
        }
    }

    int size() const { return static_cast<int>(blocks.size()); }

    Byte entry(int i, int j) const {
        return table.rows[blocks[i].front()][blocks[j].front()];
    }

    Permutation lift(const Quotient& target, const Permutation& mapping) const {
        Permutation result{};
        for (int i = 0; i < size(); ++i)
            for (std::size_t k = 0; k < blocks[i].size(); ++k)
                result[blocks[i][k]] = target.blocks[mapping[i]][k];
        return result;
    }

    const Table& table;
    std::vector<std::vector<int>> blocks;
    struct Color {
        Word rooted;
        std::size_t multiplicity;
        int inside;
        auto operator<=>(const Color&) const = default;
    };
    std::vector<Color> colors;
};

template<class F>
bool visit_maps(const Quotient& left, const Quotient& right, F visit) {
    const int n = left.size();
    if (n != right.size())
        return false;
    std::array<Word, MaxWidth> domains{};
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j)
            if (left.colors[i] == right.colors[j])
                domains[i] |= bit(j);
        if (!domains[i])
            return false;
    }
    Permutation mapping{};
    auto search = [&](auto&& self, Word remaining, const std::array<Word, MaxWidth>& choices) -> bool {
        if (!remaining)
            return visit(left.lift(right, mapping));
        int next = std::countr_zero(remaining);
        each(remaining, [&](int i) {
            if (std::popcount(choices[i]) < std::popcount(choices[next]))
                next = i;
        });
        const Word after = remaining ^ bit(next);
        Word options = choices[next];
        while (options) {
            const Word selected = low(options);
            options ^= selected;
            const int target = std::countr_zero(selected);
            auto narrowed = choices;
            bool feasible = true;
            each(after, [&](int i) {
                const Byte required = left.entry(next, i);
                Word compatible = 0;
                each(choices[i] & ~selected, [&](int j) {
                    if (right.entry(target, j) == required)
                        compatible |= bit(j);
                });
                narrowed[i] = compatible;
                feasible = feasible && compatible != 0;
            });
            if (!feasible)
                continue;
            mapping[next] = target;
            if (self(self, after, narrowed))
                return true;
        }
        return false;
    };
    return search(search, mask(n), domains);
}

struct Statistics {
    std::uint64_t measured{}, pairs{}, no_menu{}, legal_triples{};
    std::uint64_t graph_groups{}, profiles_certified{}, exact_self{}, generators{};
    std::uint64_t distinct_fingerprints{}, colliding_buckets{}, bucket_pairs{};
    std::uint64_t cross_empty{}, cross_profiles{}, cross_exact{}, cross_maps{};
    std::array<std::uint64_t, MaxJunctions + 1> by_junctions{}, positive_by_junctions{};
};

std::optional<Conflict> self_conflict(const Table& table, Statistics& stats) {
    const Quotient quotient(table);
    for (const auto& block : quotient.blocks) {
        for (std::size_t i = 1; i < block.size(); ++i) {
            auto mapping = identity(table.width);
            std::swap(mapping[block[0]], mapping[block[i]]);
            ++stats.generators;
            if (auto found = opposing(table, table, mapping))
                return found;
        }
    }
    std::optional<Conflict> result;
    const auto unchanged = identity(table.width);
    visit_maps(quotient, quotient, [&](const Permutation& mapping) {
        if (mapping != unchanged) {
            ++stats.generators;
            result = opposing(table, table, mapping);
        }
        return result.has_value();
    });
    return result;
}

std::optional<Permutation> first_exact_map(const Table& left, const Table& right) {
    if (left.width != right.width)
        return std::nullopt;
    std::optional<Permutation> result;
    visit_maps(Quotient(left), Quotient(right), [&](const Permutation& mapping) {
        require(exact_map(left, right, mapping), "quotient lift fails the full table");
        result = mapping;
        return true;
    });
    return result;
}

struct Summary {
    Signature signature;
    bool has_legal = false;
    bool profile_homogeneous = false;
};

struct Found {
    Fixture left, right;
    Conflict detail;
    std::string phase;
};

void number_array(std::ostream& out, auto begin, auto end) {
    out << '[';
    bool comma = false;
    for (; begin != end; ++begin) {
        if (comma)
            out << ',';
        out << +*begin;
        comma = true;
    }
    out << ']';
}

void quoted(std::ostream& out, const std::string& input) {
    out << '"';
    for (char c : input) {
        if (c == '"' || c == '\\')
            out << '\\';
        out << c;
    }
    out << '"';
}

void witness_json(std::ostream& out, const Found& found) {
    const auto& detail = found.detail;
    out << "{\"phase\":";
    quoted(out, found.phase);
    out << ",\"left_line\":" << found.left.line << ",\"right_line\":" << found.right.line
        << ",\"width\":" << found.left.width << ",\"left_source\":";
    quoted(out, found.left.source());
    out << ",\"right_source\":";
    quoted(out, found.right.source());
    out << ",\"left_mark\":";
    number_array(out, detail.left.begin(), detail.left.end());
    out << ",\"right_mark\":";
    number_array(out, detail.right.begin(), detail.right.end());
    out << ",\"left_legal\":" << (detail.left_legal ? "true" : "false")
        << ",\"right_legal\":" << (detail.left_legal ? "false" : "true")
        << ",\"left_to_right_bit_map\":";
    number_array(out, detail.mapping.begin(), detail.mapping.begin() + found.left.width);
    out << '}';
}

void atomic_file(const std::string& path, const std::function<void(std::ostream&)>& write) {
    const auto temporary = path + ".tmp-" + std::to_string(getpid());
    {
        std::ofstream output(temporary);
        require(output.is_open(), "cannot write " + temporary);
        write(output);
        output.close();
        require(output.good(), "failed writing " + temporary);
    }
    std::filesystem::rename(temporary, path);
}

struct Options {
    std::string input, output, dump, residuals;
    std::size_t limit = 0;
    int threads = 1;
    int expected_width = 0;
    bool force_exact = false;
};

struct Residual {
    Fixture source;
    std::size_t legal_count;
    std::uint64_t generators;
};

void checkpoint(const Options& options, const std::string& phase, std::size_t done, std::size_t total) {
    std::cerr << phase << " " << done << "/" << total << '\n';
    if (options.output.empty())
        return;
    atomic_file(options.output + ".checkpoint.json", [&](std::ostream& out) {
        out << "{\"phase\":";
        quoted(out, phase);
        out << ",\"done\":" << done << ",\"total\":" << total << "}\n";
    });
}

Table remeasure(const Fixture& fixture) {
    Graph graph(fixture);
    return measure(fixture, graph);
}

void cross_compare(const Options& options, const std::vector<Fixture>& fixtures,
                   const std::vector<Summary>& summaries, Statistics& stats, std::optional<Found>& found) {
    std::vector<std::size_t> order(fixtures.size());
    std::iota(order.begin(), order.end(), 0);
    std::sort(order.begin(), order.end(), [&](std::size_t a, std::size_t b) {
        return summaries[a].signature < summaries[b].signature;
    });
    constexpr std::size_t ProgressStride = 100000;
    std::size_t next_progress = ProgressStride;
    for (std::size_t begin = 0; begin < order.size();) {
        std::size_t end = begin + 1;
        while (end < order.size() && summaries[order[end]].signature == summaries[order[begin]].signature)
            ++end;
        ++stats.distinct_fingerprints;
        if (end - begin > 1) {
            ++stats.colliding_buckets;
            const std::uint64_t size = end - begin;
            stats.bucket_pairs += size * (size - 1) / 2;
            std::vector<std::size_t> positive, other;
            for (std::size_t i = begin; i < end; ++i) {
                const auto index = order[i];
                (summaries[index].has_legal ? positive : other).push_back(index);
            }
            const std::uint64_t empty = other.size();
            if (!options.force_exact)
                stats.cross_empty += empty * (empty - (empty != 0)) / 2;
            else {
                positive.insert(positive.end(), other.begin(), other.end());
                other.clear();
            }
            const auto first_empty = positive.size();
            positive.insert(positive.end(), other.begin(), other.end());
            std::vector<std::optional<Table>> tables(positive.size());
            auto get = [&](std::size_t index) -> const Table& {
                if (!tables[index])
                    tables[index].emplace(remeasure(fixtures[positive[index]]));
                return *tables[index];
            };
            for (std::size_t i = 0; i < first_empty; ++i) {
                const Table& left = get(i);
                const auto& left_scope = fixtures[positive[i]];
                std::optional<std::vector<Profile>> left_profile;
                for (std::size_t j = i + 1; j < positive.size(); ++j) {
                    const Table& right = get(j);
                    if (!options.force_exact && summaries[positive[i]].profile_homogeneous
                        && summaries[positive[j]].profile_homogeneous && !right.legal.empty()) {
                        if (!left_profile)
                            left_profile = MarkProfiles(left).positive(left);
                        if (*left_profile == MarkProfiles(right).positive(right)) {
                            ++stats.cross_profiles;
                            continue;
                        }
                    }
                    ++stats.cross_exact;
                    if (auto mapping = first_exact_map(left, right)) {
                        ++stats.cross_maps;
                        if (auto conflict = opposing(left, right, *mapping)) {
                            found = Found{left_scope, fixtures[positive[j]], *conflict, "cross"};
                            return;
                        }
                    }
                }
            }
        }
        begin = end;
        if (begin >= next_progress) {
            checkpoint(options, "cross comparison", begin, order.size());
            next_progress = (begin / ProgressStride + 1) * ProgressStride;
        }
    }
    require(stats.bucket_pairs == stats.cross_empty + stats.cross_profiles + stats.cross_exact,
            "incomplete cross comparison");
}

void write_dump(const std::vector<Fixture>& fixtures, const std::string& path) {
    atomic_file(path, [&](std::ostream& out) {
        for (const Fixture& fixture : fixtures) {
            const Table table = remeasure(fixture);
            out << "{\"line\":" << fixture.line << ",\"source\":";
            quoted(out, fixture.source());
            out << ",\"width\":" << fixture.width << ",\"upper\":[";
            bool comma = false;
            for (int i = 0; i < fixture.width; ++i)
                for (int j = i + 1; j < fixture.width; ++j) {
                    if (comma)
                        out << ',';
                    out << +table.rows[i][j];
                    comma = true;
                }
            out << "],\"legal\":[";
            comma = false;
            for (Mark mark : table.legal) {
                if (comma)
                    out << ',';
                number_array(out, mark.begin(), mark.end());
                comma = true;
            }
            out << "]}\n";
        }
    });
}

void write_residuals(const std::vector<std::vector<Residual>>& collected, const std::string& path) {
    std::vector<const Residual*> ordered;
    for (const auto& part : collected)
        for (const auto& record : part)
            ordered.push_back(&record);
    std::sort(ordered.begin(), ordered.end(), [](const Residual* a, const Residual* b) {
        return a->source.line < b->source.line;
    });
    atomic_file(path, [&](std::ostream& out) {
        for (const Residual* record : ordered) {
            const Fixture& fixture = record->source;
            out << "{\"width\":" << fixture.width << ",\"line\":" << fixture.line << ",\"source\":";
            quoted(out, fixture.source());
            out << ",\"legal_triples\":" << record->legal_count
                << ",\"exact_generators_checked\":" << record->generators << "}\n";
        }
    });
}

void report(std::ostream& out, const Options& options, std::size_t loaded,
            const Statistics& stats, const std::optional<Found>& found) {
    out << "{\n  \"status\":\"" << (found ? "conflict" : "complete") << "\",\n  \"input\":";
    quoted(out, options.input);
    out << ",\n  \"threads\":" << options.threads
        << ",\n  \"expected_width\":" << options.expected_width
        << ",\n  \"prefix_limit\":" << options.limit
        << ",\n  \"forced_exact\":" << (options.force_exact ? "true" : "false") << ",\n";
    auto field = [&](const std::string& name, std::uint64_t n) {
        out << "  \"" << name << "\":" << n << ",\n";
    };
    field("loaded", loaded);
    field("measured", stats.measured);
    field("scalar_entries", stats.pairs);
    field("ordinary_adjacency_groups", stats.graph_groups);
    field("no_legal_triple", stats.no_menu);
    field("legal_triple_occurrences", stats.legal_triples);
    field("self_positive_cases_certified_by_profiles", stats.profiles_certified);
    field("self_exact_cases", stats.exact_self);
    field("self_generators_checked", stats.generators);
    field("distinct_rejection_fingerprints", stats.distinct_fingerprints);
    field("colliding_fingerprint_buckets", stats.colliding_buckets);
    field("cross_pairs_in_colliding_fingerprints", stats.bucket_pairs);
    field("cross_pairs_both_menus_empty", stats.cross_empty);
    field("cross_pairs_certified_by_profiles", stats.cross_profiles);
    field("cross_pairs_submitted_to_exact_search", stats.cross_exact);
    field("cross_pairs_with_verified_exact_maps", stats.cross_maps);
    out << "  \"by_junction_count\":{";
    bool comma = false;
    for (int i = 1; i <= MaxJunctions; ++i) {
        if (!stats.by_junctions[i])
            continue;
        if (comma)
            out << ',';
        out << "\"" << i << "\":{\"types\":" << stats.by_junctions[i]
            << ",\"types_with_legal_triples\":" << stats.positive_by_junctions[i] << '}';
        comma = true;
    }
    out << "},\n  \"witness\":";
    if (found)
        witness_json(out, *found);
    else
        out << "null";
    out << "\n}\n";
}

int run(const Options& options) {
    std::ifstream input(options.input);
    require(input.is_open(), "cannot open input " + options.input);
    std::vector<Fixture> fixtures;
    std::string raw;
    std::uint64_t line = 0;
    while ((!options.limit || fixtures.size() < options.limit) && std::getline(input, raw)) {
        ++line;
        if (raw.find_first_not_of(" \t\r") == std::string::npos)
            continue;
        Fixture fixture = parse(raw, line);
        require(!options.expected_width || fixture.width == options.expected_width, "unexpected source width");
        fixtures.push_back(fixture);
    }
    require(!input.bad() && !fixtures.empty(), "empty input or input read failed");
    std::stable_sort(fixtures.begin(), fixtures.end(), [](const Fixture& a, const Fixture& b) {
        return a.graph_key() < b.graph_key();
    });
    std::vector<std::size_t> boundaries{0};
    for (std::size_t i = 1; i < fixtures.size(); ++i)
        if (fixtures[i].graph_key() != fixtures[i - 1].graph_key())
            boundaries.push_back(i);
    boundaries.push_back(fixtures.size());

    std::vector<Summary> summaries(fixtures.size());
    std::vector<Statistics> local(options.threads);
    std::vector<std::vector<Residual>> residuals(options.threads);
    std::atomic<std::size_t> next{0}, done{0};
    std::atomic<bool> stop{false};
    std::mutex shared;
    std::optional<Found> found;
    std::exception_ptr error;
    checkpoint(options, "measuring", 0, fixtures.size());
    auto worker = [&](int index) {
        try {
            auto& stats = local[index];
            while (!stop) {
                const std::size_t group = next.fetch_add(1, std::memory_order_relaxed);
                if (group + 1 >= boundaries.size())
                    break;
                const std::size_t start = boundaries[group];
                const std::size_t end = boundaries[group + 1];
                Graph graph(fixtures[start]);
                ++stats.graph_groups;
                std::size_t completed = 0;
                for (std::size_t i = start; !stop && i < end; ++i) {
                    const auto& fixture = fixtures[i];
                    const Table table = measure(fixture, graph);
                    Summary& summary = summaries[i];
                    summary.signature = table.signature;
                    summary.has_legal = !table.legal.empty();
                    ++stats.measured;
                    ++completed;
                    stats.pairs += fixture.width * (fixture.width - 1) / 2;
                    stats.legal_triples += table.legal.size();
                    ++stats.by_junctions[fixture.count];
                    stats.positive_by_junctions[fixture.count] += summary.has_legal;
                    stats.no_menu += !summary.has_legal;
                    if (!options.force_exact && !summary.has_legal)
                        continue;
                    if (!options.force_exact && MarkProfiles(table).homogeneous(table)) {
                        summary.profile_homogeneous = true;
                        ++stats.profiles_certified;
                    } else {
                        ++stats.exact_self;
                        const std::uint64_t previous_generators = stats.generators;
                        auto conflict = self_conflict(table, stats);
                        if (!options.residuals.empty() && summary.has_legal
                            && (!options.force_exact || !MarkProfiles(table).homogeneous(table))) {
                            residuals[index].push_back({fixture, table.legal.size(),
                                stats.generators - previous_generators});
                        }
                        if (conflict) {
                            std::lock_guard lock(shared);
                            if (!found)
                                found = Found{fixture, fixture, *conflict, "self"};
                            stop = true;
                        }
                    }
                }
                const std::size_t previous = done.fetch_add(completed, std::memory_order_relaxed);
                constexpr std::size_t ProgressStride = 100000;
                if (previous / ProgressStride < (previous + completed) / ProgressStride) {
                    std::lock_guard lock(shared);
                    checkpoint(options, "measuring", done.load(), fixtures.size());
                }
            }
        } catch (...) {
            std::lock_guard lock(shared);
            if (!error)
                error = std::current_exception();
            stop = true;
        }
    };
    std::vector<std::thread> workers;
    for (int i = 0; i < options.threads; ++i)
        workers.emplace_back(worker, i);
    for (auto& thread : workers)
        thread.join();
    if (error)
        std::rethrow_exception(error);
    Statistics stats;
    for (const auto& part : local) {
        stats.measured += part.measured;
        stats.pairs += part.pairs;
        stats.no_menu += part.no_menu;
        stats.legal_triples += part.legal_triples;
        stats.graph_groups += part.graph_groups;
        stats.profiles_certified += part.profiles_certified;
        stats.exact_self += part.exact_self;
        stats.generators += part.generators;
        for (int i = 1; i <= MaxJunctions; ++i) {
            stats.by_junctions[i] += part.by_junctions[i];
            stats.positive_by_junctions[i] += part.positive_by_junctions[i];
        }
    }
    if (!found) {
        require(stats.measured == fixtures.size(), "not all fixtures measured");
        checkpoint(options, "cross comparison", 0, fixtures.size());
        cross_compare(options, fixtures, summaries, stats, found);
    }
    if (options.output.empty())
        report(std::cout, options, fixtures.size(), stats, found);
    else
        atomic_file(options.output, [&](std::ostream& out) { report(out, options, fixtures.size(), stats, found); });
    if (!options.dump.empty())
        write_dump(fixtures, options.dump);
    if (!options.residuals.empty())
        write_residuals(residuals, options.residuals);
    checkpoint(options, found ? "verified conflict" : "complete", stats.measured, fixtures.size());
    return found ? 1 : 0;
}

int self_test() {
    Table first(5);
    for (int i = 0; i < first.width; ++i)
        for (int j = i + 1; j < first.width; ++j)
            first.rows[i][j] = first.rows[j][i] = static_cast<Byte>(2 + i + j);
    first.legal = {{0, 1, 2}};
    fingerprint(first);
    auto renaming = identity(first.width);
    std::reverse(renaming.begin(), renaming.begin() + first.width);
    Table relabeled(first.width);
    for (int i = 0; i < first.width; ++i)
        for (int j = 0; j < first.width; ++j)
            relabeled.rows[renaming[i]][renaming[j]] = first.rows[i][j];
    relabeled.legal = {image(first.legal.front(), renaming)};
    fingerprint(relabeled);
    require(first.signature == relabeled.signature, "relabeling changed a rejection fingerprint");
    const auto mapping = first_exact_map(first, relabeled);
    require(mapping && !opposing(first, relabeled, *mapping), "true relabeling rejected");
    relabeled.legal = {{0, 1, 2}};
    require(opposing(first, relabeled, *mapping).has_value(), "same-count wrong verdict escaped");
    relabeled.legal.clear();
    require(opposing(first, relabeled, *mapping).has_value(), "empty-menu conflict escaped");
    ++relabeled.rows[0][1];
    ++relabeled.rows[1][0];
    fingerprint(relabeled);
    require(!first_exact_map(first, relabeled), "inexact correspondence accepted");

    Table twins(5);
    for (int i = 0; i < twins.width; ++i)
        for (int j = i + 1; j < twins.width; ++j)
            twins.rows[i][j] = twins.rows[j][i] = 2;
    twins.legal = {{0, 1, 2}};
    fingerprint(twins);
    Statistics stats;
    require(!MarkProfiles(twins).homogeneous(twins) && self_conflict(twins, stats).has_value(),
            "wrong verdict on an actual scalar automorphism escaped");
    std::cout << "{\"true_permutation_accepted\":true,\"same_count_wrong_verdict_detected\":true,"
                 "\"empty_menu_conflict_detected\":true,\"inexact_table_rejected\":true,"
                 "\"self_automorphism_conflict_detected\":true}\n";
    return 0;
}

} // namespace

int main(int argc, char** argv) {
    try {
        require(argc >= 2, "usage: compare INPUT [--threads N] [--expected-width W] [--output JSON]"
                         " [--limit N] [--dump JSONL] [--residuals JSONL] [--force-exact], or compare --self-test");
        if (std::string(argv[1]) == "--self-test")
            return self_test();
        Options options;
        options.input = argv[1];
        for (int i = 2; i < argc; ++i) {
            const std::string flag = argv[i];
            if (flag == "--force-exact") {
                options.force_exact = true;
                continue;
            }
            require(i + 1 < argc, "missing argument to " + flag);
            const std::string value = argv[++i];
            if (flag == "--threads")
                options.threads = std::stoi(value);
            else if (flag == "--expected-width")
                options.expected_width = std::stoi(value);
            else if (flag == "--limit")
                options.limit = std::stoull(value);
            else if (flag == "--output")
                options.output = value;
            else if (flag == "--dump")
                options.dump = value;
            else if (flag == "--residuals")
                options.residuals = value;
            else
                throw std::runtime_error("unknown option " + flag);
        }
        require(options.threads >= 1 && options.threads <= 8, "threads must be between 1 and 8");
        return run(options);
    } catch (const std::exception& error) {
        std::cerr << "compare: " << error.what() << '\n';
        return 2;
    }
}
