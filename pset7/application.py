from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp

from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.route("/")
@login_required
def index():
    # make dictionary with purcahse data from transactions
    stocks = db.execute("SELECT symbol, SUM(amount) as amount, sum(price) as price \
                        FROM transactions WHERE u_id=:id GROUP BY symbol HAVING SUM(amount) > 0", id = session["user_id"])

    # get the users cash from dictionary
    u_cash = db.execute("SELECT cash FROM users WHERE id=:id", id=session["user_id"])[0]["cash"]

    # add the stockprice to the dictionary
    for x in stocks:
        x.update({"stockp": lookup(x["symbol"])["price"]})

    # calculate total belongings including owned cash
    own = 0
    for symbol in stocks:
        own += symbol["price"]
    totalsauce = own + u_cash

    return render_template("index.html", stocks=stocks, cash=usd(u_cash), total=usd(totalsauce))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock."""
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        purchase = request.form.get("symbol")
        stock = lookup(request.form.get("symbol"))
        user_id = session["user_id"]

        # check whether ticker symbol is valid
        if lookup(request.form.get("symbol")) == None:
            return apology("invalid ticker symbol")

        # make the amount input an integer
        try:
            amount = int(request.form.get("shares"))
        except:
            return apology("must be a number")

        # check whether the input is a positive amount
        if amount < 0:
            return apology("input positive number")

        price = lookup(purchase)["price"]

        # calculate total price
        total_price = stock["price"] * int(request.form.get("shares"))

        sauce = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=user_id)

        # check whether user has enough cash
        if sauce[0]["cash"] >= total_price:
            # if enough cash then buy and insert the purchase into transactions
            db.execute("INSERT INTO transactions (u_id, symbol, amount, price, transactiontype, stockp)\
                        VALUES (:user_id, :purchase, :amount, :price, 'bought', :stockp)", user_id=user_id, purchase=purchase, amount=int(amount), price=total_price, stockp=price)
            # if enough cash then update the users cash
            db.execute("UPDATE users SET cash = cash - :price WHERE id = :u_id", price=total_price, u_id=user_id)

        # if he doesn't then error
        else:
            return apology("Insufficient funds")

        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions."""
    # make the dict so we can display the data using Jinja
    stocks = db.execute("SELECT symbol, amount, price, transactiontype, stockp, datetime \
                        FROM transactions WHERE u_id=:id", id=session["user_id"])

    return render_template("history.html", stocks=stocks)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        quote = lookup(request.form.get("symbol"))

        # ensure user passes in symbol
        if not request.form.get("symbol"):
            return apology("Must provide symbol")

        # ensure passed in symbol is valid
        if not quote:
            return apology("Symbol doesn't exist")

        return render_template("quoted.html", name=quote["name"], symbol=quote["symbol"], price=usd(quote["price"]))
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password")

        # ensure password and confirmation are the same
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords don't match")

        # add username and password to database if username doesn't exist
        result = db.execute("INSERT INTO users (username, hash) values(:username, :hash)" \
                            ,username=request.form.get("username"), hash=pwd_context.hash(request.form.get("password")))

        if not result:
            return apology("Username already in use")

        # remember which user has logged in
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        session["user_id"] = rows[0]["id"]

        # redirect user to index page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock."""
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        symbol = request.form.get("symbol")
        amount = int(request.form.get("shares"))
        price = lookup(symbol)["price"]
        user_id = session["user_id"]
        total_price = amount * price

        # ensure user passes in symbol
        if not symbol:
            return apology("Please enter a valid symbol")
        # ensure passed in amount is positive
        if amount <= 0:
            return apology("Please enter a positive amount of shares")

        # query database for total amount of shares from passed in stocksymbol
        user_shares = db.execute("SELECT SUM(amount) as total_amount FROM transactions \
                                  WHERE u_id=:user AND symbol=:symbol GROUP BY symbol", user=user_id, symbol=symbol)

        # ensure user has enough shares
        if user_shares[0]["total_amount"] < 1 or user_shares[0]["total_amount"] < amount:
            return apology("Insufficient shares")

        # update database if user has enough shares
        else:
            db.execute("INSERT INTO transactions (u_id, symbol, amount, price, transactiontype, stockp) \
                        VALUES (:user_id, :purchase, :amount, :price, 'sold', :stockp)", user_id=session["user_id"], purchase=symbol, amount=-amount, price=-total_price, stockp=price)

            db.execute("UPDATE users SET cash = cash + :total_price WHERE id=:user_id" \
                        ,total_price = total_price, user_id = session["user_id"])

        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        user_id = session["user_id"]

        # query database for all symbols with a positive amount of shares used for making dropdown list
        symbolslst = db.execute("SELECT symbol FROM transactions WHERE u_id=:user \
                                GROUP BY symbol HAVING sum(amount) > 0", user=user_id)

        return render_template("sell.html", symbols=symbolslst)


@app.route("/changepw", methods=["GET", "POST"])
@login_required
def changepw():
    """Change the password."""

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure new password was submitted
        if not request.form.get("new_password"):
            return apology("must provide password")

        # ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password")

        # ensure password and confirmation are the same
        if request.form.get("new_password") != request.form.get("confirmation"):
            return apology("passwords don't match")

        # update database delete old hash insert new hash
        result = db.execute("UPDATE users SET hash = :hash WHERE id=:user_id" \
                            ,user_id=session["user_id"], hash=pwd_context.hash(request.form.get("new_password")))

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("changepw.html")
