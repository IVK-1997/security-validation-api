from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)

ADULT_WORDS = ["sex", "nude", "xxx"]
PROFANITY_WORDS = ["damn", "shit", "fuck"]
HARASSMENT_WORDS = ["idiot", "stupid", "hate you"]

class SecurityRequest(BaseModel):
    userId: str
    input: str
    category: str

def contains_inappropriate(text):
    text_lower = text.lower()

    for word in ADULT_WORDS + PROFANITY_WORDS + HARASSMENT_WORDS:
        if word in text_lower:
            return True, word

    return False, None

def sanitize(text):
    for word in ADULT_WORDS + PROFANITY_WORDS + HARASSMENT_WORDS:
        text = re.sub(word, "***", text, flags=re.IGNORECASE)
    return text

@app.post("/")
def validate_input(request: SecurityRequest):

    if not request.input:
        raise HTTPException(status_code=400, detail="Input cannot be empty")

    flagged, word = contains_inappropriate(request.input)

    if flagged:
        confidence = 0.95
        logging.warning(f"Blocked content from user {request.userId}")
        return {
            "blocked": True,
            "reason": f"Inappropriate content detected: {word}",
            "sanitizedOutput": sanitize(request.input),
            "confidence": confidence
        }

    return {
        "blocked": False,
        "reason": "Input passed all security checks",
        "sanitizedOutput": request.input,
        "confidence": 0.99
    }
