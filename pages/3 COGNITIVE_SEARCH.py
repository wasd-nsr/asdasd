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
    
    output_text = f"""{result['answer']}\n{source}\n{other_sources}"""
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

def remove_chat(idx):
    st.session_state['user']['chat_history'].pop(idx)
    db_update_chat()

def button_clicked(i):
    
    if i == "new":
        st.session_state['new_chat_flag'] = True
    elif i == "del":
        remove_chat(st.session_state['current_chat'])
        st.session_state['current_chat'] = len(st.session_state['user']['chat_history'])-1
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
# st.markdown(
#     """
# <style>
# div[data-baseweb="base-input"] {
#   background-color: rgba(254, 158, 76, 0.27);
# }
# </style>
# """,
#     unsafe_allow_html=True,
# )

assistant_logo = """
                <style>
                .stChatMessage > img {
                    height: auto;
                    width: 2.5rem;
                    background-color: #ffdd008f;
                }
                </style>
                """



# Generate empty lists for generated and past.
# generated stores AI generated responses
if 'current_chat' not in st.session_state:
    st.session_state['current_chat'] = None if not st.session_state['user']['chat_history'] else len(st.session_state['user']['chat_history'])-1

if 'new_chat_flag' not in st.session_state:
    st.session_state['new_chat_flag'] = False


col1, col2 = st.columns([2, 8])

with st.sidebar:
    
    st.title("Chat History")
    #max len 16
    #disable = True if not st.session_state['user']['chat_history'][-1]['user'] else False
    btn_type = "primary" if st.session_state['new_chat_flag'] else "secondary"
    st.button('➕New Chat', key="new", type=btn_type, disabled = False,
              on_click=button_clicked, args=("new",), use_container_width=True)


    if st.session_state['user']['chat_history']:
        chats = st.session_state['user']['chat_history']
        # print("chats :",chats)
        for i in range(len(chats)-1, -1, -1):
            
            if chats[i]["user"]:
                
                btn_type, btn_key = "secondary", None
                if i == st.session_state['current_chat'] and not st.session_state['new_chat_flag']:
                    
                    col1, col2 = st.columns([9, 1])
                    
                    col1.button(chats[i]["user"][0][:15],
                            on_click=button_clicked, 
                            args=(i,), use_container_width=True)
                    col2.button("🗑️", on_click=button_clicked,args=("del",))
                    
                    st.markdown(
                            """
                        <style>
                        div[data-testid="stHorizontalBlock"] {
                            gap: unset;
                        }
                        div[data-testid="stHorizontalBlock"] button:first-child {
                            width: inherit;
                            background-color: tomato;
                        }
                        </style>
                        """,
                            unsafe_allow_html=True,
                        )
                
                else:
                    st.button(chats[i]["user"][0][:15],
                            on_click=button_clicked, 
                            args=(i,), use_container_width=True)
    


  
# Display chat messages from history on app rerun
if st.session_state['user']['chat_history'] and not st.session_state['new_chat_flag']:
    
    current_chat = st.session_state['user']['chat_history'][st.session_state['current_chat']]
    
    for i in range(len(current_chat['user'])):
        for role in ['user','assistant']:
            avatar = None if role == 'user' else "./assistant_logo.png"
            with st.chat_message(role, avatar=avatar):
                st.markdown(current_chat[role][i])
    
    st.markdown(assistant_logo,unsafe_allow_html=True)


# Accept user input
if prompt := st.chat_input("ASK A QUESTION"):
    
    response = generate_response(prompt)
            
    if st.session_state['current_chat'] is None or st.session_state['new_chat_flag']:
        new_chat()
        idx = len(st.session_state['user']['chat_history'])-1
        update_chat(prompt, response, idx)
        st.session_state['current_chat'] = idx
        st.session_state['new_chat_flag'] = False
        st.experimental_rerun()
    
    else:
        idx = st.session_state['current_chat']
        update_chat(prompt, response, idx)
    
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant", avatar="./assistant_logo.png"):
        st.markdown(assistant_logo,unsafe_allow_html=True)
        
        message_placeholder = st.empty()
        full_response = ""
        assistant_response = response
        # Simulate stream of response with milliseconds delay
        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    
    
    

    
        
    
    

