/**
 * Wikipedia Analytics Dashboard
 * Main application logic
 */

// Global state
let currentChart = null;
let searchTimeout = null;

// DOM Elements
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const searchResults = document.getElementById('searchResults');
const dashboard = document.getElementById('dashboard');
const loadingOverlay = document.getElementById('loadingOverlay');
const errorToast = document.getElementById('errorToast');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadTrendingArticles();
});

/**
 * Setup event listeners
 */
function setupEventListeners() {
    searchBtn.addEventListener('click', handleSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    });

    // Debounced search
    searchInput.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        const query = searchInput.value.trim();

        if (query.length > 2) {
            searchTimeout = setTimeout(() => {
                fetchSearchResults(query);
            }, 300);
        } else {
            searchResults.innerHTML = '';
        }
    });
}

/**
 * Handle search button click
 */
async function handleSearch() {
    const query = searchInput.value.trim();
    if (!query) return;

    try {
        showLoading();

        // Search for the article
        const results = await fetchSearchResults(query);

        if (results.length > 0) {
            // Load the first result
            await loadArticle(results[0].title);
        } else {
            // Try direct article lookup
            await loadArticle(query);
        }

        hideLoading();
    } catch (error) {
        hideLoading();
        showError(error.message);
    }
}

/**
 * Fetch search results from API
 */
async function fetchSearchResults(query) {
    try {
        const response = await fetch(`/api/search/${encodeURIComponent(query)}`);
        const data = await response.json();

        if (data.success && data.results.length > 0) {
            displaySearchResults(data.results);
            return data.results;
        }

        return [];
    } catch (error) {
        console.error('Search error:', error);
        return [];
    }
}

/**
 * Display search results dropdown
 */
function displaySearchResults(results) {
    searchResults.innerHTML = results.map(result => `
        <div class="search-result-item" onclick="loadArticle('${escapeHtml(result.title)}')">
            <div class="search-result-title">${escapeHtml(result.title)}</div>
            <div class="search-result-snippet">${escapeHtml(result.snippet || 'No description available')}</div>
        </div>
    `).join('');
}

/**
 * Load article data and display dashboard
 */
async function loadArticle(title) {
    try {
        showLoading();

        // Fetch article data
        const response = await fetch(`/api/article/${encodeURIComponent(title)}`);
        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || 'Failed to load article');
        }

        // Update UI
        updateArticleInfo(data.article);
        updateViewStats(data.views);
        updateCategories(data.article.categories || []);
        updateRecentActivity(data.article.revisions || []);

        // Show dashboard
        dashboard.style.display = 'grid';
        searchResults.innerHTML = ''; // Clear search results

        // Analyze quality
        await analyzeArticleQuality(title);

        hideLoading();
    } catch (error) {
        hideLoading();
        showError(error.message);
    }
}

/**
 * Update article information section
 */
function updateArticleInfo(article) {
    document.getElementById('articleTitle').textContent = article.title;

    const extract = article.extract || 'No description available.';
    document.getElementById('articleExtract').textContent =
        extract.length > 500 ? extract.substring(0, 500) + '...' : extract;

    document.getElementById('articleLength').textContent = formatNumber(article.length || 0);
    document.getElementById('categoryCount').textContent = article.category_count || 0;
    document.getElementById('imageCount').textContent = article.image_count || 0;
    document.getElementById('revisionCount').textContent = article.revision_count || 0;
}

/**
 * Update view statistics
 */
function updateViewStats(views) {
    document.getElementById('totalViews').textContent = formatNumber(views.total || 0);
    document.getElementById('avgViews').textContent = formatNumber(Math.round(views.average || 0));
    document.getElementById('maxViews').textContent = formatNumber(views.max || 0);

    const trendElement = document.getElementById('viewTrend');
    trendElement.textContent = (views.trend || 'neutral').charAt(0).toUpperCase() + (views.trend || 'neutral').slice(1);
    trendElement.className = 'summary-value trend ' + (views.trend || 'neutral');

    // Update chart
    updateViewsChart(views.daily || []);
}

/**
 * Update categories list
 */
function updateCategories(categories) {
    const container = document.getElementById('categoriesList');

    if (categories.length === 0) {
        container.innerHTML = '<p class="text-gray-500">No categories</p>';
        return;
    }

    container.innerHTML = categories.slice(0, 15).map(cat =>
        `<span class="category-tag">${escapeHtml(cat.replace('Category:', ''))}</span>`
    ).join('');
}

/**
 * Update recent activity
 */
function updateRecentActivity(revisions) {
    const container = document.getElementById('recentEdits');

    if (revisions.length === 0) {
        container.innerHTML = '<p class="text-gray-500">No recent activity</p>';
        return;
    }

    container.innerHTML = revisions.map(rev => `
        <div class="activity-item">
            <div class="activity-user">${escapeHtml(rev.user || 'Anonymous')}</div>
            <div class="activity-time">${formatDate(rev.timestamp)}</div>
        </div>
    `).join('');
}

/**
 * Update views chart
 */
function updateViewsChart(dailyViews) {
    const ctx = document.getElementById('viewsChart').getContext('2d');

    // Destroy existing chart
    if (currentChart) {
        currentChart.destroy();
    }

    // Prepare data
    const labels = dailyViews.map(v => formatDate(v.date));
    const data = dailyViews.map(v => v.views);

    // Create gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(37, 99, 235, 0.3)');
    gradient.addColorStop(1, 'rgba(37, 99, 235, 0.0)');

    // Create chart
    currentChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Daily Views',
                data: data,
                borderColor: '#2563eb',
                backgroundColor: gradient,
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 2,
                pointHoverRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: { size: 14 },
                    bodyFont: { size: 13 },
                    displayColors: false,
                    callbacks: {
                        label: (context) => {
                            return `${formatNumber(context.raw)} views`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45,
                        font: { size: 11 }
                    }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: (value) => formatNumber(value)
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

/**
 * Analyze article quality
 */
async function analyzeArticleQuality(title) {
    try {
        // For now, use a simple quality calculation
        // In production, this would call a quality analysis endpoint

        const response = await fetch(`/api/article/${encodeURIComponent(title)}`);
        const data = await response.json();

        if (data.success) {
            const article = data.article;
            const score = calculateQualityScore(article);
            displayQualityScore(score);
        }
    } catch (error) {
        console.error('Quality analysis error:', error);
    }
}

/**
 * Calculate quality score (simplified)
 */
function calculateQualityScore(article) {
    let score = 0;
    const factors = [];

    const length = article.length || 0;
    if (length > 10000) {
        score += 30;
        factors.push('Comprehensive content');
    } else if (length > 5000) {
        score += 20;
        factors.push('Good length');
    }

    const catCount = article.category_count || 0;
    if (catCount > 10) {
        score += 20;
        factors.push('Well categorized');
    }

    const imgCount = article.image_count || 0;
    if (imgCount > 5) {
        score += 15;
        factors.push('Rich media');
    }

    const revCount = article.revision_count || 0;
    if (revCount > 50) {
        score += 20;
        factors.push('Active development');
    }

    return {
        score: Math.min(100, score),
        factors: factors
    };
}

/**
 * Display quality score
 */
function displayQualityScore(quality) {
    const scoreElement = document.getElementById('qualityScore');
    const gradeElement = document.getElementById('qualityGrade');
    const factorsElement = document.getElementById('qualityFactors');

    const score = quality.score;
    scoreElement.querySelector('.score-value').textContent = score;

    // Determine grade
    let grade;
    if (score >= 80) grade = 'A - Excellent';
    else if (score >= 60) grade = 'B - Good';
    else if (score >= 40) grade = 'C - Average';
    else grade = 'D - Needs work';

    gradeElement.textContent = grade;

    // Display factors
    factorsElement.innerHTML = quality.factors.map(f => `<li>${escapeHtml(f)}</li>`).join('');
}

/**
 * Load trending articles
 */
async function loadTrendingArticles() {
    try {
        const response = await fetch('/api/trending?limit=5');
        const data = await response.json();

        if (data.success && data.trending) {
            displayTrendingArticles(data.trending);
        }
    } catch (error) {
        console.error('Failed to load trending:', error);
    }
}

/**
 * Display trending articles
 */
function displayTrendingArticles(trending) {
    const container = document.getElementById('trendingList');

    if (!trending || trending.length === 0) {
        container.innerHTML = '<p class="text-gray-500">No trending articles</p>';
        return;
    }

    container.innerHTML = trending.map(article => `
        <div class="trending-item" onclick="loadArticle('${escapeHtml(article.title)}')">
            <div class="trending-title">${escapeHtml(article.title)}</div>
            <div class="trending-views">📈 ${formatNumber(article.views_week)} views this week</div>
        </div>
    `).join('');
}

/**
 * Utility functions
 */
function showLoading() {
    loadingOverlay.classList.add('active');
}

function hideLoading() {
    loadingOverlay.classList.remove('active');
}

function showError(message) {
    errorToast.textContent = message;
    errorToast.classList.add('active');
    setTimeout(() => {
        errorToast.classList.remove('active');
    }, 5000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    return date.toLocaleDateString();
}
