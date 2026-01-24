import pytest
import math
from typing import List

# Assuming the module under test is named 'stats' and is in the same package or available in PYTHONPATH
# For the purpose of this standalone test file, we will define the functions inline 
# or mock them if this were a real interface. Here, I will define the target functions 
# at the bottom to simulate the "System Under Test" (SUT).

# --- System Under Test (Simulated) ---
class StatsFunctions:
    @staticmethod
    def mean(data: List[float]) -> float:
        if not data:
            raise ValueError("Input data cannot be empty")
        return sum(data) / len(data)

    @staticmethod
    def median(data: List[float]) -> float:
        if not data:
            raise ValueError("Input data cannot be empty")
        sorted_data = sorted(data)
        n = len(sorted_data)
        mid = n // 2
        if n % 2 == 1:
            return sorted_data[mid]
        else:
            return (sorted_data[mid - 1] + sorted_data[mid]) / 2

    @staticmethod
    def variance(data: List[float]) -> float:
        if not data:
            raise ValueError("Input data cannot be empty")
        if len(data) < 2:
            raise ValueError("Variance requires at least two data points")
        m = StatsFunctions.mean(data)
        return sum((x - m) ** 2 for x in data) / len(data)

    @staticmethod
    def std_deviation(data: List[float]) -> float:
        return math.sqrt(StatsFunctions.variance(data))

# --- Fixtures ---

@pytest.fixture
def stats():
    """Fixture providing an instance of the StatsFunctions class."""
    return StatsFunctions()

@pytest.fixture
def sample_data():
    """Fixture providing a standard list of numbers."""
    return [1.0, 2.0, 3.0, 4.0, 5.0]

@pytest.fixture
def even_data():
    """Fixture providing an even number of items for median testing."""
    return [10.0, 20.0, 30.0, 40.0]

# --- Tests for Mean ---

class TestMean:
    def test_mean_calculates_correctly_for_positive_integers(self, stats):
        # Arrange
        data = [1, 2, 3, 4, 5]
        expected = 3.0
        
        # Act
        result = stats.mean(data)
        
        # Assert
        assert result == expected

    def test_mean_calculates_correctly_for_negative_numbers(self, stats):
        # Arrange
        data = [-1.0, -2.0, -3.0]
        expected = -2.0
        
        # Act
        result = stats.mean(data)
        
        # Assert
        assert result == expected

    def test_mean_handles_mixed_positive_and_negative(self, stats):
        # Arrange
        data = [-10, 0, 10, 20]
        expected = 5.0
        
        # Act
        result = stats.mean(data)
        
        # Assert
        assert result == expected

    def test_mean_returns_float_for_integer_input(self, stats):
        # Arrange
        data = [1, 2]
        
        # Act
        result = stats.mean(data)
        
        # Assert
        assert isinstance(result, float)
        assert result == 1.5

    def test_mean_raises_error_on_empty_list(self, stats):
        # Arrange
        data = []
        
        # Act & Assert
        with pytest.raises(ValueError) as excinfo:
            stats.mean(data)
        
        assert "cannot be empty" in str(excinfo.value)

# --- Tests for Median ---

class TestMedian:
    def test_median_odd_number_of_elements(self, stats):
        # Arrange
        data = [1.0, 3.0, 2.0] # Unsorted
        expected = 2.0
        
        # Act
        result = stats.median(data)
        
        # Assert
        assert result == expected

    def test_median_even_number_of_elements(self, stats, even_data):
        # Arrange
        expected = 25.0 # (20 + 30) / 2
        
        # Act
        result = stats.median(even_data)
        
        # Assert
        assert result == expected

    def test_median_single_element(self, stats):
        # Arrange
        data = [42.0]
        expected = 42.0
        
        # Act
        result = stats.median(data)
        
        # Assert
        assert result == expected

    def test_median_raises_error_on_empty_list(self, stats):
        # Arrange
        data = []
        
        # Act & Assert
        with pytest.raises(ValueError):
            stats.median(data)

    def test_median_handles_negative_numbers(self, stats):
        # Arrange
        data = [-5, -1, -3]
        expected = -3.0
        
        # Act
        result = stats.median(data)
        
        # Assert
        assert result == expected

# --- Tests for Variance ---

class TestVariance:
    def test_variance_population_calculation(self, stats):
        # Arrange
        # Mean is 3. Deviations: 4, 1, 0, 1, 4. Sum sq dev: 10. Var: 10/5 = 2.0
        data = [1, 2, 3, 4, 5]
        expected = 2.0
        
        # Act
        result = stats.variance(data)
        
        # Assert
        assert result == expected

    def test_variance_requires_at_least_two_data_points(self, stats):
        # Arrange
        data = [10.0]
        
        # Act & Assert
        with pytest.raises(ValueError) as excinfo:
            stats.variance(data)
        
        assert "at least two" in str(excinfo.value)

    def test_variance_raises_error_on_empty_list(self, stats):
        # Arrange
        data = []
        
        # Act & Assert
        with pytest.raises(ValueError):
            stats.variance(data)

    def test_variance_is_zero_for_identical_numbers(self, stats):
        # Arrange
        data = [5.0, 5.0, 5.0, 5.0]
        expected = 0.0
        
        # Act
        result = stats.variance(data)
        
        # Assert
        assert result == expected

# --- Tests for Standard Deviation ---

class TestStandardDeviation:
    def test_std_deviation_basic_calculation(self, stats):
        # Arrange
        # Var of [1, 2, 3, 4, 5] is 2.0. Std Dev is sqrt(2)
        data = [1, 2, 3, 4, 5]
        expected = math.sqrt(2.0)
        
        # Act
        result = stats.std_deviation(data)
        
        # Assert
        assert result == expected

    def test_std_deviation_propagates_variance_errors(self, stats):
        # Arrange
        # std_deviation calls variance. Variance raises ValueError for single element.
        data = [10.0]
        
        # Act & Assert
        with pytest.raises(ValueError):
            stats.std_deviation(data)

    def test_std_deviation_zero_for_constant_data(self, stats):
        # Arrange
        data = [100.0, 100.0, 100.0]
        expected = 0.0
        
        # Act
        result = stats.std_deviation(data)
        
        # Assert
        assert result == expected

# --- Tests for Edge Cases / Boundary Conditions ---

class TestEdgeCases:
    def test_very_large_numbers(self, stats):
        # Arrange
        data = [1e10, 1e10 + 2, 1e10 + 4]
        expected_mean = 1e10 + 2.0
        
        # Act
        result = stats.mean(data)
        
        # Assert
        assert result == expected_mean

    def test_very_small_numbers(self, stats):
        # Arrange
        data = [1e-10, 2e-10, 3e-10]
        expected_mean = 2e-10
        
        # Act
        result = stats.mean(data)
        
        # Assert
        assert result == expected_mean

    def test_floating_point_precision(self, stats):
        # Arrange
        # 1/3 is not perfectly representable
        data = [1, 1, 1]
        
        # Act
        result = stats.mean(data)
        
        # Assert
        assert result == 1.0

    def test_data_with_nan(self, stats):
        # Note: Behavior with NaN depends on requirements. 
        # Usually, stats functions should handle or reject NaN.
        # Here we test that it propagates or calculates as expected (NaN result).
        # Arrange
        data = [1.0, float('nan'), 2.0]
        
        # Act
        result = stats.mean(data)
        
        # Assert
        assert math.isnan(result)

    def test_data_with_infinity(self, stats):
        # Arrange
        data = [1.0, float('inf'), 2.0]
        
        # Act
        result = stats.mean(data)
        
        # Assert
        assert math.isinf(result)
        assert result > 0