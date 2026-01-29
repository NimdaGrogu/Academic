from huggingface_hub import hf_hub_download

import streamlit as st
import pandas as pd
import os
import joblib
import logging
from dotenv import load_dotenv
load_dotenv(dotenv_path="../.env")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("app")

HF_USERNAME = os.getenv("HF_USERNAME")
logger.info("HF_USERNAME present: %s", "yes" if HF_USERNAME else "no")
repo_id = f"{HF_USERNAME}/PIMA-Diabetes-Prediction"

# Download and load the model
model_path = hf_hub_download(repo_id=repo_id, filename="best_pima_diabetes_model_v1.joblib")                                       # enter the Hugging Face username here
model = joblib.load(model_path)

# Streamlit UI for Machine Failure Prediction
st.title("🧠PIMA Diabetes Prediction App 👩‍")
st.write("""
This application predicts the likelihood of a patient having diabetes based on their health attributes.
Please enter the sensor and configuration data below to get a prediction.
""")

# User inputs
preg = st.number_input("Number of Pregnancies", min_value=0, max_value=20, value=1)
plas = st.number_input("Plasma Glucose Concentration", min_value=0, max_value=300, value=120)
pres = st.number_input("Diastolic Blood Pressure (mm Hg)", min_value=0, max_value=200, value=70)
skin = st.number_input("Triceps Skinfold Thickness (mm)", min_value=0, max_value=100, value=20)
test = st.number_input("2-Hour Serum Insulin (mu U/ml)", min_value=0, max_value=900, value=80)
mass = st.number_input("Body Mass Index (BMI)", min_value=0.0, max_value=70.0, value=25.0, step=0.1)
pedi = st.number_input("Diabetes Pedigree Function", min_value=0.0, max_value=2.5, value=0.5, step=0.01)
age = st.number_input("Age", min_value=1, max_value=120, value=30)

# Assemble input into DataFrame
input_data = pd.DataFrame([{
    'preg': preg,
    'plas': plas,
    'pres': pres,
    'skin': skin,
    'test': test,
    'mass': mass,
    'pedi': pedi,
    'age': age
}])

# Prediction button
if st.button("Predict Diabetes"):
    prediction = model.predict(input_data)[0]
    result = "Diabetic" if prediction == 1 else "Non-Diabetic"
    st.subheader("Prediction Result:")
    st.success(f"The model predicts: **{result}**")

