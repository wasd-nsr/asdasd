#!/usr/bin/env python
# -- coding: utf-8 --

from pymongo import MongoClient
import os
from dotenv import load_dotenv
import json 
import streamlit as st

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
