"""Unit tests for AnalyticsEngine. The WikipediaAPI client is monkeypatched
so tests never hit the network."""

from api.analytics import AnalyticsEngine


def make_engine():
    return AnalyticsEngine()


def test_view_stats_computes_basic_aggregates(monkeypatch):
    engine = make_engine()
    daily = [{'date': f'2026010{i}', 'views': v, 'rank': 0} for i, v in enumerate([10, 20, 30], start=1)]
    monkeypatch.setattr(engine.wiki, 'get_page_views', lambda title, days=30: daily)

    stats = engine.get_view_stats('Some Article', days=3)

    assert stats['total'] == 60
    assert stats['average'] == 20.0
    assert stats['max'] == 30
    assert stats['min'] == 10
    assert stats['daily'] == daily


def test_view_stats_empty_when_no_data(monkeypatch):
    engine = make_engine()
    monkeypatch.setattr(engine.wiki, 'get_page_views', lambda title, days=30: [])

    stats = engine.get_view_stats('Nonexistent')

    assert stats == {
        'total': 0, 'average': 0, 'max': 0, 'min': 0, 'trend': 'neutral', 'daily': [],
    }


def test_view_stats_handles_exactly_seven_days_without_crashing(monkeypatch):
    # Regression test: get_trending_articles always requests days=7, which
    # used to divide by zero (len(views_list) - 7 == 0) and get swallowed by
    # the broad except, silently making every "trending" article show 0 views.
    engine = make_engine()
    daily = [{'views': v, 'rank': 0} for v in [10, 20, 30, 40, 50, 60, 70]]
    monkeypatch.setattr(engine.wiki, 'get_page_views', lambda title, days=30: daily)

    stats = engine.get_view_stats('Exactly A Week', days=7)

    assert stats['total'] == 280
    assert stats['trend'] == 'neutral'


def test_view_stats_trend_increasing(monkeypatch):
    engine = make_engine()
    # 7 low days followed by 7 clearly higher days -> increasing
    daily = [{'views': 10, 'rank': 0} for _ in range(7)] + [{'views': 50, 'rank': 0} for _ in range(7)]
    monkeypatch.setattr(engine.wiki, 'get_page_views', lambda title, days=30: daily)

    stats = engine.get_view_stats('Trending Article', days=14)

    assert stats['trend'] == 'increasing'


def test_view_stats_trend_decreasing(monkeypatch):
    engine = make_engine()
    daily = [{'views': 50, 'rank': 0} for _ in range(7)] + [{'views': 10, 'rank': 0} for _ in range(7)]
    monkeypatch.setattr(engine.wiki, 'get_page_views', lambda title, days=30: daily)

    stats = engine.get_view_stats('Fading Article', days=14)

    assert stats['trend'] == 'decreasing'


def test_analyze_article_quality_scores_comprehensive_article():
    engine = make_engine()
    info = {
        'length': 15000,
        'category_count': 12,
        'image_count': 8,
        'revision_count': 60,
        'extract': 'A well documented article.',
    }

    class _Wiki:
        def get_article_info(self, title):
            return info

    engine.wiki = _Wiki()

    quality = engine.analyze_article_quality('Comprehensive Article')

    assert quality['score'] == 85
    assert quality['grade'] == 'A - Excellent'
    assert 'Comprehensive content' in quality['factors']


def test_analyze_article_quality_scores_thin_article():
    engine = make_engine()

    class _Wiki:
        def get_article_info(self, title):
            return {'length': 500, 'category_count': 1, 'image_count': 0, 'revision_count': 2, 'extract': ''}

    engine.wiki = _Wiki()

    quality = engine.analyze_article_quality('Stub Article')

    assert quality['score'] == 0
    assert quality['grade'] == 'D - Needs work'


def test_get_trending_articles_ranks_by_views(monkeypatch):
    engine = make_engine()

    class _Wiki:
        def get_top_viewed_articles(self, count):
            return ['Low', 'High']

        def get_article_info(self, title):
            return {'url': f'https://en.wikipedia.org/wiki/{title}', 'extract': 'x' * 300}

        def get_page_views(self, title, days=30):
            views = 5 if title == 'Low' else 500
            return [{'views': views, 'rank': 0}]

    engine.wiki = _Wiki()

    trending = engine.get_trending_articles(limit=2)

    assert [t['title'] for t in trending] == ['High', 'Low']
    assert trending[0]['views_week'] == 500
