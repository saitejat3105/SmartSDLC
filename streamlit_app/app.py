import streamlit as st
from watsonx_utils import query_watsonx

st.set_page_config(page_title="SmartSDLC", layout="wide")
st.title("SmartSDLC – Developer Assistant")

task = st.selectbox("Choose your task", [
    "Generate Code", "Fix Bugs", "Requirement to Code", "Generate Test Cases", "Chatbot"
])

user_input = st.text_area("Describe your requirement or question:")

if st.button("Generate"):
    if user_input.strip():
        full_prompt = user_input if task == "Chatbot" else f"{task}:\n{user_input}"
        with st.spinner("Calling Granite 3.3-2B Instruct..."):
            result = query_watsonx(full_prompt)
        st.code(result, language="python")
    else:
        st.warning("Please provide a prompt.")
