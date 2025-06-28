from fastapi import HTTPException
from config import supabase
from datetime import datetime

def create_workout_session(user_id: str, access_token: str, workout_date: str):
    try:
        supabase.auth.set_session(access_token, "")
        
        # Parse the date and convert to ISO format for Supabase
        workout_datetime = datetime.fromisoformat(workout_date.replace('Z', '+00:00'))
        
        result = supabase.table("workout_sessions").insert({
            "user_id": user_id,
            "created_at": workout_datetime.isoformat()
        }).execute()
        
        if result.data:
            return {"success": True, "session_id": result.data[0]["id"]}
        else:
            raise HTTPException(status_code=400, detail="Failed to create session")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create session: {str(e)}")

def add_set_to_session(session_id: int, exercise_name: str, reps: int, weight: int, is_kg: bool, user_id: str, access_token: str):
    try:
        supabase.auth.set_session(access_token, "")
        
        # Get exercise ID, fallback to exercise name if not found
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
        
        # Get most recent session
        result = supabase.table("workout_sessions").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()
        
        if result.data:
            session = result.data[0]
            sets_result = supabase.table("session_sets").select("*").eq("session_id", session["id"]).order("created_at").execute()
            
            # Enrich sets with exercise names
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

def get_sessions_by_date(user_id: str, access_token: str, date: str):
    try:
        supabase.auth.set_session(access_token, "")
        
        # Parse date and create date range for the day
        target_date = datetime.fromisoformat(date.replace('Z', '+00:00')).date()
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())
        
        result = supabase.table("workout_sessions").select("*").eq("user_id", user_id).gte("created_at", start_of_day.isoformat()).lte("created_at", end_of_day.isoformat()).execute()
        
        return {"success": True, "sessions": result.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get sessions: {str(e)}")

def rename_workout_session(session_id: int, name: str, user_id: str, access_token: str):
    try:
        supabase.auth.set_session(access_token, "")
        
        # First check if the session exists
        check_result = supabase.table("workout_sessions").select("*").eq("id", session_id).eq("user_id", user_id).execute()
        if not check_result.data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        result = supabase.table("workout_sessions").update({
            "name": name
        }).eq("id", session_id).eq("user_id", user_id).execute()
        
        if result.data:
            return {"success": True, "data": result.data[0]}
        else:
            raise HTTPException(status_code=400, detail="Failed to rename session - no data returned")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Rename session error: {str(e)}")  # Debug logging
        raise HTTPException(status_code=400, detail=f"Failed to rename session: {str(e)}")

def get_all_sessions(user_id: str, access_token: str):
    try:
        supabase.auth.set_session(access_token, "")
        
        result = supabase.table("workout_sessions").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        
        # Enrich sessions with set counts
        enriched_sessions = []
        for session in result.data:
            sets_result = supabase.table("session_sets").select("id").eq("session_id", session["id"]).execute()
            set_count = len(sets_result.data)
            enriched_sessions.append({**session, "set_count": set_count})
        
        return {"success": True, "sessions": enriched_sessions}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get sessions: {str(e)}")

def duplicate_set(set_id: int, user_id: str, access_token: str):
    try:
        supabase.auth.set_session(access_token, "")
        
        # Get the original set
        original_set = supabase.table("session_sets").select("*").eq("id", set_id).eq("user_id", user_id).execute()
        if not original_set.data:
            raise HTTPException(status_code=404, detail="Set not found")
        
        set_data = original_set.data[0]
        
        # Create a new set with the same data
        new_set = supabase.table("session_sets").insert({
            "session_id": set_data["session_id"],
            "exercise_id": set_data["exercise_id"],
            "reps": set_data["reps"],
            "weight": set_data["weight"],
            "is_kg": set_data["is_kg"],
            "user_id": user_id
        }).execute()
        
        if new_set.data:
            return {"success": True, "data": new_set.data[0]}
        else:
            raise HTTPException(status_code=400, detail="Failed to duplicate set")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to duplicate set: {str(e)}")

def edit_set(set_id: int, reps: int, weight: int, user_id: str, access_token: str):
    try:
        supabase.auth.set_session(access_token, "")
        
        # Update the set
        result = supabase.table("session_sets").update({
            "reps": reps,
            "weight": weight
        }).eq("id", set_id).eq("user_id", user_id).execute()
        
        if result.data:
            return {"success": True, "data": result.data[0]}
        else:
            raise HTTPException(status_code=404, detail="Set not found or not authorized to edit")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to edit set: {str(e)}")

def remove_set(set_id: int, user_id: str, access_token: str):
    try:
        supabase.auth.set_session(access_token, "")
        
        # First, let's check if the set exists
        check_result = supabase.table("session_sets").select("*").eq("id", set_id).eq("user_id", user_id).execute()
        
        if not check_result.data:
            raise HTTPException(status_code=404, detail="Set not found or not authorized")
        
        # Delete the set
        result = supabase.table("session_sets").delete().eq("id", set_id).eq("user_id", user_id).execute()
        
        return {"success": True, "message": "Set removed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to remove set: {str(e)}")
