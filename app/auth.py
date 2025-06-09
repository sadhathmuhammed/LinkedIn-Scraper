from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import os

security = HTTPBasic()
USER = os.getenv("API_USER", "admin")
PASS = os.getenv("API_PASS", "secret")

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Check if the user is authenticated using HTTP Basic Auth.

    This function relies on the `security` dependency from FastAPI, which
    expects the username and password to be sent in a `Authorization` header.
    It checks the credentials against the `API_USER` and `API_PASS` environment
    variables, and raises an HTTPException if the credentials are incorrect.

    Returns the username of the authenticated user.
    """
    correct_username = secrets.compare_digest(credentials.username, USER)
    correct_password = secrets.compare_digest(credentials.password, PASS)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
