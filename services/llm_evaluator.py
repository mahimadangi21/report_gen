import os
import json
import time
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError

# Import the robust NLP implementation as a fallback
from services.ai_evaluator import evaluate_candidate as nlp_evaluate_candidate

load_dotenv()

HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
PRIMARY_MODEL = os.getenv("AI_MODEL", "Qwen/Qwen2.5-1.5B-Instruct")

# Fallback models mapping task #4 & #5
FALLBACK_MODELS = [
    PRIMARY_MODEL,
    "HuggingFaceH4/zephyr-7b-beta",
    "mistralai/Mistral-7B-Instruct-v0.2"
]

client = InferenceClient(token=HF_API_KEY) if HF_API_KEY else None

def query_huggingface(prompt: str) -> str:
    if not client:
        print("Error: HUGGINGFACE_API_KEY not found.")
        return ""
        
    for model_name in FALLBACK_MODELS:
        print(f"Trying model: {model_name}...")
        try:
            response = client.text_generation(
                prompt,
                model=model_name,
                max_new_tokens=1000,
                return_full_text=False
            )
            return response
            
        except HfHubHTTPError as e:
            if "503" in str(e) or (hasattr(e, 'response') and e.response.status_code == 503):
                print(f"Model {model_name} is loading. Re-trying in 5 seconds...")
                time.sleep(5)
                try:
                    return client.text_generation(
                        prompt, model=model_name, max_new_tokens=1000, return_full_text=False
                    )
                except Exception as ex:
                    print(f"Retry failed for {model_name}: {ex}")
                    continue
            else:
                print(f"HF API Error with {model_name}: {e}")
                continue
        except Exception as e:
            print(f"General Error with {model_name}: {e}")
            continue
            
    # If all models fail
    return ""

async def evaluate_candidate(resume_score: float, coding_score: float, transcript: str) -> dict:
    if isinstance(transcript, (dict, list)):
        transcript_str = json.dumps(transcript)
    else:
        transcript_str = str(transcript)
        
    prompt = f"""
    You are an expert AI interviewer and technical evaluator. Read the following interview transcript and evaluate the candidate.
    You must output your evaluation ONLY as a valid JSON object matching this exact structure. Do not output anything outside of the JSON.
    {{
        "candidate_name": "<Extract the name of the candidate>",
        "role": "<Extract the job role being interviewed for, e.g., Data Engineer, MERN, PHP, etc.>",
        "sentiment": "<Positive, Neutral, or Negative>",
        "confidence_level": "<High, Medium, or Low>",
        "technical_skills": ["List", "Of", "Skills", "Mentioned"],
        "soft_skills": ["List", "Of", "Soft", "Skills"],
        "weaknesses": ["List", "Of", "Weaknesses", "or", "Knowledge", "Gaps"],
        "interview_score": <A number between 0 and 100>,
        "recommendation": "<Hire, Consider, or Reject>",
        "summary": "<A concise text summary detailing the overall evaluation, strengths, and weaknesses>"
    }}
    
    Transcript:
    {transcript_str}
    """
    
    llm_response = query_huggingface(prompt)
    print("Raw LLM Response snippet:", llm_response[:100], "...")
    
    # Attempt to extract JSON from response
    try:
        if not llm_response:
            raise ValueError("Empty response from Hugging Face.")
            
        start_idx = llm_response.find("{")
        end_idx = llm_response.rfind("}")
        
        if start_idx != -1 and end_idx != -1:
            clean_json = llm_response[start_idx:end_idx+1]
            eval_data = json.loads(clean_json)
            
            interview_score = eval_data.get("interview_score", 50)
            try:
                interview_score = float(interview_score)
            except:
                interview_score = 50.0

            final_score = round(resume_score * 0.3 + interview_score * 0.4 + coding_score * 0.3, 1)
            
            return {
                **eval_data,
                "resume_score": resume_score,
                "coding_score": coding_score,
                "final_score": final_score,
                "llm_success": True,
                "evaluation_method": "HuggingFace_LLM"
            }
        else:
            raise ValueError("No JSON payload found in the LLM response.")
            
    except Exception as e:
        print("LLM evaluation failed, falling back to NLP. Error:", e)
        
        # ─── FALLBACK TO NLP ───
        nlp_result = await nlp_evaluate_candidate(resume_score, coding_score, transcript_str)
        nlp_result["llm_success"] = False
        nlp_result["evaluation_method"] = "NLP_Keyword_Matcher"
        return nlp_result
