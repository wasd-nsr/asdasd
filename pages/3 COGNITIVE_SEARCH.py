import streamlit as st
import base64
import utils as ut
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space

from api.vector_v2 import configure_api,query_vector
from data.reports_interface import document_interface


st.title("Cognitive Search")
ut.set_navigation_menu()

configure_api()
st.markdown(
    """
<style>
div[data-baseweb="base-input"] {
  background-color: rgba(254, 158, 76, 0.27);
}
</style>
""",
    unsafe_allow_html=True,
)

# st.set_page_config(page_title="HugChat - An LLM-powered Streamlit app")

# Generate empty lists for generated and past.
# generated stores AI generated responses
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
# past stores User's questions
if 'past' not in st.session_state:
    st.session_state['past'] = []

# Layout of input/response containers
input_container = st.container()
# colored_header(label='', description='', color_name='blue-30')
response_container = st.container()

# User input
# Function for taking user provided prompt as input


def get_text():
    input_text = st.text_input(
        "", "", placeholder="ASK A QUESTION", key="input")
    return input_text


# Response output
# Function for taking user prompt as input followed by producing AI generated responses
def generate_response(prompt):
    response = query_vector(prompt) #-> {'question':,'answer':,'sources':,}
    return response


## Applying the user input box
with input_container:
    user_input = get_text()

## Conditional display of AI generated responses as a function of user provided prompts
with response_container:
    if user_input:
        # response = ['Hi!'] #generate_response(user_input)
        response = generate_response(user_input)
        st.session_state.past.append(user_input)
        st.session_state.generated.append(response['answer'])
        
    if len(st.session_state['generated']):
        for i in range(len(st.session_state['generated'])-1, -1, -1):
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))
        
   
