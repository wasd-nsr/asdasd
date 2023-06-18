#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from api.vector import configure_api,query_vector
from api.vector_v2 import configure_api,query_vector
from data.reports_interface import document_interface


if __name__ == "__main__":
    configure_api()
    # query_vector("kinatu","How old is Enlai? Also give me the source of information.")
    res = query_vector("Tell me about Reliable Background Screening")
    
    print(res)
    
