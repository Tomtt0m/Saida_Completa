from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(100), nullable=False)

class SaidaCompleta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    qr_code_raw = db.Column(db.String(50))
    rota = db.Column(db.String(10))
    pre_nota = db.Column(db.String(10))
    regiao_cod = db.Column(db.String(5))
    regiao_nome = db.Column(db.String(50))
    cliente = db.Column(db.String(100))
    produto = db.Column(db.String(100))
    numero_caixa = db.Column(db.String(10))
    quantidade_de_volumes = db.Column(db.String(10))
    foto_etiqueta = db.Column(db.String(200))
    foto_palete = db.Column(db.String(200))
    horario_leitura = db.Column(db.DateTime)
    horario_foto_1 = db.Column(db.DateTime)
    horario_foto_2 = db.Column(db.DateTime)
    horario_confirmado = db.Column(db.DateTime)
