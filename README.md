# Lecture "Structured Products in Python" from Paris-Dauphine University.
# Project goals
Pricing derivatives & Structured products in Python
# Setting up the project
Run the file following commands, it will install dependencies and create a virtual environment for the project :
In Windows :
```bat
python -m venv .venv
@REM Could also be python3 -m venv .venv 
.\.venv\Scripts\pip.exe install -r requirements.txt
```
In Linux/MacOS
```bash
python -m venv .venv 
# Could also be python3 -m venv .venv 
.\.venv\bin\pip install -r requirements.txt -U
```
All the code is in the `src` folder.
The project guidelines are in the `static` folder.

# Access API
The API is available here :
https://structured-pricing-api-dauphine.koyeb.app/docs

# Access App
The App is available here (it is directly connected to the API) :
https://sp-app-in-python.streamlit.app/

# Description 
The main part of the code (the API is available in src/main_backend.py). The whole project is dockerized in order to facilitate the deployment in the cloud.