"""
Wikipedia Analytics Dashboard
Flask application for serving Wikipedia statistics and visualizations.
"""

from flask import Flask, render_template, jsonify, request
from api.wikipedia import WikipediaAPI
from api.analytics import AnalyticsEngine
import logging

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Initialize API clients
wiki_api = WikipediaAPI()
analytics = AnalyticsEngine()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')


@app.route('/api/search/<query>')
def search_articles(query):
    """Search for Wikipedia articles."""
    try:
        results = wiki_api.search(query)
        return jsonify({
            'success': True,
            'results': results[:10]  # Limit to 10 results
        })
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/article/<path:title>')
def get_article(title):
    """Get detailed article statistics."""
    try:
        article_data = wiki_api.get_article_info(title)
        view_stats = analytics.get_view_stats(title)

        return jsonify({
            'success': True,
            'article': article_data,
            'views': view_stats
        })
    except Exception as e:
        logger.error(f"Article fetch error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/views/<path:title>')
def get_views(title):
    """Get page view statistics for an article."""
    try:
        days = request.args.get('days', 30, type=int)
        view_data = analytics.get_view_stats(title, days=days)

        return jsonify({
            'success': True,
            'title': title,
            'views': view_data
        })
    except Exception as e:
        logger.error(f"View stats error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/compare', methods=['POST'])
def compare_articles():
    """Compare multiple Wikipedia articles."""
    try:
        data = request.json
        titles = data.get('titles', [])

        if len(titles) < 2:
            return jsonify({
                'success': False,
                'error': 'At least 2 articles required for comparison'
            }), 400

        comparison = analytics.compare_articles(titles)
        return jsonify({
            'success': True,
            'comparison': comparison
        })
    except Exception as e:
        logger.error(f"Comparison error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/trending')
def get_trending():
    """Get currently trending Wikipedia articles."""
    try:
        limit = request.args.get('limit', 10, type=int)
        trending = analytics.get_trending_articles(limit=limit)

        return jsonify({
            'success': True,
            'trending': trending
        })
    except Exception as e:
        logger.error(f"Trending error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stats/overview')
def get_overview_stats():
    """Get overview statistics for the dashboard."""
    try:
        stats = {
            'total_articles': wiki_api.get_total_articles(),
            'active_editors': wiki_api.get_active_editors(),
            'available_languages': wiki_api.get_supported_languages()
        }

        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        logger.error(f"Overview stats error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'success': False, 'error': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
