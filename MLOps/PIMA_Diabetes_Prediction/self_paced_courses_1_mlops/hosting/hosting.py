from huggingface_hub import HfApi
from MLOps.PIMA_Diabetes_Prediction.self_paced_courses_1_mlops.secrets import HF_TOKEN, HF_USERNAME

api = HfApi(token=HF_TOKEN)
api.upload_folder(
    folder_path="self_paced_courses_1_mlops/deployment",
    repo_id=f"{HF_USERNAME}/PIMA-Diabetes-Prediction",                                         # enter the Hugging Face username here
    repo_type="space",
    path_in_repo="",                          # optional: subfolder path inside the repo
)