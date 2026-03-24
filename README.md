---
title: AI Hiring Evaluator
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# AI Hiring Evaluator (NLP Base)

This is a FastAPI-based AI Hiring Evaluator that uses traditional NLP techniques (TF-IDF, Cosine Similarity, etc.) to evaluate candidates based on their resumes, transcripts, and job descriptions.

## Features
- Strict 4-field input evaluation (`/generate-report`)
- Traditional NLP (No LLMs needed)
- Robust JSON sanitization middleware
- Automated scoring and recommendation logic

## Local Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Download textblob corpora: `python -m textblob.download_corpora`
4. Run the server: `python main.py` or `uvicorn main:app --port 3000`
