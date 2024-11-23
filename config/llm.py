import os
from langchain_groq import ChatGroq
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from langchain_aws import ChatBedrock
from langchain_openai import ChatOpenAI
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")
GROK_API_KEY = os.environ.get("GROK_API_KEY")

embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")
# llm = ChatGroq(temperature=0, groq_api_key=GROK_API_KEY, model_name="mixtral-8x7b-32768")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
# llm = ChatBedrock(model_id="anthropic.claude-3-haiku-20240307-v1:0", model_kwargs={"temperature": 0.1}, region_name="us-east-1", credentials_profile_name="prathamesh_bedrock_profile")