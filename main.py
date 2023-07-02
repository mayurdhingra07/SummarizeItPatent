import os
import re
import openai
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pdfkit
from streamlit.server.server import Server

@st.cache_data(max_entries=1, ttl=None)
def set_api_key(Api_key):
    openai.api_key = Api_key

# Logo of the company
st.image("https://raw.githubusercontent.com/mayurdhingra07/SummarizeItPatent/main/Logo_-_High_Quality-removebg-e1591864365270-300x50.png")

# Set the title in the middle of the page
st.title("AI Patent Summarizer")

# Sidebar form
with st.sidebar.form(key='api_key_form'):
    st.session_state['Api_key'] = st.text_input('Enter your OpenAI API key', value=st.session_state.get("Api_key", ""), type="password")
    submitted = st.form_submit_button('Submit')

    if submitted:
        if 'generation' in st.session_state:
            del st.session_state['generation']

if 'Api_key' in st.session_state and st.session_state['Api_key']:
    set_api_key(st.session_state['Api_key'])

# If the API key is entered, display the patent number input
if st.session_state.get("Api_key"):
    patent_number = st.text_input("Enter a patent number", value=st.session_state.get("patent_number", ""))
else:
    patent_number = None
    st.write("Please enter your OpenAI API key to continue.")

# If a patent number is entered, download the patent content
if patent_number:
    url = f"https://patents.google.com/patent/{patent_number}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the element with the patent content
    patent_content = soup.find_all('div', {'class': 'abstract'})

    # Convert the patent content to a PDF
    pdfkit.from_file(patent_content, "patent.pdf")

    # Open the PDF file
    with open("patent.pdf", "r") as f:
        document = f.read()

else:
    document = ""  # define document variable outside the if block

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

# If the API key is set and a file has been uploaded, generate the content
if st.session_state.get("Api_key") and patent_number:
    try:
        if 'generation' not in st.session_state:
            st.session_state['generation'] = generate_and_print(system_prompt, user_prompt)
    except openai.error.RateLimitError:
        st.error("You've hit the OpenAI API rate limit. Please wait for a moment and try again.")

# Display the content, if it has been generated
if 'generation' in st.session_state:
    st.write(st.session_state['generation'])
