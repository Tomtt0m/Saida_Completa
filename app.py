from flask import Flask, render_template, redirect, url_for, request, session, flash
from models import db, Usuario, SaidaCompleta
from forms import LoginForm
from config import Config
import os
from datetime import datetime
import jsonify

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
    try:
        dados = request.get_json()

        regiao_cod = dados.get("regiao_cod")
        regiao_nome = dados.get("regiao_nome")
        cliente = dados.get("cliente")
        produto = dados.get("produto")
        rota = dados.get("rota")
        pre_nota = dados.get("pre_nota")
        numero_caixa = dados.get("numero_caixa")

        # Aqui você pode gravar no banco de dados
        # Exemplo (simulação):
        print(f"""
        Cód Região: {regiao_cod}
        Região: {regiao_nome}
        Cliente: {cliente}
        Produto: {produto}
        Rota: {rota}
        Pré-nota: {pre_nota}
        Nº Caixa: {numero_caixa}
        """)

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
        s.foto_etiqueta = path
        s.horario_foto_1 = datetime.now()
    if palete:
        path = os.path.join(app.config['UPLOAD_FOLDER'], f'palete_{id}.jpg')
        palete.save(path)
        s.foto_palete = path
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
