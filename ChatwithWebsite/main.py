# import streamlit as st
# from langchain_core.messages import AIMessage, HumanMessage
# from langchain_community.document_loaders import WebBaseLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.vectorstores import Chroma
# from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# from dotenv import load_dotenv
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain.chains import create_history_aware_retriever, create_retrieval_chain
# from langchain.chains.combine_documents import create_stuff_documents_chain
# api_key=st.secrets['api_key']
# def get_resposne(user_input):
#     retriever_chain = get_context_retriever_chain(st.session_state.vector_store)
#     conversation_rag_chain = get_conversational_rag_chain(retriever_chain)

#     response = conversation_rag_chain.invoke({
#         "chat_history": st.session_state.chat_history,
#         "input": user_input
#     })

#     return response['answer']

# def get_vectorstore_from_url(url):
#     #get the text document forms
#     loader=WebBaseLoader(url)
#     documents=loader.load()
#     text_splitter=RecursiveCharacterTextSplitter()
#     document_chunks=text_splitter.split_documents(documents)
#     #vector_store
#     vector_store=Chroma.from_documents(document_chunks,OpenAIEmbeddings(openai_api_key=api_key))
#     return vector_store

# def get_context_retriever_chain(vector_store):
#     llm = ChatOpenAI(openai_api_key=api_key)
#     retriever = vector_store.as_retriever()
#     prompt = ChatPromptTemplate.from_messages([
#         MessagesPlaceholder(variable_name="chat_history"),
#         ("user", "{input}"),
#         ("user",
#          "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation")
#     ])
#     retriever_chain = create_history_aware_retriever(llm, retriever, prompt)
#     return retriever_chain


# def get_conversational_rag_chain(retriever_chain):
#     llm = ChatOpenAI(openai_api_key=api_key)

#     prompt = ChatPromptTemplate.from_messages([
#         ("system", "Answer the user's questions based on the below context:\n\n{context}"),
#         MessagesPlaceholder(variable_name="chat_history"),
#         ("user", "{input}"),
#     ])

#     stuff_documents_chain = create_stuff_documents_chain(llm, prompt)

#     return create_retrieval_chain(retriever_chain, stuff_documents_chain)
# # app config

# st.set_page_config(page_title="chat with website")
# st.title("chat with website")

# #sidebar
# with st.sidebar:
#     st.header("setting")
#     website_url=st.text_input("website url")
# if website_url is None or website_url=="":
#     st.info("Enter the url")
# else:
#     if "chat_history" not in st.session_state:
#         st.session_state.chat_history = [
#             AIMessage(content="Hello, I am a bot. How can I help you?"),
#         ]
#     #create coversation chain
#     if "vector_store" not in st.session_state:
#         st.session_state.vector_store = get_vectorstore_from_url(website_url)
#     retriever_chain=get_context_retriever_chain(st.session_state.vector_store)

#     #user input
#     user_query=st.chat_input("Type your message here--")
#     if user_query:
#         response=get_resposne(user_query)
#         st.session_state.chat_history.append(HumanMessage(content=user_query))
#         st.session_state.chat_history.append(AIMessage(content=response))

#     for message in st.session_state.chat_history:
#         if isinstance(message,AIMessage):
#             with st.chat_message("AI"):
#                 st.write(message.content)
#         elif isinstance(message,HumanMessage):
#             with st.chat_message("Human"):
#                 st.write(message.content)

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.schema import Document
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import asyncio
import time
import re
import os

api_key = st.secrets['api_key']
os.system("playwright install")
class PlaywrightWebLoader:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive'
        }
    
    def clean_text(self, text):
        """Clean and normalize extracted text"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove common unwanted patterns
        unwanted_patterns = [
            r'Cookie.*?Accept',
            r'This website uses cookies',
            r'Accept.*?cookies',
            r'Privacy Policy.*?Terms'
        ]
        
        for pattern in unwanted_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def scrape_with_playwright(self, url):
        """Scrape website using Playwright"""
        try:
            with sync_playwright() as p:
                # Launch browser
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu'
                    ]
                )
                
                context = browser.new_context(
                    user_agent=self.headers['User-Agent'],
                    viewport={'width': 1920, 'height': 1080}
                )
                
                page = context.new_page()
                
                # Navigate to page
                response = page.goto(url, wait_until='networkidle', timeout=30000)
                
                if response.status >= 400:
                    raise Exception(f"HTTP {response.status}")
                
                # Wait for content to load
                page.wait_for_timeout(3000)
                
                # Handle cookie banners
                try:
                    cookie_selectors = [
                        'button:has-text("Accept")',
                        'button:has-text("OK")',
                        'button:has-text("Got it")',
                        '[id*="cookie"] button',
                        '[class*="cookie"] button'
                    ]
                    
                    for selector in cookie_selectors:
                        try:
                            page.click(selector, timeout=2000)
                            page.wait_for_timeout(1000)
                            break
                        except:
                            continue
                except:
                    pass
                
                # Extract content using JavaScript
                content = page.evaluate("""
                    () => {
                        // Remove unwanted elements
                        const unwanted = document.querySelectorAll('script, style, nav, header, footer, aside, .advertisement, .ads, [class*="cookie"], [id*="cookie"]');
                        unwanted.forEach(el => el.remove());
                        
                        // Find main content
                        const main = document.querySelector('main, [role="main"], .main-content, .content, article') || document.body;
                        return main.innerText || main.textContent || '';
                    }
                """)
                
                browser.close()
                
                if content and len(content.strip()) > 100:
                    return self.clean_text(content)
                
                return None
                
        except Exception as e:
            st.error(f"Playwright scraping failed: {str(e)}")
            return None
    
    def scrape_with_requests(self, url):
        """Fallback method using WebBaseLoader"""
        try:
            loader = WebBaseLoader(url)
            loader.requests_kwargs = {
                'headers': self.headers,
                'timeout': 15
            }
            documents = loader.load()
            
            if documents and len(documents[0].page_content.strip()) > 100:
                return documents[0].page_content
            
            return None
            
        except Exception as e:
            st.warning(f"WebBaseLoader failed: {str(e)}")
            return None
    
    def load_url(self, url):
        """Main method to load URL content with fallbacks"""
        st.info(f"🌐 Loading content from: {url}")
        
        # Method 1: Try Playwright first (best for modern websites)
        with st.spinner("🎭 Using Playwright to load content..."):
            content = self.scrape_with_playwright(url)
            if content:
                st.success("✅ Successfully loaded with Playwright!")
                return [Document(page_content=content, metadata={"source": url, "method": "playwright"})]
        
        # Method 2: Fallback to WebBaseLoader
        with st.spinner("🔄 Trying WebBaseLoader as fallback..."):
            content = self.scrape_with_requests(url)
            if content:
                st.success("✅ Successfully loaded with WebBaseLoader!")
                return [Document(page_content=content, metadata={"source": url, "method": "webloader"})]
        
        # If both methods fail
        st.error("❌ Failed to load content from the website. Please check the URL or try a different website.")
        return []

def get_response(user_input):
    if "vector_store" not in st.session_state or st.session_state.vector_store is None:
        return "Please enter a valid website URL first."
    
    retriever_chain = get_context_retriever_chain(st.session_state.vector_store)
    conversation_rag_chain = get_conversational_rag_chain(retriever_chain)
    response = conversation_rag_chain.invoke({
        "chat_history": st.session_state.chat_history,
        "input": user_input
    })
    return response['answer']

def get_vectorstore_from_url(url):
    """Enhanced function using Playwright web loader"""
    # Use Playwright web loader
    loader = PlaywrightWebLoader()
    documents = loader.load_url(url)
    
    if not documents:
        return None
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=200,
        length_function=len
    )
    document_chunks = text_splitter.split_documents(documents)
    
    # Create vector store
    vector_store = Chroma.from_documents(
        document_chunks, 
        OpenAIEmbeddings(openai_api_key=api_key)
    )
    
    return vector_store

def get_context_retriever_chain(vector_store):
    llm = ChatOpenAI(openai_api_key=api_key)
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        ("user", "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation")
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

# App configuration
st.set_page_config(
    page_title="Enhanced Chat with Website",
    page_icon="🤖",
    layout="wide"
)

st.title("🚀 Enhanced Chat with Website")
st.markdown("*Powered by Playwright for better web scraping*")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    st.markdown("""
    **🎯 Enhanced Features:**
    - JavaScript-heavy websites ✅
    - Cookie banner handling ✅  
    - Better content extraction ✅
    - Fallback to WebBaseLoader ✅
    """)
    
    website_url = st.text_input(
        "🌐 Website URL", 
        placeholder="https://example.com"
    )
    
    # Add a button to reload website
    if st.button("🔄 Reload Website"):
        if "vector_store" in st.session_state:
            del st.session_state.vector_store
        if "chat_history" in st.session_state:
            st.session_state.chat_history = [
                AIMessage(content="Hello! I'm ready to help you with the new website content."),
            ]
        st.rerun()
    
    # Show current loaded website
    if "vector_store" in st.session_state and st.session_state.vector_store is not None:
        st.success("✅ Website loaded successfully!")
        st.info("💬 You can now ask questions about the website content.")

# Main content
if website_url is None or website_url == "":
    st.info("👆 Please enter a website URL in the sidebar to get started.")
else:
    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage(content="Hello! I'm your website assistant. I'll help you understand the content from the website you've provided."),
        ]
    
    # Create vector store from website
    if "vector_store" not in st.session_state:
        with st.spinner("🔍 Processing website content... This may take a moment."):
            vector_store = get_vectorstore_from_url(website_url)
            
            if vector_store:
                st.session_state.vector_store = vector_store
                st.success("🎉 Website content loaded successfully! You can now ask questions.")
            else:
                st.error("❌ Failed to load website content. Please check the URL and try again.")
                st.session_state.vector_store = None
    
    # Chat interface (only show if vector store is loaded)
    if "vector_store" in st.session_state and st.session_state.vector_store is not None:
        # User input
        user_query = st.chat_input("💬 Ask me anything about the website content...")
        
        if user_query:
            # Add user message to chat history
            st.session_state.chat_history.append(HumanMessage(content=user_query))
            
            # Get AI response
            with st.spinner("🤔 Thinking..."):
                response = get_response(user_query)
            
            # Add AI response to chat history
            st.session_state.chat_history.append(AIMessage(content=response))
        
        # Display chat history
        for message in st.session_state.chat_history:
            if isinstance(message, AIMessage):
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(message.content)
            elif isinstance(message, HumanMessage):
                with st.chat_message("user", avatar="👤"):
                    st.markdown(message.content)
    
    else:
        st.warning("⚠️ Website content not loaded. Please check the URL or try reloading.")





