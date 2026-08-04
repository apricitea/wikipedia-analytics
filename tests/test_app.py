"""Route-level smoke tests. wiki/analytics are monkeypatched so tests
never hit the network."""

import pytest

import app as app_module


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(
        app_module.wiki, 'search',
        lambda query, limit=10: [{'title': query, 'snippet': 'snip', 'wordcount': 1, 'timestamp': ''}],
    )
    monkeypatch.setattr(
        app_module.wiki, 'get_article_info',
        lambda title: {'title': title, 'extract': 'x', 'length': 100, 'category_count': 1,
                        'image_count': 1, 'revision_count': 1, 'categories': [], 'revisions': []},
    )
    monkeypatch.setattr(
        app_module.analytics, 'get_view_stats',
        lambda title, days=30: {'total': 10, 'average': 5, 'max': 6, 'min': 4, 'trend': 'stable', 'daily': []},
    )
    monkeypatch.setattr(
        app_module.analytics, 'get_trending_articles',
        lambda limit=5: [{'title': 'Trend', 'url': '', 'extract': '', 'views_week': 100, 'trend': 'stable'}],
    )
    app_module.app.config['TESTING'] = True
    return app_module.app.test_client()


def test_index_renders(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'<html' in resp.data.lower()


def test_search_route(client):
    resp = client.get('/api/search/Python')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['results'][0]['title'] == 'Python'


def test_article_route(client):
    resp = client.get('/api/article/Python')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['article']['title'] == 'Python'
    assert data['views']['total'] == 10


def test_article_route_missing_article_returns_404(client, monkeypatch):
    def raise_not_found(title):
        raise ValueError('not found')

    monkeypatch.setattr(app_module.wiki, 'get_article_info', raise_not_found)
    resp = client.get('/api/article/Does Not Exist')
    assert resp.status_code == 404
    assert resp.get_json()['success'] is False


def test_trending_route(client):
    resp = client.get('/api/trending?limit=1')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['trending'][0]['title'] == 'Trend'
