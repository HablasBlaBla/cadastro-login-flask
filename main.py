from flask import Flask, render_template, url_for, request, flash, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import time


app = Flask(__name__)   
bcrypt = Bcrypt(app)

# configuração da chave secreta e do nome do banco de dados
app.config['SECRET_KEY'] = 'alef.1234'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///teste.db'
db = SQLAlchemy(app)


# tabela pra guardar os dados dos usuários cadatrados
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(60), nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    
    def __repr__(self):
        return f'Usuario {self.nome}'


def criptografarSenha(senha):
    senhaHash = bcrypt.generate_password_hash(senha)
    return senhaHash
def verificarSenhaCriptografada():
    senhaVerificada = bcrypt.check_password_hash(criptografarSenha)
    return senhaVerificada


# Rota inicial
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/home')
def home():
    nome = session.get('nome')
    if nome:
        return render_template('home.html')
    else:
        print(f'Você precisa fazer login para acessar esta área!', redirect(url_for('entrar')))
    return render_template('home.html')

# Rota pra página de cadastro
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']

        """ criptografar a senha e mandar a senha criptografada no lugar da senha "crua" enviada pelo usuário
        senhaCriptografada = bcrypt.generate_password_hash(criptografarSenha(senha)) """

        novo_usuario = Usuario(nome=nome, senha=criptografarSenha(senha))
        
        """ fiz uma tratativa de erro pra se der merda
        não mostre as mensagens de erro normais """
        
        try:
            db.session.add(novo_usuario)
            db.session.commit()

            """ adicionei o método flash pra armazenar as mensagens
            de sucesso ou erro pra mostrar pro usuário quando precisar """

            flash('Dados registrados!', 'success')
            return render_template('cadastro.html')
        except Exception as e:
            flash(f'Erro ao registrar ::::::::: {e}', 'error')
            return render_template('cadastro.html')
        finally:
            print('\n')
                
        print(f'{nome}, {senhaCriptografada}')
        return senhaCriptografada
    return render_template('cadastro.html')

@app.route('/entrar', methods=['GET', 'POST'])
def entrar():
    try:
        if request.method == 'POST':
            nome = request.form.get('nome')
            senha = request.form.get('senha')
            
            session['nome'] = request.form['nome']
            return redirect(url_for('home'))
            
            usuario = Usuario.query.filter_by(nome=nome).first()
            
            if usuario and bcrypt.check_password_hash(usuario.senha, senha):
                flash('Redirecionando em 5 segundos...', 'success')
                time.sleep(5)
                return redirect('/home')
    except Exception as e:
        flash(f'Erro ao logar ::::::::: {e}')
        
    return render_template('entrar.html')

@app.route('/sair')
def sair():
    session.pop('nome', None)
    return redirect(url_for('entrar'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # print('Banco de dados criado!')
    app.run(debug=True)
