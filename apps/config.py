import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    SECRET_KEY = os.getenv('SECRET_KEY')
    PROPAGATE_EXCEPTIONS = True
