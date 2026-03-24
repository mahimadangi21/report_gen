import urllib.request
import urllib.parse
import json

try:
    with open('transcript1.txt', 'r', encoding='utf-8') as f:
        transcript = f.read()

    payload = {
        "resume_score": 85.0,
        "coding_score": 90.0,
        "transcript": transcript
    }
    
    data = json.dumps(payload).encode('utf-8')

    req = urllib.request.Request(
        'http://localhost:3000/api/evaluate', 
        data=data, 
        headers={'Content-Type': 'application/json'}
    )
    
    with urllib.request.urlopen(req) as response:
        response_text = response.read().decode('utf-8')
        
        with open('output.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(json.loads(response_text), indent=2))
        print("Success! Response written to output.json")

except Exception as e:
    print("An error occurred:", e)
