import os
from dotenv import load_dotenv

from agent_tools.bot_tools import retriever_tool, greeting_tool, contact_us, something_wrong, random_question
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from config.llm import llm
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from history_utils import create_session_id, clear_history
from langchain.agents import AgentExecutor, create_tool_calling_agent

load_dotenv()

LANGCHAIN_TRACING_V2=os.environ.get("LANGCHAIN_TRACING_V2")
LANGCHAIN_ENDPOINT=os.environ.get("LANGCHAIN_ENDPOINT")
LANGCHAIN_API_KEY=os.environ.get("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT=os.environ.get("LANGCHAIN_PROJECT")

MEMORY_KEY = os.environ.get("MEMORY_KEY")
REDIS_URL = os.environ.get("REDIS_URL")

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are very powerful chatbot. Your job is to answer user questions based on the tools available to you. 
            """,
        ),
        MessagesPlaceholder(variable_name=MEMORY_KEY),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

tools = [retriever_tool, greeting_tool, contact_us, something_wrong, random_question]

agent = create_tool_calling_agent(llm, tools, prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

chain_with_history = RunnableWithMessageHistory(
    agent_executor,
    lambda session_id: RedisChatMessageHistory(
        session_id, url=REDIS_URL,
    ),
    input_messages_key="input",
    history_messages_key=MEMORY_KEY,
)

def create_configurable() -> str:
    config = {"configurable": {"session_id": create_session_id()}}
    return config

def get_response(query, config):
    result = chain_with_history.invoke({"input": query}, config=config)["output"]
    return result

def api_clear_history(config):
    return clear_history(config["configurable"]["session_id"])

# config = {'configurable': {'session_id': 'b14c8f2e-9f32-4408-8f79-c149a38ded2c'}} #create_configurable()
# while True:
#     query = input("Query: ")
#     if query == "end":
#         api_clear_history(config)
#         break
#     print(get_response(query, config))
#     print("\n")