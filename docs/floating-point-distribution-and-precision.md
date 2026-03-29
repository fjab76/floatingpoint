# Floating-point distribution and precision

*Pedagogic notes adapted from [bytecode.tech](https://blog.bytecode.tech/).*

Following up on the introductory article [Understanding floating-point numbers](https://blog.bytecode.tech/understanding-floating-point-numbers/), the goal of this material is to be able to visualise the distribution of floating-point numbers. To do that, it is necessary first to learn how floating-point numbers are represented in memory.

**Scope (deliberate simplification).** What follows is written for intuition, not exhaustive IEEE 754 coverage. The spacing and “segment” picture treats **normalised finite** values as the main case: implicit leading one, evenly spaced numbers within an exponent band, and the usual $2^p$ count per band. **Subnormal** numbers, **exact zero**, **infinities**, and **NaNs** change edge behaviour and formulas near the underflow threshold; they are mentioned only where the narrative needs them. Trading some rigor for clarity is intentional—once the mental model sticks, the full standard completes the picture.

## Floating-point number representation

**Exponent notation.** Write **$E$** for the **biased** exponent—the integer actually stored in the exponent field. Write **$e$** for the **unbiased** (true) exponent used in value formulas for normal numbers. They are related by

$$
e = E - \text{bias}.
$$

The same symbol $e$ appears later in segment spacing ($\min = 2^e$, and so on); there it always means this unbiased exponent.

As specified by [IEEE 754](https://en.wikipedia.org/wiki/IEEE_754-1985), a floating-point number $N$ consists of three fields: a sign bit $s$, a biased exponent field storing $E$, and a mantissa or significand $m$:

$$
N = (-1)^{s} \cdot 2^{E-\text{bias}} \cdot m
\quad
\begin{cases}
s \in \{0, 1\} \\
E \in \{0, \ldots, 255\} & \text{single precision} \\
E \in \{0, \ldots, 2047\} & \text{double precision}
\end{cases}
$$

where $m$ is normalised such that $m = 1.f$, where $f$ is the fractional part:

$$
f = \sum_{i=1}^{p} b_{i} \cdot (2^{-1})^{i}
\quad
\begin{cases}
p = 23 & \quad \text{single precision} \\
p = 52 & \quad \text{double precision} \\
b_i \in \{0, 1\}
\end{cases}
$$

**Note:** $m$ can always be normalised by multiplying by the appropriate power of 2 (in other words, by choosing the appropriate pair $(E, f)$).

For **normal** numbers, substitute $e = E - \text{bias}$ and $m = 1 + f$:

$$
N = (-1)^{s} \cdot 2^{e} \cdot (1 + f).
$$

Only the fractional part of the significand is stored, because the leading 1 is implicit.

The values *“all-0s”* and *“all-1s”* of the exponent field $E$ have special meanings (for example 0, infinity, or NaN) and are excluded from the normal-number picture above.

The bias is

$$
\text{bias} =
\begin{cases}
127 & \quad \text{single precision} \\
1023 & \quad \text{double precision}
\end{cases}
$$

Here is the [32-bit memory layout](https://en.wikipedia.org/wiki/IEEE_754-1985#/media/File:IEEE_754_Single_Floating_Point_Format.svg) of a single-precision IEEE 754 float and the [64-bit memory layout](https://en.wikipedia.org/wiki/IEEE_754-1985#/media/File:IEEE_754_Double_Floating_Point_Format.svg) of a double-precision IEEE 754 float.

## Distribution of floating-point numbers on the number line

To explore the distribution of floating-point numbers, it is useful to imagine the number line divided into segments, each segment containing all floating-point numbers that share the same **unbiased** exponent $e$ (hence the same stored $E = e + \text{bias}$ for normals).

Each of those segments has the following characteristics:

- contains $2^{p}$ floating-point numbers
- the minimum value in the segment corresponds to a significand with all digits equal to 0
- the maximum value in the segment corresponds to a significand with all digits equal to 1
- two consecutive numbers in the segment differ by 1 unit in the last position of the significand (call the absolute distance between two consecutive numbers $d_{\text{abs}}$)
- two consecutive numbers in different segments differ by a distance $d'_{\text{abs}}$ equal to $d_{\text{abs}}$ of the smaller segment
- the maximum relative distance is the absolute distance divided by the minimum number in the segment

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
d'_{\text{abs}} = \min_{e+1} - \max_e = 2^{e+1} - 2^{e} \cdot 2 \left(1-2^{-p-1}\right) = 2^{e-p}
$$

$$
d_{\text{rel}} = \frac{d_{\text{abs}}}{\min} = 2^{-p}
$$

The maximum relative distance is a function of the precision $p$ only and therefore remains constant across all segments. Thanks to this property, the relative error from rounding a real number to the nearest floating-point number will never be greater than a given constant called [machine epsilon](https://en.wikipedia.org/wiki/Machine_epsilon). The absolute rounding error is at most half the gap between consecutive numbers, so

$$
\varepsilon = \frac{\frac{d_{\text{abs}}}{2}}{\min} = 2^{-p-1}
$$

All the above identities apply to the binary representation of floating-point numbers. When applied to their decimal representation, they may differ depending on the representative chosen.

All of the above can be summarised as follows: each floating-point segment is scaled up by a factor of 2 (as if the segment were stretched) to create the next one so that

- the value of each floating-point number is doubled
- the distances in the new segment are doubled

This way, floating-point numbers become further apart ($d_{\text{abs}}$ increases) so that relative distances stay the same.

This contrasts with [fixed-point arithmetic](https://en.wikipedia.org/wiki/Fixed-point_arithmetic) whereby the absolute distance between representable values is constant, so the relative distance is inversely proportional to the magnitude of the numbers.

Some example segments in double-precision format (column $e$ is the unbiased exponent):

| $e$ | min | max | $d_{\text{abs}}$ |
|------------------|-----|-----|--------------------|
| 50 | 1125899906842624.0 | 2251799813685247.75 | 0.25 |
| 51 | 2251799813685248.0 | 4503599627370495.5 | 0.5 |
| 52 | 4503599627370496.0 | 9007199254740991.0 | 1.0 |
| 53 | 9007199254740992.0 | 18014398509481982.0 | 2.0 |
| 54 | 18014398509481984.0 | 36028797018963964.0 | 4.0 |
| 55 | 36028797018963968.0 | 72057594037927928.0 | 8.0 |
| 56 | 72057594037927936.0 | 144115188075855856.0 | 16.0 |
| 57 | 144115188075855872.0 | 288230376151711712.0 | 32.0 |
| 58 | 288230376151711744.0 | 576460752303423424.0 | 64.0 |

For values of $e \geq 53$, the distance between consecutive floating-point numbers satisfies $d_{\text{abs}} \geq 2$, so some integers must be rounded to the corresponding floating-point number. Therefore, only integers in the interval $[-2^{53}, 2^{53}]$ can be represented exactly.

That has practical consequences. Languages such as JavaScript, which represent all numbers as double-precision floats, can only represent integers in that interval exactly. Languages such as Java, which have a distinct 64-bit `long` type, can represent integers up to $2^{63}-1$. When a Java service sends a large integer to a Node.js consumer, you might see an error like:

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

## Precision revisited

In the previous post [Understanding floating-point numbers](https://blog.bytecode.tech/understanding-floating-point-numbers/), *precision* was described as “the ability to tell apart numbers arbitrarily close to each other.”

The more floating-point values are defined, the more real numbers can be distinguished in that sense.

However, no finite set of floating-point numbers can match the continuum of real numbers. Rounding real numbers to floating-point can be viewed as a [surjective](https://en.wikipedia.org/wiki/Surjective_function) function $f$ in which many reals map to the same floating-point value (many inputs, one output float).

That raises the question of how to define an inverse $f^{-1}$. Among all reals $\{r\}$ such that $f(r) = \text{FP}$, only one can be recovered when applying the inverse; for all others, $f^{-1}(f(r)) \neq r$. This is one reason floating-point behaviour can be confusing: $r$ is transformed into the binary representation of the corresponding float and back to decimal for display, and the displayed value may differ from the original.

That behaviour can be mitigated by defining precision as the number of digits $d$ such that all [d-digit decimal numbers uniquely identify and round-trip](https://www.exploringbinary.com/decimal-precision-of-binary-floating-point-numbers/) their float: $f^{-1}(f(r)) = r$.

A $d$-digit number *round-trips* if, when converted to binary and back to decimal with rounding to nearest at $d$ digits, the original $d$-digit string is recovered.

A round-trip from decimal to binary and back can therefore yield a different decimal string than the one you started with, even when both strings denote the same float.

The only way to recover the original decimal representation is to turn that surjective map into an [injective](https://en.wikipedia.org/wiki/Injective_function) one: at most one allowed decimal input per float.

To do that, restrict to a subset of the reals by limiting the number $d$ of digits in the decimal representation. That limit is tied to the scale $d_{\text{abs}}$ of floating-point numbers in the corresponding exponent band $e$: the least significant decimal digit must be at least one order of magnitude larger than $d_{\text{abs}}$.

It can be proved that in double precision, the maximum $d$ that works across the entire domain of reals is [15 digits](https://www.exploringbinary.com/number-of-digits-required-for-round-trip-conversions/) (whereas in single precision it is 6). In particular exponent bands, a larger $d$ may suffice.

After making $f$ injective, some floats may not correspond to any $d$-digit decimal: every $d$-digit decimal maps to some float, but not every float has a $d$-digit decimal representative.

### Study cases

#### Precision of a segment

The integers in the interval $\{7.2057594037927900\times10^{16}, \ldots, 7.2057594037928000\times10^{16}\}$ all have 17 digits.

The floating-point numbers in that interval are:

$\{7.2057594037927904\times10^{16},\, 7.2057594037927912\times10^{16},\, 7.2057594037927920\times10^{16},\, 7.2057594037927928\times10^{16},\, 7.2057594037927936\times10^{16},\, 7.2057594037927952\times10^{16},\, 7.2057594037927968\times10^{16},\, 7.2057594037927984\times10^{16},\, 7.2057594037928000\times10^{16}\}$.

Several decimals therefore collapse to the same float, for example:

- $\{7.2057594037927909\times10^{16}, \ldots, 7.2057594037927915\times10^{16}\} \rightarrow 7.2057594037927912\times10^{16}$
- $\{7.2057594037927945\times10^{16}, \ldots, 7.2057594037927959\times10^{16}\} \rightarrow 7.2057594037927952\times10^{16}$

With 16-digit numbers, some values still collide:

- $\{7.205759403792796\times10^{16},\, 7.205759403792797\times10^{16}\} \rightarrow 7.2057594037927968\times10^{16}$

With 15-digit precision, the integers in the interval reduce to $\{7.20575940379279\times10^{16},\, 7.20575940379280\times10^{16}\}$, where:

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

Here $FP_n$ is the last float in the band with $e = 9$, where $d_{\text{abs}} = 0.0000000000001136868377216160297393798828125$. Aligning $n$ and $d_{\text{abs}}$, the order of magnitude just above $d_{\text{abs}}$ lines up with the 16th digit of $n$:

```
1023.999999999999|887
       0.000000000000|1136868377216160297393798828125
```

So although $1023.999999999999887$ has 17 significant digits, *segment* precision in that band is at most 16 digits in the sense that not all 17-digit decimals in the band can be distinguished. For instance, these two 17-digit decimals share a float:

- $1023.0000000000004$
- $1023.0000000000005$

and only one of them will round-trip:

```python
>>> float(1023.0000000000004)
1023.0000000000005
>>> float(1023.0000000000005)
1023.0000000000005
```

(Both literals parse to the same IEEE-754 binary64 value on typical Python builds; the original blog post showed a different first line, likely a transcription typo.)

Another formulation: all 16-digit decimals in that neighbourhood can map to distinct floats, but not every float has a 16-digit decimal representative.

There is thus a distinction between **precision of an individual decimal** (minimum digits to identify its float) and **precision in a segment** (maximum digits such that all decimals of that length in the band map to distinct floats).

---

## Notes for maintainers

- **Math rendering:** This file uses `$...$` for inline math and `$$...$$` for display math, which [GitHub-flavoured Markdown](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions) supports in `.md` files. Other viewers may need MathJax or KaTeX.
- **Figures:** None are embedded; the narrative that referred to diagrams from the original blog is now text-only. Add images under `docs/assets/` and link them here if you want visuals again.
- The **JSON error** example is illustrative of JavaScript “safe integer” validation, not specific to this repository’s API.
