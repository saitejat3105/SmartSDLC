# SmartSDLC
video demo link: https://drive.google.com/file/d/1_Qm1yXGGMfJJSAUVX6HtB-jAj93YpO_S/view?usp=drive_link


commands to execute 
open command prompt in terminal in vscode
open fastapi_app 
cd fastapi_app
python -m venv venv 
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload

open another command prompt to run streamlit 
cd streamlit_app
python -m venv venv 
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
