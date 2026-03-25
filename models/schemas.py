from pydantic import BaseModel, Field
from typing import List, Optional

class GenerateReportRequest(BaseModel):
    transcript: str
    resume_score: float
    coding_score: float
    mcq_score: float
    interview_score: Optional[float] = 0.0

class ScoresModels(BaseModel):
    resume_score: float
    coding_score: float
    mcq_score: float
    interview_score: float
    final_score: float

class AnalysisModel(BaseModel):
    sentiment: str
    confidence_level: str
    strengths: List[str]
    weaknesses: List[str]
    skill_match_percentage: float

class RecommendationModel(BaseModel):
    decision: str
    reason: str
    risk_level: str

class InsightsModel(BaseModel):
    candidate_summary: str
    improvement_suggestions: List[str]

class ReportModel(BaseModel):
    role: str
    scores: ScoresModels
    analysis: AnalysisModel
    recommendation: RecommendationModel
    insights: InsightsModel

class EvaluationResponse(BaseModel):
    success: bool
    report: ReportModel
