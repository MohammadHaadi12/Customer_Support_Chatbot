from dotenv import load_dotenv
import os
from openai import OpenAI
from fastapi import FastAPI
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from fastapi import Request

load_dotenv()

app = FastAPI()

#create the rate limiter
limiter = Limiter(key_func=get_remote_address)

# Add middleware to FastAPI
app.state.limiter = limiter

client = OpenAI(api_key=os.getenv("OPENAI_APIKEY"))


class ChatData(BaseModel):
    prompt: str


def simple_chat(prompt: str):
    model = "gpt-5-nano"

    system_message = (
        "You are a customer-support assistant for an e-commerce platform. "
        "Your job is ONLY to help with order issues, shipping, refunds, account assistance, "
        "and general customer concerns.\n\n"

        "SAFETY RULES:\n"
        "- If the user asks anything unrelated to customer support, politely refuse.\n"
        "- If the user requests harmful, illegal, or inappropriate content, refuse.\n"
        "- Never produce rude or offensive language.\n"
        "- Always respond professionally.\n\n"

        "TONE INSTRUCTIONS:\n"
        "First, determine if the user's message is positive, neutral, or negative.\n"
        "- Negative: be empathetic & reassuring.\n"
        "- Neutral: be concise & helpful.\n"
        "- Positive: be friendly.\n"
    )



    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        reasoning={ "effort": "minimal"}
    )
    
    return response.output_text

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": "Too many requests. Try again later."}
    )

@app.post("/chat")
@limiter.limit("5/minute")
def chat_endpoint(data: ChatData , request: Request):
    return {"response": simple_chat(data.prompt)}

