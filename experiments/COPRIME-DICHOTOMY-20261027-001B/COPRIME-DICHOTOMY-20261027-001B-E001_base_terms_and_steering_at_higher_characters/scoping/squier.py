import sympy as sp
t = sp.symbols("t")
def bur(n, g, tt):
    M = sp.eye(n)
    i = abs(g) - 1
    if g > 0:
        M[i, i], M[i, i + 1], M[i + 1, i], M[i + 1, i + 1] = 1 - 1 / tt, 1 / tt, 1, 0
    else:
        M[i, i], M[i, i + 1], M[i + 1, i], M[i + 1, i + 1] = 0, 1, tt, 1 - tt
    return M
for n in (3, 4, 5):
    J = sp.Matrix(n, n, lambda a, b: sp.Symbol(f"j{a}{b}"))
    eqs = []
    for g in range(1, n):
        E = bur(n, g, 1 / t).T * J * bur(n, g, t) - J
        eqs += [sp.simplify(e) for e in E]
    sol = sp.solve(eqs, list(J), dict=True)
    Js = J.subs(sol[0])
    print(n, sp.simplify(Js))
