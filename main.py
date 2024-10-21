from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.middleware.proxy_fix import ProxyFix
import sqlite3
import os

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)  # Permitir o uso de proxies
app.secret_key = 'sua_chave_secreta_aqui'  # Adicione uma chave secreta para sessões
DATABASE = os.path.join(app.instance_path, 'users.db')

# Criar banco de dados se não existir
if not os.path.exists(app.instance_path):
    os.makedirs(app.instance_path)


# Criar tabela de usuários, se não existir
def create_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                whatsapp TEXT NOT NULL,
                workplace TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor = conn.execute("PRAGMA table_info(users);")
        columns = cursor.fetchall()
        print("Colunas da tabela users:", columns)


create_db()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        whatsapp = request.form.get('whatsapp')
        workplace = request.form.get('workplace')

        # Verificar se os campos obrigatórios foram preenchidos
        if not name or not address or not whatsapp or not workplace:
            flash("Por favor, preencha todos os campos.",
                  "error")  # Mensagem de erro
            return redirect(url_for('index'))

        try:
            with sqlite3.connect(DATABASE) as conn:
                conn.execute(
                    'INSERT INTO users (name, address, whatsapp, workplace) VALUES (?, ?, ?, ?)',
                    (name, address, whatsapp, workplace))
                conn.commit()
            flash("Usuário registrado com sucesso!",
                  "success")  # Mensagem de sucesso
            return redirect(
                url_for('index'))  # Redirecionar para a página inicial
        except sqlite3.Error as e:
            print(f"Erro ao registrar usuário: {e}")
            flash(f"Erro ao registrar usuário: {e}",
                  "error")  # Mensagem de erro
            return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    # Verificar se o usuário está autenticado
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.execute('SELECT * FROM users')
            users = cursor.fetchall()
        return render_template('dashboard.html', users=users)
    except Exception as e:
        print(f"Erro ao acessar o dashboard: {e}")
        return "Erro ao acessar o dashboard.", 500


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verifique se os dados estão corretos
        if username == 'lazaro' and password == '7987':
            session['logged_in'] = True  # Marcar o usuário como autenticado
            return redirect(url_for('dashboard'))
        else:
            flash("Usuário ou senha inválidos.", "error")  # Mensagem de erro
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)  # Remove a autenticação da sessão
    return redirect(url_for('index'))  # Redireciona para a página inicial


@app.route('/delete/<int:user_id>')
def delete_user(user_id):
    try:
        with sqlite3.connect(DATABASE) as conn:
            conn.execute('DELETE FROM users WHERE id = ?', (user_id, ))
            conn.commit()
        flash("Usuário excluído com sucesso!",
              "success")  # Mensagem de sucesso
        return redirect(url_for('dashboard'))
    except Exception as e:
        print(f"Erro ao excluir usuário: {e}")
        flash("Erro ao excluir usuário.", "error")  # Mensagem de erro
        return redirect(url_for('dashboard'))


@app.route('/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        whatsapp = request.form.get('whatsapp')
        workplace = request.form.get('workplace')

        try:
            with sqlite3.connect(DATABASE) as conn:
                conn.execute(
                    'UPDATE users SET name = ?, address = ?, whatsapp = ?, workplace = ? WHERE id = ?',
                    (name, address, whatsapp, workplace, user_id))
                conn.commit()
            flash("Usuário atualizado com sucesso!", "success")
            return redirect(url_for('dashboard'))
        except Exception as e:
            print(f"Erro ao editar usuário: {e}")
            flash("Erro ao editar usuário.", "error")  # Mensagem de erro
            return redirect(url_for('dashboard'))

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute('SELECT * FROM users WHERE id = ?', (user_id, ))
        user = cursor.fetchone()
    return render_template('edit.html', user=user)


if __name__ == '__main__':
    app.run(debug=True)
