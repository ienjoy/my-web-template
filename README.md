# Climate API & Bay Area Services Web Application

A modular Flask-based web application featuring a RESTful Climate Data API and a Chinese community services listing platform. This project demonstrates modern web development practices including REST API design, data persistence with CSV files, web scraping, and responsive frontend interfaces.

## Project Overview

This application serves two distinct purposes on a unified Flask server:

1. **Climate Data API** - A full-featured REST API for managing and analyzing historical climate data with CRUD operations, statistical analysis, and temperature range filtering
2. **Bay Area Services Web App** - A Chinese-language community services directory powered by automated web scraping

## Features

### Climate API (`/api/*`)
- Full CRUD operations for climate records
- Statistical analysis endpoints (mean, min, max, standard deviation)
- Temperature range filtering with query parameters
- Health check monitoring
- Comprehensive test coverage with pytest

### Bay Area Services (`/`)
- Responsive Chinese-language interface
- Automated web scraping engine
- Category-based service discovery
- CSV-based data persistence

## Project Structure

```
my-web-template/
├── src/                          # Core application logic
│   ├── climate_api.py           # Main Flask application (both APIs and routes)
│   ├── crawler.py               # Web scraper for Bay Area services
│   └── components/              # Reusable HTML/Jinja2 components
├── data/                         # Data persistence layer
│   ├── climate_data.csv         # Historical climate records (Year, Avg_Temp)
│   └── bayarea_services.csv     # Scraped community services (Title, Source)
├── templates/                    # Frontend templates
│   ├── bayarea.html             # Main Chinese services listing page
│   └── index.html               # Alternative template
├── test_api.py                   # Pytest test suite
├── requirements.txt              # Python dependencies
└── .venv/                        # Virtual environment (local only)
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   cd /home/ubuntu/my-web-template
   ```

2. **Create and activate virtual environment**
   ```bash
   # Create virtual environment
   python3 -m venv .venv

   # Activate virtual environment
   # On Linux/MacOS:
   source .venv/bin/activate

   # On Windows:
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   Or install individually:
   ```bash
   pip install flask pandas pytest requests beautifulsoup4
   ```

### Running the Application

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Start the Flask server
python src/climate_api.py
```

The server will start on `http://localhost:5000`

**Access Points:**
- Bay Area Services UI: `http://localhost:5000/`
- Climate API: `http://localhost:5000/api/*`

## API Documentation

### Climate API Endpoints

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/api/health` | Health check | None |
| GET | `/api/climate` | Retrieve all climate records | None |
| GET | `/api/climate/<year>` | Get specific year's data | `year` (path param) |
| POST | `/api/climate` | Add new climate record | JSON: `{"Year": int, "Avg_Temp": float}` |
| GET | `/api/statistics` | Get temperature statistics | None |
| GET | `/api/climate/range` | Filter by temperature range | `min_temp`, `max_temp` (query params) |

### Example API Requests

```bash
# Get all climate data
curl http://localhost:5000/api/climate

# Get specific year
curl http://localhost:5000/api/climate/2020

# Add new record
curl -X POST http://localhost:5000/api/climate \
  -H "Content-Type: application/json" \
  -d '{"Year": 2024, "Avg_Temp": 15.8}'

# Get statistics
curl http://localhost:5000/api/statistics

# Filter by temperature range
curl "http://localhost:5000/api/climate/range?min_temp=10&max_temp=20"
```

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest test_api.py -v

# Run specific test class
pytest test_api.py::TestClimateAPI -v
```

Tests cover:
- Health check endpoints
- CRUD operations
- Error handling (404 responses)
- Statistical calculations
- Temperature range filtering

## Web Scraping

Collect Bay Area services data:

```bash
python src/crawler.py
```

The scraper will:
- Start from base URL (`https://www.dadi360.com/`)
- Automatically discover category pages
- Extract service titles (15-80 characters)
- Output to `data/bayarea_services.csv`

## Development Guidelines

### Extension Standards

- **New APIs**: Prefix with `/api/v2/` and add corresponding tests in `test_api.py`
- **New Pages**: Create templates in `templates/` and add routes in `src/climate_api.py`
- **Data Files**: Store all CSV files in `data/` directory
- **Business Logic**: Place all Python scripts in `src/` directory
- **API Format**: Return JSON with `status` field

### Known Issues

- Critical: Line 20 in `src/climate_api.py` may have commented out `df` variable loading. Ensure `df = pd.read_csv('data/climate_data.csv')` is active for API functionality.

## Deployment

**Production Environment:** AWS EC2 (Ubuntu 22.04)

**Pre-deployment Checklist:**
1. Run full test suite: `pytest test_api.py -v`
2. Verify all tests pass
3. Set environment variables in `~/.bashrc` (not `.env` file)
4. Ensure data files exist in `data/` directory

## Contributing

This is an educational project for learning:
- REST API design patterns
- Flask framework fundamentals
- Pandas data manipulation
- Web scraping with BeautifulSoup
- Unit testing with pytest

Refer to `lab_guide.md` for educational exercises and progressive challenges.

## Troubleshooting

**API Error: `df` undefined**
- Check `src/climate_api.py` line 20
- Ensure `df = pd.read_csv('data/climate_data.csv')` is uncommented
- Verify `data/climate_data.csv` exists

**Scraper Returns No Data**
- Verify `base_url` is accessible
- Add `headers` to simulate browser requests in `crawler.py`

**Virtual Environment Issues**
```bash
# Deactivate and recreate
deactivate
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## License

Educational project - see institution guidelines for usage terms.
