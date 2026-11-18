"""Closed-form outline of the chain grid's count, and Golab's pi of a norm given by its support function."""
import math

import numpy as np
from scipy.optimize import brentq


def A_of(t):
    """cosh q1 + cosh q2 = A on the decay curve; A = (1 + t^2)^2 / (2 t (1 - t^2)) = cosh^2 2K / sinh 2K."""
    return (1 + t * t) ** 2 / (2 * t * (1 - t * t))


def rate(theta, A):
    """Decay rate in nats per unit length along (cos theta, sin theta): the support function of {cosh q1 + cosh q2 <= A}."""
    c, s = abs(math.cos(theta)), abs(math.sin(theta))
    f = lambda mu: math.sqrt(1 + (mu * c) ** 2) + math.sqrt(1 + (mu * s) ** 2) - A
    mu = brentq(f, 0.0, 1e8, xtol=1e-15, rtol=1e-15)
    return c * math.asinh(mu * c) + s * math.asinh(mu * s)


def golab_pi(h, M=20000):
    """Half the perimeter of the unit ball {x : h(x) <= 1} measured in the norm h itself (h a support-type norm)."""
    ph = np.linspace(0, 2 * np.pi, M, endpoint=False)
    hv = np.array([h(p) for p in ph])
    pts = np.stack([np.cos(ph) / hv, np.sin(ph) / hv], axis=1)
    seg = np.roll(pts, -1, axis=0) - pts
    ln = np.hypot(seg[:, 0], seg[:, 1])
    th = np.arctan2(seg[:, 1], seg[:, 0])
    return float(sum(h(a) * x for a, x in zip(th, ln)) / 2)


def anisotropy(h, M=4001):
    th = np.linspace(0, math.pi / 4, M)
    v = np.array([h(x) for x in th])
    return float(v.max() / v.min())
