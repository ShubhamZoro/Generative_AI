import os
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain.chains import RetrievalQA
from pinecone import Pinecone
# Streamlit app title
st.title("Document-based QA System with Pinecone")



def get_pdf_text(pdf_docs):
    text = ""
    pdf_reader = PdfReader(pdf_docs)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to split text into chunks
def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

# Upload PDF file
with st.sidebar:
    st.header("setting")
    uploaded_file = st.file_uploader(
        "Upload your pdf",type=['pdf'])
# Pinecone index details
index_name = "chatwithpdf"



# If a PDF file is uploaded
if uploaded_file is not None:
    st.write("Processing the PDF file...")
    
    # Extract and display text
    pdf_text = get_pdf_text(uploaded_file)
    st.text_area("Extracted Text", pdf_text[:1000], height=300)  
    
    # Split into chunks
    text_chunks = get_text_chunks(pdf_text)
    
    
    # Create OpenAI embeddings
    openai_api_key = st.secrets['open_api_key']
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
    
    st.write("PDF text has been processed and stored in Pinecone.")

    # Query input
    query = st.text_input("Ask a question based on the document", "")
    
    # Query processing
    if query:
        # Use the retriever and language model to answer the question
        llm = ChatOpenAI(openai_api_key=openai_api_key)
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever()
        )
        response = qa.invoke(query)
        st.write(f"Answer: {response['result']}")

else:
    st.write("Please upload a PDF to get started.")
