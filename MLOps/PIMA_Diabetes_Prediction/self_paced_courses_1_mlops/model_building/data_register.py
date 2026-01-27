from huggingface_hub.utils import RepositoryNotFoundError
from huggingface_hub import HfApi, create_repo
from dotenv import load_dotenv
import os
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("data_register")

# load local .env for local testing
load_dotenv(dotenv_path="../.env")

HF_TOKEN = os.getenv("HF_TOKEN")





# Step 1: Check if the space exists
try:
    HF_TOKEN = os.getenv("HF_TOKEN")
    logger.info("HF_TOKEN present: %s", "yes" if HF_TOKEN else "no")
    # Initialize API client
    api = HfApi(token=HF_TOKEN)

    HF_NAME = os.getenv("HF_USERNAME")
    logger.info("HF_USERNAME present: %s", "yes" if HF_NAME else "no")
    repo_id = f"{HF_NAME}/PIMA-Diabetes-Prediction"  # enter the Hugging Face username here
    repo_type = "dataset"
    api.repo_info(repo_id=repo_id, repo_type=repo_type)
    logger.info(f"Space '{repo_id}' already exists. Using it.")
except RepositoryNotFoundError:
    print(f"Space '{repo_id}' not found. Creating new space...")
    create_repo(repo_id=repo_id, repo_type=repo_type, private=False)
    print(f"Space '{repo_id}' created.")


