from fastapi import APIRouter, Body 
from app.services.rag_llm import generate_mcq_questions

router = APIRouter()

@router.post("/generate_questions")
def generate_questions(payload: dict = Body(...)):
    subject = payload.get("subject")
    num_questions = min(int(payload.get("num_questions", 15)), 20)

    questions = generate_mcq_questions(subject, num_questions)
    return {"subject": subject, "questions": questions}
