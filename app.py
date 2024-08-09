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
def process_with_openai(aggregated_code, api_key, prompt):
    api_endpoint = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": aggregated_code}
        ],
        "max_tokens": 4096
    }
    response = requests.post(api_endpoint, json=data, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors
    response_json = response.json()
    return response_json['choices'][0]['message']['content']

# Function to create a sample API call text file
def create_sample_api_call():
    sample_call = """# Sample API Call

## Example Request

To test the API, you can use curl or Postman. Here is an example using curl:

```bash
curl -X GET http://127.0.0.1:5000/your-endpoint
Example Response
{
"message": "This is an example response."
}
Replace /your-endpoint with the actual endpoint path defined in your application.
"""
file_path = "SAMPLE_API_CALL.txt"
with open(file_path, 'w') as file:
file.write(sample_call)
return file_path
Streamlit UI
st.title("PyAPI Alchemist")
App description
st.markdown("""
Welcome to PyAPI Alchemist!
Transform your Python scripts into a fully functional Flask API with ease. PyAPI Alchemist is your magical tool for converting complex code into sleek, ready-to-deploy Flask applications.
How It Works:

Upload your zip file containing Python scripts.
Enter your OpenAI API key to initiate the transformation.
Watch as your code is magically converted into a Flask API.
Download your new API-ready application.

Unleash the power of your code with PyAPI Alchemist!
""")
API Key Input
api_key = st.text_input("Enter your OpenAI API Key", type="password")
File Upload
uploaded_file = st.file_uploader("Upload a zip file containing Python scripts", type="zip")
if uploaded_file is not None and api_key:
st.write("Processing uploaded zip file...")
Copy# Display loading animation
with st.spinner('Transforming and updating your application...'):
    try:
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
            "Please provide the complete code including the Flask app setup and routes."
        )
        transformed_code = process_with_openai(aggregated_code, api_key, prompt)
        
        # Process transformed code to fix any Flask-related issues
        fix_prompt = (
            "You are an expert Python developer with extensive experience in Flask. The following code is a "
            "Flask API application generated from multiple Python files. Review the code carefully and fix "
            "any issues related to Flask to ensure that the application works correctly and is free of errors.\n\n"
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
        
        # Create sample API call text file
        sample_file_path = create_sample_api_call()
        shutil.copy(sample_file_path, updated_temp_dir)
        
        # Zip updated files
        updated_zip_path = "updated_app.zip"
        with zipfile.ZipFile(updated_zip_path, 'w') as zip_ref:
            for root, _, files in os.walk(updated_temp_dir):
                for file in files:
                    zip_ref.write(os.path.join(root, file), file)

        st.success("Transformation and fixing complete. You can download your updated zip file now.")
        
        with open(updated_zip_path, "rb") as file:
            st.download_button(
                label="Download Updated Zip File",
                data=file,
                file_name="updated_app.zip",
                mime="application/zip"
            )

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    finally:
        # Clean up temporary directories and files
        shutil.rmtree(temp_dir, ignore_errors=True)
        shutil.rmtree(updated_temp_dir, ignore_errors=True)
        if os.path.exists(sample_file_path):
            os.remove(sample_file_path)
        if os.path.exists(updated_zip_path):
            os.remove(updated_zip_path)
else:
if not api_key:
st.warning("Please enter your OpenAI API Key.")
if not uploaded_file:
st.warning("Please upload a zip file containing Python scripts.")
