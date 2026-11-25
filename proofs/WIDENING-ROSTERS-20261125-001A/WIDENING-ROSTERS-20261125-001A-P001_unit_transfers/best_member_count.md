# Exact counts from members of a finite round

Use the roster proved in [§2 of the proof](proof.md). Put $s=t-1$, let $m\ge3$, and let $r$ be a nonnegative integer. The letters $x,y$ denote nonnegative ordered sums of $s$. For brevity we write $x$ for the member $P_x$. There is also one distinct offshoot at each $s e_i$, including $s=0$ when all these sums coincide.

## The least number of witnessed steps

A transfer reduces the total amount by which $x$ exceeds $y$ by at most one. Moving a unit from a term in excess to a term in deficit reduces it by one and never makes a term negative. Hence the least number of steps between sums is

$$
d(x,y)=\sum_i(x_i-y_i)_+=\sum_i(y_i-x_i)_+ .
$$

An offshoot has just one neighbour, so it supplies no shorter route between sums. Reaching offshoot $i$ from $x$ takes $s-x_i+1$ steps. Between distinct offshoots the least number is $s+2$, also when $s=0$. Thus the exact count from $x$ is

$$
\#\{y\ge0:\ \textstyle\sum_i y_i=s,\ d(x,y)\le r\}
+\#\{i:x_i\ge s-r+1\}.
$$

From an offshoot there is one member at $r=0$. At $r\ge1$ the count is

$$
1+\binom{\min(s,r-1)+m-1}{m-1}
+(m-1)\mathbf1_{r\ge s+2}.
$$

The other $m-1$ terms of a sum reachable from its neighbour $s e_i$ add to at most $\min(s,r-1)$. Adding a slack term counts them by the displayed binomial coefficient. The last term counts the other offshoots. At $s=0$ the count from the shared neighbour is $1,m+1,m+1,\ldots$, while from each offshoot it is $1,2,m+1,m+1,\ldots$.

## A maximizing member at every radius

At $r\ge1$ everything reachable from an offshoot is reachable from its neighbour within $r$ steps. It therefore suffices to maximize the count over sums. Write $a,b$ for two entries of a starting sum $x$ with $a\ge b+2$. We show that replacing them with $a-1,b+1$ cannot reduce the count.

Fix every other target term. Let $h$ be the sum of the remaining two target terms, $k,h-k$ those terms, and $R$ the step allowance left after deducting the deficits $(x_j-y_j)_+$ in the fixed terms. The two variable terms cost

$$
(a-k)_+ + \big(k-(h-b)\big)_+ .
$$

The minimum cost is $(a+b-h)_+$. The minimizing integers lie between $a$ and $h-b$ inclusive, whichever is smaller. The cost increases by one per integer on either side. If the allowance suffices, the eligible integers before imposing $0\le k\le h$ therefore form an interval with midpoint $(h+a-b)/2$. Replacing the starting entries as above shifts that whole interval one unit to the left. Its midpoint was at least $h/2+1$. Its intersection with $[0,h]$ can only stay the same size or increase. Indeed, if an old right endpoint $v$ in $[0,h]$ is lost, the new left endpoint $u-1$ also lies in $[0,h]$, since $u+v=h+a-b\ge h+2$. This proves that the count of sums never decreases.

It remains to account for the offshoots. An offshoot can be lost only for $a=s-r+1$. In that case take the particular choice having all other target terms zero. Here $h=s$ and $R=b+1$. The eligible integer interval changes from $[a-b-1,s+1]$ to $[a-b-2,s]$. Its intersection with $[0,s]$ gains exactly one integer since $a-b\ge2$. This compensates for the possible loss of that offshoot. No other one can be lost.

Repeatedly balancing two terms strictly reduces the sum of their squares, so the operations terminate. All resulting terms differ by at most one. Permutations have the same count. Thus **each balanced sum maximizes the count at every radius**.

For an explicit finite maximum write $s=mq+h$ with $0\le h<m$. A balanced sum has $m-h$ entries $q$ and $h$ entries $q+1$. Define the formal power series

$$
F_j(u,v)=1+\frac{u}{1-u}+\sum_{a=1}^j v^a .
$$

For a source entry $j$, the three terms count leaving it fixed, raising it, and lowering it by at most $j$. A target at precisely $k$ steps raises and lowers a total of $k$ units each. The exact finite maximum is therefore

$$
\begin{aligned}
M_{m,s}(r)={}&\sum_{k=0}^{\min(r,s)}
[u^kv^k] F_q(u,v)^{m-h}F_{q+1}(u,v)^h \\
&+ h\,\mathbf1_{r\ge s-q}
 +(m-h)\,\mathbf1_{r\ge s-q+1}.
\end{aligned}
$$

The last two terms count the offshoots reached from the two possible starting entries. Every sum is within $s-q$ steps of this source. Indeed, some $y_i\ge x_i$ because the totals agree. Therefore $\sum_j\min(x_j,y_j)\ge x_i\ge q$, so $d(x,y)\le s-q$. An offshoot attached to an entry $q$ requires $s-q+1$ steps. Such an entry always exists because $h<m$. Hence the maximum first covers the whole part at $r=s-q+1$.

## When the unrestricted count is attained

Temporarily allow the target terms to take any integer values, still summing to $s$, and count sums only. Translation gives an unrestricted count $U_m(r)$ independent of the source. If all $x_i\ge r$, no target within $r$ steps has a negative entry. Also no offshoot can be reached for $r\ge1$, since $s-x_i$ is the sum of the other $m-1$ entries. Thus this source attains $U_m(r)$.

Conversely suppose some $x_j<r$, with $r\ge1$. For each $i\ne j$, the unrestricted target $x-r e_j+r e_i$ is within $r$ steps and has a negative $j$th term. These are distinct across all ordered choices of a deficient $j$ and a different $i$. At least one unrestricted target is therefore missing. If any offshoot $i$ is reached, $\sum_{j\ne i}x_j\le r-1$, so all the $m-1$ other coordinates are deficient. At least $(m-1)^2$ unrestricted targets are then missing. Since $(m-1)^2>m$ for $m\ge3$, even adding every offshoot leaves the count strictly below $U_m(r)$. If no offshoot is reached, the first missing target already gives strict inequality. Taking the maximum and including $r=0$ gives

$$
M_{m,s}(r)=U_m(r)\quad\text{exactly for}\quad 0\le r\le\lfloor s/m\rfloor .
$$

For $1\le r\le\lfloor s/m\rfloor$, the sums attaining this value are exactly those with every entry at least $r$. There are $\binom{s-mr+m-1}{m-1}$ of them. No offshoot ties in this range. From its neighbouring sum, previously reached targets remain reachable and additional sums first reached in exactly $r$ transfers exist for $1\le r\le s$. An offshoot needs the extra step to that neighbour.

## The unrestricted polynomial

Put $d=m-1$. With unbounded lowering, the single-entry series is

$$
F_\infty(u,v)=1+\frac{u}{1-u}+\frac{v}{1-v}
=\frac{1-uv}{(1-u)(1-v)} .
$$

The equal coefficients $[u^kv^k]F_\infty(u,v)^m$ count sums at exactly $k$ steps. The equal coefficients of $((1-u)(1-v))^{-m}$ are $\binom{n+d}{d}^2$. Multiplying by $(1-uv)^m$ corresponds in their generating function to multiplication by $(1-z)^m$. Summing through $r$ gives

$$
\sum_{r\ge0}U_m(r)z^r
=(1-z)^d\sum_{n\ge0}\binom{n+d}{d}^2z^n .
$$

The sum on the right without the factor $(1-z)^d$ is

$$
[w^d]\frac{(1+w)^d}{(1-z(1+w))^{d+1}}.
$$

Expanding in $w$, then extracting $[z^r]$ in the preceding equation, yields

$$
U_m(r)=\sum_{j=0}^{d}\binom dj\binom{d+j}{j}\binom rj .
$$

Its leading coefficient is $\binom{2d}{d}/d!$. For $m=3$ the expansion is $1+6r+6\binom r2=3r^2+3r+1$. For $m=4$ it is $1+12r+30\binom r2+20\binom r3=(2r+1)(5r^2+5r+3)/3$. The degree $m-1$ is attained on a range of radii growing without bound with the round. Each particular finite roster eventually saturates at its own size.
