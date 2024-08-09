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
        file_paths = [os.path.join(temp_dir, file) for file in zip_ref.namelist()]
    return file_paths, temp_dir

# Function to aggregate all files content
def aggregate_code(file_paths):
    aggregated_code = ""
    for file_path in file_paths:
        with open(file_path, 'r') as file:
            file_content = file.read()
            aggregated_code += f"# File: {file_path}\n{file_content}\n\n"
    return aggregated_code

# Function to send aggregated code to OpenAI API and get transformed content
def process_with_openai(aggregated_code, api_key):
    api_endpoint = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
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
    data = {
        "model": "gpt-4",
        "messages": [{"role": "system", "content": prompt}],
        "max_tokens": 4096
    }
    response = requests.post(api_endpoint, json=data, headers=headers)
    response_json = response.json()
    return response_json['choices'][0]['message']['content']
