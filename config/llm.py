import os
# from langchain_groq import ChatGroq
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(".env.dev"))

os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")
GROK_API_KEY = os.environ.get("GROK_API_KEY")

embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")
# llm = ChatGroq(temperature=0, groq_api_key=GROK_API_KEY, model_name="llama-3.1-70b-versatile")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
