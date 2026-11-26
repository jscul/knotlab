// First seven census rounds, with no taking. A spent knot still witnesses its
// live neighbours. Each paid loose distinction makes one new parent-child
// sharing. Only these meetings and the live loose counts enter later rosters.
#include <algorithm>
#include <iostream>
#include <iterator>
#include <set>
#include <stdexcept>
#include <vector>
using List = std::vector<int>;
using Lists = std::vector<List>;

List common(const List& a, const List& b) {
    List out;
    std::set_intersection(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(out));
    return out;
}
void unique_sorted(List& a) {
    std::sort(a.begin(), a.end());
    a.erase(std::unique(a.begin(),a.end()),a.end());
}

struct Roster {
    const Lists& meetings;
    Lists seen, near, groups;
    std::set<std::pair<int,int>> covered;
    int cliques = 0;

    void visit(List& chosen, List possible, List done) {
        if (possible.empty()) {
            if (!done.empty()) return;
            if (++cliques > 20000000) throw std::overflow_error("cliques");
            if (chosen.size() < 3) return;
            for (int w : meetings[chosen[0]]) {
                bool held = true;
                for (int v : chosen)
                    if (!std::binary_search(seen[w].begin(),seen[w].end(),v)) { held=false; break; }
                if (held) return;
            }
            groups.push_back(chosen);
            for (size_t i=0;i<chosen.size();++i) for (size_t j=0;j<i;++j)
                covered.insert(std::minmax(chosen[i],chosen[j]));
            return;
        }
        // A maximum-degree pivot keeps fully witnessed large groups cheap.
        int pivot = possible.front(), best = -1;
        for (auto choices : {&possible,&done}) for (int v : *choices) {
            int score = common(near[v],possible).size();
            if (score > best) { best = score; pivot = v; }
        }
        List branches;
        std::set_difference(possible.begin(), possible.end(), near[pivot].begin(),near[pivot].end(),
                            std::back_inserter(branches));
        for (int v : branches) {
            chosen.push_back(v);
            visit(chosen,common(possible,near[v]),common(done,near[v]));
            chosen.pop_back();
            possible.erase(std::lower_bound(possible.begin(),possible.end(),v));
            done.insert(std::lower_bound(done.begin(),done.end(),v),v);
        }
    }
    Roster(const Lists& meet, const List& loose) : meetings(meet), seen(meet.size()), near(meet.size()) {
        long long incidences=0, pairs=0;
        for (size_t w=0;w<meet.size();++w) {
            for(int v:meet[w]) if(loose[v]) seen[w].push_back(v);
            incidences+=seen[w].size()+2; // also covers the repeated sharing at the initial meeting
            if(incidences>200000000) throw std::overflow_error("incidences");
            unique_sorted(seen[w]);
            long long n=seen[w].size();
            if(n*(n-1)/2>2000000) throw std::overflow_error("witness pairs");
            for(int v:seen[w]) for(int u:seen[w]) if(v!=u) near[v].push_back(u);
        }
        for (auto& ns:near) { unique_sorted(ns); pairs += ns.size(); }
        if (pairs>4000000) throw std::overflow_error("pairs");
        // Enumerate maximal groups once, starting with their least member.
        for(size_t v=0;v<meet.size();++v) if(loose[v]) {
            List chosen{int(v)};
            auto split=std::lower_bound(near[v].begin(),near[v].end(),int(v));
            visit(chosen,List(split,near[v].end()),List(near[v].begin(),split));
        }
        for(size_t u=0;u<near.size();++u) for(int v:near[u])
            if(int(u)<v && !covered.count({int(u),v})) groups.push_back({int(u),v});
        if(groups.size()>2000000) throw std::overflow_error("groups");
    }
    List demand() const {
        List owing(meetings.size());
        for(auto& g:groups) for(int u:g) ++owing[u];
        return owing;
    }
};

int main() {
    int ration,treat,n,links;
    while(std::cin>>ration>>treat>>n>>links) {
        Lists meetings(n); List loose(n), input_size(n);
        long long distinctions=links+1; // upper bound, including a repeated initial sharing
        for(int& h:loose) {std::cin>>h; distinctions+=h;}
        for(int k=0;k<links;++k) {int a,b;std::cin>>a>>b;meetings[a].push_back(b);meetings[b].push_back(a);}
        try {
            for(int r=1;r<=8;++r) {
                Roster roster(meetings,loose);
                auto due=roster.demand();
                if(r>1) for(size_t u=n;u<loose.size();++u) {
                    int floor=std::max(1,3-input_size[u]);
                    int ordinary=std::max(floor,due[u]);
                    loose[u]=ration==0?ordinary:(ration==1?std::min(3,ordinary):floor);
                    distinctions+=loose[u];
                }
                if(distinctions>40000000) throw std::overflow_error("distinctions");
                // Demand has now completed the previous round.
                if(r>1) std::cout<<" "<<meetings.size();
                if(r==8 || meetings.size()>1500) break;
                Lists births;
                for(const List& g:roster.groups) {
                    if(std::all_of(g.begin(),g.end(),[&](int v){return due[v]<=loose[v];}))
                        births.push_back(g);
                }
                n = static_cast<int>(loose.size());
                List paid(n);
                for(auto& g:births) for(int v:g) ++paid[v];
                for(int v=0;v<n;++v) {
                    if(due[v]>loose[v] && treat==0) continue;
                    if(due[v]<=loose[v] || treat==2)
                        for(int k=paid[v];k<loose[v];++k) births.push_back({v});
                    loose[v]=0;
                }
                if (births.size()>2000000) throw std::overflow_error("births");
                for(auto& ps:births) {
                    int u=meetings.size();
                    for(int v:ps) meetings[v].push_back(u);
                    meetings.push_back(ps); loose.push_back(1); input_size.push_back(ps.size());
                }
            }
        } catch(const std::overflow_error& e) {std::cout<<" guard-" <<e.what();}
        std::cout<<"\n";
    }
}
