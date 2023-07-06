#!/usr/bin/env python
# -- coding: utf-8 --

from pymongo import MongoClient
from dotenv import load_dotenv
import streamlit as st




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
