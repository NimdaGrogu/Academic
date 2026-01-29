from ingestion import get_jd_from_url, get_pdf_text
from rag_implementation import get_rag_chain
from dotenv import load_dotenv
import streamlit as st
import os
import logging
from rich.logging import RichHandler

# Configure basic config with RichHandler
logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s", # Rich handles the timestamp and level separately
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger("app")

# load the env variables
load_dotenv(dotenv_path=".env")
open_api_key = os.getenv("OPENAI_API_KEY")


# Configuration
st.set_page_config(page_title="AI Job Hunt Assistant", page_icon="👔")
st.title("👔 AI Job Hunt Assistant")
st.markdown("Provide a job description URL and a candidate resume to get a comprehensive analysis.")


# Sidebar for Inputs

with st.sidebar:
    st.header("Input Data")
    # Input 1: Web Page Link (Job Description)
    jd_url = st.text_input("Job Description URL:" , placeholder="https://linkedin.com/jobs/...")
    # Input 2: Raw text (Job Description)
    jd_text = st.text_input("Job Description Raw Text")
    # Input 3: Upload the PDF
    uploaded_resume = st.file_uploader("Upload Candidate Resume (PDF)", type=["pdf"])
    # Button to trigger analysis
    submit = st.button("Analyse Candidate Resume")

# Main Section
if submit:
    # --- Validations ---
    if not open_api_key:
        st.error("⚠️ OpenAI API Key is missing. Please check your .env file.")
        st.stop()  # Stop execution here

    if not uploaded_resume:
        st.warning("⚠️ Please provide Resume PDF ...")
        st.stop()  # Stop execution here

    if not jd_url and not jd_text:
        st.error("⚠️ Please provide Job Description ...")
        st.stop()  # Stop execution here

    # --- Processing ---
    # A. Get Job Description Text
    # Prioritize URL if provided, otherwise use text
    job_description = get_jd_from_url(jd_url) if jd_url else jd_text

    # B. Get Resume Text
    resume_text = get_pdf_text(uploaded_resume)

    if resume_text and job_description:
        with st.spinner("Digesting Resume and Job Description..."):
            st.success("✅ Data successfully extracted!")

            # --- Debugging ---
            with st.expander("View Extracted Data"):
                st.subheader("Job Description Snippet")
                # FIX: Print the processed variable, not the input variable
                st.write(job_description[:500] + "...")

                st.subheader("Resume Snippet")
                st.write(resume_text[:500] + "...")

    with st.spinner("Analysing Candidate Resume and Job Description.."):
        # 1. Build the RAG Chain with the Resume Data
        qa_chain = get_rag_chain(resume_text)

        # 2. Define your questions
        questions = {
            "q1": "Does the candidate meet the required skills?",
            "q2": "Is the candidate a good fit for the job position?",
            "q3": "Analyze Candidate Strengths for the job position",
            "q4": "Analyze Candidate Opportunities to improve based on the job description",
            "q5": "Show match details (0-100%)",
            "q6": "Create a cover letter tailored to this job",
            "q7": "Suggest 3 ways to stand out for this specific role"
        }

        # 3. Run the Analysis
        st.markdown("---")
        st.subheader("📊 Analysis Results")

        # Create tabs for a cleaner UI
        tabs = st.tabs(["Fit Analysis", "Strengths & Weaknesses", "Cover Letter & Tips"])

        # We combine the Job Description into the query so the AI knows what to compare against
        base_query = f"Based on this Job Description: \n\n {job_description} \n\n Answer this: "

        with tabs[0]:  # Q1, Q2, Q5
            st.markdown("### 🎯 Fit Assessment")
            q1_ans = qa_chain.invoke({"query": base_query + questions["q1"]})
            st.write(f"**Skills Check:** {q1_ans['result']}")

            q2_ans = qa_chain.invoke({"query": base_query + questions["q2"]})
            st.write(f"**Fit Check:** {q2_ans['result']}")

            q5_ans = qa_chain.invoke({"query": base_query + questions["q5"]})
            st.write(f"**Match Details:** {q5_ans['result']}")

        with tabs[1]:  # Q3, Q4
            st.markdown("### 📈 SWOT Analysis")
            col1, col2 = st.columns(2)
            with col1:
                st.info("Strengths")
                q3_ans = qa_chain.invoke({"query": base_query + questions["q3"]})
                st.write(q3_ans['result'])
            with col2:
                st.warning("Opportunities")
                q4_ans = qa_chain.invoke({"query": base_query + questions["q4"]})
                st.write(q4_ans['result'])

        with tabs[2]:  # Q6, Q7
            st.markdown("### 📝 Application Kit")
            q6_ans = qa_chain.invoke({"query": base_query + questions["q6"]})
            with st.expander("Draft Cover Letter"):
                st.write(q6_ans['result'])

            q7_ans = qa_chain.invoke({"query": base_query + questions["q7"]})
            st.write(f"**How to Stand Out:**\n{q7_ans['result']}")











