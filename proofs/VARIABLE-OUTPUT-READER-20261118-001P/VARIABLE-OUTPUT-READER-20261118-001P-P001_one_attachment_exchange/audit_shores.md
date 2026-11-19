# Independent closure for six-bit shores through the fourth junction

At every depth, a live one-spent source with a six-bit shore through the fourth three-output junction and a loose holder of the attachment color has six loose distinctions in total. Its spending child takes three parents and retains one or two of its own outputs. The independent closure finds four qualifying records. In all four the selected shore is the whole source. When the child retains exactly one output, it is also the only loose holder of the attachment color.

| Child outputs still loose | Qualifying records | With an adjacent holder | With a nonadjacent holder | Shortest widths |
| ---: | ---: | ---: | ---: | :--- |
| 2 | 2 | 2 | 2 | 31, 33 |
| 1 | 2 | 2 | 0 | 31, 33 |

The third three-output birth has two parents in all four records. The 416,024 marked records include arbitrary choices of shore side for the seed and each newborn. No qualifying proper shore occurs, and no live source has a smaller shore through the fourth junction. The replay independently checks all four chronological histories, their actual loose holders, complete triple menus and selected boundaries. [Exact counts and named histories](audit_shores.json)

## Why the finite state covers every depth

The initial seed and two unary three-output births have seven loose distinctions. The third three-output birth can increase this by at most two. The fourth is ternary and leaves the loose count unchanged, and every other birth after the first two has at least as many parents as outputs. There are at most nine live holders and at most three loose distinctions per holder. The forward search permits all three parent arities for the third three-output birth. It permits the first use of the fourth junction as a parent and keeps its two other outputs loose thereafter. It records the spending child's parent count and keeps the child's identity while it has a loose output. Retirement gives a loose count of zero. For a current legal triple the check allows every currently loose holder, including the fourth junction itself.

The state keeps the exact meetings between live holders. It records only which pairs and triples have a retired common neighbor. These are sufficient for the formation law because each test asks whether a specified pair or triple has any common neighbor. Retired sites never acquire a neighbor. When live holders retire, the check restricts these relations to the surviving holders and adds the pair and triple witness sets contributed by each newly retired site. All currently loose names at a holder have the same availability, color and shore side. Consuming any one of them gives the same state transition. The canonical labels preserve these data, including the fourth and child roles.

The first closure reaches 150,884 formation states along 801,683 transitions. Of these, 8,613 have a legal triple and a spending child. A backward traversal retains the 20,063 states that can lead to such an observation. Every prefix of a history ending at a live observation belongs to this traversal.

Each transition then tries either side for the newborn, with the fourth junction always selected. It pays one ordinary crossing for each meeting whose ends have different sides. That cost is irreversible. The current boundary has that cost plus the number of loose bits held by selected sites. The eventual fourth junction contributes two loose bits, so a history paying more than four ordinary crossings cannot reach a six-bit target. Flags record any incoming meeting and any omitted site, without imposing parent closure. This second search closes after 416,024 marked states and 997,953 transitions. The four qualifiers have neither flag, with zero exceptions to the required child status. The target compares both neighboring and nonneighboring holders of color opposite the fourth junction. Each marked state and each allowable next transition is explored until the queue is exhausted, regardless of the number of already retired sites.

The checker is a standard-library C++ implementation. It uses the birth rule and literal parity boundaries, independently of the production transition and distance code. The optimized and address/undefined-behavior-sanitized builds produced byte-identical evidence. [Independent checker](audit_shores.cpp) · [Production statement](shore.md)

```sh
scratch=$(mktemp -d)
c++ -std=c++20 -O2 -Wall -Wextra -Werror audit_shores.cpp -o "$scratch/audit"
"$scratch/audit"
rm -- "$scratch/audit"
rmdir -- "$scratch"
```
