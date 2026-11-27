#include <algorithm>
#include <array>
#include <cstdint>
#include <set>
#include <unordered_map>
#include <utility>
#include <vector>

using Code = std::uint32_t;
using PairKey = std::uint64_t;
using Triple = std::array<Code, 3>;
using Cover = std::array<Code, 7>;

struct Result {
    std::vector<Cover> covers;
    std::uint64_t five = 0;
};

static PairKey key(Code x, Code y) {
    if (x > y) std::swap(x, y);
    return (PairKey(x) << 32) | y;
}

extern "C" Result* alternative_find(const Code* clauses, std::size_t size) {
    auto* result = new Result();
    // The low bit records the excluded value of the agreement. All other
    // bits are its raw carrier; comparisons below must ignore the sign.
    const auto carrier = [](Code x) { return x >> 1; };
    std::unordered_map<PairKey, std::vector<Code>> following;
    std::vector<Triple> records;
    for (std::size_t m = 0; m < size; ++m) {
        Triple clause{clauses[3*m], clauses[3*m+1], clauses[3*m+2]};
        std::sort(clause.begin(), clause.end());
        records.push_back(clause);
        for (int i = 0; i < 3; ++i)
            following[key(clause[(i+1)%3], clause[(i+2)%3])].push_back(clause[i]);
    }

    // In a 3+1 assignment three clauses use the same A reading. Their
    // common row and column select a unique clause on (A,B,C).
    for (const Triple& clause : records) for (int i = 0; i < 3; ++i) {
        Code a = clause[i], b = clause[(i+1)%3], c = clause[(i+2)%3];
        if (b > c) std::swap(b,c);
        Code used = carrier(a) | carrier(b) | carrier(c);
        for (Code b1 : following.at(key(a,c))) {
            if (used & carrier(b1)) continue;
            Code used_four = used | carrier(b1);
            for (Code c1 : following.at(key(a,b))) {
                if (used_four & carrier(c1)) continue;
                auto finish = following.find(key(b1,c1));
                if (finish == following.end()) continue;
                Code used_five = used_four | carrier(c1);
                for (Code a1 : finish->second) {
                    if (a1 == a && b < b1 && c < c1) ++result->five;
                    if (!(used_five & carrier(a1)))
                        result->covers.push_back({a,a1,b,b1,c,c1,8});
                }
            }
        }
    }

    // When the A index depends only on B, the two C readings accompany
    // both (A0,B0) and (A1,B1). Each pair has two choices of its A member.
    using Pair = std::array<Code, 2>;
    std::unordered_map<PairKey, std::vector<Pair>> shared;
    for (const auto& [p, next] : following) {
        Pair ab{static_cast<Code>(p >> 32), static_cast<Code>(p)};
        for (std::size_t i = 0; i < next.size(); ++i)
            for (std::size_t j = i+1; j < next.size(); ++j) {
                if (carrier(next[i]) & carrier(next[j])) continue;
                shared[key(next[i],next[j])].push_back(ab);
            }
    }
    for (const auto& [cs, partners] : shared) {
        Code c0 = cs >> 32, c1 = static_cast<Code>(cs);
        for (std::size_t i = 0; i < partners.size(); ++i) {
            const Pair& first = partners[i];
            Code used = carrier(first[0]) | carrier(first[1]);
            for (std::size_t j = i+1; j < partners.size(); ++j) {
                const Pair& second = partners[j];
                if (used & (carrier(second[0]) | carrier(second[1]))) continue;
                for (int x = 0; x < 2; ++x) for (int y = 0; y < 2; ++y)
                    result->covers.push_back({first[x],second[y],first[1-x],second[1-y],c0,c1,12});
            }
        }
    }
    return result;
}

extern "C" const Cover* alternative_data(Result* r) { return r->covers.data(); }
extern "C" std::size_t alternative_size(Result* r) { return r->covers.size(); }
extern "C" std::uint64_t alternative_five(Result* r) { return r->five; }
extern "C" void alternative_release(Result* r) { delete r; }
