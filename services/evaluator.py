
from models.schemas import (
    ReportModel, ScoresModels, AnalysisModel, 
    RecommendationModel, InsightsModel, EvaluationResponse
)
from utils.nlp_utils import (
    compute_similarity, extract_skills, analyze_sentiment, calculate_keyword_density_score
)

# Hardcoded Job Description as per user request to move from input
DEFAULT_JD = """
Looking for a candidate with strong proficiency in Python and Data Engineering (Hadoop, Apache Spark, Databricks). 
Should have experience with ETL/ELT pipelines, SQL, and Data Warehousing (Star/Snowflake schemas). 
Knowledge of MERN stack, PHP, or Cloud (AWS/Azure) is a plus. 
Good problem-solving and communication skills are required.
"""

def evaluate_candidate_nlp(request_data) -> ReportModel:
    # Handle the new 4-field schema by providing defaults for missing info
    # Fields no longer in the request body
    candidate_name = "Anonymous Candidate"
    role = "Software Developer"
    resume_text = getattr(request_data, "resume_text", "")
    
    # 1. Similarity & Match Scores
    # Use hardcoded DEFAULT_JD instead of request body input
    text_to_match = resume_text if resume_text else request_data.transcript
    jd_match_score = compute_similarity(text_to_match, DEFAULT_JD)
    transcript_jd_match = compute_similarity(request_data.transcript, DEFAULT_JD)
    
    # Blend JD match score (Resume vs JD heavily weighted, Transcript vs JD is bonus context)
    final_jd_match_score = (jd_match_score * 0.7) + (transcript_jd_match * 0.3)
    
    # 2. Extract Skills from JD and text
    jd_tech, jd_soft = extract_skills(DEFAULT_JD)
    resume_tech, resume_soft = extract_skills(resume_text)
    transcript_tech, transcript_soft = extract_skills(request_data.transcript)
    
    # Combine skills found from candidate
    all_candidate_tech = list(set(resume_tech + transcript_tech))
    all_candidate_soft = list(set(resume_soft + transcript_soft))
    
    # Determine Missing Skills based on JD
    missing_tech = [s for s in jd_tech if s not in all_candidate_tech]
    missing_soft = [s for s in jd_soft if s not in all_candidate_soft]
    missing_skills = missing_tech + missing_soft
    
    # Skill Match Percentage
    total_jd_skills = len(jd_tech) + len(jd_soft)
    if total_jd_skills > 0:
        matched_skills_count = len([s for s in jd_tech if s in all_candidate_tech]) + \
                               len([s for s in jd_soft if s in all_candidate_soft])
        skill_match_percentage = (matched_skills_count / total_jd_skills) * 100
    else:
        # If no JD skills defined, match against all technical skills as a generic benchmark
        from utils.nlp_utils import TECHNICAL_SKILLS
        matched_count = len([s for s in TECHNICAL_SKILLS if s in all_candidate_tech])
        skill_match_percentage = min(100.0, (matched_count / 10.0) * 100) # Benchmark against 10 skills
    
    # 3. Handle Resume Score
    resume_score = request_data.resume_score
    if resume_score is None:
        resume_score = calculate_keyword_density_score(text_to_match, jd_tech + jd_soft)
    
    # 4. Handle Interview Score (Estimate from transcript if missing)
    coding_score = request_data.coding_score
    mcq_score = request_data.mcq_score
    interview_score = getattr(request_data, "interview_score", None)
    
    if interview_score is None or interview_score == 0:
        # Estimate interview score
        from utils.nlp_utils import TECHNICAL_SKILLS
        tech_density = calculate_keyword_density_score(request_data.transcript, TECHNICAL_SKILLS)
        _, polarity = analyze_sentiment(request_data.transcript)
        # Sentiment weight (0.3) + Technical depth (0.7)
        interview_score = (tech_density * 0.7) + ((polarity + 1) * 50 * 0.3)
        interview_score = min(100.0, max(0.0, interview_score))

    # Calculate final score with 4 components (25% weight each)
    final_score = (resume_score * 0.25) + (coding_score * 0.25) + (mcq_score * 0.25) + (interview_score * 0.25)
    
    # 5. Sentiment Analysis on Transcript
    sentiment, polarity = analyze_sentiment(request_data.transcript)
    
    # 6. Recommendation Logic
    if final_score > 85:
        decision = "Strong Hire"
    elif final_score >= 70:
        decision = "Hire"
    elif final_score >= 50:
        decision = "Weak Hire"
    else:
        decision = "Reject"
        
    # Risk Level
    risk_level = "Low"
    if len(missing_skills) > max(3, total_jd_skills * 0.5):
        risk_level = "High"
    elif sentiment == "Negative":
        risk_level = "Medium"
    
    # Confidence Level
    scores_list = [resume_score, final_jd_match_score, coding_score]
    if getattr(request_data, "interview_score", None) is not None:
        scores_list.append(interview_score)
        
    min_score = min(scores_list)
    max_score = max(scores_list)
    score_diff = max_score - min_score
    
    if min_score < 40:
        confidence_level = "Low"
    elif score_diff > 30:
        confidence_level = "Medium"
    else:
        confidence_level = "High"
        
    # Strengths & Weaknesses
    strengths = []
    if coding_score > 85: strengths.append("Strong coding fundamentals")
    if skill_match_percentage > 80: strengths.append("Excellent skill match with job description")
    if getattr(request_data, "interview_score", 0) > 80: strengths.append("Performed well in interview")
    if sentiment == "Positive": strengths.append("Positive communication style")
    
    weaknesses = []
    if missing_skills: weaknesses.append(f"Missing required skills: {', '.join(missing_skills[:3])}")
    if final_jd_match_score < 50: weaknesses.append("Resume shows low relevance to job description")
    if coding_score < 50: weaknesses.append("Poor coding performance")
    if sentiment == "Negative": weaknesses.append("Negative sentiment detected in communication")
    
    # Recommendations/Insights
    candidate_summary = f"{candidate_name} is a {'strong' if final_score > 70 else 'potential'} candidate for the {role} position with a final score of {final_score:.1f}."
    improvement_suggestions = []
    if missing_skills:
        improvement_suggestions.append(f"Needs to acquire missing technical/soft skills: {', '.join(missing_skills[:3])}")
    if getattr(request_data, "interview_score", 100) < 70:
        improvement_suggestions.append("Needs to focus on interview performance and communication clearly.")
    
    reason = f"Decision '{decision}' made based on overall score of {final_score:.1f} and skill match of {skill_match_percentage:.1f}%."

    # Build Response using Pydantic Models
    report = ReportModel(
        role=role,
        scores=ScoresModels(
            resume_score=round(resume_score, 2),
            coding_score=round(coding_score, 2),
            mcq_score=round(mcq_score, 2),
            interview_score=round(interview_score, 2),
            final_score=round(final_score, 2)
        ),
        analysis=AnalysisModel(
            sentiment=sentiment,
            confidence_level=confidence_level,
            strengths=strengths,
            weaknesses=weaknesses,
            skill_match_percentage=round(skill_match_percentage, 2)
        ),
        recommendation=RecommendationModel(
            decision=decision,
            reason=reason,
            risk_level=risk_level
        ),
        insights=InsightsModel(
            candidate_summary=candidate_summary,
            improvement_suggestions=improvement_suggestions
        )
    )
    
    return report
