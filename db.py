from sqlalchemy import String, Integer, Table, Column, ForeignKey, create_engine
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase, sessionmaker
from typing import List
from config import DATABASE_URL, TMDB_API_KEY
import requests

class Base(DeclarativeBase):
    pass


engine = create_engine(DATABASE_URL, echo=True, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


movie_genres = Table(
    "movie_genres",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id"), primary_key=True),
    Column("genre_id", ForeignKey("genres.id"), primary_key=True)
)

class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tmdb_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    poster_path: Mapped[str] = mapped_column(String(200))

    genres: Mapped[List["Genre"]] = relationship(
        secondary=movie_genres, back_populates="movies"
    )

class Genre(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    movies: Mapped[List[Movie]] = relationship(
        secondary=movie_genres, back_populates="genres"
    )

def starte_db():
    Base.metadata.create_all(engine)

from sqlalchemy.exc import IntegrityError

def genre_tabelle_fuellen():
    genre_ids = {
        "Action": 28,
        "Adventure": 12,
        "Animation": 16,
        "Comedy": 35,
        "Crime": 80,
        "Documentary": 99,
        "Drama": 18,
        "Family": 10751,
        "Fantasy": 14,
        "History": 36,
        "Horror": 27,
        "Music": 10402,
        "Mystery": 9648,
        "Romance": 10749,
        "Science fiction": 878,
        "Tv movie": 10770,
        "Thriller": 53,
        "War": 10752,
        "Western": 37
    }

    db = SessionLocal()
    try:
        for name, gid in genre_ids.items():
            genre = Genre(id=gid, name=name)
            db.add(genre)

        db.commit()
    except IntegrityError:

        db.rollback()
    finally:
        db.close()



def api_abfrage_TMDB(page: int = 1):
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "sort_by": "vote_average.desc",
        "vote_count.gte": 2000,
        "page": page,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def movie_tabelle_fuellen(pages: int = 100):
    db = SessionLocal()
    try:
        for page in range(1, pages + 1):
            data = api_abfrage_TMDB(page)
            for movie_data in data["results"]:
                if db.query(Movie).filter_by(tmdb_id=movie_data["id"]).first():
                    continue

                genres = []
                for gid in movie_data.get("genre_ids", []):
                    genre = db.get(Genre, gid)
                    if genre:
                        genres.append(genre)


                movie = Movie(
                    tmdb_id=movie_data["id"],
                    title=movie_data["title"],
                    poster_path=movie_data.get("poster_path"),
                    genres=genres,
                )
                db.add(movie)

            db.commit()
    finally:
        db.close()


def bootstrap_database(pages: int = 100):
    Base.metadata.create_all(engine)

    db = SessionLocal()
    try:
        if db.query(Movie).first():
            print("✅ Datenbank enthält bereits Filme – kein Seed nötig.")
            return

        print("➡️ Fülle Genres...")
        genre_tabelle_fuellen()

        print(f"➡️ Lade Filme (ca. {pages*20} Stück)...")
        movie_tabelle_fuellen(pages=pages)

        print("✅ Datenbank wurde befüllt!")
    finally:
        db.close()


