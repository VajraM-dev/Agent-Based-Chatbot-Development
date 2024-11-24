import os
from dotenv import load_dotenv, find_dotenv
from pinecone.grpc import PineconeGRPC as Pinecone

load_dotenv(find_dotenv(".env.dev"))

pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

index = pc.Index(host=os.environ.get("PINECONE_HOST"))

def clear_records_from_index():
    try:
        index.delete(delete_all=True)
        return {"message": "Succefully deleted records from vector store.", "error_message": None}
    except Exception as e:
        return {'error_message': 'Error deleting records from pinecone index', "error": e}