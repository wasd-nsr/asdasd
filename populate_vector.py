#!/usr/bin/env python
# -*- coding: utf-8 -*-


from api.vector_v2 import create_vector, configure_api
# from api.vector import create_vector
from data.reports_interface import document_interface
from data.video_interface import  video_audio_interface
import os
from glob import glob
import numpy as np
import time


VECTOR_INDEX = "kinatu"
DOCUMENTS = np.array(glob("./data/reports/*.*"))
VIDEOS = np.array(glob("./data/videos/*.mp4"))

FILES = np.concatenate((DOCUMENTS,VIDEOS))

def common_interface(doc):    
    print(f"Populating pinecone index with {os.path.basename(doc)}")
    if os.path.basename(doc)[-4:] == ".mp4" or os.path.basename(doc)[-4:] == ".mp4":
        return video_audio_interface(doc)
    else:
        return document_interface(doc)


if __name__ == "__main__":
    configure_api()
    vectors = []
    for F in FILES:
        print(F)
        document = common_interface(F)
        docsearch = create_vector(document)

# def common_interface(doc):    
#     print(f"Populating pinecone index with {os.path.basename(doc)}")
#     if os.path.basename(doc)[-4:] == ".mp4":
#         return video_audio_interface(doc)
#     else:
#         return document_interface(doc)

# def populate(docs):
#     document = common_interface(docs)
#     docsearch = create_vector(document)
#     return docsearch


# if __name__ == "__main__":
    
#     configure_api()
#     dir = "/home/nsrie/working/work3/Kinatu.ai/data/reports/"
#     for i in os.listdir(dir):
#         if i[-5:] != ".xlsx": continue
#         file_path = dir+i
#         print(file_path)
#         populate(file_path)
#         print("done")
    

        
def populate(docs):
    document = common_interface(docs)
    docsearch = create_vector(document)
    return docsearch


VECTOR_INDEX = "kinatu"
DOCUMENT = "data/reports/Equipment Purchase Agreement.pdf"


if __name__ == "__main__":
    configure_api()
    document = document_interface(DOCUMENT)
    docsearch = create_vector(document,VECTOR_INDEX)
