from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from config import supabase

def get_exercise_suggestions(query: str):
    try:
        exercises_result = supabase.table("dim_exercises").select("exercise").execute()
        
        if not exercises_result.data:
            return {"success": True, "suggestions": []}
        
        exercise_names = [ex["exercise"] for ex in exercises_result.data]
        
        if len(query.strip()) < 2:
            return {"success": True, "suggestions": [{"exercise": name} for name in exercise_names[:5]]}
        
        try:
            query_lower = query.lower()
            exercise_texts = [name.lower() for name in exercise_names]
            
            char_vectorizer = TfidfVectorizer(ngram_range=(2, 4), analyzer='char', max_features=500)
            char_tfidf_matrix = char_vectorizer.fit_transform(exercise_texts)
            char_query_vector = char_vectorizer.transform([query_lower])
            char_similarities = cosine_similarity(char_query_vector, char_tfidf_matrix).flatten()
            
            word_vectorizer = TfidfVectorizer(ngram_range=(1, 2), analyzer='word', max_features=500)
            word_tfidf_matrix = word_vectorizer.fit_transform(exercise_texts)
            word_query_vector = word_vectorizer.transform([query_lower])
            word_similarities = cosine_similarity(word_query_vector, word_tfidf_matrix).flatten()
            
            combined_similarities = 0.6 * char_similarities + 0.4 * word_similarities
            similar_indices = combined_similarities.argsort()[::-1]
            
            suggestions = []
            for idx in similar_indices:
                if combined_similarities[idx] > 0 and len(suggestions) < 5:
                    suggestions.append({"exercise": exercise_names[idx]})
            
            if not suggestions:
                for name in exercise_names:
                    if query_lower in name.lower() and len(suggestions) < 5:
                        suggestions.append({"exercise": name})
            
            return {"success": True, "suggestions": suggestions}
            
        except Exception:
            query_lower = query.lower()
            suggestions = []
            for name in exercise_names:
                if query_lower in name.lower() and len(suggestions) < 5:
                    suggestions.append({"exercise": name})
            return {"success": True, "suggestions": suggestions}
            
    except Exception as e:
        return {"success": False, "error": str(e)}
