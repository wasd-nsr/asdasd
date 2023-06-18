import os
from pathlib import Path
from langchain.document_loaders import PyPDFLoader
from llama_index import download_loader


absolute_path = os.path.dirname(__file__)

def load_doc_with_langc(path):
    path = os.path.join(absolute_path,path)
    loader = PyPDFLoader(path)
    return loader.load_and_split()

def document_interface(file_path):
  """
    Extract text from documents
    Choose data loaders from llama hub base on file extension

    Returns:
          List[Document]: A list of documents.
                          Document.text
                          Document.extra_info
                          Document.embedding

  """

  loader_dict = {".pdf":"PDFReader",
                  ".csv":"PandasCSVReader",
                  ".xlsx":"PandasExcelReader",
                  ".docx":"DocxReader",
               }

  file_name, file_extension = os.path.splitext(file_path)
  extra_info={'file_name': file_name+file_extension}

  FileReader = download_loader(loader_dict[file_extension])
  loader = FileReader()
  documents = loader.load_data(file=Path(file_path), extra_info = extra_info)
  # documents = [d.to_langchain_format() for d in documents]

  return documents 

if __name__ =="__main__":
    print(document_interface("./reports/Background Check.xlsx"))

