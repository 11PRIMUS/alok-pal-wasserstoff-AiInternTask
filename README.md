# Document Query and Analysis System

This project is a Streamlit web application designed for uploading, processing, and analyzing various document types. Users can ask questions about specific documents or identify common themes across multiple documents.

## Features

*   **Document Upload:** Supports PDF, DOCX, TXT, and common image formats (PNG, JPG, JPEG).
*   **Text Extraction:** Utilizes OCR (Optical Character Recognition) for image-based documents and text extraction for other formats.
*   **Vector Store Integration:** Stores document embeddings in a local vector database for efficient semantic search and retrieval.
*   **Document Q&A:** Allows users to select a processed document and ask natural language questions to get answers based on its content, along with citations.
*   **Cross-Document Theme Analysis:** Enables users to select multiple documents and a query to identify and summarize common themes.
*   **Persistent Storage:** Remembers processed documents across sessions using a local vector store.

## Setup and Installation

### Prerequisites

*   Python 3.8+
*   Pip (Python package installer)

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd alok-pal-wasserstoff-AiInternTask
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    
    ```bash
    pip install -r requirements.txt
    ```
    *(If using Tesseract OCR, ensure Tesseract is installed on your system and accessible in your PATH.)*

4.  **Set up Environment Variables:**
    This application requires a `NEBIUS_API_KEY`. You can set this up in one of two ways:

        ```
    *   **Using Streamlit Secrets**
        Create a file at `.streamlit/secrets.toml` and add:
        ```toml
        NEBIUS_API_KEY = "your_actual_api_key_here"
        LANGCHAIN_API_KEY="your langchain_api_key_here"
        LANGCHAIN_PROJECT="project name to view in Langsmith"
        ```
        When deploying to services like Streamlit Community Cloud, you will set these secrets through their platform's UI.

## Usage

1.  Ensure your environment variables are set up correctly (see step 4 above).
2.  Navigate to the project's root directory in your terminal.
3.  Run the Streamlit application:
    ```bash
    streamlit run app.py
    ```
4.  Open your web browser and go to the local URL provided by Streamlit (usually `http://localhost:8501`).

### Using the Application

*   **Upload Documents:** Use the sidebar to upload your documents. The application will process them and add them to the vector store.
*   **Ask Questions:** Go to the "Ask Document" tab, select a processed document, type your question, and click "Get Answer."
*   **Analyze Themes:** Go to the "Analyze Theme" tab, select one or more documents, enter your theme query (e.g., "key challenges," "future outlook"), and click "Analyze Themes."

## Project Structure

```
alok-pal-wasserstoff-AiInternTask/
├── .streamlit/
│   └── secrets.toml       # (Optional) For Streamlit secrets
├── utils/
│   ├── __init__.py
│   ├── database.py        # Vector store initialization and operations
│   ├── ocr_doc.py         # Document parsing and text extraction
│   └── qa_system.py       # Q&A and theme analysis logic
├── vector_store_db/       # Directory for the local vector store
├── .env                   # (Optional) For local environment variables
├── .gitignore             # Specifies intentionally untracked files
├── app.py                 # Main Streamlit application file
├── requirements.txt       # Project dependencies
└── README.md              # This file
```

## Potential Future Enhancements

*   Support for more document types.
*   Integration with cloud storage for documents.
*   More advanced NLP features (e.g., summarization, entity recognition).
*   User authentication.
*   Option to choose different LLM models.
*   Improved error handling and user feedback.

---

*Remember to replace `<your-repository-url>` with the actual URL if you host this on GitHub or another platform. Also, ensure your `requirements.txt` is accurate and complete.*