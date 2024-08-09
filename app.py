import streamlit as st
import zipfile
import os
import requests
import shutil
import time

# Function to handle file uploads and extraction
def handle_file_upload(uploaded_file):
    temp_dir = "temp_app"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
        file_paths = []
        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_paths.append(os.path.join(root, file))
    return file_paths, temp_dir

# Function to aggregate all files content
def aggregate_code(file_paths):
    aggregated_code = ""
    for file_path in file_paths:
        if os.path.isfile(file_path):  # Ensure we only process files
            with open(file_path, 'r') as file:
                file_content = file.read()
                aggregated_code += f"# File: {file_path}\n{file_content}\n\n"
    return aggregated_code

# Function to send aggregated code to OpenAI API and get transformed content
def process_with_openai(aggregated_code, api_key, prompt):
    api_endpoint = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o",
        "messages": [{"role": "system", "content": prompt}],
        "max_tokens": 4096
    }
    response = requests.post(api_endpoint, json=data, headers=headers)
    
    # Print the response for debugging purposes
    response_json = response.json()
    st.write("OpenAI API Response:", response_json)  # Debugging line
    
    if 'choices' not in response_json:
        st.error("Unexpected response format from OpenAI API.")
        return ""
    
    return response_json['choices'][0]['message']['content']

# Streamlit UI
st.title("PyAPI Alchemist")

# App description
st.markdown("""
### Welcome to PyAPI Alchemist!

Transform your Python scripts into a fully functional Flask API with ease. PyAPI Alchemist is your magical tool for converting complex code into sleek, ready-to-deploy Flask applications.

**How It Works:**
1. Upload your zip file containing Python scripts.
2. Enter your OpenAI API key to initiate the transformation.
3. Watch as your code is magically converted into a Flask API.
4. Download your new API-ready application.

Unleash the power of your code with PyAPI Alchemist!
""")

# API Key Input
api_key = st.text_input("Enter your OpenAI API Key", type="password")

# File Upload
uploaded_file = st.file_uploader("Upload a zip file containing Python scripts", type="zip")

if uploaded_file is not None and api_key:
    st.write("Processing uploaded zip file...")

    # Display loading animation
    with st.spinner('Transforming and updating your application...'):
        file_paths, temp_dir = handle_file_upload(uploaded_file)

        # Aggregate all code
        aggregated_code = aggregate_code(file_paths)
        
        # Process with OpenAI API to create initial Flask app
        prompt = (
            "You are given the combined code from multiple Python files of an existing application. "
            "Your task is to transform this code into a complete, functional Flask API application. "
            "The resulting code should include:\n"
            "1. A Flask app instance in `app.py`.\n"
            "2. Necessary imports for Flask and any other required libraries.\n"
            "3. Flask routes corresponding to the functionality described in the combined code.\n"
            "4. Error handling and configuration to ensure the Flask app runs correctly.\n\n"
            "Here is the combined code from the Python files:\n"
            f"{aggregated_code}\n"
            "Please provide the complete code including the Flask app setup and routes."
        )
        transformed_code = process_with_openai(aggregated_code, api_key, prompt)
        
        # Process transformed code to fix any Flask-related issues
        fix_prompt = (
            "You are an expert Python developer with extensive experience in Flask. The following code is a "
            "Flask API application generated from multiple Python files. Review the code carefully and fix "
            "any issues related to Flask to ensure that the application works correctly and is free of errors.\n\n"
            "Here is the code to review and fix:\n"
            f"{transformed_code}\n"
            "Please provide the corrected and complete Flask application code."
        )
        fixed_code = process_with_openai(transformed_code, api_key, fix_prompt)
        
        # Save fixed code to `app.py`
        updated_temp_dir = "updated_app"
        if not os.path.exists(updated_temp_dir):
            os.makedirs(updated_temp_dir)
        
        app_file_path = os.path.join(updated_temp_dir, "app.py")
        with open(app_file_path, 'w') as file:
            file.write(fixed_code)
        
        # Zip updated files
        updated_zip_path = "updated_app.zip"
        with zipfile.ZipFile(updated_zip_path, 'w') as zip_ref:
            for root, _, files in os.walk(updated_temp_dir):
                for file in files:
                    zip_ref.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), updated_temp_dir))

        st.success("Transformation and fixing complete. You can download your updated zip file now.")
        st.download_button("Download Updated Zip File", updated_zip_path, "application/zip")

        # Clean up temporary directories
        shutil.rmtree(temp_dir, ignore_errors=True)
        shutil.rmtree(updated_temp_dir, ignore_errors=True)

    time.sleep(1)  # Optional delay to let users see the success message
else:
    if not api_key:
        st.warning("Please enter your OpenAI API Key.")

