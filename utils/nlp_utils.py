import re
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob

# Predefined Dictionaries for skills
TECHNICAL_SKILLS = [
    "python", "sql", "pandas", "ml", "machine learning", "java", "c++", "c#", 
    "docker", "kubernetes", "aws", "azure", "fastapi", "django", "flask",
    "react", "angular", "vue", "javascript", "typescript", "git", "nlp", "ai",
    "deep learning", "tensorflow", "pytorch", "scikit-learn", "data science",
    "api", "linux", "cloud", "agile", "scrum", "REST", "graphql", "nosql", "mongodb",
    "php", "quality assurance", "data engineering", "business", "analytics", "mern",
    "dataenineering", "bussiness"
]

SOFT_SKILLS = [
    "communication", "leadership", "teamwork", "problem solving", "critical thinking",
    "adaptability", "time management", "conflict resolution", "creativity",
    "collaboration", "empathy", "work ethic", "attention to detail"
]

def clean_text(text: str) -> str:
    """Simple text cleaning using regex."""
    if not text:
        return ""
    # Lowercase
    text = text.lower()
    # Remove punctuation
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    # Basic tokenization and removal of extra spaces
    tokens = text.split()
    return ' '.join(tokens)

def compute_similarity(text1: str, text2: str) -> float:
    """Computes cosine similarity between two texts using TF-IDF."""
    if not text1.strip() or not text2.strip():
        return 0.0
    text1_clean = clean_text(text1)
    text2_clean = clean_text(text2)
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([text1_clean, text2_clean])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        # Return percentage (0 to 100)
        return float(similarity) * 100
    except Exception:
        return 0.0

def extract_skills(text: str) -> Tuple[List[str], List[str]]:
    """Extracts technical and soft skills by keyword matching."""
    text_clean = clean_text(text)
    
    found_tech = []
    for skill in TECHNICAL_SKILLS:
        # Ensure we match whole words using regex word boundaries
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_clean):
            found_tech.append(skill)
            
    found_soft = []
    for skill in SOFT_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_clean):
            found_soft.append(skill)
            
    return list(set(found_tech)), list(set(found_soft))

def analyze_sentiment(text: str) -> Tuple[str, float]:
    """Analyzes sentiment using TextBlob with safety fallback."""
    if not text or len(text.strip()) < 5:
        return "Neutral", 0.0
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        if polarity > 0.1:
            sentiment = "Positive"
        elif polarity < -0.1:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
        return sentiment, polarity
    except Exception as e:
        print(f"Sentiment Analysis Error: {e}")
        return "Neutral", 0.0

def calculate_keyword_density_score(text: str, keywords: List[str]) -> float:
    """Approximates a resume score based on density of matching keywords."""
    text_clean = clean_text(text)
    if not text_clean or not keywords:
        return 0.0
    count = 0
    for kw in keywords:
        if kw in text_clean:
            count += 1
    # Let's say max expected keywords to get 100% is dynamically based on provided keywords
    max_expected = max(1, len(keywords) * 0.5) # If they have 50% of the keywords, they get max score
    score = (count / max_expected) * 100
    return min(100.0, score)
