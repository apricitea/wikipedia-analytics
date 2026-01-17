"""
Wikipedia API Client
Handles all interactions with the Wikipedia REST API and MediaWiki API.
"""

import requests
import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class WikipediaAPI:
    """Client for interacting with Wikipedia APIs."""

    def __init__(self, lang: str = 'en'):
        self.lang = lang
        self.base_url = f'https://{lang}.wikipedia.org/api/rest_v1'
        self.mediawiki_url = f'https://{lang}.wikipedia.org/w/api.php'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'WikipediaAnalytics/1.0 (Educational Purpose)'
        })

    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for Wikipedia articles.

        Args:
            query: Search query string
            limit: Maximum number of results

        Returns:
            List of article summaries
        """
        try:
            params = {
                'action': 'query',
                'list': 'search',
                'srsearch': query,
                'srlimit': limit,
                'format': 'json',
                'srprop': 'snippet|titlesize|wordcount|timestamp'
            }

            response = self.session.get(self.mediawiki_url, params=params)
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get('query', {}).get('search', []):
                results.append({
                    'title': item['title'],
                    'snippet': item.get('snippet', '').replace('<span class="searchmatch">', '').replace('</span>', ''),
                    'wordcount': item.get('wordcount', 0),
                    'timestamp': item.get('timestamp', '')
                })

            logger.info(f"Search for '{query}' returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def get_article_info(self, title: str) -> Dict:
        """Get detailed information about an article.

        Args:
            title: Article title

        Returns:
            Dictionary with article information
        """
        try:
            # Get article summary and metadata
            url = f'{self.base_url}/page/summary/{title}'
            response = self.session.get(url)
            response.raise_for_status()
            summary = response.json()

            # Get detailed article info
            params = {
                'action': 'query',
                'prop': 'info|categories|links|images|revisions',
                'titles': title,
                'format': 'json',
                'cllimit': 20,
                'pllimit': 50,
                'imlimit': 20,
                'rvlimit': 5
            }

            response = self.session.get(self.mediawiki_url, params=params)
            response.raise_for_status()
            data = response.json()

            page_id = next(iter(data.get('query', {}).get('pages', {})))
            page_data = data.get('query', {}).get('pages', {}).get(page_id, {})

            # Extract relevant information
            article_info = {
                'title': summary.get('title', title),
                'extract': summary.get('extract', ''),
                'url': summary.get('content_urls', {}).get('desktop', {}).get('page', ''),

                # Basic stats
                'page_id': page_id,
                'length': page_data.get('length', 0),
                'revision_id': page_data.get('lastrevid', 0),
                'modified': page_data.get('touched', ''),

                # Counts
                'category_count': len(page_data.get('categories', [])),
                'image_count': len(page_data.get('images', [])),
                'link_count': len(page_data.get('links', [])),
                'revision_count': len(page_data.get('revisions', [])),

                # Categories (first 20)
                'categories': [cat['title'] for cat in page_data.get('categories', [])[:10]],

                # Recent revisions
                'revisions': [
                    {
                        'revid': rev.get('revid'),
                        'timestamp': rev.get('timestamp'),
                        'user': rev.get('user')
                    }
                    for rev in page_data.get('revisions', [])
                ]
            }

            logger.info(f"Fetched info for '{title}'")
            return article_info

        except Exception as e:
            logger.error(f"Failed to get article info: {e}")
            raise

    def get_page_views(self, title: str, days: int = 30) -> List[Dict]:
        """Get page view statistics for an article.

        Args:
            title: Article title
            days: Number of days to fetch

        Returns:
            List of daily view counts
        """
        try:
            # Calculate date range
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=days)

            # Format dates for API
            start_str = start_date.strftime('%Y%m%d')
            end_str = end_date.strftime('%Y%m%d')

            # Fetch page views
            url = f'{self.base_url}/metrics/pageviews/per-article/{self.lang.wikipedia}/{title}/daily/{start_str}/{end_str}'
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()

            views = []
            for item in data.get('items', []):
                views.append({
                    'date': item['timestamp'],
                    'views': item['views'],
                    'rank': item.get('rank', 0)
                })

            logger.info(f"Fetched {len(views)} days of view data for '{title}'")
            return views

        except Exception as e:
            logger.error(f"Failed to get page views: {e}")
            return []

    def get_total_articles(self) -> int:
        """Get total number of articles in Wikipedia."""
        try:
            params = {
                'action': 'query',
                'meta': 'siteinfo',
                'siprop': 'statistics',
                'format': 'json'
            }

            response = self.session.get(self.mediawiki_url, params=params)
            response.raise_for_status()
            data = response.json()

            stats = data.get('query', {}).get('statistics', {})
            return stats.get('articles', 0)

        except Exception as e:
            logger.error(f"Failed to get total articles: {e}")
            return 0

    def get_active_editors(self) -> int:
        """Get number of active editors."""
        try:
            params = {
                'action': 'query',
                'meta': 'siteinfo',
                'siprop': 'statistics',
                'format': 'json'
            }

            response = self.session.get(self.mediawiki_url, params=params)
            response.raise_for_status()
            data = response.json()

            stats = data.get('query', {}).get('statistics', {})
            return stats.get('activeusers', 0)

        except Exception as e:
            logger.error(f"Failed to get active editors: {e}")
            return 0

    def get_supported_languages(self) -> List[str]:
        """Get list of supported Wikipedia languages."""
        # Major Wikipedia languages
        return ['en', 'de', 'fr', 'es', 'it', 'ru', 'ja', 'zh', 'pt', 'ar']

    def get_random_articles(self, count: int = 5) -> List[str]:
        """Get random article titles.

        Args:
            count: Number of random articles

        Returns:
            List of article titles
        """
        try:
            params = {
                'action': 'query',
                'list': 'random',
                'rnnamespace': 0,
                'rnlimit': count,
                'format': 'json'
            }

            response = self.session.get(self.mediawiki_url, params=params)
            response.raise_for_status()
            data = response.json()

            titles = [
                item['title']
                for item in data.get('query', {}).get('random', [])
            ]

            return titles

        except Exception as e:
            logger.error(f"Failed to get random articles: {e}")
            return []
