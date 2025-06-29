from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from auth import login_user, signup_user, reset_password
from exercises import get_exercise_suggestions
from workouts import create_workout_session, add_set_to_session, get_current_session, get_sessions_by_date, rename_workout_session, get_all_sessions, duplicate_set, edit_set, remove_set, get_session_sets

app = FastAPI(title="Workout Tracker", version="1.0.0")

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

# Request models
class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    email: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: str

class SessionRequest(BaseModel):
    user_id: str
    access_token: str
    workout_date: str

class AddSetRequest(BaseModel):
    session_id: int
    exercise_name: str
    reps: int
    weight: int
    is_kg: bool
    user_id: str
    access_token: str

class RenameSessionRequest(BaseModel):
    session_id: int
    name: str
    user_id: str
    access_token: str

class DuplicateSetRequest(BaseModel):
    set_id: int
    user_id: str
    access_token: str

class EditSetRequest(BaseModel):
    set_id: int
    reps: int
    weight: int
    user_id: str
    access_token: str

class RemoveSetRequest(BaseModel):
    set_id: int
    user_id: str
    access_token: str

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

# Test endpoint to verify database schema
@app.get("/api/test-schema")
async def test_schema(user_id: str, access_token: str):
    try:
        from config import supabase
        supabase.auth.set_session(access_token, "")
        result = supabase.table("workout_sessions").select("id, name, created_at").eq("user_id", user_id).limit(1).execute()
        return {"success": True, "test_data": result.data}
    except Exception as e:
        return {"success": False, "error": str(e)}
