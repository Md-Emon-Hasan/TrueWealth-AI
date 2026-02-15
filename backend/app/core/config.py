from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# LLM Configuration
LLM_MODEL = "openai/gpt-oss-120b"
LLM_TEMPERATURE = 0.3
LLM_MAX_TOKENS = 2048

# Embeddings Configuration
EMBEDDINGS_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Vector Store Configuration
VECTOR_DB_PATH = "../finance_db"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 128
RETRIEVAL_K = 3

# Data Configuration
PDF_PATH = '../data/The Intelligent Investor - BENJAMIN GRAHAM.pdf'

# Memory Configuration
MEMORY_LIMIT = 10
MAX_RETRY = 3