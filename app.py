import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # Obter todas as ações que o usuário possui (somar as compradas e subtrair as vendidas)
    portfolio = db.execute("""
        SELECT symbol, SUM(shares) as total_shares
        FROM transactions
        WHERE user_id = ?
        GROUP BY symbol
        HAVING total_shares > 0
    """, session["user_id"])

    # Inicializar valores
    total_value = 0
    for stock in portfolio:
        stock_info = lookup(stock["symbol"])
        stock["price"] = float(stock_info["price"])
        stock["name"] = stock_info["name"]
        stock["total_value"] = stock["total_shares"] * stock["price"]
        stock["total_value"] = float(stock["total_value"])
        total_value += stock["total_value"]

    # Obter o saldo de dinheiro do usuário
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]

    # Calcular o valor total
    total_value += cash

    return render_template("index.html", portfolio=portfolio, cash=usd(cash), total_value=usd(total_value))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")
    else:
        symbol = request.form.get("symbol").upper()
        if not symbol:
            return apology("Preencha o campo symbol")
        compra = lookup(symbol)
        if compra == None:
            return apology("Símbolo inválido")
        else:
            try:
                shares = int(request.form.get("shares"))

                if shares < 1:
                    return apology("Shares tem que ser no mínimo 1.")
            except ValueError:
                return apology("Shares devem ser um número inteiro.")

            valor_total = float(compra["price"]) * shares
            saldo_atual = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
            if valor_total > saldo_atual[0]["cash"]:
                return apology("Saldo insuficiente")
            else:
                saldo_remanescente = round(float(saldo_atual[0]["cash"]), 2) - round(valor_total, 2)
                transaction_type = "buy"
                db.execute("UPDATE users SET cash = ? WHERE id = ?",
                           saldo_remanescente, session["user_id"])
                db.execute("INSERT INTO transactions (user_id, symbol, price, shares, type, timestamp) VALUES (?, ?, ?, ?, ?, datetime('now'))",
                           session["user_id"], symbol, compra["price"], shares, transaction_type)
                return redirect("/")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    all_transactions = db.execute("""
        SELECT * FROM transactions
        WHERE user_id = ?
        """, session["user_id"])
    return render_template("history.html", all_transactions=all_transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # Se for método GET eu mostro um formulário de compra
    if request.method == "GET":
        return render_template("quote.html")
    else:
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("Campo de símbolo em branco")
        result = lookup(symbol)
        if result != None:
            result["price"] = usd(result["price"])
            return render_template("quote_post.html", result=result)
        else:
            return apology("Símbolo inválido")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Se o usuário tentar acessar vi GET vou mostrar o formulario de registro
    if request.method == "GET":
        return render_template("register.html")

    else:
        # checkando possíveis erros de input do usuário
        username = request.form.get("username")
        password = request.form.get("password")
        passwordcheck = request.form.get("confirmation")

        if not username or not password or not passwordcheck:
            return apology("Preencha todos os campos solicitados")
        elif password != passwordcheck:
            return apology("As senhas fornecidas não conferem")

        username_existed = db.execute("SELECT username FROM users WHERE username = ?", username)
        if len(username_existed) > 0:
            return apology("Já existe um usuário com esse username")
        # inserindo o novo usuário a tabela de usuários
        hash_password = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash_password)
        # log user in
        user_id = db.execute("SELECT id FROM users WHERE username = ?", username)[0]["id"]
        session["user_id"] = user_id

        # redirecionei o usuário para fazer o log in
        return redirect("/")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "GET":
        # Buscar ações do usuário
        data_user = db.execute("""
            SELECT symbol, SUM(shares) as shares
            FROM transactions
            WHERE user_id = ?
            GROUP BY symbol
            HAVING SUM(shares) > 0
        """, session["user_id"])
        print(data_user)
        return render_template("sell.html", data_user=data_user)

    else:
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))

        # Verificar se o símbolo é válido
        if not symbol:
            return apology("Escolha um símbolo válido.")

        # Verificar se o número de ações é válido
        if shares < 1:
            return apology("Número inválido de ações.")

        # Obter número de ações do usuário
        data_user = db.execute("""
            SELECT SUM(shares) as shares
            FROM transactions
            WHERE user_id = ? AND symbol = ?
            GROUP BY symbol
        """, session["user_id"], symbol)

        if len(data_user) != 1 or shares > data_user[0]["shares"]:
            return apology("Você não possui ações suficientes.")

        # Buscar preço atual da ação
        stock_info = lookup(symbol)
        if not stock_info:
            return apology("Símbolo de ação inválido.")

        # Calcular valor da venda
        valor_venda = float(stock_info["price"]) * shares

        # Inserir transação de venda (positiva) com o tipo 'sell'
        db.execute("""
            INSERT INTO transactions (user_id, symbol, price, shares, type, timestamp)
            VALUES (?, ?, ?, ?, 'sell', datetime('now'))
        """, session["user_id"], symbol, stock_info["price"], -shares)

        # Atualizar saldo de cash do usuário
        cash_atual = db.execute("SELECT cash FROM users WHERE id = ?",
                                session["user_id"])[0]["cash"]
        db.execute("UPDATE users SET cash = ? WHERE id = ?",
                   cash_atual + valor_venda, session["user_id"])

        return redirect("/")


@app.route("/addsaldo", methods=["GET", "POST"])
@login_required
def addsaldo():
    """Adicionar saldo"""
    if request.method == "GET":
        return render_template("addsaldo.html")
    else:
        saldo = int(request.form.get("saldo"))
        if not saldo or saldo < 1:
            return apology("Adicionar valor maior do que $1")

        user_saldo = db.execute("SELECT cash FROM users WHERE id = ?",
                                session["user_id"])[0]["cash"]
        novo_saldo = float(user_saldo) + saldo
        db.execute("UPDATE users SET cash = ? WHERE id = ? ", novo_saldo, session["user_id"])
        return render_template("addsaldo_success.html")
