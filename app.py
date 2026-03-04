import streamlit as st
from PyPDF2 import PdfReader
import os
from google import genai

api_key = st.secrets("GEMINI_API_KEY")
if not api_key:
    st.error("Ошибка: API ключ не найден")
    st.stop()

os.environ["GENAI_API_KEY"] = api_key
client = genai.Client()

st.set_page_config(page_title="Чат с документом (PDF)", layout="wide")
st.title("Чат с документом (PDF)")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

uploaded_file = st.file_uploader("Загрузите PDF файл", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    st.session_state.pdf_text = text[:3000]
    st.success("Файл успешно загружен")

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=None):
        st.markdown(message["content"])

user_input = st.chat_input("Введите запрос")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user", avatar=None):
        st.markdown(user_input)

    prompt = f"Документ PDF:\n{st.session_state.pdf_text}\n\nВопрос: {user_input}\nОтветьте на русском языке."

    with st.chat_message("assistant", avatar=None):
        with st.spinner("Анализ..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                answer = response.text.strip()
            except Exception as e:
                answer = f"Ошибка API: {e}"

            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})