from huggingface_hub import HfApi
from dotenv import load_dotenv
load_dotenv(dotenv_path="../.env")
import os
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("hosting")

HF_USERNAME = os.getenv("HF_USERNAME")
HF_TOKEN = os.getenv("HF_TOKEN")
logger.info("Deploying System ..")

api = HfApi(token=HF_TOKEN)
api.upload_folder(
    folder_path="deployment",
    repo_id=f"{HF_USERNAME}/PIMA-Diabetes-Prediction",                                         # enter the Hugging Face username here
    repo_type="space",
    path_in_repo="",                          # optional: subfolder path inside the repo
)