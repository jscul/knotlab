// Exact census of three agreement readings. A row is an allowed source state,
// with one representative per pair of globally complementary states.
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <numeric>
#include <random>
#include <string>
#include <vector>

#include "read_pattern.hpp"

using Word = uint64_t;
using Source = uint32_t;
using namespace std;

static bool agrees(Source assignment, Source carrier) {
    Source part = assignment & carrier;
    return part == 0 || part == carrier;
}

static int first_bit(Word value) {
    return __builtin_ctzll(value);
}

struct LawClasses {
    Source mask;
    vector<int> class_sample;
};

struct SourceTable {
    vector<Source> legal, carriers;
    vector<LawClasses> laws;
    vector<vector<Word>> values;
    vector<Word> transposed;
    vector<vector<Word>> disjoint;
    int state_words = 0, carrier_words = 0, ordinary_readings = 0;

    explicit SourceTable(const vector<Source>& masks) {
        Source union_mask = accumulate(masks.begin(), masks.end(), Source{0}, bit_or<Source>());
        // The growth archive names its raw distinctions consecutively starting at zero.
        if (union_mask & (union_mask + 1)) throw runtime_error("gaps in distinction names");
        Source half = (union_mask + 1) / 2;
        for (Source state = 0; state < half; ++state) {
            if (none_of(masks.begin(), masks.end(), [state](Source m) { return agrees(state,m); }))
                legal.push_back(state);
        }
        if (legal.empty()) return;
        mt19937 shuffle_order(782019);
        shuffle(legal.begin(), legal.end(), shuffle_order);
        state_words = (legal.size() + 63) / 64;
        for (Source m : masks) {
            int arity = __builtin_popcount(m);
            vector<int> lookup(1U << arity, -1);
            vector<int> representative;
            for (size_t t = 0; t < legal.size(); ++t) {
                // Record knot assignments up to global complement.
                Source value = legal[t] & m;
                if (value & (m & -m)) value ^= m;
                int key = 0;
                for (Source bits=m; bits; bits&=bits-1)
                    key = key*2 + bool(value & (bits & -bits));
                if (lookup[key] < 0) lookup[key] = t;
                representative.push_back(lookup[key]);
            }
            laws.push_back({m, move(representative)});
        }
        auto consider = [&](Source carrier) {
            bool first = agrees(legal[0], carrier);
            if (none_of(legal.begin(), legal.end(), [=](Source s) { return agrees(s,carrier) != first; })) return;
            ++ordinary_readings;
            for (const auto& law : laws) {
                if ((law.mask & carrier) == carrier) return;
                bool two = false;
                for (size_t t=1; t < legal.size(); ++t) {
                    if (agrees(legal[t], carrier) != agrees(legal[law.class_sample[t]], carrier)) {
                        two = true;
                        break;
                    }
                }
                if (!two) return;
            }
            carriers.push_back(carrier);
        };
        int n = __builtin_popcount(union_mask);
        for (int i=0; i<n; ++i) for (int j=i+1; j<n; ++j) {
            Source pair=(1U<<i) | (1U<<j);
            consider(pair);
            for (int k=j+1; k<n; ++k) consider(pair | (1U<<k));
        }
        size_t ncar = carriers.size();
        carrier_words = (ncar + 63) / 64;
        vector<vector<Word>> raw(n, vector<Word>(state_words));
        for (int t=0; t<64*state_words; ++t) {
            // Padding copies a real state, so it never fabricates an image word.
            Source s = legal[t < (int)legal.size() ? t : 0];
            for (; s; s&=s-1) raw[first_bit(s)][t/64] |= Word{1}<<(t%64);
        }
        values.resize(ncar, vector<Word>(state_words));
        for (size_t c=0; c<ncar; ++c) {
            Source carrier=carriers[c];
            int first = first_bit(carrier);
            for (int w=0; w<state_words; ++w) {
                Word same=~Word{0};
                for (Source others=carrier & (carrier-1); others; others&=others-1)
                    same &= ~(raw[first][w] ^ raw[first_bit(others)][w]);
                values[c][w]=same;
            }
        }
        // Read carrier words at state indices. A short certified witness list per
        // pair normally makes almost every third reading free immediately.
        transposed.assign(size_t(state_words)*64*carrier_words, 0);
        for (int t=0; t<64*state_words; ++t) {
            Word* row=transposed.data()+size_t(t)*carrier_words;
            for (size_t c=0; c<ncar; ++c)
                row[c/64] |= ((values[c][t/64] >> (t%64)) & 1) << (c%64);
        }
        disjoint.assign(ncar, vector<Word>(carrier_words));
        for (size_t i=0; i<ncar; ++i) for (size_t j=i+1; j<ncar; ++j)
            if (!(carriers[i] & carriers[j])) disjoint[i][j/64] |= Word{1}<<(j%64);
    }
};

static bool pairs_open(unsigned missing) {
    for (int omitted = 0; omitted < 3; ++omitted) {
        for (int w=0; w<8; ++w) {
            if ((missing & (1U<<w)) && (missing & (1U<<(w^(1<<omitted))))) return false;
        }
    }
    return true;
}

struct Bond {
    array<Source,3> carriers;
    unsigned missing;
};

static vector<Bond> all_bonds(const SourceTable& st) {
    vector<Bond> result;
    constexpr int drawn = 48;
    int count=st.carriers.size();
    if (count<3) return result;
    vector<unsigned char> missing(count);
    vector<Word> pair_cells(st.state_words);
    vector<Word> eligible(st.carrier_words);
    for (int i=0; i<count; ++i) for (int j=i+1; j<count; ++j) {
        if (st.carriers[i] & st.carriers[j]) continue;
        int first_group = (j+1)/64;
        bool any = false;
        for (int g=first_group; g<st.carrier_words; ++g) {
            eligible[g]=st.disjoint[i][g] & st.disjoint[j][g];
            any |= bool(eligible[g]);
        }
        if (!any) continue;
        fill(missing.begin()+j+1,missing.end(),0);
        bool open = true;
        for (int ab=0; ab<4; ++ab) {
            Word flip_i = (ab & 2) ? 0 : ~Word{0};
            Word flip_j = (ab & 1) ? 0 : ~Word{0};
            array<const Word*,drawn> observed;
            int used = 0;
            int filled=0;
            for (; filled<st.state_words && used<drawn; ++filled) {
                Word v = (st.values[i][filled]^flip_i) & (st.values[j][filled]^flip_j);
                pair_cells[filled]=v;
                for (; v && used<drawn; v&=v-1) {
                    int t=64*filled+first_bit(v);
                    observed[used++]=st.transposed.data()+size_t(t)*st.carrier_words;
                }
            }
            if (!used) { open=false; break; }
            for (int g=first_group; g<st.carrier_words; ++g) {
                Word all_one=eligible[g], all_zero=eligible[g];
                for (int t=0; t<used && (all_one | all_zero); ++t) {
                    Word row=observed[t][g];
                    all_one &= row;
                    all_zero &= ~row;
                }
                if (!(all_one|all_zero)) continue;
                // The list above is a shortcut only. Every still-possible
                // exclusion is decided on the full pair cell.
                for (; filled<st.state_words; ++filled)
                    pair_cells[filled]=(st.values[i][filled]^flip_i) & (st.values[j][filled]^flip_j);
                for (int c_value=0; c_value<2; ++c_value) {
                    Word absent = c_value ? all_zero : all_one;
                    Word flip_k = c_value ? 0 : ~Word{0};
                    for (; absent; absent&=absent-1) {
                        int k = g*64+first_bit(absent);
                        const auto& column=st.values[k];
                        int w=0;
                        for (; w<st.state_words; ++w)
                            if (pair_cells[w] & (column[w]^flip_k)) break;
                        if (w==st.state_words) missing[k] |= 1U<<(ab*2+c_value);
                    }
                }
            }
        }
        if (!open) continue;
        for (int k=j+1; k<count; ++k)
            if (missing[k] && pairs_open(missing[k]))
                result.push_back({{st.carriers[i],st.carriers[j],st.carriers[k]}, missing[k]});
    }
    return result;
}

template<typename Range>
static void json_nums(const Range& values) {
    cout << '[';
    bool first=true;
    for (auto val:values) {
        if (!first) cout << ',';
        first=false;
        cout << val;
    }
    cout << ']';
}

int main(int argc, char** argv) {
    if (argc<3) return 2;
    int export_level = stoi(argv[1]);
    vector<Source> laws;
    for (int i=2; i<argc; ++i) laws.push_back(stoul(argv[i]));
    SourceTable st(laws);
    auto bonds = all_bonds(st);
    vector<four_read::Clause> clauses;
    unsigned pairs_only=0;
    array<unsigned,8> signs{};
    for (const auto& b : bonds) {
        if (__builtin_popcount(b.missing)!=1) continue;
        unsigned w=first_bit(b.missing);
        four_read::Clause cl{};
        bool just_pairs=true;
        for (int p=0; p<3; ++p) {
            cl[p] = (four_read::Literal(b.carriers[p])<<1) | ((w>>(2-p)) & 1);
            just_pairs &= __builtin_popcount(b.carriers[p]) == 2;
        }
        ++signs[w];
        pairs_only+=just_pairs;
        sort(cl.begin(),cl.end());
        clauses.push_back(cl);
    }
    auto families = four_read::patterns(clauses);
    cout << "{\"allowed\":" << (2*st.legal.size()) << ",\"open_readings\":" << st.ordinary_readings
         << ",\"unread_readings\":" << st.carriers.size() << ",\"bonds\":" << bonds.size()
         << ",\"single_word_bonds\":" << clauses.size() << ",\"single_word_bonds_on_pairs\":" << pairs_only
         << ",\"single_word_bits_in_carrier_order\":";
    json_nums(signs);
    cout << ",\"patterns\":[";
    for (size_t f=0; f<families.size(); ++f) {
        if (f) cout << ',';
        const auto& cl=families[f];
        cout << "{\"pairs\":[";
        auto p=four_read::pairs_of(cl);
        for (int i=0; i<3; ++i) { if(i) cout << ','; json_nums(p[i]); }
        cout << "],\"clauses\":[";
        for (int i=0; i<4; ++i) { if(i) cout << ','; json_nums(cl[i]); }
        cout << "]}";
    }
    cout << ']';
    if (export_level) {
        cout << ",\"clauses\":[";
        for (size_t i=0;i<clauses.size();++i) { if (i) cout << ','; json_nums(clauses[i]); }
        cout << ']';
    }
    if (export_level>1) {
        cout << ",\"all_bonds\":[";
        for (size_t i=0;i<bonds.size();++i) {
            if(i) cout << ',';
            const auto& b=bonds[i];
            cout << '[' << b.carriers[0] << ',' << b.carriers[1] << ',' << b.carriers[2] << ',' << b.missing << ']';
        }
        cout << ']';
    }
    cout << "}\n";
}
