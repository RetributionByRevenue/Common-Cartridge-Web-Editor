from fastapi import HTTPException, Depends, Request
from fastapi.responses import RedirectResponse

# User credentials
users = {
    "mark": "pass123",
    "luke": "pass456"
}

def get_current_user(request: Request):
    """Check if user is logged in via session"""
    username = request.session.get("username")
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return username

def require_login(request: Request):
    """Redirect to login if not authenticated"""
    username = request.session.get("username")
    if not username:
        return RedirectResponse(url="/login", status_code=303)
    return username

def verify_credentials(username: str, password: str):
    """Verify username and password"""
    return username in users and users[username] == password