# Jobsite Scraper and Analyzer

[![Scrapy](https://img.shields.io/badge/Scrapy-2.11.2-brightgreen.svg)](https://scrapy.org/)
[![Selenium](https://img.shields.io/badge/Selenium-4.27.1-blue.svg)](https://selenium.dev/)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-brightgreen.svg)](https://flask.palletsprojects.com/)
[![Pandas](https://img.shields.io/badge/Pandas-2.2.2-ab5591.svg)](https://pandas.pydata.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-3.8.4-120108.svg)](https://matplotlib.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.31-e35f0e.svg)](https://www.sqlalchemy.org/)
[![Redis](https://img.shields.io/badge/Redis-5.2.1-e8e7e6.svg)](https://redis.io/)
[![MySQL](https://img.shields.io/badge/MySQL-9.0.0-fc1c03.svg)](https://www.mysql.com/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg)](https://www.docker.com/)

## Overview

A comprehensive web scraping and data analysis platform that extracts job listings from [theprotocol.it](https://theprotocol.it/) to analyze technology demand trends for developers in the Polish job market. The system provides automated data collection, intelligent analysis, and interactive visualizations to help developers understand market requirements and prioritize their learning efforts.

## 🚀 Features

### Core Functionality
- **Multi-Position Support**: Configurable job position targeting (Python, Java, JavaScript, etc.)
- **Automated Scraping**: Scheduled data collection using Celery and Redis
- **Intelligent Data Processing**: Natural language processing with NLTK and fuzzy matching
- **Interactive Visualizations**: Comprehensive charts and graphs using Matplotlib
- **RESTful API**: Flask-based web service for data access
- **Containerized Deployment**: Full Docker and Docker Compose support

### Technical Capabilities
- **Advanced Web Scraping**: Scrapy + Selenium integration for JavaScript-rendered content
- **Robust Data Pipeline**: Custom ItemPipelines and Middlewares
- **Database Integration**: MySQL with SQLAlchemy ORM
- **Task Queue Management**: Celery with Redis broker
- **Production-Ready**: Nginx reverse proxy configuration

## 🛠 Technology Stack

| Category | Technologies |
|----------|-------------|
| **Web Scraping** | Scrapy, Selenium, scrapy-selenium4 |
| **Data Processing** | Pandas, NLTK, fuzzywuzzy |
| **Visualization** | Matplotlib, Jupyter |
| **Web Framework** | Flask, SQLAlchemy |
| **Task Queue** | Celery, Redis |
| **Database** | MySQL |
| **Infrastructure** | Docker, Docker Compose, Nginx |

## 📊 Analytics Dashboard

The platform generates comprehensive visualizations including:

- **Skills Analysis**: Required vs. optional technical skills
- **Experience Levels**: Distribution of seniority requirements
- **Employment Types**: Contract types and arrangements
- **Geographic Distribution**: Location-based job distribution
- **Market Trends**: Technology demand over time
- **Ukraine Support**: Companies supporting Ukrainian developers

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/danieladdisonorg/Jobsite-Scraper-and-Analyzer.git
cd Jobsite-Scraper-and-Analyzer
```

2. **Configure environment variables**
```bash
cp .env.sample .env
```
Edit `.env` file with your configuration settings.

3. **Launch the application**
```bash
docker-compose up --build
```

4. **Access the application**
Navigate to `http://localhost:8000/scraping/diagrams`

## 📖 API Documentation

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/scraping/diagrams` | GET | Initiates data analysis and returns Celery task ID |
| `/scraping/diagrams/<task_id>` | GET | Checks task status and retrieves results |

### Configuration

Modify `config.py` to customize scraping parameters:

```python
# Target job position (lowercase)
POSITION = "python"  # Options: "java", "javascript", "dev", etc.

# Scraping frequency
SCRAPING_EVERY_DAYS = 7
```

## 🏗 Architecture

```
├── analyzing/          # Data analysis and visualization modules
├── web_server/         # Flask web application
├── main_celery/        # Celery configuration and tasks
├── static/             # Static assets and scraping results
├── config.py           # Application configuration
├── docker-compose.yml  # Container orchestration
└── requirements.txt    # Python dependencies
```

## 📈 Sample Visualizations

<div align="center">

### Skills by Experience Level
![Skills by Experience Level](./static/readme_imgs/skills_by_level_of_exp_dia.png)

### Required Technical Skills
![Required Skills](./static/readme_imgs/required_skills_dia.png)

### Optional Technical Skills
![Optional Skills](./static/readme_imgs/optional_skills_dia.png)

### Experience Level Distribution
![Experience Levels](./static/readme_imgs/level_of_exp_dia.png)

### Employment Types
![Employment Types](./static/readme_imgs/employment_type_dia.png)

### Geographic Distribution
![Locations](./static/readme_imgs/locations_dia.png)

</div>

## 🔧 Development

### Key Learning Outcomes
- **Web Scraping Mastery**: Advanced techniques with Scrapy and Selenium
- **Data Pipeline Development**: ETL processes and data transformation
- **Asynchronous Task Processing**: Celery and Redis implementation
- **Containerization**: Docker and microservices architecture
- **Data Visualization**: Statistical analysis and chart generation

### Future Enhancements

#### High Priority
- [ ] **Cloud Storage Integration**: Migrate from local file storage to cloud solutions (AWS S3, Google Cloud Storage)
- [ ] **Database Optimization**: Implement proper data warehousing for scraped content
- [ ] **Container Optimization**: Reduce Docker image sizes and improve build efficiency

#### Medium Priority
- [ ] **Code Architecture**: Refactor to follow SOLID principles and improve modularity
- [ ] **Comprehensive Testing**: Unit, integration, and end-to-end test coverage
- [ ] **CI/CD Pipeline**: Automated testing and deployment workflows
- [ ] **API Documentation**: OpenAPI/Swagger integration

#### Low Priority
- [ ] **Real-time Analytics**: WebSocket integration for live data updates
- [ ] **Machine Learning**: Predictive analytics for job market trends
- [ ] **Multi-language Support**: Expand beyond Polish job market

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

**Daniel Addison**
- GitHub: [@danieladdisonorg](https://github.com/danieladdisonorg)
- Project Link: [https://github.com/danieladdisonorg/Jobsite-Scraper-and-Analyzer](https://github.com/danieladdisonorg/Jobsite-Scraper-and-Analyzer)

---

<div align="center">
<strong>⭐ Star this repository if you find it helpful!</strong>
</div>
