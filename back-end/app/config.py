# app/config.py

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'manwhatcanisay')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///user_info.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    # 其他配置参数
