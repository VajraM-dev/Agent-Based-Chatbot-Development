from config.llm import embedding_model, llm
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_pinecone import PineconeVectorStore
from embeddings.create_embeddings import index_name

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

vector_store = PineconeVectorStore(index_name=index_name, embedding=embedding_model)

# retriever = MultiQueryRetriever.from_llm(
#     retriever=vector_store.as_retriever(search_kwargs={"k": 4}), llm=llm
# )

retriever=vector_store.as_retriever(search_kwargs={"k": 4})

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

