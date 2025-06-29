from config import supabase
from typing import Dict

def get_exercise_suggestions(query: str, max_suggestions: int = 10) -> Dict:
    """Exercise search using PostgreSQL fuzzy search with fallback."""
    try:
        if len(query.strip()) < 2:
            result = supabase.table("dim_exercises").select("exercise").limit(max_suggestions).execute()
            return {"success": True, "data": [{"name": ex["exercise"]} for ex in result.data]}
        
        # Use the fuzzy PostgreSQL search function without threshold - return top matches
        result = supabase.rpc('search_exercises_fuzzy', {
            'search_term': query.strip(),
            'similarity_threshold': 0.0,  # No threshold - return all matches ranked by similarity
            'max_results': max_suggestions
        }).execute()
        
        if result.data:
            suggestions = []
            for ex in result.data:
                suggestion = {"name": ex["exercise"]}
                # Add similarity score from fuzzy search
                if ex.get("similarity"):
                    suggestion["similarity"] = ex["similarity"]
                suggestions.append(suggestion)
            
            return {"success": True, "data": suggestions}
        
        # Fallback to simple ILIKE search if the RPC function doesn't exist
        return _fallback_search(query.strip(), max_suggestions)
        
    except Exception as e:
        # If PostgreSQL function fails, fallback to simple search
        return _fallback_search(query.strip(), max_suggestions)

def _fallback_search(query: str, max_suggestions: int) -> Dict:
    """Fallback search using simple ILIKE pattern matching."""
    try:
        query_lower = query.lower()
        result = supabase.table("dim_exercises").select("exercise").ilike("exercise", f"%{query_lower}%").limit(max_suggestions).execute()
        
        return {"success": True, "data": [{"name": ex["exercise"]} for ex in result.data]}
        
    except Exception as e:
        return {"success": False, "error": str(e)}
