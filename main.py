from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from auth import login_user, signup_user, reset_password
from exercises import get_exercise_suggestions
from workouts import start_workout_session, add_set_to_session, get_current_session, end_workout_session

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Root route serves the frontend
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

class AddSetRequest(BaseModel):
    session_id: int
    exercise_name: str
    reps: int
    weight: int
    is_kg: bool
    user_id: str
    access_token: str

class EndSessionRequest(BaseModel):
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
async def exercise_suggestions(query: str):
    return get_exercise_suggestions(query)

# Workout endpoints
@app.post("/api/start-session")
async def start_session(request: SessionRequest):
    return start_workout_session(request.user_id, request.access_token)

@app.post("/api/add-set")
async def add_set(request: AddSetRequest):
    return add_set_to_session(request.session_id, request.exercise_name, request.reps, request.weight, request.is_kg, request.user_id, request.access_token)

@app.get("/api/current-session")
async def current_session(user_id: str, access_token: str):
    return get_current_session(user_id, access_token)

@app.post("/api/end-session/{session_id}")
async def end_session(session_id: int, request: EndSessionRequest):
    return end_workout_session(session_id, request.user_id, request.access_token)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
