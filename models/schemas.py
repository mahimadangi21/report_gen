from pydantic import BaseModel, Field
from typing import List, Optional

class GenerateReportRequest(BaseModel):
    job_description: str
    transcript: str
    resume_score: float
    coding_score: float

class ScoresModels(BaseModel):
    resume_score: float
    jd_match_score: float
    coding_score: float
    interview_score: float
    final_score: float

class AnalysisModel(BaseModel):
    sentiment: str
    confidence_level: str
    strengths: List[str]
    weaknesses: List[str]
    skill_match_percentage: float

class SkillsModel(BaseModel):
    technical_skills: List[str]
    soft_skills: List[str]
    missing_skills: List[str]

class RecommendationModel(BaseModel):
    decision: str
    reason: str
    risk_level: str

class InsightsModel(BaseModel):
    candidate_summary: str
    improvement_suggestions: List[str]
    interviewer_notes: str

class ReportModel(BaseModel):
    candidate_name: str
    role: str
    scores: ScoresModels
    analysis: AnalysisModel
    skills: SkillsModel
    recommendation: RecommendationModel
    insights: InsightsModel

class EvaluationResponse(BaseModel):
    success: bool
    report: ReportModel
