from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re

app = FastAPI()

# Enable CORS for browser-based graders
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class SecurityRequest(BaseModel):
    userId: str
    input: str
    category: str


# Keyword lists
ADULT_WORDS = ["sex", "nude", "xxx","adult","porn","explicit"]
PROFANITY_WORDS = ["damn", "shit", "fuck","bitch","pussy","dick"]
HARASSMENT_WORDS = ["idiot", "stupid", "hate you"]

CONFIDENCE_THRESHOLD = 0.9


def check_inappropriate_content(text: str):
    text_lower = text.lower()

    for word in ADULT_WORDS:
        if word in text_lower:
            return True, f"Inappropriate content detected: {word}", 0.95

    for word in PROFANITY_WORDS:
        if word in text_lower:
            return True, f"Profanity detected: {word}", 0.93

    for word in HARASSMENT_WORDS:
        if word in text_lower:
            return True, f"Harassment detected: {word}", 0.92

    return False, "Input passed all security checks", 0.99


def sanitize_output(text: str):
    sanitized = text
    all_words = ADULT_WORDS + PROFANITY_WORDS + HARASSMENT_WORDS
    for word in all_words:
        sanitized = re.sub(word, "***", sanitized, flags=re.IGNORECASE)
    return sanitized


@app.post("/")
def validate_input(request: SecurityRequest):

    if not request.input:
        raise HTTPException(status_code=400, detail="Input cannot be empty")

    blocked, reason, confidence = check_inappropriate_content(request.input)

    if blocked and confidence > CONFIDENCE_THRESHOLD:
        return {
            "blocked": True,
            "reason": reason,
            "sanitizedOutput": sanitize_output(request.input),
            "confidence": confidence,
        }

    return {
        "blocked": False,
        "reason": reason,
        "sanitizedOutput": sanitize_output(request.input),
        "confidence": confidence,
    }
