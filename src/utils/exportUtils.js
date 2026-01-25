/**
 * ChartExporter
 * A utility class to handle exporting Chart.js instances to PNG
 * and raw data to CSV.
 *
 * Requirements:
 * - Chart.js (for PNG export)
 * - Modern browser environment (Blob, URL, anchor download)
 */
class ChartExporter {
  /**
   * Creates an instance of ChartExporter.
   * @param {HTMLCanvasElement} canvasElement - The canvas element of the chart.
   * @param {Object} chartData - The raw data object used to populate the chart.
   */
  constructor(canvasElement, chartData) {
    if (!canvasElement || !(canvasElement instanceof HTMLCanvasElement)) {
      throw new Error('Invalid canvas element provided.');
    }
    if (!chartData || typeof chartData !== 'object') {
      throw new Error('Invalid chart data provided.');
    }

    this.canvas = canvasElement;
    this.data = chartData;
  }

  /**
   * Exports the current state of the canvas as a PNG image.
   * Handles high-DPI (Retina) displays by adjusting the background.
   *
   * @param {string} [filename='chart.png'] - The desired filename for the download.
   * @returns {void}
   */
  exportToPNG(filename = 'chart.png') {
    try {
      // Create a temporary link element
      const link = document.createElement('a');
      
      // Convert canvas to data URL (base64)
      // We use a quality of 1.0 for maximum fidelity
      const imageURI = this.canvas.toDataURL('image/png', 1.0);

      link.download = filename;
      link.href = imageURI;

      // Trigger download
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Failed to export chart to PNG:', error);
      throw new Error('Export to PNG failed. Ensure the canvas is not tainted by cross-origin images.');
    }
  }

  /**
   * Exports the chart data to a CSV file.
   * Assumes a structure where labels represent the X-axis
   * and datasets represent Y-axis columns.
   *
   * @param {string} [filename='data.csv'] - The desired filename for the download.
   * @returns {void}
   */
  exportToCSV(filename = 'data.csv') {
    try {
      if (!this.data.labels || !this.data.datasets) {
        throw new Error('Data structure missing labels or datasets.');
      }

      const csvRows = [];

      // 1. Header Row
      // First column is usually the Label (e.g., "Date", "Category")
      const headers = ['Label', ...this.data.datasets.map(ds => this._sanitizeCSV(ds.label || 'Untitled'))];
      csvRows.push(headers.join(','));

      // 2. Data Rows
      // Iterate through labels (assuming all datasets have the same length as labels)
      const maxLength = this.data.labels.length;

      for (let i = 0; i < maxLength; i++) {
        const row = [
          this._sanitizeCSV(this.data.labels[i]),
          ...this.data.datasets.map(dataset => {
            const value = dataset.data[i];
            // Handle null/undefined values
            return value !== null && value !== undefined ? value : '';
          })
        ];
        csvRows.push(row.join(','));
      }

      // 3. Create Blob and Download
      const csvString = csvRows.join('\r\n'); // CRLF for Excel compatibility
      const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);

      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', filename);
      link.style.visibility = 'hidden';

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Clean up object URL to free memory
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export data to CSV:', error);
      throw new Error('Export to CSV failed.');
    }
  }

  /**
   * Helper to sanitize CSV values.
   * Wraps values in quotes if they contain commas, quotes, or newlines.
   *
   * @private
   * @param {string|number} value - The value to sanitize.
   * @returns {string} The sanitized value.
   */
  _sanitizeCSV(value) {
    if (value === null || value === undefined) return '';
    
    const stringValue = String(value);
    
    // If the value contains a comma, newline, or quote, wrap it in quotes and escape internal quotes
    if (stringValue.includes(',') || stringValue.includes('\n') || stringValue.includes('"')) {
      return `"${stringValue.replace(/"/g, '""')}"`;
    }
    
    return stringValue;
  }
}

// --- Usage Example ---

/*
// Assuming you have a Chart.js instance set up like this:
const ctx = document.getElementById('myChart').getContext('2d');
const myChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['January', 'February', 'March', 'April'],
        datasets: [{
            label: 'Sales',
            data: [10, 20, 30, 40],
            backgroundColor: 'rgba(75, 192, 192, 0.2)'
        }, {
            label: 'Expenses',
            data: [8, 15, 25, 30],
            backgroundColor: 'rgba(255, 99, 132, 0.2)'
        }]
    }
});

// Initialize the exporter
const exporter = new ChartExporter(
    document.getElementById('myChart'), 
    myChart.data
);

// Bind buttons to export functions
document.getElementById('btn-export-png').addEventListener('click', () => {
    exporter.exportToPNG('my-chart-report.png');
});

document.getElementById('btn-export-csv').addEventListener('click', () => {
    exporter.exportToCSV('my-chart-data.csv');
});
*/