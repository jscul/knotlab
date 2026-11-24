/* Best four-correlation (CHSH) score over the 15^4 parity outcome choices and the four one-minus sign patterns, for a batch of
   8x8 old-word tables M (REVIEW-LEADS-20261123-001C).  Same arithmetic as common.score_batch (float64).
   C: 2 x 15 x 8 (sum over lawful fresh values of the parity sign), W: 2 x 8 (number of lawful fresh values). */
#include <math.h>
void best_scores(int n, const double *M, const double *C, const double *W, int control, double *out)
{
    for (int m = 0; m < n; m++) {
        const double *Mm = M + 64 * m;
        double E[4][15][15];
        double tot = 0.0;
        for (int i = 0; i < 64; i++) tot += Mm[i];
        for (int a = 0; a < 2; a++) for (int b = 0; b < 2; b++) {
            double Mab[64]; double den = 0.0;
            for (int x = 0; x < 8; x++) for (int y = 0; y < 8; y++) {
                double v = Mm[8 * x + y];
                if (control) v /= (W[8 * a + x] * W[8 * b + y]);
                Mab[8 * x + y] = v;
                den += W[8 * a + x] * Mm[8 * x + y] * W[8 * b + y];
            }
            if (control) den = tot;
            for (int k = 0; k < 15; k++) {
                double tmp[8];
                for (int y = 0; y < 8; y++) {
                    double s = 0.0;
                    for (int x = 0; x < 8; x++) s += C[120 * a + 8 * k + x] * Mab[8 * x + y];
                    tmp[y] = s;
                }
                for (int l = 0; l < 15; l++) {
                    double s = 0.0;
                    for (int y = 0; y < 8; y++) s += tmp[y] * C[120 * b + 8 * l + y];
                    E[2 * a + b][k][l] = s / den;
                }
            }
        }
        double best = 0.0;
        for (int p = 0; p < 4; p++) {
            double s[4] = {1.0, 1.0, 1.0, 1.0}; s[p] = -1.0;
            for (int k0 = 0; k0 < 15; k0++) for (int k1 = 0; k1 < 15; k1++) {
                double umax = -1e300, umin = 1e300, vmax = -1e300, vmin = 1e300;
                for (int l = 0; l < 15; l++) {
                    double u = s[0] * E[0][k0][l] + s[2] * E[2][k1][l];
                    double v = s[1] * E[1][k0][l] + s[3] * E[3][k1][l];
                    if (u > umax) umax = u; if (u < umin) umin = u;
                    if (v > vmax) vmax = v; if (v < vmin) vmin = v;
                }
                double c1 = umax + vmax, c2 = -(umin + vmin);
                if (c1 > best) best = c1; if (c2 > best) best = c2;
            }
        }
        out[m] = best;
    }
}
