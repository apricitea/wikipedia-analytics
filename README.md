# Wikipedia Analytics Dashboard 📊

A real-time analytics dashboard for exploring Wikipedia statistics and trends.

## Features

- 🔍 **Article Search**: Search and analyze any Wikipedia article
- 📈 **View Statistics**: Track page views over time
- 🌍 **Language Comparison**: Compare articles across languages
- 📊 **Data Visualization**: Interactive charts and graphs
- 🎨 **Modern UI**: Clean, responsive design

## Tech Stack

- **Backend**: Python 3.9+ / Flask 3.0+
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Charts**: Chart.js 4.x
- **API**: Wikipedia REST API, MediaWiki API
- **Data**: Pandas, NumPy

## Installation

```bash
# Clone the repository
git clone https://github.com/apricitea/wikipedia-analytics.git
cd wikipedia-analytics

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run the Flask server
python app.py

# Open browser to http://localhost:5000
```

## API Endpoints

- `GET /api/article/<title>` - Get article statistics
- `GET /api/search/<query>` - Search Wikipedia articles
- `GET /api/views/<title>` - Get page view data
- `GET /api/languages/<title>` - Get available language versions

## Project Structure

```
wikipedia-analytics/
├── app.py                 # Flask application
├── api/
│   ├── __init__.py
│   ├── wikipedia.py       # Wikipedia API client
│   └── analytics.py       # Data analysis functions
├── static/
│   ├── css/
│   │   └── style.css      # Main stylesheet
│   └── js/
│       ├── app.js         # Frontend application
│       └── charts.js      # Chart configurations
├── templates/
│   └── index.html         # Main dashboard
└── requirements.txt       # Python dependencies
```

## Features in Detail

### Article Analysis
- Article length and structure
- Citation statistics
- Image/media count
- Revision history

### View Analytics
- Daily page views (last 30 days)
- Mobile vs desktop views
- Geographic distribution

### Language Comparison
- Available translations
- Article length by language
- Cross-language popularity

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for any purpose.

## Acknowledgments

- Wikipedia API for data access
- Chart.js for visualizations
- Flask for the web framework
