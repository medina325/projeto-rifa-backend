from dotenv import load_dotenv
import os

load_dotenv()

def get_env_var(env_var: str, default=None):
    return os.environ.get(env_var, default)
