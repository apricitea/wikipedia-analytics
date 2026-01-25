/**
 * ChartComponent
 * A reusable class wrapper for Chart.js to manage lifecycle, resizing, and configuration.
 * 
 * Features:
 * - Automatic canvas cleanup to prevent memory leaks.
 * - Responsive resizing handling.
 * - Dynamic data updating.
 * - Type-safe configuration for common chart types.
 * 
 * @requires Chart.js (https://cdn.jsdelivr.net/npm/chart.js)
 */

class ChartComponent {
  /**
   * Creates an instance of ChartComponent.
   * @param {string|HTMLCanvasElement} canvasTarget - The ID of the canvas element or the DOM element itself.
   * @param {string} type - The type of chart (e.g., 'bar', 'line', 'pie', 'doughnut').
   * @param {object} data - The data object compatible with Chart.js (labels, datasets).
   * @param {object} [options={}] - Configuration options for Chart.js.
   */
  constructor(canvasTarget, type, data, options = {}) {
    // Validate input
    if (!canvasTarget) {
      throw new Error('ChartComponent: Canvas target is required.');
    }
    if (!type || !data) {
      throw new Error('ChartComponent: Chart type and data are required.');
    }

    // Resolve DOM element
    this.canvas = typeof canvasTarget === 'string' 
      ? document.getElementById(canvasTarget) 
      : canvasTarget;

    if (!this.canvas || !(this.canvas instanceof HTMLCanvasElement)) {
      throw new Error('ChartComponent: Target element must be a valid <canvas> element.');
    }

    this.ctx = this.canvas.getContext('2d');
    this.type = type;
    this.data = data;
    this.options = options;
    this.chartInstance = null;

    // Initialize the chart
    this._init();
  }

  /**
   * Initializes the Chart.js instance.
   * @private
   */
  _init() {
    // Destroy existing instance if it exists (prevents canvas reuse errors)
    if (this.chartInstance) {
      this.chartInstance.destroy();
    }

    // Default configuration overrides for better UX
    const defaultOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
        },
        tooltip: {
          mode: 'index',
          intersect: false,
        },
      },
    };

    // Merge user options with defaults
    const mergedOptions = this._deepMerge(defaultOptions, this.options);

    try {
      this.chartInstance = new Chart(this.ctx, {
        type: this.type,
        data: this.data,
        options: mergedOptions,
      });
    } catch (error) {
      console.error('Failed to initialize Chart.js:', error);
      throw error;
    }
  }

  /**
   * Updates the chart data and re-renders.
   * @param {object} newData - The new data object.
   * @param {boolean} [animate=true] - Whether to animate the update.
   */
  updateData(newData, animate = true) {
    if (!this.chartInstance) return;

    this.chartInstance.data = newData;
    this.chartInstance.update(animate ? 'default' : 'none');
  }

  /**
   * Updates the chart configuration options.
   * @param {object} newOptions - New options to merge.
   */
  updateOptions(newOptions) {
    if (!this.chartInstance) return;

    // Chart.js update() handles option updates efficiently
    this.chartInstance.options = this._deepMerge(this.chartInstance.options, newOptions);
    this.chartInstance.update();
  }

  /**
   * Changes the type of the chart. 
   * Note: Chart.js does not support changing type dynamically easily, 
   * so we destroy and recreate.
   * @param {string} newType - The new chart type.
   */
  changeType(newType) {
    this.type = newType;
    this._init();
  }

  /**
   * Destroys the chart instance and cleans up event listeners.
   */
  destroy() {
    if (this.chartInstance) {
      this.chartInstance.destroy();
      this.chartInstance = null;
    }
  }

  /**
   * Utility to deep merge objects for options.
   * @private
   */
  _deepMerge(target, source) {
    // Simple deep merge implementation suitable for options objects
    if (typeof target !== 'object' || target === null) return source;
    if (typeof source !== 'object' || source === null) return target;

    const output = { ...target };
    for (const key in source) {
      if (Object.prototype.hasOwnProperty.call(source, key)) {
        if (typeof source[key] === 'object' && source[key] !== null && !Array.isArray(source[key])) {
          output[key] = this._deepMerge(target[key] || {}, source[key]);
        } else {
          output[key] = source[key];
        }
      }
    }
    return output;
  }
}

// --- Usage Example ---

// 1. Setup Data
const salesData = {
  labels: ['January', 'February', 'March', 'April', 'May', 'June'],
  datasets: [
    {
      label: 'Revenue ($)',
      data: [12000, 19000, 3000, 5000, 2000, 3000],
      backgroundColor: 'rgba(54, 162, 235, 0.5)',
      borderColor: 'rgba(54, 162, 235, 1)',
      borderWidth: 1,
    },
    {
      label: 'Expenses ($)',
      data: [8000, 12000, 2000, 4000, 1000, 2000],
      backgroundColor: 'rgba(255, 99, 132, 0.5)',
      borderColor: 'rgba(255, 99, 132, 1)',
      borderWidth: 1,
    }
  ]
};

// 2. Configuration
const configOptions = {
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        color: 'rgba(0, 0, 0, 0.1)'
      }
    },
    x: {
      grid: {
        display: false
      }
    }
  },
  plugins: {
    title: {
      display: true,
      text: 'Monthly Financial Overview'
    }
  }
};

// 3. Initialize
// Ensure you have a <canvas id="myChart"></canvas> in your HTML
let myChart;

try {
  myChart = new ChartComponent('myChart', 'bar', salesData, configOptions);
} catch (e) {
  console.error("Initialization failed:", e.message);
}

// 4. Example: Update data dynamically (e.g., after fetching from API)
// setTimeout(() => {
//   const updatedData = { ...salesData };
//   updatedData.datasets[0].data = [15000, 25000, 10000, 8000, 5000, 12000];
//   myChart.updateData(updatedData);
// }, 3000);

// Export for use in modules if needed
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ChartComponent;
}