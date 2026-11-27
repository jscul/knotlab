// Full signed-clause and box search on the supplied finite not-all-equal system.
#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <random>
#include <unordered_map>
#include <vector>
using namespace std;
using Word = uint64_t;
using Triple = array<int, 3>;

struct Reading {
    unsigned mask;
    vector<Word> ones;
};

unsigned normalized(unsigned state, unsigned places) {
    const auto first = places & -places;
    return ((state & first) ? ~state : state) & places;
}

bool unread(const vector<unsigned>& states, const vector<unsigned>& laws, unsigned carrier) {
    for (unsigned law : laws) {
        if ((carrier & law) == carrier) return false;
        vector<unsigned> patterns;
        for (unsigned fix = law; fix; fix = (fix - 1) & law)
            if (fix != law && !(fix & (law & -law))) patterns.push_back(fix);
        vector<int> seen(patterns.size(), -1);
        bool mixed = false;
        for (unsigned state : states) {
            unsigned fix = normalized(state, law);
            auto p = find(patterns.begin(), patterns.end(), fix);
            int& old = seen[p - patterns.begin()];
            int bit = normalized(state, carrier) == 0;
            if (old >= 0 && old != bit) { mixed = true; break; }
            old = bit;
        }
        if (!mixed) return false;
    }
    return true;
}

void scan(unsigned n, const vector<unsigned>& laws) {
    vector<unsigned> states;
    for (unsigned state = 0; state < (1u << n); state += 2) {
        if (all_of(laws.begin(), laws.end(), [&](unsigned k) {return normalized(state, k) != 0;}))
            states.push_back(state);
    }
    // Prefixes reject impossible missing-word candidates early. Every retained
    // missing word is tested against every state, independent of the ordering.
    mt19937 rng(775061);
    shuffle(states.begin(), states.end(), rng);
    const size_t blocks = (states.size()+63) / 64;
    vector<Reading> reads;
    for (unsigned carrier = 1; carrier < (1u << n); ++carrier) {
        const int size = __builtin_popcount(carrier);
        if (size < 2 || size > 3 || !unread(states, laws, carrier)) continue;
        Reading r{carrier, vector<Word>(blocks)};
        for (size_t j = 0; j < states.size(); ++j)
            if (!normalized(states[j], carrier)) r.ones[j / 64] |= Word{1} << (j%64);
        reads.push_back(move(r));
    }
    vector<Triple> clauses;
    long long candidates = 0;
    for (int a=0; a<(int)reads.size(); a++) {
        for (int b=a+1; b<(int)reads.size(); b++) {
            if (reads[a].mask & reads[b].mask) continue;
            const auto ab = reads[a].mask | reads[b].mask;
            for (int c=b+1; c<(int)reads.size(); c++) {
                if ((ab & reads[c].mask) || __builtin_popcount(ab | reads[c].mask) + 6 > (int)n) continue;
                candidates++;
                unsigned present = 0;
                for (size_t j=0; j<blocks && present!=255; j++) {
                    const auto x=reads[a].ones[j], y=reads[b].ones[j], z=reads[c].ones[j];
                    const auto full = (j+1 == blocks && states.size()%64) ?
                        (Word{1} << (states.size()%64)) - 1 : ~Word{0};
                    const Word parts[] = {~x & ~y & full, ~x & y & full,
                                          x & ~y, x & y};
                    for (int k=0; k<4; k++) {
                        if (parts[k] & ~z) present |= 1u << (2*k);
                        if (parts[k] & z) present |= 1u << (2*k+1);
                    }
                }
                if (__builtin_popcount(present)!=7) continue;
                int missing = __builtin_ctz(255u ^ present);
                clauses.push_back({2*a+((missing>>2)&1),2*b+((missing>>1)&1),2*c+(missing&1)});
            }
        }
    }
    unsigned keys = 2 * reads.size();
    auto pair_key = [=](int a, int b) {return min(a,b)*keys+max(a,b);};
    unordered_map<unsigned,vector<int>> thirds;
    for (auto [a,b,c] : clauses) {
        thirds[pair_key(a,b)].push_back(c);
        thirds[pair_key(a,c)].push_back(b);
        thirds[pair_key(b,c)].push_back(a);
    }
    for (auto& item : thirds) sort(item.second.begin(), item.second.end());
    auto law = [&](int a, int b, int c) {
        auto at = thirds.find(pair_key(a,b));
        return at!=thirds.end() && binary_search(at->second.begin(),at->second.end(),c);
    };
    auto mask = [&](int key) {return reads[key/2].mask;};
    long long boxes = 0;
    array<int,6> witness{};
    for (auto [a,b,c] : clauses) {
        const auto abc = mask(a) | mask(b) | mask(c);
        for (int x : thirds.at(pair_key(b,c))) {
            if (x <= a || (abc & mask(x))) continue;
            for (int y : thirds.at(pair_key(a,c))) {
                if (y <= b || ((abc | mask(x)) & mask(y)) || !law(x,y,c)) continue;
                for (int z : thirds.at(pair_key(a,b))) {
                    if (z <= c || ((abc | mask(x) | mask(y)) & mask(z))) continue;
                    if (law(x,b,z) && law(a,y,z) && law(x,y,z)) {
                        if (!boxes) witness = {a,x,b,y,c,z};
                        boxes++;
                    }
                }
            }
        }
    }
    cout << 2*states.size() << ' ' << reads.size() << ' ' << candidates << ' '
         << clauses.size() << ' ' << boxes;
    if (boxes) for (int i : witness) cout << ' ' << mask(i) << ' ' << (i%2);
    cout << endl;
}

int main() {
    unsigned n,h;
    while (cin >> n >> h) {
        vector<unsigned> laws(h);
        for (auto& row:laws) cin >> row;
        scan(n,laws);
    }
}
