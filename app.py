from flask import Flask
from db import bootstrap_database
app = Flask(__name__)

@app.route("/")
def index():
    return "<h1>Hello TMDB!</h1>"

bootstrap_database(20)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
