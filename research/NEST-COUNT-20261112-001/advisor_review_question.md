Review this draft cold and briefly (at most ~350 words). Check each statement for errors or gaps, say which are known (cite if you can) and what is overclaimed. Especially: is T1's usual-limit claim right; is T2 correctly stated; is the P3a gadget right; is P3c's reduction sound (complement symmetry handled, translation invariance, references); is "counting needs unbounded interfaces" fair?

# Can nested patterns count? (draft for review)

Setting. NAE on three-place knots on distinct distinctions. The A79 language (SHORT-DESC dlang): finitely many definitions, each with
k <= 6 ports and l <= 6 own distinctions; SELF only in three-port definitions; depth t (depth 1: SELF is a knot). Port relation of a
definition = the states of its ports that extend inside it. Usual limit: knots present at all but finitely many depths.

T1 (finite state; decidable fates). The tuple X_t of the self-holding definitions' port relations at depth t lies in a set of size
16^s (complement-closed relations on three ports; s = number of self-holding definitions) and X_{t+1} = Phi(X_t) for a fixed map.
So t -> X_t is eventually periodic with preperiod + period <= 16^s, every definition's relation at depth t (main included) is a
function of X_{t-1}, and "the depth-t pattern lives" is eventually periodic in t: deciding it for every t needs at most 16^s depths.
The bottomless pattern lives iff main(G) is non-empty, G the greatest fixed point from TOP, reached in at most 4s strict decreases
(compactness + Knaster–Tarski). Usual limit: a knot on the args of a depth-t SELF call recurs at depth t+1 only if a SELF call of the
copy has the same three args, i.e. the copy's own ports (pass-through: args a permutation of the ports); recursively, the knots
present at infinitely many depths are exactly the knots on the ports of copies of definitions with a pass-through call. So the usual
limit = bottomless pattern + K(ports) in each self-holding definition with a pass-through call: decidable by the same fixed point.

T2 (no counter at the ends). For any fixed b, the set of states the depth-t pattern allows on all distinctions of levels < b
(a bounded top window) is a function of X_{t-b}, hence eventually periodic in t with the same period. So no property of a bounded top
window distinguishes infinitely many depths: a nested pattern of this language cannot count its own depth as seen from its ends.
(It may still "count inside": least bonds between the top and level s can grow with s, as bond distance does on a ruler; not claimed.)

P3a (gadget). x != y holds iff there are a, b, c with NAE(x,y,a), NAE(x,y,b), NAE(x,y,c), NAE(a,b,c) (distinct triples). Equality by
two inequalities through a fresh distinction. So repeated variables in pp-definitions can be removed.
P3b (expressiveness, literature). NAE_3 is a base of the co-clone IN2 = all complement-closed Boolean relations (Böhler, Reith,
Schnoor, Vollmer 2005). With P3a, every complement-closed relation is pp-definable by NAE knots on distinct distinctions.
P3c (what breaks T1). For translation-invariant meeting patterns on Z^2 (a finite fundamental domain copied by every translation),
"the infinite pattern lives" is undecidable: given a Wang tile set, encode each site's tile by bits read relative to a per-site
reference distinction r (bit = x xor r, so every constraint is complement-closed), tie neighbouring references by equality gadgets,
and pp-define the horizontal and vertical compatibility relations (P3b): a computable map preserving the existence of a tiling,
so Berger's theorem (1966) applies. What fails is the bounded interface: a finite patch meets the rest along a boundary that grows
with it, so no finite set of port relations summarises it. The nested analogue is substitution with copies glued along growing
boundaries (Robinson 1971; Mozes 1989: substitution tilings are enforced by local rules). Counters and Turing machines are then
expressible (Wang 1961; Berger 1966).

Rarity: under the A79 weighting no pattern counts (T1, T2 hold for every description). Counting needs a language with unbounded
interfaces.

Known in kind: Lengauer–Wanke 1988 (bounded-interface hierarchical graphs); Courcelle (HR grammars, MSO decidable); Rabin 1969 (MSO
on infinite trees); periodically specified problems (Orlin 1984; Marathe, Hunt, Stearns, Radhakrishnan, 1990s: 2-D periodic SAT
undecidable/hard); Berger 1966, Wang 1961, Robinson 1971, Mozes 1989; Böhler et al. 2005; Gödel 1930 (compactness).
