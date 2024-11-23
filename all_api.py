import os
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI, HTTPException, status, Depends, UploadFile, File
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Dict
from fastapi.responses import RedirectResponse
from agent_chain import create_configurable, api_clear_history, get_response
from embeddings.create_embeddings import doc_loader
from pathlib import Path
import shutil

load_dotenv()
# -----------------------API Development--------------------------------------------------------------

API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

app = FastAPI()

SECRET_TOKEN = os.environ["FAST_API_SECRET_TOKEN"] 

async def authenticate_token(api_key: str = Depends(API_KEY_HEADER)):
    # Replace this with your actual token validation logic
    valid_tokens = [SECRET_TOKEN]
    if api_key not in valid_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

@app.get("/")
async def redirect_root_to_docs():
  return RedirectResponse("/docs")

@app.get("/getSessionConfig", status_code = status.HTTP_200_OK, dependencies=[Depends(authenticate_token)], summary="Get Session Config Dictionary", description="Returns a config dictionary consisting of session id. Use full for sending to get response from agent.")
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


class clearSessionParamBody(BaseModel):
  config: Dict

@app.post("/clear_session_history", status_code = status.HTTP_200_OK, dependencies=[Depends(authenticate_token)], summary="Clear session history", description="Clears all the session history to free up the redis server.")
def clear_session_history(params: clearSessionParamBody) -> Dict:
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

class chainParamBody(BaseModel):
  query: str
  config: Dict

@app.post("/get_response", status_code = status.HTTP_200_OK, dependencies=[Depends(authenticate_token)], summary="Agent Calling", description="Main function to chat with agent.")
def api_get_response(params: chainParamBody) -> Dict:
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

# Define the directory to store files
UPLOAD_DIR = Path(__file__).parent.resolve() / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)  # Ensure the directory exists

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
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
    embed_docs = doc_loader(path=str(file_path))
    response = embed_docs.create_embeddings()
    if response['error_message'] is None:
        return response
    else:
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "status": "error",
            "error_message": "Error while uploading the document. Looks like this is an error related to embedding the file."
        }
    )

if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8012)