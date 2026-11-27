#include <algorithm>
#include <array>
#include <bit>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
using Word = std::uint64_t;
using Mask = std::uint32_t;
using Count = std::uint64_t;
using Trip = std::array<int, 3>;
using Box = std::array<std::array<int, 2>, 3>;

struct AssignmentTable {
    std::vector<Mask> states;
    int blocks;
    Word last_block;
    std::vector<std::vector<Word>> places;
};

struct Reading {
    Mask carrier;
    std::vector<Word> agreement;
    bool every_place;
};

struct Cell {
    int block;
    Word states;
};

struct BondCensus {
    Count candidates = 0;
    Count unrestricted = 0;
    Count strict = 0;
    std::array<Count, 9> missing_count{};
    std::array<Count, 8> single_words{};
    std::vector<Trip> signed_bonds;
};

struct BoxCensus {
    Count four_shared_triples = 0;
    Count almost_complete = 0;
    Count reads_every_loose = 0;
    Count strict = 0;
    std::array<Count, 19> used_distinctions{};
    std::vector<Box> boxes;
};

AssignmentTable assignments(int width, const std::vector<Mask>& knots) {
    AssignmentTable result;
    // Complementing every distinction preserves the source laws and every reading.
    const Mask half = Mask{1} << (width - 1);
    for (Mask state = 0; state < half; ++state) {
        const auto permitted = [state](Mask law) {
            const auto projection = state & law;
            return projection != 0 && projection != law;
        };
        if (std::all_of(knots.begin(), knots.end(), permitted)) {
            result.states.push_back(state);
        }
    }
    std::mt19937 order(1671);
    std::shuffle(result.states.begin(), result.states.end(), order);
    result.blocks = (result.states.size() + 63) / 64;
    const int tail = result.states.size() % 64;
    result.last_block = tail == 0 ? ~Word{0} : (Word{1} << tail) - 1;
    result.places.assign(width, std::vector<Word>(result.blocks));
    for (std::size_t i = 0; i < result.states.size(); ++i) {
        auto remaining = result.states[i];
        while (remaining != 0) {
            const int place = std::countr_zero(remaining);
            result.places[place][i / 64] |= Word{1} << (i % 64);
            remaining &= remaining - 1;
        }
    }
    return result;
}

std::vector<int> support(Mask mask) {
    std::vector<int> places;
    while (mask != 0) {
        places.push_back(std::countr_zero(mask));
        mask &= mask - 1;
    }
    return places;
}

std::vector<std::vector<Cell>> knot_cells(const AssignmentTable& table, Mask knot) {
    const auto places = support(knot);
    std::vector<std::vector<Cell>> result(3);
    for (int b = 0; b < table.blocks; ++b) {
        const Word x = table.places[places[0]][b] ^ table.places[places[1]][b];
        const Word y = table.places[places[0]][b] ^ table.places[places[2]][b];
        const std::array<Word, 3> odd{x & y, x & ~y, y & ~x};
        for (int o = 0; o < 3; ++o) {
            if (odd[o] != 0) {
                result[o].push_back({b, odd[o]});
            }
        }
    }
    return result;
}

bool mixed(const std::vector<Word>& reading, const std::vector<Cell>& cell) {
    Word has_zero = 0;
    Word has_one = 0;
    for (const auto [block, states] : cell) {
        has_zero |= states & ~reading[block];
        has_one |= states & reading[block];
        if (has_zero && has_one) {
            return true;
        }
    }
    return false;
}

std::vector<Reading> readings(const AssignmentTable& table, const std::vector<Mask>& knots) {
    std::vector<std::vector<std::vector<Cell>>> local;
    for (Mask k : knots) {
        local.push_back(knot_cells(table, k));
    }
    std::vector<Reading> result;
    const int width = table.places.size();
    for (int a = 0; a < width; ++a) {
        for (int b = a + 1; b < width; ++b) {
            for (int c = b; c < width; ++c) {
                const bool pair = b == c;
                const Mask carrier = (Mask{1} << a) | (Mask{1} << b) | (Mask{1} << c);
                std::vector<Word> values(table.blocks);
                Word any = 0;
                Word nonagree = 0;
                std::array<Word, 3> odd{};
                for (int block = 0; block < table.blocks; ++block) {
                    const Word mask = block + 1 == table.blocks ? table.last_block : ~Word{0};
                    const Word x = table.places[a][block] ^ table.places[b][block];
                    const Word y = table.places[a][block] ^ table.places[c][block];
                    values[block] = mask ^ (x | y);
                    any |= values[block];
                    nonagree |= x | y;
                    odd[0] |= x & y;
                    odd[1] |= x & ~y;
                    odd[2] |= y & ~x;
                }
                if (!any || !nonagree) {
                    continue;
                }
                const auto determines = [&values](const auto& cells) {
                    return std::none_of(cells.begin(), cells.end(), [&values](const auto& cell) {
                        return mixed(values, cell);
                    });
                };
                if (std::any_of(local.begin(), local.end(), determines)) {
                    continue;
                }
                const bool every_place = pair || (odd[0] && odd[1] && odd[2]);
                result.push_back({carrier, std::move(values), every_place});
            }
        }
    }
    return result;
}

std::vector<std::vector<Word>> free_disjoint_pairs(const AssignmentTable& table,
                                                  const std::vector<Reading>& eligible) {
    const int n = eligible.size();
    std::vector<std::vector<Word>> result(n, std::vector<Word>((n + 63) / 64));
    for (int a = 0; a < n; ++a) {
        for (int b = a + 1; b < n; ++b) {
            if ((eligible[a].carrier & eligible[b].carrier) != 0) {
                continue;
            }
            std::array<Word, 4> words{};
            for (int block = 0; block < table.blocks; ++block) {
                const Word mask = block + 1 == table.blocks ? table.last_block : ~Word{0};
                const Word x = eligible[a].agreement[block], y = eligible[b].agreement[block];
                words[0] |= mask & ~(x | y);
                words[1] |= ~x & y;
                words[2] |= x & ~y;
                words[3] |= x & y;
                if (words[0] && words[1] && words[2] && words[3]) {
                    result[a][b / 64] |= Word{1} << (b % 64);
                    break;
                }
            }
        }
    }
    return result;
}

void pair_cells(const AssignmentTable& table, const Reading& a, const Reading& b,
                std::array<std::vector<Cell>, 4>& result) {
    for (auto& cell : result) {
        cell.clear();
    }
    for (int block = 0; block < table.blocks; ++block) {
        const Word mask = block + 1 == table.blocks ? table.last_block : ~Word{0};
        const Word x = a.agreement[block], y = b.agreement[block];
        const std::array<Word, 4> chunk{mask & ~(x | y), ~x & y, x & ~y, x & y};
        for (int w = 0; w < 4; ++w) {
            if (chunk[w]) {
                result[w].push_back({block, chunk[w]});
            }
        }
    }
}

unsigned missing_words(const Reading& c, const std::array<std::vector<Cell>, 4>& cells) {
    unsigned missing = 0;
    for (int w = 0; w < 4; ++w) {
        Word has_zero = 0, has_one = 0;
        for (const auto [block, states] : cells[w]) {
            const Word yes = c.agreement[block];
            has_zero |= states & ~yes;
            has_one |= states & yes;
            if (has_zero && has_one) {
                break;
            }
        }
        missing |= unsigned(!has_zero) << (2 * w);
        missing |= unsigned(!has_one) << (2 * w + 1);
    }
    return missing;
}

BondCensus count_bonds(const AssignmentTable& table, const std::vector<Reading>& eligible) {
    BondCensus census;
    const int n = eligible.size(), reading_blocks = (n + 63) / 64;
    const auto links = free_disjoint_pairs(table, eligible);
    std::array<std::vector<Cell>, 4> fibers;
    for (auto& cell : fibers) {
        cell.reserve(table.blocks);
    }
    for (int a = 0; a < n; ++a) {
        for (int b = a + 1; b < n; ++b) {
            if ((links[a][b / 64] & (Word{1} << (b % 64))) == 0) {
                continue;
            }
            bool ready = false;
            for (int block = b / 64; block < reading_blocks; ++block) {
                Word thirds = links[a][block] & links[b][block];
                if (!thirds) {
                    continue;
                }
                if (!ready) {
                    pair_cells(table, eligible[a], eligible[b], fibers);
                    ready = true;
                }
                while (thirds != 0) {
                    const int c = 64 * block + std::countr_zero(thirds);
                    thirds &= thirds - 1;
                    ++census.candidates;
                    const unsigned missing = missing_words(eligible[c], fibers);
                    if (!missing) {
                        continue;
                    }
                    const int number_missing = std::popcount(missing);
                    ++census.unrestricted;
                    ++census.missing_count[number_missing];
                    census.strict += eligible[a].every_place
                        && eligible[b].every_place && eligible[c].every_place;
                    if (number_missing == 1) {
                        const int word = std::countr_zero(missing);
                        ++census.single_words[word];
                        census.signed_bonds.push_back({
                            2 * a + (word >> 2),
                            2 * b + ((word >> 1) & 1),
                            2 * c + (word & 1),
                        });
                    }
                }
            }
        }
    }
    return census;
}

BoxCensus count_boxes(const std::vector<Reading>& readings, const std::vector<Trip>& signs,
                      Mask loose) {
    BoxCensus census;
    const int n = 2 * readings.size();
    const auto mask = [&readings](int signed_reading) { return readings[signed_reading / 2].carrier; };
    // In each signed triple, record the third reading that extends each pair.
    const auto slot = [](int i, int j) { return std::size_t(j) * (j - 1) / 2 + i; };
    std::vector<std::vector<int>> extensions(std::size_t(n) * (n - 1) / 2);
    std::vector<std::vector<std::array<int, 2>>> least_links(n);
    for (const auto [a, b, c] : signs) {
        extensions[slot(a, b)].push_back(c);
        extensions[slot(a, c)].push_back(b);
        extensions[slot(b, c)].push_back(a);
        least_links[a].push_back({b, c});
    }
    std::vector<std::vector<std::array<int, 2>>> common(n);
    std::vector<std::vector<int>> neighbors(n);
    std::vector<int> active;
    std::vector<int> candidates;
    for (int a0 = 0; a0 < n; ++a0) {
        for (const auto [q, r] : least_links[a0]) {
            for (const int a1 : extensions[slot(q, r)]) {
                if (a1 > a0 && !(mask(a0) & mask(a1))) {
                    common[a1].push_back({q, r});
                }
            }
        }
        for (int a1 = a0 + 1; a1 < n; ++a1) {
            auto& links = common[a1];
            if (links.size() >= 4) {
                ++census.four_shared_triples;
                active.clear();
                for (const auto [q, r] : links) {
                    if (neighbors[q].empty()) {
                        active.push_back(q);
                    }
                    if (neighbors[r].empty()) {
                        active.push_back(r);
                    }
                    neighbors[q].push_back(r);
                    neighbors[r].push_back(q);
                }
                std::sort(active.begin(), active.end());
                for (const int q : active) {
                    std::sort(neighbors[q].begin(), neighbors[q].end());
                }
                for (auto b = active.begin(); b != active.end(); ++b) {
                    const int b0 = *b;
                    if (neighbors[b0].size() < 2) {
                        continue;
                    }
                    for (auto b_next = b + 1; b_next != active.end(); ++b_next) {
                        const int b1 = *b_next;
                        if (neighbors[b1].size() < 2 || (mask(b0) & mask(b1))) {
                            continue;
                        }
                        candidates.clear();
                        std::set_intersection(
                            std::upper_bound(neighbors[b0].begin(), neighbors[b0].end(), b0),
                            neighbors[b0].end(),
                            std::upper_bound(neighbors[b1].begin(), neighbors[b1].end(), b0),
                            neighbors[b1].end(), std::back_inserter(candidates)
                        );
                        if (candidates.size() >= 2) {
                            ++census.almost_complete;
                        }
                        for (auto c = candidates.begin(); c != candidates.end(); ++c) {
                            for (auto c_next = c + 1; c_next != candidates.end(); ++c_next) {
                                const int c0 = *c, c1 = *c_next;
                                if ((mask(c0) & mask(c1)) != 0) {
                                    continue;
                                }
                                const Box box{{{a0, a1}, {b0, b1}, {c0, c1}}};
                                census.boxes.push_back(box);
                                Mask used = 0;
                                bool strict = true;
                                for (const auto& pair : box) {
                                    for (int x : pair) {
                                        used |= mask(x);
                                        strict &= readings[x / 2].every_place;
                                    }
                                }
                                census.reads_every_loose += (used & loose) == loose;
                                census.strict += strict;
                                ++census.used_distinctions[std::popcount(used)];
                            }
                        }
                    }
                }
                for (const int q : active) {
                    neighbors[q].clear();
                }
            }
            links.clear();
        }
    }
    return census;
}

// A planted signed product must survive sign permutations and fail all eight deletions.
void join_control() {
    std::vector<Reading> readings;
    for (int i = 0; i < 6; ++i) {
        readings.push_back({Mask{3} << (2 * i), {}, true});
    }
    const Box expected{{{0, 3}, {5, 6}, {8, 11}}};
    std::vector<Trip> clauses;
    for (int a : expected[0]) {
        for (int b : expected[1]) {
            for (int c : expected[2]) {
                clauses.push_back({a, b, c});
            }
        }
    }
    if (count_boxes(readings, clauses, 0).boxes != std::vector<Box>{expected}) {
        throw std::runtime_error("signed product control did not give its one box");
    }
    for (unsigned i = 0; i < clauses.size(); ++i) {
        auto drop = clauses;
        drop.erase(drop.begin() + i);
        if (!count_boxes(readings, drop, 0).boxes.empty()) {
            throw std::runtime_error("signed product control survived a deletion");
        }
    }
    readings.back().carrier = readings[4].carrier;
    if (!count_boxes(readings, clauses, 0).boxes.empty()) {
        throw std::runtime_error("the planted box survived a carrier overlap");
    }
}

template <typename T>
void print_ints(const T& values) {
    std::cout << '[';
    bool comma = false;
    for (auto value : values) {
        if (comma) {
            std::cout << ',';
        }
        std::cout << value;
        comma = true;
    }
    std::cout << ']';
}

void print_result(int width, const std::vector<Mask>& knots) {
    const auto start = std::chrono::steady_clock::now();
    Mask loose = 0;
    for (int i = 0; i < width; ++i) {
        const Mask place = Mask{1} << i;
        if (std::count_if(knots.begin(), knots.end(), [place](Mask k) { return k & place; }) == 1) {
            loose |= place;
        }
    }
    const auto table = assignments(width, knots);
    const auto eligible = readings(table, knots);
    const auto bonds = count_bonds(table, eligible);
    const auto boxes = count_boxes(eligible, bonds.signed_bonds, loose);
    const double seconds = std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count();
    std::cout << "{\"allowed_states\":" << 2 * table.states.size()
              << ",\"eligible_readings\":" << eligible.size()
              << ",\"triple_candidates\":" << bonds.candidates
              << ",\"bonds\":" << bonds.unrestricted
              << ",\"bonds_with_every_carrier_place_used\":" << bonds.strict
              << ",\"bonds_by_missing_word_count\":";
    print_ints(bonds.missing_count);
    std::cout << ",\"single_missing_bonds_by_word\":";
    print_ints(bonds.single_words);
    std::cout << ",\"signed_first_pairs_with_four_shared_links\":" << boxes.four_shared_triples
              << ",\"signed_two_pairs_with_two_common_readings\":" << boxes.almost_complete
              << ",\"boxes_reading_every_loose_distinction\":" << boxes.reads_every_loose
              << ",\"boxes_with_every_carrier_place_used\":" << boxes.strict
              << ",\"boxes_by_carrier_distinction_count\":";
    print_ints(boxes.used_distinctions);
    std::cout << ",\"loose_distinctions\":";
    print_ints(support(loose));
    std::cout << ",\"boxes\":[";
    bool box_comma = false;
    for (const auto& box : boxes.boxes) {
        if (box_comma) {
            std::cout << ',';
        }
        std::cout << '[';
        bool pair_comma = false;
        for (const auto& pair : box) {
            if (pair_comma) {
                std::cout << ',';
            }
            std::cout << '[';
            for (int i = 0; i < 2; ++i) {
                if (i) {
                    std::cout << ',';
                }
                const int x = pair[i];
                std::cout << '[';
                print_ints(support(eligible[x / 2].carrier));
                std::cout << ',' << x % 2 << ']';
            }
            std::cout << ']';
            pair_comma = true;
        }
        std::cout << ']';
        box_comma = true;
    }
    std::cout << "],\"seconds\":" << seconds << "}\n" << std::flush;
}
}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc == 2 && std::string(argv[1]) == "--join-control") {
            join_control();
            std::cout << "{\"planted_signed_box\":1,\"single_deletions_excluding_box\":8,"
                         "\"overlapping_carrier_excluding_box\":1}\n";
            return 0;
        }
        if (argc != 1) {
            throw std::runtime_error("expected zero arguments or --join-control");
        }
        int width, n_knots;
        while (std::cin >> width >> n_knots) {
            if (width < 3 || width > 22 || n_knots < 1) {
                throw std::runtime_error("expected 3 to 22 distinctions and at least one knot");
            }
            std::vector<Mask> knots(n_knots);
            for (auto& k : knots) {
                if (!(std::cin >> k) || std::popcount(k) != 3 || k >= (Mask{1} << width)) {
                    throw std::runtime_error("expected a three-distinction mask for each knot");
                }
            }
            print_result(width, knots);
        }
        if (!std::cin.eof()) {
            throw std::runtime_error("expected width, number of knots, and knot masks");
        }
    } catch (const std::exception& problem) {
        std::cerr << problem.what() << '\n';
        return 1;
    }
}
