from flask import Flask, render_template, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


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


# Rota inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota pra página de cadastro
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']

        # MEU COMENTÁRIO (ALEF): criptografar a senha e mandar a senha criptografada no lugar da senha "crua" enviada pelo usuário
        senhaCriptografada = bcrypt.generate_password_hash(senha) 
        novo_usuario = Usuario(nome=nome, senha=senhaCriptografada)
        
        # MEU COMENTÁRIO (ALEF): fiz uma tratativa de erro pra se der merda não mostre as mensagens de erro normais
        try:
            db.session.add(novo_usuario)
            db.session.commit()
            # MEU COMENTÁRIO (ALEF): adicionei o método flash pra armazenar as mensagens de sucesso ou erro pra mostrar pro usuário quando precisar
            flash('Dados registrados!', 'success')
            return render_template('cadastro.html')
        except Exception as e:
            flash(f'Erro ao registrar ::::::::: {e}', 'error')
            return render_template('cadastro.html')
        finally:
            print('\n')
                
        # print(f'{nome}, {senhaCriptografada}')
    return render_template('cadastro.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print('Banco de dados criado!')
    app.run(debug=True)