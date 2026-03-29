import re
from models.schemas import (
    ReportModel, ScoresModels, AnalysisModel, 
    RecommendationModel, InsightsModel, EvaluationResponse
)
from utils.nlp_utils import (
    compute_similarity, extract_skills, analyze_sentiment, 
    calculate_keyword_density_score, DOMAIN_SKILLS
)

# Predefined role if not found in transcript
DEFAULT_ROLE = "Software Developer"

def extract_candidate_info(transcript: str):
    """Extract candidate name and role from transcript header if possible."""
    lines = transcript.strip().split('\n')
    header = lines[0] if lines else ""
    
    # Try to extract from format like "Interview - Python TSE (Smriti Sharma)"
    name_match = re.search(r'\((.*?)\)', header)
    candidate_name = name_match.group(1) if name_match else "Anonymous Candidate"
    
    role_match = re.search(r'Interview - (.*?) \(', header)
    role = role_match.group(1) if role_match else DEFAULT_ROLE
    
    return candidate_name, role

def evaluate_candidate_nlp(request_data) -> ReportModel:
    # 1. Extract dynamic info from transcript
    candidate_name, role = extract_candidate_info(request_data.transcript)
    
    # 2. Get Scores
    resume_score = request_data.resume_score
    coding_score = request_data.coding_score
    mcq_score = request_data.mcq_score
    
    # Calculate final score with 3 components (33.3% weight each)
    final_score = (resume_score + coding_score + mcq_score) / 3
    
    # 3. Sentiment Analysis on Transcript
    sentiment, polarity = analyze_sentiment(request_data.transcript)
    
    # 4. Extract Skills from Transcript
    transcript_tech, transcript_soft = extract_skills(request_data.transcript)
    
    # 5. Detect Gaps in Knowledge from Transcript
    uncertainty_markers = [
        "not really sure", "don't know", "can't remember", "not clicking", 
        "haven't used", "no idea", "not recall", "haven't implemented",
        "don't have much knowledge", "don't really have much idea", "0 knowledge",
        "not sure about it", "generic answer", "just not leaking", "not really sure",
        "comma"
    ]
    
    technical_gaps = []
    lines = request_data.transcript.lower().split('\n')
    for i, line in enumerate(lines):
        if any(marker in line for marker in uncertainty_markers):
            # Detailed Topic Extraction
            topic = "role-specific fundamentals"
            for j in range(max(0, i-3), i):
                prev_line = lines[j]
                # Try to catch technical skills first
                prev_tech, _ = extract_skills(prev_line)
                if prev_tech:
                    topic = prev_tech[0]
                    break
                # Fallback: Extract words after "is", "about", "what", "like"
                match = re.search(r'(?:about|what is|like|explain)\s+([a-z0-9\s]+?)(?:\s|\?|$)', prev_line)
                if match:
                    potential_topic = match.group(1).strip()
                    if len(potential_topic) > 2:
                        topic = potential_topic
                        break
            if topic not in [t["topic"] for t in technical_gaps]:
                technical_gaps.append({"topic": topic, "context": line.strip()})

    # 6. IMPROVISED MODEL: Analyze Domain Coverage
    domain_coverage = {}
    for domain, skills in DOMAIN_SKILLS.items():
        matched = [s for s in skills if s in transcript_tech and s not in technical_gaps]
        if matched:
            domain_coverage[domain] = matched
            
    # Sort domains by number of skills matched (descending)
    sorted_domains = sorted(domain_coverage.keys(), key=lambda d: len(domain_coverage[d]), reverse=True)

    # 7. IMPROVISED MODEL: Clarity Score (Estimated from responses vs total words)
    # Using a slightly different detection for candidate role name
    candidate_lines = [line for line in lines if any(x in line for x in [candidate_name.lower(), "smriti"])]
    candidate_words = sum(len(line.split()) for line in candidate_lines)
    clarity_level = "High" if candidate_words > 400 else "Medium" if candidate_words > 150 else "Low"

    # 8. Recommendation Logic
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
    if coding_score < 60 or len(sorted_domains) < 1:
        risk_level = "High"
    elif sentiment == "Negative" or clarity_level == "Low":
        risk_level = "Medium"
    
    # Confidence Level
    scores_list = [resume_score, coding_score, mcq_score]
    min_score = min(scores_list)
    max_score = max(scores_list)
    score_diff = max_score - min_score
    
    if min_score < 40 or len(sorted_domains) == 0:
        confidence_level = "Low"
    elif score_diff > 30:
        confidence_level = "Medium"
    else:
        confidence_level = "High"
        
    # Strengths & Weaknesses (Improvised)
    strengths = []
    if coding_score >= 80: strengths.append("Solid technical/coding background")
    if sentiment == "Positive": strengths.append("Maintained a positive and professional tone throughout")
    
    # List top 2 domains as strengths
    for domain in sorted_domains[:2]:
        if len(domain_coverage[domain]) >= 1:
            strengths.append(f"Knowledge demonstrated in {domain}")
    
    weaknesses = []
    if technical_gaps:
        for gap in technical_gaps[:3]:
            weaknesses.append(f"Conceptual uncertainty regarding '{gap['topic']}': The candidate exhibited a lack of depth or incorrect understanding during the discussion.")
    if len(sorted_domains) < 2:
        weaknesses.append("Narrow Technical Range: Evaluation covered only a few core areas; broader cross-domain knowledge was not evident.")
    if clarity_level == "Low":
        weaknesses.append("Response Depth Concern: Technical answers were brief and lacked the structured detail expected for this seniority level.")
    
    # Recommendations/Insights
    if sorted_domains:
        top_domain = sorted_domains[0]
        candidate_summary = f"{candidate_name} is an overall {decision.lower()} for the {role} position. While they showed knowledge in {top_domain}, there are specific technical areas requiring improvement."
    else:
        candidate_summary = f"{candidate_name} is an overall {decision.lower()} for the {role} position."
    
    improvement_suggestions = []
    for gap in technical_gaps[:3]:
        improvement_suggestions.append(f"Deepen theoretical and practical understanding of '{gap['topic']}' to ensure more accurate and confident technical delivery.")
    if clarity_level != "High":
        improvement_suggestions.append("Work on 'Star' (Situation, Task, Action, Result) method for structuring technical and scenario-based responses.")
    if len(sorted_domains) < 3:
        improvement_suggestions.append("Broaden technical footprint by exploring adjacent technologies in the Cloud/DevOps or Data domains.")
    
    reason = f"Candidate evaluated as '{decision}' with '{clarity_level}' clarity level and '{risk_level}' risk."

    # Build Response using Pydantic Models
    report = ReportModel(
        role=role,
        scores=ScoresModels(
            resume_score=float(round(resume_score, 2)),
            coding_score=float(round(coding_score, 2)),
            mcq_score=float(round(mcq_score, 2)),
            final_score=float(round(final_score, 2))
        ),
        analysis=AnalysisModel(
            sentiment=sentiment,
            confidence_level=confidence_level,
            strengths=strengths,
            weaknesses=weaknesses
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
