from dotenv import load_dotenv
import os
import chromadb

load_dotenv()
CHROMA_DB_HOST=str(os.environ.get('CHROMA_DB_HOST'))
CHROMA_DB_PORT=str(os.environ.get('CHROMA_DB_PORT'))
CHROMA_DB_COLLECTION=str(os.environ.get('CHROMA_DB_COLLECTION'))
remote_db = chromadb.HttpClient(host=CHROMA_DB_HOST, port=CHROMA_DB_PORT)

