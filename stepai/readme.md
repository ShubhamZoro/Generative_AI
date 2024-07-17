#  Question Answering System

This project is a combination of a web crawler and a question-answering system. The web crawler is designed to scrape web pages, extract and save textual data. The question-answering system leverages pre-trained language models to provide answers to queries based on the crawled data.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Setup](#setup)

## Features

- **Web Crawler**: Crawls web pages starting from a given URL, extracts links based on a keyword, and saves the text data.
- **Data Chunking**: Splits the extracted text into semantically similar chunks using Sentence Transformers.
- **Vector Database**: Stores the chunks in Milvus, a vector database for fast similarity search.
- **Hybrid Retrieval**: Combines BM25 and Dense Passage Retrieval (DPR) for efficient and accurate information retrieval.
- **Question Answering**: Uses a pre-trained model to provide answers to user queries based on the retrieved chunks.

## Requirements

- Python 3.6+
- `requests`
- `beautifulsoup4`
- `nltk`
- `sentence-transformers`
- `pymilvus`
- `rank-bm25`
- `transformers`
- `streamlit`
- `numpy`
- `grpcio`

## Setup

1. **Clone the repository**

    ```bash
    git clone https://github.com/ShubhamZoro/Generative_AI/tree/main/stepai
    ```
2 **Set up Milvus**

    Follow the [Milvus installation guide](https://milvus.io/docs/v2.0.x/install_standalone-docker.md) to install and run Milvus.

3. **Install the required packages**

4** Run File**

    run Crawler.py->merge.py->stepai.py
    ```






