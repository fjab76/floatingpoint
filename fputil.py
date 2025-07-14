"""Module with functions to manipulate the binary and decimal representations of floating-point 
numbers according to the IEEE 754 standard
"""

import struct
from typing import List, Tuple
from functools import reduce


def str_to_list(s: str) -> List[int]:
    """Convert a string made up of digits into a list of integers

    If any of the characters in the string is not a digit, raise a ValueError

    '1001' --> list[1,0,0,1]
    """
    return [int(digit) for digit in s]


def list_to_str(l: list) -> str:
    """Concatenate the elements of a list into a single string

    list[1,0,0,1] --> '1001'  
    """
    return "".join([str(e) for e in l])


def next_binary_value(bits) -> bool:
    """Add 1 to the given bit pattern 'bits', assuming bits[0] is the MSB (most-significant bit)

    The function modifies the argument in place and returns a boolean to indicate whether there has been overflow (True) or not (False)
    """
    i: int = len(bits) - 1
    while i >= 0 and bits[i] == 1:
        bits[i] = 0
        i -= 1
    if i >= 0:
        bits[i] = 1
        return False

    # overflow
    return True


def unpack_double_precision_fp(bits: str) -> Tuple[int, List[int], List[int], int]:
    """Decompose the binary representation of a double-precision floating-point number 
    into its elements: 
    - sign
    - fraction bits
    - exponent bits
    - unbiased exponent
    """
    exponent_bits = bits[1:12]
    biased_exp = int(exponent_bits, 2)
    double_precision_exponent_bias = 1023
    unbiased_exp = biased_exp - double_precision_exponent_bias
    fraction_bits = bits[12:]
    sign = 1 if bits[0] == '0' else -1
    return (sign, str_to_list(fraction_bits), str_to_list(exponent_bits), unbiased_exp)


def check_infinity_or_nan(fraction: List[int], exponent: List[int]) -> None:
    """Check if the bit pattern corresponds to the special floating-point values 'Infinity' or 'NaN'
    If so, raise an OverflowError, else return None
    """
    # check if exponent is all ones
    if reduce(lambda x, y: bool(x) and bool(y), exponent, True):
        # check if fraction is all zeros
        if not reduce(lambda x, y: bool(x) or bool(y), fraction, False):
            raise OverflowError("Infinity")
        raise OverflowError("NaN")


def from_decimal_to_binary(number: float) -> Tuple[str, str]:
    """Convert a double-precision floating-point number from decimal to binary representation

    from_binary_to_decimal(from_decimal_to_binary(x)) == x

    The floating-point number is returned in binary and hexadecimal format

    7.2 --> ('0100000000011100110011001100110011001100110011001100110011001101', '0x401ccccccccccccd')    
    """
    packed: bytes = struct.pack('>d', number)
    bits: str = ''.join(format(byte, '08b') for byte in packed)
    hexrepr: str = hex(int(bits, 2))
    return (bits, hexrepr)

def next_binary_fp(strbits: str) -> str:
    """Return the binary representation of the next double-precision floating-point number

    Raise OverflowError if the argument or the resulting value is either 'Infinity' or 'NaN'

    Args:
        strbits (str): bit pattern of the original double-precision floating-point number

    Returns:
        list[int]: bit pattern of the next double-precision floating-point number
    """
    _, fraction_bits, exponent_bits, _ = unpack_double_precision_fp(strbits)
    check_infinity_or_nan(fraction_bits, exponent_bits)

    bits: List[int] = str_to_list(strbits)
    if next_binary_value(fraction_bits):
        # overflow in fraction, increase exponent
        next_binary_value(exponent_bits)
        check_infinity_or_nan(fraction_bits, exponent_bits)

    bits[12:] = fraction_bits
    bits[1:12] = exponent_bits
    return "".join([str(e) for e in bits])
