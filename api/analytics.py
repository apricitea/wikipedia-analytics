"""
Analytics Engine
Processes Wikipedia data and generates insights.
"""

import requests
import datetime
from typing import Dict, List
import logging

from .wikipedia import WikipediaAPI

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """Engine for analyzing Wikipedia data."""

    def __init__(self):
        self.wiki = WikipediaAPI()

    def get_view_stats(self, title: str, days: int = 30) -> Dict:
        """Get comprehensive view statistics for an article.

        Args:
            title: Article title
            days: Number of days to analyze

        Returns:
            Dictionary with view statistics
        """
        try:
            view_data = self.wiki.get_page_views(title, days=days)

            if not view_data:
                return {
                    'total': 0,
                    'average': 0,
                    'max': 0,
                    'min': 0,
                    'trend': 'neutral',
                    'daily': []
                }

            # Calculate statistics
            views_list = [v['views'] for v in view_data]
            total_views = sum(views_list)
            avg_views = total_views / len(views_list)
            max_views = max(views_list)
            min_views = min(views_list)

            # Determine trend
            if len(views_list) >= 7:
                recent_avg = sum(views_list[-7:]) / 7
                earlier_avg = sum(views_list[:-7]) / (len(views_list) - 7)
                if recent_avg > earlier_avg * 1.1:
                    trend = 'increasing'
                elif recent_avg < earlier_avg * 0.9:
                    trend = 'decreasing'
                else:
                    trend = 'stable'
            else:
                trend = 'neutral'

            return {
                'total': total_views,
                'average': round(avg_views, 2),
                'max': max_views,
                'min': min_views,
                'trend': trend,
                'daily': view_data
            }

        except Exception as e:
            logger.error(f"Failed to get view stats: {e}")
            return {}

    def compare_articles(self, titles: List[str]) -> Dict:
        """Compare multiple Wikipedia articles.

        Args:
            titles: List of article titles to compare

        Returns:
            Comparison data
        """
        try:
            articles_data = []

            for title in titles:
                try:
                    info = self.wiki.get_article_info(title)
                    views = self.get_view_stats(title, days=30)

                    articles_data.append({
                        'title': title,
                        'length': info.get('length', 0),
                        'categories': info.get('category_count', 0),
                        'images': info.get('image_count', 0),
                        'revisions': info.get('revision_count', 0),
                        'views_30day': views.get('total', 0),
                        'avg_daily_views': views.get('average', 0),
                        'trend': views.get('trend', 'neutral')
                    })
                except Exception as e:
                    logger.warning(f"Could not fetch data for '{title}': {e}")

            # Calculate rankings
            if articles_data:
                # Find winners in each category
                longest = max(articles_data, key=lambda x: x['length'])
                most_views = max(articles_data, key=lambda x: x['views_30day'])
                most_revisions = max(articles_data, key=lambda x: x['revisions'])

                return {
                    'articles': articles_data,
                    'rankings': {
                        'longest': longest['title'],
                        'most_viewed': most_views['title'],
                        'most_revised': most_revisions['title']
                    }
                }

            return {'articles': [], 'rankings': {}}

        except Exception as e:
            logger.error(f"Comparison failed: {e}")
            raise

    def get_trending_articles(self, limit: int = 10) -> List[Dict]:
        """Get currently trending Wikipedia articles.

        Args:
            limit: Maximum number of articles to return

        Returns:
            List of trending articles with stats
        """
        try:
            # Get random articles (simulating trending)
            titles = self.wiki.get_random_articles(count=limit * 2)

            trending = []
            for title in titles[:limit]:
                try:
                    info = self.wiki.get_article_info(title)
                    views = self.get_view_stats(title, days=7)  # Last 7 days

                    trending.append({
                        'title': title,
                        'url': info.get('url', ''),
                        'extract': info.get('extract', '')[:200] + '...',
                        'views_week': views.get('total', 0),
                        'trend': views.get('trend', 'neutral')
                    })
                except Exception as e:
                    logger.warning(f"Could not fetch trending data for '{title}': {e}")

            # Sort by views
            trending.sort(key=lambda x: x['views_week'], reverse=True)
            return trending

        except Exception as e:
            logger.error(f"Failed to get trending articles: {e}")
            return []

    def analyze_article_quality(self, title: str) -> Dict:
        """Analyze the quality of a Wikipedia article.

        Args:
            title: Article title

        Returns:
            Quality metrics and score
        """
        try:
            info = self.wiki.get_article_info(title)

            # Quality indicators
            score = 0
            factors = []

            # Length (longer articles tend to be more comprehensive)
            length = info.get('length', 0)
            if length > 10000:
                score += 30
                factors.append('Comprehensive content')
            elif length > 5000:
                score += 20
                factors.append('Good length')
            elif length > 2000:
                score += 10
                factors.append('Basic coverage')

            # Categories
            cat_count = info.get('category_count', 0)
            if cat_count > 10:
                score += 20
                factors.append('Well categorized')
            elif cat_count > 5:
                score += 10
                factors.append('Some categorization')

            # Images
            img_count = info.get('image_count', 0)
            if img_count > 5:
                score += 15
                factors.append('Rich media')
            elif img_count > 0:
                score += 5
                factors.append('Has images')

            # Recent activity
            rev_count = info.get('revision_count', 0)
            if rev_count > 50:
                score += 20
                factors.append('Active development')
            elif rev_count > 10:
                score += 10
                factors.append('Some activity')

            # Citations (estimated from extract)
            extract = info.get('extract', '')
            if '[citation' in extract or 'CN' in extract:
                factors.append('Needs citations')
                score -= 10

            # Determine grade
            if score >= 80:
                grade = 'A - Excellent'
            elif score >= 60:
                grade = 'B - Good'
            elif score >= 40:
                grade = 'C - Average'
            else:
                grade = 'D - Needs work'

            return {
                'score': max(0, min(100, score)),
                'grade': grade,
                'factors': factors,
                'metrics': {
                    'length': length,
                    'categories': cat_count,
                    'images': img_count,
                    'revisions': rev_count
                }
            }

        except Exception as e:
            logger.error(f"Quality analysis failed: {e}")
            return {'score': 0, 'grade': 'Unknown', 'factors': [], 'metrics': {}}
