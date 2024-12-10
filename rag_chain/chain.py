from config.llm import embedding_model, llm
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_pinecone import PineconeVectorStore
from embeddings.create_embeddings import index_name
from langchain.retrievers.multi_query import MultiQueryRetriever

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

vector_store = PineconeVectorStore(index_name=index_name, embedding=embedding_model)

# retriever = MultiQueryRetriever.from_llm(
#     retriever=vector_store.as_retriever(search_kwargs={"k": 4}), llm=llm
# )

retriever=vector_store.as_retriever(search_kwargs={"k": 8})

template = """ 
You are tasked with retreiving accurate data. Based on the context: {context} and the asked question: {question}, answer the question as accurately as possible.                 
"""

prompt = PromptTemplate(
                template=template,
                input_variables=["context", "question"],
            )

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)




# ---------------------new approach----------------------------

# # Step 1: Create a source-to-branch mapping
# source_to_branch = {
#     "C:\\Prathamesh\\question_pro_assignment\\uploads\\EmployeeHandbook.pdf": "Mumbai/Thane",
#     "C:\\Prathamesh\\question_pro_assignment\\uploads\\KLS_IndiaGujEmployeeHandbook_V11.pdf": "Jamnagar",
#     # Add other mappings as needed
# }

# # Step 2: Modify add_branch_context to integrate source-to-branch mapping directly
# def add_branch_context(inputs):
#     question = inputs["question"]
#     context = inputs["context"]
    
#     # Assuming source is available during chain initialization
#     source = "C:\\Prathamesh\\question_pro_assignment\\uploads\\EmployeeHandbook.pdf"  # Example source
#     branch_name = source_to_branch.get(source, "default")  # Map source to branch name
#     updated_context = f"{context} (Branch: {branch_name})"
    
#     return {"question": question, "context": updated_context}  # Update context with branch info

# # Step 3: Define the TransformChain
# transform_chain = TransformChain(
#     input_variables=["question", "context"],  # No 'source' here
#     output_variables=["question", "context"],  # Output the updated question and context
#     transform=add_branch_context
# )

# # Step 4: Define the RAG chain
# rag_chain = (
#     {"context": retriever, "question": RunnablePassthrough()}  # Exclude source
#     | transform_chain  # Add branch-specific context
#     | prompt  # Apply the prompt
#     | llm  # Query the LLM
#     | StrOutputParser()  # Parse the output
# )



