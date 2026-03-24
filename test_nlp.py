from models.schemas import EvaluationRequest
from services.evaluator import evaluate_candidate_nlp
import json

def test():
    req = EvaluationRequest(
        candidate_name="Jane Doe",
        role="Data Scientist",
        resume_text="Experienced Data Scientist with 5 years in Python, pandas, and scikit-learn. Built machine learning models for natural language processing.",
        job_description="Looking for a Data Scientist skilled in Python, Machine Learning, NLP, and SQL.",
        transcript="I have extensive experience with Python and machine learning. In my last role, I used NLP to analyze customer sentiment. I love teamwork and solving complex problems.",
        resume_score=None,
        coding_score=88.5,
        interview_score=92.0
    )
    
    report = evaluate_candidate_nlp(req)
    print(report.model_dump_json(indent=2))

if __name__ == "__main__":
    test()
