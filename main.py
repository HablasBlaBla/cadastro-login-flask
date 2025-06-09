from flask import Flask, render_template, url_for, request
from flask_bcrypt import Bcrypt
app = Flask(__name__)
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']

        senhaCriptografada = bcrypt.generate_password_hash(senha) 
        print(f'{nome}, {senhaCriptografada}')
    return render_template('cadastro.html')

if __name__ == '__main__':
    app.run(debug=True)