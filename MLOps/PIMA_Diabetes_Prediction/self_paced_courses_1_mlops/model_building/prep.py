# for data manipulation
import pandas as pd
# for creating a folder
# for data preprocessing and pipeline creation
from sklearn.model_selection import train_test_split
# for converting text data in to numerical representation
# for hugging face space authentication to upload files
from huggingface_hub import HfApi

from dotenv import load_dotenv
load_dotenv(dotenv_path="../.env")

import os

HF_USERNAME = os.getenv("HF_USERNAME")
HF_TOKEN = os.getenv("HF_TOKEN")

# Define constants for the dataset and output paths
api = HfApi(token=HF_TOKEN)
DATASET_PATH = f"hf://datasets/{HF_USERNAME}/PIMA-Diabetes-Prediction/pima.csv"   # enter the Hugging Face username here
df = pd.read_csv(DATASET_PATH)
print("Dataset loaded successfully.")

target_col = 'class'

# Split into X (features) and y (target)
X = df.drop(columns=[target_col])
y = df[target_col]

# Perform train-test split
Xtrain, Xtest, ytrain, ytest = train_test_split(
    X, y, test_size=0.2, random_state=42
)

Xtrain.to_csv("Xtrain.csv",index=False)
Xtest.to_csv("Xtest.csv",index=False)
ytrain.to_csv("ytrain.csv",index=False)
ytest.to_csv("ytest.csv",index=False)


files = ["Xtrain.csv","Xtest.csv","ytrain.csv","ytest.csv"]

for file_path in files:
    api.upload_file(
        path_or_fileobj=file_path,
        path_in_repo=file_path.split("/")[-1],  # just the filename
        repo_id=f"{HF_USERNAME}/PIMA-Diabetes-Prediction",  # enter the Hugging Face username here
        repo_type="dataset",
    )