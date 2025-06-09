from fastapi import FastAPI, Depends, HTTPException, Query
from app.auth import get_current_user
from app.linkedin import LinkedInScraper
from app.models import ConnectionResponse

app = FastAPI()

def get_scraper():
    return LinkedInScraper()

@app.get("/connections", response_model=ConnectionResponse)
def get_connections(
    start: int = Query(0), count: int = Query(10),
    scraper: LinkedInScraper = Depends(get_scraper),
    user: str = Depends(get_current_user)
):
    """
    Fetch LinkedIn connections.

    Args:
        start (int): The index of the first connection to return. Defaults to 0.
        count (int): The number of connections to return. Defaults to 10.
        user (str): The user to fetch connections for.

    Returns:
        list[Connection]: A list of connections.
    """
    try:
        connections = scraper.fetch_connections(start=start, count=count)
        return {"connections": connections, "start": start, "count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
