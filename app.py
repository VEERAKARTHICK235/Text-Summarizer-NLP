import streamlit as st
import nltk
import re
import base64
import PyPDF2
from fpdf import FPDF
import requests
import json
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

# -------------------- GEMINI API CONFIG --------------------
GEMINI_API_KEY = "AIzaSyBAgCAz2YjBHjgapIiA5pdPxRJa4JWus1I"  # Replace with your real Gemini API key
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

# -------------------- GEMINI SUMMARIZATION FUNCTION --------------------
def summarize_text(input_text, num_sentences=3):
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [
            {
                "parts": [
                    {"text": f"Summarize the following text in {num_sentences} sentences:\n{input_text}"}
                ]
            }
        ]
    }

    response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        summary = response.json()['candidates'][0]['content']['parts'][0]['text']
        return summary
    else:
        return f"Error: {response.status_code} - {response.text}"

# -------------------- EXTRACT TEXT FROM PDF --------------------
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# -------------------- TXT DOWNLOAD LINK --------------------
def get_text_download_link(text, filename="summary.txt"):
    b64 = base64.b64encode(text.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}">📥 Download as .txt</a>'

# -------------------- PDF DOWNLOAD LINK --------------------
def get_pdf_download_link(text, filename="summary.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    for line in text.split('\n'):
        pdf.multi_cell(0, 10, line)

    pdf_output = pdf.output(dest='S').encode('latin1')  # Return as bytes
    b64 = base64.b64encode(pdf_output).decode()         # Encode as base64
    return f'<a href="data:application/pdf;base64,{b64}" download="{filename}">📄 Download as .pdf</a>'

# -------------------- STREAMLIT UI --------------------
st.set_page_config(page_title="AI Text Summarizer", page_icon="🧠", layout="centered")

# Title
st.title("📝 AI Text Summarizer")
st.markdown("Summarize long articles using Google's **Gemini 1.5 Flash** API in seconds.")

# File Upload
input_text = ""
uploaded_file = st.file_uploader("📂 Upload a .txt or .pdf file", type=["txt", "pdf"])
if uploaded_file:
    if uploaded_file.type == "text/plain":
        input_text = uploaded_file.read().decode("utf-8")
    elif uploaded_file.type == "application/pdf":
        input_text = extract_text_from_pdf(uploaded_file)

# Manual Input
manual_input = st.text_area("✏️ Or paste your text below:", height=200)
if manual_input:
    input_text += "\n" + manual_input

# Summary Sentence Count
max_sentences = st.slider("🔢 Number of sentences in summary", 1, 10, 3)

# Summarize Button
if st.button("✨ Summarize"):
    if input_text.strip():
        summary = summarize_text(input_text, max_sentences)
        st.success("✅ Summary Generated")
        st.subheader("📌 Summary:")
        st.write(summary)

        st.markdown("---")
        st.markdown(get_text_download_link(summary, "summary.txt"), unsafe_allow_html=True)
        st.markdown(get_pdf_download_link(summary, "summary.pdf"), unsafe_allow_html=True)
    else:
        st.warning("⚠️ Please upload or enter text to summarize.")
