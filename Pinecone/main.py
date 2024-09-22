import os
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain.chains import RetrievalQA
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
api_key=st.secrets['openai_api_key']
def get_resposne(user_input):
    retriever_chain = get_context_retriever_chain(st.session_state.vector_store)
    conversation_rag_chain = get_conversational_rag_chain(retriever_chain)

    response = conversation_rag_chain.invoke({
        "chat_history": st.session_state.chat_history,
        "input": user_input
    })

    return response['answer']

def get_pdf_text(pdf_docs):
    text = ""

    pdf_reader = PdfReader(pdf_docs)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vectorstore_from_url(pdf_docs):
    #get the text document forms
    text=get_pdf_text(pdf_docs)
    text_chunks=get_text_chunks(text)

    openai_api_key = st.secrets['openai_api_key']
    embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)
    # Store in Pinecone vector store
    pinecone_key =st.secrets['pinecone_api_key']
    pc = Pinecone(api_key=pinecone_key)
    os.environ["PINECONE_API_KEY"] = pinecone_key
    vector_store = PineconeVectorStore.from_texts(
        texts=text_chunks,
        embedding=embedding,
        index_name=index_name
    )
    return vector_store

def get_context_retriever_chain(vector_store):
    llm = ChatOpenAI(openai_api_key=api_key)
    retriever = vector_store.as_retriever()
    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        ("user",
         "Given the above conversation, generate a search query to look up to get information relevant to the conversation")
    ])
    retriever_chain = create_history_aware_retriever(llm, retriever, prompt)
    return retriever_chain


def get_conversational_rag_chain(retriever_chain):
    llm = ChatOpenAI(openai_api_key=api_key)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer the user's questions based on the below context:\n\n{context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
    ])

    stuff_documents_chain = create_stuff_documents_chain(llm, prompt)

    return create_retrieval_chain(retriever_chain, stuff_documents_chain)
# app config

st.set_page_config(page_title="chat with pdf")
st.title("chat with pdf")

#sidebar
with st.sidebar:
    st.header("setting")
    pdf_docs = st.file_uploader(
        "Upload your pdf'",type=['pdf'])
if pdf_docs is None:
    st.info("Enter the location")
else:
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage(content="Hello, I am a bot. How can I help you?"),
        ]
    #create coversation chain
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = get_vectorstore_from_url(pdf_docs)
    retriever_chain=get_context_retriever_chain(st.session_state.vector_store)

    #user input
    user_query=st.chat_input("Type your message here--")
    if user_query:
        response=get_resposne(user_query)
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        st.session_state.chat_history.append(AIMessage(content=response))

    for message in st.session_state.chat_history:
        if isinstance(message,AIMessage):
            with st.chat_message("AI"):
                st.write(message.content)
        elif isinstance(message,HumanMessage):
            with st.chat_message("Human"):
                st.write(message.content)






