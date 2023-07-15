import streamlit as st
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
import pinecone
from langchain.vectorstores import Pinecone
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain

from db_utils import *

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from tqdm.auto import tqdm
from uuid import uuid4
from dotenv import load_dotenv
import os

from glob import glob
import numpy as np
import time


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

VECTOR_INDEX = 'kinatu'

def create_vector(doc):
    
    tokenizer = tiktoken.get_encoding('p50k_base')
    index = pinecone.Index(VECTOR_INDEX)
    
    def tiktoken_len(text):
        tokens = tokenizer.encode(
            text,
            disallowed_special=()
        )
        return len(tokens)
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=20,
        length_function=tiktoken_len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    embedding_model = OpenAIEmbeddings()
    batch_limit = 100

    texts = []
    metadatas = []

    for i, record in enumerate(tqdm(doc)):
        # first get metadata fields for this record
        metadata = {
            'source': record.extra_info["file_name"]
        }
        # now we create chunks from the record text
        record_texts = text_splitter.split_text(record.text)
        # create individual metadata dicts for each chunk
        record_metadatas = [{
            "chunk": j, "text": text, **metadata
        } for j, text in enumerate(record_texts)]
        # append these to current batches
        texts.extend(record_texts)
        metadatas.extend(record_metadatas)
        # if we have reached the batch_limit we can add texts
        if len(texts) >= batch_limit:
            ids = [record.extra_info["file_name"] + f"_{i}" for i in range(len(texts))]
            embeds = embedding_model.embed_documents(texts)
            index.upsert(vectors=zip(ids, embeds, metadatas))
            texts = []
            metadatas = []

    ids = [record.extra_info["file_name"] + f"_{i}" for i in range(len(texts))]
    embeds = embedding_model.embed_documents(texts)
    index.upsert(vectors=zip(ids, embeds, metadatas))


def create_vector2(docs):
    
    tokenizer = tiktoken.get_encoding('p50k_base')
    
    def tiktoken_len(text):
        tokens = tokenizer.encode(
            text,
            disallowed_special=()
        )
        return len(tokens)
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=20,
        length_function=tiktoken_len,
        separators=["\n\n", "\n", " ", ""]
    )

    embedding_model = OpenAIEmbeddings()

    for i, doc in enumerate(tqdm(docs)):
        splitted_doc = text_splitter.split_documents(doc)
        Pinecone.from_documents(splitted_doc, embedding_model, index_name=VECTOR_INDEX)




def query_vector2(query):
    text_field = "text"

    # switch back to normal index for langchain
    index = pinecone.Index(VECTOR_INDEX)
    embedding_model = OpenAIEmbeddings()

    vectorstore = Pinecone(
        index, embedding_model.embed_query, text_field
    )

    # completion llm
    llm = ChatOpenAI(
        model_name='gpt-3.5-turbo',
        temperature=0.0
    )
    
    
    system_template="""Use the following pieces of context to answer the users question.
    Take note of the sources and include them in the answer in the format: "SOURCES: source1 source2", 
    use "SOURCES" in capital letters regardless of the number of sources.
    If you don't know the answer, just say that "I don't know", don't try to make up an answer.
    ----------------
    {summaries}"""
    messages = [
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template("{question}")
    ]
    prompt = ChatPromptTemplate.from_messages(messages)

    
    chain_type_kwargs = {"prompt": prompt}
    
    qa_with_sources = RetrievalQAWithSourcesChain.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(),
        return_source_documents=True,
        chain_type_kwargs=chain_type_kwargs
    )

    response = qa_with_sources(query)

    return response



def query_vector(query):
    
    db = st.session_state['db']
    col = db['files_info']

    embedding_model = OpenAIEmbeddings()
    index = Pinecone.from_existing_index(VECTOR_INDEX,embedding_model)

    #model_name = "gpt-3.5-turbo"
    model_name = "gpt-4"
    llm = ChatOpenAI(model_name=model_name, temperature = 0)
    chain = load_qa_chain(llm, chain_type="stuff")

    similar_docs = index.similarity_search(query, k=5)
    print("*"*10)
    print("similar_docs: ", len(similar_docs))

    df_filtered = filter_sources(col)
    accessible_files = list(df_filtered["File Name"])
    accessible_docs = [ doc for doc in similar_docs if os.path.basename(doc.metadata['source']) in accessible_files ]
    
    print("*"*10)
    print("accessible_docs: ", len(accessible_docs))
    
    if accessible_docs:
        answer = chain.run(input_documents=accessible_docs, question=query)

        
        response = {"answer":answer,
                    "sources":accessible_docs[0].metadata['source'],
                    "source_documents":accessible_docs,
                    }
        return response

    else:
        response = {"answer":"You do not have access to the documents or there are no answer to the question",
                    "sources":None,
                    "source_documents":None,
                    }
        return response
