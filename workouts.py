from fastapi import HTTPException
from config import supabase, ENABLE_TEST_MODE, TEST_USER_ID, TEST_ACCESS_TOKEN
from datetime import datetime, timedelta

def authenticate_user(user_id: str, access_token: str):
    """Authenticate user, with test mode bypass"""
    if ENABLE_TEST_MODE and user_id == TEST_USER_ID and access_token == TEST_ACCESS_TOKEN:
        return  # Skip authentication for test mode (development only)
    supabase.auth.set_session(access_token, "")

def create_workout_session(user_id: str, access_token: str, workout_date: str):
    try:
        # Test mode - return mock data
        if ENABLE_TEST_MODE and user_id == TEST_USER_ID and access_token == TEST_ACCESS_TOKEN:
            # Parse the date and convert to ISO format for consistency
            workout_datetime = datetime.fromisoformat(workout_date.replace('Z', '+00:00'))
            session_name = f"Workout {workout_datetime.strftime('%b %d, %Y at %I:%M %p')}"
            
            mock_session = {
                "id": 9999,  # Use a high ID to avoid conflicts
                "user_id": user_id,
                "name": session_name,
                "created_at": workout_datetime.isoformat(),
                "set_count": 0
            }
            return {"success": True, "data": mock_session}
        
        authenticate_user(user_id, access_token)
        
        # Parse the date and convert to ISO format for Supabase
        workout_datetime = datetime.fromisoformat(workout_date.replace('Z', '+00:00'))
        
        # Create a default name based on the date and time
        session_name = f"Workout {workout_datetime.strftime('%b %d, %Y at %I:%M %p')}"
        
        result = supabase.table("workout_sessions").insert({
            "user_id": user_id,
            "name": session_name,
            "created_at": workout_datetime.isoformat()
        }).execute()
        
        if result.data:
            session_data = result.data[0]
            session_data["set_count"] = 0  # New session has no sets
            return {"success": True, "data": session_data}
        else:
            raise HTTPException(status_code=400, detail="Failed to create session")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to create session")

def add_set_to_session(session_id: int, exercise_name: str, reps: int, weight: int, is_kg: bool, user_id: str, access_token: str):
    try:
        # Test mode - return mock data
        if user_id == "123e4567-e89b-12d3-a456-426614174000" and access_token == "test-token-456":
            mock_set = {
                "id": 99990 + session_id,  # Use a unique ID
                "session_id": session_id,
                "exercise_id": exercise_name,
                "exercise_name": exercise_name,
                "reps": reps,
                "weight": weight,
                "is_kg": is_kg,
                "user_id": user_id,
                "created_at": datetime.now().isoformat()
            }
            return {"success": True, "data": mock_set}
            
        authenticate_user(user_id, access_token)
        
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
        # Test mode - return mock data
        if user_id == "123e4567-e89b-12d3-a456-426614174000" and access_token == "test-token-456":
            return {"success": True, "session": None, "sets": []}
            
        authenticate_user(user_id, access_token)
        
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
        # Test mode - return mock data
        if user_id == "123e4567-e89b-12d3-a456-426614174000" and access_token == "test-token-456":
            return {"success": True, "data": []}
            
        authenticate_user(user_id, access_token)
        
        # Parse date and create date range for the day
        target_date = datetime.fromisoformat(date.replace('Z', '+00:00')).date()
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())
        
        result = supabase.table("workout_sessions").select("*").eq("user_id", user_id).gte("created_at", start_of_day.isoformat()).lte("created_at", end_of_day.isoformat()).order("created_at", desc=True).execute()
        
        if not result.data:
            return {"success": True, "data": []}
        
        # Enrich sessions with set counts
        enriched_sessions = []
        for session in result.data:
            try:
                sets_result = supabase.table("session_sets").select("id").eq("session_id", session["id"]).execute()
                set_count = len(sets_result.data) if sets_result.data else 0
                enriched_sessions.append({**session, "set_count": set_count})
            except Exception:
                # If there's an error getting set count, just set it to 0
                enriched_sessions.append({**session, "set_count": 0})
        
        return {"success": True, "data": enriched_sessions}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get sessions: {str(e)}")

def rename_workout_session(session_id: int, name: str, user_id: str, access_token: str):
    try:
        authenticate_user(user_id, access_token)
        
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
        authenticate_user(user_id, access_token)
        
        result = supabase.table("workout_sessions").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        
        if not result.data:
            return {"success": True, "data": []}
        
        # Enrich sessions with set counts
        enriched_sessions = []
        for session in result.data:
            try:
                sets_result = supabase.table("session_sets").select("id").eq("session_id", session["id"]).execute()
                set_count = len(sets_result.data) if sets_result.data else 0
                enriched_sessions.append({**session, "set_count": set_count})
            except Exception:
                # If there's an error getting set count, just set it to 0
                enriched_sessions.append({**session, "set_count": 0})
        
        return {"success": True, "data": enriched_sessions}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get sessions: {str(e)}")

def duplicate_set(set_id: int, user_id: str, access_token: str):
    try:
        authenticate_user(user_id, access_token)
        
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
        authenticate_user(user_id, access_token)
        
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
        authenticate_user(user_id, access_token)
        
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

def get_session_sets(session_id: int, user_id: str, access_token: str):
    try:
        # Test mode - return mock data
        if ENABLE_TEST_MODE and user_id == TEST_USER_ID and access_token == TEST_ACCESS_TOKEN:
            return {"success": True, "data": []}
            
        authenticate_user(user_id, access_token)
        
        # Get the session details
        session_result = supabase.table("workout_sessions").select("*").eq("id", session_id).eq("user_id", user_id).execute()
        
        if not session_result.data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = session_result.data[0]
        
        # Get sets for this session
        sets_result = supabase.table("session_sets").select("*").eq("session_id", session_id).order("created_at").execute()
        
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
        
        return {"success": True, "data": enriched_sets}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get session sets: {str(e)}")
