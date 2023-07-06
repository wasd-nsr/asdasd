#!/usr/bin/env python
# -*- coding: utf-8 -*-
import streamlit as st
import pymongo
from pymongo import MongoClient
import os
from  dotenv import load_dotenv
import json 
from bson import ObjectId
import pandas as pd

load_dotenv()

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
    # collection = db["files_info"]
    return db
    

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
    
    user_group = st.session_state['user']['group']
    df = pd.DataFrame(new_file_info)
    
    # if admin, no need filter
    if "admin" in user_group:
        return df
    
    df = df.dropna()
    booll = [ True if set(d) & set(user_group) else False for d in df["Group Access"] ]
    filtered_df = df[booll]

    return filtered_df


def create_user(user_name: str,
                name: str,
                hashed_password,
                email: str,
                group: list,
                chat_hist = {'user':[],
                             'assistant':[]}
                ):
    
    
    """
    exp:
        from streamlit_authenticator import Authenticate,Hasher
        hashed_passwords = Hasher(['admin123']).generate()
        user = create_user('admin0','Admin0', hashed_passwords[0],'admin@kinatu.com',
                    ['admin'])
        x = collection.insert_one(user)
    
    """
    
    obj = {user_name:{
            'name': name,
            'password': hashed_password,
            'email': email,
            'group':group,
            'chat_history': chat_hist,
        }
           }
    return obj

def db_update_chat():
    user = st.session_state['user']
    myquery = { f"{st.session_state['username']}.name" : user['name']}
    newvalues = { "$set": { f"{st.session_state['username']}.chat_history": user['chat_history'] } }

    db = configure_mongo()
    col = db["users"]
    col.update_one(myquery, newvalues)
    print("chat_saved")