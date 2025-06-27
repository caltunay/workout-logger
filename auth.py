from fastapi import HTTPException
from config import supabase

def login_user(email: str, password: str):
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if response.user and response.session:
            return {
                "success": True,
                "access_token": response.session.access_token,
                "user_id": response.user.id
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Login failed: {str(e)}")

def signup_user(email: str, password: str):
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user:
            return {"success": True, "message": "Check email for verification"}
        else:
            raise HTTPException(status_code=400, detail="Signup failed")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Signup failed: {str(e)}")

def reset_password(email: str):
    try:
        supabase.auth.reset_password_email(email)
        return {"success": True, "message": "Password reset email sent"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Password reset failed: {str(e)}")
