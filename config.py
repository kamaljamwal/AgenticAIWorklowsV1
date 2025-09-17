import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # LLM Provider Configuration
    llm_provider: str = os.getenv("LLM_PROVIDER", "gemini")  # openai, aws, groq, gemini, ollama, huggingface, together, replicate, local_openai
    #llm_provider: str = os.getenv("LLM_PROVIDER", "openai")  # openai, aws, groq, ollama, huggingface, together, replicate, local_openai
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # AWS Bedrock Configuration
    aws_bedrock_region: str = os.getenv("AWS_BEDROCK_REGION", "us-east-1")
    aws_bedrock_model: str = os.getenv("AWS_BEDROCK_MODEL", "anthropic.claude-3-sonnet-20240229-v1:0")
    
    # GROQ Configuration
    groq_api_key: str = os.getenv("GROQ_API_KEY", "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")
    groq_model: str = os.getenv("GROQ_MODEL", "llama3-8b-8192")  # Valid GROQ models: llama3-8b-8192, llama3-70b-8192, mixtral-8x7b-32768, gemma-7b-it
    
    # Google Gemini Configuration (FREE with generous limits)
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "AIzaSyDcdsorevsUMaJE-0ufgI-g4mU2SzJEkPg")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")  # gemini-1.5-flash (free), gemini-1.5-pro (free tier)
    
    # Ollama Configuration (Local Models)
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama2")  # llama2, mistral, codellama, etc.
    
    # Hugging Face Configuration (Local Transformers)
    huggingface_model: str = os.getenv("HUGGINGFACE_MODEL", "microsoft/DialoGPT-medium")
    huggingface_device: str = os.getenv("HUGGINGFACE_DEVICE", "auto")  # auto, cpu, cuda
    huggingface_cache_dir: str = os.getenv("HUGGINGFACE_CACHE_DIR", "./hf_cache")
    
    # Together AI Configuration (Free Tier Available)
    together_api_key: str = os.getenv("TOGETHER_API_KEY", "")
    together_model: str = os.getenv("TOGETHER_MODEL", "togethercomputer/llama-2-7b-chat")
    
    # Replicate Configuration (Free Tier Available)
    replicate_api_token: str = os.getenv("REPLICATE_API_TOKEN", "")
    replicate_model: str = os.getenv("REPLICATE_MODEL", "meta/llama-2-7b-chat")
    
    # Local OpenAI-compatible server (LM Studio, text-generation-webui, etc.)
    local_openai_base_url: str = os.getenv("LOCAL_OPENAI_BASE_URL", "http://localhost:1234/v1")
    local_openai_model: str = os.getenv("LOCAL_OPENAI_MODEL", "local-model")
    local_openai_api_key: str = os.getenv("LOCAL_OPENAI_API_KEY", "not-needed")  # Most local servers don't need this
    
    # JIRA Configuration
    jira_server: str = os.getenv("JIRA_SERVER", "")
    jira_email: str = os.getenv("JIRA_EMAIL", "")
    jira_api_token: str = os.getenv("JIRA_API_TOKEN", "")
    jira_projects: list = os.getenv("JIRA_PROJECTS", "").split(",") if os.getenv("JIRA_PROJECTS") else []
    
    # GitHub Configuration
    github_token: str = os.getenv("GITHUB_TOKEN", "")
    github_repos: list = os.getenv("GITHUB_REPOS", "").split(",") if os.getenv("GITHUB_REPOS") else []
    github_organizations: list = os.getenv("GITHUB_ORGANIZATIONS", "").split(",") if os.getenv("GITHUB_ORGANIZATIONS") else []
    
    # AWS S3 Configuration
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    s3_bucket_name: str = os.getenv("S3_BUCKET_NAME", "")
    s3_content_prefixes: list = os.getenv("S3_CONTENT_PREFIXES", "").split(",") if os.getenv("S3_CONTENT_PREFIXES") else []
    
    # FileSystem Configuration
    filesystem_paths: list = os.getenv("FILESYSTEM_PATHS", os.getcwd()).split(",")
    filesystem_extensions: list = os.getenv("FILESYSTEM_EXTENSIONS", ".txt,.md,.py,.js,.json").split(",")
    filesystem_exclude_dirs: list = os.getenv("FILESYSTEM_EXCLUDE_DIRS", "node_modules,__pycache__,.git,venv,env").split(",")
    
    # Video Sources Configuration
    video_sources: list = os.getenv("VIDEO_SOURCES", "youtube,local").split(",")
    video_youtube_channels: list = os.getenv("VIDEO_YOUTUBE_CHANNELS", "").split(",") if os.getenv("VIDEO_YOUTUBE_CHANNELS") else []
    video_youtube_playlists: list = os.getenv("VIDEO_YOUTUBE_PLAYLISTS", "").split(",") if os.getenv("VIDEO_YOUTUBE_PLAYLISTS") else []
    video_local_paths: list = os.getenv("VIDEO_LOCAL_PATHS", "").split(",") if os.getenv("VIDEO_LOCAL_PATHS") else []
    video_supported_formats: list = os.getenv("VIDEO_SUPPORTED_FORMATS", ".mp4,.avi,.mkv,.mov,.wmv").split(",")
    
    # URL Sources Configuration
    url_sources: list = os.getenv("URL_SOURCES", "https://medium.com/").split(",") if os.getenv("URL_SOURCES") else []
    url_crawl_depth: int = int(os.getenv("URL_CRAWL_DEPTH", "2"))
    url_allowed_domains: list = os.getenv("URL_ALLOWED_DOMAINS", "").split(",") if os.getenv("URL_ALLOWED_DOMAINS") else []
    
    # API Sources Configuration
    api_endpoints: list = os.getenv("API_ENDPOINTS", "").split(",") if os.getenv("API_ENDPOINTS") else []
    
    # Content Processing Configuration
    content_chunk_size: int = int(os.getenv("CONTENT_CHUNK_SIZE", "1000"))
    content_overlap_size: int = int(os.getenv("CONTENT_OVERLAP_SIZE", "200"))
    content_max_file_size: int = int(os.getenv("CONTENT_MAX_FILE_SIZE", "10485760"))  # 10MB
    enable_content_indexing: bool = os.getenv("ENABLE_CONTENT_INDEXING", "true").lower() == "true"
    index_update_interval: int = int(os.getenv("INDEX_UPDATE_INTERVAL", "3600"))  # 1 hour
    
    # Application Configuration
    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    app_port: int = int(os.getenv("APP_PORT", "8000"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"

settings = Settings()
