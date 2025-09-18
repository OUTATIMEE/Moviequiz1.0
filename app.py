from db import bootstrap_database, SessionLocal, Movie, Genre
from sqlalchemy import func
from flask import Flask, render_template, request, session, jsonify
import json, os
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_key")

def prepare_round(filme):
    movie_sample = []
    new_ids = []
    for idx, film in enumerate(filme):
        movie_sample.append({
            "poster_number": f"movie_{idx}_poster",
            "id": film.id,
            "title": film.title,
            "release_date": film.release_date.isoformat() if film.release_date else None,
            "poster_path": film.poster_path,
            "vote_average": film.vote_average,
        })
        new_ids.append(film.id)

    session["movie_sample"] = movie_sample
    session["sorted_sample"] = sorted(movie_sample, key=lambda m: m["release_date"] or "")


    used_ids = session.get("used_ids", [])
    session["used_ids"] = (used_ids + new_ids)[-300:]

    return [f"https://image.tmdb.org/t/p/w500{m['poster_path']}" for m in movie_sample]

@app.route("/")
def index():
    return render_template("startseite.html")


@app.route("/start_quiz", methods=["POST"])
def genre_auswahl():
    deaktivierte_genres = json.loads(request.form['genres'])
    session["deaktivierte_genres"] = deaktivierte_genres
    session["used_ids"] = []

    db = SessionLocal()
    try:
        query = db.query(Movie)
        if deaktivierte_genres:
            query = query.filter(Movie.genres.any(~Genre.name.in_(deaktivierte_genres)))

        total = query.count()
        if total < 150:
            return render_template("startseite.html",
                                   error_msg=f"Zu wenige Filme für diese Auswahl ({total}, min. 150).")

        filme = query.order_by(func.random()).limit(5).all()

        poster_paths = prepare_round(filme)
    finally:
        db.close()

    return render_template("quizseite.html",
                           movie_0_poster=poster_paths[0],
                           movie_1_poster=poster_paths[1],
                           movie_2_poster=poster_paths[2],
                           movie_3_poster=poster_paths[3],
                           movie_4_poster=poster_paths[4])


@app.route("/runde-pruefen", methods=["POST"])
def runde_pruefen():
    data_str = request.form["auswahl"]
    user_input = json.loads(data_str)

    filme_infos = session.get("sorted_sample", [])

    ergebnisse = []
    score = 0
    gesamt = session.get("gesamtpunktzahl", 0)

    for index, user_poster_id in enumerate(user_input):
        correct_movie = filme_infos[index]
        correct_poster_id = correct_movie["poster_number"]

        if user_poster_id == correct_poster_id:
            ergebnisse.append({
                "poster_number": user_poster_id,
                "korrekt": True,
                "punkte": 100,
                "release_date": correct_movie["release_date"],
            })
            score += 100
        else:
            ergebnisse.append({
                "poster_number": user_poster_id,
                "korrekt": False,
                "punkte": 0,
                "release_date": correct_movie["release_date"],
            })

    gesamt += score
    session["gesamtpunktzahl"] = gesamt

    return jsonify({"ergebnisse": ergebnisse, "gesamt": gesamt})



@app.route("/neue_runde", methods=["GET"])
def neue_runde():
    deaktivierte_genres = session.get("deaktivierte_genres", [])
    used_ids = session.get("used_ids", [])

    db = SessionLocal()
    try:
        query = db.query(Movie)
        if deaktivierte_genres:
            query = query.filter(Movie.genres.any(~Genre.name.in_(deaktivierte_genres)))
        if used_ids:
            query = query.filter(~Movie.id.in_(used_ids))


        filme = query.order_by(func.random()).limit(5).all()
        poster_paths = prepare_round(filme)
    finally:
        db.close()

    return render_template("quizseite.html",
                           movie_0_poster=poster_paths[0],
                           movie_1_poster=poster_paths[1],
                           movie_2_poster=poster_paths[2],
                           movie_3_poster=poster_paths[3],
                           movie_4_poster=poster_paths[4])



if __name__ == "__main__":
    bootstrap_database(pages=50)
    app.run(host="0.0.0.0", port=8000, debug=True)
