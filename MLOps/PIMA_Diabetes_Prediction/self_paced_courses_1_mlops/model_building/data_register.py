from huggingface_hub.utils import RepositoryNotFoundError
from huggingface_hub import HfApi, create_repo
from MLOps.PIMA_Diabetes_Prediction.self_paced_courses_1_mlops.secrets import HF_USERNAME, HF_TOKEN

hf_username = HF_USERNAME

repo_id = f"{hf_username}/PIMA-Diabetes-Prediction"                         # enter the Hugging Face username here
repo_type = "dataset"

# Initialize API client
api = HfApi(token=HF_TOKEN)

# Step 1: Check if the space exists
try:
    api.repo_info(repo_id=repo_id, repo_type=repo_type)
    print(f"Space '{repo_id}' already exists. Using it.")
except RepositoryNotFoundError:
    print(f"Space '{repo_id}' not found. Creating new space...")
    create_repo(repo_id=repo_id, repo_type=repo_type, private=False)
    print(f"Space '{repo_id}' created.")

api.upload_folder(
    folder_path="self_paced_courses_1_mlops/data",
    repo_id=repo_id,
    repo_type=repo_type,
)