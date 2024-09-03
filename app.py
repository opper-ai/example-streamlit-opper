# Streamlit app

import os
import streamlit as st
from opperai import Opper, fn
from opperai.types import Message
from typing import List
from collections import defaultdict
from opperai.types import DocumentIn
from pydantic import BaseModel


# We set a default model for this project
os.environ["OPPER_DEFAULT_MODEL"] = "openai/gpt-4o-mini"

# Initialize Opper
opper = Opper()

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Here we define the logic to crawl the Opper documentation
def crawl_opper_docs():
    """Crawl all pages on https://docs.opper.ai and return a list of page contents"""
    base_url = "https://docs.opper.ai"
    visited = set()
    to_visit = [base_url]
    page_contents = []

    while to_visit:
        url = to_visit.pop(0)
        if url in visited:
            continue

        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract page content
                content = soup.get_text(strip=True)
                page_contents.append({
                    'url': url,
                    'content': content
                })

                # Find all links on the page
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(base_url, href)
                    
                    # Only add URLs that are part of docs.opper.ai
                    if urlparse(full_url).netloc == 'docs.opper.ai':
                        to_visit.append(full_url)

                visited.add(url)
            else:
                print(f"Failed to fetch {url}: Status code {response.status_code}")
        except Exception as e:
            print(f"Error crawling {url}: {str(e)}")

    return page_contents

# Here query an index with a question or create the index if it doesnt exist
def get_knowledge(question: str) -> str:
    
    # We get the index if it exists, otherwise we create it
    index = opper.indexes.get(name="opper_documentation")
    
    if not index:

        # We crawl the documentation and create an index
        pages = crawl_opper_docs()

        # We create the index
        index = opper.indexes.create(
            name="opper_documentation", 
            )
        
        # We add the pages to the index
        for page in pages:
            index.add(
                DocumentIn(
                    key=page['url'],
                    content=page['content'],
                    metadata={
                        "url": page['url'],
                    },
                )
            )

    # We return the result of querying the index
    return index.query(question, k=3)

class Source(BaseModel):
    url: str
    relevant_content: str

# Function to determine if the question warrants knowledge retrieval
@fn()
def decide_retrieval(messages: List[Message]) -> bool:
    """ Decide if we should retrieve knowledge or not """

# Function to create a response to the user given knowledge
@fn()
def respond_to_user(messages: List[Message], knowledge: list[str]) -> str:
    """ Respond to the user using the knowledge provided. If you dont know just say so. """

# Function to check if the response contains code
@fn()
def has_code(text: str) -> bool:
    """Return True if text contains any code, else False"""

# Set up the Streamlit page
st.title("Chat with Opper")
st.write("Powered by Opper Docs, Indexes, Calls and Tracing")
st.divider()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [Message(role="assistant", content="Hi there, how can I help you?")]

# Display chat history
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg.role):
        st.write(msg.content)

# Handle user input
if prompt := st.chat_input(placeholder="Ask a question"):
    st.session_state.messages.append(Message(role="user", content=prompt))
    st.chat_message("user").write(prompt)

    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking"):
            

            if decide_retrieval(st.session_state.messages):
                # We get relevant knowledge from index
                knowledge = get_knowledge(prompt)
            else:
                knowledge = []
                
            # We create a response to the user
            response = respond_to_user(st.session_state.messages, knowledge)
            
            # We check if the response contains code
            if has_code(response):
                st.warning("Please note that the following content includes source code. Follow our internal guidelines before using it.")
            
            st.session_state.messages.append(Message(role="assistant", content=response))
            st.write(response)

            # Handle sources if available
            if knowledge:
                with st.expander("Sources"):
                    for source in knowledge:
                        url = source.metadata.get("url")
                        if url:
                            st.write(f"[{url}]({url})")