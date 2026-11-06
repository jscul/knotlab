# Scoping before the contract (disclosed)

| script | what it computed | outcome |
| --- | --- | --- |
| `scope1.py` | general BCH braid model (then dense bracket) at p = 5 and 7 on 4_1 x4 + P4 (0,0), 4_1 x4 + P4B (6,1), T(2,p) x8 + P4 (0,1) + P4B (3p,0); algebras u4, free class 3 on (y1-, y2-), cross-layer class 3, cross-layer class 4; 32 samples | u4, free3 (y1-, y2-) and cross4: Q equal to rule R1 on every sample (ratio 1, KAPPA = 2); cross3: no obstruction on any sample |
| ticket A check | abelian examples (cross3, cross4 mod [y,[y,[x,y]]]) on gadgets K3 and P3 at p = 5, 7 | no obstruction; the full cross4 obstructs |
| `timing.log` | build all algebras; model and one solve of the largest algebra (free class 4 on x+, y1-, y2-, dimension 32) on gadget C4 at p = 7 | timing only (0.6 s and 1.8 s); no form inspected |

Never computed before the contract:
- the algebras free3 (y1-, y2-, y3-), free3 (x+, y1-, y2-) and free4 (x+, y1-, y2-) with layer-1 data on y1 only;
- the gadgets K3 at p = 5 and C4 at p = 7 for the nonabelian algebras;
- T(2,11) x8 + P4B (0,1) at p = 11;
- the model agreement with bm.py;
- the lifting test with the direct count;
- the controls.

The scoped fixtures are rerun as regression.
