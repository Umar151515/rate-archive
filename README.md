# Currency History Tracker

Automated script to fetch historical exchange rates and store them in JSON and SQLite formats.

## Data Coverage
* **Start Date:** 2004-09-27
* **Known Issues:** ~25% of dates are missing; some currencies have incomplete historical records.

## Data Structure

### 1. currency_history.json
Stores the primary configuration and raw history.
* `base_currency`: The currency used as a base for all rates.
* `latest_update`: String date of the last successful fetch (YYYY-MM-DD).
* `rates_history`: Dictionary where keys are dates and values are objects containing currency codes and rates.

### 2. currency_history.db (SQLite)
* **Table `rates`**: Columns `date` (Unix timestamp), `currency` (code), `rate` (value).
* **Table `info`**: Columns `base_currency` and `latest_update` (Unix timestamp).

## Automation
The project uses GitHub Actions to run the update script daily via cron.