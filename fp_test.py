import pytest
from fp import *
# from sp_fp import *
from fputil import *


def test_next_binary_value_overflow():  # [missing-function-docstring]
    bits = [1, 1, 1]
    assert next_binary_value(bits)


def test_next_binary_value_success():
    bits = [1, 0, 1]
    assert not next_binary_value(bits)
    assert bits == [1, 1, 0]


def test_next_binary_fp_increase_fraction():
    bits = \
        "0011111111110011001100110011001100110011001100110011001100110011"
    bits = next_binary_fp(bits)
    assert bits == "0011111111110011001100110011001100110011001100110011001100110100"


def test_next_binary_fp_increase_exponent():
    bits = \
        "0011111111111111111111111111111111111111111111111111111111111111"
    bits = next_binary_fp(bits)
    assert bits == "0100000000000000000000000000000000000000000000000000000000000000"


def test_next_binary_fp_argument_overflow():
    try:
        bits = \
            "0111111111110011001100110011001100110011001100110011001100110011"
        bits = next_binary_fp(bits)
        assert False
    except OverflowError as e:
        assert e.args[0] == "NaN"


def test_next_binary_fp_result_overflow():
    try:
        bits = \
            "0111111111101111111111111111111111111111111111111111111111111111"
        bits = next_binary_fp(bits)
        assert False
    except OverflowError as e:
        assert e.args[0] == "Infinity"


@pytest.mark.parametrize(
    "bits,expected,expected_message",
    [
        ("0011111111110011001100110011001100110011001100110011001100110011", FP(1.2, "0011111111110011001100110011001100110011001100110011001100110011", Decimal('1.1999999999999999555910790149937383830547332763671875'), 0), None),
        ("1011111111110011001100110011001100110011001100110011001100110011", FP(-1.2, "1011111111110011001100110011001100110011001100110011001100110011", Decimal('-1.1999999999999999555910790149937383830547332763671875'), 0), None),
        ("1111111111110011001100110011001100110011001100110011001100110011", OverflowError, "NaN"),
        ("1111111111110000000000000000000000000000000000000000000000000000", OverflowError, "Infinity"),
    ]
)
def test_from_binary(bits, expected, expected_message):
    if isinstance(expected, type) and issubclass(expected, OverflowError):
        with pytest.raises(expected, match=expected_message) as exc_info:
            FP.from_binary(bits)
        assert exc_info.value.args[0] == expected_message
    else:
        assert FP.from_binary(bits) == expected


def test_fp_gen():
    fp_generator = FP.from_float(0.00000000000012343).fp_gen()
    assert next(fp_generator) == \
        FP(0.00000000000012343, "0011110101000001010111110000100011001111011111011000010001010000", Decimal('0.0000000000001234300000000000102340991445314016317948146994609714965918101370334625244140625'), -43)
    assert next(fp_generator) == \
        FP(0.00000000000012343000000000004, "0011110101000001010111110000100011001111011111011000010001010001", Decimal('0.00000000000012343000000000003547764811160377940497012878851013084613441606052219867706298828125'), -43)


def test_fp_gen_infinity():
    fp_generator = FP.from_float(1.7976931348623157e+308).fp_gen()
    assert next(fp_generator) == FP(1.7976931348623157e+308, "0111111111101111111111111111111111111111111111111111111111111111", Decimal('179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368'), 1023)
    try:
        next(fp_generator)
        assert False
    except OverflowError as e:
        assert e.args[0] == "Infinity"



ctx = Context(prec=100, rounding=ROUND_HALF_UP)


@pytest.mark.parametrize(
    "data,expected",
    [
        ((9, ctx), Segment(9, Decimal('512'), Decimal('1023.9999999999998863131622783839702606201171875'), Decimal('1.136868377216160297393798828125E-13'))),
        ((52, ctx), Segment(52, Decimal('4503599627370496'), Decimal('9007199254740991'), Decimal('1'))),        
    ]
)
def test_segment_from_exponent(data, expected):
    assert Segment.from_exponent(*data) == expected

@pytest.mark.parametrize(
    "data,expected",
    [        
        ((1023.0, ctx), Segment(9, Decimal('512'), Decimal('1023.9999999999998863131622783839702606201171875'), Decimal('1.136868377216160297393798828125E-13'))),
        ((4503599627370497.0, ctx), Segment(52, Decimal('4503599627370496'), Decimal('9007199254740991'), Decimal('1')))
    ]
)
def test_segment_from_fp(data, expected):
    assert Segment.from_fp(*data) == expected


@pytest.mark.parametrize(
    "value,d,expected_count,expected_distance,expected_numbers",
    [        
        (
            0.1, # value
            18, # num digits
            2, # count
            Decimal('1E-17'), # distance
            [
                Decimal('0.10000000000000000'),
                Decimal('0.10000000000000001')
            ]
        ), 
        (
            0.01, # value
            17, # num digits
            2, # count
            Decimal('1E-18'), # distance
            [
                Decimal('0.010000000000000000'),
                Decimal('0.010000000000000001')
            ]
        ), 
        (
            1.1, # value
            17, # num digits
            2, # count
            Decimal('1E-16'), # distance
            [
                Decimal('1.1000000000000000'),
                Decimal('1.1000000000000001')
            ]
        ),           
        (
            1023.99999999999983, # value
            18, # num digits
            12, # count
            Decimal('1E-14'), # distance
            [
                Decimal('1023.99999999999983'),
                Decimal('1023.99999999999984'),
                Decimal('1023.99999999999985'),
                Decimal('1023.99999999999986'),
                Decimal('1023.99999999999987'),
                Decimal('1023.99999999999988'),
                Decimal('1023.99999999999989'),
                Decimal('1023.99999999999990'),
                Decimal('1023.99999999999991'),
                Decimal('1023.99999999999992'),
                Decimal('1023.99999999999993'),
                Decimal('1023.99999999999994')
            ]
        ),        
        (
            72057594037927945, # value
            17, # num digits
            15, # count
            1, # distance            
            [
                Decimal('72057594037927945'),
                Decimal('72057594037927946'),
                Decimal('72057594037927947'),
                Decimal('72057594037927948'),
                Decimal('72057594037927949'),
                Decimal('72057594037927950'),
                Decimal('72057594037927951'),
                Decimal('72057594037927952'),
                Decimal('72057594037927953'),
                Decimal('72057594037927954'),
                Decimal('72057594037927955'),
                Decimal('72057594037927956'),
                Decimal('72057594037927957'),
                Decimal('72057594037927958'),
                Decimal('72057594037927959')
            ]
        ),
        (
            72057594037927945, # value
            16, # num digits
            1, # count
            10, # distance            
            [
                Decimal('7.205759403792795E+16')
            ]
        )
    ]
)
def test_get_d_digit_decimals(value, d, expected_count, expected_distance, expected_numbers):
    fp = FP.from_float(value)
    count, distance, numbers = fp.get_d_digit_decimals(d)
    assert count == expected_count
    assert distance == expected_distance
    # Compare as strings to avoid Decimal context/precision issues
    assert [str(n) for n in numbers] == [str(n) for n in expected_numbers]


def test_get_d_digit_decimals_invalid_decimal():
    class DummyFP(FP):
        def __init__(self):
            # exp as string to trigger ValueError
            self.fp = 1.0
            self.bits = "0" * 64
            self.exact_decimal = Decimal("NaN")
            self.unbiased_exp = 0

    dummy = DummyFP()
    with pytest.raises(ValueError, match="dec must be a finite number"):
        dummy.get_d_digit_decimals(5)

