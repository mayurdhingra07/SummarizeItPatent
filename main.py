import os
import re
import openai
import streamlit as st
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import CharacterTextSplitter
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential, # for exponential backoff
)  

os.environ["OPENAI_API_KEY"] = "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"

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def completion_with_backoff(**kwargs):
    return openai.ChatCompletion.create(**kwargs)

st.title("AI Patent Summarizer")

uploaded_file = st.file_uploader("Upload a patent PDF", type=["pdf"])

if uploaded_file is not None:
    with open("uploaded_patent.pdf", "wb") as f:
        f.write(uploaded_file.getvalue())

    loader = UnstructuredFileLoader("uploaded_patent.pdf", mode="elements")
    document = loader.load()

MODEL_NAME = "gpt-3.5-turbo-16k-0613"
system_prompt = "You are a helpful assistant."
user_prompt = """
Summarize this patent in 250 words max using these steps:
1. Explain the patent background, with a focus on the field of the invention and prior art issues addressed.
2. Explain claim 1 in simple language step by step, when you are explaining the patent claim,
also take relevant help from the patent description to explain the patent claim better.
The patent is: {}""".format(document)

def generate_and_print(system_prompt, user_prompt, n=1):
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    response = completion_with_backoff(
        model=MODEL_NAME,
        messages=messages,
    )
    return response.choices[0].message['content'] # return the generated content

generation = generate_and_print(system_prompt, user_prompt)
st.write(generation)

