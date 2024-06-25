from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', None)
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', None)
SECRET_KEY = os.environ.get('SECRET_KEY', None)
REDIRECT_URI = os.environ.get('REDIRECT_URI', None)
