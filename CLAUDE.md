# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Universal Web App Template designed for Flask. It supports automated web scraping (crawler), RESTful API development (v2 standards), and responsive Chinese-language frontend interfaces.:

1. **Climate Data API** - Educational REST API lab teaching Flask fundamentals, data handling, and testing
2. **Bay Area Services Web App** - Chinese community services listing site with web scraping functionality

Both applications share the same Flask server but serve different purposes and data sources.

## Key Commands

### Running the Applications

```bash
# Start the Flask server (runs both apps)
python climate_api.py

# Access the applications:
# - Bay Area services web UI: http://localhost:5000/
# - Climate API endpoints: http://localhost:5000/api/*
```

### Testing

```bash
# Run all unit tests
pytest test_api.py -v

# Run specific test class
pytest test_api.py::TestClimateAPI -v
```

### Data Collection

```bash
# Run the web scraper to collect Bay Area services data
python crawler.py

# Output: bayarea_services.csv
```

### Installing Dependencies

```bash
pip install flask pandas pytest requests beautifulsoup4
```

## Architecture

### Directory Structure (新目录结构)
- `src/`: 核心逻辑与后端脚本 (如 `climate_api.py`, `crawler.py`)。
- `src/components/`: 可复用的 HTML/Jinja2 组件。
- `templates/`: 网页主入口文件 (如 `bayarea.html`)。
- `data/`: 存放所有 CSV 数据文件。

### 扩展规范 (Extension Standards - 你的开发准则)
- **代码位置**：所有新的业务逻辑（Python 脚本）必须放在 `src/` 目录下。
- **数据管理**：所有 CSV 数据库文件必须存放在 `data/` 目录中。
- **添加新页面**：在 `templates/` 下创建 `.html` 文件，并在 `src/` 下的代码中添加路由。
- **添加新 API**：所有新 API 必须以 `/api/v2/` 开头，并确保在 `test_api.py` 中同步添加对应的测试用例。
- **API 规范**：必须返回 JSON 格式，并包含 `status` 字段（示例：`GET /api/v2/services`）。
- **UI 风格**：遵循 `bayarea.html` 中的 CSS 类命名方式，保持中文社区服务的视觉一致性。

### 应用逻辑 (Application Logic)
该项目采用双用途 Flask 设计：
1. **Web UI (`/`)**: 渲染 `templates/bayarea.html`，展示从 `data/bayarea_services.csv` 读取的服务信息。
2. **REST API (`/api/*`)**: 提供气候数据的 CRUD 操作，读取 `data/climate_data.csv`。

### Data Flow (数据流更新)

```
src/crawler.py → data/bayarea_services.csv → src/climate_api.py (/) → templates/bayarea.html

data/climate_data.csv → src/climate_api.py (/api/*) → JSON responses
```

### Important Code Issues (待处理问题)
**Critical Bug**: `src/climate_api.py` 中的 `df` 变量加载问题需优先修复，确保路径指向 `data/climate_data.csv`。

## Climate API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/climate` | Retrieve all climate records |
| GET | `/api/climate/<year>` | Get specific year's data |
| POST | `/api/climate` | Add new climate record |
| GET | `/api/statistics` | Temperature statistics (mean, min, max, std) |
| GET | `/api/climate/range` | Filter by temperature range (query params: `min_temp`, `max_temp`) |
| GET | `/api/health` | Health check endpoint |

## Data Files

- **climate_data.csv**: Historical climate data with columns: `Year`, `Avg_Temp`
- **bayarea_services.csv**: Scraped Chinese community services with columns: `Title`, `Source`

## Web Scraping Logic

The `crawler.py` implements an automated discovery engine:
- Starts from a base URL (`https://www.dadi360.com/`)
- Automatically discovers category pages by finding links containing "list" or "class"
- Crawls first 50 category pages
- Extracts titles between 15-80 characters
- Outputs to CSV with source tracking

## Testing Architecture

Located in `test_api.py`:
- Uses pytest fixtures for test client setup
- Class-based test organization (`TestClimateAPI`)
- Tests cover: health checks, CRUD operations, error handling (404s), statistics, and filtering
- Run tests before deploying API changes

## Templates

Flask templates in `templates/`:
- `bayarea.html`: Chinese-language community services listing page with Jinja2 templating
- `index.html`: Alternative template (not currently used)

## Development Context

This is a VM-based learning environment for students learning:
- REST API design patterns
- Flask framework basics
- Pandas data manipulation
- Web scraping with BeautifulSoup
- Unit testing with pytest

Reference `lab_guide.md` for educational exercises and progressive difficulty challenges.

## 常见故障排除 (Troubleshooting)
- **API 报错未定义 df**：检查 `climate_api.py` 第 20 行，确保 `df = pd.read_csv('climate_data.csv')` 已取消注释并能正确加载文件。
- **爬虫无数据**：检查 `crawler.py` 的 `base_url` 是否可访问，或增加 `headers` 模拟浏览器访问。

## 部署指南 (Deployment Context)
- **生产环境**：AWS EC2 (Ubuntu 22.04)。
- **环境变量**：在生产环境中，不要修改 `.env` 文件，直接在 EC2 的 `~/.bashrc` 中设置。
- **注意事项**：部署前必须运行 `pytest` 确保所有 API 测试通过。

