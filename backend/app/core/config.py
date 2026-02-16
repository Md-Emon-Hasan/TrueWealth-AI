import os

# Model Configurations
EMBEDDINGS_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
MEMORY_LIMIT = 10

# File Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "..", "db", "vectorstore")
PDF_PATH = os.path.join(BASE_DIR, "..", "data", "financial_reports.pdf")

# RAG Configurations
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100
