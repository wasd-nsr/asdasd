import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import utils as ut

import pickle
from pathlib import Path

import streamlit as st  # pip install streamlit
from streamlit_authenticator import Authenticate,Hasher  # pip install streamlit-authenticator
from api.vector_v2 import configure_api
from utils import *
#st.set_page_config(initial_sidebar_state="collapsed")




def dashboard():
    st.title("Dashboard")
    ut.set_navigation_menu()

    # Draw a title and some text to the app:
    '''
    This is some _markdown_.
    '''

    df = pd.DataFrame({'File name': ['Document 1', 'Document 2', 'Document 3', 'Document 4', 'Document 5', 'Document 6'],
                    'Size': ['23,455 KB', '54,450 KB', '76,455 KB', '23,455 KB', '23,654 KB', '23,455 KB'],
                    'Vectors': [3, 8, 7, 9, 5, 12],
                    })
    df  # 👈 Draw the dataframe

    x = 100
    'x', x  # 👈 Draw the string 'x' and then the value of x

    # Also works with most supported chart types

    arr = np.random.normal(1, 1, size=100)
    fig, ax = plt.subplots()
    ax.hist(arr, bins=40)

    fig  # 👈 Draw a Matplotlib chart



configure_api()

if 'mongo_col' not in st.session_state:
    st.session_state['mongo_col'] = configure_mongo()

hide_bar= """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] {
        visibility:hidden;
        width: 0px !important;
    }
    [data-testid="stSidebar"][aria-expanded="false"] {
        visibility:hidden;
        width: 0px !important;
    }
    
    [data-testid="collapsedControl"] {
        display: none
    }
    </style>
"""

hashed_passwords = Hasher(['abc', 'abc123',]).generate()

cred = {
    'usernames':{
        'ali':{
            'name': 'Ali Lazim',
            'password': hashed_passwords[0],
            'group':['cs', 'qa', 'dev']
        },
        'admin':{
            'name': 'ADMIN',
            'password': hashed_passwords[1],
            'group': ['admin', 'qa', 'cs', 'dev']
        },
    }
}

cookie_obj = {
    'expiry_days': 30,
    'key': 'random_signature_key', # Must be string
    'name': 'random_cookie_name',
}


# st.session_state['user'] = {'name':None,'status':None,'username':None}

if 'auth' not in st.session_state:
    st.session_state['auth'] = Authenticate(cred,cookie_obj)

authenticator = st.session_state['auth']
name, authentication_status, username = authenticator.login("Login", "main")



if authentication_status:
    dashboard()
    st.sidebar.title(f"Welcome {st.session_state['name']}")
    
    groups = ", ".join(st.session_state['usergroup']) if len(st.session_state['usergroup']) > 1 else st.session_state['usergroup']
    st.sidebar.text(f"group: {groups}")
    authenticator.logout("Logout", "sidebar")
    
elif authentication_status == False:
    st.error("Username/password is incorrect")
    st.markdown(hide_bar, unsafe_allow_html=True)

elif authentication_status == None:
    st.warning("Please enter your username and password")
    st.markdown(hide_bar, unsafe_allow_html=True)




