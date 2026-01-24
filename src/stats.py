"""
Basic Statistics Functions

This module provides implementations for common statistical operations
including mean, median, mode, and standard deviation. It is designed
to be robust, handling edge cases such as empty lists and non-numeric
inputs.
"""

import math
from typing import List, Union, Any, Tuple

# Define a numeric type for type hinting
Number = Union[int, float]


def _validate_numeric_data(data: List[Any]) -> List[Number]:
    """
    Internal helper to validate that data is a non-empty list of numbers.

    Args:
        data: A list of values to be validated.

    Returns:
        The original list if valid.

    Raises:
        ValueError: If the list is empty or contains non-numeric values.
    """
    if not data:
        raise ValueError("Input data cannot be empty.")
    
    if not all(isinstance(x, (int, float)) for x in data):
        raise ValueError("All elements in data must be numeric (int or float).")
        
    return data


def mean(data: List[Number]) -> float:
    """
    Calculates the arithmetic mean (average) of a list of numbers.

    Args:
        data: A list of numbers (int or float).

    Returns:
        The arithmetic mean as a float.

    Raises:
        ValueError: If the input list is empty or contains non-numeric values.
    """
    _validate_numeric_data(data)
    return sum(data) / len(data)


def median(data: List[Number]) -> float:
    """
    Calculates the median (middle value) of a list of numbers.

    Args:
        data: A list of numbers (int or float).

    Returns:
        The median value as a float. If the list has an even number of
        elements, the median is the average of the two middle numbers.

    Raises:
        ValueError: If the input list is empty or contains non-numeric values.
    """
    _validate_numeric_data(data)
    
    # Create a sorted copy to avoid modifying the original list
    sorted_data = sorted(data)
    n = len(sorted_data)
    mid_index = n // 2

    if n % 2 == 1:
        # Odd number of elements: return the middle one
        return float(sorted_data[mid_index])
    else:
        # Even number of elements: average the two middle ones
        return (sorted_data[mid_index - 1] + sorted_data[mid_index]) / 2.0


def mode(data: List[Number]) -> List[Number]:
    """
    Calculates the mode (most frequent value) of a list of numbers.
    
    Returns all modes if the dataset is multimodal (multiple values 
    share the same highest frequency).

    Args:
        data: A list of numbers (int or float).

    Returns:
        A list containing the mode(s). Returns a list of all values 
        if all values are equally frequent.

    Raises:
        ValueError: If the input list is empty or contains non-numeric values.
    """
    _validate_numeric_data(data)
    
    frequency = {}
    for num in data:
        frequency[num] = frequency.get(num, 0) + 1
    
    if not frequency:
        return []

    max_freq = max(frequency.values())
    
    # Collect all values that have the maximum frequency
    modes = [k for k, v in frequency.items() if v == max_freq]
    
    # Sort modes for consistent output (optional but good for testing)
    return sorted(modes)


def standard_deviation(data: List[Number], sample: bool = True) -> float:
    """
    Calculates the standard deviation of a list of numbers.

    Args:
        data: A list of numbers (int or float).
        sample: If True (default), calculates sample standard deviation (N-1).
                If False, calculates population standard deviation (N).

    Returns:
        The standard deviation as a float.

    Raises:
        ValueError: If the input list is empty, contains non-numeric values,
                    or if sample=True and list size < 2.
    """
    _validate_numeric_data(data)
    
    n = len(data)
    
    # Sample standard deviation requires at least 2 data points
    if sample and n < 2:
        raise ValueError("Sample standard deviation requires at least two data points.")

    avg = mean(data)
    
    # Calculate sum of squared differences
    sum_squared_diff = sum((x - avg) ** 2 for x in data)
    
    if sample:
        variance = sum_squared_diff / (n - 1)
    else:
        variance = sum_squared_diff / n
        
    return math.sqrt(variance)