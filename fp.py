#!/usr/bin/env python3
"""
Floating Point utilities for exact decimal representation
"""

from decimal import Decimal

class FloatingPointInfo:
    """Class to hold floating point information including exact decimal representation."""
    
    def __init__(self, value):
        """Initialize with a float value and compute exact decimal representation."""
        self.original_value = value
        # Convert float to exact decimal representation
        self.exact_decimal = str(Decimal(str(value)))

def from_float(value):
    """
    Convert a float to a FloatingPointInfo object with exact decimal representation.
    
    Args:
        value: Float value to convert
        
    Returns:
        FloatingPointInfo object with exact_decimal attribute
    """
    return FloatingPointInfo(value)