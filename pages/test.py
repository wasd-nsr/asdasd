import streamlit as st
import base64
import utils as ut
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space

from api.vector_v2 import configure_api,query_vector
from data.reports_interface import document_interface

from db_utils import *
import random
import time

st.title("Echo Bot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

url = "https://www.dropbox.com/scl/fi/vvog3zkjuapjolbm18jqn/Basics-and-use-of-continuous-glucose-monitoring-CGM-in-diabetes-therapy.pdf?rlkey=w0w5oq1jz6yz9ldt38q9gbd0i&dl=0"

#st.markdown("check out this [link](%s)" % url)


response = f"Echo: {url}"
# Display assistant response in chat message container
with st.chat_message("assistant"):
    st.markdown(response)
# Add assistant response to chat history
st.session_state.messages.append({"role": "assistant", "content": response})