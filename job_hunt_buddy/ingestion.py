from langchain_community.document_loaders import WeatherDataLoader, WebBaseLoader
from typing import Optional
import streamlit as st
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("app")

# Function 1: Extract Text from Job Description URL
"""
Pending wrapper Funtion to validate and sanitize the input 
"""


def get_jd_from_url(url) -> Optional[str]:
    """

    :param url:
    :return:
    """
    try:
        logger.info(f"Loading URL .. {url}")
        loader = WebBaseLoader(url)
        docs = loader.load()
        # Conbine content from all pages found (maybe just one)
        return " ".join([d.page_content for d in docs])
    except Exception as e:
        st.error(f"Error fetching URL: {e}")
        return None


# Function 2: Extract Text from Uploaded PDF
def get_pdf_text(uploaded_file) -> Optional[str]:
    import pypdf
    try:
        # Read the PDF file directly from the stream
        logger.info(f"Reading PDF. {uploaded_file}")
        pdf_reader = pypdf.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None
