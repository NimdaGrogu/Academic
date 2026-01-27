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


api = HfApi(token=os.getenv("HF_TOKEN"))
api.upload_folder(
    folder_path="self_paced_courses_1_mlops/deployment",
    repo_id=f"{HF_USERNAME}/PIMA-Diabetes-Prediction",  # enter the Hugging Face username here
    repo_type = "space",
    path_in_repo = "",  # optional: subfolder path inside the repo
)



