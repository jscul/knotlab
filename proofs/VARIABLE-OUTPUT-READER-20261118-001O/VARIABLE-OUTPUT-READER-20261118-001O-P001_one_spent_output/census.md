# One spent output through 29 distinctions

Bond distance five is the sharp cutoff through width 29 for the one-spent source family. For every source in the interval, entries through five determine every actual junction support against every reachable mixed-law rival under an arbitrary common renaming of the rows and columns. In particular they determine the full legal triple menu. The finite check leaves the all-size cutoff open. [Frozen design](../../../research/VARIABLE-OUTPUT-READER-20261118-001O/preregistration.md)

| Width | Physical source types | Tag orbits | With a legal triple | Fourth junction or child directly involved | Legal named triples across representatives |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 23 | 4 | 4 | 2 | 2 | 4 |
| 25 | 74 | 74 | 27 | 22 | 72 |
| 27 | 544 | 544 | 214 | 200 | 697 |
| 29, held out | 2,854 | 2,858 | 895 | 835 | 2,790 |

There are no completed sources before width 23. Four width-29 types have two inequivalent tags from lawful histories. For example the fourth junction can be the same physical site while the later child is one of two distinct neighboring sites, depending on which of those neighbors was built first. The checker keeps that choice while constructing histories, along with whether the observation is immediately after spending. It drops both marks when comparing physical sources. [Counts and histories](census.json)

## Spending can create or preserve a legal triple

In a minimal width-23 example, the first nine supports in birth order are

```text
(0,1,2)
(0,3,4,14)
(1,5,6,15)
(3,5,7,8)
(2,9,10,16)
(4,9,11,17)
(7,11,12,18)
(6,10,12,13,19,20)
(8,13,21,22)
```

The fourth three-output junction is site 7, counting the seed as site 0. It introduces 13, 19 and 20. Site 8 spends 13 together with 8 and introduces 21 and 22. The menu immediately before spending is empty. Immediately afterward it is exactly \(\{\{14,16,21\},\{14,16,22\}\}\). The holders of each triple are sites 1, 4 and 8. Their pairs have witnesses \(\{0,5\},\{3\},\{7\}\), respectively. No witness is common to all three. The spending child holds a mark and the fourth junction witnesses the pair of the second and third holders.

Swapping 10 and 16 preserves all 253 readings through distance four. It takes \(\{14,16,21\}\) to \(\{10,14,21\}\). Distinction 10 is already used by sites 4 and 7, so the image is illegal. Ten entries differ through distance five and 16 differ in the full table. The same named proposal thus gives both the lower bound and a control on the interpretation of a cutoff.

In one width-25 example, site 8 is the fourth three-output birth and site 9 spends one of its outputs. Four existing triples survive the spend. The fourth junction still holds one mark of each. In another width-25 example the spending child witnesses a pair in a surviving triple. The evidence includes two independent measurements and the complete before and after menus for each direct role. [Literal controls](census.json)

## How the arbitrary-rival comparison works

Generation retains every lawful parent group, taking one arbitrary currently loose distinction from each parent. Choices at one holder give equivalent prefixes since their loose names are interchangeable. The current ordinary incidence and loose counts decide all subsequent parent groups. An incidence isometry that also preserves the designated junction, the child and the spend time flag therefore preserves all transitions. The construction retains that equivalence until inspection and then collects all unmarked physical types. The first two three-output births are necessarily unary, and the next two allow every parent count prescribed in the frozen source law.

For each of the 3,476 source types, every actual junction support of size \(k\leq 6\) has a pair with minimum bond size \(k\) whose common closed neighborhoods through size \(k\) comprise exactly that support. The two pair neighborhoods and the attaining size are obtained from the observed table. Any matching rival must realize an attaining bond of size \(k\) for that pair. All its members lie in the measured intersection. With only \(k\) candidates the entire equation is forced. All source junction equations are independent by their fresh distinctions. The width bound from N gives the same upper rank bound for an arbitrary reachable rival, so these forced equations already identify its full allowed-state relation and every exact pair entry. [Rival rank bound](../../VARIABLE-OUTPUT-READER-20261118-001N/VARIABLE-OUTPUT-READER-20261118-001N-P001_fourth_at_the_parents/rank.md#the-rank-bound-from-distance-four)

The code also enumerates every support-level explanation on these names. Each actual junction is a bond with at most six distinctions, so every possible rival junction is among the inclusion-minimal support words of size at most six in the now-forced equation space. From that set, replay every lawful named prefix through the required width and rank. This checks 1,025,624 prefix states across all tables, retaining exactly the original support family each time. No tagged output or birth information enters this inverse. Consequently the two surviving outputs remain loose at their corresponding physical junction, including on empty-menu sources. The direct census of full pair isometries likewise gives zero cross-type matches and all 9,691 self-isometry generators preserve every support. Through distance four there are 595 cross-type matches, of which 337 admit an opposing mark. There are also 1,408 opposing self-isometry generators.

Literal measurements on the named examples use both connected-cut enumeration and independent minimization in the binary equation space. Tested renamings transport the full pair table and every legal triple. The N controls include its terminal width-23 flip and width-27 planted flip. Both width-31 terminal explanations have six binary and three ternary literal spending choices. They all yield empty menus at width 33. For the same appended support \(\{17,28,31,32\}\), four pair entries involving 31 or 32 expose the old ambiguity through distance five.

Run `python3 -B census.py` with a C++20 compiler available. It builds the inherited cut engine in temporary storage and writes the deterministic evidence to standard output. [Checker](census.py) · [Evidence](census.json)
