"""The two starting structures of the reduction (THIRD-HOLDER-20261123-001B pre-registration, "Reduction").

EIGHTEEN: the 18-knot structure of research/REVIEW-LEADS-20261123-001/posthoc/three_holders_check.py (copied knot for knot;
its distinctions are renamed so that no internal name occurs on both sides: Alice's a b c1 k1 d e c2 c3 n1 n2 g h u v keep
their names, Bob's p q r t keep theirs; the shared distinctions are s1, s2).  Class L: every observer distinction has one
old holder.
PENCIL: the pencil 9-knot structure of the pre-registration, class S; shared distinctions n1, n2.
"""
EIGHTEEN_A = [('even', ('x1', 'a', 'b')), ('even', ('c1', 'a', 'b')), ('even', ('k1', 'a', 'b')),
              ('even', ('x2', 'd', 'e')), ('odd', ('x3', 'd', 'e')), ('even', ('c2', 'd', 'e')), ('odd', ('c3', 'd', 'e')),
              ('nae', ('c1', 'c2', 'n2')), ('nae', ('k1', 'c3', 'n1')),
              ('even', ('n2', 'g', 'h')), ('odd', ('s2', 'g', 'h')), ('even', ('n1', 'u', 'v')), ('odd', ('s1', 'u', 'v'))]
EIGHTEEN_B = [('even', ('y1', 'p', 'q')), ('even', ('s1', 'p', 'q')), ('even', ('y2', 'r', 't')), ('even', ('s2', 'r', 't')),
              ('odd', ('y3', 'r', 't'))]

PENCIL_A = [('nae', ('x1', 'x2', 'n2')), ('nae', ('x1', 'x3', 'n1')), ('even', ('x2', 'd', 'e')), ('odd', ('x3', 'd', 'e'))]
PENCIL_B = [('even', ('y1', 'p', 'q')), ('odd', ('n1', 'p', 'q')), ('even', ('y2', 'r', 't')), ('odd', ('n2', 'r', 't')),
            ('odd', ('y3', 'r', 't'))]

STARTS = {'eighteen': (EIGHTEEN_A, EIGHTEEN_B, 'L'), 'pencil': (PENCIL_A, PENCIL_B, 'S')}
