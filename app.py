from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from models import db, Usuario, SaidaCompleta
from forms import LoginForm
from config import Config
import os
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def criar_banco():
    with app.app_context():
        db.create_all()

        if not Usuario.query.first():
            u1 = Usuario(nome='admin', senha='1234')
            u2 = Usuario(nome='operador1', senha='senha1')
            db.session.add_all([u1, u2])
            db.session.commit()

        if not SaidaCompleta.query.first():
            s1 = SaidaCompleta(
                usuario_id=u1.id,
                qr_code_raw='670103050086405493500000001820250729006769',
                rota='0864',
                pre_nota='549350',
                regiao_cod='18',
                regiao_nome='E DIRETA',
                cliente='707 AUTO – SERVIÇO DE ALIMENTOS',
                produto='CO PANTENE 510ML BIOTINAMINA B3',
                numero_caixa='0067',
                horario_leitura=datetime.now(),
                horario_foto_1=datetime.now(),
                horario_foto_2=datetime.now(),
                horario_confirmado=datetime.now(),
                foto_etiqueta='static/uploads/etiqueta_exemplo.jpg',
                foto_palete='static/uploads/palete_exemplo.jpg'
            )
            db.session.add(s1)
            db.session.commit()

@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(nome=form.nome.data, senha=form.senha.data).first()
        if usuario:
            session['usuario_id'] = usuario.id
            session['usuario_nome'] = usuario.nome
            return redirect(url_for('saida'))
        else:
            flash('Usuário ou senha inválido.')
    return render_template('login.html', form=form)

@app.route('/saida')
def saida():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    return render_template('saida.html', usuario=session['usuario_nome'])

@app.route("/registrar", methods=["POST"])
def registrar():
    if 'usuario_id' not in session:
        return jsonify({"status": "erro", "mensagem": "Usuário não autenticado"}), 401

    try:
        # Captura campos do formulário
        qr_code_raw = request.form.get("qr_code_raw")
        rota = request.form.get("rota")
        pre_nota = request.form.get("pre_nota")
        codigo_regiao = request.form.get("regiao_cod")  # manter nome igual ao HTML
        regiao_nome = request.form.get("regiao_nome")
        cliente = request.form.get("cliente")
        produto = request.form.get("produto")
        numero_caixa = request.form.get("numero_caixa")
        quantidade = request.form.get("quantidade")

        # Captura arquivos
        foto_etiqueta = request.files.get("foto_etiqueta")
        foto_palete = request.files.get("foto_palete")

        # Pasta de uploads
        upload_folder = app.config.get('UPLOAD_FOLDER', 'static/uploads')
        os.makedirs(upload_folder, exist_ok=True)

        foto_etiqueta_path = None
        foto_palete_path = None

        if foto_etiqueta:
            foto_etiqueta_path = os.path.join(upload_folder, f"etiqueta_{numero_caixa}.jpg")
            foto_etiqueta.save(foto_etiqueta_path)
            foto_etiqueta_path = f"static/uploads/etiqueta_{numero_caixa}.jpg"  # caminho relativo

        if foto_palete:
            foto_palete_path = os.path.join(upload_folder, f"palete_{numero_caixa}.jpg")
            foto_palete.save(foto_palete_path)
            foto_palete_path = f"static/uploads/palete_{numero_caixa}.jpg"  # caminho relativo

        # Cria novo registro no banco
        saida = SaidaCompleta(
            usuario_id=session.get('usuario_id'),
            qr_code_raw=qr_code_raw,
            rota=rota,
            pre_nota=pre_nota,
            regiao_cod=codigo_regiao,
            regiao_nome=regiao_nome,
            cliente=cliente,
            produto=produto,
            numero_caixa=numero_caixa,
            quantidade_volumes=quantidade,
            horario_leitura=datetime.now(),
            horario_foto_1=datetime.now() if foto_etiqueta_path else None,
            horario_foto_2=datetime.now() if foto_palete_path else None,
            foto_etiqueta=foto_etiqueta_path,
            foto_palete=foto_palete_path
        )
        db.session.add(saida)
        db.session.commit()

        return jsonify({"status": "sucesso", "mensagem": "Dados registrados com sucesso"}), 200

    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 400

@app.route('/upload/<int:id>', methods=['POST'])
def upload(id):
    s = SaidaCompleta.query.get_or_404(id)
    etiqueta = request.files.get('etiqueta')
    palete = request.files.get('palete')

    if etiqueta:
        path = os.path.join(app.config['UPLOAD_FOLDER'], f'etiqueta_{id}.jpg')
        etiqueta.save(path)
        s.foto_etiqueta = f"static/uploads/etiqueta_{id}.jpg"
        s.horario_foto_1 = datetime.now()
    if palete:
        path = os.path.join(app.config['UPLOAD_FOLDER'], f'palete_{id}.jpg')
        palete.save(path)
        s.foto_palete = f"static/uploads/palete_{id}.jpg"
        s.horario_foto_2 = datetime.now()

    db.session.commit()
    return 'OK'

@app.route('/confirmar/<int:id>', methods=['POST'])
def confirmar(id):
    s = SaidaCompleta.query.get_or_404(id)
    s.horario_confirmado = datetime.now()
    db.session.commit()
    return redirect(url_for('resumo', id=id))

@app.route('/resumo/<int:id>')
def resumo(id):
    s = SaidaCompleta.query.get_or_404(id)
    return render_template('resumo.html', s=s)

@app.route('/volumes/<int:id>', methods=['POST'])
def volumes(id):
    s = SaidaCompleta.query.get_or_404(id)
    dados = request.json
    s.quantidade_volumes = dados['quantidade']
    db.session.commit()
    return 'OK'

if __name__ == '__main__':
    criar_banco()
    app.run(debug=True)
