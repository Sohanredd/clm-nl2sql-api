import os
from dotenv import load_dotenv

dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../.env'))
load_dotenv(dotenv_path=dotenv_path, override=True)

DB_ENGINE = os.getenv('DB_ENGINE', 'duckdb')
_db_path = os.getenv('DB_PATH', '../db/fclm.duckdb')
# Always resolve to absolute path relative to project root
if not os.path.isabs(_db_path):
    DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', _db_path))
else:
    DB_PATH = _db_path

ROW_LIMIT = int(os.getenv('ROW_LIMIT', 1000))
SAFE_MODE = os.getenv('SAFE_MODE', 'true').lower() == 'true'

# LLM provider placeholder (OpenAI, Anthropic, Azure, etc.)
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'none')
