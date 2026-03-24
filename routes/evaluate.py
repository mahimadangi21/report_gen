from fastapi import APIRouter, HTTPException
from models.schemas import GenerateReportRequest, EvaluationResponse
from services.evaluator import evaluate_candidate_nlp
import traceback

router = APIRouter()

@router.post("/generate-report", response_model=EvaluationResponse, description="Generates a hiring evaluation report using 4 core inputs: Job Description, Transcript, Resume Score, and Coding Score.")
def generate_report(req: GenerateReportRequest):
    try:
        report = evaluate_candidate_nlp(req)
        return EvaluationResponse(success=True, report=report)
    except Exception as e:
        print(f"Error during NLP evaluation: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to evaluate candidate", "details": str(e)}
        )
