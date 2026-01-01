from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import json

# Try to load DB config from a file, otherwise use defaults
DB_CONFIG_FILE = "backend/config/db_config.json"

def load_db_config():
    if os.path.exists(DB_CONFIG_FILE):
        try:
            with open(DB_CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        "user": "root",
        "password": "",
        "host": "localhost",
        "port": 3306,
        "db_name": "grade_system"
    }

def get_db_engine():
    config = load_db_config()
    db_url = f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['db_name']}"
    try:
        engine = create_engine(db_url, connect_args={'connect_timeout': 3})
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

# Global engine instance
_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = get_db_engine()
    return _engine

def reload_engine():
    global _engine
    if _engine:
        _engine.dispose()
    _engine = get_db_engine()
    return _engine

def is_db_available():
    return get_engine() is not None
