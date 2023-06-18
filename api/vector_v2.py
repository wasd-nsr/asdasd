import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
import pinecone
from langchain.vectorstores import Pinecone
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQAWithSourcesChain

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
        chunk_size=400,
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
            ids = [str(uuid4()) for _ in range(len(texts))]
            embeds = embedding_model.embed_documents(texts)
            index.upsert(vectors=zip(ids, embeds, metadatas))
            texts = []
            metadatas = []

    ids = [str(uuid4()) for _ in range(len(texts))]
    embeds = embedding_model.embed_documents(texts)
    index.upsert(vectors=zip(ids, embeds, metadatas))



def query_vector(query):
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
        temperature=0.1
    )

    qa_with_sources = RetrievalQAWithSourcesChain.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever()
    )

    response = qa_with_sources(query)
    
    return response