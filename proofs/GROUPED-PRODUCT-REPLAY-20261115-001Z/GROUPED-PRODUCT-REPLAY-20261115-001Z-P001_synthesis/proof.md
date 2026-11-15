# Regroup an AND proof and carry its pair parity directly

Status: Proved

## Accepted conclusions

- A checked four-input AND producer can be regrouped with polynomial overhead for every final-only cut that also keeps incoming parent statements public. For an arbitrary number of inputs, recompiling the standard AND interface and its supplied public derivations preserves one shared suffix with polynomial overhead. The balanced four-input example needs five affine parts and the chain needs four. [A, candidate-local-delta](../../GROUPED-PRODUCT-REPLAY-20261115-001A/GROUPED-PRODUCT-REPLAY-20261115-001A-P001_regroup_final/proof.md)
- A supplied degree-two proof may carry a correctly derived pair XOR directly as an ordinary quadratic while keeping the final AND on a crossed chain. The Boolean choice has an O(m) derivation. The actual rule inscriptions and boundary derivations determine whether direct replay is admissible. [B, candidate-local-delta](../../GROUPED-PRODUCT-REPLAY-20261115-001B/GROUPED-PRODUCT-REPLAY-20261115-001B-P001_carry_quadratic_xor/proof.md)
- A two-case split on the multiplying bit z gives a polynomial checked degree-two conversion of zQ when its residual uses respect the degree bound. A second independent wQ can be a genuine cubic even after z is fixed. Splitting on the directly derived quadratic Q instead handles all legal later uses through U and zU at a certified interface, with no retained pair or aggregate name. [C, candidate-local-delta](../../GROUPED-PRODUCT-REPLAY-20261115-001C/GROUPED-PRODUCT-REPLAY-20261115-001C-P001_fresh_bit_replay/proof.md)

The synthesis binds the accepted conclusions and the decision note. The scientific arguments and independent checks are in the linked proof records.
