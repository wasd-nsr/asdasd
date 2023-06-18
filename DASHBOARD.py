import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import utils as ut
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space

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
