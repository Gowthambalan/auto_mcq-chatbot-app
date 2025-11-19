import chromadb
import requests
import random
from datetime import datetime

client = chromadb.PersistentClient(path="data/vector_db")

# Call Qwen/Ollama
def call_qwen(prompt: str) -> str:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen2.5vl:7b",
            "prompt": prompt,
            "stream": False
        }
    )
    response.raise_for_status()
    return response.json()["response"]

def generate_mcq_questions(subject: str, num_questions: int = 15):
    if subject not in [c.name for c in client.list_collections()]:
        return [f"No collection found for subject: {subject}"]

    collection = client.get_collection(name=subject)
    results = collection.query(query_texts=["important concepts"], n_results=10)

    if not results["documents"] or not results["documents"][0]:
        return ["No content found. Please upload PDFs first."]

    context = "\n".join(results["documents"][0])
    seed = datetime.now().strftime("%Y%m%d%H%M%S")

    prompt = (
        f"You are a {subject} teacher. Based on the following textbook, generate exactly {num_questions} "
        f"unique and different multiple-choice questions (MCQs). Each question must follow this format:\n\n"
        f"Q: <Question>\nA. <Option 1>\nB. <Option 2>\nC. <Option 3>\nD. <Option 4>\n"
        f"Answer: <Correct Option Letter>\nExplanation: <Short Explanation>\n\n"
        f"Ensure all questions are diverse and from different concepts. Seed: {seed}\n\n"
        f"{context}"
    )

    response_text = call_qwen(prompt)

    raw_lines = response_text.strip().split("\n")
    questions = []
    q = {"question": "", "options": [], "answer": "", "explanation": ""}
    for line in raw_lines:
        if line.startswith("Q:"):
            if q["question"]:
                questions.append(q)
                q = {"question": "", "options": [], "answer": "", "explanation": ""}
            q["question"] = line[2:].strip()
        elif line.strip().startswith(("A.", "B.", "C.", "D.")):
            q["options"].append(line.strip())
        elif line.lower().startswith("answer:"):
            q["answer"] = line.split(":")[1].strip().upper()
        elif line.lower().startswith("explanation:"):
            q["explanation"] = line.split(":", 1)[1].strip()

    if q["question"]:
        questions.append(q)

    return questions[:num_questions]  # return the question list


#  New function to check answer
def validate_answer(question_obj: dict, selected_option: str) -> dict:
    correct = selected_option.strip().upper() == question_obj["answer"]
    return {
        "question": question_obj["question"],
        "your_answer": selected_option.upper(),
        "correct_answer": question_obj["answer"],
        "is_correct": correct,
        "explanation": question_obj["explanation"]
    }


# New function for subject-based chatbot
def chat_with_subject_bot(subject: str, user_question: str) -> str:
    if subject not in [c.name for c in client.list_collections()]:
        return f"No collection found for subject: {subject}"

    collection = client.get_collection(name=subject)
    results = collection.query(query_texts=[user_question], n_results=5)

    if not results["documents"] or not results["documents"][0]:
        return "No relevant content found. Please upload PDFs first."

    context = "\n".join([doc for docs in results["documents"] for doc in docs])

    prompt = (
        f"You are an expert {subject} teacher. Based on the textbook content below, answer the student question clearly, "
        f"then generate exactly 3 MCQs (with 4 options, correct answer, and short explanation) related to the same topic.\n\n"
        f"---\n"
        f"Question: {user_question}\n\n"
        f"Context:\n{context}\n\n"
        f"Format your response like:\n"
        f"**Answer:** <your explanation>\n\n"
        f"**MCQ 1:**\nQ: ...\nA. ...\nB. ...\nC. ...\nD. ...\nAnswer: ...\nExplanation: ...\n\n"
        f"... and so on."
    )

    response = call_qwen(prompt)
    return response.strip()
