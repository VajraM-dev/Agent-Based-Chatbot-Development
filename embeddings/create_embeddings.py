# from chroma_connect import remote_db
from embeddings.chroma_connect import remote_db, CHROMA_DB_COLLECTION
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import Docx2txtLoader
import os
from langchain_chroma import Chroma
from config.llm import embedding_model
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore

index_name = os.environ["PINECONE_INDEX_NAME"] 
separators=[
        "\n\n",
        "\n",
        " ",
        ".",
        ",",
        "\u200b",  # Zero-width space
        "\uff0c",  # Fullwidth comma
        "\u3001",  # Ideographic comma
        "\uff0e",  # Fullwidth full stop
        "\u3002",  # Ideographic full stop
        "",
    ]

class doc_loader:
    def __init__(self, path):
        self.path = path

    def identify_file_type(self):
        extension = os.path.splitext(self.path)[1].lower()
        if extension == '.pdf':
            return "pdf"
        elif extension == '.docx':
            return "docx"
        else:
            return None

    def load_pdf(self):
        loader = PyMuPDFLoader(self.path)
        data = loader.load()

        return data

    def load_word_file(self):
        loader = Docx2txtLoader(self.path)
        data = loader.load()

        return data
    
    def create_splits(self, data):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
                                                    chunk_overlap=100,
                                                    separators=separators)
        texts = text_splitter.split_documents(data)

        return texts
    
    def create_embeddings(self):
        try:
            file_type = self.identify_file_type()
            if file_type == 'pdf':
                data = self.load_pdf()
            if file_type == 'docx':
                data = self.load_word_file()
            if file_type is None:
                return "Please input a valid file format. Accepted file formats are .pdf and .docx"
        except Exception as e:
            return {"message":"Error parsing and loading the documents.", "error_message": e}
        # print(data)
        try:
            splits = self.create_splits(data)
        except Exception as e:
            return {"message":"Error spliting the the documents.", "error_message": e}

        # print(splits)
        try:
            PineconeVectorStore.from_documents(splits, embedding_model, index_name=index_name)
            return {"message":"Document pushed to vectorstore successfully", "error_message": None}
        except Exception as e:
            return {"message":"Error uploading the documents to vectorstore.", "error_message": e}
        
   
