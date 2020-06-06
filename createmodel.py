import os
from flask import Flask, render_template,request
from model import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://yiaktitnncxgkc:12f2f9896d80d800eaf83df606f7e5e01ce1b116bfbf204d4794c4a2e7e4fc03@ec2-54-217-224-85.eu-west-1.compute.amazonaws.com:5432/d5hgch16ad19p8"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

def main():
    db.create_all()


if __name__ == "__main__":
    with app.app_context():
        main()