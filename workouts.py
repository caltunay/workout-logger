from fastapi import HTTPException
from config import supabase

def start_workout_session(user_id: str, access_token: str):
    try:
        supabase.auth.set_session(access_token, "")
        result = supabase.table("workout_sessions").insert({"user_id": user_id}).execute()
        
        if result.data:
            return {"success": True, "session_id": result.data[0]["id"]}
        else:
            raise HTTPException(status_code=400, detail="Failed to start session")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to start session: {str(e)}")

def add_set_to_session(session_id: int, exercise_name: str, reps: int, weight: int, is_kg: bool, user_id: str, access_token: str):
    try:
        supabase.auth.set_session(access_token, "")
        
        exercise_result = supabase.table("dim_exercises").select("id").eq("exercise", exercise_name).execute()
        exercise_id = exercise_result.data[0]["id"] if exercise_result.data else exercise_name
        
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

def get_current_session(user_id: str, access_token: str):
    try:
        supabase.auth.set_session(access_token, "")
        
        result = supabase.table("workout_sessions").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()
        
        if result.data:
            session = result.data[0]
            sets_result = supabase.table("session_sets").select("*").eq("session_id", session["id"]).order("created_at").execute()
            
            enriched_sets = []
            for set_data in sets_result.data:
                exercise_name = set_data["exercise_id"]
                try:
                    exercise_result = supabase.table("dim_exercises").select("exercise").eq("id", set_data["exercise_id"]).execute()
                    if exercise_result.data:
                        exercise_name = exercise_result.data[0]["exercise"]
                except:
                    pass
                
                enriched_sets.append({**set_data, "exercise_name": exercise_name})
            
            return {"success": True, "session": session, "sets": enriched_sets}
        else:
            return {"success": True, "session": None, "sets": []}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get session: {str(e)}")

def end_workout_session(session_id: int, user_id: str, access_token: str):
    try:
        supabase.auth.set_session(access_token, "")
        result = supabase.table("workout_sessions").select("id").eq("id", session_id).eq("user_id", user_id).execute()
        
        if result.data:
            return {"success": True, "message": "Session ended"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to end session: {str(e)}")
