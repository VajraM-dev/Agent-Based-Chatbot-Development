from langchain_core.tools import tool
from rag_chain.chain import rag_chain

@tool
def retriever_tool(query:str) -> str:
    """
    This is a retriever tool, when the user asks questions try to find the answers using this tool.
    Just return the text as is. Dont write 'Based on the information provided by the tool' or anything.
    """
    try:
        answer = rag_chain.invoke(query)
    except:
        answer = "There was a problem finding your answer please try again later."

    return answer

@tool
def greeting_tool():
    """
    Use this tool when the user greets you. 
    if someone says hi, hello, I need help, what can you help me with. This tool should be used. 
    But make sure you dont reply as it is to the user take the question of the user also in mind and answer according. 
    Otherwise it will become very generic answer. 

    Format the answer properly. Dont just write a big paragrapgh such that its easy for user to read. 
    """

    greet = """
    Hello! How may I help you?
    """
    return greet

@tool
def contact_us():
    """
    When the user want to know the contact information or want to reach out QuestionPro. Use this tool
    """

    phone_numbers = """
    United States of America: +1 (800) 531 0228
    Canada: +1 (647) 956-1242
    United Kingdom: +44 20 3650 3166
    Germany: +49 301 663 5782
    Japan: +81 3-6691-1050
    Australia: +61 2 8074 5080
    UAE: +971 529 852 540
    Fax: +1 (206) 260-3243
    """

    url = "https://www.questionpro.com/in/?"
    contact_details = f"""
    You can reach out to us at the following website: {url},
    To contact us directly you can call the following: {phone_numbers}
    """
    return contact_details

@tool
def something_wrong():
    """
    Use this tool when something goes wrong or you were not able to find the answer. 
    Or when the user asks anything random which is out of scope ie you dont have any tool to address to that question then use this tool. 
    Based on the scenario either tell them what information you can offer. 
    """

    return """Sorry, I am unable to answer this at the moment."""

@tool
def random_question():
    """
    If the user asks some random question that is not available in retriever_tool then use this tool
    """

    return """The question you have asked in not related to the context I have. Please ask questions related to:  """

@tool
def content_moderation():
    """
    You are a content moderation tool embedded within a chatbot. 
    Your task is to analyze user inputs to detect and handle inappropriate, harmful, or irrelevant content.

    """

    return "I cant get you the request information because: "