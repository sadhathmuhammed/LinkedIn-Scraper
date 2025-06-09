# LinkedIn Connections Scraper API

A secure API service that logs into LinkedIn using Selenium, retrieves the logged-in user's connections using LinkedIn's internal Voyager APIs, and returns paginated data.

## Features

- Secure API using Basic Auth
- Uses Selenium to log in to LinkedIn
- Fetches connection data using internal Voyager APIs
- Session persistence to avoid repeated login
- Pagination support

## Setup

```bash
git clone https://github.com/youruser/linkedin-scraper-api
cd linkedin-scraper-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

- Add username and password of linkedin account in .env file

uvicorn app.main:app --reload
```

## API Endpoints

- GET /connections
    
Query Parameters:
start: int — Index to start from
count: int — Number of results to return

Headers:
Authorization: Bearer <session_token>

Eg: http://127.0.0.1:8000/connections?start=0&count=10

## Run tests

```PYTHONPATH=. pytest```
