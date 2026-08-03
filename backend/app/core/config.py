import os

# Model Configurations
EMBEDDINGS_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
MEMORY_LIMIT = 10

# File Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "finance_db")
PDF_PATH = os.path.join(BASE_DIR, "data", "The Intelligent Investor - BENJAMIN GRAHAM.pdf")

# RAG Configurations
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100

# Persistence
SQLITE_PATH = os.getenv("SQLITE_PATH", os.path.join(BASE_DIR, "truewealth.sqlite3"))

# Cache TTLs, seconds
EMBEDDING_CACHE_TTL = int(os.getenv("EMBEDDING_CACHE_TTL", 60 * 60 * 24 * 7))
RAG_CACHE_TTL = int(os.getenv("RAG_CACHE_TTL", 60 * 30))
MARKET_QUOTE_CACHE_TTL = int(os.getenv("MARKET_QUOTE_CACHE_TTL", 45))
NEWS_CACHE_TTL = int(os.getenv("NEWS_CACHE_TTL", 600))
DDG_CACHE_TTL = int(os.getenv("DDG_CACHE_TTL", 1200))
# never longer than market-data TTL, an answer built on a live quote can't outlive the quote
ANSWER_CACHE_TTL = min(MARKET_QUOTE_CACHE_TTL, int(os.getenv("ANSWER_CACHE_TTL", 120)))
CACHE_MAXSIZE = int(os.getenv("CACHE_MAXSIZE", 256))

# Rate limiting
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT = os.getenv("RATE_LIMIT", "20/minute")

# Outbound tool network behavior
TOOL_TIMEOUT_SECONDS = float(os.getenv("TOOL_TIMEOUT_SECONDS", 8))
TOOL_RETRY_LIMIT = int(os.getenv("TOOL_RETRY_LIMIT", 1))
