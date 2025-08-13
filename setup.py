from setuptools import setup, find_packages

setup(
    name="TrueWealth AI",
    version="0.2.0",
    author="Md Emon Hasan",
    author_email="iconicemon01@gmail.com",
    description="TrueWealth AI: Your Smart Path to Financial Freedom",
    packages=find_packages(),
    install_requires=[
        # Core Requirements
        "fastapi",
        "uvicorn",
        "python-dotenv",
        "pydantic",
        "tiktoken",
        "pypdf",
        "wikipedia",
        "sqlalchemy",
        "gunicorn",
        "pytest",
        
        # AI/LangChain Requirements
        "langchain",
        "langchain-community",
        "langchain-huggingface",
        "langchain-groq",
        "langgraph",
        "langchain-core",
        "huggingface-hub",
        "sentence-transformers",
        
        # Vector Database
        "chromadb",
        
        # Search Tools
        "duckduckgo-search",
        "yahoo-finance",
        "yahoo_fin"
    ]
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: FastAPI",
        "Framework :: Streamlit",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
