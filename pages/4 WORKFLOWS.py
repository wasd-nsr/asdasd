#!/usr/bin/env python
# -*- coding: utf-8 -*-
import streamlit as st
import utils as ut
from PIL import Image

st.title("Workflows Maketplace")
ut.set_navigation_menu()

image = Image.open('workflows.png')

st.image(image, caption='', width=1000)
