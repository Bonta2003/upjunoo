# backend/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from datetime import datetime
import os

app = FastAPI()

# Autoriser le frontend à accéder à l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En développement, autorise tout
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# 1. CONNEXION À MONGODB
# ============================================
# Remplace par ta vraie chaîne de connexion
MONGO_URI = "mongodb+srv://manuelleidrisse12_db_user:datamaster1234@projet0.trncdaw.mongodb.net/?appName=Projet0"

client = MongoClient(MONGO_URI)
db = client["upjunoo_veille"]
collection = db["tweets"]

# ============================================
# 2. ENDPOINT POUR LE TABLEAU DE BORD
# ============================================
@app.get("/api/dashboard")
async def get_dashboard():
    """Renvoie toutes les données pour le tableau de bord"""
    
    # Récupérer les 20 derniers tweets
    tweets_cursor = collection.find().sort("created_at", -1).limit(20)
    tweets = []
    
    for t in tweets_cursor:
        tweets.append({
            "id": str(t.get("tweet_id", t.get("_id"))),
            "text": t.get("text", ""),
            "author": t.get("author", {}).get("username", "inconnu"),
            "created_at": t.get("created_at"),
            "metrics": {
                "likes": t.get("metrics", {}).get("likes", 0),
                "views": t.get("metrics", {}).get("views", 0),
                "retweets": t.get("metrics", {}).get("retweets", 0)
            },
            "is_suggestion": t.get("is_suggestion", False),
            "suggestion_text": t.get("suggestion_text"),
            "sentiment": t.get("sentiment", "neutral")
        })
    
    # Statistiques globales
    all_tweets = list(collection.find())
    total = len(all_tweets)
    suggestions = len([t for t in all_tweets if t.get("is_suggestion")])
    likes = sum(t.get("metrics", {}).get("likes", 0) for t in all_tweets)
    views = sum(t.get("metrics", {}).get("views", 0) for t in all_tweets)
    
    # Compter les sentiments (si tu as ce champ)
    positive = len([t for t in all_tweets if t.get("sentiment") == "positive"])
    negative = len([t for t in all_tweets if t.get("sentiment") == "negative"])
    neutral = len([t for t in all_tweets if t.get("sentiment") == "neutral"])
    
    # Suggestions populaires
    suggestion_counts = {}
    for t in all_tweets:
        if t.get("is_suggestion") and t.get("suggestion_text"):
            key = t["suggestion_text"]
            suggestion_counts[key] = suggestion_counts.get(key, 0) + 1
    
    top_suggestions = sorted(
        [{"text": k, "count": v} for k, v in suggestion_counts.items()],
        key=lambda x: x["count"],
        reverse=True
    )[:5]
    
    return {
        "tweets": tweets,
        "total": total,
        "suggestions": suggestions,
        "likes": likes,
        "views": views,
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "topSuggestions": top_suggestions
    }

# ============================================
# 3. LANCER LE SERVEUR
# ============================================
if __name__ == "__main__":
    import uvicorn
    print("🚀 Serveur démarré sur http://localhost:8000")
    print("📊 Dashboard disponible sur http://localhost:8000/api/dashboard")
    uvicorn.run(app, host="0.0.0.0", port=8000)