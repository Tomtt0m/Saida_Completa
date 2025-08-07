import os

class Config:
    SECRET_KEY = 'sua-chave-secreta'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///saida.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/uploads'
