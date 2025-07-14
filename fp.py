"""High-level functions to manipulate floating-point numbers
"""

from decimal import ROUND_HALF_UP, Decimal, setcontext, Context
from math import log2, log10, floor
from typing import List, Tuple, Generator
from fputil import unpack_double_precision_fp, check_infinity_or_nan, from_decimal_to_binary, next_binary_fp

setcontext(Context(prec=400, rounding=ROUND_HALF_UP))


class FP:
    """Class representing a double-precision floating-point number, with the following attributes:
    - fp: the decimal value selected by Python as representative of the floating-point number
    - bits: the binary representation of the floating-point number
    - exact_decimal: the exact decimal representation of the floating-point number
    - unbiased_exp: the unbiased exponent of the floating-point number

     Regarding 'fp' attribute:
     - historically, the Python prompt and built-in repr() function would choose the representative with 17 significant digits, 0.10000000000000001. 
    Starting with Python 3.1, Python (on most systems) is now able to choose the shortest of these and simply display 0.1.
    - Python automatically displays floating-point numbers in exponential notation when the absolute value of the number is either 
    very large (greater than or equal to 1e16) or very small (less than 1e-4 and not equal to zero).

    References:
    - https://docs.python.org/3/tutorial/floatingpoint.html
    - https://www.exploringbinary.com/number-of-decimal-digits-in-a-binary-fraction/
    """

    def __init__(self, fp: float, bits: str, exact_decimal: Decimal, unbiased_exp: int):
        self.fp = fp
        self.bits = bits
        self.exact_decimal = exact_decimal
        self.unbiased_exp = unbiased_exp

    def __repr__(self):
        return f"FP(float={self.fp}, bits={self.bits}, exact_decimal={self.exact_decimal}, unbiased_exp={self.unbiased_exp})"

    def __eq__(self, other):
        return self.fp == other.fp and self.bits == other.bits and self.exact_decimal == other.exact_decimal and self.unbiased_exp == other.unbiased_exp

    def next(self) -> "FP":
        """Return the next double-precision floating-point number
        """
        return FP.from_binary(next_binary_fp(self.bits))

    def fp_gen(self) -> Generator["FP", None, None]:
        """Return a generator of consecutive FP objects in ascending order and starting from this FP
        In case of reaching the values "Infinity" or "NaN", the generator throws an OverflowError.
        """
        fp = self
        assert fp.fp >= 0, "seed must be positive or zero"
        while True:
            yield fp
            fp = fp.next()

    def get_d_digit_decimals(self, d: int):
        """Return the list of d-digit decimal numbers that map to the given double-precision floating-point number
        The list is ordered in ascending order

        Args:
            fp (FP): double-precision floating-point number
            d (int): number of significant digits to be considered

        Returns:
            tuple[int, Decimal, list[Decimal]]: number of d-digit decimal numbers that map to the given double-precision floating-point number, 
            the distance between consecutive d-digit numbers, and the list of numbers
        """
        _, digits, exp = self.exact_decimal.normalize().as_tuple()
        match exp:
            case str(exp):
                raise ValueError("dec must be a finite number")
            case _:
                exp = int(exp)

        dec_len = len(digits)
        # distance between consecutive d-digit numbers
        # when dec_len == -exp, the leading 0 is dropped, so we need to adjust the distance accordingly
        distance = Decimal(10)**(exp + dec_len - (d-1 if exp + dec_len == 0 else d))

        # first d-digit number smaller than the given number
        lower_d_digit_number = Decimal(f"{str(self.exact_decimal)[:(d if exp >= 0 else d+1)]}{'0' * (dec_len - d)}")
        # first d-digit number greater than the given number
        upper_d_digit_number = lower_d_digit_number + distance

        numbers = []
        # checking d-digit numbers smaller than the given number
        while float(lower_d_digit_number) == self.fp:
            numbers.append(lower_d_digit_number.normalize(Context(prec=d)))
            lower_d_digit_number -= distance

        # checking d-digit numbers greater than the given number
        while float(upper_d_digit_number) == self.fp:
            numbers.append(upper_d_digit_number.normalize(Context(prec=d)))
            upper_d_digit_number += distance

        return (len(numbers), distance, sorted(numbers))

    @staticmethod
    def get_number_significant_digits(decimal: str) -> int:
        """Return the number of significant digits of a decimal number.
        
        Precision of an individual decimal number defined as the minimum amount of digits to identify its floating-point number.

        Recursive implementation: on each iteration, the number of digits is reduced by one until the resulting decimal number
        points to a different floating-point number.
        """

        fp = FP.from_decimal(Decimal(decimal)).fp

        def truncate(aux_decimal: Decimal, d: int) -> int:
            _, digits, exp = aux_decimal.normalize().as_tuple()
            match exp:
                case str(exp):
                    raise ValueError("dec must be a finite number")
                case _:
                    exp = int(exp)

            dec_len = len(digits)

            # first d-digit number smaller than the given number
            lower_d_digit_number = Decimal(f"{str(aux_decimal)[:(d if exp >= 0 else d+1)]}{'0' * (dec_len - d)}")
            if float(lower_d_digit_number) == fp:
                return truncate(lower_d_digit_number, d - 1)
            return d + 1

        return truncate(Decimal(decimal), len(decimal))


    @staticmethod
    def from_decimal(dec: Decimal) -> "FP":
        """Return a FP object from the given Decimal number
        """
        return FP.from_float(float(dec))

    @staticmethod
    def from_float(f: float) -> "FP":
        """Return a FP object from the given float number
        """
        bits = from_decimal_to_binary(f)[0]
        return FP.from_binary(bits)

    @staticmethod
    def from_binary(bits: str) -> "FP":
        """Return a FP from the given binary representation       
        """
        sign, fraction_bits, exponent_bits, unbiased_exp = unpack_double_precision_fp(bits)
        check_infinity_or_nan(fraction_bits, exponent_bits)

        half = Decimal(0.5)
        mantissa = Decimal(1)
        for i in range(1, len(fraction_bits) + 1):
            place_value = fraction_bits[i - 1] * half**i
            mantissa += place_value
        exact_decimal = sign * mantissa * Decimal(2)**unbiased_exp
        return FP(float(exact_decimal), bits, exact_decimal, unbiased_exp)


class Segment:
    """Class representing a segment of double-precision floating-point numbers, with the following attributes:
    - unbiased_exp: the unbiased exponent that defines the segment
    - min_val: the minimum floating-point number in the segment represented as an exact decimal
    - max_val: the maximum floating-point number in the segment represented as an exact decimal
    - distance: the distance between consecutive binary floating-point numbers in the segment represented as an exact decimal
    """

    def __init__(self, unbiased_exp: int, min_val: Decimal, max_val: Decimal, distance: Decimal) -> None:
        self.unbiased_exp = unbiased_exp
        self.min_val = min_val
        self.max_val = max_val
        self.distance = distance

    def __repr__(self):
        return f"Segment(unbiased_exp={self.unbiased_exp}, min_val={self.min_val}, max_val={self.max_val}, distance={self.distance})"

    def __eq__(self, other):
        return self.unbiased_exp == other.unbiased_exp and self.min_val == other.min_val and self.max_val == other.max_val and self.distance == other.distance

    @staticmethod
    def from_exponent(e: int, ctx: Context) -> "Segment":
        """Calculate the segment corresponding to the unbiased exponent 'e'
        """
        setcontext(ctx)
        p = 52
        two = Decimal(2)
        min_val: Decimal = two**e
        max_val: Decimal = two**(e + 1) * (1 - two**(-p - 1))
        distance: Decimal = two**(e - p)
        return Segment(e, min_val.normalize(), max_val.normalize(), distance.normalize())

    @staticmethod
    def from_fp(f: float, ctx: Context) -> "Segment":
        """Calculate the segment containing the given floating-point number 'f'    
        """
        bits: str = from_decimal_to_binary(f)[0]
        unbiased_exp: int = unpack_double_precision_fp(bits)[3]
        return Segment.from_exponent(unbiased_exp, ctx)


def get_segments(start: int, end: int, ctx: Context) -> List[Segment]:
    """Return a list of Segment objects corresponding to the unbiased exponents in the interval [start, end-1]
    """
    return [Segment.from_exponent(e, ctx) for e in range(start, end)]


def pretty_print_segments(segments: List[Segment]) -> None:
    max_e = 5
    max_min = max([len(str(segment.min_val)) for segment in segments])
    max_max = max([len(str(segment.max_val)) for segment in segments])
    max_distance = max([len(str(segment.distance)) for segment in segments])

    header = f"| e{'':{max_e-1}}| min{'':{max_min-3}}| max{'':{max_max-3}}| distance{'':{max_distance-len('distance') if len('distance') < max_distance else 1}}|"
    row_separator = f"|{'-' * (max_e + max_min + max_max + max_distance + 12)}|"

    def prettify(r):
        return f"| {r[0]:^{max_e}}| {r[1]:{max_min}}| {r[2]:{max_max}}| {r[3]:{max_distance+5}}|"

    print('\n')
    print(header)
    print(row_separator)
    print("\n".join([prettify(segment) for segment in segments]))
    print('\n')


def tabulate_esegments(start: int, end: int) -> None:
    segments: List[Segment] = get_segments(start, end, Context(prec=400, rounding=ROUND_HALF_UP))
    pretty_print_segments(segments)


def next_n_binary_fp(start: FP, n: int) -> list[FP]:
    """Convenience function to return the next n double-precision floating-point numbers in ascending order

    See next_binary_fp() for more details
    """
    assert n > 0, "n must be a positive integer"
    fp_generator = start.fp_gen()
    return [next(fp_generator) for _ in range(n)]


def identify_surrounding_powers_of_2_and_10(x: float) -> List[Tuple[int, int]]:
    """Given a float, calculate the nearest powers of 10 and 2 and return them in ascending order

    72057594037927956 -> [(10, 16), (2, 56), (10, 17), (2, 57)] that reads: 
    10^16 < 2^56 < 72057594037927956 < 10^17 < 2^57

    https://www.exploringbinary.com/how-the-positive-powers-of-ten-and-two-are-interleaved/
    https://www.exploringbinary.com/7-bits-are-not-enough-for-2-digit-accuracy/
    """
    previous_power_of_2 = floor(log2(x))
    previous_power_of_10 = floor(log10(x))
    next_power_of_2 = previous_power_of_2 + 1
    next_power_of_10 = previous_power_of_10 + 1
    return sorted([(2, previous_power_of_2), (10, previous_power_of_10), (2, next_power_of_2), (10, next_power_of_10)], key=lambda x: x[0]**x[1])


def is_segment_precision(start: Decimal, end: Decimal, d: int) -> bool:
    """Determines whether the precision of the segment [start, end] is 'd' digits

    The precision of the segment is 'd' digits if each d-digit number in the segment maps to
    a different double-precision floating-point number
    """
    generator = FP.from_decimal(start).fp_gen()
    current_fp: FP = next(generator)
    num_mapped_decimals = current_fp.get_d_digit_decimals(d)[0]
    while num_mapped_decimals < 2 and current_fp.exact_decimal < end:
        current_fp = next(generator)
        num_mapped_decimals = current_fp.get_d_digit_decimals(d)[0]

    if num_mapped_decimals < 2:
        return True

    print(f"{num_mapped_decimals} {d}-digit decimals mapped to {current_fp.exact_decimal.normalize()}")
    return False

def print_decimal(fp: FP) -> None:
    _, digits, exp = fp.exact_decimal.normalize().as_tuple()
    print(f"Decimal: {fp.exact_decimal}, digits: {digits}, exp: {exp}, len(digits): {len(digits)}")

if __name__ == "__main__":
    # print(mpf(7.1))
    # print(to_double_precision_floating_point_binary(7.2))
    # print(to_single_precision_floating_point_binary_manual(52))
    # print(double_precision_significant_digits("72057594037927956"))
    # print(identify_range(1023.999999999999887))
    # print(identify_range(72057594037927956))
    # print(segment_params(9, Context(prec=100, rounding=ROUND_HALF_UP)))
    # print(explore_segment_precision(mpf(1023), mpf(1024), mpf(1e-18)))
    # fp_generator = fp_gen(72057594037927870)
    # print(next(fp_generator))
    # print(next(fp_generator))
    # print(next(fp_generator))
    # print(next(fp_generator))
    # print(next(fp_generator))
    # print(next(fp_generator))
    # print(next(fp_generator))
    # print(get_n_fp(72057594037927956, 3))
    # print(normalise_to_significant_digits(72057594037927956, 16))
    # print(normalise_to_significant_digits(0.0454, 1))
    # print(FP.from_float(1023.99999999999988))
    print(FP.from_float(0.1).get_d_digit_decimals(19))
    # print(FP.from_decimal(Decimal(0.1)).get_d_digit_decimals(18))
    # print(FP.get_number_significant_digits("1023.999999999999887"))

    # decimal = 72057594037927945
    # binary_val = to_double_precision_floating_point_binary(decimal)[0]
    # exact_decimal = to_exact_decimal(str_to_list(binary_val))
    # print(decimal)
    # print(binary_val)
    # print(exact_decimal)
    # tabulate_esegments(50,59)
    # print(is_segment_precision(Decimal(72057594037927945), Decimal(72057594037928000), 16))
    # print(Segment.from_fp(1.0, Context(prec=400, rounding=ROUND_HALF_UP)))

    # print_decimal(FP.from_float(0.1))
    # print_decimal(FP.from_float(1.1))
    # print_decimal(FP.from_float(1023.9999999999999))
    # print_decimal(FP.from_float(72057594037927945))
