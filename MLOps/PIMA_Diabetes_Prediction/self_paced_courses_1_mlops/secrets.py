import os
from dotenv import load_dotenv

# Load the variables from .env into the OS environment
load_dotenv()

# Access the variables
HF_USERNAME = os.getenv("HF_USERNAME")
NGROK_AUTHTOKEN = os.getenv("NGROK_AUTHTOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_BASE= os.getenv("OPENAI_API_BASE")
OPENAI_API_KEY= os.getenv("OPENAI_API_KEY")
HF_TOKEN=os.getenv("HF_TOKEN")


