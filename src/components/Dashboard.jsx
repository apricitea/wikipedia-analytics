/**
 * DashboardManager
 * Handles the rendering and state management of the main Dashboard UI.
 * Generates layout containers and populates them with statistics cards.
 */
class DashboardManager {
  /**
   * @param {string} containerId - The ID of the DOM element to render the dashboard into.
   * @param {Array} initialData - Array of objects representing statistics.
   */
  constructor(containerId, initialData = []) {
    this.container = document.getElementById(containerId);
    if (!this.container) {
      throw new Error(`Container element with ID "${containerId}" not found.`);
    }
    
    // Default data if none provided
    this.data = initialData.length ? initialData : this.getDefaultData();
    
    this.init();
  }

  /**
   * Initializes the dashboard by creating the DOM structure.
   */
  init() {
    this.renderLayout();
    this.renderCards();
  }

  /**
   * Generates the main layout structure (Header and Grid).
   */
  renderLayout() {
    this.container.innerHTML = '';

    // Create Header
    const header = document.createElement('header');
    header.className = 'dashboard-header';
    header.innerHTML = `
      <h1>System Overview</h1>
      <div class="user-profile">
        <span>Admin User</span>
        <div class="avatar"></div>
      </div>
    `;

    // Create Grid Container for Cards
    const grid = document.createElement('section');
    grid.className = 'dashboard-grid';
    this.gridElement = grid; // Store reference for updates

    this.container.appendChild(header);
    this.container.appendChild(grid);
  }

  /**
   * Iterates through data and renders statistic cards.
   */
  renderCards() {
    if (!this.gridElement) return;

    this.gridElement.innerHTML = '';
    
    this.data.forEach(item => {
      const card = this.createCardElement(item);
      this.gridElement.appendChild(card);
    });
  }

  /**
   * Creates a single DOM element for a statistic card.
   * @param {Object} item - Data object for the card.
   * @returns {HTMLElement}
   */
  createCardElement(item) {
    const article = document.createElement('article');
    article.className = `stat-card stat-card--${item.trend || 'neutral'}`;
    
    // Determine trend icon logic
    const trendIcon = this.getTrendIcon(item.trend);

    article.innerHTML = `
      <div class="stat-card__header">
        <h3 class="stat-card__title">${this.escapeHtml(item.title)}</h3>
        <span class="stat-card__icon" aria-hidden="true">${item.icon}</span>
      </div>
      <div class="stat-card__body">
        <div class="stat-card__value">${this.escapeHtml(String(item.value))}</div>
        <div class="stat-card__meta">
          <span class="stat-card__trend ${item.trend}">
            ${trendIcon} ${item.change > 0 ? '+' : ''}${item.change}%
          </span>
          <span class="stat-card__period">vs last month</span>
        </div>
      </div>
    `;
    return article;
  }

  /**
   * Returns an SVG icon string based on trend direction.
   * @param {string} trend - 'up', 'down', or 'neutral'
   * @returns {string} SVG HTML string
   */
  getTrendIcon(trend) {
    if (trend === 'up') return `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>`;
    if (trend === 'down') return `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline><polyline points="17 18 23 18 23 12"></polyline></svg>`;
    return `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line></svg>`;
  }

  /**
   * Updates the dashboard data and re-renders cards.
   * @param {Array} newData - New array of statistics objects.
   */
  updateData(newData) {
    if (!Array.isArray(newData)) {
      console.error('Invalid data format provided to updateData');
      return;
    }
    this.data = newData;
    this.renderCards();
  }

  /**
   * Helper to prevent XSS attacks by escaping HTML.
   * @param {string} unsafe - Unsafe string.
   * @returns {string} Escaped string.
   */
  escapeHtml(unsafe) {
    if (typeof unsafe !== 'string') return unsafe;
    return unsafe
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  /**
   * Provides default mock data for demonstration.
   * @returns {Array}
   */
  getDefaultData() {
    return [
      { title: 'Total Revenue', value: '$54,230', change: 12.5, trend: 'up', icon: '💰' },
      { title: 'Active Users', value: '2,450', change: 8.2, trend: 'up', icon: '👥' },
      { title: 'Bounce Rate', value: '42.3%', change: -2.1, trend: 'down', icon: '📉' },
      { title: 'Pending Issues', value: '12', change: 0, trend: 'neutral', icon: '⚠️' }
    ];
  }
}

// Example Usage:
document.addEventListener('DOMContentLoaded', () => {
  try {
    const dashboard = new DashboardManager('app-dashboard');
    
    // Example of updating data later (simulating fetch)
    // setTimeout(() => {
    //   dashboard.updateData([
    //     { title: 'New Metric', value: '100%', change: 5, trend: 'up', icon: '🚀' }
    //   ]);
    // }, 3000);
  } catch (error) {
    console.error('Failed to initialize dashboard:', error.message);
  }
});