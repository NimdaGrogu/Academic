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

api = HfApi(token=os.getenv("HF_TOKEN"))

try:
    # 1 Check if the repo exist
    api.repo_info(repo_id=repo_id, repo_type=repo_type)
except RepositoryNotFoundError:
    logger.info(f"Repository does not exist, Creating one {repo_id}")
    create_repo(repo_id, repo_type=repo_type)

api.upload_folder(
    folder_path="deployment",
    repo_id=repo_id,  # enter the Hugging Face username here
    repo_type = repo_type,
    path_in_repo = "",  # optional: subfolder path inside the repo
)



