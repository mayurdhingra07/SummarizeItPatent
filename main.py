import os
import re
import openai
import streamlit as st
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import CharacterTextSplitter
import PyPDF2
import fitz  # PyMuPDF

@st.cache_data(max_entries=1, ttl=None)
def set_api_key(Api_key):
    openai.api_key = Api_key

# Create a layout with 3 columns
col1, col2, col3 = st.columns([1,6,1])

# Place the text input in the left-most column
Api_key = col1.text_input('Enter your OpenAI API key', type="password")

if Api_key:
    set_api_key(Api_key)

# ... rest of your code ...


st.title("AI Patent Summarizer")

uploaded_file = st.file_uploader("Upload a patent PDF", type=["pdf"])

document = ""  # define document variable outside the if block

if uploaded_file is not None:
    # Save the uploaded file
    with open("uploaded_patent.pdf", "wb") as f:
        f.write(uploaded_file.getvalue())
        
    # Open the PDF file
    with fitz.open("uploaded_patent.pdf") as doc:
        # Iterate over the pages
        for page in doc:
            # Extract the text and append to the document
            document += page.get_text()

MODEL_NAME = "gpt-3.5-turbo-16k-0613"
system_prompt = "You are a helpful assistant."
user_prompt = """
Summarize this patent in 250 words max using these steps:
1. Explain the patent background, with a focus on the field of the invention and prior art issues addressed.
2. Explain claim 1 in simple language step by step, when you are explaining the patent claim,
also take relevant help from the patent description to explain the patent claim better.
The patent is: {}""".format(document)

def generate_and_print(system_prompt, user_prompt):
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    response = openai.ChatCompletion.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0,
    )

    return response.choices[0].message['content']  # return the generated content

# If the API key is set, generate the content
if Api_key and uploaded_file:
    try:
        if 'generation' not in st.session_state:
            st.session_state['generation'] = generate_and_print(system_prompt, user_prompt)
    except openai.error.RateLimitError:
        st.error("You've hit the OpenAI API rate limit. Please wait for a moment and try again.")

# Display the content, if it has been generated
if 'generation' in st.session_state:
    st.write(st.session_state['generation'])
