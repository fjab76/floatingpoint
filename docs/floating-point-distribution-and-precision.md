# Floating-point numbers

**Outline**

- [Intuition: floats vs reals](#floating-point-numbers-vs-real-numbers) — catchment intervals and a surprising Python example
- [Informal precision](#precision) — spacing, hardware paths, and arbitrary-precision contrast
- [IEEE representation](#floating-point-number-representation) — sign, exponent, and significand (normal numbers)
- [Distribution](#distribution-of-floating-point-numbers-on-the-number-line) — segments, ULP, safe integers
- [Decimal round-trips](#decimal-round-trips) — canonical decimals, digit limits, segment vs individual precision

## Floating-point numbers vs real numbers

Understanding floating-point numbers is essential when working with decimal values. 

Floating-point numbers can also represent whole numbers outside the range of the integers, at the cost of precision. 

Here's a simple example to illustrate the behaviour of floating-point arithmetic:

```python
>>> r = 72057594037927955
>>> r + 1.0 < r
True
```

Here `r` is an arbitrary-precision `int`, the literal `1.0` is binary64 (`double`), and at that magnitude the spacing between neighbouring doubles exceeds 1, so `r + 1.0` can round back down and compare less than `r`.

To build intuition, it helps to ask what problem floating-point is meant to solve.

Let's first make a detour and take a look at the integer numbers: in any given interval, the amount of integers is finite. That property simplifies integers representation. Vendors define computer architectures to support a specific interval and if you ever go beyond the maximum value, you wrap around to the other end of the interval (what is known as [modular arithmetic](https://en.wikipedia.org/wiki/Modular_arithmetic)):

```java
// Java
jshell> Integer.MAX_VALUE + 1 == Integer.MIN_VALUE
true
```

Here's the problem now: given two real numbers, no matter how close they are to each other, it is always possible to find another number in between. That's another way to say that, in any given interval, there are infinite real numbers.

### Standard IEEE 754

To get around this problem, the [IEEE 754](https://en.wikipedia.org/wiki/IEEE_754-1985) standard was devised to pick a discrete set of reference values so that any other real is mapped to one of them, typically by *round to nearest, ties to even*.

Think of each representable float as owning a *catchment interval* on the number line: every real number $r$ in that interval rounds to the same floating-point value $FP_1$, e.g.

```python
>>> float(72057594037927956)
7.205759403792795e+16
```

For the same literal, older Java prints a different decimal string than Python:

```java
// Java (JShell 11.0.11)
jshell> double d = 72057594037927956d
d ==> 7.2057594037927952E16
```

What matters is that floating-point numbers are defined in binary format, so as long as two decimal numbers have the same binary representation, both are correct. In this case, both $7.205759403792795\times 10^{16}$ and $7.2057594037927952\times 10^{16}$ correspond to the same double-precision binary format

```
0100001101110000000000000000000000000000000000000000000000000001
```

There are 15 integers from $7.2057594037927945\times 10^{16}$ through $7.2057594037927959\times 10^{16}$ (not to mention the infinite values resulting of adding a fractional part to each of those integers).

Arguably, the canonical representative would be the exact decimal number $7.2057594037927952\times 10^{16}$ corresponding to the binary representation. On the other hand, it can be argued that the last digit in the 17-digit $7.2057594037927952\times 10^{16}$ is not significant as the 16-digit decimal number $7.205759403792795\times 10^{16}$ is enough to represent the floating-point binary number. And in general this is the preferred approach. The Java behaviour seen above was considered as a [bug](https://bugs.java.com/bugdatabase/view_bug.do?bug_id=4511638) and is already fixed in newer versions:

```java
// Java (JShell 21)
jshell> double d = 72057594037927956d
d ==> 7.205759403792795E16
```

## Precision

The more floating-point values lie in a given interval, the smaller the spacing between neighbours, so fewer distinct real numbers share the same floating-point number.

All real numbers that map to the same floating-point number are **indistinguishable** at that precision.

When [IEEE 754](https://en.wikipedia.org/wiki/IEEE_754-1985) speaks of [single-](https://en.wikipedia.org/wiki/Single-precision_floating-point_format) and [double-precision](https://en.wikipedia.org/wiki/Double-precision_floating-point_format) formats, it is largely about how many distinct floating-point values the format provides.

Integers from $72057594037927945$ to $72057594037927959$ can all round to the same double $72057594037927952$, so the rounding error can be up to $7$ in that binade, small relative to $10^{16}$, but whether that is acceptable or not depends on the use case.

### Floating-point vs arbitrary-precision arithmetic

Floating-point arithmetic is fast because FPUs implement it in hardware, for example, on typical x86-64 systems scalar `double` and `float` often use SIMD-family registers (e.g. 128-bit SSE `xmm0`–`xmm15`); historically, x87 stack-based floating-point was a separate path, and the exact hardware story depends on platform, ABI, and compiler. When more precision is needed, libraries implement arbitrary-precision arithmetic in software—`BigDecimal` in Java, [mpmath](https://mpmath.org) in Python, and so on.

A tiny $\pi$ integration example shows the speed gap:

```python
def double_pi(num_steps):
    step_size = 1.0 / num_steps
    total = 0
    for i in range(num_steps):
        x = (i + 0.5) * step_size
        total += 4.0 / (1.0 + x**2)
    return step_size * total


from mpmath import mp, mpf


def arbitrary_precision_pi(num_steps, precision):
    mp.dps = precision
    half = mpf("0.5")
    four = mpf(4)
    one = mpf(1)
    step_size = mpf(1) / num_steps
    total = mpf(0)
    for i in range(num_steps):
        x = (i + half) * step_size
        total += four / (one + x**2)
    return step_size * total
```

For `num_steps = 1e7`, `double_pi` finishes in a couple of seconds on a typical laptop, while `arbitrary_precision_pi` can take minutes.

*The `% time` excerpts below are illustrative and machine-dependent.*

```text
% time python pi.py
3.141592653589731
python pi.py  1.70s user 0.02s system 95% cpu 1.802 total
```

```text
% time python pi.py
3.1415926535897973
python pi.py  121.73s user 0.18s system 99% cpu 2:02.32 total
```

---

What follows explains how floating-point numbers are laid out in memory, how they are distributed on the number line, and how decimal round-trips relate to “precision” in a stricter sense.

## Floating-point number representation

What follows is written for intuition, not exhaustive IEEE 754 coverage.

 **Subnormal** numbers, **exact zero**, **infinities**, and **NaNs** are not covered.

**Exponent notation.** Write **$E$** for the **biased** exponent, the integer actually stored in the exponent field in memory. Write **$e$** for the **unbiased** (true) exponent used in value formulas for normal numbers. They are related by

$$
e = E - \text{bias}.
$$

As specified by [IEEE 754](https://en.wikipedia.org/wiki/IEEE_754-1985), a floating-point number $N$ consists of three fields: a sign bit $s$, a biased exponent field storing $E$, and a mantissa or significand $m$:

$$
N = (-1)^{s} \cdot 2^{E-\text{bias}} \cdot m
\quad
\begin{cases}
s \in 0, 1 
E \in 0, \ldots, 255 & \text{single precision} 
E \in 0, \ldots, 2047 & \text{double precision}
\end{cases}
$$

where $m$ is normalised such that $m = 1.f$, where $f$ is the fractional part:

$$
f = \sum_{i=1}^{p} b_{i} \cdot (2^{-1})^{i}
\quad
\begin{cases}
p = 23 & \quad \text{single precision} 
p = 52 & \quad \text{double precision} 
b_i \in 0, 1
\end{cases}
$$

**Note:** $m$ can always be normalised by multiplying by the appropriate power of 2 (in other words, by choosing the appropriate pair $(E, f)$).

Therefore

$$
N = (-1)^{s} \cdot 2^{e} \cdot (1 + f).
$$

Only the fractional part of the significand is stored, because the leading 1 is implicit.

The values *“all-0s”* and *“all-1s”* of the exponent field $E$ have special meanings (for example 0, infinity, or NaN).

The bias is

$$
\text{bias} =
\begin{cases}
127 & \quad \text{single precision} 
1023 & \quad \text{double precision}
\end{cases}
$$

Here is the [32-bit memory layout](https://en.wikipedia.org/wiki/IEEE_754-1985#/media/File:IEEE_754_Single_Floating_Point_Format.svg) of a single-precision IEEE 754 float and the [64-bit memory layout](https://en.wikipedia.org/wiki/IEEE_754-1985#/media/File:IEEE_754_Double_Floating_Point_Format.svg) of a double-precision IEEE 754 float.

## Distribution of floating-point numbers on the number line

To explore the distribution of floating-point numbers, it is useful to imagine the number line divided into segments, each segment containing all floating-point numbers that share the same **unbiased** exponent $e$ (hence the same stored $E = e + \text{bias}$).

Each of those segments has the following characteristics:

- contains $2^{p}$ floating-point numbers
- the minimum value in the segment corresponds to a significand with all digits equal to 0
- the maximum value in the segment corresponds to a significand with all digits equal to 1
- two consecutive numbers in the segment differ by 1 unit in the last position of the significand (that's the absolute distance between two consecutive numbers $d_{\text{abs}}$ in that segment)
- two consecutive numbers in different segments differ by a distance $d'*{\text{abs}}$ equal to $d*{\text{abs}}$ of the smaller segment
- the maximum relative distance in a segment is the absolute distance divided by the minimum number in the segment

$$
\min = 2^{e}
$$

$$
\max = 2^{e} \left(1+\sum_{i=1}^{p}{2^{-i}}\right) = 2^{e} \sum_{i=0}^{p}{2^{-i}}
$$

Applying the formula for the sum of the first $n$ terms of a geometric progression:

$$
\max = 2^{e} \cdot 2 \left(1-2^{-p-1}\right)
$$

$$
\text{length} = \max - \min = 2^{e} \left(1 - 2^{-p}\right) \approx 2^{e}
$$

$$
d_{\text{abs}} = 2^{e} \cdot 2^{-p} = 2^{e-p}
$$

$$
d'*{\text{abs}} = \min*{e+1} - \max_e = 2^{e+1} - 2^{e} \cdot 2 \left(1-2^{-p-1}\right) = 2^{e-p}
$$

$$
d_{\text{rel}} = \frac{d_{\text{abs}}}{\min} = 2^{-p}
$$

The maximum relative distance is a function of the precision $p$ only and therefore remains constant across all segments. Thanks to this property, the relative error from rounding a real number to the nearest floating-point number will never be greater than a given constant often discussed under the name [machine epsilon](https://en.wikipedia.org/wiki/Machine_epsilon). The relative gap between adjacent floats in a segment is $d_{\text{rel}} = 2^{-p}$; many texts define $\varepsilon_{\mathrm{mach}} = 2^{-p}$ (e.g. the spacing “at 1.0” in binary64). Here we reserve $\varepsilon$ for the **round-to-nearest** bound: the absolute rounding error is at most half the gap between consecutive numbers, so

$$
\varepsilon = \frac{\frac{d_{\text{abs}}}{2}}{\min} = 2^{-p-1}
$$

i.e. half the relative ULP width in a segment. All the above identities apply to the binary representation of floating-point numbers. When applied to their decimal representation, they may differ depending on the representative chosen.

All of the above can be summarised as follows: each floating-point segment is scaled up by a factor of 2 (as if the segment were stretched) to create the next one so that

- the value of each floating-point number is doubled
- the distances in the new segment are doubled

This way, floating-point numbers become further apart ($d_{\text{abs}}$ increases) so that relative distances stay the same.

This contrasts with [fixed-point arithmetic](https://en.wikipedia.org/wiki/Fixed-point_arithmetic) whereby the absolute distance between representable values is constant, so the relative distance is inversely proportional to the magnitude of the numbers.

Some example segments in double-precision format (column $e$ is the unbiased exponent):


| $e$ | min                  | max                  | $d_{\text{abs}}$ |
| --- | -------------------- | -------------------- | ---------------- |
| 50  | 1125899906842624.0   | 2251799813685247.75  | 0.25             |
| 51  | 2251799813685248.0   | 4503599627370495.5   | 0.5              |
| 52  | 4503599627370496.0   | 9007199254740991.0   | 1.0              |
| 53  | 9007199254740992.0   | 18014398509481982.0  | 2.0              |
| 54  | 18014398509481984.0  | 36028797018963964.0  | 4.0              |
| 55  | 36028797018963968.0  | 72057594037927928.0  | 8.0              |
| 56  | 72057594037927936.0  | 144115188075855856.0 | 16.0             |
| 57  | 144115188075855872.0 | 288230376151711712.0 | 32.0             |
| 58  | 288230376151711744.0 | 576460752303423424.0 | 64.0             |


For values of $e \geq 53$, the distance between consecutive floating-point numbers satisfies $d_{\text{abs}} \geq 2$, so some integers must be rounded to the corresponding floating-point number. **Every** integer in $[-2^{53}, 2^{53}]$ is represented exactly in double precision (the usual contiguous **safe integer** range); outside that interval, not every integer is exact, though some larger integers still happen to coincide with a representable value.

That has practical consequences. Languages such as JavaScript, which represent all numbers as double-precision floats, guarantee exact integer arithmetic only for integers in that interval (the `Number.MIN_SAFE_INTEGER` / `MAX_SAFE_INTEGER` range). Languages such as Java, which have a distinct 64-bit `long` type, can represent integers up to $2^{63}-1$. When a Java service sends a large integer to a Node.js consumer, you might see an error like:

```json
{
    "errors": [
        {
            "code": "400",
            "message": "\"id\" must be a safe number"
        }
    ]
}
```

## Decimal round-trips and precision

As in [Precision](#precision) above, *precision* was described as “the ability to tell apart numbers arbitrarily close to each other.”

The more floating-point values are defined, the more real numbers can be distinguished.

However, no finite set of floating-point numbers can match the continuum of real numbers. Rounding real numbers to floating-point can be viewed as a [surjective](https://en.wikipedia.org/wiki/Surjective_function) map $f$ in which many real numbers map to the same floating-point value. 

As a result, among all real numbers $\{r\}$ such that $f(r) = FP$, only one can be recovered when applying the inverse function. For all others, $f^{-1}(f(r)) \neq r$. 

And this is one of the reasons why floating-point numbers are confusing.

This undesirable behaviour can be avoided by defining precision as the number of digits $d$ such that all [d-digit numbers can be uniquely identified and therefore round-trip](https://www.exploringbinary.com/decimal-precision-of-binary-floating-point-numbers) so that $f^{-1}(f(r)) = r$.

The value of $d$ is determined by the scale of $d_{abs}$ in the corresponding interval $e$: intuitively, the least significant digit of the $d$-digit decimal must be at least one order of magnitude greater than $d_{abs}$.

It can be proved that in double precision, the maximum $d$ that works across the entire domain of reals is [15 digits](https://www.exploringbinary.com/number-of-digits-required-for-round-trip-conversions/) (whereas in single precision it is 6). In particular exponent bands, a larger $d$ may suffice.

__Note__: some floating-point numbers may not correspond to any $d$-digit decimal, in other words, every $d$-digit decimal maps to some floating-point number but not every floating-point number is mapped by a $d$-digit decimal.

### Study cases

#### Precision of a segment

The integers in the interval $7.2057594037927900\times10^{16}, \ldots, 7.2057594037928000\times10^{16}$ all have 17 digits.

The floating-point numbers in that interval are:

$7.2057594037927904\times10^{16}, 7.2057594037927912\times10^{16}, 7.2057594037927920\times10^{16}, 7.2057594037927928\times10^{16}, 7.2057594037927936\times10^{16}, 7.2057594037927952\times10^{16}, 7.2057594037927968\times10^{16}, 7.2057594037927984\times10^{16}, 7.2057594037928000\times10^{16}$.

Several decimals therefore collapse to the same float, for example:

- $7.2057594037927909\times10^{16}, \ldots, 7.2057594037927915\times10^{16} \rightarrow 7.2057594037927912\times10^{16}$
- $7.2057594037927945\times10^{16}, \ldots, 7.2057594037927959\times10^{16} \rightarrow 7.2057594037927952\times10^{16}$

With 16-digit numbers, some values still collide:

- $7.205759403792796\times10^{16}, 7.205759403792797\times10^{16} \rightarrow 7.2057594037927968\times10^{16}$

With 15-digit precision, the integers in the interval reduce to $7.20575940379279\times10^{16}, 7.20575940379280\times10^{16}$, where:

- $7.20575940379279\times10^{16} \rightarrow 7.2057594037927904\times10^{16}$
- $7.20575940379280\times10^{16} \rightarrow 7.2057594037928000\times10^{16}$

and every other float in the interval is “orphan”: no 15-digit decimal maps to it.

Intuitively, precision in a given interval is the number of decimal digits corresponding to one order of magnitude finer than the spacing $d_{\text{abs}}$ between consecutive floats in that interval. Here the order of magnitude of $d_{\text{abs}}$ is tens, and 15 digits give precision at the scale of hundreds.

#### Precision of an individual number

Even within a 15-digit “segment” discussion, the number $7.2057594037927945\times10^{16}$ effectively needs 17 digits of decimal context, because the 17th digit decides which float is produced:

- $7.2057594037927945\times10^{16} \rightarrow 72057594037927952$

Without the last digit:

- $7.205759403792794\times10^{16} \rightarrow 72057594037927936$

#### How to calculate precision of an individual number

In general, the precision of an arbitrary decimal is the length of the *shortest* representative that round-trips.

For example, the 19-digit $n = 1023.999999999999887$ maps to some float $FP_n$. Truncating digits gives:

- 19 digits: $1023.999999999999887 \rightarrow FP_n$
- 18 digits: $1023.99999999999988 \rightarrow FP_n$
- 17 digits: $1023.9999999999998 \nrightarrow FP_n$

Yet this other 17-digit decimal still maps to $FP_n$:

- 17 digits: $1023.9999999999999 \rightarrow FP_n$

No 16-digit decimal maps to $FP_n$. If the 17-digit candidate round-trips, it is the representative. The exact decimal rounded to 17 digits recovers that string:

- $1023.9999999999999$
- $1023.9999999999998\mid863131622783839702606201171875$ (exact tail shown for context)

The precision is therefore 17 digits—consistent with Python’s `float` parsing and string conversion:

```python
>>> float(1023.999999999999887)
1023.9999999999999
```

Here $FP_n$ is the last float in the band with $e = 9$.

Although $1023.999999999999887$ has 17 significant digits, *segment* precision in that band is at most 16 digits in the sense that not all 17-digit decimals in the band can be distinguished. For instance, these two 17-digit decimals share a float:

- $1023.0000000000004$
- $1023.0000000000005$

and only one of them will round-trip:

```python
>>> float(1023.0000000000004)
1023.0000000000005
>>> float(1023.0000000000005)
1023.0000000000005
```

There is thus a distinction between **precision of an individual decimal** (minimum digits to identify its float) and **precision in a segment** (maximum digits such that all decimals of that length in the band map to distinct floats).



