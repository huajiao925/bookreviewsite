import os
import requests

from flask import Flask, flash, session, render_template, jsonify, request, redirect, url_for
from flask_session import Session
from functools import wraps
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from model import *
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'aosivunvw3i28fhosd!#$%9s8dhqiuh'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://yiaktitnncxgkc:12f2f9896d80d800eaf83df606f7e5e01ce1b116bfbf204d4794c4a2e7e4fc03@ec2-54-217-224-85.eu-west-1.compute.amazonaws.com:5432/d5hgch16ad19p8"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgres://yiaktitnncxgkc:12f2f9896d80d800eaf83df606f7e5e01ce1b116bfbf204d4794c4a2e7e4fc03@ec2-54-217-224-85.eu-west-1.compute.amazonaws.com:5432/d5hgch16ad19p8")
db = scoped_session(sessionmaker(bind=engine))


def login_required(t):
    @wraps(t)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return t(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect('/login')
    return wrap

@app.route("/", methods=["GET","POST"])
def index():
    error = None
    keyword = request.form.get("search")
    if request.method == "POST":
        if not keyword:
            return render_template("index.html", error="search can not be empty")
        query = '%' + keyword + '%'
        query = query.title()
        ##get book and put into a list
        result = db.execute("SELECT isbn, title, author, year FROM Books WHERE \
                            isbn LIKE :query OR \
                            title LIKE :query OR \
                            author LIKE :query",
                            {"query": query})
        if result.rowcount == 0:
            return render_template("index.html", error='not found')
        books = result.fetchall()
        return render_template("index.html", books=books)
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    #clear user login info
    session.clear()
    error = None
    if request.method == "POST":
        if not request.form.get("username"):
            return render_template('register.html', error="username cannot be empty")
        checkname = db.execute("SELECT * FROM users WHERE name = :username",
                   {"username": request.form.get("username")}).fetchone()
        if checkname:
            return render_template('register.html', error= "user aleady exists.")
        elif not request.form.get("password"):
            return render_template('register.html', error="password cannot be empty")
        elif not request.form.get("confirmpwd"):
            return render_template('register.html', error="must confirm the password")
        elif not request.form.get("password") == request.form.get("confirmpwd"):
            return render_template('register.html', error="passwords does not match")

        hashedPassword = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256')
        db.execute("INSERT INTO users(name, password) VALUES(:username,:password)",
                   {"username": request.form.get("username"),
                    "password": hashedPassword
                   })
        db.commit()
        flash("Done")
        return render_template("login.html")
    else:
        return render_template("register.html")


@app.route("/login", methods = ["GET","POST"])
def login():
    session.clear()
    username = request.form.get("username")
    message = None
    if request.method == "POST":
        if not request.form.get("username"):
            return render_template("login.html", error="username cannot be empty")
        elif not request.form.get("password"):
            return render_template("login.html", error="password cannot be empty")

        validation = db.execute("SELECT * FROM users WHERE name = :username",
                           {"username": request.form.get("username")}).fetchone()
        if validation == None:
            return render_template('login.html', error="user name or password incorrect")
        elif not check_password_hash(validation[2], request.form.get("password")):
            return render_template('login.html', error="user name or password incorrect")

        session['logged_in'] = True
        session['username'] = username
        return redirect("/")
    else:
        return render_template("login.html")


def logout():
    session.pop('logged_in', None)
    flash("You were logged out.")
    return redirect("/login")


@app.route("/review/<isbn>", methods=['GET', 'POST'])
@login_required
def reviews(isbn):

    row1 = db.execute("SELECT id FROM Books WHERE isbn= :isbn", {"isbn": isbn})
    book_id = row1.fetchone()
    book_id = book_id[0]

    if request.method=='GET':
        #retrieve info from Books and Reviews table
        row2 = db.execute("SELECT title, author, year, isbn FROM Books WHERE isbn = :isbn", {'isbn': isbn})
        row3 = db.execute("SELECT rate, review FROM Reviews WHERE book_id = :book_id", {'book_id': book_id})
        book_info = row2.fetchall()
        review_info = row3.fetchall()
        #retrieve info from GoodRead API
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key":"TIxJyicdHh1JvXDa278OA","isbns":isbn})

        if res.status_code == 200:
            result = res.json()
            gd_avg_rating = result["books"][0]["average_rating"]
            gd_review_count = result["books"][0]["reviews_count"]
        else:
            gd_avg_rating = '-'
            gd_review_count = '-'
        return render_template('reviews.html', bookinfo=book_info, reviewinfo=review_info,
                               gd_avg_rating=gd_avg_rating,
                               gd_review_count=gd_review_count)
    # request.method = 'POST'
    else:
        error = None
        if not request.form.get("rating"):
            return render_template('reviews.html', error="rating cannot be empty")
        ur_rating = request.form.get("rating")
        ur_review = request.form.get("review")
        row = db.execute("SELECT id FROM Books WHERE isbn= :isbn", {"isbn": isbn})
        book_id = row.fetchone()
        book_id = book_id[0]
        print(ur_rating)
        db.execute("INSERT INTO reviews(book_id, rate, review) VALUES (:book_id, :ur_rating, :ur_review)",
                   {
                       "book_id": book_id,
                       "ur_rating": ur_rating,
                       "ur_review": ur_review
                    })
        db.commit()
        return redirect("/review/" + isbn)
