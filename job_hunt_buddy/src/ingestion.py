from langchain_community.document_loaders import WebBaseLoader
from typing import Optional
import streamlit as st
import logging

import logging
from rich.logging import RichHandler

# Configure basic config with RichHandler
logging.basicConfig(
    level=logging.WARNING,
    format="%(message)s", # Rich handles the timestamp and level separately
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger("ingestion")

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
def get_pdf_text_pypdf(uploaded_file, verbose=False) -> Optional[str]:
    import pypdf
    try:
        # Read the PDF file directly from the stream
        logger.info(f"Reading PDF. {uploaded_file}")
        pdf_reader = pypdf.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        if verbose:
            logger.info(f"Extracted Text\n\n {text}")
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None


def get_pdf_text_pdfplumber(uploaded_file, verbose=False)-> Optional[str]:
    import pdfplumber
    try:
        logger.info(f"Reading PDF. {uploaded_file}")
        with pdfplumber.open(uploaded_file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
            if verbose:
                logger.info(f"Extracted Text\n\n {text}")
            return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None



