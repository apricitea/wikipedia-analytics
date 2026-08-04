# Wikipedia Analytics

[![CI](https://github.com/apricitea/wikipedia-analytics/actions/workflows/ci.yml/badge.svg)](https://github.com/apricitea/wikipedia-analytics/actions/workflows/ci.yml)

A Flask dashboard for exploring Wikipedia article statistics and trends — search
articles, pull view-count history via the Wikipedia REST/MediaWiki APIs, and chart
results with Chart.js.

## Stack

- **Backend**: Flask (`app.py`), with a Wikipedia API client (`api/wikipedia.py`) and an
  analytics engine (`api/analytics.py`) built on top of it
- **Frontend**: server-rendered Jinja template (`templates/index.html`) + vanilla JS
  (`static/js/app.js`) + Chart.js (via CDN)

## Run it

```bash
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000`. Search for an article, click a result to see its
stats and 30-day view chart, or browse the trending panel (yesterday's actual
most-viewed articles, from Wikimedia's public pageviews API).

## API routes

| Route | Description |
|---|---|
| `GET /api/search/<query>` | Article search via the MediaWiki API |
| `GET /api/article/<title>` | Article metadata + 30-day view stats |
| `GET /api/trending?limit=N` | Yesterday's top-viewed articles, ranked by 7-day views |

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

Unit tests cover the analytics scoring/trend logic and the Flask routes; the
Wikipedia API client is monkeypatched so the suite runs without network access.
