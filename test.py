from dotenv import load_dotenv
import os
import google.generativeai as genai
import pandas as pd
from contextlib import redirect_stdout
from io import StringIO
import streamlit as st
import numpy as np

# Load Google API key from .env file
load_dotenv()
genai.configure(api_key=os.getenv("AIzaSyBhhuP8aHx9E-CpBuVVvd-GE88Zjn1iyd4"))

# Function to load Gemini Pro model
model = genai.GenerativeModel("gemini-pro")

def get_gemini(Question):
    # Assuming model.generate_content is a function that generates a response based on the input question
    response = model.generate_content(Question)
    return f"{response.text}"

st.title("Gemini Pro Generator")

# File Upload
uploaded_file = st.file_uploader("Upload CSV/Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.subheader("Top 10 Rows of the DataFrame:")
        st.write(df.head(10))

    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    # User Input and Question Generation
    variable = st.text_input("Enter the prompt:")
    if not variable:
        st.warning("Please enter a prompt.")
    else:
        question = f"Use the dataframe with name df with columns {df.columns} and generate python code for " + variable

        # Generate response using Gemini Pro
        try:
            response = get_gemini(question)
            start_index1 = response.find('#')
            start_index2 = response.rfind(')')
            exec_code = response[start_index1:start_index2 + 1]

            with StringIO() as output_buffer:
                with redirect_stdout(output_buffer):
                    exec(exec_code)
                captured_output = output_buffer.getvalue()
            st.subheader("Captured Output:")
            st.code(captured_output, language='python')

        except Exception as e:
            st.error(f"Error executing generated code: {e}")

else:
    st.info("Please upload a CSV or Excel file.")