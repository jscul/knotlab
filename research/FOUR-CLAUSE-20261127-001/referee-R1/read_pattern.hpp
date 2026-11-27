#ifndef FOUR_CLAUSE_REFEREE_READ_PATTERN_HPP
#define FOUR_CLAUSE_REFEREE_READ_PATTERN_HPP

#include <algorithm>
#include <array>
#include <cstdint>
#include <limits>
#include <stdexcept>
#include <tuple>
#include <vector>

namespace four_read {

// A literal packs a nonempty raw carrier mask and its selected value.
using Literal = std::uint64_t;
using Clause = std::array<Literal, 3>;
using Pairing = std::array<std::array<Literal, 2>, 3>;

namespace pattern_detail {

using Id = std::uint32_t;
using Family = std::array<Clause, 4>;

struct Incidence {
    std::array<Id, 2> other;
    Literal raw_union;
};

struct Split {
    std::array<Id, 3> remainder;
    Id shared;
    unsigned partition;
};

inline std::array<Clause, 2> restore_clauses(
    Id first, const Split& row, const std::vector<Literal>& literals
) {
    Clause left{literals[row.shared], literals[first], literals[row.remainder[row.partition]]};
    Clause right{literals[row.shared], literals[row.remainder[(row.partition + 1) % 3]],
                 literals[row.remainder[(row.partition + 2) % 3]]};
    std::sort(left.begin(), left.end());
    std::sort(right.begin(), right.end());
    return {left, right};
}

inline Literal shared_literal(const Clause& a, const Clause& b) {
    Literal shared = 0;
    for (Literal literal : a) {
        if (std::find(b.begin(), b.end(), literal) == b.end()) {
            continue;
        }
        if (shared != 0) {
            throw std::invalid_argument("clause pair shares several literals");
        }
        shared = literal;
    }
    if (shared == 0) {
        throw std::invalid_argument("clause pair shares no literal");
    }
    return shared;
}

}  // namespace pattern_detail

// A qualifying family has a single shared signed literal for each of the six
// pairs of clauses. A literal's partner is the one shared by the other two
// clauses. Each pair can be used for the both reading.
inline Pairing pairs_of(const std::array<Clause, 4>& family) {
    using pattern_detail::shared_literal;
    Pairing pairs{{
        {shared_literal(family[0], family[1]), shared_literal(family[2], family[3])},
        {shared_literal(family[0], family[2]), shared_literal(family[1], family[3])},
        {shared_literal(family[0], family[3]), shared_literal(family[1], family[2])},
    }};
    for (auto& pair : pairs) {
        std::sort(pair.begin(), pair.end());
    }
    std::sort(pairs.begin(), pairs.end());
    return pairs;
}

// Two clauses sharing a literal split their four other literals into two
// pairs. A second such split of the same four literals, of a different
// partition, completes the family when the two shared carriers are disjoint.
// The shared literals then form one pair in the family. Every family has
// three descriptions this way. Use the one in which the least signed literal
// is shared. Sort splits in batches by the least of the four other literals.
inline std::vector<std::array<Clause, 4>> patterns(const std::vector<Clause>& input) {
    using namespace pattern_detail;
    std::vector<Clause> clauses = input;
    std::vector<Literal> literals;
    literals.reserve(3 * clauses.size());
    for (Clause& clause : clauses) {
        std::sort(clause.begin(), clause.end());
        Literal raw = 0;
        for (Literal literal : clause) {
            Literal carrier = literal >> 1;
            if (carrier == 0 || (raw & carrier) != 0) {
                throw std::invalid_argument("lower clause has empty or overlapping carriers");
            }
            raw |= carrier;
            literals.push_back(literal);
        }
    }
    std::sort(clauses.begin(), clauses.end());
    clauses.erase(std::unique(clauses.begin(), clauses.end()), clauses.end());
    std::sort(literals.begin(), literals.end());
    literals.erase(std::unique(literals.begin(), literals.end()), literals.end());
    if (literals.size() > std::numeric_limits<Id>::max()) {
        throw std::length_error("too many literals to index");
    }

    std::vector<Literal> carriers;
    carriers.reserve(literals.size());
    for (Literal literal : literals) {
        carriers.push_back(literal >> 1);
    }
    std::vector<std::vector<Incidence>> incident(literals.size());
    for (const Clause& clause : clauses) {
        std::array<Id, 3> ids;
        for (unsigned i = 0; i < 3; ++i) {
            ids[i] = static_cast<Id>(
                std::lower_bound(literals.begin(), literals.end(), clause[i]) - literals.begin()
            );
        }
        incident[ids[0]].push_back({{ids[1], ids[2]}, carriers[ids[1]] | carriers[ids[2]]});
        incident[ids[1]].push_back({{ids[0], ids[2]}, carriers[ids[0]] | carriers[ids[2]]});
        incident[ids[2]].push_back({{ids[0], ids[1]}, carriers[ids[0]] | carriers[ids[1]]});
    }
    for (auto& entries : incident) {
        std::sort(entries.begin(), entries.end(), [](const Incidence& a, const Incidence& b) {
            return a.other < b.other;
        });
    }

    std::vector<Family> result;
    std::vector<Split> rows;
    for (Id first = 0; first < literals.size(); ++first) {
        if (incident[first].size() < 2) {
            continue;
        }
        rows.clear();
        for (const Incidence& entry : incident[first]) {
            for (unsigned side = 0; side < 2; ++side) {
                const Id shared = entry.other[side];
                const Id next = entry.other[1 - side];
                if (next < first || incident[next].size() < 2) {
                    continue;
                }
                const Literal raw_union = carriers[first] | carriers[next];
                const auto& others = incident[shared];
                auto it = std::upper_bound(
                    others.begin(), others.end(), first,
                    [](Id value, const Incidence& candidate) { return value < candidate.other[0]; }
                );
                for (; it != others.end(); ++it) {
                    if ((raw_union & it->raw_union) != 0 || incident[it->other[0]].size() < 2 ||
                        incident[it->other[1]].size() < 2) {
                        continue;
                    }
                    Split row{{next, it->other[0], it->other[1]}, shared, 0};
                    std::sort(row.remainder.begin(), row.remainder.end());
                    row.partition = static_cast<unsigned>(
                        std::find(row.remainder.begin(), row.remainder.end(), next) - row.remainder.begin()
                    );
                    rows.push_back(row);
                }
            }
        }
        std::sort(rows.begin(), rows.end(), [](const Split& a, const Split& b) {
            return std::tie(a.remainder, a.partition, a.shared) <
                   std::tie(b.remainder, b.partition, b.shared);
        });

        auto group = rows.cbegin();
        while (group != rows.cend()) {
            auto group_end = std::find_if(group, rows.cend(), [&](const Split& row) {
                return row.remainder != group->remainder;
            });
            std::array<decltype(group), 4> splits;
            auto next = group;
            for (unsigned i = 0; i < 3; ++i) {
                splits[i] = next;
                while (next != group_end && next->partition == i) {
                    ++next;
                }
            }
            splits[3] = group_end;
            for (unsigned i = 0; i < 3; ++i) {
                for (unsigned j = i + 1; j < 3; ++j) {
                    for (auto a = splits[i]; a != splits[i + 1]; ++a) {
                        for (auto b = splits[j]; b != splits[j + 1]; ++b) {
                            if (std::min(a->shared, b->shared) > first ||
                                (carriers[a->shared] & carriers[b->shared]) != 0) {
                                continue;
                            }
                            auto left = restore_clauses(first, *a, literals);
                            auto right = restore_clauses(first, *b, literals);
                            Family family{left[0], left[1], right[0], right[1]};
                            std::sort(family.begin(), family.end());
                            result.push_back(family);
                        }
                    }
                }
            }
            group = group_end;
        }
    }
    std::sort(result.begin(), result.end());
    return result;
}

}  // namespace four_read

#endif
