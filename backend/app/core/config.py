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
# yfinance news fetches and renders full article pages via WebBaseLoader, measured ~13s in practice
MARKET_DESK_TIMEOUT_SECONDS = float(os.getenv("MARKET_DESK_TIMEOUT_SECONDS", 15))

# Model gateway, all Groq-hosted, tiered by task cost/quality tradeoff
MODEL_ANSWER = os.getenv("MODEL_ANSWER", "openai/gpt-oss-120b")
MODEL_REASONING = os.getenv("MODEL_REASONING", "llama-3.3-70b-versatile")
MODEL_CLASSIFY = os.getenv("MODEL_CLASSIFY", "llama-3.1-8b-instant")
GATEWAY_CACHE_TTL = int(os.getenv("GATEWAY_CACHE_TTL", 300))
GATEWAY_RETRY_LIMIT = int(os.getenv("GATEWAY_RETRY_LIMIT", 1))

# due diligence, thresholds below are unvalidated starting points
DUE_DILIGENCE_SKIP_WHEN_CLEAN = os.getenv("DUE_DILIGENCE_SKIP_WHEN_CLEAN", "true").lower() == "true"
DUE_DILIGENCE_MAX_REVISIONS = int(os.getenv("DUE_DILIGENCE_MAX_REVISIONS", 1))

# portfolio analysis
PORTFOLIO_HISTORY_PERIOD = os.getenv("PORTFOLIO_HISTORY_PERIOD", "6mo")
PORTFOLIO_CONCENTRATION_THRESHOLD_PCT = float(os.getenv("PORTFOLIO_CONCENTRATION_THRESHOLD_PCT", 40))

# semantic memory, on top of the MEMORY_LIMIT recency buffer above
SEMANTIC_MEMORY_TOP_K = int(os.getenv("SEMANTIC_MEMORY_TOP_K", 3))
MEMORY_COLLECTION_NAME = "conversation_memory"

# human review queue triggers, unvalidated starting points
REVIEW_ON_HIGH_RISK = os.getenv("REVIEW_ON_HIGH_RISK", "true").lower() == "true"
REVIEW_ON_COMPLIANCE_VIOLATION = os.getenv("REVIEW_ON_COMPLIANCE_VIOLATION", "true").lower() == "true"
REVIEW_ON_UNSUPPORTED_FIGURES = os.getenv("REVIEW_ON_UNSUPPORTED_FIGURES", "true").lower() == "true"
REVIEW_ON_MARKET_DATA_UNAVAILABLE = os.getenv("REVIEW_ON_MARKET_DATA_UNAVAILABLE", "true").lower() == "true"
# violations that auto-fix themselves (the disclaimer gets appended regardless) don't need a human
REVIEW_IGNORED_VIOLATIONS = {"missing_disclaimer"}
