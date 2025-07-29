import streamlit as st
from app.services.rag_llm import chat_with_subject_bot, generate_mcq_questions, validate_answer

st.title("MCQ Generator")

subject = st.selectbox("Select Subject", ["chemistry", "physics", "maths"])
num_questions = st.slider("Number of Questions", 1, 20, 5)

if st.button("Generate MCQs"):
    st.session_state["mcqs"] = generate_mcq_questions(subject, num_questions)
    st.success(f"Generated {len(st.session_state['mcqs'])} questions for {subject}")

if "mcqs" in st.session_state:
    for idx, q in enumerate(st.session_state["mcqs"]):
        st.markdown(f"**Q{idx + 1}. {q['question']}**")
        selected = st.radio(
            f"Select your answer for Q{idx + 1}",
            q["options"],
            key=f"answer_{idx}"
        )

        if st.button(f"Check Answer {idx+1}"):
            selected_option = selected.split(".")[0].strip().upper()  # Extract A/B/C/D
            result = validate_answer(q, selected_option)
            if result["is_correct"]:
                st.success(f"✅ Correct! Explanation: {result['explanation']}")
            else:
                st.error(f"❌ Wrong. Correct answer is {result['correct_answer']}. Explanation: {result['explanation']}")

st.divider()
st.subheader("🧠 Subject Tutor Chatbot")

# # Initialize chat history
# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []

# chat_subject = st.selectbox("Choose Subject", ["chemistry", "physics", "maths"], key="chat_subject_chat")
# user_input = st.text_input("Ask a question (e.g., Explain Atomic Structure)", key="user_question")

# if st.button("Send") and user_input.strip():
#     with st.spinner("Thinking..."):
#         response = chat_with_subject_bot(chat_subject, user_input)
    
#     # Append to chat history
#     st.session_state.chat_history.append({
#         "role": "user",
#         "text": user_input
#     })
#     st.session_state.chat_history.append({
#         "role": "bot",
#         "text": response
#     })

# # Display the chat history
# for msg in st.session_state.chat_history:
#     if msg["role"] == "user":
#         st.markdown(f"**👤 You:** {msg['text']}")
#     else:
#         st.markdown(f"**🤖 Bot:**\n\n{msg['text']}", unsafe_allow_html=True)


if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

chat_subject = st.selectbox("Choose Subject", ["chemistry", "physics", "maths"], key="chat_subject_chat")
user_input = st.text_input("Ask a conceptual question", key="chat_input")

col1, col2 = st.columns([1, 4])
with col1:
    send = st.button("Send")
with col2:
    clear = st.button("🗑️ Clear Chat")

if send and user_input.strip():
    with st.spinner("Thinking..."):
        response = chat_with_subject_bot(chat_subject, user_input)
    st.session_state.chat_history.append({"role": "user", "text": user_input})
    st.session_state.chat_history.append({"role": "bot", "text": response})

if clear:
    st.session_state.chat_history = []

    # Render chat
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"**👤 You:** {msg['text']}")
    else:
        st.markdown(f"**🤖 Bot:**\n\n{msg['text']}", unsafe_allow_html=True)