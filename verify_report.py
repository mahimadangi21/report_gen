from models.schemas import GenerateReportRequest
from services.evaluator import evaluate_candidate_nlp
import json

def run_evaluation():
    # Create a request with the newly added skills
    # Skills provided by user: php, quality assurance, dataenineering, bussiness, analytics, mern, python
    # Note: dataenineering and bussiness are misspelled in the prompt, so I included them in the list.
    
    req = GenerateReportRequest(
        job_description="Looking for an expert in PHP, Quality Assurance, Data Engineering, Business Analytics, MERN stack, and Python.",
        transcript="I am proficient in PHP and Quality Assurance. My background includes dataenineering and bussiness analytics. I also build apps using the MERN stack and Python.",
        resume_score=85.0,
        coding_score=92.0
    )
    
    # Run the evaluation logic
    report = evaluate_candidate_nlp(req)
    
    # Output the result
    print("--- AI Hiring Evaluation Report ---")
    print(json.dumps(report.model_dump(), indent=2))

if __name__ == "__main__":
    run_evaluation()
