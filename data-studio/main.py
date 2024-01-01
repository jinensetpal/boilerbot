import os
from flask import Flask, render_template, request, url_for, redirect, send_from_directory
 
app = Flask(__name__)
app.config["SECRET_KEY"] = "retracted"
 

@app.route("/login", methods=["GET", "POST"])
def login():
    return redirect(url_for("home"))
 
 
@app.route("/logout")
def logout():
    return redirect(url_for("home"))
 
# the home page, login required. If not logged in, redirect to login page
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/stats")
def stats():
    return render_template("stats.html")

@app.route("/api")
def api():
    return render_template("api.html")

@app.route("/llm")
def llm():
    return render_template("llm.html")

@app.route("/dataset")
def dataset():
    return render_template("dataset.html")

@app.route("/annotation")
def annotation():
    return render_template("annotation.html")

# static files in the protected folder
@app.route("/protected/<path:filename>")
def protected(filename):
    return send_from_directory(
        './protected/',
        filename
    )

 
if __name__ == "__main__":
    app.run()
