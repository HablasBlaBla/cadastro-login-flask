from flask import Flask, render_template, url_for, request, flash, redirect, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import requests
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


class Professor(db.Model):
    __tablename__ = 'professores'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    cpf = db.Column(db.String(14), nullable=False, unique=True)
    senha = db.Column(db.String(255), nullable=False)
    data_cadastro = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    ultimo_login = db.Column(db.DateTime, nullable=True)
    ativo = db.Column(db.Boolean, default=True)
    admin = db.Column(db.Boolean, default=False)

    alunos = db.relationship('Aluno', backref='professor', lazy=True)
    emprestimos = db.relationship('Emprestimo', backref='professor', lazy=True)

    def __repr__(self):
        return f'Professor {self.nome}'


class Aluno(db.Model):
    __tablename__ = 'alunos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(255), nullable=False)
    serie = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professores.id'), nullable=True)

    emprestimos = db.relationship('Emprestimo', backref='aluno', lazy=True)

    def __repr__(self):
        return f'Aluno {self.nome}'


class Livro(db.Model):
    __tablename__ = 'livros'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(255), nullable=False)
    autor = db.Column(db.String(255), nullable=False)
    isbn = db.Column(db.String(20), nullable=False)
    capa_url = db.Column(db.String(700), nullable=True)
    descricao = db.Column(db.Text, nullable=True)
    categoria = db.Column(db.String(100), nullable=True)
    ano_publicacao = db.Column(db.String(4), nullable=False)
    genero = db.Column(db.String(100), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)

    emprestimos = db.relationship('Emprestimo', backref='livro', lazy=True)

    def __repr__(self):
        return f'Livro {self.titulo}'


class Emprestimo(db.Model):
    __tablename__ = 'emprestimos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=True)
    livro_id = db.Column(db.Integer, db.ForeignKey('livros.id'), nullable=True)
    data_emprestimo = db.Column(db.Date, nullable=False)
    data_devolucao = db.Column(db.Date, nullable=True)
    devolvido = db.Column(db.String(50), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professores.id'), nullable=True)

    def __repr__(self):
        return f'Emprestimo {self.id}'


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
@app.route('/painel')
def home():
    nome = session.get('nome')
    if nome:
        return render_template('painel.html')
    else:
        print(f'Você precisa fazer login para acessar esta área!', redirect(url_for('entrar')))
    return render_template('painel.html')

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
                
        # print(f'{nome}, {senhaCriptografada}')
    return render_template('cadastro.html')

@app.route('/cadastroAluno', methods=['GET', 'POST'])
def cadastro_aluno():
    if request.method == 'POST':
        nome = request.form.get('nome')
        serie = request.form.get('serie')
        email = request.form.get('email')

        if not nome or not serie or not email:
            flash('Por favor, preencha todos os campos.', 'error')
            return render_template('cadastroAluno.html')

        # Check if email already exists
        existing_aluno = Aluno.query.filter_by(email=email).first()
        if existing_aluno:
            flash('Email já cadastrado para outro aluno.', 'error')
            return render_template('cadastroAluno.html')

        # For simplicity, set a default password or generate one
        default_password = '123456'  # In real app, generate securely or ask user
        senha_criptografada = criptografarSenha(default_password)

        novo_aluno = Aluno(
            nome=nome,
            serie=serie,
            email=email,
            senha=senha_criptografada
        )
        try:
            db.session.add(novo_aluno)
            db.session.commit()
            flash('Aluno cadastrado com sucesso!', 'success')
            return redirect(url_for('cadastro_aluno'))
        except Exception as e:
            flash(f'Erro ao cadastrar aluno: {e}', 'error')
            return render_template('cadastroAluno.html')
    return render_template('cadastroAluno.html')

@app.route('/cadastroProfessor', methods=['GET', 'POST'])
def cadastro_professor():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        cpf = request.form.get('cpf')
        senha = request.form.get('senha')

        if not nome or not email or not cpf or not senha:
            flash('Por favor, preencha todos os campos.', 'error')
            return render_template('cadastroProfessor.html')

        # Check if email or cpf already exists
        existing_professor_email = Professor.query.filter_by(email=email).first()
        existing_professor_cpf = Professor.query.filter_by(cpf=cpf).first()
        if existing_professor_email:
            flash('Email já cadastrado para outro professor.', 'error')
            return render_template('cadastroProfessor.html')
        if existing_professor_cpf:
            flash('CPF já cadastrado para outro professor.', 'error')
            return render_template('cadastroProfessor.html')

        senha_criptografada = criptografarSenha(senha)

        novo_professor = Professor(
            nome=nome,
            email=email,
            cpf=cpf,
            senha=senha_criptografada
        )
        try:
            db.session.add(novo_professor)
            db.session.commit()
            flash('Professor cadastrado com sucesso!', 'success')
            return redirect(url_for('cadastro_professor'))
        except Exception as e:
            flash(f'Erro ao cadastrar professor: {e}', 'error')
            return render_template('cadastroProfessor.html')
    return render_template('cadastroProfessor.html')



from flask import flash

@app.route('/entrar', methods=['GET', 'POST'])
def entrar():
    try:
        if request.method == 'POST':
            # Check if request is JSON or form
            if request.is_json:
                data = request.get_json()
                login = data.get('login')
                senha = data.get('senha')
            else:
                login = request.form.get('login')
                senha = request.form.get('senha')

            professor = Professor.query.filter((Professor.email == login) | (Professor.cpf == login)).first()

            if professor and bcrypt.check_password_hash(professor.senha, senha):
                session['professor_id'] = professor.id
                session['professor_nome'] = professor.nome
                flash('Login bem sucedido! Redirecionando...', 'success')
                return redirect(url_for('home'))
            else:
                flash('Email/CPF ou senha inválidos.', 'error')
                return render_template('entrar.html')
    except Exception as e:
        flash(f'Erro ao logar: {e}', 'error')
        return render_template('entrar.html')

    return render_template('entrar.html')



@app.route('/sair')
def sair():
    session.pop('nome', None)
    return redirect(url_for('entrar'))
@app.route('/cabecalho')
def cabecalho():
    return render_template('outros/cabecalho.html')




@app.route('/livrosApi', methods=['GET', 'POST'])
def livros_api():
    query = ''
    livros_api_results = []
    if request.method == 'POST':
        # Check if this is a multi-book add request
        if 'selected_books' in request.form:
            selected_books = request.form.getlist('selected_books')
            success_count = 0
            for book_id in selected_books:
                # The book data is sent as JSON string in hidden input, parse it
                import json
                book_data_json = request.form.get(f'book_data_{book_id}')
                if not book_data_json:
                    continue
                book_data = json.loads(book_data_json)
                titulo = book_data.get('titulo', '')
                autor = book_data.get('autor', '')
                isbn = book_data.get('isbn', '')
                capa_url = book_data.get('capa_url', '')
                descricao = book_data.get('descricao', '')
                categoria = book_data.get('categoria', '')
                ano_publicacao = book_data.get('ano_publicacao', '')
                genero = book_data.get('genero', '')
                quantidade = 1
                # Check if book already exists by ISBN
                existing_livro = Livro.query.filter_by(isbn=isbn).first()
                if existing_livro:
                    continue
                novo_livro = Livro(
                    titulo=titulo,
                    autor=autor,
                    isbn=isbn,
                    capa_url=capa_url,
                    descricao=descricao,
                    categoria=categoria,
                    ano_publicacao=ano_publicacao,
                    genero=genero,
                    quantidade=quantidade
                )
                db.session.add(novo_livro)
                success_count += 1
            if success_count > 0:
                try:
                    db.session.commit()
                    flash(f'{success_count} livro(s) cadastrado(s) com sucesso!', 'success')
                except Exception as e:
                    flash(f'Erro ao cadastrar livros: {e}', 'error')
            else:
                flash('Nenhum livro novo foi cadastrado.', 'info')
        else:
            # Search books from Google Books API
            query = request.form.get('titulo', '')
            if query:
                url = f'https://www.googleapis.com/books/v1/volumes?q=intitle:{query}'
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    livros_api_results = data.get('items', [])
                else:
                    flash('Erro ao buscar livros na API do Google Books.', 'error')
    return render_template('livrosApi.html', livros_api=livros_api_results, query=query)

@app.route('/livrosCadastrados')
def livros_cadastrados():
    livros = Livro.query.all()
    return render_template('livrosCadastrados.html', livros=livros)

@app.route('/alunosCadastrados')
def alunos_cadastrados():
    alunos = Aluno.query.order_by(Aluno.serie.desc()).all()
    return render_template('alunosCadastrados.html', alunos=alunos)

@app.route('/professoresCadastrados')
def professores_cadastrados():
    professores = Professor.query.order_by(Professor.nome).all()
    return render_template('professoresCadastrados.html', professores=professores)

from datetime import datetime

@app.route('/cadastroEmprestimo', methods=['GET', 'POST'])
def cadastro_emprestimo():
    alunos = Aluno.query.order_by(Aluno.nome).all()
    livros = Livro.query.order_by(Livro.titulo).all()

    if request.method == 'POST':
        aluno_id = request.form.get('aluno_id')
        livro_id = request.form.get('livro_id')
        data_emprestimo_str = request.form.get('data_emprestimo')
        data_devolucao_str = request.form.get('data_devolucao')

        if not aluno_id or not livro_id or not data_emprestimo_str:
            flash('Por favor, preencha os campos obrigatórios.', 'error')
            return render_template('cadastroEmprestimo.html', alunos=alunos, livros=livros)

        try:
            data_emprestimo = datetime.strptime(data_emprestimo_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Data de empréstimo inválida.', 'error')
            return render_template('cadastroEmprestimo.html', alunos=alunos, livros=livros)

        data_devolucao = None
        if data_devolucao_str:
            try:
                data_devolucao = datetime.strptime(data_devolucao_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Data de devolução inválida.', 'error')
                return render_template('cadastroEmprestimo.html', alunos=alunos, livros=livros)

        novo_emprestimo = Emprestimo(
            aluno_id=aluno_id,
            livro_id=livro_id,
            data_emprestimo=data_emprestimo,
            data_devolucao=data_devolucao,
            devolvido='Não'
        )
        try:
            db.session.add(novo_emprestimo)
            db.session.commit()
            flash('Empréstimo cadastrado com sucesso!', 'success')
            return redirect(url_for('cadastro_emprestimo'))
        except Exception as e:
            flash(f'Erro ao cadastrar empréstimo: {e}', 'error')
            return render_template('cadastroEmprestimo.html', alunos=alunos, livros=livros)

    return render_template('cadastroEmprestimo.html', alunos=alunos, livros=livros)

@app.route('/emprestimos', methods=['GET', 'POST'])
def emprestimos():
    emprestimos = Emprestimo.query.order_by(Emprestimo.data_emprestimo.desc()).all()

    if request.method == 'POST':
        emprestimo_id = request.form.get('emprestimo_id')
        emprestimo = Emprestimo.query.get(emprestimo_id)
        if emprestimo and emprestimo.devolvido.lower() != 'sim':
            emprestimo.devolvido = 'Sim'
            try:
                db.session.commit()
                flash('Empréstimo marcado como devolvido.', 'success')
            except Exception as e:
                flash(f'Erro ao atualizar empréstimo: {e}', 'error')
        else:
            flash('Empréstimo não encontrado ou já devolvido.', 'error')

    return render_template('emprestimos.html', emprestimos=emprestimos)

@app.route('/devolverEmprestimo/<int:emprestimo_id>', methods=['POST'])
def devolver_emprestimo(emprestimo_id):
    emprestimo = Emprestimo.query.get(emprestimo_id)
    if emprestimo and emprestimo.devolvido.lower() != 'sim':
        emprestimo.devolvido = 'Sim'
        try:
            db.session.commit()
            flash('Empréstimo marcado como devolvido.', 'success')
        except Exception as e:
            flash(f'Erro ao atualizar empréstimo: {e}', 'error')
    else:
        flash('Empréstimo não encontrado ou já devolvido.', 'error')
    return redirect(url_for('emprestimos'))



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # print('Banco de dados criado!')
    app.run(debug=True)
