#!/usr/bin/env python
# -- coding: utf-8 --

import streamlit as st
import pandas as pd
import utils as ut
from io import StringIO
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
from populate_vector import* 
from api.vector import configure_api 
import pinecone
from utils import *
from collections import OrderedDict
import os 
from datetime import datetime 
from dateutil import parser
import json

st.title("Enterprise Knowledge Base")
ut.set_navigation_menu()

PICONE_INDEX = "kinatu"
ROOT_FOLDER = os.path.dirname(__file__)

def configure_tab():
    st.set_page_config(
        page_title="Kinatu AI"
    )

def process_file(file_path):
    file_info = {}
    
    filesize = os.path.getsize(file_path) /1024
    filename,file_extension = os.path.splitext(file_path)
    modify_date = datetime.now().strftime("%m/%d/%Y, %H:%M:%S") 

    file_info["File Name"] = os.path.basename(filename)+file_extension
    file_info["File Extension"] = file_extension
    file_info["File Size"] = str(round(filesize,2))+" KB"
    file_info["Last Modify"] = modify_date
    file_info["Vector index"] = PICONE_INDEX
    return file_info


def re_draw_table(file_data):
    df = pd.DataFrame(file_data)
    df_filtered = df.drop(columns=['_id'])
    st.dataframe(df_filtered)
   
def save_file(file, save_directory,col):
    file_name = file.name
    file_extension = os.path.splitext(file_name)[1].lower()

    allowed_extensions = [".xlsx", ".doc", ".docx", ".pdf", ".mp4", ".m4a"]
    success = False
    if file_extension in allowed_extensions:
        save_path = os.path.join(save_directory, file_name)
        with open(save_path, "wb") as f:
            f.write(file.getbuffer())
        populate(save_path)
        file_info = process_file(save_path)
        st.success(f"Vector saved successfully into {PICONE_INDEX}")
        to_json = json.dumps(file_info)
        insert_new_file(col,file_info)
        success = True
    else:
        st.warning("File type not supported. Please upload a valid file.")
    return success
FIRST_LOAD = False

if __name__ == "__main__":
    col = configure_mongo()
    uploaded_file = st.file_uploader("Upload file", type=["xlsx", "doc", "docx", "pdf", "mp4", "m4a"])
     # Button to refresh the table
    
    
    new_file_info = query_mongo_collection(col)
    re_draw_table(new_file_info)

    if uploaded_file is not None:
        success = save_file(uploaded_file, ROOT_FOLDER,col)
        if success:
            new_file_info = query_mongo_collection(col)
            re_draw_table(new_file_info)
            success = False

