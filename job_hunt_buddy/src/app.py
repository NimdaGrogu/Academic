# Libraries

from ingestion import get_jd_from_url, get_pdf_text_pypdf, get_pdf_text_pdfplumber
from rag_implementation import get_rag_chain
from helper import extract_match_score
from dotenv import load_dotenv
import streamlit as st
import os
import logging
from rich.logging import RichHandler


# Configure basic Logging config with RichHandler
logging.basicConfig(
    level=logging.WARNING,
    format="%(message)s", # Rich handles the timestamp and level separately
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger("app")

# load the env variables
load_dotenv()
open_api_key = os.getenv("OPENAI_API_KEY")

# Streamlit Configuration
st.set_page_config(page_title="AI Job Hunt Assistant", page_icon="🚀", layout='wide')
# Main Streamlit
st.title("👔 AI Job Hunt Assistant")
st.markdown("**Provide a job description URL and a candidate resume to get a comprehensive analysis.**")
# Sidebar for Inputs
with st.sidebar:
    st.header("Input Data")
    # Input 1: Web Page Link (Job Description)
    jd_url = st.text_input(placeholder="https://linkedin.com/jobs/view/..",
                           max_chars=5000,
                           label="Job Description URL ")
    # Input 2: Raw text (Job Description)
    jd_text = st.text_input("Job Description Raw Text", max_chars=5000)
    # Input 3: Upload the PDF
    uploaded_resume = st.file_uploader("Upload Candidate Resume (PDF)", type=["pdf"])
    # Button to trigger analysis
    submit = st.button("Analyse Candidate Resume")


    # Markdown for the badge
    sidebar_footer_style = """
    <style>
    /* This targets the specific container in the sidebar */
    [data-testid="stSidebar"] > div:first-child {
        display: flex;
        flex-direction: column;
        height: 100vh;
    }

    /* This targets the last element inside the sidebar and pushes it down */
    [data-testid="stSidebar"] > div:first-child > div:last-child {
        margin-top: auto;
    }
    </style>
    """
    # 4. Add your footer content (This must be the LAST thing you write to the sidebar)
    st.markdown("---")  # Optional horizontal rule
    st.link_button("Visit GitHub Repo", "https://github.com/NimdaGrogu/Academic/tree/main/job_hunt_buddy")
    st.caption("© 2026 Grogus")

    # 3. Inject the CSS
    st.markdown(sidebar_footer_style, unsafe_allow_html=True)

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
    # Prioritize URL if provided, otherwise use text and check if the URL is not None, HTTP Errors
    if jd_url:
        job_description = get_jd_from_url(jd_url)
        if job_description is None:
            st.error("❌ Something went wrong accessing the URL provided, try again or try the raw text instead..")
            st.stop()
    else:
        job_description = jd_text


    # B. Get Resume Text
    with st.spinner("Extracting information from the resume .."):
        resume_text = get_pdf_text_pdfplumber(uploaded_resume)
        st.success("✅ Done ..")

    if resume_text and job_description:
        with st.spinner("Processing Resume and Job Description..."):
            #st.success("✅ Data successfully extracted!")

            with st.expander("View Extracted Data"):
                st.subheader("Job Description Snippet")
                st.write(job_description[:500] + "...")
                st.subheader("Resume Snippet")
                st.write(resume_text[:500] + "...")

    with st.spinner("Analysing Candidate Resume and Job Description.."):
        # 1. Build the RAG Chain with the Resume Data
        qa_chain = get_rag_chain(resume_text, uploaded_resume.name)

        # 2. Define your questions
        questions = {
            "q1": "Does the candidate meet the required skills?",
            "q2": "Is the candidate a good fit for the job position?",
            "q3": "Evaluate and analyse the candidate resume and job description, and Show match details  between (0-100%)",
            "q4": "Analyze Candidate Strengths for the job position",
            "q5": "Analyze Candidate Opportunities to improve based on the job description",
            "q6": "Analyze Candidate Weaknesses based on the job description",
            "q7": "Create a cover letter tailored to this job, use the resume to fill out information like the name and "
                  "contact information",
            "q8": "Suggest ways to stand out for this specific role",
            "q9": "Implementing the STAR Framework, Pretend you are the candidate and put together a speech based on the resume and the job"
                  "description and requirements"
        }

        # 3. Run the Analysis
        st.markdown("---")
        st.subheader("📊 Analysis Results")

        # Create tabs for a cleaner UI
        tabs = st.tabs(["Fit Analysis", "Strengths & Weaknesses", "Cover Letter & Tips", "Interview Tips"])

        # We combine the Job Description as a context in the base query
        base_query = f"Based on this Job Description: \n\n {job_description} \n\n Answer this: "

        with tabs[0]:  # Q1, Q2, Q3
            st.markdown("### 🎯 Fit Assessment")
            logger.info("Entering Fit Assessment")
            logger.info("**Skills Check:** LLM Processing Q1")
            q1_ans = qa_chain.invoke({"query": f"{base_query}\n\n{questions['q1']}"})
            with st.expander("**Skills Check:**"):
                st.write(f"{q1_ans['result']}")

            logger.info("Fit Check:** LLM Processing Q2")
            q2_ans = qa_chain.invoke({"query": f"{base_query}\n\n{questions['q2']}"})
            with st.expander("**Fit Check:**" ):
                st.write(f"{q2_ans['result']}")

            logger.info("**Match Details:** LLM Processing Q3")
            q3_ans = qa_chain.invoke({"query": f"{base_query}\n\n{questions['q3']}"})
            with st.expander("**Match Details:** "):
                # Parse the number
                score = extract_match_score(q3_ans['result'])
                # Display the Progress Bar
                st.metric(label="Match Score", value=f"{score}%")
                st.progress(score / 100)
                if score < 50:
                    st.error("Low Match - Missing critical skills.")
                elif score < 80:
                    st.warning("Good Match - Some gaps identified.")
                else:
                    st.success("High Match - Strong candidate!")
                # -------------------------------
                st.divider()
                st.write(f"{q3_ans['result']}")

        with tabs[1]:  # Q4, Q5 , Q6
            st.markdown("### 📈 SWOT Analysis")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info("Strengths",icon="💪")
                ## LOGGING
                q4_ans = qa_chain.invoke({"query": f"{base_query}\n\n{questions['q4']}"})
                st.write(q4_ans['result'])
            with col2:
                st.warning("Opportunities", icon="🌤️")
                q5_ans = qa_chain.invoke({"query": f"{base_query}\n\n{questions['q5']}"})
                st.write(q5_ans['result'])
            with col3:
                st.error("Weaknesses",icon="🚨")
                q6_ans = qa_chain.invoke({"query": f"{base_query}\n\n{questions['q6']}"})
                st.write(q6_ans['result'])

        with tabs[2]:  # Q7, Q8
            st.markdown("### 📝 Application Kit")
            q7_ans = qa_chain.invoke({"query": f"{base_query}\n\n{questions['q7']}"})
            with st.expander("Draft Cover Letter"):
                st.write(q7_ans['result'])
            q8_ans = qa_chain.invoke({"query": f"{base_query}\n\n{questions['q8']}"})
            with st.expander("**How to Stand Out:**"):
                st.write(f"{q8_ans['result']}")
        with tabs[3]: # Q9
            st.markdown("### 💬 STAR Framework speech ")
            q9_ans = qa_chain.invoke({"query": f"{base_query}\n\n{questions['q9']}"})
            st.write(f"**STAR Framework**\n{q9_ans['result']}")

        st.success("✅ Data successfully Processed!")












