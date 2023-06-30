#!/usr/bin/env python
# -- coding: utf-8 --

from pymongo import MongoClient
import os
from dotenv import load_dotenv
import json 
import streamlit as st
import pandas as pd
from bson import ObjectId

class MongoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

def configure_mongo():
    load_dotenv()
    MONGO_USER = os.getenv("MONGO_USER")
    MONGO_PASS = os.getenv("MONGO_PASS")
    connection_string = f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}@cluster0.smd7qvr.mongodb.net/?retryWrites=true&w=majority"
            
    cluster = MongoClient(connection_string)
    #cluster = MongoClient(st.secrets["mongo"])
    db = cluster["kinatu"]
    collection = db["files_info"]
    return collection
    

def insert_new_file(collection,json_data):
    collection.insert_one(json_data)


def query_mongo_collection(collection):

    item = collection.find()
    # Converting to the JSON
    #json_data = json.dumps(list(item), cls=MongoEncoder)
    # Close the MongoDB connection
    return list(item)

def filter_sources(col):
    """
        filtering sources according to user access group
    """
    new_file_info = query_mongo_collection(col)
    for f in new_file_info:
        f.pop("_id")
        if "Vector index" in f.keys():
            f.pop("Vector index")
    
    user_group = st.session_state['usergroup']
    df = pd.DataFrame(new_file_info)
    
    # if admin, no need filter
    if "admin" in user_group:
        return df
    
    df = df.dropna()
    booll = [ True if set(d) & set(user_group) else False for d in df["Group Access"] ]
    filtered_df = df[booll]

    return filtered_df

def set_navigation_menu():
    st.sidebar.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url(https://www.medixbot.com/guru_fox_logo_120.png);
                background-repeat: no-repeat;
                padding-top: 40px;
                background-position: 80px 20px;
            }
            [data-testid="stSidebarNav"]::before {
                content: "GURUFOX AI";
                margin-left: 50px;
                margin-top: 20px;
                font-family: "Courier New";
                font-size: 30px;
                font-weight: bold;
                color: #737373;
                position: relative;
                top: 100px;
            }
         
        </style>
        """,
        unsafe_allow_html=True,
    )
