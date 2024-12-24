

import os
from dotenv import find_dotenv, load_dotenv
import streamlit as st
import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm import OpenAI
import re
import ast
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, create_sql_query_chain

# Set Streamlit page configuration (must be the first Streamlit command)
st.set_page_config(layout="wide", page_title="Database Administrator")

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

def create_dataframe(result, columns):
    json_data = []
    result = ast.literal_eval(result)
    for row in result:
        row_dict = dict(zip(columns, row))
        json_data.append(row_dict)
    return pd.DataFrame(json_data)

def extract_columns_from_query(query):
    query = ' '.join(query.split())
    select_part_match = re.search(r'select\s+(.+?)\s+from', query, re.IGNORECASE)
    if select_part_match:
        select_part = select_part_match.group(1)
        columns = []
        current_column = []
        in_quotes = False
        parenthesis_level = 0
        for char in select_part:
            if char == '"':
                in_quotes = not in_quotes
            if char == '(' and not in_quotes:
                parenthesis_level += 1
            if char == ')' and not in_quotes:
                parenthesis_level -= 1
            if char == ',' and not in_quotes and parenthesis_level == 0:
                columns.append(''.join(current_column).strip())
                current_column = []
            else:
                current_column.append(char)
        if current_column:
            columns.append(''.join(current_column).strip())
        processed_columns = []
        for col in columns:
            alias_match = re.search(r' as\s+"?([\w]+)"?', col, re.IGNORECASE)
            if alias_match:
                processed_columns.append(alias_match.group(1))
            elif '.' in col:
                processed_columns.append(col.split('.')[-1].strip(' "'))
            else:
                processed_columns.append(col.strip(' "'))
        return processed_columns
    return []

def load_db(db_name):
    return SQLDatabase.from_uri(f"sqlite:///{db_name}")

def chain_create(db):
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    return create_sql_query_chain(llm, db)

def sql_infer(db, chain, user_question):
    sql_query = chain.invoke({"question": user_question})
    result = db.run(sql_query)
    st.code(sql_query)
    columns = extract_columns_from_query(sql_query)
    df = create_dataframe(result, columns)
    with st.expander("Dataframe Preview"):
        st.write(df)
    answer_prompt = PromptTemplate.from_template(
        """Given the following user question, corresponding SQL query, and SQL result,
            generate a proper reply to give to user

            Question:{question}
            SQL Query:{query}
            SQL Result:{result}
            Answer:"""
    )
    llm_model = ChatOpenAI(model="gpt-3.5-turbo")
    llm = LLMChain(llm=llm_model, prompt=answer_prompt)
    ans = llm(inputs={"question": user_question, "query": sql_query, "result": result})
    return ans["text"], df

def main():
    st.title("SQL Chatbot")
    col1, col2 = st.columns([2, 3])

    # Initialize session state variables
    if "db" not in st.session_state:
        st.session_state.db = None
    if "chain" not in st.session_state:
        st.session_state.chain = None
    if "df" not in st.session_state:
        st.session_state.df = None
    if "query_result" not in st.session_state:
        st.session_state.query_result = None
    if "graph_response" not in st.session_state:
        st.session_state.graph_response = None

    with col1:
        file_name = st.text_input("Enter name of a DB file")
        if st.button("Load DB"):
            try:
                db = load_db(file_name)
                st.session_state.db = db
                st.session_state.chain = chain_create(db)
                st.success("Database loaded successfully!")
                st.subheader("Table Names")
                st.code(db.get_usable_table_names())
                st.subheader("Schemas")
                st.code(db.get_table_info())
            except Exception as e:
                st.error(f"Failed to load database: {e}")

    with col2:
        if st.session_state.db:
            question = st.text_input("Write a question about the data", key="question")
            if st.button("Get Answer"):
                try:
                    out, df = sql_infer(st.session_state.db, st.session_state.chain, question)
                    st.session_state.df = df
                    st.session_state.query_result = out
                    st.session_state.graph_response = None  # Clear previous graph response
                    st.subheader("Answer")
                    st.write(out)
                except Exception as e:
                    st.error(f"Error: {e}")

            # Show previous results if available
            if st.session_state.df is not None:
                st.subheader("Previous DataFrame")
                st.write(st.session_state.df)

            if st.session_state.query_result is not None:
                st.subheader("Previous Answer")
                st.write(st.session_state.query_result)

            graph_query = st.text_input("Ask to make a graph from the above dataframe")
            if st.button("Create Graph"):
                try:
                    if st.session_state.df is not None:
                        llm = OpenAI(api_token=os.getenv("OPENAI_API_KEY"))
                        df = SmartDataframe(st.session_state.df, config={
                            "llm": llm
                        })
                        response = df.chat(graph_query)
                        st.session_state.graph_response = response  # Save graph response
                        st.image(st.session_state.graph_response)
                    else:
                        st.warning("No DataFrame available to create a graph.")
                except Exception as e:
                    st.error(f"Graph creation failed: {e}")



if __name__ == "__main__":
    main()


