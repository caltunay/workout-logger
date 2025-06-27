from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

app = FastAPI()

# Supabase configuration
supabase_url = os.getenv("SUPABASE_PROJECT_URL", "")
supabase_key = os.getenv("SUPABASE_ANON_PUBLIC_KEY", "")
supabase: Client = create_client(supabase_url, supabase_key)

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

@app.post("/login")
async def login(email: str = Form(...), password: str = Form(...)):
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if response.user and response.session:
            return {
                "success": True, 
                "message": "Login successful",
                "access_token": response.session.access_token,
                "user_id": response.user.id
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Login failed: {str(e)}")

@app.post("/signup")
async def signup(email: str = Form(...), password: str = Form(...)):
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user:
            return {"success": True, "message": "Signup successful. Check your email for verification."}
        else:
            raise HTTPException(status_code=400, detail="Signup failed")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Signup failed: {str(e)}")

@app.post("/forgot-password")
async def forgot_password(email: str = Form(...)):
    try:
        response = supabase.auth.reset_password_email(email)
        return {"success": True, "message": "Password reset email sent"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Password reset failed: {str(e)}")

# Exercise suggestion endpoint
@app.get("/api/exercise-suggestions")
async def get_exercise_suggestions(query: str):
    try:
        # Get all exercises from dim_exercises
        exercises_result = supabase.table("dim_exercises").select("exercise").execute()
        
        if not exercises_result.data or len(exercises_result.data) == 0:
            return {"success": True, "suggestions": []}
        
        # Extract exercise names
        exercise_names = [ex["exercise"] for ex in exercises_result.data]
        
        # If query is empty or too short, return first 5 exercises
        if len(query.strip()) < 2:
            return {"success": True, "suggestions": [{"exercise": name, "match": ""} for name in exercise_names[:5]]}
        
        try:
            # Use dual TF-IDF approach: character n-grams for partial matches + word similarity
            query_lower = query.lower()
            exercise_texts = [name.lower() for name in exercise_names]
            
            # Character-based TF-IDF for partial matching
            char_vectorizer = TfidfVectorizer(
                ngram_range=(2, 4),
                lowercase=True,
                analyzer='char',
                max_features=500
            )
            
            char_tfidf_matrix = char_vectorizer.fit_transform(exercise_texts)
            char_query_vector = char_vectorizer.transform([query_lower])
            char_similarities = cosine_similarity(char_query_vector, char_tfidf_matrix).flatten()
            
            # Word-based TF-IDF for word variations (curl vs curls)
            word_vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),
                lowercase=True,
                analyzer='word',
                max_features=500,
                token_pattern=r'\b\w+\b'
            )
            
            word_tfidf_matrix = word_vectorizer.fit_transform(exercise_texts)
            word_query_vector = word_vectorizer.transform([query_lower])
            word_similarities = cosine_similarity(word_query_vector, word_tfidf_matrix).flatten()
            
            # Combine both similarities with weights (60% character, 40% word)
            combined_similarities = 0.6 * char_similarities + 0.4 * word_similarities
            
            # Get indices sorted by similarity (descending)
            similar_indices = combined_similarities.argsort()[::-1]
            
            # Get top 5 suggestions with similarity > 0
            suggestions = []
            for idx in similar_indices:
                if combined_similarities[idx] > 0 and len(suggestions) < 5:
                    exercise_name = exercise_names[idx]
                    similarity_score = combined_similarities[idx]
                    suggestions.append({
                        "exercise": exercise_name,
                        "match": f"{int(similarity_score * 100)}%"
                    })
            
            # If no good matches, do simple substring matching
            if len(suggestions) == 0:
                for name in exercise_names:
                    if query_lower in name.lower() and len(suggestions) < 5:
                        suggestions.append({
                            "exercise": name,
                            "match": "partial match"
                        })
            
            return {"success": True, "suggestions": suggestions}
            
        except Exception as e:
            # Fallback to simple substring matching if TF-IDF fails
            query_lower = query.lower()
            suggestions = []
            for name in exercise_names:
                if query_lower in name.lower() and len(suggestions) < 5:
                    suggestions.append({
                        "exercise": name,
                        "match": "partial match"
                    })
            return {"success": True, "suggestions": suggestions}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

# Workout session endpoints
@app.post("/api/start-session")
async def start_workout_session(
    user_id: str = Form(...),
    access_token: str = Form(...)
):
    try:
        # Set the auth token for this request
        supabase.auth.set_session(access_token, "")
        
        result = supabase.table("workout_sessions").insert({
            "user_id": user_id
        }).execute()
        
        if result.data:
            return {"success": True, "session_id": result.data[0]["id"]}
        else:
            raise HTTPException(status_code=400, detail="Failed to start session")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to start session: {str(e)}")

@app.post("/api/add-set")
async def add_set_to_session(
    session_id: int = Form(...),
    exercise_name: str = Form(...),
    reps: int = Form(...),
    weight: int = Form(...),
    is_kg: bool = Form(False),
    user_id: str = Form(...),
    access_token: str = Form(...)
):
    try:
        # Set the auth token for this request
        supabase.auth.set_session(access_token, "")
        
        # Try to get exercise ID from dim_exercises table, or use exercise name as ID
        exercise_result = supabase.table("dim_exercises").select("id").eq("exercise", exercise_name).execute()
        
        if exercise_result.data:
            exercise_id = exercise_result.data[0]["id"]
        else:
            # Use exercise name as exercise_id since user can enter any exercise
            exercise_id = exercise_name
        
        # Add set to session_sets table
        result = supabase.table("session_sets").insert({
            "session_id": session_id,
            "exercise_id": exercise_id,
            "reps": reps,
            "weight": weight,
            "is_kg": is_kg,
            "user_id": user_id
        }).execute()
        
        if result.data:
            return {"success": True, "data": result.data[0]}
        else:
            raise HTTPException(status_code=400, detail="Failed to add set")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to add set: {str(e)}")

@app.get("/api/current-session")
async def get_current_session(
    user_id: str,
    access_token: str
):
    try:
        # Set the auth token for this request
        supabase.auth.set_session(access_token, "")
        
        # Get latest active session
        result = supabase.table("workout_sessions").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()
        
        if result.data:
            session = result.data[0]
            
            # Get sets for this session - handle both dim_exercises references and plain text
            sets_result = supabase.table("session_sets").select("*").eq("session_id", session["id"]).order("created_at").execute()
            
            # Enrich with exercise names
            enriched_sets = []
            for set_data in sets_result.data:
                # Try to get exercise name from dim_exercises
                exercise_name = set_data["exercise_id"]  # Default to the ID itself
                try:
                    exercise_result = supabase.table("dim_exercises").select("exercise").eq("id", set_data["exercise_id"]).execute()
                    if exercise_result.data:
                        exercise_name = exercise_result.data[0]["exercise"]
                except:
                    pass  # Use exercise_id as name if lookup fails
                
                enriched_sets.append({
                    **set_data,
                    "exercise_name": exercise_name
                })
            
            return {"success": True, "session": session, "sets": enriched_sets}
        else:
            return {"success": True, "session": None, "sets": []}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get session: {str(e)}")

@app.post("/api/end-session/{session_id}")
async def end_workout_session(
    session_id: int,
    user_id: str = Form(...),
    access_token: str = Form(...)
):
    try:
        # Set the auth token for this request
        supabase.auth.set_session(access_token, "")
        
        # Just acknowledge the session exists
        result = supabase.table("workout_sessions").select("id").eq("id", session_id).eq("user_id", user_id).execute()
        
        if result.data:
            return {"success": True, "message": "Session ended"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to end session: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
