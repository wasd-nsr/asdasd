#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from data.reports_interface import document_interface
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.vectorstores import Pinecone
import pinecone
from dotenv import load_dotenv
from langchain import PromptTemplate

import json


def configure_api():
    load_dotenv()
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_KEY")
    os.environ["SERPAPI_API_KEY"] = os.getenv("SERPAPI_KEY")
    PICONE_AI_KEY = os.getenv("PICONE_KEY")
    PICONE_ENV = os.getenv("PICON_ENV")
    # init pinecone here
    pinecone.init(
            api_key = PICONE_AI_KEY,
            environment = PICONE_ENV
        )
           
def create_vector(documents,index_name):
    embedding_model = OpenAIEmbeddings()
    docseach = Pinecone.from_texts([str(d.page_content)+"[source:"+str(d.metadata)+"]" for d in documents],embedding_model,index_name = index_name)
    return docseach

def query_vector(index_name,query):
    
    embedding_model = OpenAIEmbeddings()
    llm = OpenAI(temperature = 0)
    chain = load_qa_chain(llm,chain_type = "refine")
    index_search = Pinecone.from_existing_index(index_name,embedding_model)

    
    docs = index_search.similarity_search(query)
    
    print(len(docs))
    print(docs)

    response = chain.run(input_documents = docs, question = query)
    
    print(response)

    return response
