from utils.nlp_utils import extract_skills

def test_new_skills():
    test_text = "I have experience in php, quality assurance, and data engineering. I also know bussiness analytics, mern stack and python."
    tech_skills, soft_skills = extract_skills(test_text)
    
    print(f"Text: {test_text}")
    print(f"Extracted Technical Skills: {tech_skills}")
    
    expected_new_skills = ["php", "quality assurance", "data engineering", "analytics", "mern", "python"]
    # "business" is in the text as "bussiness" (user wrote "bussiness" and I added "business" to the list?) 
    # Let me check what I added.
    
    for skill in expected_new_skills:
        if skill in tech_skills:
            print(f"✅ Found: {skill}")
        else:
            print(f"❌ Missing: {skill}")

if __name__ == "__main__":
    test_new_skills()
