// Screen transpositions on reached stages from starts with repeated meetings.
#define main previous_reached_driver
#include "../../GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds/reach_bound.cpp"
#undef main

namespace swaps {
using Count = unsigned long long;
struct Totals {
    Count starts = 0, stages = 0, candidates = 0, pair_only = 0, pair_flip = 0;
    Count triples = 0, both = 0;
    int max_age = 0;
};

struct Wired {
    Adj graph;
    std::vector<Mask> stars;
    explicit Wired(const Rows& rows, const Incidence& inc)
        : graph(inc.ordinary), stars(rows.size() + bool(inc.live), 0) {
        require(inc.own.size() < 63, "distinction width exceeds bit packing");
        if (inc.live) graph.emplace_back(inc.live);
        for (int u = 0; u < int(rows.size()); ++u) {
            for (int x : rows[u]) stars[u] |= bit(x);
            if (!inc.loose[u].empty()) {
                graph[u] |= bit(rows.size());
                for (int x : inc.loose[u]) stars.back() |= bit(x);
            }
        }
    }
    bool genuine() const {
        Mask all = bit(graph.size()) - 1;
        for (int u = 0; u < int(graph.size()); ++u) {
            if (!connected(graph, all ^ bit(u))) return false;
        }
        return true;
    }
    std::vector<Mask> bonds() const {
        const Mask all = bit(graph.size()) - 1;
        std::vector<Mask> boundary(bit(graph.size() - 1));
        std::vector<Mask> result;
        for (Mask side = 1; side < boundary.size(); ++side) {
            Mask cut = boundary[side & (side - 1)] ^ stars[std::countr_zero(side)];
            boundary[side] = cut;
            if (connected(graph,side) && connected(graph,all ^ side)) result.push_back(cut);
        }
        return result;
    }
};

class Scan {
    int width_bound, current_bound, current_width;
    std::vector<std::pair<int,int>> edges;
    std::vector<int> degree, multiplicities, loose;
    std::map<std::pair<int,int>,Totals> totals;

    void stage(const Rows& source, const Rows& current, int age, Totals& score) {
        Incidence inc(current);
        const int w = inc.own.size();
        Wired graph(current,inc);
        require(graph.genuine(), "reached inadmissible stage");
        ++score.stages;
        score.max_age = std::max(score.max_age, age);
        Mask movable = bit(w)-1;
        for (Mask live = inc.live; live;) movable &= ~graph.stars[take(live)];
        if (std::popcount(movable) < 2) return;

        auto bonds = graph.bonds();
        std::vector<std::vector<int>> pair(w,std::vector<int>(w,Inf));
        for (Mask b : bonds) {
            const int size = std::popcount(b);
            for (Mask left=b; left;) {
                int i=take(left);
                for (Mask right=left; right;) {
                    int j=take(right);
                    pair[j][i]=pair[i][j]=std::min(pair[i][j],size);
                }
            }
        }
        std::map<int,std::vector<int>> link;
        auto triple_link = [&](int x) -> const std::vector<int>& {
            auto [it, fresh] = link.try_emplace(x,w*w,Inf);
            auto& value=it->second;
            if (fresh) for (Mask b : bonds) if (b & bit(x)) {
                const int size=std::popcount(b);
                for (Mask left=b ^ bit(x); left;) {
                    int i=take(left);
                    for (Mask right=left; right;) {
                        int j=take(right);
                        value[i*w+j]=std::min(value[i*w+j],size);
                    }
                }
            }
            return value;
        };

        for (Mask left=movable; left;) {
            int x=take(left);
            for (Mask right=left; right;) {
                int y=take(right);
                // If the two columns agree, or their two-site support is itself an
                // equation, the transposition already preserves every equation.
                if (inc.own[x]==inc.own[y] || pair[x][y]==2) continue;
                ++score.candidates;
                bool same=true, flip=true;
                for (int z=0; z<w; ++z) if (z!=x && z!=y) {
                    if (pair[x][z]!=pair[y][z]) { same=false; break; }
                    if ((inc.own[x]==inc.own[z])!=(inc.own[y]==inc.own[z])) flip=false;
                }
                if (!same) continue;
                ++score.pair_only;
                score.pair_flip+=flip;
                auto& a=triple_link(x); auto& b=triple_link(y);
                for (int z=0; z<w && same; ++z) if (z!=x && z!=y)
                    for (int t=z+1; t<w; ++t) if (t!=x && t!=y && a[z*w+t]!=b[z*w+t]) {
                        same=false; break;
                    }
                if (same) {
                    ++score.triples;
                    score.both+=flip;
                    std::cout << "H " << source.size() << ' ' << age << ' ' << x << ' ' << y << ' ' << flip;
                    for (const auto& row : source) {
                        std::cout << ' ' << row.size();
                        for (int item : row) std::cout << ' ' << item;
                    }
                    std::cout << '\n';
                }
            }
        }
    }

    void replay(int width) {
        Rows rows(degree.size());
        int x=0;
        for (int i=0; i<int(edges.size()); ++i) {
            auto [u,v]=edges[i];
            for (int j=0; j<multiplicities[i]; ++j,++x) {
                rows[u].push_back(x); rows[v].push_back(x);
            }
        }
        for (int u=0; u<int(rows.size()); ++u)
            for (int k=0; k<loose[u]; ++k) rows[u].push_back(x++);
        require(width==x,"starting width");
        Incidence origin(rows);
        if (!Wired(rows,origin).genuine()) return;
        auto& score=totals[{int(rows.size()),width}];
        ++score.starts;
        Rows here=rows;
        for (int age=1;;++age) {
            Incidence before(here);
            Rows next=grow(here,before,Rule(before.ordinary).groups(before.live));
            if (next.empty() || int(next.size())>current_bound) break;
            Incidence at(next);
            if (int(at.own.size())>current_width) break;
            // A reached position must admit a further complete round to test its table.
            if (grow(next,at,Rule(at.ordinary).groups(at.live)).empty()) break;
            stage(rows,next,age,score);
            here=std::move(next);
        }
    }
    void loose_assignments(int u,int width) {
        if (u==int(degree.size())) { replay(width); return; }
        int minimum=std::max(0,3-degree[u]);
        for (int l=minimum; l+width<=width_bound; ++l) {
            loose[u]=l; loose_assignments(u+1,width+l);
        }
    }
    void shared_assignments(int i,int width,bool doubled) {
        if (width+int(edges.size())-i>width_bound) return;
        if (i==int(edges.size())) {
            if (doubled) loose_assignments(0,width);
            return;
        }
        auto [u,v]=edges[i];
        for (int m=1; m<=2; ++m) {
            multiplicities[i]=m; degree[u]+=m; degree[v]+=m;
            shared_assignments(i+1,width+m,doubled || m==2);
            degree[u]-=m; degree[v]-=m;
        }
    }
public:
    Scan(int width,int cap,int width_cap):width_bound(width),current_bound(cap),current_width(width_cap) {}
    void run() {
        int n,e;
        while (std::cin>>n>>e) {
            edges.resize(e);
            for (auto& [u,v] : edges) std::cin>>u>>v;
            degree.assign(n,0); multiplicities.assign(e,1); loose.assign(n,0);
            shared_assignments(0,0,false);
        }
        for (auto [key,s] : totals)
            std::cout << "S " << key.first << ' ' << key.second << ' ' << s.starts << ' ' << s.stages
                << ' ' << s.max_age << ' ' << s.candidates << ' ' << s.pair_only << ' ' << s.pair_flip
                << ' ' << s.triples << ' ' << s.both << '\n';
    }
};
}

int main(int argc,char** argv) {
    if (argc!=4) return 2;
    swaps::Scan(std::stoi(argv[1]),std::stoi(argv[2]),std::stoi(argv[3])).run();
}
