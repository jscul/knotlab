// Exact bond minima for all pairs in a later literal stage.
#include <algorithm>
#include <bit>
#include <cstdint>
#include <iostream>
#include <vector>

using Shore = uint32_t;
using Cut = __uint128_t;

bool connected(Shore side, const std::vector<Shore>& adj) {
    Shore seen=0, todo=side & -side;
    while (todo) {
        Shore x=todo & -todo;
        todo ^= x;
        seen |= x;
        todo |= adj[std::countr_zero(x)] & side & ~seen;
    }
    return seen==side;
}

int main() {
    int n, edges, old;
    if (!(std::cin>>n>>edges>>old) || n<2 || n>30 || edges>128 || old>edges) return 2;
    std::vector<Shore> adj(n);
    std::vector<Cut> stars(n);
    for (int i=0;i<edges;i++) {
        int u,v;
        if (!(std::cin>>u>>v) || u==v || u<0 || v<0 || u>=n || v>=n) return 2;
        adj[u] |= Shore{1}<<v;
        adj[v] |= Shore{1}<<u;
        stars[u] |= Cut{1}<<i;
        stars[v] |= Cut{1}<<i;
    }
    std::vector<std::vector<int>> table(old,std::vector<int>(old,edges+1));
    Shore shore=0, full=(Shore{1}<<n)-1;
    Cut included = old==128 ? ~Cut{0} : (Cut{1}<<old)-1;
    Cut cut=0;
    for (Shore step=1;step<(Shore{1}<<(n-1));step++) {
        Shore toggled=step & -step;
        shore ^= toggled;
        cut ^= stars[std::countr_zero(toggled)];
        Cut marks=cut & included;
        if (!(marks & (marks-1)) || !connected(shore,adj) || !connected(full^shore,adj)) continue;
        int size=std::popcount(uint64_t(cut)) + std::popcount(uint64_t(cut>>64));
        auto index=[](Cut word) { return uint64_t(word) ? std::countr_zero(uint64_t(word))
                                                        : 64+std::countr_zero(uint64_t(word>>64)); };
        for (;marks;marks&=marks-1) {
            int i=index(marks);
            for (Cut rest=marks & (marks-1);rest;rest&=rest-1) {
                int j=index(rest);
                table[i][j]=std::min(table[i][j],size);
            }
        }
    }
    for (int i=0;i<old;i++) for (int j=i+1;j<old;j++) std::cout<<(table[i][j]==edges+1 ? -1 : table[i][j])<<' ';
    std::cout<<'\n';
}
