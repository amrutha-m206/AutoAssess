import streamlit as st
import pymupdf as fitz
from groq import Groq

client = Groq(api_key="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")




# Function to extract text from a PDF
def extract_text_from_pdf(uploaded_file):
    """Extract text from the uploaded PDF file."""
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as pdf_document:
        for page in pdf_document:
            text += page.get_text()
    return text


def generate_questions(text, num_questions):
    """Generate quiz questions from extracted text using Groq's Llama model."""
    max_input_length = 1024 - 100
    truncated_text = text[:max_input_length]

    prompt = (
        f"Generate {num_questions} quiz questions based on the following text. For each question, provide 4 distinct multiple choice options with one correct answer. Do not include 'None of the above' or similar options like 'All of the above'. Clearly mark the correct answer as follows:\n\n"
        f"For each question, provide 4 options, and make sure the correct answer is clearly labeled like this: 'Answer: <correct_answer>'\n\n"
        f"{truncated_text}"
    )

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
        )

        response_content = chat_completion.choices[0].message.content.strip()

        if not response_content or "question" not in response_content.lower():
            st.error("No valid questions generated. Please try again.")
            return [], [], []

        questions, options, correct_answers = [], [], []
        lines = response_content.splitlines()
        current_question, current_options, current_answer = None, [], None

        for line in lines:
            line = line.strip()
            if line.lower().startswith("question") or "?" in line:
                if current_question:
                    questions.append(current_question)
                    options.append(current_options)
                    correct_answers.append(current_answer)
                question_text = line.split(":", 1)[-1].strip()
                current_question, current_options, current_answer = (
                    question_text,
                    [],
                    None,
                )
            elif line.lower().startswith(("a)", "b)", "c)", "d)")):
                current_options.append(line.strip())
            elif "answer:" in line.lower():  # Make sure we capture answers correctly
                # Extract the correct answer and clean up any extraneous text
                current_answer = line.split(":", 1)[-1].strip()

        if current_question:
            questions.append(current_question)
            options.append(current_options)
            correct_answers.append(current_answer)

        return (
            questions[:num_questions],
            options[:num_questions],
            correct_answers[:num_questions],
        )

    except Exception as e:
        st.error(f"Error generating questions: {e}")
        return [], [], []


st.title("AutoAssess - Real Time Self Assessment System")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
num_questions = st.slider("Select number of questions", 1, 10, value=3)

if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

if st.button("Generate Quiz") and uploaded_file:
    text = extract_text_from_pdf(uploaded_file)
    questions, options, correct_answers = generate_questions(text, num_questions)

    st.session_state.questions = questions
    st.session_state.options = options
    st.session_state.correct_answers = correct_answers
    st.session_state.quiz_submitted = False
    st.session_state.user_answers.clear()

if "questions" in st.session_state:
    st.subheader("Generated Quiz Questions")
    with st.form(key="quiz_form"):
        for i, (question, opts) in enumerate(
            zip(st.session_state.questions, st.session_state.options), 1
        ):
            st.write(f"Q{i}: {question}")
            selected_answer = st.radio(
                f"Select your answer for Question {i}", opts, key=f"question_{i}",index=None
            )
            st.session_state.user_answers[i] = selected_answer

        submit_button = st.form_submit_button(label="Submit Quiz")

        if submit_button:
            # Check answers and calculate score
            score = 0
            for i in range(num_questions):
                user_answer = st.session_state.user_answers.get(i + 1)
                if user_answer and user_answer == st.session_state.correct_answers[i]:
                    score += 1

            st.session_state.score = score
            st.session_state.total_questions = num_questions
            st.session_state.quiz_submitted = True

if st.session_state.quiz_submitted:
    st.success(
        f"Your score: {st.session_state.score}/{st.session_state.total_questions}"
    )

    st.subheader("Correct Answers")
    for i in range(num_questions):
        user_answer = st.session_state.user_answers.get(i + 1)
        correct_answer = st.session_state.correct_answers[i]

      
        st.write(f"Q{i+1}: {st.session_state.questions[i]}")

        
        user_answer_display = user_answer if user_answer else "No answer selected"
        
    
        if user_answer == correct_answer:
            answer_status = "Correct"
            answer_color = "green"
        else:
            answer_status = "Incorrect"
            answer_color = "red"

        st.write(
            f"Your Answer: {user_answer_display} ({answer_status})", unsafe_allow_html=True
        )
        st.write(
            f"Correct Answer: {correct_answer} (Correct)", unsafe_allow_html=True
        )
        st.write("---")

