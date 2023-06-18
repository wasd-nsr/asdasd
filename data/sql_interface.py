from typing import Dict, List, Optional

from llama_index.readers.base import BaseReader
from llama_index.readers.schema.base import Document


# ref https://github.com/emptycrown/llama-hub/blob/main/llama_hub/mongo/base.py

class SimpleMongoReader(BaseReader):
    """Simple mongo reader.

    Concatenates each Mongo doc into Document used by LlamaIndex.

    Args:
        host (str): Mongo host.
        port (int): Mongo port.
        max_docs (int): Maximum number of documents to load.

    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        uri: Optional[str] = None,
        max_docs: int = 1000,
    ) -> None:
        """Initialize with parameters."""
        try:
            import pymongo  # noqa: F401
            from pymongo import MongoClient  # noqa: F401
        except ImportError:
            raise ImportError(
                "`pymongo` package not found, please run `pip install pymongo`"
            )
        if uri:
            if uri is None:
                raise ValueError("Either `host` and `port` or `uri` must be provided.")
            self.client: MongoClient = MongoClient(uri)
        else:
            if host is None or port is None:
                raise ValueError("Either `host` and `port` or `uri` must be provided.")
            self.client = MongoClient(host, port)
        self.max_docs = max_docs

    def load_data(
        self, db_name: str, collection_name: str, query_dict: Optional[Dict] = None
    ) -> List[Document]:
        """Load data from the input directory.

        Args:
            db_name (str): name of the database.
            collection_name (str): name of the collection.
            query_dict (Optional[Dict]): query to filter documents.
                Defaults to None

        Returns:
            List[Document]: A list of documents.

        """
        documents = []
        extra_info={'file_name': db_name+":"+collection_name}

        db = self.client[db_name]
        if query_dict is None:
            cursor = db[collection_name].find()
        else:
            cursor = db[collection_name].find(query_dict)


        # check for specific key
        # must be rewrite according to the Data structure
        for item in cursor:

            # if "text" not in item:
            #     raise ValueError("`text` field not found in Mongo document.")
            # documents.append(Document(item["text"]))

            #documents.append(Document(item["summary"], extra_info=extra_info))

            txt = ""
            for k,v in item.items():
              if not isinstance(v,str):
                v = str(v)
              txt += k + " : " + v + "\n"

            documents.append(Document(txt, extra_info=extra_info))

        return documents

def db_interface(uri, db_name, collection_name):

  DBReader = SimpleMongoReader(uri=uri)
  documents = DBReader.load_data(db_name, collection_name)

  return documents

if __name__ == '__main__':
  
  # create mongodb atlas and setup user access
  uri = "mongodb+srv://reader:1qoZtQZYveSjMEGY@cluster0.dfpvfxo.mongodb.net/?retryWrites=true&w=majority"
  db_name = "sample_airbnb"
  collection_name = "listingsAndReviews"

  print(db_interface(uri, db_name, collection_name)[0])

