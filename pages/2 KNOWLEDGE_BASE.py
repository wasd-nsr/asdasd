#!/usr/bin/env python
# -- coding: utf-8 --

import streamlit as st
import pandas as pd
import utils as ut
from io import StringIO
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
from populate_vector import* 
# from api.vector import configure_api 
import pinecone
from utils import *
from db_utils import *
from collections import OrderedDict
import os 
from datetime import datetime 
from dateutil import parser
import json
from api.vector_v2 import configure_api

st.title("Enterprise Knowledge Base")
ut.set_navigation_menu()


PICONE_INDEX = "kinatu"
ROOT_FOLDER = os.path.dirname(__file__)
DATA_DIR = os.path.join(os.getcwd(),"data")


def configure_tab():
    st.set_page_config(
        page_title="Kinatu AI"
    )


def process_file(file_path, groups):
    file_info = {}
    
    filesize = os.path.getsize(file_path) /1024
    filename,file_extension = os.path.splitext(file_path)
    modify_date = datetime.now().strftime("%m/%d/%Y, %H:%M:%S") 

    file_info["File Name"] = os.path.basename(filename)+file_extension
    file_info["File Extension"] = file_extension
    file_info["File Size"] = str(round(filesize,2))+" KB"
    file_info["Group Access"] = groups
    file_info["Last Modify"] = modify_date
    file_info["Added by"] = st.session_state['user']['name']
    return file_info


def modify_access(col):
    """
        modify the right access to the knowledge source
    """
    
    myquery = { "File Name": "D1NAMO dataset.pdf" }
    newvalues = { "$set": { "Group Access": ["admin"],
                            "Added by": "Admin"} }
    col.update_one(myquery, newvalues)

def save_file(file, save_directory, groups, col):
    file_name = file.name
    file_extension = os.path.splitext(file_name)[1].lower()

    allowed_extensions = [".xlsx", ".doc", ".docx", ".pdf", ".mp4", ".m4a"]
    success = False
    if file_extension in allowed_extensions:
        save_path = os.path.join(save_directory,"reports", file_name)
        with open(save_path, "wb") as f:
            f.write(file.getbuffer())
        populate(save_path)
        file_info = process_file(save_path, groups)
        st.success(f"Vector saved successfully into {PICONE_INDEX}")
        to_json = json.dumps(file_info)
        insert_new_file(col,file_info)
        success = True
    else:
        st.warning("File type not supported. Please upload a valid file.")
    return success

FIRST_LOAD = False

if __name__ == "__main__":
    db = st.session_state['db']
    col = db['files_info']

    
    tab1, tab2, tab3 = st.tabs(["Available sources",
                                "Add new source",
                                "Accessibility"])
    
    
    with tab1:
        #st.subheader("Available sources")
        table = st.empty()
        df_filtered = filter_sources(col)
        table.dataframe(df_filtered, use_container_width=True)

    with tab2:
        #st.subheader("Add new source")
        
        with st.form("my-form", clear_on_submit=True):
            success = False
            groups_access = st.multiselect(
                    '1.Choose groups that have access',
                    st.session_state['user']['group'],
                    st.session_state['user']['group'])
            uploaded_file = st.file_uploader("2.Upload file", type=["xlsx", "doc", "docx", "pdf", "mp4", "m4a"])
            submitted = st.form_submit_button("➕Add")
            if uploaded_file is not None and submitted:
                success = save_file(uploaded_file, DATA_DIR, groups_access,col)

            if success:
                df_filtered = filter_sources(col)
                table.dataframe(df_filtered, use_container_width=True)
    
    
    
    st.markdown(
                    """
                <style>
                div[data-baseweb="tab-list"] button:last-child{
                    visibility: collapse;
                }
                </style>
                """,
                    unsafe_allow_html=True,
                )
    
    user_group = st.session_state['user']['group']
    if "admin" in user_group:
        st.markdown(
                    """
                <style>
                div[data-baseweb="tab-list"] button:last-child{
                    visibility: unset;
                }
                </style>
                """,
                    unsafe_allow_html=True,
                )
        with tab3:
            df_filtered = filter_sources(col)
            with st.form("accessibility-form", clear_on_submit=True):
                success = False
                
                files = st.multiselect(
                        '1.Choose file/files',
                        df_filtered["File Name"],
                        [])
                
                groups_access = st.multiselect(
                    '2.Choose groups that have access',
                    st.session_state['user']['group'],
                    st.session_state['user']['group'])
                
                
                
                submitted = st.form_submit_button("➕Add")
                if uploaded_file is not None and submitted:
                    success = save_file(uploaded_file, DATA_DIR, groups_access,col)

                if success:
                    df_filtered = filter_sources(col)
                    table.dataframe(df_filtered, use_container_width=True)