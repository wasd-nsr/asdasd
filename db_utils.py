#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymongo
from pymongo import MongoClient
import os
from  dotenv import load_dotenv

load_dotenv()



cluster = MongoClient("mongodb+srv://"+os.getenv("MONGO_USER")+":"+os.getenv("MONGO_PASS")+"@cluster-test.fndbj.mongodb.net/UserData?retryWrites=true&w=majority")
db = cluster["kinatu"]
collection = db["kinatu"]
collection.insert_one({"_id":0, "user_name":"Soumi"})
collection.insert_one({"_id":100, "user_name":"Ravi"})
