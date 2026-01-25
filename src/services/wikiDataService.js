/**
 * WikipediaAnalyticsService
 * 
 * A service class to interact with the Wikimedia Analytics API.
 * Specifically designed to fetch pageview statistics for given articles.
 * 
 * API Reference: https://wikitech.wikimedia.org/wiki/Analytics/AQS/Pageviews
 * 
 * @example
 * const service = new WikipediaAnalyticsService();
 * const views = await service.getDailyPageviews('en.wikipedia.org', 'Albert_Einstein', '2023-01-01', '2023-01-31');
 */

class WikipediaAnalyticsService {
  /**
   * Creates an instance of the service.
   * 
   * @param {Object} [options={}] - Configuration options
   * @param {string} [options.userAgent='WikipediaAnalyticsService/1.0'] - Custom User-Agent string for API requests
   * @param {string} [options.baseUrl='https://wikimedia.org/api/rest_v1/metrics/pageviews'] - Base API URL
   */
  constructor(options = {}) {
    this.baseUrl = options.baseUrl || 'https://wikimedia.org/api/rest_v1/metrics/pageviews';
    // Wikimedia requires a User-Agent header identifying the application/script
    this.userAgent = options.userAgent || 'WikipediaAnalyticsService/1.0 (https://github.com/example/repo)';
  }

  /**
   * Fetches daily pageview data for a specific article.
   * 
   * @param {string} project - The project domain (e.g., 'en.wikipedia.org', 'es.wiktionary.org')
   * @param {string} articleTitle - The title of the article (case-sensitive, spaces usually replaced with underscores)
   * @param {string} startDate - Start date in 'YYYY-MM-DD' format
   * @param {string} endDate - End date in 'YYYY-MM-DD' format
   * @param {string} [access='all-access'] - Access method: 'all-access', 'desktop', 'mobile-app', 'mobile-web'
   * @param {string} [agent='user'] - Agent type: 'user', 'spider', 'bot', 'all-agents'
   * @returns {Promise<Array<Object>>} A promise resolving to an array of daily view objects
   * @throws {Error} If validation fails or the API request errors
   */
  async getDailyPageviews(project, articleTitle, startDate, endDate, access = 'all-access', agent = 'user') {
    this._validateParams(project, articleTitle, startDate, endDate);

    // Normalize article title: replace spaces with underscores
    const normalizedTitle = articleTitle.trim().replace(/ /g, '_');

    // Construct the endpoint URL
    // Structure: /per-article/{project}/{access}/{agent}/{article}/daily/{start}/{end}
    const endpoint = `${this.baseUrl}/per-article/${project}/${access}/${agent}/${normalizedTitle}/daily/${startDate}/${endDate}`;

    try {
      const response = await fetch(endpoint, {
        method: 'GET',
        headers: {
          'User-Agent': this.userAgent,
          'Accept': 'application/json'
        }
      });

      if (!response.ok) {
        // Handle HTTP errors (e.g., 404 Not Found, 500 Server Error)
        await this._handleApiError(response);
      }

      const data = await response.json();

      // The API returns { items: [...] }
      if (!data.items || !Array.isArray(data.items)) {
        throw new Error('Unexpected API response format.');
      }

      return data.items;

    } catch (error) {
      // Re-throw network errors or errors thrown in _handleApiError
      throw new Error(`Failed to fetch pageviews: ${error.message}`);
    }
  }

  /**
   * Fetches aggregated pageview data (sum of views over the period).
   * 
   * @param {string} project - The project domain
   * @param {string} articleTitle - The title of the article
   * @param {string} startDate - Start date in 'YYYY-MM-DD' format
   * @param {string} endDate - End date in 'YYYY-MM-DD' format
   * @returns {Promise<Object>} An object containing aggregated statistics
   */
  async getAggregatedPageviews(project, articleTitle, startDate, endDate) {
    const dailyData = await this.getDailyPageviews(project, articleTitle, startDate, endDate);

    if (dailyData.length === 0) {
      return { totalViews: 0, averageDailyViews: 0, days: 0 };
    }

    const totalViews = dailyData.reduce((sum, item) => sum + item.views, 0);
    
    return {
      totalViews,
      averageDailyViews: Math.round(totalViews / dailyData.length),
      days: dailyData.length,
      startDate,
      endDate
    };
  }

  /**
   * Validates input parameters.
   * @private
   */
  _validateParams(project, articleTitle, startDate, endDate) {
    if (!project || typeof project !== 'string') throw new Error('Invalid project specified.');
    if (!articleTitle || typeof articleTitle !== 'string') throw new Error('Invalid article title specified.');
    
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateRegex.test(startDate) || !dateRegex.test(endDate)) {
      throw new Error('Dates must be in YYYY-MM-DD format.');
    }

    if (new Date(startDate) > new Date(endDate)) {
      throw new Error('Start date cannot be after end date.');
    }
  }

  /**
   * Handles API error responses.
   * @private
   */
  async _handleApiError(response) {
    let errorMessage = `API Error: ${response.status} ${response.statusText}`;
    
    try {
      // Attempt to parse error details from JSON body
      const errorData = await response.json();
      if (errorData.detail) {
        errorMessage += ` - ${errorData.detail}`;
      }
    } catch (e) {
      // Ignore if response is not JSON
    }
    
    throw new Error(errorMessage);
  }
}

// Export for use in Node.js or ES modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = WikipediaAnalyticsService;
}