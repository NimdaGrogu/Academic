# 1. Text Splitting
# (Remains largely the same, but often imported from langchain_text_splitters in newer docs)
import os

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
# Embeddings & Chat Model
# (Now live in the dedicated langchain_openai package)
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# Vector Store
# (Lives in langchain_community)
from langchain_community.vectorstores import FAISS

# Prompts
# (ChatPromptTemplate is preferred over PromptTemplate for Chat Models)
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
# 5. Chains
#from langchain_classic.chains import create_retrieval_chain
#from langchain_classic.chains.combine_documents import create_stuff_documents_chain
#from langchain_core.documents import Document

# Logging and OpenAI configuration
from dotenv import load_dotenv
import logging
from rich.logging import RichHandler

# Configure basic config with RichHandler
logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s", # Rich handles the timestamp and level separately
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger("rag")

# load the env variables
load_dotenv(dotenv_path=".env")


def get_rag_chain(resume_text):

    # 1. Split the text into chunks
    logger.info("Split text into chunks")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(resume_text)

    # 2. Create Embeddings & Vector Store
    # This turns text into vectors so we can search it
    # Initialize the OpenAI Embeddings model with API credentials
    logger.info("Create Embeddings & Vector Store")
    embeddings = OpenAIEmbeddings(
        openai_api_key=os.getenv("OPENAI_API_KEY"),  #  OpenAI API key for authentication
        openai_api_base=os.getenv("OPENAI_API_BASE")  # OpenAI API base URL endpoint
    )
    ## Check if the Vector Store exist
    # DB Persistence
    # Vector DB folder
    out_dir = 'vector_db'  # name of the vector database
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    db_index_file_name = "index"
    db_faiss_path = f"{out_dir}/{db_index_file_name}.faiss"
    if os.path.exists(db_faiss_path):
        logger.info("Existing vector store found. Loading...")
        # Load existing
        vectorstore_local = FAISS.load_local(
            folder_path=out_dir,
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )
    else:
        print("No vector store found. Creating new embeddings...")
        vector_store = FAISS.from_texts(chunks, embedding=embeddings)
        vector_store.save_local(folder_path=out_dir, index_name="index")
        logger.info("Vector store saved successfully.")
        logger.info("Loading New Vector Store ..")
        vectorstore_local = FAISS.load_local(
            folder_path=out_dir,
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )

    # 3. Setup the Retriever
    # We will retrieve the top 3 most relevant chunks of the resume
    retriever = vectorstore_local.as_retriever(search_type="similarity", search_kwargs={"k": 3})

    # 4. Define the Prompt
    # This tells the LLM how to behave
    prompt_template = """
    You are an expert IT Recruiter. 
    Analyse and Interpret the following pieces of context (Candidate Resume) and use it to answer the question based on the Job Description provided.

    Context (Resume): {context}

    Job Description: {question}
    
    Your task are the following:
    1- DO NOT ANSWER ANY QUESTION OUTSIDE THE Job Description and Candidate Resume if you encounter this situation
    reply "Sorry I can't help you with your query .."
    2- Fairly Analyze and Interpret the candidate resume based on the job description and provide a professional assessment.
    """

    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    # 5. Create the Chain
    llm = ChatOpenAI(model="gpt-4o", temperature=0)  # Use gpt-4 or gpt-3.5-turbo

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )

    return qa_chain