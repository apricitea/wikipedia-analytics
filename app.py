"""
Wikipedia Analytics Dashboard
Flask entrypoint wiring the WikipediaAPI client and AnalyticsEngine to the
dashboard frontend (templates/index.html, static/js/app.js).
"""

from flask import Flask, render_template, jsonify, request

from api.wikipedia import WikipediaAPI
from api.analytics import AnalyticsEngine

app = Flask(__name__)
wiki = WikipediaAPI()
analytics = AnalyticsEngine()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/search/<query>')
def search(query):
    results = wiki.search(query)
    return jsonify({'success': True, 'results': results})


@app.route('/api/article/<title>')
def article(title):
    try:
        info = wiki.get_article_info(title)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404

    views = analytics.get_view_stats(title, days=30)
    return jsonify({'success': True, 'article': info, 'views': views})


@app.route('/api/trending')
def trending():
    limit = request.args.get('limit', default=5, type=int)
    articles = analytics.get_trending_articles(limit=limit)
    return jsonify({'success': True, 'trending': articles})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
