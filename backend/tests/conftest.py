import os

from app.core.config import get_settings

os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "postgresql+psycopg://test:test@localhost:5432/portfolio_test"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["CORS_ORIGINS"] = '["http://localhost:5173"]'
os.environ["TELEGRAM_BOT_TOKEN"] = ""
os.environ["TELEGRAM_CHAT_ID"] = ""

get_settings.cache_clear()
