#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <iterator>
#include <map>
#include <numeric>
#include <random>
#include <vector>

using Word = std::uint64_t;
using Bits = std::vector<Word>;

struct Bond {
    std::array<Word, 3> carriers;
    Word missing;
};

struct BondResult {
    std::vector<Bond> bonds;
    std::array<Word, 3> counts{};  // allowed representatives, unread readings, eligible triples
};

struct BoxResult {
    std::vector<std::array<Word, 6>> boxes;
    Word qualifying_pairs = 0;
};

static bool agrees(Word state, Word carrier) {
    const Word part = state & carrier;
    return part == 0 || part == carrier;
}

static void set_bit(Bits& row, std::size_t bit) {
    row[bit / 64] |= Word{1} << (bit % 64);
}

static Bits packed_agreement(const Bits& states, Word carrier) {
    Bits packed((states.size() + 63) / 64);
    for (std::size_t i = 0; i < states.size(); ++i) {
        if (agrees(states[i], carrier)) {
            set_bit(packed, i);
        }
    }
    return packed;
}

static std::vector<Bits> knot_fixings(const Bits& states, Word support) {
    // Complementing an entire state preserves every law and agreement.
    // Thus a fixing and its complement have the same possible readings.
    const Word first = support & -support;
    std::map<Word, Bits> by_pattern;
    for (std::size_t i = 0; i < states.size(); ++i) {
        Word pattern = states[i] & support;
        if (pattern & first) {
            pattern ^= support;
        }
        auto [entry, fresh] = by_pattern.try_emplace(pattern, (states.size() + 63) / 64, Word{0});
        set_bit(entry->second, i);
    }
    std::vector<Bits> fixings;
    for (auto& [pattern, mask] : by_pattern) {
        fixings.push_back(std::move(mask));
    }
    return fixings;
}

static bool varies(const Bits& yes, const Bits& fixing) {
    bool false_seen = false;
    bool true_seen = false;
    for (std::size_t i = 0; i < fixing.size(); ++i) {
        false_seen |= (fixing[i] & ~yes[i]) != 0;
        true_seen |= (fixing[i] & yes[i]) != 0;
        if (true_seen && false_seen) {
            return true;
        }
    }
    return false;
}

static std::array<Word, 4> pair_words(Word a, Word b, Word valid) {
    return {valid & ~a & ~b, valid & ~a & b, valid & a & ~b, a & b};
}

static bool free_pair(const Bits& a, const Bits& b, Word last) {
    unsigned present = 0;
    for (std::size_t i = 0; i < a.size(); ++i) {
        auto parts = pair_words(a[i], b[i], i + 1 == a.size() ? last : ~Word{0});
        for (unsigned part = 0; part < 4; ++part) {
            present |= static_cast<unsigned>(parts[part] != 0) << part;
        }
        if (present == 15) {
            return true;
        }
    }
    return false;
}

static unsigned present_words(const std::array<Word, 4>& pair, Word c) {
    unsigned present = 0;
    for (unsigned part = 0; part < 4; ++part) {
        present |= static_cast<unsigned>((pair[part] & ~c) != 0) << (2 * part);
        present |= static_cast<unsigned>((pair[part] & c) != 0) << (2 * part + 1);
    }
    return present;
}

static unsigned missing_words(const Bits& a, const Bits& b, const Bits& c, Word last,
                              const std::vector<std::array<Word, 4>>& first_blocks) {
    unsigned present = 0;
    for (std::size_t i = 0; i < first_blocks.size(); ++i) {
        present |= present_words(first_blocks[i], c[i]);
        if (present == 255) {
            return 0;
        }
    }
    unsigned missing = 255 ^ present;
    for (unsigned unresolved = missing; unresolved; unresolved &= unresolved - 1) {
        const unsigned code = std::countr_zero(unresolved);
        const bool choose_a = code & 4;
        const bool choose_b = code & 2;
        const bool choose_c = code & 1;
        for (std::size_t i = first_blocks.size(); i < a.size(); ++i) {
            const Word valid = i + 1 == a.size() ? last : ~Word{0};
            const Word signs_a = choose_a ? a[i] : ~a[i];
            const Word signs_b = choose_b ? b[i] : ~b[i];
            const Word signs_c = choose_c ? c[i] : ~c[i];
            if (valid & signs_a & signs_b & signs_c) {
                missing ^= 1u << code;
                break;
            }
        }
    }
    return missing;
}

static bool all_laws_needed(const std::vector<Bits>& one_violation, const Bond& bond) {
    for (const Bits& restored : one_violation) {
        bool restores_word = false;
        for (Word state : restored) {
            unsigned code = 0;
            for (Word carrier : bond.carriers) {
                code = (code << 1) | static_cast<unsigned>(agrees(state, carrier));
            }
            if (bond.missing & (1u << code)) {
                restores_word = true;
                break;
            }
        }
        if (!restores_word) {
            return false;
        }
    }
    return true;
}

extern "C" BondResult* census_bonds(unsigned n, unsigned law_count, const Word* support,
                                     bool require_all_laws) {
    const Word limit = Word{1} << n;
    auto* result = new BondResult();
    Word once = 0;
    Word twice = 0;
    for (unsigned j = 0; j < law_count; ++j) {
        twice |= once & support[j];
        once |= support[j];
    }
    const Word required = require_all_laws ? once ^ twice : 0;
    if (std::popcount(required) > 9) {
        return result;
    }

    Bits states;
    std::vector<Bits> one_violation(law_count);
    for (Word state = 0; state < limit; state += 2) {
        unsigned culprit = law_count;
        bool one_at_most = true;
        for (unsigned j = 0; j < law_count; ++j) {
            if (!agrees(state, support[j])) {
                continue;
            }
            if (!require_all_laws || culprit != law_count) {
                one_at_most = false;
                break;
            }
            culprit = j;
        }
        if (one_at_most && culprit == law_count) {
            states.push_back(state);
        } else if (one_at_most) {
            one_violation[culprit].push_back(state);
        }
    }
    result->counts[0] = states.size();
    if (n < 6 || states.empty()) {
        return result;
    }
    std::mt19937 random(98251);
    // The prefix can only witness presence. Unwitnessed words use the whole table.
    std::shuffle(states.begin(), states.end(), random);
    std::vector<std::vector<Bits>> fixings;
    for (unsigned j = 0; j < law_count; ++j) {
        fixings.push_back(knot_fixings(states, support[j]));
    }

    Bits carriers;
    for (unsigned i = 0; i < n; ++i) {
        for (unsigned j = i + 1; j < n; ++j) {
            Word pair = (Word{1} << i) | (Word{1} << j);
            carriers.push_back(pair);
            for (unsigned k = j + 1; k < n; ++k) {
                carriers.push_back(pair | (Word{1} << k));
            }
        }
    }
    std::sort(carriers.begin(), carriers.end());
    Bits kept;
    std::vector<Bits> values;
    for (Word carrier : carriers) {
        if (std::any_of(support, support + law_count,
                        [&](Word row) { return (carrier & row) == carrier; })) {
            continue;
        }
        Bits yes = packed_agreement(states, carrier);
        if (std::all_of(fixings.begin(), fixings.end(), [&](const auto& knot) {
                return std::any_of(knot.begin(), knot.end(), [&](const auto& fixing) {
                    return varies(yes, fixing);
                });
            })) {
            kept.push_back(carrier);
            values.push_back(std::move(yes));
        }
    }
    const std::size_t n_readings = kept.size();
    result->counts[1] = n_readings;
    if (n_readings < 3) {
        return result;
    }
    const unsigned tail = states.size() % 64;
    const Word last = tail ? (Word{1} << tail) - 1 : ~Word{0};
    const std::size_t witness_blocks = std::min<std::size_t>(8, values.front().size());
    std::vector<Bits> compatible(n_readings, Bits((n_readings + 63) / 64));
    for (unsigned i = 0; i < n_readings; ++i) {
        for (unsigned j = i + 1; j < n_readings; ++j) {
            if ((kept[i] & kept[j]) == 0 && free_pair(values[i], values[j], last)) {
                set_bit(compatible[i], j);
            }
        }
    }

    std::vector<std::array<Word, 4>> first_blocks(witness_blocks);
    for (unsigned i = 0; i < n_readings; ++i) {
        for (unsigned j_block = (i + 1) / 64; j_block < compatible[i].size(); ++j_block) {
            for (Word js = compatible[i][j_block]; js; js &= js - 1) {
                unsigned j = 64 * j_block + std::countr_zero(js);
                const Word carrier_pair = kept[i] | kept[j];
                const Word uncovered = required & ~carrier_pair;
                if (std::popcount(uncovered) > 3) {
                    continue;
                }
                for (std::size_t w = 0; w < witness_blocks; ++w) {
                    Word valid = w + 1 == values[i].size() ? last : ~Word{0};
                    first_blocks[w] = pair_words(values[i][w], values[j][w], valid);
                }
                for (unsigned k_block = (j + 1) / 64; k_block < compatible[j].size(); ++k_block) {
                    Word shared = compatible[i][k_block] & compatible[j][k_block];
                    for (Word ks = shared; ks; ks &= ks - 1) {
                        unsigned k = 64 * k_block + std::countr_zero(ks);
                        if ((uncovered & kept[k]) != uncovered) {
                            continue;
                        }
                        ++result->counts[2];
                        unsigned missing = missing_words(values[i], values[j], values[k], last, first_blocks);
                        if (missing != 0) {
                            Bond bond{{kept[i], kept[j], kept[k]}, missing};
                            if (!require_all_laws || all_laws_needed(one_violation, bond)) {
                                result->bonds.push_back(bond);
                            }
                        }
                    }
                }
            }
        }
    }
    return result;
}

extern "C" const Bond* census_bond_data(const BondResult* result) {
    return result->bonds.data();
}

extern "C" std::size_t census_bond_count(const BondResult* result) {
    return result->bonds.size();
}

extern "C" const Word* census_bond_counts(const BondResult* result) {
    return result->counts.data();
}

extern "C" void census_bond_release(BondResult* result) {
    delete result;
}

static bool disjoint(Word a, Word b) {
    return ((a >> 1) & (b >> 1)) == 0;
}

using Link = std::pair<unsigned, unsigned>;

extern "C" BoxResult* census_boxes(std::size_t count, const Bond* bonds) {
    auto* result = new BoxResult();
    std::vector<std::array<Word, 3>> signed_bonds;
    Bits readings;
    for (std::size_t i = 0; i < count; ++i) {
        if (!std::has_single_bit(bonds[i].missing)) {
            continue;
        }
        unsigned word = std::countr_zero(bonds[i].missing);
        std::array<Word, 3> readings_here;
        for (unsigned p = 0; p < 3; ++p) {
            readings_here[p] = (bonds[i].carriers[p] << 1) | ((word >> (2 - p)) & 1);
        }
        signed_bonds.push_back(readings_here);
        readings.insert(readings.end(), readings_here.begin(), readings_here.end());
    }
    std::sort(readings.begin(), readings.end());
    readings.erase(std::unique(readings.begin(), readings.end()), readings.end());
    auto id = [&](Word reading) {
        return static_cast<unsigned>(std::lower_bound(readings.begin(), readings.end(), reading) - readings.begin());
    };
    std::vector<std::vector<Link>> links(readings.size());
    for (const auto& bond : signed_bonds) {
        std::array<unsigned, 3> r = {id(bond[0]), id(bond[1]), id(bond[2])};
        std::sort(r.begin(), r.end());
        links[r[0]].emplace_back(r[1], r[2]);
        links[r[1]].emplace_back(r[0], r[2]);
        links[r[2]].emplace_back(r[0], r[1]);
    }
    for (auto& incidence : links) {
        std::sort(incidence.begin(), incidence.end());
        incidence.erase(std::unique(incidence.begin(), incidence.end()), incidence.end());
    }

    std::vector<Link> common;
    std::vector<std::vector<unsigned>> neighbours(readings.size());
    std::vector<unsigned> active;
    std::vector<unsigned> common_neighbours;
    for (unsigned a0 = 0; a0 < readings.size(); ++a0) {
        // In each box the least signed reading determines its first pair.
        const auto first = std::lower_bound(links[a0].begin(), links[a0].end(), Link{a0 + 1, 0});
        if (links[a0].end() - first < 4) {
            continue;
        }
        for (unsigned a1 = a0 + 1; a1 < readings.size(); ++a1) {
            if (links[a1].size() < 4 || !disjoint(readings[a0], readings[a1])) {
                continue;
            }
            const auto next = std::lower_bound(links[a1].begin(), links[a1].end(), Link{a0 + 1, 0});
            if (links[a1].end() - next < 4) {
                continue;
            }
            common.clear();
            std::set_intersection(first, links[a0].end(), next, links[a1].end(), std::back_inserter(common));
            // Every common link is disjoint from each of the first two carriers.
            if (common.size() < 4) {
                continue;
            }
            ++result->qualifying_pairs;
            active.clear();
            for (const auto& [b, c] : common) {
                if (neighbours[b].empty()) {
                    active.push_back(b);
                }
                if (neighbours[c].empty()) {
                    active.push_back(c);
                }
                neighbours[b].push_back(c);
                neighbours[c].push_back(b);
            }
            std::sort(active.begin(), active.end());
            for (unsigned r : active) {
                std::sort(neighbours[r].begin(), neighbours[r].end());
            }
            for (std::size_t p = 0; p < active.size(); ++p) {
                unsigned b0 = active[p];
                auto larger = std::upper_bound(neighbours[b0].begin(), neighbours[b0].end(), b0);
                if (neighbours[b0].end() - larger < 2) {
                    continue;
                }
                for (std::size_t q = p + 1; q < active.size(); ++q) {
                    unsigned b1 = active[q];
                    if (neighbours[b1].size() < 2 || !disjoint(readings[b0], readings[b1])) {
                        continue;
                    }
                    common_neighbours.clear();
                    std::set_intersection(larger, neighbours[b0].end(), neighbours[b1].begin(), neighbours[b1].end(),
                                          std::back_inserter(common_neighbours));
                    for (std::size_t i = 0; i < common_neighbours.size(); ++i) {
                        for (std::size_t j = i + 1; j < common_neighbours.size(); ++j) {
                            const unsigned c0 = common_neighbours[i];
                            const unsigned c1 = common_neighbours[j];
                            if (disjoint(readings[c0], readings[c1])) {
                                result->boxes.push_back({readings[a0], readings[a1], readings[b0],
                                                         readings[b1], readings[c0], readings[c1]});
                            }
                        }
                    }
                }
            }
            for (unsigned r : active) {
                neighbours[r].clear();
            }
        }
    }
    return result;
}

extern "C" const Word* census_box_data(const BoxResult* result) {
    return result->boxes.empty() ? nullptr : result->boxes.front().data();
}

extern "C" std::size_t census_box_count(const BoxResult* result) {
    return result->boxes.size();
}

extern "C" Word census_box_pairs(const BoxResult* result) {
    return result->qualifying_pairs;
}

extern "C" void census_box_release(BoxResult* result) {
    delete result;
}
