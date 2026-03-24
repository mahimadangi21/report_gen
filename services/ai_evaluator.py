import json
import re
from typing import Any


# ─── Keyword Lists ────────────────────────────────────────────────────────────

# Business Analyst keywords
BA_KEYWORDS = [
    "bpmn", "uml", "rtm", "brd", "frd", "srs", "agile", "waterfall", "scrum",
    "sprint", "jira", "devops", "use case", "activity diagram", "sequence diagram",
    "stakeholder", "requirement", "scope creep", "change request", "root cause analysis",
    "five why", "roi", "product backlog", "user story", "wireframe", "prototype",
    "sketch", "adobe xd", "figma", "documentation", "functional", "non-functional",
]

# Data Engineering keywords
DE_KEYWORDS = [
    "python", "sql", "mysql", "power bi", "excel", "databricks", "apache airflow",
    "spark", "spark sql", "pyspark", "hadoop", "etl", "elt", "data lake",
    "data warehouse", "delta lake", "snowflake", "star schema", "snowflake schema",
    "data modelling", "data engineering", "data analyst", "data scientist",
    "big data", "pandas", "numpy", "indexing", "primary key", "foreign key",
    "transitive dependency", "normalisation", "normalization", "dcl", "commit",
    "rollback", "savepoint", "lambda", "join", "query", "structured data",
    "unstructured data", "unity catalogue", "metastore", "airflow", "pipeline",
    "kafka", "aws", "azure", "gcp", "docker", "api", "rest api",
]

# Data Science keywords
DS_KEYWORDS = [
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", 
    "pytorch", "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn", 
    "statistics", "probability", "model deployment", "predictive modeling", 
    "transformer", "neural network", "regression", "classification", "clustering"
]

# Data Analyst keywords
DA_KEYWORDS = [
    "excel", "power bi", "tableau", "sql", "dashboard", "reporting", 
    "data visualization", "data cleaning", "vlookup", "pivot table", 
    "dax", "google analytics", "metrics", "kpi", "etl", "query", "analysis"
]

# MERN Stack keywords
MERN_KEYWORDS = [
    "mongodb", "express", "react", "node.js", "javascript", "typescript", 
    "redux", "mongoose", "rest api", "graphql", "jwt", "frontend", 
    "backend", "full stack", "spa", "dom", "component", "hook"
]

# PHP Developer keywords
PHP_KEYWORDS = [
    "php", "laravel", "codeigniter", "symfony", "mysql", "apache", 
    "nginx", "composer", "eloquent", "mvc", "phpmyadmin", "oop", "pdo", 
    "backend", "restful", "lumen"
]

ALL_TECHNICAL_KEYWORDS = BA_KEYWORDS + DE_KEYWORDS + DS_KEYWORDS + DA_KEYWORDS + MERN_KEYWORDS + PHP_KEYWORDS

SOFT_SKILL_KEYWORDS = {
    "Communication":    ["explain", "communicate", "language", "understand", "words", "clear", "sir"],
    "Analytical":       ["analyse", "analysis", "research", "identify", "reason", "query"],
    "Problem-Solving":  ["solve", "solution", "tackle", "approach", "fix", "implement"],
    "Adaptability":     ["learn", "upskill", "new technology", "research", "adapt", "shift"],
    "Technical Depth":  ["etl", "elt", "spark", "hadoop", "pipeline", "schema", "database"],
    "Initiative":       ["planned", "trying", "learning", "study", "research", "eager", "start"],
    "Presentation":     ["share screen", "show", "demo", "editor", "screenshot"],
}

POSITIVE_WORDS = [
    "good", "great", "understand", "clear", "explain", "knowledgeable", "yes sir",
    "learn", "improve", "manage", "solution", "correct", "right", "yes",
    "analyse", "confident", "approach", "research", "implement", "eager",
]

NEGATIVE_WORDS = [
    "not", "haven't", "don't", "didn't", "fail", "wrong", "miss",
    "unable", "cannot", "weak", "poor", "lack", "sorry",
]

# Role-specific weakness patterns
BA_WEAKNESS_PATTERNS = [
    (r"haven.t implemented", "RTM not implemented in practice"),
    (r"(not able|unable) to explain", "Difficulty explaining some concepts"),
    (r"can you (please )?repeat", "Needed clarification on scenario questions"),
    (r"i.*would take.*days", "Needs a few days to onboard new domains"),
    (r"try to convince", "Escalation approach could be more proactive"),
]

DE_WEAKNESS_PATTERNS = [
    (r"i guess|application factor", "Uncertainty on some advanced concepts"),
    (r"missing something|not picking", "Incomplete query during live coding task"),
    (r"lazy evolution|slow", "Hadoop limitations mentioned but not fully articulated"),
    (r"4 bits of data|unity catalogue", "Slight confusion on 4 V's of Big Data question"),
]

DS_WEAKNESS_PATTERNS = [
    (r"overfitting|underfitting", "Needs clarity on handling model generalization"),
    (r"hyperparameter|tuning", "Limited practical experience in complex model tuning"),
    (r"deploy|production", "Limited exposure to end-to-end model deployment schemas"),
]

DA_WEAKNESS_PATTERNS = [
    (r"dax|complex calculation", "Struggles with advanced DAX or complex table calculations"),
    (r"slow dashboard|performance", "Dashboard performance tuning is an area of growth"),
    (r"data cleaning.*hard", "Requires more practice dealing with highly unstructured data"),
]

MERN_WEAKNESS_PATTERNS = [
    (r"prop drilling|context", "Slight confusion on optimal state management techniques"),
    (r"aggregation pipeline", "MongoDB aggregation pipelines not fully mastered"),
    (r"event loop", "Basic understanding of Node.js event concurrency but lacks depth"),
]

PHP_WEAKNESS_PATTERNS = [
    (r"n\+1|query problem", "Needs improvement in query optimization (N+1 problem)"),
    (r"dependency injection", "Understanding of dependency injection container could be stronger"),
    (r"trait|interface", "OOP concepts like Traits and Interfaces need more practical usage"),
]


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _detect_role(transcript: str) -> str:
    """Detect role from transcript header."""
    lower = transcript.lower()
    if "mern" in lower or "full stack" in lower or "react" in lower:
        return "MERN"
    elif "php" in lower or "laravel" in lower:
        return "PHP"
    elif "data science" in lower or "data scientist" in lower or "machine learning" in lower:
        return "DS"
    elif "data analyst" in lower or "data analysis" in lower:
        return "DA"
    elif "tse de" in lower or "data engineer" in lower:
        return "DE"
    elif "tse ba" in lower or "business analyst" in lower:
        return "BA"
    
    # Fallback: count keyword hits
    hits = {
        "MERN": sum(1 for k in MERN_KEYWORDS if k in lower),
        "PHP": sum(1 for k in PHP_KEYWORDS if k in lower),
        "DS": sum(1 for k in DS_KEYWORDS if k in lower),
        "DA": sum(1 for k in DA_KEYWORDS if k in lower),
        "DE": sum(1 for k in DE_KEYWORDS if k in lower),
        "BA": sum(1 for k in BA_KEYWORDS if k in lower),
    }
    return max(hits, key=hits.get)


def _detect_candidate_name(transcript: str) -> str:
    """Detect candidate name: the non-Nadeem speaker who appears most often."""
    # Find all speaker name+timestamp lines like "Pushpendra Menaria   0:26"
    all_names = re.findall(r"^([A-Z][a-z]+ [A-Z][a-z]+)\s{2,}\d+:\d+", transcript, re.MULTILINE)
    if not all_names:
        return "The candidate"
    # Count occurrences per name
    counts = {}
    for name in all_names:
        counts[name] = counts.get(name, 0) + 1
    # Remove the interviewer (Nadeem) — pick the other most-frequent name
    sorted_names = sorted(counts.items(), key=lambda x: -x[1])
    for name, _ in sorted_names:
        if "nadeem" not in name.lower():
            return name
    return sorted_names[0][0]


def _candidate_text(transcript: str, candidate_name: str) -> str:
    """Extract only the candidate's lines."""
    lines, capture = [], False
    first = candidate_name.split()[0].lower()
    for line in transcript.splitlines():
        stripped = line.strip()
        if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+\s{2,}\d+:\d+', stripped):
            speaker = stripped.split("  ")[0].strip().lower()
            capture = (first in speaker)
            continue
        if capture and stripped:
            lines.append(stripped)
    return " ".join(lines).lower()


def _find_technical_skills(text: str, role: str) -> list:
    role_keywords = {
        "MERN": MERN_KEYWORDS,
        "PHP": PHP_KEYWORDS,
        "DS": DS_KEYWORDS,
        "DA": DA_KEYWORDS,
        "DE": DE_KEYWORDS,
        "BA": BA_KEYWORDS,
    }
    keywords = role_keywords.get(role, DE_KEYWORDS)
    found = []
    for kw in keywords:
        if kw in text:
            label = kw.upper() if len(kw) <= 5 else kw.title()
            if label not in found:
                found.append(label)
    return found


def _find_soft_skills(text: str) -> list:
    return [skill for skill, words in SOFT_SKILL_KEYWORDS.items() if any(w in text for w in words)]


def _find_weaknesses(full_text: str, role: str) -> list:
    role_patterns = {
        "MERN": MERN_WEAKNESS_PATTERNS,
        "PHP": PHP_WEAKNESS_PATTERNS,
        "DS": DS_WEAKNESS_PATTERNS,
        "DA": DA_WEAKNESS_PATTERNS,
        "DE": DE_WEAKNESS_PATTERNS,
        "BA": BA_WEAKNESS_PATTERNS,
    }
    patterns = role_patterns.get(role, DE_WEAKNESS_PATTERNS)
    lower = full_text.lower()
    found = [label for pattern, label in patterns if re.search(pattern, lower)]
    return found if found else ["Limited hands-on production experience"]


def _sentiment(text: str) -> str:
    pos = sum(1 for w in POSITIVE_WORDS if w in text)
    neg = sum(1 for w in NEGATIVE_WORDS if w in text)
    ratio = pos / max(neg, 1)
    if ratio >= 3:
        return "Positive"
    elif ratio >= 1.5:
        return "Neutral"
    return "Negative"


def _confidence(text: str) -> str:
    hedges = len(re.findall(r"\b(i think|i guess|maybe|perhaps|not sure|sorry|um|uh)\b", text))
    asserts = len(re.findall(r"\b(yes sir|definitely|certainly|absolutely|clearly|of course|yes)\b", text))
    if asserts > hedges + 2:
        return "High"
    elif hedges <= 5:
        return "Medium"
    return "Low"


def _interview_score(skills: list, soft: list, sentiment: str, confidence: str) -> int:
    score  = 40
    score += min(len(skills) * 3, 25)
    score += min(len(soft)   * 3, 15)
    score += {"Positive": 10, "Neutral": 5, "Negative": 0}[sentiment]
    score += {"High": 10, "Medium": 6, "Low": 2}[confidence]
    return min(max(score, 0), 100)


def _recommendation(final: float) -> str:
    if final >= 75:
        return "Hire"
    elif final >= 60:
        return "Consider"
    return "Reject"


def _summary(name, role, sentiment, confidence, skills, weaknesses, recommendation, interview_score, final_score) -> str:
    role_labels = {
        "MERN": "MERN Stack Development",
        "PHP": "PHP Development",
        "DS": "Data Science",
        "DA": "Data Analysis",
        "DE": "Data Engineering",
        "BA": "Business Analysis",
    }
    role_label = role_labels.get(role, "Technical")
    skill_str  = ", ".join(skills[:6]) if skills else f"core {role_label} concepts"
    weak_str   = weaknesses[0] if weaknesses else "minor knowledge gaps"
    
    return (
        f"{name} demonstrated a {sentiment.lower()} overall impression during the {role_label} interview, "
        f"communicating with {confidence.lower()} confidence. \n"
        f"• Key strengths: Proven familiarity with {skill_str}.\n"
        f"• Areas for improvement: {weak_str}.\n"
        f"• Scoring metrics: Interview Score: {interview_score}/100 | Final Assessment Score: {final_score:.1f}/100.\n"
        f"Conclusion: We recommend the status as '{recommendation}' based on this evaluation."
    )


# ─── Main Entry Point ─────────────────────────────────────────────────────────

async def evaluate_candidate(resume_score: float, coding_score: float, transcript: Any) -> dict:
    if isinstance(transcript, (dict, list)):
        transcript_text = json.dumps(transcript)
    else:
        transcript_text = str(transcript)

    role           = _detect_role(transcript_text)
    candidate_name = _detect_candidate_name(transcript_text)
    candidate_text = _candidate_text(transcript_text, candidate_name)
    full_lower     = transcript_text.lower()

    technical_skills = _find_technical_skills(candidate_text + " " + full_lower, role)
    soft_skills      = _find_soft_skills(candidate_text)
    weaknesses       = _find_weaknesses(full_lower, role)
    sentiment        = _sentiment(candidate_text)
    confidence_level = _confidence(candidate_text)
    interview_score  = _interview_score(technical_skills, soft_skills, sentiment, confidence_level)
    final_score      = round(resume_score * 0.3 + interview_score * 0.4 + coding_score * 0.3, 1)
    recommendation   = _recommendation(final_score)

    summary = _summary(
        candidate_name, role, sentiment, confidence_level,
        technical_skills, weaknesses, recommendation,
        interview_score, final_score
    )

    return {
        "candidate_name":   candidate_name,
        "role":             role,
        "sentiment":        sentiment,
        "confidence_level": confidence_level,
        "technical_skills": technical_skills,
        "soft_skills":      soft_skills,
        "weaknesses":       weaknesses,
        "interview_score":  interview_score,
        "resume_score":     resume_score,
        "coding_score":     coding_score,
        "final_score":      final_score,
        "recommendation":   recommendation,
        "summary":          summary
    }
