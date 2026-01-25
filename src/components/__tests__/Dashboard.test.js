import pytest
from unittest.mock import MagicMock, patch, call
from dashboard import Dashboard
from chart import Chart

# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_chart():
    """Fixture providing a mocked Chart component."""
    return MagicMock(spec=Chart)

@pytest.fixture
def dashboard(mock_chart):
    """Fixture providing a Dashboard instance with mocked dependencies."""
    # Assuming Dashboard takes a list of charts or a factory
    return Dashboard(charts=[mock_chart])

# =============================================================================
# Chart Component Tests
# =============================================================================

class TestChart:
    """Comprehensive unit tests for the Chart component."""

    def test_chart_initialization_with_valid_data(self):
        """
        Arrange-Act-Assert: Test normal initialization.
        Ensure a chart is created with the correct title and data.
        """
        # Arrange
        title = "Sales 2023"
        data = [10, 20, 30]

        # Act
        chart = Chart(title=title, data=data)

        # Assert
        assert chart.title == title
        assert chart.data == data
        assert chart.is_visible is False  # Assuming default state

    def test_chart_render_returns_html_string(self):
        """Test that the render method produces a non-empty string."""
        # Arrange
        chart = Chart(title="Test", data=[1, 2, 3])

        # Act
        html_output = chart.render()

        # Assert
        assert isinstance(html_output, str)
        assert len(html_output) > 0
        assert "Test" in html_output

    def test_chart_update_data_modifies_state(self):
        """Test that updating data changes the internal state."""
        # Arrange
        chart = Chart(title="Test", data=[1, 2, 3])
        new_data = [5, 5, 5]

        # Act
        chart.update_data(new_data)

        # Assert
        assert chart.data == new_data

    def test_chart_update_data_with_empty_list(self):
        """Test edge case: Updating chart with an empty list."""
        # Arrange
        chart = Chart(title="Test", data=[1, 2, 3])

        # Act & Assert
        # Assuming the chart allows clearing data
        chart.update_data([])
        assert chart.data == []

    def test_chart_update_data_raises_error_on_invalid_type(self):
        """Test error case: Passing non-iterable data raises ValueError."""
        # Arrange
        chart = Chart(title="Test", data=[1, 2, 3])

        # Act & Assert
        with pytest.raises(ValueError) as excinfo:
            chart.update_data("invalid_string_data")
        
        assert "Invalid data format" in str(excinfo.value)

    def test_chart_visibility_toggle(self):
        """Test toggling visibility state."""
        # Arrange
        chart = Chart(title="Test", data=[1, 2, 3])

        # Act
        chart.show()
        assert chart.is_visible is True

        chart.hide()
        assert chart.is_visible is False

# =============================================================================
# Dashboard Component Tests
# =============================================================================

class TestDashboard:
    """Comprehensive unit tests for the Dashboard component."""

    def test_dashboard_initialization(self, mock_chart):
        """Test normal behavior: Dashboard initializes with charts."""
        # Arrange & Act
        dash = Dashboard(charts=[mock_chart])

        # Assert
        assert len(dash.charts) == 1
        assert dash.charts[0] == mock_chart

    def test_dashboard_render_calls_render_on_children(self, mock_chart):
        """
        Test that dashboard.render() triggers render() on all child charts.
        """
        # Arrange
        mock_chart_2 = MagicMock(spec=Chart)
        dash = Dashboard(charts=[mock_chart, mock_chart_2])

        # Act
        dash.render()

        # Assert
        mock_chart.render.assert_called_once()
        mock_chart_2.render.assert_called_once()

    def test_dashboard_add_chart(self, mock_chart):
        """Test adding a new chart to the dashboard."""
        # Arrange
        dash = Dashboard(charts=[])
        new_chart = MagicMock(spec=Chart)

        # Act
        dash.add_chart(new_chart)

        # Assert
        assert len(dash.charts) == 1
        assert new_chart in dash.charts

    def test_dashboard_remove_chart(self, mock_chart):
        """Test removing an existing chart."""
        # Arrange
        dash = Dashboard(charts=[mock_chart])

        # Act
        dash.remove_chart(mock_chart)

        # Assert
        assert len(dash.charts) == 0

    def test_dashboard_remove_non_existent_chart_raises_error(self, mock_chart):
        """Test error case: Trying to remove a chart that isn't in the list."""
        # Arrange
        other_chart = MagicMock(spec=Chart)
        dash = Dashboard(charts=[mock_chart])

        # Act & Assert
        with pytest.raises(ValueError):
            dash.remove_chart(other_chart)

    def test_dashboard_refresh_updates_all_charts(self, mock_chart):
        """
        Test that the refresh logic calls update/refresh on children.
        Assuming charts have a 'refresh' method.
        """
        # Arrange
        dash = Dashboard(charts=[mock_chart])
        
        # Mocking a refresh method specifically if it differs from render
        mock_chart.refresh = MagicMock()

        # Act
        dash.refresh()

        # Assert
        mock_chart.refresh.assert_called_once()

    def test_dashboard_handles_empty_chart_list(self):
        """Test edge case: Dashboard with no charts renders gracefully."""
        # Arrange
        dash = Dashboard(charts=[])

        # Act & Assert
        # Should not raise an error
        try:
            dash.render()
            assert True
        except Exception:
            pytest.fail("Dashboard.render() raised an exception with no charts")

    def test_dashboard_aggregates_data_from_charts(self, mock_chart):
        """
        Test complex logic: Dashboard aggregates data from all charts.
        """
        # Arrange
        chart_a = MagicMock(spec=Chart)
        chart_b = MagicMock(spec=Chart)
        
        chart_a.data = [1, 2]
        chart_b.data = [3, 4]
        
        dash = Dashboard(charts=[chart_a, chart_b])

        # Act
        # Assuming a method get_total_data_points
        total = dash.get_total_data_points()

        # Assert
        assert total == 4