from random import randint
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from worker import *

app = Flask(__name__)

@app.route("/")
def homepage():
	return render_template("homepage.html")


@app.route("/", methods=['POST'])
def my_form_post():
    text = request.form['topic']
    if len(text) < 1:
    	text = fallback_list[randint(0, len(fallback_list))]
    search_term = text.lstrip().lower()
    joined_df = map_sentiment(search_term)
    build_plot(search_term, joined_df, text)
    return redirect(url_for('display', most_populous=None))


@app.route("/updated")
def display():
	return render_template("updated.html") # if something is undefined, pass as a param


if __name__ == "__main__":
    app.run()