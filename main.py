from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import os
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pydantic import BaseModel, validator, Field
from auth import login_user, signup_user, reset_password
from exercises import get_exercise_suggestions
from workouts import create_workout_session, add_set_to_session, get_current_session, get_sessions_by_date, rename_workout_session, get_all_sessions, duplicate_set, edit_set, remove_set, get_session_sets
from config import CORS_ORIGINS, RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW, ENVIRONMENT

app = FastAPI(title="Workout Tracker", version="1.0.0")

# Security middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Add trusted host middleware for production
if ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["your-domain.com", "*.your-domain.com"]
    )

# Rate limiting middleware
rate_limit_storage = defaultdict(list)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    current_time = datetime.now()
    
    # Clean old requests
    rate_limit_storage[client_ip] = [
        req_time for req_time in rate_limit_storage[client_ip]
        if current_time - req_time < timedelta(seconds=RATE_LIMIT_WINDOW)
    ]
    
    # Check rate limit
    if len(rate_limit_storage[client_ip]) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Add current request
    rate_limit_storage[client_ip].append(current_time)
    
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    return response

# Serve React build files
if os.path.exists("dist"):
    app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")
else:
    # Fallback to static files if dist doesn't exist
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    if os.path.exists("dist/index.html"):
        return FileResponse("dist/index.html")
    else:
        return FileResponse("static/index.html")

# Request models with validation
class LoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=254)
    password: str = Field(..., min_length=8, max_length=128)
    
    @validator('email')
    def validate_email(cls, v):
        import re
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', v):
            raise ValueError('Invalid email format')
        return v

class SignupRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=254)
    password: str = Field(..., min_length=8, max_length=128)
    
    @validator('email')
    def validate_email(cls, v):
        import re
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', v):
            raise ValueError('Invalid email format')
        return v

class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=254)
    
    @validator('email')
    def validate_email(cls, v):
        import re
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', v):
            raise ValueError('Invalid email format')
        return v

class SessionRequest(BaseModel):
    user_id: str = Field(..., min_length=36, max_length=36)  # UUID format
    access_token: str = Field(..., min_length=10, max_length=2048)
    workout_date: str

class AddSetRequest(BaseModel):
    session_id: int = Field(..., gt=0)
    exercise_name: str = Field(..., min_length=1, max_length=100)
    reps: int = Field(..., gt=0, le=1000)
    weight: int = Field(..., gt=0, le=10000)
    is_kg: bool
    user_id: str = Field(..., min_length=36, max_length=36)
    access_token: str = Field(..., min_length=10, max_length=2048)

class RenameSessionRequest(BaseModel):
    session_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=100)
    user_id: str = Field(..., min_length=36, max_length=36)
    access_token: str = Field(..., min_length=10, max_length=2048)

class DuplicateSetRequest(BaseModel):
    set_id: int = Field(..., gt=0)
    user_id: str = Field(..., min_length=36, max_length=36)
    access_token: str = Field(..., min_length=10, max_length=2048)

class EditSetRequest(BaseModel):
    set_id: int = Field(..., gt=0)
    reps: int = Field(..., gt=0, le=1000)
    weight: int = Field(..., gt=0, le=10000)
    user_id: str = Field(..., min_length=36, max_length=36)
    access_token: str = Field(..., min_length=10, max_length=2048)

class RemoveSetRequest(BaseModel):
    set_id: int = Field(..., gt=0)
    user_id: str = Field(..., min_length=36, max_length=36)
    access_token: str = Field(..., min_length=10, max_length=2048)

# Auth endpoints
@app.post("/api/login")
async def login(request: LoginRequest):
    return login_user(request.email, request.password)

@app.post("/api/signup")
async def signup(request: SignupRequest):
    return signup_user(request.email, request.password)

@app.post("/api/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    return reset_password(request.email)

# Exercise endpoints
@app.get("/api/exercise-suggestions")
async def exercise_suggestions(query: str, limit: int = 10):
    # Input validation
    if len(query) < 1 or len(query) > 100:
        raise HTTPException(status_code=400, detail="Query must be between 1 and 100 characters")
    if limit < 1 or limit > 50:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 50")
    return get_exercise_suggestions(query, limit)

# Workout endpoints
@app.post("/api/create-session")
async def create_session(request: SessionRequest):
    return create_workout_session(request.user_id, request.access_token, request.workout_date)

@app.get("/api/sessions-by-date")
async def sessions_by_date(user_id: str, access_token: str, date: str):
    return get_sessions_by_date(user_id, access_token, date)

@app.post("/api/add-set")
async def add_set(request: AddSetRequest):
    return add_set_to_session(request.session_id, request.exercise_name, request.reps, 
                             request.weight, request.is_kg, request.user_id, request.access_token)

@app.get("/api/current-session")
async def current_session(user_id: str, access_token: str):
    return get_current_session(user_id, access_token)

@app.post("/api/rename-session")
async def rename_session(request: RenameSessionRequest):
    return rename_workout_session(request.session_id, request.name, request.user_id, request.access_token)

@app.get("/api/all-sessions")
async def all_sessions(user_id: str, access_token: str):
    return get_all_sessions(user_id, access_token)

@app.post("/api/duplicate-set")
async def duplicate_set_endpoint(request: DuplicateSetRequest):
    return duplicate_set(request.set_id, request.user_id, request.access_token)

@app.post("/api/edit-set")
async def edit_set_endpoint(request: EditSetRequest):
    return edit_set(request.set_id, request.reps, request.weight, request.user_id, request.access_token)

@app.post("/api/remove-set")
async def remove_set_endpoint(request: RemoveSetRequest):
    return remove_set(request.set_id, request.user_id, request.access_token)

@app.get("/api/session-sets")
async def session_sets(session_id: int, user_id: str, access_token: str):
    return get_session_sets(session_id, user_id, access_token)

# Custom exception handler to prevent information leakage
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    if ENVIRONMENT == "development":
        # Show detailed errors in development
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(exc)}")
    else:
        # Hide detailed errors in production
        raise HTTPException(status_code=500, detail="Internal server error")

# Serve React app for all other routes (SPA routing) - must be last!
@app.get("/{path:path}")
async def serve_react(path: str):
    # This should only catch non-API routes for SPA routing
    if os.path.exists("dist/index.html"):
        return FileResponse("dist/index.html")
    else:
        return FileResponse("static/index.html")
