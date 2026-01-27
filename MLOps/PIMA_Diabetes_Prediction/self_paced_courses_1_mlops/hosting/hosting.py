from huggingface_hub import HfApi
import os
HF_USERNAME = os.getenv("HF_USERNAME")
HF_TOKEN = os.getenv("HF_TOKEN")

api = HfApi(token=HF_TOKEN)
api.upload_folder(
    folder_path="self_paced_courses_1_mlops/deployment",
    repo_id=f"{HF_USERNAME}/PIMA-Diabetes-Prediction",                                         # enter the Hugging Face username here
    repo_type="space",
    path_in_repo="",                          # optional: subfolder path inside the repo
)