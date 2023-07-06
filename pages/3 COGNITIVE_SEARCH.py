import streamlit as st
import base64
import utils as ut
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space

from api.vector_v2 import configure_api,query_vector
from data.reports_interface import document_interface

from db_utils import *


def get_text():
    input_text = st.text_input(
        "prompt", "", placeholder="ASK A QUESTION",
        key="input", label_visibility='collapsed')
    return input_text

# def print_result(result):
#   output_text = f"""### Answer: 
#   {result['answer']}
  
#   ### Sources: 
#   {result['sources']}
  
#   ### All relevant sources:
#   {' '.join(list(set([doc.metadata['source'] for doc in result['source_documents']])))}
#   """
#   print(output_text)
#   return output_text


def print_result(result):
    
    source = "\n\nSources:\n"+result['sources'] if result['sources'] is not None else ""
    
    if result['source_documents'] is not None:
        all_sources = ' '.join(list(set([doc.metadata['source'] for doc in result['source_documents']])))
        other_sources = "\n\nAll relevant sources:\n"+all_sources
    else:
        other_sources = ""    
    
    output_text = f"""{result['answer']}{source}{other_sources}"""
    print(output_text)
    return output_text

# Response output
# Function for taking user prompt as input followed by producing AI generated responses
def generate_response(prompt):
    response = query_vector(prompt) #-> {'question':,'answer':,'sources':,}
    print(response)
    response = print_result(response)
    return response


def update_chat(prompt, response, idx):
    st.session_state['user']['chat_history'][idx]['user'].append(prompt)
    st.session_state['user']['chat_history'][idx]['assistant'].append(response)
    db_update_chat()
    

def new_chat():
    st.session_state['user']['chat_history'].append(
        {
            'user':[],
            'assistant':[],
        }
    )

def button_clicked(i):
    
    if i == "new":
        st.session_state['new_chat_flag'] = True
    else:
        st.session_state['current_chat'] = i
        st.session_state['new_chat_flag'] = False

# {
# 'user':[],
# 'assistant':[]
#     },

# st.set_page_config(layout="wide")
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
if 'current_chat' not in st.session_state:
    st.session_state['current_chat'] = None if not st.session_state['user']['chat_history'] else len(st.session_state['user']['chat_history'])-1

if 'new_chat_flag' not in st.session_state:
    st.session_state['new_chat_flag'] = False


col1, col2 = st.columns([2, 8])

with col1:
    #max len 16
    #disable = True if not st.session_state['user']['chat_history'][-1]['user'] else False
    btn_type = "primary" if st.session_state['new_chat_flag'] else "secondary"
    st.button('New Chat', key="new", type=btn_type, disabled = False,
              on_click=button_clicked, args=("new",), use_container_width=True)

    
    if st.session_state['user']['chat_history']:
        chats = st.session_state['user']['chat_history']
        # print("chats :",chats)
        for i in range(len(chats)-1, -1, -1):
            
            btn_type, btn_key = "secondary", None
            if i == st.session_state['current_chat'] and not st.session_state['new_chat_flag']:
                btn_type = "primary" 
                btn_key = "primary"
            
            if chats[i]["user"]:
                st.button(chats[i]["user"][0][:15],
                          type= btn_type,
                          key = None,
                          on_click=button_clicked, 
                          args=(i,), use_container_width=True)

    
    
with col2:
    # Layout of input/response containers
    input_container = st.container()
    # colored_header(label='', description='', color_name='blue-30')
    response_container = st.container()
    
    ## Applying the user input box
    with input_container:
        user_input = get_text()

    ## Conditional display of AI generated responses as a function of user provided prompts
    with response_container:
        
        if user_input:
            # response = ['Hi!'] #generate_response(user_input)
            response = generate_response(user_input)
            
            if st.session_state['current_chat'] is None or st.session_state['new_chat_flag']:
                new_chat()
                idx = len(st.session_state['user']['chat_history'])-1
                update_chat(user_input, response, idx)
                st.session_state['current_chat'] = idx
            
            else:
                idx = st.session_state['current_chat']
                update_chat(user_input, response, idx)
            
            st.session_state['new_chat_flag'] = False
                
        if st.session_state['user']['chat_history'] and not st.session_state['new_chat_flag']:
            
            prompts = st.session_state['user']['chat_history'][st.session_state['current_chat']]['user']
            responses = st.session_state['user']['chat_history'][st.session_state['current_chat']]['assistant']
            
            for i in range(len(prompts)-1, -1, -1):
                message(prompts[i], is_user=True, key=str(i) + '_user')
                message(responses[i], key=str(i))
                
        
            
        
        
   
