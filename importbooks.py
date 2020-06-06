import csv
import os

from flask import Flask, render_template, request
from model import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URL"] = "[herokuURI]"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

def main():
    f = open('books1.csv')
    reader = csv.reader(f)
    books =[]
    for isbn,title,author,year in reader:
        book = Books(isbn=isbn,title=title,author=author,year=year)
        books.append(book)
    db.session.add_all(books)
    print('done')
    db.session.commit()
    print('done')

if __name__ == "__main__":
    with app.app_context():
        main()
