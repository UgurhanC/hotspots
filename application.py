from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
import os

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
db = SQL("sqlite:///hotspots.db")


@app.route("/")
@login_required
def index():
    return render_template("register.html")
    # # make dictionary with purcahse data from transactions
    # stocks = db.execute("SELECT symbol, SUM(amount) as amount, sum(price) as price \
    #                     FROM transactions WHERE u_id=:id GROUP BY symbol HAVING SUM(amount) > 0", id = session["user_id"])

    # # get the users cash from dictionary
    # u_cash = db.execute("SELECT cash FROM users WHERE id=:id", id=session["user_id"])[0]["cash"]

    # # add the stockprice to the dictionary
    # for x in stocks:
    #     x.update({"stockp": lookup(x["symbol"])["price"]})

    # # calculate total belongings including owned cash
    # own = 0
    # for symbol in stocks:
    #     own += symbol["price"]
    # totalsauce = own + u_cash

    # return render_template("index.html", stocks=stocks, cash=usd(u_cash), total=usd(totalsauce))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if inlog(username, password) == -1:
            return apology("inlog failed")

        session["user_id"] = inlog

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

@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    """forgot password."""

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure email was submitted
        if not request.form.get("email"):
            return apology("must provide email / email adress unknown")

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("forgot.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure name was submitted
        if not request.form.get("name"):
            return apology("must provide name")

        # ensure username was submitted
        elif not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password")

        # ensure password and confirmation are the same
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords don't match")

         # ensure email was submitted
        elif not request.form.get("email"):
            return apology("must provide email adress")

        # add name and username and password and email to database if username doesn't exist
        result = db.execute("INSERT INTO users (name, username, hash, email) values(:name, :username, :hash, :email)" \
                            ,name=request.form.get("name"), username=request.form.get("username"), hash=pwd_context.hash(request.form.get("password")), email=request.form.get("email"))

        if not result:
            return apology("Username already in use")

        # remember which user has logged in
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        session["user_id"] = rows[0]["user_id"]

        # redirect user to index page
        return redirect(url_for("login"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


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

@app.route("/changeun", methods=["GET", "POST"])
@login_required
def changeun():
    return apology("todo")

@app.route("/follow", methods=["GET", "POST"])
@login_required
def follow():
    return apology("todo")

@app.route("/like", methods=["GET", "POST"])
@login_required
def like():
    return apology("todo")

@app.route("/react", methods=["GET", "POST"])
@login_required
def react():
    return apology("todo")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == 'POST':
        UPLOAD_FOLDER = os.getcwd() + "/pics"

        ALLOWED_EXTENSIONS = ['.png', '.jpg', '.jpeg']
        file = request.files['image']
        f = os.path.join(UPLOAD_FOLDER, file.filename)

        extension = os.path.splitext(file.filename)[1]
        if extension not in ALLOWED_EXTENSIONS:
            return apology("extension not allowed")
        if not request.form.get("location"):
            return apology("location must be given")
        if request.form.get("location")[0].isupper() == False:
            return apology("no capital letter")
        if not request.form.get("caption"):
            db.execute("INSERT INTO photo (user_id, filename, location) VALUES (:user_id, :filename, :location)",
               user_id='1', filename=file.filename, location=request.form.get("location"))
        else:
            db.execute("INSERT INTO photo (user_id, filename, location) VALUES (:user_id, :filename, :location)",
               user_id='1', filename=file.filename, location=request.form.get("location"))
        file.save(f)

        else:

        return render_template('index.html')
    else:
        return render_template('upload.html')
