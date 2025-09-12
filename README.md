# Strava Analytics Dashboard

A comprehensive local web application for tracking and analyzing your Strava activity data with daily automatic updates.

## Features

### Dashboard Views
- **Daily, Weekly, Monthly** activity summaries
- **Progress tracking** with activity counts, distance, elevation gain, and time
- **Streak tracking** showing consecutive days and total active days
- **Goal tracking** for weekly distance targets
- **Interactive graphs** with week/month comparison capabilities
- **Monthly calendar view** showing daily activity status
- **Relative Effort analysis**
- **Monthly recap reports**

### Activity Management
- Filterable activity list
- Individual activity records showing:
  - Activity name
  - Completion time
  - Distance and elevation
  - Route maps
  - Year-over-year comparisons

## Technical Implementation

### Data Pipeline
- Python script using Strava API v3
- Daily cron job for automatic data updates
- Database schema with tables for:
  - Activities
  - Athlete
  - Club
  - Equipment
  - Routes
  - Segment
  - Stream
  - Load

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/hectorflores28/flask-strava-analytics-dashboard
   cd strava-python-project
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Strava API credentials**
   - Register an application at [Strava API Settings](https://www.strava.com/settings/api)
   - Update `config.py` with your client ID and secret

4. **Initialize database**
   ```bash
   python init_db.py
   ```

5. **Set up cron job for daily updates**
   ```bash
   # Add to crontab (crontab -e)
   0 2 * * * cd /path/to/strava-python-project && python daily_update.py
   ```

6. **Run the web application**
   ```bash
   python app.py
   ```

### Project Structure
```
strava-python-project/
├── StravaAPIv3.md          # API reference documentation
├── config.py               # Configuration settings
├── daily_update.py         # Daily data update script
├── init_db.py              # Database initialization
├── app.py                  # Web application
├── models.py               # Database models
├── requirements.txt        # Python dependencies
└── templates/              # Web templates
    ├── index.html          # Dashboard
    ├── activities.html     # Activity list
    └── monthly.html        # Monthly view
```

## API Reference
See [Strava API v3 Documentation](StravaAPIv3.md) in the root directory for complete Strava API v3 documentation and endpoint details.

## Development
This project uses:
- Python 3.8+
- Flask web framework
- SQLite database (can be configured for other databases)
- Strava API v3 with OAuth2 authentication

## Support
For issues and questions, please refer to:
- Strava API documentation: https://developers.strava.com/docs/reference/
- Project issues page

---

*This project is not affiliated with Strava, Inc. but uses their API according to their terms of service.*