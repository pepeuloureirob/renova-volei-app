import os
import sqlite3
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "renova_secret"

# =========================
# BANCO DE DADOS (CORREÇÃO RENDER)
# =========================
DB_DIR = "database"
DB = os.path.join(DB_DIR, "database.db")

if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# =========================
# CÁLCULO DE SUB
# =========================
def calcular_sub(data_nascimento):
    hoje = date.today()
    nascimento = datetime.strptime(data_nascimento, "%Y-%m-%d").date()
    idade = hoje.year - nascimento.year

    if idade <= 12:
        return "Sub13"
    elif idade <= 14:
        return "Sub15"
    elif idade <= 16:
        return "Sub17"
    elif idade <= 18:
        return "Sub19"
    elif idade <= 20:
        return "Sub21"
    elif idade <= 22:
        return "Sub23"
    else:
        return "Adulto"

# =========================
# INIT DB (AGORA EXECUTA NO RENDER)
# =========================
def init_db():
    conn = get_db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS atletas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        nascimento TEXT,
        altura TEXT,
        endereco TEXT,
        telefone TEXT,
        responsavel TEXT,
        telefone_responsavel TEXT,
        escola TEXT,
        clube TEXT,
        padrao_treino TEXT,
        padrao_jogo TEXT,
        camisa TEXT,
        numero TEXT,
        sub TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS competicoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        data TEXT,
        subs TEXT,
        local TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS inscricoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        atleta_id INTEGER,
        competicao_id INTEGER
    )
    """)

    conn.commit()
    conn.close()

# 🔥 ESSENCIAL PARA O RENDER
init_db()

# =========================
# DASHBOARD
# =========================
@app.route("/")
def dashboard():
    conn = get_db()
    subs = ["Sub13", "Sub15", "Sub17", "Sub19", "Sub21", "Sub23", "Adulto"]
    contagem = {}

    for sub in subs:
        total = conn.execute(
            "SELECT COUNT(*) FROM atletas WHERE sub=?",
            (sub,)
        ).fetchone()[0]
        contagem[sub] = total

    conn.close()
    return render_template("dashboard.html", contagem=contagem)

# =========================
# ATLETAS
# =========================
@app.route("/atletas")
def atletas():
    conn = get_db()
    atletas = conn.execute(
        "SELECT * FROM atletas ORDER BY sub, nome"
    ).fetchall()
    conn.close()
    return render_template("atletas.html", atletas=atletas)

# =========================
# CADASTRAR ATLETA
# =========================
@app.route("/cadastrar_atleta", methods=["GET", "POST"])
def cadastrar_atleta():
    if request.method == "POST":
        dados = request.form
        sub = calcular_sub(dados["nascimento"])

        conn = get_db()
        conn.execute("""
        INSERT INTO atletas (
            nome, nascimento, altura, endereco, telefone,
            responsavel, telefone_responsavel, escola, clube,
            padrao_treino, padrao_jogo, camisa, numero, sub
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dados["nome"],
            dados["nascimento"],
            dados["altura"],
            dados["endereco"],
            dados["telefone"],
            dados["responsavel"],
            dados["telefone_responsavel"],
            dados["escola"],
            dados["clube"],
            dados["padrao_treino"],
            dados["padrao_jogo"],
            dados["camisa"],
            dados["numero"],
            sub
        ))

        conn.commit()
        conn.close()

        flash("Atleta cadastrado com sucesso!")
        return redirect(url_for("dashboard"))

    return render_template("cadastrar_atleta.html")

# =========================
# EDITAR ATLETA
# =========================
@app.route("/editar_atleta/<int:id>", methods=["GET", "POST"])
def editar_atleta(id):
    conn = get_db()

    if request.method == "POST":
        dados = request.form
        sub = calcular_sub(dados["nascimento"])

        conn.execute("""
        UPDATE atletas SET
            nome=?, nascimento=?, altura=?, endereco=?, telefone=?,
            responsavel=?, telefone_responsavel=?, escola=?, clube=?,
            padrao_treino=?, padrao_jogo=?, camisa=?, numero=?, sub=?
        WHERE id=?
        """, (
            dados["nome"],
            dados["nascimento"],
            dados["altura"],
            dados["endereco"],
            dados["telefone"],
            dados["responsavel"],
            dados["telefone_responsavel"],
            dados["escola"],
            dados["clube"],
            dados["padrao_treino"],
            dados["padrao_jogo"],
            dados["camisa"],
            dados["numero"],
            sub,
            id
        ))

        conn.commit()
        conn.close()

        flash("Atleta atualizado!")
        return redirect(url_for("atletas"))

    atleta = conn.execute(
        "SELECT * FROM atletas WHERE id=?",
        (id,)
    ).fetchone()

    conn.close()
    return render_template("editar_atleta.html", atleta=atleta)

# =========================
# REMOVER ATLETA
# =========================
@app.route("/remover_atleta/<int:id>")
def remover_atleta(id):
    conn = get_db()
    conn.execute("DELETE FROM atletas WHERE id=?", (id,))
    conn.commit()
    conn.close()

    flash("Atleta removido.")
    return redirect(url_for("atletas"))

# =========================
# COMPETIÇÕES
# =========================
@app.route("/competicoes")
def competicoes():
    conn = get_db()
    competicoes = conn.execute("""
        SELECT * FROM competicoes
        ORDER BY ABS(julianday(data) - julianday('now'))
    """).fetchall()
    conn.close()

    return render_template("competicoes.html", competicoes=competicoes)

# =========================
# CADASTRAR COMPETIÇÃO
# =========================
@app.route("/cadastrar_competicao", methods=["GET", "POST"])
def cadastrar_competicao():
    if request.method == "POST":
        dados = request.form

        conn = get_db()
        conn.execute("""
        INSERT INTO competicoes (nome, data, subs, local)
        VALUES (?, ?, ?, ?)
        """, (
            dados["nome"],
            dados["data"],
            dados["subs"],
            dados["local"]
        ))

        conn.commit()
        conn.close()

        flash("Competição cadastrada!")
        return redirect(url_for("dashboard"))

    return render_template("cadastrar_competicao.html")

# =========================
# RUN LOCAL
# =========================
if __name__ == "__main__":
    app.run(debug=True)
