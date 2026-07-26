# Wikipedia Analytics

A Flask dashboard for exploring Wikipedia article statistics and trends — search
articles, pull view-count history via the Wikipedia REST/MediaWiki APIs, and chart
results with Chart.js.

## Stack

- **Backend**: Flask, with a Wikipedia API client (`api/wikipedia.py`) and an analytics
  engine (`api/analytics.py`) built on top of it
- **Frontend**: server-rendered Jinja templates (`templates/`) + vanilla JS
  (`static/js/app.js`) + Chart.js (via CDN)

## Run it

```bash
pip install -r requirements.txt
python app.py
```

## Known cleanup items

A few files in this repo are leftover scaffolding not wired into the running app —
noting them here instead of silently leaving them:

- `src/components/*.jsx`, `src/services/*.js` — a React-style frontend attempt with no
  `package.json` or build tooling anywhere in the repo, so it can't actually run
- `app.py`'s FAQ blueprint and `models/user.py` — generic auth/FAQ boilerplate unrelated
  to Wikipedia analytics
