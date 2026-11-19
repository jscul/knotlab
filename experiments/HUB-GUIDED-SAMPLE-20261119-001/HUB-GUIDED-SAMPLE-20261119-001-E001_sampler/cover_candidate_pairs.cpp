// Exhaust the candidate pairs after removing all pairs of each literal covering group.
#define main archived_sequential_entry
#include "../../NINTH-ROUND-SAMPLE-20261119-001/NINTH-ROUND-SAMPLE-20261119-001-E001_estimate/sequential.cpp"
#undef main

using Bits=std::vector<Word>;

namespace {
// The archived reader used 16-bit vertex IDs for a separate particle type.
// Coverage itself uses int IDs and size_t row offsets throughout.
Roster read_cover_roster(const std::string& path) {
    std::ifstream stream(path);
    Roster data{};
    require(bool(stream >> data.n >> data.blocks) && data.n > 0 && data.blocks >= 0, "invalid block roster");
    std::string line;
    std::getline(stream,line);
    for (int b = 0; b < data.blocks; ++b) {
        require(bool(std::getline(stream,line)), "invalid block count");
        std::istringstream row(line);
        std::vector<int> sites;
        for (int u; row >> u;) {
            require(u >= 0 && u < data.n, "invalid junction");
            sites.push_back(u);
        }
        require(row.eof() && sites.size() >= 2, "invalid block row");
        data.members.push_back(std::move(sites));
    }
    return data;
}

struct Cover {
    Roster input;
    Graph closed;
    std::vector<Bits> blocks;
    std::vector<std::vector<int>> holders;
    std::vector<int> biggest;
    int stride;
    Word checks=0,groups=0,certified=0;
    std::vector<std::pair<int,int>> residuals;

    explicit Cover(const std::string& file):input(read_cover_roster(file)),closed(input.n),holders(input.n),stride(closed.stride) {
        std::vector<int> names(input.n);
        std::iota(names.begin(),names.end(),0);
        closed.add_blocks(input.members,names);
        for(int b=0;b<input.blocks;++b){
            Bits mask(stride);
            for(int u:input.members[b]){mask[u/64]|=Word{1}<<(u%64);holders[u].push_back(b);}
            blocks.push_back(std::move(mask));biggest.push_back(b);
        }
        std::stable_sort(biggest.begin(),biggest.end(),[&](int a,int b){
            return input.members[a].size()>input.members[b].size();
        });
        if(biggest.size()>12)biggest.resize(12);
    }
    static std::vector<int> common(const std::vector<int>& left,const std::vector<int>& right){
        std::vector<int> result;
        std::set_intersection(left.begin(),left.end(),right.begin(),right.end(),std::back_inserter(result));
        return result;
    }
    bool witness(const Bits& allowed,const std::vector<int>& held,std::vector<int>& sites){
        if(held.empty())return true;
        Bits outside_all=allowed, short_set(stride),temp(stride);
        int fewest=input.n+1;
        for(int b:held){
            int count=0;
            for(int w=0;w<stride;++w){
                temp[w]=allowed[w]&~blocks[b][w];outside_all[w]&=temp[w];
                count+=std::popcount(temp[w]);
            }
            if(!count)return false;
            if(count<fewest){fewest=count;short_set=temp;}
        }
        for(int w=0;w<stride;++w)if(outside_all[w]){
            sites.push_back(64*w+std::countr_zero(outside_all[w]));return true;
        }
        for(int w=0;w<stride;++w)for(Word choices=short_set[w];choices;choices&=choices-1){
            int v=64*w+std::countr_zero(choices);
            for(int j=0;j<stride;++j)temp[j]=allowed[j]&closed.row(v)[j];
            sites.push_back(v);
            if(witness(temp,common(held,holders[v]),sites))return true;
            sites.pop_back();
        }
        return false;
    }
    void solve(){
        std::vector<Word> left=closed.storage;
        for(int u=0;u<input.n;++u) for(int j=0;j<stride;++j){
            auto& x=left[std::size_t(u)*stride+j];x &=~before(j,u+1);checks+=std::popcount(x);
        }
        Bits allowed(stride),group(stride);
        for(int u=0;u<input.n;++u)for(int j=u/64;j<stride;++j){
            Word& rowbit=left[std::size_t(u)*stride+j];
            while(rowbit){
                Word first=rowbit&-rowbit;int v=64*j+std::countr_zero(first);
                std::vector<int> initial={u,v};
                for(int w=0;w<stride;++w)allowed[w]=closed.row(u)[w]&closed.row(v)[w];
                if(!witness(allowed,common(holders[u],holders[v]),initial)){
                    residuals.emplace_back(u,v);rowbit^=first;continue;
                }
                std::fill(group.begin(),group.end(),0);
                for(int point:initial){
                    group[point/64]|=Word{1}<<(point%64);
                    for(int w=0;w<stride;++w)allowed[w]&=closed.row(point)[w];
                }
                for(int w=0;w<stride;++w)allowed[w]&=~group[w];
                int picked=0;
                for(int w=0;w<stride;++w){
                    while(allowed[w]){
                        if(picked%64==0){
                            bool done=false;
                            for(int b:biggest){
                                bool fits=true;
                                for(int k=w;k<stride&&fits;++k)fits=!(allowed[k]&~blocks[b][k]);
                                if(fits){for(int k=w;k<stride;++k)group[k]|=allowed[k];done=true;break;}
                            }
                            if(done){w=stride;break;}
                        }
                        Word bit=allowed[w]&-allowed[w];int point=64*w+std::countr_zero(bit);
                        group[w]|=bit;allowed[w]^=bit;
                        for(int k=w;k<stride;++k)allowed[k]&=closed.row(point)[k];
                        ++picked;
                    }
                }
                ++groups;
                for(int w=0;w<stride;++w)for(Word p=group[w];p;p&=p-1){
                    int point=64*w+std::countr_zero(p);
                    Word* dest=&left[std::size_t(point)*stride];
                    for(int k=w;k<stride;++k){
                        if(dest[k]){Word taken=dest[k]&group[k];certified+=std::popcount(taken);dest[k]^=taken;}
                    }
                }
            }
        }
        require(certified+residuals.size()==checks,"pair accounting failed");
    }
};
}
int main(int argc,char** argv){
    try{
        require(argc==2,"need a block roster");
        Cover run(argv[1]);run.solve();
        std::cout<<"{\"candidate_pairs\":"<<run.checks<<",\"covered_pairs\":"<<run.certified
                 <<",\"covering_groups\":"<<run.groups<<",\"residual_count\":"<<run.residuals.size()<<",\"residual_pairs\":[";
        for(std::size_t i=0;i<run.residuals.size();++i){
            auto [u,v]=run.residuals[i];if(i)std::cout<<',';std::cout<<'['<<u<<','<<v<<']';
        }
        std::cout<<"]}\n";
    } catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
