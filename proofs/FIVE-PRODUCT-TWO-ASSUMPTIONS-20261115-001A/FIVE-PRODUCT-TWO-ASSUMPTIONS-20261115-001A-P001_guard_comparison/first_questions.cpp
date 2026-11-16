// Reuse the immutable two-triple verifier and the original-coordinate affine lifts.
// Its standalone command entry is unused by this focused replay.
#define main predecessor_one_premise_command
#include "one_premise.cpp"
#undef main

int main() {
    Model model;
    GivenTwo available_rule;
    assert(model.embedding_count == 9216);
    for (int a : {0, 1}) {
        // Canonical packed triples (x1,x0,u), (x2,x1+x3,v), (x4,x3+x5,s+u+v).
        int x2_equation = 8 | (a << 9);
        int v_zero = 32;
        int x0_zero = 2;
        for (int q=1; q<512; ++q) {
            int total = 1;
            for (int answer : {0,1}) {
                int lower = 0;
                for (const auto& e : model.embs[q][answer]) {
                    int g=pulled(x2_equation,e), j=pulled(v_zero,e), l=pulled(x0_zero,e);
                    // A citation of the conjunctive premise always establishes each
                    // of these broader premises. All three imply the same update
                    // once their respective stored rule is supplied to the small proof.
                    for (int broad : {g,j,g^j})
                        lower=std::max(lower, available_rule.cost(broad,l));
                }
                total+=lower;
            }
            std::cout << a << ' ' << q << ' ' << total << '\n';
        }
    }
}
