# Context Search Tool for PDF Files
Enterprise self-hosted PDF vector search engine.

## Tech Stack to be used
- **Backend / API**: FastAPI
- **Background processing**: Celery workers (for heavy ingest)
- **Vector DB**: Qdrant
- **File storage** (binary PDFs, images): MinIO
- **Embedding model**: BGE (text embeddings)
- **PDF metadata & user data**: Postgres
- **Frontend / viewer**: React + pdf.js

## Goal
Build a self-hosted internal tool that lets users upload PDFs, performs semantic + lexical retrieval over text with OpenIE triple extraction for relation-aware queries, and returns results with highlighted spans and image matches. System must be persistent across restarts and user sessions (uploads remain available).

# Software Requirements
To develop an AI tool that:
- Accepts a phrase or sentence as input.
- Processes multiple PDF files as data sources.
- Finds the most semantically relevant content (even if paraphrased or analogous) across the documents.
- Provides the user with the name of the PDF and the corresponding page number or location where the relevant content is found.

## Key Features

### Input Format
- Text input: A phrase or sentence provided by the user for searching.

### Document Parsing
- The tool must process uploaded PDF files, extract their text content (page by page), and prepare the data for searching.

### Matching Mechanism
- The tool should use semantic similarity to capture broader meanings and not limit searches to exact matches.

### Output Format
The tool should return:
- The name of the PDF file.
- The page number(s) where the highly relevant text is located.
- Highlight the relevant text on the page, if possible.
- Rank the relevance of different matches using confidence scores.

## User Authentication
- User Accounts with secure login/logout. Users authenticate with email+password
- API should use JWT Token-Based Authentication

## Evaluation Criteria
- Test the tool with diverse phrases/sentences containing synonyms, paraphrasing, or analogous meanings.
- Measure the accuracy: Ensure the output includes the correct PDF file, page number, and relevant content.
- Evaluate the tool for speed and scalability, ensuring it performs robustly with increasing document size and number of files.