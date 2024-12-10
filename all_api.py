import os
import uvicorn
from fastapi import FastAPI, HTTPException, status, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Dict
from fastapi.responses import RedirectResponse
from agent_chain import create_configurable, api_clear_history, get_response
from embeddings.create_embeddings import doc_loader
from pathlib import Path
import shutil
from delete_index_contents import clear_records_from_index
import json
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from redis import asyncio as aioredis
from contextlib import asynccontextmanager

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(".env.dev"))
# -----------------------API Development--------------------------------------------------------------
# set API Header
API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

# set rate limit
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Redis connection
    redis_connection = await aioredis.from_url(
        os.environ["REDIS_URL"], encoding="utf-8", decode_responses=True
    )
    # Initialize FastAPILimiter
    await FastAPILimiter.init(redis_connection)
    try:
        yield  # Application startup complete
    finally:
        await redis_connection.aclose()   # Cleanup during shutdown

# initiate FastAPI
app = FastAPI(lifespan=lifespan)

# limit the CORS
origins = [
    "http://localhost",
    "http://localhost:8501",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_TOKEN = os.environ["FAST_API_SECRET_TOKEN"] 

# Function to authenticate token
async def authenticate_token(api_key: str = Depends(API_KEY_HEADER)):
    valid_tokens = [SECRET_TOKEN]
    if api_key not in valid_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

@app.get("/")
async def redirect_root_to_docs():
  return RedirectResponse("/docs")

# API to create session config, needed for redis & langchain chathistory maintainence
@app.get("/getSessionConfig", status_code = status.HTTP_200_OK, dependencies=[Depends(authenticate_token), Depends(RateLimiter(times=20, seconds=60))], summary="Get Session Config Dictionary", description="Returns a config dictionary consisting of session id. Use full for sending to get response from agent.")
async def get_session_id() -> Dict:
    try:
        return create_configurable()
    except Exception as e:
      print("Error: ", e)
      raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "error_message": "Error creating config for the session."
            }
        )
    
# API to create session config, needed for redis & langchain chathistory maintainence
@app.get("/deleteVectorstoreRecords", status_code = status.HTTP_200_OK, dependencies=[Depends(authenticate_token), Depends(RateLimiter(times=20, seconds=60))], summary="Clear vector store", description="Clears all the records from vector store.")
async def delete_vectorstore_records() -> Dict:
    response = clear_records_from_index()
    if response['error_message'] is None:
        return response
    else:
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "status": "error",
            "error_message": "Error deleting records from vector store.",
            "response_error_message": f"""{response['error']}"""
        }
    )

# API to clear any chat history.
class clearSessionParamBody(BaseModel):
  config: Dict

@app.post("/clear_session_history", status_code = status.HTTP_200_OK, dependencies=[Depends(authenticate_token), Depends(RateLimiter(times=5, seconds=60))], summary="Clear session history", description="Clears all the session history to free up the redis server.")
async def clear_session_history(params: clearSessionParamBody) -> Dict:
    try:
        result = api_clear_history(params.config)
        return {"result": result}
    except Exception as e:
      print("Error: ", e)
      raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "error_message": "Error deleting the session history."
            }
        )

# Main API to process the user query and answer it. 
class chainParamBody(BaseModel):
  query: str
  config: Dict

@app.post("/get_response", status_code = status.HTTP_200_OK, dependencies=[Depends(authenticate_token), Depends(RateLimiter(times=100, seconds=60))], summary="Agent Calling", description="Main function to chat with agent.")
async def api_get_response(params: chainParamBody) -> Dict:
    try:
        result = get_response(params.query, params.config)
        return {"result": result}
    except Exception as e:
      print("Error: ", e)
      raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "error_message": "There was an error fetching your answer. Looks like there is an error at the backend."
            }
        )

# API to upload documents
# Define the directory to store files
UPLOAD_DIR = Path(__file__).parent.resolve() / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)  # Ensure the directory exists

class metadataParam(BaseModel):
  metadata: Dict[str, str]

@app.post("/upload/", status_code = status.HTTP_200_OK, dependencies=[Depends(authenticate_token), Depends(RateLimiter(times=20, seconds=60))], summary="Upload Documents", description="Used to upload PDF and Word files.")
async def upload_file(metadata: str = Form(...), file: UploadFile = File(...)):
    metadata = json.loads(metadata)
    print(type(metadata))
    # Validate file type
    allowed_types = ["application/pdf", 
                     "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOCX are allowed.")
    
    # Construct a custom file path
    file_path = UPLOAD_DIR / file.filename

    # Save the file
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # return file_path
    embed_docs = doc_loader(path=str(file_path), metadata=dict(metadata))
    response = embed_docs.create_embeddings()
    if response['error_message'] is None:
        return response
    else:
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "status": "error",
            "error_message": "Error while uploading the document. Looks like this is an error related to embedding the file.",
            "response_error_message": response['error_message']
        }
    )

if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8012)