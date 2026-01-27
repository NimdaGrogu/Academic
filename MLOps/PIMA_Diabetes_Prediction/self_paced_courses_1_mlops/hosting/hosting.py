from huggingface_hub import HfApi, create_repo
from dotenv import load_dotenv
from huggingface_hub.errors import RepositoryNotFoundError

load_dotenv(dotenv_path="../.env")
import os
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("hosting")

HF_TOKEN = os.getenv("HF_TOKEN")
logger.info("HF_TOKEN present: %s", "yes" if HF_TOKEN else "no")
HF_USERNAME = os.getenv("HF_USERNAME")
logger.info("HF_USERNAME present: %s", "yes" if HF_USERNAME else "no")
repo_id = f"{HF_USERNAME}/PIMA-Diabetes-Prediction"
repo_type = "space"

try:
    logger.info("Deploying System ..")
    api = HfApi(token=HF_TOKEN)
    # Step 1: Check if the space exists
    api.repo_info(repo_id=repo_id, repo_type=repo_type)
    logger.info(f"Space '{repo_id}' Exist::Deploying")
    repo_type="space"
    # Step 2: Upload the files to deploy
    logger.info(f"Uploading the data.")
    api.upload_folder(
        folder_path="/MLOps/PIMA_Diabetes_Prediction/self_paced_courses_1_mlops/deployment",
        repo_id=repo_id,  # enter the Hugging Face username here
        repo_type=repo_type,
        path_in_repo="",  # optional: subfolder path inside the repo
    )
except RepositoryNotFoundError:
    logger.info(f"Space '{repo_id}' not found. Creating new space...")
    create_repo(repo_id=repo_id, repo_type=repo_type, private=False, space_sdk="docker")
    logger.info(f"Space '{repo_id}' created.")
    api.upload_folder(
        folder_path="MLOps/PIMA_Diabetes_Prediction/self_paced_courses_1_mlops/deployment",
        repo_id=repo_id,  # enter the Hugging Face username here
        repo_type=repo_type,
        path_in_repo="",  # optional: subfolder path inside the repo
    )
